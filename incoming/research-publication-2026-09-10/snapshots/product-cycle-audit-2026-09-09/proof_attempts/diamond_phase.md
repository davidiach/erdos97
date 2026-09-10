# Circle-completion phase equations and a two-diamond obstruction

Date: 9 September 2026. **Restricted written proof, expert review pending.**
This is not a proof of unrestricted Erdos #97 or of the entire nine-orbit case.

## 1. Hypotheses and the reusable equation

Let omega=exp(2*pi*i/3), and T(z)={z,omega*z,omega^2*z}. Let the union of
finitely many distinct nonzero orbits T(z_i) be in strictly convex position.
Choose the representatives in one angular sector of width L=2*pi/3, in
strict increasing phase order theta_0<...<theta_(m-1)<theta_0+L.

This phase normalization is legitimate: two distinct orbits cannot have a
vertex on the same ray, since the smaller radial point would lie in the
other triangle. The origin is inside every nondegenerate orbit triangle.

Write i -(g)-> j when |z_i-omega^g z_j|^2=3|z_i|^2. These are SOURCE-side
radii, not a common distance and not arbitrary rich radii.

Suppose i,j,k,l are distinct orbit labels and the four arrows are

    i -(a)-> j,  i -(b)-> k,  j -(c)-> l,  k -(d)-> l,
    a+c = b+d (mod 3).

Then put g=b-c (mod 3), and sigma(0)=0, sigma(1)=1, sigma(2)=-1. We prove

    z_i z_l = omega^g z_j z_k,                              (1)
    theta_i+theta_l-theta_j-theta_k = sigma(g) L.           (2)

The gain alignment is indispensable. We do not use (1) for unmatched gains.
The identity holds for a local diamond in an arbitrary larger graph; no full
rectangular grid, equal radii, recurrence, or initial product parametrization
is assumed.

## 2. Circle-intersection completion, including the exceptional branch

The completion identity itself is retained in PR #942, `product_component.md`,
Section 3, at source commit 9b8b8f807ae8b21f10780a7d11f6c5cec65f26e7
(Git blob 2ccb3e6eb195eaad77f780d2fc56c4dd744636d0). Here it is restated,
then translated to a general gain-labelled phase equation.

For distinct representatives x,A,B,C satisfying

    |A-x|^2=|B-x|^2=3|x|^2,
    |C-A|^2=3|A|^2,   |C-B|^2=3|B|^2,

normalize x=1 by a complex similarity. Both AB and -2 lie on the two
last circles. Indeed |AB-A|^2=|A|^2 |B-1|^2=3|A|^2; likewise for B.
The first equation gives |A+2|^2=3|A|^2, and similarly for B.
The circles have distinct centers A and B, so have at most two common points.
Thus C=AB or C=-2. This remains valid at tangency or if the displayed roots
coincide; no other root is introduced.

If C=-2x, then x=(omega*C+omega^2*C)/2. The two endpoints are distinct
vertices of T(C), making x nonextreme. Strict convexity therefore removes
this branch, proving C=AB/x.

For the gain-labelled diamond use x=z_i, A=omega^a z_j, B=omega^b z_k,
C=omega^(a+c) z_l. Gain alignment makes this last physical point serve
both circles. Division gives (1).

For (2), the left side belongs strictly to (-2L,2L), since all representatives
lie in one sector of width L. It equals gL modulo 2*pi=3L by (1).
Only 0, L, -L, respectively, have this property in that open interval.
The alternatives +/-2L are endpoints and are excluded, not silently included.
This proves (2) without a discrete angle grid or numerical branch choice.

Consequently a chord-angle model with q_i=3*theta_i plus one shared constant
may append the integer equality

    q_i+q_l-q_j-q_k-2*sigma(g)*pi=0.

This is an additional geometric consequence, not one of the original
selected isosceles equalities by itself.

## 3. A two-diamond cancellation

The following seven arrows occur in each of the three newly found linear
relaxation survivors (labels not shown play no role):

    0 -(1)-> 1,  0 -(1)-> 2,
    1 -(1)-> 6,  2 -(1)-> 6,
    2 -(1)-> 8,
    6 -(2)-> 3,  8 -(2)-> 3.

The two diamonds are (0,1,2,6) and (2,6,8,3). Equation (1) gives

    z_0 z_6 = z_1 z_2,
    z_2 z_3 = omega^2 z_6 z_8.

Every factor is nonzero. Cancelling yields

    z_0 z_3 = omega^2 z_1 z_8.                             (3)

The sector order is 0<1<3<8 (the positions of 2 and 6 are irrelevant to
this final step). The quotient z_3/z_1 has argument strictly between 0 and L.
The quotient omega^2 z_8/z_0 has its corresponding argument strictly between
-L and 0. They cannot be equal. This contradicts (3).

Equivalently the phase equations sum to

    (theta_3-theta_1)+(L-theta_8+theta_0)=0,

although both summands are strictly positive. This is the four-term exact
integer certificate checked by `verify/diamond_phase.py`: two strict order
premises, minus the two diamond equalities, cancel identically.

The proof is not an all-order exclusion of the abstract seven-arrow graph:
the indicated phase order and gains matter. It is also not a claim that every
all-rich graph contains two such diamonds.

## 4. Why this is not just another numerical LP rejection

For each of the three full nine-orbit systems, separately retained rational
vectors satisfy BOTH of the previously used linear relaxations:

* 8,775 positive physical-triangle angles, all forced isosceles equalities,
  all 18 own-side right angles and direct strict radius/angle orders;
* 99 positive ordinary-distance classes, 35,100 strict Kalmanson inequalities,
  8,775 strict triangle inequalities, maximum-root weak bounds, direct radius
  orders, and the new supplier-arc radius implications.

`verify/check_positive_relaxations.py` recomputes each condition in rational
arithmetic. The positive margins are not merely a solver tolerance. The angle
and distance assignments are SEPARATE vectors: they are not asserted to be
one joint Euclidean realization.

The three angle minima are 1/282, 1/265, 1/261 in the checker's normalized rows.
The distance minima are 1/13856, 1/14045, 1/22123 with the sum of quotient
class distances normalized to one. The new diamond equations reject all three.

Before discovering (3), 90 numerical phase-cycle realizations were attempted.
They approached coincident orbit labels and nonconvex shapes. Small residuals
were caused by degeneration, not certified solutions. The exact proof now
removes all strictly convex realizations of these specified systems, rather
than merely the numerically visited component.

## 5. Positive and negative controls

A genuine convex 12-point diamond is checked in the packet, using

    U(t)=(1-t^2+2it)/(1+t^2),
    a=1+sqrt(3)U(8/3), b=1+sqrt(3)U(5/2),
    T(1) union T(a) union T(b) union T(ab).

All 120 supporting halfplanes and all pair distances are exact in Q(sqrt(3)).
Thus a diamond is not prohibited merely by its existence. Only an incompatible
combination of its forced phase identities and order is prohibited.

An exact 18-point same-upper-half-plane six-cycle also closes with monodromy
omega, but has twelve strict interior points. It protects against extending
#942's three-cycle monodromy contradiction to all cycle lengths.

## 6. Remaining unrestricted obligation

Neither all-richness nor cardinal minimality has been proved to force these
gain-aligned diamonds or the phase contradiction. Arbitrary witnesses need not
be parts of equilateral triangles at all. The complete unrestricted Erdos #97
success condition remains unmet.
