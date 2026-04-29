# Prompt 2 Run 01

The clean rigorous continuation is an exact obstruction theorem. I am **not**
replacing the signed-area coefficients by symmetric ones; the obstruction is
stated in terms of the original `Delta`-coefficients.

## 1. Set up the lifted rank-four configuration

Write

```text
q_j = x_j^2 + y_j^2,
z_j = (1, x_j, y_j, q_j) in R^4,
```

and let `Z` be the `n x 4` matrix with rows `z_j`.

For the row centered at `i`, with chosen cohort `C_i={a,b,c,d}`, define

```text
lambda^i_a = Delta_bcd,
lambda^i_b = -Delta_acd,
lambda^i_c = Delta_abd,
lambda^i_d = -Delta_abc,
```

and `lambda^i_j=0` outside `C_i`. Thus the `i`-th row of `L` is `lambda^i`.

Because `C_i` lies on a circle centered at `p_i`,

```text
q_j = 2 p_i dot p_j + (r_i^2 - |p_i|^2)  for j in C_i,
```

so `q` is affine on `C_i`. Therefore

```text
LZ = 0.
```

If `P` is non-concyclic, then `rank Z = 4`. Indeed, `rank Z <= 3` would mean
that `q=x^2+y^2` is globally affine on `P`, i.e.

```text
x_j^2 + y_j^2 = alpha x_j + beta y_j + gamma
```

for all `j`, which is exactly the equation of one common circle. Thus, in the
non-concyclic case,

```text
U := span{1,x,y,q}
```

is a genuine four-dimensional subspace of `ker L`.

So the substantive lemma is equivalent to proving

```text
ker L = U.
```

Equivalently,

```text
ker L / U = 0.
```

The rest of the answer gives an exact finite obstruction to this quotient being
nonzero.

---

## 2. Exact quotient reduction

Choose any four indices

```text
B={b_1,b_2,b_3,b_4}
```

such that the `4 x 4` matrix `Z_B` is nonsingular. Such a `B` exists because
`rank Z=4`. Let

```text
N=[n]\B.
```

Every vector `h in R^n` has a unique decomposition

```text
h = u + g,
```

where `u in U` and `g_b=0` for every `b in B`. Namely, `u` is the unique
element of `U` agreeing with `h` on `B`.

Since `U subseteq ker L`, we have

```text
h in ker L iff g in ker L.
```

But `g` is supported on `N`. Therefore, if `L_N` denotes the submatrix of `L`
obtained by keeping only the columns indexed by `N`, then

```text
ker L / U is isomorphic to ker L_N.
```

Hence

```text
dim ker L = 4 + dim ker L_N.
```

So the desired rank rigidity lemma is equivalent to:

```text
L_N has full column rank n-4.
```

This is already a sharp reduction: exotic syzygies are exactly nonzero vectors
in `ker L_N`.

---

## 3. Weighted two-core obstruction

Now define a finite peeling process on the column set `N`.

For a current subset `S subseteq N`, let

```text
E_i(S)=C_i cap S.
```

If for some row `i`,

```text
E_i(S)={v}
```

is a singleton, then the `i`-th equation reads

```text
lambda^i_v g_v = 0.
```

Because the polygon is strictly convex, no three cohort points are collinear,
so every signed-area coefficient in a row is nonzero. Hence `lambda^i_v != 0`,
and therefore `g_v=0`. Thus `v` cannot belong to the support of an exotic
kernel vector.

So we may delete `v`. Repeat this deletion until no row meets the remaining
set in exactly one vertex.

Let the final set be

```text
S_B subseteq N.
```

It is the maximal subset of `N` such that every row `C_i` meets `S_B` in either
`0` or at least `2` vertices:

```text
|C_i cap S_B| in {0,2,3,4} for every i.
```

Call `S_B` the **weighted two-core** of the chosen cohort system after deleting
the base `B`.

Peeling preserves the kernel, so

```text
ker L_N is isomorphic to ker A_B,
```

where `A_B` is the matrix with columns indexed by `S_B`, rows indexed by those
`i` with `C_i cap S_B != empty`, and entries

```text
(A_B)_{iv}=lambda^i_v.
```

Thus

```text
dim ker L = 4 + dim ker A_B.
```

This gives the promised exact classification:

```text
Exotic syzygies are exactly null vectors of the weighted two-core matrix A_B.
```

In particular, the rank rigidity lemma holds if and only if, for one
equivalently every nonconcyclic base `B`,

```text
rank A_B = |S_B|.
```

---

## 4. The finite obstruction list

After peeling, decompose the incidence graph of `A_B` into connected
components. A component consists of a vertex set `S_nu subseteq S_B` and the
rows meeting it. Let `A_nu` be the corresponding block.

Then

```text
dim ker L = 4 + sum_nu (|S_nu| - rank A_nu).
```

So every exotic syzygy belongs to one of the following explicit finite
patterns.

### Pattern I: unused columns

If a vertex `v in N` is in no chosen cohort at all, then the corresponding
column of `L_N` is zero. Then

```text
e_v in ker L_N,
```

so

```text
dim ker L > 4.
```

Thus any proof of the substantive lemma must first prove that no column can be
unused by the chosen four-cohort system.

### Pattern II: pair-row gain cycles

Suppose a core component has only rows meeting the component in exactly two
vertices. A row meeting `{u,v}` gives

```text
lambda^i_u g_u + lambda^i_v g_v = 0,
```

or

```text
g_v = -(lambda^i_u/lambda^i_v) g_u.
```

Thus the component is a signed weighted graph with edge gain

```text
gamma_i(u -> v) = -lambda^i_u/lambda^i_v.
```

A nonzero syzygy exists exactly when every cycle has gain product `1`:

```text
product_cycle gamma_i = 1.
```

If the pair-row component is a tree, it automatically contributes one exotic
degree of freedom. If it has cycles, it contributes precisely when the
signed-area gain products are balanced.

This is a concrete rank-defect mechanism using the actual `Delta`-coefficients.

### Pattern III: genuine hypercore components

If a component contains a row meeting `3` or `4` active vertices, then the
obstruction is exactly the vanishing of the maximal minors of its coefficient
matrix.

For a component with `m=|S_nu|` active vertices,

```text
dim ker A_nu > 0 iff rank A_nu < m.
```

Equivalently, all `m x m` minors of `A_nu` vanish. Each such minor is an
explicit polynomial in the original signed-area coefficients

```text
Delta_rst.
```

If the component has fewer than `m` active rows, then it is automatically
rank-defective. If it has at least `m` active rows, then the finite list of
determinant tests gives the exact obstruction.

---

## 5. What remains to prove the original lemma

The substantive rank rigidity lemma is therefore equivalent to the following
purely finite statement:

> For some nonconcyclic base `B` with `det Z_B != 0`, the weighted two-core
> `A_B` has full column rank.

Equivalently, every possible exotic support must be killed by one of the
following mechanisms:

```text
a row meeting it in exactly one active vertex;
an unbalanced pair-row gain cycle;
a full-rank hypercore determinant.
```

Thus a complete proof of the proposed rigidity lemma must rule out all weighted
two-core rank defects arising from the chosen centered four-cohorts.

This reduction is exact and finite for every fixed polygon and chosen cohort
system. It does not use generic dimension counting, and it keeps the actual
affine-circuit coefficients

```text
Delta_bcd, -Delta_acd, Delta_abd, -Delta_abc
```

throughout.
