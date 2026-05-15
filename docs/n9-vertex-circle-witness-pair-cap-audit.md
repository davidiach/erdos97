# n=9 Witness-pair Cap Audit

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note audits one row-level counting filter in the repo-native `n=9`
vertex-circle exhaustive checker: an unordered witness pair `{a,b}` may occur
together in at most two selected rows. It does not claim a proof of `n=9`, does
not claim a counterexample, does not complete independent review of the
exhaustive checker, and does not update the official/global status.

## Witness-pair Cap Lemma

Let `P` be a strictly convex polygon. Fix two distinct labels `a,b`. If a
center `x` selects both `a` and `b`, then

```text
|p_x - p_a| = |p_x - p_b|.
```

Thus `p_x` lies on the perpendicular bisector of segment `p_a p_b`. A line
meets the boundary of a strictly convex polygon in at most two vertices, so at
most two centers can select both `a` and `b`.

Equivalently, for every unordered witness pair `{a,b}`,

```text
#{ x : a,b in S_x } <= 2.
```

This is a necessary condition for any selected-witness realization.

## Partial-prune Monotonicity

For a partial assignment `A`, let

```text
c_A({a,b}) = #{ x in dom(A) : a,b in S_x }.
```

If a candidate row `S_y` contains `{a,b}` and `c_A({a,b}) >= 2`, then adding
`S_y` makes `c({a,b}) >= 3`, contradicting the witness-pair cap. Since later
rows only increase these counts, such a rejection cannot be repaired by
extending the partial assignment.

Conversely, if every witness pair in a candidate row has current count at most
`1`, then adding that row does not violate this cap. Other filters may still
reject the row, but the witness-pair cap alone does not.

Thus the monotone partial version of the cap is exactly:

```text
reject S_y iff some pair {a,b} in S_y has c_A({a,b}) >= 2.
```

## Checker Equivalence

The checked source block is
`src/erdos97/n9_vertex_circle_exhaustive.py`.

For each row mask, the checker stores all six unordered pairs of selected
witnesses:

```python
ROW_PAIR_INDICES = {
    m: [PAIR_INDEX[pair(a, b)] for a, b in combinations(MASK_BITS[m], 2)]
    for opts in OPTIONS
    for m in opts
}
```

When testing a candidate row against a partial assignment, it applies exactly
the monotone cap predicate:

```python
if any(witness_pair_counts[pidx] >= PAIR_CAP for pidx in ROW_PAIR_INDICES[m]):
    continue
```

where `PAIR_CAP = 2`. After accepting a row into the branch, it increments
exactly those six pair counts and later decrements the same six counts during
backtracking.

## One-off Audit

The audit is now replayable together with the other row-level incidence
filters:

```bash
python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --json
```

The command recomputes the row-pair indices, local cap predicate, update
roundtrip, and witness-pair frequency histogram from the stored checker tables.
The transcript below records the historical one-off counts now stabilized by
that command.

A one-off audit recomputed the row-pair indices from `MASK_BITS`, tested every
local count profile in `{0,1,2}^6` for every unique row mask, and checked that
the increment/decrement update returns to the original count vector.

```text
unique row masks: 126
row-pair index mismatches: 0
rows with non-six pair indices: 0
local cap profiles tested: 91854
local cap predicate mismatches: 0
increment/decrement roundtrip errors: 0
witness-pair frequency histogram across unique row masks:
  21: 36
```

The final histogram is a combinatorial sanity check: in a 9-label universe,
each of the `36` unordered pairs occurs in exactly `binom(7,2) = 21` four-row
masks.

## Scope

This audit covers only the witness-pair cap and its partial-prune
monotonicity in the `n=9` checker.

It does not audit the selected-indegree cap, the two-overlap crossing filter,
the vertex-circle strict-edge lemma, the vertex-circle quotient obstruction,
row0 coverage, archive reconciliation, or the 184 frontier assignments. It
does not prove the full `n=9` finite case, does not prove Erdos Problem #97,
and does not give a counterexample.
