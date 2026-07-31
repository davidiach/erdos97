# C25 persistent-augmented residual compression

Status: bounded fixed-pattern, fixed-order exact-certificate diagnostic. No
all-order obstruction, geometric counterexample, general proof, or
official-status update is claimed.

This packet samples deterministic alternative LP objectives for the eight
wide exact certificates learned by the 144-history-blocked C25 persistent
width-4 augmented CEGAR. Every retained support is exactified, checked as a
positive circuit, and expanded through all 25 quotient-preserving
translations.

## Result

- Source widths: `197, 197, 193, 194, 192, 200, 191, 195`.
- Compressed widths: `6, 6, 3, 8, 4, 7, 3, 4`.
- Exact compressed certificates: `8/8`.
- New clause orbits relative to the four active seeds: `8/8`.
- Exact affine certificate images replayed: `200`.
- Coverage targets: `16` probe orders and `8` active-seed-escaping residual
  orders.
- Active seeds cover `16/24`; the compressed residuals cover the complementary
  `8/24`; together they cover `24/24`.
- Exact residual cross-coverage: `22` direct and `54` affine edges.
- The width-3 orbit from `residual:2` alone covers all eight residual targets;
  exhaustive source-subset enumeration verifies an exact one-source minimum
  affine cover with total width `3`.
- Decision:
  `ADD_MINIMUM_COMPRESSED_RESIDUAL_COVER_BEFORE_NEXT_C25_ORDER_SEARCH`.

Generate:

```bash
python scripts/exploration/compress_sparse_full_cone_c25_persistent_augmented_residuals.py \
  --out data/runs/sparse_full_cone_c25_persistent_augmented_residual_compression_2026-07-30/summary.json
```

Replay without rerunning the objective search:

```bash
python scripts/exploration/compress_sparse_full_cone_c25_persistent_augmented_residuals.py \
  --check data/runs/sparse_full_cone_c25_persistent_augmented_residual_compression_2026-07-30/summary.json
```

SHA-256 of `summary.json`:

`b4d620a5039365b63fa16c906e604f45e0bdacb364a8fb4a9a5e42a7c040526e`
