# C19 Fifth-Pair Two-Row Prefilter

Status: `EXACT_OBSTRUCTION` for the recorded fifth-pair child branches only.

This checkpoint tests a cheap exact prefilter against the full fifth-pair
frontier recorded by the compact C19 prefix-window sweep. For each recorded
fifth-pair child, the checker builds the Kalmanson inequalities whose cyclic
order is forced by the five boundary pairs and searches for either:

- a single forced row whose selected-distance quotient vector is zero; or
- two forced rows whose quotient vectors are exact opposites.

Either case gives a positive-integer strict-inequality certificate with total
coefficient zero, hence an exact contradiction for every completion of that
one boundary-prefix child. No LP is needed for these hits.

The checker then applies the existing exact Kalmanson/Farkas routine only to
the children missed by the two-row lookup. This records how useful the
prefilter would be before future fifth-pair LP calls.

It does not certify any branch beyond the recorded sweep artifact, does not
prove Erdos Problem #97, and does not produce a counterexample.

## Artifact

```text
reports/c19_fifth_pair_two_row_prefilter.json
```

Regenerate it with:

```bash
python scripts/analyze_c19_fifth_pair_two_row_prefilter.py \
  --assert-expected \
  --out reports/c19_fifth_pair_two_row_prefilter.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

## Sources

The diagnostic reads:

```text
reports/c19_fourth_pair_frontier_classifier.json
data/certificates/c19_kalmanson_prefix_window_sweep_128_287.json
```

## Counts

| Count | Value |
|---|---:|
| Fourth-pair survivor parents | 88 |
| Fifth-pair child branches | 7,920 |
| Two-row prefilter certificates | 7,917 |
| Prefilter misses | 3 |
| Exact Farkas fallback certificates | 3 |
| Final unclosed children | 0 |

Per-window prefilter misses:

| Window | Fifth-pair children | Prefilter misses | Final unclosed |
|---|---:|---:|---:|
| 128-159 | 180 | 0 | 0 |
| 160-191 | 630 | 0 | 0 |
| 192-223 | 1,350 | 1 | 0 |
| 224-255 | 810 | 0 | 0 |
| 256-287 | 4,950 | 2 | 0 |

The three fallback children are:

```text
c19_window_fifth_child_0212_0023_0000
c19_window_fifth_child_0261_0059_0041
c19_window_fifth_child_0274_0059_0041
```

Their fallback support sizes are `59`, `50`, and `56`, respectively.

## Claim Boundary

This is a bounded exact obstruction over the recorded fifth-pair children from
the compact C19 sweep. It strengthens the replay story for those children by
showing that 7,917 of 7,920 can be closed before any LP call, with only three
ordinary exact Farkas fallbacks.

This does not kill abstract `C19_skew` across all cyclic orders. It also does
not justify skipping fifth-pair subdivision in unscanned windows unless the
same checker is run on those generated child states.

The first forward use of this prefilter is recorded in
[`c19-kalmanson-prefix-window-prefilter-extension.md`](c19-kalmanson-prefix-window-prefilter-extension.md):
the 320-479 windows have 10,350 fifth-pair child branches; 10,342 close by the
two-row lookup, and the remaining 8 close by ordinary exact Farkas fallback.
Those eight fallback supports are reconstructed in
[`c19-prefilter-fallback-supports.md`](c19-prefilter-fallback-supports.md).
