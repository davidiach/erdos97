# Prompt 2 local output: affine-circuit rank rigidity

Status: reformulation and obstruction classification only. No rank-rigidity
proof or geometric counterexample is claimed.

Let L(P) be the selected four-cohort affine-circuit matrix. The unavoidable
kernel contains

```text
1, x, y, q=x^2+y^2.
```

The question is whether, in the non-concyclic case, these are the only kernel
vectors.

## Equivalent lifting formulation

For any vector h=(h_1,...,h_n), the row equation

```text
Delta_bcd h_a - Delta_acd h_b + Delta_abd h_c - Delta_abc h_d = 0
```

is exactly the condition that the four lifted points

```text
(x_a,y_a,h_a), (x_b,y_b,h_b), (x_c,y_c,h_c), (x_d,y_d,h_d)
```

are coplanar in R^3. Thus

```text
h in ker L(P)
```

if and only if h is a height assignment for which every selected four-cohort is
coplanar after lifting.

The four unavoidable height functions correspond to the plane liftings
1,x,y and the paraboloid lifting q=x^2+y^2. The reason q works is special:
on a circle centered at p_i=(alpha,beta), the equation

```text
x^2+y^2 = 2 alpha x + 2 beta y + (r_i^2-alpha^2-beta^2)
```

is affine in x,y.

Therefore an exotic kernel vector is exactly an exotic lifting that makes every
selected four-cohort coplanar without being a global affine-plus-paraboloid
height function.

## Why the rank claim needs extra hypotheses

The rank statement cannot plausibly be attacked from geometry alone without
also controlling the selected support pattern. The matrix L(P) has no entries
in a column j unless vertex j appears in at least one selected four-cohort. If a
column were unused, then the coordinate vector e_j would lie in ker L(P), giving
an immediate extra kernel direction unrelated to concyclicity.

More generally, if the selected four-cohort support hypergraph decomposes into
two column sets that are never linked by a row, then piecewise unavoidable
height functions produce additional kernel vectors. This is a combinatorial
rank-defect mechanism, not a metric one.

Thus a corrected rigidity target must include at least:

1. column coverage;
2. no support decomposition into independent column components;
3. enough overlapping four-cohorts to make the affine-circuit matroid connected;
4. a rank certificate for the actual Delta-weighted matrix, not merely for the
   unweighted support pattern.

## Classification of exotic syzygies

Every exotic syzygy falls into one of the following linear-algebraic mechanisms.

1. Uncovered-column syzygy. Some vertex never appears in any selected cohort.
   Then its height is unconstrained.

2. Component syzygy. The selected four-cohort hypergraph splits into column
   components. Each component can carry its own affine-plus-paraboloid height
   assignment, producing extra global kernel dimensions.

3. Hinge syzygy. A small separator T of vertices is the only overlap between two
   large groups of rows. If the separator does not force the affine and
   paraboloid pieces to agree across the groups, a piecewise lifting survives.

4. Metric cancellation syzygy. The support pattern is connected, but the signed
   Delta coefficients satisfy a special algebraic dependency. This is the truly
   geometric case: it must be detected by computing rank over the coordinate
   field or by an exact symbolic certificate.

## Strongest output

The substantive rank rigidity lemma is best restated as a certificate problem:

For each selected four-cohort pattern that survives the combinatorial filters,
form L(P) with exact signed-area coefficients. Prove that

```text
ker L(P) / span{1,x,y,x^2+y^2} = 0
```

by an exact rank certificate, or else extract a nonzero exotic lifting h and
classify it by the mechanisms above.

This run did not prove that the quotient kernel vanishes in general. It
identifies the missing object as an affine-circuit rigidity certificate for
the selected support pattern.
