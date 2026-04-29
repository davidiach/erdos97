# Prompt 2 Run 01 Audit

Status: heuristic/audit note. This file records local review of an AI-generated
prompt result. It is not a proof of Erdos Problem #97 and does not claim a
counterexample.

## Verdict

This is a useful algebraic reduction.

The main quotient statement is correct: for a non-concyclic configuration, the
unavoidable kernel `U = span{1,x,y,x^2+y^2}` can be split off by choosing any
four-point lifted base with nonsingular `Z_B`. Exotic syzygies are then exactly
the kernel of the remaining-column matrix.

The weighted two-core peeling is also correct as a linear-algebra reduction:
singleton rows force active coordinates to vanish, so peeling preserves the
kernel.

What it does not do:

- it does not prove rank rigidity;
- it does not rule out exotic syzygies;
- it does not give a base-independent combinatorial obstruction without the
  signed-area weights.

This is worth keeping as guidance for the affine-circuit/rank-rigidity path,
especially as a specification for a future checker.

## Checked Claims

### Lifted Rank-Four Setup

For each vertex, set

`z_j = (1, x_j, y_j, x_j^2 + y_j^2)`.

For a selected four-cohort `C_i={a,b,c,d}`, the signed-area coefficients

```text
Delta_bcd, -Delta_acd, Delta_abd, -Delta_abc
```

give the unique affine dependence among the four planar points, up to scalar.
Since the cohort lies on a circle centered at `p_i`, the quadratic coordinate
`q=x^2+y^2` is affine on that cohort:

```text
q_j = 2 p_i dot p_j + (r_i^2 - |p_i|^2).
```

Therefore the corresponding row of `L` annihilates the four columns
`1,x,y,q`, so `LZ=0`.

If the whole point set is not concyclic, then `rank Z=4`. More precisely,
`rank Z <= 3` would give a nontrivial relation

```text
alpha + beta x + gamma y + delta (x^2+y^2) = 0
```

on all vertices. If `delta != 0`, all vertices lie on one circle; if
`delta = 0`, all vertices lie on one line, impossible for a strict convex
polygon with the sizes considered here.

### Quotient Reduction

Choose `B` with `det Z_B != 0` and let `N=[n]\B`.

The evaluation map `U -> R^B` is an isomorphism. Hence every `h in R^n` has a
unique decomposition

```text
h = u + g,
```

where `u in U` and `g` vanishes on `B`.

Because `U subset ker L`,

```text
h in ker L iff g in ker L.
```

Thus

```text
ker L / U is isomorphic to ker L_N
```

and

```text
dim ker L = 4 + dim ker L_N.
```

This was also checked with a small exact rational linear-algebra script using
random matrices satisfying `LU=0`.

The phrase "for one equivalently every base" is acceptable only with this
qualification: the base must satisfy `det Z_B != 0`. For such bases, the
dimension `dim ker L_N` is independent of the base because it equals
`dim ker L - 4`.

### Weighted Two-Core Peeling

For a current active column set `S`, if a row meets `S` in a singleton `{v}`,
then the row equation forces

```text
lambda_v g_v = 0.
```

Strict convexity gives no three cohort points collinear, so all signed-area
coefficients in a selected four-cohort are nonzero. Therefore `g_v=0`, and
`v` can be deleted from the active support.

Iterating this process produces the unique maximal active subset `S_B` for
which every row meets `S_B` in either `0` or at least `2` vertices. Kernel
dimension is preserved by extending core solutions by zero on peeled columns:

```text
ker L_N is isomorphic to ker A_B.
```

This was also checked locally on random sparse exact matrices.

### Obstruction Components

The component decomposition of the incidence graph is standard block-diagonal
linear algebra:

```text
dim ker L = 4 + sum_nu (|S_nu| - rank A_nu).
```

The three listed obstruction types are valid for a fixed base and fixed chosen
cohort system:

1. An unused column outside the base is a zero column of `L_N`, hence an exotic
   quotient vector.
2. A pair-row-only component is a gain graph. A connected component has a
   nonzero solution exactly when every cycle has gain product `1`; a tree
   component automatically contributes one degree of freedom.
3. A component with rows of size `3` or `4` is controlled exactly by the
   maximal minors of its weighted coefficient matrix.

Nuance for Pattern I: "unused column" is base-dependent in the quotient
description. The immediate obstruction is an unused vertex that lies outside
the chosen base `B`.

## Repository Value

Worth keeping:

- the quotient reduction as a precise formulation of exotic syzygies;
- the weighted two-core as a future checker target;
- the pair-row gain-cycle criterion as a concrete rank-defect mechanism.

Not worth claiming:

- a proof that `ker L=U`;
- a proof that all two-cores have full rank;
- a weight-free combinatorial obstruction.

Recommended next artifact:

Implement a small checker that, for a selected witness pattern and symbolic or
numeric coordinates, builds the affine-circuit matrix `L`, chooses valid lifted
bases `B`, computes the weighted two-core, and reports pair-row gain cycles and
rank-defective hypercore components.

## Run 02 Continuation: Minimal Certificates

The continuation in `run-02.md` refines the weighted two-core obstruction into
a minimal-support circuit certificate. This refinement is mathematically sound
with a few wording cautions.

### What Is Correct

Fix a valid lifted base `B` and write `N=[n]\B`. If `ker L_N` is nonzero, take
a nonzero kernel vector `g` with minimal support `S`.

Then:

- no row can meet `S` in exactly one active vertex, because the corresponding
  nonzero signed-area coefficient would force that coordinate of `g` to vanish;
- the active matrix `A_S` has one-dimensional kernel;
- equivalently, `rank A_S = |S|-1`;
- one may choose `|S|-1` active rows `T` forming a row basis;
- the usual cofactor vector of `A_{T,S}` spans the nullspace;
- every remaining active row must satisfy the corresponding cofactor
  determinant identity.

Conversely, any such cofactor certificate gives a nonzero vector in `ker L_N`,
hence an exotic class in `ker L/U`.

A small exact rational sanity check over random sparse matrices found the
expected behavior: every nonzero kernel contained a minimal-support certificate
of this form.

### Wording Cautions

The statement "every exotic syzygy is exactly one of these finite cofactor
certificates" should be read as:

> every nonzero exotic quotient contains a minimal-support representative
> producing one such certificate, and every such certificate yields an exotic
> quotient vector.

If `ker L_N` has dimension greater than one, a general exotic vector can be a
linear combination of several circuit vectors and need not itself be a single
minimal certificate.

The phrase "for one, equivalently every, base" is valid only after restricting
to bases `B` with `det Z_B != 0`. Under that restriction, the quotient
dimension is base-independent:

`dim ker L_N = dim ker L - 4`.

Pattern I is likewise quotient-base dependent: the immediate zero-column
certificate is an unused vertex lying outside the chosen base `B`.

### Pair-Gain Components

The gain-graph interpretation is correct for components whose active rows all
meet the support in exactly two vertices.

For a connected pair-gain component:

- if the component is a tree, it contributes one degree of freedom;
- if it has cycles, it contributes one degree of freedom exactly when all cycle
  gain products are `1`;
- if any cycle is unbalanced, that connected pair component has no nonzero
  all-active solution.

So "a cycle contributes one degree of freedom" should be understood at the
connected-component level, not one independent degree for every balanced cycle.

### Mixed Hypercore Components

The proposed contraction of balanced pair-gain components is a valid way to
compress the pair equations before applying the same cofactor-circuit test to
the remaining hyperrows.

This is best treated as an implementation plan:

1. compute pair-equation connected components;
2. reject supports containing unbalanced pair cycles;
3. contract balanced pair components to component parameters;
4. run the cofactor/minor certificate test on the contracted active matrix.

### Repository Value

This continuation makes Prompt 2 more useful, not more conclusive. It turns
the rank-rigidity question into an explicit finite certificate search:

- isolated quotient columns;
- balanced pair-gain components;
- mixed hypercore cofactor identities.

That is a good target for a future script, but it remains a classification of
possible defects rather than a proof that no defects occur.
