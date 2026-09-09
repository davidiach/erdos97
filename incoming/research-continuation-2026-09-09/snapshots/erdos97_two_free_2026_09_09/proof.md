# Two internally supported vertices cannot close the fixed-seed cap

Research date: 9 September 2026. Repository baseline:
`047d05149382e48b602b292df4b8fc9e2da560bb`.

**Restricted computer-assisted proof candidate; independent mathematical review
pending. This is not a proof or counterexample to unrestricted Erdős #97, a
new accepted finite bound, a formal proof, or a claim of published novelty.**

## 1. The exact statement

Identify the plane with the complex numbers and put

\[
\omega=(-1+i\sqrt3)/2,\qquad
z(t)=-\frac12+\frac{3t}{1+3t^2}
+i\sqrt3\frac{1-3t^2}{2(1+3t^2)},
\]
\[
t_0=\frac1{10},\qquad t_1=\frac{83-3\sqrt{721}}{200}.
\]

Fix the nine-point old set

\[
P=\{\omega^k:0\le k<3\}
\cup\{\omega^k z(t_0):0\le k<3\}
\cup\{\omega^k\overline{z(t_1)}:0\le k<3\}.
\]

Label these groups consecutively, with rotation exponent increasing within
 each group. Its counterclockwise order is

```
4, 2, 6, 5, 0, 7, 3, 1, 8.
```

For a finite set S define

\[
C_S(x,r)=\{y\in S\setminus\{x\}:|x-y|=r\}.
\]

A point is *rich* if some positive radius has at least four witnesses. Let Q
be a nonempty finite set disjoint from P. Assume P union Q is strictly convex
and every point of Q is rich in P union Q. No richness assumption is made on
any old point.

Define the genuinely internally supported new vertices by

\[
I_P(Q)=\{q\in Q:\ \text{for every }r>0\text{ with }
|C_{P\cup Q}(q,r)|\ge4,\quad |C_P(q,r)|\le1\}.
\]

The assumption that every point of Q is rich is essential: this definition
is not being used vacuously at good new points. A point in I needs at least
three **other points of Q**, not necessarily three points of I, at each of
its rich radii.

> **Theorem 1 (new).** Under these hypotheses, \(|I_P(Q)|=2\) is impossible.

There is no assumption about symmetry, an arc carrier, common radii, a
prescribed witness pattern, or the number of added points. The old seed,
however, is fixed exactly as displayed.

The preceding packets, preserved inside `inputs/internal_support.zip`, give:

* I empty forces the unique next recurrence triangle, and that extension
  leaves the six old good vertices good;
* \(|I|=1\) is impossible.

Combining those results with Theorem 1 gives the following restricted
consequence for an actual counterexample extending this seed.

> **Corollary 2.** If every point of P union Q is rich, then
> \(|I_P(Q)|\ge3\).

Section 8 gives an exact rich cap with \(|I|=3\). Thus three is attained among
rich caps with nonempty I. That example does **not** make the old points all
rich, so it does not establish sharpness of a bound for complete all-rich
repairs.

## 2. Fixed-seed geometry and the finite reduction

All base computations use pairs (x,y) denoting Cartesian (x,sqrt(3)y). The
squared norm is x²+3y². Coordinates and all initial domain endpoints lie in
Q(sqrt(721)); multiplying an orientation determinant in these coordinates
by the positive number sqrt(3) gives its Cartesian determinant.

### 2.1 Old-witness ceiling

A genuinely new point x such that P union {x} is strictly convex can have at
most two equidistant old points at any radius. This is a checked finite fact
about P, not an asserted property of arbitrary old polygons.

The complete computation enumerates the 84 old triples. All are
noncollinear. Their 64 distinct circumcenters are either an old point (six
centers) or prevent strict convex extension. The other 58 have an explicit
certificate putting one of the ten points P union {x} in the closed triangle
of three others: 55 containments are strict and three have a zero boundary
sign. Such a point cannot be an extreme vertex. Both implementations
reconstruct the circumcenter equalities and these containment signs.

Every point equidistant from three old points would have to be one of these
centers. This proves the ceiling. The inherited certificate SHA256 is
`753f31b4c80dcb044025ef35dfcdd7172bbb31d7fd7ebe2a0ff092a03ce9e941`.

### 2.2 Insertion cells

A new point preserving all old extreme vertices can see only one old edge:
seeing two consecutive old edges would make their intervening old vertex
non-extreme. Strict convexity also prohibits lying on an old side line in a
way that would retain three collinear vertices. Thus there are nine possible
open insertion cells, indexed by the old edge in the displayed order.

For a cell with old edge a,b, intersect the lines of the preceding and
following old sides at v. For this particular seed, T=(a,v,b) is a positively
oriented bounded triangle covering the closure of that cell. The vertex v is
beyond a,b and lies in the closed inward half-planes of the other old sides.
These assertions, including the coverage signs for all nine cells, are
recomputed exactly. They are not assumed for an arbitrary convex polygon.

We use all of T. Its boundary includes inadmissible degeneracies; that is a
safe enlargement for a nonexistence proof.

### 2.3 Two-old-supported slots and capacity one

If x has equal distance to two chosen old points a,b, write its perpendicular
bisector as

\[
x(s)=m+s v,\quad m=(a+b)/2,\quad v\perp(b-a),\ v\ne0.
\]

Clipping each of the 36 bisectors against each of the nine strict insertion
cells gives exactly 42 nonempty bounded open intervals, or *slots*. The
primary construction intersects the linear strict half-plane inequalities;
the separate implementation constructs ray exits. No nonempty interval is
silently dropped because it would be unbounded: the code fails in that case.
For this seed every retained slot is bounded and lies on one open ray from m.

Each slot has capacity at most one. If two distinct points on the same ray
are x=m+s v and y=m+t v with 0<s<t, then

\[
x=\frac{1-s/t}{2}a+\frac{1-s/t}{2}b+\frac{s}{t}y
\]

is strictly inside triangle a,b,y. The negative ray is identical after
reversing its direction. All four points cannot belong to a strictly convex
set. This capacity argument needs no richness or symmetry.

For two different slots i,j, the equation needed for i to use j at its
assigned old-pair radius is

\[
|x_i(s)-x_j(t)|^2-|x_i(s)-a_i|^2=0.
\]

The expression is affine in s and convex quadratic in t. Source endpoints
and target endpoints or stationary points therefore give its exact range on
the closed rectangle. The 1,722 ordered tests retain 123 possible directed
edges. They are recomputed by both implementations; an edge means only
"not ruled out by this necessary test."

### 2.4 Why there is no arbitrary cap-size cutoff

Suppose I={f,g}. At every ordinary q in Q minus {f,g}, choose a rich radius
with two old witnesses, which is possible by definition of I and the ceiling.
Assign q to its slot. The assignments are injective by the capacity lemma.
Choose four witnesses at each such radius, retaining the two old witnesses
and any two new ones. At f and g, choose any rich radius and four witnesses;
there are zero or one old witnesses and respectively four or three new ones.

Every hypothetical cap in Theorem 1 therefore maps into 42 ordinary slots
and two free points. In particular it has at most 44 new vertices. This
bound is a consequence of the geometry and hypotheses, not a search cutoff
chosen in advance.

The model is deliberately more permissive than the theorem: it does not
need to establish that f or g lack a different two-old-supported rich
radius, and it does not impose richness on the old points.

## 3. Covering both free points and their radii

Order the two cell indices a<=b, relabeling f and g as necessary. Even if a=b,
no relative order of f,g inside their common cell is prescribed. There are
45 unordered cell pairs. Each free point has ten old-support cases: one of
the nine specified old witnesses or no old witness. Thus there are exactly

\[
45\cdot10\cdot10=4500
\]

cases. All are retained explicitly; no rotational identification is needed.

The position domain for a case is the closed product T_a times T_b. A node
of the certificate bisects one triangle across an edge midpoint and retains
**both** children. The two child products cover the parent including the
common seam. Certificate validation checks exact midpoint construction,
positive child orientation, complete case coverage, and both children at
every internal node.

The final forest contains 24,742 nodes and 14,621 leaves, with maximum depth
36. Every leaf is rejected. An unresolved leaf, a missing child, a search
node guard, or a depth guard is an error, not an exclusion.

## 4. Continuous-domain distance tests

Write D(x,y)=|x-y|² in the true Euclidean norm. Every test below ranges over
an entire closed segment or triangle; no sample grid or floating residual
is used to decide a sign.

### 4.1 Ordinary source using a free witness

For an ordinary slot x(s) with old witness a and a free point f in T,

\[
H(s,f)=D(x(s),f)-D(x(s),a)
\]

is affine in s. Its extrema use the two slot endpoints. At either endpoint
x, the minimum over f is the squared distance from x to T minus D(x,a),
and the maximum is attained at a vertex of T. Keep the directed edge only
if the resulting closed range contains zero.

### 4.2 One-old free source using an ordinary witness

For free f with fixed old witness a,

\[
J(f,s)=D(f,x(s))-D(f,a)
\]

is affine in f. Its extrema therefore use triangle vertices. At each such
vertex it is a convex quadratic in s, so endpoints and an in-range
stationary point exhaust the extrema. The independent checker reconstructs
the quadratic from evaluations rather than importing the primary expansion.

### 4.3 One-old free source using the other free point

For f in T, g in U and fixed old witness a,

\[
K(f,g)=D(f,g)-D(f,a)
\]

is affine in f. For each vertex f of T, its minimum over U is the distance
from f to U squared minus D(f,a), and its maximum occurs at a vertex of U.
The direction g to f is checked separately, using g's old witness.

### 4.4 A free source with no old witness

No fixed radius is available. For each potential target slot or other free
triangle compute the entire closed interval [L_j,U_j] of squared distances
from the source triangle to that target domain. A segment-triangle distance
or triangle-triangle distance gives the minimum. The maximum is attained
among pairs of domain vertices.

The primary implementation uses intersections and nearest-point projections.
The separate implementation takes the convex hull of the Minkowski
differences and computes its squared distance from the origin. The two
methods operate in independent exact arithmetic representations.

If four actual witnesses have one common squared radius, their four distance
intervals share a point. Let l be the largest of their lower endpoints. Then
all four intervals contain l. Consequently the inclusion-maximal target
sets present at interval endpoints cover every possible choice of a common
radius. The primary checker considers both kinds of endpoints; the separate
checker uses lower endpoints only. Both yield the same maximal cover sets.

This does not pretend that all edges in a cover can be realized
simultaneously. It is a necessary common-radius restriction, subsequently
combined with the simultaneous witness-row tests below.

## 5. A complete necessary witness-row search

Use new indices 0..41 for the ordinary slots and 42,43 for f,g. Their
physical labels are 9..50,51,52; the old labels remain 0..8.

An occupied ordinary slot needs two occupied new out-neighbors; a free
vertex needs three or four according to its old-support case. Delete any
node with fewer available out-neighbors than required, repeating to a fixed
point. No occupied vertex of an actual realization can be the first removed
occupied vertex. Therefore every actual cap survives this deletion. If
either mandatory free vertex is removed, the subdomain is impossible.

For each remaining common-radius cover, enumerate every full four-witness
row from the fixed old support and the available new targets. Then search
for a witness-closed set containing both f,g. Every other slot is optional.
An assigned row makes all of its new witnesses mandatory in turn.

At each step choose an as-yet unassigned mandatory source, branch over every
compatible row, and propagate empty row domains. A target whose rich row
has become impossible cannot be used as a witness. The search is exhaustive;
there is no optimizer decision inside the proof checker.

Only a reachable witness-closed subset is needed. In an actual cap, start
from f,g and follow the chosen new-witness edges. This gives such a finite
subset. Every selected row remains present, and deleting other points does
not destroy strict convexity. Thus rejection of every closed subset rules
out the original cap, even when the original cap had unused components.

### 5.1 Two-circle and crossing constraints

Two distinct selected source circles cannot share three witnesses. If two
rows share exactly two witnesses a,b, their centers lie on the perpendicular
bisector of a,b. They must lie on opposite rays from the midpoint; otherwise
the nearer center is inside the triangle formed by the farther center,a,b.
Therefore the source chord and witness chord cross, and their four endpoints
alternate in the polygon's cyclic order.

Taking a subset of a strictly convex polygon preserves its cyclic order.
Thus all new points belonging to cell k occur between the endpoints of that
old edge in the full polygon. Old points get even cyclic ranks 2k, and points
inserted into cell k get rank 2k+1. All orders within a tied rank are allowed. The primary test
enumerates the 24 orders of the four labels consistent with these weak ranks;
the independent test counts cyclic descents of the alternating sequences.
These encodings agree on all 256 four-label rank assignments in {0,1,2,3}.
No unjustified order within a cell is imposed.

### 5.2 Global consistency of ordinary distances

A complete row selection can still pass pairwise circle checks while forcing
incompatible equalities between distances belonging to different centers.
This is exactly what happened in the last three geometric subdomains.

For four distinct convex points a,b,c,d in cyclic order, intersect the
diagonals and apply strict triangle inequalities to obtain

\[
d_{ac}+d_{bd}>d_{ab}+d_{cd},\qquad
 d_{ac}+d_{bd}>d_{ad}+d_{bc}.
\]

Here d is ordinary, not squared, Euclidean distance. Equal selected squared
distances imply equal ordinary distances because all distances are positive.

Build the equivalence classes of unordered chords forced by all selected
rows. Express each displayed strict inequality in those classes. Use only
quadruples with four distinct weak ranks, so that their order is forced
without any choice within a cell. Reject a selection if one coefficient
vector is zero or if two such vectors are negatives of one another.
The resulting strict sum would be 0>0.

The primary implementation uses a union-find quotient and integer vectors.
The independent implementation uses connected components and cancellation
of signed multisets, traversing the quadrilaterals in reverse order. A third
small arithmetic routine checks the retained explicit cancellation records.
No linear-program infeasibility status is trusted.

If this test finds nothing, the selected system is **not** called realizable.
It is retained as a necessary abstract assignment, and the geometric domain
must be refined further or reported unresolved. In the delivered partition,
no such assignment remains at any leaf.

## 6. The terminal obstruction and the completed finite computation

The first sweep subdivided to depth 20. Eighteen support/region cases required
further refinement. Refinement to depth 36 closed all but three final product
subdomains, in the cases

```
cells (2,5), old witnesses (3,4)
cells (2,8), old witnesses (3,5)
cells (5,8), old witnesses (4,5).
```

They approached old vertices rather than yielding exact geometric candidates.
Their abstract rows were nevertheless retained and tested, not dismissed
because their numerical appearance was degenerate.

There are exactly 24 distinct terminal witness-closed systems across those
three subdomains. Each has an exact zero or two-inequality cancellation.
The primary chooses two zero and 22 inverse certificates. The independent
traversal chooses six zero and 18 inverse certificates. These are different
choices of a rejecting certificate, not a disagreement about any survivor.
All 24 systems and their explicit primary certificates are retained in
`data/last_leaf_cancellations.json`.

### A short readable instance

One retained system has the selected equalities

\[
 d_{52,39}=d_{52,31},\quad
 d_{11,31}=d_{11,0},\quad
 d_{15,39}=d_{15,0}.
\]

The forced cyclic quadrilateral orders are (39,31,52,15) and (31,0,11,15).
Their strict inequalities give

\[
 d_{39,52}+d_{31,15}>d_{39,15}+d_{31,52}
 \quad\Longrightarrow\quad d_{31,15}>d_{39,15},
\]
\[
 d_{31,11}+d_{0,15}>d_{31,15}+d_{0,11}
 \quad\Longrightarrow\quad d_{0,15}>d_{31,15}.
\]

But d_{39,15}=d_{0,15}. This is a strict two-cycle. Each displayed equality
comes from a different selected center. It illustrates why separately
possible edges were insufficient. This use of strict convex-distance
inequalities is an application of the existing method, not a novelty claim
for those inequalities.

### Full replay results

| Quantity | Primary | Separate checker |
|---|---:|---:|
| Support/region cases | 4,500 | 4,500 |
| Partition nodes | 24,742 | 24,742 |
| Closed leaves | 14,621 | 14,621 |
| Maximum subdivision depth | 36 | 36 |
| Remaining row models tested | 14,146 | 14,146 |
| Exact row-search nodes | 1,170,689 | 1,069,214 |
| Terminal metric rejections | 24 | 24 |
| Unresolved leaves | 0 | 0 |

The row-search counts differ because the independent checker reverses
variable tie-breaking and candidate order. Both recompute the geometry and
reject every covered domain. The independent radical-sign decisions used
outward rational square-root enclosures; its largest required enclosure
precision was 32 bits. This is exact sign certification, not floating-point
coordinate precision or a distance tolerance.

Sections 2–5 show that a hypothetical cap with I={f,g} must survive in at least
one of these cases and leaves and must produce a surviving closed row
assignment. The finite replay shows that none exists. This proves Theorem 1,
subject to review of the written reductions and checker implementations.

## 7. What was—and was not—enforced

The proof enforces fixed old coordinates, the full domains of both free
points, their support cases, common radius covers when no old witness fixes a
radius, the distance equalities implied by all selected rows, witness closure, pairwise circle limits,
forced cyclic crossing, and the stated strict convex-distance cancellations.

It does **not** solve every simultaneous coordinate equation directly. Rather,
it proves that already these necessary consequences are inconsistent on the
complete covered domain. It also does not need mutual convexity constraints
between every possible pair of new slots: omitting some necessary conditions
only enlarges the rejected domain.

Neither numerical optimization nor a sampled coordinate grid establishes the
exclusion. A solver timeout, missing branch, unresolved closed subset, or
zero-only boundary situation is never interpreted as an impossibility proof.

## 8. An exact control attaining three internally supported vertices

Use the already known recurrence

\[
t_{j+1}=\frac{1-2t_j+3t_j^2-
\sqrt{(1-t_j)(1-3t_j)(1+3t_j^2)}}2,
\]

with the positive square root and t0=1/10, and define a_j=z(t_j) for even j
and conjugate(z(t_j)) for odd j. The old seed comprises the anchors,a0,a1.
Set

\[
Q=T(a_2)\cup T(a_3),\qquad T(a)=\{a,\omega a,\omega^2 a\}.
\]

This is a known recurrence member, **not a newly discovered construction**.
The new packet verifies this specific 15-point set directly, without assuming
the earlier arbitrary-length convexity argument has been accepted.

For every j>=1, each rotated a_j has the four named witnesses

\[
\omega^k,\quad\omega^k a_{j-1},\quad
\omega^{k+1}a_j,\quad\omega^{k+2}a_j.
\]

The equalities follow from the defining recurrence and the exact identity

\[
|\overline{z(s)}-z(t)|^2-3|z(s)|^2
=-\frac{9\{s^2-(1-2t+3t^2)s+t^2\}}
 {(1+3s^2)(1+3t^2)}.
\]

The first control checker uses a tower of three positive quadratic radicals
and reduces every sign recursively to rational signs. It checks every
distance class and all 195 strict supporting-half-plane inequalities in the
explicit order

```
4,10,2,12,6,5,11,0,13,7,3,9,1,14,8.
```

The separate control checker imports none of that arithmetic. It establishes
six universal identities by rational polynomial expansion and uses 512-bit
outward dyadic integer enclosures for strict inequalities and all-radius
upper bounds. Distinct radius classes have disjoint interval groups; these
bounds meet the exact lower multiplicities supplied by the identities.
Small residuals are not accepted as equalities.

Both give the complete maximum-multiplicity census

\[
(2,2,2,\ 3,3,3,\ 4,4,4,\ 4,4,4,\ 4,4,4).
\]

Every added point is rich. Each point of T(a2) has its rich class supported
by two old points: its anchor and a1. Each point of T(a3) has exactly one old
witness, its anchor, and three new witnesses. The all-radius census certifies
that it has no alternative rich radius with two old witnesses. Consequently

\[
I_P(Q)=T(a_3),\qquad |I_P(Q)|=3.
\]

The old six exceptions remain good. Thus this attains the internal-support
threshold among rich caps, but is not an all-rich polygon, does not repair the
seed, and does not prove that three internally supported vertices suffice
for a complete repair.

## 9. Reproducibility and independent-review boundary

Run the commands in README.md. The 4,500-case certificate is a complete binary
partition, not a list of numerical optimizer outcomes. Its generator checks
partition-path coverage; both mathematical replayers independently reject
all leaves. Exact final cancellation records have an additional small
arithmetic checker. The entire preceding packet is hash-bound and retained
byte-for-byte, including its nested earlier packets.

The separate implementation uses different arithmetic, geometric extrema,
common-radius cover construction, graph deletion order, witness-search
order, crossing test, and distance-quotient representation. This improves
implementation diversity. Both implementations were nevertheless produced
in this research session; **this is not external independent mathematical
review or a Lean formalization**.

Reviewers should scrutinize the insertion-cell cover, the one-slot-per-new-
vertex reduction, the quantifiers on selected versus all rich radii, the
soundness and completeness of witness-closed subset search, all physical-label
and cyclic-rank conversions, and the strict ordinary-distance inequalities.
The checked inequalities do not by themselves formalize those geometric
arguments.

The unrestricted problem remains outside this theorem. A three-or-more-
internally-supported cap capable of making all old points rich, a construction
moving the old seed, and counterexamples not containing this seed are not
excluded here. No new unrestricted finite lower bound or repository accepted
claim is inferred.
