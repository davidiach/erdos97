# Bootstrap T12 151:6 Label-4 Center-8 Target-Sparse Two-Row Repairs

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines the target-sparse completion preflight. The previous packet
recorded:

```text
All 12 one-row completions of target-pair rows to [0,4,6] fail basic filters.
```

This packet asks the next narrow repair question:

```text
After one target-pair row is completed to [0,4,6], can one additional row
replacement repair the selected-row assignment through the basic filters?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_target_sparse_two_row_repairs.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_target_sparse_two_row_repairs.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_center8_target_sparse_two_row_repairs.json
```

## Inputs

This packet joins:

- `data/certificates/bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.json`;
- `data/certificates/bootstrap_t12_151_6_label4_center8_target_sparse_completions.json`.

## Gate Result

The repair-extension gate is:

```text
NOT_READY_TARGET_SPARSE_TWO_ROW_REPAIRS_FAIL_BASIC_FILTERS
```

Pinned summary:

| Quantity | Value |
| --- | ---: |
| target-sparse assignments | `[0,11]` |
| source one-row completions | `12` |
| repair centers per completion | `8` |
| replacement rows per repair center | `69` |
| one-completion plus one-repair candidates | `6624` |
| basic-filter surviving candidates | `0` |
| vertex-circle checked candidates | `0` |

Every repair candidate still has a crossing violation. Most also retain a
witness-pair-cap violation, and some add a selected-indegree-cap violation:

| Failure reason | Attempts |
| --- | ---: |
| crossing | `6624` |
| witness-pair cap | `6582` |
| selected-indegree cap | `1260` |

The candidate distribution is:

| Quantity | Value |
| --- | --- |
| assignment repair candidates | `{0: 1104, 11: 5520}` |
| completion rows | `[0,1,4,6]` x2208, `[0,2,4,6]` x552, `[0,3,4,6]` x552, `[0,4,5,6]` x552, `[0,4,6,7]` x552, `[0,4,6,8]` x2208 |
| missing target labels | `{0: 1104, 4: 3312, 6: 2208}` |

## Reading

The useful conclusion is:

```text
The target-sparse cases do not have a one-completion plus one-repair escape
inside the selected-row basic filters.
```

This is stronger than the one-row completion preflight, but it is still not a
geometric obstruction. It says that after completing one target-pair row to the
cascade triple `[0,4,6]`, changing one more non-completion row arbitrarily
cannot repair the resulting selected-row assignment.

The remaining target-sparse work must use genuine support geometry, a stronger
multi-row mechanism, or a center-migration route. This packet deliberately
does not claim assignments `0` and `11` are impossible.

## What This Does Not Prove

This artifact does not prove assignments `0` and `11` are impossible, does not
prove center migration, does not prove support existence, does not prove row
forcing, does not prove endpoint-`8` forcing, does not prove that pair `[3,5]`
is impossible, does not prove `n=9`, does not prove the bootstrap bridge, and
does not prove Erdos Problem #97.
