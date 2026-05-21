# Bootstrap T12 151 Singleton Two-Row-Drop Audit

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet extends the source-`151` singleton-support audit for the two
one-outside-label targets:

```text
151:5
151:8
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_singleton_two_row_drop.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_singleton_two_row_drop.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_151_singleton_two_row_drop.json`.

## Scan Scope

The source input is the existing singleton-support audit packet:

```text
data/certificates/bootstrap_t12_151_singleton_support_audit.json
```

For row `151:5`, the target row ranges over the nine selected rows containing
bootstrap-core witnesses `[2,4]` and at least one singleton support from
`[7,8]`.

For row `151:8`, the target row ranges over the nine selected rows containing
bootstrap-core witnesses `[1,2]` and at least one singleton support from
`[5,7]`.

For each target, the scan chooses two non-target row centers and allows both
of those selected rows to be arbitrary `4`-sets. Thus each target checks

```text
9 * binom(8,2) * 70 * 70 = 1,234,800
```

candidate states, and the two targets together check `2,469,600` states.

The scan uses only the same basic selected-row filters as the one-row-drop
audit:

- row-pair cap;
- witness-pair cap;
- two-overlap crossing in the natural cyclic order.

No Euclidean realization, exact distance equation, minimality hypothesis, or
rich-class forcing hypothesis is used.

## Result

The two-row-drop relaxation has `56` survivors in total:

```text
151:5 -> 28 survivors
151:8 -> 28 survivors
```

All survivors are trivial original-neighborhood survivors: the target row is
the original source-`151` row, and both dropped rows are also equal to their
original source-`151` rows.

The checked scan status is:

```text
ONLY_ORIGINAL_SOURCE151_ROWS_SURVIVE_TWO_ROW_DROP_SUPPORT_AUDIT
```

The rejection category counts are:

```text
151:5
  crossing                         1,871
  row_pair+crossing                1,063
  row_pair+witness_pair            1,277
  row_pair+witness_pair+crossing   1,214,683
  witness_pair+crossing            15,878
  survive                          28

151:8
  crossing                         3,059
  row_pair+crossing                1,146
  row_pair+witness_pair            1,135
  row_pair+witness_pair+crossing   1,215,556
  witness_pair+crossing            13,876
  survive                          28
```

## Remaining Gap

This closes the two-moving-row version of the narrow local escape route for
source-`151` singleton-support targets under the same basic filters. It still
does not prove that singleton support labels are forced by a genuine rich-class
catalogue, does not allow three or more other rows to move, and does not model
additional auxiliary rich supports.

## What This Does Not Prove

This artifact does not prove singleton support existence, row forcing, `n=9`,
the bootstrap bridge, or Erdos Problem #97. It is a finite proof-mining
diagnostic for two T12 row targets.
