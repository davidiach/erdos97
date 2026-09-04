# Boundary-detour distance forest lemma

Status: `PAPER_PROOF_CANDIDATE / REVIEW_PENDING`.

This note records a geometric strengthening of the alternate-vertex perimeter
obstruction in `docs/alternate-vertex-perimeter-obstruction.md`. It is a
restricted lemma, not a proof or disproof of Erdős Problem #97 and not a
source-of-truth status update.

## Statement

Let

\[
P=(v_0,v_1,\ldots,v_{n-1})
\]

be a strictly convex polygon in cyclic order. Let `X` be a subset of its
vertices with no two members consecutive on the boundary. Fix `r>0`.

Write the members of `X` in inherited cyclic order. Assume that every boundary
arc of `P` between consecutive members of `X` has total Euclidean length at
least `2r`.

Form the graph `H_r(X)` whose vertices are `X` and whose edges are the pairs at
Euclidean distance exactly `r`.

> **Boundary-detour distance forest lemma.** `H_r(X)` is a forest.

The hypothesis concerns the length of each boundary detour, not the individual
side lengths. In particular, sides elsewhere in the polygon may be shorter
than `r`.

## Step 1: a sparse-subpolygon perimeter bound

Write

\[
X=\{x_0,x_1,\ldots,x_{s-1}\}
\]

in inherited cyclic order. For the boundary arc from `x_i` to `x_{i+1}`, let

- `L_i` be its total Euclidean length; and
- `sigma_i` be the sum of the exterior turns at the vertices strictly inside
  that arc.

Indices are cyclic. Since `X` contains no consecutive polygon vertices, every
arc has at least one internal vertex and hence `sigma_i>0`.

The directions of the boundary edges on one arc rotate monotonically through
an angular range `sigma_i`. If `0<sigma_i<pi`, project all of those edges onto
the bisector of their direction interval. Every projected edge retains at
least the factor `cos(sigma_i/2)`, so

\[
|x_i x_{i+1}|
 \ge L_i\cos(\sigma_i/2)
 \ge 2r\cos(\sigma_i/2).
\]

For `0<t<pi`, strict concavity of cosine on `[0,pi/2]` gives

\[
\cos(t/2)>1-t/\pi.
\]

If `sigma_i=pi`, the chord is positive while the right-hand side below is
zero. If `sigma_i>pi`, that right-hand side is negative. Thus in every case

\[
|x_i x_{i+1}|>2r\left(1-\frac{\sigma_i}{\pi}\right).       \tag{1}
\]

The internal vertices of the arcs partition the vertices of `P` outside `X`.
Consequently

\[
\sum_i\sigma_i
 =2\pi-\sum_{x\in X}\tau_x
 <2\pi,
\]

because every exterior turn `tau_x` at a member of `X` is positive. Summing
(1) gives

\[
\operatorname{per}(X)
  >2r\left(s-\frac1\pi\sum_i\sigma_i\right)
  >2r(s-2).                                             \tag{2}
\]

Here `per(X)` is the perimeter of the convex polygon on `X` in inherited
order.

### Boundary-detour perimeter lemma

Equation (2) proves the reusable intermediate statement:

> If each boundary detour between consecutive members of a
> boundary-independent `s`-vertex set has length at least `2r`, then the
> convex-hull perimeter of that set is greater than `2r(s-2)`.

The same hypothesis remains true after passing from `X` to a subset `Y`: a
boundary arc between consecutive members of `Y` is a union of one or more of
the original arcs and therefore still has length at least `2r`.

## Step 2: triangles of `r`-edges are impossible

Suppose three members `A,B,C` of `X` are pairwise at distance `r`. Pass to the
subset `Y={A,B,C}`. Each of its three boundary arcs has length at least `2r`.
Let one such arc have internal turn `sigma`.

If `sigma<pi`, the same projection argument gives

\[
r=|AB|\ge 2r\cos(\sigma/2),
\]

and hence

\[
\sigma\ge 2\pi/3.
\]

If `sigma\ge pi`, the same lower bound is automatic. Thus all three arc-turn
sums are at least `2pi/3`, so their sum is at least `2pi`.

But those three sums omit the positive exterior turns at `A,B,C`; their total
is therefore strictly less than `2pi`. This contradiction rules out a
triangle in `H_r(X)`.

## Step 3: longer cycles are impossible

Assume `H_r(X)` has a simple cycle of length `g>=4`, and let `Y` be its vertex
set. The boundary-detour hypothesis survives passage to `Y`, so (2) gives

\[
\operatorname{per}(Y)>2r(g-2).
\]

The graph cycle is a closed polygonal tour through every point of `Y`, of total
length exactly `gr`. The perimeter of the convex hull of finitely many points
is no greater than the length of any closed polygonal tour visiting those
points. Therefore

\[
\operatorname{per}(Y)\le gr.
\]

For `g>=4`,

\[
2(g-2)\ge g,
\]

with equality only at `g=4`. Hence

\[
\operatorname{per}(Y)>2r(g-2)\ge gr,
\]

contradicting the cycle tour. Together with Step 2, this proves that `H_r(X)`
has no cycle and is a forest.

## Useful minimum-side corollary

If every side of `P` has length at least `r`, then any boundary-independent
set automatically satisfies the detour hypothesis: each arc contains at least
two boundary edges and therefore has length at least `2r`.

Thus the earlier formulation remains valid as a direct corollary:

> In a strictly convex polygon whose sides all have length at least `r`, the
> graph of distance-`r` edges on any boundary-independent vertex set is a
> forest.

## Erdős-97 corollary: every radius level is a forest

Consider a strictly convex polygon in alternating notation

\[
E_0,Q_0,E_1,Q_1,\ldots,E_{m-1},Q_{m-1}.
\]

Suppose each `E_i` has a selected radius `rho_i` whose distance class contains
both boundary neighbours:

\[
|E_iQ_{i-1}|=|E_iQ_i|=\rho_i.
\]

Fix an arbitrary radius value `R` and put

\[
X_R=\{E_i:\rho_i=R\}.
\]

The set `X_R` is boundary-independent. More importantly, every boundary arc
between consecutive members of `X_R` begins with an edge of length `R` leaving
its first centre and ends with an edge of length `R` entering its second
centre. Its total length is therefore at least `2R`, regardless of the side
lengths or selected radii at the intermediate vertices.

Applying the lemma with `r=R` gives:

> **Radius-level reciprocal-forest corollary.** For every `R`, the graph on
> `X_R` joining pairs at distance `R` is a forest.

This is the full same-radius distance graph, not merely a chosen selected-edge
subgraph. If two centres in `X_R` are distance `R` apart, each belongs to the
other centre's complete radius-`R` class. Any selected reciprocal graph at
that radius is therefore a subgraph of this forest.

Consequently every nontrivial same-radius component has a centre with at most
one same-radius reciprocal neighbour. In particular:

1. if every `E_i` has one common selected radius and at least two additional
   `E`-witnesses at that radius, the resulting graph has minimum degree at
   least two, contradicting the forest lemma;
2. if a connected reciprocal selected graph on the `E_i` has minimum degree
   at least two, reciprocal edges propagate one common radius through the
   component and the same contradiction follows; and
3. the coprime step-`k` Hamiltonian pattern from
   `docs/alternate-vertex-perimeter-obstruction.md` is a special case, since
   its reciprocal graph is already a cycle.

## Cross-radius escape forced by the lemma

The corollary also identifies the exact escape from the common-radius route.
Suppose every centre `E_i` has at least two additional witnesses among the
other `E`-vertices. At a leaf or isolated vertex of each same-radius forest,
at least one of those witnesses must have a *different selected radius* from
the centre. Thus any surviving configuration must export witness incidences
between distinct radius levels.

This is genuine variable-radius information: a proof can no longer close the
alternating-boundary-neighbour branch by analysing one radius level in
isolation. It must control the directed cross-radius dependency graph.

## What this advances—and what remains open

The earlier terminal required a specified Hamiltonian reciprocal cycle and a
common radius propagated along it. The new lemma removes Hamiltonicity,
fixed-step symmetry, global side-length lower bounds, and the common-radius
assumption. It applies independently at every selected-radius level.

The remaining extraction problem is still substantial. In an arbitrary
hypothetical counterexample:

- a rich distance class need not contain both boundary neighbours;
- the two non-boundary witnesses need not lie in one boundary-independent
  centre set; and
- cross-radius witness dependencies can be one-way, so the forest conclusion
  alone does not create a cycle at one fixed radius.

The next proof target is therefore a geometric restriction on those
cross-radius exports—for example, a fan-in bound, an ordered dependency-cycle
obstruction, or a forced return to one radius level. None of those statements
is claimed here.

## Arithmetic replay

The companion command checks the exact coefficient spine used after the two
geometric projection steps:

```bash
python scripts/check_sparse_minimum_distance_forest.py \
  --assert-expected --summary-json
```

It verifies symbolically that the long-cycle margin is

```text
2*(g-2)-g = g-4 >= 0  for every g >= 4,
```

and records the normalized triangle turn budget

```text
3*(1/3) = 1,
```

against the strict total-turn upper bound. This replay is not a formal proof
of the projection lemma; the complete paper proof is the argument above.
