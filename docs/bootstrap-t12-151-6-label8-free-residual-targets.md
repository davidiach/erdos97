# Bootstrap T12 151:6 Label-8-Free Residual Targets

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note sharpens the hard side of the source-`151` row-`6` private-lane
strict-core split. The previous split records `12` label-`8`-free row-`6`
three-row strict-cycle core occurrences, with `10` distinct exact signatures.
This packet asks what all of those residual signatures have in common.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label8_free_residual_targets.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label8_free_residual_targets.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label8_free_residual_targets.json
```

## Inputs

This packet is a derivative check over:

- `data/certificates/bootstrap_t12_151_6_private_lane_strict_core_split.json`.

It replays the exact label-`8`-free residual signatures and records their
auxiliary-center pairs, target-row intersections, strict-cycle rows, and
label-`4` incidence.

## Residual Target Result

Pinned summary:

| Quantity | Value |
| --- | ---: |
| distinct label-`8`-free signatures | `10` |
| label-`8`-free occurrences | `12` |
| auxiliary-row signature incidences | `20` |
| auxiliary-row occurrence incidences | `24` |
| label-`4` auxiliary-row signature incidences | `18` |
| label-`4` auxiliary-row occurrence incidences | `22` |
| signatures with any auxiliary label `4` | `10` |
| signatures with label `4` in both auxiliary rows | `8` |
| occurrences with label `4` in both auxiliary rows | `10` |
| signatures with label-`4`-free strict-cycle edges | `2` |
| signatures with center `8` as an auxiliary center | `3` |
| occurrences with center `8` as an auxiliary center | `4` |

Thus the residual label-`8`-free lane is not label-free: every exact residual
signature introduces label `4` through an auxiliary row. Most residual
occurrences use label `4` in both auxiliary rows.

The two exceptional signatures are important. Their auxiliary rows still
include label `4`, but the extracted strict-cycle edges do not directly mention
label `4`. A future label-`4` bridge therefore cannot rely only on visible
cycle-edge endpoints; for those cases it must use the selected-distance
equalities carried by the auxiliary rows.

## Reading

The next proof-facing target is now smaller:

- prove that a genuine minimal/rich-class support system cannot realize any
  of these label-`4`-mandatory residual signatures; or
- prove that the same label-`4` auxiliary support geometry forces an
  endpoint-`8` support or a label-`8`-visible row-`6` core.

This packet does not decide which route is correct. It only makes the residual
obligation explicit and machine-checked.

## What This Does Not Prove

This artifact does not prove outside-pair support existence, does not prove row
forcing, does not prove that pair `[3,5]` is impossible, does not prove
endpoint-`8` forcing, does not prove `n=9`, does not prove the bootstrap
bridge, and does not prove Erdos Problem #97.
