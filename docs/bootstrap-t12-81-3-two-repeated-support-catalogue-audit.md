# Bootstrap T12 81:3 two-repeated-support catalogue audit

Status: diagnostic bookkeeping only; not mathematical evidence for a general theorem.

This note follows up
`docs/bootstrap-t12-81-3-repeated-support-catalogue-audit.md`.  The
one-layer repeated-support packet checks the smallest non-sequential
continuation after the ordered chain-closure survivors.  This packet checks
the next minimal widening: two repeated supports attached to already activated
prefix centers, each disjoint from the supports already present at its own
center, followed by the same center-`6` supply test.

## Model

The input prefixes are the four stored chain-closure survivors.  The checker
starts from the one-repeated-support candidates and adds a second disjoint
same-center support at an already activated non-`3` center.  The resulting
unordered support catalogues are deduplicated before testing center-`6` supply
extensions.

In the stored prefixes there is one unique two-repeated-support catalogue, and
it has two ordered generation paths:

| prefix | repeated support at center `2` | repeated support at center `8` |
|---:|---|---|
| 1 | `[0,5,6,7]` | `[2,3,5,6]` |

For that catalogue, center `6` is then allowed any support containing at least
three labels from the current closure.  Selected rows at a center with
auxiliary supports may be a 4-subset of one support or disjoint from every
support at that center.  The checker uses only the same row-pair,
witness-pair, crossing, and same-center disjointness filters as the earlier
`81:3` CSP packets.

Run:

```bash
python scripts/check_bootstrap_t12_81_3_two_repeated_support_catalogue_audit.py --assert-expected --json
```

## Result

The unique two-repeated-support catalogue is already initially incompatible
under the catalogue-level incidence/crossing/witness-pair filters.  Its `118`
center-`6` supply-extension attempts are also initially incompatible.  The
packet records zero initially compatible supply catalogues and zero
selected-row completions.

## Interpretation

This closes only one bounded continuation of the stored `81:3` chain-closure
survivors: two repeated supports at already activated prefix centers, each
disjoint from the supports already present at its own center, followed by one
center-`6` activation support.

The remaining gap is still real.  This does not prove support existence,
genuine rich-class order, row forcing, `n=9`, the bootstrap bridge, or Erdos
Problem #97; and it is not a counterexample.
