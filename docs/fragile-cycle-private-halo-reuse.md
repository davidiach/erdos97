# Fragile-cycle private-halo reuse pair budget

Status: exact fixed-core pair-budget lemma with abstract full-row guardrails.
This note does not force the `23=27` quotient core, close the four/five-halo
regimes, prove Euclidean realizability, prove `n=11` or `n=12`, prove
Erdos Problem #97, or give a counterexample.

## Question

The fixed-core slot budget leaves one unresolved alternative:

- every four-halo retained cover has at least three retained-private halos;
- every five-halo retained cover has five retained-private halos.

Here retained-private means occurrence in exactly one of the four retained
rows. It says nothing about the other selected rows of a full system. The
next structural question is therefore exact:

```text
How many retained-private halos can remain private
after selecting one four-witness row at every center?
```

Call a retained-private halo **selected-private** when it occurs in no
non-retained selected row. Any retained-private halo that is not
selected-private is reused by a non-retained selected row and hence belongs to
an additional rich class in the underlying geometry.

## Pair-budget lemma

Let `P` be a set of `q` selected-private halos. Delete the labels in `P`
from the witness universe, leaving `n-q` possible witnesses for every
non-retained row. All `n-4` non-retained rows lie wholly in that universe and
contribute

```text
6(n-4)
```

witness-pair occurrences.

For retained row `i`, let `p_i` be the number of labels of `P` in that
row. Its remaining witnesses contribute `C(4-p_i,2)` pairs outside `P`.
Because every selected-private halo is retained-private,

```text
sum_i p_i = q,     0 <= p_i <= 2.
```

Every unordered witness pair occurs in at most two selected rows. Therefore a
necessary condition for a full selected system is

```text
6(n-4) + sum_i C(4-p_i,2) <= 2 C(n-q,2).       (*)
```

This uses only four-uniformity and the two-circle witness-pair cap. It does not
use a finite-search inference.

## Consequences

For four halos, `n=11`. If three retained-private halos were
selected-private, the retained load is at least

```text
min sum_i C(4-p_i,2) = 15.
```

The left side of `(*)` would be `42+15=57`, while the available capacity is
`2 C(8,2)=56`. Hence at most two retained-private halos remain
selected-private in any full extension. Consequently:

- a cover with three retained-private halos reuses at least one;
- a cover with four retained-private halos reuses at least two.

For five halos, `n=12`. Four selected-private halos have retained load at
least `12`, so the required load is `48+12=60` against capacity
`2 C(8,2)=56`. Thus at most three of the five halos remain selected-private,
and every full extension reuses at least two.

This is the promised rich-class crosswalk: the large-halo alternative cannot
remain completely private. It forces explicit additional rich-class
incidences outside the four retained rows.

## Falsification guardrails

The artifact stores two full selected-row systems and independently replays
self-exclusion, four-uniformity, row intersection/crossing, witness-pair
capacity, selected-indegree capacity, active retained coverage, essential
matching, and selected-row good deletion for every nonempty proper seed.

| Guardrail | Retained-private | Selected-private | Reused |
| --- | --- | --- | --- |
| four halos, `n=11` | `7,8,9,10` | `8` | `7,9,10` |
| five halos, `n=12` | `7,8,9,10,11` | `9,10` | `7,8,11` |

These witnesses falsify the stronger incidence claim that every
retained-private halo must be reused. They also show why the conclusion is a
bridge obligation rather than fixed-core closure. Both full systems contain
an equilateral hinge and a Kalmanson splice, so neither is a Euclidean escape
or counterexample. The pair-budget lower bounds are not claimed sharp.

## Updated bridge target

Combining the slot budget with this lemma gives:

```text
four halos:
  3 retained-private -> at least 1 additional rich-class reuse
  4 retained-private -> at least 2 additional rich-class reuses

five halos:
  5 retained-private -> at least 2 additional rich-class reuses
```

The next useful step is geometric: use the retained row together with these
forced reuse rows to obtain a critical-radius branch, deletion-profile
constraint, hinge/splice motif, or another exact metric obstruction. The
separate entry problem of forcing the `23=27` core from a genuine fragile
matching cycle also remains open.

## Replay

```bash
python scripts/check_fragile_cycle_private_halo_reuse.py \
  --check --assert-expected --summary-json

python -m pytest -q \
  tests/test_fragile_cycle_private_halo_reuse.py \
  tests/test_check_fragile_cycle_private_halo_reuse.py
```

The generated artifact is
`data/certificates/fragile_cycle_private_halo_reuse.json`; do not edit it
directly.
