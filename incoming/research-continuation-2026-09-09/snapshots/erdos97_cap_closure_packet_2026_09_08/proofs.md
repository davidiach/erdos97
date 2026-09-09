# Rigidity of two-old-supported rich caps

**Research date: 8 September 2026.**  
**Status: restricted paper-proof / exact-certificate candidate; review pending.**  
No unrestricted proof or counterexample to Erdős #97, external mathematical
review, Lean formalization, or literature novelty is claimed.

## 1. What is classified

For a finite strictly convex point set X and a vertex x, write

\[
N_X(x,r)=\#\{y\in X\setminus\{x\}:|x-y|=r\}.
\]

A vertex is **rich** if some positive radius has N_X(x,r) at least four; it
is **good** otherwise. The unrestricted target requires a good vertex in
every finite strictly convex polygon. A putative counterexample must be
rich at every vertex, including every newly added vertex.

Fix the exact nine-point seed P below. A **two-old-supported rich cap** is a
nonempty finite set Q, disjoint from P, such that:

1. P union Q is in strictly convex position;
2. for each q in Q there exists a positive radius r_q with
   N_(P union Q)(q,r_q) >= 4 and at least two of its witnesses in P.

No bound on |Q| is imposed. The radii, old witness pairs, new witness
assignments, locations, and symmetry of Q are not prescribed. In particular,
the cap is not assumed to lie on the earlier carrier or to have C3 symmetry.
No richness assumption is made about the old vertices for the classification.

**Theorem A (fixed-seed, arbitrary finite cap size).** There is exactly one
two-old-supported rich cap over P. It consists of the three points in the
next triangle of the existing alternating recurrence. Its addition leaves
all six old good vertices good.

This is a uniqueness/rigidity result, not a new partial construction. The
three-point cap was already present as the next step of the unbounded family.
The new conclusion is that the much larger class just defined contains
nothing else.

**Corollary A1.** No all-rich strictly convex extension P union Q can have a
rich radius with two old witnesses at every new vertex.

**Corollary A2 (necessary escape).** In any all-rich finite strictly convex
extension of this fixed P, there is a new vertex q such that **every** radius
making q rich has at most one witness in P, and therefore at least three
witnesses in Q minus {q}.

This does not say that Q is internally three-rich at every vertex. It does
not rule out the escape just described, caps with no old support at some
vertices, or co-design that moves any old point.

## 2. The exact seed and the unique cap

Use complex coordinates, with

\[
\omega=\frac{-1+i\sqrt3}{2},\qquad
z(t)=-\frac12+\frac{3t}{1+3t^2}
      +i\sqrt3\frac{1-3t^2}{2(1+3t^2)}.
\]

Set

\[
t_0=\frac1{10},\qquad t_1=\frac{83-3\sqrt{721}}{200},
\qquad a=z(t_0),\quad b=\overline{z(t_1)}.
\]

In the labels used by the certificates,

\[
P=(1,\omega,\omega^2,a,\omega a,\omega^2a,b,\omega b,\omega^2b).
\]

Its counterclockwise boundary order is

```
4, 2, 6, 5, 0, 7, 3, 1, 8.
```

The old maximum multiplicities are (2,2,2,3,3,3,4,4,4).

Let t_2 be the smaller root of

\[
s^2-(1-2t_1+3t_1^2)s+t_1^2=0,
\qquad 0<t_2<t_1.
\]

Equivalently,

\[
t_2=\frac{1-2t_1+3t_1^2-
\sqrt{(1-t_1)(1-3t_1)(1+3t_1^2)}}2.
\]

Then Theorem A identifies the unique cap as

\[
\boxed{Q=\{z(t_2),\omega z(t_2),\omega^2z(t_2)\}.}
\]

The exact twelve-point census is

\[
(2,2,2,3,3,3,4,4,4,4,4,4).
\]

Thus this cap makes all three new vertices rich but does not repair the old
exceptions. This census is checked directly, rather than inferred from
acceptance of the earlier arbitrary-length written proof.

## 3. Replayed prerequisite: at most two old witnesses

The supplied preceding packet proves for this P that a genuinely new point
x with P union {x} strictly convex cannot be equidistant from three old
vertices. Both new checkers replay its complete certificate.

There are exactly 84 old triples. Each is noncollinear, so it has a unique
circumcenter. The complete list has 64 distinct centers: six are already
old vertices; the other 58 make some point of P union {center} lie in the
closed triangle of three other points. Of those, 55 have strictly positive
containment signs and three have a boundary containment sign. Closed
containment is sufficient to disqualify an extreme point.

Any point equidistant from three old vertices must be one of these centers,
so the list is exhaustive. This is the old certificate, not a new result.
The original packet ZIP is retained unchanged in `inputs/previous_packet.zip`.
Its certificate bytes and their SHA256 are recorded in the new report.

It follows that a cap satisfying Section 1 has **exactly two** old witnesses
at its chosen rich radius. It has at least two distinct new witnesses at
that radius, even when its full distance class has more than four points.

Strict convex independence is hereditary, so the prerequisite applies to
each q separately when the entire extension is strictly convex.

## 4. A general finite reduction using perpendicular bisectors

The next two geometric observations are not specific to the seed.

### 4.1 A new point has exactly one insertion cell

Let p_0,...,p_(n-1) be a counterclockwise strictly convex polygon. If adjoining
a new point x preserves every point as an extreme point, x is inserted
between two consecutive old vertices in the new boundary order. Consequently,
relative to the oriented old supporting edges, x is strictly outside that
one old edge and strictly inside every other old edge.

Conversely, those strict signs give a strictly convex insertion. One may
see this either by the supporting edges of the enlarged hull or by replacing
the uniquely visible edge with its two segments to x.

No zero supporting sign is allowed: a new point on the line through an old
edge would put three distinct collinear points in the enlarged set, and
one of them would not be extreme. An x with all signs positive is inside
the old polygon, so is not new and extreme.

These open regions will be called **insertion cells**. Thus they exhaust
all possible positions of any new vertex of any finite convex extension.
The statement is about each new point individually; positions in the same
cell still have to be mutually compatible in the actual extension.

### 4.2 One point per ray of an old-pair bisector

Suppose x has old witnesses a,b at equal distance. It is on their perpendicular
bisector. Put m=(a+b)/2 and write x=m+t v for a fixed nonzero perpendicular
vector v. Since m is in the old convex hull, t is nonzero.

Two admissible new vertices cannot have parameters 0<t_1<t_2 on this same
ray. Indeed,

\[
m+t_1v=\frac{t_1}{t_2}(m+t_2v)
+\frac{1-t_1/t_2}{2}a+\frac{1-t_1/t_2}{2}b.
\]

All three coefficients are positive, so the nearer point is strictly inside
the triangle formed by the farther point and a,b. The same argument applies
to the negative ray.

In particular, for any fixed n-point old polygon, a convex extension in
which each new point is assigned two equidistant old witnesses has at most
2*binomial(n,2)=n(n-1) new points. This cardinal bound does not require the
new points to be rich.

### 4.3 At most one admissible interval on each ray

At the midpoint m, each old supporting-edge affine function is nonnegative.
Along a fixed ray, a supporting sign can become negative only once. Sort
the nonnegative times at which signs change from nonnegative to negative.
Exactly one negative sign occurs between the first and second exit times.
If the two earliest times coincide, that ray has no insertion interval.
There is no later interval with exactly one negative sign because an already
negative affine sign cannot become positive again further along this ray.

Thus an old-pair bisector meets the admissible region in at most two open
intervals, one on each ray. These intervals are the **slots** used below.
The slot capacity is one, regardless of how many new vertices are sought.

In general the interval may be unbounded. The two inputs in this packet have
only bounded nonempty slots. The executable deliberately raises an error on
an unbounded input rather than pretending it has exhausted that case.
The geometric cardinal bound above remains valid without boundedness.

## 5. Computing the 42 slots for the nine-point seed

To avoid Cartesian square roots in the arithmetic, store a point as (x,y)
meaning the actual Cartesian point (x,sqrt(3)*y). The norm and inner product are

\[
N(x,y)=x^2+3y^2,\qquad
\langle (x,y),(u,v)\rangle=xu+3yv.
\]

All old coordinates belong to K=Q(sqrt(721)). Ordinary orientation signs
are unchanged by the positive y-scaling.

For an old pair a,b, set

\[
m=\frac{p_a+p_b}{2},\qquad
u=p_b-p_a,\qquad v=(-3u_y,u_x).
\]

Then x(s)=m+s v parametrizes the entire perpendicular bisector in the scaled
metric. Each insertion-cell inequality is affine in s. The primary checker
intersects these half-line conditions for every pair and every cell.

The independent checker instead starts at m and sorts first and second
supporting-line exit times along each of the two rays. The complete
interval lists agree exactly, including empty ray cases and all endpoints.
There are 42 nonempty slots from the 36 old pairs. Some pairs have one
admissible ray and some two. Every endpoint is specified exactly in K in
`data/verification.json`.

Every candidate cap vertex is assigned to a slot by its selected two old
witnesses. By Section 4, no two cap vertices can occupy the same assigned
slot. A point might admit some different pair at a different radius; the
argument only needs one selected rich radius and its pair. The old ceiling
prevents three old points from sharing that selected radius.

## 6. An exact directed graph containing every possible cap dependency

Consider source slot i, with x(s)=m_i+s v_i, and target slot j, with
 y(t)=m_j+t v_j. Let p_a be one of the source's two old witnesses. A new
point y(t) can be a witness for x(s) at its selected old-supported radius
only if

\[
F_{ij}(s,t)=N(x(s)-y(t))-N(x(s)-p_a)=0.
\]

After cancellation, this polynomial is affine in s and quadratic in t,
with strictly positive t-squared coefficient N(v_j). Hence its exact
minimum and maximum on the **closed** parameter rectangle are found by:

* taking the two source endpoints;
* for each endpoint, evaluating the target quadratic at its two endpoints
  and at its stationary point when that lies in the interval.

For any fixed target parameter, an affine source function attains its
extrema at source endpoints. Minimizing and maximizing over the target
interval therefore yields precisely the listed finite evaluations. The
stationary point is also an element of K. No numerical tolerance is used.

Draw a directed edge i -> j when the resulting range includes zero. Omit
self-loops: one slot can hold only one point, and a vertex cannot witness
itself.

This is a **necessary-edge overapproximation**. It does not claim that all
edges in the graph can be realized simultaneously, or even that every
closed-endpoint zero has an admissible open-slot realization. Keeping such
extra edges makes the exclusion conservative.

Among all 42*41=1,722 ordered distinct-slot pairs, the exact computation gives

| Interval sign | Number |
|---|---:|
| Strictly negative throughout | 483 |
| Strictly positive throughout | 1,116 |
| Range includes zero | 123 |

The two implementations use different coefficient constructions: the primary
uses the geometric coefficient formula, while the oracle interpolates the
target quadratic from its values at 0,1,-1. They agree on every endpoint and
stationary-point extremum, summarized by a canonical SHA256 over all 1,722
exact min/max records, and on the entire 123-edge list.

## 7. Peeling gives a three-slot core, without a cap-size cutoff

Every cap vertex has at least two distinct new witnesses. Slot capacity is
one. Therefore its occupied slot has at least two outgoing graph neighbors
among the occupied slots.

Iteratively remove every slot that has fewer than two outgoing neighbors
among the remaining slots. An actual occupied slot can never be removed:
its two occupied witness slots would still be present at the first putative
removal. This induction does not assume a size bound on the cap.

The batch deletion sizes are 21, 15, and 3. The only remaining slots are

| Slot | Old witness pair | Insertion edge (old labels) |
|---:|---|---|
| 6 | (0,6) | (3,1) |
| 14 | (1,7) | (4,2) |
| 22 | (2,8) | (5,0) |

The induced graph contains all six directed edges between these three
slots. The independent checker also deletes low-outdegree vertices one at
a time in reverse label order and obtains the same core.

A nonempty occupied set has at least three slots because each source needs
two distinct others. It is contained in this three-slot core, so it occupies
**exactly these three slots**, one point per slot.

This is why the computation is not merely a search through caps of size
three or a finite list of witness assignments. The geometric slot cover,
capacity lemma, and deletion induction reduce every finite cap under the
stated two-old-support hypothesis to those three points.

## 8. Symmetry and common center are forced, not assumed

Call the three cap points q_0,q_1,q_2 in the order of slots 6,14,22. At each
q_i, both other cap points are witnesses at the same selected radius. Thus
all three pairwise distances agree: the cap is a nondegenerate equilateral
triangle, and all selected radii are its side length d.

The old anchor witnessed at q_i is omega^i, so

\[
|q_i-\omega^i|=d\qquad (i=0,1,2).
\]

The three slot intervals force positive orientation of (q_0,q_1,q_2), and
also force the scaled y-coordinate inequality q_(0,y)>q_(1,y). The checker
verifies the orientation determinant and y-difference at all eight corners
of the three-interval box. Each expression is affine in each individual
parameter, so its positive corner signs imply positivity throughout the box.

An oriented equilateral triangle has a representation

\[
q_i=c+\omega^i z
\]

for complex c,z with z nonzero. Expanding the equal anchor distances gives

\[
|q_i-\omega^i|^2
=|c|^2+|z-1|^2+2\operatorname{Re}
   (\overline c\,\omega^i(z-1)).
\]

The three real parts are equal. Their sum is zero because
1+omega+omega^2=0; hence all three are zero. Two of these real equations
already imply

\[
\overline c(z-1)=0.
\]

Therefore either c=0 or z=1. The second alternative would give
q_0-q_1=1-omega, whose scaled y-coordinate is -1/2. That contradicts the
positive y-difference forced by the slots. Thus c=0 and

\[
q_i=\omega^i z,\qquad d^2=3|z|^2.
\]

This elementary calculation does not assume or invoke the earlier
review-pending matched-equilateral six-point lemma. In the current slots,
the translation alternative is eliminated directly by a coordinate sign.

## 9. The last equation has exactly one admissible root

The old pair at q_0 is (0,6), namely 1 and b. Hence

\[
|z-1|^2=|z-b|^2=3|z|^2.
\]

The first two quantities being equal puts z on the already computed
bisector slot 6. Write z=m+s v in that slot. The first own-side equation is

\[
1-2N(z)-2z_x=0.
\]

It becomes A*s^2+B*s+C=0, where

\[
\begin{aligned}
A&=-\frac{3015}{292}-\frac{7857}{30076}\sqrt{721},\\
B&=-\frac{873}{292}-\frac{6723}{30076}\sqrt{721},\\
C&=-\frac{747}{1168}+\frac{2619}{120304}\sqrt{721}.
\end{aligned}
\]

Its discriminant is

\[
\Delta=\frac{5103}{146}+\frac{23571}{15038}\sqrt{721}>0.
\]

The exact interval for s is

\[
\frac{17-3\sqrt{721}}{124}
<s<
-\frac{5767}{12514}-\frac{12\sqrt{721}}{6257}.
\]

Both algebraic roots (-B +/- sqrt(Delta))/(2A) are checked. The branch with
minus sqrt(Delta) is outside this interval; the branch with plus sqrt(Delta)
is strictly inside. Since A is negative, the latter is the smaller root in
s. Thus there is exactly one possible z, with no decimal root choice.

For the arithmetic, the field norm of Delta is

\[
\operatorname{Norm}_{K/\mathbb Q}(\Delta)
=-\frac{4\,133\,430}{7519}<0.
\]

In particular Delta cannot be a square in K, since the norm of a square is
a rational square. The oracle can therefore safely use the independent
basis 1,sqrt(721),sqrt(Delta),sqrt(721*Delta). It determines exact zeros
algebraically and every nonzero sign by rational square-root enclosures.
The stored run isolates all required nonzero signs at 32-bit enclosure
precision; this is an exact interval separation, not 32-bit floating-point
geometry.

The accepted root is identified exactly with z(t_2) from Section 2. One can
recover its circle parameter as

\[
t=\frac{z_x+1/2}{3(z_y+1/2)}.
\]

Both numerator and denominator are positive. The checker proves by cross
multiplication that 0<t<t_1 and

\[
t^2-(1-2t_1+3t_1^2)t+t_1^2=0.
\]

The smaller-root condition is therefore the one defining t_2. The circle
identity then gives the displayed z(t_2), not another parametrization branch.

## 10. Attainment, convexity, and the six remaining exceptions

Label the new points 9,10,11 in their omega-rotation order. The exact boundary
order of the twelve-point extension is

```
4, 10, 2, 6, 5, 11, 0, 7, 3, 9, 1, 8.
```

All 120 edge-versus-other-point supporting signs are strictly positive.
Every pairwise separation is positive. Both checkers calculate all distance
classes exactly, with maxima

```
2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4, 4.
```

Each new point witnesses its two orbit mates and its assigned old pair.
Thus the unique cap exists and satisfies the hypothesis. The old anchors
and first chain triangle remain good at every radius, proving Corollary A1.

For Corollary A2, negate the hypothesis of Theorem A at the new vertices of
an all-rich extension. At least one new vertex cannot have any rich radius
with two old witnesses, since otherwise the extension would be the unique
non-all-rich twelve-point set. At any of its rich radii, at most one witness
is old, so at least three distinct witnesses are new. This is a necessary
condition, not a contradiction.

## 11. Controls and the boundary of the argument

### A positive control over a different old set

The old six outer points from the earlier exact middle-cycle control admit
a three-point equilateral rich cap. In that control every cap point has two
old witnesses and its two cap mates. The independent slot construction has
24 slots, 132 necessary edges, and a 21-slot two-out core. The true cap's
three slots (2,11,20) survive. Both implementations verify all 63 supporting
signs and the full maxima (4,4,4,2,2,2,2,2,2).

Thus the general graph machinery does not reject every two-old-supported
rich cap. The rigidity conclusion is about the particular nine-point seed,
not an arbitrary old polygon.

### Allowing one cap vertex to use three new witnesses

`exploratory/one_free_relaxation.py` investigates the first escape from the
hypothesis: one new vertex is allowed an unconstrained position in an old
insertion cell and must use at least three other new witnesses. The regular
new vertices retain their two-old-supported slots.

A coarse exact interval graph, deliberately ignoring many simultaneous
realization constraints, retains survivors in all nine possible insertion
cells. Six cells retain 12 regular slots plus the free vertex; the other
three retain 15 regular slots plus the free vertex. These are abstract
necessary-condition survivors, not coordinates or geometric examples.

This check does not settle the one-free-vertex case. In particular, it would
be invalid to infer from Theorem A that a cap needing three new witnesses
at one vertex is impossible. The scope restriction is real and explicitly
preserved.

## 12. Verification versus mathematical acceptance

`verify.py` reconstructs the seed, replays the old 84-triple prerequisite,
recomputes all 42 slots and 1,722 interval pairs, peels the graph, isolates
both final quadratic roots, certifies the unique convex cap, and reproduces
the entire stored exact report.

`oracle.py` imports none of the primary arithmetic, geometry, or graph code.
It uses a different interval construction, different polynomial coefficient
calculation, different deletion order, and a different radical sign method.
It checks the geometric controls and the final root and census as well.

The original `quadratic.py` and `extensions.py` are retained byte-for-byte
under `prior_math/`; they are not advertised as new or independent code.
The old packet ZIP is also retained unchanged. The new oracle is a second
implementation produced in this same research session, not external review.

The written implications from convex geometry to slots, slot occupancy to
graph degree, and equalities to the concentric equilateral form remain
explicit mathematical review obligations. Executable algebra checks and
unit tests are not a formal proof of those general implications. No accepted
repository status has been changed.
