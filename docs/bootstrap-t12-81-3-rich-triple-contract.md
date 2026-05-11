# Bootstrap T12 81:3 Rich-Triple Contract

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note records the next, weaker target after the focused `81:3` closure
packet. The full fixed row is not needed for the stored `T12/F16` equality
connector. It is enough for a genuine rich distance class at center `3` to
contain witnesses `0` and `1`.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_3_rich_triple_contract.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_3_rich_triple_contract.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_3_rich_triple_contract.json`.

## Scope

The input packet is
`data/certificates/bootstrap_t12_81_3_closure_target.json`.

This packet proves only a local conditional:

```text
If a genuine rich distance class at center 3 contains witnesses 0 and 1,
then [1,3]=[0,3].
```

The proof is just the definition of a rich distance class at center `3`. If
both witnesses are in the same class, then `|p_3-p_1|=|p_3-p_0|`, which is the
connector equality used by the `T12/F16` local strict-cycle packet.

The packet does not prove that such a rich class exists, does not prove the
full fixed row `3 -> [0,1,4,6]`, and does not prove that the `T12/F16` local
packet is geometrically available.

## Triple Partition

For the fixed row witnesses

```text
[0,1,4,6]
```

the three-witness activation triples split as follows:

```text
connector-forcing triples: [0,1,4], [0,1,6]
connector-avoiding triples: [0,4,6], [1,4,6]
```

The deletion seed from the closure-target packet is:

```text
[0,1,4]
```

So activation from that seed would force the connector pair `[0,1]`. The only
activation triples from the fixed witness set that avoid the connector pair
both require label `6`.

## Escape Mechanism

The precise remaining escape is:

```text
CONNECTOR_ESCAPE_REQUIRES_RICH_CLASSES_AVOID_PAIR_0_1
```

To avoid the equality connector at center `3`, every genuine rich class
centered at `3` must avoid containing witnesses `0` and `1` together. If center
`3` still activates through the fixed-row witness set, it must activate through
`[0,4,6]` or `[1,4,6]`, so label `6` must become available before center `3`
activates.

## Next Target

The next proof-facing question is now order-resolved rather than full-row
resolved:

```text
Can real rich-class closure force activation at center 3 from [0,1,4],
or must any connector-avoiding activation first expose label 6?
```

Either outcome would reduce the bridge gap. A positive result gives the
needed connector without proving the full fixed row. A negative result should
be packaged as an exact escape packet explaining how label `6` becomes
available first without already forcing the connector.

## What This Does Not Prove

This artifact does not prove row forcing, rich-class existence, `n=9`, the
bootstrap bridge, or Erdos Problem #97. It only records the exact local
conditional and the smaller escape target left open after the `81:3`
closure-target packet.
