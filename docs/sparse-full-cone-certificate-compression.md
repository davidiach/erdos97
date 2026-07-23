# Sparse full-cone certificate compression

Status: bounded randomized search with exact fixed-order outputs. No general
proof, all-order C25/C29 obstruction, geometric counterexample, or official
status change is claimed.

## Why deletion is not the operation

The six certificates from the first full-cone CEGAR pilot were produced as
positive circuits: their quotient-row matrix has a one-dimensional nullspace
with a strictly positive generator. Therefore no proper subset of one stored
support can retain a zero dependency. Clause compression must find a different
positive circuit, not delete rows from the existing one.

`scripts/exploration/compress_sparse_full_cone_certificates.py` does this by
assigning deterministic pseudorandom linear costs to all fixed-order
Kalmanson rows. Each LP optimum samples a different extreme positive
dependency. A numerically smaller support is retained only after exact integer
weights are recovered and the selected-distance quotient sum is independently
verified as zero.

## Exact bounded result

Twenty-four objectives were sampled for each of the four CEGAR models that
also survive vertex-circle and Altman filters:

| Pattern | Model | Original width | Exact compressed width | Removed | Reduction |
|---|---:|---:|---:|---:|---:|
| `C25_sidon_2_5_9_14` | 2 | 205 | 100 | 105 | 51.2% |
| `C29_sidon_1_3_7_15` | 0 | 304 | 204 | 100 | 32.9% |
| `C29_sidon_1_3_7_15` | 1 | 302 | 213 | 89 | 29.5% |
| `C29_sidon_1_3_7_15` | 2 | 306 | 208 | 98 | 32.0% |

All four compressed supports are exact positive circuits. They remain large,
but the C25 clause is less than half the original width and every C29 clause
loses roughly one third of its ordered quadrilaterals.

## Cross-model coverage

Within the strong source packet:

- C25 model 2 covers only model 2;
- C29 model 0 covers only model 0;
- C29 model 1 covers only model 1;
- C29 model 2 covers models 1 and 2.

The last row is the first observed reusable full-cone clause in this workstream:
one exact compressed dependency blocks two independently discovered
inverse-pair/vertex-circle/Altman escape orders. Four models are far too few to
infer general coverage.

## Next target

Seed the full-cone CEGAR solver with these compressed clauses and extend the
model budget. Record clause hit counts before generating a new certificate.
If the reusable C29 clause continues to block multiple models, mine its
translation/automorphism orbit and shared quotient-vector structure. If a
model escapes the full cone entirely, hand it to the guarded free-Cartesian
solver.

Replay:

```bash
python scripts/exploration/compress_sparse_full_cone_certificates.py \
  --check data/runs/sparse_full_cone_compression_2026-07-23/summary.json
```
