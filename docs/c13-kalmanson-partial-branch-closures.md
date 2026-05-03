# C13 Kalmanson Partial Branch Closures

Status: `EXACT_OBSTRUCTION` for 5,108 fixed two-sided boundary prefixes of
`C13_sidon_1_2_4_10`.

This is not an all-order cyclic-order search and does not prove that the
abstract C13 Sidon pattern is impossible across all cyclic orders.

## Artifact

```text
data/certificates/c13_kalmanson_partial_branch_closures.json
```

Regenerate it with:

```bash
python scripts/certify_c13_kalmanson_partial_branches.py \
  --assert-expected \
  --out data/certificates/c13_kalmanson_partial_branch_closures.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

The committed artifact is compact. It records closure counts, support-size
histograms, twelve checked certificate examples, and a digest plus first/last
windows for the 832 boundary prefixes not closed by this pass. Add
`--include-certificates` to include full certificate objects for the stored
examples.

## Method

The scan uses the same canonical two-boundary-pair states as the prefix-branch
pilot. Each state represents cyclic orders of the form:

```text
0, left[0], left[1], middle permutation, right[1], right[0]
```

For each boundary prefix, the script keeps only Kalmanson quadrilateral
inequalities whose four labels have a unique order in every completion of the
prefix. Any quadrilateral containing two or more unordered middle labels is
discarded.

If a positive-integer Farkas combination of these prefix-forced inequalities
has zero total coefficient after quotienting by the selected row distance
equalities, the contradiction `0 > 0` holds for every completion of that one
boundary prefix.

## Counts

| Count | Value |
|---|---:|
| Raw two-boundary-pair states | 11,880 |
| Canonical states after reflection accounting | 5,940 |
| Prefix-forced Kalmanson rows per state | 170 |
| Certified prefix branches | 5,108 |
| Unclosed prefix branches | 832 |

Support sizes for the closed branches range from 2 to 15 inequalities. The
committed artifact records the full support-size histogram and a digest of the
full unclosed-branch label list.

## Claim Boundary

Each closed branch is an exact obstruction for all cyclic-order completions of
that fixed two-sided boundary prefix. This is stronger than a fixed-order
certificate for one sampled completion.

The remaining 832 boundary prefixes are not counterexamples and are not
evidence of realizability. They only mark where this particular prefix-forced
Kalmanson certificate pass did not find an exact obstruction.

This does not close all cyclic orders of `C13_sidon_1_2_4_10`, and it does not
prove Erdos Problem #97.

## Next Step

A third-pair refinement is recorded in
`docs/c13-kalmanson-third-pair-refinement.md` and
`data/certificates/c13_kalmanson_third_pair_refinement.json`. It attacks the
832 unclosed two-boundary-pair prefixes by adding one more forced left/right
boundary pair, closing 46,567 of 46,592 child branches and leaving 25 child
branches unresolved by that pass.
