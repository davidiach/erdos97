# Gröbner Basis Corroboration at n = 10 (Erdős #97)

**Date:** 2026-05-06
**Status:** REVIEW_PENDING. No general proof or counterexample is claimed.
The official/global status of Erdős #97 (FALSIFIABLE/OPEN) is unchanged.

## Scope

This memo records a sympy Gröbner-basis attack on a uniform random sample
of pre-vertex-circle full witness assignments at n = 10, complementing the
existing **vertex-circle singleton-slice artifact** at
`data/certificates/n10_vertex_circle_singleton_slices.json` which already
reports `total_full = 0` for all 126 row0 choices under the vertex-circle
filter.

The point of this run is *not* to produce a second-source proof of n = 10
because we sample, not enumerate, the pre-vertex-circle survivors. The
output is best read as algebraic corroboration: every pattern in the
sample is exactly killed by the Gröbner basis alone (`GB = {1}` over `QQ`,
no complex solutions, hence no Euclidean realization), and no
sampled pattern needed a real-root / non-degeneracy decoder follow-up.
No GB computation timed out at the 60 s budget; the slowest finished
in 9.1 s.

## Setup

For each pattern, every row `i` lists 4 selected witnesses in cyclic order
`{a, b, c, d}` such that any realisation `p_0, ..., p_9 in R^2` must satisfy

  `|p_i - p_a| = |p_i - p_b| = |p_i - p_c| = |p_i - p_d|`.

We encode this as 3 polynomial equations per row in coordinates
`(x_0, y_0, ..., x_9, y_9) in Q^{20}`, with the rigid-motion + scale gauge

  `x_0 = y_0 = 0` (translation), `y_1 = 0` (rotation), `x_1 = 1` (scale).

This leaves **16 free variables** and **30 polynomial equations** over `QQ`.
We compute a grevlex Gröbner basis, time-boxed to 60 s.
For nontrivial bases we look for a univariate elimination polynomial in
`y_9, y_8, x_9, x_8` and check whether real roots exist via
`sympy.real_roots` with a 30 s budget.

## Pipeline

1. **Survivor collection.** Run `GenericVertexSearch(10)` with
   `use_vertex_circle=False` (column / pair-cap filters only). Cap at
   4 survivors per row0 slice, 200 survivors total. Output:
   `data/certificates/n10_groebner_survivors_cache.json`.
2. **Sample.** Sample 100 of 200 collected patterns uniformly at random
   (seed `20260506`).
3. **Gröbner pass.** For each sampled pattern, build the 30-poly system
   in 16 variables, compute grevlex GB over `QQ`, and classify:
   - `GB_TRIVIAL`     - basis equals `{1}`; pattern is unrealizable.
   - `GB_NO_REAL`     - basis nontrivial, but a univariate elimination
     polynomial in `y_9 / y_8 / x_9 / x_8` has no real roots; unrealizable.
   - `GB_NONTRIVIAL`  - basis nontrivial; either no univariate
     elimination polynomial was found in the tested variables, or it
     does admit real roots. Decoder follow-up needed.
   - `GB_TIMEOUT`     - GB computation exceeded 60 s; honest unresolved.
   - `GB_ERROR`       - sympy raised an unexpected exception (rare).

## Caveats

* **Sampling, not enumeration.** Pre-vertex-circle survivor count at n = 10
  is large (row0 = 0 alone yields ~160 survivors with the column / pair
  caps, suggesting ~10K-20K total). The full enumeration is feasible in
  hours of pure Python; this run only walks the first 50 of 126 row0
  choices to populate the cache, then samples.
* **Timeouts are honest.** A timeout means the GB step did not finish in
  60 s, not that the system is realisable.
* **Real-root step is heuristic.** We only test univariate eliminations
  in 4 specific variables (`y_9, y_8, x_9, x_8`). A nontrivial basis
  whose univariate eliminations do admit real roots is *not* a
  realisability proof - convexity is not encoded - but it is not killed
  by this pipeline either; it falls in `GB_NONTRIVIAL`.

## Provenance

Files produced by this run:

```text
scripts/groebner_n10.py                                        # attack driver
data/certificates/n10_groebner_survivors_cache.json            # 200 cached pre-VC survivors
data/certificates/n10_groebner_results.json                    # 100 sampled GB verdicts
docs/n10-groebner-corroboration.md                             # this memo
```

The script can be re-run with `--cached-survivors` pointing at the
existing cache to skip the collection step. Increase `--collect-budget-sec`
or remove `--per-row0-cap` to enlarge the candidate pool.

## Results

```text
sympy:                       1.14.0
survivors collected:         200      (cap=200, per-row0-cap=4, row0=0..49)
sample size:                 100      (uniform, seed=20260506)
GB_TRIVIAL count:            100 / 100
GB_NO_REAL count:              0 / 100
GB_NONTRIVIAL count:           0 / 100
GB_TIMEOUT count:              0 / 100
GB_ERROR count:                0 / 100
total Gröbner wall-clock:    162.8 s   (sum of per-pattern GB times)
GB pass wall-clock:          172.7 s   (including bookkeeping)
GB times (per pattern):      min=0.38 s, median=1.12 s, mean=1.63 s, max=9.08 s
```

**Every one of the 100 sampled n = 10 pre-vertex-circle patterns has the
trivial grevlex Gröbner basis `{1}` over `QQ`.** Each is therefore an
unrealizable polynomial system: no `(x_0, y_0, ..., x_9, y_9) in C^{20}`
satisfies the 30 distance-equality polynomials, hence none in `R^{20}`,
hence no Euclidean realization exists for that pattern. This is consistent
with - and a strong second-source signal for - the existing review-pending
vertex-circle finding that no n = 10 selected-witness assignment in cyclic
order admits a realization.

No nontrivial basis arose, so no univariate elimination polynomials were
extracted in this sample. No GB computation timed out at the 60 s budget;
the slowest single computation took 9.1 s.

See `data/certificates/n10_groebner_results.json` for per-pattern rows,
basis sizes, GB times, and the trivial-basis representations.

## Honest assessment

* The vertex-circle filter remains the only known *complete* obstruction
  at n = 10 in this repo (review-pending, but with full 126-row0
  singleton-slice coverage and 0 surviving full assignments).
* The Gröbner attack on this 100-pattern sample (drawn uniformly from a
  200-pattern, 50-row0 cache of pre-vertex-circle survivors) gives a
  **uniformly trivial-basis verdict**: every sampled pattern's distance
  ideal generates the unit ideal in `Q[x_2, ..., x_9, y_2, ..., y_9]`.
  This is a positive corroboration signal: at the n = 8 finite case
  14 / 15 incidence-completeness classes were trivial GB, and at n = 9
  150 / 184 selected-witness assignments were trivial GB; n = 10 (in this
  sample) is 100 / 100 trivial. There is no nontrivial-but-no-real
  family in this sample, and no GB_NONTRIVIAL pattern that would need
  decoder follow-up.
* This is **not** a complete second-source proof at n = 10. We sampled,
  not enumerated; only 50 of 126 row0 choices contributed to the cache,
  and only 4 of typically ~160 survivors per row0 entered the cache. To
  promote the Gröbner step to a finite-case proof, a future run would
  need (i) full pre-vertex-circle survivor enumeration at n = 10 (about
  10K-20K patterns, hours of CPU in pure Python), and (ii) a per-pattern
  budget high enough to reach trivial / nontrivial verdict on every
  pattern. The 60 s sympy budget was sufficient for the present
  100-pattern sample - the slowest GB took 9.1 s.
* Convex position is not algebraically encoded; any nontrivial-with-real
  pattern in a future enumeration would still need a strict-convexity
  decoder analogous to the n = 8 class 14 hexagram analysis. None
  arose in this sample.
