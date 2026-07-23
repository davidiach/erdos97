# Sparse full-cone order CEGAR pilot (2026-07-22)

Status: `BOUNDED_FULL_CONE_CERTIFICATE_LIMIT_REACHED` for both fixed
patterns. No general proof, all-order obstruction, geometric realization, or
counterexample is claimed.

## Method

The pilot searches cyclic orders with Z3. It first learns exact clauses for
every encountered two-inequality Kalmanson inverse pair. When an order escapes
that filter, an exact full Kalmanson/Farkas certificate is generated. The
ordered quadrilaterals in that certificate produce one stronger clause that
forbids every cyclic order realizing the entire certificate support.

Thus each full-cone iteration blocks an order family, not only the current
model. A certificate-limit result remains bounded and does not prove all-order
coverage.

## Run

```bash
python scripts/exploration/pilot_sparse_full_cone_order_cegar.py \
  --full-certificate-limit 3 \
  --max-iterations 2000 \
  --conflict-cap 1024 \
  --random-seed 7 \
  --out data/runs/sparse_full_cone_cegar_2026-07-22/summary.json
```

| Pattern | Z3 iterations | Inverse-pair clauses | Full-cone clauses | Models passing vertex-circle + Altman |
|---|---:|---:|---:|---:|
| `C25_sidon_2_5_9_14` | 530 | 14,921 | 3 | 1/3 |
| `C29_sidon_1_3_7_15` | 432 | 20,568 | 3 | 3/3 |

The C25 full certificates use 196, 188, and 205 distinct ordered
quadrilaterals. The C29 certificates use 304, 302, and 306. All six orders are
independently replayed as exact escapes from the direct inverse-pair filter,
and all six full-cone certificates verify as exact weighted zero sums.

## Replay

```bash
python scripts/exploration/pilot_sparse_full_cone_order_cegar.py \
  --check data/runs/sparse_full_cone_cegar_2026-07-22/summary.json
```

Expected: six inverse-pair escape orders and six exact full-cone certificates
verify.

SHA-256 of `summary.json`:

```text
500db3c990ae9d6db520cd8ce591cb76af7afdd87d893d6fd3285bce7ec0a75c
```
