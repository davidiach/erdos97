# Initial GitHub Issues

Open these after the repository is public and the label set from `.github/labels.yml` exists.

## Enumerate all n=7 Fano-incidence cyclic labelings up to dihedral symmetry

Labels: `SAT_SMT`, `INCIDENCE_PATTERN`, `EXACTIFICATION`

Goal: enumerate all cyclic labelings of the n=7 equality case, modulo dihedral symmetry, and record the induced perpendicularity constraints.

## Prove or refute B12 degeneration

Labels: `FAILED_APPROACH`, `NUMERICAL_EVIDENCE`, `EXACTIFICATION`

Goal: determine whether the best `B12_3x4_danzer_lift` residual tends to zero only as convexity or edge margins collapse.

## Run B20 margin sweep with anti-clustering constraints

Labels: `NUMERICAL_EVIDENCE`

Goal: repeat the constrained margin sweep for `B20_4x5_FR_lift`, including diagnostics that detect cluster collapse.

## Add interval-arithmetic verifier

Labels: `EXACTIFICATION`

Goal: verify strict convexity and selected distance equalities with interval arithmetic for saved candidates or exact templates.

## Literature sweep for nearby repeated-distance constructions

Labels: `LITERATURE_RISK`

Goal: check Danzer, Fishburn-Reeds, and related repeated-distance-in-convex-polygons literature for existing obstructions or examples.

## Strengthen incidence SAT beyond the pairwise cap

Labels: `SAT_SMT`

Goal: add finite necessary constraints stronger than `|S_a cap S_b| <= 2`, while keeping heuristic filters separate from necessary filters.
