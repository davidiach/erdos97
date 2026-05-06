"""Stronger incidence filters for selected-witness search at n >= 11.

This module records new partial-assignment filters that are PROVABLY necessary
consequences of the geometric setup of Erdos Problem #97. They are intended to
be combined with the existing pair-cap, two-overlap crossing, witness-pair
indegree cap, column indegree cap, and vertex-circle nested-chord filters in
``src/erdos97/generic_vertex_search.py``.

Each filter here is justified geometrically. None depend on numerics.

Provenance and scope
--------------------
None of the filters here prove the global Erdos Problem #97. They prune the
selected-witness search tree more aggressively. The official/global status of
Problem #97 is unchanged.

Filters implemented
-------------------

F1 (Triple uniqueness, "L6'"):
    Three points in general position determine a unique circumcenter. If three
    distinct labels {a,b,c} all sit in S_i for two distinct centers i and j,
    then both p_i and p_j are circumcenters of the triangle (p_a,p_b,p_c).
    Combined with L2 (no three vertices of a strictly convex polygon are
    collinear), the three points are noncollinear, so the circumcenter is
    unique, forcing p_i = p_j. Contradiction since the polygon vertices are
    distinct.

    Thus: every unordered triple {a,b,c} of distinct labels appears in at most
    ONE selected row S_i.

    Implementation: maintain a triple-count map. A candidate row mask is
    rejected if it would push any triple count above 1.

F2 (Forced-perpendicularity odd cycle):
    By the crossing-bisector lemma (see ``docs/mutual-rhombus-filter.md``),
    whenever ``S_x cap S_y = {a,b}`` holds with two overlaps, the line
    ``p_x p_y`` is the perpendicular bisector of ``p_a p_b``. If we form the
    "forced perpendicularity" graph on chord labels with an undirected edge
    {x,y} -- {a,b} for every two-overlap row pair (in either direction), then a
    valid Euclidean realization 2-colors this graph by horizontal/vertical
    direction up to common rotation.  Hence an odd cycle is a contradiction.

    Implementation: maintain incrementally a 2-coloring (BFS) of the perp
    graph. A candidate mask which would force a new perp edge that breaks the
    2-coloring is rejected.

F3 (Mutual-rhombus rational closure):
    By the mutual-rhombus lemma, whenever {x,y} and {a,b} are mutual ``phi``
    images (i.e. ``phi({x,y}) = {a,b}`` and ``phi({a,b}) = {x,y}``), we have
    p_x + p_y = p_a + p_b. Each such reciprocal pair gives an exact integer
    linear equation on coordinate-axis variables. If the rational nullspace of
    the resulting matrix forces ``X_u = X_v`` for distinct u,v, then any
    realization has p_u = p_v, contradicting strict convexity.

    Implementation: maintain incrementally the integer matrix of mutual-phi
    rows; check via fraction-based row reduction whether any pair of distinct
    coordinate variables is forced equal.

Filter F1 fires often in dense partial assignments at n=11 because the row
size is 4, so binom(4,3)=4 triples per row. Once even ~6 rows are selected,
many candidate triples have been used.

Filter F2 fires when a directed phi cycle forms an odd-length cycle in the
underlying undirected perp graph. This catches a contradiction earlier than
the existing ``odd_forced_perpendicular_cycle`` whole-pattern check.

Filter F3 fires whenever a mutual phi 2-cycle is closed, often when at least
two pairs of rows mutually share two witnesses each.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import combinations
from time import monotonic
from typing import Iterable

Pair = tuple[int, int]
Triple = tuple[int, int, int]
RowMask = int
Assignment = dict[int, int]


def _pair_norm(a: int, b: int) -> Pair:
    if a == b:
        raise ValueError("loop pair")
    return (a, b) if a < b else (b, a)


def _triple_norm(a: int, b: int, c: int) -> Triple:
    triple = sorted((a, b, c))
    if len(set(triple)) != 3:
        raise ValueError("triple has duplicates")
    return (triple[0], triple[1], triple[2])


def _bits(mask: int, n: int) -> list[int]:
    return [i for i in range(n) if (mask >> i) & 1]


def row_triples(witnesses: Iterable[int]) -> list[Triple]:
    """Return sorted triples drawn from the four witnesses of a row."""
    witnesses = sorted(witnesses)
    return [
        _triple_norm(witnesses[a], witnesses[b], witnesses[c])
        for a, b, c in combinations(range(len(witnesses)), 3)
    ]


# --------------------------------------------------------------------------- #
# F1: Triple uniqueness                                                      #
# --------------------------------------------------------------------------- #


def triple_unique_check_mask(
    new_witnesses: Iterable[int], triple_counts: dict[Triple, int]
) -> bool:
    """Return True if adding this row's triples keeps all triple counts <= 1."""
    new_witnesses = list(new_witnesses)
    seen: set[Triple] = set()
    for triple in row_triples(new_witnesses):
        if triple in seen:
            continue
        seen.add(triple)
        if triple_counts.get(triple, 0) >= 1:
            return False
    return True


def add_row_to_triples(
    new_witnesses: Iterable[int], triple_counts: dict[Triple, int]
) -> list[Triple]:
    """Increment triple counts for the row's four 3-subsets and return them."""
    triples = row_triples(new_witnesses)
    for triple in triples:
        triple_counts[triple] = triple_counts.get(triple, 0) + 1
    return triples


def remove_row_from_triples(
    triples: Iterable[Triple], triple_counts: dict[Triple, int]
) -> None:
    """Decrement triple counts after a backtrack."""
    for triple in triples:
        triple_counts[triple] -= 1
        if triple_counts[triple] == 0:
            del triple_counts[triple]


# --------------------------------------------------------------------------- #
# F2: Forced-perpendicularity 2-coloring                                     #
# --------------------------------------------------------------------------- #


@dataclass
class PerpColoring:
    """Incremental BFS 2-coloring of the forced-perpendicularity graph.

    The keys are normalized chord pairs (a,b). After every assignment edit the
    state is reset and rebuilt from scratch since edges may delete during
    backtracking.

    A return value of ``False`` from :py:meth:`try_add_edges` means the new
    edges break 2-colorability (i.e., an odd cycle has formed).
    """

    chords: list[Pair]
    color: dict[Pair, int] = field(default_factory=dict)
    parent: dict[Pair, Pair | None] = field(default_factory=dict)

    def reset(self) -> None:
        self.color.clear()
        self.parent.clear()

    def _bfs_assign(self, start: Pair, edges: dict[Pair, set[Pair]]) -> bool:
        from collections import deque

        self.color[start] = 0
        self.parent[start] = None
        queue: "deque[Pair]" = deque([start])
        while queue:
            u = queue.popleft()
            for v in edges.get(u, ()):
                if v not in self.color:
                    self.color[v] = 1 - self.color[u]
                    self.parent[v] = u
                    queue.append(v)
                elif self.color[v] == self.color[u]:
                    return False
        return True

    def is_bipartite(self, edges: dict[Pair, set[Pair]]) -> bool:
        self.reset()
        for start in sorted(edges):
            if start in self.color:
                continue
            if not self._bfs_assign(start, edges):
                return False
        return True


def perp_edges_from_assignment(
    assign: Assignment, mask_bits: dict[int, list[int]]
) -> dict[Pair, set[Pair]]:
    """Compute the undirected perp graph for a partial assignment.

    For every ordered pair (i, j) of assigned centers with |S_i cap S_j| == 2
    and shared witnesses {a, b}, add the undirected edge ``{i,j} -- {a,b}``.
    Multiple two-overlaps merely confirm the same edge (no multiplicity needed
    for 2-coloring).
    """
    out: dict[Pair, set[Pair]] = defaultdict(set)
    items = list(assign.items())
    for ix in range(len(items)):
        i, mi = items[ix]
        wi = set(mask_bits[mi])
        for jx in range(ix + 1, len(items)):
            j, mj = items[jx]
            inter = wi & set(mask_bits[mj])
            if len(inter) == 2:
                ij = _pair_norm(i, j)
                ab = _pair_norm(*sorted(inter))
                if ij == ab:
                    continue
                out[ij].add(ab)
                out[ab].add(ij)
    return out


def perp_2coloring_ok(
    assign: Assignment, mask_bits: dict[int, list[int]]
) -> bool:
    """Return True if the forced-perp graph for ``assign`` is bipartite."""
    edges = perp_edges_from_assignment(assign, mask_bits)
    if not edges:
        return True
    pc = PerpColoring(chords=sorted(edges))
    return pc.is_bipartite(edges)


def parallel_endpoint_conflict(
    assign: Assignment, mask_bits: dict[int, list[int]]
) -> tuple[Pair, Pair, Pair] | None:
    """Return a triple ``(e, f1, f2)`` exhibiting an F4 endpoint conflict.

    F4 lemma. If the forced-perpendicularity graph contains two edges
    ``e--f1`` and ``e--f2`` such that distinct chords ``f1`` and ``f2`` share
    an endpoint, then both ``f1`` and ``f2`` are perpendicular to ``e``, so
    they are parallel to each other. Two distinct parallel lines cannot share
    a point. As distinct chords with a common endpoint, ``f1`` and ``f2``
    coincide as a line iff their three labeled endpoints are collinear; L2
    forbids that for a strictly convex polygon. Hence ``f1`` and ``f2`` are
    distinct lines through the shared endpoint, so they are not parallel,
    contradicting the perpendicularity to ``e``.

    Returns ``None`` when no conflict is found.

    F4 fires shallower than F2 (which needs an odd cycle = 3 edges in cycle).
    F4 fires as soon as two phi edges incident to the same chord meet at a
    common endpoint of their other ends. This often appears after only a few
    rows have been assigned.
    """
    edges = perp_edges_from_assignment(assign, mask_bits)
    for e, neighbors in edges.items():
        if len(neighbors) < 2:
            continue
        nbrs = list(neighbors)
        for i in range(len(nbrs)):
            f1 = nbrs[i]
            for j in range(i + 1, len(nbrs)):
                f2 = nbrs[j]
                if f1 == f2:
                    continue
                if set(f1) & set(f2):
                    return e, f1, f2
    return None


def parallel_endpoint_ok(
    assign: Assignment, mask_bits: dict[int, list[int]]
) -> bool:
    """Return True iff no F4 parallel-endpoint conflict is detected."""
    return parallel_endpoint_conflict(assign, mask_bits) is None


# --------------------------------------------------------------------------- #
# F3: Mutual-rhombus rational closure                                        #
# --------------------------------------------------------------------------- #


def mutual_phi_rows_from_assignment(
    assign: Assignment, mask_bits: dict[int, list[int]]
) -> list[tuple[int, int, int, int]]:
    """Return label tuples (x, y, a, b) for every mutual-phi reciprocal pair.

    A row is generated when ``phi({x,y}) = {a,b}`` and ``phi({a,b}) = {x,y}``
    for assigned centers. Each unordered pair of pairs is recorded once.
    """
    items = list(assign.items())
    phi: dict[Pair, Pair] = {}
    for ix in range(len(items)):
        i, mi = items[ix]
        wi = set(mask_bits[mi])
        for jx in range(ix + 1, len(items)):
            j, mj = items[jx]
            inter = wi & set(mask_bits[mj])
            if len(inter) == 2:
                pq = tuple(sorted(inter))
                phi[_pair_norm(i, j)] = (pq[0], pq[1])

    seen: set[tuple[Pair, Pair]] = set()
    out: list[tuple[int, int, int, int]] = []
    for chord, image in phi.items():
        if image in phi and phi[image] == chord:
            key = (chord, image) if chord < image else (image, chord)
            if key in seen:
                continue
            seen.add(key)
            x, y = key[0]
            a, b = key[1]
            out.append((x, y, a, b))
    return out


def _row_reduce_to_classes(
    rows: list[list[Fraction]], n: int
) -> list[list[int]]:
    """Compute forced-equal label classes from rational rows.

    Each row encodes ``sum_i c_i * X_i = 0``. We row-reduce using exact
    Fractions to compute a basis of the nullspace, then union-find labels that
    have equal coordinates in every basis vector.
    """
    if not rows:
        return []

    A = [row[:] for row in rows]  # copy
    pivots: list[int] = []
    pivot_cols: dict[int, int] = {}
    r = 0
    for c in range(n):
        # find pivot
        pr = None
        for rr in range(r, len(A)):
            if A[rr][c] != 0:
                pr = rr
                break
        if pr is None:
            continue
        A[r], A[pr] = A[pr], A[r]
        # normalize
        pivot_val = A[r][c]
        A[r] = [x / pivot_val for x in A[r]]
        # eliminate
        for rr in range(len(A)):
            if rr != r and A[rr][c] != 0:
                factor = A[rr][c]
                A[rr] = [x - factor * y for x, y in zip(A[rr], A[r])]
        pivots.append(c)
        pivot_cols[c] = r
        r += 1
        if r == len(A):
            break

    # nullspace basis: for each free variable f, set X_f = 1 and X_other_free = 0,
    # solve for pivots.
    free_cols = [c for c in range(n) if c not in pivot_cols]
    basis: list[list[Fraction]] = []
    for f in free_cols:
        vec = [Fraction(0)] * n
        vec[f] = Fraction(1)
        for pc in pivots:
            row = A[pivot_cols[pc]]
            # X_pc = - sum_{c != pc} row[c] * X_c
            val = Fraction(0)
            for c in range(n):
                if c == pc:
                    continue
                val -= row[c] * vec[c]
            vec[pc] = val
        basis.append(vec)

    # union-find: u ~ v iff vec[u] == vec[v] for all basis vectors
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for u in range(n):
        for v in range(u + 1, n):
            if all(vec[u] == vec[v] for vec in basis):
                union(u, v)

    classes: dict[int, list[int]] = defaultdict(list)
    for label in range(n):
        classes[find(label)].append(label)
    return sorted(cls for cls in classes.values() if len(cls) >= 2)


def mutual_rhombus_forced_collisions(
    assign: Assignment, n: int, mask_bits: dict[int, list[int]]
) -> list[list[int]]:
    """Return non-singleton forced-equal label classes from mutual-phi pairs.

    If any class has size >= 2, the partial assignment is infeasible because it
    would force two distinct strictly-convex-polygon vertices to coincide.
    """
    quartets = mutual_phi_rows_from_assignment(assign, mask_bits)
    if not quartets:
        return []
    rows: list[list[Fraction]] = []
    for x, y, a, b in quartets:
        row = [Fraction(0)] * n
        row[x] += 1
        row[y] += 1
        row[a] -= 1
        row[b] -= 1
        rows.append(row)
    return _row_reduce_to_classes(rows, n)


def mutual_rhombus_ok(
    assign: Assignment, n: int, mask_bits: dict[int, list[int]]
) -> bool:
    """Return True iff no mutual-rhombus forced collision is detected."""
    return not mutual_rhombus_forced_collisions(assign, n, mask_bits)


# --------------------------------------------------------------------------- #
# Combined search driver                                                     #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class StrongerSearchResult:
    """Counts for one row0 slice using the stronger filters."""

    n: int
    row_size: int
    row0_choices: int
    row0_start: int
    row0_end: int
    use_filters: tuple[str, ...]
    nodes_visited: int
    full_assignments: int
    aborted: bool
    counts: dict[str, int]
    elapsed_seconds: float | None = None

    def to_json(self) -> dict[str, object]:
        return {
            "N": self.n,
            "row_size": self.row_size,
            "row0_choices": self.row0_choices,
            "row0_start": self.row0_start,
            "row0_end": self.row0_end,
            "filters": list(self.use_filters),
            "nodes": self.nodes_visited,
            "full": self.full_assignments,
            "aborted": self.aborted,
            "counts": dict(sorted(self.counts.items())),
            "elapsed_seconds": self.elapsed_seconds,
        }


class StrongerVertexSearch:
    """Wrapper around :class:`GenericVertexSearch` that also runs F1/F2/F3."""

    def __init__(self, n: int, row_size: int = 4, pair_cap: int = 2) -> None:
        from erdos97.generic_vertex_search import GenericVertexSearch

        self.gvs = GenericVertexSearch(n=n, row_size=row_size, pair_cap=pair_cap)
        self.n = n
        self.row_size = row_size
        self.pair_cap = pair_cap

    @property
    def row0_choice_count(self) -> int:
        return self.gvs.row0_choice_count

    def exhaustive_search(
        self,
        *,
        row0_start: int = 0,
        row0_end: int | None = None,
        use_vertex_circle: bool = True,
        use_triple_unique: bool = True,
        use_perp_2color: bool = True,
        use_parallel_endpoint: bool = True,
        use_mutual_rhombus: bool = True,
        node_limit: int | None = None,
    ) -> StrongerSearchResult:
        """Exhaustive search with vertex-circle plus the F1/F2/F3/F4 filters."""
        gvs = self.gvs
        if row0_end is None:
            row0_end = gvs.row0_choice_count
        if not 0 <= row0_start <= row0_end <= gvs.row0_choice_count:
            raise ValueError("invalid row0 slice")
        if node_limit is not None and node_limit <= 0:
            raise ValueError("node_limit must be positive")

        nodes = 0
        full = 0
        aborted = False
        counts: Counter[str] = Counter()
        start_time = monotonic()

        triple_counts: dict[Triple, int] = {}

        filter_flags = []
        if use_vertex_circle:
            filter_flags.append("vertex_circle")
        if use_triple_unique:
            filter_flags.append("triple_unique")
        if use_perp_2color:
            filter_flags.append("perp_2color")
        if use_parallel_endpoint:
            filter_flags.append("parallel_endpoint")
        if use_mutual_rhombus:
            filter_flags.append("mutual_rhombus")

        def search(
            assign: Assignment,
            column_counts: list[int],
            witness_pair_counts: list[int],
        ) -> None:
            nonlocal aborted, full, nodes
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
                    counts[gvs.vertex_circle_status(assign)] += 1
                return

            best_center = None
            best_options = None
            for center in range(self.n):
                if center in assign:
                    continue
                opts = gvs.valid_options_for_center(
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
                witnesses = gvs.mask_bits[mask]

                # F1: Triple uniqueness pre-check.
                if use_triple_unique and not triple_unique_check_mask(
                    witnesses, triple_counts
                ):
                    counts["partial_triple_unique"] += 1
                    continue

                assign[center] = mask
                added_triples = (
                    add_row_to_triples(witnesses, triple_counts)
                    if use_triple_unique
                    else []
                )
                for target in witnesses:
                    column_counts[target] += 1
                for pidx in gvs.row_pair_indices[mask]:
                    witness_pair_counts[pidx] += 1

                pruned = False

                if use_vertex_circle:
                    status = gvs.vertex_circle_status(assign)
                    if status != "ok":
                        counts[f"partial_{status}"] += 1
                        pruned = True

                if not pruned and use_perp_2color and not perp_2coloring_ok(
                    assign, gvs.mask_bits
                ):
                    counts["partial_perp_odd_cycle"] += 1
                    pruned = True

                if not pruned and use_parallel_endpoint and not parallel_endpoint_ok(
                    assign, gvs.mask_bits
                ):
                    counts["partial_parallel_endpoint"] += 1
                    pruned = True

                if not pruned and use_mutual_rhombus and not mutual_rhombus_ok(
                    assign, self.n, gvs.mask_bits
                ):
                    counts["partial_mutual_rhombus"] += 1
                    pruned = True

                if not pruned:
                    search(assign, column_counts, witness_pair_counts)

                for pidx in gvs.row_pair_indices[mask]:
                    witness_pair_counts[pidx] -= 1
                for target in witnesses:
                    column_counts[target] -= 1
                if use_triple_unique:
                    remove_row_from_triples(added_triples, triple_counts)
                del assign[center]
                if aborted:
                    return

        for row0_index in range(row0_start, row0_end):
            row0 = gvs.options[0][row0_index]
            assign = {0: row0}
            column_counts = [0] * self.n
            witness_pair_counts = [0] * len(gvs.pairs)
            row0_witnesses = gvs.mask_bits[row0]
            for target in row0_witnesses:
                column_counts[target] += 1
            for pidx in gvs.row_pair_indices[row0]:
                witness_pair_counts[pidx] += 1
            triple_counts.clear()
            if use_triple_unique:
                add_row_to_triples(row0_witnesses, triple_counts)

            ok = True
            if use_vertex_circle:
                status = gvs.vertex_circle_status(assign)
                if status != "ok":
                    counts[f"row0_{status}"] += 1
                    ok = False
            if ok and use_perp_2color and not perp_2coloring_ok(
                assign, gvs.mask_bits
            ):
                counts["row0_perp_odd_cycle"] += 1
                ok = False
            if ok and use_parallel_endpoint and not parallel_endpoint_ok(
                assign, gvs.mask_bits
            ):
                counts["row0_parallel_endpoint"] += 1
                ok = False
            if ok and use_mutual_rhombus and not mutual_rhombus_ok(
                assign, self.n, gvs.mask_bits
            ):
                counts["row0_mutual_rhombus"] += 1
                ok = False

            if ok:
                search(assign, column_counts, witness_pair_counts)
            if aborted:
                break

        return StrongerSearchResult(
            n=self.n,
            row_size=self.row_size,
            row0_choices=gvs.row0_choice_count,
            row0_start=row0_start,
            row0_end=row0_end,
            use_filters=tuple(filter_flags),
            nodes_visited=nodes,
            full_assignments=full,
            aborted=aborted,
            counts=dict(counts),
            elapsed_seconds=monotonic() - start_time,
        )
