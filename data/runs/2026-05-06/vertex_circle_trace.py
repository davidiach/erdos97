"""Trace the vertex-circle obstruction on the 2 non-ear circulant patterns.

For each pattern, output:
- The merged UF classes (chord-length equivalence classes).
- The directed strict-cycle graph after UF quotient.
- The actual cycle (cause of strict_cycle status).

Goal: find an obstruction structure that is *combinatorially* tied to the
K_4-bicycle stuck cores.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from itertools import combinations

REPO = "/home/user/erdos97"
sys.path.insert(0, os.path.join(REPO, "src"))

from erdos97.n9_vertex_circle_exhaustive import (
    N, PAIRS, PAIR_INDEX, MASK_BITS, SELECTED_PAIR_INDICES, STRICT_EDGES,
    UnionFind, OPTIONS, ROW_PAIR_INDICES, mask, vertex_circle_status,
)

PAT_81 = [[1, 3, 6, 7], [2, 4, 7, 8], [0, 3, 5, 8], [0, 1, 4, 6],
          [1, 2, 5, 7], [2, 3, 6, 8], [0, 3, 4, 7], [1, 4, 5, 8], [0, 2, 5, 6]]
PAT_151 = [[2, 3, 6, 8], [0, 3, 4, 7], [1, 4, 5, 8], [0, 2, 5, 6],
           [1, 3, 6, 7], [2, 4, 7, 8], [0, 3, 5, 8], [0, 1, 4, 6], [1, 2, 5, 7]]


def rows_to_mask_assignment(rows):
    return {c: mask(rows[c]) for c in range(N)}


def trace_vertex_circle(rows, name):
    print(f"\n--- {name} ---")
    assign = rows_to_mask_assignment(rows)
    print(f"vertex_circle_status: {vertex_circle_status(assign)}")

    uf = UnionFind(len(PAIRS))
    for center, m in assign.items():
        sp = SELECTED_PAIR_INDICES[(center, m)]
        for pidx in sp[1:]:
            uf.union(sp[0], pidx)

    classes = defaultdict(list)
    for pidx, p in enumerate(PAIRS):
        classes[uf.find(pidx)].append(p)
    classes = dict(sorted(classes.items()))
    print(f"\nUF chord-length classes (size > 1):")
    big = [(root, members) for root, members in classes.items() if len(members) > 1]
    for root, mems in big[:10]:
        print(f"  class root={root}, size={len(mems)}: {mems}")

    print(f"\nDirected strict-edge graph after UF quotient:")
    graph = defaultdict(set)
    for center, m in assign.items():
        for outer, inner in STRICT_EDGES[(center, m)]:
            o, i = uf.find(outer), uf.find(inner)
            if o == i:
                print(f"  SELF-EDGE detected at center={center}: outer={PAIRS[outer]} inner={PAIRS[inner]} merged")
                continue
            graph[o].add(i)

    # Find cycle
    def find_cycle(graph):
        color = {}
        path = []

        def dfs(node):
            color[node] = 1
            path.append(node)
            for nxt in graph.get(node, []):
                if color.get(nxt, 0) == 1:
                    # cycle from path
                    idx = path.index(nxt)
                    return path[idx:]
                if color.get(nxt, 0) == 0:
                    res = dfs(nxt)
                    if res:
                        return res
            color[node] = 2
            path.pop()
            return None

        for n in list(graph):
            if color.get(n, 0) == 0:
                res = dfs(n)
                if res:
                    return res
        return None

    cyc = find_cycle(graph)
    if cyc:
        print(f"  Strict-cycle found, length={len(cyc)}, members (root indices):")
        for root in cyc:
            members = classes[root]
            print(f"    root={root}, chord-length-class: {members}")
    else:
        print(f"  No strict-cycle found.")


def main():
    print("Vertex-circle obstruction trace")
    print("=" * 70)
    trace_vertex_circle(PAT_81, "idx=81 offsets {+1,+3,-2,-3}")
    trace_vertex_circle(PAT_151, "idx=151 offsets {+2,+3,-1,-3}")


if __name__ == "__main__":
    main()
