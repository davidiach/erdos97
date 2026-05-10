# Bootstrap T12 Activation-Support Requirements

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines the bootstrap/T12 row-pressure packets by asking a smaller
question than "is the full missing row forced?":

```text
Which witness subset is actually needed for the stored T12/F16 quotient
connector or strict edge?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_activation_requirements.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_activation_requirements.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_activation_requirements.json`.

## Scope

The input is fixed selected-row proof-mining data from:

- `data/certificates/bootstrap_vertex_circle_overlay.json`;
- `data/certificates/bootstrap_t12_row_pressure.json`.

The artifact is not full rich-class data and does not prove that any missing
row is geometrically forced. It classifies only the relation requirements
inside the stored T12/F16 local strict-cycle certificate.

For an equality connector row with center `c`, the relation requirement is the
pair of non-center endpoints needed to force one quotient equality. For a
strict-edge row, the relation requirement is the union of the outer and inner
chord endpoints needed for the vertex-circle comparison.

## Results

The two tight bootstrap/T12 sources have six missing row centers and seven
role-sensitive relation requirements.

| Source | Row | Roles | Requirement status |
|---:|---:|---|---|
| `81` | `3` | equality connector | connector pair already in the bootstrap-core witnesses; also closure-sufficient |
| `81` | `8` | equality connector | connector pair already in the bootstrap-core witnesses; singleton supports still matter for row activation |
| `151` | `5` | equality connector | needs outside pair `{7,8}`; either singleton alone is only partial |
| `151` | `6` | equality connector | needs endpoint `8`; support pairs `{3,8}` and `{5,8}` suffice, `{3,5}` does not |
| `151` | `7` | strict edge | closure-exposed but still missing private endpoint `6` for the strict edge |
| `151` | `8` | strict edge and equality connector | support `{5}` suffices for the connector, but no singleton support suffices for the strict edge |

Headline counts:

```text
row records: 6
relation requirements: 7
equality connector requirements: 5
strict-edge endpoint requirements: 2
bootstrap-core-sufficient requirements: 2
support-sufficient requirements: 3
closure-sufficient requirements: 1
hard strict requirements: 2
```

The joined follow-up map in `docs/bootstrap-t12-bridge-target-map.md` uses
these relation states to name the row-by-row bridge-lemma targets.

## Negative-Control Reading

The main guardrail is source `151`, row `7`. The deletion closure exposes row
center `7` and witnesses `[0,1,4]`, but the stored T12 strict edge needs
endpoint set `[0,1,6]`. Thus "center plus three visible target witnesses" is
not enough to force the strict edge used by the T12 certificate.

This is a reporting negative control, not a polygon and not a counterexample.

## What This Does Not Prove

This artifact does not prove that any missing T12 row is forced, does not prove
`n=9`, does not prove the bootstrap bridge, does not independently review the
vertex-circle checker, and does not alter the official/global status of Erdos
Problem #97.

## Reviewer Focus

Check that the artifact keeps three notions separate:

- relation requirement: the pair or endpoint set used by the stored T12
  quotient certificate;
- activation support: a stored bootstrap/row-pressure support option that
  supplies enough witnesses for that relation requirement;
- row forcing: the unproved geometric bridge step that would make the row or
  rich class exist in a genuine minimal counterexample.
