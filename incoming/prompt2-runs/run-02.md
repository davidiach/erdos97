# Prompt 2 Run 02

Continuation result from the same Prompt 2 session.

Continuing from the quotient reduction, the clean next step is to make the
obstruction **minimal**. That gives an exact finite certificate for every
possible exotic syzygy.

I will write this as a theorem.

---

# The certificate theorem for exotic syzygies

Let

```text
Z_j=(1,x_j,y_j,q_j), q_j=x_j^2+y_j^2,
```

and let `U=span{1,x,y,q} subseteq R^n`.

For row `i`, with chosen cohort `C_i={a,b,c,d}`, write

```text
lambda^i_a = Delta_bcd,
lambda^i_b = -Delta_acd,
lambda^i_c = Delta_abd,
lambda^i_d = -Delta_abc,
```

and `lambda^i_v=0` outside `C_i`. Thus

```text
(Lh)_i = sum_{v in C_i} lambda^i_v h_v.
```

Because the polygon is strictly convex, no three vertices are collinear, so
every coefficient appearing in a row is nonzero.

Also, under the four-cohort hypothesis, `P` cannot actually be globally
concyclic. Indeed, if all `p_j` lay on one circle `Omega`, then the centered
circle through `C_i` would meet `Omega` in four points, hence would equal
`Omega`. Its center would then be `p_i`, but `p_i in Omega`, impossible for a
nondegenerate circle. Thus `U` is automatically four-dimensional.

---

## Theorem

Fix any four-point base

```text
B={b_1,b_2,b_3,b_4}
```

such that the `4 x 4` matrix `Z_B` is nonsingular, and put

```text
N=[n]\B.
```

Then

```text
ker L/U is isomorphic to ker L_N,
```

where `L_N` is the submatrix of `L` using only the columns in `N`.

Moreover, `ker L/U != 0` if and only if there exists a finite certificate

```text
(B,S,T)
```

with the following data:

- `S subseteq N`, `S != empty`;
- no row meets `S` in exactly one vertex;
- `T` is a set of `|S|-1` active rows;
- the `(|S|-1) x |S|` matrix

```text
A_{T,S} = (lambda^i_v)_{i in T, v in S}
```

has rank `|S|-1`;

- if `S={s_1,...,s_m}`, `m=|S|`, then the cofactor vector

```text
g_{s_j} = (-1)^j det A_{T,S\{s_j}}
```

has no zero coordinate and is annihilated by every active row:

```text
sum_{v in C_i cap S} lambda^i_v g_v = 0  for every row i.
```

Equivalently, for every active row `i notin T`,

```text
sum_{j=1}^m lambda^i_{s_j} (-1)^j det A_{T,S\{s_j}} = 0.
```

This is an explicit determinant identity in the original signed-area
coefficients `Delta_rst`.

Thus every exotic syzygy is exactly one of these finite cofactor certificates.

---

# Proof

First, as before, `U subseteq ker L`. Since `Z_B` is nonsingular, every
`h in R^n` has a unique decomposition

```text
h = u + g,
```

where `u in U` and `g_b=0` for all `b in B`. Namely, `u` is the unique element
of `U` agreeing with `h` on `B`.

Because `U subseteq ker L`,

```text
h in ker L iff g in ker L.
```

But `g` vanishes on `B`, so this is equivalent to

```text
L_N g_N = 0.
```

Therefore

```text
ker L/U is isomorphic to ker L_N.
```

Now suppose `ker L_N != 0`. Choose a nonzero vector `g in ker L_N` with
minimal support

```text
S = supp g subseteq N.
```

If some row `i` met `S` in exactly one vertex `v`, then the `i`-th equation
would be

```text
lambda^i_v g_v = 0.
```

Since `lambda^i_v != 0`, this would force `g_v=0`, contradicting `v in S`.
Hence every row meets `S` in `0` or at least `2` vertices.

Let `A_S` be the active matrix with columns `S` and rows those `i` for which
`C_i cap S != empty`. The restriction `g_S` lies in `ker A_S`.

By minimality of `S`,

```text
dim ker A_S = 1.
```

Indeed, if `dim ker A_S >= 2`, then we could take two independent null vectors
and form a nontrivial linear combination cancelling one chosen coordinate of
`g_S`, producing a nonzero kernel vector with strictly smaller support. That
contradicts minimality.

Thus

```text
rank A_S = |S|-1.
```

Choose `|S|-1` active rows `T` forming a full-rank row basis. Then `A_{T,S}`
has rank `|S|-1`, so its nullspace is one-dimensional. The standard cofactor
vector

```text
g_{s_j}=(-1)^j det A_{T,S\{s_j}}
```

spans that nullspace. Minimality forces every coordinate of this cofactor
vector to be nonzero.

Finally, because the original `g` is killed by every active row, every active
row `i` must satisfy

```text
sum_{v in C_i cap S} lambda^i_v g_v = 0.
```

Substituting the cofactor formula gives the displayed determinant identities.

Conversely, if such a certificate exists, define `g` on `S` by the cofactor
formula and set `g=0` outside `S`. The certificate says every row annihilates
`g`. Since `g` vanishes on `B`, and no nonzero element of `U` can vanish on
`B`, this gives a genuine exotic element of `ker L/U`.

That proves the theorem.

---

# The three actual obstruction patterns

The theorem reduces everything to three concrete mechanisms.

## Pattern 1: isolated quotient columns

If `v in N` is not used by any active row after deleting `B`, then `S={v}` is
a certificate.

Equivalently,

```text
e_v in ker L_N.
```

So a proof of rank rigidity must first rule out the possibility that, after
subtracting a four-point base, some vertex is invisible to all chosen cohorts.

---

## Pattern 2: pure pair-gain components

Suppose every active row meets `S` in exactly two vertices. Then `S` carries a
weighted graph structure.

A row `i` meeting

```text
C_i cap S = {u,v}
```

gives

```text
lambda^i_u g_u + lambda^i_v g_v = 0,
```

so

```text
g_v = -(lambda^i_u/lambda^i_v) g_u.
```

Define the gain

```text
gamma_i(u -> v) := -lambda^i_u/lambda^i_v.
```

For a cycle

```text
v_0 -> v_1 -> ... -> v_k = v_0,
```

the propagated value is consistent if and only if

```text
prod_{r=1}^k gamma_{i_r}(v_{r-1} -> v_r) = 1.
```

Thus a pure pair component contributes an exotic syzygy precisely when its gain
graph is balanced.

In particular:

- a pair-gain tree automatically contributes one exotic degree of freedom;
- a pair-gain cycle contributes one exotic degree of freedom exactly when its
  signed-area gain product is `1`;
- an unbalanced pair cycle kills the would-be syzygy.

All gains are the actual `Delta`-ratios, not symmetrized coefficients.

---

## Pattern 3: mixed hypercore determinants

Now suppose some active row meets `S` in three or four vertices.

First contract every balanced pair-gain component. More explicitly, inside a
balanced pair component `K`, choose a root `r_K`. Every vertex `v in K` has a
well-defined multiplier `eta_v` such that

```text
g_v = eta_v t_K.
```

The multipliers are products of the actual gains

```text
-lambda^i_u/lambda^i_v
```

along pair paths.

Now take a row `i` meeting several pair components. It becomes the equation

```text
sum_K (sum_{v in C_i cap S cap K} lambda^i_v eta_v) t_K = 0.
```

Thus, after pair contraction, the remaining obstruction is an ordinary finite
hypermatrix circuit. If the contracted active matrix has columns
`K_1,...,K_m`, then an exotic syzygy exists exactly when some `(m-1)`-row
submatrix has a nonzero cofactor null vector and every remaining row satisfies
the corresponding cofactor determinant identity.

So the mixed obstruction is:

```text
balanced pair propagation + one cofactor circuit in the contracted hypercore.
```

---

# Final equivalence

The substantive rank rigidity lemma is therefore equivalent to the following
finite statement:

> For one, equivalently every, base `B` with `det Z_B != 0`, there is no
> nonempty set `S subseteq [n]\B` admitting one of the three certificates
> above.

Equivalently,

```text
ker L = U
```

if and only if all of the following are ruled out:

```text
(I) isolated quotient columns;
(II) balanced pure pair-gain components;
(III) mixed hypercore cofactor determinant identities.
```

This is the precise finite obstruction list. A full proof of the rank rigidity
lemma must show that the geometry of strictly convex centered four-cohorts
forbids all three; a counterexample must exhibit one of them.
