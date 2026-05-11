# Bootstrap T12 Relation-Sufficient Rows

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note isolates the T12 bridge-target rows whose stored connector relation
requirements are already supplied by bootstrap-core or support diagnostics,
while the row/rich-class forcing step remains open. It answers a narrower
question than row forcing:

```text
Which T12 row targets have relation evidence already available, but still need
a geometric argument that the whole selected row is forced?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_relation_sufficient_rows.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_relation_sufficient_rows.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_relation_sufficient_rows.json`.

## Scope

The input packet is:

- `data/certificates/bootstrap_t12_bridge_target_map.json`.

This packet is not full rich-class data. A relation-sufficient row is a fixed
selected-row bridge target whose connector requirement is already visible in
the bootstrap core or in stored support options. That is not a theorem that
the row itself is geometrically forced.

## Results

There are three relation-sufficient row targets:

| Source | Row | Requirement | Relation state | Row-forcing gap |
|---:|---:|---|---|---|
| `81` | `3` | `81:3:connector:2:0` | bootstrap-core sufficient | full-row closure exposure still needs rich-class forcing |
| `81` | `8` | `81:8:connector:0:0` | bootstrap-core sufficient | core connector visible, but private singleton row activation remains |
| `151` | `6` | `151:6:connector:2:0` | support sufficient | outside-pair support still needs connector row forcing |

Headline counts:

```text
relation-sufficient rows: 3
bootstrap-core sufficient requirements: 2
support-sufficient requirements: 1
closure-exposed support packets: 1
one-outside-label support packets: 1
outside-pair support packets: 1
excluded hard/open rows: 151:5, 151:7, 151:8
```

## Reading

Row `81:3` is the cleanest closure-exposed positive control: the deletion
closure contains the row center and all four selected row witnesses, and the
stored connector pair `[0,1]` is already in the bootstrap core. A future bridge
lemma would still need to turn this fixed-row closure exposure into an actual
equality-connector rich class.

Row `81:8` has connector pair `[0,2]` already in the bootstrap core, and its
outside labels `[5,6]` have singleton support options. The missing step is not
the relation itself; it is the geometric argument that a private row center
plus singleton support activates the whole row.

Row `151:6` has connector pair `[0,8]`, with support-sufficient outside-pair
options and two private-pair ledger hits, `[3,8]` and `[5,8]`. The packet keeps
that as partial support only; it does not promote the ledger contact to row
forcing.

## What This Does Not Prove

This artifact does not prove that any relation-sufficient row, connector
endpoint, row center, or rich class is forced. It does not prove `n=9`, does
not prove the bootstrap bridge, does not independently review the
vertex-circle checker, and does not alter the official/global status of Erdos
Problem #97.

## Reviewer Focus

The exact next bridge question is whether relation-sufficient connector
evidence can be upgraded to genuine row/rich-class forcing for rows `81:3`,
`81:8`, and `151:6`. This is intentionally separate from the hard strict
endpoint packet and the open connector-pair packet.
