# n=10 q=2 rich vertex-circle closure diagnostic

Status: `REVIEW_PENDING_DIAGNOSTIC` / finite support-quotient catalogue.

This note records a small widening of the `n=10` mixed rich-support capacity
diagnostic. It is not a proof of `n=10`, not a proof of Erdos Problem #97, and
not a counterexample.

## Setup

Fix the natural cyclic order on labels `0,1,...,9`. At each center, represent one available rich distance class by a support of size `4` or `5`:

- an exact-four class is represented by its four witnesses;
- a class of size at least five is represented by an arbitrary five-witness sub-support.

The earlier mixed-rich capacity diagnostic closes all cases with `q=3,...,7` size-five supports under the row-pair cap, two-overlap crossing, and witness-pair capacity filters, while recording a direct `q=2` support-filter witness. The new checker exhausts that `q=2` layer after adding the rich vertex-circle quotient gate.

For each rich class, the quotient gate unions all center-witness distances in the class and adds every nested-interval strict distance inequality from the full witness set. A strict self-edge or directed strict cycle obstructs the partial assignment; the obstruction is monotone under adding more rows.

## Checked command

```bash
python scripts/check_n10_q2_rich_vertex_circle.py --write --assert-expected
python scripts/check_n10_mixed_rich_support_capacity.py --check --assert-expected --json
python scripts/check_n10_q2_rich_vertex_circle.py --check --assert-expected --json
```

Artifact:

```text
data/certificates/n10_q2_rich_vertex_circle.json
```

## Summary

The checker reduces the two size-five centers by dihedral symmetry and searches all labelled support choices for each representative.

```text
size-five centers  nodes visited  dead ends  vertex-circle prunes  max depth  self-edge prunes  strict-cycle prunes
[0,1]              10,569         3,003      5,649                 5          2,332             3,317
[0,2]              34,486         13,406     12,911                6          4,738             8,173
[0,3]              66,565         34,642     17,162                6          7,537             9,625
[0,4]              95,385         50,264     22,718                6          8,276             14,442
[0,5]              113,919        58,559     27,272                6          9,962             17,310
```

Aggregate counts:

```text
representatives checked:        5
clean complete assignments:     0
nodes visited:                  320,924
dead ends:                      159,874
vertex-circle prunes:           85,712
self-edge prunes:               32,845
strict-cycle prunes:            52,867
maximum search depth reached:   6
```

## Consequence

Within the four/five support abstraction, adding the rich vertex-circle quotient
closes the previously sharp `q=2` layer. Combined with the existing
support-capacity closure for `q=3,...,7`, any `n=10` candidate surviving these
support-plus-quotient filters has at most one size-five support; equivalently,
at least nine centers are exact-four-only at this abstraction level. The new
checker itself exhausts exactly the `q=2` layer; the `q=3,...,7` part of the
combined consequence remains the earlier
`n10_mixed_rich_support_capacity` artifact.

The companion `q=1` replay in `docs/n10-q1-rich-vertex-circle.md` closes the
next layer. Combining all three artifacts leaves only the all-exact-four `q=0`
layer in this support-plus-quotient abstraction.

## Scope warnings

- This is a necessary support/quotient diagnostic only.
- It does not replay turn inequalities, Kalmanson certificates, or Euclidean realizability.
- This checker alone leaves the `q=0` and `q=1` four/five support cases to
  stronger filters.
- It does not prove `n=10`, does not prove Erdos Problem #97, and does not
  provide a counterexample.
