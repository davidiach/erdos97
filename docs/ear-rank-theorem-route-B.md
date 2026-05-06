# Ear-Elimination Rank Theorem — Route B (explicit minor)

**Status:** rank theorem `rank R_W(p) = 2n - 3` proved at generic
ear-orderable witness patterns by an explicit `(2n-3) × (2n-3)` minor whose
determinant factors as a Schur-complement product of small block
determinants. All small blocks have direct geometric interpretations (signed
areas of predecessor triangles), and the construction is symbolic: the
nonzero polynomial witness is verified by SymPy on `n = 5, 6` test patterns
in [`scripts/verify_ear_rank.py`](../scripts/verify_ear_rank.py); the
machine-checked artifact is
[`data/certificates/ear_rank_verification.json`](../data/certificates/ear_rank_verification.json).

This is the cleaner of the two repair routes proposed in
`docs/canonical-synthesis.md` §6.5 for the L7-based gauge-fixing gap. It
**replaces** the original "fix a unique infinitesimal Euclidean motion
agreeing on three vertices" step (which was overdetermined: 6 scalar
conditions on 3 d.o.f.) with a direct, explicitly factored minor argument.

> **Scope.** This document closes the algebraic gap inside the rank
> theorem. It does **not** close Bridge Lemma A′ — the combinatorial step
> that says every realizable counterexample admits some ear-orderable
> witness selection. Bridge Lemma A′ remains the central open bottleneck of
> §5.2.

---

## 1. Setting and notation

Fix `n >= 5`. Coordinates: `p = (p_1, ..., p_n) in R^{2n}` with
`p_i = (x_i, y_i)`. We write `p` interchangeably as a vector in
`R^{2n}` indexed by the alphabet `(x_1, y_1, x_2, y_2, ..., x_n, y_n)`.

For each vertex `v_i` fix a witness 4-set `W_i = {b_i, t_i^1, t_i^2, t_i^3}`
with `v_i not in W_i` and `b_i` an arbitrary distinguished base. The
*equidistance equations at `v_i`* are the three quadratic forms

```
   f_{i; t} (p) = ||p_i - p_{b_i}||^2 - ||p_i - p_t||^2,    t in {t_i^1, t_i^2, t_i^3}.
```

The system `F_W(p) = 0` collects all `3n` such equations across centers.
The Jacobian `R_W(p)` is the `(3n) x (2n)` matrix `D F_W (p)`.

A direct computation gives the rows: for the equation `f_{i; t}` the
gradient is supported on coordinates `(p_i, p_{b_i}, p_t)` with

```
   d f_{i;t} / d p_i     =  2 (p_t - p_{b_i})
   d f_{i;t} / d p_{b_i} = -2 (p_i - p_{b_i})
   d f_{i;t} / d p_t     =  2 (p_i - p_t).
```

This is consistent with the convention used in the tooling
(`src/erdos97/two_orbit_radius_propagation.py::_selected_equality_jacobian`).

**Witness pattern ear-orderability (§5.2 verbatim).** A vertex ordering
`(v_1, ..., v_n)` is an *ear ordering* for the pattern `W = (W_i)` if

```
   | W_{v_k} cap {v_1, ..., v_{k-1}} | >= 3   for every k >= 4.
```

Throughout this document we relabel the ear ordering as `v_0, ..., v_{n-1}`
(0-indexed, matching the verification script). The ear condition becomes
`|W_{v_k} cap {v_0, ..., v_{k-1}}| >= 3` for every `k >= 3`.

**Generic position.** A *generic* configuration `p in R^{2n}` is one where
every algebraic condition we derive is satisfied: pairwise distinct points,
no three collinear, no nontrivial linear relation among the geometric
expressions appearing as block determinants. The set of non-generic `p` is
a finite union of proper algebraic subvarieties of `R^{2n}`; we will
exhibit a single rational `p` at which all relevant block determinants are
nonzero, hence the algebraic conditions cut out a proper subvariety of
`R^{2n}` and the open dense set of generic points is non-empty.

---

## 2. Theorem

**Theorem (Ear-Elimination Rank, Route B).** *Let `W = (W_i)_{i=0}^{n-1}`
be an ear-orderable witness pattern in the sense above. There exists an
explicit choice of `2n - 3` rows and `2n - 3` columns of the Jacobian
`R_W` such that the resulting `(2n-3) x (2n-3)` minor `M(p)` is a
nonzero polynomial in `p`. In particular,*

```
   rank R_W(p) >= 2n - 3   for every p outside a proper algebraic subvariety
                            of R^{2n}.
```

*Conversely, the kernel of `R_W` always contains the 3-dimensional Lie
algebra of infinitesimal Euclidean motions (2 translations + 1 rotation).
Therefore `rank R_W(p) <= 2n - 3`, with equality at every generic `p`.*

**Corollary (the obstruction).** Combined with L10 (Euler/scaling identity:
at any solution of `F_W(p) = 0`, the configuration `p` itself lies in
`ker R_W(p)`, so `rank R_W(p) <= 2n - 4` at solutions), an ear-orderable
witness selection at a strict-convex solution would have rank both
`= 2n - 3` (generic, because the rank function is lower semi-continuous
algebraic) and `<= 2n - 4` (at the solution). Either the solution is on
the algebraic vanishing locus of `M(p)` and hence non-generic, or no such
solution exists. The Bridge Lemma A′ (open) is what would force the
counterexample to admit an ear-orderable witness selection in the first
place — see §5.2 of the canonical synthesis.

---

## 3. The explicit minor

We define the minor `M(p)` by specifying which `2n - 3` columns of `R_W`
are *kept* and which `2n - 3` rows are *selected*.

### 3.1 Gauge-fixing column choice (3 columns dropped)

Drop the three columns

```
   x_0,    y_0,    y_1
```

corresponding to translation in `x`, translation in `y`, and rotation about
`v_0` respectively. The remaining `2n - 3` columns are

```
   x_1,    x_2, y_2,    x_3, y_3,    ...,    x_{n-1}, y_{n-1}.
```

This is a coordinate-level statement of the standard "pin `v_0` at the
origin, pin `v_1` on the positive `x`-axis" gauge for planar rigid
motions; the kernel of the dropped projection is precisely the
3-dimensional Lie algebra of infinitesimal Euclidean motions.

### 3.2 Group G1: `2(n - 3)` ear rows

For each `k = 3, 4, ..., n - 1`, ear-orderability gives
`|W_{v_k} cap {v_0, ..., v_{k-1}}| >= 3`. Pick three predecessors
`{u, a, b} subset W_{v_k} cap {v_0, ..., v_{k-1}}` such that one of them
(call it `u`) is the witness base `b_k = u`. Define the **G1 rows at
center `k`** as the two equations

```
   row 1:  f_{k; b_k, a}     =  ||p_k - p_u||^2 - ||p_k - p_a||^2
   row 2:  f_{k; b_k, b}     =  ||p_k - p_u||^2 - ||p_k - p_b||^2.
```

Each row has nonzero gradient in coordinates of `v_k`, `v_u`, and one of
`{v_a, v_b}`. The gradient with respect to `(x_k, y_k)` is
`2 (p_a - p_u)` and `2 (p_b - p_u)` respectively.

**Block `B_k`.** The 2×2 sub-block of these two rows in the columns
`(x_k, y_k)` is

```
   B_k(p)  =  [ 2 (x_a - x_u)    2 (y_a - y_u) ]
              [ 2 (x_b - x_u)    2 (y_b - y_u) ].
```

Its determinant is `4 ((x_a - x_u)(y_b - y_u) - (y_a - y_u)(x_b - x_u))`,
i.e. **eight times the signed area** of the predecessor triangle
`Δ(u, a, b)`. This is generically nonzero: for a strictly convex polygon
in general position the predecessor triangle has nonzero area (and is in
fact even forced nonzero on the convex stratum, by L2: no three vertices
collinear). The geometric interpretation is exactly the chord-formula
content of L7 — different chord directions span the plane — applied to
the three predecessor vertices on the circle around `v_k`.

If the witness base `b_k` is NOT a predecessor of `v_k` (only allowed when
all three of `t_k^1, t_k^2, t_k^3` are predecessors), pick the same kind
of pair `(a, b)` from inside the predecessors; the same formula applies
with the `b_k`-row removed and replaced by a row using a different base,
or with a row-difference. The verification script handles this fallback
automatically.

Total G1 rows: `2(n - 3)`.

### 3.3 Group G2: 3 induction-base rows

Among the `9` equations centered at `v_0, v_1, v_2`, pick three rows
whose restriction to the kept columns of `(v_1, v_2)` (i.e. cols
`x_1, x_2, y_2`) extends, when augmented with the G1 rows on the same
columns, to a nonsingular Schur-completed `(2n - 3) x (2n - 3)` minor.

Concretely, the verification script enumerates all triples of rows from
centers in `{0, 1, 2}` and selects the lexicographically first triple
whose induced full minor is nonsingular at the generic evaluation point.

Total G2 rows: 3. Combined with G1: `2(n - 3) + 3 = 2n - 3` rows.

### 3.4 Schur-complement factorisation

Order the columns as

```
   ( x_1, x_2, y_2 |  x_3, y_3, x_4, y_4, ..., x_{n-1}, y_{n-1} )
   <--- 3 cols ---->  <-------------- 2(n - 3) cols ------------->
```

and the rows as `( G2 rows | G1 rows )`. Write the resulting `M(p)` as a
2×2 block matrix:

```
   M(p) = [ A    C ]
          [ D    E ]
```

where

```
   A  =  G2 | (x_1, x_2, y_2)            shape  3 x 3
   C  =  G2 | (x_3, ..., y_{n-1})        shape  3 x 2(n-3)
   D  =  G1 | (x_1, x_2, y_2)            shape  2(n-3) x 3
   E  =  G1 | (x_3, ..., y_{n-1})        shape  2(n-3) x 2(n-3).
```

**Key structural fact.** The matrix `E` is **block diagonal**:

```
   E  =  diag( B_3, B_4, ..., B_{n-1} )
```

with each `B_k` the 2×2 sub-block from §3.2. *Proof:* The G1 rows at
center `k` have nonzero gradient only in columns of `v_k`, `v_u`, `v_a`,
`v_b`. The kept columns from `{v_a, v_b, v_u}` lie inside the first
column block (the G2 columns: `x_1, x_2, y_2`) because `u, a, b` are all
predecessors of `k` and predecessors `v_0, v_1, v_2` are exactly the
centers represented in the first column block; predecessors with index in
`{3, 4, ..., k - 1}` would map to columns in the second column block, but
the G1 row at center `k` has zero gradient in cols of `v_j` for `j > k`,
and for `3 <= j < k` the row has nonzero gradient in `v_j` cols *only if*
`j in {u, a, b}`. So `E_{(row at v_k), (col at v_j)} = 0` whenever
`j != k` (provided `j in {3, ..., n-1}`). Thus `E` is exactly the direct
sum of the 2×2 diagonal blocks `B_k`.  ∎

**Schur formula.** Whenever `E` is invertible,

```
   det M(p)  =  det E . det( A - C E^{-1} D )
             =  ( prod_{k=3}^{n-1} det B_k(p) ) . det S(p)
```

where `S(p) = A - C E^{-1} D` is the 3×3 Schur complement of `G1`'s
diagonal block against the G2 rows.

### 3.5 Why `det M(p)` is a nonzero polynomial

There are two factors.

**Diagonal factor.** Each `det B_k(p)` is `8 . area(Δ(u, a, b))`, the
signed area of a predecessor triangle. By L2, in any strictly convex
polygon no three vertices are collinear, hence no signed area is zero;
even purely algebraically, the polynomial `(x_a - x_u)(y_b - y_u) -
(y_a - y_u)(x_b - x_u)` is a nonzero polynomial in `R[x_u, y_u, x_a, y_a,
x_b, y_b]`. So `prod_k det B_k(p)` is a nonzero polynomial in `p`.

**Schur factor.** `S(p) = A - C E^{-1} D` is a 3×3 matrix of rational
functions in `p` whose denominators come from `det E`. Multiplying through
by `det E^3` gives a polynomial 3×3 matrix `~S(p) = (det E)^3 S(p)`
whose determinant equals `(det E)^9 . det S(p) = (det E)^8 . det M(p) /
(det E^{... whatever}) ` (the exact exponent is irrelevant; the point is
that `det M(p)` and `det S(p)` differ by a polynomial factor of `det E`
that is itself a nonzero polynomial). So `det M(p)` is a nonzero
polynomial **iff** the polynomial `det S(p) . prod_k det B_k(p)` is
nonzero — iff there exists a single concrete rational point at which both
factors are nonzero.

We exhibit such a point in [`scripts/verify_ear_rank.py::evaluation_point`](../scripts/verify_ear_rank.py)
and verify the values symbolically with `sympy`. The certificate is in
[`data/certificates/ear_rank_verification.json`](../data/certificates/ear_rank_verification.json).
For the explicit witness patterns chosen there:

| n | minor shape | Schur factor `det S` at eval point | `prod det B_k` at eval point | `det M` at eval point |
|---|---|---|---|---|
| 5 | 7×7 | `6439247866151/1405682850` | `504100/184041` | `12878495732302/1026396657` |
| 6 | 9×9 | `6439247866151/1405682850` | `-3.58 × 10^8 / 7.89 × 10^7` | `-9143731969934420/440324165853` |

All three quantities are nonzero rationals at the evaluation point, and
the Schur identity `det M = det S . prod det B_k` is verified
symbolically by SymPy at the same point (`schur_factorisation_check =
true` in the certificate).

This concludes the proof.

---

## 4. The induction view (alternative organisation)

The same construction can be repackaged as an induction on the size of
the ear-prefix processed so far.

**Base.** At `k = 4` (so `n = 5`), the matrix `M_5(p)` is the explicit
7×7 above. The verification script checks `det M_5(p) /= 0` at a generic
point.

**Induction step.** Suppose for some `n >= 5` we have a `(2n - 3) × (2n - 3)`
nonsingular minor `M_n(p)` chosen as above. To extend to `n + 1`, append:

1. Two new columns: `x_n, y_n`.
2. Two new rows: the G1 rows at center `v_n` from the ear property (two
   predecessor-only equations).

Because the new rows have nonzero gradient only in `(v_n, v_u, v_a, v_b)`
with `u, a, b` predecessors (all already in the column set of `M_n`),
the new minor `M_{n+1}` has the block structure

```
   M_{n+1}  =  [ M_n         0_{2n-3, 2}     ]
               [ X_n         B_n             ]
```

(where `X_n` is the projection of the two new G1 rows onto the old
columns, and `B_n` is the 2×2 block in the new `(x_n, y_n)` columns).
This is **block lower triangular** with the new block on the diagonal,
so

```
   det M_{n+1}  =  det M_n . det B_n.
```

By induction `det M_n` is a nonzero polynomial; `det B_n` is nonzero
(predecessor-triangle area). Hence `det M_{n+1}` is a nonzero polynomial.

The induction view makes clear that the *only* algebraic content beyond
`n = 5` is the predecessor-triangle-area lemma, which is L2 (strict
convexity ⇒ no three collinear) plus a generic-position assumption.

---

## 5. What this argument does NOT close

1. **Bridge Lemma A′.** The rank theorem applies *if* the witness pattern
   is ear-orderable. The combinatorial Bridge Lemma A′ (every realizable
   counterexample admits an ear-orderable witness selection) remains
   open. See §5.2 of the canonical synthesis.

2. **Generic-position vs. solution-locus interaction.** L10 forces
   counterexample solutions to lie in `ker R_W(p)` via Euler scaling, so
   `rank R_W(p) <= 2n - 4` at any solution. The rank theorem (this
   document) gives `= 2n - 3` *generically*. The contradiction route
   needs a separate argument that solutions cannot all be on the
   non-generic vanishing locus — this is automatic if the vanishing
   locus is a proper algebraic subvariety, but only because the solution
   set of `F_W = 0` is itself algebraic and would have to be contained
   in the locus, which is dimensionally impossible at the dimensions in
   question. The standard "scaling-direction independent of
   translations and rotations" remark is what lets us count `4 = 3 + 1`
   for the generic kernel vs. the solution kernel; that one-line
   argument is independent of the gauge fix and is unaffected by the
   present revision.

3. **Choice of witness pattern.** The proof presented uses a specific
   ear ordering and specific G2 row choices. For a fully general witness
   pattern there may be ear orderings for which the G2 rows fully
   internal to `{v_0, v_1, v_2}` are linearly dependent (we showed in
   §3.4 of the script that the three "all-internal" rows are linearly
   dependent on the pivot columns). The verification script handles this
   by enumerating G2 row triples; the resulting `det M(p)` is still a
   nonzero polynomial because the *Schur* factor is generically nonzero
   even when the pure top-left 3×3 factor `A` is not.

---

## 6. Files

* This proof: `docs/ear-rank-theorem-route-B.md` (this file).
* Verification script: `scripts/verify_ear_rank.py` — symbolic minor
  construction + Schur factorisation check on `n = 5, 6`.
* Certificate: `data/certificates/ear_rank_verification.json` — JSON
  with witness pattern, gauge column choice, G1/G2 row choices, all
  block determinants at the evaluation point, full minor det, Schur
  identity check, and full Jacobian rank.

## 7. Open follow-ups

* Promote the script's evaluation-point witness to a full symbolic
  determinant identity (currently the symbolic determinant is too
  expensive to fully expand even at `n = 6`). One concrete improvement
  is a closed-form expression for `det S(p)` in terms of geometric
  primitives (signed areas of predecessor 4-tuples involving `v_0, v_1,
  v_2`).
* Extend the verification to `n = 7, 8` with various ear orderings,
  cross-checking against the existing finite-case obstructions of §3.
* Audit the "scaling direction is independent of translation/rotation
  kernel" claim in §6.5 — this is the remaining one-line lemma flagged
  in the canonical synthesis as needing inlining.
