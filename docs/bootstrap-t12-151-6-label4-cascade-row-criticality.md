# Bootstrap T12 151:6 Label-4 Cascade Row-Criticality

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines the source-`151` row-`6` label-`4` cascade after the
support-hypothesis ledger. The point is small but important: the cascade
signatures are not closed by a one-row or two-row quotient obstruction. The
stored vertex-circle strict cycle appears only when all three local rows
`5`, `6`, and `8` are present.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_cascade_row_criticality.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_cascade_row_criticality.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_cascade_row_criticality.json
```

## Inputs

This packet joins:

- `data/certificates/bootstrap_t12_151_6_label8_free_residual_targets.json`;
- `data/certificates/bootstrap_t12_151_6_label4_support_hypothesis_ledger.json`.

The support ledger identifies the row-`6` cascade

```text
D[0,6] = D[4,5] = D[5,6]
```

as requiring center `5` with witness pair `[4,6]` and center `6` with witness
pair `[0,5]`. The residual-target packet identifies the exact label-`8`-free
signatures where that cascade occurs.

## Row-Criticality Result

Pinned summary:

| Quantity | Value |
| --- | ---: |
| cascade signature indices | `7, 8, 9` |
| cascade signature count | `3` |
| cascade occurrence count | `4` |
| required local rows | `{5,6,8}` |
| full-core status counts | `3` strict cycles |
| proper nonempty row truncations | `18` |
| proper truncation status counts | `18` quotient-clean |
| full-core cycle lengths | one length-`2`, two length-`3` |

Every cascade signature has auxiliary center pair `5,8`. In each case:

- the full local package `{5,6,8}` is a vertex-circle strict cycle;
- deleting row `5`, row `6`, or row `8` leaves a quotient-clean two-row
  truncation;
- every singleton row is also quotient-clean.

The cycle-edge rows are always `5` and `8`. Row `6` contributes the private
target equality class `[0,3,5,7]`; rows `5` and `6` supply the cascade
equalities named by the support ledger; row `8` supplies the extra strict
endpoint row needed by the residual cycle.

## Reading

The useful narrowing is:

```text
The cascade route is three-row critical. A future bridge lemma must force the
full local package {5,6,8}, not merely the row-5/row-6 cascade support
equalities.
```

This prevents an overstrong proof attempt: the support package named by the
previous ledger is not enough by itself to close the selected-distance quotient
graph. The next geometric target must either force the row-`8` strict endpoint
row from genuine support/minimality data, or prove a different support-rich
obstruction that bypasses this three-row local core.

## What This Does Not Prove

This artifact does not prove support existence, does not prove row forcing,
does not prove that pair `[3,5]` is impossible, does not prove endpoint-`8`
forcing, does not prove `n=9`, does not prove the bootstrap bridge, and does
not prove Erdos Problem #97.
