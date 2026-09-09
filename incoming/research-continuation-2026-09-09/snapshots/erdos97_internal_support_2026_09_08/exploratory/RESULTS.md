# Moving-coordinate exploration: retained outcomes and exact status corrections

**No numerical configuration in this directory is a counterexample or a live
near-exact candidate. No finite scan establishes a family-wide exclusion.**

## Model and source

This is a separate moving-coordinate branch, not a perturbation of the fixed
nine-point P used in the cap theorem. The initializer uses the repository's
numerical Danzer-type nonagon at commit
`047d05149382e48b602b292df4b8fc9e2da560bb`, from
`src/erdos97/danzer18_doubling.py` and
`scripts/check_danzer18_base_nonagon.py`.

Each old numerical point is replaced by three points on a short outer arc.
Independent arc-fraction perturbations break C3 symmetry. During numerical
optimization all 27 physical points can move, except for the four real
similarity gauges fixing two well-separated points. Free coordinates have
bounds [-3,3] in that normalized coordinate system. The cluster order and the
three-original-target-cluster witness pools remain restricted throughout.
Each chosen row is held fixed within its coordinate optimization; this is not
an optimizer that searches all possible rows continuously.

The exact pair-capacity lemma excludes two copies under these pool assumptions.
At three copies it forces the 2+1+1 split, leaving 81 rows per physical center
and 2,187 binary selection variables. The direct pattern selector imposes 270
same-side witness-pair capacity constraints. Every selected pattern is checked
using integer cyclic-order and circle-sharing tests outside the optimizer.

## Initial pattern selection and four geometry runs

Two earlier lazy-cut selection runs (`moving_seed_271.json` and
`moving_seed_811.json`) ended after 50 rounds without a pattern passing all
of the circle/crossing tests. They are algorithmic non-completions, not exact
infeasibility certificates.

The direct same-side model produced a pattern interactively; its rows are in
`triple_pattern_candidate.json`. The retained optimizer-result metadata are
in `initial_interactive_milp_metadata.json`. The full original solver log and
its exact wall time were not retained and are not reconstructed. A time-limit
solver status is not a proof of optimality; the finite rows are independently
checkable regardless of how they were found.

Four completed coordinate optimizations followed:

| Run seed | Arc scale | Pattern source | Maximum normalized squared-distance difference | Final minimum pair distance |
|---|---:|---|---:|---:|
| 271 | 0.03 | retained interactive pattern | 0.001486677643133261 | 0.00046552289839338085 |
| 811 | 0.08 | same retained pattern | 0.003217669981452299 | 0.000999999999997452 |
| 405 | 0.06 | direct model, distinct pattern | 0.0033673747079601434 | 0.0008341748551475358 |
| 912 | 0.15 | direct model, distinct pattern | 0.0033088061034499414 | 0.0009999999999999582 |

Normalization divides each squared-distance difference by the initial mean
squared witness distance for its row. These numbers are not relative errors
against a certified final radius. Every run reached its imposed minimum pair
separation, within the optimizer's numerical feasibility tolerance. All final
supporting determinants were positive numerically, but the required area
bounds had tiny negative numerical slacks. None had zero distance residual.
The optimizer's successful termination means local numerical termination,
not satisfaction of the original exact equations.

The code checks analytic derivatives against centered differences before
optimization. It retains initial/final coordinates, rows, gauges, constraints,
iterations, timings, residuals, and actual rather than presumed hull margins.
The source SHA256 for these four invocations is

```
b5d779fd63dfecb1847c169ba94253c4c24ca42e884f9cfba70403734b99c54b
```

Actual command forms, from the packet root (the original environment used
`/opt/pyvenv/bin/python -S`, with its site-packages directory in PYTHONPATH):

```
python exploratory/moving_seed.py --seed 271 --epsilon .03 --pattern exploratory/triple_pattern_candidate.json --output exploratory/moving_realization_271.json
python exploratory/moving_seed.py --seed 811 --epsilon .08 --pattern exploratory/triple_pattern_candidate.json --output exploratory/moving_realization_811.json
python exploratory/moving_seed.py --seed 405 --epsilon .06 --direct --output exploratory/moving_realization_405.json
python exploratory/moving_seed.py --seed 912 --epsilon .15 --direct --output exploratory/moving_realization_912.json
```

The tested numerical environment was Python 3.13.5, NumPy 2.3.5 and SciPy
1.17.0, with BLAS/OpenMP thread counts set to one. Time-limited mixed-integer
search is not promised to regenerate identical selected rows on other
machines; retained rows and their exact obstructions do replay without it.

## Exact retrospective correction

The stronger full ordinary-distance convex-quadrilateral check rejects all
three distinct initial patterns. There are 14 exact certificates: eight for
the pattern used by 271/811, one two-inequality certificate for 405, and five
for 912. Only the four selected source rows 2,5,6,7 are needed in the 405
certificate. Details and a direct two-inequality explanation are in the main
proof note, Section 9.

These runs therefore have **fixed-pattern, fixed-order obstruction** status.
They must not be used as evidence about failure to realize live patterns.
The later exact audit supersedes the earlier limited-preflight status while
leaving original numerical reports unchanged.

## Fresh exact-preflight-filtered scan

`filtered_moving.py` runs the stronger exact check before any geometric
optimization. Each positive integer contradiction identifies a subset of
selected rows; the pattern selector is forbidden to repeat that assignment.
The mathematical validity of a learned cut is checked independently of the
mixed-integer solver.

The completed repaired scan (`filtered_moving_622_repaired.json`) used seed
622, 12 pattern iterations, and a 20-second per-iteration mixed-integer solver
limit. All twelve selected patterns pass the circle/crossing and cluster
resource checks, but each has an exact strict-quadrilateral contradiction.
The scan retains **119 exact one-inequality certificates**, which yield
**117 distinct learned row-assignment cuts**. No geometry optimization is run
on any of these rejected patterns. The twelve patterns are mutually distinct
and distinct from the three earlier patterns.

```
python exploratory/filtered_moving.py --seed 622 --rounds 12 --time-limit 20 --output exploratory/filtered_moving_622_repaired.json
```

This is a bounded discovery scan of twelve choices, **not an enumeration of
all tripled-Danzer patterns**. The exact scope is the 15 distinct fixed
patterns with retained certificates, not a general obstruction to every
27-point configuration, every triple-copy pool, or every cyclic order.

## Failed diagnostic invocations retained

A five-second-per-iteration invocation returned no integral assignment on its
first iteration. Its saved report is `filtered_moving_622.json`; this proves
no infeasibility.

A subsequent invocation stopped on a duplicate-cut programming guard: two
different valid certificates in the same iteration minimized to the same
row-assignment cut. The code incorrectly treated that as repetition of an
already-excluded assignment from an earlier iteration. Its stderr is
`filtered_moving_622_longer.stderr`; it produced no completed result JSON.
The source before the fix is retained in
`history/filtered_moving_before_duplicate_cut_fix.py`.

The repaired code distinguishes cuts existing before an iteration from
multiple certificates generating the same new cut within that iteration.
A genuinely repeated earlier forbidden assignment still raises an error.
The completed 12-iteration report above was produced by a fresh rerun after
this fix, not reconstructed from the failed invocation.

## What this does not establish

No continuous parameter domain, all possible witness pool, or all cyclic
order was exhausted by the moving-coordinate experiments. No optimizer
status supplies an exclusion. The exact pair-capacity lemma and the retained
strict-quadrilateral certificates are separate mathematical results with
explicit hypotheses. The fixed-seed one-free theorem uses neither the
numerical initializer nor any of these optimizations.
