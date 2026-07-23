# Sparse full-cone seeded affine CEGAR

Status: bounded fixed-pattern exact-clause diagnostic. No general proof,
all-order C25/C29 obstruction, geometric counterexample, or official-status
change is claimed.

## Exact seed expansion

The four compressed certificates in
`data/runs/sparse_full_cone_compression_2026-07-23/summary.json` were used as
seeds. Before an image entered Z3, the checker required its affine label map to
preserve the complete selected-distance quotient partition and replayed the
transformed positive certificate exactly.

For both patterns, the only accepted multiplier was `1`. All translations are
valid, giving one `25`-clause orbit for C25 and three disjoint `29`-clause
orbits for C29. In particular, multiplier `-1` (reflection) does not preserve
either selected-distance quotient. The exact expansion is cyclic, not
dihedral.

## Counterfactual hit-count probe

Seed clauses cannot be counted after they are active because Z3 never returns
a model they block. The experiment therefore first enumerated a separate
bounded stream of inverse-pair escape orders. Each order was exactly blocked
only after its seed-orbit matches were recorded. The seeded solver was then
rebuilt with the learned inverse-pair clauses and all valid seed images active
from the start.

| Pattern | Probe iterations | Inverse clauses | Probe orders | Strong probe orders | Seed-covered probe orders |
|---|---:|---:|---:|---:|---:|
| `C25_sidon_2_5_9_14` | 394 | 13,538 | 16 | 16 | 0 |
| `C29_sidon_1_3_7_15` | 417 | 19,692 | 16 | 16 | 0 |

Here ?strong? means the order also escapes the vertex-circle, Altman
signature, and exact Altman-linear filters. Thus the previously observed
C29 model-2 clause coverage of source model 1 did not persist in this fresh
32-order stream, even after all exact translations were included.

This is bounded negative evidence about reuse, not proof that the seed clauses
never recur.

## Longer seeded CEGAR result

Every newly found exact certificate was itself expanded through its complete
valid translation orbit before the search continued:

| Pattern | Seed clauses | Seeded iterations | Final inverse clauses | New exact certificates | New clause widths | New translated clauses | Strong new models |
|---|---:|---:|---:|---:|---|---:|---:|
| `C25_sidon_2_5_9_14` | 25 | 32 | 13,873 | 8 | 188, 202, 209, 208, 204, 206, 205, 208 | 200 | 7/8 |
| `C29_sidon_1_3_7_15` | 87 | 77 | 20,734 | 8 | 294, 294, 291, 293, 290, 289, 289, 292 | 232 | 8/8 |

All `16` new source certificates and all `544` seed/learned affine images
verify as exact positive zero sums. Every learned orbit has full translation
size (`25` or `29`), and all `16` new canonical orbit hashes are distinct.
Both searches stopped at the configured eight-certificate limit, not at
UNSAT.

## Next target

Compress the `16` new certificates, then measure the compressed clauses across
all `48` stored fresh orders (the `32` probe orders plus `16` seeded models).
Because raw seed reuse was zero in the fresh probe, prioritize shared
quotient-vector supports and unions of small circuits instead of assuming that
one large certificate orbit will recur.

Replay:

```bash
python scripts/exploration/run_sparse_full_cone_seeded_cegar.py \
  --check data/runs/sparse_full_cone_seeded_cegar_2026-07-23/summary.json
```
