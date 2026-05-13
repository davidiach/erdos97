# Bootstrap T12 81:3 Trigger-Family Uniqueness

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet follows `docs/bootstrap-t12-81-3-escape-auxiliary-csp.md`. That CSP
allowed one center-`6` supply class and one center-`3` connector-avoiding class
to exist as auxiliary rich classes. This audit checks the specified trigger
families themselves under the same-center disjointness rule:

```text
At one fixed center, two distinct rich distance classes are disjoint.
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_3_trigger_uniqueness.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_3_trigger_uniqueness.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_3_trigger_uniqueness.json`.

## Audit Scope

The center-`6` supply-trigger family consists of the five 4-sets containing the
deletion seed `[0,1,4]`:

```text
[0,1,2,4], [0,1,3,4], [0,1,4,5], [0,1,4,7], [0,1,4,8]
```

Every pair in this family intersects in exactly three labels. Therefore a
same-center rich-class catalogue at center `6` can contain at most one class
from this supply-trigger family.

The center-`3` connector-avoiding family consists of the eight 4-sets using
either `[0,4,6]` or `[1,4,6]`:

```text
[0,2,4,6], [0,4,5,6], [0,4,6,7], [0,4,6,8],
[1,2,4,6], [1,4,5,6], [1,4,6,7], [1,4,6,8]
```

Every pair in this family intersects in at least `[4,6]`. The checked
intersection histogram is:

```text
intersection size 2: 12 pairs
intersection size 3: 16 pairs
```

Therefore a same-center rich-class catalogue at center `3` can contain at most
one class from this connector-avoiding trigger family.

## Result

The checked scan status is:

```text
SPECIFIED_TRIGGER_FAMILIES_ARE_SAME_CENTER_UNIQUE
```

The summary counts are:

```text
center-6 supply classes: 5
center-6 disjoint trigger pairs: 0
center-6 max pairwise-disjoint trigger family size: 1

center-3 connector-avoiding classes: 8
center-3 disjoint trigger pairs: 0
center-3 max pairwise-disjoint trigger family size: 1
```

For any fixed auxiliary class in either family, the selected row at that same
center has exactly two equal-or-disjoint 4-set options: the class itself, or
the unique disjoint 4-set complement in the eight labels other than the center.
This justifies the two-choice selected-row model used by the auxiliary CSP
inside these specified trigger families.

## Remaining Gap

This removes only one wording-level looseness from the auxiliary-CSP gap:
within the specified trigger families, a richer catalogue cannot contain two
center-`6` supply triggers or two center-`3` connector-avoiding triggers at the
same center.

It does not rule out replacement classes outside these specified trigger
families, does not prove that either trigger class exists in a genuine
counterexample, and does not add a new minimality or rich-class forcing
hypothesis.

## What This Does Not Prove

This artifact does not prove row forcing, rich-class existence, `n=9`, the
bootstrap bridge, or Erdos Problem #97. It is a small exact proof-mining audit
around the `81:3` escape route.
