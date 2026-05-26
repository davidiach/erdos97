# Bootstrap T12 81:3 Post-8 Supply-Chain CSP

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet is a catalogue-accounting companion to
`docs/bootstrap-t12-81-3-second-step-chains.md`, following the source prefix
packet in `docs/bootstrap-t12-81-3-first-supply-chains.md`. The source packet
found exactly three basic-filter survivor prefixes, all with center `8` as the
first activation from the deletion seed `[0,1,4]`, and none of those prefixes
admitted an immediate center-`6` supply support.

Here the same finite support-chain model is pushed to its natural endpoint
after center `8`. Before center `6` activates, the only remaining non-seed,
non-target, non-supply centers are:

```text
2,5,7
```

So the checker enumerates every ordered continuation through any subset of
`[2,5,7]`, then tries center `6`.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_3_post8_supply_chains.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_3_post8_supply_chains.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_3_post8_supply_chains.json`.

## Scan scope

The scan starts from the three stored center-`8` prefix survivors. At every
additional intermediate center, the auxiliary rich support may be any support of
size at least `4` containing at least three already-closed labels. At each
auxiliary center, the selected row may be any four-subset of the auxiliary
support or any four-set disjoint from it. Non-auxiliary centers may use any
selected four-set.

The filters are the same basic finite filters used in the source packet:

```text
row-pair cap
witness-pair cap
two-overlap crossing
same-center disjointness
```

The scan does not test Euclidean realizability.

## Result

The post-center-`8` continuation closes under these filters. The companion
second-step packet records the pruned continuation search; this packet records
the raw support-catalogue denominator before initial compatibility pruning.

| intermediate centers before `6` | support catalogues | initially compatible | selected-search nodes | empty domains | selected-row survivors |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 228 | 0 | 0 | 0 | 0 |
| 1 | 80,712 | 14 | 86 | 29 | 0 |
| 2 | 23,890,752 | 20 | 94 | 30 | 0 |
| 3 | 3,894,192,576 | 24 | 43 | 26 | 0 |
| total | 3,918,164,268 | 58 | 223 | 85 | 0 |

The only initially compatible intermediate orders are:

```text
length 1: 2
length 2: 2,5 and 2,7
length 3: 2,5,7
```

No initially compatible catalogue admits a selected-row completion.

The checked scan status is:

```text
NO_POST8_PRE6_SUPPLY_CHAIN_SURVIVORS_UNDER_BASIC_FILTERS
```

## Interpretation

Within this finite chain model, the three stored center-`8` prefixes no longer
leave a longer route to center `6`. This is the same closure boundary as the
second-step packet, with the added raw-catalogue accounting. The remaining
`81:3` escape must therefore leave this audited model, for example by using
additional simultaneous rich supports, a different minimality or rich-class
forcing hypothesis, or geometry not captured by these basic filters.

## What this does not prove

This artifact does not prove row forcing, rich-class existence, `n=9`, the
bootstrap bridge, or Erdos Problem #97. It is a proof-mining diagnostic for one
specific `81:3` post-center-`8` label-`6` escape model.
