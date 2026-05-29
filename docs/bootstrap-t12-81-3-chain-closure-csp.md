# Bootstrap T12 81:3 ordered chain-closure CSP

Status: diagnostic bookkeeping only; not mathematical evidence for a general theorem.

This note follows up `docs/bootstrap-t12-81-3-first-supply-chains.md`.  The
first-supply packet leaves three first-step prefix survivors, all beginning at
center `8`, and shows that none admits an immediate center-`6` label-`6` supply
support.  The ordered chain-closure CSP asks the next finite question: after a
surviving prefix, can any longer sequence of basic support activations reach
center `6` before the target center `3`?

## Model

The closure starts with the deletion seed `[0,1,4]`.  The center-`3`
connector-avoiding support is one of the same supports used by the rich-support
CSP: it contains `[0,4,6]` while avoiding `1`, or contains `[1,4,6]` while
avoiding `0`.  Center `3` is then held back as the eventual connector target.

A next auxiliary support may be centered at any not-yet-closed label in
`[2,5,6,7,8]`; it must contain at least three currently closed labels.  For
each candidate support catalogue, the checker reuses the same exact row-pair,
witness-pair, crossing, and same-center disjointness filters as the
rich-support and first-supply packets.  A prefix is followed only when the
catalogue still has a complete selected-row assignment under those filters.

Run:

```bash
python scripts/check_bootstrap_t12_81_3_chain_closure_csp.py --assert-expected --json
```

## Result

The scan checks `5,916` candidate chain extensions:

| depth | candidate extensions |
|---:|---:|
| 1 | 4,650 |
| 2 | 912 |
| 3 | 354 |

Only four non-supply prefixes survive the basic filters:

| connector support at center 3 | chain centers | chain supports |
|---|---|---|
| `[0,2,4,6]` | `[8]` | `[[0,1,4,7]]` |
| `[0,2,4,6]` | `[8,2]` | `[[0,1,4,7], [1,3,4,8]]` |
| `[1,2,4,6]` | `[8]` | `[[0,1,4,7]]` |
| `[1,4,6,8]` | `[8]` | `[[0,1,4,5]]` |

No surviving prefix has next activated center `6`.  In aggregate, the checker
records `9,214` search nodes, `5,498` empty domains, `5,213` initially
incompatible catalogues, `703` searched catalogues, four stopped-after-first
prefix solutions, and zero supply-chain survivors.

## Interpretation

This closes the current longer-chain diagnostic inside the sequential
support-chain model: the only extra branch beyond the old first-step packet is
`8 -> 2`, and that branch still cannot reach center `6` under the same filters.

The immediate repeated-support follow-up is recorded in
`docs/bootstrap-t12-81-3-repeated-support-catalogue-audit.md`.  The remaining
gap is still broader than this sequential model: this packet does not prove
that genuine rich-class catalogues must expose supports in this order; it does
not prove row forcing, `n=9`, the bridge, or Erdos Problem #97; and it is not a
counterexample.
