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

### Fixed-pattern exact obstructions

Status: `EXACT_OBSTRUCTION`.

The mutual-rhombus midpoint filter kills the fixed selected patterns
`B12_3x4_danzer_lift`, `B20_4x5_FR_lift`, `C20_pm_4_9`, `C16_pm_1_6`,
`C13_pm_3_5`, and `C9_pm_2_4`. The pattern `C17_skew` is killed by an odd
forced-perpendicularity cycle.

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

## Numerical Attempts

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
2. Push the finite incidence/exact pipeline toward `n=9`, or identify the first
   survivor class that blocks scaling.
3. Investigate `C19_skew`, which is not killed by the current mutual-rhombus
   or vertex-circle filters as an abstract incidence pattern.
4. Add interval-arithmetic verification for convexity and distance equations.
