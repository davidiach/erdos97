# Two-full-cap intersection lemma

Status: `REVIEW_PENDING_LEMMA_PACKET`.

This note supplements `docs/rigid-n15-moser-geometry.md`.  It gives an exact
geometric obstruction that becomes available when two adjacent rigid caps are
full side-length circles.

It does not prove Erdős Problem 97 and does not by itself contradict the
remaining rigid `n=15` cover counts.

## 1. Setting

Let `A,B,C` be an equilateral triangle of side length `s`, promoted as the
non-obtuse MEC/Moser triangle of a strictly convex carrier `P`.  Suppose

```text
C_A subset circle(A,s),
C_B subset circle(B,s),
```

where `C_A` is the closed cap from `B` to `C` opposite `A` and `C_B` is the
closed cap from `C` to `A` opposite `B`.

MEC containment and the cap-side condition put the interior vertices of these
caps on the minor `60`-degree arcs

```text
Gamma_A = minor arc BC of circle(A,s),
Gamma_B = minor arc CA of circle(B,s).
```

The two circles meet at `C` and at the opposite equilateral point outside the
MEC disk.  Hence the carrier caps meet only at `C`.

## 2. Lemma

### Two adjacent full arcs cannot both be cut twice

Let `p` be a carrier vertex distinct from `A,B,C`, and let `Omega` be any
positive-radius circle centered at `p`.  Then it is impossible that

```text
|Omega cap Gamma_A| >= 2
and
|Omega cap Gamma_B| >= 2.
```

Here intersections are sets of distinct geometric points; the statement is
stronger than the corresponding finite-carrier assertion.

### Proof

Assume `Omega` meets `Gamma_A` at two distinct points `x_1,x_2`.

Both `A` and `p` are equidistant from `x_1,x_2`.  Therefore the line `Ap` is
the perpendicular bisector of chord `x_1x_2`.  The midpoint of a chord whose
endpoints lie in the open minor arc `BC` lies on a ray from `A` inside the
closed `60`-degree cone

```text
K_A = cone_A(AB,AC).
```

Thus the unoriented line `Ap` has one ray in `K_A` and its opposite ray in
`-K_A`.

The opposite ray contains no point of the MEC disk except `A`.  Indeed every
unit direction `u` in `K_A` points strictly into the disk at the boundary point
`A`, so `(O-A).u>0`, where `O` is the MEC center.  For `t>0`, the point on the
opposite ray is `A-tu`, and

```text
|A-tu-O|^2
 = |A-O|^2 - 2t(A-O).u + t^2
 > |A-O|^2.
```

It is outside the MEC disk.  Since every carrier point lies in that disk and
`p!=A`, we conclude

```text
p in K_A.
```

Applying the same argument to the two intersections with `Gamma_B` gives

```text
p in K_B = cone_B(BC,BA).
```

The intersection of these two inward vertex cones is exactly the closed
triangle:

```text
K_A cap K_B = conv{A,B,C}.
```

Hence `p` lies in the convex hull of three other carrier vertices.  This
contradicts convex independence.  ∎

The same proof covers endpoint intersections by a limiting argument, or by
using closed cones throughout.  A carrier center equal to an apex is excluded
explicitly in the statement; in the tri-apex residual the Moser apices are
also deletion-robust and therefore are not unique-four centers.

## 3. Exact-four consequence

Let `Q_p` be the exact four-point class of a non-apex unique-four center `p`.
Each of the two full cap circles is distinct from the circle centered at `p`,
so ordinary two-circle intersection gives

```text
|Q_p cap C_A| <= 2,
|Q_p cap C_B| <= 2.
```

If `Q_p` contained four points of `C_A union C_B`, then it would have to contain
exactly two from each cap and could not contain their common endpoint `C`.
That is precisely the forbidden double-two intersection above.  Therefore

```text
|Q_p cap (C_A union C_B)| <= 3.             (1)
```

At rigid `n=15`, two adjacent full caps have union size

```text
|C_A union C_B| = 6+6-1 = 11.
```

Consequently any minimal unique-four cover needs at least four distinct
unique-four centers merely to cover this eleven-point union.

This matches, rather than exceeds, the global lower bound
`ceil(15/4)=4`; hence (1) is a real geometric strengthening but not yet a
terminal contradiction.

## 4. Next coupling target

The equality-near case is now sharply specified.  Four unique-four centers
covering the eleven-point two-cap union have total capacity only twelve under
(1).  Any exact equality or one-overlap pattern forces most classes to have a
`2+1` split across the two full caps, while the four remaining vertices lie in
the third cap interior.

A useful next theorem would classify this near-saturated cover and force either

* a checkerboard Kalmanson core;
* a repeated outside pair at two centers in one ordered cap; or
* a third full cap, entering the Reuleaux exclusion from the companion note.

No such classification is claimed here.
