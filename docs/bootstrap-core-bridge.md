# Bootstrap-core bridge

Status: `LEMMA` / bridge fork. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note records the rich-triple closure formulation of the ear-orderable
bridge. It refines the adaptive radius-blocker alternative by replacing a
terminal stuck set with a generating core, deletion closures, private halos,
and a weighted cyclic outside-pair capacity ledger.

## Full rich classes

Let `P` be a strictly convex 4-bad polygon with vertex set `V` in cyclic order.
For a vertex `y` and radius `r > 0`, define the full distance class

```text
D_y(r) = { z in V \ {y} : |p_y p_z| = r }.
```

The rich row family at `y` is

```text
R(y) = { D_y(r) : |D_y(r)| >= 4 }.
```

A selected row at `y` is any 4-subset of a class in `R(y)`. Distinct classes
in `R(y)` are disjoint, because each witness has one distance from `y`.

## Rich-triple closure

For `A subset V`, define `cl(A)` as the least set containing `A` with this
closure rule:

```text
if y in V, C in R(y), and |C cap cl(A)| >= 3, then y is in cl(A).
```

Define the bootstrap rank

```text
rho(P) = min { |A| : cl(A) = V }.
```

## Closure-rank lemma

`P` admits an ear-orderable selected-witness system if and only if
`rho(P) <= 3`.

Here ear-orderable uses the repo convention: the first three vertices are the
base, and the three-earlier-witness condition is imposed only from the fourth
vertex onward.

Proof. If an ear order exists, take its first three vertices as `A`. Each later
vertex is added by three earlier witnesses in one rich class, so `cl(A)=V`.

Conversely, suppose `cl(A)=V` for `|A| <= 3`. Enlarge `A` to a 3-set if needed.
Take any finite closure construction sequence. When a vertex `y` first enters
the closure, some triple `T subset C in R(y)` is already present. Since
`|C| >= 4`, choose `q in C \ T`, and select the row `T union {q}` at `y`.
This gives three earlier witnesses for every non-base vertex. The three base
vertices may receive arbitrary rich rows. Thus the selected system is
ear-orderable.

## Bootstrap cores and private halos

A generator is a set `U` with `cl(U)=V`.

A minimal generator is inclusion-minimal: no proper subset of `U` generates
`V`. A minimum generator is cardinality-minimum: `|U|=rho(P)`.

Assume `rho(P)>3`, and let `U` be any minimal generator. Put `O=V\U`. For
`u in U`, define

```text
A_u = cl(U \ {u})
D_u = O \ A_u
```

where `D_u` is the private halo of `u`.

Then:

1. `|U| >= 4`.
2. `u notin A_u`.
3. For every `C in R(u)`, `|C cap A_u| <= 2`.
4. Therefore `|C cap D_u| >= |C|-2 >= 2`.
5. In particular, `U` is a radius-blocker: `|C cap U| <= 2` for every
   `u in U` and `C in R(u)`.

Proof. Since `U` is minimal, `A_u != V`. If `u in A_u`, then `U subset A_u`,
and closedness gives `V=cl(U) subset A_u`, a contradiction. Hence `u notin
A_u`. If some rich class at `u` had three points in `A_u`, the closure rule
would add `u`, again a contradiction. Since `U\{u} subset A_u` and witnesses
exclude their center, the witnesses outside `A_u` lie in `O\A_u=D_u`.

This theorem needs only inclusion-minimality for the private-halo conclusion.
To certify a non-ear escape, however, one must also certify `rho(P)>3`, for
example by checking that every 3-seed has proper closure. A larger
inclusion-minimal generator can coexist with a smaller generator in a general
closure system.

The review-pending complement-seeding follow-up in
`docs/bootstrap-core-complement-seeding.md` specializes to a
cardinality-minimum generator `U`. With `O=V\U`, it proves the linear bound
`2|U| <= 3|O|`. It also identifies the equality case as a union of equilateral
three-vertex source components and shows that strict convexity forces at least
`15` vertices in that tight case. That follow-up is a stronger size ledger,
not a blocker contradiction or a proof of Erdos Problem #97.

## Weighted cyclic private-pair capacity

For `u in U` and `C in R(u)`, write

```text
H_{u,C} = C cap D_u.
```

Then `|H_{u,C}| >= |C|-2`. Count all private pairs:

```text
I_priv = { (u,C,{a,b}) : u in U, C in R(u), {a,b} subset H_{u,C} }.
```

For an outside pair `{a,b} subset O`, let `kappa_U(a,b)` be the number of the
two open cyclic arcs from `a` to `b` that contain at least one vertex of `U`.
Thus `kappa_U(a,b)` is `1` or `2` when `U` is nonempty.

Then every non-ear bootstrap core satisfies

```text
sum_{u in U} sum_{C in R(u)} binom(|C cap D_u|, 2)
  <= sum_{{a,b} subset O} kappa_U(a,b).
```

Consequently,

```text
sum_{u in U} sum_{C in R(u)} binom(|C|-2, 2)
  <= sum_{{a,b} subset O} kappa_U(a,b)
  <= 2 binom(|O|, 2).
```

Proof. Fix an outside pair `{a,b}`. If it appears in a private pair charged by
`u`, then `u` is equidistant from `a` and `b`, so `u` lies on the perpendicular
bisector of segment `ab`. In a strictly convex polygon, at most two vertices
can lie on this line. Since `a` and `b` lie on opposite sides of their
perpendicular bisector, each boundary arc from `a` to `b` crosses that line.
Thus, if two such core vertices occur, they lie in the two different open
cyclic arcs between `a` and `b`. The pair can therefore be charged to at most
one core center from each arc containing core vertices. Summing over outside
pairs gives the first inequality, and `|C cap D_u| >= |C|-2` gives the second.

## Outside-run form

Let `R_1,...,R_t` be the maximal consecutive outside-vertex runs in the cyclic
order, with lengths `o_i`. Then

```text
sum_{{a,b} subset O} kappa_U(a,b)
  = 2 binom(|O|, 2) - sum_i binom(o_i, 2).
```

If `a,b` lie in different outside runs, both arcs between them contain a core
vertex, so `kappa=2`. If they lie in the same outside run, one open arc stays
inside that outside run and contains no core vertex, so `kappa=1`.

This run term is the useful strengthening over the earlier one-pair-per-center
bound. Clustered halo vertices reduce capacity; highly interleaved halo
vertices maximize it.

## Fragile-cover overlay

If `P` is a minimal counterexample, every fragile critical row is an exact
critical 4-tie. If such a row is centered at a core vertex `u in U`, then it is
one class `C in R(u)` of size 4, and the private-halo theorem gives

```text
|C cap D_u| >= 2.
```

Thus each core-centered fragile row contributes at least one private outside
pair to the weighted capacity ledger. If it has three or four private-halo
witnesses, it contributes three or six pairs, not just one.

This overlay applies only to exact critical 4-ties, not to arbitrary selected
rows or abstract fragile candidates.

## Certificate semantics

A non-ear/bootstrap-core escape certificate should contain three layers:

1. `rho(P)>3`, usually by exhaustive failure of all 3-seed closures.
2. A generating core `U` and a closure order showing `cl(U)=V`.
3. Deletion closures `A_u`, private halos `D_u`, rich-class private slices, and
   the weighted cyclic capacity ledger.

The helper module `src/erdos97/bootstrap_cores.py` implements this finite
bookkeeping. The smoke checker is:

```bash
python scripts/check_bootstrap_core_bridge.py --assert-expected
```

The checked `C13_sidon_1_2_4_10` fixed-row benchmark is used only as a
bookkeeping negative control. That fixed selected-witness pattern is already
killed across all cyclic orders by the repo's exact Kalmanson/Farkas search.

The follow-up diagnostic `docs/bootstrap-core-crosswalk.md` applies the same
singleton-rich bookkeeping to current sparse/frontier fixed-row motifs. It
records that these audited cases have rank greater than 3 but still pass the
weighted private-halo capacity ledger, so the ledger is a bridge target rather
than an obstruction by itself.
