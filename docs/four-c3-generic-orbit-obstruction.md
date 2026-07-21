# Four generic concentric equilateral-triangle orbits

Status: `LEMMA` draft / exact restricted-family obstruction (review pending).

This note rules out one structured counterexample family for Erdos Problem
#97.  It is not a proof of the general problem, does not rule out the
half-step branches described below, and does not produce a counterexample.

## Statement

Let `O` be a point in the Euclidean plane.  For `i = 0,1,2,3`, let

```text
T_i = { O + r_i exp(I(phi_i + 2*pi*k/3)) : k = 0,1,2 },
```

where `r_i > 0`.  Suppose that the twelve points in the four orbits are
distinct and are the vertices of a strictly convex polygon.  Assume also that
no two orbit phases differ by a half-step:

```text
phi_j - phi_i != pi/3  (mod 2*pi/3),  i != j.
```

Then the twelve-point set is not 4-bad: at least one vertex has no four other
vertices at one common positive distance.

In fact the proof shows that, under the hypotheses, it is impossible for all
four orbit representatives to be 4-rich.

## Aligned phases are already excluded by convexity

First note that two distinct orbits cannot have

```text
phi_j - phi_i = 0  (mod 2*pi/3).
```

If their radii are equal, the two orbits coincide.  If their radii are
different, a point of the smaller orbit lies strictly between `O` and the
corresponding point of the larger orbit.  The center `O` is an interior point
of the convex hull because it is the center of each equilateral triangle.
Consequently the smaller radial point is an interior point of the full convex
hull, contradicting the assumption that all twelve points are vertices.

Thus every pairwise phase difference is generic: it is neither `0` nor
`pi/3` modulo `2*pi/3`.

## Atom shape at a representative

Fix a representative `A_0` of an orbit `T_i`.  Its two orbit-mates are both at
squared distance `3 r_i^2` from `A_0`.

For a different orbit `T_j`, the three squared distances from `A_0` have the
form

```text
r_i^2 + r_j^2 - 2 r_i r_j cos(delta + 2*pi*k/3),  k = 0,1,2.
```

Two of these values are equal only if

```text
delta = 0 or pi/3  (mod 2*pi/3).
```

Both possibilities were excluded above.  Hence each of the other three
orbits contributes at most one point to any circle centered at `A_0`.

It follows that a circle through four other vertices must contain the two
orbit-mates of `A_0`, plus one vertex from each of two distinct supplier
orbits.  Its squared radius is necessarily `3 r_i^2`.

If every orbit representative is 4-rich, choose two supplier orbits for each
representative and draw directed arcs `i -> j` to them.  This gives eight
directed arcs on four labels.  There are only six unordered label-pairs, so
some pair carries both orientations, say `i -> j` and `j -> i`.

## Reciprocal-supplier lemma

We show that such a reciprocal pair forces `T_i = T_j`.

Normalize `r_i = 1`, put `rho = r_j/r_i > 0`, and let `alpha` be the angular
difference for the selected `T_j` witness in the `T_i` row.  If the selected
reverse witness has index shift `ell`, then its angular difference is

```text
2*pi*m/3 - alpha,  where m in {0,1,2}.
```

The two selected-distance equalities are

```text
rho^2 - 2*rho*cos(alpha) = 2,
1 - 2*rho*cos(2*pi*m/3 - alpha) = 2*rho^2.       (1)
```

If `m = 0`, the two cosine terms are equal.  Subtracting the two forms of
`2*rho*cos(alpha)` gives `rho^2 = 1`, and then
`cos(alpha) = -1/2`.

If `m = 1`, equation (1) gives

```text
cos(alpha) = (rho^2 - 2)/(2*rho),
sin(alpha) = -sqrt(3)*rho/2.
```

The identity `cos(alpha)^2 + sin(alpha)^2 = 1` reduces exactly to

```text
(rho^2 - 1)^2 / rho^2 = 0.
```

Thus `rho = 1`.  The case `m = 2` is the reflected calculation and gives
`sin(alpha) = +sqrt(3)*rho/2`, with the same square identity and conclusion.

In every case `rho = 1` and `alpha` is a multiple of `2*pi/3`.  Undoing the
selected witness index shift shows

```text
phi_j - phi_i = 0  (mod 2*pi/3).
```

Equal radii then make `T_i` and `T_j` the same orbit, contrary to the twelve
points being distinct.  This contradiction proves the statement.

## A half-step row reduction

Although the full half-step branches remain open, one tempting escape row is
impossible immediately.  Suppose `T_i,T_j` are half-step partners and a row
centered at a vertex of `T_i` consists of its two orbit-mates together with
the symmetric pair from `T_j`.  Put `t=r_j/r_i`.  Equality of the own-pair
and cross-pair squared distances is

```text
3 r_i^2 = r_i^2 + r_j^2 - r_i r_j,
```

or

```text
t^2 - t - 2 = (t - 2)(t + 1) = 0.
```

Positivity forces `t=2`.  But the two selected `T_j` witnesses have angular
offsets `+pi/3` and `-pi/3`, so their midpoint is exactly the `T_i` center
vertex.  That vertex is not extreme, contradicting strict convexity.

Consequently a half-step-rich row cannot be made from the own pair plus the
partner pair.  The still-open escape shape uses the partner pair together
with one singleton from each of two other orbits; reciprocal rows involving
that different radius are not covered by the lemma above.

## Exact replay

The companion checker replays the three reciprocal cases symbolically:

```bash
python scripts/check_four_c3_generic_orbit_obstruction.py --assert-expected --json
```

It verifies the cosine-elimination identities and the half-step midpoint
factorization; it is a check of these algebraic reductions, not an exhaustive
solver for arbitrary twelve-point configurations.

## Scope boundary

The half-step hypothesis is essential to this proof.  If
`phi_j - phi_i = pi/3 mod 2*pi/3`, two witnesses from `T_j` can form one
cross-orbit distance pair.  A rich row can then use that pair instead of its
own two orbit-mates, and the directed outdegree-two argument no longer
applies.  Half-step partners form a matching among the four orbits, but the
one-pair and two-pair branches require additional analysis.

The result also says nothing about partial triangle orbits, triangles with
different centers, other orbit sizes, or arbitrary strictly convex polygons.
