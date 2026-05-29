# Bootstrap T12 81:3 repeated-support catalogue audit

Status: diagnostic bookkeeping only; not mathematical evidence for a general theorem.

This note follows up `docs/bootstrap-t12-81-3-chain-closure-csp.md`.  The
ordered chain-closure CSP leaves four prefix survivors in a sequential
one-support-per-center model, and none can activate center `6` next.  This
packet checks the smallest non-sequential continuation: add one disjoint
same-center support to one already activated prefix center, then test the
eligible center-`6` supply supports.

## Model

The input prefixes are the four stored chain-closure survivors.  For each
already activated non-`3` center in such a prefix, the checker adds one support
at the same center that is disjoint from the existing support there.  In the
stored prefixes this gives five repeated-support candidates:

| prefix | repeated center | repeated support |
|---:|---:|---|
| 0 | `8` | `[2,3,5,6]` |
| 1 | `2` | `[0,5,6,7]` |
| 1 | `8` | `[2,3,5,6]` |
| 2 | `8` | `[2,3,5,6]` |
| 3 | `8` | `[2,3,6,7]` |

For every repeated-support catalogue, center `6` is then allowed any support
containing at least three labels from the current closure.  Selected rows at a
center with auxiliary supports may be a 4-subset of one support or disjoint
from every support at that center.  The checker uses only the same row-pair,
witness-pair, crossing, and same-center disjointness filters as the earlier
`81:3` CSP packets.

Run:

```bash
python scripts/check_bootstrap_t12_81_3_repeated_support_catalogue_audit.py --assert-expected --json
```

## Result

The five repeated-support catalogues generate `464` center-`6`
supply-extension attempts.  Only one combined catalogue is initially compatible:

| prefix | repeated support | center-`6` supply support |
|---:|---|---|
| 1 | center `8`: `[2,3,5,6]` | `[2,4,7,8]` |

That catalogue still has no complete selected-row assignment under the same
basic filters.  The packet records zero center-`6` supply-extension survivors.

## Interpretation

This closes only one bounded continuation of the stored `81:3` chain-closure
survivors: a single disjoint repeated support at an already activated prefix
center, followed by one center-`6` activation support.

The remaining gap is still real.  This does not prove support existence,
genuine rich-class order, row forcing, `n=9`, the bootstrap bridge, or Erdos
Problem #97; and it is not a counterexample.
