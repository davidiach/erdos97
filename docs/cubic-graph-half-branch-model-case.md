# Cubic-Graph Half-Branch Model Case

Status: `LEMMA` / `FAILED_SEARCH_FAMILY`.

This note records a restricted exact obstruction obtained by prescribing four
roots of a distance fiber and retaining the quadratic cofactor. It does not
prove Erdos Problem #97, does not produce a counterexample, and does not
change the repository source-of-truth status.

## Statement

Let

```text
f(x) = A*x^3 + B*x^2 + C*x + D,  A != 0,
```

and let `xi = -B/(3*A)` be its inflection abscissa. Suppose `T` is a finite
set of distinct real parameters contained in either closed half-line

```text
T subset [xi, +infinity)  or  T subset (-infinity, xi].
```

Then the point whose parameter is farthest from `xi` has at most three other
sampled points at any one Euclidean distance on the graph of `f`.
Consequently, no such one-sided finite sample can be a counterexample to
Erdos Problem #97.

The statement includes the case in which the inflection point itself is
sampled.

## Euclidean Normalization

Translate the inflection point to the origin. Since

```text
f(xi + t) - f(xi) = A*t^3 + f'(xi)*t,
```

the translated graph has the form

```text
gamma(t) = (t, a*t^3 + b*t),  a != 0.
```

These are Euclidean translations, not general affine changes, so they
preserve distances. If all translated parameters are nonpositive, a
180-degree rotation sends them to the same normal form with nonnegative
parameters. It is therefore enough to consider a finite set

```text
T subset [0, +infinity).
```

## Marked-Cofactor Proof

Let `s = max T`. Suppose for contradiction that four distinct parameters

```text
q1, q2, q3, q4 in T \ {s}
```

give points at one common squared distance `rho` from `gamma(s)`. Then
`0 <= qk < s` and `rho > 0`.

Put

```text
mu = b/a,  kappa = 1/a^2 > 0.
```

After division by `a^2`, the monic distance fiber is

```text
P(t) = (||gamma(t) - gamma(s)||^2 - rho)/a^2
     = (t-s)^2 * ((t^2 + s*t + s^2 + mu)^2 + kappa)
       - rho/a^2.
```

The coefficients needed below are

```text
P(t) = t^6
       + 2*mu*t^4
       - 2*s*(s^2 + mu)*t^3
       + (mu^2 + kappa)*t^2
       - 2*s*(mu*(s^2 + mu) + kappa)*t
       + constant.
```

In particular, the `t^5` coefficient is zero and the `t^2` coefficient is
strictly positive.

Mark the four witness roots by writing

```text
Q(t) = product_k (t-qk)
     = t^4 - e1*t^3 + e2*t^2 - e3*t + e4,
```

where `e1,e2,e3,e4` are the elementary symmetric functions of the `qk`.
The roots are distinct, so `Q` divides `P`. Both polynomials are monic, hence

```text
P(t) = Q(t) * (t^2 + u*t + nu)
```

for real `u,nu`. Comparing the `t^5` coefficients gives `u=e1`.

Now evaluate the factorization at the center. Since every `qk<s`,

```text
Q(s) = product_k (s-qk) > 0,
```

whereas `P(s)=-rho/a^2<0`. Therefore

```text
s^2 + e1*s + nu < 0.
```

Here `s>0` and `e1>0`, so `nu<0`.

The `t^2` coefficient of the factorization gives the exact identity

```text
mu^2 + kappa = nu*e2 - e1*e3 + e4.
```

Four distinct nonnegative witness parameters imply `e2>0` and
`e1*e3>e4`. If one witness is zero, then `e4=0` while `e1,e3>0`. If all are
positive, the expansion of `e1*e3` contains `4*e4` and additional positive
terms. Thus

```text
nu*e2 - e1*e3 + e4 < 0.
```

This contradicts `mu^2+kappa>0`. Hence no radius centered at `gamma(s)` can
contain four other sampled points.

## Convexity Check

On the normalized half-line,

```text
(a*t^3 + b*t)' = 3*a*t^2 + b.
```

This derivative is strictly monotone on `[0,+infinity)`: increasing when
`a>0` and decreasing when `a<0`. The graph is therefore strictly convex or
strictly concave on the closed half-branch, even though its second derivative
vanishes at the endpoint `t=0`. Every finite set of distinct samples lies on
one strict boundary chain of its convex hull, so all sampled points are
vertices and no three are collinear.

## Degree-Four Boundary

Companion status: `EXACT_NEGATIVE_CONTROL` / one rich row only.

The endpoint conclusion does not extend to arbitrary strictly convex quartic
graphs. An exact negative control is

```text
g(t) = (3/5)*t + (3/10)*t^2 - t^3 + (13/10)*t^4.
```

Its second derivative is

```text
g''(t) = (78/5)*t^2 - 6*t + 3/5.
```

The leading coefficient is positive and the discriminant is `-36/25`, so
`g''(t)>0` for every real `t`. Thus the graph is globally strictly convex.

For `Gamma(t)=(t,g(t))`, the center `Gamma(-1)=(-1,2)`, and squared radius
`5`, clearing denominators from the distance fiber gives

```text
100*(||Gamma(t)-Gamma(-1)||^2 - 5)
  = 169*t^8 - 260*t^7 + 178*t^6 + 96*t^5
    - 631*t^4 + 436*t^3 + 16*t^2 - 40*t.
```

An exact Sturm count has variation `6` at `-1` and variation `2` at `1`, so
this polynomial has exactly four distinct roots in `(-1,1)`. They are
isolated by

```text
(-3/10,-1/4),  {0},  (2/5,1/2),  (7/10,4/5),
```

with one root in each listed interval or singleton. Hence one endpoint of a
strictly convex quartic arc can have four other arc points on a common circle.
This supplies only one rich row. It is not a finite branch closure, not a
counterexample, and not evidence that the other four points have rich rows.
It shows that degree four is a genuinely nontrivial next target for a
marked-root closure search.

## Why the Marked Roots Matter

The useful mechanism is not a local-rank or injectivity claim. The four desired
witnesses are installed first as roots of `Q`, and the degree-six distance
fiber is allowed to retain its hidden quadratic cofactor. Evaluating that
cofactor at the center forces its constant term negative, while a different
coefficient comparison forces the same expression positive. This is the
root-first design principle suggested by the constant-Jacobian example, used
here as an exact obstruction rather than as an analogy-based conclusion.

## Scope

This lemma rules out polynomial cubic graphs, and their rigid-motion images,
only when all sampled parameters lie on one closed side of the inflection. It
does not cover samples using both sides, arbitrary implicit or parametrically
cubic curves, multi-arc constructions, or general strictly convex polygons.
