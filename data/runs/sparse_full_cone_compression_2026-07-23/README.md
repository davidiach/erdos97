# Sparse full-cone certificate compression (2026-07-23)

Status: `BOUNDED_CLAUSE_COMPRESSION_DIAGNOSTIC`.

Every retained certificate is exact, but the randomized alternative-circuit
search is not exhaustive. No all-order C25/C29 obstruction, geometric
realization, counterexample, or proof of Erdos Problem #97 is claimed.

## Run

```bash
python scripts/exploration/compress_sparse_full_cone_certificates.py \
  --trials 24 \
  --seed 0 \
  --tolerance 1e-9 \
  --out data/runs/sparse_full_cone_compression_2026-07-23/summary.json
```

The input models are the four full-cone CEGAR orders that also escape
vertex-circle and Altman filters. Each stored source support is already an
exact positive circuit, so direct row deletion cannot compress it. The script
samples alternative LP extreme points over all fixed-order Kalmanson rows and
exactifies each improving support.

| Pattern | Source model | Source quads | Compressed quads | Reduction |
|---|---:|---:|---:|---:|
| `C25_sidon_2_5_9_14` | 2 | 205 | 100 | 51.2% |
| `C29_sidon_1_3_7_15` | 0 | 304 | 204 | 32.9% |
| `C29_sidon_1_3_7_15` | 1 | 302 | 213 | 29.5% |
| `C29_sidon_1_3_7_15` | 2 | 306 | 208 | 32.0% |

The compressed C29 model-2 clause covers both strong source models 1 and 2.
The other three clauses cover their own source model only within this small
packet. This is bounded cross-model reuse evidence, not order-space coverage.

## Replay

```bash
python scripts/exploration/compress_sparse_full_cone_certificates.py \
  --check data/runs/sparse_full_cone_compression_2026-07-23/summary.json
```

Expected: four compressed exact certificates verify, together with their
ordered-quad counts, reductions, and coverage matrix.

SHA-256 of `summary.json`:

```text
bc084a5949c796e781718a85306edcb84bc326d19255ff86f30d0716458a36fa
```
