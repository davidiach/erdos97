# Bootstrap T12 151:6 Label-4 Transfer Obligations

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines the source-`151` row-`6` private-lane residual target from
selected-distance transfer paths to row-local equality obligations. The
previous transfer-path ledger pins shortest selected-distance paths from
label-`4` pairs to strict-cycle endpoint pairs. This packet records which
centered equal-distance statements those positive-length paths require.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_transfer_obligations.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_transfer_obligations.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_transfer_obligations.json
```

## Inputs

This packet is a derivative check over:

- `data/certificates/bootstrap_t12_151_6_label4_transfer_paths.json`.

It keeps only positive-length transfer paths. Direct endpoint hits are already
visible at the strict-cycle endpoint and add no extra row-local transfer
obligation.

## Obligation Result

Pinned summary:

| Quantity | Value |
| --- | ---: |
| positive transfer class incidences | `8` |
| occurrence-weighted positive transfer incidences | `9` |
| row-local transfer equality edges | `11` |
| occurrence-weighted transfer equality edges | `13` |
| unique path motifs | `6` |
| unique edge obligations | `7` |
| label-`4` spoke-swap edges | `8` |
| occurrence-weighted label-`4` spoke-swap edges | `9` |
| target-center-touching edges | `6` |
| occurrence-weighted target-center-touching edges | `8` |
| row-`6` connector-step edges | `3` |
| occurrence-weighted row-`6` connector-step edges | `4` |

Positive transfer-edge rows:

| Row | Signature-edge count | Occurrence-edge count |
| ---: | ---: | ---: |
| `5` | `6` | `7` |
| `6` | `3` | `4` |
| `7` | `2` | `2` |

Path-shape split:

| Path shape | Signature count | Occurrence count |
| --- | ---: | ---: |
| one-edge row-`5` label-`4` spoke swap | `3` | `3` |
| one-edge row-`7` label-`4` spoke swap | `2` | `2` |
| two-edge row-`5`/row-`6` connector cascade | `3` | `4` |

The row-local reading is:

- every positive transfer starts as a label-`4` spoke swap at row `5` or row
  `7`;
- the two quotient-equality-only exceptions are both one-edge row-`5`
  obligations;
- every row-`6` transfer obligation is the same connector step
  `[5,6]=[0,6]`;
- that row-`6` connector step appears only after the row-`5` step
  `[4,5]=[5,6]`.

## Reading

The next proof-facing target is now more concrete:

```text
Any genuine source-151 row-6 private-halo residual support that uses a
positive label-4 transfer must realize one of seven row-local equality
obligations, and any row-6 transfer must pass through the repeated
row-5/row-6 connector cascade.
```

This does not prove that the residual support geometry is impossible. It turns
the label-`4` transfer into exact centered equal-distance statements that a
future support-geometry lemma can attack directly.

## What This Does Not Prove

This artifact does not prove outside-pair support existence, does not prove row
forcing, does not prove that pair `[3,5]` is impossible, does not prove
endpoint-`8` forcing, does not prove `n=9`, does not prove the bootstrap
bridge, and does not prove Erdos Problem #97.
