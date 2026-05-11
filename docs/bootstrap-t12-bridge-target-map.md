# Bootstrap T12 Bridge Target Map

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note joins the current bootstrap/T12 row-pressure packets into one
role-aware target map. The map is meant to answer:

```text
For each missing T12/F16 row, which exact bridge lemma would have to be proved
before the stored vertex-circle strict-cycle certificate can be used?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_bridge_target_map.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_bridge_target_map.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_bridge_target_map.json`.

## Scope

The input packets are fixed selected-row proof-mining diagnostics:

- `data/certificates/bootstrap_t12_row_pressure.json`;
- `data/certificates/bootstrap_t12_closure_exposed.json`;
- `data/certificates/bootstrap_t12_one_outside.json`;
- `data/certificates/bootstrap_t12_outside_pair.json`;
- `data/certificates/bootstrap_t12_activation_requirements.json`.

The target map does not contain full rich-class data. A bridge-lemma target is
an open proof obligation, not a theorem, not a Euclidean realization
certificate, and not evidence for a counterexample.

## Results

The two tight bootstrap/T12 sources have six missing row targets and seven
role-sensitive relation requirements.

| Source | Row | Pressure packet | Relation state | Bridge target |
|---:|---:|---|---|---|
| `81` | `3` | closure-exposed | bootstrap-core sufficient | full-row deletion closure to equality-connector row |
| `81` | `8` | one-outside-label | bootstrap-core sufficient | private center plus singleton support row activation |
| `151` | `5` | one-outside-label | open connector pair | singleton activation plus both outside connector endpoints |
| `151` | `6` | outside-pair | support sufficient | outside-pair connector with partial private-pair ledger contact |
| `151` | `7` | closure-exposed | hard strict endpoint | add missing endpoint `6` to a closure-exposed strict edge |
| `151` | `8` | one-outside-label | connector support plus hard strict endpoint | split connector support from strict-edge endpoint forcing |

Headline counts, using the target map's exclusive relation-state
classification:

```text
row targets: 6
relation requirements: 7
equality connector requirements: 5
strict-edge endpoint requirements: 2
bootstrap-core sufficient relation requirements: 2
support-sufficient relation requirements: 2
open connector requirements: 1
hard strict endpoint requirements: 2
```

## Negative-Control Reading

The map preserves two separate negative controls.

First, source `151`, row `7` is deletion-closure-exposed through row center
`7` and witnesses `[0,1,4]`, but the stored strict edge needs endpoint set
`[0,1,6]`. Closure exposure alone therefore does not supply the strict edge.

Second, source `151`, row `5` has singleton row-pressure support, but its
stored equality connector needs the outside pair `[7,8]`. A one-label row
activation argument would still need to explain why the connector relation
receives both endpoints.

The hard strict-endpoint follow-up in
`docs/bootstrap-t12-hard-strict-endpoints.md` isolates the first negative
control and the mixed row `151:8`, where singleton supports split the strict
endpoint set.

The open connector-pair follow-up in
`docs/bootstrap-t12-open-connector-pair.md` isolates the second negative
control, row `151:5`, where singleton supports and one deletion closure see
only one endpoint of connector pair `[7,8]`.

The relation-sufficient row follow-up in
`docs/bootstrap-t12-relation-sufficient-rows.md` isolates the complementary
positive-control bucket: rows `81:3`, `81:8`, and `151:6`, where connector
relation evidence is already bootstrap-core sufficient or support-sufficient,
but row/rich-class forcing remains an open bridge target.

## What This Does Not Prove

This artifact does not prove that any missing T12 row is forced, does not prove
`n=9`, does not prove the bootstrap bridge, does not independently review the
vertex-circle checker, and does not alter the official/global status of Erdos
Problem #97.

## Reviewer Focus

Check the three layers separately:

- row pressure: closure-exposed, one-outside-label, or outside-pair support;
- relation requirement: the connector pair or strict-edge endpoint set used by
  the stored T12/F16 quotient certificate;
- bridge target: the still-unproved geometric row-forcing statement needed to
  turn fixed-row bookkeeping into a genuine minimal-counterexample reduction.
