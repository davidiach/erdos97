# Minimum-radius component injectivity

Status: `PAPER_PROOF_CANDIDATE / REVIEW_PENDING`.

This note closes the three short return motifs left by
`docs/radius-level-return-locality.md`, but only at the minimum radius level in
the alternating boundary-neighbour branch. It is not a proof or disproof of
Erdős Problem #97 and not a source-of-truth status update.

## 1. Setup

Let a strictly convex polygon have cyclic order

\[
E_0,Q_0,E_1,Q_1,\ldots,E_{m-1},Q_{m-1}.
\]

Assume the complete rich class at every `E_i` contains both boundary neighbours
at radius `rho_i`:

\[
|E_iQ_{i-1}|=|E_iQ_i|=\rho_i.
\]

Put

\[
R=\min_i\rho_i,
\qquad
X=\{E_i:\rho_i=R\}.
\]

Every polygon side has length at least `R`. By
`docs/radius-level-linear-forest.md`, the full distance-`R` graph on `X` is a
disjoint union of paths.

Call `W` an extra witness of `U in X` when

\[
|WU|=R
\]

and `W` is not one of the two boundary neighbours of `U`.

## 2. Boundary-edge triangle-rhombus obstruction

We first isolate the only algebraic local configuration needed below.

> **Lemma.** Let `W,X` be consecutive vertices of a strictly convex polygon
> with `|WX|=1`. There do not exist three further distinct polygon vertices
> `U,Y,V`, all on the interior side of the boundary line `WX`, satisfying
>
> \[
> |WU|=|UX|=|XY|=|YV|=|VW|=1.
> \]

### Proof

Normalize

\[
W=0,\qquad X=1
\]

in the complex plane, with every other polygon vertex in the open upper
half-plane. The unit triangle on the boundary edge has only one upper apex, so

\[
U=u:=e^{i\pi/3}.
\]

Write

\[
Y=1+e^{i\theta},\qquad V=e^{i\phi},
\qquad 0<\theta,\phi<\pi.
\]

The remaining equality `|Y-V|=1` gives

\[
1+\cos\theta
 =\cos\phi+\cos(\theta-\phi).
\]

Using sum-to-product,

\[
2\cos^2(\theta/2)
 =2\cos(\theta/2)\cos(\phi-\theta/2).
\]

Since `0<theta<pi`, division by the positive factor
`2*cos(theta/2)` is valid. With `0<phi<pi`, the only possibilities are

\[
\phi=\theta
\]

or `phi=0`; the latter would give `V=X`. Hence

\[
V=v:=e^{i\theta},\qquad Y=1+v,
\]

so `W,X,Y,V` form a rhombus.

It remains to compare the direction `v` with the fixed direction
`u=e^{i*pi/3}`.

### Case 1: `0<theta<pi/3`

Define

\[
a=\frac{\sin(\pi/3-\theta)}{\sin(\pi/3)},
\qquad
b=\frac{\sin\theta}{\sin(\pi/3)}.
\]

Then `a,b>0`, `b<1`, and the sine-resolution identity gives

\[
v=a+bu.
\]

Consequently

\[
V=\frac{1-b}{1+a}W
  +\frac{b}{1+a}U
  +\frac{a}{1+a}Y.
\]

All three coefficients are positive and sum to one, so `V` is strictly inside
triangle `WUY`.

### Case 2: `theta=pi/3`

Then `V=U`, contrary to distinctness.

### Case 3: `pi/3<theta<2pi/3`

Set

\[
a=\frac{\sin(\theta-\pi/3)}{\sin\theta},
\qquad
b=\frac{\sin(\pi/3)}{\sin\theta}.
\]

Both `a,b` lie strictly between zero and one, and

\[
u=a+bv.
\]

Thus `U` has parallelogram coordinates `(a,b)` strictly inside the rhombus
with vertices `W,X,V,Y`. Explicitly,

\[
U=(1-a)(1-b)W+a(1-b)X+(1-a)bV+abY,
\]

with all four coefficients positive.

### Case 4: `theta=2pi/3`

Then `Y=U`, again contrary to distinctness.

### Case 5: `2pi/3<theta<pi`

Put

\[
d=\sin(\theta-\pi/3),
\quad
a=\frac{\sin\theta}{d},
\quad
b=1-\frac{\sin(\pi/3)}{d}.
\]

Here `a,b>0`, while

\[
a+b
 =1+\frac{\sin\theta-\sin(\pi/3)}{d}<1.
\]

A direct sine resolution gives

\[
Y=aU+bV+(1-a-b)W.
\]

Hence `Y` lies strictly inside triangle `WUV`.

Every possible value of `theta` either identifies two vertices or makes one of
the five points non-extreme, contradicting strict convexity. `QED`

The statement scales from unit length to any positive radius.

## 3. No target can return to one minimum-level component

> **Minimum-radius component-injectivity theorem.** Let `W` be a polygon
> vertex outside `X`. Then `W` cannot be an extra radius-`R` witness for two
> vertices in the same path component of the distance-`R` graph on `X`.

### Proof

Suppose `W` is an extra witness for distinct path vertices `U,V`. Let

\[
U=X_0,X_1,\ldots,X_\ell=V
\]

be the unique path between them. Every path edge and both edges `WU,WV` have
length `R`.

The return-locality theorem already rules out `ell>=4`. It remains to treat
`ell=1,2,3`.

### Path length one

The three vertices `W,U,V` are pairwise at distance `R`. The two `E`-vertices
`U,V` are never adjacent on the polygon boundary, and `W` is an extra witness
of both, so the three-vertex set is boundary-independent. Since every polygon
side has length at least `R`, the minimum-side distance-forest lemma forbids
this distance-`R` triangle.

### Path length two

Write the path as

\[
U-X_1-V.
\]

If `W` is not adjacent to `X_1` on the polygon boundary, then
`{W,U,X_1,V}` is boundary-independent. Its distance-`R` graph contains the
four-cycle

\[
W-U-X_1-V-W,
\]

contradicting the distance-forest lemma.

If `W` is adjacent to `X_1`, then `|WX_1|=R` because `X_1 in X` has both
boundary neighbours in its radius-`R` class. Both `U` and `V` are intersections
of the two radius-`R` circles centered at `W,X_1`. The two distinct
intersections lie on opposite sides of the boundary line `WX_1`, whereas all
other polygon vertices lie in one open half-plane. Contradiction.

### Path length three

Write

\[
U-X_1-X_2-V.
\]

If `W` is adjacent to neither internal vertex, then the five vertices are
boundary-independent and their distance-`R` graph contains

\[
W-U-X_1-X_2-V-W,
\]

contradicting the distance-forest lemma.

If `W` is adjacent to both internal vertices, then `W` is at distance `R` from
all four members

\[
U,X_1,X_2,V
\]

of `X`. This contradicts the radius-level common-target fan-in cap of three.

Finally suppose `W` is adjacent to exactly one internal vertex, say `X_1`.
After scaling by `R`, the boundary edge `WX_1`, the triangle

\[
W-U-X_1,
\]

and the four-cycle

\[
W-X_1-X_2-V-W
\]

satisfy the boundary-edge triangle-rhombus lemma. Contradiction. The case in
which `W` is adjacent only to `X_2` is symmetric.

All path lengths are excluded. `QED`

## 4. Consequences for the minimum-level export graph

Create a bipartite graph with

- one left vertex for each path component of the distance-`R` graph on `X`;
- one right vertex for each outside polygon vertex used as an extra
  radius-`R` witness; and
- one edge for each component-target incidence.

The preceding results imply:

1. the graph is simple: one target has at most one incidence with each path
   component;
2. every path component has degree at least two, because its two endpoints
   each require an outside witness, while an isolated centre requires two
   distinct outside witnesses;
3. every target has degree at most two, by the minimum-level extra-target cap
   from `docs/radius-level-linear-forest.md`.

Thus the entire minimum-radius branch has been reduced to a simple bipartite
component-target graph with left minimum degree two and right maximum degree
two.

## 5. Cycles in the component-target graph are locally concentrated

Suppose the bipartite export graph has a simple cycle containing `k` path
components and `k` outside targets. In each path component, join the two
attachment centres used by the cycle with their unique radius-level path. Let
`ell_i>=0` be its number of path edges and put

\[
L=\sum_{i=1}^k\ell_i.
\]

Lifting the bipartite cycle gives a simple distance-`R` cycle with

\[
g=2k+L
\]

vertices and edges.

Every polygon side has length at least `R`. A boundary gap between consecutive
vertices of the lifted set has detour length at least `2R` unless those two
vertices are adjacent on the original polygon boundary. No two `X`-vertices
are adjacent, so every one-edge gap is incident to at least one of the `k`
outside targets. Each target has only two boundary neighbours. Hence the number
`h` of possible one-edge gaps satisfies

\[
h\le2k.
\]

The weak-arc detour-cycle lemma rules out the lifted cycle whenever

\[
g\ge h+4.
\]

Since `g=2k+L` and `h<=2k`, every export-graph cycle must satisfy

\[
L\le3.                                                 \tag{1}
\]

> **Component-cycle locality corollary.** Along any cycle of the minimum-level
> export graph, the sum of the path distances between its paired attachment
> centres is at most three.

Thus an unbounded graph-theoretic cycle has only four possible path-length
profiles up to distributing zeroes:

```text
L=0,
L=1,
L=2,
L=3.
```

The number of zero-distance component passages can still be arbitrarily large,
so (1) is a finite *metric-defect* reduction rather than a finite cardinality
classification.

## 6. Remaining gap

At the minimum radius level, target reuse inside one path component is now
completely excluded. Any target of degree two must connect two different
components. Any cycle among components and targets must concentrate all of its
within-component travel into at most three radius-`R` path edges.

This does not yet force a contradiction. The export graph may be a tree with
leaves on the target side, and cycles with total path length zero through three
remain possible at the present level of abstraction. Closing those profiles
requires additional cyclic-order information, the rich rows of the outside
targets, or a minimal-counterexample/deletion argument.

## 7. Replay boundary

The exact arithmetic replay records

```text
(2*g-6)-g=g-6
```

for the one-target return theorem and the more general weak-arc coefficient
comparison. The trigonometric convex-combination proof in Section 2 and the
short-motif case split are paper arguments and are not formalized by that
replay.
