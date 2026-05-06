"""Main Bridge Lemma A' attack.

Strategy: try to PROVE that any 'minimally stuck' pattern (one where every
vertex is stuck simultaneously, no peeling possible) must violate either
vertex-circle, perpendicularity, or convex-position constraints.

Concretely, we enumerate FULL-STUCK patterns: 4-regular witness patterns
where the WHOLE vertex set (or every starting subset) is stuck. Bridge Lemma A'
fails iff any such pattern is realizable. Equivalently the pattern has some
'non-peelable terminal' — i.e., reverse-peeling lands in a stuck core.

We then test whether all the surviving combinatorial patterns are killable
by some geometric obstruction.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from itertools import combinations, permutations

REPO = "/home/user/erdos97"
sys.path.insert(0, os.path.join(REPO, "src"))

sys.path.insert(0, os.path.join(REPO, "data/runs/2026-05-06"))

from erdos97.n9_vertex_circle_exhaustive import UnionFind, mask
from bridge_lemma_attack_test import (
    is_ear_orderable, vertex_circle_status_n, rows_to_masks
)


def all_stuck_sets(rows, threshold=3, min_size=4):
    n = len(rows)
    masks = rows_to_masks(rows)
    out = []
    for size in range(min_size, n + 1):
        for sub in combinations(range(n), size):
            sm = sum(1 << v for v in sub)
            if all(bin(masks[c] & sm).count("1") < threshold for c in sub):
                out.append(sub)
    return out


def k4_bicycle_cores(rows):
    n = len(rows)
    masks = rows_to_masks(rows)
    cores = []
    for sub in combinations(range(n), 4):
        sm = sum(1 << v for v in sub)
        if all(bin(masks[c] & sm).count("1") == 2 for c in sub):
            cores.append(sub)
    return cores


# --------------------------------------------------------------------------
# Stuck-set conditions for Bridge Lemma A' to fail
# --------------------------------------------------------------------------
#
# Bridge Lemma A' equivalent statement:
# "Every realizable strictly-convex k=4 counterexample admits a sequence
#  v_1, ..., v_n with each v_k (k>=4) having >=3 of its 4 selected witnesses
#  among {v_1,...,v_{k-1}}."
#
# Reverse phrasing (peeling): for every starting set S = V, there exists a
# sequence of peelings ending at <=3 vertices.
#
# Failure: there's some 4-regular pattern such that EVERY peeling sequence
# from V eventually lands in a stuck terminal subset.
#
# This is equivalent to: there exists some subset S ⊆ V with |S| >= 4 such
# that every v in S has |E_v ∩ S| <= 2, AND S is reachable from V by some
# (or every) reverse-peeling sequence.
#
# CLAIM (combinatorial): if a pattern has no K_4-bicycle stuck core (i.e.
# no size-4 stuck set S where every v has internal_count == 2 in S), then
# it's ear-orderable.
#
# CONJECTURE (strong, possibly false): a pattern is non-ear-orderable iff
# it admits a K_4-bicycle stuck core.

# --------------------------------------------------------------------------
# Test conjecture
# --------------------------------------------------------------------------

def test_k4_bicycle_iff_non_ear():
    """For all known patterns at n=8 and n=9, test if having a K_4-bicycle
    stuck core is equivalent to being non-ear-orderable."""
    print("Testing: non-ear ⟺ has K_4-bicycle stuck core?")

    # n=8
    path = os.path.join(REPO, "data/incidence/n8_reconstructed_15_survivors.json")
    with open(path) as f:
        data = json.load(f)
    n8 = [(s["id"], [[j for j, v in enumerate(r) if v] for r in s["rows"]]) for s in data]
    print("\nn=8 patterns (15):")
    for pid, rows in n8:
        ear = is_ear_orderable(rows)
        cores = k4_bicycle_cores(rows)
        agree = (not ear) == (len(cores) > 0)
        marker = "✓" if agree else "✗"
        print(f"  {marker} id={pid}: ear={ear}, K_4-bicycle cores={len(cores)}")

    # n=9 (need to regenerate)
    print("\nn=9 patterns (regenerate 184):")
    from bridge_lemma_attack import generate_n9_184
    n9 = generate_n9_184()
    n_disagree = 0
    for idx, rows in enumerate(n9):
        ear = is_ear_orderable(rows)
        cores = k4_bicycle_cores(rows)
        if (not ear) != (len(cores) > 0):
            n_disagree += 1
            if n_disagree <= 5:
                print(f"  DISAGREE: idx={idx}, ear={ear}, K_4-bicycle cores={len(cores)}")
    print(f"  Total disagreements at n=9: {n_disagree} / 184")
    if n_disagree == 0:
        print("  *** CONJECTURE HOLDS at n=8 (15) and n=9 (184). ***")


# --------------------------------------------------------------------------
# Try to prove: K_4-bicycle stuck core => geometric obstruction
# --------------------------------------------------------------------------

def attempt_proof_k4_bicycle_implies_obstruction(rows, S):
    """For each K_4-bicycle stuck core S = {a, b, c, d}, the 4 selected rows
    contain 8 internal directed edges = 4 undirected edges = a 4-cycle in
    the induced selected graph on S.

    L4 (perp-bisector vertex bound): no 5 points concyclic with center on a
    perp-bisector chord shared by two centers...

    Geometric necessity: Each row's 4 selected witnesses lie on a circle around
    the center. For the K_4-bicycle, S has only 2 of 4 selected witnesses
    "inside" the core, the other 2 "outside" V\\S.

    For each v in S: outside witnesses = w_v, w'_v ∈ V\\S, with
    ||v - w_v|| = ||v - w'_v|| (= r_v).

    L5 (two-circle cap): each unordered pair {x, y} in V appears as outside
    pair for at most 2 rows in S.

    Total outside-pair incidences = 4 (one pair per row in S since each row
    has exactly 2 outside witnesses) = 4. Number of unordered pairs in V\\S =
    C(n-4, 2). So each outside pair appears ≤ 2 times; with LHS=4, RHS_max =
    2*C(n-4, 2) which is ≥ 4 always (since n ≥ 5 here).

    So L5 alone doesn't kill K_4-bicycles.

    What else can kill them? Concyclic 4-tuples constraint:
    For each v in S, the 4 selected witnesses (2 inside S + 2 outside) are
    concyclic. 4 v's means 4 circles. These 4 circles must intersect in
    constrained ways.

    Specifically: for v_1, v_2 in S adjacent in the 4-cycle (i.e., v_1's
    selected internal witnesses include v_2), we have ||v_1 - v_2|| = r_{v_1},
    and similarly ||v_2 - v_1|| = r_{v_2}, so r_{v_1} = r_{v_2}.

    But the K_4-bicycle has a 4-cycle pattern: v_1 → v_2 → v_3 → v_4 → v_1.
    Each step forces equality of selected radii. So r_{v_1} = r_{v_2} = r_{v_3}
    = r_{v_4}.

    Hence: ALL four centers have the SAME selected radius r. So all 4 outside
    witnesses (each pair (w_v, w'_v) for v in S) lie on circles of equal radius
    r centered at v_1, v_2, v_3, v_4. Each pair of these unit circles can
    intersect in at most 2 points => at most C(4,2)*2 = 12 outside witnesses
    in total, but we only have ~ 8 outside witnesses (4 v's * 2 outside).

    More crucially: for two adjacent centers v_i, v_{i+1} in the 4-cycle,
    the two outside witnesses w_v_i, w'_v_i are on the v_i-circle of radius r,
    and w_v_{i+1}, w'_v_{i+1} are on the v_{i+1}-circle of radius r. Adjacent
    circles intersect in at most 2 points; since v_i and v_{i+1} are at
    distance r (selected radii equal & both selected each other), one intersection
    point is the perpendicular bisector reflection at distance r away from
    midpoint(v_i, v_{i+1}) — this is the radical axis.

    Conclusion: K_4-bicycle => uniform radius r on the 4-cycle => severe
    geometric constraints on outside witnesses.

    This is a START but not yet a closed proof. Need more.
    """
    n = len(rows)
    masks = rows_to_masks(rows)

    # Build directed selected-edge graph in S
    edges = []
    sm = sum(1 << v for v in S)
    for c in S:
        for w in rows[c]:
            if (sm >> w) & 1:
                edges.append((c, w))

    # Each v in S has 2 internal edges out: v -> w means r_v = ||v - w||
    # If both v -> w and w -> v are present, then r_v = ||v - w|| = r_w.
    # Find all forced radius equalities
    edge_set = set(edges)
    radius_pairs = set()
    for c, w in edges:
        if (w, c) in edge_set:
            radius_pairs.add(frozenset({c, w}))

    # Build union-find over centers in S forced to share radius
    parent = {v: v for v in S}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    for fr in radius_pairs:
        a, b = list(fr)
        union(a, b)

    classes = defaultdict(list)
    for v in S:
        classes[find(v)].append(v)
    return {
        "S": S,
        "edges_in_S_directed": edges,
        "bidirectional_radius_pairs": [list(fr) for fr in radius_pairs],
        "radius_classes": list(classes.values()),
    }


def main():
    test_k4_bicycle_iff_non_ear()

    # detail: bidirectional structure of K_4-bicycles
    print()
    print("=" * 70)
    print("K_4-bicycle structure: bidirectional internal edges")
    print("=" * 70)

    PAT_81 = [[1, 3, 6, 7], [2, 4, 7, 8], [0, 3, 5, 8], [0, 1, 4, 6],
              [1, 2, 5, 7], [2, 3, 6, 8], [0, 3, 4, 7], [1, 4, 5, 8], [0, 2, 5, 6]]
    cores = k4_bicycle_cores(PAT_81)
    for S in cores[:3]:
        ana = attempt_proof_k4_bicycle_implies_obstruction(PAT_81, S)
        print(f"  S={ana['S']}: edges={ana['edges_in_S_directed']}")
        print(f"    bidirectional pairs: {ana['bidirectional_radius_pairs']}")
        print(f"    forced radius classes: {ana['radius_classes']}")


if __name__ == "__main__":
    main()
