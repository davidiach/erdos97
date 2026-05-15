# n=9 Selected-indegree Cap Audit

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note audits one row-level counting filter in the repo-native `n=9`
vertex-circle exhaustive checker: each label can occur as a selected witness in
at most

```text
floor(2*(n-1)/(row_size-1))
```

selected rows, assuming the witness-pair cap. It does not claim a proof of
`n=9`, does not claim a counterexample, does not complete independent review
of the exhaustive checker, and does not update the official/global status.

## Selected-indegree Cap Lemma

Let `P` be a strictly convex polygon and let `S_x` be the selected witness
`row_size`-set for center `x`. For a fixed label `v`, define its selected
indegree by

```text
d(v) = #{ x : v in S_x }.
```

Assume the witness-pair cap:

```text
#{ x : v,u in S_x } <= 2
```

for every unordered pair `{v,u}` with `u != v`.

Each selected row containing `v` contributes exactly `row_size-1` row-local
pairs `{v,u}`. Summing over all `u != v` gives

```text
(row_size-1) d(v) <= 2*(n-1).
```

Therefore

```text
d(v) <= floor(2*(n-1)/(row_size-1)).
```

For the repo-native `n=9` checker, `row_size = 4`, so every label has
selected indegree at most

```text
floor(2*8/3) = 5.
```

This is a necessary incidence consequence of the witness-pair cap. It is not
an independent geometric obstruction stronger than that cap.

## Partial-prune Monotonicity

For a partial assignment `A`, let

```text
d_A(v) = #{ x in dom(A) : v in S_x }.
```

If a candidate row `S_y` contains `v` and `d_A(v) >= 5`, then adding `S_y`
makes `d(v) >= 6`, contradicting the selected-indegree cap above. Later rows
only increase selected-indegree counts and cannot repair this violation.

Conversely, if every label in a candidate row has current count at most `4`,
then adding that row does not violate the selected-indegree cap. Other
filters may still reject the row, but the selected-indegree cap alone does
not.

Thus the monotone partial version of the `n=9` cap is exactly:

```text
reject S_y iff some v in S_y has d_A(v) >= 5.
```

## Checker Equivalence

The checked source block is
`src/erdos97/n9_vertex_circle_exhaustive.py`.

The checker defines

```python
MAX_INDEGREE = (PAIR_CAP * (N - 1)) // (ROW_SIZE - 1)
```

with `PAIR_CAP = 2`, `N = 9`, and `ROW_SIZE = 4`, hence
`MAX_INDEGREE = 5`.

When testing a candidate row against a partial assignment, it applies exactly
the monotone cap predicate:

```python
if any(column_counts[target] >= MAX_INDEGREE for target in MASK_BITS[m]):
    continue
```

After accepting a row into the branch, it increments exactly those four
selected-label counts and later decrements the same four counts during
backtracking.

## One-off Audit

The audit is now replayable together with the other row-level incidence
filters:

```bash
python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --json
```

The command recomputes the selected-indegree formula, local cap predicate,
update roundtrip, and label frequency histogram from the stored checker tables.
The transcript below records the historical one-off counts now stabilized by
that command.

A one-off audit checked the formula, every unique row-mask shape, every local
count profile in `{0,1,2,3,4,5}^4` for every unique row mask, and the
increment/decrement roundtrip.

```text
max indegree formula 5 5
unique row masks 126
row mask shape errors 0
local column profiles tested 163296
local column predicate mismatches 0
increment/decrement roundtrip errors 0
label frequency histogram across unique row masks {56: 9}
```

The final histogram is a combinatorial sanity check: in a 9-label universe,
each of the `9` labels occurs in exactly `binom(8,3) = 56` four-row masks.

## Scope

This audit covers only the selected-indegree cap and its partial-prune
monotonicity in the `n=9` checker, assuming the witness-pair cap already
audited separately.

It does not audit the two-overlap crossing filter, the witness-pair cap proof,
the vertex-circle strict-edge lemma, the vertex-circle quotient obstruction,
row0 coverage, archive reconciliation, or the 184 frontier assignments. It
does not prove the full `n=9` finite case, does not prove Erdos Problem #97,
and does not give a counterexample.
