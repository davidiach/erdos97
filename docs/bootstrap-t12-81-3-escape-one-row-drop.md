# Bootstrap T12 81:3 One-Row-Drop Escape Scan

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet is the next relaxation after
`docs/bootstrap-t12-81-3-escape-candidates.md`. That previous scan preserved
the seven source-`81` rows outside centers `3` and `6`. Here we allow any one
of those seven rows to move, one dropped center at a time.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_3_escape_one_row_drop.json`.

## Scan Scope

For each dropped center in

```text
0,1,2,4,5,7,8
```

the scan enumerates all

```text
70
```

possible replacement selected rows for that center. It also uses the same
replacement space as the previous escape-candidate scan:

```text
5
```

possible center-`6` supply classes containing deletion seed `[0,1,4]`, and

```text
8
```

possible connector-avoiding center-`3` classes using either `[0,4,6]` or
`[1,4,6]`.

So there are:

```text
7 * 70 * 5 * 8 = 19600
```

one-row-drop candidates.

## Result

All `19600` candidates fail the basic exact incidence/crossing filters:

```text
surviving candidates: 0
```

The aggregate rejection counts are:

```text
crossing: 77
row_pair+crossing: 18
row_pair+witness_pair+crossing: 18889
witness_pair+crossing: 616
```

Thus the checked scan status is:

```text
NO_BASIC_FILTER_SURVIVORS_WHEN_ANY_ONE_OTHER_SOURCE81_ROW_DROPS
```

## Remaining Gap

This is still not a bridge proof. It only rules out this finite relaxed
escape model:

```text
drop exactly one preserved non-3/non-6 source-81 row,
replace row 6 by one pre-3 supply class,
replace row 3 by one connector-avoiding class.
```

It does not rule out escape mechanisms that move two or more of the other
source-`81` rows, use more than one replacement class at centers `3` or `6`, or
depend on additional minimal/rich-class hypotheses not included in this scan.

## What This Does Not Prove

This artifact does not prove row forcing, rich-class existence, `n=9`, the
bootstrap bridge, or Erdos Problem #97. It is a finite proof-mining diagnostic
that narrows one concrete escape route.
