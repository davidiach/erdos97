# Bootstrap T12 151 Singleton-Support Audit

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet follows the one-outside-label ledger for the two source-`151`
singleton-support targets:

```text
151:5
151:8
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_singleton_support_audit.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_singleton_support_audit.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_151_singleton_support_audit.json`.

## Scan Scope

For row `151:5`, the scan enumerates every center-`5` selected row containing
bootstrap-core witnesses `[2,4]` and at least one singleton support from
`[7,8]`.

For row `151:8`, the scan enumerates every center-`8` selected row containing
bootstrap-core witnesses `[1,2]` and at least one singleton support from
`[5,7]`.

Each target has nine activation rows.

First, the scan replaces only the target row and preserves the other eight
source-`151` selected rows.

Second, it performs a one-row-drop relaxation: for each dropped non-target
center, the dropped row may be any of its `70` possible selected 4-sets while
the target row uses one of its nine singleton-support activation rows. This
gives:

```text
151:5: 9 * 8 * 70 = 5040
151:8: 9 * 8 * 70 = 5040
```

Both scans use only the basic selected-row filters:

- row-pair cap;
- witness-pair cap;
- two-overlap crossing.

No Euclidean realization, exact distance equation, minimality hypothesis, or
rich-class forcing hypothesis is used.

## Result

In the fixed-neighborhood scan, each target has exactly one survivor: its
original source-`151` row.

```text
151:5 -> [2,4,7,8]
151:8 -> [1,2,5,7]
```

In the one-row-drop relaxation, each target has eight survivors. All are the
trivial original-neighborhood survivors: the target row is original, and the
dropped row is also equal to its original source-`151` row.

The checked scan status is:

```text
ONLY_ORIGINAL_SOURCE151_SINGLETON_ROWS_SURVIVE_SUPPORT_AUDITS
```

## Remaining Gap

This closes a narrow local escape route for the two source-`151`
singleton-support targets under a fixed source-`151` neighborhood and a
one-row-drop stress test. It does not prove that singleton support labels are
forced by a genuine rich-class catalogue, does not allow two or more other rows
to move, and does not model additional auxiliary rich supports.

A follow-up two-row-drop relaxation is recorded in
`docs/bootstrap-t12-151-singleton-two-row-drop.md`. It allows any unordered
pair of non-target rows to move arbitrarily and finds only the same trivial
original-neighborhood survivors. That extension is still finite
incidence/crossing bookkeeping only, not row forcing or a bridge proof.

## What This Does Not Prove

This artifact does not prove singleton support existence, row forcing, `n=9`,
the bootstrap bridge, or Erdos Problem #97. It is a finite proof-mining
diagnostic for two T12 row targets.
