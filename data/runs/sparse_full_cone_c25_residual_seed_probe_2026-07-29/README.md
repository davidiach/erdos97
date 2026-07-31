# C25 residual-seed augmentation probe

Status: bounded history-disjoint exact-clause coverage diagnostic. No
all-order obstruction, geometric counterexample, general proof, or
official-status update is claimed.

This packet blocks all 112 previously stored C25 orders under rotation and
reversal, generates 32 fresh inverse-pair-escape orders without activating
full-cone seed clauses, and compares three nested exact seed packets.

## Result

- Blocked history: `112` dihedral order classes.
- Fresh probe: `32` orders, all lightweight-filter survivors.
- Probe search: `563` Z3 iterations and `14,901` inverse-pair clauses.
- Transferred-only packet: 3 orbits, 75 exact affine images, coverage `32/32`.
- Transferred plus residual width 3: 4 orbits, 100 exact affine images,
  coverage `32/32`.
- Transferred plus all residuals: 11 orbits, 275 exact affine images,
  coverage `32/32`.
- Width-3 marginal over transferred seeds: `0`.
- Other residual marginal over width-3 augmentation: `0`.
- The transferred width-3 and width-14 orbits each individually cover all 32
  probe orders.
- Decision:
  `STOP_C25_RESIDUAL_SEED_AUGMENTATION_AFTER_BOUNDED_PROBE`.

Generate:

```bash
python scripts/exploration/probe_sparse_full_cone_c25_residual_seed_augmentation.py \
  --out data/runs/sparse_full_cone_c25_residual_seed_probe_2026-07-29/summary.json
```

Replay without rerunning Z3:

```bash
python scripts/exploration/probe_sparse_full_cone_c25_residual_seed_augmentation.py \
  --check data/runs/sparse_full_cone_c25_residual_seed_probe_2026-07-29/summary.json
```

SHA-256 of `summary.json`:

`a58f1f8caa7df997b16b225b12cd8622ef498759d3c9f43d6f0d8dda7d496502`
