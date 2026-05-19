# Closest-Pair Radius Barrier

Status: `LEMMA` / structural necessary condition.

This note records a small exact obstruction for the global closest-pair
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

## Proof

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

## Scope

This is weaker than a global contradiction. It only says that closest-pair
endpoints cannot witness badness at the minimum intervertex distance. In a
counterexample, such vertices would need a separate four-rich distance class at
a larger radius.
