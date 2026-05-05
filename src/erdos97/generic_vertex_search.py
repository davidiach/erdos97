"""Generic selected-witness search with vertex-circle pruning.

This is a clean, parameterized version of the finite-case search used by the
review-pending n=9 and n=10 vertex-circle artifacts. It is meant for audit
regressions and slice reruns, not as a new global proof route.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from time import monotonic

Pair = tuple[int, int]
RowMask = int
Assignment = dict[int, int]


@dataclass(frozen=True)
class SearchResult:
    """Deterministic counts for one row0 slice of the generic search."""

    n: int
    row_size: int
    row0_choices: int
    row0_start: int
    row0_end: int
    vertex_circle_pruning: bool
    nodes_visited: int
    full_assignments: int
    aborted: bool
    counts: dict[str, int]
    elapsed_seconds: float | None = None

    def to_json(self, include_elapsed: bool = False) -> dict[str, object]:
        row: dict[str, object] = {
            "N": self.n,
            "M": self.row0_choices,
            "row0_start": self.row0_start,
            "row0_end": self.row0_end,
            "vertex_circle_pruning": self.vertex_circle_pruning,
            "nodes": self.nodes_visited,
            "full": self.full_assignments,
            "aborted": self.aborted,
            "counts": dict(sorted(self.counts.items())),
        }
        if include_elapsed and self.elapsed_seconds is not None:
            row["elapsed"] = self.elapsed_seconds
        return row


class UnionFind:
    """Small deterministic union-find over pair indices."""

    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, a: int, b: int) -> None:
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return
        if root_b < root_a:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a


class GenericVertexSearch:
    """Exact selected-witness search in the natural cyclic order."""

    def __init__(self, n: int, row_size: int = 4, pair_cap: int = 2) -> None:
        if n < row_size + 1:
            raise ValueError("n must be at least row_size + 1")
        if row_size != 4:
            raise ValueError("only row_size=4 is currently supported")
        self.n = n
        self.row_size = row_size
        self.pair_cap = pair_cap
        self.max_indegree = (pair_cap * (n - 1)) // (row_size - 1)
        self.pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        self.pair_index = {pair: idx for idx, pair in enumerate(self.pairs)}
        self.options = self._build_options()
        self.mask_bits = {mask: self._bits(mask) for rows in self.options for mask in rows}
        self.row_pair_indices = {
            mask: [
                self._pair_index(a, b)
                for a, b in combinations(self.mask_bits[mask], 2)
            ]
            for rows in self.options
            for mask in rows
        }
        self.selected_pair_indices = {
            (center, mask): [
                self._pair_index(center, witness)
                for witness in self.mask_bits[mask]
            ]
            for center in range(n)
            for mask in self.options[center]
        }
        self.strict_edges = self._build_strict_edges()
        self.compatible = self._build_compatibility()

    @property
    def row0_choice_count(self) -> int:
        return len(self.options[0])

    def exhaustive_search(
        self,
        *,
        row0_start: int = 0,
        row0_end: int | None = None,
        use_vertex_circle: bool = True,
        node_limit: int | None = None,
    ) -> SearchResult:
        """Run the deterministic search on a row0 slice."""
        if row0_end is None:
            row0_end = self.row0_choice_count
        if not 0 <= row0_start <= row0_end <= self.row0_choice_count:
            raise ValueError("invalid row0 slice")
        if node_limit is not None and node_limit <= 0:
            raise ValueError("node_limit must be positive")

        nodes = 0
        full = 0
        aborted = False
        counts: Counter[str] = Counter()
        start_time = monotonic()

        def search(
            assign: Assignment,
            column_counts: list[int],
            witness_pair_counts: list[int],
        ) -> None:
            nonlocal aborted
            nonlocal full
            nonlocal nodes
            if aborted:
                return
            nodes += 1
            if node_limit is not None and nodes >= node_limit:
                aborted = True
                return
            if len(assign) == self.n:
                full += 1
                if use_vertex_circle:
                    counts["full_survivor"] += 1
                else:
                    counts[self.vertex_circle_status(assign)] += 1
                return

            best_center = None
            best_options = None
            for center in range(self.n):
                if center in assign:
                    continue
                opts = self.valid_options_for_center(
                    center,
                    assign,
                    column_counts,
                    witness_pair_counts,
                )
                if best_options is None or len(opts) < len(best_options):
                    best_center = center
                    best_options = opts
                    if not opts:
                        break
            if not best_options:
                return

            center = best_center
            assert center is not None
            for mask in best_options:
                assign[center] = mask
                for target in self.mask_bits[mask]:
                    column_counts[target] += 1
                for pidx in self.row_pair_indices[mask]:
                    witness_pair_counts[pidx] += 1

                status = self.vertex_circle_status(assign) if use_vertex_circle else "ok"
                if status == "ok":
                    search(assign, column_counts, witness_pair_counts)
                else:
                    counts[f"partial_{status}"] += 1

                for pidx in self.row_pair_indices[mask]:
                    witness_pair_counts[pidx] -= 1
                for target in self.mask_bits[mask]:
                    column_counts[target] -= 1
                del assign[center]
                if aborted:
                    return

        for row0_index in range(row0_start, row0_end):
            row0 = self.options[0][row0_index]
            assign = {0: row0}
            column_counts = [0] * self.n
            witness_pair_counts = [0] * len(self.pairs)
            for target in self.mask_bits[row0]:
                column_counts[target] += 1
            for pidx in self.row_pair_indices[row0]:
                witness_pair_counts[pidx] += 1
            status = self.vertex_circle_status(assign)
            if status == "ok":
                search(assign, column_counts, witness_pair_counts)
            else:
                counts[f"row0_{status}"] += 1
            if aborted:
                break

        return SearchResult(
            n=self.n,
            row_size=self.row_size,
            row0_choices=self.row0_choice_count,
            row0_start=row0_start,
            row0_end=row0_end,
            vertex_circle_pruning=use_vertex_circle,
            nodes_visited=nodes,
            full_assignments=full,
            aborted=aborted,
            counts=dict(counts),
            elapsed_seconds=monotonic() - start_time,
        )

    def vertex_circle_status(self, assign: Assignment) -> str:
        """Return ``ok``, ``self_edge``, or ``strict_cycle`` for assigned rows."""
        uf = UnionFind(len(self.pairs))
        for center, mask in assign.items():
            selected_pairs = self.selected_pair_indices[(center, mask)]
            base = selected_pairs[0]
            for pidx in selected_pairs[1:]:
                uf.union(base, pidx)

        graph: dict[int, list[int]] = defaultdict(list)
        for center, mask in assign.items():
            for outer, inner in self.strict_edges[(center, mask)]:
                outer_root = uf.find(outer)
                inner_root = uf.find(inner)
                if outer_root == inner_root:
                    return "self_edge"
                graph[outer_root].append(inner_root)

        color: dict[int, int] = {}

        def dfs(node: int) -> bool:
            color[node] = 1
            for nxt in graph.get(node, []):
                state = color.get(nxt, 0)
                if state == 1:
                    return True
                if state == 0 and dfs(nxt):
                    return True
            color[node] = 2
            return False

        for node in list(graph):
            if color.get(node, 0) == 0 and dfs(node):
                return "strict_cycle"
        return "ok"

    def valid_options_for_center(
        self,
        center: int,
        assign: Assignment,
        column_counts: list[int],
        witness_pair_counts: list[int],
    ) -> list[int]:
        """Return row masks compatible with the partial assignment."""
        out: list[int] = []
        for mask in self.options[center]:
            if not all(
                self.rows_compatible(center, mask, other, other_mask)
                for other, other_mask in assign.items()
            ):
                continue
            if any(
                column_counts[target] >= self.max_indegree
                for target in self.mask_bits[mask]
            ):
                continue
            if any(
                witness_pair_counts[pidx] >= self.pair_cap
                for pidx in self.row_pair_indices[mask]
            ):
                continue
            out.append(mask)
        return out

    def rows_compatible(self, i: int, mask_i: int, j: int, mask_j: int) -> bool:
        """Return whether two rows satisfy the pairwise exact filters."""
        if i < j:
            return mask_j in self.compatible[(i, j)][mask_i]
        return mask_i in self.compatible[(j, i)][mask_j]

    def _build_options(self) -> list[list[int]]:
        options: list[list[int]] = []
        for center in range(self.n):
            rows: list[int] = []
            for combo in combinations(
                [target for target in range(self.n) if target != center],
                self.row_size,
            ):
                rows.append(self._mask(combo))
            options.append(rows)
        return options

    def _build_strict_edges(self) -> dict[tuple[int, int], list[tuple[int, int]]]:
        strict_edges: dict[tuple[int, int], list[tuple[int, int]]] = {}
        for center in range(self.n):
            for mask in self.options[center]:
                witnesses = sorted(
                    self.mask_bits[mask],
                    key=lambda witness: (witness - center) % self.n,
                )
                edges: list[tuple[int, int]] = []
                for outer_start in range(4):
                    for outer_end in range(outer_start + 1, 4):
                        for inner_start in range(4):
                            for inner_end in range(inner_start + 1, 4):
                                if (outer_start, outer_end) == (inner_start, inner_end):
                                    continue
                                contains = (
                                    outer_start <= inner_start
                                    and inner_end <= outer_end
                                    and (
                                        outer_start < inner_start
                                        or inner_end < outer_end
                                    )
                                )
                                if contains:
                                    outer = self._pair_index(
                                        witnesses[outer_start],
                                        witnesses[outer_end],
                                    )
                                    inner = self._pair_index(
                                        witnesses[inner_start],
                                        witnesses[inner_end],
                                    )
                                    edges.append((outer, inner))
                strict_edges[(center, mask)] = edges
        return strict_edges

    def _build_compatibility(self) -> dict[tuple[int, int], dict[int, set[int]]]:
        compatible: dict[tuple[int, int], dict[int, set[int]]] = {}
        for i in range(self.n):
            for j in range(i + 1, self.n):
                source = (i, j)
                table: dict[int, set[int]] = {}
                for mask_i in self.options[i]:
                    allowed: set[int] = set()
                    row_i = set(self.mask_bits[mask_i])
                    for mask_j in self.options[j]:
                        common = row_i & set(self.mask_bits[mask_j])
                        ok = True
                        if len(common) > self.pair_cap:
                            ok = False
                        elif len(common) == self.pair_cap:
                            target = tuple(sorted(common))
                            ok = self._chords_cross(source, (target[0], target[1]))
                        if ok:
                            allowed.add(mask_j)
                    table[mask_i] = allowed
                compatible[(i, j)] = table
        return compatible

    def _mask(self, values: tuple[int, ...]) -> int:
        out = 0
        for value in values:
            out |= 1 << value
        return out

    def _bits(self, mask: int) -> list[int]:
        return [idx for idx in range(self.n) if (mask >> idx) & 1]

    def _pair_index(self, a: int, b: int) -> int:
        if a == b:
            raise ValueError("loop pair")
        if b < a:
            a, b = b, a
        return self.pair_index[(a, b)]

    def _in_open_arc(self, a: int, b: int, x: int) -> bool:
        return ((x - a) % self.n) < ((b - a) % self.n) and x != a and x != b

    def _chords_cross(self, chord1: Pair, chord2: Pair) -> bool:
        a, b = chord1
        c, d = chord2
        if len({a, b, c, d}) < 4:
            return False
        return self._in_open_arc(a, b, c) != self._in_open_arc(a, b, d)
