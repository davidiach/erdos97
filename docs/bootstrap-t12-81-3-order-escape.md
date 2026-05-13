# Bootstrap T12 81:3 Order Escape

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note records the order-resolved follow-up to the `81:3` rich-triple
connector contract. The previous packet reduced the target to the pair
`[0,1]`: any genuine rich class at center `3` containing witnesses `0` and
`1` gives the T12/F16 connector `[1,3]=[0,3]`. A connector-avoiding activation
through the fixed witness set `[0,1,4,6]` must therefore use `[0,4,6]` or
`[1,4,6]`, so label `6` must be available before center `3` activates.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_3_order_escape.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_3_order_escape.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_3_order_escape.json`.

## Scope

This packet audits only the fixed singleton-rich model from source `81`, where
each selected row is treated as the only rich class at its center. It does not
prove that the row `81:3` is a genuine rich class, does not prove genuine
rich-class closure order, and does not rule out additional rich classes.

## Fixed-Row Order Audit

From seed

```text
[0,1,4]
```

the fixed singleton-rich closure order is:

```text
[0,1,4,3,6]
```

The only initial activation is center `3`, using trigger:

```text
[0,1,4]
```

That trigger contains the connector pair `[0,1]`. Label `6` is not available
before this step.

The next fixed singleton-rich step adds label `6`, but only after center `3`
has entered:

```text
center 6 trigger: [0,3,4]
```

So the fixed selected-row bookkeeping does not realize the connector-avoiding
escape. In that model, label `6` is supplied only by a trigger that already
uses center `3`.

## Same-Center Disjointness Guard

There is one extra fixed-row-preservation guard. The source `81` fixed row at
center `6` is:

```text
center 6: [0,3,4,7]
```

Distinct rich distance classes at a single center are disjoint, because each
target vertex has a unique distance from that center. Therefore, if this
center-`6` row is preserved as a genuine rich class, any additional center-`6`
class must avoid `0`, `3`, `4`, and `7`.

But a pre-`3` supply of label `6` from the deletion seed `[0,1,4]` would need
an additional center-`6` rich class containing all three seed labels. This is
impossible while preserving the fixed center-`6` row, since the seed labels
`0` and `4` already lie in `[0,3,4,7]`.

So the checked guard status is:

```text
NO_PRE_3_LABEL_6_SUPPLY_PRESERVING_CENTER_6_FIXED_CLASS
```

This guard is conditional on preserving the fixed source-`81` center-`6` row.
It does not prove that center `3` activates, does not prove that row `81:3` is
genuine, and does not rule out bridge hypotheses that do not preserve the
center-`6` fixed row as a genuine distance class.

## Remaining Escape

The remaining exact escape status is:

```text
GENUINE_RICH_CLASS_PRE_3_LABEL_6_SUPPLY_OPEN
```

A genuine escape now needs one of the following:

```text
a genuine rich class at some non-3 center that adds label 6 before center 3
```

or

```text
an exact proof that no such pre-3 label-6 supply exists under the
minimal/rich-class hypotheses
```

with guardrails showing that any proposed supply does not already force the
T12 connector by another route.

## What This Does Not Prove

This artifact does not prove row forcing, rich-class existence, `n=9`, the
bootstrap bridge, or Erdos Problem #97. It only records that the fixed
singleton-row closure order fails to supply label `6` before center `3`, so
the next target must use genuine rich-class data rather than the current fixed
selected-row packet alone.
