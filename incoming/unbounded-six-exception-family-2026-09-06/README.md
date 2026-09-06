# An unbounded exact partial family for Erdős #97

Date: 2026-09-06.

**Status: PAPER_PROOF_CANDIDATE / REVIEW_PENDING, with exact algebra and finite-instance checks.**

This packet supplies a written arbitrary-size construction and proof, not a
proof or counterexample to unrestricted Erdős Problem #97. Every member has
exactly six vertices satisfying the conclusion of that problem. The other
vertices have at least four equidistant witnesses. No independent external
mathematical review, formalization, optimality, or novelty relative to the
published literature is claimed. No repository status or accepted bound is changed.

## 1. Statement

For a finite set P and p in P, write

    M_P(p) = max_(r>0) #{q in P\{p} : |p-q|=r}.

Call p **rich** when M_P(p)>=4, and **good** when M_P(p)<=3.

**Theorem (written proof below).** For every integer m>=1 there is an explicitly
defined set P_m of 3(m+1) points in strictly convex position such that:

* three vertices have maximum multiplicity exactly 2;
* three vertices have maximum multiplicity exactly 3;
* the remaining 3(m-1) vertices have maximum multiplicity at least 4.

Thus the number of good vertices is exactly six, independently of size.
In particular, the proportion of good vertices tends to zero. This rules out
a universal positive-proportion strengthening of #97. It does not rule out a
universal positive constant number of good vertices and does not contradict
#97's requirement of at least one.

The proof does NOT establish that every rich vertex has maximum multiplicity
exactly four for all m. The finite instances checked in this packet do have
that stronger distribution.

The preceding repository packet recorded one 66-point construction with the
same counts 3,3,60. The present recurrence starts with different, much simpler
coordinates and proves arbitrary finite continuation with six exceptions.
It is not merely a longer numerical run of that construction. See provenance
and the comparison in Section 9.

## 2. Exact recurrence and coordinates

Identify the plane with C. Put

    omega = (-1+i*sqrt(3))/2,
    D(t) = 1+3t^2,
    B(t) = 1-2t+3t^2,

    z(t) = -1/2 + 3t/D(t)
           + i*sqrt(3)*(1-3t^2)/(2D(t)).

Start t_0=1/10. Define

    t_(j+1) = [B(t_j)-sqrt((1-t_j)(1-3t_j)D(t_j))]/2.       (1)

Every square root is the nonnegative real root. An equivalent, numerically
stable expression is

    t_(j+1) = 2t_j^2 /
       [B(t_j)+sqrt((1-t_j)(1-3t_j)D(t_j))].                (2)

Define alternating conjugates

    a_j = z(t_j)          if j is even,
    a_j = conjugate(z(t_j)) if j is odd.

Finally,

    P_m = {1,omega,omega^2}
          union {omega^k a_j : 0<=j<m, 0<=k<3}.             (3)

The first orbit representative is rational over Q(sqrt(3)):

    a_0 = (-43+97i*sqrt(3))/206,
    |a_0|^2 = 73/103.

Equations (1)-(3), with the root choices specified, are exact coordinates for
every finite m. They are not decimal approximations.

### The recurrence is defined and strictly decreases forever

For 0<t<=1/10, the discriminant satisfies

    B(t)^2-4t^2 = (1-t)(1-3t)(1+3t^2)>0.

Let f_t(s)=s^2-B(t)s+t^2. Then

    f_t(0)=t^2>0,
    f_t(t)=-t(1-t)(1-3t)<0.

The smaller root is therefore strictly between 0 and t, and it is the root in
(1). In particular, 0<t_(j+1)<t_j<=1/10 at every step. There are no repeated
parameters or finite-time zero parameters.

For later use,

    f_(1/10)(1/80) = -7/32000 < 0,

so t_j<1/80 whenever j>=1.

The parameters converge to zero: their decreasing limit L would satisfy
f_L(L)=-L(1-L)(1-3L)=0, and the only such L in [0,1/10] is zero.
This limit is NOT used to turn an infinite object into a finite counterexample.

## 3. Four witnesses at every noninitial chain orbit

Direct expansion gives

    |z(t)|^2 = 1-3t/D(t),
    |z(t)-1|^2 = 3|z(t)|^2.                               (4)

The second equality is invariant under conjugation, so the anchor 1 witnesses
every a_j at its own equilateral-triangle side radius.

The additional identity is

    |conjugate(z(s))-z(t)|^2 - 3|z(s)|^2
       = -9 [s^2-(1-2t+3t^2)s+t^2]/[D(s)D(t)].            (5)

Substitute s=t_j and t=t_(j-1). Equation (1) makes the numerator zero.
Conjugation handles either parity of j, giving

    |a_j-a_(j-1)|^2=3|a_j|^2,       j>=1.                 (6)

For each j>=1, the four distinct witnesses of a_j are

    1, a_(j-1), omega*a_j, omega^2*a_j.                    (7)

The last two distances equal sqrt(3)|a_j| because they are its orbit mates.
Rotating all four witnesses proves the same assertion at omega*a_j and
omega^2*a_j. Distinctness of all the points is established together with strict
convexity in Section 4. Thus (7) proves at least four witnesses at 3(m-1)
vertices, without an equality tolerance or floating-point solver.

## 4. Strict convexity at every finite length

This is the essential infinite-size step: adding arbitrarily many points does
not eventually place an earlier point inside the hull.

Put

    q(t)=omega^2 z(t)
        =(2-3t-3t^2)/(2D(t))
           + i*sqrt(3)*3t(t-1)/(2D(t)),
    c=(1+i*sqrt(3))/4.

The arc q(t), 0<=t<=1/10, lies on the circle

    |q(t)-c|^2=3/4,

and q(0)=1. Every point in P_m is an anchor or belongs to one of the six arcs

    omega^k q(t), omega^k conjugate(q(t)), k=0,1,2.

We prove that each nonanchor point of these six arcs has a strict supporting
line relative to the entire six-arc union and all three anchors.

### Exact supporting margins

For s>0 let n(s)=q(s)-c. This is nonzero and is the candidate outward normal
at q(s). Use the ordinary Euclidean dot product. Set

    r_(+,k)(t)=omega^k q(t),
    r_(-,k)(t)=omega^k conjugate(q(t)).

Exact expansion gives

    n(s) dot [q(s)-r_(eps,k)(t)]
        = 3 P_(eps,k)(s,t)/(2D(s)D(t)),                    (8)

where:

    P_(+,0) = 3(s-t)^2;

    P_(+,1) = (9s^2t^2+9s^2t-18st^2+6st+3t^2-3t+2)/2;

    P_(+,2) = (18s^2t^2-9s^2t+3s^2+6st-6s+3t+1)/2;

    P_(-,0) = (3/2)(3s^2t^2-3s^2t+2s^2-6st^2+2st+t^2+t);

    P_(-,1) = (3st-1)^2;

    P_(-,2) = (9s^2t+3s^2+6st-6s+6t^2-3t+1)/2.

All denominators in (8) are positive. On 0<=s,t<=1/10:

    P_(+,1) >= 841/1000 > 0,
    P_(+,2) >= 391/2000 > 0,
    P_(-,2) >= 1/20 > 0,
    P_(-,1) >= (97/100)^2 > 0.

The first three lower bounds follow by discarding nonnegative nonconstant
terms and bounding every negative monomial by its value in absolute magnitude
at s=t=1/10. They are conservative bounds, not claimed minima.
For the fourth, 3st<=3/100.

The remaining cross-arc polynomial has the positive decomposition

    P_(-,0) = (3/2)[s^2(2-3t)+2st(1-3t)+t^2+t+3s^2t^2].   (9)

It is strictly positive whenever (s,t)!=(0,0). On the same arc P_(+,0)>0
whenever s!=t. The map q is injective on this interval: for example,
|q(t)-1|^2=9t^2/D(t) is strictly increasing for t>0.

It follows that n(s) strictly exposes q(s) among all distinct points of the
six arcs and the anchors (the anchors occur at t=0 in these formulas).
Rotation and reflection give a strict supporting normal for every other
nonanchor point. They also establish that distinct arcs have no duplicate
points with positive parameters.

Finally all nonanchor points have norm squared 1-3t/D(t)<1 by (4), while
1,omega,omega^2 have norm one. Each anchor is uniquely exposed by its own
radial normal: for example Re(q)<=|q|<1 for any nonanchor q, and the other two
anchors have real part -1/2.

Thus every point of P_m is uniquely exposed and hence a vertex of its convex
hull. No three such points can be collinear, since a middle point of three
collinear points could not be uniquely exposed. The points are distinct and
P_m is in strictly convex position. This proves strict convexity for every
finite m; no numerical lower bound uniform in m is asserted or needed.

## 5. The anchors have maximum multiplicity exactly two

For each t>0, the squared distances from 1 to the orbit of z(t) are, in some
order,

    L(t)=9t^2/D(t),
    M(t)=3-9t/D(t),
    H(t)=3/D(t).                                           (10)

Conjugating the orbit merely permutes the same three distances. On
0<t<=1/10, each of L,M,H is injective: the signs of their derivatives are
respectively positive, negative, negative. Moreover,

    L(t)<1,   M(t)>2,   H(t)>2.

Since the parameters t_j are distinct, a distance in the small range occurs
at most once, and one in the large ranges occurs at most twice (once from M
and once from H). All three quantities are strictly below 3. The anchor's
other two anchor-orbit vertices are at squared distance exactly 3. Therefore
M_(P_m)(1)=2. Rotational symmetry gives the same conclusion at omega,omega^2.

## 6. The initial chain orbit has maximum multiplicity exactly three

Let p=a_0=(-43+97i*sqrt(3))/206. Its two orbit mates and the anchor 1 have
squared distance 219/103 from p. The other two anchors have squared distances
9/103 and 300/103.

It remains to bound all distances to later orbits, whose parameters lie in
0<u<1/80. Define

    F_(+,k)(u)=|p-omega^k z(u)|^2,
    F_(-,k)(u)=|p-omega^k conjugate(z(u))|^2.

Each denominator is 103D(u). The numerators and strict derivative signs on
0<u<=1/80 are:

| Function | Numerator | Derivative sign |
|---|---|---|
| F_(+,0) | 9(10u-1)^2 | negative |
| F_(+,1) | 3(219u^2-270u+100) | negative |
| F_(+,2) | 3(9u^2+21u+73) | positive |
| F_(-,0) | 3(3u-10)^2 | negative |
| F_(-,1) | 3(300u^2-270u+73) | negative |
| F_(-,2) | 9(73u^2+7u+1) | positive |

For completeness, after differentiating and clearing the positive denominator
103D(u)^2, the six derivative numerators are respectively

    18(3u+10)(10u-1),
    162(15u^2-3u-5),
    -63(3u^2+20u-1),
    18(3u-10)(10u+1),
    162(15u^2+3u-5),
    -63(3u^2-20u-1).

Their stated signs follow immediately on [0,1/80]. In particular, every
function is injective and never equals its limit at u=0 for positive u.
The limits are 9/103,219/103,300/103, with exactly two functions per limit.

These three groups have disjoint ranges. Indeed each point of a later orbit
is within distance 3u/sqrt(D(u))<=3/80 of its limiting anchor e. Since
|p-e|<2, the difference in squared distances is bounded by

    ||p-y|^2-|p-e|^2|
       <=2|p-e||y-e|+|y-e|^2
        <4(3/80)+(3/80)^2=969/6400<1/4.

The three limits are pairwise separated by more than 1/2, so the open bands
of radius 1/4 around them are disjoint. Within each band there are only two
injective parameter functions; each parameter t_j occurs once in the chain.
Thus any later-point distance occurs at most twice. None equals the three
anchor-distance limits: its own function is strictly monotone from its limit,
and the other bands do not contain that limit.

Consequently the three already listed witnesses at 219/103 are the unique
maximum class at p, and M_(P_m)(p)=3. Rotation proves the same for its orbit.
Together with Sections 3-5 this proves the theorem.

## 7. What this establishes about the unconditional problem

This family establishes

    inf_P #{p in P: M_P(p)<=3}/|P| = 0,

where the infimum is over finite nonempty strictly convex planar sets of at
least two points. For any c>0, take m+1>2/c to violate a purported universal
lower bound c|P| on the number of good vertices. The good count in this family
is still six, not zero.

The four-witness radii vary with the orbit. This is not a common-unit-distance
construction. The two-constraint chain adds three already-rich vertices but
does not repair its three anchor vertices or the three initial vertices.
Their all-radius upper bounds are proved in Sections 5-6. Increasing m does
not make any of these six exceptions become rich.

Nor does taking the limit help: the chain parameters tend to zero and the
new points accumulate at the already present anchors. The theorem and #97 are
finite-set statements. No limiting argument here supplies a finite all-rich set.

Thus the recurrence proves arbitrary convex continuation of a partial
construction, not the missing unconditional contradiction or complete
counterexample. The existing extraction question for arbitrary all-rich
polygons remains outside this packet.

## 8. Exact checks and reproduction

Python 3.10+; no third-party package is required.

    python algebra.py
    python verify.py --algebra-only
    python verify.py --chain-orbits 5 --bits 2048
    python verify.py --chain-orbits 9 --bits 8192
    python verify.py --chain-orbits 11 --bits 16384
    python -m unittest -v test_family.py

`algebra.py` implements polynomial arithmetic over rational numbers directly.
It checks the recurrence discriminant, the equal-distance identities, all six
supporting-margin identities and rational positivity bounds, and all six
initial-seed distance functions and derivative signs. It checks the algebra
underlying the arbitrary-size proof; it does not formalize the geometric
interpretation of strict supporting lines or the counting argument.

`verify.py` constructs an individual finite instance using outward-rounded
dyadic intervals. It obtains a certified polar order, checks every supporting
edge against every other point, proves all point pairs distinct, and verifies
the complete distance-class distribution at each vertex. Equalities are
inherited only from the proved recurrence and rotational identities. All
other distance classes must be strictly separated by their intervals. An
unresolved comparison is a failure, never an inferred equality or inequality.
A disjoint-set quotient records only proved identities; interval intersections
for that quotient combine enclosures of already-proved equal quantities.

The verifier fails closed when precision is insufficient. Because t_(j+1) is
approximately t_j^2, later parameters become extremely small, and high m can
require enormous precision for a full numerical enclosure census. The
arbitrary-size paper proof does not require executing such a census at each m.

### Fresh completed finite checks

| Chain orbits m | Points | Bits | Full support checks | Distinct pairs | Unequal distance-class separations | Distribution |
|---:|---:|---:|---:|---:|---:|---|
| 5 | 18 | 2048 | 288 | 153 | 1767 | 3 at M=2, 3 at M=3, 12 at M=4 |
| 9 | 30 | 8192 | 840 | 435 | 9987 | 3 at M=2, 3 at M=3, 24 at M=4 |
| 11 | 36 | 16384 | 1224 | 630 | 18147 | 3 at M=2, 3 at M=3, 30 at M=4 |

Additional small checks and a 1024/2048-bit agreement check occur in the
28-test suite. The different precisions execute the same verifier, not
independent implementations or external review. No complete 66-, 72-, or
300-point interval census is claimed. Those sizes are covered by the written
arbitrary-size theorem, with m=21,23,99 respectively.

`test_output.txt` records the actual completed standard-library test run.
`validation.json` records commands, source hashes and scope. The artifact is
self-contained; repository-wide CI was not run and no PR was opened.

### Repository integration note (2026-09-06)

The statements above describe the preparation session. During publication the
four Python sources were reformatted onto separate statements to satisfy the
repository lint gate (`ruff` E701, E702, F401), two unused imports were removed
from `test_family.py`, and that module now loads `verify.py` under the module
name `unbounded_six_family_verify` because other incoming packets also ship a
top-level `verify.py` and a single pytest session would otherwise bind the
wrong one. The edits are formatting and module loading only: no identity,
bound, threshold or reported value changed, `algebra_checks.json` and the three
finite reports regenerate byte-identically from the reformatted sources, and
the 28-test suite still passes. `manifest.json` and `validation.json` carry the
updated hashes; `validation.json` also records the delivered source hashes.
`test_output.txt` keeps the preparation run's bytes; a rerun after the reformat
differs only in the reported elapsed time.

## 9. Provenance and review obligations

The repository input re-read in this session is:

    davidiach/erdos97
    docs/orbit66-exact-partial-construction.md
    Git blob f691606b6cb63668a99da2d332a96db74621380f

That note provides the previous 66-point counts and the incoming/outgoing
constraint-circle framework. The earlier conversation's six-point rational
near-coincidence example used the same parameterization z(t) (there called
h). The new contributions of this packet are the alternating-conjugate
recurrence, its arbitrary-length convexity proof by six-arc support margins,
and the all-length classification of exactly six exceptional vertices.
No claim of published novelty is made from this provenance comparison.

Interval arithmetic follows the outward-rounded integer technique of the
prior packets, now with per-object precision. SymPy and floating experiments
were used during discovery of identities but are not dependencies of the
stored exact verifier or evidence for a claimed equality.

Review should independently check the sign and direction of (5), the six
rotation/reflection cases in (8), the transition from strict supports to
convex independence, the initial-orbit band argument, and all quantifiers in
the all-size theorem. The 28 tests supplement these paper proof obligations;
they are not an independent mathematical review.
