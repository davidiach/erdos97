# C25 transfer-CEGAR residual compression

Status: bounded fixed-pattern, fixed-order exact-certificate diagnostic. No
all-order obstruction, geometric counterexample, general proof, or
official-status update is claimed.

This packet samples deterministic alternative LP objectives for the eight
wide exact certificates learned by the C25 transferred-clause seeded CEGAR.
Every retained support is exactified, checked as a positive circuit, and
expanded through all 25 quotient-preserving translations.

## Result

- Source widths: `199, 190, 200, 193, 194, 197, 191, 199`.
- Compressed widths: `7, 9, 5, 3, 7, 4, 6, 4`.
- Exact compressed certificates: `8/8`.
- New clause orbits relative to the three active transferred seeds: `8/8`.
- Exact affine certificate images replayed: `200`.
- Coverage targets: `16` probe orders and `8` residual orders.
- Affine coverage: `22/24` targets and `150` cross-coverage edges.
- Direct residual coverage: `8/8` targets and `16` cross-coverage edges.
- The new width-`3` orbit from `seeded:3` alone covers all eight residual
  targets; exhaustive enumeration verifies that this is a one-source minimum
  affine cover with total width `3`.
- Probe orders `probe:0` and `probe:1` are covered by neither the three
  transferred seeds nor any of the eight compressed residual orbits.
- Stop decision:
  `CONTINUE_C25_CLAUSE_EXPANSION_WITH_COMPRESSED_RESIDUALS`.

Generate:

```bash
python scripts/exploration/compress_sparse_full_cone_c25_transfer_residuals.py \
  --out data/runs/sparse_full_cone_c25_transfer_residual_compression_2026-07-29/summary.json
```

Replay without rerunning the LP objective search; the checker requires one
compressed row per source and validates the stored trial provenance:

```bash
python scripts/exploration/compress_sparse_full_cone_c25_transfer_residuals.py \
  --check data/runs/sparse_full_cone_c25_transfer_residual_compression_2026-07-29/summary.json
```

SHA-256 of `summary.json`:

`e90b7af7af1bac40d61606b6e9f7d400232bbe6d648860e5cc0d8519b2536dea`
