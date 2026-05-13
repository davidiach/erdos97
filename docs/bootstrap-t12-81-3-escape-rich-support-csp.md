# Bootstrap T12 81:3 Rich-Support Auxiliary Escape CSP

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet strengthens `docs/bootstrap-t12-81-3-escape-auxiliary-csp.md`.
There, the center-`6` supply object and center-`3` connector-avoiding object
were represented by 4-set auxiliary classes. Here they may be larger rich
distance-class supports.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_3_escape_rich_support_csp.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_3_escape_rich_support_csp.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_3_escape_rich_support_csp.json`.

## Scan Scope

The center-`6` supply support may be any rich support of size `4` through `8`
containing the deletion seed `[0,1,4]`. The support-size histogram is:

```text
size 4:  5
size 5: 10
size 6: 10
size 7:  5
size 8:  1
```

The center-`3` connector-avoiding support may contain `[0,4,6]` but not `1`,
or `[1,4,6]` but not `0`. This keeps the support from already containing the
connector pair `[0,1]`. The support-size histogram is:

```text
size 4:  8
size 5: 12
size 6:  8
size 7:  2
```

For centers `3` and `6`, the selected row may be any 4-subset of the auxiliary
support or any 4-set disjoint from it. The seven other selected-row centers

```text
0,1,2,4,5,7,8
```

may choose any of their `70` possible selected 4-sets.

The total implicit selected-row assignment space is:

```text
996734092900000000
```

The checker treats each auxiliary support as a genuine rich support for the
basic filters: support pairs contribute all witness-pairs inside the support,
two supports at different centers may not share three witnesses, and a
two-witness overlap must satisfy the same crossing condition as selected rows.

## Result

The rich-support auxiliary CSP has no complete assignment satisfying the basic
filters:

```text
surviving assignments: 0
```

The checked scan status is:

```text
NO_BASIC_FILTER_SURVIVORS_WITH_RICH_SUPPORT_AUXILIARIES
```

The deterministic backtracking summary is:

```text
auxiliary support pairs: 930
initial support-pair incompatible: 700
initial support-pair searched: 230
search nodes: 2169
empty domains: 1268
complete solutions: 0
```

## Remaining Gap

This closes the larger-support version of the focused `81:3` escape model:
within this model, the supply or connector need not be exactly a 4-set class.

It still does not prove that a supply or connector support exists, does not
model additional auxiliary rich supports at other centers, and does not add a
minimality or rich-class forcing hypothesis. It also remains an incidence and
crossing diagnostic, not a Euclidean realizability theorem.

## What This Does Not Prove

This artifact does not prove row forcing, rich-class existence, `n=9`, the
bootstrap bridge, or Erdos Problem #97. It narrows one concrete escape route in
the `81:3` proof-mining chain.
