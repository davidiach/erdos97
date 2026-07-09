# Results Ledger

This file is the compact results ledger for what this repository currently
claims, what it has only tested numerically, and what remains open. For the
long-form canonical synthesis and claim reconciliation, read
`docs/canonical-synthesis.md`.

Official/global status: falsifiable/open. This repository claims no general
proof and no counterexample.

Strongest local result: the elementary geometric theorem in
`docs/n8-geometric-proof.md` rules out bad strictly convex polygons with
`n <= 8`. The selected-witness method independently corroborates `n <= 8` in
a repo-local, machine-checked finite-case sense. The 2026-07-09 repository
audit rederived the proof; independent external review remains recommended
before paper-style citation and is not claimed.

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
with order-free strict convex position (every vertex exposed in some
direction, so no assumption that the canonical label order is the boundary
order) are UNSAT, so no class has a strictly convex octagon realization in any
order. In fact 14 of the 15 classes are already UNSAT with no convexity
assumption at all (order-independent); only class 14 needs the exposed-vertex
constraint. This is a second source for both the cyclic-order class and all
fourteen PB+ED classes -- including the four Groebner-dependent ones (`3`,
`4`, `5`, `14`) the SymPy-free recheck skips -- using neither Groebner bases
nor the cyclic-order combinatorics. `EXACT_OBSTRUCTION` (SMT), repo-local
cross-check pending external review; it strengthens but does not replace the
existing artifacts. See `data/certificates/n8_survivors_smt.json`.

### Theorem: geometric exclusion of n <= 8

Status: `REPO_LOCAL_THEOREM`; elementary proof rederived twice in the
2026-07-09 repository audit. Independent external/publication review remains
encouraged and is not claimed.

A short geometric note in `docs/n8-geometric-proof.md` gives an independent
human-readable route to the `n <= 8` exclusion: a base-apex lemma bounds the
number of isosceles triangles by `n(n-2)`, badness gives at least `6n`, and the
saturated octagon case forces an equilateral octagon whose length-3 diagonals
require at least four exterior turns of size `2*pi/3`, contradicting total
turn `2*pi`.

This theorem is now the primary human-readable small-case route. It does not
alter the global status of Erdos Problem #97 or remove the independently useful
machine-checked `n=8` finite-case artifact.

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
window g