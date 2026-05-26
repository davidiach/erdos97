# Bootstrap T12 81:3 Second-Step Chain CSP

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet is the next audit after
`docs/bootstrap-t12-81-3-first-supply-chains.md`. That earlier packet found
exactly three basic-filter survivor prefixes. All three begin by activating
center `8` from seed `[0,1,4]`, and none admits an immediate center-`6`
label-`6` supply support.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_3_second_step_chains.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_3_second_step_chains.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_3_second_step_chains.json`.

## Scan Scope

The deletion seed remains:

```text
[0,1,4]
```

The source prefixes are the three stored center-`8` survivor prefixes from
`data/certificates/bootstrap_t12_81_3_first_supply_chains.json`.
After center `8`, the active closure is:

```text
[0,1,4,8]
```

The possible distinct intermediate centers before center `6` are:

```text
2,5,7
```

For each ordered chain of distinct intermediate centers, each intermediate
center receives one auxiliary support. A support is allowed exactly when it has
size at least `4`, excludes its own center, and contains at least three labels
from the current active closure. The active closure is then enlarged by the new
center label.

After any chain length `0` through `3`, center `6` receives one candidate
label-`6` supply support using the same activation rule. The stored
connector-avoiding center-`3` support from the source prefix is kept fixed.

The checker uses the same basic filters as the previous support CSP:

```text
row-pair cap
witness-pair cap
two-overlap crossing
same-center disjointness
```

It does not test Euclidean realizability.

## Result

The distinct-intermediate continuation scan closes this bounded model. It finds
no full selected-row assignment for any ordered chain of distinct intermediate
centers from `{2,5,7}` before center `6` supplies label `6`.

The deterministic scan summary is:

```text
source center-8 prefixes: 3
intermediate centers after center 8: 2,5,7
maximum distinct intermediate chain length: 3
support prefixes pruned before label-6 supply: 4112
label-6 supply catalogues tested: 9528
initially incompatible label-6 catalogues: 9470
searched label-6 catalogues: 58
search nodes: 223
empty domains: 85
detected solutions: 0
surviving chains: 0
```

By chain length, the label-`6` supply catalogue counts are:

```text
length 0: 228 tested, 228 initially incompatible, 0 searched
length 1: 708 tested, 694 initially incompatible, 14 searched
length 2: 2072 tested, 2052 initially incompatible, 20 searched
length 3: 6520 tested, 6496 initially incompatible, 24 searched
```

The checked scan status is:

```text
NO_DISTINCT_INTERMEDIATE_CENTER8_TO_LABEL6_CHAINS
```

## Interpretation

This narrows the previous remaining escape. The earlier boundary case was:

```text
seed [0,1,4]
  -> center 8 first
  -> some longer chain before center 6
  -> center 6 supplies label 6
  -> center 3 activates through a connector-avoiding support
```

Within the bounded model where every post-`8` intermediate activation uses a
new center from `{2,5,7}` and exactly one auxiliary support at that center, no
such chain survives the same basic filters.

The remaining escape is now outside this distinct-intermediate,
one-support-per-center model. Examples still not ruled out here include
repeated or multiple rich supports at one center, richer catalogues not
represented by a single support per activated center, or a future
minimal/rich-class theorem that changes which supports must be considered.

## What This Does Not Prove

This artifact does not prove row forcing, rich-class existence, `n=9`, the
bootstrap bridge, or Erdos Problem #97. It is a proof-mining diagnostic for one
specific `81:3` pre-`3` label-`6` escape model.
