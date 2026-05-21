# Bootstrap T12 81:8 Singleton-Support Two-Row-Drop Audit

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet continues the source-`81`, row-`8` singleton-support audit by
relaxing the fixed source-`81` neighborhood one step beyond the one-row-drop
scan. The target row still contains bootstrap-core witnesses `[0,2]` and at
least one singleton support from `[5,6]`.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_8_singleton_support_two_row_drop.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_8_singleton_support_two_row_drop.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_8_singleton_support_two_row_drop.json`.

## Scan Scope

The scan uses the same nine center-`8` activation rows as
`docs/bootstrap-t12-81-8-singleton-support-audit.md`:

```text
[0,1,2,5]
[0,1,2,6]
[0,2,3,5]
[0,2,3,6]
[0,2,4,5]
[0,2,4,6]
[0,2,5,6]
[0,2,5,7]
[0,2,6,7]
```

For every unordered pair of non-target centers from

```text
0,1,2,3,4,5,6,7
```

both dropped rows may be any of their `70` possible selected 4-sets while row
`8` uses one of the nine activation rows. This gives

```text
9 * binomial(8,2) * 70 * 70 = 1,234,800
```

two-row-drop candidates.

The scan uses only the basic selected-row filters:

- row-pair cap;
- witness-pair cap;
- two-overlap crossing.

No Euclidean realization, exact distance equation, minimality hypothesis, or
rich-class forcing hypothesis is used.

## Result

There are `28` survivors, one for each dropped pair. All `28` are the trivial
original-neighborhood survivors:

```text
row 8 = [0,2,5,6]
both dropped rows = their original source-81 rows
```

The aggregate two-row-drop rejection counts are:

```text
crossing: 1871
row_pair+crossing: 1063
row_pair+witness_pair: 1277
row_pair+witness_pair+crossing: 1214683
witness_pair+crossing: 15878
survive: 28
```

The checked scan status is:

```text
ONLY_ORIGINAL_ROW8_SURVIVES_WHEN_ANY_TWO_OTHER_SOURCE81_ROWS_DROP
```

## Interpretation

This closes the first two-row relaxation of the `81:8` local escape route:
there is no non-original center-`8` singleton-support activation survivor even
when any two other source-`81` rows are allowed to move arbitrarily under the
basic selected-row incidence and crossing filters.

This is still a finite proof-mining diagnostic. It does not prove that
singleton support labels exist in a genuine rich-class catalogue, and it does
not prove that row `8` is forced by minimality or geometry.

## Remaining Gap

The next gap is no longer the one-row or two-row stress test for this fixed
target. Remaining escape mechanisms could still move three or more other
source-`81` rows, use additional auxiliary rich supports, or require a new
minimal/rich-class hypothesis that forces the support before any fixed-row
neighborhood is available.

## What This Does Not Prove

This artifact does not prove singleton support existence, row forcing, `n=9`,
the bootstrap bridge, or Erdos Problem #97. It does not produce or certify a
counterexample.
