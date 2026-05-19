# Diameter-Lens Local Lemmas

Status: `LOCAL_LEMMA_NOTE` / `REVIEW_PENDING`.

This note extracts local diameter geometry from the 2026-05-19 research batch.
It is not a proof of Erdos Problem #97 and does not claim that the diameter
endpoint reduction is closed. Its main point is the opposite: the endpoint
lemmas are useful, but the double-boundary package alone is sharp and
geometrically realizable.

Throughout, `S_v` denotes a chosen selected 4-witness row, not the full rich
distance class at `v`.

## Setup

Let `{A,B}` be a global diameter pair of length `D`, normalized as

```text
A = (-D/2, 0),  B = (D/2, 0).
```

Every vertex lies in the lens

```text
B(A,D) cap B(B,D).
```

For boundary witnesses on the two diameter circles, write

```text
R(theta) = A + D (cos theta, sin theta),
L(phi)   = B + D (-cos phi, sin phi).
```

The selected-diameter lemmas use angles in `[-pi/3, pi/3]` after the pinching
lemma below.

## Lemma 1: Diameter-Circle Pinching

If `B in S_A`, then the selected radius at `A` is `D`, so every selected
witness in `S_A` lies on `C(A,D)`. For two witnesses with angular separation
`Delta` around `A`,

```text
|xy| = 2D sin(Delta/2).
```

Since `D` is the global diameter, `|xy| <= D`, so `Delta <= pi/3`. Thus the
selected diameter witnesses from `A` lie in a closed angular interval of width
at most `pi/3`. The same statement holds at `B`.

## Lemma 2: Mutual Selected-Diameter Overlap

If `B in S_A` and `A in S_B`, then the non-endpoint selected witness overlap
has size at most one:

```text
|(S_A cap S_B) \ {A,B}| <= 1.
```

A common non-endpoint witness lies in `C(A,D) cap C(B,D)`, which consists of
the two equilateral apexes over `AB`. Those two apexes are distance
`sqrt(3)D > D` apart, so both cannot occur in a diameter-`D` point set.

## Lemma 3: Seven-Vertex Lower Bound

If both endpoint rows select the diameter radius and contain the opposite
endpoint, then

```text
|{A,B} union S_A union S_B| >= 7.
```

Indeed, each endpoint row contributes the other endpoint and three
non-endpoint witnesses, and Lemma 2 allows at most one non-endpoint overlap:

```text
2 + (3 + 3 - 1) = 7.
```

## Lemma 4: Same-Side Constraint

For `theta, phi in [-pi/3, pi/3]`,

```text
|R(theta) - L(phi)| <= D  iff  theta*phi >= 0.
```

After dividing by `D^2`,

```text
|R(theta)-L(phi)|^2 / D^2
  = (cos theta + cos phi - 1)^2 + (sin theta - sin phi)^2
  = 3 + 2 cos(theta+phi) - 2 cos theta - 2 cos phi.
```

Thus `|R(theta)-L(phi)| <= D` is equivalent to

```text
1 + cos(theta+phi) <= cos theta + cos phi.
```

Using sum-to-product and the positivity of `cos((theta+phi)/2)` on the stated
range, this becomes

```text
cos((theta+phi)/2) <= cos((theta-phi)/2),
```

which is equivalent on this interval to

```text
|theta+phi| >= |theta-phi|,
```

and hence to `theta*phi >= 0`.

## Sharp Negative Control

The double-boundary same-side and seven-vertex lemmas do not themselves force
a contradiction.

Normalize `D = 1`, `A = (-1/2,0)`, `B = (1/2,0)`. For
`0 < alpha < beta < pi/3`, set

```text
L(t) = B + (-cos t, sin t),
R(t) = A + ( cos t, sin t),
E    = L(pi/3) = R(pi/3).
```

The seven points

```text
A, L(alpha), L(beta), E, R(beta), R(alpha), B
```

in cyclic order form a strictly convex diameter-lens cap. The endpoint rows

```text
S_A = {B, R(alpha), R(beta), E},
S_B = {A, L(alpha), L(beta), E}
```

both select the diameter radius, have exactly one non-endpoint common witness
`E`, and attain the seven-vertex lower bound. Same-arc distances are chords of
angular width less than `pi/3`, and cross-arc distances are controlled by the
same-side lemma, so all pairwise distances are at most `1`.

This skeleton is not 4-bad. It only disproves the local reading that endpoint
geometry plus strict convexity already gives a contradiction. A proof must use
the witness rows at the boundary witnesses or another exact certificate.

## Full-Class Branching Caution

A missing selected edge is not evidence of diameter-poorness. For a diameter
pair `{v,u}`, define the full diameter class

```text
M_v(u) = {x != v : |vx| = |vu|}.
```

If `|M_v(u)| >= 4`, a selected row can be chosen at the diameter radius and can
be chosen to include `u`; this is a full-class branch. If `|M_v(u)| <= 3`,
then every selected row at `v` has radius strictly smaller than the diameter,
and any linear certificate for this branch must preserve that strictness.

The poor-endpoint branch does not automatically imply angular pinching. If the
selected radius is at most `D/2`, every chord of the selected circle already
has length at most `D`.

## Boundary-Witness Isolation

This review-pending local lemma is a possible finite-pruning ingredient.

Let `D = 1`, `A = (0,0)`, `B = (1,0)`, and

```text
K^+ = B(A,1) cap B(B,1) cap {y >= 0}.
```

If `R(theta) = (cos theta, sin theta)` with `0 < theta < pi/3`, and
`X in K^+` satisfies

```text
|X - R(theta)| = 1,
```

then `X = A`.

The boundary check is elementary: on `AB`, equality forces the segment
parameter to be `0`; on the same right arc, all chord gaps are strictly less
than `pi/3`; and on the opposite left arc, the same-side formula gives equality
only at the endpoint angle `0`. The squared distance to `R(theta)` is convex,
so no interior point of the convex half-lens can have a larger value than the
boundary maximum.

Consequence: if a noncommon upper right-arc witness `R` reciprocates the
selected edge `A <-> R`, then `R`'s selected radius is the diameter, and its
other three diameter witnesses must lie below the line `AB`. This is not a
standalone obstruction and does not apply to the common equilateral apex.
