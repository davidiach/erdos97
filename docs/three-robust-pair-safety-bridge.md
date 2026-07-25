# Three-robust pair-safety bridge

Status: `LEMMA` / proof-facing bridge theorem.

This note does **not** prove Erdős Problem 97 and does not claim a
counterexample.  It isolates a new consequence of cardinal minimality when the
three vertices of a non-obtuse minimum-enclosing-circle support triangle are
all robust under every singleton deletion.

## Setup

Let `P` be a cardinality-minimal strictly convex 4-bad polygon, assuming one
exists.  A surviving center `z` is **singleton-robust** when deleting any other
single vertex leaves a rich distance class at `z`.

For a center `z`, write its rich distance classes as pairwise-disjoint sets

```text
C_1, ..., C_t,
```

where every `|C_i| >= 4`.  For a deletion set `D` not containing `z`, the
center `z` becomes good after deleting `D` exactly when

```text
|C_i cap D| >= |C_i| - 3
```

for every rich class `C_i`.

A pair `{x,y}` disjoint from `z` is **z-blocking** when deleting `x,y` makes
`z` good.  Given three surviving centers `Z={p,q,r}`, call a pair
**Z-safe** when it is disjoint from `Z` and is not blocking at any of
`p,q,r`.

The three centers below will be the three noncollinear vertices of a
non-obtuse triangle supporting the minimum enclosing circle of `P`.

## Lemma 1: pair-blockable robust centers have support at most eight

Let `z` be singleton-robust.  If some pair blocks `z`, then the complete rich
profile at `z` is exactly one of:

```text
T5:  one rich class of size five;
T44: two rich classes, each of size four.
```

In particular, all endpoints of all `z`-blocking pairs lie in a fixed set
`U_z` of size at most eight.

### Proof

Put `delta(C)=|C|-3` for a rich class.  If a pair blocks `z`, disjointness of
the rich classes gives

```text
sum_C delta(C) <= 2.
```

Every deficit is a positive integer.  Thus the only numerical possibilities
are one deficit `2`, one deficit `1`, or two deficits `1`.

One deficit `1` would mean that `z` has one size-four rich class and no other
rich class.  Deleting any member of that class would already make `z` good,
contrary to singleton robustness.  The remaining possibilities are one
size-five class (`T5`) and two size-four classes (`T44`).

In `T5`, a blocking pair consists of two members of the five-class.  In
`T44`, it consists of one member from each of the two four-classes.  Therefore
all blocking-pair endpoints lie in the union of the displayed classes, of
size five or eight.  ∎

## Lemma 2: no critical four-circle contains all three MEC vertices

Let `p,q,r` be the noncollinear vertices of a non-obtuse triangle on the
minimum enclosing circle.  No polygon vertex `a` is equidistant from all
three.

### Proof

A point equidistant from three noncollinear points is their circumcenter.  The
circumcenter here is the center of the minimum enclosing circle and belongs to
the non-obtuse support triangle.  It is not an extreme vertex of the polygon:
in the acute case it is inside the triangle, and in the right case it is the
midpoint of the hypotenuse.  ∎

Consequently, an exact critical four-class contains at most two of
`{p,q,r}` and hence contains at least two witnesses outside that set.

## Theorem: three-robust pair-safety

Assume the three MEC support vertices `p,q,r` are singleton-robust.  If

```text
|P| >= 28,
```

then some exact critical four-class contains a `Z`-safe pair, where
`Z={p,q,r}`.

Equivalently, there are a critical center `a` and two distinct witnesses
`x,y` in its exact four-class such that

```text
x,y notin {p,q,r},
```

and each of `p,q,r` remains 4-rich after deleting `x,y`.

### Proof

Minimality supplies exact critical four-classes covering every polygon
vertex: for every deleted source `v`, some surviving blocker center has a
unique rich class of size exactly four containing `v`.

For each `z in Z`, if no pair blocks `z`, put `U_z=empty`.  Otherwise let
`U_z` be the size-five support or the union of the two size-four supports from
Lemma 1.  Set

```text
U = U_p union U_q union U_r.
```

Then `|U| <= 24`.

Suppose, for contradiction, that no exact critical class contains a `Z`-safe
pair.  Let `F` be any exact critical four-class and let `v in F \ Z`.
By Lemma 2, `F \ Z` has at least two elements, so choose
`w in F \ Z` with `w != v`.  The pair `{v,w}` is not `Z`-safe and is
disjoint from `Z`; therefore it blocks at least one `z in Z`.  Lemma 1 then
gives `v,w in U_z`, and in particular `v in U`.

Thus every non-MEC vertex appearing in any critical four-class lies in `U`.
The critical classes cover every polygon vertex, so

```text
P \ Z subset U.
```

Hence

```text
|P| <= |Z| + |U| <= 3 + 24 = 27,
```

contrary to `|P| >= 28`.  ∎

## Cap-local tightening

The preceding theorem does not use the cap order.  The cap geometry gives a
sharper description of the only way a critical row can fail to contain a safe
pair.

Let `C` be one of the three closed MEC caps with endpoints `p,q`, and let `r`
be the third MEC vertex.  Let `a` be a critical center in `C`, with exact
four-class `F_a`, and put

```text
X = F_a \ C.
```

The ordered-cap one-sided distance theorem gives

```text
|F_a cap C| <= 2,
```

so `|X| >= 2`.

### Endpoint blocking capacity

For either endpoint `z in {p,q}`, at most one pair from `X` can be
`z`-blocking.

Indeed, if a rich class at `z` contained two points `x,y in X`, then the two
distinct cap centers `a,z` would both be equidistant from the same pair
outside `C`, contradicting ordered-cap outside-pair uniqueness.  Hence every
rich class at `z` meets `X` in at most one point.  A `T5` profile blocks no
pair of `X`, while a `T44` profile blocks at most the single cross-pair between
its two at-most-singleton intersections with `X`.

At the third MEC vertex `r`, Lemma 1 and the two-circle intersection bound show
that at most four pairs of `X` can be `r`-blocking.

Therefore the union of the three blocking graphs covers at most six pairs of
`X`, with the endpoint contributions at most one each.

### Exact four-outside tight profile

If `|X|=4` and every pair of `X` is blocked at one of `p,q,r`, then all bounds
are equalities:

1. `r` has a `T44` profile whose two four-classes meet `X` in a `2+2`
   partition and block the four cross-pairs;
2. `p` and `q` each have a separated `T44` profile and block one of the two
   within-part pairs;
3. the two pairs in the `2+2` partition are co-radial from both `a` and `r`,
   so their chords are parallel and have the common perpendicular-bisector
   line `ar`.

This is the unique capacity-tight four-witness residual, up to exchanging the
MEC endpoints and relabelling the two parts.

### Exact three-outside residual

If `|X|=3` and no safe pair exists, the only capacity-tight possibilities are:

1. the third vertex `r` blocks a two-edge star (`T44` intersection type
   `2+1`) and an endpoint blocks the remaining edge; or
2. the three MEC vertices block one edge each.

Thus the unrestricted all-large-caps problem is reduced locally to these
three- and four-outside profiles whenever one insists that a chosen critical
row contain no pair surviving at all three MEC vertices.

## Scope and next target

The theorem gives a genuine cardinality-independent bridge, but it is not yet
a removable-vertex theorem.  A `Z`-safe pair deletes the pair's critical
center while preserving all three MEC support vertices only after an
additional argument controlling the other critical centers.

The next useful statement is one of the following:

```text
(A) a Z-safe pair in a critical row forces a removable proper deletion set;
```

or

```text
(B) every minimal counterexample with 15 <= n <= 27 is impossible, and the
    safe-pair branch for n >= 28 descends to that finite range.
```

The cap-local tight profiles above are the exact regression cases for any
attempt at (A).  A proof may not assume that endpoint blocking makes the pair
co-radial: the tight residual uses separated `T44` classes precisely to avoid
that false inference.
