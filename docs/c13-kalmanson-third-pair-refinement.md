# C13 Kalmanson Third-Pair Refinement

Status: `EXACT_OBSTRUCTION` for 46,567 third-pair refinements of the
two-boundary-pair C13 frontier.

This is not an all-order cyclic-order search and does not prove that the
abstract `C13_sidon_1_2_4_10` pattern is impossible across all cyclic orders.

## Artifact

```text
data/certificates/c13_kalmanson_third_pair_refinement.json
```

Regenerate it with:

```bash
python scripts/refine_c13_kalmanson_third_pair.py \
  --assert-expected \
  --out data/certificates/c13_kalmanson_third_pair_refinement.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed. The full replay takes about three
minutes on the current checkout.

## Method

The previous partial-branch pass left 832 canonical two-boundary-pair prefixes
unclosed. This refinement appends one additional ordered left/right boundary
pair to each of those prefixes. Each parent has eight unplaced labels, hence
`8 * 7 = 56` third-pair children.

For every child branch, the script keeps only Kalmanson quadrilateral
inequalities whose vertex order is forced by that three-pair boundary prefix.
Each child has 490 prefix-forced Kalmanson rows. A positive-integer Farkas
combination of those rows is an exact obstruction for every completion of that
child branch.

## Counts

| Count | Value |
|---|---:|
| Unclosed two-pair parent prefixes | 832 |
| Third-pair children per parent | 56 |
| Third-pair child branches scanned | 46,592 |
| Prefix-forced Kalmanson rows per child | 490 |
| Certified third-pair child branches | 46,567 |
| Unclosed third-pair child branches | 25 |

The committed artifact records checked certificate summaries for representative
closed children, the support-size histogram, a digest of the scanned child
labels, and all 25 unclosed third-pair child records.

## Claim Boundary

Each certified child is an exact obstruction for every cyclic-order completion
of that fixed three-pair boundary prefix. The 25 unclosed children are not
counterexamples and are not evidence of realizability. They only mark where
this prefix-forced Kalmanson pass did not find an exact obstruction.

This does not close all cyclic orders of `C13_sidon_1_2_4_10`, and it does not
prove Erdos Problem #97.

## Next Step

Attack the 25 unclosed third-pair children by adding one more forced boundary
pair, adding additional exact inequality families, or deriving a branch-level
certificate that covers all completions of one remaining child.
