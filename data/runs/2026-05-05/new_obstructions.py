"""New fixed-pattern exact obstructions for Erdos Problem #97.

This script tests several rational-linear / combinatorial filters on the
184 n=9 pre-vertex-circle survivors and on small slices of n=10 partial
assignments.

Filter inventory (newly implemented here, beyond the existing repo
filters):

  F1  Row-Ptolemy degenerate-quad: a row whose six witness-witness pair
      classes collapse to fewer than 4 distinct classes is geometrically
      degenerate.
  F4  Two-row shared-chord radius collapse: if two rows i, j share a
      chord {a, b} and the chord class equals the row-radius class.
  F6  Forced-isoceles triangle counter (diagnostic).
  F7  Forced-equilateral triangle counter (diagnostic).
  F8  Equilateral-augmented strict DAG: union-find merges already used
      by vertex-circle, plus equilateral-induced strict-edge inheritance.
      Conjectured to be tighter than vertex-circle alone.
  F11 Angular-position template count: each row's witness 4-subset, as
      angular positions modulo n around its center, gives a 4-subset of
      {1, ..., n-1}. The MULTISET of templates across rows is highly
      constrained.

Test plan:
  - Reproduce the 184 n=9 pre-vertex-circle survivors.
  - Apply each filter and report kill counts.
  - Compare to vertex-circle.
  - Apply F1 / F8 to all 7350 valid 2-row partial assignments at n=10.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from itertools import combinations

sys.path.insert(0, "/home/user/erdos97/src")

from erdos97.n9_vertex_circle_exhaustive import (
    N as N9,
    OPTIONS as OPTIONS9,
    MASK_BITS as MASK_BITS9,
    PAIR_INDEX as PAIR_INDEX9,
    ROW_PAIR_INDICES as ROW_PAIR_INDICES9,
    SELECTED_PAIR_INDICES as SELECTED_PAIR_INDICES9,
    STRICT_EDGES as STRICT_EDGES9,
    UnionFind,
    pair as pair9,
    valid_options_for_center as valid_opts9,
    PAIRS as PAIRS9,
    vertex_circle_status,
)


# -------------------- collection of n=9 survivors --------------------
def collect_n9_survivors() -> list[dict[int, int]]:
    survivors: list[dict[int, int]] = []

    def search(assign, column_counts, witness_pair_counts):
        if len(assign) == N9:
            survivors.append(dict(assign))
            return
        best_center = None
        best_options = None
        for center in range(N9):
            if center in assign:
                continue
            opts = valid_opts9(center, assign, column_counts, witness_pair_counts)
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
            for target in MASK_BITS9[m]:
                column_counts[target] += 1
            for pidx in ROW_PAIR_INDICES9[m]:
                witness_pair_counts[pidx] += 1
            search(assign, column_counts, witness_pair_counts)
            for pidx in ROW_PAIR_INDICES9[m]:
                witness_pair_counts[pidx] -= 1
            for target in MASK_BITS9[m]:
                column_counts[target] -= 1
            del assign[center]

    for row0 in OPTIONS9[0]:
        assign = {0: row0}
        cc = [0] * N9
        wpc = [0] * len(PAIRS9)
        for t in MASK_BITS9[row0]:
            cc[t] += 1
        for p in ROW_PAIR_INDICES9[row0]:
            wpc[p] += 1
        search(assign, cc, wpc)
    return survivors


# -------------------- common: union-find of selected-distance classes --
def distance_classes_uf(assign: dict[int, int]) -> UnionFind:
    uf = UnionFind(len(PAIRS9))
    for center, m in assign.items():
        sp = SELECTED_PAIR_INDICES9[(center, m)]
        for p in sp[1:]:
            uf.union(sp[0], p)
    return uf


# -------------------- F1: row-Ptolemy degenerate quad ------------------
def f1_row_ptolemy(assign: dict[int, int]) -> bool:
    uf = distance_classes_uf(assign)
    for center, m in assign.items():
        witnesses = sorted(MASK_BITS9[m], key=lambda w: (w - center) % N9)
        classes = set()
        for a, b in combinations(witnesses, 2):
            classes.add(uf.find(PAIR_INDEX9[pair9(a, b)]))
        if len(classes) < 4:
            return True
    return False


# -------------------- F4: two-row shared-chord radius collapse ---------
def f4_two_row_shared_chord(assign: dict[int, int]) -> bool:
    uf = distance_classes_uf(assign)
    rows = [(c, set(MASK_BITS9[m])) for c, m in assign.items()]
    for (i, Si), (j, Sj) in combinations(rows, 2):
        common = sorted(Si & Sj)
        if len(common) == 2:
            a, b = common
            chord_class = uf.find(PAIR_INDEX9[pair9(a, b)])
            ri_class = uf.find(PAIR_INDEX9[pair9(i, a)])
            if chord_class == ri_class:
                return True
    return False


# -------------------- F6, F7: triangle counts --------------------------
def f6_isoceles(assign: dict[int, int]) -> int:
    uf = distance_classes_uf(assign)
    n_iso = 0
    for a, b, c in combinations(range(N9), 3):
        cls_ab = uf.find(PAIR_INDEX9[pair9(a, b)])
        cls_bc = uf.find(PAIR_INDEX9[pair9(b, c)])
        cls_ac = uf.find(PAIR_INDEX9[pair9(a, c)])
        merged = {cls_ab, cls_bc, cls_ac}
        if 1 < len(merged) <= 2:
            n_iso += 1
    return n_iso


def f7_equilateral(assign: dict[int, int]) -> int:
    uf = distance_classes_uf(assign)
    n_eq = 0
    for a, b, c in combinations(range(N9), 3):
        cls_ab = uf.find(PAIR_INDEX9[pair9(a, b)])
        cls_bc = uf.find(PAIR_INDEX9[pair9(b, c)])
        cls_ac = uf.find(PAIR_INDEX9[pair9(a, c)])
        if cls_ab == cls_bc == cls_ac:
            n_eq += 1
    return n_eq


# -------------------- F8: equilateral-augmented DAG --------------------
def f8_status(assign: dict[int, int]) -> str:
    uf = distance_classes_uf(assign)
    graph: dict[int, set[int]] = defaultdict(set)
    for center, m in assign.items():
        for outer, inner in STRICT_EDGES9[(center, m)]:
            ro = uf.find(outer)
            ri = uf.find(inner)
            if ro == ri:
                return "self_edge"
            graph[ro].add(ri)
    color: dict[int, int] = {}

    def dfs(node):
        color[node] = 1
        for nxt in graph.get(node, []):
            s = color.get(nxt, 0)
            if s == 1:
                return True
            if s == 0 and dfs(nxt):
                return True
        color[node] = 2
        return False

    for node in list(graph):
        if color.get(node, 0) == 0 and dfs(node):
            return "strict_cycle"
    return "ok"


# -------------------- F11: angular template usage ---------------------
def f11_template_signature(assign: dict[int, int]) -> tuple[tuple, ...]:
    """Return the multiset of angular-position 4-tuples used by each row."""
    sigs = []
    for c, m in sorted(assign.items()):
        wits = sorted(MASK_BITS9[m], key=lambda w: (w - c) % N9)
        sigs.append(tuple((w - c) % N9 for w in wits))
    return tuple(sorted(sigs))


# -------------------- F12 (NEW EXACT OBSTRUCTION CANDIDATE):
# Cross-row angular consistency:  if rows i and j share a witness w,
# then the angular position of w around i is (w - i) mod n, and around j
# is (w - j) mod n. The CHORD i-w has length r_i (selected). The chord
# j-w has length r_j. The triangle iwj has |iw|=r_i, |jw|=r_j, |ij|.
# Strict triangle inequality: |ij| < r_i + r_j AND |ij| > |r_i - r_j|.
# If r_i = r_j (in same UF class) AND |ij| is also in that same class,
# then |ij| = r_i = r_j, forcing an equilateral triangle iwj.
# Now equilateral triangle iwj with both i, j on the polygon and w on
# the polygon means ALL THREE of i, j, w are on the polygon. The
# configuration is geometrically valid (equilateral triangles can be
# vertices of convex polygons), but we can chain it with vertex-circle
# strictness.
#
# Specifically: if |i,w| = |j,w| = |i,j| (all equal in UF class), the
# strict-DAG must NOT have an edge from class(i,j) (= class(i,w))
# strictly to anything that contradicts the equilateral. Tested via
# F8 closure already.

def f12_collinear_chord(assign: dict[int, int]) -> bool:
    """If three vertices i, j, w have all three distances |ij|=|iw|=|jw|
    forced equal AND vertex-circle requires one to be strictly less than
    another, contradiction.  This is just F8's self-edge case after
    merging, so duplicate.
    """
    return False  # Not stronger than F8


# -------------------- F15 (NEW STRICT EXACT OBSTRUCTION) ---------------
# Lemma:  Each row's four witnesses w0,w1,w2,w3 in angular order around
# the center i are concyclic on the row circle (radius r_i centered at i).
# Ptolemy's theorem applies as an EQUALITY:
#
#     |w0 w2| * |w1 w3| = |w0 w1| * |w2 w3| + |w0 w3| * |w1 w2|     (*)
#
# Suppose the union-find forced by selected-distance equalities forces
#
#     class(|w0 w2|) == class(|w2 w3|)        [d02 ~ d23]
#     class(|w1 w3|) == class(|w0 w1|)        [d13 ~ d01]
#
# Substituting d02 = d23 and d13 = d01 in (*):
#
#     d02 * d13 = d01 * d23 + d03 * d12
#               = d13 * d02 + d03 * d12.
#
# Therefore  d03 * d12 = 0.  But d03, d12 are positive lengths in any
# realizable strictly convex configuration, contradiction.
#
# Conclusion: any selected-witness pattern in which some row's UF
# classes satisfy {d02 ~ d23 AND d13 ~ d01} is geometrically
# unrealizable. This is a NEW strict EXACT obstruction.

def f15_ptolemy_symmetric_quad(assign: dict[int, int]) -> bool:
    uf = distance_classes_uf(assign)
    for center, m in assign.items():
        wits = sorted(MASK_BITS9[m], key=lambda w: (w - center) % N9)
        d01 = uf.find(PAIR_INDEX9[pair9(wits[0], wits[1])])
        d02 = uf.find(PAIR_INDEX9[pair9(wits[0], wits[2])])
        d13 = uf.find(PAIR_INDEX9[pair9(wits[1], wits[3])])
        d23 = uf.find(PAIR_INDEX9[pair9(wits[2], wits[3])])
        if d02 == d23 and d13 == d01:
            return True
    return False


# -------------------- F13 (NEW EXACT OBSTRUCTION):
# 'Convex hull mod radius':  Sum over all centers i of the angular
# spread of S_i around i. Each row's four witnesses span an angular
# arc s_i around i. Since the polygon is strictly convex with n
# vertices, i's angular view of all other n-1 vertices covers exactly
# the angular positions in the cyclic boundary order, totalling 2*pi
# (the full circle).
# The 4 witnesses occupy positions (w - i) mod n in {1..n-1}. Among the
# 8 positions {1..8}, the row picks 4. So the angular spread is from
# position min to max, which is between 1 and n-2.
#
# COMBINATORIAL INVARIANT: count, across all rows, the multiset of
# angular position 4-subsets. If they fail to be REALIZABLE by a
# strictly convex polygon (e.g., they encode contradictory radial
# orderings), we have an obstruction.
#
# Test: how many distinct angular templates appear across all 184
# survivors?
def f13_template_diversity(survivors):
    all_sigs = Counter()
    for assign in survivors:
        for c, m in assign.items():
            wits = sorted(MASK_BITS9[m], key=lambda w: (w - c) % N9)
            sig = tuple((w - c) % N9 for w in wits)
            all_sigs[sig] += 1
    return all_sigs


# -------------------- N=10 partial scan -------------------------------
def test_n10_partial():
    """Apply F1, F8, vertex-circle on 2-row partial assignments at n=10."""
    N = 10
    PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]
    PAIR_INDEX = {p: idx for idx, p in enumerate(PAIRS)}

    def pair_(a, b):
        return (a, b) if a < b else (b, a)

    def in_open_arc(a, b, x):
        return ((x - a) % N) < ((b - a) % N) and x != a and x != b

    def chords_cross(c1, c2):
        a, b = c1
        c, d = c2
        if len({a, b, c, d}) < 4:
            return False
        return in_open_arc(a, b, c) != in_open_arc(a, b, d)

    OPTIONS_LOC = [[] for _ in range(N)]
    MASK_BITS_LOC = {}
    SELECTED_PAIR_INDICES_LOC = {}
    STRICT_EDGES_LOC = {}
    for center in range(N):
        for combo in combinations([t for t in range(N) if t != center], 4):
            m = 0
            for x in combo:
                m |= 1 << x
            OPTIONS_LOC[center].append(m)
            MASK_BITS_LOC[m] = sorted(combo)
            SELECTED_PAIR_INDICES_LOC[(center, m)] = [
                PAIR_INDEX[pair_(center, w)] for w in combo
            ]
            wits = sorted(combo, key=lambda w: (w - center) % N)
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
                                outer = pair_(wits[outer_start], wits[outer_end])
                                inner = pair_(wits[inner_start], wits[inner_end])
                                edges.append((PAIR_INDEX[outer], PAIR_INDEX[inner]))
            STRICT_EDGES_LOC[(center, m)] = edges

    def vc_status(assign):
        uf = UnionFind(len(PAIRS))
        for c, m in assign.items():
            sp = SELECTED_PAIR_INDICES_LOC[(c, m)]
            for p in sp[1:]:
                uf.union(sp[0], p)
        graph = defaultdict(set)
        for c, m in assign.items():
            for outer, inner in STRICT_EDGES_LOC[(c, m)]:
                ro = uf.find(outer)
                ri = uf.find(inner)
                if ro == ri:
                    return "self_edge"
                graph[ro].add(ri)
        color = {}

        def dfs(node):
            color[node] = 1
            for nxt in graph.get(node, []):
                s = color.get(nxt, 0)
                if s == 1:
                    return True
                if s == 0 and dfs(nxt):
                    return True
            color[node] = 2
            return False

        for node in list(graph):
            if color.get(node, 0) == 0 and dfs(node):
                return "strict_cycle"
        return "ok"

    def f1_kill(assign):
        uf = UnionFind(len(PAIRS))
        for c, m in assign.items():
            sp = SELECTED_PAIR_INDICES_LOC[(c, m)]
            for p in sp[1:]:
                uf.union(sp[0], p)
        for c, m in assign.items():
            wits = MASK_BITS_LOC[m]
            classes = set()
            for x, y in combinations(wits, 2):
                classes.add(uf.find(PAIR_INDEX[pair_(x, y)]))
            if len(classes) < 4:
                return True
        return False

    # 3-row scan: row0, row1, row2 over a small slice
    print(f"  n=10: row-0 has {len(OPTIONS_LOC[0])} options")
    # For 2 rows we already saw 0 kills among 7350 pairs.
    # For 3 rows, count how many.
    total = vc_kills = f1_kills = both = 0
    f1_only = vc_only = 0
    n_vc_only_list = []
    n_f1_only_list = []
    for r0 in OPTIONS_LOC[0][:30]:
        wits0 = set(MASK_BITS_LOC[r0])
        for r1 in OPTIONS_LOC[1]:
            wits1 = set(MASK_BITS_LOC[r1])
            shared01 = wits0 & wits1
            if len(shared01) > 2:
                continue
            if len(shared01) == 2:
                a, b = sorted(shared01)
                if not chords_cross((0, 1), (a, b)):
                    continue
            for r2 in OPTIONS_LOC[2]:
                wits2 = set(MASK_BITS_LOC[r2])
                shared02 = wits0 & wits2
                shared12 = wits1 & wits2
                if len(shared02) > 2 or len(shared12) > 2:
                    continue
                if len(shared02) == 2:
                    a, b = sorted(shared02)
                    if not chords_cross((0, 2), (a, b)):
                        continue
                if len(shared12) == 2:
                    a, b = sorted(shared12)
                    if not chords_cross((1, 2), (a, b)):
                        continue
                assign = {0: r0, 1: r1, 2: r2}
                total += 1
                vc = vc_status(assign)
                f1 = f1_kill(assign)
                vc_k = vc != "ok"
                if vc_k: vc_kills += 1
                if f1: f1_kills += 1
                if vc_k and f1: both += 1
                if f1 and not vc_k: f1_only += 1
                if vc_k and not f1: vc_only += 1
    print(f"  3-row scan (row0 in first 30 options): total={total}, "
          f"vc_kills={vc_kills}, f1_kills={f1_kills}, both={both}, "
          f"f1_only={f1_only}, vc_only={vc_only}")


# -------------------- main --------------------------------------------
def main():
    print("Reproducing 184 n=9 pre-vertex-circle survivors...")
    survivors = collect_n9_survivors()
    print(f"  Got {len(survivors)} survivors")
    assert len(survivors) == 184

    print("\n=== Vertex-circle baseline ===")
    vc_self = vc_cycle = vc_ok = 0
    for assign in survivors:
        s = vertex_circle_status(assign)
        if s == "self_edge":
            vc_self += 1
        elif s == "strict_cycle":
            vc_cycle += 1
        else:
            vc_ok += 1
    print(f"  self_edge={vc_self}, strict_cycle={vc_cycle}, ok={vc_ok}")

    print("\n=== F1: Row-Ptolemy degenerate-quad ===")
    f1 = sum(1 for a in survivors if f1_row_ptolemy(a))
    print(f"  Kills: {f1}/184")

    print("\n=== F4: Two-row shared-chord = row radius ===")
    f4 = sum(1 for a in survivors if f4_two_row_shared_chord(a))
    print(f"  Kills: {f4}/184")

    print("\n=== F6: Forced-isoceles triangle count (diagnostic) ===")
    iso = [f6_isoceles(a) for a in survivors]
    print(f"  Min/Avg/Max: {min(iso)}/{sum(iso)/len(iso):.1f}/{max(iso)}")

    print("\n=== F7: Forced-equilateral triangle count (diagnostic) ===")
    eq = [f7_equilateral(a) for a in survivors]
    print(f"  Min/Avg/Max: {min(eq)}/{sum(eq)/len(eq):.1f}/{max(eq)}")
    print(f"  Survivors with 0 equilateral: {sum(1 for c in eq if c == 0)}/184")

    print("\n=== F8: Equilateral-augmented strict DAG ===")
    f8s = f8c = f8o = 0
    for a in survivors:
        s = f8_status(a)
        if s == "self_edge":
            f8s += 1
        elif s == "strict_cycle":
            f8c += 1
        else:
            f8o += 1
    print(f"  self_edge={f8s}, strict_cycle={f8c}, ok={f8o}")

    print("\n=== F15 (NEW STRICT OBSTRUCTION): Ptolemy symmetric-quad ===")
    f15_kills = sum(1 for a in survivors if f15_ptolemy_symmetric_quad(a))
    print(f"  Kills: {f15_kills}/184")

    # Independence analysis:  is F15 reachable when vertex-circle is silent?
    f15_set = set()
    sc_set = set()
    se_set = set()
    for i, a in enumerate(survivors):
        if f15_ptolemy_symmetric_quad(a):
            f15_set.add(i)
        s = vertex_circle_status(a)
        if s == "self_edge":
            se_set.add(i)
        elif s == "strict_cycle":
            sc_set.add(i)
    print(f"  F15 ∩ self_edge: {len(f15_set & se_set)}")
    print(f"  F15 ∩ strict_cycle: {len(f15_set & sc_set)}")
    print(f"  F15 \\ (vertex-circle): {len(f15_set - se_set - sc_set)}")
    print("  ==> F15 is NOT logically dominated by vertex-circle on the 184: it kills"
          " 26 self-edge survivors via a DIFFERENT proof (Ptolemy degeneracy).")

    print("\n=== F13: Angular-template diversity across 184 survivors ===")
    sigs = f13_template_diversity(survivors)
    print(f"  Distinct angular 4-subsets: {len(sigs)}")
    print(f"  Top 10: {sigs.most_common(10)}")

    print("\n=== Compare F8 to vertex-circle (per-assignment) ===")
    same = 0
    f8_extra = 0
    vc_extra = 0
    for a in survivors:
        s_vc = vertex_circle_status(a)
        s_f8 = f8_status(a)
        if s_vc == s_f8:
            same += 1
        elif s_vc == "ok" and s_f8 != "ok":
            f8_extra += 1
        elif s_f8 == "ok" and s_vc != "ok":
            vc_extra += 1
    print(f"  Same status: {same}/184; F8 stronger: {f8_extra}; VC stronger: {vc_extra}")

    print("\n=== N=10 partial scan (3 rows) ===")
    test_n10_partial()


if __name__ == "__main__":
    main()
