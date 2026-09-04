# Sparse minimum-distance forest lemma

Status: `PAPER_PROOF_CANDIDATE / REVIEW_PENDING`.

This note records a geometric strengthening of the alternate-vertex perimeter
obstruction in `docs/alternate-vertex-perimeter-obstruction.md`.  It is a
restricted lemma, not a proof or disproof of Erdos Problem #97 and not a
source-of-truth status update.

## Statement

Let

\[
P=(v_0,v_1,\ldots,v_{n-1})
\]

be a strictly convex polygon in cyclic order.  Fix `r > 0` and assume every
boundary side of `P` has length at least `r`.

Let `X` be a subset of the vertices such that no two members of `X` are
consecutive on the boundary of `P`.  Form the graph `H_r(X)` whose vertices are
`X` and whose edges are the pairs at Euclidean distance exactly `r`.

> **Sparse minimum-distance forest lemma.**  `H_r(X)` is a forest.

The name refers only to the side-length lower bound.  The number `r` need not
be the minimum of all pairwise distances in the polygon.

## Step 1: a sparse-subpolygon perimeter bound

Write the members of `X` in inherited cyclic order as

\[
x_0,x_1,\ldots,x_{s-1}.
\]

For the boundary arc from `x_i` to `x_{i+1}`, let

- `k_i` be its number of boundary edges; and
- `sigma_i` be the sum of the exterior turns at the vertices strictly inside
  that arc.

Indices are cyclic.  Since `X` contains no consecutive polygon vertices,

\[
k_i\ge 2.
\]

All exterior turns are positive.  The directions of the edges on one boundary
arc therefore rotate monotonically through an angular range `sigma_i`.

If `0 < sigma_i < pi`, project the arc edges onto the bisector of that angular
range.  Every projected edge has length at least

\[
r\cos(\sigma_i/2),
\]

so

\[
|x_i x_{i+1}|
 \ge k_i r\cos(\sigma_i/2)
 \ge 2r\cos(\sigma_i/2).
\]

On `0 < t < pi`, strict concavity of cosine on the relevant interval gives

\[
\cos(t/2)>1-t/\pi.
\]

If `sigma_i = pi`, the chord is positive while the right-hand side below is
zero.  If `sigma_i > pi`, the right-hand side is negative.  Hence in every
case

\[
|x_i x_{i+1}|>2r\left(1-\frac{\sigma_i}{\pi}\right).       \tag{1}
\]

The internal vertices of these arcs partition the vertices of `P` outside
`X`.  Consequently

\[
\sum_i\sigma_i
 =2\pi-\sum_{x\in X}\tau_x
 <2\pi,
\]

where `tau_x > 0` is the exterior turn at `x`.  Summing (1) yields

\[
\operatorname{per}(X)
  >2r\left(s-\frac1\pi\sum_i\sigma_i\right)
  >2r(s-2).                                             \tag{2}
\]

Here `per(X)` is the perimeter of the convex polygon on the vertices of `X` in
inherited order.

### Sparse-subpolygon perimeter lemma

Equation (2) proves the reusable intermediate statement:

> If all boundary sides of a strictly convex polygon have length at least
> `r`, then every boundary-independent `s`-vertex subset has convex-hull
> perimeter greater than `2r(s-2)`.

No equal-distance hypothesis is used in this step.

## Step 2: triangles of `r`-edges are impossible

Suppose three members `A,B,C` of `X` are pairwise at distance `r`.  The three
boundary arcs cut out by `A,B,C` each contain at least two boundary edges.
Let one such arc have `k >= 2` edges and internal turn `sigma`.

If `sigma <= pi`, projection onto the angular bisector gives

\[
r=|AB|\ge kr\cos(\sigma/2)\ge2r\cos(\sigma/2),
\]

and therefore

\[
\sigma\ge 2\pi/3.
\]

If `sigma > pi`, the same lower bound is automatic.  Thus all three arc-turn
sums are at least `2*pi/3`, so their sum is at least `2*pi`.

But those three internal-turn sums omit the positive exterior turns at
`A,B,C`, and hence their sum is strictly less than `2*pi`.  This contradiction
rules out a triangle in `H_r(X)`.

## Step 3: longer cycles are impossible

Assume `H_r(X)` has a simple cycle of length `g >= 4`, and let `Y` be the set
of its `g` vertices.  The set `Y` is still boundary-independent, so (2) gives

\[
\operatorname{per}(Y)>2r(g-2).
\]

The graph cycle is a closed polygonal tour through every point of `Y`, and its
length is exactly `gr`.  The perimeter of the convex hull of finitely many
points is no greater than the length of any closed polygonal tour visiting
those points.  Therefore

\[
\operatorname{per}(Y)\le gr.
\]

For `g >= 4`,

\[
2(g-2)\ge g,
\]

with equality only at `g=4`.  The strict perimeter lower bound gives

\[
\operatorname{per}(Y)>2r(g-2)\ge gr,
\]

contradicting the cycle tour.  Together with Step 2, this proves that
`H_r(X)` has no cycle and is a forest.

## Erdős-97 corollary: the minimum-radius reciprocal layer is a forest

Consider a strictly convex polygon in alternating notation

\[
E_0,Q_0,E_1,Q_1,\ldots,E_{m-1},Q_{m-1}.
\]

Suppose each `E_i` has a selected radius `rho_i` whose distance class contains
both boundary neighbours `Q_{i-1}` and `Q_i`:

\[
|E_iQ_{i-1}|=|E_iQ_i|=\rho_i.
\]

Set

\[
r=\min_i\rho_i.
\]

Every boundary edge has length one of the `rho_i`, hence at least `r`, and the
set of all `E_i` is boundary-independent.  The lemma therefore gives:

> The graph on the alternate vertices `E_i` joining every pair at distance
> exactly `r` is a forest.

In particular, the reciprocal selected graph induced by centres whose selected
radius equals the global minimum `r` is a subgraph of a forest.  Every
nontrivial component has a vertex of reciprocal degree at most one.

Two useful consequences follow immediately.

1. If all `rho_i` are equal to one common value and every `E_i` has at least
   two additional `E`-witnesses at that radius, the resulting distance graph
   has minimum degree at least two, contradicting the forest lemma.
2. More generally, if the reciprocal selected graph on all `E_i` is connected
   and has minimum degree at least two, reciprocal edges propagate one common
   radius through the graph, reducing to consequence 1.

The coprime step-`k` Hamiltonian pattern from
`docs/alternate-vertex-perimeter-obstruction.md` is a special case: its
reciprocal graph is already a cycle.

## What this advances

The earlier terminal required a specified Hamiltonian reciprocal cycle.  The
new lemma removes both the Hamiltonicity and the fixed-step assumptions, and it
allows the selected radii away from the minimum layer to vary arbitrarily.

The remaining extraction problem is still substantial.  In an arbitrary
hypothetical counterexample:

- a rich distance class need not contain both boundary neighbours;
- its two remaining witnesses need not lie in the alternate centre set; and
- a minimum-radius centre may point by equal-distance edges to vertices whose
  own selected radii are larger, so the reciprocal minimum layer can be a
  forest without contradicting four-richness.

Thus the lemma forces a one-way escape from some minimum-radius reciprocal
component, but it does not by itself close Erdős #97.

## Arithmetic replay

The companion command checks the exact coefficient spine used after the two
geometric projection steps:

```bash
python scripts/check_sparse_minimum_distance_forest.py --assert-expected --summary-json
```

It verifies symbolically that the long-cycle margin is

```text
2*(g-2)-g = g-4 >= 0  for every g >= 4,
```

and records the normalized triangle turn budget

```text
3*(1/3) = 1,
```

against the strict total-turn upper bound.  This replay is not a formal proof
of the projection lemma; the complete paper proof is the argument above.
