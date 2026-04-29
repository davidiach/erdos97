# Corrected synthesis of the ten prompt outputs

Date: 2026-04-29

Status: reviewed research artifact only. No complete proof and no
counterexample to Erdos Problem #97 are claimed here.

## Verdict

None of the ten outputs gives a valid complete proof or counterexample for the
full problem.

The strongest reliable partial outputs are Outputs 8 and 9. Outputs 6 and 7
also contain useful standalone lemmas. Output 10 must be rejected as a proof:
its central supporting-tangent lemma is false.

## Reliable components

### Favorite-distance reformulation

The original problem is equivalent to the following selected-radius statement.

For every assignment of one positive radius rho_i to each vertex p_i of a
strictly convex polygon, at least one assigned circle

```text
C_i = {x : |x-p_i| = rho_i}
```

contains at most three vertices of P \ {p_i}.

This is a logical equivalence, not a simplification by itself. If every vertex
were bad, choose one rich radius at each vertex. Conversely, a vertex that is
good for every radius is good for every selected radius.

### Common-witness rigidity

If two distinct centers x,y are both equidistant from the same three
non-collinear points a,b,c, then x=y, because a nondegenerate triangle has a
unique circumcenter.

Since a strictly convex polygon has no three collinear vertices, any selected
four-cohorts S_i,S_j in a hypothetical counterexample satisfy

```text
|S_i cap S_j| <= 2      for i != j.
```

This is one of the core exact incidence constraints.

### Small cases n <= 6

The theorem is true for n <= 6.

For n <= 4 this is immediate. For n=5, if every vertex were bad, each vertex
would be equidistant from all four other vertices. Taking any two centers, the
remaining three vertices would be common witnesses, contradicting
common-witness rigidity.

For n=6, suppose every vertex is bad and choose one rich radius at each vertex.
No vertex can have all five other vertices at that radius: if p did, then any
other bad vertex q would need four witnesses, at least three of which lie on
the circle centered at p, again contradicting common-witness rigidity.

Thus each row has exactly four selected witnesses and one exceptional vertex.
Write

```text
S_i = P \ {p_i, p_{f(i)}}.
```

The map f has no fixed points. If f has a 2-cycle i <-> j, then S_i and S_j
share the four vertices P \ {p_i,p_j}, contradicting |S_i cap S_j| <= 2.
If f has no 2-cycle, then because f is a finite fixed-point-free map, it has a
directed cycle of length at least 3. For consecutive vertices i -> j -> k in
that cycle,

```text
S_i = P \ {p_i,p_j}
S_j = P \ {p_j,p_k}
```

and these two selected sets share the three vertices P \ {p_i,p_j,p_k}, again
contradicting |S_i cap S_j| <= 2.

Therefore no all-bad strictly convex polygon exists for n=6.

### Middle-angle lemma

Let p be a bad vertex, and let q_1,...,q_m be equal-distance witnesses ordered
by the boundary chain after removing p. For each middle index 2 <= t <= m-1,
the polygonal interior angle at q_t is greater than pi/2.

More quantitatively, if q_{t-1},q_t,q_{t+1} subtend angle theta at p through
q_t, then

```text
epsilon(q_t) <= theta/2,
```

where epsilon is the exterior angle.

This is a valid local restriction. It is not enough by itself, because large
convex polygons can have many obtuse vertices.

### Safe exterior-angle descent

The reviewed outputs support the weaker local descent

```text
p bad => some witness w has epsilon(w) < (pi - epsilon(p)) / 2.
```

The stronger claimed bound

```text
epsilon(w) <= (pi - epsilon(p)) / 3
```

from Output 1 is not justified in general and should not be used.

### Minimal-counterexample indispensability

If a counterexample exists, choose one with the minimum number of vertices.
Then every vertex v is indispensable for some other center u: after deleting v,
some remaining vertex u becomes good, while in the original polygon u was bad.
Therefore v lies in an exact four-cohort centered at u.

The stronger repaired form is:

```text
In a minimal counterexample, every vertex v lies in the unique four-cohort
of at least one fragile center u.
```

The uniqueness follows because every rich radius of u in the original polygon
must contain v; a fixed vertex v has only one distance from u.

This gives a real dependency structure, but it is not a contradiction by
itself.

### Parabola model case

For points

```text
p(t_i) = (t_i, t_i^2)
```

with distinct real t_i, the vertex with minimal |t_i| is good.

For fixed t, the squared distance to p(u) is

```text
|p(u)-p(t)|^2 = (u-t)^2 (1 + (u+t)^2).
```

If four other parameters a,b,c,d were at one common distance from p(t), then
they would be the four roots of a quartic with zero cubic coefficient, so

```text
a + b + c + d = 0.
```

Vieta's formula also gives

```text
a^2 + b^2 + c^2 + d^2 = 4t^2 - 2.
```

If |t| is minimal among the parameters, then the left side is at least 4t^2,
a contradiction. Hence p(t) is good.

The convex-position justification is that finite points on the strictly convex
graph y=x^2, ordered by t and closed by the endpoint chord, are all hull
vertices.

## Rejected or corrected claims

### Output 10 is not a proof

Output 10 claimed that if y is a middle point of an equal-radius set centered
at x, then the tangent at y to that circle is a supporting line of the whole
polygon. This is false.

One explicit counterexample is:

```text
x = (0,0)
a = (1/2, -sqrt(3)/2)
y = (1,0)
z = (11/10, 3/10)
b = (1/2, sqrt(3)/2)
c = (0,1)
```

in cyclic order

```text
x, a, y, z, b, c.
```

The vertices form a strictly convex hexagon. The points a,y,b,c all lie on the
unit circle centered at x, and y is a middle element of that equal-radius set.
But the tangent at y is X=1, while z has X=11/10. Thus the tangent is not a
supporting line of the polygon.

Therefore Output 10's Lemma 2, Lemma 3, and final middle-incidence count all
collapse.

### Output 1's alpha/3 descent is not established

The claimed descent

```text
epsilon(q) <= (pi - epsilon(p)) / 3
```

depends on choosing a small middle gap among four witnesses. But the middle
gap can be large, for example in a gap pattern like

```text
0.1, 0.8, 0.1.
```

The safe general bound from this local method is the weaker alpha/2 form above.

### Output 2 has a false chord-length claim

For two points on a circle of radius r separated by central angle theta, the
chord length is

```text
2r sin(theta/2).
```

It is less than r only when theta < pi/3, not merely when theta < pi.

### Output 5's n=6 proof is not acceptable

The middle-angle lemma is valid, but Output 5's n=6 proof uses an unsupported
claim that a vertex can be a middle witness at most once. That kind of claim is
unsafe and is invalid in the stronger tangent-support form used in Output 10.

The n <= 6 proof should instead use the exception-map argument recorded above.

### Output 8's diameter example is mislabeled

The displayed bad vertices in Output 8 are not actually diameter endpoints for
the stated parameters. The example may still show two specified bad vertices,
but it should not be used as a diameter-endpoint counterexample.

### Output 9's alternating octagon discussion has a multiplicity error

The equality discussed there gives only three vertices at the target distance
from the coordinate-axis vertex, not four. The octagon discussion should be
treated only as a failed search note after correction.

## Best current obstruction

After correction, the strongest useful formulation is:

Can a finite strictly convex polygon support selected four-cohorts S_i at every
vertex such that:

```text
|S_i| = 4,
i notin S_i,
all points of S_i are equidistant from p_i,
|S_i cap S_j| <= 2 for i != j,
and the fragile-cover dependency from minimality can be satisfied?
```

The known local angle facts and the n <= 6 argument do not rule this out for
all n. A full proof still needs a genuinely global incidence, cyclic-order, or
metric rigidity argument.

## Recommended next directions

1. Use Outputs 8 and 9 as the base partial write-up.
2. Add the parabola model case from Output 6.
3. Add the minimal-counterexample fragile-cover lemma from Output 7.
4. Treat Output 10 as a failed proof route with the explicit tangent-support
   counterexample above.
5. Do not use the alpha/3 descent, the false chord claim, the mislabeled
   diameter example, or the octagon multiplicity claim.
