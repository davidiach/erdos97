# Free-Cartesian sparse-order preflight (2026-07-22)

Status: `NO_COUNTEREXAMPLE_FOUND_IN_BOUNDED_RUN`.

Trust: exact fixed-order certificates plus bounded numerical-search plumbing.
No general proof and no counterexample are claimed.

## Run

```bash
python scripts/exploration/search_free_cartesian_sparse.py \
  --orders-per-pattern 12 \
  --seed 20260722 \
  --restarts 12 \
  --max-nfev 6000 \
  --out data/runs/free_cartesian_sparse_2026-07-22/summary.json
```

The 12 C25 and 12 C29 orders all passed the lightweight crossing,
vertex-circle, and Altman screens. Every order was then killed by a stored and
independently replayable exact Kalmanson/Farkas certificate. Consequently the
free-Cartesian optimizer correctly made zero coordinate attempts.

| Pattern | Orders | Lightweight survivors | Exact fixed-order obstructions | Coordinate attempts | Candidates |
|---|---:|---:|---:|---:|---:|
| `C25_sidon_2_5_9_14` | 12 | 12 | 12 | 0 | 0 |
| `C29_sidon_1_3_7_15` | 12 | 12 | 12 | 0 | 0 |

C25 certificate supports contain 177--207 strict inequalities; C29 supports
contain 263--288. These are fixed-order conclusions only. The 24-order sample
is not cyclic-order coverage and is not an obstruction for either abstract
pattern.

## Replay

```bash
python scripts/exploration/search_free_cartesian_sparse.py \
  --check data/runs/free_cartesian_sparse_2026-07-22/summary.json
```

Expected result: `24` exact fixed-order certificates verify and there are zero
numerical candidates.

SHA-256 of `summary.json`:

```text
b76b25d8a6fc8a5d4bf441e3c3bb5fb66e38e07c675a685221f07935e3b6c62e
```
