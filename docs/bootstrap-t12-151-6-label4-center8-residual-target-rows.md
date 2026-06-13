# Bootstrap T12 151:6 Label-4 Center-8 Residual Target Rows

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines the six private-lane assignments left open by the center-`8`
core-route packet. The previous route map recorded:

```text
Six private-lane assignments have no center-8 local core containing [0,4,6].
```

This packet asks the next narrow question:

```text
Do those residual assignments at least contain [0,4,6] as a non-center-8 row
inside their strict cores?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_residual_target_rows.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_residual_target_rows.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_center8_residual_target_rows.json
```

## Inputs

This packet joins:

- `data/certificates/bootstrap_t12_151_6_private_lane_strict_core_split.json`;
- `data/certificates/bootstrap_t12_151_6_label4_center8_core_route.json`.

## Gate Result

The residual gate is:

```text
NOT_READY_RESIDUAL_TARGET_ROWS_DO_NOT_FORCE_CENTER8
```

Pinned summary:

| Quantity | Value |
| --- | ---: |
| residual assignments | `6` |
| residual assignment indices | `[0,5,7,9,10,11]` |
| residual strict cores | `19` |
| residual label-`8`-visible cores | `15` |
| residual label-`8`-free cores | `4` |
| residual center-`8` cores | `1` |
| residual center-`8` target cores | `0` |
| assignments with an off-center `[0,4,6]` row | `4` |
| target-sparse assignments | `[0,11]` |
| off-center `[0,4,6]` row occurrences | `5` |

The off-center target rows are:

| Assignment | Core | Row center | Row |
| ---: | ---: | ---: | --- |
| `5` | `0` | `5` | `[0,2,4,6]` |
| `7` | `1` | `7` | `[0,1,4,6]` |
| `9` | `1` | `2` | `[0,3,4,6]` |
| `9` | `2` | `2` | `[0,3,4,6]` |
| `10` | `3` | `7` | `[0,2,4,6]` |

The two target-sparse assignments, `0` and `11`, still have target-pair rows
but no strict-core row containing the full triple `[0,4,6]`.

## Reading

The useful conclusion is:

```text
The residual cases split into center-migration targets and target-sparse
targets.
```

Assignments `5`, `7`, `9`, and `10` already contain `[0,4,6]`, but only at
row centers `2`, `5`, or `7`. Those rows do not supply the center-`8` endpoint
target without a genuine center-migration lemma. Assignments `0` and `11`
require a separate obstruction or stronger source because no checked residual
strict-core row contains the full target triple.

## What This Does Not Prove

This artifact does not prove center migration, does not prove support
existence, does not prove row forcing, does not prove endpoint-`8` forcing,
does not prove that pair `[3,5]` is impossible, does not prove `n=9`, does not
prove the bootstrap bridge, and does not prove Erdos Problem #97.
