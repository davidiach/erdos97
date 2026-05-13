# Bootstrap T12 151:6 Outside-Pair Audit

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet follows the outside-pair and relation-sufficient ledgers for source
`151`, row `6`. That row has bootstrap-core witness `[0]` and three outside
support pairs:

```text
[3,5]
[3,8]
[5,8]
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_outside_pair_audit.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_outside_pair_audit.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_151_6_outside_pair_audit.json`.

## Scan Scope

The scan enumerates every center-`6` selected row containing bootstrap-core
witness `[0]` and at least one outside support pair from `[3,5]`, `[3,8]`, or
`[5,8]`. There are thirteen such rows:

```text
[0,1,3,5]
[0,1,3,8]
[0,1,5,8]
[0,2,3,5]
[0,2,3,8]
[0,2,5,8]
[0,3,4,5]
[0,3,4,8]
[0,3,5,7]
[0,3,5,8]
[0,3,7,8]
[0,4,5,8]
[0,5,7,8]
```

First, the scan replaces only source-`151` row `6` and preserves the other
eight source-`151` selected rows.

Second, it performs a one-row-drop relaxation: for each dropped center in

```text
0,1,2,3,4,5,7,8
```

the dropped row may be any of its `70` possible selected 4-sets while row `6`
uses one of the thirteen outside-pair activation rows. This gives

```text
13 * 8 * 70 = 7280
```

one-row-drop candidates.

Both scans use only the basic selected-row filters:

- row-pair cap;
- witness-pair cap;
- two-overlap crossing.

No Euclidean realization, exact distance equation, minimality hypothesis, or
rich-class forcing hypothesis is used.

## Result

In the fixed-neighborhood scan, the only survivor is the original row:

```text
[0,3,5,8]
```

The fixed-neighborhood rejection counts are:

```text
crossing: 2
row_pair+witness_pair+crossing: 9
witness_pair+crossing: 1
survive: 1
```

In the one-row-drop relaxation, there are eight survivors. All eight are the
trivial original-neighborhood survivors: row `6` is `[0,3,5,8]`, and the
dropped row is also equal to its original source-`151` row.

The aggregate one-row-drop rejection counts are:

```text
crossing: 118
row_pair+crossing: 15
row_pair+witness_pair: 36
row_pair+witness_pair+crossing: 6824
witness_pair+crossing: 279
survive: 8
```

The checked scan status is:

```text
ONLY_ORIGINAL_ROW6_SURVIVES_FIXED_AND_ONE_ROW_DROP_SUPPORT_AUDITS
```

## Remaining Gap

This closes a narrow local escape route for the `151:6` bridge target under a
fixed source-`151` neighborhood and a one-row-drop stress test. It does not
prove that outside support pairs are forced by a genuine rich-class catalogue,
does not allow two or more other rows to move, and does not model additional
auxiliary rich supports.

## What This Does Not Prove

This artifact does not prove outside-pair support existence, row forcing,
`n=9`, the bootstrap bridge, or Erdos Problem #97. It is a finite proof-mining
diagnostic for one relation-sufficient row target.
