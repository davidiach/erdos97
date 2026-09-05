# A right-angle obstruction and the seven-orbit own-side boundary

Date: 2026-09-05. Base: `b86a5737ed447613b140d0e5b85cb0dd3339f36c`.

Status: **REVIEW_PENDING_RESTRICTED_COMPUTER_ASSISTED_OBSTRUCTION**.

No general proof or counterexample to Erdős Problem #97 is claimed. This
packet does not update the accepted finite bound, status metadata, or historical
certificates. Both the paper reduction and the implementations require review.
No external independent review, formalization, or published novelty is claimed.

## 1. Result

Identify the plane with the complex numbers, and put

    omega = (-1+i sqrt(3))/2,
    T_i = {z_i, omega*z_i, omega^2*z_i},
    r_i = |z_i|, rho_i = sqrt(3)*r_i.

All representatives are nonzero, and distinct indices describe distinct orbits.
The term **own-side** refers specifically to the distance `rho_i` from a point
of `T_i`. Its two orbit-mates already supply two witnesses at that distance.
An own-side arrow `i -> j`, with rotation gain `g`, means

    |z_i - omega^g*z_j| = rho_i.

**Restricted theorem, review pending.** A nonempty strictly convex union of
at most seven distinct concentric equilateral-triangle orbits cannot give
every vertex four witnesses at its own-side radius.

Thus a construction relying on an own-side four-tie at EVERY orbit would
require at least eight orbits, or 24 vertices. This is NOT a 24-vertex lower
bound for arbitrary counterexamples: other radii of rich classes, arbitrary
21-gons, and non-C3 configurations are not covered. Systems with eight or more
orbits, including the 22-orbit/66-point partial construction, are not excluded.

The new geometric ingredient below applies to any number of orbits. The
finite enumeration is used only to prove that every at-most-seven-orbit
system encounters it or one of the preceding obstructions.

This packet continues the six-orbit investigation in draft PR #934, but is
self-contained: it freshly replays the five- and six-orbit cases, does not
import that draft, and does not depend on the pending convex-power-quotient
theorem in #931.

## 2. An own-side arrow is also a right-angle constraint

Let `a` be a source and `b` its selected witness, absorbing the rotation gain
into `b`. Set `c=omega*b` and `d=omega^2*b`: these are the OTHER two vertices
of the supplier triangle. For arbitrary `a,b`, the exact identity is

    2 (c-a) dot (d-a) = 3|a|^2 - |a-b|^2.                (1)

Indeed, `b+c+d=0`, and expanding the three squared distances gives

    |a-b|^2 + |a-c|^2 + |a-d|^2 = 3(|a|^2+|b|^2).

Also `|c-d|^2=3|b|^2`. Subtracting and applying the polarization identity
proves (1). Consequently, if `|a-b|^2=3|a|^2`, then

    (c-a) dot (d-a) = 0.

All points are distinct in a strictly convex configuration, so this is a
nondegenerate right angle `angle cad = pi/2`.

Equivalently, the source lies on the circle with diameter `cd`. This is the
geometric content of the outgoing constraint circle previously used in the
orbit66 construction, not an additional assumption about that circle.

`verify.py` checks (1) as a rational polynomial identity in four independent
variables after representing coordinates as `(x,sqrt(3)y)`. Evaluating small
floating residuals is not used to establish this identity.

## 3. Two right angles at an extreme vertex force interlacing

**General geometric lemma.** Let `p,a,b,c,d` be five distinct vertices of a
strictly convex polygon. If

    angle apb = angle cpd = pi/2,

then the segments `ab` and `cd` properly cross.

**Proof.** Because `p` is a strict hull vertex, all rays from `p` to the other
vertices lie in an angular interval of length strictly less than `pi`.
Their directions are distinct: three collinear vertices would make the
middle one non-extreme. Their order agrees with the boundary order starting
after `p`, as follows also by triangulating the convex polygon from `p`.

The endpoint rays of each right angle delimit a subinterval of length
`pi/2`. The two intervals cannot be disjoint: their combined span would be
at least `pi`. Neither can contain the other: they have the same length,
and equal endpoints would repeat a ray. Their endpoints must therefore
strictly alternate. The four corresponding vertices alternate on the polygon
boundary, which is exactly the criterion for `ab` and `cd` to cross. QED.

**Own-side corollary.** If one orbit has arrows to two different supplier
orbits, the sides OPPOSITE the two selected supplier vertices must cross.
For arrows `i -> j` of gain `g` and `i -> k` of gain `h`, the required
crossing is between

    {omega^(g+1)*z_j, omega^(g+2)*z_j}
    and
    {omega^(h+1)*z_k, omega^(h+2)*z_k}.                  (2)

Exponents are taken modulo 3. This is not the earlier shared-witness
crossing-bisector rule. In (2), the four endpoints are generally NOT selected
witnesses of the source. It supplies new information even when every pair
of selected rows has at most one common witness.

Two outgoing arrows at a single center are not themselves impossible. The
exact positive control in Section 9 attains them and satisfies (2). The
extreme-center assumption is essential: the origin and the four axis points
`(1,0),(0,1),(-1,0),(0,-1)` give two disjoint right-angle intervals and
noncrossing opposite chords, but the origin is not a hull vertex.

## 4. Reductions to oriented two-out graphs

A different orbit contributes at most one own-side witness to a strict hull
vertex. Suppose that `b` and `omega*b` were both witnesses of `a`. Their
perpendicular bisector is the line through the origin and `omega^2*b`, so
`a=t*omega^2*b` for real `t`. The equality becomes

    t^2+t+1 = 3t^2,  hence (t-1)(2t+1)=0.

The root `t=1` identifies the two orbits. The root `t=-1/2` makes `a` the
midpoint of `b` and `omega*b`, not an extreme point. Both are excluded.
Thus four own-side witnesses permit selection of two distinct supplier
orbits at every center.

For `s=|a|^2, t=|b|^2`, the existing cubic identity is

    product_(k=0,1,2) (|a-omega^k*b|^2-3s)
      = |a^3-b^3|^2 - 9s(s-t)^2.                       (3)

For completeness put `q=a*conj(b)` and `X=t-2s`. The product on the left
is `X^3-3stX-2Re(q^3)`. Expansion gives
`t^3-9st^2+18s^2t-8s^3-2Re(q^3)`, also the right side.
The earlier note is
[`docs/orbit66-exact-partial-construction.md`](../../docs/orbit66-exact-partial-construction.md).

Writing `w_i=z_i^3`, an arrow implies

    |w_i-w_j| = 3r_i |r_i^2-r_j^2|.                    (4)

Distinct equal-radius orbits cannot have an arrow: (4) would give `w_i=w_j`.
Arrows in both directions likewise force equal radii and then the same orbit.
Therefore the selected two-out graph is oriented, with no reciprocal pair.
For `m<5`, the necessary edge count `2m <= m(m-1)/2` is impossible.

### Increasing paths cannot have downward shortcuts

Suppose an undirected path `v_0,...,v_h`, with `h>=2`, has strictly increasing
radii. Put `R=r_(v_h)`. On each path edge the source radius is at most `R`,
and on at least one edge it is strictly smaller. Equation (4) gives

    sum_j |w_(v_(j+1))-w_(v_j)|
      < 3R sum_j (r_(v_(j+1))^2-r_(v_j)^2)
      = 3R(r_(v_h)^2-r_(v_0)^2).

A downward shortcut `v_h -> v_0` would have length equal to the last
quantity, contradicting the triangle inequality along the path. This uses
only actual cubed points, not convexity of their quotient.

Label orbits in nondecreasing radius order, breaking ties arbitrarily. A
selected edge never joins a tie, so any index-increasing path has strictly
increasing actual radii. The shortcut test is therefore valid with ties;
we do not assume that every pair of orbit radii is distinct.

## 5. Complete graph and angular coverage

The primary graph generator enumerates each two-subset of the other `m-1`
labels at each center, skipping a row only when it creates a reciprocal
pair with an already assigned row. It then checks the shortcut condition.
A separate graph mode enumerates ALL row tuples without partial reciprocal
pruning and uses a different, Floyd-closure shortcut implementation.

| Orbits | Raw row tuples in the second graph enumeration | Oriented graphs | Shortcut rejects | Remaining |
|---:|---:|---:|---:|---:|
| 5 | 7,776 | 24 | 24 | 0 |
| 6 | 1,000,000 | 14,490 | 14,486 | 4 |
| 7 | 170,859,375 | 4,590,360 | 4,587,605 | 2,755 |

The independently generated graph lists agree byte for byte. The seven-orbit
list includes proper closed subsystems; it does not silently prune them by
assuming acceptance of the six-orbit draft.

The origin is inside each equilateral orbit triangle. Two orbit vertices
cannot lie on the same ray: the nearer one would not be extreme. After a
common rotation and choice of representative in each orbit, take

    alpha_0=0,   0<alpha_i<2pi/3 for i!=0.

There are `(m-1)!` sector orders, and the actual `3m` boundary positions are
that order repeated in three sectors. This describes continuous angular
possibilities by order; it is not a grid or an equal-angle assumption.

For a selected arrow, let `u=r_j/r_i` and let `theta` be the angle to the
selected rotated witness. Its equality gives

    cos(theta) = u/2 - 1/u.

This expression is strictly increasing, equaling `-1/2` at `u=1`.
A downward arrow therefore selects the unique rotation in the open angular
sector `(2pi/3,4pi/3)`. An upward arrow selects one of the two other rotations.
In a fixed sector order, a later target has downward gain 1 and upward gains
0 or 2; an earlier target has downward gain 2 and upward gains 0 or 1.
Every actual configuration has one of these choices. Some enumerated choices
are impossible for additional continuous reasons; over-including them is safe.

The 2,755 graphs yield 1,983,600 graph/angular-order pairs and a total of
118,368,000 gain assignments. No rational-angle restriction is imposed.

## 6. The older metric filters used before the new lemma

All distance variables in this section are ORDINARY Euclidean lengths.
Selected spokes within an orbit have common length `rho_i=sqrt(3)*r_i`.
Unselected pairs remain separate variables in the primary implementation.
Not imposing all additional rotational equalities enlarges the relaxation;
it cannot exclude a realizable case.

**Two-circle and crossing-bisector constraints.** Two distinct centers cannot
share three selected witnesses. When they share two, both centers lie on
their perpendicular bisector. Strict convexity puts them on opposite sides
of the witness line: otherwise the nearer center lies inside the triangle
of the farther center and the witnesses. Thus the center and witness chords
must cross. These are necessary conditions for every selected system.

**Kalmanson inequalities.** For boundary positions `a<b<c<d`, splitting the
crossing diagonals at their intersection and using strict triangle inequalities
gives

    d_ac+d_bd-d_ab-d_cd > 0,
    d_ac+d_bd-d_ad-d_bc > 0.                            (5)

Cancel through the selected-distance equivalence classes. A zero row is
impossible. A two-term remainder `d_x-d_y>0` gives a strict comparison.
The orbit order also supplies weak comparisons `rho_i<=rho_(i+1)`.
A directed comparison cycle is impossible if it contains a strict edge;
every detected cycle does, since the weak radial edges alone are acyclic.

If a row of (5) involves only orbit radii, write it as `sum c_i*rho_i`, where
`sum c_i=0`. It equals

    sum_(h=1,...,m-1) (sum_(i=h,...,m-1) c_i) * (rho_h-rho_(h-1)).

If all suffix coefficients are nonpositive, the expression is nonpositive,
contradicting (5). This remains valid for tied radii.

The direct orbit labels in the primary code are sound because the same-orbit
triangles equate their three side lengths, and no selected cross-pair can
be owned by two different sources without a reciprocal orbit pair. The
separate phase oracle instead reconstructs all these classes from individual
selected spokes, using a disjoint-set representation.

## 7. The 138 survivors expose precisely the new information

With the new right-angle test deliberately deferred, the complete seven-orbit
case partition is:

| Result | Gain assignments |
|---|---:|
| Two-circle / crossing-bisector rejection | 106,265,912 |
| Zero / radial-dominated Kalmanson rejection | 8,287,570 |
| Kalmanson comparison-cycle rejection | 3,814,380 |
| Survive those filters | **138** |
| Total | **118,368,000** |

All 138 are stored in `frontier.json`. They are abstract selected systems,
NOT coordinates or counterexamples. `verify.py` independently reconstructs
each expanded system and its equality graph, verifies that the older filters
indeed leave it alive, then supplies its explicit noncrossing opposite sides.
Every one is rejected by Sections 2-3. `report.json` pins the hashes of the
138 records and the 138 certificates.

For example, the first stored case has radius-labelled row masks

    [18,96,65,17,6,12,48],

i.e. targets

    0->{1,4}, 1->{5,6}, 2->{0,6}, 3->{0,4},
    4->{1,2}, 5->{2,3}, 6->{4,5},

and sector order `[0,1,6,2,3,4,5]`. Its gains are

    [2,0, 0,2, 2,1, 2,2, 2,2, 2,2, 1,1].

The stored rejecting center identifies two opposite supplier sides that do
not alternate. The exact identities force both to subtend right angles at
that source, contradicting the general interlacing lemma. The checker
calculates the endpoint indices rather than relying on this prose example.

## 8. Full fresh replay with the new filter first

Running the right-angle test before metric work changes the partition, not
the covered domain or conclusion:

| Result | Gain assignments |
|---|---:|
| Right-angle noninterlacing | 95,720,400 |
| Two-circle / crossing-bisector | 21,373,460 |
| Zero / radial-dominated Kalmanson | 959,898 |
| Kalmanson comparison cycle | 314,242 |
| Survivors | **0** |

The separate `oracle.cpp` also exhausts all 118,368,000 cases. It constructs
complete right-angle-admissible gain tuples without the primary pair-prefix
pruning, checks every physical center pair instead of reducing them by C3,
builds distance classes by spoke unions, and detects cycles by topological
deletion rather than recursive DFS. It matches the right-angle and pair
counts exactly and finds 1,274,140 metric rejections, with zero survivors.

Both implementations were written in this research session. A different
implementation is not external independent mathematical review. The numeric
sector indices used by the oracle encode order relative to the 120-degree
sectors, never sampled angle values.

## 9. Exact positive and hypothesis controls

Take the three orbits generated by

    a=1, b=(-5+i sqrt(3))/7, c=(-5-i sqrt(3))/7.

The checker certifies all nine points as strict hull vertices using rational
supporting-edge determinants. At `a` the selected witnesses `b,c` are both
at distance `sqrt(3)`. Their opposite triangle sides really do cross, and
the two right angles are verified by exact dot products.

The full maximum-multiplicity distribution is three vertices with multiplicity
four and six with multiplicity two. This is a valid TWO-ARROW LOCAL control,
not a full bad system or a counterexample. It prevents the false shortcut
"a strict hull vertex can never have two own-side arrows."

The interior-origin/axis-points control in Section 3 separately records why
the extreme-center hypothesis cannot be dropped. These finite controls
check implementations and assumptions; the universal lemma is proved in prose.

## 10. Reproduction and evidence boundaries

From this directory, using Python 3.10+ and a C++17 compiler:

```sh
python verify.py --check
python -m unittest -v test_seven_orbits.py
python replay.py --quick --check
python replay.py --full --jobs 4 --check
python replay.py --full --deferred --jobs 4 --check
```

The first command verifies the stored 138 cases and exact controls; it does
NOT regenerate the full search. Quick replay regenerates the graph lists,
the small cases, and three seven-orbit slices. Full replay freshly runs both
complete phase implementations. Adding `--deferred` also regenerates the
entire pre-right-angle frontier and compares every stored record.

`--sanitize` builds with undefined-behavior sanitization. `--workdir` retains
fresh execution records and requires an empty directory. `--collect DIR`
only validates already completed execution records; it is deliberately
labelled differently from regeneration. `--write` regenerates `report.json`
from those records. Every claimed exhaustive phase result requires complete
shard coverage and zero survivors; timeouts, nonzero exits, malformed reports,
overlaps, missing shards, and positive survivors are not accepted as exclusions.

`validation.json` records the commands and source hashes used for delivery.
Standalone checks are not repository-wide CI. This environment lacks a full
repository checkout; the attempted GitHub clone failed DNS resolution, and
Ruff is not installed. Repository-wide `make verify-fast`, `make verify-artifacts`,
and Ruff were not run here. Hosted CI and review remain separate gates.

## 11. What remains

The all-size right-angle interlacing lemma is now available as a necessary
filter beyond seven orbits. No argument here forces an obstruction in every
larger system, removes C3 symmetry, or replaces arbitrary rich radii by
own-side radii. The unrestricted long-radius problem remains unclosed in this
packet. The repository's accepted general finite-case bound is unchanged.
