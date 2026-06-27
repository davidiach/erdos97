# n=9 Kalmanson Three-row Core Compression

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`.

This note records a proof-mining compression of the review-pending fixed-order
`n=9` selected-witness Kalmanson replay. It does not prove Erdos Problem #97,
does not provide a counterexample, does not complete independent review, and
does not promote `n=9` beyond the repo's current review-pending finite-case
status.

## Scope

The checker in
`scripts/check_n9_kalmanson_three_row_core_compression.py` is self-contained:
it imports no project modules, reads no stored Kalmanson certificate as input,
and regenerates the fixed-cyclic-order selected-witness frontier directly from
the exact pair/crossing/count filters.

It reaches the same frontier as the fresh Kalmanson self-edge replay:

```text
raw row options per center: 70
raw assignments: 70^9 = 40,353,607,000,000,000
search nodes visited: 100,818
terminal assignments: 184
frontier replay sha256:
  3e6e208cd4212f9275eba2f0be9e32558da9b77544304d33d09abc953feeee9d
```

For each terminal assignment, the checker searches all strict Kalmanson
inequalities and all subsets of selected rows in increasing cardinality. The
stored artifact records both the first self-edge used by the older replay and
the best row-minimal self-edge found by this full subset search.

## Compression Result

Every one of the 184 terminal assignments has an optimally chosen Kalmanson
self-edge core using exactly three selected rows:

```text
best Kalmanson minimal core size histogram: {"3": 184}
best Kalmanson kind/core histogram: K1 -> 95, K2 -> 89
cyclic-dihedral core signatures: 56
compressed certificate sha256:
  55edb73475517dcc4e8413cdb84082957bc8426d2d67bd25cc28502ef3c124c0
```

For comparison, minimizing only the first Kalmanson self-edge in the existing
replay order gives larger row cores in many cases:

```text
first-self-edge minimal core size histogram:
  {"3": 90, "4": 53, "5": 31, "6": 6, "7": 4}
```

The useful new information is therefore proof-mining information: the `n=9`
frontier does not merely have Kalmanson self-edges, it has three-row Kalmanson
self-edge cores after the Kalmanson inequality is chosen optimally.

## Certificate

The generated artifact is:

```text
data/certificates/n9_kalmanson_three_row_core_compression.json
```

Each record contains the full terminal assignment, the first replay-compatible
Kalmanson self-edge, the row-minimal core for that first self-edge, the best
row-minimal Kalmanson self-edge, the three selected rows in that best core, and
a cyclic-dihedral signature for the best core.

## Commands

Regenerate and check the artifact:

```bash
python scripts/check_n9_kalmanson_three_row_core_compression.py --write --assert-expected --summary-json
python scripts/check_n9_kalmanson_three_row_core_compression.py --check --assert-expected --summary-json
```

The checker asserts the 184-assignment frontier, the Kalmanson split, the
all-three-row best-core histogram, the 56 best-core dihedral signatures, and
the compressed certificate digest.

## Audit Boundary

This artifact is a local-lemma mining aid. It still relies on the
selected-witness finite encoding, the two-overlap crossing predicate, the
witness-pair capacity filter, and the strict Kalmanson inequality convention.
It should be reviewed as a compression layer on top of the existing
review-pending `n=9` Kalmanson route, not as a source-of-truth theorem claim.

The next proof-facing step is to classify the 56 cyclic-dihedral three-row
signatures into reusable human-readable local lemmas, then look for bridge
hypotheses that force one of those local cores without enumerating the whole
`n=9` frontier.
