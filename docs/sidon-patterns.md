# Sidon-type circulant patterns: empirical realizability

Trust labels: `EXACT_OBSTRUCTION` for the natural cyclic orders under Altman
linear certificates, and for the fixed `C13_sidon_1_2_4_10` pattern across all
cyclic orders under the Kalmanson two-certificate order search, and for one
fixed `C29_sidon_1_3_7_15` cyclic order under the full Kalmanson/Farkas
certificate;
`NUMERICAL_EVIDENCE` for the SLSQP plateau. No general proof or counterexample
claim.

## Headline finding

For `C13_sidon_1_2_4_10` -- the (13,4,1) Singer planar-difference-set
circulant -- constrained SLSQP under strict convexity does **not** drive the
equality residual toward zero as the convexity margin is tightened.
The RMS equality residual plateaus near 0.84 and the per-row squared-distance
spread plateaus near 3.4 across four orders of magnitude in margin. This is
qualitatively different from the `B12_3x4_danzer_lift` cluster-degeneration
signature, where residual decays monotonically as the margin tightens and the
optimum collapses toward a degenerate equilateral-triangle skeleton. Both
outcomes are informative; for `C13_sidon_1_2_4_10` the outcome is an apparent
positive residual plateau, consistent with the LLM-run conjecture that Sidon-type
cohort patterns form a structural wall against the row-4 matrix bound but are
not realisable by any strictly convex 13-gon. This is numerical evidence
only.

## Patterns

The three Sidon-type circulant incidence patterns added to the catalog are:

1. `C13_sidon_1_2_4_10`: `n = 13`, `S_i = {i+1, i+2, i+4, i+10} mod 13`.
   `D = {1,2,4,10}` is the (13,4,1) Singer planar difference set translated
   off zero. Every nonzero residue appears exactly once as a difference of
   two elements of `D`, so `|S_a cap S_b| = 1` for every `a != b`. Verified
   by `tests/test_sidon_patterns.py::test_c13_sidon_singer_difference_set_property`.
2. `C25_sidon_2_5_9_14`: `n = 25`, `D = {2,5,9,14}`. All 12 pairwise
   differences distinct mod 25. `|S_a cap S_b| in {0, 1}`.
3. `C29_sidon_1_3_7_15`: `n = 29`, `D = {1,3,7,15}`. All 12 pairwise
   differences distinct mod 29. `|S_a cap S_b| in {0, 1}`.

In all three the witness in-degree is constantly 4 and the two-circle
common-selected-neighbour cap `|S_a cap S_b| <= 2` is satisfied with margin
to spare. The natural cyclic orders are now exactly killed by Altman linear
certificates; see `data/certificates/altman_linear_certificate_sweep.json`.
The fixed C13 abstract-order version is now exactly killed by the Kalmanson
two-certificate order search. The C25 and C29 abstract-order versions remain
incidence-pattern leads at the all-order level, but one recorded non-natural
C29 order is now exactly killed by
`data/certificates/c29_sidon_fixed_order_kalmanson_165_unsat.json`.

## LLM-run provenance

These three patterns surfaced from prior LLM proof-attempt runs against the
row-4 matrix bound. The runs repeatedly suggested that Sidon-type cohort
patterns -- where every pairwise selected-witness intersection is bounded by
1 -- form a structural wall against that bound but cannot be realised
geometrically by a strictly convex polygon. The conjecture motivating this
PR is exactly that empirical statement. C13 is the smallest Sidon-type
circulant in the family (a Singer planar difference set) and is the cheapest
test of the conjecture.

## Engine extension

Before the Altman certificate sweep, the legacy search engine used a
least-squares trust-region (TRF) solver
with soft barrier penalties. The Sidon test requires hard-margin strict
convexity, so an SLSQP path was added:

- `--optimizer slsqp`: minimise the squared distance-equality residual
  subject to inequality constraints `convexity_margin >= margin`,
  `edge_length >= margin`, `pair_distance >= margin`. Here
  `convexity_margin` is the verifier-grade full edge-vs-vertex margin, not
  just consecutive-turn orientation.
- `--margin <value>`: numerical convexity / edge / pair margin enforced as
  a hard SLSQP constraint (and used as a soft margin under `--optimizer trf`).

The polar parameterisation gives free angles and free radii. **No
coordinate symmetry is imposed on cyclic incidence patterns.** The polar
parameterisation places vertex `0` at angle `0` purely as a translation /
rotation gauge, but the angular gaps and radii are independent free
variables. A regular-polygon initialisation would force a symmetric
optimum; instead random jittered initialisation is used (`init_polar_x`)
and 20 restarts per run, so symmetric local minima have to compete with
generic ones. Verified by reading the parameterisation code and by
inspecting the radius standard deviations in the runs below (`std(r) > 0.34`
across all four margins, far from the regular-13-gon value `0`).

## Run protocol

```
erdos97-search --pattern C13_sidon_1_2_4_10 \
  --mode polar --restarts 20 --max-nfev 2000 \
  --optimizer slsqp --margin <m> --seed 2026 \
  --out data/runs/C13_sidon_m<m>.json
```

with `m in {1e-3, 1e-4, 1e-5, 1e-6}`. Outputs are committed to
`data/runs/`.

## Result table

| margin | eq_rms | max squared-distance spread | per-row spread (min/median/max) | convexity margin achieved | min edge length | radii std |
|--------|--------|------------------------------|----------------------------------|----------------------------|-----------------|-----------|
| 1e-3   | 0.8483 | 3.383                        | 1.09 / 1.89 / 3.38               | 1.00e-03                   | 3.30e-02        | 0.350     |
| 1e-4   | 0.8414 | 3.367                        | 0.96 / 1.93 / 3.37               | 1.00e-04                   | 1.07e-02        | 0.376     |
| 1e-5   | 0.8392 | 3.368                        | 0.90 / 1.92 / 3.37               | 1.00e-05                   | 3.29e-03        | 0.386     |
| 1e-6   | 0.8385 | 3.372                        | 0.90 / 1.91 / 3.37               | 1.00e-06                   | 1.03e-03        | 0.389     |

(Polygon normalised so that the centroid is at the origin and the mean
squared radius is 1; squared-distance spreads are in those units.)

## Interpretation

1. **Residual plateaus, not decreases monotonically.** Tightening the
   margin by three orders of magnitude moves `eq_rms` from `0.848` to
   `0.838`. Differences are at the third decimal; the equality residual
   is essentially flat at an apparent positive residual floor. This contrasts with
   the B12 archive (`best_B12_slsqp_m1e-6.json`), where `eq_rms` decays
   to `~2e-3` and `max_spread` to `~7e-3` as the margin tightens, with
   the optimum collapsing toward four near-equilateral clusters.
2. **The full convexity margin hits the imposed bound.**
   `min_edge` shrinks from `3.3e-2` at `m=1e-3` to `1.0e-3` at `m=1e-6`,
   but remains well above the imposed edge and pair-distance floor. The
   optimiser is primarily fighting the convexity wall; relaxing that wall
   lets the polygon get marginally thinner, not closer to satisfying the
   equality system.
3. **No cluster collapse.** Radii vary from `~0.55` to `~1.76` with
   `std ~ 0.39`. Vertices are spread, not bunched. The B12 signature of
   four-cluster collapse near an equilateral skeleton is absent here.
4. **Per-row squared-distance spread is far from machine zero.** With
   a target of zero and a normalisation to mean squared radius `1`, the
   median per-row spread is `~1.9` and the max is `~3.4`. These are
   not numerical near-misses; they are large structural residuals.

The natural reading is: under strict convexity the C13 Sidon-type
incidence system has no solution near the basin found by these 20 restarts,
and the failure mode is a flat residual rather than a degenerate collapse.
That is informative either way: the conjecture predicted a wall, and the
numerics are consistent with one.

## What this is not

- It is not a proof of abstract-order non-realisability. Twenty SLSQP
  restarts in a particular polar basin do not exhaust the configuration
  space, and the exact Altman certificate currently applies only to the
  natural label order.
- It is not a counterexample to anything. The pattern is INCIDENCE_PATTERN;
  the run is NUMERICAL_EVIDENCE.
- It is not an all-order verdict on `C25_sidon_2_5_9_14` or
  `C29_sidon_1_3_7_15`. Later fixed-order diagnostics killed one C25 order by
  vertex-circle and Altman filters and one C29 order by a full
  Kalmanson/Farkas certificate, but neither result settles the corresponding
  abstract Sidon pattern across all cyclic orders.

## Suggested next steps (not done in this PR)

- Try `--optimizer trf` on the natural pattern with strong convex-margin
  weight as an independent crosscheck of the plateau.
- Try the `direct` and `support` parameterisations on both the natural pattern
  and the registered non-natural survivor order from
  `data/certificates/sparse_order_survivors.json`.
- Increase restarts beyond 20 and seeds beyond `2026`.
- If the plateau survives all three of those, attempt an exact-rank argument
  or a sparse-overlap extension targeted at the Sidon class.

The C25 and C29 pattern definitions are in the catalog. Since C13 is now
exactly killed by the Kalmanson two-certificate order search, future Sidon work
should either scale that search or first find stronger pruning templates.

## Non-natural C13 survivor order

The older sparse-frontier fixed-order filters missed the registered order

```text
5,0,10,8,9,7,4,6,2,11,12,3,1
```

for `C13_sidon_1_2_4_10`; see
`data/certificates/sparse_order_survivors.json`. The compact C13 Kalmanson
pilot kills this same fixed order by an exact 2-inequality certificate; see
`docs/kalmanson-c13-pilot.md`. The follow-up search in
`docs/kalmanson-two-order-search.md` kills the fixed C13 abstract pattern
across all cyclic orders. The search engine supports this order directly via
`--cyclic-order`, relabelling the incidence pattern so the supplied order
becomes the natural boundary order.

The first constrained SLSQP run on this non-natural order is stored in
`data/runs/C13_sidon_order_survivor_slsqp_m1e-4_seed20260502.json`. It reports
`eq_rms = 0.6569` and `max_spread = 2.728` at convexity margin `1e-4`.
This is lower than the natural-order C13 plateau but still far from an exact
candidate.
