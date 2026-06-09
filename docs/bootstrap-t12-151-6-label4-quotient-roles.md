# Bootstrap T12 151:6 Label-4 Quotient Roles

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note pushes the source-`151` row-`6` private-lane residual target one step
closer to the actual quotient obstruction. The previous residual ledger shows
that every label-`8`-free exact signature uses auxiliary witness label `4`.
This packet asks whether label `4` reaches the strict quotient cycle itself,
or only sits elsewhere in the selected rows.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_quotient_roles.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_quotient_roles.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_quotient_roles.json
```

## Inputs

This packet is a derivative check over:

- `data/certificates/bootstrap_t12_151_6_label8_free_residual_targets.json`.

It rebuilds the selected-distance quotient classes for each of the `10`
label-`8`-free residual signatures and records how label `4` appears in the
quotient classes used by the extracted strict cycles.

## Quotient Role Result

Pinned summary:

| Quantity | Value |
| --- | ---: |
| distinct label-`8`-free signatures | `10` |
| label-`8`-free occurrences | `12` |
| signatures with a label-`4` cycle quotient class | `10` |
| occurrences with a label-`4` cycle quotient class | `12` |
| direct label-`4` cycle-edge signatures | `8` |
| direct label-`4` cycle-edge occurrences | `10` |
| quotient-equality-only label-`4` signatures | `2` |
| quotient-equality-only label-`4` occurrences | `2` |
| label-`4` cycle-class signature incidences | `19` |
| label-`4` cycle-class occurrence incidences | `23` |

Thus label `4` is not merely present in the residual rows. In every residual
signature, at least one strict-cycle quotient class contains a pair involving
label `4`.

There are two modes:

- `direct_cycle_edge`: label `4` appears directly in a chosen strict-cycle
  edge endpoint. This covers `8` signatures and `10` occurrences.
- `quotient_equality_only`: the chosen cycle edges do not directly mention
  label `4`, but selected-distance equalities place a label-`4` pair in one
  of the cycle quotient classes. This covers `2` signatures and `2`
  occurrences.

## Reading

The next proof-facing target can now be stated at the quotient level:

```text
Any genuine source-151 row-6 private-halo residual support must either
force a direct label-4 strict-cycle edge or force the quotient-equality-only
label-4 transfer.
```

This does not yet prove that the residual support geometry is impossible. It
does identify exactly where label `4` must enter the selected-distance quotient
obstruction, including the two equality-only exceptions.

## What This Does Not Prove

This artifact does not prove outside-pair support existence, does not prove row
forcing, does not prove that pair `[3,5]` is impossible, does not prove
endpoint-`8` forcing, does not prove `n=9`, does not prove the bootstrap
bridge, and does not prove Erdos Problem #97.
