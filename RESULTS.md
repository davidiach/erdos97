# Results Ledger

This file is the compact results ledger for what this repository currently
claims, what it has only tested numerically, and what remains open. For the
long-form canonical synthesis and claim reconciliation, read
`docs/canonical-synthesis.md`.

Overall status: Erdős Problem #97 remains open. This repository claims no
proof and no counterexample.

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

### Conditional exactification artifact: reconstructed n=8 survivor classes

Status: `EXACTIFICATION`, `CONDITIONAL`.

A reconstructed canonical list of 15 `n=8` incidence survivor classes was tested
by exact cyclic-order and perpendicular-bisector filters. The cyclic-order
noncrossing filter kills 1 class. The remaining 14 classes are killed by exact
perpendicular-bisector algebra, full equal-distance algebra where needed, or
strict-convexity failure. No floating-point equality or numerical search is
used.

This is not promoted to an unconditional theorem in the ledger because the
reconstructed JSON must still be tied to the original survivor-enumeration
provenance. In this workspace, the reconstructed classes were matched up to
simultaneous relabeling against the archived
`erd archive/outputs/data/n8_exact_geometry_filter_results.json` artifact. See
`docs/n8-exact-survivors.md` and `certificates/n8_exact_analysis.json`.

## Numerical Attempts

### B12_3x4_danzer_lift

Status: near-miss degeneration, rejected as counterexample.

Diagnostics:

- max selected-distance spread: `0.006806368780585714`
- RMS equality residual: `0.0019599509549614457`
- convexity margin: `9.999999943508973e-07`
- minimum edge length: `0.0007465865604262556`
- verifier status at tolerance `1e-6`: rejected

Interpretation:

The residual improves as the polygon approaches a three-cluster degeneration.
This is evidence about a failed route, not a solution.

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

1. Confirm the `n=8` archive provenance and independently review the class
   `3`, `4`, and `14` exact certificates.
2. Prove or refute degeneration for `B12_3x4_danzer_lift`.
3. Run a `B20_4x5_FR_lift` anti-clustering margin sweep.
4. Add interval-arithmetic verification for convexity and distance equations.
5. Strengthen the incidence SAT/SMT abstraction beyond the pairwise cap.
