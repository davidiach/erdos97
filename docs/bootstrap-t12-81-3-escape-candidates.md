# Bootstrap T12 81:3 Escape Candidates

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet is the next relaxation after the `81:3` order-escape guard. The
guard in `docs/bootstrap-t12-81-3-order-escape.md` assumes the source-`81`
center-`6` fixed row `[0,3,4,7]` is preserved. Here we drop that one row, and
also allow the target center-`3` row to be replaced by a connector-avoiding
class.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_3_escape_candidates.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_3_escape_candidates.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_3_escape_candidates.json`.

## Scan Scope

The scan preserves the seven source-`81` rows outside centers `3` and `6`:

```text
0,1,2,4,5,7,8
```

It then enumerates:

```text
5
```

possible center-`6` supply classes containing the deletion seed `[0,1,4]`, and

```text
8
```

possible connector-avoiding center-`3` classes using either `[0,4,6]` or
`[1,4,6]`.

So there are:

```text
5 * 8 = 40
```

relaxed escape candidates.

## Result

All `40` candidates fail the basic exact incidence/crossing filters:

```text
surviving candidates: 0
```

The rejection counts are:

```text
crossing: 2
row_pair+witness_pair+crossing: 33
witness_pair+crossing: 5
```

Thus the checked scan status is:

```text
NO_BASIC_FILTER_SURVIVORS_UNDER_SOURCE81_OTHER_ROWS_PRESERVED
```

## Remaining Gap

This is still not a bridge proof. It only rules out this very specific relaxed
escape model:

```text
preserve the seven non-3/non-6 source-81 rows,
replace row 6 by one pre-3 supply class,
replace row 3 by one connector-avoiding class.
```

It does not rule out richer catalogues that do not preserve those other rows,
that use more than one replacement class at centers `3` or `6`, or that need
additional minimal/rich-class hypotheses not included in this scan.

## What This Does Not Prove

This artifact does not prove row forcing, rich-class existence, `n=9`, the
bootstrap bridge, or Erdos Problem #97. It is a finite proof-mining diagnostic
that narrows one concrete escape route.
