# Sparse full-cone fresh certificate compression

Status: bounded randomized search with exact fixed-pattern, fixed-order
certificates and coverage replay. No all-order obstruction, geometric
counterexample, general proof, or official-status update is claimed.

This run applies six deterministic alternative LP objectives to each of the 63
exact positive circuits in
`data/runs/sparse_full_cone_fresh_order_screen_2026-07-31/summary.json`.
Numerical supports are retained only after exact integer recovery, exact
zero-sum replay, and a modular-rank positive-circuit audit.

Every retained certificate is expanded through all exact
quotient-preserving affine maps, and its direct and affine-orbit clause
coverage is recomputed over the same 63-order fresh packet.

## Result

| Pattern | Sources | Improved | Width range | New width <= 12 | Direct cross-edges | Affine cross-edges |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `C25_sidon_2_5_9_14` | 31 | 31 | 3-143 | 2 | 58 | 90 |
| `C29_sidon_1_3_7_15` | 32 | 32 | 7-214 | 1 | 6 | 6 |
| **Total** | **63** | **63** |  | **3** | **64** | **96** |

The predeclared stopping rule therefore returns
`CONTINUE_CLUSTER_MINING` for both patterns. This is a bounded packet-level
decision, not evidence of all-order coverage.

Generate:

```bash
python scripts/exploration/compress_sparse_full_cone_fresh_certificates.py \
  --out data/runs/sparse_full_cone_fresh_compression_2026-08-01/summary.json
```

Replay without solving the randomized LPs:

```bash
python scripts/exploration/compress_sparse_full_cone_fresh_certificates.py \
  --check data/runs/sparse_full_cone_fresh_compression_2026-08-01/summary.json
```

SHA-256 of `summary.json`:

`53cc04f72ff7671871a1b2907afdbf942b89d5f6ffca0bc2c74556f5c82a528b`
