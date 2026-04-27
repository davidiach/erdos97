# A short geometric obstruction for bad convex octagons

Status: proof-note draft; independent review requested.

This note gives a human-readable geometric proof that no bad convex polygon
exists with `n <= 8`. It is independent of the selected-witness incidence
enumeration retained in `docs/n8-incidence-enumeration.md` and
`docs/n8-exact-survivors.md`.

It does not prove Erdos Problem #97. The case `n >= 9` remains open.

Here a bad polygon means a strictly convex polygon in which every vertex has at
least four other vertices at one common distance from that vertex.

## Base-apex lemma

Let `A` be the vertex set of a strictly convex polygon, and let `a,b in A` be
distinct. On each side of the line `ab`, there is at most one vertex
`p in A \ {a,b}` with

```text
|pa| = |pb|.
```

Consequently, the unordered base pair `{a,b}` has at most one apex if `ab` is a
polygon side, and at most two apices if `ab` is a diagonal.

Proof. All such apices lie on the perpendicular bisector of `ab`. Normalize
coordinates so that

```text
a = (-1,0), b = (1,0).
```

Suppose two apices `p=(0,s)` and `q=(0,t)` lie on the same side of the line
`ab`, with `0 < s < t`. Then

```text
p = (s/t) q + ((1 - s/t)/2) a + ((1 - s/t)/2) b.
```

Thus `p` lies in `conv{a,b,q}`, contradicting strict convexity because `p`
would not be an extreme vertex of `conv(A)`.

If `ab` is a polygon side, all other vertices lie on the same side of its
supporting line, so there is at most one apex. If `ab` is a diagonal, there is
at most one apex on each side. If two apices exist for a diagonal base, they lie
on opposite sides of the base line, and the segment joining them crosses the
base segment.

## Isosceles-triangle count

Let `T(A)` be the number of triples `(p,{a,b})` such that `p,a,b in A`,
`p notin {a,b}`, `a != b`, and

```text
|pa| = |pb|.
```

Thus `p` is the distinguished apex of an isosceles triangle with base `{a,b}`.

If `A` is bad, then

```text
T(A) >= 6n.
```

Indeed, at each vertex `p`, one distance layer contains at least four other
vertices, and those four vertices determine `binom(4,2)=6` unordered base pairs
equidistant from `p`.

The base-apex lemma gives the upper bound

```text
T(A) <= n + 2*(binom(n,2) - n) = n(n-2).
```

There are `n` polygon sides, each supporting at most one apex, and
`binom(n,2)-n` diagonals, each supporting at most two apices.

Therefore a bad convex `n`-gon would satisfy

```text
6n <= n(n-2),
```

so `n >= 8`. In particular, no bad convex polygon exists with `n <= 7`.

This is an independent human proof of the small-case exclusion. The repository
still retains the incidence and Fano material because those artifacts are
structurally useful and reproducible.

## No bad convex octagon

Assume `A = {v_0,...,v_7}` is a bad convex octagon, indexed cyclically. The
previous count gives both

```text
T(A) >= 48
T(A) <= 48,
```

so equality holds everywhere. Thus:

1. Every polygon side is the base of exactly one isosceles triangle.
2. Every diagonal is the base of exactly two isosceles triangles, one apex on
   each side of the diagonal.

For the length-2 diagonal `v_i v_{i+2}`, one side contains only `v_{i+1}`.
Since the diagonal must have an apex on each side, `v_{i+1}` must be the apex
on the short side. Hence

```text
|v_i v_{i+1}| = |v_{i+1} v_{i+2}|.
```

This holds for every `i`, so all side lengths are equal. Let the common side
length be `s`.

Let `tau_j in (0,pi)` be the exterior turn angle at `v_j`. Since the octagon is
strictly convex,

```text
sum_{j=0}^7 tau_j = 2*pi.
```

For an equilateral convex polygon,

```text
|v_{j-1} v_{j+1}| = 2s cos(tau_j/2).
```

Therefore `|v_{j-1} v_{j+1}| = s` if and only if

```text
tau_j = 2*pi/3.
```

Now consider the length-3 diagonal `v_i v_{i+3}`. The short side contains
exactly `v_{i+1}` and `v_{i+2}`. Equality saturation says this diagonal must
have an apex on that short side.

If `v_{i+1}` is the apex, then

```text
|v_i v_{i+1}| = |v_{i+1} v_{i+3}|.
```

Since side lengths are `s`, this says `s = |v_{i+1} v_{i+3}|`, so
`tau_{i+2} = 2*pi/3`.

If `v_{i+2}` is the apex, then

```text
|v_i v_{i+2}| = |v_{i+2} v_{i+3}|.
```

Since side lengths are `s`, this says `|v_i v_{i+2}| = s`, so
`tau_{i+1} = 2*pi/3`.

Thus, for every `i`, at least one of `tau_{i+1}` and `tau_{i+2}` equals
`2*pi/3`.

Let

```text
M = {j : tau_j = 2*pi/3}.
```

The previous condition says `M` hits every adjacent pair of indices in the
8-cycle. Any vertex cover of an 8-cycle has size at least `4`. Therefore

```text
sum_j tau_j >= 4*(2*pi/3) = 8*pi/3 > 2*pi,
```

contradicting the total exterior turn.

Therefore no bad convex octagon exists. Combining this with the count gives no
bad convex polygon with `n <= 8`.

## Relationship to the existing n=8 artifacts

This proof note is intended as a compact human-readable obstruction. It does
not remove or supersede the machine-checked selected-witness pipeline in
`docs/n8-incidence-enumeration.md` and `docs/n8-exact-survivors.md`.

The computational artifacts remain useful because they audit selected-witness
incidence structure, exact survivor classes, and certificate machinery. This
note is a separate geometric argument that should be independently reviewed
before being used as a public theorem-style claim outside the repository.
