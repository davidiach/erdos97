# Sparse full-cone small-template fresh stream

Status: bounded exact-template transfer diagnostic over deterministic
history-disjoint fixed-pattern orders. No general proof, all-order C25/C29
obstruction, geometric counterexample, or official-status change is claimed.

## Canonical template packet

The source compression artifact
`data/runs/sparse_full_cone_seeded_compression_2026-07-29/summary.json`
contains seven exact positive circuits with at most eight ordered
quadrilaterals:

| Pattern | Source models | Widths | Affine images |
| --- | --- | --- | ---: |
| `C25_sidon_2_5_9_14` | `0,2,3,7` | `7,8,5,3` | 100 |
| `C29_sidon_1_3_7_15` | `0,1,7` | `5,4,4` | 87 |

`scripts/exploration/probe_sparse_full_cone_small_templates.py` reconstructs
each source certificate, applies every quotient-preserving multiplier and
translation, chooses the lexicographically first exact certificate image for
the lexicographically first ordered-quadrilateral clause, and stores that
certificate explicitly. All seven canonical certificates have unit weights
and exact zero quotient-vector sum. Their canonical clause hashes are
distinct.

## Freshness protocol

The source packet contains 24 stored orders per pattern: 16 counterfactual
probe orders and eight seeded CEGAR orders. Before generating a fresh stream,
the solver blocks each of those orders and its reversal. Every new order and
its reversal are also blocked immediately after discovery. Thus all 32 fresh
orders per pattern are distinct from the historical packet and from one
another under cyclic rotation and reversal.

The stream uses fresh deterministic Z3 seeds (`20260730` for C25 and
`20261730` for C29) and retains only orders that independently replay with
zero two-inequality inverse-pair conflicts. This uses the repository's
existing order solver and inverse-pair implementation. “Fresh” therefore
means deterministic and history-disjoint; it is not a statistical
independence claim or an independent implementation.

The seven templates are not asserted as blocking clauses while the stream is
generated. Doing that would force a zero-hit result by construction. They are
loaded only to compute exact post-generation coverage.

## Exact transfer result

| Pattern | Templates | Fresh orders | Lightweight survivors | Template-covered | Iterations | Learned inverse clauses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| C25 | 4 | 32 | 31 | 0 | 525 | 14,623 |
| C29 | 3 | 32 | 32 | 0 | 489 | 20,817 |
| **Total** | **7** | **64** | **63** | **0** |  |  |

No fresh order contains the ordered-quadrilateral support of any of the 187
exact affine template images. In particular, none of the 63 fresh orders that
also survive the vertex-circle and both Altman filters is covered.

Together with the earlier zero hits on 32 counterfactual probe orders, this
supports treating the seven tiny circuits as cluster-specific diagnostics in
the current bounded workstream rather than prospective broad order-search
clauses. It does not prove that their coverage is finite or characterize every
order they cover.

## Limitations and next target

The stream is bounded, solver-selected, and nonuniform. It does not enumerate
cyclic orders, rerun the full Kalmanson cone on the fresh orders, or address
geometric realizability. A zero template hit is not evidence that an order
escapes the full cone: a different positive circuit may still obstruct it.

The next useful step is therefore to run the exact full-cone certificate
screen on the 63 fresh lightweight survivors. Any order with no exact
certificate becomes a higher-priority coordinate/geometry target; otherwise,
compress only the newly observed certificates and test whether they define a
new order cluster before adding more template-seeded search.

Replay:

```bash
python scripts/exploration/probe_sparse_full_cone_small_templates.py \
  --check data/runs/sparse_full_cone_small_template_fresh_stream_2026-07-29/summary.json
```
