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

Status: proved.

In any true counterexample, for distinct centers `a,b`,
`|S_a cap S_b| <= 2`. Otherwise two distinct circles would share at least
three points.

### Lemma: incidence counting gives n >= 7

Status: proved.

The directed 4-out incidence pattern and the pairwise cap imply no
counterexample can have `n <= 6`; the convexity-of-indegree count gives
`n >= 7`.

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

### Lemma: minimal-counterexample critical tie

Status: proved.

In a counterexample with the minimum possible number of vertices, every vertex
`x` is essential to some remaining vertex `y`: deleting `x` makes `y` good, so
`x` lies in the unique distance class of size exactly 4 at `y`. This is a
structural condition on minimal counterexamples, not a contradiction by itself.

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
review is still recommended before paper-style or public theorem claims.

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
rectangle-trap filter, leaving 1 `accepted_frontier` incidence/order pattern
for later filters. This is a bounded diagnostic slice only, not an `n=9`
completeness theorem. See `docs/n9-incidence-frontier.md` and
`scripts/check_n9_incidence_frontier.py`.

### Review-pending exhaustive n=9 vertex-circle check

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`.

The new repo-native checker in `scripts/check_n9_vertex_circle_exhaustive.py`
enumerates all 70 row-0 selected-witness choices for a cyclically labelled
nonagon. With vertex-circle pruning enabled it visits 16,752 nodes and leaves
0 full assignments. Its cross-check disables vertex-circle pruning during
branching, finds 184 full assignments passing the pair/crossing/count filters,
then classifies all 184 as exact vertex-circle obstructions: 158 self-edges and
26 strict cycles.

This is a candidate extension of the repo-local finite-case pipeline to `n=9`,
but it is not yet the source-of-truth strongest result. The raw incoming bundle
also contains 184-pattern/16-orbit and 102-certificate Kalmanson verifier
variants whose symmetry conventions need separate review. See
`docs/n9-vertex-circle-exhaustive.md`,
`data/certificates/n9_vertex_circle_exhaustive.json`, and
`incoming/archive-output-2026-05-03/`.

### Review-pending second-source proof: n=8 and n=9 Gröbner basis

Status: `MACHINE_CHECKED_ALGEBRAIC_PROOF_REVIEW_PENDING`.

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
generator `y_8^2 + 1/4 = 0` ruling out real solutions. Families F07, F08,
F09, F13 (orbit total 16) have nontrivial zero-dimensional ideals; every
real solution sympy returns has 5+ vertices coinciding, reducing to only
4 distinct points `{(0,0), (1,0), (±1/2, ±sqrt(3)/2)}` — no
non-degenerate Euclidean realization. Combined: all 184 labelled n=9
assignments are unrealizable as strictly-convex 9-gons by algebraic
geometry alone (≈32 s wall-clock total). Artifact:
`data/certificates/2026-05-05/n9_groebner_results.json`.

This complements the existing vertex-circle filter — which independently
kills all 184 n=9 patterns by geometric strict-monotonicity arguments —
and gives the n=9 selected-witness result two-source verification. The
overall n=9 finite case is the strongest multi-source local result in
this repository, conditional on independent reviewer audit of both the
vertex-circle implementation and the Gröbner real-root / non-degeneracy
decoders.

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
the n=9 vertex-circle counts and reruns row0 singleton `0`, but the full n=10
search still needs independent implementation review or a compact replayable
certificate format before any public theorem-style use. It is not promoted to
the source-of-truth strongest result. See
`docs/n10-vertex-circle-singleton-slices.md`.

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

## Numerical Attempts

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
not as an exact obstruction. The pattern remains an `INCIDENCE_PATTERN`, and the
run artifacts are `NUMERICAL_EVIDENCE` only. See `docs/sidon-patterns.md` and
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
