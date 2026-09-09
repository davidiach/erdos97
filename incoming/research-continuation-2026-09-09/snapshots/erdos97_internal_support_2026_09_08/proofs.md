# One internally supported cap vertex is not enough

Research date: 8 September 2026. Repository baseline:
`047d05149382e48b602b292df4b8fc9e2da560bb`.

**Restricted computer-assisted theorem and elementary lemmas; independent
mathematical review pending. No unrestricted proof, counterexample, accepted
status transition, Lean formalization, or novelty claim is made.**

## 1. Exact seed and statement

Identify the Euclidean plane with the complex numbers. Let

\[
 \omega=(-1+i\sqrt3)/2,\qquad
 z(t)=-\tfrac12+\frac{3t}{1+3t^2}
       +i\sqrt3\frac{1-3t^2}{2(1+3t^2)},
\]
\[
 t_0=\tfrac1{10},\qquad t_1=\frac{83-3\sqrt{721}}{200}.
\]
The **fixed old set** is
\[
 P=\{\omega^k:0\le k<3\}
   \cup\{\omega^kz(t_0):0\le k<3\}
   \cup\{\omega^k\overline{z(t_1)}:0\le k<3\}.
\]
Label the three groups consecutively, with rotation exponent increasing
within each group. The counterclockwise boundary order is
`[4,2,6,5,0,7,3,1,8]`.

For a finite point set S, write
\[
 C_S(x,r)=\{y\in S\setminus\{x\}:|x-y|=r\}.
\]
A vertex is *rich* if some positive radius has at least four witnesses.
Assume throughout the main theorem that Q is a nonempty finite set disjoint
from P, that P union Q is in strictly convex position, and that every point
of Q is rich in P union Q. The points of P need **not** be rich.

Define
\[
 I_P(Q)=\{q\in Q:\ \text{every }r>0\text{ with }|C_{P\cup Q}(q,r)|\ge4
                 \text{ has }|C_P(q,r)|\le1\}.
\]
These are the new vertices that cannot choose a rich radius supported by two
old points. Each of their rich radii needs at least three other points of Q.
This does **not** mean three witnesses in I_P(Q); the witnesses can be other
cap vertices.

> **Theorem 1.** Under these hypotheses, `|I_P(Q)| = 1` is impossible.

The theorem has no assumed symmetry, carrier, shared radius, selected witness
pattern, or cap-size cutoff. The old seed is exactly the one displayed above.

The preceding delivered packet proves that `I_P(Q)` empty forces Q to be the
unique next recurrence triangle, and verifies that the old six good vertices
remain good in that extension. Together these give:

> **Corollary 2.** If the entire set P union Q is rich, then
> `|I_P(Q)| >= 2`.

Thus the previous lower bound of one genuinely internally supported new
vertex improves to two. No theorem about two or more such vertices is proved
here. Moving the old seed invalidates the fixed-seed certificates.

## 2. Replayed prerequisites and their scope

The preceding packet is retained, byte for byte, in `inputs/cap_closure.zip`.
Its SHA256 is

```
0a81018d0cb791362dda69506bc5044b260ef8d21d8627820dcf5f86234cc33c
```

The loader checks this before loading any inherited implementation. The
complete inherited replay, including its 30 tests and the earlier 31 tests,
was rerun in this research session. Its reports are retained separately from
this packet's new tests.

Two prerequisites enter Theorem 1.

**Old-witness ceiling.** If x is genuinely new and P union {x} is in strict
convex position, x has at most two equidistant points in P at every radius.
Every triple of P is noncollinear. A point equidistant from three old points
must be their circumcenter. All 84 triples give 64 distinct circumcenters:
six are old points, and each other center has an exact containment certificate
preventing a strict convex extension. Both arithmetic implementations replay
this enumeration. This is a fact about this particular P, not all old sets.

**Old-pair slots.** For each old pair a,b, potential points equidistant from
a,b lie on their perpendicular bisector. Write such a line as
`x(s) = m + s v`. Exact oriented-half-plane inequalities characterize where
inserting x preserves every old vertex. They produce 42 open intervals,
called *slots*. Each lies entirely in one open ray from the midpoint m.
All endpoints and line coordinates lie in Q(sqrt(721)), in the convention
that `(x,y)` denotes the Cartesian point `(x,sqrt(3)*y)`.

There is at most one cap vertex in any one slot. In fact, if
`x = m+s v`, `y=m+t v` lie on the same ray, `0<s<t`, then
\[
 x=(1-s/t)\tfrac{a+b}{2}+(s/t)y
\]
is strictly inside the triangle a,b,y. A strictly convex point set cannot
contain all four points. The negative-ray case is identical after reversal.
This capacity statement needs neither richness nor fixed witness radii.

A rich new vertex that can use two old witnesses can be assigned one of the
42 slots, with its chosen old pair and chosen rich radius. The ceiling makes
that old contribution exactly two. Distinct assigned vertices occupy
distinct slots. The actual number of other equidistant new vertices may
exceed two; using the lower bound two only enlarges the search domain.

The inherited exact rectangle tests give 123 possible directed edges between
distinct slots. An edge i -> j is retained whenever some parameters in their
**closed** intervals could satisfy
\[
 |x_i-x_j|^2=|x_i-a_i|^2,
\]
where a_i is either member of i's assigned old pair. These tests are
necessary, not sufficient, and the closure admits boundary degeneracies that
actual strict convex sets cannot use. Enlarging in this way is safe for an
exclusion. The whole graph, all 1,722 ordered slot-pair tests, and the inherited
range digest are rebuilt, not accepted from a stored list.

## 3. Covering the free vertex without discretizing its position

Suppose for contradiction that I_P(Q) consists of one point f. Assign each
other cap vertex a two-old rich radius and its slot as above. Choose any rich
radius of f. By the definition of I_P(Q), it has either zero old witnesses
or exactly one, a member of the nine-point P.

A single point that can be added without destroying the original convex
vertices can see only one old edge. Seeing two consecutive old edges makes
their intervening old vertex non-extreme; seeing a longer visible chain
likewise removes an old vertex. Boundary collinearities are forbidden by
strict convexity. Thus f lies in one of nine insertion cells.

For old edge a,b, intersect the preceding and following side lines to obtain
v. For this seed the resulting triangle T=(a,v,b) has positive orientation,
and v is strictly beyond edge a,b and in the closed inward half-plane of
every other old edge. These facts are verified by exact signs for every cell.
The closure of the allowable insertion cell is contained in this triangle.
Using all of T may admit extra points; it does not omit an admissible f.

Consequently the full free-vertex domain is covered by

* nine triangle cells with one of nine specified old witnesses; and
* nine triangle cells with no old witness.

There are 90 cases. No rotational quotient is used. All nine rotations are
checked explicitly, avoiding an unproved identification of slot labels.

Each triangle can be split along the midpoint of one edge into two closed
triangles. Their union is the parent, and their intersection is their common
edge. The primary generator selects a longest edge; the second checker
requires only a valid edge and exact midpoint subdivision. Leaves include
boundaries, so repeated subdivision cannot create uncovered open seams.
A configured depth limit is a computational guard: reaching it while
unresolved raises an error, rather than claiming an exclusion. No case in
the retained run reached an unresolved leaf.

## 4. Exact range bounds on an entire triangle and slot

Use the true Euclidean norm, written in scaled coordinates as
`||(x,y)||^2=x^2+3y^2`. For a slot `x(s)=m+s v`, `s in [l,u]`, and free vertex
`f in T`, the following bounds are computed exactly.

### 4.1 Ordinary source, free witness

The necessary equation for slot i to use f is
\[
 H(s,f)=|x(s)-f|^2-|x(s)-a_i|^2=0.
\]
For fixed f, H is affine in s, since the quadratic terms cancel. Hence both
global extremes use s=l or s=u. At either endpoint x, the minimum over f is
`dist(x,T)^2-|x-a_i|^2`; the maximum is attained at a triangle vertex. Distance
to a closed triangle is zero for an interior point and otherwise is the
minimum of the exact projections onto its three edges. Retain i -> f only
when the resulting closed range contains zero.

### 4.2 Free source with one old witness

When f's chosen old witness is a, the necessary equation for f to use slot i
is
\[
 J(s,f)=|f-x(s)|^2-|f-a|^2=0.
\]
For fixed s it is affine in f. Therefore its extrema over T occur at triangle
vertices. At each such vertex it is a convex quadratic in s. The maximum is
at a slot endpoint; the minimum is at an endpoint or the stationary point if
that point belongs to [l,u]. All those values lie in the base exact field.
The separate checker derives the quadratic by evaluations at 0,+1,-1 rather
than importing the primary coefficient formula.

### 4.3 Free source with no old witness

Here the radius itself is unknown. For each slot compute the interval
\[
 [L_i,U_i]=\operatorname{range}\{|f-x_i(s)|^2:f\in T,\ l_i\le s\le u_i\}.
\]
The maximum is attained among the six endpoint/triangle-vertex pairs. The
minimum is the squared distance between the closed slot segment and T.
The primary implementation uses exact segment-triangle intersection and
nearest endpoint/edge projections. The separate checker builds the convex
hull of the six Minkowski differences and finds the squared distance of the
origin to that convex hull. These are different constructions of the same
convex distance minimum.

All range decisions use exact algebraic signs or outward rational square-root
enclosures. Neither residual thresholds nor sampled grids establish a sign.

## 5. The dependency argument at each leaf

Build a directed graph on the 42 ordinary slots plus f. The slot-to-slot
edges are the inherited necessary edges; slot-to-f edges use Section 4.1.

Any actual occupied ordinary slot must have at least two distinct occupied
out-neighbors. When f has one old witness, it needs at least three ordinary
out-neighbors, and its possible edges use Section 4.2. When it has no old
witness, it needs at least four ordinary out-neighbors.

Repeatedly delete vertices with fewer than the required number of currently
available out-neighbors. No actual occupied vertex can be the first deleted
occupied vertex: all its actual witnesses would still be present. Induction
therefore shows that an actual configuration survives every deletion. If f
is deleted, that domain is impossible. The two implementations use batch
versus reverse sequential deletion and verify the same terminal core.

### One-old case

The triangle/slot range bounds, followed by this degree deletion, exclude all
81 cases after exact subdivision. No circle-sharing lemma is needed at their
terminal leaves.

### Zero-old case: common radius and forced rows

First allow f to point to every ordinary slot, then delete by degree. For the
remaining slots, compute [L_i,U_i]. At an actual squared radius r, all actual
witness slots must have intervals containing r.

Every such target set is contained in a target set at an interval endpoint:
choose the maximum of the lower endpoints of the intervals in the actual
set. That endpoint still lies in each of those intervals. Thus the finitely
many inclusion-maximal endpoint target sets cover every possible common
radius. Retain only sets of size at least four, restrict f's outgoing edges
to each set in turn, and repeat the degree deletion.

If f survives, an ordinary slot with exactly two available outgoing neighbors
must use **both**, in addition to its two assigned old witnesses. These four
witnesses are compulsory if that slot is occupied. Two occupied distinct
centers cannot have three common compulsory witnesses: their distinct
centered circles would have three intersection points, which is impossible.

The certificate lists these incompatible pairs. For every four-element subset
of f's remaining possible targets, it gives an incompatible pair contained
in that subset. Since f needs at least four distinct witnesses, none of the
subsets can be realized. This excludes the leaf. The checker reconstructs
every compulsory row and every four-element subset; omission is rejected.

Witness labels are kept distinct throughout: old points have labels 0..8;
ordinary slot i has abstract label 9+i; f has abstract label 51. These are
roles in a necessary relaxation, not claimed coordinates of a realization.

## 6. Complete certificate census and conclusion

`data/one_free_certificate.json` records:

| Free vertex's old support | Cases | Tree nodes | Leaves | Maximum depth |
|---|---:|---:|---:|---:|
| Exactly one old witness | 81 | 345 | 213 | 7 |
| No old witness | 9 | 15 | 12 | 1 |
| Total | 90 | 360 | 225 | 7 |

The zero-old leaves contain 33 compulsory-pair conflict records and cover
153 four-subsets in total. These counts refer to stored branches; they are
not counts of all possible geometric configurations.

Every admissible position and old-support choice for f belongs to one of the
90 root domains. Every root is covered by its exact subdivision tree, and
every leaf is impossible by Section 5. Therefore the assumed f cannot exist.
This proves Theorem 1, conditional only on the explicitly replayed
fixed-seed prerequisites and the written geometric reductions.

The preceding cap classification handles I_P(Q) empty. Its sole extension
has maxima `(2,2,2,3,3,3,4,4,4,4,4,4)`, so it is not all-rich. Applying
Theorem 1 to the remaining possibility proves Corollary 2.

The finite calculation is not an arbitrary numerical cutoff: ordinary
vertices are injected into the 42 slots before computation. In particular,
one-free caps automatically have at most 43 new vertices. No statement that
an arbitrary counterexample has at most 52 vertices is implied.

## 7. Positive control: the exclusion is not universal over old seeds

Here is a rational, strictly convex 14-point set with a designated four-point
rich cap and **exactly one** member of I relative to a different ten-point old
set. This prevents overgeneralizing Theorem 1.

Let the four new points be
\[
 q_0=(0,0),\quad q_1=(1,0),\quad q_2=(3/5,4/5),\quad q_3=(0,1).
\]
For rational t define the rational rotation
\[
 R_t(x,y)=\frac{((1-t^2)x-2ty,\ 2tx+(1-t^2)y)}{1+t^2}.
\]
The ten old points, in label order 4..13, are
\[
 R_{1/100}q_2;
 \quad q_1+R_{k/100}(q_3-q_1),\ k=1,2,3;
\]
\[
 q_3+R_{k/100}(q_1-q_3),\ k=1,2,3;
 \quad q_2+R_{k/100}(q_0-q_2),\ k=1,2,3.
\]
The boundary order is
`[7,0,11,12,13,1,8,9,10,2,4,3,5,6]`.
All 168 strict supporting signs and all 91 distinct pairs are checked. The
minimum supporting determinant is `2000000/250350122509`.
The complete rich classes are:

| Center | Squared radius | Witnesses | Old / new contributions |
|---|---:|---|---|
| 0 | 1 | 1,2,3,4 | 1 old, 3 new |
| 1 | 2 | 3,5,6,7 | 3 old, 1 new |
| 2 | 1 | 0,11,12,13 | 3 old, 1 new |
| 3 | 2 | 1,8,9,10 | 3 old, 1 new |

Every old point has all-radius maximum multiplicity one. Thus I={q_0}, but
this is **not** an all-rich polygon and not an improvement in the number of
good vertices. Its role is hypothesis calibration. Rational rotations and
convex-arc repair reuse the earlier packet's elementary repair mechanism.

A separate check converts each rational point to integer homogeneous
coordinates, evaluates 3-by-3 determinants, and compares squared-distance
ratios. It reproduces the full census without calling the primary geometry
functions.

## 8. Moving-seed branch: a symmetry-free cluster resource restriction

The following elementary capacity fact is already implicit in the repository's
base-apex/crossing-bisector arguments, and is reused rather than claimed as a
new general geometric principle.

**Pair capacity.** For two vertices a,b of a strictly convex polygon, at most
one other vertex on either given open side of line ab can be equidistant from
a,b. Such vertices lie on one ray of the perpendicular bisector; two on that
ray give the strict triangle containment from Section 2.

Partition a polygon's cyclic order into consecutive clusters. All vertices
outside a given cluster lie on the same open side of any chord joining two
vertices in that cluster. Thus an internal pair can serve as equal-distance
witnesses to at most one outside center.

> **Two-copy obstruction.** Suppose there are m consecutive clusters of two
> vertices each. It is impossible for every one of the 2m centers to select
> four equidistant witnesses drawn from at most three **other** clusters.

Each four-witness row uses an internal pair by pigeonhole. Each of the m
internal pairs has outside-center capacity one. The required at least 2m
pair uses exceed m. This proof permits arbitrary coordinates, different
radii, and nonsymmetric deformations. It assumes the consecutive two-point
clusters and the stated restricted witness pools; it is not an obstruction
to arbitrary 18-point polygons or all possible deformations.

> **Three-copy saturation.** With m consecutive clusters of three vertices,
> under the analogous all-rich, at-most-three-other-clusters hypothesis, every
> chosen four-witness row must split as 2+1+1 between its target clusters, and
> each of the 3m internal pairs must be used exactly once.

There are 3m centers. Every row consumes at least one internal pair, while
there are exactly 3m pair resources. Equality is forced everywhere. A 2+2 row
would consume two pairs; a 3+1 row would consume three. The only cost-one
four-subsets have type 2+1+1. For three target triples, exactly 81 subsets
have this type. This is a necessary restriction, not realizability.

This motivated a 27-point, nonsymmetric, three-copy experiment using the
repository's *numerically specified* Danzer-type nine-point base only as an
initializer. All 27 physical coordinates are variable modulo four similarity
gauges, with finite optimization bounds. No exact claim about the initializer
or a resulting four-rich configuration is inferred from its decimal values.

## 9. Exact obstruction of the initially optimized witness patterns

The initial four numerical runs used three distinct patterns passing the
circle-sharing, cyclic crossing, and cluster-resource filters. They attained
nonzero normalized squared-distance errors, and drove their closest pairs to
the imposed separation limits. They are not near-exact counterexamples.

A stronger exact post-check rejects **all three fixed patterns in their
specified order**. For four vertices a,b,c,d in cyclic order, strict convexity
implies the ordinary-distance inequalities
\[
 d_{ac}+d_{bd}>d_{ab}+d_{cd},\qquad
 d_{ac}+d_{bd}>d_{ad}+d_{bc}.
\]
To prove them, intersect the diagonals at o and apply strict triangle
inequalities to each opposite side pair. Each side sum is strictly smaller
than the total diagonal length. Squared distances are **not** substituted
into these inequalities. Selected equal-distance rows equate ordinary
lengths as well as their squares.

The exact checker forms positive integer sums of these strict inequalities
and verifies that all chord coefficients cancel using only named selected
rows. Eight one-inequality certificates reject the seed-271 pattern (also
used by run 811); five reject the seed-912 pattern. The seed-405 pattern has
a certificate with just two inequalities and four required equality rows:

```
required selected centers: 2,5,6,7
cyclic quadruple (6,7,1,2), other-side-pairs inequality, weight 1
cyclic quadruple (6,8,2,5), other-side-pairs inequality, weight 1
```

Here the first inequality reads `d(6,1)+d(7,2)>d(6,2)+d(7,1)`;
the second reads `d(6,2)+d(8,5)>d(6,5)+d(8,2)`.
The selected rows force `d(6,1)=d(6,5)`, `d(7,2)=d(7,1)`, and
`d(8,5)=d(8,2)`, so their sum would assert a quantity is strictly greater
than itself. The full stored rows allow both primary and separate graph-based
checkers to reconstruct these identifications.

This audit corrects the status of those patterns: they are **obstructed
fixed-pattern benchmarks**, not live Euclidean candidates. Numerical stalls
on them do not constitute evidence against untested configurations.
The subsequent filtered scan calls the exact quadrilateral checker before
any coordinate optimization. Its bounded outcomes, failures, and any
certificates are documented in `exploratory/RESULTS.md`; no family-wide
exhaustion is claimed.

## 10. Verification boundary and remaining mathematical gap

The principal theorem's two implementations use different representations
of algebraic numbers, distance minima, quadratic coefficients, and graph
deletion. Both were produced in this research session. Neither constitutes
external independent mathematical review. There is no Lean proof of this
packet or of Erdős97.

The proof obligations for a reviewer are the fixed-seed circumcenter/slot
reduction, completeness of the nine insertion domains, range formulas on
closed domains, capacity of each slot, preservation under graph deletion,
common-radius endpoint cover, and interpretation of compulsory witness
conflicts. Source and certificate replay make these obligations inspectable;
passing tests alone is not their mathematical proof.

The new theorem excludes exactly one internally supported cap vertex over
this particular P. It neither excludes two such vertices nor forces an
arbitrary all-rich polygon to contain P. The cluster argument restricts
specific consecutive-copy witness pools only. A complete solution still
requires an exact all-rich strictly convex construction or an unrestricted
geometric argument, not extrapolation from these results.
