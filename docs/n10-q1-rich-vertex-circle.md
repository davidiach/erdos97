# n=10 q=1 rich vertex-circle closure diagnostic

Status: `REVIEW_PENDING_DIAGNOSTIC` / finite support-quotient catalogue.

This note records a small narrowing of the `n=10` four/five rich-support
abstraction. It is not a proof of `n=10`, not a proof of Erdos Problem #97, and
not a counterexample.

## Setup

Fix the natural cyclic order on labels `0,1,...,9`. At each center, represent
one available rich distance class by a support of size `4` or `5`:

- an exact-four class is represented by its four witnesses;
- a class of size at least five is represented by an arbitrary five-witness
  sub-support.

The earlier mixed-rich support-capacity diagnostic closes all cases with
`q=3,...,7` size-five supports under the row-pair cap, two-overlap crossing,
and witness-pair capacity filters. The follow-up `q=2` rich vertex-circle
quotient diagnostic closes the `q=2` layer after adding the rich
vertex-circle quotient gate. The checker recorded here exhausts the remaining
`q=1` layer with the same support-plus-quotient filters.

For each rich class, the quotient gate unions all center-witness distances in
the class and adds every nested-interval strict distance inequality from the
full witness set. A strict self-edge or directed strict cycle obstructs the
partial assignment; the obstruction is monotone under adding more rows.

## Checked command

```bash
python scripts/check_n10_q1_rich_vertex_circle.py --write --assert-expected
python scripts/check_n10_q1_rich_vertex_circle.py --check --assert-expected --json
```

Artifact:

```text
data/certificates/n10_q1_rich_vertex_circle.json
```

## Summary

There is one dihedral representative for the unique size-five center. It is
represented as center set `[0]`; support choices themselves remain labelled.

```text
size-five centers  nodes visited  dead ends  vertex-circle prunes  max depth  self-edge prunes  strict-cycle prunes
[0]                362,556        97,419     181,302               7          82,444            98,858
```

Aggregate counts:

```text
representatives checked:        1
clean complete assignments:     0
nodes visited:                  362,556
dead ends:                      97,419
vertex-circle prunes:           181,302
self-edge prunes:               82,444
strict-cycle prunes:            98,858
maximum search depth reached:   7
```

The first recorded obstruction is a self-edge after four rows:

```text
0 -> {1,2,3,4,5}
6 -> {0,1,7,9}
7 -> {0,2,6,8}
8 -> {3,6,7,9}
```

At row `7`, the witness order is `[8,0,2,6]`; the outer chord `[6,8]`
strictly contains the inner chord `[0,6]`, and the selected-distance quotient
has already identified those two ordinary pair distances.

## Consequence

Within the four/five support abstraction, adding the rich vertex-circle
quotient closes the `q=1` layer. Combined with the existing `q=2` rich
vertex-circle closure and the existing support-capacity closure for
`q=3,...,7`, any `n=10` support assignment surviving these filters must be
all-exact-four at this abstraction level:

```text
q = 0 only.
```

Equivalently, this support-plus-quotient layer says that any surviving
four/five rich-support abstraction has ten exact-four-only centers. The checker
itself exhausts exactly the `q=1` layer; the `q=2` and `q=3,...,7` parts of the
combined consequence remain the earlier artifacts.

## Scope warnings

- This is a necessary support/quotient diagnostic only.
- It does not replay turn inequalities, Kalmanson certificates, or Euclidean
  realizability.
- It leaves the `q=0` exact-four case to stronger finite-case or local-lemma
  filters.
- It does not prove `n=10`, does not prove Erdos Problem #97, and does not
  provide a counterexample.
