# Bootstrap T12 81:3 First-Supply-Chain Prefix CSP

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet is the next audit after
`docs/bootstrap-t12-81-3-escape-rich-support-csp.md`. That earlier CSP ruled
out a direct center-`6` rich-support supply of label `6` together with a
connector-avoiding center-`3` support. Here the first pre-`3` activation from
the seed may be any non-seed, non-`3` center, not only center `6`.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_3_first_supply_chains.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_3_first_supply_chains.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_3_first_supply_chains.json`.

## Scan Scope

The deletion seed remains:

```text
[0,1,4]
```

The first pre-`3` activation center may be any label in:

```text
2,5,6,7,8
```

At that first center, the auxiliary rich support may be any support of size
`4` through `8` containing the seed. This gives `31` supports per first-step
center, or `155` first-step supports total.

The connector-avoiding center-`3` support is the same support family from the
rich-support CSP: it contains `[0,4,6]` but not `1`, or `[1,4,6]` but not `0`.
There are `30` such center-`3` supports.

For the auxiliary centers, the selected row may be any 4-subset of the support
or any 4-set disjoint from it. All other selected-row centers may choose any of
their `70` possible selected 4-sets.

The total implicit selected-row assignment space for these first-step prefixes
is:

```text
4983670464500000000
```

The checker uses the same basic filters as the previous support CSP:

```text
row-pair cap
witness-pair cap
two-overlap crossing
same-center disjointness
```

It does not test Euclidean realizability.

## Result

The first-step prefix scan does not close completely. It finds exactly three
basic-filter survivor prefixes:

```text
surviving first-step prefixes: 3
first-step survivor centers: 8
```

All three survivors start by activating center `8` from the seed. They are not
full pre-`3` label-`6` supply chains.

The deterministic prefix scan summary is:

```text
first-step support pairs: 4650
initial support-pair incompatible: 3958
initial support-pair searched: 692
search nodes: 8852
empty domains: 5339
detected prefix survivors: 3
```

The checker then tries to extend those three survivor prefixes by an immediate
center-`6` supply support, using the closure labels `[0,1,4,8]`. There are
`76` possible center-`6` supply supports per prefix, hence `228` immediate
extension candidates total. All are initially incompatible with the already
stored first-step and connector supports:

```text
immediate label-6 extension candidates: 228
surviving immediate label-6 extensions: 0
```

The checked scan status is:

```text
PREFIX_SURVIVORS_FOUND_BUT_NO_IMMEDIATE_LABEL6_SUPPLY_EXTENSION
```

## Interpretation

This is useful because it shows the direct center-`6` support is not the only
first-step question. The first admissible prefix, under these basic filters,
can start at center `8`. But the three surviving center-`8` prefixes do not
immediately supply label `6`.

So the remaining escape is narrower than before:

```text
seed [0,1,4]
  -> center 8 first
  -> some longer chain before center 6
  -> center 6 supplies label 6
  -> center 3 activates through a connector-avoiding support
```

The current packet does not rule out that longer chain. It records the three
prefix boundary cases that a future chain audit should attack.

## What This Does Not Prove

This artifact does not prove row forcing, rich-class existence, `n=9`, the
bootstrap bridge, or Erdos Problem #97. It is a proof-mining diagnostic for one
specific `81:3` pre-`3` label-`6` escape model.
