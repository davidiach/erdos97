# FAILED_APPROACH: C3-equivariant doubled-Danzer 18-gon at the 2026-07 base family

Status: FAILED_APPROACH (repo trust taxonomy), supported by
NUMERICAL_EVIDENCE artifacts. No counterexample and no counterexample
candidate is claimed anywhere in this route.

## The route

Double the `k=3` Danzer-type `C3`-symmetric nonagon (two copies
`s in {0,1}`, 18 vertices, 12 slice coordinates) and look for a
`C3`-equivariant deformation that splits every copy pair while giving each
of the 6 center classes four equidistant witnesses from its 6-point pool -
which would make every vertex of a strictly convex 18-gon have four
equidistant other vertices. Model, pools, and conventions:
`src/erdos97/danzer18_doubling.py`; provenance:
`docs/codex-handoff-triage-2026-07-13.md`.

## What was tested (2026-07-22)

1. First-order census at the collision point: all `15^6` witness
   assignments; rank counts `11,206,584 / 182,540 / 1,497 / 4` for ranks
   `9/8/7/6`, matching the external census exactly, with mpmath dps=40 rank
   spot-checks. See `docs/danzer18-doubling-census.md` and
   `data/certificates/danzer18_collision_rank_census.json`.

2. Nonlinear continuation on the 19 externally supplied survivor
   assignments: 528 deterministic Levenberg-Marquardt runs from
   kernel-direction seeds at three family points. See
   `docs/reports/danzer18-continuation-run-2026-07-22.md` and
   `data/certificates/danzer18_survivor_continuation.json`.

3. Second-order obstruction and family scan for the 8 chiral all-split
   survivors (same artifact).

4. Enlarged-pool escape scan along the base family
   (`data/certificates/danzer18_family_coincidence_scan.json`).

## Why the route fails at this base family

- Every one of the 528 continuation runs converges only by collapsing back
  onto the collided manifold (zero runs meet the acceptance criteria
  residual `< 1e-12` with all three copy-pair separations `> 1e-4`).
- Only 8 of the `15^6` assignments (the chiral period-2 family) have
  first-order kernels that split all three copy pairs, and each of them is
  killed at second order: the Lyapunov-Schmidt obstruction
  `|P_coker d^2F[v,v]| = 1.552627` at the base point (mpmath dps=50), and
  stays above `1.5518` at every scanned collided family point
  `t in [-0.6, 0.6]`. Pinned-split residual floors scale as
  `0.33 * eps^2` - a clean quadratic wall, not a solver failure.
- 150,370 of the 184,041 excess-corank assignments have kernels with no
  split component at all; 33,663 more split at most two orbits, and probes
  of those found only single-orbit-split nonlinear branches.
- The one enlarged-pool escape (making the near-coincidence
  `d^2(v0, v4) = 3` exact along the family) does not exist: the family
  terminates in a degenerate triple-covered equilateral triangle at
  `t* ~ 0.3944` and the coincidence becomes exact only in that collapse
  limit.

## What survives the failure

Genuine one-orbit-split nonlinear branches exist (residual polished to
`2.3e-40` at dps=40 for a `(10,0,5,5,0,0)` branch point with orbit-1 pair
split `0.1431` and the other two pairs collided to 40 digits; 40-digit
coordinates stored in the continuation artifact). These 12-distinct-point
configurations are not candidates, but they are concrete seed material for
the non-equivariant follow-up: perturbing them in the full 36-dof,
54-equation system to test whether breaking the `C3` symmetry unlocks
further splitting.

## Claim boundary

This certificate closes only the `C3`-equivariant doubled-Danzer route at
the 2026-07 base family (the scanned strictly convex family window),
against the tested witness-pool structure. Not covered: non-equivariant
perturbations of the doubled configuration, other Danzer-type base
families or cross structures, other doubling patterns, and Erdos Problem
#97 itself, whose official status remains falsifiable/open. Evidence grade
is numerical (float64 continuation with mpmath dps=40..50 confirmation of
ranks, obstructions, and branch points); no exact algebraic certificate is
claimed for the second-order obstruction value.
