# Bootstrap T12 81:3 Auxiliary-Rich-Class Escape CSP

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet relaxes `docs/bootstrap-t12-81-3-escape-full-neighborhood.md`.
There, the center-`6` supply class and center-`3` connector class were also the
selected rows at their centers. Here those two classes may instead be
auxiliary rich classes.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_3_escape_auxiliary_csp.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_3_escape_auxiliary_csp.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_3_escape_auxiliary_csp.json`.

## Scan Scope

The scan keeps the same auxiliary escape classes:

```text
5
```

possible center-`6` supply classes containing deletion seed `[0,1,4]`, and

```text
8
```

possible connector-avoiding center-`3` classes using either `[0,4,6]` or
`[1,4,6]`.

For centers `3` and `6`, the selected row may be either the auxiliary class or
the unique disjoint 4-set at that center. This encodes the same-center
distance-class rule: two distinct rich classes at one center are disjoint.

All seven other selected-row centers

```text
0,1,2,4,5,7,8
```

may choose any of their

```text
70
```

possible selected 4-sets. The implicit selected-row assignment space is:

```text
5 * 8 * 2 * 2 * 70^7 = 1317668800000000
```

The checker uses exact backtracking with row-pair, witness-pair, cyclic
crossing, and same-center disjointness filters.

## Result

The auxiliary-rich-class CSP has no complete assignment satisfying these basic
filters:

```text
surviving assignments: 0
```

The checked scan status is:

```text
NO_BASIC_FILTER_SURVIVORS_WITH_AUXILIARY_SUPPLY_AND_CONNECTOR_CLASSES
```

The deterministic backtracking summary is:

```text
fixed auxiliary pairs: 40
initial auxiliary-pair incompatible: 8
initial auxiliary-pair searched: 32
search nodes: 1287
empty domains: 730
complete solutions: 0
```

## Remaining Gap

This is still not a bridge proof. It rules out the finite relaxed escape model
where one center-`6` supply class and one center-`3` connector class are added
as auxiliary rich classes, and each center still contributes one selected row.

It does not rule out richer catalogues with more than one auxiliary
supply/connector class, replacement classes outside the specified spaces, or
additional minimal/rich-class hypotheses not included in this scan.

## What This Does Not Prove

This artifact does not prove row forcing, rich-class existence, `n=9`, the
bootstrap bridge, or Erdos Problem #97. It is a finite proof-mining diagnostic
that narrows one concrete escape route.
