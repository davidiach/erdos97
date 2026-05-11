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
