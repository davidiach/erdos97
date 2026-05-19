# Hyperbola Branch Model Case

Status: `LEMMA` / `FAILED_SEARCH_FAMILY`.

This note records a restricted exact obstruction. It does not prove Erdos
Problem #97, does not produce a counterexample, and does not change the
repository source-of-truth status. It only rules out finite vertex sets lying
on one branch of a Euclidean hyperbola.

## Statement

Let `T` be a finite set of distinct real parameters on one branch of a
nondegenerate Euclidean hyperbola. After a Euclidean motion, write the branch
as

```text
p(s) = (a*cosh(s), b*sinh(s)),  a,b > 0.
```

Then the corresponding finite point set cannot be a counterexample to Erdos
Problem #97.

## Proof

Fix a center parameter `sigma` and put

```text
A = a^2,  B = b^2,
C = cosh(sigma),  S = sinh(sigma).
```

The squared distance from `p(sigma)` to `p(s)` is

```text
D_sigma(s) =
  A*(cosh(s) - C)^2
  + B*(sinh(s) - S)^2.
```

Write `z = exp(s)` and `w = exp(sigma)`. The equation
`D_sigma(s) = rho` becomes, after multiplying by `z^2`, a quartic

```text
((A+B)/4) z^4
- (A*C + B*S) z^3
+ K z^2
- (A*C - B*S) z
+ ((A+B)/4)
= 0,
```

where the middle coefficient `K` depends on `rho` and `sigma` but is not
needed.

Suppose four distinct witness parameters `s1,s2,s3,s4` are all at the same
positive distance from `p(sigma)`, and write `zk = exp(sk)`. These four `zk`
are the four roots of the quartic. Vieta's formula gives

```text
sum_k zk = 4*(A*C + B*S)/(A+B).
```

Because the constant and leading coefficients are equal, the product of the
roots is `1`; hence the sum of reciprocal roots is the third elementary
symmetric sum. Vieta's formula for the linear coefficient gives

```text
sum_k zk^(-1) = 4*(A*C - B*S)/(A+B).
```

Adding and dividing by `2` yields

```text
sum_k cosh(sk) = 4*A*C/(A+B),
```

or equivalently

```text
(1/4) * sum_k cosh(sk) = (a^2/(a^2 + b^2))*cosh(sigma).
```

The multiplier `a^2/(a^2+b^2)` is strictly less than `1`.

Now let `T` be the finite parameter set of an alleged counterexample. Choose
`sigma in T` minimizing `cosh(sigma)`. Every witness parameter `sk in T` has
`cosh(sk) >= cosh(sigma)`, so the average of four witness `cosh` values is at
least `cosh(sigma)`. The displayed identity says the same average is strictly
less than `cosh(sigma)`, a contradiction.

Thus no finite point set on one hyperbola branch can be a counterexample.

## Convexity Check

The right branch can be written as the graph

```text
x = a*sqrt(1 + (y/b)^2).
```

This is a strictly convex function of `y`. Therefore any finite set of
distinct points on the branch, listed by increasing `y` or equivalently by
increasing `s`, is in strictly convex position: the polygonal chain through
the sampled points is a strict boundary chain of the convex hull.

## Scope

This obstruction is useful as a negative control for one-branch hyperbolic
construction attempts. It is not a bridge to the full problem. It does not
cover point sets using both branches of a hyperbola, and it does not imply
that arbitrary strictly convex polygons reduce to hyperbolic configurations.
