# Bootstrap T12 151:6 Label-4 Center-8 Target-Sparse Three-Row Repairs

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines the target-sparse repair-extension packet. The previous
packet recorded:

```text
All 6624 one-completion plus one-repair candidates fail basic filters.
```

This packet asks the next narrow repair question:

```text
After one target-pair row is completed to [0,4,6], can two additional row
replacements repair the selected-row assignment through the basic filters?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_target_sparse_three_row_repairs.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_target_sparse_three_row_repairs.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_center8_target_sparse_three_row_repairs.json
```

## Inputs

This packet joins:

- `data/certificates/bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.json`;
- `data/certificates/bootstrap_t12_151_6_label4_center8_target_sparse_completions.json`;
- `data/certificates/bootstrap_t12_151_6_label4_center8_target_sparse_two_row_repairs.json`.

## Gate Result

The depth-two repair gate is:

```text
NOT_READY_TARGET_SPARSE_THREE_ROW_REPAIRS_FAIL_BASIC_FILTERS
```

Pinned summary:

| Quantity | Value |
| --- | ---: |
| target-sparse assignments | `[0,11]` |
| source one-row completions | `12` |
| repair center pairs per completion | `28` |
| replacement row pairs per repair-center pair | `4761` |
| one-completion plus two-repair candidates | `1599696` |
| basic-filter surviving candidates | `0` |
| vertex-circle checked candidates | `0` |

Every depth-two repair candidate still has a crossing violation. Nearly every
candidate also retains a witness-pair-cap violation, and many add a
selected-indegree-cap violation:

| Failure reason | Attempts |
| --- | ---: |
| crossing | `1599696` |
| witness-pair cap | `1597494` |
| selected-indegree cap | `774974` |

The candidate distribution is:

| Quantity | Value |
| --- | --- |
| assignment repair candidates | `{0: 266616, 11: 1333080}` |
| completion rows | `[0,1,4,6]` x533232, `[0,2,4,6]` x133308, `[0,3,4,6]` x133308, `[0,4,5,6]` x133308, `[0,4,6,7]` x133308, `[0,4,6,8]` x533232 |
| missing target labels | `{0: 266616, 4: 799848, 6: 533232}` |

## Reading

The useful conclusion is:

```text
The target-sparse cases do not have a one-completion plus two-repair escape
inside the selected-row basic filters.
```

This strengthens the one-row and one-additional-row preflights, but it is
still not a geometric obstruction. It says that after completing one
target-pair row to the cascade triple `[0,4,6]`, changing two more
non-completion rows arbitrarily cannot repair the resulting selected-row
assignment through the basic filters.

The remaining target-sparse work must use genuine support geometry, center
migration, or a stronger mechanism than one completion plus two arbitrary row
repairs. This packet deliberately does not claim assignments `0` and `11` are
impossible.

## What This Does Not Prove

This artifact does not prove assignments `0` and `11` are impossible, does not
prove center migration, does not prove support existence, does not prove row
forcing, does not prove endpoint-`8` forcing, does not prove that pair `[3,5]`
is impossible, does not prove `n=9`, does not prove the bootstrap bridge, and
does not prove Erdos Problem #97.
