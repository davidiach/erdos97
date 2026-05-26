# n=12 all-five-rich determinant obstruction

Status: `LEMMA` / exact support-level obstruction. This note does not claim a
general proof of Erdos Problem #97, does not prove the full `n=12` case, and
does not claim a counterexample.

The support-saturation obstruction in
`docs/support-saturation-obstruction.md` already rules out the all-five-rich
`n=12` equality wall. This note records an independent determinant obstruction
for the same support-level boundary; it is useful as a separate algebraic
certificate, not as a stronger global status claim.

## Setup

Let `V` be the vertex set of a strictly convex 12-gon in cyclic hull order. For
each center `i`, suppose there is a same-radius support of size at least five.
Choose one five-element subset

```text
R_i subset V \ {i}
```

from such a support at every center.

The rich-support counting lemma gives

```text
sum_i binom(|R_i|, 2) <= n(n - 2).
```

For `n = 12` and `|R_i| = 5`, this is tight:

```text
12 * binom(5, 2) = 120 = 12 * (12 - 2).
```

Because the proof of the counting lemma is a pointwise capacity count over
witness pairs, equality forces every capacity to be saturated:

- every hull-edge witness pair occurs in exactly one chosen support;
- every non-edge witness pair occurs in exactly two chosen supports.

## Determinant obstruction

Let `A` be the `12 x 12` incidence matrix with

```text
A[i,j] = 1  iff  j in R_i.
```

The diagonal of `A` is zero and every row has sum `5`. By the saturated pair
count above, the off-diagonal entries of the column Gram matrix `A^T A` are
forced:

```text
(A^T A)[a,b] = 1  if {a,b} is a hull edge,
(A^T A)[a,b] = 2  otherwise.
```

The diagonal entries are also forced. Fix a column `a`. The total saturated
capacity of witness pairs containing `a` is

```text
2 * 1 + 9 * 2 = 20.
```

Every occurrence of `a` in a chosen five-support contributes four such pairs,
so column `a` occurs `20 / 4 = 5` times. Thus `A^T A = G`, where `G` has
first row

```text
[5, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1].
```

An exact determinant calculation gives

```text
det(G) = 2,592,000 = 2^8 * 3^4 * 5^3 = 720^2 * 5.
```

This is not a perfect square. But if an integer incidence matrix `A` existed,
then

```text
det(G) = det(A^T A) = det(A)^2,
```

which must be a perfect square integer. Contradiction.

## Consequence

There is no strictly convex 12-gon in which every vertex has five equidistant
witnesses.

Equivalently, any hypothetical 4-bad convex 12-gon must have at least one
exact-four center. This independently closes the first size-five equality wall
left by the edge-sensitive pair count alone: that count allowed the
all-five-rich `n=12` case by equality, but the saturated incidence matrix has
nonsquare determinant. The conclusion is redundant with the support-saturation
obstruction, which rules out the same equality wall by geometric turn-cover
bookkeeping.

This is only a support-level obstruction. It does not handle mixed exact-four /
size-five catalogues, prove `n=12`, prove `n=9`, `n=10`, or `n=11`, or prove
Erdos Problem #97.

## Verification command

```bash
python scripts/check_n12_rich_support_determinant.py --check --json
```

The checker uses exact integer arithmetic and verifies the equality budget,
forced column sums, forced Gram first row, determinant factorization, and
nonsquare determinant obstruction.
