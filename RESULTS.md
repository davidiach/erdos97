# Results Ledger

This file is the compact source of truth for what this repository currently
claims, what it has only tested numerically, and what remains open.

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

### Conditional structure: n=7 equality case

Status: proved as an incidence consequence; geometric impossibility unresolved.

For `n=7`, equality in the incidence count forces all indegrees to be 4 and
every pair of selected 4-sets to intersect in exactly 2 points. The complements
`T_i = V \ S_i` form a Fano-plane-like family of 3-sets. If
`S_i cap S_j = {a,b}`, then segment `p_a p_b` is perpendicular to segment
`p_i p_j` by the radical-axis theorem.

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

## Open Subproblems

1. Enumerate all `n=7` Fano-incidence cyclic labelings up to dihedral symmetry.
2. Prove or refute degeneration for `B12_3x4_danzer_lift`.
3. Run a `B20_4x5_FR_lift` anti-clustering margin sweep.
4. Add interval-arithmetic verification for convexity and distance equations.
5. Strengthen the incidence SAT/SMT abstraction beyond the pairwise cap.
