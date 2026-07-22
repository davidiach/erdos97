# Free-Cartesian sparse-pattern preflight

Status: `EXACT_FIXED_ORDER_NEGATIVE_CONTROLS` plus a numerical construction
search scaffold. No general proof and no counterexample are claimed.

## Why the route changed

The previously stored C25 step-7 and C29 Z3 orders are not live coordinate
targets. The C25 order is exactly killed by vertex-circle and Altman filters;
the C29 order is exactly killed by the stored 165-inequality full Kalmanson
certificate. Optimizing either fixed order would therefore spend numerical
effort on an exact impossibility.

The replacement driver
`scripts/exploration/search_free_cartesian_sparse.py` enforces a hard gate:

1. sample a fixed cyclic order with label `0` fixed to remove rotations;
2. run crossing, vertex-circle, Altman-signature, and exact Altman-linear
   filters;
3. search for and exactify a full fixed-order Kalmanson/Farkas certificate;
4. run free-Cartesian least squares only if no exact certificate is found.

The coordinate engine in `src/erdos97/free_cartesian.py` fixes
`p_0=(0,0)` and `p_1=(1,0)`, leaving `2n-4` free Cartesian variables. It uses
three independent squared-distance differences per center, pair-separation
hinges, and every edge-versus-nonincident-vertex strict-convexity hinge. The
full residual Jacobian is analytic and is checked against central finite
differences in `tests/test_free_cartesian.py`.

## Checked run

The artifact under
`data/runs/free_cartesian_sparse_2026-07-22/` contains 24 complete exact
fixed-order certificates:

| Pattern | Deterministic orders | Passed lightweight filters | Exact full-cone obstructions | Coordinate attempts |
|---|---:|---:|---:|---:|
| `C25_sidon_2_5_9_14` | 12 | 12 | 12 | 0 |
| `C29_sidon_1_3_7_15` | 12 | 12 | 12 | 0 |

The certificate support sizes are 177--207 for C25 and 263--288 for C29. The
artifact checker replays the selected-distance quotient and exact weighted
zero sum for all 24 certificates.

During development, a wider LP-only smoke test sampled another 200 C25 orders
with seed `20260723` and 50 C29 orders with seed `20260724`. It found a positive
dual support for every order (C25 support sizes 176--209; C29 263--295). That
wider screen is numerical diagnostic evidence only; the 24 stored certificates
are the exact reproducible result.

## Interpretation and next target

This run found no order eligible for Cartesian optimization. That is stronger
than another failed coordinate fit: the sampled fixed orders are impossible
before coordinates enter. It is still not an all-order result for C25 or C29.

The useful next target is discrete: either find a cyclic order that escapes
the full Kalmanson cone, at which point the implemented Cartesian solver can
start immediately, or promote the recurring high-support certificates into a
reusable all-order forbidden-template/SMT argument. Repeating unconstrained
coordinate optimization on certified orders has no research value.

Replay:

```bash
python scripts/exploration/search_free_cartesian_sparse.py \
  --check data/runs/free_cartesian_sparse_2026-07-22/summary.json
```
