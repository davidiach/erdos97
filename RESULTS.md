# Results Ledger

This file is the compact results ledger for what this repository currently
claims, what it has only tested numerically, and what remains open. For the
long-form canonical synthesis and claim reconciliation, read
`docs/canonical-synthesis.md`.

Official/global status: falsifiable/open. This repository claims no general
proof and no counterexample.

Strongest local finite-case artifact: the selected-witness method rules out
`n <= 8` in a repo-local, machine-checked finite-case sense. External
independent review is still recommended before paper-style or public
theorem-style claims.

## Certified Results

### Lemma: pairwise circle-intersection cap

Status: `LEMMA`.

In any true counterexample, for distinct centers `a,b`,
`|S_a cap S_b| <= 2`. Otherwise two distinct circles would share at least
three points.

### Lemma: incidence counting gives n >= 7

Status: proved.

The directed 4-out incidence pattern and the pairwise cap imply no
counterexample can have `n <= 6`; the convexity-of-indegree count gives
`n >= 7`.

### Lemma: edge-sensitive rich-support counting wall

Status: proved.

For any choice of one same-radius support `R_i` at each center, not necessarily
of size four,

```text
sum_i binom(|R_i|, 2) <= n(n - 2).
```

Indeed, a fixed unordered witness pair `{a,b}` can occur in at most two
supports, because all centers using both witnesses lie on the perpendicular
bisector of `ab`. If `{a,b}` is a hull edge, its perpendicular bisector already
meets the polygon boundary at the edge midpoint and cannot contain two further
boundary vertices, so that edge pair has capacity one. There are `n` hull-edge
witness pairs and `binom(n,2)-n` non-edge witness pairs, giving
`n + 2*(binom(n,2)-n) = n(n-2)` by double-counting.

Consequently, if every center has a rich class of size at least `k`, then the
edge-sensitive pair count gives `n >= binom(k, 2) + 2`. The
support-saturation obstruction rules out the equality wall for `k >= 4`, so
the all-centers size-five subcase is impossible for `n <= 12`; the global pair
budget alone gives at least seven exact-four centers in a hypothetical 4-bad
nonagon, at least five in a hypothetical 4-bad decagon, and at least three in a
hypothetical 4-bad hendecagon. The rich-support checker now also records a
nonagon profile-deficiency refinement excluding the remaining raw
non-exact-four profiles by label-deficiency residues. The localized per-label
support-pair cap gives a second route to the same nonagon conclusion: each
witness label can occur in at most four chosen supports, so any hypothetical
4-bad nonagon is already forced into the all-exact-four,
selected-indegree-four support case by counting alone. See
`docs/rich-support-counting-lemma.md`,
`docs/support-saturation-obstruction.md`, and
`docs/localized-rich-support-counting.md`.
The all-five-rich `n=12` equality wall also has an independent determinant
obstruction: saturation would force a `12 x 12` column Gram matrix with first
row `[5,1,2,2,2,2,2,2,2,2,2,1]` and determinant
`2,592,000 = 720^2 * 5`, which is not a square. This rechecks the same boundary
already closed by support saturation; it is not a proof of the full `n=12`
case. See `docs/n12-rich-support-determinant-obstruction.md` and
`scripts/check_n12_rich_support_determinant.py`.

### Lemma: crossing-bisector and sharpened count

Status: `EXACT_OBSTRUCTION`.

If two selected witness rows share exactly two labels, the source chord is the
perpendicular bisector of the common-witness chord and the two chords cross at
the common-witness midpoint. Adjacent row-pairs therefore have intersection
size at most `1`, improving the incidence count to `n >= 8`.

This gives a short independent exclusion of `n <= 7`. The Fano enumeration is
still retained because it is structurally useful and reproducible.

For a hypothetical `n=8` counterexample, equality holds throughout: witness
indegrees are all 4, adjacent row-pairs meet in exactly one selected witness,
nonadjacent row-pairs meet in exactly two, and the common-witness map is a
crossing permutation of the 20 octagon diagonals.

### Lemma: adjacent closest-pair nonagon barrier

Status: `LEMMA` / structural necessary condition.

An endpoint of a globally closest pair cannot use the closest-pair distance as
its four-rich radius. Combining this radius barrier with the adjacent-row
crossing-bisector cap gives a conditional small nonagon obstruction: if an
all-bad polygon has a globally closest pair that is a polygon side, then it
has at least ten vertices.

Equivalently, any hypothetical all-bad nonagon must have every globally closest
pair realized by a diagonal rather than by a side. This is not an `n=9` proof:
closest pairs in strictly convex polygons need not be adjacent. See
`docs/closest-pair-radius-barrier.md` and
`scripts/check_adjacent_closest_pair_nonagon_barrier.py`.

### Restricted symmetric two-orbit reductions

Status: `EXACT_OBSTRUCTION` for the stated symmetry classes only.

For a full `C_k`-symmetric strictly convex configuration with `k >= 3` and at
most two noncentral rotation orbits, the per-circle cap forces any bad row to
split its four witnesses as `2+2` across the two orbits. Pair symmetry forces
the orbit phases to be same-ray or half-step modulo `2*pi/k`; same-ray makes
the smaller orbit non-vertex, and half-step reduces to the alternating
two-radius regular family already killed by the exact checker. The `k=3`
hexagon boundary is handled separately by the factor
`3 - (1 + b^2 - b) = (2 - b)(b + 1)` on `1/2 < b < 2`.
A direct gear-equation certificate gives the same half-step obstruction by
forcing one expression to be both at least and strictly below
`4 sin^2(pi/(2k))`.

The same note records the local radius-ratio vertex condition
`R_min >= R_max*cos(pi/k)` and the exterior-center obstruction for at most
three concentric circles. These are narrow symmetry-class obstructions only:
they do not cover `k=2`, mirror-only symmetry, partial orbits, three or more
noncentral orbits, four or more exterior-center concentric circles, `n=9`, or
Erdos Problem #97. See `docs/symmetric-two-orbit-reduction.md` and
`scripts/check_two_orbit_radius_propagation.py`.

### Lemma: minimal-counterexample critical tie

Status: proved.

In a counterexample with the minimum possible number of vertices, every vertex
`x` is essential to some remaining vertex `y`: deleting `x` makes `y` good, so
`x` lies in the unique distance class of size exactly 4 at `y`. This is a
structural condition on minimal counterexamples, not a contradiction by itself.

### Lemma: selected-path self-edge obstruction

Status: proved local criterion.

Selected rows identify spoke distances and therefore generate equivalence
classes of unordered vertex-pair distances. If a local row core contains both
a selected-distance equality path from pair `p` to pair `q` and a valid
vertex-circle strict inequality `p > q`, then no strictly convex realization
can satisfy that core: the equality path gives `D(p) = D(q)`, while the strict
edge gives `D(p) > D(q)`.

This is only a reusable final-contradiction lemma. It does not prove that every
`n=9` frontier assignment, every minimal counterexample, or every convex
polygon must contain such a core. The current `n=9` T01-T09 packet audit
remains review-pending. See `docs/n9-vertex-circle-self-edge-criterion.md`.

### Lemma: directed strict-cycle obstruction

Status: proved local criterion.

Selected rows identify spoke distances and therefore generate equivalence
classes of unordered vertex-pair distances. If a local row core contains a
cyclic list of valid vertex-circle strict inequalities `p_i > q_i`, and
selected-distance equality paths from each `q_i` to the next `p_{i+1}`, then
no strictly convex realization can satisfy that core: the inequalities combine
after quotienting into a directed cycle

```text
D(p_0) > D(p_1) > ... > D(p_{k-1}) > D(p_0).
```

This is only a reusable final-contradiction lemma. It does not prove that every
`n=9` frontier assignment, every minimal counterexample, or every convex
polygon must contain such a core. The current `n=9` T10-T12 packet audit
remains review-pending. See `docs/n9-vertex-circle-strict-cycle-criterion.md`.

### Lemma: strict quotient-graph obstruction

Status: proved local criterion.

For any local selected-row core with certified vertex-circle strict edges,
quotient unordered pair distances by the selected-row equalities. A strictly
convex realization can have neither a loop nor a directed cycle in this strict
quotient graph, because each strict edge strictly decreases the corresponding
real distance value. The same local criterion applies to a supplied rich
same-radius class after quotienting all center-witness spokes in that class.

This is the common abstraction behind the selected-path self-edge and directed
strict-cycle obstruction lemmas. It is only a final local obstruction test:
acyclicity is not evidence of realizability, and this does not prove that
every counterexample must contain such an obstruction. See
`docs/n9-vertex-circle-quotient-soundness-audit.md`.

The bridge-facing corollary is the finite closed-descent version: a nonempty
finite set of quotient classes cannot have every class strictly descending to
a class in the same set, possibly itself. Following those descent edges would
eventually produce a directed strict cycle. The helper
`validate_closed_descent_region` checks this certificate shape for supplied
strict quotient graphs, including exact-four selected-row and rich-class
quotient graphs.

### Theorem: selected-witness incidence rules out n <= 7

Status: proved and reproducible.

The incidence count rules out `n <= 6`. For `n=7`, equality forces all
indegrees to be 4 and every pair of selected 4-sets to intersect in exactly
2 points. The complements `T_i = V \ S_i` form Fano lines with `i in T_i`.

The exact enumerator checks all 30 labelled Fano planes and 720 pointed
equality families, reducing them to 54 cyclic-dihedral classes. In every
family, the common-witness chord map has cycle type `7+7+7`, so the required
radical-axis perpendicularity constraints contain odd cycles. This obstructs
all `n=7` selected-witness equality patterns. See
`docs/n7-fano-enumeration.md`.

### Machine-checked finite-case artifact: selected-witness incidence rules out n = 8

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT` in repo-local sense. External
review is still recommended before paper-style or public theorem claims. The
individual survivor-class kills are `EXACT_OBSTRUCTION_PER_SURVIVOR_CLASS`;
the aggregate `n=8` exclusion is the machine-checked finite-case artifact.

The incidence-completeness checker derives `n=8` indegree regularity from the
column-pair cap, exhaustively enumerates all selected-witness systems satisfying
the necessary incidence filters, and reduces the survivors to 15 canonical
classes up to simultaneous relabeling.

The exact obstruction checker then kills all 15 classes. The cyclic-order
noncrossing filter kills 1 class. The remaining 14 classes are killed by exact
perpendicular-bisector algebra, full equal-distance algebra where needed, or
strict-convexity failure. No floating-point equality or numerical search is
used. See `docs/n8-incidence-enumeration.md`,
`docs/n8-exact-survivors.md`, `data/incidence/n8_incidence_completeness.json`,
and `certificates/n8_exact_analysis.json`.

The independent SymPy-free recheck in `docs/n8-independent-obstruction.md`
uses separate rational-arithmetic code to reproduce the cyclic-order counts
for all 15 classes and independently kill 11 classes. It intentionally leaves
the Groebner-dependent classes `3`, `4`, `5`, and `14` to the original exact
survivor checker, so it is an audit-strengthening cross-check rather than an
independent public proof.

A focused class `14` audit in `docs/n8-class14-certificate.md` rebuilds only
that class's `PB+ED` polynomial system, compares the stored Groebner basis,
derives the four real branches, and verifies exact strict-interior failure on
each branch. This isolates the most delicate survivor-class obstruction for
review; it is not a new public theorem claim.

A companion residual audit in `docs/n8-residual-certificates.md` isolates
classes `3`, `4`, and `5`: duplicate vertices, collinearity, and the class `5`
Groebner-y2 contradiction after the recorded substitutions. It is another
repo-local review aid, not a status upgrade.

An independent SMT cross-check in `docs/n8-survivors-smt-cross-check.md`
(`scripts/check_n8_survivors_smt.py`) covers all 15 classes uniformly with a
different decision procedure: z3 nonlinear real arithmetic finds, for every
class, that the equal-distance + perpendicular-bisector constraints together
with strict convexity (label order) are UNSAT, so no class has a strictly
convex octagon realization. This is a second source for both the cyclic-order
class and all fourteen PB+ED classes -- including the four Groebner-dependent
ones (`3`, `4`, `5`, `14`) the SymPy-free recheck skips -- using neither
Groebner bases nor the cyclic-order combinatorics. `EXACT_OBSTRUCTION` (SMT),
repo-local cross-check pending external review; it strengthens but does not
replace the existing artifacts. See `data/certificates/n8_survivors_smt.json`.

### Proof-note draft: geometric exclusion of n <= 8

Status: proof-note draft; independent review requested.

A short geometric note in `docs/n8-geometric-proof.md` gives an independent
human-readable route to the `n <= 8` exclusion: a base-apex lemma bounds the
number of isosceles triangles by `n(n-2)`, badness gives at least `6n`, and the
saturated octagon case forces an equilateral octagon whose length-3 diagonals
require at least four exterior turns of size `2*pi/3`, contradicting total
turn `2*pi`.

This note does not alter the global status of Erdos Problem #97 and does not
replace the existing machine-checked `n=8` finite-case artifact.

### Minimal fragile-cover bridge

Status: `LEMMA` / partial bridge theorem.

Every minimal counterexample admits a partial fragile-cover witness system:
for each deleted vertex `x`, minimality produces a remaining center `y` whose
unique exact 4-tie contains `x`; retaining these exact 4-ties gives a cover of
all vertices by fragile rows. The rows satisfy the two-circle cap and the
radical-axis crossing rule for two-overlaps, and they must extend to a full
selected-witness incidence system because every vertex in the original
counterexample is bad. The optional full-extension checker rejects the single
block-6 fragile cover but still permits two disjoint blocks, so this is a
necessary structural bridge only, not a contradiction and not the open
ear-orderable bridge. See `docs/minimal-fragile-cover-bridge.md`.

The stored block-6 vertex-circle full-extension audit adds a stronger geometric
gate for that same two-block negative control in the natural cyclic order: all
full selected-row extensions are closed by vertex-circle quotient self-edge or
strict-cycle obstructions. This rejects one abstract family that passes the
fragile-cover hypergraph and full-extension checks, but it is still not an
all-order/all-extension bridge proof. See
`docs/block6-fragile-vertex-circle-extension-audit.md`.

The follow-up crossing-order sample stores two deterministic terminal-extension
windows from that audit. Across `200` sampled full extensions, the crossing
enumerator finds `796` crossing-compatible cyclic orders, and every sampled
order is killed by a vertex-circle quotient self-edge. This is only a bounded
diagnostic sample, not all-extension or all-order closure; see
`data/certificates/block6_terminal_crossing_vertex_circle_sample.json`.

The stronger crossing-order full sweep stores the complete terminal-extension
window generated by that natural-order two-block audit. Across `105,978`
terminal full extensions, the crossing enumerator finds `385,517`
crossing-compatible cyclic orders; `384,318` are killed by a quotient
self-edge and `1,199` by a strict cycle, with no vertex-circle-clean order
found. This still does not cover selected-row systems outside the natural-order
terminal generator, so it is not all-extension/all-order block-6 closure and
not a fragile-bridge proof; see
`data/certificates/block6_terminal_crossing_vertex_circle_full_sweep.json`.

The fixed-order block-6 probe then checks the natural order plus three
non-natural cyclic orders. Each non-natural order has a legal terminal
selected-row extension outside the natural-order generator, but all four
fixed-order searches close under order-specific vertex-circle pruning. The
probe is fixed-order diagnostic evidence only, not all-order closure; see
`data/certificates/block6_fixed_order_vertex_circle_probe.json`.

The follow-up block-preserving shuffle-order sweep checks all `462` normalized
cyclic orders that preserve internal order inside the two six-label blocks
while shuffling the blocks. Every order-specific full-extension search closes
under vertex-circle quotient pruning, with `276,230` self-edge prunes and
`316,519` strict-cycle prunes. The sweep records `458` orders with a legal
terminal selected-row extension and `4` with no terminal extension; `457` first
terminal extensions fail the natural-order crossing rule, so they are outside
the natural-order terminal generator. This is still a bounded fixed-order-family
diagnostic only, not all-order closure; see
`data/certificates/block6_shuffle_order_vertex_circle_sweep.json`.

The companion reversed-second-block shuffle sweep checks the `462` normalized
orders that preserve `1,2,3,4,5` in the first block and `11,10,9,8,7,6` in the
second. This records a negative control for the current vertex-circle gate:
`446` orders close, but `16` orders have a vertex-circle-clean full selected-row
extension before any stronger metric-order filter is applied. The artifact
stores those 16 clean abstract row systems as fixed-order escape targets. They
are not Euclidean realizations, not counterexamples, and not evidence of
all-order closure; see
`data/certificates/block6_reversed_block_shuffle_vertex_circle_escape.json`.

A follow-up fixed-order Kalmanson packet closes exactly those 16 clean
assignment/order pairs by quotient-cone certificates. The certificates use
`394` strict Kalmanson rows in total, with total weight `16850`; every combined
coefficient vector vanishes after selected-distance quotienting. This is exact
for the stored fixed rows and fixed cyclic orders only, not an all-order
obstruction or fragile-bridge proof; see
`data/certificates/block6_reversed_block_clean_kalmanson.json`.

The companion two-stage crosswalk
`data/certificates/block6_reversed_block_two_stage_closure.json` checks that
the two packets line up on the same 16 clean indices and that the combined
bounded family count is complete: `446 + 16 = 462`. This is still only the
reversed-second-block fixed-order family.

The first-block-forward two-orientation crosswalk
`data/certificates/block6_forward_block_two_orientation_closure.json` then
joins the original forward-second-block sweep with that reversed-block packet.
It verifies `462 + 462 = 924` closed normalized shuffle orders when the first
block orientation is fixed forward and the second block is either forward or
reversed. This is a convenience cross-artifact diagnostic only; it does not
cover first-block-reversed orientations, arbitrary cyclic orders, all
selected-row systems, the fragile bridge, or Erdos Problem #97.

The oriented-block reversal crosswalk
`data/certificates/block6_oriented_block_reversal_closure.json` adds the two
first-block-reversed orientation families by explicit cyclic reversal duality.
It verifies that the generated `forward-forward` orders reverse bijectively to
the `reversed-reversed` orders, and `forward-reversed` orders reverse
bijectively to the `reversed-forward` orders. This gives `1848` closed
oriented-block shuffle orders by transfer from the first-block-forward packet.
The scope remains bounded to block-preserving oriented shuffles; it is not
arbitrary cyclic-order closure, all selected-row closure, the fragile bridge,
or Erdos Problem #97.

The block-6 fifth/sixth-row survivor diagnostics are exact bounded negative
controls for overly local bridge claims. They show that all `166` clean
fifth-row states have a clean legal sixth-row continuation, every unordered
added-center pair supports clean six-row states, and the low-support branch
continues through many clean seventh and eighth rows before only `12` clean
seven-row states become terminal at the eighth-row test. This is natural-order
proof-mining bookkeeping only, not a fragile-bridge proof or realizability
claim; see `docs/block6-fragile-sixth-row-survivor-catalog.md` and
`scripts/check_block6_fragile_sixth_row_survivors.py`.

### Bootstrap-core bridge

Status: `LEMMA` / bridge fork.

For the full rich distance-class family, rich-triple closure rank is exactly
the ear-orderable selected-witness bridge: rank at most 3 is equivalent to an
ear-orderable selection. If the rank is greater than 3, any inclusion-minimal
generating core has deletion closures and private halos that make it a
radius-blocker with a weighted cyclic outside-pair capacity ledger. This is a
necessary bridge target only; it is not a proof of Erdos Problem #97 and not a
counterexample. See `docs/bootstrap-core-bridge.md` and
`scripts/check_bootstrap_core_bridge.py`.

The checked bootstrap-core crosswalk applies the same singleton-rich
bookkeeping to current fixed-row frontier motifs. All eight audited cyclic-order
cases have rank greater than 3, and none violates the weighted private-halo
capacity ledger. This is negative diagnostic information only, not evidence of
realizability; see `docs/bootstrap-core-crosswalk.md`,
`scripts/check_bootstrap_core_crosswalk.py`, and
`data/certificates/bootstrap_core_crosswalk.json`.

The full `n=9` exact-four radius-blocker packet fixes the natural cyclic order
and blocker `{0,1,2,3}`, then quantifies over every exact four-row compatible
with that blocker. After the row-pair, witness-pair, indegree, and two-overlap
crossing filters, it finds `90` incidence survivors; all `90` are killed by
vertex-circle replay (`70` self-edges and `20` strict cycles). This is finite
packet evidence only, not an `n=9` theorem, not a bridge proof, and not a
counterexample. See `docs/n9-full-radius-blocker-vertex-circle-packet.md`,
`scripts/check_n9_full_radius_blocker_vertex_circle_packet.py`, and
`data/certificates/n9_full_radius_blocker_vertex_circle_packet.json`.

The natural-order `n=9` radius-blocker shape sweep widens the same exact-four
packet to all `10` cyclic-dihedral four-blocker representatives. Their orbit
sizes sum to all `126` labelled four-vertex blockers in the fixed natural
order. After the same filters, the sweep finds `1,358` incidence survivors;
all are killed by vertex-circle replay (`1,164` self-edges and `194` strict
cycles). This is still finite packet evidence only, not an `n=9` theorem, not
a bridge proof, and not a counterexample. See
`docs/n9-radius-blocker-shape-sweep.md`,
`scripts/check_n9_radius_blocker_shape_sweep.py`, and
`data/certificates/n9_radius_blocker_shape_sweep.json`.

The order-reduction crosswalk for that sweep records the relabelling
`order[i] -> i`, which sends any supplied cyclic order and four-blocker subset
to a natural-order labelled four-blocker already covered by the shape sweep.
This closes the cyclic-order placement gap only for the exact-four packet
semantics; it does not handle richer classes and does not prove the bridge.
See `docs/n9-radius-blocker-order-reduction.md`,
`scripts/check_n9_radius_blocker_order_reduction_crosswalk.py`, and
`data/certificates/n9_radius_blocker_order_reduction_crosswalk.json`.

A bounded richer-class projection pilot starts from one checked `n=9`
`{0,1,2,3}` obstruction example and enlarges every center row to one synthetic
size-five rich class while preserving blocker compatibility. Expanding each
larger class to all exact four-subsets gives projected row-option counts
`[5,5,5,5,5,5,5,5,5]`, with raw upper bound `1,953,125`; after the same
filters, the one incidence survivor is killed by a vertex-circle self-edge.
This is a forgetful selected-row projection only, not full rich-class quotient
replay, not an `n=9` theorem, not a bridge proof, and not a counterexample.
See `docs/n9-radius-blocker-rich-projection-pilot.md`,
`scripts/check_n9_radius_blocker_rich_projection_pilot.py`, and
`data/certificates/n9_radius_blocker_rich_projection_pilot.json`.

A full rich-class quotient replay now checks the same synthetic size-five
family without choosing selected four-subsets. It unions all center-to-witness
distances in each rich class and generates nested-chord inequalities from each
full class. The resulting quotient has `225` strict edges and is obstructed by
`193` self-edge conflicts. This is one finite rich-class family only, not an
`n=9` theorem, not a bridge proof, and not a counterexample. See
`docs/n9-radius-blocker-rich-quotient-pilot.md`,
`scripts/check_n9_radius_blocker_rich_quotient_pilot.py`, and
`data/certificates/n9_radius_blocker_rich_quotient_pilot.json`.

A generated rich-class quotient sweep widens that full replay to `20`
synthetic size-five packets, one stored self-edge example and one stored
strict-cycle example for each of the `10` natural-order four-blocker shapes.
The sweep checks `180` size-five rich classes and `4,500` strict edges; all
`20` packets are quotient-obstructed by self-edges, with `3,533` total
self-edge conflicts. This remains generated finite packet evidence only, not
arbitrary rich-class classification, not an `n=9` theorem, not a bridge proof,
and not a counterexample. See
`docs/n9-radius-blocker-rich-quotient-sweep.md`,
`scripts/check_n9_radius_blocker_rich_quotient_sweep.py`, and
`data/certificates/n9_radius_blocker_rich_quotient_sweep.json`.

A bounded rich-extension neighborhood sweep varies the added labels in that
generated baseline. It enumerates every radius-blocker-preserving
Hamming-distance `1` or `2` replacement around the `20` baseline packets,
checking `5,996` variants, `53,964` size-five rich classes, and `1,349,100`
strict edges. All `5,996` variants are quotient-obstructed by self-edges, with
`1,017,368` total self-edge conflicts. This remains finite neighborhood
evidence only, not the full extension-product catalogue, not arbitrary
rich-class classification, not an `n=9` theorem, not a bridge proof, and not a
counterexample. See
`docs/n9-radius-blocker-rich-extension-neighborhood.md`,
`scripts/check_n9_radius_blocker_rich_extension_neighborhood.py`, and
`data/certificates/n9_radius_blocker_rich_extension_neighborhood.json`.

A one-packet rich-extension product pilot then exhausts the first maximum-size
source packet in the generated family:
`n9_full_exact_four_radius_blocker_shape_U0135_natural_order:self_edge:0`.
It checks all `196,608` radius-blocker-preserving size-five extension variants
for that packet, `1,769,472` size-five rich classes, and `44,236,800` strict
edges. All variants are quotient-obstructed by self-edges, with `33,895,908`
total self-edge conflicts. This remains finite packet evidence only, not the
full product over all `20` generated packets, not arbitrary rich-class
classification, not an `n=9` theorem, not a bridge proof, and not a
counterexample. See
`docs/n9-radius-blocker-rich-extension-product-pilot.md`,
`scripts/check_n9_radius_blocker_rich_extension_product_pilot.py`, and
`data/certificates/n9_radius_blocker_rich_extension_product_pilot.json`.

An all-packet generated rich-extension product sweep now exhausts the full
extension product over all `20` generated source packets. It checks
`2,899,968` radius-blocker-preserving size-five variants, `26,099,712`
size-five rich classes, and `652,492,800` strict edges. All variants are
quotient-obstructed by self-edges, with `467,149,054` total self-edge
conflicts. This remains finite generated-packet evidence only, not arbitrary
rich-class classification, not an `n=9` theorem, not a bridge proof, and not a
counterexample. See
`docs/n9-radius-blocker-rich-extension-product-sweep.md`,
`scripts/check_n9_radius_blocker_rich_extension_product_sweep.py`, and
`data/certificates/n9_radius_blocker_rich_extension_product_sweep.json`.

A generator-independent all-five-rich support obstruction now checks the
subcase where every center of a nonagon has some rich distance class of size at
least five. The checker enumerates the full `56^9 =
5,416,169,448,144,896` size-five support assignment space by exact
backtracking under only the two-circle row-pair cap and radical-axis crossing
for two-overlaps. It visits `136` assignment nodes, reaches maximum depth `2`,
and leaves `0` complete assignments. This is a repo-local support subcase
only: it does not enumerate mixed exact-four/size-five catalogues, does not
prove `n=9`, does not prove the adaptive radius-blocker bridge, and is not a
counterexample. See
`docs/n9-all-five-rich-support-obstruction.md`,
`scripts/check_n9_all_five_rich_support_obstruction.py`, and
`data/certificates/n9_all_five_rich_support_obstruction.json`.

A follow-up mixed rich-support reduction checks the four/five support
catalogue at every center. It enumerates `126` support options per center,
applies the two-circle row-pair cap, radical-axis crossing for two-overlaps,
and witness-pair capacity, then searches the full `126^9 =
8,004,512,848,309,157,376` raw assignment space by exact backtracking. The
search visits `108,018` nodes and leaves `184` complete assignments, all with
`0` size-five supports. Repo-locally, this reduces any `n=9` selected-witness
counterexample to the all-exact-four frontier before vertex-circle replay. It
does not independently prove the review-pending exact-four exhaustive checker,
does not prove `n=9`, and is not a counterexample. See
`docs/n9-mixed-rich-support-reduction.md`,
`scripts/check_n9_mixed_rich_support_reduction.py`, and
`data/certificates/n9_mixed_rich_support_reduction.json`.

A companion crosswalk now checks that those `184` terminal mixed-support
assignments are exactly the stored `184` pre-vertex-circle exact-four frontier
assignments as a labelled row set. The two generators order six assignments
differently, but their sorted row-set SHA-256 digest agrees:
`dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55`. The
matched stored frontier statuses are `158` self-edges and `26` strict cycles.
This is support-to-frontier bookkeeping only: it does not prove the
review-pending exact-four exhaustive checker, prove `n=9`, or give a
counterexample. See `docs/n9-mixed-rich-frontier-crosswalk.md`,
`scripts/check_n9_mixed_rich_frontier_crosswalk.py`, and
`data/certificates/n9_mixed_rich_frontier_crosswalk.json`.

The companion bootstrap / vertex-circle overlay joins the two tight
non-ear-orderable `n=9` crosswalk rows to the review-pending strict-cycle
certificate chain by selected-row signature. Both land on the same `T12/F16`
strict-cycle template, with capacity margins `8` and `6`, but the strict-cycle
local row cores are not contained in the bootstrap core. This is proof-mining
diagnostic information only; see `docs/bootstrap-vertex-circle-overlay.md`,
`scripts/check_bootstrap_vertex_circle_overlay.py`, and
`data/certificates/bootstrap_vertex_circle_overlay.json`.

The follow-up bootstrap/T12 forcing-target ledger records what the overlay
would still need a bridge lemma to force. Source `81` needs equality-connector
row centers `3` and `8` and has no direct private-pair hit; source `151` needs
row centers `5,6,7,8` and has two direct private-pair hits. This is still an
open proof-mining target, not a proof that the missing rows are forced; see
`docs/bootstrap-t12-forcing-targets.md`,
`scripts/check_bootstrap_t12_forcing_targets.py`, and
`data/certificates/bootstrap_t12_forcing_targets.json`.

The row-pressure refinement splits those six missing row centers by the kind
of bridge ingredient they would need: two are already exposed in a deletion
closure, three need one outside label while the row center remains private,
and one needs an outside pair with two private-pair ledger hits. This is still
diagnostic bookkeeping only; see `docs/bootstrap-t12-row-pressure.md`,
`scripts/check_bootstrap_t12_row_pressure.py`, and
`data/certificates/bootstrap_t12_row_pressure.json`.

The closure-exposed subpacket isolates the two deletion-closure-exposed rows
from that ledger. Rows `81:3` and `151:7` share core witnesses `[0,1,4]` and
are exposed by the deletion closure for core vertex `2`; only `81:3` has its
full selected row contained in the closure. This is a smaller proof-mining
target only; see `docs/bootstrap-t12-closure-exposed.md`,
`scripts/check_bootstrap_t12_closure_exposed.py`, and
`data/certificates/bootstrap_t12_closure_exposed.json`.

The one-outside-label subpacket isolates the three singleton-support rows
from the same ledger: `81:8`, `151:5`, and `151:8`. Each row has two
bootstrap-core witnesses, two singleton outside supports, and a row center
private in every deletion closure. In each row, exactly one support is private
in all deletion halos and one is internal to the deletion closure for core
vertex `2`. This is still diagnostic bookkeeping only; see
`docs/bootstrap-t12-one-outside.md`,
`scripts/check_bootstrap_t12_one_outside.py`, and
`data/certificates/bootstrap_t12_one_outside.json`.

The outside-pair subpacket isolates the last row-pressure row, `151:6`. This
equality-connector row has one bootstrap-core witness, three activation-ready
outside-pair supports, and row center `6` private in every deletion closure.
All three support pairs are private in every deletion halo; two supports,
`[3,8]` and `[5,8]`, also hit the private-pair ledger, while `[3,5]` is
private-halo-only. This is still diagnostic bookkeeping only; see
`docs/bootstrap-t12-outside-pair.md`,
`scripts/check_bootstrap_t12_outside_pair.py`, and
`data/certificates/bootstrap_t12_outside_pair.json`.

The activation-support requirement ledger refines those T12 row gaps by
separating relation requirements from unproved row forcing. Across the six
missing row centers it records five equality-connector pair requirements and
two strict-edge endpoint-set requirements. Two connector requirements are
already satisfied at the bootstrap-core witness level, three requirements have
stored support options that supply the needed witnesses, and two strict-edge
requirements remain hard. This is still diagnostic bookkeeping only; see
`docs/bootstrap-t12-activation-requirements.md`,
`scripts/check_bootstrap_t12_activation_requirements.py`, and
`data/certificates/bootstrap_t12_activation_requirements.json`.

The bridge-target map joins the T12 row-pressure, support, and activation
ledgers into six explicit next-lemma targets. It records two closure-exposed
rows, three one-outside-label rows, and one outside-pair row; under its
exclusive relation-state classification, two requirements are bootstrap-core
sufficient, two are support-sufficient, one connector pair remains open, and
two strict endpoint requirements remain hard. This is still diagnostic
bookkeeping only; see
`docs/bootstrap-t12-bridge-target-map.md`,
`scripts/check_bootstrap_t12_bridge_target_map.py`, and
`data/certificates/bootstrap_t12_bridge_target_map.json`.

The hard strict-endpoint subpacket isolates the two hard strict requirements
from that map. Both occur in source `151`: row `7` is closure-exposed but still
misses endpoint `6`, and row `8` has singleton supports that each supply only
one of the outside strict endpoints `5` and `7`. This is still diagnostic
bookkeeping only; see `docs/bootstrap-t12-hard-strict-endpoints.md`,
`scripts/check_bootstrap_t12_hard_strict_endpoints.py`, and
`data/certificates/bootstrap_t12_hard_strict_endpoints.json`.

The open connector-pair subpacket isolates the remaining open connector
requirement from that map. Source `151`, row `5` needs connector pair `[7,8]`;
the deletion closure for core vertex `2` and the singleton supports each see
only one connector endpoint. This is still diagnostic bookkeeping only; see
`docs/bootstrap-t12-open-connector-pair.md`,
`scripts/check_bootstrap_t12_open_connector_pair.py`, and
`data/certificates/bootstrap_t12_open_connector_pair.json`.

The relation-sufficient row subpacket isolates the three rows from that map
whose connector requirements are already bootstrap-core sufficient or
support-sufficient: `81:3`, `81:8`, and `151:6`. It keeps the remaining
row/rich-class forcing target explicit rather than promoting relation evidence
to a bridge theorem. This is still diagnostic bookkeeping only; see
`docs/bootstrap-t12-relation-sufficient-rows.md`,
`scripts/check_bootstrap_t12_relation_sufficient_rows.py`, and
`data/certificates/bootstrap_t12_relation_sufficient_rows.json`.

The focused `81:3` closure-target packet extracts the cleanest current
subcase from those ledgers. Source `81` row `3` is the unique
relation-sufficient target whose full fixed selected row is contained in a
deletion closure, with closure labels `[0,1,3,4,6]`; it is also the one-step
T12 equality connector `[1,3]=[0,3]`. The packet records the exact remaining
gap as fixed full-row closure evidence versus genuine rich-class forcing. This
is still diagnostic bookkeeping only; see
`docs/bootstrap-t12-81-3-closure-target.md`,
`scripts/check_bootstrap_t12_81_3_closure_target.py`, and
`data/certificates/bootstrap_t12_81_3_closure_target.json`.

The follow-up `81:3` rich-triple connector contract records the weaker local
conditional actually needed by the T12 equality connector. Any genuine rich
class at center `3` containing witnesses `0` and `1` gives `[1,3]=[0,3]`; the
full fixed row `[0,1,4,6]` is not required for that connector. The packet also
pins the connector-avoiding escape: activation through the fixed witness set
must use `[0,4,6]` or `[1,4,6]`, so label `6` must be available before center
`3`. This remains diagnostic bookkeeping only, not a proof that the rich class
or row is forced; see
`docs/bootstrap-t12-81-3-rich-triple-contract.md`,
`scripts/check_bootstrap_t12_81_3_rich_triple_contract.py`, and
`data/certificates/bootstrap_t12_81_3_rich_triple_contract.json`.

The order-resolved `81:3` fixed-row escape audit checks the current
singleton-rich closure order for that same seed. In the fixed selected-row
model, `[0,1,4]` enables only center `3`, with trigger `[0,1,4]`; label `6`
enters later through center `6` with trigger `[0,3,4]`, depending on center
`3`. Thus the fixed packet does not realize the connector-avoiding escape. It
also records that, if the source-`81` center-`6` row `[0,3,4,7]` is preserved
as genuine, same-center disjointness blocks any additional center-`6` class
from containing the seed triple `[0,1,4]`. This is still diagnostic
bookkeeping only, not a proof about genuine rich classes; see
`docs/bootstrap-t12-81-3-order-escape.md`,
`scripts/check_bootstrap_t12_81_3_order_escape.py`, and
`data/certificates/bootstrap_t12_81_3_order_escape.json`.

The relaxed `81:3` escape-candidate scan then drops preservation of the
source-`81` center-`3` and center-`6` rows while preserving the other seven
rows. It enumerates the `40` one-class replacement candidates for pre-`3`
label-`6` supply followed by connector-avoiding center-`3` activation. All
`40` fail the basic row-pair, witness-pair, or crossing filters. This remains
a fixed-row-neighborhood diagnostic only, not a proof of `n=9` or the
bootstrap bridge; see `docs/bootstrap-t12-81-3-escape-candidates.md`,
`scripts/check_bootstrap_t12_81_3_escape_candidates.py`, and
`data/certificates/bootstrap_t12_81_3_escape_candidates.json`.

The one-row-drop follow-up relaxes that fixed-row-neighborhood guard one step
further. For each of the seven source-`81` rows outside centers `3` and `6`,
it drops that one row and enumerates all `70` replacement 4-sets while keeping
the same center-`6` supply and center-`3` connector-avoiding replacement
space. All `19600` candidates fail the same basic row-pair, witness-pair, or
crossing filters. This is still a finite diagnostic only, not a proof of
genuine rich-class order, `n=9`, or the bootstrap bridge; see
`docs/bootstrap-t12-81-3-escape-one-row-drop.md`,
`scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py`, and
`data/certificates/bootstrap_t12_81_3_escape_one_row_drop.json`.

The two-row-drop follow-up repeats the same finite stress test while allowing
any pair of the seven source-`81` rows outside centers `3` and `6` to move.
For each dropped pair it checks all `70 * 70` replacement-row choices, for a
total of `4116000` candidates. All candidates fail the same basic row-pair,
witness-pair, or crossing filters. This is still a finite diagnostic only, not
a proof of genuine rich-class order, `n=9`, or the bootstrap bridge; see
`docs/bootstrap-t12-81-3-escape-two-row-drop.md`,
`scripts/check_bootstrap_t12_81_3_escape_two_row_drop.py`, and
`data/certificates/bootstrap_t12_81_3_escape_two_row_drop.json`.

The full-neighborhood CSP then lets all seven source-`81` rows outside centers
`3` and `6` move at once, while keeping the same one-class replacement spaces
at centers `3` and `6`. The implicit space has `329417200000000` assignments.
Exact backtracking with the basic row-pair, witness-pair, and crossing filters
visits `1177` search nodes and finds no complete assignment. This subsumes the
one- and two-row fixed-neighborhood stress tests, but remains a diagnostic
only: it is not a proof of genuine rich-class order, `n=9`, or the bootstrap
bridge; see `docs/bootstrap-t12-81-3-escape-full-neighborhood.md`,
`scripts/check_bootstrap_t12_81_3_escape_full_neighborhood.py`, and
`data/certificates/bootstrap_t12_81_3_escape_full_neighborhood.json`.

The auxiliary-rich-class CSP relaxes the selected-row role of those two escape
classes. The center-`6` supply class and center-`3` connector class may exist
as auxiliary rich classes, while the selected rows at centers `3` and `6` may
be either those classes or disjoint classes. All seven other selected rows are
arbitrary. The implicit selected-row space has `1317668800000000` assignments;
exact backtracking visits `1287` nodes and finds no complete assignment under
the row-pair, witness-pair, crossing, and same-center disjointness filters.
This remains a finite diagnostic only, not a proof of genuine rich-class
order, `n=9`, or the bootstrap bridge; see
`docs/bootstrap-t12-81-3-escape-auxiliary-csp.md`,
`scripts/check_bootstrap_t12_81_3_escape_auxiliary_csp.py`, and
`data/certificates/bootstrap_t12_81_3_escape_auxiliary_csp.json`.

The trigger-family uniqueness audit checks the two specified auxiliary trigger
families from that CSP. All five center-`6` supply classes containing
`[0,1,4]` pairwise intersect, and all eight center-`3` connector-avoiding
classes using label `6` pairwise intersect. Thus same-center distance-class
disjointness permits at most one class from each specified trigger family, and
for any fixed auxiliary trigger the selected row at that center has exactly
two equal-or-disjoint 4-set options: the trigger itself or the unique disjoint
complement. This is only a proof-mining audit of those trigger families; it
does not prove trigger-class existence, row forcing, `n=9`, or the bootstrap
bridge. See `docs/bootstrap-t12-81-3-trigger-uniqueness.md`,
`scripts/check_bootstrap_t12_81_3_trigger_uniqueness.py`, and
`data/certificates/bootstrap_t12_81_3_trigger_uniqueness.json`.

The rich-support auxiliary CSP then allows those two auxiliary objects to be
larger rich distance-class supports. It enumerates 31 center-`6` supply
supports containing `[0,1,4]` and 30 center-`3` connector-avoiding supports
using label `6`, for 930 fixed auxiliary support pairs. Selected rows at
centers `3` and `6` may be any 4-subset of the auxiliary support or any
disjoint 4-set; the other seven selected rows are arbitrary. The implicit
selected-row space has `996734092900000000` assignments, and exact
backtracking visits `2169` nodes with no complete assignment under the
row-pair, witness-pair, crossing, and same-center disjointness filters. This
is still a finite diagnostic only, not a proof of support existence, row
forcing, `n=9`, or the bootstrap bridge. See
`docs/bootstrap-t12-81-3-escape-rich-support-csp.md`,
`scripts/check_bootstrap_t12_81_3_escape_rich_support_csp.py`, and
`data/certificates/bootstrap_t12_81_3_escape_rich_support_csp.json`.

The first-supply-chain prefix CSP then lets the first pre-`3` activation after
seed `[0,1,4]` occur at any non-seed, non-`3` center. Among `4650`
first-step/support-prefix pairs, exact backtracking leaves exactly three
basic-filter prefix survivors, all starting at center `8`, and no immediate
center-`6` label-`6` supply extension. The second-supply-chain prefix
crosswalk then lets one additional non-target, non-supply center activate
from closure `[0,1,4,8]`; it leaves one center-`8` then center-`2` prefix,
with support `[1,3,4,8]`, and no immediate center-`6` label-`6` supply
extension for that prefix. The second-step-chain continuation CSP then tests
distinct intermediate centers from `{2,5,7}` after those center-`8`
prefixes before one center-`6` label-`6` supply support. It prunes `4112`
support prefixes, tests `9528` label-`6` supply catalogues, searches `58` of
them, and finds no surviving chain. These remain bounded proof-mining
diagnostics, not support existence, row forcing, `n=9`, or the bootstrap
bridge. See `docs/bootstrap-t12-81-3-first-supply-chains.md`,
`scripts/check_bootstrap_t12_81_3_first_supply_chains.py`,
`data/certificates/bootstrap_t12_81_3_first_supply_chains.json`, and
`docs/bootstrap-t12-81-3-second-supply-chains.md`,
`scripts/check_bootstrap_t12_81_3_second_supply_chains.py`,
`data/certificates/bootstrap_t12_81_3_second_supply_chains.json`, plus
`docs/bootstrap-t12-81-3-second-step-chains.md`,
`scripts/check_bootstrap_t12_81_3_second_step_chains.py`,
`data/certificates/bootstrap_t12_81_3_second_step_chains.json`. The companion
post-`8` supply-chain accounting packet records the raw denominator for the
same bounded chain model: `3,918,164,268` support catalogues, `58` initially
compatible catalogues, `223` selected-search nodes, and no selected-row
survivor. See `docs/bootstrap-t12-81-3-post8-supply-chains.md`,
`scripts/check_bootstrap_t12_81_3_post8_supply_chains.py`, and
`data/certificates/bootstrap_t12_81_3_post8_supply_chains.json`.
The ordered chain-closure CSP then tests every eligible sequential activation
from closure `[0,1,4]`, holding center `3` back and requiring each new support
to contain at least three currently closed labels. It checks `5916` candidate
extensions, leaves four non-supply prefix survivors, and finds zero
center-`6` supply-chain survivors. This closes only the sequential
support-chain model, not repeated or multiple rich supports and not any
genuine rich-class/minimality bridge. See
`docs/bootstrap-t12-81-3-chain-closure-csp.md`,
`scripts/check_bootstrap_t12_81_3_chain_closure_csp.py`, and
`data/certificates/bootstrap_t12_81_3_chain_closure_csp.json`.
A one-layer repeated-support audit then attaches one disjoint same-center
support to each already activated prefix center in those four stored
prefixes. The five repeated-support catalogues produce `464` center-`6`
supply-extension attempts; only one is initially compatible, and it still has
zero selected-row completions. This closes only that one repeated-support
layer, not arbitrary multiple-support catalogues or a rich-class/minimality
bridge. See
`docs/bootstrap-t12-81-3-repeated-support-catalogue-audit.md`,
`scripts/check_bootstrap_t12_81_3_repeated_support_catalogue_audit.py`, and
`data/certificates/bootstrap_t12_81_3_repeated_support_catalogue_audit.json`.
A two-repeated-support audit deduplicates the next catalogue layer. The only
unique two-support catalogue comes from prefix `1`, with repeated supports at
centers `2` and `8`; it is initially incompatible, and all `118` center-`6`
supply-extension attempts are initially incompatible as well. This closes only
that two-repeated-support layer, not arbitrary multiple-support catalogues or
a rich-class/minimality bridge. See
`docs/bootstrap-t12-81-3-two-repeated-support-catalogue-audit.md`,
`scripts/check_bootstrap_t12_81_3_two_repeated_support_catalogue_audit.py`,
and
`data/certificates/bootstrap_t12_81_3_two_repeated_support_catalogue_audit.json`.
A repeated-support saturation audit then enumerates all further
same-center-disjoint repeated supports in the same stored-prefix model. It
records four base catalogues, five one-repeated-support catalogues, one
deduplicated two-repeated-support catalogue, and no three-repeated-support
catalogue. This saturates only that stored-prefix repeated-support model, not
richer catalogues, new activation provenance, support existence, row forcing,
`n=9`, or the bridge. See
`docs/bootstrap-t12-81-3-repeated-support-saturation-audit.md`,
`scripts/check_bootstrap_t12_81_3_repeated_support_saturation_audit.py`, and
`data/certificates/bootstrap_t12_81_3_repeated_support_saturation_audit.json`.

The source-`81` row-`8` singleton-support audit probes the other
relation-sufficient source-`81` row. Center `8` has bootstrap-core witnesses
`[0,2]` and singleton support labels `5` and `6`; the audit enumerates the
nine selected rows containing `[0,2]` and one of those supports. In the fixed
source-`81` neighborhood, only the original row `[0,2,5,6]` survives the
row-pair, witness-pair, and crossing filters. In the one-row-drop relaxation,
all eight survivors are trivial original-neighborhood survivors: row `8`
remains `[0,2,5,6]`, and the dropped row remains its original source-`81` row.
This is still a finite diagnostic only, not a proof of singleton support
existence, row forcing, `n=9`, or the bootstrap bridge. See
`docs/bootstrap-t12-81-8-singleton-support-audit.md`,
`scripts/check_bootstrap_t12_81_8_singleton_support_audit.py`, and
`data/certificates/bootstrap_t12_81_8_singleton_support_audit.json`.

The source-`81` row-`8` singleton-support two-row-drop follow-up lets any two
non-target source-`81` rows move while row `8` ranges over the same nine
activation rows. It checks `1,234,800` candidates and leaves `28` survivors,
all of them trivial original-neighborhood survivors: row `8` is still
`[0,2,5,6]`, and both dropped rows are still their original source-`81` rows.
This is still a finite diagnostic only, not a proof of singleton support
existence, row forcing, `n=9`, or the bootstrap bridge. See
`docs/bootstrap-t12-81-8-singleton-support-two-row-drop.md`,
`scripts/check_bootstrap_t12_81_8_singleton_support_two_row_drop.py`, and
`data/certificates/bootstrap_t12_81_8_singleton_support_two_row_drop.json`.

The source-`81` row-`8` full-neighborhood vertex-circle packet is a
negative-control boundary for that audit. It fixes row `8` to the same nine
activation rows but lets every other center choose an arbitrary selected
4-set. Basic incidence/crossing filters leave `34` complete assignments,
including `27` with non-original row `8`; vertex-circle quotient replay kills
all `34` by `27` self-edges and `7` strict cycles. This is still a finite
diagnostic only, not a proof of singleton support existence, row forcing,
`n=9`, or the bootstrap bridge. See
`docs/bootstrap-t12-81-8-full-neighborhood-vertex-circle.md`,
`scripts/check_bootstrap_t12_81_8_full_neighborhood_vertex_circle.py`, and
`data/certificates/bootstrap_t12_81_8_full_neighborhood_vertex_circle.json`.

The source-`151` row-`6` outside-pair audit probes the remaining
relation-sufficient row target. Center `6` has bootstrap-core witness `[0]`
and outside support pairs `[3,5]`, `[3,8]`, and `[5,8]`; the audit enumerates
the thirteen selected rows containing `[0]` and one of those support pairs. In
the fixed source-`151` neighborhood, only the original row `[0,3,5,8]`
survives the row-pair, witness-pair, and crossing filters. In the one-row-drop
relaxation, all eight survivors are trivial original-neighborhood survivors:
row `6` remains `[0,3,5,8]`, and the dropped row remains its original
source-`151` row. This is still a finite diagnostic only, not a proof of
outside-pair support existence, row forcing, `n=9`, or the bootstrap bridge.
See `docs/bootstrap-t12-151-6-outside-pair-audit.md`,
`scripts/check_bootstrap_t12_151_6_outside_pair_audit.py`, and
`data/certificates/bootstrap_t12_151_6_outside_pair_audit.json`.

The source-`151` row-`6` outside-pair two-row-drop follow-up extends the same
audit by allowing any unordered pair of non-target rows to move arbitrarily.
It checks `1,783,600` candidate states, leaves `28` survivors, and all
survivors are the trivial original-neighborhood rows: row `6` remains
`[0,3,5,8]`, and both dropped rows remain their source-`151` rows. This closes
only the next relaxation level for that diagnostic; it is not outside-pair
support existence, row forcing, `n=9`, or the bootstrap bridge. See
`docs/bootstrap-t12-151-6-outside-pair-two-row-drop.md`,
`scripts/check_bootstrap_t12_151_6_outside_pair_two_row_drop.py`, and
`data/certificates/bootstrap_t12_151_6_outside_pair_two_row_drop.json`.

The source-`151` row-`6` outside-pair full-neighborhood vertex-circle packet
then lets every other center choose arbitrary selected `4`-sets while row `6`
stays in the same thirteen-row activation family. Basic filters leave `28`
complete assignments, including `21` with non-original row `6`; vertex-circle
quotient replay kills all `28` by `20` self-edges and `8` strict cycles. This
is still a finite diagnostic only, not a proof of outside-pair support
existence, row forcing, `n=9`, or the bootstrap bridge. See
`docs/bootstrap-t12-151-6-outside-pair-full-neighborhood-vertex-circle.md`,
`scripts/check_bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.py`,
and
`data/certificates/bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.json`.

The source-`151` row-`6` outside-pair connector contract records the local
conditional needed by the T12/F16 equality connector. If a genuine rich class
at center `6` contains witnesses `0` and `8`, then `[0,6]=[8,6]`. It partitions
the outside supports into connector-forcing endpoint-`8` pairs `[3,8]` and
`[5,8]`, and the connector-avoiding private-halo-only pair `[3,5]`. This is
still a finite diagnostic only, not a proof of outside-pair support existence,
row forcing, `n=9`, or the bootstrap bridge. See
`docs/bootstrap-t12-151-6-outside-pair-connector-contract.md`,
`scripts/check_bootstrap_t12_151_6_outside_pair_connector_contract.py`, and
`data/certificates/bootstrap_t12_151_6_outside_pair_connector_contract.json`.

The source-`151` row-`6` private-lane residual packets now identify the
row-local label-`4` obligations left by the connector-avoiding pair `[3,5]`.
After the label-`8`-free residual-target, quotient-role, and transfer-path
ledgers, the obligation checker records `8` positive transfer incidences, `7`
unique centered equality obligations, and `6` path motifs. Every positive
transfer starts with a label-`4` spoke swap at row `5` or row `7`, while the
only row-`6` transfer obligation is the connector step `[5,6]=[0,6]` after
row `5` supplies `[4,5]=[5,6]`. The length-component checker collapses those
obligations into `6` undirected segment-length components over `9` distinct
segments: `3` edge-diagonal components, `2` diagonal-only components, and one
row-`5`/row-`6` connector cascade `D[0,6]=D[4,5]=D[5,6]`. This is still a
finite diagnostic only. The component-feasibility negative control gives a
strict cyclic convex `9`-gon arc witness for each of those six components
considered alone, including a modulus-`13` witness for the row-`6` cascade.
Thus component-alone impossibility is rejected, and any future exclusion must
use extra private-support, rich-class, row-forcing, or activation-provenance
hypotheses. The support-hypothesis ledger names those extra inputs: the six
components induce seven centered support requirements, the row-`6` cascade
requires center `5` with witnesses `[4,6]` and center `6` with witnesses
`[0,5]`, and none of the seven requirements is the exact private pair
`[3,5]`. The cascade row-criticality packet then checks the three cascade
signatures with auxiliary center pair `5,8`: the full local row package
`{5,6,8}` is strict-cycle obstructed, while every nonempty proper row
truncation is quotient-clean. This is not a proof of support existence, row
forcing, endpoint-`8` forcing, `[3,5]` impossibility, simultaneous
realization of all components, `n=9`, or the bootstrap bridge.
See
`docs/bootstrap-t12-151-6-label4-transfer-obligations.md`,
`scripts/check_bootstrap_t12_151_6_label4_transfer_obligations.py`, and
`data/certificates/bootstrap_t12_151_6_label4_transfer_obligations.json`, plus
`docs/bootstrap-t12-151-6-label4-transfer-length-components.md`,
`scripts/check_bootstrap_t12_151_6_label4_transfer_length_components.py`, and
`data/certificates/bootstrap_t12_151_6_label4_transfer_length_components.json`,
plus `docs/bootstrap-t12-151-6-label4-transfer-component-feasibility.md`,
`scripts/check_bootstrap_t12_151_6_label4_transfer_component_feasibility.py`,
and
`data/certificates/bootstrap_t12_151_6_label4_transfer_component_feasibility.json`,
plus `docs/bootstrap-t12-151-6-label4-support-hypothesis-ledger.md`,
`scripts/check_bootstrap_t12_151_6_label4_support_hypothesis_ledger.py`, and
`data/certificates/bootstrap_t12_151_6_label4_support_hypothesis_ledger.json`,
plus `docs/bootstrap-t12-151-6-label4-cascade-row-criticality.md`,
`scripts/check_bootstrap_t12_151_6_label4_cascade_row_criticality.py`, and
`data/certificates/bootstrap_t12_151_6_label4_cascade_row_criticality.json`.

The source-`151` singleton-support audit covers the two remaining
one-outside-label row targets, `151:5` and `151:8`. Row `151:5` uses
bootstrap-core witnesses `[2,4]` and singleton supports `7` and `8`; row
`151:8` uses bootstrap-core witnesses `[1,2]` and singleton supports `5` and
`7`. Each target has nine activation rows. In the fixed source-`151`
neighborhoods, only the original target rows `[2,4,7,8]` and `[1,2,5,7]`
survive the row-pair, witness-pair, and crossing filters. The one-row-drop
relaxations again have only trivial original-neighborhood survivors. This is
still a finite diagnostic only, not a proof of singleton support existence,
row forcing, `n=9`, or the bootstrap bridge. See
`docs/bootstrap-t12-151-singleton-support-audit.md`,
`scripts/check_bootstrap_t12_151_singleton_support_audit.py`, and
`data/certificates/bootstrap_t12_151_singleton_support_audit.json`.

The source-`151` singleton-support two-row-drop follow-up extends the same
audit by allowing any unordered pair of non-target rows to move arbitrarily.
It checks `2,469,600` candidate states across targets `151:5` and `151:8`,
leaves `56` survivors, and all survivors are the trivial original-neighborhood
rows. This closes only the next relaxation level for that diagnostic; it is
not singleton-support existence, row forcing, `n=9`, or the bootstrap bridge.
See `docs/bootstrap-t12-151-singleton-two-row-drop.md`,
`scripts/check_bootstrap_t12_151_singleton_two_row_drop.py`, and
`data/certificates/bootstrap_t12_151_singleton_two_row_drop.json`.

The source-`151` singleton-support full-neighborhood vertex-circle follow-up
then lets all other centers choose arbitrary selected `4`-sets while the target
row stays in the same nine-row activation family. Basic filters leave `50`
complete assignments across targets `151:5` and `151:8`, including `36` with
non-original target rows; vertex-circle quotient replay kills all `50` by
`37` self-edges and `13` strict cycles. This is still a finite diagnostic
only, not a proof of singleton support existence, row forcing, `n=9`, or the
bootstrap bridge. See
`docs/bootstrap-t12-151-singleton-full-neighborhood-vertex-circle.md`,
`scripts/check_bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.py`,
and
`data/certificates/bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.json`.

The singleton full-neighborhood crosswalk joins the source-`81` row-`8` packet
with the source-`151` rows `5` and `8` packet. Across the three current
one-outside-label singleton-support targets, basic filters leave `84` complete
assignments, including `63` with non-original target rows; exact
vertex-circle quotient replay kills all `84` by `64` self-edges and `20`
strict cycles. This is still diagnostic-only cross-artifact bookkeeping, not
singleton-support existence, row forcing, `n=9`, the bootstrap bridge, Erdos
Problem #97, or a counterexample. See
`docs/bootstrap-t12-singleton-full-neighborhood-crosswalk.md`,
`scripts/check_bootstrap_t12_singleton_full_neighborhood_crosswalk.py`, and
`data/certificates/bootstrap_t12_singleton_full_neighborhood_crosswalk.json`.

### Fixed-pattern exact obstructions

Status: `EXACT_OBSTRUCTION`.

The mutual-rhombus midpoint filter kills the fixed selected patterns
`B12_3x4_danzer_lift`, `B20_4x5_FR_lift`, `C20_pm_4_9`, `C16_pm_1_6`,
`C13_pm_3_5`, and `C9_pm_2_4`. The pattern `C17_skew` is killed by an odd
forced-perpendicularity cycle.

The phi 4-cycle rectangle-trap filter kills a registered fixed `n=9`
selected-witness pattern with directed cycle
`{0,6}->{2,8}->{1,5}->{4,7}->{0,6}`. The cycle is not a reciprocal 2-cycle and
not an odd perpendicularity cycle. The exact obstruction uses the cyclic
subsequence `0,1,2,4,5,6,7,8`, a midpoint-rectangle normalization, and the
identity `D1 + D3 + D5 + D7 = -4*a*b` with cyclic-order signs `a,b > 0`. This
is a fixed-pattern obstruction only, not an `n=9` completeness theorem. See
`docs/phi4-rectangle-trap.md`,
`scripts/check_phi4_rectangle_trap.py`, and
`data/certificates/n9_phi4_rectangle_trap.json`.

The reusable frontier scan in `data/certificates/phi4_frontier_scan.json`
applies the same filter to registered fixed-order cases. It records the
registered `n=9` pattern as the only current positive hit among the scanned
cases, and confirms that the registered sparse non-natural orders remain
invisible to phi4 traps because they have no `phi` edges. This is negative
filter information only, not evidence of realizability.

The round-two Kalmanson/Farkas certificate kills the fixed `C19_skew`
selected-witness pattern with offsets `[-8,-3,5,9]` in the cyclic order
`[18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1]`. The certificate is a
positive integer sum of 2 strict Kalmanson distance inequalities whose total
coefficient vector is exactly zero after quotienting by the selected-distance
equalities. See `docs/round2/round2_merged_report.md`,
`docs/round2/kalmanson_distance_filter.md`,
`scripts/check_kalmanson_certificate.py`, and
`data/certificates/round2/c19_kalmanson_known_order_two_unsat.json`. The earlier
94-inequality certificate remains checked as provenance.

The follow-up Z3 Kalmanson order certificate kills the fixed abstract
`C19_skew` selected-witness pattern across all cyclic orders. The artifact
`data/certificates/c19_skew_all_orders_kalmanson_z3.json` stores 7,981 exact
forbidden ordered-quadrilateral pairs; the verifier checks that every stored
pair is a two-inequality Kalmanson inverse pair after selected-distance
quotienting and then replays the accumulated cyclic-order constraints as Z3
UNSAT. This is an exact obstruction for this fixed abstract pattern only, not a
proof of Erdos #97. See `docs/kalmanson-two-order-search.md` and
`scripts/check_kalmanson_two_order_z3.py`.

The sampled C19 prefix-window artifacts also record a bounded
prefix/fourth/fifth refinement chain for the first 480 deterministic
three-boundary-prefix states. The latest catalog-prefilter replay applies the
three checked unit supports in `reports/c19_prefilter_catalog_unit_supports.json`
after the two-row lookup, closing the eight recorded two-row misses and
reducing ordinary fifth-pair Farkas fallbacks over windows 288-479 from eight
to zero. This is exact for the sampled branches only and does not add an
all-order claim beyond the Z3 certificate above. See
`docs/c19-kalmanson-prefix-window-catalog-prefilter-sweep.md`.

The C13 Kalmanson pilot kills the registered non-natural
`C13_sidon_1_2_4_10` order `[5,0,10,8,9,7,4,6,2,11,12,3,1]`. The certificate is
a positive integer sum of 2 strict Kalmanson distance inequalities whose total
coefficient vector is exactly zero after selected-distance quotienting. A
follow-up exact order search now kills the fixed abstract
`C13_sidon_1_2_4_10` pattern across all cyclic orders: every cyclic order
contains a two-inequality inverse-pair obstruction. See
`docs/kalmanson-two-order-search.md`,
`scripts/check_kalmanson_two_order_search.py`, and
`data/certificates/c13_sidon_all_orders_kalmanson_two_search.json`.

The C29 sparse-frontier fixed order
`[0,27,11,4,19,5,26,12,6,21,13,28,14,2,20,18,7,24,10,25,17,3,9,15,1,22,8,23,16]`
is killed by the exact certificate
`data/certificates/c29_sidon_fixed_order_kalmanson_165_unsat.json`. This is a
positive integer sum of 165 strict Kalmanson distance inequalities whose total
coefficient vector is exactly zero after quotienting by the selected-distance
equalities for offsets `[1,3,7,15]`. It retires this one fixed-order stress
test, but it is not an all-order obstruction for the abstract C29 Sidon pattern
and not a proof of Erdos #97.

The bounded `n=9` incidence/CSP frontier scan in
`data/certificates/n9_incidence_frontier_bounded.json` fixes the natural order
and row `0` to the registered seed row `{1,2,3,8}`. In that row0-fixed slice,
the default run completes before its explicit limits: it checks 3 full patterns,
killing 1 by an odd forced-perpendicularity cycle and 1 by the phi4
rectangle-trap filter. The remaining previous `accepted_frontier` pattern is
now classified by 6 row-Ptolemy product-cancellation certificates under the
fixed natural cyclic order, leaving 0 accepted-frontier items in the default
slice. This is a bounded diagnostic slice only, not an `n=9` completeness
theorem, and the row-Ptolemy certificates are fixed supplied-order obstructions
only. See `docs/n9-incidence-frontier.md` and
`scripts/check_n9_incidence_frontier.py`.

The exact no-reciprocal `n=9` regular-tournament audit in
`scripts/check_n9_regular_tournament_kalmanson.py` enumerates all `3,230,080`
labelled regular tournaments on cyclic labels `0,1,...,8`. In this subcase,
every unordered pair is selected in exactly one direction. Substituting the row
radius variables into strict Kalmanson inequalities gives a strongly connected
strict-implication graph for every tournament, hence a strict cycle
obstruction. This proves only that any `n=9` selected-witness candidate must
have at least one reciprocal selected pair. It is not an `n=9` proof and does
not promote the review-pending exhaustive vertex-circle checker. See
`docs/n9-regular-tournament-kalmanson-audit.md`.

The exact one-reciprocal `n=9` Kalmanson audit in
`scripts/check_n9_one_reciprocal_kalmanson.py` checks the next branch after the
regular-tournament case: exactly one reciprocal selected unordered pair, hence
exactly one absent unordered pair by the selected-edge count. The checker uses
cyclic-dihedral reduction to check `76` status representatives covering all
`1,260` labelled reciprocal/absent status choices, then searches all degree-4
orientations of the remaining pairs. Every branch is killed by a strict
Kalmanson implication cycle after selected-distance quotienting. Combined with
the no-reciprocal audit, this proves only that any `n=9` selected-witness
candidate must have at least two reciprocal selected pairs, and hence at least
two absent unordered pairs. It is not an `n=9` proof and does not promote the
review-pending exhaustive vertex-circle checker. See
`docs/n9-one-reciprocal-kalmanson-audit.md`.

### Review-pending exhaustive n=9 vertex-circle check

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`.

The new repo-native checker in `scripts/check_n9_vertex_circle_exhaustive.py`
enumerates all 70 row-0 selected-witness choices for a cyclically labelled
nonagon. With vertex-circle pruning enabled it visits 16,752 nodes and leaves
0 full assignments. Its cross-check disables vertex-circle pruning during
branching, finds 184 full assignments passing the pair/crossing/count filters,
then classifies all 184 as exact vertex-circle obstructions: 158 self-edges and
26 strict cycles.

The companion input-data audit
`scripts/check_n9_vertex_circle_input_audit.py --check --assert-expected --summary-json`
recomputes the row-0 choices as the 70 lexicographic 4-subsets of labels
`1..8` and checks the stored witness lists, masks, summary counts, and
no-overclaiming scope. Use `--json` instead when the full expected-count block
is needed. It does not rerun the brancher or replay the
vertex-circle certificates.
The turn-inequality frontier replay
`scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --summary-json`
checks stored integer dual certificates for the candidate weak turn system on
all 184 regenerated pair/crossing/count frontier assignments. It records all
184 weak systems as arithmetically infeasible, but the geometric turn lemma and
indexing conventions remain review-pending, so this does not promote `n=9`.
Use `--json` instead when the full certificate rows are needed.
The compact Kalmanson self-edge replay
`scripts/check_n9_kalmanson_selfedge.py --verify-certificate data/certificates/n9_kalmanson_selfedge.json --assert-expected --summary-json`
checks a separate certificate in which each of those 184 terminal assignments
has a single strict Kalmanson inequality whose two sides become the same
quotient multiset after selected-distance quotienting. This is a
review-pending audit aid only; it does not independently complete review of the
brancher or promote `n=9`. Use `--json` when the full replay payload is needed.
The independent replay
`scripts/check_n9_kalmanson_selfedge_independent_replay.py --check --assert-expected --summary-json`
treats that stored certificate as input data and rechecks row shape, row-pair
crossing, witness-pair capacity, selected-distance quotienting, the stored
self-edge records, assignment uniqueness, and digest agreement without
importing the Kalmanson generator module. It is still stored-certificate
bookkeeping only, not brancher coverage or a proof of `n=9`. Use `--json` when
the first stored self-edge example record is needed.
A fixed-center-order replay command,
`scripts/check_n9_vertex_circle_mro_branching_replay.py --check --assert-expected --summary-json`,
also closes the vertex-circle-pruned search and reaches the same
`184 = 158 + 26` pre-vertex-circle frontier classification as the dynamic
minimum-remaining-options artifact. This checks branch-order agreement only;
use `--json` when the full fixed-order replay sections are needed.
The strict-edge geometry audit
`scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --summary-json`
checks that every candidate selected row produces exactly the proper-interval
strict inequalities used by the checker, with `5,670` total local strict
edges across 630 candidate rows. This is local rule verification only; use
`--json` when the full mismatch example block is needed.
The incidence-filter audit
`scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --summary-json`
checks the row-level two-overlap crossing table, witness-pair cap predicate,
and selected-indegree cap predicate. This is row-filter implementation
agreement only. Use `--json` instead when the full histogram blocks are
needed.
The quotient-soundness audit
`scripts/check_n9_vertex_circle_quotient_soundness.py --check --assert-expected --summary-json`
checks that the stored local-core rows and 184 stored frontier assignments get
the same selected-distance quotient status from the exhaustive checker, the
reusable replay helper, and a small direct replay. This is implementation
agreement only; use `--json` when the full per-view status and mismatch
example blocks are needed.
The closed-descent packet
`scripts/check_n9_vertex_circle_closed_descent_packet.py --check --assert-expected --json`
turns the 16 stored compact local-core quotient obstructions into checked
finite descent regions and extracted strict-cycle certificates. It records
`13` one-class regions and `3` multi-class regions, with cycle-length counts
`1:13`, `2:1`, and `3:2`. This is diagnostic local-packet data only, not a
proof of `n=9` or a bridge proof.
The partial-pruning audit
`scripts/check_n9_vertex_circle_partial_pruning.py --check --assert-expected --summary-json`
checks all 94,024 nonempty selected-row subsets of the stored 184 frontier
assignments. It finds zero checker/replay status mismatches and zero stored
extension violations for obstructed subsets. This is stored-frontier pruning
diagnostics only. Use `--json` when the full mismatch example block is needed.
The frontier-assignment audit
`scripts/check_n9_vertex_circle_frontier_assignment_audit.py --check --assert-expected --summary-json`
checks the stored 184 frontier assignments directly. It records zero row-shape,
center-coverage, crossing, witness-pair-cap, and selected-indegree-cap errors;
this is stored-frontier diagnostics only. Use `--json` when the full example
error block is needed.
The branch-option audit
`scripts/check_n9_vertex_circle_branch_options.py --check --assert-expected --summary-json`
checks 520,598 no-vertex-circle fixed-order option contexts and finds zero
helper/direct option mismatches and zero maintained-count mismatches. This is
branch-option implementation diagnostics only. The dynamic-MRO choice audit
`scripts/check_n9_vertex_circle_dynamic_mro_choices.py --check --assert-expected --summary-json`
checks the actual minimum-remaining-options center choice on both dynamic
searches. It recomputes all unassigned-center option lists at every reached
state, finds zero center-choice mismatches, zero helper/direct option
mismatches, and zero maintained-count mismatches. This is branch-choice
implementation diagnostics only. The frontier-coverage crosswalk
`scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check --assert-expected --summary-json`
reruns the dynamic no-vertex-circle brancher and verifies that its 184
complete selected-row assignments match the stored frontier classification
artifact row-for-row, with zero status mismatches. This is stored-frontier
coverage bookkeeping only; use `--json` for the full audit records. The
dihedral-orbit audit
`scripts/check_n9_vertex_circle_dihedral_orbit_audit.py --check --assert-expected --summary-json`
independently replays the 18 dihedral relabelings for the stored motif-family
representatives and cross-checks the 184 frontier-classification rows against
those disjoint orbits. It is orbit bookkeeping only. Use `--json` when the
full mismatch example block is needed.
The motif-obstruction audit
`scripts/check_n9_vertex_circle_motif_obstruction_audit.py --check --assert-expected --summary-json`
treats the 16 stored motif representatives as input and checks their
representative self-edge equality paths or strict-cycle edge chains after
recomputing quotient classes and strict interval edges. It is
stored-certificate bookkeeping only. Use `--json` when the full example error
block is needed.
The frontier comparison
`scripts/compare_n9_vertex_circle_frontier.py --check --assert-expected --summary-json`
checks the stored P18/C19 comparison artifact against the current local-core
and vertex-circle helpers. It records zero exact n=9 local-core embeddings into
the recorded P18 and C19 patterns, while preserving the P18 strict-cycle and
C19 fixed-order pass guardrails. It is comparison diagnostics only, not a
transfer theorem, counterexample, or proof of `n=9`. Use `--json` when the
full pattern records are needed.
The local-core subset audit
`scripts/check_n9_vertex_circle_local_core_subset_audit.py --check --assert-expected --summary-json`
checks that the compact local-core packet rows are exact subsets of the stored
full motif representatives and already force the same obstruction status by
direct quotient replay. It is compact-core bookkeeping only. Use `--json` when
the full example error block is needed.
The focused packet catalog audit
`scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py --check --assert-expected --summary-json`
checks that the 12 focused local-lemma packets, source template packet records,
template catalog records, and aggregate focused-note crosschecks agree on the
same `184` assignments and 16 families. Use `--json` instead when the full
packet records are needed. It is packet/catalog bookkeeping only, not packet
soundness, local-lemma completeness, frontier coverage, or a proof of `n=9`.
The focused mini-replay crosswalk
`scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py --check --assert-expected --summary-json`
joins those same 12 focused packets to their packet-specific minimal
input-data replay artifacts. Use `--json` instead when the full mini-replay
records are needed. The local-lemma audit path
`scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --summary-json`
runs the packet/catalog, focused mini-replay, aggregate/simple-replay,
exhaustive/local-lemma, and relation-skeleton/local-lemma handoffs with
adjacent drift localization, plus the relation-skeleton/closed-descent
companion summary. Use `--json` instead when the full layer and manifest
records are needed. These are review-pending handoff audits only, not packet
soundness, local-lemma completeness, frontier coverage, or a proof of `n=9`.
The relation-skeleton/closed-descent crosswalk
`scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py --check --assert-expected --summary-json`
checks the same 16 families against the closed-descent packet, matching
self-edge skeletons to one-class regions and strict-cycle skeletons to
multi-class regions. It is packet bookkeeping only.

This is a candidate extension of the repo-local finite-case pipeline to `n=9`,
but it is not yet the source-of-truth strongest result. The raw incoming bundle
also contains 184-pattern/16-orbit and 102-certificate Kalmanson verifier
variants whose symmetry conventions need separate review. See
`docs/n9-vertex-circle-exhaustive.md`,
`data/certificates/n9_vertex_circle_exhaustive.json`, and
`incoming/archive-output-2026-05-03/`.

### Review-pending n=8 proof and n=9 Gröbner pruning

Status: `MACHINE_CHECKED_ALGEBRAIC_PROOF_REVIEW_PENDING` for `n=8`;
`PARTIAL_EXACT_PRUNING_REVIEW_PENDING` for `n=9`.

The 2026-05-05 multi-agent attack (see `docs/erdos97-attack-2026-05-05.md`)
adds an independent algebraic-geometry verification at n=8 and n=9 using
sympy's Gröbner basis over `QQ`.

For n=8 (15 incidence-completeness survivors): 14 of 15 patterns have
grevlex Gröbner basis equal to {1} — no complex solutions exist, hence no
Euclidean realization. The remaining pattern (id=14) has a zero-dimensional
ideal with elimination polynomial `y_7^4 - (7/2) y_7^2 + 1/16 = 0`; its
4 real algebraic configurations all collapse to a hexagram on the lattice
`{0, 1/2, 1±sqrt(3)/2}^2` and fail strict convexity. This gives a complete
Gröbner-basis-only proof of n=8 (≈3.4 s wall-clock total). Artifact:
`data/certificates/2026-05-05/n8_groebner_results.json`.

For n=9 (184 surviving witness assignments collapsed to 16 dihedral
families): 11 of 16 families (150 / 184 labelled assignments) have
grevlex Gröbner basis equal to {1}. Family F12 (orbit 18) has a Gröbner
generator `y_8^2 + 1/4 = 0` ruling out real solutions. The 2026-05-05
artifacts therefore exactly kill 168 / 184 labelled assignments. A 2026-05-06
follow-up adds replayable real-root / non-degeneracy decoders for F07, F08,
F09, and F13 (orbit total 16). The decoder enumerates 80 real algebraic
configurations across the four families and records zero strictly convex
configurations, with every accepted real configuration degenerate. Artifacts:
`data/certificates/2026-05-05/n9_groebner_results.json` and
`data/certificates/n9_groebner_real_root_decoders.json`; verifier:
`scripts/decode_n9_groebner_f07_f13.py`.

This complements the existing vertex-circle filter — which independently
kills all 184 n=9 patterns by geometric strict-monotonicity arguments — but
the algebraic route remains review-pending and does not promote n=9 beyond
the existing audit-target status without independent review.

### Review-pending n=10 vertex-circle singleton-slice draft

Status: `MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING`.

An incoming generic checker continuation is recorded as
`data/certificates/n10_vertex_circle_singleton_slices.json`. It covers all
126 row0 singleton slices for a cyclically labelled decagon, reports 4,142,738
total visited nodes, 0 full assignments, and no aborted slices. The imported
counts are:

```text
partial self-edge prunes:   4,467,592
partial strict-cycle prunes: 5,318,250
```

This is a draft audit target only. The repo-native generic checker reproduces
the n=9 vertex-circle counts and reruns row0 singleton IDs `0`, `63`, and
`125`, but the full n=10 search still needs independent implementation review
or a compact replayable
certificate format before any public theorem-style use. It is not promoted to
the source-of-truth strongest result. See
`docs/n10-vertex-circle-singleton-slices.md`.

The bounded `n=10` row0-index-0 turn pilot in
`data/certificates/n10_turn_row0_pilot.json` is finite bookkeeping only. It
records 160 raw assignments in the first row0 slice: 156 have weak-turn Farkas
certificates, and the four weak-turn SAT escapes are all killed by row0-local
vertex-circle self-edges. The derived artifact
`data/certificates/n10_turn_row0_escape_self_edges.json` records those four
first self-edge templates compactly. This is proof-mining evidence only, not a
complete n=10 search, not a proof of `n=10`, and not a counterexample. See
`docs/n10-turn-row0-pilot.md` and
`docs/n10-turn-row0-escape-self-edges.md`.

The derived crosswalk in
`data/certificates/n10_turn_row0_combined_closure.json` packages that bounded
row0 slice as a disjoint closure partition: the stored weak-turn Farkas
certificates close `156` assignments, and the four weak-turn SAT escapes
`[74,103,156,157]` are exactly the four stored row0-local vertex-circle
self-edge templates. This is still finite bookkeeping only, not a complete
n=10 search, not a proof of `n=10`, and not a counterexample. See
`docs/n10-turn-row0-combined-closure.md`.

The generator-independent `n=10` mixed rich-support capacity diagnostic in
`data/certificates/n10_mixed_rich_support_capacity.json` applies only
support-level necessary filters: row-pair cap, two-overlap crossing, and
witness-pair capacity. It checks all dihedral center-set representatives with
`q=3,...,7` size-five supports and finds no complete assignments; a direct
`q=2` witness shows this is sharp for those filters alone. Thus this
abstraction leaves at most two size-five supports, or at least eight
exact-four-only centers, in any surviving `n=10` support assignment. This is
finite support bookkeeping only, not a proof of `n=10`, not a proof of Erdos
Problem #97, and not a counterexample. See
`docs/n10-mixed-rich-support-capacity.md`.

The follow-up rich vertex-circle quotient diagnostics in
`data/certificates/n10_q2_rich_vertex_circle.json` and
`data/certificates/n10_q1_rich_vertex_circle.json` close the exactly-two and
exactly-one size-five layers, respectively. Combined with the support-capacity
catalogue, this leaves only the all-exact-four `q=0` layer inside the
four/five support-plus-quotient abstraction. This remains review-pending
finite bookkeeping only, not an `n=10` proof and not a global status update.

The row-circle Ptolemy diagnostic in
`docs/row-circle-ptolemy-nlp.md` adds the Ptolemy equality forced by each
selected witness quadruple being concyclic around its center. It numerically
obstructs the registered `C19_skew` abstract order with margin about
`-0.00264843`; this is `NUMERICAL_NONLINEAR_DIAGNOSTIC` only and requires
exactification before it can be used as an obstruction. The registered
`C13_sidon_1_2_4_10` order records optimizer failure in this row-circle
Ptolemy diagnostic, but it is now killed by the separate fixed-order Kalmanson
certificate above. The follow-up active-set artifact
`data/certificates/c19_row_circle_ptolemy_active_set.json` records the
optimized C19 distance classes and tight numerical constraints for
exactification work, including a SciPy SLSQP multiplier summary; it is not an
exact certificate. The companion multiplier-reduction artifact pairs all 19
row-circle equalities with their duplicate global Ptolemy rows and reduces the
largest absolute combined multiplier to `24`, clarifying that the largest raw
weights are redundancy noise.

Under the natural cyclic order, `P18_parity_balanced` and
`P24_parity_balanced` are killed by adjacent-row two-overlap via the
crossing-bisector lemma. As abstract incidence patterns with arbitrary cyclic
order, `P24_parity_balanced` is killed by the exact finite crossing CSP, and
`P18_parity_balanced` is killed by crossing constraints plus the vertex-circle
order strict-cycle filter.

See `docs/mutual-rhombus-filter.md` and
`scripts/check_mutual_rhombus_filter.py`. See also
`docs/cyclic-crossing-csp.md`, `docs/vertex-circle-order-filter.md`,
`data/certificates/p24_cyclic_crossing_unsat.json`, and
`data/certificates/p18_vertex_circle_order_unsat.json`.

### Sparse frontier fixed-order diagnostics

Status: `FIXED_ORDER_DIAGNOSTIC`.

The C25/C29 sparse-frontier probe in
`data/certificates/c25_c29_sparse_frontier_probe.json` records two fixed-order
stress tests for the larger Sidon entries. For `C25_sidon_2_5_9_14`, the
Kalmanson Z3 refinement found a step-7 fixed cyclic order with no
two-inequality Kalmanson inverse-pair obstruction, but the same order is
exactly killed by vertex-circle and Altman filters.

For `C29_sidon_1_3_7_15`, the refinement found one fixed cyclic order that
survived the lightweight fixed-order exact filter sweep and the two-inequality
Kalmanson inverse-pair search. It also passed the metric-order LP and a slow
global Ptolemy NLP diagnostic with positive margins. The row-circle Ptolemy NLP
was too slow to complete interactively. The fixed order is now exactly killed
by the separate 165-inequality Kalmanson/Farkas certificate
`data/certificates/c29_sidon_fixed_order_kalmanson_165_unsat.json`. The
original probe remains useful as a record of which weaker filters failed.

The follow-up sparse-frontier Kalmanson escape audit in
`data/certificates/sparse_frontier_kalmanson_escape_audit.json` independently
replays the direct two-inequality Kalmanson inverse-pair filter for the stored
C25/C29 fixed orders over all `2*binom(n,4)` strict Kalmanson rows. It checks
`25,300` rows for the C25 fixed order and `47,502` rows for the C29 fixed
order, finding zero inverse-pair conflicts in both cases. This confirms the
stored zero-conflict conclusion while recording that the older probe's
`rows_seen` counters were not full-row counts. It is a fixed-order filter
diagnostic only, not an all-order obstruction or proof of Erdos Problem #97.

### Lemma draft (review pending): two-orbit circulant configurations

Status: `LEMMA` draft, review pending; restricted family only.

No strictly convex polygon whose vertex set is two concentric regular
`m`-gons (any radii, any relative rotation, `m >= 3`) has four equidistant
other vertices at every vertex. The proof first forces the relative rotation
to `0` (impossible by a ray argument) or the exact half-step `pi/m`, then
forces each first-orbit witness row to one same-orbit pair plus one
cross-orbit pair, and finally shows the resulting radius-ratio quadratic has
no root in the strict-convexity window `(cos(pi/m), sec(pi/m))` by a
four-case cosine-ladder argument. Within its family this supersedes the
fixed quarter-turn half-step ansatz obstruction, and it is an independent
second-source derivation of the same family obstruction as the restricted
symmetric two-orbit reduction entry above: that note's gear equation is
algebraically identical to the row equation here, and its `k = 3` boundary
factor matches the `m = 3` window-endpoint hit. It is not a proof of Erdos
Problem #97 and says nothing about three or more orbits. See
`docs/two-orbit-circulant-obstruction.md`; machine audit:
`scripts/check_two_orbit_dynamic_window_lemma.py --max-m 400 --assert-clear`
(5,313,300 offset pairs float64-screened with high-precision escalation for
the one exact `m = 3` boundary hit at `x = sec(pi/3)`, zero window roots,
boundary hit excluded by strictness).

### Lemma draft (review pending): half-step matching for multi-orbit cyclic configurations

Status: `LEMMA` draft, review pending; structural reduction only.

In any strictly convex union of `t >= 2` noncentral `C_m` orbits, no
pairwise orbit offset is `0 mod 2*pi/m`, and the half-step pairs
(offset exactly `pi/m`) form a partial matching on the orbits: no orbit can
be half-step-aligned with two others, since the two partners would then be
mutually aligned. Any row using two witnesses from a foreign orbit forces
that orbit pair to be half-step, so for `t = 3` at least two pairwise
offsets are generic and the rows of at least one orbit are forced into
own-pair-plus-two-singles shape, carrying two distance equations each.
Every `t = 3` branch is strictly overdetermined (three unknowns against at
least four equations, or four against six). This is structural reduction
bookkeeping toward the window analyses; it is not an obstruction for
`t >= 3`, not an `n`-range exclusion, and not a proof of Erdos Problem #97.
See `docs/half-step-matching-reduction.md`.

### Three-orbit (t=3) paired-cosine reduction and finite-m closure screen

Status: `LEMMA` draft (review pending) for the reduction;
`NUMERICAL_EVIDENCE` with exact-escalation bookkeeping for the per-`m`
screen verdicts; the `m = 0 mod 4` quarter cells are named open sub-cases.

For three concentric regular `m`-gon orbits, the normalization
`0 < beta < gamma < 2h` admits at most one half-step offset, splitting the
search into four exhaustive branches; every witness row decomposes into
equidistance atoms whose equations are linear in the cosine/sine of one
unknown offset, and pairing the two equations on each offset pins the radii
by univariate polynomials (the `B`-`C` half-step branch is homogeneous and
pins the radius ratio to algebraic constants). The screen enumerates every
discrete branch cell for `m = 3..16`, refutes every float64 candidate by
60-digit deterministic re-derivation or excludes it as an exact boundary
hit, and finds no feasible survivor and no unresolved case. The branch-`G`
pinning identity degenerates exactly at `m = 0 mod 4`, `a1 = a2 = m/4`,
`s = m/2`; those quarter cells carry one-parameter solution families, are
skipped by the point screen, and remain open. Not an all-`m` lemma, not an
exact certificate for the screened cells, and not a proof of Erdos Problem
#97. See `docs/three-orbit-window-closure.md`,
`scripts/check_three_orbit_window_closure.py --min-m 3 --max-m 16
--assert-clear`, and
`data/certificates/three_orbit_window_closure_m3_16.json`.

### Exact SMT closure of the m=4 three-square quarter cell (n=12)

Status: `LEMMA` draft (review pending) for the reduction; `EXACT_OBSTRUCTION`
(SMT certificate) for the infeasibility decision.

The smallest open three-orbit quarter cell, `m = 4` (three concentric
squares, `n = 12`), is closed exactly. Because a square's only own
equidistance pair from a vertex is its 90-degree diagonal pair, branch-G
4-badness of three squares is equivalent to three explicit algebraic
conditions: `P(y) in {+-cos b, +-sin b}`, `P(z) in {+-cos g, +-sin g}`, and
`Q(y,z) in {+-cos(g-b), +-sin(g-b)}`, with `P(r)=(r^2-1)/(2r)` and
`Q=(z^2-y^2)/(2yz)` (equivalently `P=sinh(ln r)`, `Q=sinh(ln z - ln y)`). A z3
nonlinear-real-arithmetic certificate shows that, together with the
strict-convexity radius window `cos h < y,z < 1/cos h` and
`0 < b < g < pi/2`, all 64 discrete sign/witness combinations are UNSAT --
without even invoking the convexity inequalities, so the strictly convex case
is a fortiori empty. Hence no strictly convex three-square configuration is
branch-G 4-bad. SMT UNSAT is an accepted exact-obstruction certificate here
(as with the existing Kalmanson z3 certificates). Restricted-family result:
the `m = 4` half-step branches AB/AC/BC are screen-grade in the three-orbit
artifact, the `m = 8, 12, 16` quarter cells remain open, and the
official/global status is unchanged. See
`docs/three-square-m4-exact-closure.md`,
`scripts/check_three_square_m4_closure.py --assert-clear`, and
`data/certificates/three_square_m4_closure.json`.

### Three-orbit quarter-cell A-row reduction and boundary-band lemma

Status: `LEMMA` (exact, self-checked) for the reductions; `NUMERICAL_EVIDENCE`
for the `m = 8, 12, 16` non-convexity; `m = 4` closed exactly above.

Two exact, `m`-uniform lemmas reduce the remaining quarter cells. (1) A-row
reduction: in every quarter cell the A-row and B-row own pair is the 90-pair,
so `A_0` is 4-bad only if it has a B-vertex and a C-vertex at squared distance
2, i.e. `P(y) in {cos(b+2kh)}` and `P(z) in {cos(g+2kh)}`; these involve only
the A/B rows and are uniform in the C-row choice `a3`, so the quarter cell
closes iff `A_0` cannot be 4-bad. (2) Boundary-band confinement: since
`pi/2 ≡ 0 (mod 2h)` for `m = 0 mod 4` and `|P| < P(sec h)` in the window, those
witness offsets are forced into `(0, delta) ∪ (2h - delta, 2h)`,
`delta = arcsin(P(sec h))` -- the cross orbit must nearly align with the A
orbit. A float grid over `m in {4,8,12,16}` finds every sampled witness
configuration strictly non-convex, but the locus is **tangent** to the
convexity boundary (the maximum minimum-turn is `< 0` yet vanishes and is
grid-dependent), so for `m >= 8` this is evidence of closure, not a
certificate; those cells remain open. Recorded route limit: the exact-SMT
route does not scale past `m = 4` (z3 NRA times out on the cubic turn
determinants and the witness disjunctions). The clean open lemma that would
close all quarter cells: on the witness locus inside the window the minimum
per-period turn determinant is `<= 0`, with equality only at the degenerate
orbit-coincidence limit. See `docs/quarter-cell-closure.md`,
`scripts/check_quarter_cell_closure.py --assert-clear`, and
`data/certificates/quarter_cell_closure.json`.

## Numerical Attempts

### Dynamic-witness free-pattern sweep (2026-06-09)

Status: `NUMERICAL_EVIDENCE`; no candidate found.

The dynamic-witness searcher lets every center re-select its best witness
4-set (minimum-spread window over sorted squared distances) at every
evaluation, so one continuous run probes all witness patterns reachable by a
configuration family instead of one registered pattern at a time. The first
recorded sweep covers cyclic-equivariant cells `C_m` with `t` orbits for
`10 <= n = m*t <= 36` plus small asymmetric cells, with hard anti-cluster
separation floors and convexity-margin guards plus floor annealing.

No run approached the candidate gate. Strictly convex local optima plateau at
relative spreads around `1e-2` to `1e-1` at healthy margins; every strictly
convex record below spread `2e-3` has normalized convexity margin below
`1e-4`, and the smallest spreads (about `1e-4`) also pin the pairwise
separation at the anti-cluster floor, which is the historical
B12/AlphaEvolve cluster degeneration mode, recorded here as boundary
diagnostics rather than near-misses. With the convexity guard dropped, a
deterministic seeded test converges to the exact nonconvex 24-point
metric-linear configuration at relative spread below `1e-10`, confirming
the alternation machinery can land on exact solutions that are in its
basin. See `docs/dynamic-witness-free-pattern-search.md` and
`data/runs/dynamic_witness_sweep_2026-06-09/summary.json`.

A second deep pass reran the 32 symmetric `t >= 3` cells at 64 restarts each
plus asymmetric `n = 10..16`. Outcome unchanged and sharpened: still no
candidate, best strictly convex relative spread `4.3e-5` (a floor-riding
degeneration at margin `5.4e-8`), every strictly convex record below `1e-3`
either flagged `near_pair_floor` or with margin below `1e-5`, and the
unconstrained lane near `1e-7`, consistent with exact nonconvex solutions
existing while the strictly convex side walls off. See
`data/runs/dynamic_witness_sweep_2026-06-09b/summary.json`.

### C13_sidon_1_2_4_10

Status: exact all-cyclic-order obstruction for this fixed selected-witness
pattern by two-inequality Kalmanson inverse-pair search.

The numerical runs below are retained as historical diagnostic data only. The
fixed abstract C13 pattern is no longer a live sparse-frontier lead.

Diagnostics from constrained SLSQP with polar parameterization, 20 restarts,
seed `2026`, and hard verifier-grade convexity / edge / pair margins:

- margins tested: `1e-3`, `1e-4`, `1e-5`, `1e-6`
- RMS equality residuals: `0.848`, `0.841`, `0.839`, `0.838`
- max selected-distance spreads: about `3.37` to `3.38`
- achieved convexity margins: approximately the requested margin in each run
- minimum edge lengths: `3.3e-2`, `1.1e-2`, `3.3e-3`, `1.0e-3`

Interpretation:

The runs do not produce a near-miss counterexample. The equality residual stays
large in normalized coordinates and is best read as a plateau in the SLSQP basin,
not as an exact obstruction. The fixed abstract pattern is now retired by the
all-order Kalmanson search; these older run artifacts are
`NUMERICAL_EVIDENCE` only. See `docs/sidon-patterns.md` and
`data/runs/C13_sidon_m{1e-3,1e-4,1e-5,1e-6}.json`.

### B12_3x4_danzer_lift

Status: historical near-miss degeneration; fixed selected pattern exactly
killed.

Diagnostics:

- max selected-distance spread: `0.006806368780585714`
- RMS equality residual: `0.0019599509549614457`
- convexity margin: `9.999999943508973e-07`
- minimum edge length: `0.0007465865604262556`
- verifier status at tolerance `1e-6`: rejected

Interpretation:

The residual improves as the polygon approaches a three-cluster degeneration.
This is evidence about a failed route, not a solution. The fixed selected
pattern is now exactly killed by the mutual-rhombus midpoint equations, while
the numerical artifact remains useful as a degeneration diagnostic.

### Archived C12 artifacts

Status: normalized archive imports, rejected as counterexamples.

The synthesis pass imported two machine-readable C12 artifacts into
`data/runs/` so they can be checked by the same verifier as other runs:

- `archive_C12_offsets_4_5_8_11_near_convex.json`: verifier status at
  tolerance `1e-6` is rejected. Its selected-distance spread is about
  `1.85e-6`, and empirical multiplicities alternate between 4 and 3, so half
  the centers do not meet the 4-neighbor target even numerically.
- `archive_C12_offsets_2_3_4_10_degenerate.json`: verifier status at
  tolerance `1e-6` is rejected. The equality residual is tiny only because the
  configuration collapses; the convexity margin is negative and the minimum
  pair distance is essentially zero.

See `dropped_kernels.md` for the rejection log. These files are retained as
search-history artifacts, not as live candidates.

## Open Subproblems

1. Independently review the `n=8` incidence checker and the class `3`, `4`,
   and `14` exact certificates.
2. Independently review the review-pending exhaustive `n=9` vertex-circle
   checker before promoting it to source-of-truth finite-case status.
3. Audit the draft `n=10` singleton-slice package with an independent checker
   or replayable terminal-conflict certificate before promoting it beyond
   draft review-pending status.
4. Use the retired `C13_sidon_1_2_4_10` and `C19_skew` sparse patterns as
   benchmarks while searching for new incidence families or a bridge from
   arbitrary counterexamples to a classified selected-witness family.
5. Add interval-arithmetic verification for convexity and distance equations.
