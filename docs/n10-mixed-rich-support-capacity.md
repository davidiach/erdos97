# n=10 mixed rich-support capacity diagnostic

Status: `REVIEW_PENDING_DIAGNOSTIC` / generator-independent finite support
catalogue.

This note records a small support-level widening of the `n=9` mixed
rich-support reduction. It is not a proof of `n=10`, not a proof of Erdos
Problem #97, and not a counterexample.

## Setup

Fix the natural cyclic order on labels `0,1,...,9`. At each center, represent
one available rich distance class by a support of size `4` or `5`:

- an exact-four class is represented by its four witnesses;
- a class of size at least five is represented by an arbitrary five-witness
  sub-support.

The checker applies only the same support-level necessary filters used in the
mixed `n=9` catalogue:

1. **row-pair cap:** two distinct distance circles share at most two witness
   vertices;
2. **two-overlap crossing:** when two rows share exactly two witnesses, the
   center chord and shared-witness chord must cross in the cyclic order;
3. **witness-pair capacity:** an unordered witness pair can occur together in
   rich classes at at most two centers.

Thus, if a genuine convex decagon counterexample had `q` centers with a rich
class of size at least five, then some support assignment with exactly `q`
size-five supports would survive these necessary filters.

## Pair-budget first pass

The witness-pair capacity alone gives a quick upper bound. A size-four support
uses `binom(4,2)=6` witness pairs, while a size-five support uses
`binom(5,2)=10`. Since each unordered label pair can be used at most twice,
the total capacity for `n=10` is `2*binom(10,2)=90`. Therefore

```text
6(10-q) + 10q <= 90,
```

so `q <= 7`. The new checker exhausts the remaining cases `q=3,...,7`.

## Exhaustive support search

For each `q` from `3` through `7`, the checker enumerates the dihedral
representatives of the `q` centers that receive size-five supports. It then
searches all labelled support choices for that representative center set using
bitset domains, pair-cap propagation, row-pair compatibility propagation, and
minimum-domain branching. The support choices themselves are not quotient by
symmetry.

Checked command:

```bash
python scripts/check_n10_mixed_rich_support_capacity.py --check --assert-expected --json
```

Artifact:

```text
data/certificates/n10_mixed_rich_support_capacity.json
```

Summary of the checked run:

```text
q  dihedral reps checked  complete assignments  max depth reached
3  8                       0                     8
4  16                      0                     5
5  16                      0                     4
6  16                      0                     2
7  8                       0                     1
```

The checker also validates a direct `q=2` support assignment, so the bound is
sharp for these three necessary filters alone.

A follow-up rich vertex-circle quotient diagnostic,
`docs/n10-q2-rich-vertex-circle.md`, closes that sharp `q=2` layer after adding
one stronger quotient filter. The support-capacity artifact here remains only
the three-filter `q=3,...,7` catalogue.

## Consequence

Repo-locally, this finite catalogue reduces the `n=10` four/five support
abstraction as follows:

```text
any support assignment surviving these filters has at most 2 size-five supports;
equivalently, at least 8 centers are exact-four-only.
```

This is a useful branch cut for the review-pending `n=10` work because it says
that any size-at-least-five rich-class escape must be extremely sparse before
vertex-circle, Kalmanson, turn, or Euclidean realizability filters are even
applied.

## Scope warnings

- This is a necessary support-catalogue diagnostic only.
- It does not replay vertex-circle, Kalmanson, turn-inequality, or Euclidean
  realizability filters.
- It leaves the `q=0`, `q=1`, and `q=2` four/five support cases to stronger
  filters at this support-capacity level.
- It does not prove `n=10`, does not prove Erdos Problem #97, and does not
  provide a counterexample.
