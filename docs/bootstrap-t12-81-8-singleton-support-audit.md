# Bootstrap T12 81:8 Singleton-Support Audit

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet follows the one-outside-label and relation-sufficient ledgers for
source `81`, row `8`. That row has bootstrap-core witnesses `[0,2]` and two
singleton outside supports, labels `5` and `6`.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_8_singleton_support_audit.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_8_singleton_support_audit.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_8_singleton_support_audit.json`.

## Scan Scope

The scan enumerates every center-`8` selected row containing the bootstrap-core
witnesses `[0,2]` and at least one singleton support from `[5,6]`. There are
nine such rows:

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

First, the scan replaces only source-`81` row `8` and preserves the other
eight source-`81` selected rows.

Second, it performs a one-row-drop relaxation: for each dropped center in

```text
0,1,2,3,4,5,6,7
```

the dropped row may be any of its `70` possible selected 4-sets while row `8`
uses one of the nine singleton-support activation rows. This gives

```text
9 * 8 * 70 = 5040
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
[0,2,5,6]
```

The fixed-neighborhood rejection counts are:

```text
row_pair+witness_pair+crossing: 6
witness_pair+crossing: 2
survive: 1
```

In the one-row-drop relaxation, there are eight survivors. All eight are the
trivial original-neighborhood survivors: row `8` is `[0,2,5,6]`, and the
dropped row is also equal to its original source-`81` row.

The aggregate one-row-drop rejection counts are:

```text
crossing: 47
row_pair+crossing: 11
row_pair+witness_pair: 36
row_pair+witness_pair+crossing: 4692
witness_pair+crossing: 246
survive: 8
```

The checked scan status is:

```text
ONLY_ORIGINAL_ROW8_SURVIVES_FIXED_AND_ONE_ROW_DROP_SUPPORT_AUDITS
```

## Remaining Gap

This closes a narrow local escape route for the `81:8` bridge target under a
fixed source-`81` neighborhood and a one-row-drop stress test. It does not
prove that singleton support labels are forced by a genuine rich-class
catalogue, does not allow two or more other rows to move, and does not model
additional auxiliary rich supports.

## What This Does Not Prove

This artifact does not prove singleton support existence, row forcing, `n=9`,
the bootstrap bridge, or Erdos Problem #97. It is a finite proof-mining
diagnostic for one relation-sufficient row target.
