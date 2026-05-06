# C19 Sampled Kalmanson Fifth-Pair Refinement

Status: `EXACT_OBSTRUCTION` for the fifth-pair subdivision of the 53 sampled
`C19_skew` fourth-pair child branches left open by the sampled fourth-pair
refinement.

Combined with the prior sampled prefix and fourth-pair artifacts, this closes
all 128 sampled three-boundary-prefix branches in the bounded C19 pilot. This
is not an all-order C19 search, does not prove Erdos Problem #97, and does not
produce a counterexample.

## Artifact

```text
data/certificates/c19_kalmanson_sampled_fifth_pair_refinement.json
```

Regenerate it with:

```bash
python scripts/refine_c19_kalmanson_sampled_fifth_pair.py \
  --assert-expected \
  --out data/certificates/c19_kalmanson_sampled_fifth_pair_refinement.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

## Method

The sampled fourth-pair refinement left 53 fourth-pair children unclosed.
These children belong to 15 of the 28 sampled three-boundary-prefix parents
that survived the direct prefix pass.

Each fourth-pair child has 10 remaining middle labels. This refinement appends
one additional ordered left/right boundary pair, giving `10 * 9 = 90`
fifth-pair children per parent and 4,770 child branches total.

For every child branch, the script keeps only Kalmanson quadrilateral
inequalities whose vertex order is forced by the five-pair boundary prefix.
Each child has 3,300 prefix-forced Kalmanson rows. A positive-integer Farkas
combination of those rows is an exact obstruction for every cyclic-order
completion of that child branch.

Because every fifth-pair child below each remaining fourth-pair parent closes,
all 53 fourth-pair parents are closed by finite subdivision.

## Counts

| Count | Value |
|---|---:|
| Sampled fourth-pair parents refined | 53 |
| Fifth-pair children per parent | 90 |
| Fifth-pair child branches scanned | 4,770 |
| Prefix-forced Kalmanson rows per child | 3,300 |
| Certified fifth-pair child branches | 4,770 |
| Unclosed fifth-pair child branches | 0 |
| Fourth-pair parents closed by subdivision | 53 |
| Fourth-pair parents still open after subdivision | 0 |

Combined sampled-frontier accounting:

| Source | Count |
|---|---:|
| Sampled three-pair prefixes in prior pilot | 128 |
| Sampled prefixes closed directly by prior pilot | 100 |
| Sampled prefixes closed by fourth-pair subdivision | 13 |
| Sampled prefixes closed by fifth-pair subdivision | 15 |
| Sampled prefixes remaining open after fifth-pair subdivision | 0 |

## Claim Boundary

Each certified fifth-pair child is an exact obstruction for every completion
of that one recorded five-pair boundary prefix. The 53 fourth-pair parent
closures come only from finite subdivision of their 90 recorded children.

The combined sampled-prefix conclusion is:

```text
100 sampled three-pair prefixes close directly
+ 13 sampled three-pair prefixes close by fourth-pair subdivision
+ 15 sampled three-pair prefixes close by fifth-pair subdivision
= 128 sampled three-pair prefixes closed
```

This is still a sampled-frontier result. The pilot samples only 128 of
6,683,040 canonical three-boundary-prefix states. Therefore this artifact is
not exhaustive for `C19_skew` and does not affect the global status of Erdos
Problem #97.

## Next Step

The next deterministic prefix window is recorded in
`docs/c19-kalmanson-prefix-window-128-159.md`, which closes branch indices 128
through 159 by the same exact certificate chain. Larger C19 scans should add a
reusable window driver or cheaper pruning before LP calls so the fifth-pair
fallback remains reviewable.
