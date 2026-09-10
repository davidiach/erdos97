# A supplier arc forces radial lifting

**All-size restricted geometric lemma; written proof, independent expert review
pending.** The hypothesis is concentric equilateral-triangle orbits and their
own-side radii, not arbitrary rich vertices of a convex polygon.

Let omega=exp(2*pi*i/3). Let A,B,C,D be representatives of four distinct
nonzero C3 orbits in this phase order in one sector shorter than 2*pi/3.
Suppose their entire union is strictly convex and

    |B-A|^2=3|B|^2,    |B-omega^2 C|^2=3|B|^2.             (1)

Then

    |C|<|A|,     |D|>|C|,                                (2)
    |C-omega D|^2>3|C|^2.                                (3)

Every intervening D satisfies this; it need not be rich or select a radius.
Hence the three arrows B->A (gain 0), B->C (gain 2), C->D (gain 1) are
impossible in this sector order. Similarities, cyclic relabelling and reflection
give the corresponding versions in other sectors and orientations.

## Proof

Normalize B=1. Write A=r_A exp(-i alpha), C=r_C exp(i gamma),
D=r_D exp(i delta), where alpha,gamma,delta>0, gamma<delta and
alpha+delta<2*pi/3.

For every two distinct orbit representatives x,y in a strictly convex union,
|y|<2|x|: otherwise T(y), whose inradius is |y|/2, contains x. Equality would
also make x nonextreme. In particular r_A,r_C<2.

The equation |r exp(i theta)-1|^2=3 is equivalent to
cos(theta)=r/2-1/r. Thus r<2 forces cos(theta)<1/2.
For the first arrow, 0<alpha<2*pi/3, so alpha>pi/3. For the second arrow,
0<gamma<2*pi/3 and theta=gamma-2*pi/3, so gamma<pi/3.
Set beta=2*pi/3-alpha. We obtain

    0<gamma<delta<beta<pi/3.

Both C and A'=omega A lie on the right arc of Gamma: |z-omega|^2=3,
with their polar arguments gamma and beta. Parametrize this arc by

    X(t)=(-1/2+sqrt(3)cos t, sqrt(3)/2+sqrt(3)sin t),
    -pi/6<t<pi/6.

It goes from 1 to E=(1,sqrt(3)). Its polar argument strictly increases, since
cross(X,X')=3+sqrt(3)cos(t-2*pi/3)>0. Its squared norm strictly increases,
since its derivative is -2sqrt(3)sin(t-2*pi/3)>0 on this interval.
Therefore |C|<|A'|=|A|.

We need a chord bound rather than only radial monotonicity. Put c=C=X(t_c)
and F(t)=c dot (X(t)-c), for t_c<=t<=pi/6. On this interval

    F''(t)=-sqrt(3)(c_x cos t+c_y sin t)<0,

because the difference of t and the polar argument gamma of c lies strictly
between -pi/2 and pi/2. Further, F(t_c)=0. The circle equation gives
|c|^2=2-c_x+sqrt(3)c_y, hence

    F(pi/6)=c dot(E-c)=2(c_x-1)>0.

Here c_x>1 follows immediately from the parametrization on the open arc.
Concavity now gives F(t)>0 for every t_c<t<=pi/6. In particular
c dot(A'-c)>0.

The ray at argument delta meets the open segment c A' at some Y, since
its argument is strictly between gamma and beta and their difference is
less than pi. Then c dot Y>|c|^2, and Cauchy-Schwarz implies |Y|>|c|.
If |D|<=|c|, D lies strictly between 0 and Y. The origin is interior to T(B),
while Y lies on c A'. Such D is an interior/nonextreme point of the existing
convex hull, contradiction. Thus |D|>|C|.

Finally the angle from C to omega D is
2*pi/3+(delta-gamma), strictly between 2*pi/3 and pi. Therefore

    |C-omega D|^2
      > |C|^2+|D|^2+|C||D|
      > 3|C|^2,

which proves (3). No limiting parameter, nonstrict convexity, or assumed
richness at D was used.

## Exact calibration and non-vacuity

The packet's `supplier_arc_positive_12` uses
Q(t)=omega+(1-omega)U(t), U(t)=(1-t^2+2it)/(1+t^2), and

    A=omega^2 Q(3/100), B=1, C=Q(1/100),
    D=(100000001/100000000) Q(1/50).

All 12 points in their orbits are strictly convex, both equalities (1) hold,
and both strict conclusions are checked exactly in Q(sqrt(3)). The remaining
source arrow is not imposed. The norm of D is still below that of A, so this
control does not support replacing |D|>|C| by |D|>|A|.

An independent integer chord-angle certificate for the three-arrow corollary
is retained in `reports/three_arrow_core_basic.json`. It uses only positive
triangle angles and forced isosceles equalities, not explicit right-angle or
radius-order rows. The all-size radial conclusion above is the written proof,
not an extrapolation from that finite certificate.
