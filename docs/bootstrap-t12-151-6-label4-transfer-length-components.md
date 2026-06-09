# Bootstrap T12 151:6 Label-4 Transfer Length Components

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines the source-`151` row-`6` private-lane residual target from
row-local equality obligations to undirected segment-length components. The
previous obligation ledger records which centered equal-distance statements
are used by positive label-`4` transfer paths. This packet forgets the row
orientation and records the geometric segment equalities and cyclic gap
profiles those obligations force.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_transfer_length_components.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_transfer_length_components.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_transfer_length_components.json
```

## Inputs

This packet is a derivative check over:

- `data/certificates/bootstrap_t12_151_6_label4_transfer_obligations.json`.

Each unique transfer-path motif induces one undirected component of equal
segment lengths.

## Length-Component Result

Pinned summary:

| Quantity | Value |
| --- | ---: |
| positive transfer signature incidences | `8` |
| positive transfer occurrence incidences | `9` |
| length components | `6` |
| distinct segments in those components | `9` |
| two-segment components | `5` |
| three-segment components | `1` |
| components containing a hull edge | `4` |
| diagonal-only components | `2` |
| components with an edge-to-diagonal equality | `4` |
| components touching target center `6` | `1` |
| components containing the row-`6` connector step | `1` |

Geometry-class split:

| Geometry class | Component count | Signature incidences | Occurrence incidences |
| --- | ---: | ---: | ---: |
| `edge_diagonal_equality` | `3` | `3` | `3` |
| `edge_edge_diagonal_chain` | `1` | `3` | `4` |
| `diagonal_only_equality` | `2` | `2` | `2` |

The unique segment cyclic-gap profile is:

| Cyclic gap | Segment count |
| ---: | ---: |
| `1` | `2` |
| `2` | `1` |
| `3` | `4` |
| `4` | `2` |

The only component that reaches row `6` is:

```text
D[0,6] = D[4,5] = D[5,6]
```

This is the repeated row-`5`/row-`6` connector cascade. It contains two hull
edges, `D[4,5]` and `D[5,6]`, tied to the cyclic-gap-`3` diagonal `D[0,6]`.

The remaining positive transfers split into:

- three row-`5` edge-to-diagonal equalities:
  `D[4,5]=D[5,7]`, `D[4,5]=D[0,5]`, and `D[4,5]=D[2,5]`;
- two row-`7` diagonal-only equalities:
  `D[4,7]=D[1,7]` and `D[4,7]=D[2,7]`.

## Reading

The next proof-facing target is now support-geometric:

```text
Any genuine source-151 row-6 private-halo residual support using a positive
label-4 transfer must realize one of six equal-length segment components; the
only route through row 6 is the edge-edge-diagonal cascade
D[0,6]=D[4,5]=D[5,6].
```

This does not prove that the residual support geometry is impossible. It turns
the row-local label-`4` transfer obligations into exact edge/diagonal cases
that a future support-geometry lemma can attack directly.

## What This Does Not Prove

This artifact does not prove outside-pair support existence, does not prove row
forcing, does not prove that pair `[3,5]` is impossible, does not prove
endpoint-`8` forcing, does not prove `n=9`, does not prove the bootstrap
bridge, and does not prove Erdos Problem #97.
