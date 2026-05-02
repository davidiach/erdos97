# A Short Note on Small Counterexamples to Erdos Problem 97

Draft note for independent review, 2026-04-30.

## Abstract

Erdos Problem #97 asks whether every convex polygon has a vertex with no four
other vertices equidistant from it. This note proves a small-case obstruction:
no strictly convex counterexample exists with at most eight vertices. The proof
is elementary. It counts isosceles triangles by their apexes and by their base
pairs, then treats the octagon equality case using exterior turn angles.

This note does not prove Erdos Problem #97. It only shows that any
counterexample, if one exists, must have at least nine vertices.

## 1. Introduction

Call a strictly convex polygon bad if every vertex has at least four other
vertices at one common distance from that vertex. A bad polygon is exactly the
finite configuration that would falsify Erdos Problem #97.

The known nearby examples do not settle the problem. Danzer constructed a
9-point convex example for the analogous 3-neighbor statement, and
Fishburn--Reeds constructed a 20-point common-unit-distance 3-neighbor example.
Both are `k=3` phenomena. The 4-neighbor convex-polygon problem remains open at
the official problem page as of the 2026-04-30 check.

The purpose of this note is narrower: to give a human-readable proof of the
repo-local small-case exclusion for `n <= 8`.

## 2. Statement

Theorem. Let `A` be the vertex set of a strictly convex polygon. If every vertex
of `A` has four other vertices at a common distance from it, then `|A| >= 9`.

Equivalently, no bad strictly convex polygon exists with `n <= 8`.

## 3. A base-apex lemma

For distinct vertices `a,b in A`, call a vertex `p` an apex over the base
`{a,b}` if `p` is distinct from `a,b` and

```text
|pa| = |pb|.
```

Lemma. For a fixed base `{a,b}`, there is at most one apex on each side of the
line `ab`. Consequently a polygon side has at most one apex, and a diagonal has
at most two apices.

Proof. All apices over `{a,b}` lie on the perpendicular bisector of `ab`.
Normalize coordinates so that

```text
a = (-1,0),   b = (1,0).
```

Suppose two apices `p=(0,s)` and `q=(0,t)` lie on the same side of the line
`ab`, with `0 < s < t`. Then

```text
p = (s/t) q + ((1 - s/t)/2) a + ((1 - s/t)/2) b.
```

Thus `p` lies in the convex hull of `{a,b,q}`, so `p` cannot be an extreme
vertex of the polygon. This contradicts strict convexity. Hence at most one
apex lies on each side of `ab`.

If `ab` is a polygon side, all other vertices lie on one side of its supporting
line, so there is at most one apex. If `ab` is a diagonal, there can be at most
one apex on each side.

## 4. Counting isosceles triples

Let `T(A)` be the number of triples `(p,{a,b})` such that `p,a,b` are vertices,
`p` is distinct from `a,b`, and

```text
|pa| = |pb|.
```

If `A` is bad, then each vertex has a distance layer containing at least four
other vertices. Those four vertices determine `binom(4,2) = 6` unordered bases,
so

```text
T(A) >= 6n.
```

The base-apex lemma gives the opposite bound. There are `n` side bases, each
with capacity at most one, and `binom(n,2)-n` diagonal bases, each with capacity
at most two. Therefore

```text
T(A) <= n + 2*(binom(n,2)-n) = n(n-2).
```

A bad `n`-gon must satisfy

```text
6n <= n(n-2),
```

and hence `n >= 8`. This already rules out `n <= 7`.

## 5. The octagon equality case

It remains to rule out a bad octagon. Suppose

```text
A = {v_0, v_1, ..., v_7}
```

is indexed cyclically and is bad. The inequalities above become

```text
48 <= T(A) <= 48,
```

so equality holds everywhere.

First, every vertex contributes exactly six isosceles triples. Since the
octagon is bad, some distance class from each vertex has size at least four.
The only partition of the other seven vertices whose equal-distance pair count
is exactly six and which contains a part of size at least four is

```text
4,1,1,1.
```

Second, every base-pair capacity is saturated. Thus every side is the base of
exactly one isosceles triangle, and every diagonal is the base of exactly two,
one apex on each side of the diagonal.

Consider the length-2 diagonal `v_i v_{i+2}`. One side of this diagonal contains
only the intermediate vertex `v_{i+1}`. Since the diagonal must have an apex on
each side, `v_{i+1}` is the apex on the short side. Hence

```text
|v_i v_{i+1}| = |v_{i+1} v_{i+2}|.
```

This holds for every `i`, so all side lengths are equal. Let their common value
be `s`.

Let `tau_j in (0,pi)` be the exterior turn angle at `v_j`. Since the polygon is
strictly convex,

```text
tau_0 + tau_1 + ... + tau_7 = 2*pi.
```

For an equilateral convex polygon,

```text
|v_{j-1} v_{j+1}| = 2s cos(tau_j/2).
```

Thus `|v_{j-1} v_{j+1}| = s` if and only if

```text
tau_j = 2*pi/3.
```

Now consider the length-3 diagonal `v_i v_{i+3}`. Its short side contains
exactly `v_{i+1}` and `v_{i+2}`. Saturation says this diagonal has an apex on
that short side.

If `v_{i+1}` is the apex, then

```text
|v_i v_{i+1}| = |v_{i+1} v_{i+3}|,
```

so `|v_{i+1} v_{i+3}| = s`, and hence `tau_{i+2} = 2*pi/3`.

If `v_{i+2}` is the apex, then

```text
|v_i v_{i+2}| = |v_{i+2} v_{i+3}|,
```

so `|v_i v_{i+2}| = s`, and hence `tau_{i+1} = 2*pi/3`.

Therefore, for every `i`, at least one of the adjacent turns
`tau_{i+1}, tau_{i+2}` equals `2*pi/3`. Let

```text
M = {j : tau_j = 2*pi/3}.
```

Then `M` meets every adjacent pair of indices in the 8-cycle. Any vertex cover
of an 8-cycle has size at least four, so

```text
sum_j tau_j >= 4*(2*pi/3) = 8*pi/3 > 2*pi,
```

contradicting the exterior-turn sum.

Thus no bad octagon exists. Combined with the count for `n <= 7`, this proves
the theorem.

## 6. Status and review notes

This is a proof-note draft. It is independent of the repository's incidence
enumeration and exact survivor scripts, but it should still receive independent
mathematical review before being used as a public theorem-style claim outside
the repository.

The argument does not address `n >= 9` and does not claim a proof or
counterexample for Erdos Problem #97.

## References

1. T. F. Bloom, "Erdos Problem #97," Erdos Problems,
   https://www.erdosproblems.com/97, accessed 2026-04-30.
2. P. Erdos, "Some combinatorial and metric problems in geometry," Intuitive
   Geometry, Colloquia Mathematica Societatis Janos Bolyai 48, 167--177, 1987.
3. P. Erdos, "On some problems of elementary and combinatorial geometry,"
   Annali di Matematica Pura ed Applicata 103, 99--108, 1975.
4. P. C. Fishburn and J. A. Reeds, "Unit distances between vertices of a convex
   polygon," Computational Geometry 2(2), 81--91, 1992.
