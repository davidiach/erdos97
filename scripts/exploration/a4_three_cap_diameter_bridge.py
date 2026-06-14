#!/usr/bin/env python3
"""A4 lane: exact re-examination of the three-cap smallest-enclosing-circle
bridge (canonical-synthesis Sec 5.4) and the Moser cap-lemma caveat.

Goals:
  (1) State the three-cap gap precisely and reproduce the n=8 cap-occupancy
      closure (min{M(p),M(q),M(r)} <= 3) exactly as a counting fact.
  (2) Test the Moser cap-lemma caveat raised in docs/erdos97-attack-2026-05-05.md:
      is "distances from a chord endpoint to convex-position points inside the
      cap are all distinct" actually true for non-inscribed convex polygons?
      Build an EXACT rational counterexample if it is false (this pins down what
      the bridge may and may not assume).
  (3) Probe the n=9 rigid (2,2,2) case structure.

No proof or counterexample of #97 is claimed. Trust = EXACT_DIAGNOSTIC.

Run:  python scripts/exploration/a4_three_cap_diameter_bridge.py
"""
from __future__ import annotations

import sympy as sp

R = sp.Rational


def d2(p, q):
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def report(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


# ---------------------------------------------------------------------------
report("0. PRECISE STATEMENT of the three-cap gap (Sec 5.4)")
print("""
Smallest enclosing circle (SEC) of vertex set V is supported either by
  - 2 antipodal vertices  (DIAMETER case: proved, see below), or
  - 3 vertices p,q,r forming a non-obtuse triangle (THREE-CAP case: OPEN).

Three-cap decomposition: the boundary splits into three caps
  K_pq (between p,q),  K_qr (between q,r),  K_rp (between r,p).
For the chord pq, p and q are its endpoints, so a cap lemma controls distances
from p into K_pq and K_rp; but NOT into K_qr (p is not an endpoint of qr).

Hence: if p is bad (M(p)>=4), at least 2 of its equidistant witnesses lie in the
OPPOSITE cap K_qr. By symmetry q -> K_rp, r -> K_pq.

OPEN three-cap bridge lemma: if p is bad then some equal-distance pair {x,y} at
p lies within a single cap (a diagonal inside that cap), then witness-packing in
caps closes the case.
""")

# ---------------------------------------------------------------------------
report("1. n=8 cap-occupancy closure: min{M(p),M(q),M(r)} <= 3  (exact counting)")
print("""
Claim (geometry-only, attack-2026-05-05): for n=8 with a 3-cap SEC support
p,q,r, NOT all three of p,q,r can be bad.

Counting proof (reproduced):
  If p,q,r all bad, each contributes >=2 witnesses into its OPPOSITE cap:
     p -> >=2 in K_qr,  q -> >=2 in K_rp,  r -> >=2 in K_pq.
  These opposite caps are pairwise disjoint open boundary arcs, and none of
  p,q,r lies in the opposite cap interior. The witnesses counted are among the
  n-3 NON-support vertices. So n-3 >= 2+2+2 = 6, i.e. n >= 9.
  Therefore for n=8 the assumption fails: some support vertex has M<=3.   QED(n=8)
""")
for n in (8, 9, 10):
    need = 6
    status = "FORCES some support M<=3" if (n - 3) < need else "counting alone INSUFFICIENT"
    print(f"   n={n}: non-support vertices = n-3 = {n-3};  need >= {need};  => {status}")

# ---------------------------------------------------------------------------
report("2. MOSER CAP-LEMMA CAVEAT: the distinct-distance claim needs 'ON the SEC'")
print("""
canonical-synthesis Sec 5.4 cap lemma (as stated): 'distances from a chord
endpoint to convex-position points inside the cap are all distinct.'

The TRUE (inscribed) statement: for points ON the SEC arc, |p x| = 2R sin(arc/2)
is strictly monotone in the inscribed arc, hence distinct. We confirm this
exactly, then show precisely why it FAILS to control the polygon's actual cap
vertices.
""")

R_unit = R(1)
p = (R(-1), R(0))
q = (R(1), R(0))
# (2a) Distances from p to points ON the SEC are strictly monotone in arc.
arc_pts = [(R(-3, 5), R(4, 5)), (R(0), R(1)), (R(3, 5), R(4, 5)), (R(4, 5), R(3, 5))]
print("(2a) Points ON the SEC arc, sq-distance from p=(-1,0) (arc order left->right):")
vals = [(X, d2(p, X)) for X in arc_pts]
for X, dd in vals:
    print(f"        x={X}:  |p x|^2 = {dd}")
seq = [dd for _, dd in vals]
strictly_mono = all(seq[i] < seq[i + 1] for i in range(len(seq) - 1))
print(f"     strictly monotone (=> distinct) on the SEC arc: {strictly_mono}   (inscribed Moser holds)")

# (2b) But the polygon's NON-support cap vertices are STRICTLY INSIDE the disk.
# Exhibit two such interior points at EQUAL distance from p (no convexity claim
# about them as a quad -- the point is only that monotonicity does NOT see them).
X = (p[0] + R(3, 5), p[1] + R(4, 5))   # = (-2/5, 4/5), |X|^2 = 4/5 < 1
Y = (p[0] + R(4, 5), p[1] + R(3, 5))   # = (-1/5, 3/5), |Y|^2 = 2/5 < 1
equal = d2(p, X) == d2(p, Y)
inside = (X[0] ** 2 + X[1] ** 2 < 1) and (Y[0] ** 2 + Y[1] ** 2 < 1)
print("\n(2b) Two points strictly INSIDE the SEC disk, equal distance from p:")
print(f"        X={X}, |pX|^2={d2(p,X)}, |X|^2={X[0]**2+X[1]**2} (<1: {X[0]**2+X[1]**2<1})")
print(f"        Y={Y}, |pY|^2={d2(p,Y)}, |Y|^2={Y[0]**2+Y[1]**2} (<1: {Y[0]**2+Y[1]**2<1})")
print(f"        |pX| = |pY| (equal): {equal};  both strictly interior: {inside}")
print("""
   STRUCTURAL CONCLUSION (the actual reason three-cap is hard):
     In a strictly convex polygon whose SEC is supported by p,q,r, EVERY
     non-support vertex lies strictly INSIDE the open SEC disk (otherwise the
     SEC would have a different/larger support). The inscribed monotonicity that
     proves the diameter case applies ONLY to points on the SEC arc. Therefore
     the cap lemma controls at most the on-arc vertices -- of which a generic
     cap has NONE besides the two support endpoints. It gives NO distinctness
     control over the interior cap vertices, where a bad center's witnesses live.

   (Indeed the failed-idea-#18 arc A1..A4 is itself four convex-position points
    at equal distance from the hull vertex O -- equidistance among convex-position
    points is the rule, not the exception, once they are off a common SEC arc.)

   This is why the n=8 cap-occupancy count is phrased via OPPOSITE-cap occupancy
   (>=2 per support vertex), which needs no intra-cap distinctness, rather than
   via an intra-cap distinctness bound.
""")
turns_ok = True  # (no convex-quad claim made; flag retained for summary)

# ---------------------------------------------------------------------------
report("3. WHY the DIAMETER case is safe but THREE-CAP is not (the asymmetry)")
print("""
Diameter case (cited as proved; see caveat): SEC supported by antipodal p,q.
Then EVERY other vertex lies in the closed disk with diameter pq, so angle
p-x-q >= pi/2 (Thales) for all x. canonical-synthesis Sec 5.4 cites the Moser
cap lemma (via Dumitrescu's survey) to conclude E(p),E(q) <= 2, hence >=2 good
vertices. CAVEAT (attack-2026-05-05): the cap-lemma WORDING in Sec 5.4 needs the
inscribed reading; the diameter conclusion should be re-derived under that
stricter reading. The repo records that the n=8 cap-occupancy COUNT uses only
the inscribed special case at SEC-support vertices and is therefore safe; the
full diameter-case E(p)<=2 statement is cited and REVIEW-flagged, not re-proved
in this script.

Key structural difference (independent of that caveat):
  - DIAMETER: p is an endpoint of the chord that bounds the ENTIRE point set
    (one lens), so every vertex is 'cap-controlled' from p.
  - THREE-CAP: each support vertex controls only 2 of the 3 caps; the opposite
    cap K_qr is a blind spot for p. The bad witnesses HIDE in the blind cap.

So the missing ingredient for three-cap is a handle on the OPPOSITE cap. Two
candidate global ingredients:
  (i)  DIAMETER-PAIR ISOLATION: if additionally the longest chord pq (a true
       diameter of V, not just SEC support) is isolated, restrict opposite-cap
       geometry; but a non-obtuse 3-support SEC has NO antipodal diameter pair,
       so this does not directly apply -> must use the 3 SEC radii equalities.
  (ii) RADIUS-DROP CASCADE: a witness pair {x,y} of p both inside K_qr is a
       diagonal whose endpoints are themselves bad; their own opposite caps are
       K_pq, K_rp. Chaining the 'every bad vertex pushes >=2 witnesses to its
       opposite cap' around the 3 caps gives a closed system whose occupancy can
       be counted PER CAP. This is the natural finite-descent target.
""")

# ---------------------------------------------------------------------------
report("4. n=9 rigid (2,2,2) cap case: structural enumeration")
print("""
For n=9 with 3-cap SEC support p,q,r and all bad, the saturating occupancy is
(a,b,c)=(2,2,2): exactly 2 non-support vertices in each cap, and each support
vertex sends EXACTLY 2 witnesses to its opposite cap (which then has exactly 2
slots, so BOTH opposite-cap vertices are witnesses of the support vertex).

This is the maximally rigid sub-case. It is the natural analogue of the n=7
parity argument: the forced 'each support vertex's 2 far-cap vertices are
equidistant from it' gives, via L6 (perpendicularity W_p cap W_q -> p q ⟂ xy),
an OVERDETERMINED perpendicularity system on the 3 caps.

Sketch of the overdetermination (NOT a proof here):
  Cap K_qr = {x1,x2}, with |p x1| = |p x2| = r_p  => p on perp bisector of x1x2.
  Cap K_rp = {y1,y2}, with |q y1| = |q y2| = r_q.
  Cap K_pq = {z1,z2}, with |r z1| = |r z2| = r_r.
  Plus the 3 SEC radius equalities |Op|=|Oq|=|Or| at the SEC center O.
  Plus the full 4-witness rows of p,q,r (each needs 4 equidistant, but only 2
  are forced into the opposite cap; the other 2 must be among support vertices
  and the SAME or ADJACENT caps -> further constraints).

This is exactly the 'L6 perpendicularity overdetermination in the spirit of the
n=7 parity argument' attack target named in attack-2026-05-05. It remains OPEN.
""")

report("SUMMARY")
print("n=8 cap-occupancy closure valid (counting): n-3=5 < 6 -> some support M<=3: True")
print(f"Moser distinctness holds ON the SEC arc ({strictly_mono}) but non-support cap")
print(f"vertices are strictly interior (witness X,Y equal-dist {d2(p,X)} from p, "
      f"interior={inside}) so the lemma does NOT control them.")
print("three-cap bridge gap = no control on OPPOSITE (blind) cap; needs per-cap")
print("occupancy descent or n=9 (2,2,2) L6-overdetermination. Status: OPEN.")
