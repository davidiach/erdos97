# Prompt 0 local output: method-free control

Status: partial progress only. No proof or counterexample is claimed.

Let

```text
m_i(P)=max_{r>0} #{j != i : |p_j-p_i|=r}.
```

The target statement is that every strictly convex finite polygon has some
vertex i with m_i(P) <= 3.

## A local obstruction to naive proofs

It is possible for a single vertex of a strictly convex polygon to have four
other vertices at one common distance. Put p_0=(0,0) and, for angles

```text
-60 deg < theta_1 < theta_2 < theta_3 < theta_4 < 60 deg,
```

put q_t=(cos theta_t, sin theta_t). For a sufficiently separated choice of the
four angles, the polygon

```text
p_0, q_1, q_2, q_3, q_4
```

in this cyclic order is strictly convex: the q_t form a strictly convex arc of
the unit circle and p_0 lies strictly outside the chordal hull of that arc.
Every q_t is at distance 1 from p_0. Thus a proof cannot show that every vertex
has multiplicity at most three. The obstruction, if true, is necessarily global.

## Selected-cohort reduction

Assume for contradiction that P is bad, so m_i(P) >= 4 for every i. For each i,
choose a radius r_i for which

```text
S_i={j != i : |p_j-p_i|=r_i}
```

has size at least four. If necessary, choose an arbitrary four-subset of this
set; this gives a pointed four-uniform system (i;S_i).

The selected system satisfies the following exact constraints.

Lemma 1, self-exclusion. i is not in S_i.

This is immediate from the definition j != i.

Lemma 2, pairwise intersection. If i != k, then |S_i cap S_k| <= 2.

Proof. S_i is contained in the circle centered at p_i with radius r_i, and
S_k is contained in the circle centered at p_k with radius r_k. Since p_i != p_k,
the two circles are distinct. Two distinct circles in the plane intersect in at
most two points. Hence they contain at most two common vertices of P.

Lemma 3, two-shared-cohort crossing. Suppose S_i cap S_k contains two distinct
indices a,b. Then the cyclic pair {i,k} separates the cyclic pair {a,b}.

Proof. The points p_a and p_b are the two intersections of the circles centered
at p_i and p_k. In coordinates with p_i and p_k on the x-axis, the equations of
the two circles subtract to give a linear equation x=c. Thus p_a and p_b have
the same projection to the line p_i p_k and opposite signed distances from that
line. Equivalently, they are reflections across the line p_i p_k.

Here strict convexity is load-bearing: for a chord p_i p_k of a strictly convex
polygon, every other vertex lies strictly in one of the two open half-planes
cut out by the line p_i p_k, and the two open arcs between i and k in the cyclic
order lie on opposite sides of that line. Since p_a and p_b lie on opposite
sides, they lie on opposite cyclic arcs between i and k. This is exactly the
separation statement.

## Strongest theorem obtained

The method-free attempt proves only this reduction:

If a counterexample to the target statement exists, then there exists a cyclic
pointed four-uniform hypergraph with one edge (i;S_i) at each vertex satisfying
self-exclusion, pairwise intersection at most two, and the two-shared-cohort
crossing rule.

This is not enough to prove a contradiction. The missing step is a global
classification or discharging theorem for such cyclic pointed four-uniform
systems, plus a metric realization test for surviving systems.

## Load-bearing hypotheses

Strict convexity is used only in Lemma 3, where sides of a chord correspond to
cyclic arcs. Finiteness is used to select maximum radii. Planarity is used in
the two-circle intersection bound. The centered-on-vertex condition is used in
both the circle-intersection bound and the crossing lemma; without fixed centers
at vertices, the selected incidence system loses its strongest constraints.
