"""Exact exhaustive n=9 selected-witness search with vertex-circle pruning.

This module records a review-pending finite-case checker for Erdos Problem #97.
It does not prove the full problem and does not claim a counterexample.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations

N = 9
ROW_SIZE = 4
PAIR_CAP = 2
MAX_INDEGREE = (PAIR_CAP * (N - 1)) // (ROW_SIZE - 1)
ORDER = tuple(range(N))

Pair = tuple[int, int]
RowMask = int
Assignment = dict[int, RowMask]

EXPECTED_MAIN_NODES = 16_752
EXPECTED_MAIN_FULL = 0
EXPECTED_MAIN_PRUNES = {
    "partial_self_edge": 11_271,
    "partial_strict_cycle": 11_011,
}
EXPECTED_CROSS_CHECK_NODES = 100_817
EXPECTED_CROSS_CHECK_FULL = 184
EXPECTED_CROSS_CHECK_STATUSES = {
    "self_edge": 158,
    "strict_cycle": 26,
}


@dataclass(frozen=True)
class SearchResult:
    """Deterministic search counts for one n=9 exhaustive run."""

    vertex_circle_pruning: bool
    row0_choices: int
    nodes_visited: int
    full_assignments: int
    counts: dict[str, int]

    def to_json(self) -> dict[str, object]:
        return {
            "vertex_circle_pruning": self.vertex_circle_pruning,
            "row0_choices": self.row0_choices,
            "nodes_visited": self.nodes_visited,
            "full_assignments": self.full_assignments,
            "counts": dict(sorted(self.counts.items())),
        }


def pair(a: int, b: int) -> Pair:
    """Return a normalized unordered pair and reject loops."""
    if a == b:
        raise ValueError("loop pair")
    return (a, b) if a < b else (b, a)


def mask(values: tuple[int, ...] | list[int]) -> int:
    """Return the bit mask for a sequence of labels."""
    out = 0
    for value in values:
        out |= 1 << value
    return out


def bits(m: int) -> list[int]:
    """Return sorted labels present in ``m``."""
    return [idx for idx in range(N) if (m >> idx) & 1]


def in_open_arc(a: int, b: int, x: int) -> bool:
    """Return whether x lies strictly on the cyclic arc a -> b."""
    return ((x - a) % N) < ((b - a) % N) and x != a and x != b


def chords_cross(chord1: Pair, chord2: Pair) -> bool:
    """Strict crossing of two disjoint chords in the natural cyclic order."""
    a, b = chord1
    c, d = chord2
    if len({a, b, c, d}) < 4:
        return False
    return in_open_arc(a, b, c) != in_open_arc(a, b, d)


PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]
PAIR_INDEX = {p: idx for idx, p in enumerate(PAIRS)}

OPTIONS: list[list[int]] = []
for center in range(N):
    OPTIONS.append(
        [
            mask(combo)
            for combo in combinations(
                [target for target in range(N) if target != center],
                ROW_SIZE,
            )
        ]
    )

MASK_BITS = {m: bits(m) for opts in OPTIONS for m in opts}
ROW_PAIR_INDICES = {
    m: [PAIR_INDEX[pair(a, b)] for a, b in combinations(MASK_BITS[m], 2)]
    for opts in OPTIONS
    for m in opts
}
SELECTED_PAIR_INDICES = {
    (center, m): [PAIR_INDEX[pair(center, witness)] for witness in MASK_BITS[m]]
    for center in range(N)
    for m in OPTIONS[center]
}

STRICT_EDGES: dict[tuple[int, int], list[tuple[int, int]]] = {}
for center in range(N):
    for m in OPTIONS[center]:
        witnesses = sorted(MASK_BITS[m], key=lambda w: (w - center) % N)
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
                            and (outer_start < inner_start or inner_end < outer_end)
                        )
                        if contains:
                            outer = pair(witnesses[outer_start], witnesses[outer_end])
                            inner = pair(witnesses[inner_start], witnesses[inner_end])
                            edges.append((PAIR_INDEX[outer], PAIR_INDEX[inner]))
        STRICT_EDGES[(center, m)] = edges

COMPATIBLE: dict[tuple[int, int], dict[int, set[int]]] = {}
for i in range(N):
    for j in range(i + 1, N):
        source = pair(i, j)
        table: dict[int, set[int]] = {}
        for mi in OPTIONS[i]:
            allowed: set[int] = set()
            row_i = set(MASK_BITS[mi])
            for mj in OPTIONS[j]:
                common = row_i & set(MASK_BITS[mj])
                ok = True
                if len(common) > PAIR_CAP:
                    ok = False
                elif len(common) == PAIR_CAP:
                    target = pair(*tuple(common))
                    ok = chords_cross(source, target)
                if ok:
                    allowed.add(mj)
            table[mi] = allowed
        COMPATIBLE[(i, j)] = table


def rows_compatible(i: int, mi: int, j: int, mj: int) -> bool:
    """Return whether two selected rows satisfy the pairwise exact filters."""
    if i < j:
        return mj in COMPATIBLE[(i, j)][mi]
    return mi in COMPATIBLE[(j, i)][mj]


class UnionFind:
    """Small deterministic union-find over pair indices."""

    def __init__(self, size: int):
        self.parent = list(range(size))

    def find(self, item: int) -> int:
        parent = self.parent
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(self, a: int, b: int) -> None:
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return
        if root_b < root_a:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a


def vertex_circle_status(assign: Assignment) -> str:
    """Return ``ok``, ``self_edge``, or ``strict_cycle`` for assigned rows."""
    uf = UnionFind(len(PAIRS))
    for center, m in assign.items():
        selected_pairs = SELECTED_PAIR_INDICES[(center, m)]
        base = selected_pairs[0]
        for pidx in selected_pairs[1:]:
            uf.union(base, pidx)

    graph: dict[int, list[int]] = defaultdict(list)
    for center, m in assign.items():
        for outer, inner in STRICT_EDGES[(center, m)]:
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
    center: int,
    assign: Assignment,
    column_counts: list[int],
    witness_pair_counts: list[int],
) -> list[int]:
    """Return row masks compatible with the partial assignment."""
    out: list[int] = []
    for m in OPTIONS[center]:
        if not all(
            rows_compatible(center, m, other, other_m)
            for other, other_m in assign.items()
        ):
            continue
        if any(column_counts[target] >= MAX_INDEGREE for target in MASK_BITS[m]):
            continue
        if any(witness_pair_counts[pidx] >= PAIR_CAP for pidx in ROW_PAIR_INDICES[m]):
            continue
        out.append(m)
    return out


def exhaustive_search(use_vertex_circle: bool = True) -> SearchResult:
    """Run the deterministic exhaustive n=9 selected-witness search."""
    nodes = 0
    full = 0
    counts: Counter[str] = Counter()

    def search(
        assign: Assignment,
        column_counts: list[int],
        witness_pair_counts: list[int],
    ) -> None:
        nonlocal nodes, full
        nodes += 1
        if len(assign) == N:
            full += 1
            if use_vertex_circle:
                counts["full_survivor"] += 1
            else:
                counts[vertex_circle_status(assign)] += 1
            return

        best_center = None
        best_options = None
        for center in range(N):
            if center in assign:
                continue
            opts = valid_options_for_center(
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
        for m in best_options:
            assign[center] = m
            for target in MASK_BITS[m]:
                column_counts[target] += 1
            for pidx in ROW_PAIR_INDICES[m]:
                witness_pair_counts[pidx] += 1

            status = vertex_circle_status(assign) if use_vertex_circle else "ok"
            if status == "ok":
                search(assign, column_counts, witness_pair_counts)
            else:
                counts[f"partial_{status}"] += 1

            for pidx in ROW_PAIR_INDICES[m]:
                witness_pair_counts[pidx] -= 1
            for target in MASK_BITS[m]:
                column_counts[target] -= 1
            del assign[center]

    for row0 in OPTIONS[0]:
        assign = {0: row0}
        column_counts = [0] * N
        witness_pair_counts = [0] * len(PAIRS)
        for target in MASK_BITS[row0]:
            column_counts[target] += 1
        for pidx in ROW_PAIR_INDICES[row0]:
            witness_pair_counts[pidx] += 1
        if vertex_circle_status(assign) == "ok":
            search(assign, column_counts, witness_pair_counts)

    return SearchResult(
        vertex_circle_pruning=use_vertex_circle,
        row0_choices=len(OPTIONS[0]),
        nodes_visited=nodes,
        full_assignments=full,
        counts=dict(counts),
    )


def summary_payload() -> dict[str, object]:
    """Return the stable JSON payload for the n=9 review artifact."""
    main = exhaustive_search(use_vertex_circle=True)
    cross_check = exhaustive_search(use_vertex_circle=False)
    return {
        "type": "n9_vertex_circle_exhaustive_v1",
        "trust": "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This review-pending artifact checks only the n=9 selected-witness finite case.",
            "Public theorem-style use requires independent review of the computer-assisted enumeration.",
        ],
        "n": N,
        "row_size": ROW_SIZE,
        "cyclic_order": list(ORDER),
        "filters": [
            "two selected rows share at most two witnesses",
            "two-overlap source and witness chords cross in the cyclic order",
            "each witness pair occurs in at most two selected rows",
            "selected indegree is at most floor(2*(n-1)/(row_size-1))",
            "vertex-circle nested witness chords create no self-edge or strict cycle after selected-distance quotienting",
        ],
        "main_search": main.to_json(),
        "cross_check_without_vertex_circle_pruning": cross_check.to_json(),
        "conclusion": (
            "No n=9 selected-witness assignment survives these exact necessary "
            "filters in this checker."
        ),
        "scope": (
            "Candidate repo-local machine-checked finite-case extension only; "
            "does not update the official/global falsifiable-open status."
        ),
    }


def assert_expected_counts(payload: dict[str, object] | None = None) -> None:
    """Assert the review artifact still matches the reproduced archive counts."""
    if payload is None:
        payload = summary_payload()
    main = payload["main_search"]
    cross_check = payload["cross_check_without_vertex_circle_pruning"]
    if not isinstance(main, dict) or not isinstance(cross_check, dict):
        raise AssertionError("malformed n=9 vertex-circle payload")
    if main["nodes_visited"] != EXPECTED_MAIN_NODES:
        raise AssertionError(f"unexpected main nodes: {main['nodes_visited']}")
    if main["full_assignments"] != EXPECTED_MAIN_FULL:
        raise AssertionError(f"unexpected main full assignments: {main['full_assignments']}")
    if main["counts"] != EXPECTED_MAIN_PRUNES:
        raise AssertionError(f"unexpected main prune counts: {main['counts']}")
    if cross_check["nodes_visited"] != EXPECTED_CROSS_CHECK_NODES:
        raise AssertionError(f"unexpected cross-check nodes: {cross_check['nodes_visited']}")
    if cross_check["full_assignments"] != EXPECTED_CROSS_CHECK_FULL:
        raise AssertionError(
            f"unexpected cross-check full assignments: {cross_check['full_assignments']}"
        )
    if cross_check["counts"] != EXPECTED_CROSS_CHECK_STATUSES:
        raise AssertionError(f"unexpected cross-check statuses: {cross_check['counts']}")
