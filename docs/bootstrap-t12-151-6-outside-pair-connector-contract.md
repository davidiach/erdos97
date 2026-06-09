# Bootstrap T12 151:6 Outside-Pair Connector Contract

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note records the weaker connector target left after the source-`151`
row-`6` outside-pair packets. The full fixed row is not needed for the stored
`T12/F16` equality connector. It is enough for a genuine rich distance class at
center `6` to contain the bootstrap-core witness `0` and the connector endpoint
`8`.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_outside_pair_connector_contract.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_outside_pair_connector_contract.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_151_6_outside_pair_connector_contract.json`.

## Scope

The input packets are:

- `data/certificates/bootstrap_t12_outside_pair.json`;
- `data/certificates/bootstrap_t12_relation_sufficient_rows.json`.

This packet proves only a local conditional:

```text
If a genuine rich distance class at center 6 contains witnesses 0 and 8,
then [0,6]=[8,6].
```

The proof is just the definition of a rich distance class at center `6`. If
both witnesses are in the same class, then `|p_6-p_0|=|p_6-p_8|`, which is the
connector equality used by the `T12/F16` local strict-cycle packet.

The packet does not prove that such a rich class exists, does not prove either
endpoint-`8` support exists, does not prove the full fixed row `6 -> [0,3,5,8]`,
and does not prove that the `T12/F16` local packet is geometrically available.

## Outside-Pair Partition

The outside-pair packet records three support pairs for row `151:6`:

```text
[3,5], [3,8], [5,8]
```

Together with the bootstrap-core witness `0`, these support pairs split as:

```text
connector-forcing supports: [3,8], [5,8]
connector-avoiding support: [3,5]
```

The endpoint-`8` supports also hit the private-pair ledger:

```text
ledger-hit supports: [3,8], [5,8]
private-halo-only support: [3,5]
```

## Escape Mechanism

The precise remaining escape is:

```text
CONNECTOR_ESCAPE_REQUIRES_PRIVATE_HALO_ONLY_PAIR_3_5
```

To avoid the equality connector at center `6`, a genuine outside-pair support
for row `151:6` must avoid endpoint `8`. In the current outside-pair ledger,
that leaves the single private-halo-only pair `[3,5]`.

## Next Target

The next proof-facing question is now narrower:

```text
Can genuine outside-pair/rich-class geometry force one of [3,8] or [5,8],
or can the private-halo-only pair [3,5] realize the connector-avoiding escape?
```

The companion partition
`docs/bootstrap-t12-151-6-outside-pair-escape-partition.md` locates this escape
inside the full-neighborhood packet: private-halo-only rows leave `12`
basic-filter survivors, while endpoint-`8` connector-available rows leave
`16`; exact vertex-circle replay kills all `28`.

Either outcome would reduce the bridge gap. Forcing an endpoint-`8` support
gives the needed connector without proving the full fixed row. Explaining the
`[3,5]` escape would isolate the exact geometric route that keeps the connector
out.

## What This Does Not Prove

This artifact does not prove support existence, row forcing, `n=9`, the
bootstrap bridge, or Erdos Problem #97. It only records the exact local
conditional and the smaller outside-pair escape target left open after the
`151:6` full-neighborhood vertex-circle packet.
