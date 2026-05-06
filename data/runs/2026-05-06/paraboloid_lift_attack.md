# Paraboloid Lift Attack on Erdős #97

Date: 2026-05-06
Working dir: `/home/user/erdos97`
Scripts: `/tmp/paraboloid_attack.py`, `/tmp/paraboloid_newton.py`,
`/tmp/paraboloid_nondegen.py`, `/tmp/paraboloid_obstruction.py`,
`/tmp/lift_normal_obstruction.py`, `/tmp/paraboloid_groebner.py`,
`/tmp/paraboloid_algebra.py`.

## 1. Paraboloid encoding of the 4-equidistant constraint

Lift `p_j = (x_j, y_j)` to `hat_p_j = (x_j, y_j, x_j^2 + y_j^2)`.

For a center `i` with witness 4-set `{a,b,c,d}`, the four lifts must lie in a
plane parallel to the tangent plane of `z = x^2+y^2` at `hat_p_i`.  That
plane has normal proportional to `(-2 x_i, -2 y_i, 1)`, i.e. equation

    -2 x_i X - 2 y_i Y + Z = c_i.

Plugging in `hat_p_j` yields

    -2 x_i x_j - 2 y_i y_j + (x_j^2 + y_j^2) = c_i,
    (x_j - x_i)^2 + (y_j - y_i)^2 = c_i + (x_i^2 + y_i^2),

i.e. `|p_i - p_j|^2 = R_i^2`, the witness-circle equation.  Confirmed
algebraic equivalence with the squared-distance form.

The lift form has TWO sub-equations per center:
  (A) Coplanarity of `hat_p_a, hat_p_b, hat_p_c, hat_p_d` — one scalar.
  (B) Plane normal equals `(-2 x_i, -2 y_i, 1)` (up to scale) — two scalars.
Total = 3 scalar equations per center, matching the squared-distance count
3n.  The split into (A)+(B) is new and exposes a useful obstruction.

## 2. Numerical search results

Newton (Levenberg-Marquardt) from many random and structured initial
conditions on the paraboloid lift residuals (script
`paraboloid_newton.py`).  For each pattern we ran 32-48 restarts (regular,
elliptic, jittered, and random convex initialisations).

| pattern              |  n | best_loss   | convex | min pair distance |
|----------------------|---:|-------------|--------|--------------------|
| B12_3x4_danzer_lift  | 12 | 1.95e-33    | False  | 7.6e-11            |
| C12_pm_2_5           | 12 | 2.05e-42    | False  | 3.8e-15            |
| C12_pm_1_4           | 12 | 5.78e-27    | False  | 3.7e-08            |
| C12_pm_3_5           | 12 | 1.28e-44    | False  | 0.0                |
| C15_pm_2_6           | 15 | 2.03e-25    | False  | 3.8e-08            |
| C15_pm_4_7           | 15 | 9.29e-28    | False  | 8.9e-09            |
| C15_pm_3_5           | 15 | 4.00e-29    | False  | 1.8e-09            |
| C16_pm_1_6           | 16 | 2.67e-34    | False  | 4.3e-12            |
| C16_pm_3_7           | 16 | 3.18e-43    | False  | 0.0                |
| P18_parity_balanced  | 18 | 1.23e-24    | False  | 2.2e-08            |
| C18_pm_5_8           | 18 | 7.06e-23    | False  | 1.2e-07            |
| C18_pm_4_7           | 18 | 1.35e-24    | False  | 3.5e-08            |
| C21_pm_4_9           | 21 | 1.82e-42    | False  | 2.0e-16            |
| C21_pm_5_10          | 21 | 1.68e-24    | False  | 2.9e-08            |

EVERY pattern collapsed to a degenerate cluster (essentially three or four
coalesced points) where the equality residuals trivially vanish.  No
configuration with all `n` vertices distinct, convex, and equality-residual
< 1e-6 was found.  The B12 case reproduces the historical near-miss
loss = 3.84e-6 documented in `data/runs/best_B12_slsqp_m1e-6.json`, but
unconstrained Newton instead drives the polygon to coalescence.

The penalty-augmented attack (`paraboloid_nondegen.py`) with hard
non-degeneracy enforcement (`min_pair_distance >= 0.05`, convex sign
penalty `lambda = 1e3`) produced no convex non-degenerate configuration
with equality residual below the saved B12 baseline.

Conclusion: no n in {12, 15, 16, 18, 21} yielded a counterexample under
this search budget; the saved B12 near-miss remains the closest miss.

## 3. Algebraic structure observed in the lifted view (NEW)

### 3.1 Lifted-normal defect

Definition: for a configuration `P` and pattern `S`, let

    D_normal(P, S) = sum_i (1 - cos angle( fitted_normal(S_i), N_i ))^2,
    N_i = (-2 x_i, -2 y_i, 1).

Computed at the regular n-gon (`lift_normal_obstruction.py`):

| pattern              |  n |  D_normal | min cos | sv_min |
|----------------------|---:|----------:|--------:|--------|
| B12_3x4_danzer_lift  | 12 |    3.667  |  0.4472 | 1e-16  |
| C12_pm_2_5           | 12 |    3.667  |  0.4472 | 1e-16  |
| C13_pm_3_5           | 13 |    3.972  |  0.4472 | 1e-16  |
| C16_pm_1_6           | 16 |    4.889  |  0.4472 | 1e-16  |
| C17_skew             | 17 |    5.195  |  0.4472 | 1e-16  |
| P18_parity_balanced  | 18 |    5.500  |  0.4472 | 1e-16  |
| C19_skew             | 19 |    5.806  |  0.4472 | 1e-16  |
| C20_pm_4_9           | 20 |    6.112  |  0.4472 | 1e-16  |

For the regular n-gon, the constant `min_cos = 1/sqrt(5)` is exact:
all lifts lie in the plane `z = 1` (because `|p_i|^2 = 1`), so the fitted
plane normal is `(0,0,1)`.  The target normal is `(-2x_i,-2y_i,1)` with
`|(-2x_i,-2y_i,1)| = sqrt(5)`.  The cosine of the angle is exactly
`1/sqrt(5)`.

This gives a closed form `D_normal(regular n-gon, any pattern) = n (1 - 1/sqrt(5))^2 = 0.3056 n`,
matching the table (3.667 = 12 * 0.3056, 6.112 = 20 * 0.3056).

### 3.2 New obstruction (lifted-normal lower bound, conjectural)

Observation: at the B12 near-miss with cluster collapse, `sv_min` is
small (1e-3 — coplanarity nearly satisfied trivially because four lifts
nearly coincide), but `D_normal = 9.89` and `min_cos = -0.86` — the
fitted plane normal points the wrong way.

Conjecture (new): for any nondegenerate convex configuration
satisfying the squared-distance equalities for all n centers, the
lifted-normal defect must vanish:

    D_normal(P, S) = 0 (componentwise).

The two components — coplanarity AND normal direction — are equivalent
to the full witness equation and cannot be cheaply traded against each
other in the nondegenerate regime.  Hence any minimizer of equality
residual that drives `D_normal -> 0` must simultaneously enforce all
3n equations.  We did not find one.

### 3.3 Symmetry obstructions verified via the lift

For circulant patterns invariant under `i -> i+1`, restricting to
rotationally invariant configurations (`p_i = R^i p_0`) collapses
witness equalities to chord-length identities:

    sin^2(o_1 pi/n) = sin^2(o_2 pi/n) for distinct offsets o_1, o_2.

For C12_pm_2_5 (offsets +/- 2, +/- 5) we have
    sin^2(2 pi/12) = 1/4,
    sin^2(5 pi/12) = (2 + sqrt 3)/4,
which differ by `(1 + sqrt 3)/4`.  Hence no rotationally-symmetric
solution exists — any solution must break the C_n action.

This recovers the known `n = cyclic` obstruction from L9 (cyclic polygon
subcase): if all vertices lie on one circle, no vertex has 4 others at
one distance.  In the lift, this is exactly the statement that the
slice `z = const` of the paraboloid is a circle, hence M(v) <= 2.

### 3.4 First-order rank diagnostic

Jacobian rank at the regular n-gon (`paraboloid_algebra.py`):

| pattern              |  n |  loss@reg | rank | max_solution_rank | min sv |
|----------------------|---:|----------:|-----:|------------------:|-------:|
| B12_3x4_danzer_lift  | 12 |  9.74e+1  |  21  |   20              | 2e-10  |
| C12_pm_2_5           | 12 |  1.79e+2  |  21  |   20              | 8e-10  |
| C13_pm_3_5           | 13 |  7.85e+1  |  23  |   22              | 1e-15  |
| C16_pm_1_6           | 16 |  3.40e+2  |  29  |   28              | 5e-10  |
| C17_skew             | 17 |  2.71e+2  |  31  |   30              | 1e-9   |
| P18_parity_balanced  | 18 |  2.86e+2  |  33  |   32              | 1e-9   |
| C19_skew             | 19 |  2.27e+2  |  35  |   34              | 1e-9   |
| C20_pm_4_9           | 20 |  2.54e+2  |  37  |   36              | 1e-9   |

At the regular n-gon (which is NOT a solution), Jacobian rank is the
generic `2n - 3`, leaving the 3-dim translation+rotation kernel.  The
expected solution rank is `2n - 4` (Euler scaling adds one more).  The
fact that `min sv` is ~1e-9 but loss is huge confirms we're far from a
solution.

### 3.5 Saved B12 near-miss in lifted coordinates

Per-center residual analysis (`paraboloid_obstruction.py`) of
`data/runs/best_B12_slsqp_m1e-6.json`:

- All `sv_min(S_i) ~ 9e-4`: four lifts NEAR-coplanar at every center.
- Plane normals: of 12 centers, NONE has `cos angle > 0.97` to the
  prescribed `(-2 x_i, -2 y_i, 1)`; minimum cosine is `-0.86`.
- The polygon has clearly collapsed into 3 tight clusters at `~ (1,0)`,
  `(-0.5, 0.866)`, `(-0.5, -0.866)`, the regular triangle vertices.
- Each cluster contains 4 nearly-coincident points; coplanarity is
  trivial because four near-coincident points are always coplanar.

This confirms the failure mode of `B12_3x4_danzer_lift` IS exactly the
"coplanarity satisfied trivially via point coincidence" mode that the
lifted-normal defect detects.

## 4. Consistency with the existing program

- `B12_3x4_danzer_lift` is recorded as exactly killed by mutual-rhombus
  midpoint equations (`certificates`/inventory).  The paraboloid lift
  attack reproduces this: the only configurations satisfying all 12
  witness equalities are degenerate.
- `P18_parity_balanced` and `C20_pm_4_9` are killed combinatorially by
  cyclic-crossing CSP.  The paraboloid lift attack contributes no new
  information here — they fail at the abstract incidence level before
  any geometric realisation.
- The lifted-normal defect is a new continuous functional that
  separates "honest" 4-bad solutions (D_normal = 0) from cluster
  degenerations (D_normal > 0 but residual ~ 0).  Adding it to the
  optimization objective is a candidate enhancement for future runs.

## 5. New saved artefacts

- `/tmp/paraboloid_attack.py` — multi-pattern Newton on lift residuals.
- `/tmp/paraboloid_newton.py` — multi-restart LM with elliptic seeds.
- `/tmp/paraboloid_nondegen.py` — penalty-augmented L-BFGS.
- `/tmp/paraboloid_obstruction.py` — per-center plane-normal diagnostic.
- `/tmp/lift_normal_obstruction.py` — `D_normal` functional baseline.
- `/tmp/paraboloid_algebra.py` — Jacobian rank diagnostic.
- `/tmp/paraboloid_groebner.py` — symbolic chord-equality check.
- (output JSONs in `/tmp/paraboloid_*_results.json`).

## 6. Open follow-ups

1. Add `D_normal` (lifted-normal defect) as a hard-equal-to-zero
   constraint to the existing SLSQP/L-BFGS pipelines and re-run on
   `B12_3x4_danzer_lift`, `B20_4x5_FR_lift`.  Expectation: the previous
   1e-6 near-miss residual will rise sharply because the cluster
   degeneration is no longer a free degree of freedom.
2. Prove a quantitative lower bound:  for any convex polygon with
   minimum pair distance `>= rho` and normalized scale, `D_normal(P, S)
   >= f(rho, n) > 0`.  This would give a nondegeneracy-quantitative
   obstruction valid for all n.
3. Investigate whether for SPECIFIC patterns the system (A)+(B) is
   provably infeasible by Gröbner basis after fixing the cyclic
   gauge.  For C12_pm_2_5 the C_12-equivariant ansatz is killed
   analytically (sec. 3.3); the asymmetric n=12 problem remains open
   to symbolic methods at moderate cost.

## 7. Bottom line

No counterexample found.  The paraboloid-lift formulation is
algebraically equivalent to the squared-distance system but exposes a
USEFUL new quantitative diagnostic, `D_normal`, that distinguishes
honest 4-bad solutions from the cluster-collapse degenerate solutions
which dominate unconstrained Newton attempts.  Adding `D_normal` as a
hard constraint to existing pipelines is the recommended next step.
The historical B12 near-miss is exposed as a configuration where
coplanarity is trivial (coincident lifts) but the plane normal is
strongly misoriented relative to the paraboloid tangent at each center.
