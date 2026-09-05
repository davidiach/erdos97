# Common suppliers force radius interlacing, even at irrational angles

Date: 2026-09-05. Continuation of draft PR #931.

Status: **COMPUTER_ASSISTED_RESTRICTED_THEOREMS / REVIEW_PENDING**.
No proof or counterexample to unrestricted Erdos Problem #97 is claimed. In
particular, the six-orbit result below is NOT an all-radius result for every
18-point polygon, nor for every C3-symmetric 18-point polygon. The geometric
translation and the code need independent review before theorem promotion.
No novelty claim relative to the published literature is made.

## 1. Definitions

Let omega=(-1+i sqrt(3))/2. For each nonzero complex representative z_i set

    T_i = {z_i, omega*z_i, omega^2*z_i},   r_i = |z_i|.

Assume the orbits are pairwise distinct and their union is in strictly convex
position. An **own-side arrow** i -> j means that, for some gain g in {0,1,2},

    |z_i - omega^g*z_j|^2 = 3*r_i^2.                         (1)

The two other vertices of T_i are already at distance sqrt(3)*r_i from z_i.
We are studying extra witnesses at that SAME radius, not at arbitrary radii.
All references to radii r_i in the interlacing statements mean distances
from the common rotation center, not the selected distance sqrt(3)*r_i.

The angular phases may be arbitrary real numbers. In particular, nothing in
this packet assumes that an angle is a rational multiple of pi, or that a
radius is bounded by an incident polygon side.

## 2. Common-supplier interlacing theorem

**Theorem.** Suppose four distinct orbits A,B,C,D in a strictly convex C3
union satisfy all four own-side arrows

    A -> C,  A -> D,  B -> C,  B -> D.

Then

    min(r_C,r_D) < max(r_A,r_B) < max(r_C,r_D).               (2)

The source pair's largest radius lies STRICTLY between the two supplier
radii. Equality of r_A and r_B is permitted by the hypotheses. Equality of
the supplier radii is ruled out by the conclusion. The proof does not assume
that all four radii are distinct.

This theorem is established by a complete finite reduction to 486 exact
integer contradiction certificates. Sections 5-8 give the reduction,
geometry-to-model argument, coefficient convention, and certificate rule.
No floating-point infeasibility result is accepted as a certificate.

### An infinite consequence: paired-supplier cycles cannot close

Form a directed graph on unordered pairs of orbit labels. Put

    {A,B} -> {C,D}

exactly when these are disjoint pairs and all four arrows above hold. Define
R({A,B})=max(r_A,r_B). Equation (2) implies

    R({A,B}) < R({C,D}).                                    (3)

This graph is acyclic. Unlike the single-orbit arithmetic potential in the
preceding packet, this strict increase needs NO rational-angle hypothesis.
It acts on pairs, not on individual arrows; individual directed cycles can
and do exist at irrational angles.

Consequently any cyclic sequence of disjoint groups, each of size at least
two, is impossible when every member of each group sends an own-side arrow
to every member of the next group. For each adjacent group pair choose two
members of the source group including a largest-radius member and two of
the target group including a largest-radius member. Applying (3) forces a
strict increase of the group maximum around the cycle.

In particular the previously stored six-label abstract control

    {0,1} -> {4,5} -> {2,3} -> {0,1}

with all four arrows on each group transition cannot have such a strictly
convex C3 realization, whatever its angular phases or radii. The old
monotone-path rule alone did not reject this graph.

## 3. A finite consequence: at most six own-side orbits cannot all be bad

**Theorem.** A strictly convex union of at most six distinct concentric
C3 orbits cannot give every vertex four witnesses at its own orbit-side
radius sqrt(3)*r_i.

The proof combines (2) with two preliminary facts, then exhausts a small
finite directed-graph domain. The facts are included to make the dependency
chain explicit. They do not use the earlier radius-window theorem or the
continuous power-quotient convexity theorem.

### A supplier orbit contributes at most one witness

If b and omega*b both witness a at its own-side radius, the perpendicular
bisector makes a=t*omega^2*b for a real t. The radius equation is

    t^2+t+1=3*t^2,   or   (t-1)*(2*t+1)=0.

At t=1 the two orbits coincide. At t=-1/2 the center a is the midpoint of
b and omega*b and is not extreme. Thus distinct strict-hull orbits supply
at most one witness each at this radius. A four-tie therefore needs two
DISTINCT supplier orbits. Selecting two per center gives outdegree exactly
two; ignoring any extra arrows is a valid necessary-condition reduction.

### No reciprocity and no monotone downward shortcuts

Write s=|a|^2, t=|b|^2. Direct multiplication, or the cubic polynomial for the
three rotated squared distances, gives the existing identity

    product_(g=0,1,2)(|a-omega^g*b|^2-3*s)
        = |a^3-b^3|^2-9*s*(s-t)^2.                          (4)

Hence i -> j implies

    |z_i^3-z_j^3| = 3*r_i*|r_i^2-r_j^2|.                  (5)

Equal radii would force equal cubes, hence coincident orbits. Two opposite
arrows give, on squaring (5) in both directions,
9*(s-t)^3=0 and the same contradiction. These arguments need no convexity.

Suppose an underlying undirected path v_0,...,v_h, h>=2, has strictly
increasing radii. Put R=r_(v_h). On each path edge, its source radius is at
most R; at least one edge's source radius is strictly smaller. Thus (5) gives

    sum_j |z_(v_(j+1))^3-z_(v_j)^3|
        < 3*R*(r_(v_h)^2-r_(v_0)^2).

A downward arrow v_h -> v_0 would make its cubed chord equal the right side,
contradicting the ordinary triangle inequality along the path. The path
edges can point either way. This is the monotone-radius no-shortcut rule.

### Exhaustive graph domain, including possible equal radii

Sort the orbit labels 0,...,m-1 by NONDECREASING r_i, breaking ties arbitrarily.
Every graph edge joins unequal radii. Therefore a path with strictly
increasing indices has strictly increasing radii even if some nonadjacent,
noninteracting orbits have equal radii. The no-shortcut rule remains valid.

At each label choose an unordered two-element subset of the other labels as
its outgoing row. Reject reciprocal pairs and downward edges with an
alternative increasing-index path of length at least two. Complete exact
branching gives:

| Number of orbits | Graphs surviving these two rules |
|---:|---:|
| 3 | 0 |
| 4 | 0 |
| 5 | 0 |
| 6 | 4 |

For fewer than three orbits, there are not two distinct suppliers. The four
six-orbit survivors, in radial order, are:

    G0: [{3,4},{0,5},{0,5},{1,2},{1,2},{3,4}]
    G1: [{3,5},{0,5},{0,5},{1,2},{1,2},{3,4}]
    G2: [{4,5},{0,5},{0,5},{1,2},{1,2},{3,4}]
    G3: [{4,5},{4,5},{0,1},{0,1},{2,3},{2,3}].

G0, G1 and G2 have {3,4}->{1,2}, contrary to the upper inequality of (2).
G3 has {0,1}->{4,5}, contrary to the lower inequality of (2). These are
strict radius contradictions even when ties were allowed initially:
each source is connected to both target orbits, so the relevant compared
radii cannot tie. Hence none has a convex own-side realization.

The primary depth-first search uses an incrementally maintained reachability
check. The separate `--full-product-crosscheck` enumerates ALL 10^6 six-orbit
row tuples without branch pruning, uses tuple membership to reject reciprocal
arrows, and uses an explicit increasing-path traversal. It compares its four
survivors to the primary brancher. The completed cross-check found 14,490
reciprocal-free row systems, four no-shortcut survivors and zero survivors
after common-supplier interlacing. This is a different implementation of the
finite graph coverage, not independent external mathematical review.

## 4. The seven-orbit graph gap remains real

The following seven-label abstract graph, in increasing radial rank, survives
both the path rule and every application of (2):

    0 -> {1,2}
    1 -> {4,6}
    2 -> {1,6}
    3 -> {0,6}
    4 -> {2,3}
    5 -> {1,3}
    6 -> {4,5}.

Its outgoing two-sets are all different, so no two centers have two common
selected suppliers. The common-supplier rule has nothing to act on.

The checker verifies this exact graph. It does NOT provide coordinates,
distances, a complete geometric angle assignment, or a convex realization.
This is a negative control for the two graph rules, not a counterexample to
Erdos #97. No exhaustive seven-orbit geometric exclusion is claimed.

## 5. Reduction of the local theorem to 486 cases

Restrict the alleged configuration in Section 2 to its four orbits. A subset
of strictly convex vertices remains convexly independent. No two distinct
orbits can have the same phase modulo 2pi/3: the smaller radial point would
lie inside the larger orbit's triangle, unless the orbits coincided.

Choose the four representatives in one fundamental phase interval, ordered
counterclockwise. Labels 0,1,2,3 denote those representatives; i+4*k denotes
omega^k*z_i. Thus the twelve boundary labels occur in natural order 0,...,11.
This uses angular order, NOT equally spaced angular phases.

Up to cyclic starting point and relabeling within the two pairs, the binary
source/target order has exactly two types:

    topology 0: source labels {0,1}, target labels {2,3};
    topology 1: source labels {0,2}, target labels {1,3}.

Each of the four arrows has a gain g in {0,1,2}. All 3^4=81 choices are
examined, in source-major, target-major order. Rotating an individual
representative merely changes these gains and does not escape the census.

The negation of (2) has three cases, with strict comparisons because
source-target equal radii are impossible:

    mode 0: both sources smaller than both targets;
    mode 1: first source larger than both targets;
    mode 2: second source larger than both targets.

No comparison between the two sources or between the two targets is imposed
unless implied by a mode. The modes cover equality at the boundary as well,
because the forbidden equality would be on an arrow.

We therefore need exactly 2*81*3=486 contradictions. The artifact contains
one exact certificate for every case, with no omitted, duplicated, or
unknown case. Of these, 480 use the chord-angle model of Section 6 and six
use the ordinary-distance model of Section 7.

## 6. Exact chord-angle model

There is a variable for each simultaneous-rotation class of unordered
chords. For m orbits the number of classes is

    m + 3*binom(m,2).

For a pair of vertex labels a<b, let i=a mod m, j=b mod m, and let k,l be
their layers (integer quotients by m). If i=j there is one own-triangle
chord class. If i<j the class is (i,j,l-k mod 3); if i>j interchange the
orbit labels and reverse the layer difference. Equality of lengths along
an own-side arrow merges that spoke class with the source's own-triangle
chord class. A disjoint-set quotient takes the transitive closure.

### Direction lifts and exact rotation offsets

Let phi_ab be consistent unwrapped directions of the directed chords
p_a->p_b for a<b in counterclockwise convex order. These directions can be
chosen so that for a<b<c the triangle angles are exactly

    at a: phi_ac-phi_ab,
    at b: pi+phi_ab-phi_bc,
    at c: phi_bc-phi_ac.                                    (6)

All three are strictly positive. One justification of simultaneous
consistency is to move the two endpoints continuously in their ordered
boundary parameters. The chord direction lifts continuously on the domain
of ordered distinct endpoints; convexity puts the above direction
differences in (0,pi). Equivalently, extend p(t) periodically around the
polygon and lift chord directions on t<u<t+n, taking the forward tangent
limit as u tends to t. Moving both endpoints by a full period adds 2pi.

For each simultaneous-rotation class C choose its first lexicographic
representative pair (a_C,b_C). Rotating both endpoints by m labels normally
adds 2pi/3 to phi. If one endpoint wraps through 3m and the sorted chord
reverses, the consistent change is 2pi/3-pi. Two endpoint wraps subtract
2pi. Tracking the sum of endpoint labels consequently gives

    3*phi_ab = q_C + eta_ab*pi,
    eta_ab = (a+b-a_C-b_C)/m,   q_C=3*phi_(a_C,b_C).         (7)

The offset eta_ab is an INTEGER. This formula expresses rotational
symmetry; it does not assume regular placement of the distinct orbit phases.

There are 22 chord-class variables and one pi variable when m=4. Substituting
(7) into three times (6) produces integer coefficient rows. The middle angle
has constant 3*pi; the other two have constant zero before the offsets.
The model adds pi>0 and fixes the arbitrary global orientation with
phi_01=0. This gauge is legitimate because every other condition is unchanged
by adding one constant to all chord directions.

### Equal and ordered lengths imply linear angle relations

For every triangle and each pair of its opposite sides:

- equal selected-distance quotient classes imply equality of opposite angles;
- a specified strict comparison r_i>r_j implies the same comparison of
  own-triangle side lengths sqrt(3)*r_i and sqrt(3)*r_j; whenever these
  two length classes are the opposite sides, the opposite angles have the
  corresponding strict order.

The implication from side order to angle order holds for every nondegenerate
Euclidean triangle, including obtuse ones. All vertex triples of a strictly
convex polygon are nondegenerate.

Thus every actual forbidden configuration yields a solution to

    A*x > 0,   E*x = 0,                                    (8)

where A,E have integer entries. The model is only necessary; no implication
from an abstract solution of (8) to Euclidean realizability is asserted.
The two positive controls in Section 9 have both exact coordinates and a
separate rational feasible vector for this model, to test against spurious
universal rejection.

## 7. Ordinary-distance fallback for six cases

The metric model uses the same rotational chord classes and selected-distance
quotient, but variables denote ORDINARY lengths, not squared lengths or
angles. Its strict rows are:

    d_ac+d_bd-d_ab-d_cd > 0,
    d_ac+d_bd-d_ad-d_bc > 0       for a<b<c<d,
    d_ab+d_bc-d_ac > 0           for every distinct triangle ordering,
    d_ab > 0,

together with the own-side length comparisons prescribed by the mode.
The first two inequalities follow by splitting the crossing diagonals of a
strictly convex quadrilateral at their intersection and adding strict
triangle inequalities. After quotienting equal distances these remain
integer linear strict inequalities. They give the remaining six exact
certificates when the angle-only model is insufficient.

The fallback cases (topology,gain_code,mode) are exactly

    (0,39,1), (0,67,2), (1,7,2),
    (1,38,1), (1,39,1), (1,79,2).

Here gain_code is the base-three four-digit code, most significant digit
first, in the arrow order of Section 5.

## 8. Certificate acceptance rule and reproducibility

`certificates.json` stores records of the form

    [topology, gain_code, mode, kind, strict_terms, equality_terms].

Kind 0 is the angle model and kind 1 the metric model. Each term is
[row_index, integer_multiplier]. Model rows are sorted lexicographically
and duplicates are removed, making the index convention reproducible.

For each record the checker reconstructs A,E from the case rather than
trusting a stored matrix. It then verifies

    sum_i lambda_i*A_i + sum_j mu_j*E_j = 0,

with every retained lambda_i a POSITIVE integer, at least one lambda_i
present, and every mu_j a signed nonzero integer. Row indices cannot repeat.
All coordinates of the sum must be exactly zero. Summing (8) would then give
0>0. This is an exact contradiction, not a small numerical residual.

All 486 records passed this rule. The largest certificate has 21 nonzero
terms, and the largest absolute integer multiplier is 210. The replay also
checks exact case coverage and the 480-angle/6-metric census.

`generate_certificates.py` uses NumPy/SciPy to DISCOVER multipliers. It
rationalizes them and invokes the same integer checker before saving any
record. Solver tolerances cannot make an invalid coefficient identity pass
replay. The verification program does not import the generator, NumPy,
SciPy, or any other third-party package. Regeneration may produce different
valid multipliers with another solver version; proof replay uses the pinned
artifact and exact reconstructed rows.

A second encoder, `audit_expanded_model.py`, retains all 66 individual chord
variables. It constructs rotation relations explicitly, obtains the direction
offsets by graph traversal rather than the label-sum formula, and merges
whole distance classes instead of using the folded disjoint-set code. Its
projected angle and metric row sets agree exactly with the primary encoder
in all 486 cases. This is an implementation cross-check, not independent
external review and not a replacement for the geometric argument.

This is a computer-assisted local proof. The finite arithmetic replay does
not by itself establish the geometric soundness in Sections 5-7. That part
is the written argument and remains an independent review obligation.

## 9. Exact controls

### Common suppliers are possible in the permitted radial order

Using coordinates z=x+i*sqrt(3)*y, take the four representatives in phase
order

    z_0 = 1,
    z_1 = (157+63*i*sqrt(3))/148,
    z_2 = (71+53*i*sqrt(3))/74,
    z_3 = (4+5*i*sqrt(3))/7.

Their twelve rotations are strictly convex. The exact arrows are

    (source,target,gain) = (1,0,2), (1,2,2), (3,0,2), (3,2,1).

The squared radii are

    1, 247/148, 91/37, 13/7.

Hence targets {0,2} bracket the maximum radius of sources {1,3}, as (2)
requires. The checker verifies all 120 supporting-edge determinants, pair
separations, arrow identities, and every distance class. It also verifies a
rational feasible angle assignment against the equalities and ALL strict
radial comparisons for this fixture. This is not a complete four-bad set.

### A genuine irrational-angle cycle must remain allowed

The three seeds from the existing orbit66 construction, normalized by a
common similarity, are

    a_0=1,
    a_1=(-26503+8991*i*sqrt(3))/21854,
    a_2=(-44665+10753*i*sqrt(3))/37058.

Using phase-ordered representatives a_0,omega^2*a_1,omega^2*a_2, they have
arrows (0,1,2),(1,2,1),(2,0,2). All nine vertices are strictly convex and
have maximum multiplicity THREE. A rational feasible angle-model vector
passes exact replay. Each selected angle has a rational noninteger value of
2*cos(2*theta), certifying that theta/pi is irrational (a rational-angle
value of this expression would be a rational algebraic integer, hence an
integer). The checker verifies these expressions exactly.

The pair-ascent theorem permits this cycle because no two centers share two
suppliers. It must not be misreported as acyclicity of the original arrow
graph. The 66-point construction is neither completed nor excluded here.

## 10. Run and claim boundary

From this directory, Python 3.10+ is sufficient for proof replay:

    python check_common_suppliers.py --check
    python check_common_suppliers.py --check --full-product-crosscheck
    python -m unittest -v test_common_suppliers.py
    python audit_expanded_model.py

Regenerate the diagnostic report after intentional changes with

    python check_common_suppliers.py --write

The certificate DISCOVERY program separately needs NumPy and SciPy:

    python generate_certificates.py

The report is generated from replay; do not edit it by hand. A successful
replay is not repository-wide CI, independent external review, a formalized
Euclidean proof, or an automatic change to the repository's accepted status.

What is established here, subject to independent review, is common-supplier
radius interlacing, its all-size paired-cycle obstruction, and the complete
at-most-six-orbit OWN-SIDE exclusion. What is not established is an arbitrary-
size own-side exclusion, exclusion of all rich radii in C3 sets, any reduction
of general convex polygons to C3 symmetry, or a proof/disproof of Erdos #97.
The explicit seven-label graph shows why another global forcing argument is
still needed.
