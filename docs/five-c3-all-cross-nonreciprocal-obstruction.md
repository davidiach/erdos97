# Five-orbit all-cross nonreciprocal obstruction

Status: `LEMMA` draft / exact restricted-pattern obstruction (review pending).

This note closes the strongest all-cross continuation left by
`docs/five-c3-tournament-obstruction.md`: every one of five orbit rows uses
four cross-orbit singletons, and every mutual gain-pair is nonreciprocal.  It
does not close all all-cross systems, because a reciprocal mutual gain-pair
requires a different argument.

## Statement

Let `omega = exp(2*pi*I/3)`.  For five nonzero complex numbers `z_i`, define

```text
T_i = {z_i, omega*z_i, omega^2*z_i},  i=0,...,4.
```

Assume the five orbits are pairwise distinct and no two are half-step
partners:

```text
arg(z_j)-arg(z_i) != pi/3  (mod 2*pi/3).
```

At the representative `z_i`, suppose a selected four-tie consists of one
point from each other orbit.  Thus there are gains `g_ij in Z/3Z` and a
positive squared row radius `R_i` such that

```text
abs(z_i - omega^g_ij*z_j)^2 = R_i,  j != i.    (1)
```

Assume every unordered pair is nonreciprocal:

```text
g_ij + g_ji != 0  (mod 3),  i != j.            (2)
```

Then the ten orbits-and-rows conditions (1)-(2) are impossible.

Condition (2) is independent of the choice of representative in each orbit.
Replacing `z_i` by `omega^h_i*z_i` changes `g_ij` by `h_i-h_j`, so the mutual
sum is unchanged.  The result is metric and does not use convexity once
pairwise distinctness and the no-half-step assumption are stated.

## Pair reduction

Put

```text
U_i = abs(z_i)^2
```

and fix an unordered pair `{i,j}`.  Write

```text
w = omega^g_ij*z_j*conj(z_i),
A = Re(w)                    = (U_i+U_j-R_i)/2,
C = Re(omega^(g_ij+g_ji)*conj(w))
                              = (U_i+U_j-R_j)/2.
```

If the mutual gain sum is `1`, writing `w=A+I*B` gives

```text
B = (2*C+A)/sqrt(3).
```

For gain sum `2`, the sign of `B` is reversed.  In either case,
`abs(w)^2=U_i*U_j` reduces exactly to

```text
F_ij = 3*(U_i^2+U_i*U_j+U_j^2)
       - 3*(U_i+U_j)*(R_i+R_j)
       + R_i^2+R_i*R_j+R_j^2
     = 0.                                           (3)
```

Thus all `2^10` assignments of nonzero mutual gain sums have the same radial
equations.  No enumeration is needed.

## Four-dimensional orthogonality

Define

```text
q_i = 3*U_i^2 - 3*U_i*R_i + R_i^2,
W_i = (U_i, R_i, q_i, 1).
```

On four-dimensional real space use the symmetric bilinear form with matrix

```text
J = [ 3 -3  0  0 ]
    [-3  1  0  0 ]
    [ 0  0  0  1 ]
    [ 0  0  1  0 ].
```

Its two diagonal blocks have negative determinant, so `J` is nondegenerate
of signature `(2,2)`.  Direct expansion gives

```text
<W_i,W_j>_J = F_ij,                               (4)
<W_i,W_i>_J = 3*(R_i-U_i)*(R_i-3*U_i).           (5)
```

Equations (2)-(4) make the five nonzero vectors `W_i` pairwise orthogonal in
a four-dimensional nondegenerate space.

At least one `W_i` must be isotropic, since the diagonal Gram determinant is
the product of the five values in (5), while its rank is at most four.  In
fact at least two must be isotropic.  If exactly one were isotropic, the
other four nonisotropic orthogonal vectors would be a basis, leaving no
nonzero vector orthogonal to all four.

If exactly two are isotropic, the other three span a nondegenerate
three-space.  Its orthogonal complement is one-dimensional, so the two
isotropic vectors are proportional.  Their last coordinates are both one,
and hence they are equal.

If at least three are isotropic, their span is totally isotropic and has
dimension at most two in signature `(2,2)`.  More concretely, (5) puts every
isotropic vector in one of the two types

```text
R_i = U_i  or  R_i = 3*U_i.                     (6)
```

Two of at least three have the same type.  For a same-type pair, (3)
factorizes as

```text
F_ij = (U_i-U_j)^2       when R_k=U_k,
F_ij = 3*(U_i-U_j)^2     when R_k=3*U_k.
```

Thus those two vectors are again equal.  In every case there are distinct
indices `i,j` with

```text
U_i=U_j=U,
R_i=R_j=U                 or
R_i=R_j=3*U.                                      (7)
```

## Geometric contradiction at the exceptional pair

For the selected `i -> j` witness, divide `w` by `U`.  It has modulus one,
and (1) and (7) give

```text
Re(w/U) = 1/2   when R_i=U,
Re(w/U) = -1/2  when R_i=3*U.
```

In the first case the phase difference is `pi/3 modulo 2*pi/3`: the two
orbits are half-step partners, contrary to the hypothesis.  In the second
case the phase difference is zero modulo `2*pi/3`; equal `U` then makes the
two orbits identical, contrary to pairwise distinctness.  This proves the
statement.

## Exact replay

The companion checker verifies both nonzero gain-sum eliminations, the
bilinear representation and signature, the diagonal factorization, and the
two exceptional same-type factorizations:

```bash
python scripts/check_five_c3_all_cross_nonreciprocal_obstruction.py \
  --assert-expected --json
```

The checker is an exact algebra replay, not a numerical feasibility search.

## Scope boundary

This note requires all ten mutual gain sums to be nonzero.  It leaves open
an all-cross system with even one reciprocal pair
`g_ij+g_ji=0 modulo 3`.  It also leaves open mixed systems in which some
orbit rows use their own equilateral pair, half-step orbit pairs, partial
orbits, different rotation centers, and arbitrary strictly convex polygons.
