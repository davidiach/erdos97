# All own-side C3 four-witness systems through six orbits are obstructed

Date: 2026-09-05. Base: `b86a5737ed447613b140d0e5b85cb0dd3339f36c`.

Status: **EXACT_FINITE_CERTIFICATE / PAPER_REDUCTION_REVIEW_PENDING**.
No general proof or counterexample to Erdos Problem #97 is claimed. This
isolated packet does not change accepted bounds, global status metadata, or
activate a reviewed status transition. No external independent review or
published novelty is claimed.

## 1. Result and exact scope

Let `omega=(-1+i sqrt(3))/2`. Consider a strictly convex union of distinct
nonzero concentric equilateral-triangle orbits

    T_i = {z_i, omega*z_i, omega^2*z_i},  i=0,...,m-1.

Write `r_i=|z_i|`, `s_i=r_i^2`, and `w_i=z_i^3`. An own-side arrow `i -> j`
means that some rotated point of `T_j` is at distance `sqrt(3)*r_i` from
`z_i`. The two orbit-mates already give two witnesses at this radius.

**Computer-assisted obstruction, review pending.** For `m <= 6`, it is
impossible for every orbit to have four witnesses at its own triangle-side
radius. Thus an own-side construction of a counterexample requires at least
seven orbits, hence at least 21 vertices.

This covers ALL phase choices, ALL boundary orders, ALL selected two-target
orbit graphs, and ALL orbit radii, including equal radii where permitted.
There is no rational-angle, local-side-length, alternating-boundary,
reciprocity, or common-radius assumption.

It does NOT assert that every strictly convex union of six triangle orbits
has a vertex good at every radius. Four-fold ties at OTHER radii, including
all-cross row shapes, are outside the hypothesis. Arbitrary 18-gons and
systems with seven or more orbits are also outside this result.

The original six-label target

    0 -> {4,5}; 1 -> {4,5}; 2 -> {0,1};
    3 -> {0,1}; 4 -> {2,3}; 5 -> {2,3}

is excluded with every radial ordering, not just `r_0<...<r_5`. In fact no
larger strictly convex orbit system can contain this graph as an own-side
subgraph: retain its six orbits and apply the obstruction. This corollary
does not say the motif is forced in every larger system.

## 2. Cubic identity and the radius-path obstruction

The identity from
[`orbit66-exact-partial-construction.md`](../../docs/orbit66-exact-partial-construction.md)
is

    product_{k=0,1,2} (|a-omega^k b|^2 - 3s)
      = |a^3-b^3|^2 - 9s(s-t)^2,  s=|a|^2, t=|b|^2.       (1)

For a direct derivation put `q=a*conj(b)`, `X=t-2s`, and
`U=Re(q^3)`. The three factors have product `X^3-3stX-2U`.
Expanding gives `t^3-9st^2+18s^2t-8s^3-2U`, exactly the right side of (1).

Consequently an own-side arrow implies

    |w_i-w_j| = 3 r_i |s_i-s_j|.                          (2)

An edge between distinct equal-radius orbits is impossible: (2) gives
`w_i=w_j`, identifying the orbits. Opposite arrows are impossible too:
applying (2) in both directions either identifies the orbits or forces
`r_i=r_j`, with the same consequence. This excludes opposite arrows even
when their selected rotations are different.

**No downward shortcut.** If the underlying undirected arrow graph has a
path `v_0,...,v_h`, `h>=2`, with strictly increasing radii, it cannot also
have the arrow `v_h -> v_0`.

To prove this, let `R=r_(v_h)`. The source radius on each path edge is at
most its larger endpoint radius and hence at most `R`. At least one is
strictly less than `R`, because the path has at least two edges. Equation
(2) gives

    sum_j |w_(v_(j+1))-w_(v_j)|
       < 3R sum_j (s_(v_(j+1))-s_(v_j))
       = 3R(s_(v_h)-s_(v_0)).                            (3)

The proposed downward arrow would have length equal to the final quantity,
contradicting the ordinary triangle inequality along the cubed path.
No convexity of the cube quotient is used. In particular this proof does
not depend on the review-pending convex-power-quotient theorem in #931.

## 3. Why the graph enumeration covers every own-side system

One different orbit can supply at most one own-side witness in strictly
convex position. Suppose two of its vertices are `b,omega*b`. Their
perpendicular bisector is the line through `omega^2*b` and the origin, so
the source has the form `a=t*omega^2*b`, with real `t`. The own-side equality
is

    t^2+t+1 = 3t^2,  or  (t-1)(2t+1)=0.

For `t=1` the orbits coincide. For `t=-1/2`, the source is the midpoint of
`b` and `omega*b`, not an extreme point. Both are excluded.

Thus four own-side witnesses at every orbit allow selection of exactly two
DISTINCT target orbits per source. By Section 2 the selected graph is
oriented: it has no reciprocal pair. For `m<5`, the edge count
`2m <= m(m-1)/2` is impossible.

For `m=5` or `6`, label orbits in nondecreasing radius order. Equal-radius
orbits are allowed: break ties arbitrarily. No selected edge can join tied
orbits. Therefore any index-increasing path in the underlying graph has
strictly increasing ACTUAL radii along every edge. Both the no-shortcut
prune and the later upward/downward classification remain valid with ties.

`all_systems.py` enumerates every choice of two targets among the other
`m-1` labels, pruning only reciprocal pairs. It then supplies an explicit
increasing path and downward edge for each radius-path rejection.

| Orbits | Oriented two-out graphs | No-shortcut rejections | Remaining |
|---:|---:|---:|---:|
| 5 | 24 | 24 | 0 |
| 6 | 14,490 | 14,486 | 4 |

The four remaining radius-labelled graphs are, in lexicographic order:

    G0: {3,4}, {0,5}, {0,5}, {1,2}, {1,2}, {3,4}
    G1: {3,5}, {0,5}, {0,5}, {1,2}, {1,2}, {3,4}
    G2: {4,5}, {0,5}, {0,5}, {1,2}, {1,2}, {3,4}
    G3: {4,5}, {4,5}, {0,1}, {0,1}, {2,3}, {2,3}

These are abstract necessary-condition survivors, not coordinates.

## 4. Exhausting continuous angular choices by finite rotation gains

The origin is in the interior of each equilateral orbit's triangle, hence
inside the whole convex hull. Distinct orbits cannot have representatives
on the same ray modulo `2pi/3`: the smaller would lie inside the larger
triangle, or equal radii would identify them.

Rotate the whole configuration and choose representatives so that

    alpha_0=0,  0<alpha_i<2pi/3 for i!=0.

This is only a similarity and independent relabelling within each orbit.
Their angular order is `(0, permutation(1,...,5))`, giving 120 possibilities.
The 18 actual boundary positions are this order repeated in three sectors.
No equally spaced angles are assumed.

For an arrow, write `u=r_target/r_source` and let `theta` be its actual
source-to-witness angle. Expanding its distance equality gives

    cos(theta) = u/2 - 1/u.

The right side is strictly increasing in `u`, and equals `-1/2` at `u=1`.
Thus a downward arrow requires `2pi/3<theta<4pi/3` modulo `2pi`, whereas
an upward arrow requires the complementary open 240-degree arc.

With representatives in one 120-degree sector and distinct angular order:

* A downward arrow has exactly one possible rotation gain: 1 if the target
  is later in the sector order, and 2 if it is earlier.
* An upward arrow has exactly two possible gains: 0 and respectively 2 or
  1 in those same two cases.

Each surviving graph has four upward arrows. Hence each has exactly
`120*2^4=1920` necessary phase/order cases. This finite reduction covers
irrational as well as rational angles; the integer sector indices in the
C++ checker encode ordering, NOT angle values or a grid search.

## 5. Exact convex-distance certificates close every case

Each expanded physical vertex selects its two orbit-mates and the two
rotated target vertices. Only the following necessary facts are used.

**Crossing-bisector condition.** If two centers share two witnesses, the
center chord and the witness chord must cross. Both centers lie on the
perpendicular bisector. Two centers on the same side of the witness line
would place the nearer one inside the triangle formed by the witnesses
and the farther center, contradicting extremality. Thus they are on
opposite sides, and the chords cross at the witness midpoint.

**Strict ordinary-distance Kalmanson inequalities.** For boundary positions
`a<b<c<d`, splitting the crossing diagonals at their intersection and using
strict triangle inequalities yields

    d_ac+d_bd-d_ab-d_cd > 0,
    d_ac+d_bd-d_ad-d_bc > 0.                              (4)

Here `d` is ordinary distance, NOT squared distance. Selected spokes within
one row are equated. Reduce (4) through this equality relation. A zero
coefficient vector is a contradiction; two opposite coefficient vectors
sum to the contradiction `0>0`.

| Graph | Phase/order cases | Crossing certificates | Two-inequality certificates | Survivors |
|---|---:|---:|---:|---:|
| G0 | 1,920 | 1,600 | 320 | 0 |
| G1 | 1,920 | 1,888 | 32 | 0 |
| G2 | 1,920 | 1,888 | 32 | 0 |
| G3 | 1,920 | 1,712 | 208 | 0 |
| Total | 7,680 | 7,088 | 592 | 0 |

Every case has an explicit certificate. The Python finder uses a
disjoint-set structure; replay reconstructs distance equalities instead
as connected components of an equality graph. Every certificate is checked,
not just its census. `--certificates` exports the complete collection;
`all_systems_report.json` pins its SHA256 and the separate graph audit hash.

For example, original-target G3 case 417 has angle order
`(0,2,1,4,3,5)` and gains `(0,0,0,2,2,1,2,2,2,1,2,2)`, in source/target row
order. The second inequalities of (4) on quadruples `(0,1,8,12)` and
`(0,2,3,8)` reduce respectively to

    d_0,8 - d_0,3 > 0,   d_0,3 - d_0,8 > 0.

Their sum is impossible. Subscripts here are physical boundary positions,
not orbit labels.

Together Sections 2-5 prove the claimed restricted obstruction, conditional
on the auditable finite enumeration and certificate implementations. The
paper reduction and source code remain review pending, not Lean-formalized
or externally reviewed.

## 6. Separate C++ full-enumeration check

`oracle.cpp --all-systems` starts from ALL `6^5=7776` five-orbit row choices
and ALL `10^6=1000000` six-orbit row choices. Unlike the Python generator,
it checks reciprocal edges only after a whole graph is formed. It uses
increasing-path Floyd closure rather than predecessor-path discovery,
bitsets for witnesses, and whole-class relabelling rather than a DSU.

It retains the same four graphs. It then checks all 720 angular orders,
without fixing orbit 0 first, covering 46,080 gain/order cases. Results:

    crossing obstructions       42,528
    Kalmanson inverse pairs      3,552
    survivors                        0

The sixfold counts match the Python reduction. This is a separately
implemented complete finite replay, not external independent mathematical
review. Both implementations use the mathematical lemmas proved above.

The original doubled-cycle target also has a separate radial-order audit:
all 720 total radius orders reduce to 48 orders in two graph-automorphism
classes, and its 3,840 reduced phase/order cases all close. The default
C++ mode checks all 48 retained radius orders without this automorphism
quotient; `--all-angle-orders` checks 552,960 target-specific cases with
zero survivors. Those larger counts contain symmetry-redundant coverage,
not additional orbit sizes.

## 7. Controls, tests, and reproduction

The exact nine-point C3 seed from the orbit66 construction passes the
crossing and metric filters with three equidistant witnesses at every
vertex. Its coordinates, convexity, all distance multiplicities, and
selected equalities are checked with rational arithmetic in
`(x,sqrt(3)*y)` coordinates. This is a genuine geometrically realizable
positive control, not a four-witness counterexample.

Tests cover graph completeness, every discarded graph's path certificate,
rotation-gain coverage, selected-row covariance, all phase certificates,
tampered certificates, malformed inputs, and the positive control. Rational
samples also calibrate (1); they are not its general polynomial proof.

From this directory:

```sh
python all_systems.py --check
python all_systems.py --certificates /tmp/all_own_side_six_certificates.json
python certificate.py --check
python -m unittest -v test_six_orbit_radial.py test_all_own_side_six.py
c++ -O3 -std=c++17 -Wall -Wextra -Wpedantic oracle.cpp -o /tmp/c3-oracle
/tmp/c3-oracle --all-systems
/tmp/c3-oracle --all-angle-orders
```

To regenerate reports, run the respective Python commands with `--write`.
The main checks use only the Python standard library and a C++17 compiler.
`validation.json` records completed local checks and source hashes.

Twenty focused tests and the undefined-behavior-sanitized all-systems C++
replay passed. Repository-wide fast/artifact suites and Ruff were not run
locally: this environment has no full checkout, GitHub DNS access failed,
and Ruff is unavailable. Those are separate CI/review gates.

## 8. What remains

The proposed 18-point doubled-cycle route is closed, and the result extends
to every own-side construction with at most six orbits. It does not complete
or obstruct the 22-orbit, 66-point partial construction, reduce its missing
witness deficit, or exclude seven-orbit or larger own-side systems.

The main next construction choices are seven or more orbits, different
rich-radius row shapes, or nonsymmetric configurations. None is asserted
to be realizable. No finite-case bound for arbitrary convex polygons is
promoted by this packet, and no unrestricted solution is claimed.
