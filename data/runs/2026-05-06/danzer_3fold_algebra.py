"""Algebraic approach: 3-fold symmetric n=9, force E=4.
Three orbits of 3 points each. Using 3-fold symmetry:
- A_k at (r_A, 2pi*k/3 + phi_A), k=0,1,2 with phi_A = pi/2 (or 0).
- B_k similar with phi_B
- C_k similar with phi_C.
By rotational symmetry, every vertex of type A has the same multiset of distances to others.
Same for B and C.
So we only need to ensure E=4 at THREE representative vertices: A_0, B_0, C_0.
At A_0: distances are
  d(A_0, A_1) = d(A_0, A_2) [by sym] = sqrt(3)*r_A (always)
  d(A_0, B_k) for k=0,1,2 take 3 generally distinct values
  d(A_0, C_k) for k=0,1,2 take 3 generally distinct values
A_0 already has 2 equal sister distances.
For A_0 to have E=4 we need 4 other distances all equal.
Options:
(a) sqrt(3)*r_A = some d(A_0, B_k) = some d(A_0, C_k)... need 4 total at one radius.
    The pair (A_1, A_2) gives 2; need 2 more at the same radius.
(b) d(A_0, B_k) = d(A_0, B_j) = d(A_0, C_l) = d(A_0, C_m) all equal (4 elements at one radius from {B_k, C_l}).
(c) Some other combination.

Let me parameterize and search algebraically using sympy.
"""
import sympy as sp
import numpy as np
import math

rA, rB, rC, phiA, phiB, phiC = sp.symbols('rA rB rC phiA phiB phiC', positive=True, real=True)

# Set phi_A = 0 by rotation freedom; r_A = 1 by scale freedom.
# So free: r_B, r_C, phi_B, phi_C.

def coords(rA_val, rB_val, rC_val, phiA_val, phiB_val, phiC_val):
    pts = []
    for k in range(3):
        ang = phiA_val + 2*sp.pi*k/3
        pts.append((rA_val*sp.cos(ang), rA_val*sp.sin(ang)))
    for k in range(3):
        ang = phiB_val + 2*sp.pi*k/3
        pts.append((rB_val*sp.cos(ang), rB_val*sp.sin(ang)))
    for k in range(3):
        ang = phiC_val + 2*sp.pi*k/3
        pts.append((rC_val*sp.cos(ang), rC_val*sp.sin(ang)))
    return pts

# A_0 at angle 0:
# d(A_0, B_k)^2 = (rA - rB cos(phiB+2pi k/3))^2 + (rB sin(phiB+2pi k/3))^2
#               = rA^2 + rB^2 - 2 rA rB cos(phiB + 2pi k/3)
# So 3 values of cos(phiB+2pi k/3): cos(phiB), cos(phiB+2pi/3), cos(phiB-2pi/3).

# Let theta = phiB. The three values are cos(theta), cos(theta-2pi/3), cos(theta+2pi/3).
# These sum to 0 (always). Three roots of T_3(c)=cos(3theta)/3 ... I'll just compute.

import sympy as sp

phiB_sym = sp.Symbol('phiB')
phiC_sym = sp.Symbol('phiC')

cos_vals_B = [sp.cos(phiB_sym + 2*sp.pi*k/3) for k in range(3)]
cos_vals_C = [sp.cos(phiC_sym + 2*sp.pi*k/3) for k in range(3)]

rA_sym = 1
rB_sym = sp.Symbol('rB', positive=True)
rC_sym = sp.Symbol('rC', positive=True)

# Squared distances from A_0 (at angle 0):
d_A0_Bk = [rA_sym**2 + rB_sym**2 - 2*rA_sym*rB_sym*c for c in cos_vals_B]
d_A0_Ck = [rA_sym**2 + rC_sym**2 - 2*rA_sym*rC_sym*c for c in cos_vals_C]
# sister distances (A_0 to A_1, A_2):
d_A0_Aj = [3 * sp.Symbol('rA_sq'), 3 * sp.Symbol('rA_sq')]  # placeholder

# From A_0 we have 8 other vertices.
# Distances squared (8 values):
print("=== Multiset of d^2 from A_0 ===")
multiset_A0 = d_A0_Aj + d_A0_Bk + d_A0_Ck
for x in multiset_A0:
    print("  ", sp.simplify(x))

# By sym, A_1, A_2 have same multiset.
# Same for orbit B (vertex B_0 at (rB cos phiB, rB sin phiB)):
# d(B_0, B_1) = d(B_0, B_2) = sqrt(3)*rB
# d(B_0, A_k) = 3 distinct values dep on (phiB - 2pi*k/3)
# d(B_0, C_k) = 3 distinct values dep on (phiB - phiC - 2pi*k/3)
print()

# Plan: for E=4 at A_0, need 4 of 8 distances to be equal.
# Easiest: find r_B, r_C, phiB, phiC such that
#   d(A_0, A_1)^2 = d(A_0, A_2)^2 = d(A_0, B_0)^2 = d(A_0, B_1)^2 (4 equal)
# That means cos(phiB) = cos(phiB + 2pi/3) => phiB = pi/3 (so cos = 1/2 = cos(-2pi/3+pi/3)=cos(-pi/3)=1/2)
# Hmm: cos(phiB) = cos(phiB+2pi/3) iff phiB+phiB+2pi/3 = 0 mod 2pi or phiB = -(phiB+2pi/3)+2pi k
# 2phiB = -2pi/3 + 2pi k => phiB = -pi/3 + pi k. So phiB = -pi/3 or phiB = 2pi/3.

# At phiB = -pi/3: cos(phiB) = 1/2 = cos(-pi/3+2pi/3) = cos(pi/3) = 1/2.  Yes.
# Then 3rd cos(phiB - 2pi/3) = cos(-pi) = -1.
# So at A_0, distances to B_0, B_1, B_2 are sqrt(rA^2 + rB^2 - rA*rB), sqrt(rA^2+rB^2-rA*rB),
#   sqrt(rA^2+rB^2+2*rA*rB) = rA + rB.
# Equate sqrt(3)*rA = sqrt(rA^2+rB^2 - rA*rB):
#   3 rA^2 = rA^2 + rB^2 - rA*rB
#   2 rA^2 = rB^2 - rA*rB
#   rB^2 - rA*rB - 2*rA^2 = 0
#   rB = (rA + sqrt(rA^2 + 8*rA^2))/2 = (rA + 3*rA)/2 = 2*rA.
# So rB = 2 (with rA=1).

# Now at A_0, witness set at distance sqrt(3)*rA: {A_1, A_2, B_0, B_1} (size 4!) E=4!
# Let's check if it's E=4 at B_0 too.

rA_val = sp.Rational(1)
rB_val = 2
phiB_val = -sp.pi/3
print(f"\nWith rA={rA_val}, rB={rB_val}, phiB={phiB_val}:")
print("Distances from A_0 (squared):")
ms = [sp.simplify(x.subs({rA_sym: rA_val, rB_sym: rB_val, phiB_sym: phiB_val})) for x in multiset_A0[:5]]
for i, x in enumerate(ms):
    print(f"  d^2_{i}: {x}")
# A_0's witness set so far: 4 at d^2 = 3 (A_1, A_2, B_0, B_1).
# Now we need similar at B_0.
# B_0 at (rB cos phiB, rB sin phiB) = (2*1/2, 2*(-sqrt(3)/2)) = (1, -sqrt(3))
# Wait, phiB = -pi/3: cos = 1/2, sin = -sqrt(3)/2. B_0 = (1, -sqrt(3)).
# B_0's distances:
# - to B_1 = (2 cos(phiB+2pi/3), 2 sin(phiB+2pi/3)) = (2 cos(pi/3), 2 sin(pi/3)) = (1, sqrt(3)). dist = 2*sqrt(3)
# - to B_2 = (2 cos(phiB-2pi/3), 2 sin(phiB-2pi/3)) = (2 cos(-pi), 2 sin(-pi)) = (-2, 0). dist^2 = 9 + 3 = 12. dist=2sqrt(3).
# - to A_0 = (1, 0). dist^2 = 0 + 3 = 3.
# - to A_1 (at angle 2pi/3): A_1 = (cos(2pi/3), sin(2pi/3)) = (-1/2, sqrt(3)/2). dist B_0 to A_1:
#    (1-(-1/2))^2 + (-sqrt(3)-sqrt(3)/2)^2 = (3/2)^2 + (3 sqrt(3)/2)^2 = 9/4 + 27/4 = 9.  dist=3.
# - to A_2 (at angle -2pi/3): A_2 = (-1/2, -sqrt(3)/2). dist B_0 to A_2:
#    (1-(-1/2))^2 + (-sqrt(3)+sqrt(3)/2)^2 = (3/2)^2 + (-sqrt(3)/2)^2 = 9/4 + 3/4 = 3. dist=sqrt(3).
# - to C_k (3 values dep on phiC, rC).

# So at B_0, distances are: {2sqrt(3), 2sqrt(3), sqrt(3), 3, sqrt(3), C_0, C_1, C_2}
# Sister distances both 2sqrt(3) (count 2). Plus 2 at sqrt(3) (A_0, A_2).
# For E=4 at B_0: need 4 at one radius.
# sqrt(3): currently 2 (A_0, A_2). Need 2 more at sqrt(3) (i.e., d(B_0,C_k)=sqrt(3) for 2 values of k).
#   d(B_0, C_k)^2 = rB^2 + rC^2 - 2 rB rC cos(phiB - phiC - 2pi k/3) = 3
#   4 + rC^2 - 4 rC cos(phiB - phiC - 2pi k/3) = 3
#   rC^2 + 1 = 4 rC cos(...)
# Need this for 2 values of k => cos(phiB - phiC) = cos(phiB - phiC - 2pi/3) (or the third pair).
# phiB - phiC = -(phiB - phiC - 2pi/3) mod 2pi
# 2(phiB - phiC) = 2pi/3 + 2pi k => phiB - phiC = pi/3 + pi k
# So phiC = phiB - pi/3 = -pi/3 - pi/3 = -2pi/3 (or phiB - 4pi/3)
# Try phiC = -2pi/3: cos(phiB - phiC) = cos(-pi/3 - (-2pi/3)) = cos(pi/3) = 1/2.
# Then equation: rC^2 + 1 = 4 rC * 1/2 = 2 rC. So rC^2 - 2 rC + 1 = 0. rC = 1.
# But that puts C on same circle as A (rA = 1)! Coincides? Let's check.

print("\n=== Trying phiC = -2pi/3, rC = 1 ===")
# But that means C is at angle -2pi/3 + 2pi k/3, same as A's angle 0, 2pi/3, -2pi/3 modulo orbit.
# So C and A have the same orbit (overlap).
# This solution is DEGENERATE.

# Try phiC = 2pi/3: cos(phiB - phiC) = cos(-pi/3 - 2pi/3) = cos(-pi) = -1.
# Equation: rC^2 + 1 = 4 rC * (-1)? Negative => no positive rC solution.

# Try second equation: cos(phiB - phiC - 2pi/3) = cos(phiB - phiC + 2pi/3)
# phiB - phiC - 2pi/3 = -(phiB - phiC + 2pi/3) mod 2pi
# 2(phiB - phiC) = 0 mod 2pi => phiB - phiC = 0 or pi.
# phiC = phiB = -pi/3: C orbit aligns with B orbit. Degenerate.
# phiC = phiB - pi = -pi/3 - pi = -4pi/3 = 2pi/3 (mod 2pi).
# cos(phiB - phiC) = cos(-pi) = -1. As above no soln.

# So with the symmetric rB=2, phiB=-pi/3 choice, the only way to lift A_0
# to E=4 via radius sqrt(3) gives a degenerate C orbit.

# Alternative: at A_0, choose 4 equidistant witnesses from a different radius, e.g.,
# {B_0, B_1, C_0, C_1} all equal but at radius != sqrt(3)*rA.
# Then sister A pair contributes 2 at sqrt(3)*rA, and we'd need them to NOT count toward E=4.
# But E=4 = 4 equidistant; we still want any 4. So {B_0, B_1, C_0, C_1} must be at one radius r, with r != sqrt(3)*rA OK.
# Then E(A_0) = max(2, 4) = 4. Good.
# Similarly need E=4 at B_0 and C_0.

# At A_0:
# d(A_0, B_0)^2 = d(A_0, B_1)^2 => cos(phiB) = cos(phiB+2pi/3) => phiB = -pi/3 or 2pi/3 (as before).
# Same for C: phiC = -pi/3 or 2pi/3.
# If both phiB=phiC=-pi/3, then B and C orbits ALIGN (same angles), so C_k and B_k are radial.
# Need d(A_0, B_0) = d(A_0, B_1) = d(A_0, C_0) = d(A_0, C_1) at the SAME value.
# d(A_0, B_0)^2 = 1 + rB^2 - rB
# d(A_0, C_0)^2 = 1 + rC^2 - rC
# Set equal: rB^2 - rB = rC^2 - rC => (rB - rC)(rB + rC - 1) = 0.
# So rB = rC (orbits coincide if also phiB = phiC, which we have) OR rB + rC = 1.
# rB + rC = 1 with both positive and != 0: e.g., rB = 0.7, rC = 0.3.
# But rA = 1 and we need orbit B and C distinct from A. With phiB = phiC = -pi/3,
# B at angle -pi/3, A at angle 0. So they're at different angles. OK.

# Check: with rA=1, phiA=0, rB=0.7, phiB=-pi/3, rC=0.3, phiC=-pi/3.
# What about phiB = phiC means same direction. If we DON'T allow phiB=phiC, we need
# phiB and phiC each = -pi/3 OR 2pi/3 INDEPENDENTLY.
# Try phiB = -pi/3, phiC = 2pi/3. Then orbits B and C are at angles {-pi/3, pi/3, pi} and {2pi/3, 4pi/3=−2pi/3, 0}.
# But angle 0 in C overlaps with A_0 at angle 0!
# Wait C_0 at angle phiC = 2pi/3, C_1 at 2pi/3+2pi/3 = 4pi/3 = -2pi/3, C_2 at 2pi/3-2pi/3 = 0.
# C_2 at angle 0 with radius rC. A_0 at angle 0 with radius 1. They're collinear from origin
# but different radii (if rC != 1). So they coincide only if rC = 1.
# OK so phiC = 2pi/3 with rC != 1 works.

# But wait we wanted d(A_0, C_0)^2 = d(A_0, C_1)^2.
# With phiC = 2pi/3, cos(phiC) = -1/2, cos(phiC + 2pi/3) = cos(4pi/3) = -1/2,
# cos(phiC - 2pi/3) = cos(0) = 1.
# So d(A_0, C_0)^2 = d(A_0, C_1)^2 = 1 + rC^2 - 2*rC*(-1/2) = 1 + rC^2 + rC
# d(A_0, C_2)^2 = 1 + rC^2 - 2*rC*1 = (1-rC)^2.

# So at A_0, with phiB=-pi/3, phiC=2pi/3:
# distances squared:
#  to A_1, A_2: 3 (sqrt(3))
#  to B_0, B_1: 1 + rB^2 - rB
#  to B_2: (1+rB)^2
#  to C_0, C_1: 1 + rC^2 + rC
#  to C_2: (1-rC)^2

# For E=4 at A_0, need 4 equal. Possibilities:
#  3 = 1+rB^2-rB AND 3 = 1+rC^2+rC: gives 4 with the A pair.
#    rB^2 - rB - 2 = 0 => rB = 2 (positive root)
#    rC^2 + rC - 2 = 0 => rC = 1 (positive root). But rC = rA = 1 -> orbits coincide if same angles.
#    A_0 at angle 0, A_1 at 2pi/3, A_2 at -2pi/3. C orbit at 2pi/3, -2pi/3, 0.
#    So C_0 = A_1, C_1 = A_2, C_2 = A_0! Total degeneracy.
# So 3 = both gives degenerate.

# Alternative: 4 equal NOT including the A_1, A_2 pair.
#  e.g., 1+rB^2-rB = 1+rC^2+rC = (1-rC)^2 (4 elements: B_0, B_1, C_0, C_1, missing... wait we have only 8 vertices).
# Let me list all 8 distances more carefully.

print("\nCount of distances to enforce E=4 at A_0:")
print("8 distances (by symmetric counts): {3, 3, dB1, dB1, dB2, dC1, dC1, dC2}")
print("where dB1=1+rB^2-rB, dB2=(1+rB)^2, dC1=1+rC^2+rC, dC2=(1-rC)^2")
print()
# To get E=4 we need ANY 4 to coincide.
# Already have multiplicities: 2 (the A pair), 2 (B_0=B_1), 1, 2 (C_0=C_1), 1.
# Combine 2-grp + 2-grp at same value: e.g.,
#   3 = dB1 AND 3 = dC1: degenerate (as above).
#   dB1 = dC1: possible without involving A_pair. 1+rB^2-rB = 1+rC^2+rC -> rB^2-rB = rC^2+rC ->
#     (rB-rC)(rB+rC) = rB+rC -> if rB+rC != 0: rB - rC = 1. So rB = rC + 1.
#   With rB = rC+1, the 4-element witness set at A_0 = {B_0, B_1, C_0, C_1}, all at distance sqrt(1+rC^2+rC).

# Now check E=4 at B_0:
# B_0 at angle phiB = -pi/3, radius rB.
# Distances squared:
#  to B_1, B_2: 3 rB^2 (sister distances)
#  to A_k: 1 + rB^2 - 2 rB cos(angle of A_k - phiB) where A_k at 2pi*k/3 - phiB = 2pi*k/3 + pi/3.
#    cos values: cos(pi/3) = 1/2, cos(pi) = -1, cos(-pi/3) = 1/2. So 2 with cos=1/2 (A_0, A_2) and 1 with cos=-1 (A_1).
#  to C_k: rB^2 + rC^2 - 2 rB rC cos(phiC - phiB - 2pi k/3)
#    phiC - phiB = 2pi/3 - (-pi/3) = pi. So cos(pi - 2pi k/3) for k=0,1,2: cos(pi)=-1, cos(pi-2pi/3)=cos(pi/3)=1/2, cos(pi+2pi/3)=cos(5pi/3)=1/2.
#    So 2 with cos=1/2 and 1 with cos=-1.

# Distances at B_0:
#  3 rB^2 (×2)
#  1+rB^2 - rB (×2, from A_0,A_2)
#  (1+rB)^2 (×1, from A_1)
#  rB^2 + rC^2 + 2 rB rC (×1, from C_0)  [cos = -1, distance squared = (rB+rC)^2]
#  rB^2 + rC^2 - rB rC (×2, from C_1, C_2)  [cos=1/2]

# For E=4 at B_0: need 4 equal.
# Multiplicities are 2, 2, 1, 1, 2.
# Pair candidates: combine a 2-grp and another 2-grp:
#   3 rB^2 = 1+rB^2-rB: 2rB^2 + rB - 1 = 0 -> rB = (-1+sqrt(1+8))/4 = 2/4 = 1/2. So rB = 1/2.
#   3 rB^2 = rB^2+rC^2 - rB*rC: 2rB^2 + rB*rC - rC^2 = 0.
#   1+rB^2 - rB = rB^2 + rC^2 - rB rC: 1 - rB = rC^2 - rB rC -> 1 - rB = rC(rC - rB) -> with rB = rC+1: 1-(rC+1) = rC(rC-rC-1) -> -rC = -rC. ALWAYS HOLDS!

print("=== KEY: with rB = rC+1, equation '1+rB^2-rB = rB^2+rC^2-rB*rC' is identically true ===")
print()
# So at B_0: with rB = rC + 1, we automatically get 4 equal at distance sqrt(1+rB^2-rB) = sqrt(1+rC^2+rC) (same as A_0 lift).
# Multiplicity at B_0:
#  - (A_0, A_2): 2 elements at distance sqrt(1+rB^2-rB)
#  - (C_1, C_2): 2 elements at distance sqrt(rB^2+rC^2-rB*rC)
# These are equal under rB = rC+1!
# So {A_0, A_2, C_1, C_2}: 4 at one radius! E(B_0) = 4. EXCELLENT!

# Now check E=4 at C_0:
# C_0 at angle phiC = 2pi/3, radius rC.
# Distances squared:
#  to C_1, C_2: 3 rC^2
#  to A_k: 1 + rC^2 - 2 rC cos(angle A_k - phiC) where A_k at 2pi k/3 - 2pi/3 = 0 (k=1), 2pi/3 (k=2), -2pi/3 (k=0).
#    cos(0)=1, cos(2pi/3)=-1/2, cos(-2pi/3)=-1/2. So multiplicities 1 (k=1) at cos=1, 2 (k=0,2) at cos=-1/2.
#  to B_k: rB^2 + rC^2 - 2 rB rC cos(phiB - phiC - 2pi k/3) where phiB - phiC = -pi/3 - 2pi/3 = -pi.
#    cos(-pi - 2pi k/3) for k=0,1,2: cos(-pi) = -1, cos(-pi - 2pi/3) = cos(-5pi/3) = cos(pi/3) = 1/2,
#    cos(-pi - 4pi/3) = cos(-7pi/3) = cos(-7pi/3 + 2pi) = cos(-pi/3) = 1/2.
#    So 1 at cos=-1 (B_0), 2 at cos=1/2 (B_1, B_2).

# Distances squared at C_0:
#  3 rC^2 (×2)
#  (1-rC)^2 (×1, from A_1) [cos=1]
#  1 + rC^2 + rC (×2, from A_0, A_2) [cos=-1/2]
#  (rB+rC)^2 (×1, from B_0) [cos=-1]
#  rB^2 + rC^2 - rB*rC (×2, from B_1, B_2) [cos=1/2]

# Pair candidates: combine 2-grps:
#   3 rC^2 = 1 + rC^2 + rC: 2rC^2 - rC - 1 = 0 -> rC = (1+3)/4 = 1.
#   3 rC^2 = rB^2 + rC^2 - rB rC: 2rC^2 + rB*rC - rB^2 = 0.
#   1+rC^2+rC = rB^2 + rC^2 - rB rC: 1+rC = rB^2 - rB*rC -> with rB = rC+1: rB^2 - rB*rC = (rC+1)^2 - (rC+1)*rC = rC^2 + 2rC + 1 - rC^2 - rC = rC + 1. CHECK: equals 1 + rC. YES!

# So with rB = rC+1, the equation '1+rC^2+rC = rB^2+rC^2-rB*rC' holds!
# Then at C_0: 4 equal: (A_0, A_2, B_1, B_2) at radius sqrt(1+rC^2+rC). E(C_0) = 4!

print("MIRACULOUS: 3-fold symmetric n=9 with phiA=0, phiB=-pi/3, phiC=2pi/3, rA=1, rB=rC+1 gives E=4 at all vertices!")
print("This holds for ANY rC > 0 (one-parameter family).")
print()

# Convexity check: are the 9 points in convex position for all rC > 0?
# Vertices on three concentric circles at radii rA=1, rB=rC+1, rC.
# We need rC > 0. If rC < 1, then C is innermost and A is between. If 1 < rC < rB,
# A is innermost. We need all 9 on convex hull = a convex 9-gon.
# That means each circle's points must lie on the convex hull, i.e., none of the
# inner circle's points can lie on the line/inside the outer triangles.

# Strict convexity: the 9 vertices in cyclic angular order must form a convex polygon.
# Since they're on 3 different circles, this is a non-trivial geometric constraint.

# Let me verify numerically for rC = 0.5 (so rB = 1.5):
def make_pts(rC):
    rA = 1.0
    rB = rC + 1
    phiA, phiB, phiC = 0.0, -math.pi/3, 2*math.pi/3
    pts = []
    for k in range(3):
        a = phiA + 2*math.pi*k/3
        pts.append((rA*math.cos(a), rA*math.sin(a)))
    for k in range(3):
        a = phiB + 2*math.pi*k/3
        pts.append((rB*math.cos(a), rB*math.sin(a)))
    for k in range(3):
        a = phiC + 2*math.pi*k/3
        pts.append((rC*math.cos(a), rC*math.sin(a)))
    return np.array(pts)

for rC_test in [0.1, 0.3, 0.5, 0.8, 1.5, 2.0]:
    P = make_pts(rC_test)
    # Verify E values
    D = np.linalg.norm(P[:,None]-P[None,:], axis=-1)
    print(f"\nrC={rC_test}, rB={rC_test+1}:")
    for v in range(9):
        ds = sorted([(D[v,j], j) for j in range(9) if j != v])
        # Group by tolerance
        groups = []; cur_d, cur = ds[0][0], [ds[0][1]]
        for d, j in ds[1:]:
            if abs(d - cur_d) < 1e-9:
                cur.append(j)
            else:
                groups.append((cur_d, cur)); cur_d, cur = d, [j]
        groups.append((cur_d, cur))
        sizes = [len(g[1]) for g in groups]
        print(f"  v{v}: sizes={sizes}, max E = {max(sizes)}")
    # Convexity
    c = P.mean(0)
    angles = np.arctan2(P[:,1]-c[1], P[:,0]-c[0])
    order = np.argsort(angles)
    Q = P[order]
    crosses = []
    for i in range(9):
        a, b, d = Q[i], Q[(i+1)%9], Q[(i+2)%9]
        v1 = b-a; v2 = d-b
        crosses.append(v1[0]*v2[1] - v1[1]*v2[0])
    print(f"  cyclic order: {order.tolist()}")
    print(f"  cross products: {[round(x,4) for x in crosses]}")
    print(f"  convex strict: {all(c > 0 for c in crosses)}")
    if not all(c > 0 for c in crosses):
        print(f"  min cross: {min(crosses)}")
