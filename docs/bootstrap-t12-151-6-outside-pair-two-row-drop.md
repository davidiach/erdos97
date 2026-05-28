# Bootstrap T12 151:6 Outside-Pair Two-Row-Drop Audit

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet extends the source-`151` row-`6` outside-pair audit by allowing
two non-target selected rows to move at the same time. Row `6` remains inside
the thirteen bootstrap-core-plus-outside-pair activation rows from
`docs/bootstrap-t12-151-6-outside-pair-audit.md`.

Run the checker with:

```bash
python scripts/check_bootstrap_t12_151_6_outside_pair_two_row_drop.py --check --assert-expected --json
```

Regenerate the artifact with:

```bash
python scripts/check_bootstrap_t12_151_6_outside_pair_two_row_drop.py --write --assert-expected
```

The checked artifact is:

```text
data/certificates/bootstrap_t12_151_6_outside_pair_two_row_drop.json
```

## Scan Scope

The scan uses the stored source-`151` row-`6` outside-pair audit as input. It
checks all states where:

- center `6` uses one of the `13` candidate rows containing bootstrap-core
  witness `[0]` and outside support pair `[3,5]`, `[3,8]`, or `[5,8]`;
- two centers from `{0,1,2,3,4,5,7,8}` are dropped;
- each dropped center may use any of its `70` selected `4`-sets;
- all other source-`151` rows are fixed.

This gives:

```text
13 * C(8,2) * 70^2 = 1,783,600
```

candidate states.

The scan uses only basic selected-row filters:

- row-pair cap;
- witness-pair cap;
- two-overlap crossing in the natural cyclic order.

No Euclidean realization, exact distance equation, minimality hypothesis, or
rich-class forcing hypothesis is used.

## Result

The two-row-drop scan leaves `28` survivors. These are exactly the trivial
original-neighborhood survivors, one for each dropped-center pair:

```text
row 6 remains [0,3,5,8]
both dropped rows remain their original source-151 rows
```

The rejection counts are:

```text
crossing: 3,670
row_pair+crossing: 1,591
row_pair+witness_pair: 1,356
row_pair+witness_pair+crossing: 1,756,671
survive: 28
witness_pair+crossing: 20,284
```

The checked scan status is:

```text
ONLY_ORIGINAL_ROW6_SURVIVES_TWO_ROW_DROP_OUTSIDE_PAIR_AUDIT
```

## Remaining Gap

This closes the next local relaxation level for the `151:6` outside-pair bridge
target. It does not prove outside-pair support existence, does not prove row
forcing, does not allow three or more other rows to move, and does not model
additional auxiliary rich supports.

## What This Does Not Prove

This artifact does not prove `n=9`, the bootstrap bridge, Erdos Problem #97, or
a counterexample. It is a finite proof-mining diagnostic for one
relation-sufficient row target.
