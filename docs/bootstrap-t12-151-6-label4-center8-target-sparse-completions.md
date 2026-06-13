# Bootstrap T12 151:6 Label-4 Center-8 Target-Sparse Completions

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines the two target-sparse residual assignments left by the
center-`8` residual target-row packet. The previous split recorded:

```text
Assignments 0 and 11 contain no full [0,4,6] row in any residual strict core.
```

This packet asks the next narrow question:

```text
Can either target-sparse assignment be repaired by replacing one non-target
witness in a target-pair row, thereby completing that row to contain [0,4,6]?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_target_sparse_completions.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_target_sparse_completions.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_center8_target_sparse_completions.json
```

## Inputs

This packet joins:

- `data/certificates/bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.json`;
- `data/certificates/bootstrap_t12_151_6_label4_center8_residual_target_rows.json`.

## Gate Result

The target-sparse completion gate is:

```text
NOT_READY_TARGET_SPARSE_ONE_ROW_COMPLETIONS_FAIL_BASIC_FILTERS
```

Pinned summary:

| Quantity | Value |
| --- | ---: |
| target-sparse assignments | `[0,11]` |
| target-pair rows inspected | `6` |
| one-row completion attempts | `12` |
| valid four-set completions generated | `12` |
| basic-filter surviving completions | `0` |
| vertex-circle checked completions | `0` |
| endpoint-exact allowed completions | `8` |
| endpoint-exact disallowed completions | `4` |

All twelve one-row completions fail basic filters before vertex-circle replay.
Each attempt has both a witness-pair-cap violation and a crossing violation.

Distribution details:

| Quantity | Value |
| --- | --- |
| completion assignment counts | `{0: 2, 11: 10}` |
| completion row centers | `{2: 4, 3: 2, 7: 6}` |
| missing target labels | `{0: 2, 4: 6, 6: 4}` |
| completion rows | `[0,1,4,6]` x4, `[0,2,4,6]` x1, `[0,3,4,6]` x1, `[0,4,5,6]` x1, `[0,4,6,7]` x1, `[0,4,6,8]` x4 |

## Reading

The useful conclusion is:

```text
The target-sparse cases do not have a one-row repair inside the fixed
selected-row assignment.
```

This is useful because it blocks the cheapest local escape for assignments `0`
and `11`: simply completing one already target-pair row to `[0,4,6]` violates
the same selected-row witness-pair and crossing filters used by the
full-neighborhood packet.

The remaining target-sparse work must therefore be stronger than a one-row
repair. It can try to prove a genuine support-geometry obstruction for
assignments `0` and `11`, find a multi-row mechanism, or route the proof
through a separate center-migration lemma for the off-center rows.

## What This Does Not Prove

This artifact does not prove assignments `0` and `11` are impossible, does not
prove center migration, does not prove support existence, does not prove row
forcing, does not prove endpoint-`8` forcing, does not prove that pair `[3,5]`
is impossible, does not prove `n=9`, does not prove the bootstrap bridge, and
does not prove Erdos Problem #97.
