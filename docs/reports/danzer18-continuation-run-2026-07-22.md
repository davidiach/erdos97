# Doubled-Danzer 18-gon: continuation run report (2026-07-22)

Status: NUMERICAL_EVIDENCE / FAILED_APPROACH support. No counterexample and
no counterexample candidate is claimed. This report records the decisive
continuation test on the 19 externally supplied survivor assignments for the
C3-equivariant doubling of the Danzer-type nonagon, together with the
first-order census reproduction and the follow-up family diagnostics.

Companion documents and artifacts:

- `docs/danzer18-doubling-census.md` (census NUMERICAL_EVIDENCE note)
- `docs/danzer18-doubling-failed-approach.md` (FAILED_APPROACH certificate)
- `data/certificates/danzer18_collision_rank_census.json`
- `data/certificates/danzer18_survivor_continuation.json`
- `data/certificates/danzer18_family_coincidence_scan.json`
- Scripts: `scripts/check_danzer18_base_nonagon.py`,
  `scripts/check_danzer18_collision_census.py`,
  `scripts/check_danzer18_survivor_continuation.py`,
  `scripts/check_danzer18_family_coincidences.py`
- Shared model: `src/erdos97/danzer18_doubling.py`

## Step 1: base nonagon rebuilt and verified

`python scripts/check_danzer18_base_nonagon.py --check --json` at mpmath
dps=60:

- Newton polish of the supplied seed converges to cross-witness residuals
  below `4e-61` (threshold `1e-50`).
- All nine points are strict hull vertices; cyclic boundary order matches
  the external record `[2, 4, 8, 0, 5, 6, 1, 3, 7]`; minimum exterior turn
  `0.3957` (threshold `0.01`); minimum vertex distance `0.0471`.
- The gauge-fixed 6x4 Jacobian has singular values
  `(7.57, 4.91, 2.47, 1.7e-31)`: rank 3, so the nonagon sits in a
  1-parameter family. The recorded near-coincidence is
  `d^2(v0, v4) = 2.9977804311`.

## Step 2: collision rank census reproduced exactly

`python scripts/check_danzer18_collision_census.py --full --write-artifact`
(float64 batched SVD, relative rank tolerance `1e-8`; trivial kernel =
rotation + scaling + diagonal base-family flex projected out):

| projected rank | count      | external count | match |
|----------------|------------|----------------|-------|
| 9 (no excess)  | 11,206,584 | 11,206,584     | yes   |
| 8              | 182,540    | 182,540        | yes   |
| 7              | 1,497      | 1,497          | yes   |
| 6              | 4          | 4              | yes   |

The four rank-6 assignments are exactly the external ones
`(0,0,0,0,0,0)`, `(0,0,0,0,5,5)`, `(0,0,5,5,0,0)`, `(5,5,0,0,0,0)`, and
`(5,5,5,5,5,5)` has rank 9 (zero excess), which resolves the 2026-07-13
bisector-cycle question negatively at first order. An mpmath dps=40 rank
spot-check over a fixed 12-assignment sample confirms every flagged rank
(null singular values around `1e-40`, spectral gaps of order 1), ruling out
float artifacts.

## Step 3 preflight: the 19-survivor filter does NOT reproduce as described

Split-support classification of all 184,041 excess-corank assignments
(nontrivial kernel projections onto the three anti-diagonal split planes,
stable under tolerance sweeps `1e-4` to `1e-10`):

| split-support size | count   |
|--------------------|---------|
| 0 orbits           | 150,370 |
| 1 orbit            | 33,075  |
| 2 orbits           | 588     |
| 3 orbits           | 8       |

Exactly 8 assignments have nontrivial kernels with nonzero components on
all three orbit splitting directions: the chiral period-2 family
`(1,2,1,2,1,2)`, `(1,2,2,1,2,1)`, `(2,1,1,2,2,1)`, `(2,1,2,1,1,2)`,
`(3,4,3,4,3,4)`, `(3,4,4,3,4,3)`, `(4,3,3,4,4,3)`, `(4,3,4,3,3,4)`.
These are 8 of the 19 externally supplied survivors. The other 11 external
survivors do not satisfy the stated first-order criterion under the
documented conventions: their kernels have split support on at most one
orbit, and five of them (`(1,10,0,0,9,0)`, `(4,6,0,0,3,1)`,
`(5,4,0,0,12,7)`, `(11,0,0,0,10,14)`, `(13,1,4,3,0,0)`) have purely
diagonal nontrivial kernels with no split component at all. The tuple
conventions themselves are pinned by the exact census reproduction above
(in particular the asymmetric rank-6 list), so this is a genuine
discrepancy with the external filter description, not a labeling mismatch.
All 19 were nevertheless run through the full continuation test below.

## Step 3: continuation on all 19 survivors - all negative

`python scripts/check_danzer18_survivor_continuation.py --write-artifact`.
Deterministic LM continuation (fixed RNG seeds 97/1897), seeds
`slide(t) + eps * v` over every nontrivial kernel direction (and seeded
in-kernel combinations where the kernel dimension exceeds 1),
`eps in {1e-3, 1e-2, 5e-2, 1e-1}`, `t in {0, +0.1, -0.1}`:
528 runs total. Acceptance required residual `< 1e-12` AND all three
copy-pair separations `> 1e-4`.

Result: 528/528 runs converge to machine residual and 528/528 COLLAPSE
back onto the collided manifold. Zero acceptance-criteria candidates.

Per-survivor verdicts (best run = converged run with largest minimum pair
separation):

| assignment        | rank | ker dim | kernel split support | runs | best residual | best min pair sep | verdict |
|-------------------|------|---------|----------------------|------|---------------|-------------------|---------|
| (1,2,1,2,1,2)     | 8    | 1       | all three            | 24   | 1.1e-15       | 1.3e-08           | FAILED (collapse) |
| (1,2,2,1,2,1)     | 8    | 1       | all three            | 24   | 1.8e-15       | 1.7e-08           | FAILED (collapse) |
| (1,3,11,1,5,5)    | 8    | 1       | orbit 2 only         | 24   | 2.2e-15       | 4.3e-16           | FAILED (collapse) |
| (1,10,0,0,9,0)    | 8    | 1       | none (diagonal)      | 24   | 8.9e-16       | 0.0               | FAILED (collapse) |
| (2,1,1,2,2,1)     | 8    | 1       | all three            | 24   | 1.8e-15       | 2.1e-08           | FAILED (collapse) |
| (2,1,2,1,1,2)     | 8    | 1       | all three            | 24   | 4.4e-16       | 1.3e-08           | FAILED (collapse) |
| (3,4,3,4,3,4)     | 8    | 1       | all three            | 24   | 2.2e-15       | 2.0e-08           | FAILED (collapse) |
| (3,4,4,3,4,3)     | 8    | 1       | all three            | 24   | 1.3e-15       | 5.4e-09           | FAILED (collapse) |
| (4,3,3,4,4,3)     | 8    | 1       | all three            | 24   | 2.7e-15       | 2.2e-08           | FAILED (collapse) |
| (4,3,4,3,3,4)     | 8    | 1       | all three            | 24   | 1.3e-15       | 2.2e-08           | FAILED (collapse) |
| (4,6,0,0,3,1)     | 8    | 1       | none (diagonal)      | 24   | 8.9e-16       | 0.0               | FAILED (collapse) |
| (5,4,0,0,12,7)    | 8    | 1       | none (diagonal)      | 24   | 8.9e-16       | 0.0               | FAILED (collapse) |
| (5,5,6,10,6,11)   | 8    | 1       | orbit 0 only         | 24   | 1.3e-15       | 1.6e-16           | FAILED (collapse) |
| (5,5,10,1,6,12)   | 8    | 1       | orbit 0 only         | 24   | 1.3e-15       | 3.1e-16           | FAILED (collapse) |
| (6,11,5,5,1,10)   | 8    | 1       | orbit 1 only         | 24   | 2.2e-15       | 3.0e-16           | FAILED (collapse) |
| (10,0,5,5,0,0)    | 7    | 2       | orbit 1 only         | 96   | 1.8e-15       | 1.8e-16           | FAILED (collapse) |
| (10,8,5,5,2,11)   | 8    | 1       | orbit 1 only         | 24   | 1.8e-15       | 4.5e-16           | FAILED (collapse) |
| (11,0,0,0,10,14)  | 8    | 1       | none (diagonal)      | 24   | 8.9e-16       | 0.0               | FAILED (collapse) |
| (13,1,4,3,0,0)    | 8    | 1       | none (diagonal)      | 24   | 1.8e-15       | 1.7e-16           | FAILED (collapse) |

The best minimum separations of order `1e-8` for the chiral family are
exactly `sqrt(residual tolerance)` and are the signature of a quadratic
collapse, not of a nearby split branch. Convexity margins were not reached
by any run: every converged endpoint is a collided configuration whose
deduplicated 9-point hull is the (strictly convex) base-family nonagon, so
criterion 4 was never in play; criteria 2/3 already fail everywhere.

## Why the negative is structural, not a solver failure

Three independent diagnostics in the continuation artifact:

1. Pinned-split residual floors. Minimizing the 18-equation residual on
   the affine slice where the anti-diagonal split component is pinned to
   `eps` (with scaling and rotation gauges pinned; without the gauge pin LM
   escapes by shrinking the whole configuration to the origin, which
   makes every residual vanish identically - a degenerate artifact, noted
   and excluded) gives, for all 8 chiral survivors,

       floor(eps) = kappa * eps^2,  kappa in [0.327, 0.335],

   with log-log slope 2.00 over `eps in [1e-3, 1e-1]`. A genuine all-split
   branch would drive the floor to zero.

2. Second-order Lyapunov-Schmidt obstruction. For each chiral survivor
   with all-split kernel direction v (unit), the cokernel projection of the
   second derivative, `|P_coker d^2F[v, v]|`, equals `1.552627` at the base
   point, recomputed in mpmath at dps=50 (kernel direction refined to
   `|J v| ~ 9e-31`; kernel singular gap `0.431` vs `1.8e-30`). A smooth
   branch tangent to v requires this projection to vanish; it is bounded
   away from zero by 1.55.

3. Family scan. The same obstruction, recomputed at 25 collided family
   points `t in [-0.6, 0.6]` (the strictly convex part of the scanned
   window; the family degenerates at `t ~ 0.394`, see below), stays in
   `[1.5518, 1.72]` for all 8 chiral survivors and attains its minimum
   near `t = -0.05`. No sign change and no approach to zero: no all-split
   branch bifurcates anywhere along the scanned family.

For the 11 non-chiral survivors the pinned floors scale linearly
(first-order obstruction, `kappa`-equivalents up to `3e+3`), consistent
with their kernels having no all-orbit split component.

## Genuine partial branches (one orbit split) - near-miss material

The pinned-split diagnostic did find real nonlinear branches, but only
with exactly ONE orbit pair split: for `(1,3,11,1,5,5)`,
`(5,5,6,10,6,11)`, `(5,5,10,1,6,12)`, `(6,11,5,5,1,10)`,
`(10,0,5,5,0,0)`, `(10,8,5,5,2,11)` (and, off the 19-list, for sampled
two-orbit-support census assignments) the floor reaches machine zero with
one pair split by about `0.14` while the other two copy pairs collide
exactly. A representative branch point for `(10,0,5,5,0,0)` is polished in
mpmath to residual `2.3e-40` at dps=40 and stored with 40-digit
coordinates in the continuation artifact: orbit-1 pair split `0.1431`,
orbit-0 and orbit-2 pairs collided to all 40 digits. These configurations
have only 12 distinct points and are NOT candidates; they are recorded as
seed material for the non-equivariant (full 36-dof, 54-equation) follow-up
(extension c of the task).

A bounded probe of the 588 two-orbit-support census assignments (8 fixed
samples) found no two-orbit-split branch: every machine-zero floor again
had exactly one orbit split.

## Extension a: no valid enlarged-pool family point exists

`python scripts/check_danzer18_family_coincidences.py --write-artifact`:
sliding along the 1-parameter family, the minimum vertex distance shrinks
monotonically (0.047 at t=0, 5e-6 at t=0.39) and the family terminates at
a degenerate endpoint `t* ~ 0.3944042` where the polished configuration is
a triply covered equilateral triangle (`r -> (1,1,1)`,
`phi -> (0, 2pi/3, 0)`). The recorded near-coincidence
`d^2(v0, v4) - 3 = -2.2e-3` at the base point tends to zero only in this
collapse limit and stays strictly negative at every nondegenerate family
point; all four sign-change roots found in the scan window lie at the
degenerate endpoint (minimum vertex distance below 1e-6 at each root).
Consequently there is no nondegenerate family point where the witness
pools enlarge, and the planned enlarged-pool census has no valid base
point on this family branch.

## Verdict

FAILED_APPROACH (repo trust taxonomy) for the C3-equivariant doubled-
Danzer 18-gon route at this base family:

- 0 of 19 survivors produce an acceptance-criteria candidate;
- the only first-order-eligible survivors (the 8 chiral period-2
  assignments) are killed by a second-order obstruction bounded below by
  1.55 across the entire strictly convex part of the scanned base family;
- the remaining 11 survivors fail already at first order under the
  documented conventions (filter discrepancy documented above);
- the enlarged-pool escape (extension a) does not exist on this family;
- the surviving interesting structure - genuine one-orbit-split branches -
  is recorded with 40-digit coordinates for the non-equivariant follow-up.

Not claimed: anything about non-equivariant perturbations, other base
families, other doubling structures, or Erdos Problem #97 itself.
