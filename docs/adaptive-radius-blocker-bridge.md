# Adaptive radius-blocker bridge

Status: `LEMMA` / bridge fork. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note records the useful proof-facing extraction from the 2026-05-10
bridge-output triage. It replaces a fixed-row peeling question by an adaptive
alternative over all rich distance classes.

## Definitions

Let `P` be a strictly convex 4-bad polygon with vertex set `V`. For a vertex
`y`, let `R(y)` be the family of rich distance classes at `y`:

```text
R(y) = { C subset V \ {y} : C is one exact distance class at y and |C| >= 4 }.
```

A selected row at `y` is any 4-subset of a class in `R(y)`.

For `U subset V`, with `|U| >= 4`, call `U` a radius-blocker if

```text
for every y in U and every C in R(y), |C cap U| <= 2.
```

Thus no vertex inside `U` has any rich class with three witnesses still inside
`U`.

## Lemma

For any strictly convex 4-bad polygon, adaptive reverse peeling has the
following alternative.

Either:

1. it reaches a three-vertex seed and constructs an ear-orderable selected
   witness system; or
2. it stops at a radius-blocker.

Consequently, if a hypothetical counterexample admits no ear-orderable
selected-witness system, then it contains a radius-blocker.

If `P` is a minimal counterexample and `U` is such a blocker, with
`O = V \ U`, then every rich class at every center in `U` contains at least
two vertices of `O`, and

```text
|U| <= |O| (|O| - 1).
```

Moreover, any fragile critical 4-tie centered at a vertex of `U` contains at
most two vertices of `U` and at least two vertices of `O`.

## Proof

Start with `X = V`. If `|X| > 3` and `X` is not a radius-blocker, then some
`y in X` and some rich class `C in R(y)` have `|C cap X| >= 3`. Choose a
selected row at `y` containing three vertices of `C cap X`, and remove `y`
from `X`.

If this process reaches a three-set, put that three-set first in the forward
order and append the removed vertices in reverse removal order. When a vertex
`y` is added back, the three witnesses chosen at its removal time are already
present, because they remained in the set after `y` was removed. Choosing
arbitrary rich rows for the three seed vertices completes a full selected
witness system. This is an ear-orderable selection.

If the process stops with `|X| >= 4`, then by construction no `y in X` has a
rich class meeting `X` in three or more vertices. Hence `X` is a
radius-blocker.

Now suppose an ear-orderable selected-witness system is impossible. A maximal
adaptive peeling cannot reach a three-set, so it stops at a blocker `U`.
For every `y in U` and every `C in R(y)`, the blocker condition gives
`|C cap U| <= 2`. Since `|C| >= 4`, each such class contains at least two
vertices outside `U`.

Choose one outside pair from one rich class for each `y in U`. A fixed
unordered outside pair `{a,b}` can be chosen for at most two centers, because
all such centers lie on the perpendicular bisector of `ab`, and a line meets a
strictly convex polygon boundary in at most two vertices. There are
`binom(|O|, 2)` outside pairs, so

```text
|U| <= 2 binom(|O|, 2) = |O| (|O| - 1).
```

Finally, if a fragile critical 4-tie is centered at some `y in U`, it is one
of the rich classes in `R(y)`. The blocker condition therefore permits at most
two of its four witnesses inside `U`, so at least two are in `O`.

## Research use

This fork is useful because it handles the noncanonical selection issue: a real
bad polygon may have several rich distance classes at a center, and fixed-row
stuck sets do not see that disjunction.

The next bridge target is therefore precise:

```text
minimal fragile cover + full badness + strict convex geometry
    => no radius-blocker.
```

or else:

```text
construct an exact radius-blocker escape mechanism that survives the current
vertex-circle, Kalmanson/Farkas, row-circle, and fragile-cover filters.
```

The helper module `src/erdos97/adaptive_blockers.py` implements the finite
bookkeeping behind this alternative. It does not certify geometry by itself.

Check the smoke tests with:

```bash
python -m pytest tests/test_adaptive_blockers.py -q
```
