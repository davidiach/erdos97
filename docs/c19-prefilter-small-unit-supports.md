# C19 Prefilter Small Unit Supports

Status: `EXACT_OBSTRUCTION` diagnostic for seven of the eight sampled C19
fifth-pair children that miss the two-row Kalmanson prefilter.

This note does not prove Erdos Problem #97, does not kill abstract
`C19_skew`, and does not produce a counterexample.

## Artifact

```text
reports/c19_prefilter_small_unit_support_search.json
```

Regenerate it with:

```bash
python scripts/analyze_c19_prefilter_small_unit_supports.py \
  --assert-expected \
  --out reports/c19_prefilter_small_unit_support_search.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

## Scope

The source is the compact prefilter sweep:

```text
data/certificates/c19_kalmanson_prefix_window_prefilter_sweep_288_479.json
```

The analyzer reconstructs only the eight fifth-pair children recorded there as
ordinary Farkas fallback cases. For each reconstructed child it exhaustively
searches for the existence of a unit-weight cancellation using one, two, or
three forced Kalmanson rows. It records one support witness for each child
where such a cancellation exists.

## Counts

| Count | Value |
|---|---:|
| Fallback fifth-pair children | 8 |
| Two-row prefilter misses rechecked | 8 |
| Three-row unit supports found | 7 |
| Children still missing a support of size <= 3 | 1 |
| Pair sums checked | 15,428,396 |

The only fallback child still missing a unit support of size at most three is:

```text
c19_window_fifth_child_0430_0081_0011
```

The seven found supports all have exactly three unit-weight forced Kalmanson
rows. This gives a concrete exact target for a future prefilter upgrade:
recognize the repeated 3-row unit cancellation pattern without running the
ordinary Farkas LP.

That target is replayed as an explicit support catalog in
[`c19-prefilter-catalog-unit-supports.md`](c19-prefilter-catalog-unit-supports.md).
The catalog contains two distinct three-row support patterns and certifies the
same seven fallback children by exact vector summation.

## Claim Boundary

Each listed small unit support is an exact obstruction for completions of one
recorded fifth-pair boundary-prefix child. The missing child still closes by
the ordinary exact Farkas certificate recorded in
[`c19-prefilter-fallback-supports.md`](c19-prefilter-fallback-supports.md).
The result certifies no branch beyond the sampled 288-479 prefilter-window
sweep.
