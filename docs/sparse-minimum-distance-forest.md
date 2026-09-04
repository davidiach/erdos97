# Boundary-detour distance forest and fan-in lemmas

Status: `PAPER_PROOF_CANDIDATE / REVIEW_PENDING`.

This note records geometric strengthenings of the alternate-vertex perimeter
obstruction in `docs/alternate-vertex-perimeter-obstruction.md`. They are
restricted lemmas, not a proof or disproof of Erdős Problem #97 and not a
source-of-truth status update.

## 1. Boundary-detour distance forest

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
side lengths. Sides elsewhere in the polygon may be shorter than `r`.

### Step 1: a sparse-subpolygon perimeter bound

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

Equation (2) is a reusable intermediate statement:

> **Boundary-detour perimeter lemma.** If each boundary detour between
> consecutive members of a boundary-independent `s`-vertex set has length at
> least `2r`, then the convex-hull perimeter of that set is greater than
> `2r(s-2)`.

The same hypothesis remains true after passing from `X` to a subset `Y`: a
boundary arc between consecutive members of `Y` is a union of one or more of
the original arcs.

### Step 2: triangles of `r`-edges are impossible

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
is strictly less than `2pi`. This contradiction rules out a triangle in
`H_r(X)`.

### Step 3: longer cycles are impossible

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

### Minimum-side corollary

If every side of `P` has length at least `r`, then any boundary-independent
set automatically satisfies the detour hypothesis: each arc contains at least
two boundary edges and therefore has length at least `2r`.

Thus:

> In a strictly convex polygon whose sides all have length at least `r`, the
> graph of distance-`r` edges on any boundary-independent vertex set is a
> forest.

## 2. A common target has fan-in at most three

The detour hypothesis also bounds how many vertices of `X` can lie on one
circle centered at another polygon vertex.

> **Boundary-detour fan-in lemma.** Under the hypotheses above, fix a polygon
> vertex `z` outside `X`. At most three vertices `x` in `X` can satisfy
> `|zx|=r`.

### Proof

Suppose `y_1,...,y_k` are the members of `X` at distance `r` from `z`, listed
along the boundary chain that does not pass through `z`.

A fan triangulation from the strictly convex vertex `z` shows that the rays
`zy_i` occur in the same order and lie in the open interior-angle cone at `z`.
Let

\[
\alpha_i=\angle y_i z y_{i+1}\qquad(1\le i<k).
\]

Then every `alpha_i>0` and

\[
\sum_{i=1}^{k-1}\alpha_i<\pi.                            \tag{3}
\]

The boundary arc from `y_i` to `y_{i+1}` avoiding `z` is a union of one or
more consecutive `X`-arcs, so its length is at least `2r`. Let its internal
turn be `sigma_i`. If `sigma_i<pi`, projection along that arc and the chord
formula on the circle centered at `z` give

\[
2r\sin(\alpha_i/2)
 =|y_i y_{i+1}|
 \ge2r\cos(\sigma_i/2).
\]

Both half-angles lie in `[0,pi/2]`, hence

\[
\sigma_i\ge\pi-\alpha_i.
\]

The same conclusion is automatic when `sigma_i\ge pi`. Summing and using (3),

\[
\sum_{i=1}^{k-1}\sigma_i
 \ge(k-1)\pi-\sum_{i=1}^{k-1}\alpha_i
 >(k-2)\pi.                                             \tag{4}
\]

The arcs in (4) are disjoint portions of the polygon boundary, so their
internal turns sum to less than `2pi`. If `k>=4`, (4) is already greater than
or equal to `2pi`, a contradiction. Therefore `k<=3`. `QED`

The value three is only an upper bound from this argument; no sharpness claim
is made.

## 3. Erdős-97 radius-level consequences

Consider a strictly convex polygon in alternating notation

\[
E_0,Q_0,E_1,Q_1,\ldots,E_{m-1},Q_{m-1}.
\]

Suppose each `E_i` has a rich radius `rho_i` whose complete distance class
contains both boundary neighbours:

\[
|E_iQ_{i-1}|=|E_iQ_i|=\rho_i.
\]

Fix an arbitrary radius value `R` and put

\[
X_R=\{E_i:\rho_i=R\}.
\]

The set `X_R` is boundary-independent. Every boundary arc between consecutive
members of `X_R` begins with an edge of length `R` leaving its first centre and
ends with an edge of length `R` entering its second centre. Its total length is
therefore at least `2R`, regardless of intermediate side lengths or radii.

Applying the two lemmas with `r=R` gives:

1. **Radius-level reciprocal forest.** The graph on `X_R` joining pairs at
   distance `R` is a forest.
2. **Radius-level fan-in cap.** Any polygon vertex outside `X_R` is at distance
   `R` from at most three members of `X_R`.

The first graph is the full same-radius distance graph, not merely a chosen
selected-edge subgraph. If two centres in `X_R` are distance `R` apart, each
belongs to the other centre's complete radius-`R` class.

Consequently every nontrivial same-radius component has a centre with at most
one same-radius reciprocal neighbour. The coprime step-`k` Hamiltonian pattern
from `docs/alternate-vertex-perimeter-obstruction.md` is a special case, since
its same-radius graph is already a cycle.

### Exact export accounting

Let `n_R=|X_R|`, and let the radius-`R` forest have `c_R` connected components.
Assume each centre has at least `d>=2` non-boundary witnesses at distance `R`.
This is automatic with `d=2` when its rich class has size at least four and its
two boundary neighbours are already in that class.

The forest has at most `n_R-c_R` internal edges. Internal edges account for at
most `2(n_R-c_R)` centre-to-witness incidences. Therefore the number `B_R` of
incidences from centres in `X_R` to vertices outside `X_R` obeys

\[
B_R\ge d n_R-2(n_R-c_R)
     =(d-2)n_R+2c_R.                                   \tag{5}
\]

For the Erdős threshold `d=2`, every same-radius forest component exports at
least two incidences in aggregate:

\[
B_R\ge2c_R.                                             \tag{6}
\]

By the fan-in cap, one outside target absorbs at most three of those incidences.
Thus at least

\[
\left\lceil\frac{(d-2)n_R+2c_R}{3}\right\rceil          \tag{7}
\]

distinct outside targets are required.

This accounting is deliberately careful about what “outside” means. A target
outside `X_R` may be

- another `E`-vertex with a different selected radius; or
- a `Q`-vertex, possibly with the same selected radius.

Thus (5)--(7) force export from the same-radius `E`-forest, but they do **not**
unconditionally force a change of radius. If the non-boundary witnesses are
known separately to lie among the `E`-vertices, then every exported target does
have a different selected radius and the bounds become genuine cross-radius
bounds.

## 4. Three consecutive centres cannot share one extra witness

There is a further local restriction in the alternating setting.

> **Consecutive-three common-witness lemma.** Let three consecutive alternate
> centres `U,V,Z` have the same selected radius `R`. Let `A` be the boundary
> vertex between `U,V`, and `B` the boundary vertex between `V,Z`. There is no
> polygon vertex `W`, distinct from `A,B`, such that
>
> \[
> |WU|=|WV|=|WZ|=R.
> \]

### Proof

Translate `W` to the origin, scale `R` to one, and rotate so that
`V=(1,0)`. Since `W` is a strictly convex polygon vertex, the rays from `W` to
`U,V,Z` occur in their boundary order inside an angle strictly smaller than
`pi`. Hence for some `a,b>0` with `a+b<pi`,

\[
U=(\cos a,-\sin a),\qquad Z=(\cos b,\sin b).
\]

The points `W` and `A` are the two intersections of the unit circles centered
at `U,V`. Therefore

\[
A=U+V-W=U+V.
\]

Likewise

\[
B=V+Z.
\]

Put

\[
D=\sin a+\sin b+\sin(a+b)>0,
\]

and

\[
\lambda=\frac{\sin b}{D},\qquad
\mu=\frac{\sin a}{D}.
\]

A direct coordinate calculation gives

\[
\lambda A+\mu B=V.
\]

Moreover `lambda,mu>0` and

\[
\lambda+\mu
 =\frac{\sin a+\sin b}{D}<1
\]

because `sin(a+b)>0`. Thus

\[
V=\lambda A+\mu B+(1-\lambda-\mu)W
\]

is a strict convex combination of the three other polygon vertices `A,B,W`.
This contradicts strict convexity. `QED`

In particular, one outside target cannot absorb three *extra* radius-`R`
witness incidences from three consecutive `R`-centres: being extra at all
three centres ensures it is distinct from the intervening boundary vertices.

## 5. What this advances—and what remains open

The earlier terminal required a specified Hamiltonian reciprocal cycle and a
common radius propagated along it. The forest lemma removes Hamiltonicity,
fixed-step symmetry, global side-length lower bounds, and the common-radius
assumption. It applies independently at every selected-radius level. The
fan-in and export lemmas additionally prevent unlimited concentration at one
outside witness.

The remaining extraction problem is still substantial. In an arbitrary
hypothetical counterexample:

- a rich distance class need not contain both boundary neighbours;
- its non-boundary witnesses need not lie in one parity class; and
- same-radius forest exports can move to the opposite parity without changing
  radius, or can form one-way dependencies between different radii.

The next proof target is a geometric restriction on those exports—for example,
a stronger target-capacity theorem, an ordered dependency-cycle obstruction,
or a minimal-counterexample argument forcing enough rows into the
boundary-neighbour branch. None of those statements is claimed here.

## 6. Arithmetic replay

The companion command checks the exact coefficient spine used after the
geometric projection steps and the export-count formula:

```bash
python scripts/check_sparse_minimum_distance_forest.py \
  --assert-expected --summary-json
```

It verifies symbolically that

```text
2*(g-2)-g = g-4 >= 0  for every g >= 4,
3*(1/3) = 1,
d*n - 2*(n-c) = (d-2)*n + 2*c,
```

and records the fan-in threshold `4 -> contradiction`. This replay is not a
formal proof of the projection or angular-order lemmas; the complete paper
proofs are the arguments above.
