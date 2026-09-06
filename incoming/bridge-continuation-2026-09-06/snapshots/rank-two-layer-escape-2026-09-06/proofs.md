# Two-closer radius layers: a planar edge budget and forced upward witnesses

Date: 6 September 2026.

**Status: restricted paper-proof candidates with exact regression controls;
independent mathematical review pending.** This packet proves neither the
unrestricted statement of Erdős Problem #97 nor the impossibility of every
variable-radius two-closer four-rich system. It does not promote a finite-case
bound, claim published novelty, or modify the repository's accepted status.

The arbitrary-size conclusions below depend on the written proofs. The finite
rational tests are regression evidence, not their quantifier over all real
polygons. The argument is self-contained apart from elementary plane geometry
and elementary facts about polygon triangulations, which are justified where
used.

## 1. Definitions and principal conclusions

A finite planar set is **strictly convex** here when every point is a strict
vertex of its convex hull; in particular, no three points are collinear. Sets
of one or two points use the usual convex-independence convention.

For a vertex v, put

    C_v(r) = {w != v : |vw| = r},
    b_v(r) = #{w != v : |vw| < r},
    M_P(v) = max over r>0 of |C_v(r)|.

Assign a positive radius rho_v to every vertex. A vertex is **rich at its
assigned radius** if |C_v(rho_v)| >= 4. The **two-closer hypothesis** is

    b_v(rho_v) <= 2 for every v.                              (1)

This is an additional restriction, not a consequence of a hypothetical
counterexample to Erdős #97.

The main results are:

1. The graph of edges |uv| < min(rho_u,rho_v) is noncrossing and has maximum
   degree two. Cycles are allowed; it is not asserted to be a forest.
2. At a fixed radius r, if b_v(r)<=2 at all n vertices, the number e_r of
   distance-r edges satisfies, for n>=2,

       e_r <= 2n - 3 - p - 2c,                               (2)

   where p is the number of nontrivial path components and c the number of
   cycle components in the graph of edges shorter than r. Isolated vertices
   do not contribute to p. All cycle lengths, including three, contribute to c.
3. Under (1), let r=min rho_v and Y={v:rho_v=r}. Suppose every vertex of Y is
   rich. There are at least four DISTINCT vertices q outside Y receiving a
   distance-r witness incidence from Y, and each such q satisfies

       r < rho_q < 2r.                                      (3)

   If m=|Y|>=2, the number U of exported incidences satisfies

       U >= 6 + 2p_Y + 4c_Y,                                (4)

   with p_Y,c_Y computed using the shorter-than-r graph on Y. For m=1, U>=4.

Thus a common-radius two-closer all-rich system is impossible. A fully rich
minimum-radius layer with at most three vertices above it is also impossible.
The four-target bound and the six-incidence bound are separately attained by
exact partial configurations. They are not asserted jointly sharp for every
layer size or every component pattern.

A new nine-point exact control shows why this forcing result cannot simply
be iterated by deleting the minimum layer: the entire minimum layer is rich,
yet its deletion makes a higher-radius rich vertex good at every radius. The
control does not make every original vertex rich, so it does not refute a
bridge that genuinely uses universal four-richness.

## 2. A crossing-diagonal endpoint lemma

**Lemma 2.1.** In a strictly convex quadrilateral a,b,c,d in that cyclic order,
some vertex has both incident sides strictly shorter than its incident
(diagonally opposite) diagonal.

### Proof

Write A=|ac| and B=|bd|, and interchange the diagonal names if necessary so
A<=B. Splitting the crossing diagonals at their intersection and applying
strict triangle inequalities gives

    |ab|+|cd| < A+B,
    |ad|+|bc| < A+B.                                       (5)

Suppose the conclusion fails. At b choose an incident side of length at least
B, and do the same at d. If the chosen sides are opposite, their sum is at
least 2B>=A+B, contrary to (5). Otherwise they meet at a or c. By symmetry,
suppose they are ab and ad, both of length at least B.

At c, failure of the conclusion supplies bc or cd of length at least A.
Pair bc with ad, or cd with ab, respectively. Either pair contradicts (5).
This proves the lemma. QED.

**Corollary 2.2 (variable-radius mutual-short graph).** Under (1), the graph

    uv is an edge iff |uv| < min(rho_u,rho_v)

is noncrossing and has maximum degree two.

### Proof

The degree assertion follows directly from (1). If two such edges crossed,
Lemma 2.1 would give one of their endpoints v with two adjacent quadrilateral
vertices closer than its diagonal endpoint. All three other quadrilateral
vertices would then be strictly closer than rho_v, contrary to (1). QED.

The strict inequalities matter. A square with each radius equal to its
diagonal has two strictly closer points at each vertex, but its distance-r
edges cross. Its strictly shorter edges form a four-cycle. These are exact
controls in the packet.

## 3. Fixed-radius edge bound

We now prove (2). Fix r>0 and assume b_v(r)<=2 for all vertices of a strictly
convex set S of size n. Let H be the graph of edges shorter than r. It has
maximum degree two and is noncrossing by Corollary 2.2 with constant radii.
Its components are isolated vertices, nontrivial paths, or cycles.

The cases n=1 and n=2 are immediate. For n=1, e_r=0. For n=2 the claimed
bound is checked according as the unique distance is below, equal to, or above r.
For the remainder assume n>=3.

### 3.1 Empty closed diameter disks

Call uv a **strict Gabriel edge** if the closed disk with diameter uv contains
no other vertex of S. This definition deliberately excludes points on the
boundary of that disk.

A third point z belongs to that disk exactly when

    (z-u) dot (z-v) <= 0,

or, equivalently,

    |uz|^2 + |zv|^2 <= |uv|^2.                              (6)

We call such a z a blocker of uv.

Strict Gabriel edges are noncrossing. Indeed, if ac and bd crossed, at least
one angle of the convex quadrilateral abcd would be at least pi/2, since its
four angles sum to 2pi. Its vertex would lie in the closed diameter disk of
the opposite diagonal by (6), contradicting that diagonal's strict Gabriel
property.

Let G consist of the strict Gabriel edges whose lengths are at most r.
It is therefore a noncrossing graph on the convex vertices of S.

### 3.2 Blocked short edges occur only in isolated triangles

Let s=|E(H)|. If a short edge uv is blocked by z, equation (6), positivity of
the two distances, and |uv|<r give

    |uz|<r and |zv|<r.

Thus u,v,z form a triangle in H. Each of its vertices already has two H
neighbors, so this triangle is an entire component of H.

A triangle has at most one angle at least pi/2. Consequently, each triangular
component of H has at most one blocked short edge. A different vertex outside
that component cannot block one of its edges: it would create a third short
neighbor at an endpoint.

Write t for the number of triangular components and t' for the number of
blocked short edges. We have

    0 <= t' <= t,
    number of short edges in G = s-t'.                      (7)

In particular, all sides of every H cycle of length at least four belong to G.

### 3.3 Blocked distance-r edges have distinct degree-two blockers

If a distance-r edge uv is blocked by z, (6) gives |uz|<r and |zv|<r.
Thus z has degree exactly two in H, with neighbors precisely u and v. It is
not in a triangular component because uv is not short.

Choose one blocker for each blocked distance-r edge. This assignment is
injective: a degree-two vertex has only one unordered pair of H neighbors,
so cannot be assigned to two different blocked edges.

Let d_2 be the number of H-degree-two vertices. The available blocker vertices
are exactly the d_2-3t degree-two vertices outside short triangles. Let N be
the number of blocked distance-r edges and define the number of unused
available blocker vertices by

    delta = d_2-3t-N >= 0.                                 (8)

The choice need not be unique. Any injective choice gives the argument below.

### 3.4 A triangulation supplies a second charge for every longer short cycle

Extend G to a triangulation T of the convex n-gon. One may first add missing
polygon sides and then add noncrossing diagonals until every bounded face
is triangular. A convex n-gon triangulation has n-2 triangles and 2n-3 edges:
this follows by induction after splitting at any diagonal, with the triangle
as the base case.

Put

    M = |E(T) minus E(G)| = 2n-3-|E(G)|.                    (9)

Consider a cycle C of H with k>=4 vertices. Its edges are in G, hence T. A
noncrossing cycle on points in strictly convex position follows their inherited
cyclic order: a chord separating the other cycle vertices into two nonempty
sides would force a crossing in the remainder of the cycle. No other vertex
of S lies inside its polygon, because such a vertex would not be extreme in S.
Therefore T restricts to a triangulation of the convex k-gon bounded by C.

This triangulation has at least two ears, where an ear at v is a triangle
formed by v and its two neighbors on C. For completeness, its triangle-adjacency
dual graph is a tree: removing a diagonal splits the polygon, proving
connectedness and the k-3 edge count on k-2 triangle nodes. For k>=4 this tree
has at least two nodes and at least two leaves; each leaf gives an ear.

Choose two ears. For each chosen ear at v, let ab be its base, with a,b the
two H neighbors of v.

* If v is an unused available blocker, charge that unused vertex, one unit
  from delta.
* Otherwise v was assigned as blocker of a distance-r edge. Its two H
  neighbors determine the assigned edge uniquely as ab. The ear puts ab in
  T, but its blocker makes it absent from G. Charge that added edge, one unit
  from M.

The two charges are distinct. Two ear bases in one cycle can coincide only
for opposite ears of a quadrilateral. In that case the injective blocker
assignment can assign their common base to at most one of the two ear
vertices; the other ear pays through its unused vertex instead. Different
cycle components have disjoint vertex sets and cannot reuse a vertex or an
edge with those endpoints.

If c is the number of ALL cycle components of H, the nontriangular cycles
number c-t. We have proved

    M + delta >= 2(c-t).                                   (10)

This is the step that strengthens the bound for cycles rather than pretending
that the short graph is a forest. The accompanying independent finite
combinatorial audit checks the charge rule on all triangulations through
nine cycle vertices, but that audit is not needed for the all-size proof.

### 3.5 Counting

Using (7)-(9), the number e_r of distance-r edges is

    e_r = |E(G)| - (s-t') + N
        = 2n-3 - (s-d_2) + t' - 3t - (M+delta).

For a maximum-degree-two graph, s-d_2 is exactly the number p of nontrivial
path components: each path contributes one, and each cycle or isolated vertex
contributes zero. Since t'<=t, equation (10) gives

    e_r <= 2n-3-p+t-3t-2(c-t)
         = 2n-3-p-2c.

This proves (2). QED.

### 3.6 Consequences and sharpness qualifications

First, e_r<=2n-3, and if H is nonempty then e_r<=2n-4. Thus not every vertex
can have four distance-r neighbors. The same estimate holds after restricting
to ANY subset of S: the two-closer assumption and strict convexity are
hereditary. Accordingly, the distance-r graph is 3-degenerate. Equivalently,
it admits a deletion ordering in which each deleted vertex has at most three
remaining distance-r neighbors.

An equilateral triangle and the convex rhombus formed by two equilateral
triangles attain e_r=2n-3. No claim is made that this leading expression is
sharp for every n, or that the separate path and cycle penalties are optimal
for every component pattern.

The entire distance-at-most-r graph is not asserted planar. A square at its
diagonal radius has crossing distance-r edges and passes every hypothesis.
Only H and the auxiliary strict Gabriel graph G are planar.

## 4. Minimum-layer extraction with varying radii

Assume (1), put

    r = min_v rho_v,
    Y = {v : rho_v=r},     m=|Y|,

and suppose every member of Y has at least four distance-r witnesses in the
FULL set P. An **exported incidence** is an ordered pair (y,q) with y in Y,
q outside Y, and |yq|=r. Let U count those incidences and Q be the set of their
distinct target vertices.

### 4.1 An external target can receive at most two exports

For q outside Y, rho_q>r. Every point at distance at most r from q is
strictly closer than rho_q, so (1) implies

    #{v != q : |qv| <= r} <= 2.                            (11)

In particular a target receives at most two exported incidences. If it
receives two, it has no neighbor at distance strictly less than r at all.
This counts points in the entire P, not merely the minimum layer.

### 4.2 The incidence lower bound

For m>=2 apply (2) to Y at radius r. Let e_r(Y) count its internal distance-r
edges, and p_Y,c_Y its short-component counts. Counting the distance-r
incidences at Y gives

    4m <= sum_(y in Y) |C_y(r)| = 2e_r(Y)+U.

Therefore

    U >= 4m-2(2m-3-p_Y-2c_Y)
      = 6+2p_Y+4c_Y.                                     (12)

For m=1, the unique minimum vertex has four distinct witnesses, all external,
so U>=4 directly.

### 4.3 Why at least FOUR distinct external vertices are necessary

For m=1 this is immediate. For m>=2, suppose |Q|<=3. Equation (11) gives
U<=6. Comparing with (12) forces

    U=6, |Q|=3, p_Y=c_Y=0.

In particular H_Y is empty: there are no distances shorter than r inside Y.
Every target q in Q receives two incidences and, by (11), has no distance
shorter than r to any other point of P.

Now take any y in Y and select four of its distance-r witnesses. All are in
Y union Q. No two of these witnesses can be separated by a distance shorter
than r, by the preceding paragraph.

But at a strict hull vertex the rays to all other vertices lie in an angular
interval of width strictly less than pi. Four rays produce three successive
gaps, one of which is strictly less than pi/3. The corresponding witnesses
a,b satisfy

    |ab| = 2r sin(angle ayb / 2) < r,

a contradiction. Therefore |Q|>=4. QED.

The reasoning does not assume witnesses are consecutive vertices on the
polygon boundary. It uses only their angular order within the hull cone.

### 4.4 The strict factor-two radius band

Let y be rich at radius r and let q be one of its witnesses, with rho_q>r.
Choose three other witnesses w_1,w_2,w_3. Strict convexity gives no collinear
triple, so strict triangle inequalities give

    |qw_j| < |qy|+|yw_j| = 2r,       j=1,2,3.

Also |qy|=r<2r. If rho_q>=2r, q would have at least four strictly closer
vertices: y,w_1,w_2,w_3. This contradicts (1), and proves (3).

This argument actually needs only b_q(rho_q)<=3. It applies to any upward
selected witness edge from a four-rich source, whether or not the source is
in the minimum layer. The band does NOT apply to every higher-radius center;
a higher center may instead send an essential witness edge DOWN to the minimum
layer. Section 7 gives an exact example with such a higher center at 2r.

### 4.5 Explicit restricted closures

The conclusions immediately exclude the following systems under (1):

* a common assigned radius with every vertex rich;
* an all-rich minimum layer with at most three vertices outside that layer;
* an all-rich system with at most three vertices receiving an incidence
  |yq|=rho_y<rho_q from any other vertex;
* an all-rich system whose strictly-closer relation is symmetric, meaning
  |uv|<rho_u if and only if |uv|<rho_v for every pair u,v.

The last claim follows because an exported incidence has |yq|=rho_y<rho_q,
so would violate that symmetry. Symmetric closeness is an EXTRA assumption;
it is not supplied by convexity, rank two, or counterexample minimality.
It does not force equal radii: the exact four-point two-cluster control in
the tests has distinct actual assigned radii and an empty symmetric
strictly-closer relation.

## 5. A disk-containment rank jump

There is one useful radius statement that needs no rank cap in its hypothesis.
Let p and q be distinct vertices, let q have k witnesses at radius s>0, and
suppose R>=|pq|+s. The disk of radius R centered at p contains the disk of
radius s centered at q. Then

    b_p(R) >= k+1 - indicator(|pq|=s).                     (13)

Indeed, q is strictly inside the larger disk. Every radius-s witness w other
than p is also strictly inside: equality in

    |pw| <= |pq|+|qw| <= R

would force p,q,w collinear, which strict convexity excludes. There are k
such witnesses unless p itself is one, in which case there are k-1.
Together with q this proves (13).

Consequently, in an all-rich system with at most THREE strictly closer points
at every assigned radius, no assigned disk can contain another. Hence

    |rho_p-rho_q| < |pq| for every distinct p,q.             (14)

For four-rich q, the bound in (13) is at least four, and is at least five
when p is not on the selected circle around q. The lower bound four is sharp:
in the five-point control below, the radius-2 disk at the first unit witness
contains the radius-1 disk at the origin and has exactly four other vertices
strictly inside it.

Equation (14) is necessary, not sufficient. It does not exclude all-rich
rank-three systems, all-rich rank-two systems, or arbitrary counterexamples.

## 6. Exact controls for the numerical constants

All coordinates below are exact. `exact_controls.json` contains the full
supporting-line checks' minimum margins, exact distance classes, graph
certificates, and radius assignments. All radii in these three assigned-radius
controls are actual third-nearest distances, counting ties with multiplicity.

### 6.1 Four distinct upward targets can occur

Use

    p0=(0,0),
    p1=(24/25,7/25),   p2=(3/5,4/5),
    p3=(-3/5,4/5),     p4=(-24/25,7/25),

with squared radii

    [1,338/125,36/25,36/25,338/125].

The strictly-closer counts are [0,2,2,2,2]. The minimum layer is {p0}, which is
four-rich. It has exactly four distinct upward targets. This is the same
five-point rank-two guardrail delivered in the previous rank-one packet;
its role as a sharp four-target control is new to the present argument.
The other four vertices are not rich.

### 6.2 Six exported incidences can occur with two minimum centers

Use the eight points

    p0=(0,0),                  p1=(1,0),
    p2=(7/25,24/25),           p3=(-4/5,3/5),
    p4=(-399/401,40/401),      p5=(18/25,24/25),
    p6=(9/5,3/5),             p7=(800/401,40/401).

Their strictly convex cyclic order is

    [4,0,1,7,6,5,2,3].

Assign squared radii

    [1,1,162/125,162/125,23716/10025,
         162/125,162/125,23716/10025].

The two minimum centers have rows

    p0 -> {p1,p2,p3,p4},
    p1 -> {p0,p5,p6,p7}

at radius one. They have no strictly closer points; the other six each have
exactly two. There is one internal unit edge and exactly six exported
incidences, attaining (12) with m=2 and p_Y=c_Y=0.

The other six centers are not rich. This is a sharp partial control, not an
all-rich realization.

## 7. Exact return to a fully rich minimum layer

The following construction is the new obstruction to a naive iteration of
Section 4. Define the rational unit-circle parametrization

    u(t)=((1-t^2)/(1+t^2), 2t/(1+t^2)).

Set

    p0 = (0,0),
    p1 = u(1/4),       p2 = u(1/3),
    p3 = u(10/7),      p4 = u(39),
    p5 = 2u(29),
    p6 = p5+2u(16/5),
    p7 = p5+2u(22/3),
    p8 = p5+2u(19/3).

This directly proves the selected identities

    |p0 pj|=1 for j in {1,2,3,4},
    |p5 pj|=2 for j in {0,6,7,8}.

There is no approximate-equality inference. The remaining exact checks use
rational squared distances and determinants.

### Complete coordinates and assignments

| Label | x | y | Assigned squared radius |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 1 |
| 1 | 15/17 | 8/17 | 4356/2533 |
| 2 | 4/5 | 3/5 | 1058/745 |
| 3 | -51/149 | 140/149 | 1058/745 |
| 4 | -760/761 | 39/761 | 138338/113389 |
| 5 | -840/421 | 58/421 | 4 |
| 6 | -430542/118301 | 151018/118301 | 4 |
| 7 | -814070/207553 | 139738/207553 | 4 |
| 8 | -303592/77885 | 58724/77885 | 4 |

The strictly convex cyclic order is

    [7,5,4,0,1,2,3,6,8].

All 63 supporting-edge/other-point determinants are strictly positive; the
smallest is exactly

    209808/25628605.

The strictly closer sets and assigned witnesses are:

| Center | Strictly closer labels | Assigned-radius witness labels |
|---:|---|---|
| 0 | none | 1,2,3,4 |
| 1 | 0,2 | 3 |
| 2 | 0,1 | 3 |
| 3 | 0,4 | 2 |
| 4 | 0,5 | 3 |
| 5 | 3,4 | 0,6,7,8 |
| 6 | 7,8 | 5 |
| 7 | 6,8 | 5 |
| 8 | 6,7 | 5 |

Thus every assigned radius has at most two strictly closer points, and every
assigned radius is its center's actual third-nearest distance. The unique
minimum-radius vertex is p0, and it is rich. Its four higher-radius targets
p1,...,p4 all obey (3).

However, p5 is genuinely four-rich at its higher radius 2 and uses p0 as one
of its four witnesses. The exact ALL-RADIUS maximum multiplicities are

    [4,1,1,1,1,4,1,1,1].

Delete the entire minimum layer {p0}. For surviving original labels 1,...,8,
the all-radius maxima become

    [1,1,1,1,3,1,1,1].

So p5 becomes good at every radius, not just at its originally assigned one.
The disappearance of the tie is an exact equality-class computation, not a
failure of a chosen numerical tolerance.

### What this does and does not refute

This refutes the statement:

> Under the two-closer hypothesis, deleting an entirely rich minimum-radius
> layer preserves richness of all previously rich higher-radius centers.

It also shows why (3) cannot be misread as constraining every higher-radius
rich center: p5 is at 2r but is not a witness of the minimum center. It sends
a selected edge in the opposite direction.

Seven of the nine original vertices are not rich. The construction does NOT
refute a statement that additionally assumes every vertex of the original
polygon is rich, and is NOT a counterexample to Erdős #97. The extra global
hypothesis is exactly what a remaining bridge must exploit.

## 8. Verification and limits

Run with Python 3.10 or later, without third-party packages:

    python verify.py --check
    python oracle.py
    python -m unittest -v test_bridge.py

`verify.py --write` regenerates the deterministic JSON objects. Assignments
are deduplicated within each geometric fixture instance. The finite fixture
families are selected circle/ellipse/parabola subsets, deterministic integer
hulls, rational one- and two-star controls, and the named controls. They are
not an enumeration of arbitrary real polygons or arbitrary witness systems.

The completed main run contains:

* 639 geometric fixture instances and 16,963 supporting-line checks;
* 20,379 convex-quadrilateral tests of Lemma 2.1;
* 5,873 fixed-radius graph/certificate checks, including 475 blocked
  distance-r edges and 136 ear-resource charges;
* 6,429 assigned-radius checks, including 129 fully rich minimum-layer
  instances and 33 instances with more than one minimum center;
* 51 passing unit tests, including rejected float inputs, degenerate inputs,
  rank-three misuse, square crossings, actual third-nearest radii, and the
  return control's full distance profiles.

The separate finite combinatorial audit enumerates all 624 triangulations of
convex k-gons for 4<=k<=9 and all 259,890 injective blocked-base assignments in
that relaxation. It checks the two-ear resource inequality without assuming
any such abstract assignment is geometrically realizable.

`oracle.py` is a second representation of the stored named controls. It does
not import the main geometry, fixture, or verifier modules. It checks signed
crossings by orientation products, disk blockers by dot products, distance
classes, graph component counts, and deletion profiles. Its scope is twelve
geometric controls, fourteen fixed-radius certificates, and three assigned-
radius controls, not the entire regression census or a separate all-size
formal proof. Both implementations were written in this session; this is not
independent external mathematical review.

The geometric hull-cone, crossing, triangulation, and injection arguments need
independent review. No repository-wide CI was run. No GitHub branch, PR, or
accepted-status metadata was changed by this packet.

## 9. The remaining bridge, stated without replacing its quantifiers

An unrestricted counterexample has not been shown to admit assigned rich
radii with at most two strictly closer vertices. Even conditional on that
additional rank-two restriction, universal four-richness has not yet been
shown impossible here.

What is now forced is a rich minimum layer with at least four upward targets
in a strict factor-two radius band and, for multiple minimum centers, a
quantified export deficit. A successful induction must handle downward
selected edges returning to earlier layers; deleting a layer and assuming
higher richness survives is invalid under the weaker hypotheses, as the
nine-point exact control demonstrates.

Thus the new claims are (2), (3), (4), the mutual-short graph lemma, the stated
restricted closures, and the disk-containment rank jump. The missing claim
is an all-size contradiction that uses richness at EVERY vertex to reconcile
these upward exports with downward returns. It is not established by this
packet.
