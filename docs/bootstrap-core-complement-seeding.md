# Bootstrap-core complement seeding

Status: `LEMMA_DRAFT` / `REVIEW_PENDING`. This note claims neither a general
proof of Erdos Problem #97 nor a counterexample.

This note strengthens the bootstrap-core bridge for a cardinality-minimum
generator. The complement of the generator, together with one seed from each
source component of a residual dependency graph, generates the full vertex
set. This gives a linear bound on the bootstrap rank. The equality case has
additional exact structure, and strict convexity rules out its smallest
parameter choice.

The definitions of full rich classes, rich-triple closure `cl`, bootstrap rank
`rho(P)`, and ear-orderability are those in
`docs/bootstrap-core-bridge.md`.

## Complement-seeding lemma

Let `P` be a 4-bad polygon with vertex set `V`, and let `U` be a
cardinality-minimum generator for full rich-triple closure:

```text
cl(U) = V,
|U| = rho(P).
```

Put

```text
O = V \ U,
k = |U|,
m = |O|.
```

Then

```text
2k <= 3m.
```

Equivalently,

```text
rho(P) <= 3|V|/5.
```

The proof of this bound uses only the full rich-class closure system: every
rich class has at least four members and excludes its center. Strict convexity
enters only in the later geometric equality-case refinement.

### Proof

Let

```text
A = cl(O),
W = U \ A.
```

Since `U` has minimum cardinality, it is inclusion-minimal. Therefore, for
every `u in U` and every rich class `C` centered at `u`,

```text
|C cap U| <= 2.
```

Indeed, `u` is not a member of its own rich class. If `C` contained three
members of `U`, then `cl(U \ {u})` would add `u` and would consequently contain
`cl(U)=V`, contradicting minimality of `U`.

Now fix `u in W`. Since `u notin A=cl(O)`, no rich class at `u` contains three
members of `A`, so

```text
|C cap A| <= 2.
```

On the other hand, `|C| >= 4` and `|C cap U| <= 2`, so `C` contains at least
two members of `O`. Because `O subset A`, the two preceding bounds force every
rich class at `u` to have exactly the form

```text
C = {two vertices of O} union {two vertices of W}.
```

In particular, every such class has exactly four members and contains no
vertex of `A cap U`.

Choose one rich class at every `u in W`. If its two `W`-members are `v,w`, add
the directed arcs

```text
v -> u,
w -> u.
```

Every vertex of this directed graph on `W` has two distinct in-neighbors. In
the condensation DAG, every source strongly connected component therefore
has at least three vertices: both in-neighbors of each vertex must remain in
that source component, and neither can be the vertex itself.

Choose one seed from each source component. Starting with all of `O` and those
seeds, one active in-neighbor of `u` combines with the two `O`-members of the
chosen rich class at `u` to activate `u`. Strong connectivity activates an
entire source component from its seed. A topological traversal of the
condensation DAG then activates every remaining component.

If there are `s` source components, this constructs a generator of size at
most

```text
m + s <= m + |W|/3 <= m + k/3.
```

Since `U` has minimum cardinality,

```text
k <= m + k/3,
```

which is equivalent to `2k <= 3m`.

## Equality structure

Suppose

```text
2k = 3m.
```

Every inequality in the proof is then an equality. Consequently:

1. `|W|=k`, so `A cap U` is empty and `cl(O)=O`.
2. Every source strongly connected component has exactly three vertices.
3. The source components partition `U`; there are no non-source components.
4. For a component `T={a,b,c}`, the chosen rich class at each center consists
   of the other two members of `T` and exactly two members of `O`.

At center `a`, the witnesses `b,c` lie in one distance class, so
`|ab|=|ac|`. The analogous equalities at `b` and `c` show that every
three-vertex source component is an equilateral triangle.

## Five-outside lemma for a tight source triangle

Now assume that `P` is strictly convex. Let `T={a,b,c}` be one of the tight
source components, with side length `s`. Its three chosen classes have the
form

```text
C_a = {b,c,x_1,x_2},
C_b = {a,c,y_1,y_2},
C_c = {a,b,z_1,z_2},
```

where all six displayed outside-witness positions belong to `O`, and every
member of `C_a` is at distance `s` from `a`, with the analogous statements at
`b` and `c`.

These six positions use at least five distinct vertices of `O`.

### Proof

An outside vertex can witness at most two of `a,b,c`. A point equidistant from
all three is their circumcenter, whose distance from an equilateral triangle's
vertices is `s/sqrt(3)`, not `s`.

If an outside vertex `x` witnesses both `a` and `b`, then

```text
|xa| = |xb| = s.
```

The two radius-`s` circles centered at `a` and `b` meet at `c` and at the
reflection `c'` of `c` across the line `ab`. Since `x` lies outside `T`, it
must equal `c'`. Thus each shared outside witness is uniquely associated with
one edge of `T`.

If the six witness positions used at most four outside vertices, incidence
counting would force at least two outside vertices to witness two centers.
They correspond to two distinct edges of `T`. Any two edges of a triangle
share a vertex; suppose the edges are `ab` and `ac`. The reflected apexes for
those two edges have `a` as their midpoint. Hence the polygon vertex `a` lies
on a segment joining two other polygon vertices, contradicting strict
convexity.

Therefore at least five distinct outside vertices are required.

## Tight-case size consequence

In the equality case, `U` is partitioned into three-vertex components, so
`k` is divisible by `3`. The relation `2k=3m` then makes `m` even. Since the
non-ear branch has `k>3`, its first numerical possibility is

```text
(k,m) = (6,4).
```

The five-outside lemma rules this out. Therefore every strictly convex tight
case satisfies

```text
m >= 6,
k >= 9,
|V| = k+m >= 15.
```

Equivalently, for a strictly convex non-ear bootstrap core with fewer than
15 vertices, the complement-seeding inequality is strict.

## Scope and remaining gap

This package strengthens the radius-blocker size ledger. It does not eliminate
non-tight blockers, does not control reuse of outside witnesses across
different tight source triangles, and does not force the fragile critical
cover of a vertex-minimal counterexample to meet the chosen source-component
classes.

The closure-rank lemma proves that `rho(P) <= 3` is equivalent to the existence
of an ear-orderable selected-witness system. The further claim that every such
system yields a rank contradiction remains conditional on the gauge-fixing
repair recorded in `docs/claims.md` and `docs/canonical-synthesis.md`. Nothing
in this note supplies that repair.

Independent proof review is requested before theorem-style use.
