# Rigid `n=15` Moser geometry

Status: `CONDITIONAL_LEMMA_PACKET`.

This note records two exact deductions conditional on the all-large-caps
tri-apex hypotheses below at their rigid equality boundary `|A| = 15`.  Those
geometric hypotheses are not independently established by this packet:

1. the Moser triangle cannot have a uniquely shortest side;
2. the fully symmetric three-full-cap case is impossible, because it places the
   carrier on a Reuleaux-triangle boundary where every non-apex point has
   distance multiplicity at most two.

Neither result proves Erdős Problem 97, treats `|A| > 15`, or closes the other
active unique-radius terminal.  The purpose is to remove two genuine geometric
branches and expose the remaining mixed one-/two-radius configurations.

The stored finite-algebra report is regenerated and checked by

```bash
python scripts/check_rigid_n15_shortest_side_grid.py --artifact data/certificates/rigid_n15_shortest_side_grid.json --check --assert-expected --json
```

This checks only branch counts and integer Kalmanson coefficient cancellation.

## 1. Rigid tri-apex hypotheses

Let `A,B,C` be the vertices of the non-obtuse MEC/Moser triangle, in cyclic
order, and let `I_A,I_B,I_C` be the four-point strict interiors of the three
opposite caps.  At the rigid boundary every closed cap has six points:

```text
C_A = {B,C} union I_A,
C_B = {C,A} union I_B,
C_C = {A,B} union I_C,
|I_A| = |I_B| = |I_C| = 4.
```

The remainder of the packet assumes that every apex `X` satisfies one of two
alternatives, together with the exact cap-contribution shapes derived below:

```text
one-class branch: some radius class has at least 6 points;
two-radius branch: two distinct radii each have at least 4 points.
```

Assume the general class-versus-cap bound and the sharp one-hit contribution
bound for adjacent caps.  They make these alternatives exact at `n=15`.

### Rigid one-class shape

The class has exactly six points.  It contains all four points of `I_X`, and
exactly one point in each adjacent closed cap.

Indeed, a class at the opposite apex has at most the six points of its opposite
cap in total.  At most two class points lie outside `I_X`, while a six-class has
at least four in `I_X`; since `|I_X|=4`, equality holds everywhere.  The two
outside hits cannot lie in the same adjacent cap because each adjacent cap is a
one-hit region.

### Rigid two-radius shape

There are exactly two disjoint four-classes.  Each class contains exactly two
points of `I_X` and exactly one point in each adjacent closed cap.  The two
classes partition `I_X`.

Each class contributes at least two interior points.  Distinct radius classes
are disjoint, and the interior has only four points, so both contributions are
exactly two.  Their remaining two points are forced one-per-adjacent-cap.

Write

```text
k_X = 1 in the one-class branch,
k_X = 2 in the two-radius branch.
```

## 2. Two geometric inputs

The proof below also takes the following two MEC statements as inputs.  The
finite checker does not verify either statement.  The adjacent-cap ceiling has
the direct disk-segment justification recorded below; shortest-side pair
injectivity remains a separate geometric proof obligation for this packet.

### Shortest-side pair injectivity

If `AB` is a shortest side of the non-obtuse MEC triangle, then no two distinct
carrier points have the same ordered pair of distances to `A` and `B`.
Equivalently, one radius class at `A` and one radius class at `B` intersect in
at most one carrier point.

The geometric reason is reflection.  Two common points would be mirror images
across `AB`.  MEC containment and the shortest-side condition force the point
on the triangle side of `AB` into the Moser triangle, where a further carrier
vertex is forbidden by convex independence.

### Adjacent-cap distance ceiling

For a point `x` in the cap adjacent to apex `A` along side `AB`,

```text
|Ax| <= |AB|.
```

The adjacent cap lies in the circular segment of the MEC disk cut off by chord
`AB`.  Its relevant boundary arc has central angle at most `pi`, because the
Moser triangle is non-obtuse.  Chord length from `A` is therefore maximized at
`B`.

## 3. Exact checkerboard lemma

### Lemma

Let six carrier vertices occur in the cyclic order

```text
A < B < x00,x11 < x01,x10,
```

where the order inside either two-point block is arbitrary.  Suppose there are
two radius values at each center with

```text
at A: x00,x01 have radius a0;  x10,x11 have radius a1,
at B: x00,x10 have radius b0;  x01,x11 have radius b1.
```

Then the configuration is impossible.

The same conclusion holds with the two perfect matchings swapped.

### Proof

For cyclic vertices `A<B<x<y`, strict Kalmanson `K2` says

```text
|Ax| + |By| > |Ay| + |Bx|.
```

Assume first that the early block is `{x00,x11}` and the late block is
`{x01,x10}`.  Apply `K2` to `A,B,x00,x01`:

```text
a0 + b1 > a0 + b0,
```

so `b1>b0`.  Apply it to `A,B,x11,x10`:

```text
a1 + b0 > a1 + b1,
```

so `b0>b1`, a contradiction.

For the other perfect matching the same two inequalities are exchanged.  The
checker records their exact integer coefficient vectors; in either orbit the
two strict vectors sum to zero, giving `0>0`.  ∎

## 4. No uniquely shortest side at `n=15`

### Conditional theorem

Under the rigid tri-apex hypotheses, the Moser triangle has no uniquely shortest
side.

### Proof

Suppose `AB` is uniquely shortest, with third apex `C`.

First, no selected rich class at `A` contains `C`.  If one did, its radius would
be `|AC|`.  The same class has one hit `y` in the other adjacent cap, the cap
along side `AB`.  The adjacent-cap ceiling gives

```text
|AC| = |Ay| <= |AB|,
```

contradicting `|AB|<|AC|`.  Symmetrically, no rich class at `B` contains `C`.

Consequently every one of the `k_A` selected classes at `A` has its `C`-side
outside hit in `I_B`, and every one of the `k_B` selected classes at `B` has its
`C`-side outside hit in `I_A`.

The `A`-classes partition `I_A` and the `B`-classes partition `I_B`.  Hence each
of those cross hits occupies a cell in the `k_A by k_B` grid of intersections
between an `A`-class and a `B`-class.  The cross hits are distinct, and
shortest-side pair injectivity permits at most one point in each grid cell.
Therefore

```text
k_A + k_B <= k_A k_B.
```

For `(k_A,k_B)=(1,1),(1,2),(2,1)` this is false.  The only remaining case is
`(2,2)`, where equality forces every grid cell to be occupied exactly once.

The two hits in `I_A` use one point from each `B`-class.  They must also use one
point from each `A`-class: otherwise one `A`-row would already occupy both of its
grid cells, while its mandatory hit in `I_B` would create a second point in one
of those cells.  Thus the `I_A` cells form one perfect matching of the `2 by 2`
grid.  The `I_B` cells form the complementary perfect matching.

In cyclic order all `I_A` vertices occur before all `I_B` vertices when the
order is started at `A,B`.  The exact checkerboard lemma now gives a
contradiction.  ∎

### Consequence

A non-equilateral triangle with no uniquely shortest side has two equal shortest
sides.  Thus the rigid Moser triangle is either

```text
isosceles with two equal shortest sides,
```

or equilateral.

## 5. Structure of the remaining isosceles branch

Assume

```text
|AB| = |AC| < |BC|.
```

For any shortest side, if neither endpoint has a selected rich class through
the third apex, the cross-hit count starts at the second paragraph of Section
4 and gives the same count/checkerboard contradiction.  Applied to `AB`, at
least one endpoint therefore has a selected class through `C`.  It cannot be
`B`, because the adjacent-cap ceiling would give `|BC|<=|BA|`.  Hence `A` has
a selected class through `C`; since `|AB|=|AC|`, that full distance class also
contains `B`.

Therefore:

* in the one-class branch at `A`, that six-class is exactly
  `C_A={B,C} union I_A`; the whole opposite six-point cap lies on one circle
  centered at `A`;
* in the two-radius branch, one exact four-class is `{B,C}` together with two
  points of `I_A`; the other exact four-class uses the remaining two points of
  `I_A` and one point in each adjacent strict interior.

This is the precise remaining non-equilateral split.

## 6. Equilateral flagging

In the equilateral case, call an apex **flagged** when one of its rich classes
contains the other two apices.

For each side, the shortest-side proof shows that at least one of its endpoints
is flagged: otherwise the same count/checkerboard contradiction applies.  The
flagged vertices therefore form a vertex cover of a triangle, so at least two
of the three apices are flagged.

A flagged apex in the one-class branch has its entire opposite cap on the side-
length circle centered at that apex.  A flagged apex in the two-radius branch
has one exact four-class consisting of the other two apices and two opposite-
cap interior points.

## 7. Fully Reuleaux subcase

### Conditional theorem

Suppose the rigid Moser triangle is equilateral and all three opposite caps are
the full six-point side-length classes centered at their opposite apices.  Then
the carrier is not 4-bad.

### Geometry of the boundary

Normalize the side length to one and write

```text
A=(0,sqrt(3)/2), B=(-1/2,0), C=(1/2,0).
```

The four interior points of `C_A` lie on the minor arc `BC` of the unit circle
centered at `A`; the other two cap statements give the analogous arcs `CA`
centered at `B` and `AB` centered at `C`.  The fifteen carrier points therefore
lie on the boundary of the Reuleaux triangle determined by `A,B,C`.

Take a non-apex point `p` on the open arc `BC` centered at `A`.  Put

```text
u=|pB|, v=|pC|,
```

and reverse `B,C` if necessary so that `u<=v`.

Along the same arc, chord length from `p` is strictly monotone on either side of
`p`; hence a radius `r<u` occurs at at most two points, a radius `u<r<v` at at
most one point, and a radius `r>v` at no point of that arc.

Along the adjacent arc `AB` centered at `C`, distance from `p` varies strictly
from `u` to `1`; along the adjacent arc `CA` centered at `B`, it varies strictly
from `v` to `1`.  Thus:

```text
r < u       : at most two hits, both on the own arc;
u < r < v   : at most one own-arc hit and one AB-arc hit;
v < r <= 1  : at most one hit on each adjacent arc;
r > 1       : no boundary hit.
```

At `r=u`, the adjacent-`AB` hit is the already-counted endpoint `B`; the own
arc has at most one further hit.  If `u<v`, then at `r=v` the own arc has only
the endpoint `C`, the adjacent-`CA` hit is the same point, and the `AB` arc has
at most one further hit.  If `u=v`, the own-arc hits are exactly the two
endpoints and both adjacent contributions duplicate them.  Thus every positive
radius contains at most two other boundary points, including at the omitted
equalities.

For completeness, the adjacent-arc monotonicity is immediate in the displayed
coordinates.  Parameterize

```text
p=A+(cos(theta),sin(theta)),  theta in [4pi/3,5pi/3],
q=B+(cos(phi),sin(phi)),      phi in [0,pi/3].
```

Then

```text
d/dphi |p-q|^2
 = 2[(1/2+cos(theta)) sin(phi)
     -(sqrt(3)/2+sin(theta)) cos(phi)] >= 0,
```

because `1/2+cos(theta)>=0` while `sqrt(3)/2+sin(theta)<=0` on the stated
intervals, so both displayed terms are nonnegative.  The other adjacent arc is
symmetric.  Strictness holds away
from shared endpoints.

So every non-apex carrier point is not 4-rich, contradicting the counterexample
hypothesis.  ∎

## 8. What remains

Under the packet hypotheses, the only remaining rigid `n=15` branches are:

* the non-equilateral isosceles case where the common apex uses its two-radius
  branch, or uses one full cap while the other two apices have mixed structure;
* equilateral configurations in which at least two apices are flagged but one
  or more flagged apices use the two-radius branch.

The most concrete next target is a two-full-cap / unique-four-cover lemma.  A
full cap is a six-point subset of one circle.  Every distinct exact-four circle
meets it in at most two points, by the existing two-circle cap kernel.  Covering
a full cap therefore needs at least three unique-four centers.  With two full
caps, any center whose class contributes two points to each cap creates a
four-point, three-circle radical-axis configuration; classifying that
configuration in cap order is the next nonlinear obstruction target.

## 9. Scope boundary

This packet establishes deductions only conditional on the rigid cap shapes,
the adjacent-cap one-hit bound, and shortest-side pair injectivity.  The stored
checker verifies none of those geometric inputs.  The packet does not provide
a descent from `|A|>15` to `15`, show that a full cap occurs in every remaining
branch, or close the active tri-apex or unique-radius theorem in the external
Lean formalization.  No general proof or counterexample for Erdos Problem #97
is claimed.
