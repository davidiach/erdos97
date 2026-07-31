# C25 width-4 replacement augmented CEGAR

Status: bounded fixed-pattern, history-blocked exact-clause diagnostic. No
all-order obstruction, geometric counterexample, general proof, or
official-status update is claimed.

This packet blocks the complete current 192-order C25 history and activates
the three transferred exact seed orbits, persistent width-4 orbit, and only
the new width-4 replacement selected by the preceding escape-compression
packet. The old nonmarginal width-3 seed is inactive.

## Result

- Blocked dihedral order classes: `192`.
- Active exact seed orbits: `5`, with widths `3, 5, 14, 4, 4`.
- Inactive exact seed summaries: `24`.
- Active exact affine seed images: `125`.
- Fresh history-disjoint probe orders: `16`.
- Four parent seeds cover `16/16` probe orders.
- Replacement width-4 only also covers `16/16`, all already covered by the
  parent seeds, so its fresh-probe marginal coverage is `0/16`.
- Five-seed CEGAR learns eight new exact full-cone certificates of widths
  `198, 193, 195, 195, 196, 200, 199, 201`.
- The run reaches its eight-certificate limit with no unresolved model and
  adds `200` unique affine clauses.
- The checker replays `325` exact affine certificate images in total.
- Decision: `COMPRESS_NEW_C25_REPLACEMENT_AUGMENTED_ESCAPES`.

Generate:

```bash
python scripts/exploration/run_sparse_full_cone_c25_replacement_augmented_cegar.py \
  --out data/runs/sparse_full_cone_c25_replacement_augmented_cegar_2026-07-31/summary.json
```

Replay:

```bash
python scripts/exploration/run_sparse_full_cone_c25_replacement_augmented_cegar.py \
  --check data/runs/sparse_full_cone_c25_replacement_augmented_cegar_2026-07-31/summary.json
```

SHA-256 of `summary.json`:

`cb3a06a79c21fa8ce3c883888458d3762b457fd8f7082f2535d5b88288d313ce`
