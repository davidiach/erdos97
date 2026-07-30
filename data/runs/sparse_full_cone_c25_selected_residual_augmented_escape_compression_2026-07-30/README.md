# C25 selected-residual augmented escape compression

Status: bounded fixed-pattern, fixed-order exact-certificate diagnostic. No
all-order obstruction, geometric counterexample, general proof, or
official-status update is claimed.

This packet samples deterministic alternative LP objectives for the eight
wide exact certificates learned by the 168-history five-seed C25 CEGAR. Every
retained support is exactified, checked as a positive circuit, and expanded
through all 25 quotient-preserving translations.

## Result

- Source widths: `219, 220, 214, 216, 211, 217, 219, 210`.
- Compressed widths: `7, 6, 4, 4, 9, 6, 4, 3`.
- Exact compressed certificates: `8/8`.
- New clause orbits relative to all five active source seeds: `8/8`.
- Exact affine certificate images replayed: `200`.
- Coverage targets: `16` probe and `8` five-seed-escaping residual orders.
- The four parent seeds cover `16/24`; the old selected width-3 seed adds zero
  marginal targets.
- The new compressed affine orbits cover `20/24`; together with the four
  parent seeds they cover `24/24`.
- Exact cross-source reuse: `31` direct and `129` affine edges.
- The new width-4 orbit from `residual:2` alone covers all eight residual
  targets and is the exact one-source minimum residual cover.
- Decision:
  `REPLACE_NONMARGINAL_WIDTH3_WITH_MINIMUM_COMPRESSED_ESCAPE_COVER`.

Generate:

```bash
python scripts/exploration/compress_sparse_full_cone_c25_selected_residual_augmented_escapes.py \
  --out data/runs/sparse_full_cone_c25_selected_residual_augmented_escape_compression_2026-07-30/summary.json
```

Replay:

```bash
python scripts/exploration/compress_sparse_full_cone_c25_selected_residual_augmented_escapes.py \
  --check data/runs/sparse_full_cone_c25_selected_residual_augmented_escape_compression_2026-07-30/summary.json
```

SHA-256 of `summary.json`:

`8098645542bcfa4775295baf4262b9abf10e0f8b13aaa13b87badfbef1976a4f`
