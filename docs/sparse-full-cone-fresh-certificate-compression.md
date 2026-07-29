# Sparse full-cone fresh certificate compression

Status: bounded alternative-objective search with exact fixed-pattern,
fixed-order outputs. No general proof, all-order C25/C29 obstruction,
geometric counterexample, or official-status change is claimed.

## Target and stopping rule

The exact fresh-order screen in
`docs/sparse-full-cone-fresh-order-screen.md` produced 63 positive circuits
whose widths were 197-217 for C25 and 282-304 for C29. The earlier seven
three-to-eight-quad templates covered none of these orders.

This follow-up asks whether a small deterministic alternative-objective budget
can expose a new small circuit or exact reuse inside the fresh packet. Before
the run, "small" was fixed at width at most 12. The cluster-mining route stops
only if no new small clause and no direct or quotient-preserving affine
cross-order reuse appears.

## Exact protocol

`scripts/exploration/compress_sparse_full_cone_fresh_certificates.py` samples
six seeded LP objectives per source order. A numerical support is retained
only when:

1. exact positive integer weights are recovered;
2. exact quotient-vector replay gives zero;
3. modular rank proves that the support is a positive circuit; and
4. its ordered-quadrilateral width improves on the stored source certificate.

The retained circuits are expanded through all quotient-preserving affine
maps. Every transformed certificate and every claimed coverage edge is
recomputed exactly by the checker, which also requires exactly one compressed
row for every source record. The LP search is bounded and non-exhaustive;
only the stored certificates and coverage edges are exact conclusions.

## Compression result

| Pattern | Sources | Exact improvements | Source width | Compressed width | Reduction range |
| --- | ---: | ---: | ---: | ---: | ---: |
| `C25_sidon_2_5_9_14` | 31 | 31 | 197-217 | 3-143 | 66-208 |
| `C29_sidon_1_3_7_15` | 32 | 32 | 282-304 | 7-214 | 86-292 |

Most retained circuits remain large: 28 of 31 C25 widths and 31 of 32 C29
widths exceed 100. The low-budget search nevertheless finds three new
unit-weight circuits below the predeclared threshold:

| Pattern | Source | Width | Best trial | Direct targets | Affine-orbit targets |
| --- | ---: | ---: | ---: | ---: | ---: |
| C25 | `fresh:19` | 5 | 5 | 7/31 | 29/31 |
| C25 | `fresh:28` | 3 | 1 | 21/31 | 31/31 |
| C29 | `fresh:28` | 7 | 5 | 6/32 | 6/32 |

None of these canonical clause orbits occurs in the prior 16-certificate
compression packet. A fourth new C25 circuit, width 14 from `fresh:15`, covers
25 of 31 targets directly and affinely.

## Exact fresh-packet reuse

| Pattern | Direct cross-edges | Affine cross-edges | Directly covered targets | Affinely covered targets |
| --- | ---: | ---: | ---: | ---: |
| C25 | 58 | 90 | 31/31 | 31/31 |
| C29 | 6 | 6 | 32/32 | 32/32 |
| **Total** | **64** | **96** | **63/63** | **63/63** |

Self-coverage is excluded from the edge counts. Every target is covered
because each retained source certificate covers its own order; the cross-edge
counts measure additional reuse.

The C25 width-3 circuit is the strongest bounded reuse signal: its affine
orbit covers all 31 C25 targets. The C29 width-7 circuit covers one six-order
cluster and gains no additional target under affine expansion.

Quotient-vector frequency remains diffuse. Across the 31 C25 certificates,
3,208 distinct vectors occur, 338 are shared, and the maximum certificate
frequency is five. Across C29, the corresponding values are 5,613, 321, and
four. The high C25 clause reuse is therefore carried by a few small circuits,
not a large common quotient-vector core.

## Decision and next target

Both patterns return `CONTINUE_CLUSTER_MINING`: the bounded stopping condition
does not fire because new small circuits and exact cross-order reuse exist.
This reverses only the proposed route decision, not any mathematical status.

That audit is completed in
`docs/sparse-full-cone-fresh-template-transfer.md`. The C25 width-`3` and
width-`5` circuits transfer to both the prior packet and a second
history-disjoint stream, while the C29 width-`7` circuit has zero hits across
all 56 outside-source targets. Continue only the C25 exact-clause route and
stop packet-specific C29 template mining.

Replay:

```bash
python scripts/exploration/compress_sparse_full_cone_fresh_certificates.py \
  --check data/runs/sparse_full_cone_fresh_compression_2026-07-29/summary.json
```
