# C19 Kalmanson Prefix Window Sweep

Status: `EXACT_OBSTRUCTION` for five deterministic C19
three-boundary-prefix windows, branch indices 128 through 287.

This is a bounded sampled-window artifact, not an all-order C19 search. It
does not prove Erdos Problem #97, does not kill abstract `C19_skew`, and does
not produce a counterexample.

## Artifact

```text
data/certificates/c19_kalmanson_prefix_window_sweep_128_287.json
```

Regenerate it with:

```bash
python scripts/sweep_c19_kalmanson_prefix_windows.py \
  --assert-expected \
  --out data/certificates/c19_kalmanson_prefix_window_sweep_128_287.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed. The full replay is marked slow in the
test suite because it runs five complete prefix-window chains.

## Method

The sweep reuses `scripts/certify_c19_kalmanson_prefix_window.py` on three
consecutive 32-prefix windows:

```text
128-159
160-191
192-223
224-255
256-287
```

Each window first tries direct three-boundary-prefix Kalmanson/Farkas
certificates. Direct survivors are subdivided by one ordered left/right
boundary pair. Fourth-pair survivors are subdivided by one more ordered
left/right boundary pair. The sweep stores compact per-window accounting and
survivor lists rather than full closed certificate examples.

## Counts

| Count | Value |
|---|---:|
| Three-boundary-prefix branches scanned | 160 |
| Prefix branches closed by the recorded chain | 160 |
| Prefix branches remaining after the recorded chain | 0 |
| Direct prefix certificates | 112 |
| Direct prefix survivors | 48 |
| Fourth-pair children below direct survivors | 6,336 |
| Fourth-pair child certificates | 6,248 |
| Fourth-pair child survivors | 88 |
| Fifth-pair children below fourth-pair survivors | 7,920 |
| Fifth-pair child certificates | 7,920 |
| Fifth-pair child survivors | 0 |

Per-window summary:

| Window | Direct closed | Direct survivors | Fourth children closed | Fourth survivors | Fifth children closed |
|---|---:|---:|---:|---:|---:|
| 128-159 | 31 | 1 | 130 / 132 | 2 | 180 / 180 |
| 160-191 | 23 | 9 | 1,181 / 1,188 | 7 | 630 / 630 |
| 192-223 | 19 | 13 | 1,701 / 1,716 | 15 | 1,350 / 1,350 |
| 224-255 | 24 | 8 | 1,047 / 1,056 | 9 | 810 / 810 |
| 256-287 | 15 | 17 | 2,189 / 2,244 | 55 | 4,950 / 4,950 |

## Claim Boundary

Each listed certificate is an exact obstruction for every completion of the
recorded boundary prefix at that branch depth. The sweep conclusion is only a
finite-subdivision conclusion for branch indices 128 through 287.

Together with the initial sampled-prefix chain, the currently recorded C19
sampled-prefix coverage is:

```text
128 initial sampled prefixes closed by the prefix/fourth/fifth chain
+ 160 prefixes in windows 128-287
= 288 deterministic sampled three-boundary-prefix branches closed
```

This remains a tiny sampled slice of 6,683,040 canonical three-boundary-prefix
states. It does not affect the global status of Erdos Problem #97.

## Follow-Up Extension

The exact two-row prefilter in
[`c19-fifth-pair-two-row-prefilter.md`](c19-fifth-pair-two-row-prefilter.md)
was then applied to later C19 windows in
[`c19-kalmanson-prefix-window-prefilter-extension.md`](c19-kalmanson-prefix-window-prefilter-extension.md).
It closes windows 288-479, bringing recorded sampled coverage to 480
deterministic three-boundary-prefix branches. This remains sampled-window
work only.
