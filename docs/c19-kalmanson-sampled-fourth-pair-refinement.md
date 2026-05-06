# C19 Sampled Kalmanson Fourth-Pair Refinement

Status: `EXACT_OBSTRUCTION` for 3,643 fourth-pair child branches below the
28 sampled `C19_skew` three-boundary prefixes left open by the bounded prefix
pilot.

This is a sampled-frontier refinement, not an all-order C19 search. It does
not prove Erdos Problem #97, does not kill abstract `C19_skew`, and does not
produce a counterexample.

## Artifact

```text
data/certificates/c19_kalmanson_sampled_fourth_pair_refinement.json
```

Regenerate it with:

```bash
python scripts/refine_c19_kalmanson_sampled_fourth_pair.py \
  --assert-expected \
  --out data/certificates/c19_kalmanson_sampled_fourth_pair_refinement.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

## Method

The preceding bounded prefix pilot samples the first 128 deterministic
reflection-pruned three-boundary-prefix states for `C19_skew` and closes 100
of them by exact prefix-forced Kalmanson/Farkas certificates. This refinement
starts from the 28 unclosed sampled prefixes recorded in that artifact.

Each sampled parent has 12 remaining middle labels. The refinement appends one
additional ordered left/right boundary pair, giving `12 * 11 = 132` fourth-pair
children per parent and 3,696 child branches total.

For every child branch, the script keeps only Kalmanson quadrilateral
inequalities whose vertex order is forced by the four-pair boundary prefix.
Each child has 1,932 prefix-forced Kalmanson rows. A positive-integer Farkas
combination of those rows is an exact obstruction for every cyclic-order
completion of that child branch.

When every fourth-pair child below a sampled three-pair parent is closed, that
sampled parent is closed by finite subdivision.

## Counts

| Count | Value |
|---|---:|
| Sampled three-pair parents refined | 28 |
| Fourth-pair children per parent | 132 |
| Fourth-pair child branches scanned | 3,696 |
| Prefix-forced Kalmanson rows per child | 1,932 |
| Certified fourth-pair child branches | 3,643 |
| Unclosed fourth-pair child branches | 53 |
| Sampled parents closed by subdivision | 13 |
| Sampled parents still open after subdivision | 15 |

Combining the direct prefix pilot with this refinement, the sampled frontier
status is:

| Source | Count |
|---|---:|
| Sampled three-pair prefixes in prior pilot | 128 |
| Sampled prefixes closed directly by prior pilot | 100 |
| Sampled prefixes refined here | 28 |
| Sampled prefixes closed by fourth-pair subdivision | 13 |
| Sampled prefixes still unclosed after fourth-pair subdivision | 15 |

## Claim Boundary

Each certified fourth-pair child is an exact obstruction for every completion
of that one recorded four-pair boundary prefix. The 13 sampled parent closures
come only from finite subdivision of their 132 recorded children.

The 53 fourth-pair children left open by this pass were not counterexamples
and were not evidence of realizability. They marked the sampled frontier that
the later fifth-pair refinement subdivides exactly.

This refinement starts from only 28 sampled parents. The prior pilot samples
128 of 6,683,040 canonical three-boundary-prefix states. Therefore this
artifact is not exhaustive for `C19_skew` and does not affect the global
status of Erdos Problem #97.

## Next Step

The fifth-pair follow-up is recorded in
`docs/c19-kalmanson-sampled-fifth-pair-refinement.md`. It subdivides the 53
still-open fourth-pair children, closes all 4,770 fifth-pair children by exact
certificates, and therefore closes all 128 sampled C19 three-boundary-prefix
branches from the bounded prefix pilot.

The next exact move should increase the deterministic prefix sample or add
cheaper pruning before scaling the same subdivision chain.
