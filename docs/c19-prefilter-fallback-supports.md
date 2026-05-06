# C19 Prefilter Fallback Supports

Status: `EXACT_OBSTRUCTION` diagnostic for the eight fifth-pair children in
the sampled C19 prefilter-window sweep that miss the two-row Kalmanson
prefilter.

This note does not prove Erdos Problem #97, does not kill abstract
`C19_skew`, and does not produce a counterexample.

## Artifact

```text
reports/c19_prefilter_fallback_supports.json
```

Regenerate it with:

```bash
python scripts/analyze_c19_prefilter_fallback_supports.py \
  --assert-expected \
  --out reports/c19_prefilter_fallback_supports.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

## Scope

The source is the compact prefilter sweep:

```text
data/certificates/c19_kalmanson_prefix_window_prefilter_sweep_288_479.json
```

The analyzer reconstructs only the fifth-pair children recorded there as
ordinary Farkas fallback cases. For each reconstructed child it checks:

- the exact two-row prefilter returns no certificate;
- the ordinary prefix-forced Kalmanson/Farkas search returns an exact
  positive-integer certificate;
- the certificate verifies to a zero coefficient sum after quotienting by the
  selected-distance equalities.

## Counts

| Count | Value |
|---|---:|
| Fallback fifth-pair children | 8 |
| Two-row prefilter misses rechecked | 8 |
| Exact Farkas certificates | 8 |
| Final unclosed fallback children | 0 |
| Forced Kalmanson rows per child | 3,300 |

Support-size histogram:

| Support size | Count |
|---:|---:|
| 7 | 1 |
| 8 | 1 |
| 19 | 1 |
| 47 | 1 |
| 50 | 1 |
| 52 | 1 |
| 54 | 1 |
| 58 | 1 |

The two smallest-support children have unit or nearly unit weights, but the other fallback
certificates require larger supports and weights. The diagnostic therefore
does not identify an immediate extension of the two-row prefilter; it gives a
checked target list for a future exact prefilter search.

A follow-up small-unit support search is recorded in
[`c19-prefilter-small-unit-supports.md`](c19-prefilter-small-unit-supports.md).
It finds exact three-row unit Kalmanson cancellations for seven of the eight
fallback children. The child `c19_window_fifth_child_0430_0081_0011` remains a
size-3 unit-support miss and still uses the ordinary Farkas certificate
recorded here.
The two distinct three-row supports are replayed as cataloged exact prefilter
rules in
[`c19-prefilter-catalog-unit-supports.md`](c19-prefilter-catalog-unit-supports.md).

## Claim Boundary

Each listed fallback certificate is an exact obstruction for completions of one
recorded fifth-pair boundary-prefix child. The result certifies no branch
beyond the sampled 288-479 prefilter-window sweep.
