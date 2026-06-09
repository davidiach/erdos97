# Bootstrap T12 151:6 Label-4 Support Hypothesis Ledger

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines the source-`151` row-`6` private-lane label-`4` transfer
components into the genuine centered support hypotheses that a future
support-geometry exclusion would need to use. It is a proof-target ledger, not
a proof that those supports exist and not an obstruction by itself.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_support_hypothesis_ledger.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_support_hypothesis_ledger.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_support_hypothesis_ledger.json
```

## Inputs

This packet is a derivative check over:

- `data/certificates/bootstrap_t12_151_6_label4_transfer_obligations.json`;
- `data/certificates/bootstrap_t12_151_6_label4_transfer_length_components.json`;
- `data/certificates/bootstrap_t12_151_6_label4_transfer_component_feasibility.json`.

Each centered equality obligation is read as a support hypothesis of the form
"center `c` has a selected-distance class containing witnesses `a` and `b`".

## Support-Hypothesis Result

Pinned summary:

| Quantity | Value |
| --- | ---: |
| label-`4` support-need components | `6` |
| unique centered support requirements | `7` |
| components requiring one support center | `5` |
| components requiring two support centers | `1` |
| components requiring the row-`6` target connector | `1` |
| components whose requirements hit exact private pair `[3,5]` | `0` |
| unique requirements equal to exact private pair `[3,5]` | `0` |
| components requiring label-`4` as a support witness | `6` |
| components requiring label-`8` as a support witness | `0` |

The unique support requirements split by row center as:

| Center | Unique requirements | Signature incidences | Occurrence incidences |
| ---: | ---: | ---: | ---: |
| `5` | `4` | `6` | `7` |
| `6` | `1` | `3` | `4` |
| `7` | `2` | `2` | `2` |

The role split is:

| Role | Unique requirements | Signature incidences | Occurrence incidences |
| --- | ---: | ---: | ---: |
| `row5_label4_spoke_swap` | `3` | `3` | `3` |
| `row5_label4_to_target_center_step` | `1` | `3` | `4` |
| `row6_target_connector_step` | `1` | `3` | `4` |
| `row7_label4_spoke_swap` | `2` | `2` | `2` |

The row-`6` connector cascade

```text
D[0,6] = D[4,5] = D[5,6]
```

is the only two-center support target. It requires:

| Center | Witness pair | Role |
| ---: | --- | --- |
| `5` | `[4,6]` | `row5_label4_to_target_center_step` |
| `6` | `[0,5]` | `row6_target_connector_step` |

All cascade incidences have auxiliary center pair `5,8`, with `3` signature
incidences and `4` occurrence incidences. The equal-length component itself
remains component-alone feasible by the previous cyclic-arc negative control;
the point here is that a successful exclusion must use the extra support
hypotheses above, plus the still-separate private pair `[3,5]` or rich-class
input.

## Reading

The useful narrowing is:

```text
The label-4 transfer machinery never directly asks for the exact private pair
[3,5]. The row-6 route asks only for center 6 with witnesses [0,5], after a
row-5 support using witnesses [4,6].
```

Therefore the next bridge lemma should not attack the bare component
`D[0,6]=D[4,5]=D[5,6]` in isolation. It should attack the cascade under
genuine support geometry: row `5` with `[4,6]`, row `6` with `[0,5]` inside
the private target class `[0,3,5,7]`, and the additional private-pair or
rich-class hypothesis that brings `[3,5]` into the argument.

## What This Does Not Prove

This artifact does not discharge the support hypotheses it names, does not
prove outside-pair support existence, does not prove row forcing, does not
prove that pair `[3,5]` is impossible, does not prove endpoint-`8` forcing,
does not prove `n=9`, does not prove the bootstrap bridge, and does not prove
Erdos Problem #97.
