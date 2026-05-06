# C19 Prefilter Catalog Unit Supports

Status: `EXACT_OBSTRUCTION` diagnostic replaying three cataloged unit
Kalmanson supports over the eight sampled C19 fifth-pair children that miss
the two-row prefilter.

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

The first two support patterns are extracted from:

```text
reports/c19_prefilter_small_unit_support_search.json
```

The third support is the six-row unit cancellation recorded in
`reports/codex_goal_erdos97_log.md`. The analyzer reconstructs only the eight
fallback children in the source sweep. It then checks the cataloged unit
supports by exact vector summation after quotienting by the selected-distance
equalities.

The same catalog is applied as a two-stage prefilter sweep in
[`c19-kalmanson-prefix-window-catalog-prefilter-sweep.md`](c19-kalmanson-prefix-window-catalog-prefilter-sweep.md).
That sweep preserves the sampled 288-479 coverage and reduces ordinary
fifth-pair Farkas fallbacks from eight to zero.

## Counts

| Count | Value |
|---|---:|
| Fallback fifth-pair children | 8 |
| Two-row prefilter misses rechecked | 8 |
| Cataloged unit support patterns | 3 |
| Fallback children closed by the catalog | 8 |
| Children still missing a catalog support | 0 |

Catalog usage:

| Catalog support | Count |
|---|---:|
| `unit_support_000` | 6 |
| `unit_support_001` | 1 |
| `unit_support_002` | 1 |

## Claim Boundary

Each catalog hit is an exact obstruction for completions of one recorded
fifth-pair boundary-prefix child. The catalog is a cheap replay of supports
found by the exhaustive small-unit diagnostic plus the logged six-row
cancellation, not a new all-order C19 argument. The eight children still have
ordinary exact Farkas certificates recorded in
[`c19-prefilter-fallback-supports.md`](c19-prefilter-fallback-supports.md).
