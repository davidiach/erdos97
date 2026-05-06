"""Optimized selected-witness search with vertex-circle pruning.

This is a faster, bitset-based reimplementation of
``GenericVertexSearch`` intended for n = 11 exhaustive coverage.

Key optimizations versus ``generic_vertex_search.py``:

1. Per-(i, j) compatibility is precomputed as a Python ``int`` bitset over
   the *index* of mask_j in ``options[j]``; AND-ing these bitsets for each
   already-assigned center gives the per-center "remaining options" set in
   O(num_assigned) bitset ops.
2. Constraint propagation: every time we assign a center+mask, we AND its
   (c -> cc) compatibility bitset into ``remaining[cc]`` for every still-free
   center cc.  This is dramatically more aggressive than the on-the-fly
   compatibility check used by ``GenericVertexSearch``.
3. Column-overflow and witness-pair-overflow checks are propagated lazily
   at branch time but use precomputed mask -> column-target / pair-index
   lookups.
4. The vertex-circle status is computed *incrementally*: the union-find
   ``parent`` array is mutated on union (without path compression) and rolled
   back on undo by storing the previous parent value of the just-merged
   root; the strict-edge graph is appended-to and popped-from in LIFO.
   Each backtrack is O(num_added).
5. Dihedral (reflection) symmetry is applied at row 0: only the canonical
   representative under x -> -x mod n is searched; the orbit factor is 2.

The artifacts agree with ``GenericVertexSearch`` on full-assignment counts
across all tested cases (every n=9 row0; every spot-checked n=10 row0).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from time import monotonic


@dataclass(frozen=True)
class FastSearchResult:
    n: int
    row0_index: int
    row0_mask: int
    nodes_visited: int
    full_assignments: int
    aborted: bool
    elapsed_seconds: float
    counts: dict

    def to_json(self) -> dict:
        return {
            "n": self.n,
            "row0_index": self.row0_index,
            "row0_mask": self.row0_mask,
            "nodes": self.nodes_visited,
            "full": self.full_assignments,
            "aborted": self.aborted,
            "elapsed": self.elapsed_seconds,
            "counts": dict(sorted(self.counts.items())),
        }


def _mask(values) -> int:
    out = 0
    for v in values:
        out |= 1 << v
    return out


def _bits(mask: int, n: int) -> list:
    return [i for i in range(n) if (mask >> i) & 1]


def _in_open_arc(a: int, b: int, x: int, n: int) -> bool:
    return ((x - a) % n) < ((b - a) % n) and x != a and x != b


def _chords_cross(a: int, b: int, c: int, d: int, n: int) -> bool:
    if len({a, b, c, d}) < 4:
        return False
    return _in_open_arc(a, b, c, n) != _in_open_arc(a, b, d, n)


class FastVertexSearch:
    """Bitset-based selected-witness search."""

    def __init__(self, n: int, row_size: int = 4, pair_cap: int = 2) -> None:
        if row_size != 4:
            raise ValueError("only row_size=4 supported")
        if n < row_size + 1:
            raise ValueError("n too small")
        self.n = n
        self.row_size = row_size
        self.pair_cap = pair_cap
        self.max_indegree = (pair_cap * (n - 1)) // (row_size - 1)

        self.pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        self.pair_index = {p: idx for idx, p in enumerate(self.pairs)}
        self.num_pairs = len(self.pairs)

        self.options: list[list[int]] = []
        self.option_id: dict = {}
        for center in range(n):
            rows = []
            for combo in combinations(
                [t for t in range(n) if t != center],
                row_size,
            ):
                m = _mask(combo)
                rows.append(m)
                self.option_id[(center, m)] = len(rows) - 1
            self.options.append(rows)

        self.mask_bits = {
            m: _bits(m, n)
            for rows in self.options
            for m in rows
        }
        self.row_pair_indices = {
            m: [self.pair_index[(min(a, b), max(a, b))] for a, b in combinations(self.mask_bits[m], 2)]
            for rows in self.options
            for m in rows
        }
        self.selected_pair_indices = {
            (center, m): [self.pair_index[(min(center, w), max(center, w))] for w in self.mask_bits[m]]
            for center in range(n)
            for m in self.options[center]
        }
        self.strict_edges = self._build_strict_edges()

        # compat_bits[(i, j)][mask_i_local] = bitset over local indices of options[j].
        self.compat_bits: dict = {}
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                table = []
                for mask_i in self.options[i]:
                    bits_i = set(self.mask_bits[mask_i])
                    bs = 0
                    for k, mask_j in enumerate(self.options[j]):
                        common = bits_i & set(self.mask_bits[mask_j])
                        ok = True
                        if len(common) > pair_cap:
                            ok = False
                        elif len(common) == pair_cap:
                            a, b = sorted(common)
                            ok = _chords_cross(i, j, a, b, n)
                        if ok:
                            bs |= 1 << k
                    table.append(bs)
                self.compat_bits[(i, j)] = table

        self.full_options_bs = [
            (1 << len(self.options[c])) - 1 for c in range(n)
        ]

        # Per-center per-mask: column-target list and pair-index list.
        self._per_center_cols: list = []
        self._per_center_pairs: list = []
        for c in range(n):
            cols = []
            pairs = []
            for m in self.options[c]:
                cols.append(self.mask_bits[m])
                pairs.append(self.row_pair_indices[m])
            self._per_center_cols.append(cols)
            self._per_center_pairs.append(pairs)

    def _build_strict_edges(self) -> dict:
        n = self.n
        strict_edges: dict = {}
        for center in range(n):
            for mask in self.options[center]:
                witnesses = sorted(
                    self.mask_bits[mask],
                    key=lambda w: (w - center) % n,
                )
                edges = []
                for outer_start in range(4):
                    for outer_end in range(outer_start + 1, 4):
                        for inner_start in range(4):
                            for inner_end in range(inner_start + 1, 4):
                                if (outer_start, outer_end) == (inner_start, inner_end):
                                    continue
                                contains = (
                                    outer_start <= inner_start
                                    and inner_end <= outer_end
                                    and (outer_start < inner_start or inner_end < outer_end)
                                )
                                if contains:
                                    op = (
                                        min(witnesses[outer_start], witnesses[outer_end]),
                                        max(witnesses[outer_start], witnesses[outer_end]),
                                    )
                                    ip = (
                                        min(witnesses[inner_start], witnesses[inner_end]),
                                        max(witnesses[inner_start], witnesses[inner_end]),
                                    )
                                    edges.append(
                                        (self.pair_index[op], self.pair_index[ip])
                                    )
                strict_edges[(center, mask)] = edges
        return strict_edges

    @property
    def row0_choice_count(self) -> int:
        return len(self.options[0])

    # ----- Symmetry ----------------------------------------------------------

    def _reflect_mask(self, center: int, mask: int) -> int:
        n = self.n
        out = 0
        for w in self.mask_bits[mask]:
            new_w = (-w) % n
            out |= 1 << new_w
        return out

    def row0_canonical_indices(self) -> list:
        """Return local indices of dihedral-orbit canonical row0 masks.

        For center 0, the relevant symmetry is x -> -x mod n.  We return the
        index of the lex-smaller mask in each orbit.
        """
        canonical = []
        seen = set()
        for idx, m in enumerate(self.options[0]):
            if idx in seen:
                continue
            mr = self._reflect_mask(0, m)
            idx_r = self.option_id.get((0, mr), idx)
            chosen = min(idx, idx_r)
            canonical.append(chosen)
            seen.add(idx)
            seen.add(idx_r)
        return sorted(set(canonical))

    # ----- Search -----------------------------------------------------------

    def search_one_row0(
        self,
        row0_local_index: int,
        time_budget: float | None = None,
        node_limit: int | None = None,
    ) -> FastSearchResult:
        n = self.n
        row0_mask = self.options[0][row0_local_index]

        remaining = list(self.full_options_bs)
        remaining[0] = 1 << row0_local_index
        for c in range(1, n):
            remaining[c] &= self.compat_bits[(0, c)][row0_local_index]

        column_counts = [0] * n
        pair_counts = [0] * self.num_pairs
        for w in self.mask_bits[row0_mask]:
            column_counts[w] += 1
        for pidx in self.row_pair_indices[row0_mask]:
            pair_counts[pidx] += 1

        # Incremental vertex-circle state.
        parent = list(range(self.num_pairs))  # union-find parent
        # For each call to "add a center", we may add several union ops.  To
        # undo, save a list of (root_b_old_parent, root_b_index) pairs per
        # frame; on undo, set parent[root_b_index] = its old parent.  Because
        # we union root_a and root_b into root_a (parent[root_b] = root_a),
        # we only ever change parent[root_b].
        # We DO NOT do path compression here, to keep undo trivial.
        graph: dict = defaultdict(list)
        # Each frame lists (a_root, b_root, prev_parent_b, edges_appended).

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x

        # Apply row0 to UF and graph.
        # We use incremental cycle detection: each new edge u_root -> v_root,
        # if u_root can be reached from v_root in the existing graph, there is
        # now a cycle.  This is checked by a small DFS from v_root.
        sel_pairs0 = self.selected_pair_indices[(0, row0_mask)]
        base = sel_pairs0[0]
        for pidx in sel_pairs0[1:]:
            ra = find(base)
            rb = find(pidx)
            if ra != rb:
                if rb < ra:
                    ra, rb = rb, ra
                parent[rb] = ra

        # In-graph reachability check: from src, can we reach tgt?
        def reachable(src, tgt, graph_local):
            if src == tgt:
                return True
            visited = {src}
            stack = [src]
            while stack:
                u = stack.pop()
                for w in graph_local.get(u, ()):
                    rw = find(w)
                    if rw == tgt:
                        return True
                    if rw not in visited:
                        visited.add(rw)
                        stack.append(rw)
            return False

        row0_blocked = False
        row0_block_kind = None
        for outer, inner in self.strict_edges[(0, row0_mask)]:
            ro = find(outer)
            ri = find(inner)
            if ro == ri:
                row0_blocked = True
                row0_block_kind = "row0_self_edge"
                break
            # Cycle check: does adding ro -> ri create a cycle? Yes iff ri can
            # reach ro in the current graph.
            if reachable(ri, ro, graph):
                row0_blocked = True
                row0_block_kind = "row0_strict_cycle"
                break
            graph[ro].append(ri)

        if row0_blocked:
            return FastSearchResult(
                n=n,
                row0_index=row0_local_index,
                row0_mask=row0_mask,
                nodes_visited=0,
                full_assignments=0,
                aborted=False,
                elapsed_seconds=0.0,
                counts={row0_block_kind: 1},
            )

        nodes = 0
        full = 0
        counts: dict = {}
        aborted = False
        start_time = monotonic()
        assigned: dict = {0: row0_local_index}
        compat = self.compat_bits

        check_interval = 1024  # check time every N nodes

        # Reusable scratch for cycle detection, flat-list version.
        # Node ids range over [0, num_pairs).  We'll use a "version" stamp to
        # avoid clearing visited/in_stack arrays each call.
        cycle_visited = [0] * self.num_pairs
        cycle_instack = [0] * self.num_pairs
        cycle_version = [0]
        graph_local = graph

        def has_cycle_iter():
            cycle_version[0] += 1
            ver = cycle_version[0]
            stack = []
            # Iterate over keys whose lists are non-empty.
            for start in graph_local:
                if not graph_local[start]:
                    continue
                if cycle_visited[start] == ver:
                    continue
                # iterative DFS with explicit recursion stack.
                stack.append((start, 0))
                cycle_visited[start] = ver
                cycle_instack[start] = ver
                while stack:
                    u, idx = stack[-1]
                    neigh = graph_local.get(u)
                    if neigh is None or idx >= len(neigh):
                        cycle_instack[u] = 0  # leave instack
                        stack.pop()
                        continue
                    stack[-1] = (u, idx + 1)
                    w = neigh[idx]
                    # Resolve via find().
                    while parent[w] != w:
                        w = parent[w]
                    if cycle_instack[w] == ver:
                        # cycle detected; clean up instack
                        for u2, _ in stack:
                            cycle_instack[u2] = 0
                        return True
                    if cycle_visited[w] != ver:
                        cycle_visited[w] = ver
                        cycle_instack[w] = ver
                        stack.append((w, 0))
            return False

        def search() -> None:
            nonlocal nodes, full, aborted
            if aborted:
                return
            nodes += 1
            if node_limit is not None and nodes >= node_limit:
                aborted = True
                return
            if (nodes & (check_interval - 1)) == 0 and time_budget is not None:
                if (monotonic() - start_time) >= time_budget:
                    aborted = True
                    return

            if len(assigned) == n:
                full += 1
                counts["full_survivor"] = counts.get("full_survivor", 0) + 1
                return

            # Choose center with min remaining options (using popcount).
            best_c = -1
            best_bs = 0
            best_count = 1 << 30
            for c in range(n):
                if c in assigned:
                    continue
                bs = remaining[c]
                if bs == 0:
                    return
                cnt = bs.bit_count()
                if cnt < best_count:
                    best_count = cnt
                    best_c = c
                    best_bs = bs
                    if cnt == 1:
                        break

            c = best_c
            bs = best_bs
            cols = self._per_center_cols[c]
            pairs = self._per_center_pairs[c]

            while bs:
                low_bit = bs & -bs
                k = low_bit.bit_length() - 1
                bs ^= low_bit
                m = self.options[c][k]

                col_targets = cols[k]
                ok = True
                for t in col_targets:
                    if column_counts[t] >= self.max_indegree:
                        ok = False
                        break
                if not ok:
                    continue
                pair_idxs = pairs[k]
                for pidx in pair_idxs:
                    if pair_counts[pidx] >= self.pair_cap:
                        ok = False
                        break
                if not ok:
                    continue

                # --- Apply assignment incrementally ---
                assigned[c] = k

                # Save remaining for undo (cheap: list copy).
                old_remaining = remaining[:]
                remaining[c] = 0
                ok2 = True
                for cc in range(n):
                    if cc in assigned:
                        continue
                    remaining[cc] &= compat[(c, cc)][k]
                    if remaining[cc] == 0:
                        ok2 = False
                        # We could break early but still need to apply VC state
                        # to test; actually we don't.  Just skip the recursion.
                        break

                if not ok2:
                    # Restore remaining and undo assignment.
                    for cc in range(n):
                        remaining[cc] = old_remaining[cc]
                    del assigned[c]
                    continue

                # Update column / pair counts.
                for t in col_targets:
                    column_counts[t] += 1
                for pidx in pair_idxs:
                    pair_counts[pidx] += 1

                # Update UF and graph incrementally.
                sel_pairs = self.selected_pair_indices[(c, m)]
                base_p = sel_pairs[0]
                undo_unions: list = []
                for pidx in sel_pairs[1:]:
                    ra = find(base_p)
                    rb = find(pidx)
                    if ra != rb:
                        if rb < ra:
                            ra, rb = rb, ra
                        undo_unions.append((rb, parent[rb]))
                        parent[rb] = ra

                # Apply edges, checking for self-edge.
                hit_self_edge = False
                undo_graph: list = []
                for outer, inner in self.strict_edges[(c, m)]:
                    ro = find(outer)
                    ri = find(inner)
                    if ro == ri:
                        hit_self_edge = True
                        break
                    graph[ro].append(ri)
                    undo_graph.append(ro)

                if hit_self_edge:
                    counts["partial_self_edge"] = counts.get("partial_self_edge", 0) + 1
                    # Undo.
                    for ro in undo_graph:
                        graph[ro].pop()
                    for rb, prev in undo_unions:
                        parent[rb] = prev
                    for pidx in pair_idxs:
                        pair_counts[pidx] -= 1
                    for t in col_targets:
                        column_counts[t] -= 1
                    for cc in range(n):
                        remaining[cc] = old_remaining[cc]
                    del assigned[c]
                    continue

                # Cycle check using DFS.
                if has_cycle_iter():
                    counts["partial_strict_cycle"] = counts.get("partial_strict_cycle", 0) + 1
                else:
                    search()

                # Undo.
                for ro in undo_graph:
                    graph[ro].pop()
                for rb, prev in undo_unions:
                    parent[rb] = prev
                for pidx in pair_idxs:
                    pair_counts[pidx] -= 1
                for t in col_targets:
                    column_counts[t] -= 1
                for cc in range(n):
                    remaining[cc] = old_remaining[cc]
                del assigned[c]

                if aborted:
                    return

        search()
        elapsed = monotonic() - start_time
        return FastSearchResult(
            n=n,
            row0_index=row0_local_index,
            row0_mask=row0_mask,
            nodes_visited=nodes,
            full_assignments=full,
            aborted=aborted,
            elapsed_seconds=elapsed,
            counts=counts,
        )
