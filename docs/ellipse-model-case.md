# Ellipse Model Case

Status: `LEMMA` / `FAILED_SEARCH_FAMILY`.

This note records a restricted exact obstruction. It does not prove Erdos
Problem #97, does not produce a counterexample, and does not change the
repository source-of-truth status. It only rules out finite vertex sets lying
on one Euclidean ellipse.

## Statement

Let `T` be a finite set of distinct parameters on a nondegenerate Euclidean
ellipse. Then the corresponding finite point set cannot be a counterexample to
Erdos Problem #97.

The circle case is included separately: if all points lie on one circle, then a
circle centered at any one vertex intersects the common circumcircle in at most
two other points.

## Proof

Euclidean motions and uniform scaling preserve centered equal-distance
relations, so a noncircular ellipse may be written as

```text
p(t) = (a*cos(t), b*sin(t)),  a > b > 0.
```

Put `lambda = a^2/b^2 > 1`. After dividing squared distances by `b^2`, the
squared distance from the center parameter `tau` to parameter `t` is

```text
D_tau(t) =
  lambda*(cos(t) - cos(tau))^2
  + (sin(t) - sin(tau))^2.
```

Suppose four distinct witness parameters `t1,t2,t3,t4` are all at the same
positive distance from `p(tau)`. Write `z = exp(i*t)`. The equation
`D_tau(t) = rho` becomes, after multiplying by `z^2`, a quartic of the form

```text
((lambda - 1)/4) z^4
+ (-lambda*cos(tau) + i*sin(tau)) z^3
+ C z^2
+ (-lambda*cos(tau) - i*sin(tau)) z
+ ((lambda - 1)/4)
= 0,
```

where the middle coefficient `C` depends on `rho` and `tau` but is not needed.
The four witness values `zk = exp(i*tk)` are the four roots of this quartic.
By Vieta's formula,

```text
sum_k zk = 4*(lambda*cos(tau) - i*sin(tau))/(lambda - 1).
```

Taking real parts gives

```text
(1/4) * sum_k cos(tk) = (lambda/(lambda - 1))*cos(tau).
```

Now let `T` be the finite parameter set of an alleged counterexample. If some
point has positive cosine, choose `tau in T` with `cos(tau)` maximal and write
`M = cos(tau) > 0`. Every witness has cosine at most `M`, so the average of the
four witness cosines is at most `M`. The displayed identity says the average is
`lambda*M/(lambda - 1)`, which is strictly larger than `M`, a contradiction.

If no point has positive cosine and `T` has at least three points, then the
minimum cosine value `m` is negative. Choose `tau in T` with `cos(tau)=m`.
Every witness has cosine at least `m`, so the average of the four witness
cosines is at least `m`. The identity says the average is
`lambda*m/(lambda - 1)`, which is strictly smaller than `m`, again a
contradiction. If all cosine values are zero, there are at most two distinct
ellipse points, so the set cannot be a counterexample anyway.

Thus no finite point set on a noncircular ellipse can be a counterexample. The
circle case was handled above.

## Convexity Check

An ellipse is the boundary of a strictly convex body. Any finite set of
distinct points on it, listed in cyclic order, is therefore in strictly convex
position: each listed point is an extreme point and no three listed points are
collinear.

## Scope

This obstruction is useful as a negative control for circular and elliptical
construction attempts, including affine-regular polygons that still lie on one
Euclidean ellipse. It is not a bridge to the full problem. A general strictly
convex polygon need not lie on an ellipse, and arbitrary affine or projective
transformations do not preserve Euclidean centered equal-distance relations.
