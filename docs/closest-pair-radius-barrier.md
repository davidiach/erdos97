# Closest-Pair Radius Barrier

Status: `LEMMA` / structural necessary condition.

This note records small exact obstructions for the global closest-pair
distance. It does not prove Erdos Problem #97 and does not produce a
counterexample.

## Statement

Let `P` be the vertex set of a strictly convex polygon, and let

```text
delta = min { |p-q| : p,q in P, p != q }.
```

If `p` is an endpoint of a pair at distance `delta`, then at most three other
vertices of `P` lie at distance `delta` from `p`.

Consequently, in any counterexample, every endpoint of a globally closest pair
must use only richer distance classes whose radii are strictly larger than
`delta`.

A conditional nonagon subcase also follows from the same closest-pair
exclusion plus the two-overlap crossing-bisector rule: if an all-bad polygon
has a globally closest pair that is a polygon side, then it has at least ten
vertices. Equivalently, any hypothetical all-bad nonagon must have every
globally closest pair realized by a diagonal, not by a side.

## Radius Proof

Let `p` be a closest-pair endpoint. Suppose, for contradiction, that four
distinct vertices

```text
q1,q2,q3,q4
```

all lie on the circle of radius `delta` centered at `p`.

At a vertex of a strictly convex polygon, all other vertices lie in the closed
cone spanned by the two incident edge rays, and that cone has aperture
strictly less than `pi`. Put the four vertices `q1,q2,q3,q4` in angular order
around `p`. Their total angular span is therefore strictly less than `pi`.

Because `delta` is the global minimum intervertex distance, any two of the
`q_i` must be at least `delta` apart. On the circle of radius `delta` centered
at `p`, two points with angular gap `theta in [0,pi]` are separated by

```text
2*delta*sin(theta/2).
```

This is smaller than `delta` whenever `theta < pi/3`. Hence each of the three
consecutive angular gaps among the four ordered `q_i` is at least `pi/3`.
Their span is at least

```text
3*(pi/3) = pi,
```

contradicting the strict-convexity cone span.

Thus no closest-pair endpoint can have four other vertices at the closest-pair
distance.

## Adjacent Closest Pair

Suppose now that a counterexample has a globally closest pair `v0,v1` that is
a side of the polygon, with vertices labelled in cyclic order

```text
v0, v1, ..., v(n-1).
```

For each bad vertex `x`, choose a same-radius witness set `S(x)` of size four.
By the closest-pair radius barrier, `v1 notin S(v0)` and `v0 notin S(v1)`.
Because `v0v1` is a side, the crossing-bisector rule gives

```text
|S(v0) cap S(v1)| <= 1.
```

Hence

```text
|S(v0) union S(v1)| >= 4 + 4 - 1 = 7.
```

This union is contained in the `n - 2` vertices other than `v0,v1`, so
`n >= 9`.

It remains to exclude the borderline `n = 9` case under the same adjacent
closest-pair hypothesis. If `n = 9`, then the preceding inequalities saturate:

```text
S(v0) union S(v1) = {v2, v3, ..., v8},
|S(v0) cap S(v1)| = 1.
```

Consider `v2`. If `S(v0) cap S(v2)` contained two vertices, the
crossing-bisector rule would force those two common witnesses to lie on
opposite open cyclic arcs between `v0` and `v2`. One of those arcs contains
only `v1`, but `v1 notin S(v0)`. Therefore

```text
|S(v0) cap S(v2)| <= 1.
```

Also `v1` and `v2` are adjacent, so

```text
|S(v1) cap S(v2)| <= 1.
```

Every vertex among `v3,...,v8` lies in `S(v0) union S(v1)`, and these two
intersection caps allow `S(v2)` to contain at most two vertices from that
union. Since `S(v2)` has size four and cannot contain `v2`, it must contain
both `v0` and `v1`.

The same endpoint argument at `v8` shows that `S(v8)` must also contain both
`v0` and `v1`: use adjacency of `v8,v0`, and for the pair `v1,v8` note that
the open arc from `v8` to `v1` through `v0` contains only `v0`, while
`v0 notin S(v1)`.

Thus `S(v2) cap S(v8)` contains both `v0` and `v1`. But `v0` and `v1` lie on
the same open cyclic arc between `v2` and `v8`, contradicting the
crossing-bisector rule for two common witnesses. Therefore the `n = 9`
borderline is impossible, and any counterexample with an adjacent closest pair
has `n >= 10`.

The finite row-level boundary can also be replayed by:

```bash
python scripts/check_adjacent_closest_pair_nonagon_barrier.py --check --summary-json
```

This checker enumerates the possible selected rows at centers `0`, `1`, `2`,
and `8` under the closest-pair endpoint exclusions, the two-circle row-pair
cap, and the two-overlap crossing rule. It verifies that all `5,760` partial
boundary assignments are rejected by the final `S(v2),S(v8)` row-pair check.
It is a combinatorial audit of this conditional subcase only.

## Scope

These are weaker than a global contradiction. The radius barrier only says that
closest-pair endpoints cannot witness badness at the minimum intervertex
distance. In a counterexample, such vertices would need a separate four-rich
distance class at a larger radius.

The adjacent-pair consequence is conditional: a closest pair in a strictly
convex polygon need not be a polygon side. It rules out only all-bad nonagons
whose global closest-pair distance is attained by an adjacent pair. It does not
prove `n = 9`, does not promote the review-pending finite-case artifacts, and
does not prove Erdos Problem #97.
