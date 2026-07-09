# STATE.md - Erdos Problem #97 working state

Status: no general proof and no counterexample are claimed.

This is the short working dashboard. For the long-form canonical synthesis,
claim taxonomy, failed-route reconciliation, and source/hash inventory, read
`docs/canonical-synthesis.md` before adding new claims, search branches, or
proof attempts.

Canonical status metadata is recorded in `metadata/erdos97.yaml`. It separates
the official/global falsifiable/open status from this repo's local small-case
theorem and finite-case artifacts.

## Target

Find, or rule out, a strictly convex polygon with vertices
`p_0,...,p_{n-1}` such that every center `i` has a 4-set
`S_i` of other vertices with all squared distances `|p_i-p_j|^2`,
`j in S_i`, equal. Radii and selected 4-sets may vary with `i`;
the directed incidence graph need not be symmetric.[^repo]

## Strongest proved state

An elementary geometric theorem rules out bad strictly convex polygons with
`n <= 8`; see `docs/n8-geometric-proof.md`. It counts apex-marked isosceles
triangles to exclude `n <= 7`, then shows that a bad octagon would be
equilateral and would need at least four exterior turns equal to `2*pi/3`,
contradicting total exterior turn `2*pi`. The proof was independently
rederived within the repository audit on 2026-07-09. External/publication
review remains recommended and is not claimed.

The selected-witness method independently corroborates `n <= 8` in a
repo-local, machine-checked finite-case sense. Its core filters are the
two-circle cap `|S_a cap S_b| <= 2`, radical-axis crossing/bisection when two
rows share exactly two witnesses, the sharpened incidence count forcing
`n >= 8`, and
the `n=8` column-pair cap forcing all witness indegrees to equal 4.
The older `n=7` Fano enumeration remains in the repo because it is a useful
independent reproduction of the equality-case obstruction.[^small]

For `n=8`, `scripts/enumerate_n8_incidence.py` enumerates all necessary
selected-witness incidence survivors and reduces them to 15 canonical classes.
Exact cyclic-order noncrossing kills 1 class, and exact perpendicular-bisector /
equal-distance algebra kills the other 14. See
`docs/n8-incidence-enumeration.md` and `docs/n8-exact-survivors.md`.
External independent review remains recommended before public use of these
computer-assisted artifacts.

A separate SymPy-free independent recheck covers the cyclic-order counts for
all 15 `n=8` survivor classes and independently kills 11 of them by
cyclic-order or rational linear-span arguments. It deliberately does not cover
the Groebner-based classes `3`, `4`, `5`, and `14`, so it is a defensive
cross-check rather than an independent replacement for the full exact
survivor artifact. See `docs/n8-independent-obstruction.md`.

A further independent second source now covers all 15 classes uniformly with a
different decision procedure: `scripts/check_n8_survivors_smt.py` asks z3
nonlinear real arithmetic whether any strictly convex octagon -- encoded
order-free, every vertex exposed in some direction, so no assumption that the
canonical label order is the boundary order -- satisfies each class's
equal-distance + perpendicular-bisector constraints, and finds every class
UNSAT. In fact 14 of the 15 classes are already UNSAT with no convexity
assumption at all (order-independent); only class 14 needs the
exposed-vertex constraint. This cross-checks both the cyclic-order class and
all fourteen PB+ED classes -- including the four Groebner-dependent ones the
SymPy-free recheck skips -- without using Groebner bases or the cyclic-order
combinatorics. Repo-local exact-obstruction cross-check pending external
review. See `docs/n8-survivors-smt-cross-check.md` and
`data/certificates/n8_survivors_smt.json`.

The class `14` Groebner-dependent branch now has a small focused audit checker:
`scripts/check_n8_class14_certificate.py --check --json` rebuilds that one
`PB+ED` system, compares the stored Groebner basis, derives the four real
branches, and verifies by exact orientation signs that each branch has four
hull vertices and four strict interior labels. This is still repo-local audit
support pending external review, not a public theorem claim. See
`docs/n8-class14-certificate.md`.

A companion residual checker,
`scripts/check_n8_residual_certificates.py --check --json`, isolates the
class `3`, `4`, and `5` duplicate, collinearity, and Groebner-y2 certificates.
It verifies the stored substitution chains and ideal equivalence for class `5`
without importing the full exact survivor checker. This is also repo-local
audit support pending external review. See `docs/n8-residual-certificates.md`.

For the general bridge problem, minimality now gives a small proved foothold:
every minimal counterexample admits a partial fragile-cover witness system made
from exact critical 4-ties. This is necessary structure only; the block-6
abstract family shows that fragile-cover hypergraph constraints alone are too
weak. See `docs/minimal-fragile-cover-bridge.md`.

A stored block-6 vertex-circle full-extension audit adds one geometric gate to
that negative control: in the natural cyclic order, the two-block block-6
family has no full selected-row extension surviving the vertex-circle quotient
self-edge / strict-cycle filter. This is still a natural-order diagnostic, not
an all-order/all-extension bridge proof. See
`docs/block6-fragile-vertex-circle-extension-audit.md`.

A checked block-6 crossing-order sample now widens that diagnostic without
changing its scope: two deterministic terminal-extension windows, covering
`200` full extensions and `796` crossing-compatible cyclic orders, are all
killed by vertex-circle quotient self-edges. This is still a bounded sample,
not an all-extension or all-order obstruction. See
`data/certificates/block6_terminal_crossing_vertex_circle_sample.json`.

The stronger stored block-6 crossing-order full sweep exhausts the `105,978`
terminal full extensions generated by the natural-order two-block audit and
checks all `385,517` crossing-compatible cyclic orders those terminal
extensions admit. Every order is killed by the same vertex-circle quotient
filter (`384,318` self-edges and `1,199` strict cycles). This still does not
cover selected-row systems outside that natural-order terminal generator and is
not a fragile-bridge proof. See
`data/certificates/block6_terminal_crossing_vertex_circle_full_sweep.json`.

A fixed-order block-6 probe now confirms the generator gap is concrete: three
non-natural cyclic orders have legal terminal selected-row extensions that fail
the natural-order crossing rule. For the natural order and those three
non-natural orders, the order-specific full-extension search still closes by
vertex-circle quotient pruning. This is fixed-order evidence only, not
all-order closure. See
`data/certificates/block6_fixed_order_vertex_circle_probe.json`.

A block-preserving shuffle-order sweep widens that fixed-order diagnostic to
all `462` normalized cyclic orders that keep the two six-label block orders
internally fixed while shuffling the blocks. All `462` order-specific
full-extension searches close by vertex-circle quotient pruning; `458` orders
have a legal terminal extension, and `457` first terminal extensions are
outside the natural-order terminal generator. This is still a bounded
fixed-order-family diagnostic, not all-order closure. See
`data/certificates/block6_shuffle_order_vertex_circle_sweep.json`.

A companion reversed-second-block shuffle sweep records the first real boundary
of this vertex-circle gate: among the `462` normalized orders preserving
`1,2,3,4,5` in the first block and `11,10,9,8,7,6` in the second, `446` close
but `16` have a vertex-circle-clean full selected-row extension. These clean
abstract rows are not Euclidean realizations and not counterexamples; they are
fixed-order escape targets for stronger filters. See
`data/certificates/block6_reversed_block_shuffle_vertex_circle_escape.json`.
Those 16 fixed assignment/order pairs now have exact Kalmanson quotient-cone
certificates, totaling `394` strict rows and weight sum `16850`; this closes
only that bounded escape set, not all oriented-block shuffles, arbitrary
orders, the fragile bridge, or Erdos #97. See
`data/certificates/block6_reversed_block_clean_kalmanson.json`.
The compact crosswalk
`data/certificates/block6_reversed_block_two_stage_closure.json` verifies the
combined arithmetic for this bounded family: `446` vertex-circle closures plus
`16` Kalmanson clean-row closures cover the `462` reversed-block shuffle
orders.
The follow-up first-block-forward two-orientation crosswalk joins that packet
to the original forward-second-block sweep: `462` forward-second-block
vertex-circle closures plus the `462` reversed-second-block two-stage closures
cover `924` normalized first-block-forward shuffle orders. This is still only
a bounded fixed-order-family diagnostic; it does not include
first-block-reversed orientations, arbitrary cyclic orders, all selected-row
systems, the fragile bridge, or Erdos #97. See
`data/certificates/block6_forward_block_two_orientation_closure.json`.
A further reversal-duality crosswalk generates all four oriented-block shuffle
families and verifies that cyclic reversal maps `forward-forward` to
`reversed-reversed`, and `forward-reversed` to `reversed-forward`. This
transfers the first-block-forward closure counts to `1848` normalized
oriented-block shuffle orders. It is still only bounded block-preserving order
bookkeeping, not arbitrary cyclic-order closure, all selected-row closure, the
fragile bridge, or Erdos #97. See
`data/certificates/block6_oriented_block_reversal_closure.json`.

The block-6 row-depth survivor diagnostics record why still more local bridge
subclaims fail inside the same negative-control family: all `166` clean
fifth-row states admit a clean sixth row, every unordered added-center pair
has clean six-row support, and the low-support branch has many clean seventh
and eighth-row continuations before only `12` clean seven-row states become
eighth-row terminal. This is bounded natural-order proof-mining information,
not a fragile-bridge proof or Euclidean realization claim. See
`docs/block6-fragile-sixth-row-survivor-catalog.md`.

A separate rich-triple closure bridge records that ear-orderability is
equivalent to bootstrap rank at most 3. Failure of that rank condition yields
inclusion-minimal generating cores with deletion closures, private halos, and a
weighted cyclic outside-pair capacity ledger. This is still only bridge
bookkeeping, not a contradiction or counterexample. See
`docs/bootstrap-core-bridge.md`. A follow-up crosswalk applies this ledger to
current fixed-row frontier motifs and records that the audited singleton-rich
cases have rank greater than 3 but still pass the weighted capacity check; see
`docs/bootstrap-core-crosswalk.md`.

The full `n=9` exact-four radius-blocker packet fixes natural order and blocker
`{0,1,2,3}` and quantifies over all exact four-row choices compatible with that
blocker. Its 90 incidence survivors are all vertex-circle obstructed (`70`
self-edges and `20` strict cycles). This is finite packet evidence only, not an
`n=9` proof, a bridge proof, or a counterexample. See
`docs/n9-full-radius-blocker-vertex-circle-packet.md`.

The natural-order `n=9` radius-blocker shape sweep repeats that exact-four
packet over all `10` cyclic-dihedral four-blocker shapes, covering all `126`
labelled four-vertex blockers in the fixed natural order. Its `1,358`
incidence survivors are all vertex-circle obstructed (`1,164` self-edges and
`194` strict cycles). This is still finite packet evidence only, not an `n=9`
proof, a bridge proof, or a counterexample. See
`docs/n9-radius-blocker-shape-sweep.md`.

The order-reduction crosswalk records that any supplied cyclic order and
four-blocker subset for this exact-four packet relabels to natural order by
sending `order[i]` to `i`. Thus arbitrary cyclic-order placements of a
four-blocker reduce to the stored `126` labelled natural-order blocker
coverage, still only within the exact-four packet semantics. See
`docs/n9-radius-blocker-order-reduction.md`.

A bounded richer-class projection pilot enlarges one checked `n=9`
`{0,1,2,3}` obstruction example so each center has one synthetic size-five
rich class. Expanding each larger class to all exact four-subsets gives
`5^9 = 1,953,125` projected selected-row choices; after incidence/order
filters, the single survivor is vertex-circle obstructed. This is only a
forgetful projection diagnostic, not full rich-class quotient replay, not an
`n=9` proof, and not a counterexample. See
`docs/n9-radius-blocker-rich-projection-pilot.md`.

A full rich-class quotient replay now checks the same synthetic size-five
family without choosing exact four-subsets. It unions every center-to-witness
distance in each rich class and generates nested-chord inequalities from the
full class. The resulting quotient has `225` strict edges and is obstructed by
`193` self-edge conflicts. This is one finite rich-class family only, not an
`n=9` proof or bridge proof. See
`docs/n9-radius-blocker-rich-quotient-pilot.md`.

A generated rich-class quotient sweep now repeats the same full replay over
`20` synthetic size-five packets derived from the stored self-edge and
strict-cycle obstruction examples for the `10` natural-order four-blocker
shapes. All `20` generated packets are obstructed by quotient self-edges, with
`3,533` total self-edge conflicts across `4,500` strict edges. This remains
finite packet evidence only, not arbitrary rich-class classification, not an
`n=9` proof, and not a bridge proof. See
`docs/n9-radius-blocker-rich-quotient-sweep.md`.

A bounded rich-extension neighborhood sweep now varies the added labels in
those `20` generated packets. It checks the baseline plus every Hamming-distance
`1` or `2` replacement by radius-blocker-preserving size-five extensions,
covering `5,996` variants. All `5,996` variants are obstructed by quotient
self-edges, with `1,017,368` total self-edge conflicts across `1,349,100`
strict edges. This remains finite neighborhood evidence only, not a full
rich-class catalogue, not an `n=9` proof, and not a bridge proof. See
`docs/n9-radius-blocker-rich-extension-neighborhood.md`.

A one-packet rich-extension product pilot now exhausts the first maximum-size
source packet from that generated family:
`n9_full_exact_four_radius_blocker_shape_U0135_natural_order:self_edge:0`.
It checks all `196,608` radius-blocker-preserving size-five extension variants
for that packet, and all are obstructed by quotient self-edges, with
`33,895,908` total self-edge conflicts across `44,236,800` strict edges. This
is still finite packet evidence only, not the full `20`-packet product, not an
arbitrary rich-class classification, not an `n=9` proof, and not a bridge
proof. See `docs/n9-radius-blocker-rich-extension-product-pilot.md`.

The follow-up all-packet generated-product sweep exhausts the full extension
product over all `20` generated source packets, checking `2,899,968`
radius-blocker-preserving size-five variants. All variants are obstructed by
quotient self-edges, with `467,149,054` total self-edge conflicts across
`652,492,800` strict edges. This is still finite generated-packet evidence
only, not an arbitrary rich-class classification, not an `n=9` proof, and not
a bridge proof. See `docs/n9-radius-blocker-rich-extension-product-sweep.md`.

The generator-independent all-five-rich support catalogue leaves the generated
radius-blocker packets entirely. It enumerates every choice of one size-five
support at each center of a natural-order nonagon: `56^9 =
5,416,169,448,144,896` raw assignments. Using only the two-circle row-pair cap
and the radical-axis crossing rule for two-overlaps, the exact backtracking
search visits `136` assignment nodes and finds `0` complete assignments. This
repo-local subcase says any `n=9` selected-witness counterexample must have at
least one center whose available rich classes are exact-four-only; it is still
not an `n=9` proof, not the adaptive blocker bridge, and not a counterexample.
See `docs/n9-all-five-rich-support-obstruction.md`.

A sharpened rich-support counting lemma now gives a proof-level shortcut for
all-five-rich subcases: for any same-radius supports `R_i`,
`sum_i binom(|R_i|, 2) <= n(n 