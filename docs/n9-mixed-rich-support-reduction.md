# n=9 mixed rich-support reduction

Status: `REVIEW_PENDING_DIAGNOSTIC` / generator-independent finite support
catalogue. No general proof of Erdos Problem #97 is claimed. No
counterexample is claimed.

This note extends `docs/n9-all-five-rich-support-obstruction.md` from the
all-size-five subcase to the mixed four/five support catalogue. Work in the
cyclic order `0,1,2,3,4,5,6,7,8`. For each center, enumerate every four- or
five-subset of the other eight labels. A complete assignment chooses one such
support at each center.

The checker applies only exact necessary filters:

- two distinct distance circles share at most two witness vertices;
- if two centers share exactly two witnesses, the center chord and the
  shared-witness chord must cross in the cyclic order;
- any unordered witness pair can occur together in rich classes at at most two
  centers.

The last condition is the perpendicular-bisector pair-sharing cap: all centers
equidistant from the same two witness vertices lie on one line, and a line
meets a strict convex polygon boundary in at most two vertices.

## Checked Result

The checked artifact is:

```text
data/certificates/n9_mixed_rich_support_reduction.json
```

Verify it with:

```bash
python scripts/check_n9_mixed_rich_support_reduction.py --check --assert-expected --json
```

There are `126` possible supports at each center (`70` four-sets and `56`
five-sets), for `8,004,512,848,309,157,376` raw assignments. The exact
backtracking search visits `108,018` assignment nodes and leaves `184`
complete assignments. All `184` complete assignments use only four-witness
supports:

```text
complete assignments with 0 size-five supports: 184
complete assignments with >=1 size-five support: 0
```

Thus the generator-independent mixed support catalogue collapses to the same
all-exact-four frontier size already used by the review-pending `n=9`
vertex-circle pipeline.

The companion crosswalk
`data/certificates/n9_mixed_rich_frontier_crosswalk.json` checks the stronger
bookkeeping statement: the `184` terminal mixed-support assignments are
exactly the stored `184` pre-vertex-circle frontier assignments as a labelled
row set. The two generators order six assignments differently, but their
sorted row-set digest is identical:

```text
dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55
```

Verify it with:

```bash
python scripts/check_n9_mixed_rich_frontier_crosswalk.py --check --assert-expected --json
```

## Consequence

Repo-locally, this rules out any size-at-least-five rich distance class in an
`n=9` selected-witness counterexample. If such a class existed, choosing five
witnesses inside it and choosing one rich class at every other center would
give a complete mixed support assignment with at least one size-five support
satisfying the checked necessary filters.

## Boundary

This reduction does not independently prove the exact-four vertex-circle
exhaustive checker. It does not prove `n=9`, does not prove the adaptive
radius-blocker bridge, does not prove Erdos Problem #97, and does not provide a
counterexample.

The next review target is the exact-four frontier itself: the `184`
all-exact-four assignments still need the existing vertex-circle/review
pipeline or a smaller reusable local-lemma replacement.
