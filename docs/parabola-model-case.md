# Parabola Model Case

Status: `LEMMA` / `FAILED_SEARCH_FAMILY`.

This note records a restricted exact obstruction. It does not prove Erdos
Problem #97, does not produce a counterexample, and does not change the
repository source-of-truth status. It only rules out one natural algebraic
search family: finite vertex sets lying on one nondegenerate affine parabola.

## Statement

Let

```text
gamma(t) = p0 + u*t + v*t^2
```

where `p0,u,v` are planar vectors and `u,v` are linearly independent. For a
finite set `T` of distinct real parameters, set

```text
P_T = { gamma(t) : t in T }.
```

Then an endpoint parameter of `T` gives a good vertex. More precisely, if
`M = max T`, then `gamma(M)` has at most three other points of `P_T` at any one
positive Euclidean distance. The same holds for `m = min T`.

Consequently no finite point set on a nondegenerate affine parabola can be a
counterexample to Erdos Problem #97.

## Proof

It is enough to prove the claim for the right endpoint `M = max T`. The left
endpoint is identical after reversing the parameter.

For a fixed positive squared radius `rho > 0`, define

```text
F(t) = ||gamma(t) - gamma(M)||^2 - rho.
```

Since

```text
gamma(t) - gamma(M) = u*(t-M) + v*(t^2-M^2),
```

the function `F(t)` is a real polynomial of degree four. Its leading
coefficient is `||v||^2`, which is positive because `v != 0`. Also

```text
F(M) = -rho < 0,
```

while `F(t) -> +infinity` as `t -> +infinity`. By continuity, there is at
least one real root `t_+ > M`.

Now suppose that `gamma(M)` had four other vertices of `P_T` at the same
positive squared distance `rho`. Their parameters would be four distinct
numbers

```text
t1,t2,t3,t4 in T \ {M}.
```

Because `M` is the maximum parameter, all four satisfy `tk < M`. They are four
distinct roots of `F(t)`. Together with the root `t_+ > M`, this gives five
distinct real roots of a degree-four polynomial, impossible.

Thus every positive radius centered at `gamma(M)` contains at most three other
points of `P_T`, so `E(gamma(M)) <= 3`.

## Convexity Check

The curve `gamma(t)` is an invertible affine image of the standard parabola
`(t,t^2)`. Finite sets of distinct points on the standard parabola are in
strictly convex position when ordered by increasing parameter: no three are
collinear, and every listed point is an extreme point of the convex hull.
Invertible affine maps preserve strict convex position. Hence this is a
genuine strictly convex polygon subcase, not only an algebraic point-set
calculation.

## Scope

This obstruction is useful as a negative control for parabolic construction
attempts. It is not a bridge to the full problem. A general strictly convex
polygon need not lie on any affine parabola, and non-Euclidean affine or
projective transformations do not preserve the centered equal-distance
property.

The proof also allows the selected radius to vary with the center. It is not a
common-radius reduction.
