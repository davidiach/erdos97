# Sparse full-cone fresh-template transfer audit

Status: bounded exact-template transfer over fixed C25/C29 order packets. No
general proof, all-order C25/C29 obstruction, geometric counterexample, or
official-status change is claimed.

## Target

The fresh-certificate compression in
`docs/sparse-full-cone-fresh-certificate-compression.md` found three new
unit-weight circuits below its predeclared width-12 threshold:

- C25 widths 3 and 5;
- C29 width 7.

It also found a C25 width-14 circuit whose affine orbit covers 25 of 31 source
targets. The same-packet stopping rule therefore returned continue, but
same-packet reuse can still be a generator cluster effect.

This audit asks whether those four circuits transfer outside the 63-order
source packet.

## Exact template selection

`scripts/exploration/probe_sparse_full_cone_fresh_template_transfer.py`
selects a compressed certificate exactly when:

1. its width is at most 12; or
2. its affine orbit covers at least 24 source targets.

Each selected circuit is canonicalized under every quotient-preserving affine
map. The resulting four canonical clause hashes are distinct, all
certificates have exact unit weights, and the acting groups contain 104 maps:
75 across the three C25 templates and 29 for the C29 template.

## Outside-packet protocol

The templates are replayed over two target packets.

First, the prior compression packet contributes 24 stored orders per pattern:
16 counterfactual probes and eight seeded CEGAR orders.

Second, a new deterministic solver stream contributes 32 orders per pattern.
Before generation, the solver blocks:

- all 24 prior orders per pattern and their reversals; and
- all 32 orders per pattern from the first fresh stream and their reversals.

Thus each second stream is disjoint under cyclic rotation and reversal from 56
historical orders of the same pattern. The new seeds are `20260802` for C25
and `20261802` for C29. Every retained order exactly replays with zero
two-inequality inverse-pair conflicts.

Templates are evaluated only after an order is generated. They are never
asserted as blocking clauses, so zero hits are not forced by construction.

## Exact transfer result

| Pattern | Templates | Source covered | Prior covered | Prior strong covered | Second covered | Second strong covered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `C25_sidon_2_5_9_14` | 3 | 31/31 | 16/24 | 16/23 | 16/32 | 16/32 |
| `C29_sidon_1_3_7_15` | 1 | 6/32 | 0/24 | 0/24 | 0/32 | 0/32 |

The exact per-template coverage is:

| Pattern | Source | Width | Source hits | Prior hits | Second-stream hits |
| --- | ---: | ---: | ---: | ---: | ---: |
| C25 | `fresh:15` | 14 | 25 | 8 | 0 |
| C25 | `fresh:19` | 5 | 29 | 9 | 16 |
| C25 | `fresh:28` | 3 | 31 | 16 | 14 |
| C29 | `fresh:28` | 7 | 6 | 0 | 0 |

The C25 width-3 and width-5 circuits both transfer to a second
history-disjoint stream. Their union covers 16 of the 32 second-stream orders.
The width-14 C25 circuit transfers back to the prior packet but not to the
second stream.

The C29 width-7 circuit has zero coverage across all 56 outside-source targets.
Its observed reuse remains confined to six orders of its source cluster.

## Route decision

The predeclared rule stops packet-specific mining only when both outside
packets have zero hits. It therefore yields different decisions:

- C25: `CONTINUE_EXACT_TEMPLATE_TRANSFER`;
- C29: `STOP_PACKET_SPECIFIC_TEMPLATE_MINING`.

This is a bounded search-policy decision, not an all-order conclusion. For C25,
the next useful experiment is a C25-only exact clause-seeded CEGAR run using
the transferable width-3 and width-5 orbits, with the width-14 orbit retained
as a secondary prior-packet clause. For C29, do not spend another objective or
fresh-stream budget on the current template family unless a new structural
reason appears.

Replay:

```bash
python scripts/exploration/probe_sparse_full_cone_fresh_template_transfer.py \
  --check data/runs/sparse_full_cone_fresh_template_transfer_2026-08-02/summary.json
```
