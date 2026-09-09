# Mathematical results and exact scope

Date: 8 September 2026.
Status: written proof / exact-certificate candidates, review pending.
No unrestricted resolution, external review, formalization, or novelty claim.

Throughout, a finite planar set is in **strictly convex position** when every
point is a vertex of its convex hull. For a point `p` in a finite set `X`, put

\[
 C_X(p,r)=\{q\in X\setminus\{p\}:|p-q|=r\},\qquad
 M_X(p)=\max_{r>0}|C_X(p,r)|.
\]

A vertex is **rich** when `M_X(p) >= 4`, and **good** otherwise. The target of
Erdős #97 is an all-radius good vertex in every finite strictly convex
polygon. A repair of old vertices is not a counterexample unless every new
vertex is rich as well.

## 1. A general old-vertex repair lemma

**Theorem 1.** Let `P` be a finite strictly convex polygon and let `S` be a
subset of `k` of its vertices. There is a finite strictly convex extension
`P'` containing every point of `P`, with at most `3k` new points, in which
every member of `S` is rich. Already-rich old vertices remain rich.

There is no assertion about richness at the new points. In particular this
is not a counterexample to Erdős #97.

### Proof

First fix one old vertex `p`. Choose a farthest vertex `q` from `p`, and let
`r=|p-q|>0`. The closed disk `D` with center `p` and radius `r` contains the
whole current set.

Every boundary point of a Euclidean disk is uniquely exposed by its tangent
supporting line. Thus any finite set of distinct points added on the circle
`partial D` will itself consist of extreme points of the enlarged set, and
`q` will remain extreme.

For each old vertex `v != q`, choose a linear functional `L_v` uniquely
maximized at `v` over the current finite set. The positive gap

\[
 L_v(v)-L_v(q)>0
\]

persists for all points sufficiently close to `q`. Since only finitely many
old vertices are involved, there is one neighborhood of `q` on which all
these gaps persist simultaneously. Add distinct points on a sufficiently
small circle arc in this neighborhood, avoiding existing points. Each old
`v != q` retains its exposing functional, while `q` and every new point have
the circle's tangent supporting lines. The whole enlarged set is strictly
convex.

If `m=|C_P(p,r)|<4`, add exactly `4-m` such points. Since `m>=1`, this uses at
most three points. Vertex `p` is now rich at radius `r`.

Repeat this operation for the chosen old vertices that are not already
rich. No previous point is moved or deleted, so an equal-distance witness
set established at an earlier stage remains present. At most three points
are added per selected old vertex. This proves the bound `3k`. QED.

For algebraic input coordinates, the added points can be chosen algebraic.
Indeed, apply a rational rotation matrix

\[
 R(s)=\frac1{1+s^2}
 \begin{pmatrix}1-s^2&-2s\\2s&1-s^2\end{pmatrix}
\]

to `q-p`, with distinct sufficiently small rational `s`, and translate back
by `p`. For rational Cartesian input this even preserves rationality. The
strict supporting inequalities give a nonempty open choice interval.

### Meaning of the lemma

There cannot be a general argument that a particular old good vertex must
remain good under every strictly convex extension. All old defects can be
moved onto newly added vertices. A global proof has to account for those
new vertices; a counterexample has to repair them too.

## 2. The fixed nine-point seed

Identify the plane with the complex numbers, and define

\[
 \omega=\frac{-1+i\sqrt3}{2},\qquad
 z(t)=-\frac12+\frac{3t}{1+3t^2}
       +i\sqrt3\,\frac{1-3t^2}{2(1+3t^2)}.
\]

Set

\[
 t_0=\frac1{10},\qquad
 t_1=\frac{83-3\sqrt{721}}{200},\qquad
 a=z(t_0),\qquad b=\overline{z(t_1)}.
\]

The parameter `t_1` is the smaller root of

\[
 s^2-\frac{83}{100}s+\frac1{100}=0,
\]

and satisfies `0<t_1<t_0`. It is exactly the first recurrence step of the
repository's six-exception family, not a decimal replacement for it.

In label order, let

\[
 P=(1,\omega,\omega^2,
       a,\omega a,\omega^2a,
       b,\omega b,\omega^2b).
\]

This is the nine-point member of the earlier unbounded partial family.
All its coordinates have the form

\[
 (x,\sqrt3 y),\qquad x,y\in\mathbb Q(\sqrt{721}).
\]

The exact checker verifies strict supporting signs in the cyclic order

```
4, 2, 6, 5, 0, 7, 3, 1, 8.
```

Its all-radius maximum multiplicities are

\[
 (2,2,2,3,3,3,4,4,4).
\]

For the three anchors `0,1,2`, the multiplicity-two class has squared radius
`3`. For `3,4,5`, the multiplicity-three class has squared radius

\[
 3|a|^2=\frac{219}{103},\qquad |a|^2=\frac{73}{103}.
\]

The old rich vertices `6,7,8` are rich at their own orbit-side radius.
These finite-instance claims are checked directly here, rather than relying
on acceptance of the earlier all-size written proof.

## 3. A sharp prescribed-radius off-carrier repair

For `i=0,...,5`, define the six deficient circles

\[
 \Gamma_i=\{x:|x-p_i|^2=R_i^2\},\qquad
 R_i^2=\begin{cases}3,&0\le i\le2,\\219/103,&3\le i\le5.\end{cases}
\]

**Theorem 2.** Suppose `Q` is disjoint from `P`, the union `P union Q` is in
strictly convex position, and every `p_i`, `0<=i<=5`, has at least four
witnesses on its specified circle `Gamma_i`. Then `|Q|>=9`.

This bound is attained by an explicit nine-point cap below. No symmetry or
carrier assumption is imposed in the lower bound. Its fixed-seed and
prescribed-radius hypotheses are essential qualifications.

### 3.1 The finite geometric certificate

**Claim.** A new point admissible in a strictly convex extension of `P` lies
on at most one of the six circles `Gamma_i`.

There are exactly 15 unordered circle pairs. The certificate
`data/prescribed_circle_pairs.json` exhausts all of them and both real
intersection branches for each. Among the 30 branches, 12 coincide with
old points. At each of the other 18 intersections, the certificate exhibits
an old point strictly inside a triangle formed by other points of
`P union {intersection}`. Thus no new pair intersection is admissible.

Here is the exact reduction used to exhaust intersections. Store a Cartesian
point as `(x,y)` meaning `(x,sqrt(3)*y)`, and use

\[
 N(x,y)=x^2+3y^2.
\]

For centers `A,B`, squared radii `r2,s2`, let

\[
 v=B-A,\quad d=N(v)>0,\quad
 h=\frac{r2-s2+d}{2d},\quad
 S=\frac{r2/d-h^2}{3}.
\]

The complete intersection set, when `S>=0`, is

\[
 A+hv\ \mathbin{\pm}\ \sqrt S\,(-3v_y,v_x).
\]

When `S=0` the two expressions coincide; when `S<0` there is no real
intersection. In the present 15 pairs, `S>0` in every case. Subtracting the
two circle equations gives the line parameter `h`; substitution into either
circle leaves exactly this quadratic. Thus no intersection branch is omitted.

A triangle containment certificate consists of a target point `v`, three
other labels `a,b,c`, positive orientation of `(a,b,c)`, and nonnegative
orientations

\[
 [a,b,v],\quad[b,c,v],\quad[c,a,v].
\]

These imply that `v` belongs to the closed triangle of the other three
points, so it cannot be an extreme point. For all 18 non-old intersections
here, all three signs are strictly positive. Both checkers verify the circle
identities, root coverage, and containment signs exactly.

### 3.2 Counting the necessary additions

Each anchor needs at least two new witnesses on its specified circle; each
initial-chain vertex needs at least one. The total number of required new
incidences is therefore

\[
 3\cdot2+3\cdot1=9.
\]

Each new point contributes to at most one of these six circles by the claim.
Therefore `|Q|>=9`. This argument applies to caps of arbitrary finite size,
not merely to a search over caps up to nine points. QED for the lower bound.

### 3.3 An exact cap attaining nine

Define three complex numbers

\[
 c_1=\frac{-10585-9397i\sqrt3}{20006},\qquad
 c_2=\frac{-2785-2197i\sqrt3}{5006},\qquad
 c_3=\frac{209908-34731i\sqrt3}{260281}.
\]

Add all their rotations:

\[
 Q=\{\omega^k c_j:0\le k<3,\ 1\le j\le3\}.
\]

An alternative description makes the incoming witness equalities immediate.
Put

\[
 U(s)=\frac{1-3s^2+2i\sqrt3 s}{1+3s^2},\qquad |U(s)|=1.
\]

Then

\[
 \begin{aligned}
 c_1&=1+U(-1/100)(\omega^2-1),\\
 c_2&=1+U(-1/50)(\omega^2-1),\\
 c_3&=a+U(-3/50)(1-a).
 \end{aligned}
\]

Thus `|c_1-1|^2=|c_2-1|^2=3`, and `|c_3-a|^2=219/103`.
Rotating supplies the other five deficient centers. All original witnesses
remain present.

Label the added orbits `9,10,11`, `12,13,14`, and `15,16,17`, respectively.
The strict convexity certificate uses the boundary order

```
17, 4, 12, 9, 2, 6, 15, 5, 13, 10, 0, 7, 16, 3, 14, 11, 1, 8.
```

All `18*(18-2)=288` strict supporting-half-plane signs are positive, and all
153 pairwise squared separations are strictly positive. The exact distance census gives

\[
 \boxed{M_{P\cup Q}(p_i)=4\quad(0\le i<9),\qquad
        M_{P\cup Q}(p_i)=2\quad(9\le i<18).}
\]

The original six-arc carrier is contained in the union of the three circles

\[
 |x-\omega^k|^2=3|x|^2,\qquad k=0,1,2.
\]

For each of the nine added points, all three differences between the two
sides are nonzero. The 27 inequalities are checked exactly. Hence every
added point is genuinely off the carrier, not just off the old recurrence.

This establishes attainment and completes Theorem 2. It does not establish
an all-rich cap: the nine new vertices are good, with multiplicity exactly
two. The good-vertex count worsens from six to nine.

## 4. New cap vertices cannot have three old witnesses

**Theorem 3.** For the fixed seed `P` of Section 2, suppose `x notin P` and
`P union {x}` is in strictly convex position. Then, for every `r>0`,

\[
 \#\{p\in P:|x-p|=r\}\le2.
\]

No location, symmetry, selected-radius, or carrier restriction on `x` is
assumed.

### Proof by complete finite certificate

Suppose instead that three old points `p_a,p_b,p_c` are equidistant from `x`.
The old set is strictly convex, so the triple is noncollinear. It determines
one and only one circumcenter, and `x` must be that point.

There are exactly `binomial(9,3)=84` old triples. Their complete list and
centers are recorded in `data/base9_circumcenters.json`. The 84 triples give
64 distinct centers. Six centers coincide with old vertices, and so cannot
be a new `x`. For every one of the remaining 58 centers the certificate gives
a point in the closed triangle of three other points of `P union {x}`.
There are 55 strict-interior certificates and three non-strict closed-triangle
certificates. Non-strict containment is sufficient to exclude an extreme
point; it is not silently promoted to a strict inequality.

The checkers verify that every old triple occurs exactly once, that each
claimed center is equidistant from its triple, that the triple is
noncollinear, and that each coincidence or containment certificate is valid.
Consequently every possible `x` is excluded. QED.

### Cap-internal consequence

Let `Q` be any finite set disjoint from `P` such that `P union Q` is strictly
convex. Strict convex independence is hereditary, so Theorem 3 applies to
every `q in Q` separately. If `q` has four equal-distance witnesses in
`P union Q`, at most two can be old. Therefore at least two distinct witnesses
must belong to `Q minus {q}` at the same radius.

In particular, an all-rich added cap must contain a directed selected-witness
graph of minimum outdegree at least two internally. One or two newly added
points cannot form an already-rich cap for this fixed seed. This is a
necessary condition, not a contradiction: directed cycles and internally
supported larger caps remain possible.

This theorem does **not** persist automatically when old vertices move, old
points are removed, or the old seed is changed. It is also not a general
fact about convex sets. For a positive control, the three points

\[
 (1/2,-\sqrt3/2),\ (1,0),\ (1/2,\sqrt3/2)
\]

can be extended strictly convexly by their circumcenter `(0,0)`, which is
equidistant from all three. The test suite checks that control, preventing
misinterpretation of Theorem 3 as a universal circumcenter-location lemma.

## 5. A four-rich, two-closer middle-witness cycle

This configuration is separate from the preceding seed and cap.

Let

\[
 A=(0,0),\ B=(1,0),\ C=(1/2,\sqrt3/2),\
 O=(1/2,\sqrt3/6).
\]

Let `T` be rotation by 120 degrees about `O`, and define

\[
 a(t)=\left(\frac{1-3t^2}{1+3t^2},
             \frac{-2\sqrt3 t}{1+3t^2}\right).
\]

Take the nine points in label order

\[
 X=(A,B,C,\ a(1/40),T a(1/40),T^2a(1/40),
                  a(1/20),T a(1/20),T^2a(1/20)).
\]

All coordinates are rational in the stored `(x,sqrt(3)*y)` representation.
The exact strictly convex order is

```
8, 5, 0, 6, 3, 1, 7, 4, 2.
```

At radius one, **every vertex of `X` has exactly two strictly closer points**.
The three core centers `A,B,C` have exactly four unit-distance witnesses.
For a hull center, list its selected witnesses in their boundary fan order
and call positions two and three its two middle witnesses. The exact rows are

| Source | Four witnesses in fan order | Middle witnesses |
|---|---|---|
| A = 0 | 6, 3, 1, 2 | 3, 1 |
| B = 1 | 7, 4, 2, 0 | 4, 2 |
| C = 2 | 8, 5, 0, 1 | 5, 0 |

Consequently the middle-witness graph contains the directed triangle

\[
 A\longrightarrow B\longrightarrow C\longrightarrow A.
\]

Its underlying undirected graph is not a forest. This is a counterexample
to a forest assertion for four-witness rows even under the two-closer
condition at every assigned center. It strengthens the earlier repository
negative control, whose displayed rows had only three witnesses.

All 63 supporting signs, all assigned-radius closer counts, the fan orders,
and the complete distance census are checked exactly. The maxima are

\[
 (4,4,4,2,2,2,2,2,2).
\]

The remaining six vertices are not rich. Therefore this control does not
refute a theorem requiring richness at **every original vertex**, does not
close the variable-radius two-closer problem, and is not an Erdős #97
counterexample. It also does not rule out weaker acyclicity statements using
a differently selected subgraph or additional global hypotheses.

## 6. Arithmetic and trust boundary

The primary field is `Q(sqrt(721))`. For `a+b*sqrt(721)`, signs are obtained
by rational comparison of `a*a` and `721*b*b`, after separating same-sign
and opposite-sign cases. No floating approximation participates.

Circle-pair coordinates use `a+b*sqrt(S)` over that field. Their signs reduce
to signs of `a*a-b*b*S` with the appropriate signs of `a` and `b`. The code
handles square radicands and semantic zero; it does not assume every
extension is irreducible.

The oracle is a separate implementation. It represents values as flattened
polynomials in two radicals, reduces their squares exactly, folds reducible
radicals, and isolates nonzero signs using rational lower and upper square
root bounds. On the delivered certificates, 32-bit rational enclosures
already separate every nonzero sign. Exact zero is determined algebraically,
not by a small interval or a floating tolerance.

The 31 tests include malformed or inexact input rejection, missing triples,
missing intersection branches, altered radii and coordinates, invalid hull
orders, false coincidence claims, reversed containment triangles, radical
reduction controls, and replay through the separate oracle.

The finite certificate reductions above are explicit written geometric
arguments. They have not been formalized in Lean or reviewed by an external
mathematician. Two implementations and passing tests are not substitutes
for that review. None of the numerical co-design runs supports an exact
mathematical claim.
