# Bootstrap T12 151:6 Label-4 Center-8 Migration Preflight

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines the residual split after the source-`151` row-`6`
center-`8` route packet. The previous residual packet recorded:

```text
Four residual assignments contain [0,4,6] only as off-center rows, while
assignments 0 and 11 are target-sparse.
```

This packet asks the next narrow question:

```text
Do the off-center [0,4,6] rows already migrate to the center-8 endpoint target
under current checked support evidence?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_migration_preflight.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_migration_preflight.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_center8_migration_preflight.json
```

## Inputs

This packet joins:

- `data/certificates/bootstrap_t12_151_6_label4_center8_residual_target_rows.json`;
- `data/certificates/bootstrap_t12_151_6_label4_center8_rich_triple_preflight.json`;
- `data/certificates/bootstrap_t12_151_6_label4_center8_source_crosswalk.json`;
- `data/certificates/bootstrap_t12_151_6_label4_cascade_endpoint8_targets.json`.

## Gate Result

The migration gate is:

```text
NOT_READY_CENTER_MIGRATION_NOT_PROVED
```

Pinned summary:

| Quantity | Value |
| --- | ---: |
| residual assignments | `6` |
| off-center residual assignments | `4` |
| off-center residual assignment indices | `[5,7,9,10]` |
| target-sparse assignment indices | `[0,11]` |
| migration candidate row occurrences | `5` |
| migration candidate source centers | `[2,5,7]` |
| distinct center-`8` exact rows if migrated | `3` |
| support requirements at center `8` | `0` |
| source-`151` row-`8` candidates with a target pair | `0` |

The migration candidates are:

| Assignment | Core | Source Center | Candidate Center-`8` Row |
| ---: | ---: | ---: | --- |
| `5` | `0` | `5` | `[0,2,4,6]` |
| `7` | `1` | `7` | `[0,1,4,6]` |
| `9` | `1` | `2` | `[0,3,4,6]` |
| `9` | `2` | `2` | `[0,3,4,6]` |
| `10` | `3` | `7` | `[0,2,4,6]` |

Each candidate center-`8` exact row is inside the conditional endpoint-target
family checked by the cascade endpoint packet. The blocker is not local
quotient obstruction after migration; the blocker is that no current checked
evidence proves the migration or supplies an independent center-`8` rich class.

## Reading

The useful conclusion is:

```text
The off-center residual cases are plausible center-migration targets, but the
current packet stack does not prove center migration.
```

The existing support preflight has no center-`8` support requirement and no
support requirement containing the full triple `[0,4,6]`. The existing
source-`151` row-`8` singleton packet is also not a source for this target:
its candidates use core `[1,2]` with supports `[5,7]`, and none contains even
a pair from `[0,4,6]`.

## What This Does Not Prove

This artifact does not prove center migration, does not prove support
existence, does not prove row forcing, does not prove endpoint-`8` forcing,
does not prove that assignments `0` and `11` are impossible, does not prove
that pair `[3,5]` is impossible, does not prove `n=9`, does not prove the
bootstrap bridge, and does not prove Erdos Problem #97.
