# A transitive-triangle radius rule, a forbidden diamond, and seven-orbit closure

Date: 2026-09-05. Continuation of `davidiach/erdos97`, after research PR #931
head `12ccc553a41fa08fc3100f3da84003343b73032a`. A final read confirmed
#931 merged as `e955c4513b44989c34bef22e5ae1cdd85b949c3b`; the final
background-model variable-rename fix is retained without changing any
mathematical row or certificate.

Status: **PAPER_PROOF_CANDIDATES / COMPUTER_ASSISTED_RESTRICTED_THEOREMS /
REVIEW_PENDING**. No independent external mathematical review or published
novelty is claimed. No unrestricted proof or counterexample to Erdős Problem
#97 is claimed. No accepted general finite-case bound is promoted.

## Results and scope

For a strictly convex union of distinct concentric equilateral-triangle
orbits, at each source consider ONLY the distance to its two orbit-mates.
An arrow means that another orbit supplies a witness at this own-side radius.
This packet establishes:

1. A transitive triangle `A->B, B->C, A->C` forces
   **`r_B < r_A < r_C`**, where the r's are distances from the rotation center.
   This applies at arbitrary size and arbitrary real angular phases.
2. Consequently the five-arrow diamond
   `A->B,C; B->C,D; C->D` is impossible on four distinct orbits. It does not
   require two sources to have an identical supplier pair.
3. A strictly convex union of at most **seven** distinct C3 orbits cannot
   give every vertex four witnesses at its own orbit-side radius. An
   exclusively own-side construction therefore needs at least eight orbits,
   or 24 vertices.

The last statement is **not** a general exclusion of 21-point polygons or
an all-radius exclusion of every C3-symmetric 21-point polygon. Four-fold
classes not using the source's orbit-mates remain outside this construction.
There is no reduction from arbitrary polygons to this symmetry family.

The prior six-orbit bound appears both in #931's common-supplier packet and
in the separate #934. The seven-orbit extension and the transitive-triangle
rule here are the continuation, not a relabeling of that six-orbit result.

## 1. Definitions and preliminary geometry

Put

    omega = (-1+i*sqrt(3))/2,
    T_i = {z_i, omega*z_i, omega^2*z_i},
    r_i = |z_i| > 0.

The orbits are pairwise distinct and all their points are extreme points of
their common convex hull. An own-side arrow i->j, with gain g in {0,1,2}, is

    |z_i-omega^g*z_j|^2 = 3*r_i^2.                         (1)

The selected radius is sqrt(3)*r_i, NOT r_i. Every use of a radial order
below refers to the r_i, not a polygon boundary-side length.

The origin is strictly inside every orbit triangle. Two different orbits
cannot have the same phase modulo 2pi/3: the shorter radial point would
lie strictly between the origin and a vertex of the larger triangle, unless
the orbits coincided. Thus one may choose one representative per orbit in a
fundamental angular interval, with distinct phases. Their phase order,
repeated in three layers, is the polygon boundary order. No angular grid
or equal angular spacing is assumed.

A useful bound follows from the incircle of each orbit triangle. The
triangle of radius r_j contains the closed disk of radius r_j/2 about the
origin. Any other polygon vertex at norm at most r_j/2 would be in that
triangle and would not be an extreme point of the union. Consequently

    r_j/r_i < 2   for every two distinct orbits i,j.         (2)

The inequality is strict: a point on a side of another triangle is not a
new extreme point. This does not bound the selected radius by an incident
side of the full polygon; no such short-radius hypothesis is used here.

The existing cubic identity is

    product_(g=0,1,2)(|a-omega^g*b|^2-3s)
        = |a^3-b^3|^2-9s(s-t)^2,
    s=|a|^2, t=|b|^2.                                    (3)

Hence i->j implies

    |z_i^3-z_j^3|=3*r_i*|r_i^2-r_j^2|.                    (4)

It follows that an arrow cannot join distinct equal-radius orbits, and a
pair cannot support both arrow orientations. An increasing-radius undirected
path of length at least two cannot have a downward endpoint shortcut:
its cubed edge lengths sum to strictly less than the shortcut length in
(4). This is an ordinary triangle-inequality argument and does NOT depend
on the prior convex-power-quotient theorem.

One supplier orbit can contribute at most one own-side witness. If both b
and omega*b supplied a, their perpendicular bisector gives
`a=t*omega^2*b` with real t. The distance equation becomes

    t^2+t+1=3t^2,  or (t-1)(2t+1)=0.

The first root identifies the orbits. The second makes a the midpoint of
the two witnesses. Both contradict the stated hypotheses. Thus a four-fold
own-side class requires two distinct supplier orbits.

## 2. Transitive triangles have coherent rotation gains

Define the circle

    C = {x in complex numbers: |x-1|^2=3}.

Suppose A->B, B->C, A->C. Incorporate the gains of the first two arrows into

    x = omega^g_AB * z_B/z_A,
    y = omega^g_BC * z_C/z_B,
    eta = omega^(g_AC-g_AB-g_BC).

Then x,y,eta*x*y all belong to C. The three orbits are distinct.

For w in C, its equation gives the exact conjugation rule

    conjugate(w) = (w+2)/(w-1).                            (5)

The denominator is nonzero since 1 is not in C. Equating the conjugate of
eta*x*y to eta^(-1)*conjugate(x)*conjugate(y), then clearing the nonzero
denominators, gives F_eta=0, where

    F_eta = (x+2)(y+2)(eta*x*y-1)
            - eta*(eta*x*y+2)*(x-1)*(y-1).

For eta=1, direct expansion yields

    F_1=3*(x*y*(x+y)-2).                                  (6)

For either primitive cube root eta, expansion modulo eta^2+eta+1=0 gives

    F_eta=(2eta+1)*(x-eta^2)*(y-eta^2)*(x*y+2).             (7)

The first factor is nonzero. The roots x=eta^2 and y=eta^2 identify two
orbits. The root xy=-2 makes z_C/z_A equal to -2 times a cube root of unity:
a suitable rotated A vertex is then the midpoint of two vertices of T_C.
That also contradicts convex independence. Therefore eta=1.

**Gain coherence lemma.** Every transitive own-side triangle in a strictly
convex C3 union has

    g_AC = g_AB + g_BC (mod 3).

This is not an assertion about every directed cycle. In particular, the
known strictly convex three-orbit directed cycle is retained as a positive
control and has maximum distance multiplicity three at all nine vertices.

The sparse polynomial checker expands (6) and (7) exactly. It does not infer
zero from a numerical residual. The primitive factorization is closely
related to the earlier circle-product lemmas already recorded in the repo;
no claim of published novelty is made for that algebraic identity.

## 3. The radial alternatives, by elementary algebra

Gauge representatives so the three transitive arrows have gain zero, and
put p=xy=z_C/z_A. Equations (5)-(6) give

    p*(x+y)=2.

Write U=|x|^2, V=|y|^2, T=|p|^2=UV. Since x,y,p all belong to C,

    U+V=2*Re(x+y)+4=4*Re(1/p)+4=6-4/T.                   (8)

First, |p|>1. Let R=|p|. The arithmetic-geometric mean inequality applied
to (8) yields

    6-4/R^2 >= 2R,
    (R-1)*(R^2-2R-2) <= 0.

For 0<R<1, both factors on the left are negative, a contradiction. If R=1,
then U+V=2 and UV=1 force U=V=1. The equations |x|=1 and |x-1|^2=3 make x
a primitive cube root, identifying the A and B orbits. Thus R>1. Bound (2)
also gives R<2, hence 1<T<4.

Now (8) implies

    (U-1)*(V-1) = (T-1)*(T-4)/T < 0.                     (9)

Therefore one of U,V is below one and the other is above. In geometric
terms the only alternatives are

    r_B < r_A < r_C,    or    r_A < r_C < r_B.             (10)

In particular an index-increasing transitive triangle in radial order is
impossible. This elementary part is one of the predicates used in the
finite seven-orbit search.

## 4. The larger-middle alternative is impossible: 18 exact cases

The remaining alternative r_A<r_C<r_B is excluded by the chord-angle model
in Section 7. This produces the stronger local theorem

    A->B, B->C, A->C  ==>  r_B < r_A < r_C.                (11)

Here is the full finite reduction; the angles remain arbitrary real values.
Fix A as the first representative phase in a fundamental interval. There
are two possible orders of B,C. After the gain-coherence lemma, choose gauged
representatives so all three arrows have zero gain. Returning those gauged
representatives to the chosen fundamental interval assigns shifts

    s_A=0, s_B in {0,1,2}, s_C in {0,1,2}.

The shifts are discrete choices of orbit representatives, not restrictions
on their continuous phases. In fundamental representatives the gain of
u->v is s_v-s_u mod 3. Thus there are exactly

    2*3^2=18

phase-order/shift cases. In every one, impose only the radial comparisons
r_B>r_C and r_C>r_A, together with the three arrows. The angle model has 12
rotation chord classes and one pi variable. Every case has an explicit
positive-integer/equality-integer cancellation certificate in
`transitive_radius_certificates.json`.

`verify_transitive_radius` regenerates all 18 matrices and checks exact case
coverage and every coefficient of the contradiction. An expanded encoder
with all 36 individual chord directions gives exactly the same projected
model rows. The positive geometric control in Section 9 has the PERMITTED
radial order, and also has a separately checked rational feasible vector
for this angle model.

This is a computer-assisted local proof, not yet a short all-prose proof of
the larger-middle exclusion. The continuous geometry-to-linear-model
translation remains an external review obligation.

## 5. The five-arrow diamond is forbidden at every size

Suppose four distinct orbits have

    A -> B,C
    B -> C,D
    C -> D.                                              (12)

Applying (11) to A,B,C gives r_B<r_A<r_C. Applying it to B,C,D gives
r_C<r_B<r_D. In particular both r_B<r_C and r_C<r_B would hold. Contradiction.

This obstruction has DIFFERENT supplier pairs {B,C} and {C,D}. It therefore
operates in configurations where the previous repeated-supplier-pair rule
has nothing to act on.

For additional cross-checking, the packet retains a separate certificate
proof of (12) that was obtained BEFORE the stronger triangle theorem. The
two triangle coherences gauge all five arrows to zero. Up to a phase start
at A, there are 3! orders and 3^3 representative shifts, or 162 cases. Every
case is angle-obstructed with NO radial comparisons. All 162 certificates
are replayed in `diamond_certificates.json`. The seven-orbit finite search
uses this independently replayed five-arrow predicate plus the elementary
alternatives (10); it does not rely on the later 18-case strengthening.

The former seven-orbit guardrail

    0->{1,2}; 1->{4,6}; 2->{1,6}; 3->{0,6};
    4->{2,3}; 5->{1,3}; 6->{4,5}

contains (12) with (A,B,C,D)=(0,2,1,6). Thus this is an arbitrary-size local
obstruction to that guardrail, not just another search over its seven labels.
Already its transitive triangle 0->2->1, 0->1 violates (11) in its stated
increasing radial order.

### An additional algebraic rigidity identity

In a coherently gauged chain write x=z_B/z_A, y=z_C/z_B, z=z_D/z_C.
The two zero-gain triangle equations give

    xy(x+y)=2=yz(y+z),
    (x-z)(x+y+z)=0.

If x+y+z=0, then xyz=-2 and A is a midpoint of two D-orbit vertices. Otherwise
x=z, hence z_A*z_D=z_B*z_C. This algebraic reduction helps explain why the
five-arrow pattern is rigid. It alone is not advertised as a convexity
contradiction; the certified local radius rule supplies that contradiction.

## 6. Complete finite exclusion through seven orbits

Assume every orbit in a strictly convex C3 union has four own-side witnesses.
Select two distinct supplier orbits at each source. Delete any other arrows.
The resulting selected directed graph has outdegree exactly two.

Sort orbit labels 0,...,m-1 by NONDECREASING radius, breaking ties arbitrarily.
There is no edge between equal-radius orbits. Accordingly, every strictly
index-increasing graph path has strictly increasing physical radii, even
when noninteracting labels tie. A forbidden comparison along an actual
edge cannot be rescued by a tie.

The finite graph domain uses the preliminary no-reciprocity/no-shortcut
facts from Section 1 and the earlier common-supplier theorem

    A->C,D and B->C,D
      ==> min(r_C,r_D) < max(r_A,r_B) < max(r_C,r_D).        (13)

For self-contained replay its 486 exact certificates, exact model generator,
written reduction, and valid geometric controls are included. The proof
uses 480 angle certificates and six ordinary-distance certificates; it is
not assumed merely because its repository code once printed the expected
answer. See `common-supplier-background.md` and the provenance note.

The seven-orbit domain then has the following exact counts:

| Predicate stage | Complete graphs remaining |
|---|---:|
| All choices of two suppliers per vertex | 170,859,375 = 15^7 |
| No reciprocal arrows | 4,590,360 |
| No forbidden increasing-radius shortcut | 2,755 |
| Common-supplier interlacing (13) | 1,027 |
| No five-arrow diamond (12) | 349 |
| No index-increasing transitive triangle, by (10) | 177 |

The primary Python brancher prunes partial graphs only by monotone necessary
conditions. The separate C++ `graph_oracle.cpp` visits ALL 15^7 complete row
tuples without partial branch pruning, then applies the predicates. It uses
Boolean path closure instead of the primary reachability representation and
returns exactly the same sorted 177 masks. For three through six orbits, the
same Python domain already has zero graphs at the end of these predicates;
fewer than three orbits cannot supply two distinct target orbits.

The later stronger three-orbit rule (11) could reduce the 177 graphs further.
We deliberately retain the larger, already certificate-covered domain. No
phase case is discarded by an unrecorded extra rule.

### Complete phase and gain domain for the remaining graphs

Set the first fundamental phase to be orbit 0. Enumerate all 6!=720 orders
of the other six labels. For a directed edge i->j set u=r_j/r_i. Equation (1)
gives

    cos(theta)=u/2-1/u.

A downward edge has u<1 and hence cos(theta)<-1/2. If the target phase is
later than the source phase in the fundamental interval, its only possible
gain is 1; otherwise it is 2. An upward edge has cos(theta)>-1/2. It permits
gain 0, plus gain 2 when the target phase is later, or gain 1 otherwise.
These choices are necessary overapproximations; they are NOT angle grids.

For a graph with u upward arrows there are 720*2^u cases. Across the 177
radial graphs the exact sum is 7,718,400. The generated domain does not
assume that nonedge radii are different.

### Every phase case has an exact recorded contradiction

The phase search expands each case to the 21 actual vertex labels and their
four selected witnesses. It first tests two-circle and shared-witness chord
crossing restrictions. It then identifies ordinary distances under simultaneous
rotation and selected-row equalities and tests strict Kalmanson zero or
positive-scalar inverse pairs. It records an explicit certificate for every
such rejection rather than only an aggregate counter.

| Final phase obstruction | Cases |
|---|---:|
| Two-circle / shared-witness crossing | 5,754,240 |
| One zero Kalmanson row | 0 |
| Two positive-scalar-opposite Kalmanson rows | 1,963,930 |
| Residual cases rejected by exact angle certificates | 230 |
| Total | 7,718,400 |
| Unresolved / realizable cases supplied | 0 |

For each residual, the angle model uses the selected arrows and strict
radius comparisons ONLY along actual graph edges. It does not impose strict
inequalities between all noninteracting radial labels. Every one of the 230
has an exact integer contradiction in `seven_angle_certificates.json`.
The full phase replay reconstructs the exact residual keys and requires a
one-to-one match to these angle certificates.

This establishes the seven-orbit own-side obstruction conditional on the
written geometric reductions and correct replay implementation. It is not
a numerical search failure and not a claim about other radii.

## 7. Why the integer angle and distance certificates are sound

This section summarizes the geometric model so the new result need not be
read as a black-box invocation of the preceding packet.

For a<b<c in counterclockwise convex boundary order, choose compatible
unwrapped directions phi_ab of the directed chords. The triangle angles are

    phi_ac-phi_ab,
    pi+phi_ab-phi_bc,
    phi_bc-phi_ac.                                        (14)

They are strictly positive. Such simultaneous lifts follow by continuously
moving ordered boundary endpoints and lifting the chord direction, with
its forward-tangent limit as the endpoints approach. Convexity puts the
three displayed differences in (0,pi).

Threefold rotation adds 2pi/3 to a chord direction; if one endpoint wraps
around the 3m labels and the sorted chord reverses, it subtracts pi as well.
For each rotational chord class Q with representative pair (a_Q,b_Q), this
produces

    3*phi_ab = q_Q + [(a+b-a_Q-b_Q)/m]*pi.                 (15)

The bracket is an integer. These rotation identities make no assumptions
about equal spacing of the orbit phases. The number of chord classes is
m+3*binom(m,2), namely 12,22,70 for m=3,4,7 respectively. The angle model
adds a pi variable, requires pi>0 and fixes the harmless direction gauge
phi_01=0.

Own-side arrows equate a source's spoke length to its own-triangle side
length. Take the transitive closure of these length equalities and the
rotation equalities. In every triangle, equal opposite sides force equal
opposite angles, and strictly ordered opposite sides force the same strict
order of their opposite angles. A specified r_i>r_j is a valid ordering of
the own-triangle lengths sqrt(3)*r_i and sqrt(3)*r_j. Apply that ordering
whenever those length classes occur as opposite sides of a triangle.

Substitute (15) into three times (14) and these angle relations. An alleged
configuration therefore supplies a real solution of integer linear equations
and strict inequalities

    E*x=0, A*x>0.

A certificate consists of nonempty strict terms with positive integer
multipliers lambda and equality terms with signed nonzero integer
multipliers mu, satisfying coefficient by coefficient

    sum lambda_i*A_i + sum mu_j*E_j = 0.

It would force 0>0. The verifier rebuilds the matrices from the arrows,
phase order and explicitly stated radial comparisons; it does not trust
saved matrices or solver success flags. Unknown, repeated or out-of-range
indices, noninteger weights, nonpositive strict weights and nonzero residuals
are rejected. At least one strict term is mandatory.

For ordinary-distance certificates, strict convexity gives, for a<b<c<d,

    d_ac+d_bd > d_ab+d_cd,
    d_ac+d_bd > d_ad+d_bc.

These follow from the crossing diagonal intersection and strict triangle
inequalities. Distances are ordinary lengths, NOT squared lengths. Rotation
and selected-witness equalities are linear identifications of these lengths.
Zero quotient rows and positive-scalar-opposite quotient rows are therefore
contradictions. The six background metric certificates also use ordinary
strict triangle inequalities and positivity of nonzero lengths.

The separate `ExpandedEncoding` retains all individual chord variables and
obtains their rotation offsets by graph traversal instead of (15). It uses
whole-class relabeling instead of the folded distance quotient. All projected
rows are compared for the 18 new triangle cases, the 162 diamond cases,
the 230 seven-orbit residuals, and the 486 background cases: 896 cases in
total. Agreement is an implementation cross-check, not an independent proof
of the geometric interpretation.

## 8. The full phase certificate stream

`phase_certificates.bin.gz` is a losslessly compressed proof stream. After
decompression its format is:

- eight-byte magic `C3P7v1\r\n`;
- one five-byte little-endian record for EVERY phase case, in the precisely
  enumerated order of `radial_graphs.txt`, lexicographic phase permutations,
  and increasing binary codes on upward-arrow gain choices;
- each record is `(uint8 kind, uint16 a, uint16 b)`.

For kind 1, a and b encode the center pair and common-witness pair as
`first*21+second`. The checker reconstructs the complete common set; it
checks the two-circle cap or the required failure of crossing. For kind 2,
a is a zero Kalmanson-row index and b is 65535. For kind 3, a,b index the
two Kalmanson rows. The checker reduces their integer vectors, divides by
positive gcds, and requires exact negatives. For kind 4, a is the sequential
residual index and b is zero; the case must later have a matching angle
certificate. A residual is never treated as a realization or accepted proof
without its angle identity.

The total uncompressed size is exactly 8+5*7,718,400=38,592,008 bytes.
The compressed stream is 4,344,245 bytes (about 4.3 MB). There are no missing-record, unknown-kind,
truncated-input, wrong-index or trailing-byte exceptions to the acceptance
rule.

`phase_search.cpp` discovers the elementary records using a disjoint-set
quotient and hash-indexed sparse Kalmanson vectors. `phase_replay.cpp` does
NOT rediscover them. It uses an explicit equality graph with component
traversal and maps of integer coefficients. It independently regenerates
the full phase domain, checks each supplied record, and emits exactly the
230 residual keys for matching to the angle certificates.

## 9. Positive controls and falsification tests

### One transitive triangle really is possible

Let

    a=1,
    b=(-19-i*sqrt(3))/26,
    c=[-179+3*sqrt(105)-i*sqrt(3)*(19+45*sqrt(105))]/676.

Take these three representatives and their C3 rotations. The exact checker
proves that all nine points are distinct and convexly independent, and that

    a->b, a->c, b->c

all hold with zero gain. Their squared radii are

    r_a^2=1,
    r_b^2=7/13,
    r_c^2=(497+3*sqrt(105))/338.

Thus r_b<r_a<r_c, exactly the permitted order. Their complete maximum
multiplicity profile is [4,3,2] repeated three times; this is NOT a
counterexample to #97. The three source-orbit vertices have multiplicity
four and the six others do not.

No floating-point comparison establishes these facts. Coordinates are
stored as (x,sqrt(3)*y), where x,y belong to the exact field Q(h),
h=sqrt(105)/26>0. All field operations are rational coefficient operations;
signs of a+b*h use rational squaring. The specified hull order passes all
63 supporting-edge tests, and every distance class is computed exactly.
A separate rational vector also satisfies the corresponding folded angle
model, preventing false rejection of all transitive triangles.

### Previous valid configurations are retained

The exact common-supplier rectangle from the preceding packet obeys the
interlacing rule and passes its angle model. The exact irrational-angle
three-orbit directed cycle remains strictly convex and has multiplicity
three everywhere. Both controls recompute all distance classes and exact
supporting-edge determinants.

Regression tests include missing and duplicate diamond cases, perturbed
integer multipliers, zero strict weights, invalid binary headers and kinds,
truncated proof records, out-of-range inequalities and incorrect residual
indices. These tests supplement, rather than replace, mathematical review.

## 10. Replay, files and trust boundary

Python 3.10+ is sufficient for the static exact checks. Full replay additionally
requires GCC or Clang with C++17 support. No numerical solver or third-party Python package
is imported by the verifier.

    python verify.py --check
    python verify.py --check --full
    python -m unittest -v test_diamond_seven.py

The first command verifies all integer angle/metric certificates, regenerates
the pruned graph domain, checks controls and the compressed proof hash, and
compares the static report. It does NOT itself inspect every elementary
binary record. The `--full` command additionally replays all 7,718,400 phase
records, enumerates all 170,859,375 complete graph tuples using the separate
C++ oracle, matches the 230 residuals exactly and compares the expanded
encodings. Neither command interprets a search timeout as an exclusion.

For further defensive checks:

    python verify.py --check --full --sanitize
    python verify.py --check --full --regenerate-phase

The former uses undefined-behavior sanitization in the compiled checkers.
The latter rediscovers the elementary phase proof and requires identical
uncompressed bytes, not merely matching counts. Solver-based discovery of
the small angle certificates is separate and is not needed for replay. The
optional `discover.py` requires NumPy and SciPy; for example,
`python discover.py triangle --output /tmp/new-triangle-certificates.json`
rediscovers and exact-checks the 18 local triangle identities. It never
silently replaces the pinned proof artifacts.

`report.json` is generated by `python verify.py --write`. `validation.json`
records an actual completed final full/sanitized replay. The earlier completed
full replay, including byte-identical elementary-certificate regeneration,
is retained as `validation_initial.json`; it predates adding the independent
18-case triangle strengthening and has a different static report hash.
`PROVENANCE.md` separates copied background from new files. All 22 regression tests passed; their actual output is saved in
`test_results.txt`. A file-hash manifest accompanies the deliverable.

These are two in-session representations of finite encodings, not independent
external review, Lean formalization, or repository-wide CI. A full repository
checkout was not available here, and accepted status files were not edited.
This packet was not pushed by this session: the currently exposed GitHub
tools supported reads but supplied no commit/PR write action. The accompanying
addition-only patch is a repository handoff, not a claim of publication.

## 11. The still-missing global argument

The triangle and diamond theorems hold for any number of orbits, but a general
two-out graph need not contain either pattern. The seven-orbit finite result
does not establish an arbitrary-size forcing theorem. Eight or more orbits
remain outside the completed exhaustive domain.

A global completion of this C3 own-side route must either force one of the
local obstructions (possibly after adding genuinely forced arrows), prove
another obstruction for configurations avoiding them, or find a convex
realization outside the excluded finite domain. The fact that an abstract
graph survives some necessary predicates would not provide that realization.

For unrestricted Erdős #97, arbitrary radii and arbitrary convex polygons
remain additional issues. Nothing here reduces them to concentric C3 orbits.
The previous 66-point partial construction remains partial, not completed or
universally eliminated by this packet. The new local obstruction and the
seven-orbit closure are concrete progress, not a claimed final solution.
