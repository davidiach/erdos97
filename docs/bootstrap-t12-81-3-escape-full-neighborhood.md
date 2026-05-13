# Bootstrap T12 81:3 Full-Neighborhood Escape CSP

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet is the next relaxation after
`docs/bootstrap-t12-81-3-escape-two-row-drop.md`. The earlier scans allowed
one or two of the seven source-`81` rows outside centers `3` and `6` to move.
Here all seven of those rows may move at once.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_3_escape_full_neighborhood.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_3_escape_full_neighborhood.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_3_escape_full_neighborhood.json`.

## Scan Scope

The scan keeps the same replacement space at centers `3` and `6`:

```text
5
```

possible center-`6` supply classes containing deletion seed `[0,1,4]`, and

```text
8
```

possible connector-avoiding center-`3` classes using either `[0,4,6]` or
`[1,4,6]`.

For every fixed pair of such classes, the seven remaining row centers

```text
0,1,2,4,5,7,8
```

may each choose any of their

```text
70
```

possible selected 4-sets. The implicit assignment space is therefore:

```text
5 * 8 * 70^7 = 329417200000000
```

The checker does not enumerate this space naively. It uses exact backtracking
with row-pair, witness-pair, and cyclic crossing filters as pruning rules.

## Result

The full-neighborhood CSP has no complete assignment satisfying the basic
filters:

```text
surviving assignments: 0
```

The checked scan status is:

```text
NO_BASIC_FILTER_SURVIVORS_WHEN_ALL_OTHER_SOURCE81_ROWS_MOVE
```

The deterministic backtracking summary is:

```text
fixed replacement pairs: 40
initial fixed-pair incompatible: 8
initial fixed-pair searched: 32
search nodes: 1177
empty domains: 684
complete solutions: 0
```

## Remaining Gap

This is still not a bridge proof. It rules out the finite relaxed escape model
where centers `3` and `6` each receive one replacement class from the specified
spaces, and the other seven source-`81` rows are arbitrary selected 4-sets.

It does not rule out richer catalogues that use multiple simultaneous rich
classes per center, replacement classes outside the specified center-`3` and
center-`6` spaces, or additional minimal/rich-class hypotheses not included in
this scan.

## What This Does Not Prove

This artifact does not prove row forcing, rich-class existence, `n=9`, the
bootstrap bridge, or Erdos Problem #97. It is a finite proof-mining diagnostic
that narrows one concrete escape route.
