"""Equilateral triangle obstruction analysis for K_4-bicycle stuck cores in n=9 circulants.

OBSERVATION: In each K_4-bicycle stuck core S of the n=9 non-ear circulants,
3 of the 4 vertices form an "all-mutual" triangle: each selects the other two
as selected witnesses. This forces:

    r_a = r_b = r_c    for the triangle vertices a, b, c.

Combined with concyclic constraint at each center, this is *very* restrictive.

CLAIM: An "all-mutual triangle" {a, b, c} with each a selected witness of the other
two forces:
   - r_a = r_b = r_c =: R
   - the triangle (a, b, c) is equilateral with side R.

PROOF SKETCH:
- a's selected radius r_a = ||a - b|| (since b is a's selected witness)
- a's selected radius r_a = ||a - c|| (since c is a's selected witness)
- So ||a - b|| = ||a - c|| = r_a.
- Similarly r_b = ||b - a|| = ||b - c||, so ||a - b|| = ||b - c|| = r_b.
- And r_c = ||c - a|| = ||c - b||.
- Combining: ||a - b|| = ||b - c|| = ||c - a|| = R, equilateral.

This is a very strong constraint on the polygon.

Now, the K_4-bicycle stuck core S = {a, b, c, d} has the triangle {a, b, c}
plus a fourth vertex d. The 4-th vertex d has selected witnesses including
2 of {a, b, c}. WLOG d → a, d → c, but a not → d and c not → d. Etc.

So d is a vertex with ||d - a|| = ||d - c|| = r_d. But ||a - c|| = R, so
d is on the perp-bisector of ac, at distance r_d from a (or equivalently
from c), forming an isoceles triangle.

Now the polygon is strictly convex with the equilateral triangle {a, b, c}
embedded in it. For n=9 in cyclic order [0,1,...,8], the K_4-bicycles have
S like (0, 1, 4, 7). These four vertices in cyclic order are at positions
{0, 1, 4, 7} — *not* consecutive. The triangle {1, 4, 7} (positions 1, 4, 7)
is at cyclic positions 1, 4, 7 — i.e., *equally spaced* around the 9-gon
(positions differ by 3).

CRUCIAL: For the polygon to be strictly convex with vertices labeled 0..8 in
cyclic order, the vertex {1, 4, 7} is exactly the orbit of 1 under rotation
by 120 degrees in the 9-gon. If the polygon were a regular 9-gon, then
positions 1, 4, 7 would form an equilateral triangle. But for a *non-regular*
strictly convex 9-gon, this triangle is generically NOT equilateral.

The forced equilateral constraint is therefore VERY restrictive: among all
strictly convex 9-gons (a (2*9 - 3 = 15)-dimensional moduli space), the
condition "vertices 1, 4, 7 form an equilateral triangle" is codimension 2
(equating 2 distances). Combined with the other K_4-bicycle constraints
(other pairs of equal distances) and the original 4-bad polygon equations,
this is OVERDETERMINED.

For the n=9 non-ear circulants, all 9 cores are cyclic shifts of (0, 1, 4, 7).
That gives 9 forced equilateral triangles {0+k, 3+k, 6+k} for k = 0, 1, ..., 8.

Wait — only the {1, 4, 7} triangle has the offset structure. Let's check:
S = (0, 1, 4, 7). Inner triangle is whichever set has bidirectional edges.

This gives 9 separate triangles, but cyclically shifted, each forcing 3 vertices
into equilateral position. Combined: the polygon must have many sets of 3
equally-spaced vertices forming equilateral triangles. This is essentially
forcing the polygon to be regular = contradiction with strict convexity / 4-bad.

Let me now verify that this is what the vertex-circle obstruction is checking.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from itertools import combinations

REPO = "/home/user/erdos97"
sys.path.insert(0, os.path.join(REPO, "src"))


PAT_81 = [[1, 3, 6, 7], [2, 4, 7, 8], [0, 3, 5, 8], [0, 1, 4, 6],
          [1, 2, 5, 7], [2, 3, 6, 8], [0, 3, 4, 7], [1, 4, 5, 8], [0, 2, 5, 6]]
PAT_151 = [[2, 3, 6, 8], [0, 3, 4, 7], [1, 4, 5, 8], [0, 2, 5, 6],
           [1, 3, 6, 7], [2, 4, 7, 8], [0, 3, 5, 8], [0, 1, 4, 6], [1, 2, 5, 7]]


def rows_to_masks(rows):
    return [sum(1 << v for v in row) for row in rows]


def k4_bicycle_cores_with_triangles(rows):
    """Return list of (core, triangle, fourth_vertex) where triangle is the
    all-mutual triangle inside the core."""
    n = len(rows)
    masks = rows_to_masks(rows)
    out = []
    for sub in combinations(range(n), 4):
        sm = sum(1 << v for v in sub)
        if not all(bin(masks[c] & sm).count("1") == 2 for c in sub):
            continue
        # find all-mutual triangles inside
        for triple in combinations(sub, 3):
            ok = True
            for a, b in combinations(triple, 2):
                if b not in rows[a] or a not in rows[b]:
                    ok = False
                    break
            if ok:
                fourth = [v for v in sub if v not in triple][0]
                out.append((sub, list(triple), fourth))
                break
    return out


def find_all_mutual_triangles(rows):
    """All triples {a, b, c} with each a selected witness of the other two."""
    n = len(rows)
    out = []
    for a, b, c in combinations(range(n), 3):
        if b in rows[a] and c in rows[a] and a in rows[b] and c in rows[b] and a in rows[c] and b in rows[c]:
            out.append((a, b, c))
    return out


def main():
    print("=" * 70)
    print("All-mutual triangle search: forced equilateral triangle obstruction")
    print("=" * 70)

    for name, rows in [("idx=81 offsets {+1,+3,-2,-3}", PAT_81),
                       ("idx=151 offsets {+2,+3,-1,-3}", PAT_151)]:
        print(f"\n--- {name} ---")
        triangles = find_all_mutual_triangles(rows)
        print(f"# all-mutual triangles: {len(triangles)}")
        for t in triangles[:10]:
            offset_diff = [(t[1] - t[0]) % 9, (t[2] - t[1]) % 9, (t[0] - t[2]) % 9]
            print(f"  {t}: cyclic-offset differences {offset_diff}")
        # K_4-bicycle cores with their inner triangles
        cores = k4_bicycle_cores_with_triangles(rows)
        print(f"# K_4-bicycle cores with all-mutual triangle: {len(cores)}")
        for s, tri, fourth in cores[:5]:
            print(f"  core={s}, triangle={tri}, fourth={fourth}")

    print()
    print("=" * 70)
    print("All ear-orderable n=9 patterns: do they also have all-mutual triangles?")
    print("=" * 70)

    sys.path.insert(0, os.path.join(REPO, "data/runs/2026-05-06"))
    from bridge_lemma_attack import generate_n9_184
    n9 = generate_n9_184()
    has_triangle = []
    no_triangle = []
    for idx, rows in enumerate(n9):
        tris = find_all_mutual_triangles(rows)
        if tris:
            has_triangle.append((idx, tris))
        else:
            no_triangle.append((idx, rows))
    print(f"# patterns with all-mutual triangle: {len(has_triangle)} / {len(n9)}")
    print(f"# patterns without all-mutual triangle: {len(no_triangle)} / {len(n9)}")

    # Check: do non-ear ones all have all-mutual triangles?
    sys.path.insert(0, os.path.join(REPO, "data/runs/2026-05-06"))
    from bridge_lemma_attack_test import is_ear_orderable
    for idx, rows in n9:
        pass

    non_ear_indices = [81, 151]
    for idx in non_ear_indices:
        tris = find_all_mutual_triangles(n9[idx])
        print(f"  non-ear idx={idx}: # all-mutual triangles = {len(tris)}")

    # Among ear-orderable, how many have all-mutual triangles?
    ear_with_tri = 0
    ear_without_tri = 0
    for idx, rows in enumerate(n9):
        if idx in non_ear_indices:
            continue
        tris = find_all_mutual_triangles(rows)
        if tris:
            ear_with_tri += 1
        else:
            ear_without_tri += 1
    print(f"  ear-orderable with all-mutual triangle: {ear_with_tri}")
    print(f"  ear-orderable without all-mutual triangle: {ear_without_tri}")


if __name__ == "__main__":
    main()
