# C19 Prefilter Catalog Unit Supports

Status: `EXACT_OBSTRUCTION` diagnostic replaying two cataloged three-row
unit Kalmanson supports over the eight sampled C19 fifth-pair children that
miss the two-row prefilter.

This note does not prove Erdos Problem #97, does not kill abstract
`C19_skew`, and does not produce a counterexample.

## Artifact

```text
reports/c19_prefilter_catalog_unit_supports.json
```

Regenerate it with:

```bash
python scripts/analyze_c19_prefilter_catalog_unit_supports.py \
  --assert-expected \
  --out reports/c19_prefilter_catalog_unit_supports.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

## Scope

The source sweep is:

```text
data/certificates/c19_kalmanson_prefix_window_prefilter_sweep_288_479.json
```

The support catalog is extracted from:

```text
reports/c19_prefilter_small_unit_support_search.json
```

The analyzer reconstructs only the eight fallback children in the source
sweep. It then checks the two cataloged three-row unit supports by exact vector
summation after quotienting by the selected-distance equalities.

## Counts

| Count | Value |
|---|---:|
| Fallback fifth-pair children | 8 |
| Two-row prefilter misses rechecked | 8 |
| Cataloged three-row support patterns | 2 |
| Fallback children closed by the catalog | 7 |
| Children still missing a catalog support | 1 |

Catalog usage:

| Catalog support | Count |
|---|---:|
| `unit_support_000` | 6 |
| `unit_support_001` | 1 |
| none | 1 |

The only catalog miss is:

```text
c19_window_fifth_child_0430_0081_0011
```

## Claim Boundary

Each catalog hit is an exact obstruction for completions of one recorded
fifth-pair boundary-prefix child. The catalog is a cheap replay of supports
found by the exhaustive small-unit diagnostic, not a new all-order C19
argument. The remaining miss still closes by the ordinary exact Farkas
certificate recorded in
[`c19-prefilter-fallback-supports.md`](c19-prefilter-fallback-supports.md).
