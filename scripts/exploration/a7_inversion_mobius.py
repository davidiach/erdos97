#!/usr/bin/env python3
"""A7: Inversion / Mobius reformulation of Erdos #97 (deeper than the pilot).

This is an EXPLORATION script. It does NOT prove Erdos Problem #97, does NOT
claim a counterexample, and does NOT certify Euclidean realizability. It uses
EXACT rational arithmetic (fractions.Fraction) throughout for the geometric
checks, so any reported equality is exact, not floating-point.

It investigates whether a single geometric inversion (or any Mobius transform)
compresses the simultaneous per-center 4-equidistant condition, and whether the
extra structure exposed by inversion at a witness yields a NEW exact
realizability filter usable on the n=9 frontier.

Sections
--------
1. Single-inversion incompatibility theorem (exact, finite reason).
2. Witness-inversion structure: image of a center is the FOOT-related point;
   the image line is perpendicular to b-hat(center). Derive the exact
   foot/perpendicularity constraint that the incidence-only pilot dropped.
3. Exact filter candidate: cross-ratio / collinearity constraints implied by
   inversion, tested as a *combinatorial* necessary condition on the 184
   frontier assignments (these are abstract; realizability is the open part).
4. A concrete exact realizable witness check on a small hand example, to make
   sure the inversion formulas are exact and the perpendicularity claim holds.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTIER = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)


# ---------------------------------------------------------------------------
# Exact 2D inversion in the plane (rational, via Fraction).
# Inversion at center c with radius^2 = k maps point p (p != c) to
#   inv(p) = c + k * (p - c) / |p - c|^2.
# With k rational and p, c rational, inv(p) is rational. Good for exact checks.
# ---------------------------------------------------------------------------
Pt = tuple[Fraction, Fraction]


def sub(a: Pt, b: Pt) -> Pt:
    return (a[0] - b[0], a[1] - b[1])


def add(a: Pt, b: Pt) -> Pt:
    return (a[0] + b[0], a[1] + b[1])


def smul(s: Fraction, a: Pt) -> Pt:
    return (s * a[0], s * a[1])


def dot(a: Pt, b: Pt) -> Fraction:
    return a[0] * b[0] + a[1] * b[1]


def norm2(a: Pt) -> Fraction:
    return a[0] * a[0] + a[1] * a[1]


def cross(a: Pt, b: Pt) -> Fraction:
    return a[0] * b[1] - a[1] * b[0]


def invert(p: Pt, c: Pt, k: Fraction) -> Pt:
    d = sub(p, c)
    return add(c, smul(k / norm2(d), d))


def collinear(a: Pt, b: Pt, cc: Pt) -> bool:
    return cross(sub(b, a), sub(cc, a)) == 0


def perpendicular(u: Pt, v: Pt) -> bool:
    return dot(u, v) == 0


# ---------------------------------------------------------------------------
# Section 2 + 4: exact verification of the inversion-at-witness structure.
#
# Claim to verify EXACTLY on a concrete rational example:
#   Let center O have 4 witnesses W1..W4 on a circle C(O,r) (|O - Wj| = r).
#   Pick one witness b = W1 as the inversion center, radius^2 = k arbitrary.
#   Then:
#     (a) inv(W2), inv(W3), inv(W4) are collinear (circle-through-center -> line).
#     (b) that image line L is PERPENDICULAR to the segment b--inv(O).
#         (Because the diameter of C(O,r) through b maps to the normal of L;
#          inv(O) lies on the perpendicular from b to L.)
#     (c) inv(O) is the reflection of b across L scaled appropriately; concretely
#         the foot of b on L equals the midpoint structure -- we just verify the
#         perpendicularity exactly, which is the load-bearing NEW constraint.
# ---------------------------------------------------------------------------
def build_centered_circle_example() -> dict[str, object]:
    """A concrete EXACT rational center+4-witness configuration on one circle."""
    o: Pt = (Fraction(0), Fraction(0))
    # Four rational points on the unit circle (Pythagorean directions).
    # (3/5,4/5),(4/5,3/5),(5/13,12/13),(12/13,5/13): all unit distance from O.
    w1: Pt = (Fraction(3, 5), Fraction(4, 5))
    w2: Pt = (Fraction(4, 5), Fraction(3, 5))
    w3: Pt = (Fraction(5, 13), Fraction(12, 13))
    w4: Pt = (Fraction(12, 13), Fraction(5, 13))
    witnesses = [w1, w2, w3, w4]
    # sanity: all unit distance from O (exact)
    radii2 = [norm2(sub(w, o)) for w in witnesses]
    assert all(r == Fraction(1) for r in radii2), radii2

    b = w1
    k = Fraction(7, 3)  # arbitrary nonzero inversion power
    inv_o = invert(o, b, k)
    inv_w = [invert(w, b, k) for w in witnesses[1:]]  # images of the other 3

    # (a) collinearity of the 3 images
    coll = collinear(inv_w[0], inv_w[1], inv_w[2])

    # (b) perpendicularity: direction of image line vs b->inv(O)
    line_dir = sub(inv_w[1], inv_w[0])
    bo = sub(inv_o, b)
    perp = perpendicular(line_dir, bo)

    # (c) inv(O) collinear with b and the foot? Verify inv(O) lies on the line
    # through b perpendicular to L (i.e. b->inv(O) is normal to L) AND that the
    # foot of inv(O) onto L is the same as foot of b onto L (both give the line's
    # closest point). We already have perp; also check inv(O) is NOT on L:
    o_on_line = collinear(inv_w[0], inv_w[1], inv_o)

    return {
        "radii2_all_one": all(r == Fraction(1) for r in radii2),
        "three_images_collinear": coll,
        "image_line_perp_to_b_invO": perp,
        "invO_on_image_line": o_on_line,
        "inv_O": [str(inv_o[0]), str(inv_o[1])],
        "image_points": [[str(p[0]), str(p[1])] for p in inv_w],
        "comment": (
            "Exact: 3 images collinear; image line perpendicular to b->inv(O); "
            "inv(O) off the line. This perpendicular foot constraint is the "
            "extra exact data the incidence-only pilot discarded."
        ),
    }


# ---------------------------------------------------------------------------
# Section 1: single-inversion incompatibility (finite combinatorial reason).
#
# A single inversion at center q linearizes circle C_i (center p_i, radius r_i)
# IFF C_i passes through q, i.e. |p_i - q| = r_i, i.e. q is itself a witness on
# C_i. For ALL n centers to be linearized by ONE inversion at q, q would have to
# lie on every center's selected circle simultaneously, i.e. q is a witness of
# every center. On the frontier each vertex is a witness of exactly 4 centers
# (indegree 4 < 9). So no single vertex-centered inversion linearizes all rows.
# More strongly: even an inversion at an arbitrary plane point q (not a vertex)
# linearizes C_i only if q is on C_i; q on all 9 distinct centered circles is
# generically impossible (>=3 circles in general position share no common point).
# This is the precise no-go for "inversion-as-global-linearization".
# ---------------------------------------------------------------------------
def single_inversion_obstruction(rows_list: list[list[list[int]]]) -> dict[str, object]:
    """For each assignment, max number of circles ANY vertex lies on (indegree).

    If this max is < n for all assignments, no vertex-centered single inversion
    can linearize all rows; we report it as the exact finite obstruction.
    """
    n = 9
    worst = 0
    per_assignment_max = []
    for rows in rows_list:
        indeg = [0] * n
        for r in rows:
            for w in r[1:]:
                indeg[w] += 1
        m = max(indeg)
        per_assignment_max.append(m)
        worst = max(worst, m)
    return {
        "n": n,
        "max_indegree_over_all_assignments": worst,
        "linearizable_circles_by_one_vertex_inversion": worst,
        "needed_for_global_linearization": n,
        "global_single_inversion_possible": worst >= n,
        "distinct_max_values": sorted(set(per_assignment_max)),
    }


# ---------------------------------------------------------------------------
# Section 3: inversion-at-witness collinearity as a COMBINATORIAL filter.
#
# Fix witness b. The circles through b are exactly the centers i with b in S_i.
# Inverting at b sends each such circle to a line through {S_i - {b}} (3 pts).
# Two such lines coincide iff their image-point sets share >= 2 points, which
# (since inversion is a bijection on the plane minus b) happens iff the ORIGINAL
# two circles share >= 2 points besides b -- but two distinct circles meet in at
# most 2 points, so sharing 2 points besides b is impossible for distinct
# circles. Hence forced lines never merge: this reproduces the pilot's "no
# compression" at the incidence level, and we re-derive WHY exactly.
#
# The NEW ingredient we test: the image of the CENTER p_i, namely inv(p_i),
# together with the perpendicularity constraint, links the 4 lines at b. We
# encode the abstract necessary condition that the 4 image lines at b and the 4
# image centers inv(p_i) must be jointly realizable with each inv(p_i) being the
# inversive image of the center of its line. We test whether this adds any
# *combinatorial* (label-only) constraint beyond incidence -- expectation: it is
# purely metric, so NO new combinatorial filter. We document that precisely.
# ---------------------------------------------------------------------------
def witness_inversion_combinatorial(
    rows_list: list[list[list[int]]],
) -> dict[str, object]:
    n = 9
    total_witness_pivots = 0
    forced_lines = 0
    merges = 0
    # also: do any two centers sharing witness b also share a SECOND witness?
    # That would mean two circles meeting in 2 points besides b -> impossible
    # for distinct circles, so it must be 0 (a sanity / soundness check).
    second_shared_violations = 0
    for rows in rows_list:
        S = [set(r[1:]) for r in rows]
        for b in range(n):
            centers_through_b = [i for i in range(n) if b in S[i]]
            if not centers_through_b:
                continue
            total_witness_pivots += 1
            # forced lines = the 3-point image sets
            line_sets = [S[i] - {b} for i in centers_through_b]
            forced_lines += len(line_sets)
            # count merges: pairs sharing >=2 image points
            for x, y in combinations(range(len(line_sets)), 2):
                if len(line_sets[x] & line_sets[y]) >= 2:
                    merges += 1
            # second-shared check (besides b)
            for i, j in combinations(centers_through_b, 2):
                shared = S[i] & S[j]
                if len(shared - {b}) >= 2:
                    second_shared_violations += 1
    return {
        "total_witness_pivots": total_witness_pivots,
        "forced_lines": forced_lines,
        "line_merges_found": merges,
        "two_circles_share_two_pts_besides_b": second_shared_violations,
        "new_combinatorial_filter": merges > 0,
    }


def foot_of(b: Pt, line_pts: tuple[Pt, Pt]) -> Pt:
    """Exact foot of b onto the line through line_pts (two distinct points)."""
    p, q = line_pts
    d = sub(q, p)
    t = dot(sub(b, p), d) / norm2(d)
    return add(p, smul(t, d))


def reflect_across_line(b: Pt, line_pts: tuple[Pt, Pt]) -> Pt:
    f = foot_of(b, line_pts)
    return sub(smul(Fraction(2), f), b)


def inversion_foot_lemma_demo() -> dict[str, object]:
    """EXACT demo of the Inversion-Foot Lemma on a rational config.

    Lemma: invert circle C(O,r) through b at b (power k). The image line L is the
    perpendicular bisector of [b, inv(O)]: foot_L(b) = midpoint(b, inv(O)) and
    inv(O) = reflection of b across L. We verify this exactly, then verify that
    the 3 inverted witnesses indeed lie on that perpendicular-bisector line.
    """
    o: Pt = (Fraction(1), Fraction(0))
    # witnesses on unit circle centered at O -> on circle |p-O|=1. Use b plus
    # three other rational points at distance 1 from O.
    b: Pt = (Fraction(0), Fraction(0))  # |b-O| = 1
    w2: Pt = (Fraction(1) + Fraction(3, 5), Fraction(4, 5))  # O + (3/5,4/5)
    w3: Pt = (Fraction(1) + Fraction(4, 5), Fraction(3, 5))
    w4: Pt = (Fraction(1) - Fraction(5, 13), Fraction(12, 13))
    for w in (b, w2, w3, w4):
        assert norm2(sub(w, o)) == Fraction(1), w
    k = Fraction(11, 4)
    inv_o = invert(o, b, k)
    imgs = (invert(w2, b, k), invert(w3, b, k), invert(w4, b, k))
    # line L from first two images
    line_pts = (imgs[0], imgs[1])
    foot = foot_of(b, line_pts)
    mid = smul(Fraction(1, 2), add(b, inv_o))
    refl = reflect_across_line(b, line_pts)
    return {
        "all_witnesses_on_circle": True,
        "three_images_collinear": collinear(*imgs),
        "foot_equals_midpoint_b_invO": foot == mid,
        "invO_is_reflection_of_b_across_L": refl == inv_o,
        "L_is_perp_bisector_of_b_invO": (foot == mid and refl == inv_o),
        "comment": (
            "EXACT: image line L = perpendicular bisector of [b, inv(O)]. "
            "Thus inv(O) determines L completely; the 3 inverted witnesses lie "
            "on perp-bisector([b, inv(O)])."
        ),
    }


def witness_perp_bisector_coupling(
    rows_list: list[list[list[int]]],
) -> dict[str, object]:
    """Test whether the perp-bisector structure couples the 4 lines at b.

    At witness b, the 4 centers O_1..O_4 through b give 4 image lines
    L_j = perp-bisector([b, inv(O_j)]). The image points of b's role: note the
    CENTERS O_j are themselves vertices, and each O_j is in turn a center whose
    own circle does NOT pass through b in general. The key abstract question:
    do the 4 lines at b share inverted witness points (forming an incidence net),
    and does any inverted CENTER inv(O_j) coincide with an inverted WITNESS of
    another line at the same b (which would force a collinearity-of-centers
    constraint independent of coordinates)?

    Because inversion at b is a label-respecting bijection (b excluded), two
    image objects coincide iff the originals coincide. inv(O_j) is the image of
    a CENTER, inverted witnesses are images of WITNESSES; a center can also BE a
    witness of another row. We test, purely combinatorially: at each b, is some
    center O_j (through b) ALSO a witness of another center O_m (through b)?
    If yes, then inv(O_j) lies on L_m, giving 'center on another's image line':
    an exact incidence linking center-images to lines. We count these.
    """
    n = 9
    coincidences = 0  # center O_j is a non-b witness of O_m, both through b
    pivots_with_coincidence = 0
    total_pivots = 0
    for rows in rows_list:
        S = [set(r[1:]) for r in rows]
        for b in range(n):
            through = [i for i in range(n) if b in S[i]]
            if not through:
                continue
            total_pivots += 1
            found = False
            for oj in through:
                for om in through:
                    if oj == om:
                        continue
                    # is center oj (a vertex) a witness of center om (besides b)?
                    if oj in (S[om] - {b}):
                        coincidences += 1
                        found = True
            if found:
                pivots_with_coincidence += 1
    return {
        "total_witness_pivots": total_pivots,
        "center_on_other_image_line_incidences": coincidences,
        "pivots_with_such_incidence": pivots_with_coincidence,
        "gives_center_image_line_coupling": coincidences > 0,
        "note": (
            "Where positive, inv(O_j) is FORCED onto image line L_m, AND L_m is "
            "the perp-bisector of [b, inv(O_m)]. So |inv(O_j)-b| = |inv(O_j)-"
            "inv(O_m)|: an exact metric relation among inverted vertices. This "
            "is a metric (not combinatorial) filter; realizability test below."
        ),
    }


def turns(pts: list[Pt]) -> list[Fraction]:
    n = len(pts)
    out = []
    for i in range(n):
        a, b, c = pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        out.append(cross(sub(b, a), sub(c, b)))
    return out


def convexity_not_preserved_certificate() -> dict[str, object]:
    """EXACT certificate that inversion at a vertex destroys strict convexity.

    A strictly convex octagon (all turn-determinants positive) is inverted at one
    vertex (which goes to infinity and is dropped). The remaining 7 image points,
    taken in the same cyclic order with STRAIGHT chords, have mixed-sign and zero
    turn-determinants, hence are not strictly convex. Geometric reason: inversion
    sends the polygon's straight edges to circular ARCS, so the image bounded by
    chords need not be convex. This is exact rational arithmetic.
    """
    poly: list[Pt] = [
        (Fraction(0), Fraction(0)),
        (Fraction(100), Fraction(0)),
        (Fraction(101), Fraction(1)),
        (Fraction(101), Fraction(50)),
        (Fraction(100), Fraction(51)),
        (Fraction(0), Fraction(51)),
        (Fraction(-1), Fraction(50)),
        (Fraction(-1), Fraction(1)),
    ]
    t0 = turns(poly)
    c = poly[0]
    img = [invert(p, c, Fraction(1)) for p in poly[1:]]
    ti = turns(img)
    signs = [1 if x > 0 else (-1 if x < 0 else 0) for x in ti]
    return {
        "original_convex": all(x > 0 for x in t0),
        "inverted_at": "vertex0 (sent to infinity, dropped)",
        "image_turn_signs": signs,
        "image_strictly_convex": len(set(signs)) == 1 and 0 not in signs,
        "convexity_preserved": len(set(signs)) == 1 and 0 not in signs,
        "image_turns": [str(x) for x in ti],
        "comment": (
            "EXACT: inversion at a vertex turns a strictly convex octagon into a "
            "non-convex (mixed-sign, with collinear triples) image. Convexity, the "
            "ingredient any #97 impossibility proof MUST use, has no clean image."
        ),
    }


def cross_ratio_center_blindness() -> dict[str, object]:
    """Cross-ratio (the Mobius invariant) detects concyclicity but NOT the center.

    The #97 per-center condition is '4 points on a circle CENTERED AT v', strictly
    stronger than '4 points concyclic'. The cross-ratio of 4 points is real iff
    they are concyclic-or-collinear, and is invariant under all Mobius maps. But
    two different circles with different centers can carry point quadruples of the
    same cross-ratio: the center is an affine/metric datum cross-ratio discards.
    So no Mobius-invariant (cross-ratio) constraint can encode 'centered at v'.
    """
    # Two quadruples on different circles (different centers), each with a real
    # cross-ratio; their cross-ratios coincide here, showing center-blindness.
    import cmath  # noqa: PLC0415 (local: demo only)

    def cr(z: list[complex]) -> complex:
        z1, z2, z3, z4 = z
        return ((z1 - z3) * (z2 - z4)) / ((z1 - z4) * (z2 - z3))

    # quad A: unit circle centered at 0, at angles 0,90,180,270
    a = [cmath.rect(1, t) for t in (0, cmath.pi / 2, cmath.pi, 3 * cmath.pi / 2)]
    # quad B: same circle but TRANSLATED center 5+0j (different center), same angles
    b = [5 + p for p in a]
    cra, crb = cr(a), cr(b)
    return {
        "cross_ratio_quadA_centered_0": [round(cra.real, 9), round(cra.imag, 9)],
        "cross_ratio_quadB_centered_5": [round(crb.real, 9), round(crb.imag, 9)],
        "both_real_concyclic": abs(cra.imag) < 1e-9 and abs(crb.imag) < 1e-9,
        "cross_ratios_equal_despite_different_centers": abs(cra - crb) < 1e-9,
        "comment": (
            "Cross-ratio is blind to the circle's CENTER. The #97 condition needs "
            "the center (a polygon vertex), so the Mobius-invariant layer cannot "
            "express it. The center re-enters only as a non-invariant metric datum."
        ),
    }


def main() -> int:
    data = json.loads(FRONTIER.read_text(encoding="utf-8"))
    rows_list = [a["selected_rows"] for a in data["assignments"]]

    result = {
        "trust": "EXPLORATION_EXACT_DIAGNOSTIC_ONLY",
        "claim_scope": (
            "Exact inversion/Mobius analysis on the 184 n=9 frontier; not a proof "
            "of #97, not a counterexample, not a realizability certificate."
        ),
        "section1_single_inversion_obstruction": single_inversion_obstruction(rows_list),
        "section2_4_exact_inversion_structure": build_centered_circle_example(),
        "section2b_inversion_foot_lemma": inversion_foot_lemma_demo(),
        "section3_witness_inversion_combinatorial": witness_inversion_combinatorial(
            rows_list
        ),
        "section4_perp_bisector_coupling": witness_perp_bisector_coupling(rows_list),
        "section5_convexity_not_preserved": convexity_not_preserved_certificate(),
        "section6_cross_ratio_center_blind": cross_ratio_center_blindness(),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
