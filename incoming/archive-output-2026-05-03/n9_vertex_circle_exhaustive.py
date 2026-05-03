#!/usr/bin/env python3
"""Exact finite search for n=9 Erdős-97 selected-witness systems.

This is a standalone verifier for the report.  It labels the vertices of a
strictly convex 9-gon by their cyclic boundary order 0,1,...,8 and enumerates
all ways to choose four selected equidistant witnesses S_i for every center i.
It prunes only by exact necessary conditions:

  1. two selected witness sets share at most two vertices;
  2. if S_i and S_j share exactly two vertices x,y, then chords ij and xy
     must cross in the cyclic order;
  3. any witness-pair {x,y} can occur in at most two rows; consequently any
     target vertex can have selected indegree at most floor(2*(9-1)/(4-1)) = 5;
  4. vertex-circle strict chord monotonicity: nested witness intervals around
     a center imply strict inequalities between witness-witness distances; a
     self-edge or directed cycle among distance classes is impossible.

No floating point arithmetic is used.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from time import perf_counter

N = 9
ROW_SIZE = 4
PAIR_CAP = 2
MAX_INDEGREE = (PAIR_CAP * (N - 1)) // (ROW_SIZE - 1)
ORDER = tuple(range(N))


def pair(a: int, b: int) -> tuple[int, int]:
    if a == b:
        raise ValueError("loop pair")
    return (a, b) if a < b else (b, a)


def mask(values) -> int:
    out = 0
    for value in values:
        out |= 1 << value
    return out


def bits(m: int) -> list[int]:
    return [idx for idx in range(N) if (m >> idx) & 1]


def in_open_arc(a: int, b: int, x: int) -> bool:
    """Return whether x lies strictly on the cyclic arc a -> b."""
    return ((x - a) % N) < ((b - a) % N) and x != a and x != b


def chords_cross(chord1: tuple[int, int], chord2: tuple[int, int]) -> bool:
    """Strict crossing of two chords in the cyclic order 0,1,...,N-1."""
    a, b = chord1
    c, d = chord2
    if len({a, b, c, d}) < 4:
        return False
    return in_open_arc(a, b, c) != in_open_arc(a, b, d)


PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]
PAIR_INDEX = {p: idx for idx, p in enumerate(PAIRS)}

OPTIONS: list[list[int]] = []
for center in range(N):
    OPTIONS.append([
        mask(combo)
        for combo in combinations([target for target in range(N) if target != center], ROW_SIZE)
    ])

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

# For each possible row, precompute all strict inequalities between
# witness-witness distance pairs forced by nested intervals on the circle
# centered at that row's center.
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

# Pairwise compatibility of two selected rows under the circle-intersection and
# crossing-bisector necessary conditions.
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
    if i < j:
        return mj in COMPATIBLE[(i, j)][mi]
    return mi in COMPATIBLE[(j, i)][mj]


class UnionFind:
    def __init__(self, size: int):
        self.parent = list(range(size))

    def find(self, item: int) -> int:
        parent = self.parent
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(self, a: int, b: int) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return
        if rb < ra:
            ra, rb = rb, ra
        self.parent[rb] = ra


def vertex_circle_status(assign: dict[int, int]) -> str:
    """Return 'ok', 'self_edge', or 'strict_cycle' for assigned rows."""
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
    assign: dict[int, int],
    column_counts: list[int],
    witness_pair_counts: list[int],
) -> list[int]:
    out: list[int] = []
    for m in OPTIONS[center]:
        if not all(rows_compatible(center, m, other, other_m) for other, other_m in assign.items()):
            continue
        if any(column_counts[target] >= MAX_INDEGREE for target in MASK_BITS[m]):
            continue
        if any(witness_pair_counts[pidx] >= PAIR_CAP for pidx in ROW_PAIR_INDICES[m]):
            continue
        out.append(m)
    return out


def exhaustive_search(use_vertex_circle: bool = True) -> tuple[int, int, Counter]:
    nodes = 0
    full = 0
    counts: Counter[str] = Counter()

    def search(assign: dict[int, int], column_counts: list[int], witness_pair_counts: list[int]) -> None:
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
            opts = valid_options_for_center(center, assign, column_counts, witness_pair_counts)
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
    return nodes, full, counts


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cross-check",
        action="store_true",
        help="enumerate without vertex-circle pruning, then classify the full assignments by the vertex-circle filter",
    )
    args = parser.parse_args()

    if args.cross_check:
        start = perf_counter()
        raw_nodes, raw_full, raw_counts = exhaustive_search(use_vertex_circle=False)
        raw_elapsed = perf_counter() - start
        print("n=9 cross-check without vertex-circle pruning")
        print(f"row0 choices: {len(OPTIONS[0])}")
        print(f"nodes visited: {raw_nodes}")
        print(f"full assignments passing pair/crossing/count filters: {raw_full}")
        print(f"vertex-circle status of those full assignments: {dict(raw_counts)}")
        print(f"elapsed_seconds: {raw_elapsed:.6f}")
        return 0

    start = perf_counter()
    nodes, full, counts = exhaustive_search(use_vertex_circle=True)
    elapsed = perf_counter() - start
    print("n=9 exhaustive selected-witness search with vertex-circle pruning")
    print(f"row0 choices: {len(OPTIONS[0])}")
    print(f"nodes visited: {nodes}")
    print(f"full assignments surviving all filters: {full}")
    print(f"prune counts: {dict(counts)}")
    print(f"elapsed_seconds: {elapsed:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
