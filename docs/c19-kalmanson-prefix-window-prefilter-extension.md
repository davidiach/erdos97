# C19 Kalmanson Prefilter Window Extension

Status: `EXACT_OBSTRUCTION` for six deterministic C19
three-boundary-prefix windows, branch indices 288 through 479.

This checkpoint extends the bounded C19 prefix-window scan beyond the compact
128-287 sweep. It uses the same prefix/fourth/fifth subdivision chain, but at
fifth-pair depth it first tries the exact two-row Kalmanson prefilter before
calling the ordinary LP/exact Farkas routine.

It is not an all-order C19 search, does not prove Erdos Problem #97, and does
not produce a counterexample.

## Artifacts

```text
data/certificates/c19_kalmanson_prefix_window_288_319_prefilter.json
data/certificates/c19_kalmanson_prefix_window_320_351_prefilter.json
data/certificates/c19_kalmanson_prefix_window_352_383_prefilter.json
data/certificates/c19_kalmanson_prefix_window_384_415_prefilter.json
data/certificates/c19_kalmanson_prefix_window_416_447_prefilter.json
data/certificates/c19_kalmanson_prefix_window_448_479_prefilter.json
data/certificates/c19_kalmanson_prefix_window_prefilter_sweep_288_479.json
reports/c19_prefilter_fallback_supports.json
```

Regenerate them with:

```bash
python scripts/certify_c19_kalmanson_prefix_window_prefilter.py \
  --start-index 288 \
  --window-size 32 \
  --assert-expected \
  --out data/certificates/c19_kalmanson_prefix_window_288_319_prefilter.json

python scripts/certify_c19_kalmanson_prefix_window_prefilter.py \
  --start-index 320 \
  --window-size 32 \
  --assert-expected \
  --out data/certificates/c19_kalmanson_prefix_window_320_351_prefilter.json

python scripts/certify_c19_kalmanson_prefix_window_prefilter.py \
  --start-index 352 \
  --window-size 32 \
  --assert-expected \
  --out data/certificates/c19_kalmanson_prefix_window_352_383_prefilter.json

python scripts/certify_c19_kalmanson_prefix_window_prefilter.py \
  --start-index 384 \
  --window-size 32 \
  --assert-expected \
  --out data/certificates/c19_kalmanson_prefix_window_384_415_prefilter.json

python scripts/certify_c19_kalmanson_prefix_window_prefilter.py \
  --start-index 416 \
  --window-size 32 \
  --assert-expected \
  --out data/certificates/c19_kalmanson_prefix_window_416_447_prefilter.json

python scripts/certify_c19_kalmanson_prefix_window_prefilter.py \
  --start-index 448 \
  --window-size 32 \
  --assert-expected \
  --out data/certificates/c19_kalmanson_prefix_window_448_479_prefilter.json

python scripts/sweep_c19_kalmanson_prefix_windows_prefilter.py \
  --assert-expected \
  --out data/certificates/c19_kalmanson_prefix_window_prefilter_sweep_288_479.json

python scripts/analyze_c19_prefilter_fallback_supports.py \
  --assert-expected \
  --out reports/c19_prefilter_fallback_supports.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed. The aggregate sweep artifact stores
compact per-window accounting and survivor labels for the whole 288-479 range;
the individual window artifacts retain closed example certificates.

## Counts

| Window | Direct closed | Direct survivors | Fourth children closed | Fourth survivors | Fifth children closed |
|---|---:|---:|---:|---:|---:|
| 288-319 | 32 | 0 | 0 / 0 | 0 | 0 / 0 |
| 320-351 | 26 | 6 | 786 / 792 | 6 | 540 / 540 |
| 352-383 | 23 | 9 | 1,180 / 1,188 | 8 | 720 / 720 |
| 384-415 | 20 | 12 | 1,569 / 1,584 | 15 | 1,350 / 1,350 |
| 416-447 | 19 | 13 | 1,669 / 1,716 | 47 | 4,230 / 4,230 |
| 448-479 | 16 | 16 | 2,073 / 2,112 | 39 | 3,510 / 3,510 |

Across the 320-479 windows, 10,342 of 10,350 fifth-pair children close by the
two-row prefilter. The remaining 8 children close by ordinary exact Farkas
fallback.

The aggregate artifact
`data/certificates/c19_kalmanson_prefix_window_prefilter_sweep_288_479.json`
replays the six windows together. It records 192 scanned prefixes, 136 direct
prefix certificates, 7,277 of 7,392 fourth-pair children closed by ordinary
exact Farkas certificates, 10,342 fifth-pair children closed by the two-row
prefilter, and 8 fifth-pair children closed by exact Farkas fallback.

The fallback-support diagnostic in
[`c19-prefilter-fallback-supports.md`](c19-prefilter-fallback-supports.md)
reconstructs those eight fallback children and records their exact Farkas
support sizes: 7, 8, 19, 47, 50, 52, 54, and 58 inequalities.

Together with the initial sampled-prefix chain and the 128-287 compact sweep,
the currently recorded C19 sampled-prefix coverage is:

```text
128 initial sampled prefixes closed by the prefix/fourth/fifth chain
+ 160 prefixes in windows 128-287
+ 192 prefixes in prefilter windows 288-479
= 480 deterministic sampled three-boundary-prefix branches closed
```

This remains a tiny sampled slice of 6,683,040 canonical three-boundary-prefix
states.

## Claim Boundary

Each closure is an exact obstruction for every completion of the recorded
boundary prefix at that branch depth. The prefilter conclusions are exact
two-row Kalmanson cancellations after selected-distance quotienting.

The result does not kill abstract `C19_skew` across all cyclic orders. It
records six deterministic 32-prefix windows in the sampled C19 workstream.
