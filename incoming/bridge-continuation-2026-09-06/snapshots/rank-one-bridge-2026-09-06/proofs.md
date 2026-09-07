# A one-closer-point obstruction for Erdős Problem 97

Date: 6 September 2026.

**Status: restricted paper-proof candidate with exact finite regression checks;
independent mathematical review pending.** No unrestricted proof or
counterexample to Erdős Problem 97 is claimed. No accepted finite-case bound,
repository status, published novelty, or external review is claimed.

## 1. Problem, notation, and result

For a finite planar set X and x in X, define

\[
 C_x(r)=\{y\in X\setminus\{x\}:|x-y|=r\},\qquad
 b_x(r)=|\{y\in X\setminus\{x\}:|x-y|<r\}|.
\]

Write M_X(x)=max_{r>0}|C_x(r)|, with value zero for a singleton. Erdős
Problem 97 asks whether every finite strictly convex vertex set X has an x
with M_X(x) <= 3. A hypothetical counterexample would have M_X(x) >= 4 at
every vertex. The radius may depend on the vertex.

Strictly convex position here means that every point is an extreme point of
conv(X), and, for at least three points, no three are collinear. Sets of one
or two distinct points are admitted using the usual convex-independence
convention; the conclusions for them are immediate.

### Theorem 1: minimum-layer deficiency

Let X be a nonempty finite set in strictly convex position. For each x in X,
assign a radius rho_x > 0 such that

\[
 b_x(\rho_x)\le1.                                      \tag{1}
\]

Put

\[
 r=\min_{x\in X}\rho_x,\quad
 Y=\{x\in X:\rho_x=r\},\quad m=|Y|,
\]

and count richness against the **full** set X:

\[
 B=\{p\in Y:|C_p(r)|\ge4\}.
\]

Then

\[
 \boxed{|B|\le\max(0,m-2).}                            \tag{2}
\]

Thus a minimum layer of at least two vertices contains at least two vertices
with at most three witnesses at the assigned radius. A singleton minimum
layer has no four-rich vertex.

### Theorem 2: no one-closer-point four-witness core

Under the hypotheses of Theorem 1, not every vertex can have four witnesses
at its assigned radius:

\[
 \boxed{\text{Some }x\in X\text{ satisfies }|C_x(\rho_x)|\le3.} \tag{3}
\]

There is no bound on |X|. The radii may all differ, and the hypotheses impose
no conic, symmetry, common-radius, incident-side, boundary-independence,
reciprocity, or minimal-counterexample condition.

**Quantifier boundary.** Equations (2) and (3) concern the assigned radii.
They do not assert that the identified vertices are good at every radius.
The unrestricted problem allows radii with two or more strictly closer
points; this proof does not eliminate that possibility.

## 2. Four hull witnesses contain a strictly short pair

### Lemma 1

Let p be a strict hull vertex of a finite strictly convex set. If four
other vertices a_1,a_2,a_3,a_4 satisfy |p-a_i|=r, then some two of them have
mutual distance strictly less than r.

### Proof

All rays from p to the other vertices lie inside the interior-angle cone at
p, whose width is strictly less than pi. Order the four selected rays by
angle. Their three successive positive angular gaps have sum less than pi.
At least one gap theta is therefore strictly less than pi/3. The two
corresponding witnesses have distance

\[
 2r\sin(\theta/2)<2r\sin(\pi/6)=r.
\]

The witnesses need not be consecutive on the polygon boundary. Ordering
rays from the fixed hull vertex is all that is used. QED.

**Why four matters.** Three rays have only two successive gaps. They can
have all three pairwise witness distances greater than r while spanning
less than pi. Section 7 gives an exact control.

## 3. Transferring the short pair into the minimum layer

### Lemma 2

Under (1), suppose p in Y has four radius-r witnesses. There exist a,b in Y
such that

\[
 |p-a|=|p-b|=r,\qquad |a-b|<r.                          \tag{4}
\]

### Proof

Lemma 1 supplies distinct witnesses a,b with |a-b|<r. Minimality gives
rho_a >= r. If rho_a > r, the two distinct vertices p and b are both
strictly closer to a than rho_a, since

\[
 |a-p|=r<\rho_a,\qquad |a-b|<r<\rho_a.
\]

This contradicts b_a(rho_a) <= 1. Hence rho_a=r. The same argument at b
proves rho_b=r. QED.

This is a radius comparison, not an assertion that witness membership is
reciprocal at arbitrary radii. Here the two equal-radius spokes become
reciprocal specifically because the endpoints have been forced into Y.

## 4. A matching of short edges forces planarity

The following geometric lemma is independent of the assigned-radius
problem and can be reused on its own.

### Lemma 3: threshold-graph planarity

Let Y be a finite strictly convex set and r>0. Suppose the graph consisting
of all pairs at distance strictly less than r is a matching. Then the
straight-line graph

\[
 G_r(Y)=(Y,\{\{a,b\}:|a-b|\le r\})
\]

is noncrossing. In particular, it is outerplanar in the inherited convex
order.

### Proof of the crossing inequalities used below

For a,b,c,d in counterclockwise convex order, let t be the intersection of
the diagonals ac and bd. Adding strict triangle inequalities through t gives

\[
 |ac|+|bd|>|ab|+|cd|,                                  \tag{5}
\]
\[
 |ac|+|bd|>|ad|+|bc|.                                  \tag{6}
\]

For example, |ab|<|at|+|tb| and |cd|<|ct|+|td| add to (5).
All lengths in (5)-(6) are ordinary Euclidean lengths, not squared lengths.
Strictness follows because the quadrilateral is strictly convex.

### Proof of Lemma 3

Suppose ac and bd are crossing edges of G_r(Y).

**Case 1: at least one diagonal is short.** Say |ac|<r. Since all short
edges form a matching, neither a nor c can have any other neighbor at
distance less than r. Each of the four sides ab,bc,cd,da is incident to a
or c, so all four have length at least r. But |ac|+|bd|<2r, contrary to (5).

**Case 2: neither diagonal is short.** Then |ac|=|bd|=r. By (5), at least
one of ab,cd is short. By (6), at least one of ad,bc is short. Any edge in
the first pair shares a vertex with any edge in the second pair. That
shared vertex has two short neighbors, again contradicting the matching
hypothesis.

Both cases are impossible. QED.

This is **not** a middle-neighbor forest assertion. G_r(Y) may have cycles,
including triangles; the proof only establishes noncrossing. Indeed, the
face count below uses those triangles rather than trying to forbid them.

## 5. Proof of the minimum-layer theorem

For y in Y, condition (1) says that at most one member of X is strictly
closer than r to y. Consequently the short-edge graph on Y is a matching.
Apply Lemma 3 to obtain the noncrossing graph G=G_r(Y).

Every p in B supplies, by Lemma 2, a triangle p,a,b in G with exactly one
short edge, its base ab. The other two edges have length r.

Every triangle of a noncrossing straight-line graph on strictly convex
vertices bounds a bounded triangular face. No other vertex can be inside
the triangle: it would fail to be extreme in conv(Y). No edge can pass
through the triangle without crossing one of its sides; overlapping sides
and passage through an unrelated vertex are excluded by strict convexity.
Thus no graph vertex or graph edge subdivides this triangle.

Assign one such triangular face to each p in B, choosing arbitrarily if
more than one is available. This assignment is injective. The face's
unique short edge identifies its opposite vertex p; the same triangular
face cannot be assigned to two different apices.

For m>=3, add the boundary edges and then noncrossing diagonals until G is
extended to a triangulation of the convex m-gon. Its bounded faces number
m-2, and all pre-existing triangular faces remain faces. Hence

\[
 |B|\le\#\{\text{triangular bounded faces of }G\}\le m-2.
\]

For m=1 or m=2, (4) cannot hold, so B is empty. This proves (2). Since Y is
nonempty and max(0,m-2)<m, there is a nonrich p in Y, proving (3). QED.

The graph need not be connected, and it need not contain all boundary
edges initially. Extending it to a triangulation handles both issues.

## 6. Consequences with carefully stated quantifiers

### 6.1 A second-nearest-distance window

For |X|>=3, let d_2(x) be the second smallest entry in the multiset

\[
 \{|x-y|:y\in X\setminus\{x\}\}.
\]

Ties are counted with multiplicity. For r>0,

\[
 r\le d_2(x)\quad\Longleftrightarrow\quad b_x(r)\le1.
\]

Therefore some x in X satisfies

\[
 \boxed{\forall\,0<r\le d_2(x),\quad |C_x(r)|\le3.}    \tag{7}
\]

Otherwise, at each x select one violating radius rho_x<=d_2(x). These
choices contradict Theorem 2. Sets of at most two points satisfy the
unrestricted desired conclusion directly.

### 6.2 Necessary condition on a hypothetical counterexample

If M_X(x)>=4 at every vertex, (7) still supplies a vertex x. At that vertex,
**every** radius with at least four witnesses must have at least two
strictly closer vertices:

\[
 |C_x(r)|\ge4\quad\Longrightarrow\quad b_x(r)\ge2.       \tag{8}
\]

This is a necessary condition, not a contradiction. The proof does not
show that an all-rich polygon admits a selection of radii satisfying (1).

### 6.3 Hereditary directed-graph formulation

Fix radii satisfying (1) relative to X. Put a directed edge x->y exactly
when |x-y|=rho_x. Every nonempty induced vertex subset Z contains a vertex
with at most three outgoing neighbors in Z. Indeed, the inherited radii
still have at most one strictly closer point in Z, so Theorem 2 applies to
Z. Thus this directed graph is 3-out-degenerate.

This concerns one fixed assignment of radii. It is not a bound on the
union of all four-rich classes, or on arbitrary directed witness graphs.

### 6.4 Relation to the earlier incident-side window

The repository's side-cap packet treats radii no larger than either of the
original incident polygon sides. The theorem here instead allows one
arbitrarily close vertex and does not bound a selected radius by those
sides. Section 7.3 gives a rich radius 1 with an incident side of squared
length 101/10000, while the one-closer condition holds.

Neither theorem is asserted to imply the other. In particular, no claim is
made that one vertex simultaneously supplies both window conclusions, or
that arbitrary mixtures of the two hypotheses admit a global obstruction.

## 7. Exact controls and sharpness

The coordinates and squared radii below are exact rationals. Full witness
rows, supporting-line determinants, and all-radius multiplicity profiles
are regenerated in verification.json.

### 7.1 Sharpness of the minimum-layer deficit

Use the strictly convex pentagon

\[
 p_0=(0,0),\quad p_1=(1,0),\quad p_2=(5/13,12/13),
 \quad p_3=(-4/5,3/5),\quad p_4=(-24/25,7/25),
\]

and assign squared radii

\[
 (\rho_0^2,\ldots,\rho_4^2)=(1,16/13,16/13,1,1).
\]

Every assigned radius is realized by an actual distance. The strict-closer
counts are (0,1,1,1,1), and the full assigned-radius witness rows are

```
0 -> {1,2,3,4}
1 -> {2}
2 -> {1}
3 -> {0}
4 -> {0}.
```

The minimum layer is Y={0,3,4}. Its only rich vertex is 0, so |B|=1=m-2.
The two-vertex deficiency cannot be universally increased even to three.
This does not claim that equality is geometrically achievable at every m.
The all-radius maximum multiplicities are (4,1,1,1,1).

### 7.2 Several short-base triangles can have one apex

The pentagon

\[
 (0,0),(24/25,7/25),(3/5,4/5),(-3/5,4/5),(-24/25,7/25)
\]

with every assigned radius 1 has strict-closer counts (0,1,1,1,1).
Its first vertex has four unit witnesses and two different short-base
triangles. The proof counts the rich center once, not twice. This example
also rules out the local statement that a single vertex satisfying the
one-closer hypothesis cannot be four-rich.

### 7.3 A permitted radius much longer than an incident side

Take

\[
 (0,0),(1/10,-1/100),(1,0),(5/13,12/13),
 (-4/5,3/5),(-24/25,7/25).
\]

At the first vertex, the last four displayed points are unit witnesses;
only (1/10,-1/100) is closer. The incident edge to that closer vertex has
squared length 101/10000. Assign each vertex its actual second-nearest
distance. The resulting squared radii are

\[
 (1,8101/10000,1,1,1,1),
\]

and all strict-closer counts are one. This is consistent with the theorem:
the minimum-radius vertex is not four-rich. The first vertex illustrates
why a second-nearest window is not merely an incident-side bound.

### 7.4 Four cannot be replaced by three in Lemma 1

For

\[
 (0,0),(1,0),(5/13,12/13),(-4/5,3/5),
\]

the first vertex has three unit witnesses, but all three pairwise distances
among those witnesses are greater than 1. The set is strictly convex.

## 8. Why the two-closer-point extension is not proved

Two exact controls distinguish failure of the present proof from a
counterexample to the original problem.

### 8.1 The minimum-layer deficiency itself fails with two closer points

Use the pentagon of Section 7.2 and assign the actual third-nearest
distance at each vertex. Its squared radius vector is

\[
 (1,338/125,36/25,36/25,338/125).
\]

The strict-closer counts are (0,2,2,2,2). The **unique** minimum-radius vertex
is the first vertex, which has four witnesses at radius 1. Thus (2) is
false under the weaker assumption b_x(rho_x)<=2.

The other four vertices are not four-rich at any radius. This is a
counterexample to the rank-two *minimum-layer claim*, not to Theorem 2
under its stated hypothesis, a possible rank-two core theorem, or Erdős 97.

### 8.2 Propagation can escape to a genuinely four-rich higher-radius center

The following eight points are strictly convex in cyclic order
[4,5,7,6,0,1,2,3]:

| Index | x | y |
|---:|---:|---:|
| 0 | 0 | 0 |
| 1 | 99/101 | 20/101 |
| 2 | 5/13 | 12/13 |
| 3 | 19/181 | 180/181 |
| 4 | -119/169 | 120/169 |
| 5 | -415195/252317 | 31052/252317 |
| 6 | -13579/8957 | -412/8957 |
| 7 | -62815/40729 | -684/40729 |

Assign rho_i^2=1 except rho_4^2=16/13. Then

\[
 C_0(1)=\{1,2,3,4\},\qquad
 C_4(4/\sqrt{13})=\{2,5,6,7\}.
\]

The strict-closer counts are (0,1,2,2,2,2,2,2). In particular,

\[
 |p_0-p_3|=|p_0-p_4|=1,\quad |p_3-p_4|<1,
 \quad \rho_4=4/\sqrt{13}>1.
\]

The target p_4 has precisely p_0 and p_3 strictly closer than rho_4. Unlike
in Lemma 2, two closer points are now allowed; the target is not forced
back to the minimum radius. Moreover, it is itself four-rich at its higher
radius. The all-radius maximum multiplicities are exactly

\[
 (4,1,1,1,4,1,1,1).
\]

All 48 supporting-line checks are strictly positive; their smallest
ordinary determinant is 162432/247911157. These facts are checked by exact
rational arithmetic, including every distance class rather than only the
two selected rich rows.

The formula that generates the control is also exact. Identify rational
pairs with complex numbers and put

\[
 U(t)=\frac{1-t^2+2it}{1+t^2},\qquad |U(t)|=1.
\]

Set p_0=0, and p_1,p_2,p_3,p_4 equal to U(t) at

\[
 t=1/10,\ 2/3,\ 9/10,\ 12/5.
\]

For v=p_2-p_4, set the last three points to p_4+v U(u), respectively, at

\[
 u=-38/7,\ -7/2,\ -15/4.
\]

This explains the two exact rich radii directly; the all-radius upper
bounds and convexity are separately checked. The assigned radius 1 at
indices 5,6,7 is not realized; this is permitted by the hypothesis under
examination. No claim that every selected row has four witnesses is made.

### 8.3 Planarity can fail with two short neighbors

In a unit square, set r=sqrt(2). Each vertex has two strictly closer
neighbors, and both diagonals belong to G_r. They cross. Thus Lemma 3 also
cannot simply replace its matching hypothesis by maximum short degree two.

Together these controls identify two separate difficulties for the next
regime: minimum-radius transfer and noncrossing can both fail. They do not
establish that a globally four-rich rank-two configuration exists.

## 9. Verification and limitations

Run with Python 3.10 or later; only its standard library is required:

```
python verify.py --check
python -m unittest -v test_bridge.py
```

The geometry checker rejects floating-point input. It uses exact rational
squared distances and all supporting-edge half-plane tests. Two fixtures
use the exact encoding (x,sqrt(3)*y); their distances are computed as
(dx)^2+3(dy)^2, not by an affine-invariance assumption about Euclidean
lengths. Equality is never inferred from a numerical residual.

The deterministic report checks 381 geometric fixtures and 12,902
rank-one radius assignments. It includes 255 nonempty subsets of the
eight-point control, but each subset is tested with its own permitted
rank-one radii; the rank-two radii are not silently treated as rank one.
There are 130 assignments with a rich minimum-layer center, 5,270
supporting-line checks, 861 separate common-scale planarity checks, and
3,207 crossing-quadrilateral checks. Tests with no rich minimum-layer
center are still useful hypothesis and graph regressions, not additional
rich examples.

A separate combinatorial routine enumerates all 196 triangulations of
convex polygons with 3 through 8 vertices and all 15,726 matching choices
on their edges. It verifies the triangular-face/apex accounting. These
abstract graphs need not have Euclidean edge-length realizations; this is
a check of the combinatorial layer, not a construction claim.

All 33 unit tests pass in the recorded run. They include exact equality
boundaries, invalid geometry, prohibited inputs, permutations, rational
similarities, subsets, and the rank-two failure controls.

**Limitations:** the arbitrary-size results depend on the written proofs,
not on finite enumeration. The geometric arguments have not been
formalized in a proof assistant or independently reviewed. The numerical
search that found the eight-point pattern was bounded and nonexhaustive;
its exact rational reconstruction, not its search residuals, is the
retained mathematical evidence. Repository-wide CI was not run, no PR was
opened in this continuation, and no source-of-truth repository status was
changed.

## 10. Remaining bridge

For the full problem, no proof has been obtained that an all-rich strictly
convex polygon admits rich radii with b_x(rho_x)<=1 at every vertex. Theorem
2 says it cannot. The necessary condition (8) isolates an unavoidable
higher-rank vertex, rather than proving that no counterexample exists.

The earlier conic/chain theorems likewise do not imply this radius-rank
hypothesis, and this packet does not force an all-rich polygon onto a
conic or into a one-deletion weak convex chain. What is now closed is the
arbitrary-size, variable-radius one-closer-point regime. The unrestricted
case, including rich radii with two or more strictly closer vertices,
remains unresolved by this work.
