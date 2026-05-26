# Bootstrap/T12 81:3 second-supply-chain prefix CSP

Status: proof-mining diagnostic only; not mathematical evidence for a public
theorem.

This packet extends the source-`81`, row-`3` first-supply-chain audit by one
prefix step.  The previous packet leaves three basic-filter first-step prefix
survivors, all activating center `8` from deletion seed `[0,1,4]`, and none of
those prefixes admits an immediate center-`6` label-`6` supply support.  This
second-step packet asks whether one more pre-`3` activation can be inserted
before trying the center-`6` supply.

## What is checked

For each of the three stored first-step prefix survivors, the checker:

1. forms the enlarged closure `[0,1,4,8]`;
2. allows one additional non-target, non-supply center from `{2,5,7}` to
   activate from that closure;
3. enumerates every rich support of size `4` through `8` at that second-step
   center with at least three labels in the closure;
4. keeps the inherited center-`3` connector-avoiding support from the
   first-step prefix;
5. lets selected rows at auxiliary centers be any `4`-subset of their support
   or any disjoint `4`-set, while all remaining selected rows are arbitrary
   `4`-sets; and
6. applies the same row-pair, witness-pair, crossing, and same-center
   disjointness filters used by the first-supply-chain CSP.

The scan covers `684` fixed second-step prefix candidates:
`3` first-step prefixes times `3` second-step centers times `76` possible
second-step supports.

## Result

The scan leaves exactly one second-step prefix survivor:

- first-step survivor index: `1`;
- first-step center: `8`;
- first-step support: `[0,1,4,7]`;
- inherited center-`3` support: `[0,2,4,6]`;
- second-step center: `2`;
- second-step support: `[1,3,4,8]`.

The aggregate second-step scan records:

- `678` initially incompatible support catalogues;
- `6` searched support catalogues;
- `303` search nodes;
- `135` empty domains; and
- `1` detected second-step prefix survivor.

The follow-up immediate-label-`6` extension scan uses the closure
`[0,1,2,4,8]` from that survivor.  It checks all `118` center-`6` label-`6`
supply supports enabled by at least three labels in that closure.  No immediate
center-`6` label-`6` extension survives.

## Interpretation

This records an intermediate frontier in the longer-chain gap after the
center-`8` first-step prefixes.  In this two-step prefix audit, only the chain
prefix

```text
[0,1,4] -> center 8 via [0,1,4,7] -> center 2 via [1,3,4,8]
```

remains after two pre-`3` activation steps, and even that prefix has no
immediate center-`6` supply extension under the same basic filters.

The companion second-step-chain and post-`8` supply-chain packets continue the
same one-support-per-activated-center model through longer distinct-center
continuations.  This packet is therefore best read as a compact crosswalk from
the three first-supply survivors to the unique two-step prefix boundary.

This is not a proof of genuine rich-class order, not a proof of row forcing,
not a proof of `n=9`, not a proof of the bootstrap bridge, and not a
counterexample.

## Reproduction

```bash
python scripts/check_bootstrap_t12_81_3_second_supply_chains.py --check --assert-expected --json
```

The generator command is:

```bash
python scripts/check_bootstrap_t12_81_3_second_supply_chains.py --write --assert-expected
```

The checked artifact is:

```text
data/certificates/bootstrap_t12_81_3_second_supply_chains.json
```

## Remaining gap

The surviving two-step prefix is still not a full pre-`3` label-`6` supply
chain.  The companion distinct-intermediate and post-`8` packets audit longer
distinct-center continuations of this same model; repeated or multiple supports
at a center, richer catalogues with additional auxiliary supports, and a
minimality theorem forcing supports into this audited catalogue remain outside
this packet.
