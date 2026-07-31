# C25 selected-residual width-3 augmented CEGAR

Status: bounded fixed-pattern, history-blocked exact-clause diagnostic. No
all-order obstruction, geometric counterexample, general proof, or
official-status update is claimed.

This packet blocks the complete current 168-order C25 history and activates
only the three transferred exact seed orbits, persistent width-4 orbit, and
the width-3 orbit selected by the preceding residual-compression packet.

## Result

- Blocked dihedral order classes: `168`.
- Active exact seed orbits: `5`, with widths `3, 5, 14, 4, 3`.
- Inactive exact seed summaries: `16`.
- Active exact affine seed images: `125`.
- Fresh history-disjoint probe orders: `16`.
- Four parent seeds cover `16/16` probe orders.
- Selected width-3 only covers `4/16`, all already covered by the parent
  seeds, so its fresh-probe marginal coverage is `0/16`.
- Five-seed CEGAR learns eight new exact full-cone certificates of widths
  `219, 220, 214, 216, 211, 217, 219, 210`.
- The run reaches its eight-certificate limit with no unresolved model and
  adds `200` unique affine clauses.
- The checker replays `325` exact affine certificate images in total.
- Decision: `COMPRESS_NEW_C25_SELECTED_RESIDUAL_AUGMENTED_ESCAPES`.

Generate:

```bash
python scripts/exploration/run_sparse_full_cone_c25_selected_residual_augmented_cegar.py \
  --out data/runs/sparse_full_cone_c25_selected_residual_augmented_cegar_2026-07-30/summary.json
```

Replay:

```bash
python scripts/exploration/run_sparse_full_cone_c25_selected_residual_augmented_cegar.py \
  --check data/runs/sparse_full_cone_c25_selected_residual_augmented_cegar_2026-07-30/summary.json
```

SHA-256 of `summary.json`:

`f6abf754d8fb31913ddb986e993ccf4917a985c41890ca1e2c22d5ae081a2388`
