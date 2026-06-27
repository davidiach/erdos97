# Bootstrap T12 151:6 Label-4 Center-8 Migration Support Crosswalk

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note joins two previously checked packets:

- `docs/bootstrap-t12-151-6-label4-center8-residual-target-rows.md`;
- `docs/bootstrap-t12-151-6-label4-support-hypothesis-ledger.md`.

The residual target-row packet split the six no-center-`8` assignments into
four off-center `[0,4,6]` cases and two target-sparse cases. This crosswalk
asks the next narrow question:

```text
Do the current centered support hypotheses already back those off-center rows
in a way that supplies center-8 migration?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_migration_support_crosswalk.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_migration_support_crosswalk.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_center8_migration_support_crosswalk.json
```

## Gate Result

The migration-support gate is:

```text
NOT_READY_SUPPORT_BACKING_DOES_NOT_MIGRATE_OFF_CENTER_ROWS
```

Pinned summary:

| Quantity | Value |
| --- | ---: |
| residual assignments | `6` |
| off-center `[0,4,6]` row occurrences | `5` |
| target-sparse assignments | `[0,11]` |
| support requirement centers | `[5,6,7]` |
| center-`8` support requirements | `0` |
| off-center rows with same-center support backing | `3` |
| off-center rows at unsupported center `2` | `2` |
| assignments with same-center support-backed off-center rows | `[5,7,10]` |
| assignments with unsupported off-center rows | `[9]` |
| same-center support matches | `5` |
| endpoint-triple pairs covered by same-center support | `[0,4]`, `[4,6]` |
| endpoint-triple pairs still missing | `[0,6]` |
| off-center rows using row-`5` `[4,6]` cascade support | `1` |
| off-center rows using row-`6` `[0,5]` cascade support | `0` |

The support-backed off-center rows are:

| Assignment | Core | Row center | Row | Same-center support pairs |
| ---: | ---: | ---: | --- | --- |
| `5` | `0` | `5` | `[0,2,4,6]` | `[0,4]`, `[2,4]`, `[4,6]` |
| `7` | `1` | `7` | `[0,1,4,6]` | `[1,4]` |
| `10` | `3` | `7` | `[0,2,4,6]` | `[2,4]` |

Assignment `9` has two off-center target rows, but both are centered at `2`,
where the current support ledger has no centered support requirement.
Assignments `0` and `11` remain target-sparse and require a separate
obstruction or a stronger source.

## Reading

The useful narrowing is:

```text
Same-center support backing is present in part of the residual off-center
catalogue, but it is not center-8 migration.
```

Only assignment `5` aligns an off-center target row with the row-`5` `[4,6]`
cascade support. The row-`6` `[0,5]` cascade support does not appear as an
off-center target row, and no current support requirement is centered at `8`.
A future lemma would therefore need genuine geometry that moves
same-center-supported off-center rows to a center-`8` rich class, or it must
obstruct assignments `0` and `11` by another route.

## What This Does Not Prove

This artifact does not prove center migration, does not prove support
existence, does not prove row forcing, does not prove endpoint-`8` forcing,
does not prove assignments `0` and `11` impossible, does not prove that pair
`[3,5]` is impossible, does not prove `n=9`, does not prove the bootstrap
bridge, and does not prove Erdos Problem #97.
