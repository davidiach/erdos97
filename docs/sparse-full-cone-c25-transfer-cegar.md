# C25 transferred-clause seeded CEGAR

Status: bounded fixed-pattern exact-clause search over history-disjoint C25
orders. No general proof, all-order C25 obstruction, geometric counterexample,
or official-status change is claimed.

## Target

The outside-packet audit in
`docs/sparse-full-cone-fresh-template-transfer.md` found that the C25 width-3
and width-5 circuits transfer to both the prior packet and a second
history-disjoint stream. The width-14 C25 circuit transfers to the prior packet
only. The C29 template family did not transfer and is deliberately absent from
this experiment.

This follow-up asks how much the three exact C25 seed orbits prune a genuinely
new order stream, and whether seed-escaping orders yield exact full-cone
certificates.

## Exact seed and history protocol

`scripts/exploration/run_sparse_full_cone_c25_transfer_cegar.py` assigns:

- width 3 and width 5: `PRIMARY_CROSS_STREAM_TRANSFER`;
- width 14: `SECONDARY_PRIOR_PACKET_TRANSFER`.

The selected-distance quotient admits translations only. The three seed
circuits therefore produce 75 exact affine images, all replayed before their
ordered-quadrilateral clauses are used.

Both solver phases block 88 known C25 orders and their reversals:

| Packet | Blocked C25 orders |
| --- | ---: |
| Prior probe/seeded packet | 24 |
| First fresh stream | 32 |
| Second fresh stream | 32 |
| **Total** | **88** |

The 88 orders are distinct under cyclic rotation and reversal. History
blocking is a novelty device, not a proof rule; it prevents any solver status
from being interpreted as an all-order conclusion.

## Counterfactual seed coverage

The probe learns inverse-pair clauses but does not activate the transferred
full-cone seeds. It finds 16 new history-disjoint inverse-pair escape orders,
all of which also survive the vertex-circle and both Altman filters.

| Seed width | Matched probe orders | Matching affine-clause occurrences |
| ---: | ---: | ---: |
| 14 | 7/16 | 7 |
| 5 | 14/16 | 33 |
| 3 | 14/16 | 127 |

The union covers 14/16 probe orders. Thus the width-3 and width-5 circuits
retain high exact coverage after excluding every order used in their discovery
and transfer audits.

The probe reaches its 16-order limit after 519 iterations with 14,761 learned
inverse-pair clauses.

## Seeded CEGAR result

The seeded phase starts with the probe's inverse-pair clauses and all 75
transferred seed clauses active. Each seed-escaping order is screened against
the complete fixed-order Kalmanson row family. Every recovered certificate is
expanded through its 25 exact translations before the search continues.

| Model | Lightweight survivor | Exact support | Quad width | New affine clauses |
| ---: | --- | ---: | ---: | ---: |
| 0 | yes | 199 | 199 | 25 |
| 1 | yes | 191 | 190 | 25 |
| 2 | yes | 200 | 200 | 25 |
| 3 | yes | 194 | 193 | 25 |
| 4 | yes | 194 | 194 | 25 |
| 5 | yes | 197 | 197 | 25 |
| 6 | yes | 191 | 191 | 25 |
| 7 | yes | 199 | 199 | 25 |

All eight orders are history-disjoint, escape every transferred seed image and
every previously learned image, and have exact positive zero-sum
certificates. The checker replays 275 exact affine certificate images: 75
seeds plus 200 learned images.

The run stops after 21 seeded iterations at the configured
eight-certificate limit. It does not reach UNSAT, and it finds no unresolved
full-cone screen or coordinate target.

## Decision and next target

The transferred C25 circuits are genuinely reusable order-search clauses, but
the first residual certificates are again wide. The completed follow-up in
`docs/sparse-full-cone-c25-transfer-residual-compression.md` compresses all
eight to exact widths `3`--`9`. One new width-`3` orbit covers all eight
residual orders and 14/16 probe orders, while the two original seed-escaping
probe orders remain uncovered. The continuation rule therefore fires:
compare width-`3`-only and all-eight residual augmentation on a new
history-disjoint C25 probe before extending the certificate-learning limit.

Replay:

```bash
python scripts/exploration/run_sparse_full_cone_c25_transfer_cegar.py \
  --check data/runs/sparse_full_cone_c25_transfer_cegar_2026-08-03/summary.json
```
