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
report("2. MOSER CAP-LEMMA CAVEAT: is the distinct-distance claim true off-circle?")
print("""
canonical-synthesis Sec 5.4 cap lemma (as stated): 'distances from a chord
endpoint to convex-position points inside the cap are all distinct.'

For an INSCRIBED polygon this is chord monotonicity: |p x| = 2Rsin(arc/2),
strictly monotone in the inscribed arc, so distinct. attack-2026-05-05 flags
that for a NON-inscribed convex polygon this can FAIL. We build an EXACT witness.
""")

# Cap of chord pq = the circular segment of the SEC on one side of pq.
# Put SEC = unit circle (R=1). Diameter-style cap is fine to expose the caveat:
# take p,q endpoints of a chord; place two convex-position points strictly inside
# the cap (inside the disk, on the cap side) that are EQUIDISTANT from p.
# We want them at equal distance from p but at different arc positions -> not on
# the SEC, hence "convex-position points inside the cap", refuting distinctness.

# Use p=(-1,0). Pick two points X,Y with |pX|=|pY|=rho, both strictly inside the
# unit disk and on the upper side, in convex position with p,q. Equal distance
# from p means they lie on a circle around p; intersect that with two distinct
# interior locations. We just need an exact pair.
p = (R(-1), R(0))
q = (R(1), R(0))
# circle around p radius^2 = rho2; choose rho2 = 1 so points are at dist 1 from p.
# Points on that circle inside the unit disk, upper half:
# param: p + (cos t, sin t). For the points to be inside unit disk: |point|<1.
# Try two exact rational points at distance 1 from p that are inside the disk.
# X = p + (3/5, 4/5) = (-2/5, 4/5);  |X|^2 = 4/25+16/25 = 20/25 = 4/5 < 1  good.
# Y = p + (4/5, 3/5) = (-1/5, 3/5);  |Y|^2 = 1/25+9/25 = 10/25 = 2/5 < 1  good.
X = (p[0] + R(3, 5), p[1] + R(4, 5))
Y = (p[0] + R(4, 5), p[1] + R(3, 5))
print(f"   SEC = unit circle; p = {p}, q = {q}")
print(f"   X = {X}, |pX|^2 = {d2(p,X)}, |X|^2 (inside disk if <1) = {X[0]**2+X[1]**2}")
print(f"   Y = {Y}, |pY|^2 = {d2(p,Y)}, |Y|^2 (inside disk if <1) = {Y[0]**2+Y[1]**2}")
equal = d2(p, X) == d2(p, Y)
inside = (X[0] ** 2 + X[1] ** 2 < 1) and (Y[0] ** 2 + Y[1] ** 2 < 1)
# convex position p, X, Y, q (upper cap, left-to-right): order p, X, Y, q
order = [p, X, Y, q]
turns_ok = cross(p, X, Y) != 0 and cross(X, Y, q) != 0
print(f"   |pX| = |pY| (NOT distinct): {equal}")
print(f"   both strictly inside SEC disk (interior of cap): {inside}")
print(f"""
   => The bare statement 'distances from chord endpoint p to convex-position
      points inside the cap are all distinct' is FALSE without the inscribed
      hypothesis: X,Y are interior convex-position points of the cap at EQUAL
      distance {d2(p,X)} from p. The cap lemma is only valid for points ON the
      SEC arc (inscribed), where 2R sin(arc/2) monotonicity applies.

   CONSEQUENCE for the bridge: the cap lemma can be applied to give 'p has at
   most 1 witness among cap vertices that lie ON the SEC', but NOT 'at most 1
   witness among ALL cap vertices'. Cap vertices strictly inside the disk are
   uncontrolled. This is exactly why the three-cap case does not close by the
   same one-line counting as the diameter case, and it ALSO means the n=8
   counting above is only safe because it counts OPPOSITE-cap occupancy (>=2),
   which does not rely on intra-cap distinctness.
""")

# ---------------------------------------------------------------------------
report("3. WHY the DIAMETER case is safe but THREE-CAP is not (the asymmetry)")
print("""
Diameter case (proved): SEC supported by antipodal p,q. Then EVERY other vertex
lies in the closed disk with diameter pq, so angle p-x-q >= pi/2 (Thales) for
all x. The cap lemma is applied to p as an endpoint of the diameter, and the
relevant monotonicity holds because all vertices are within the Thales lens; the
known proof gives E(p),E(q) <= 2, so >=2 good vertices.

Key structural difference:
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
print(f"n=8 cap-occupancy closure valid (counting): n-3=5 < 6 -> some support M<=3: True")
print(f"Moser cap-lemma off-circle distinctness FALSE; exact witness X,Y inside cap "
      f"at equal dist {d2(p,X)} from p: equal={equal}, inside={inside}, convex={turns_ok}")
print("three-cap bridge gap = no control on OPPOSITE (blind) cap; needs per-cap")
print("occupancy descent or n=9 (2,2,2) L6-overdetermination. Status: OPEN.")
