# C19 Kalmanson Prefix Window Catalog Prefilter Sweep

Status: `EXACT_OBSTRUCTION` for deterministic sampled C19
three-boundary-prefix windows 288 through 479.

This note does not prove Erdos Problem #97, does not kill abstract
`C19_skew`, and does not produce a counterexample.

## Artifact

```text
data/certificates/c19_kalmanson_prefix_window_catalog_prefilter_sweep_288_479.json
```

Regenerate it with:

```bash
python scripts/sweep_c19_kalmanson_prefix_windows_catalog_prefilter.py \
  --assert-expected \
  --out data/certificates/c19_kalmanson_prefix_window_catalog_prefilter_sweep_288_479.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

## Scope

This is the same sampled prefix range as the compact two-row prefilter sweep
in
[`c19-kalmanson-prefix-window-prefilter-extension.md`](c19-kalmanson-prefix-window-prefilter-extension.md).
The direct prefix and fourth-pair stages are unchanged.

At the fifth-pair stage, the sweep uses a two-stage exact prefilter:

1. the existing two-row Kalmanson cancellation lookup;
2. the three cataloged unit supports from
   [`c19-prefilter-catalog-unit-supports.md`](c19-prefilter-catalog-unit-supports.md).

Only children missed by both exact prefilters call the ordinary
Kalmanson/Farkas routine.

## Counts

| Count | Value |
|---|---:|
| Sampled prefix branches | 192 |
| Prefix branches closed after chain | 192 |
| Fourth-pair child branches | 7,392 |
| Fourth-pair child certificates | 7,277 |
| Fifth-pair child branches | 10,350 |
| Fifth-pair two-row prefilter certificates | 10,342 |
| Fifth-pair catalog prefilter certificates | 8 |
| Fifth-pair ordinary Farkas fallbacks | 0 |
| Unclosed fifth-pair children | 0 |

Compared with the two-row-only compact sweep, the catalog prefilter reduces
ordinary fifth-pair Farkas fallback attempts from eight to zero.

## Claim Boundary

Every closure in this artifact is exact for the recorded sampled branch it
addresses. The artifact does not certify any branch outside deterministic
prefix indices 288 through 479 and does not address all cyclic orders of
`C19_skew`. The catalog supports are reusable exact prefilter rules for these
recorded fallback states, not a general geometric theorem.
