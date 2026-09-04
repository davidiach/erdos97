# Radius-level linear forests and endpoint exports

Status: `PAPER_PROOF_CANDIDATE / REVIEW_PENDING`.

This note strengthens `docs/sparse-minimum-distance-forest.md`. It is a
restricted geometric result, not a proof or disproof of Erdős Problem #97 and
not a source-of-truth status update.

## 1. The detour-controlled distance graph has degree at most two

Use the hypotheses of the boundary-detour distance forest lemma. Thus `X` is a
boundary-independent set of vertices of a strictly convex polygon, `r>0`, and
every boundary arc between consecutive members of `X` has total length at
least `2r`. Let `H_r(X)` join the pairs in `X` at distance exactly `r`.

> **Linear-forest strengthening.** Every vertex of `H_r(X)` has degree at most
> two. Since the earlier lemma proves that `H_r(X)` is a forest, every component
> is a path or an isolated vertex.

There is also a quantitative local conclusion:

> If `x` has two neighbours `y,z` in `H_r(X)`, then
>
> \[
> \angle yxz>\pi/3.
> \]

### Two-neighbour angle bound

List the three vertices in inherited cyclic order as `x,y,z`, reversing the
polygon order if necessary. Let `sigma_0,sigma_1,sigma_2` be the internal
exterior-turn sums on the boundary arcs

\[
x\longrightarrow y,\qquad y\longrightarrow z,\qquad z\longrightarrow x.
\]

Each arc is a union of one or more consecutive `X`-arcs and therefore has
length at least `2r`.

The first and third chords have length `r`. The projection estimate used in
the forest proof gives

\[
\sigma_0\ge2\pi/3,
\qquad
\sigma_2\ge2\pi/3.                                    \tag{1}
\]

Put `alpha=angle yxz`. Since `x` is a strictly convex polygon vertex,
`0<alpha<pi`. The two points `y,z` lie on the circle of radius `r` centered at
`x`, so

\[
|yz|=2r\sin(\alpha/2).
\]

Projection along the middle boundary arc gives

\[
2r\sin(\alpha/2)\ge2r\cos(\sigma_1/2)
\]

when `sigma_1<pi`; the resulting inequality is automatic when
`sigma_1>=pi`. Hence

\[
\sigma_1\ge\pi-\alpha.                                 \tag{2}
\]

The three open-arc turn sums omit the positive exterior turns at `x,y,z`, so

\[
\sigma_0+\sigma_1+\sigma_2<2\pi.
\]

Combining this with (1)--(2) gives

\[
\frac{4\pi}{3}+\pi-\alpha<2\pi,
\]

and therefore `alpha>pi/3`.

### Three neighbours are impossible

Suppose `x` has three distance-`r` neighbours `y_1,y_2,y_3`, listed in their
boundary and angular order away from `x`. Put

\[
\alpha_1=\angle y_1xy_2,
\qquad
\alpha_2=\angle y_2xy_3.
\]

All three rays lie in the open interior-angle cone at `x`, hence

\[
\alpha_1+\alpha_2<\pi.                                 \tag{3}
\]

For the four boundary arcs cut out by

\[
x,y_1,y_2,y_3,
\]

the two end chords have length `r`, so their internal turn sums are at least
`2pi/3`. The two middle arcs have internal turn sums at least
`pi-alpha_1` and `pi-alpha_2`. Their total is therefore greater than

\[
\frac{4\pi}{3}+2\pi-(\alpha_1+\alpha_2)
>\frac{7\pi}{3},
\]

by (3). But the four open-arc turn sums total less than `2pi`, a
contradiction. Thus the degree is at most two.

## 2. Radius-level components are paths

Use the alternating boundary-neighbour setup

\[
E_0,Q_0,E_1,Q_1,\ldots,E_{m-1},Q_{m-1},
\]

where the complete rich class at each `E_i` contains both boundary neighbours
at radius `rho_i`. For a fixed value `R`, put

\[
X_R=\{E_i:\rho_i=R\}.
\]

Every boundary detour between consecutive members of `X_R` has length at least
`2R`. Consequently the full distance-`R` graph on `X_R` is a disjoint union of
paths and isolated vertices, and every angle made by two consecutive edges of
one such path is greater than `60` degrees.

This improves the export bookkeeping from the companion note. At the Erdős
threshold, each centre has at least two non-boundary radius-`R` witnesses.
Therefore:

- every endpoint of a nontrivial radius-level path has at least one witness
  outside `X_R`;
- every isolated vertex has at least two distinct witnesses outside `X_R`;
- internal path vertices may use their two path neighbours as both required
  non-boundary witnesses, but cannot have a third same-level neighbour.

The aggregate bound

\[
B_R\ge2c_R
\]

still holds, where `c_R` is the number of path components, but the incidences
are now localized at component endpoints rather than arising from an arbitrary
forest deficit.

## 3. Strong fan-in at the minimum `E`-radius

Let

\[
R_*=\min_i\rho_i.
\]

Every polygon side has length at least `R_*`, because each side is incident to
exactly one `E_i` and has length `rho_i`.

Fix a polygon vertex `W`, and consider the centres in `X_{R_*}` for which `W`
is a **non-boundary** witness. None of those centres is adjacent to `W` on the
polygon boundary. The set consisting of `W` and all of those source centres is
therefore boundary-independent. Since every polygon side has length at least
`R_*`, the minimum-side corollary and the degree-two strengthening apply to
that set.

> **Minimum-level extra-target cap.** A single vertex can be a non-boundary
> radius-`R_*` witness for at most two centres in `X_{R_*}`.

Hence the `2c_{R_*}` mandatory external incidences require at least
`c_{R_*}` distinct extra targets. Moreover, by the return-locality lemma in
`docs/radius-level-return-locality.md`, the two endpoint exports of a path with
at least five vertices cannot share one target.

This conclusion uses minimum radius only among the `E`-centres in the chosen
alternating branch. It does not assert that `R_*` is the globally shortest
pairwise distance or the selected radius of an opposite-parity target.

## 4. A consecutive same-level edge cannot have a second common apex

There is a further local obstruction when one path edge joins consecutive
alternate centres.

> **Consecutive-edge common-witness obstruction.** Let consecutive alternate
> centres `U,V` have the same rich radius `R`, let `A` be the boundary vertex
> between them, and assume `|UV|=R`. Then there is no non-boundary polygon
> vertex `W` such that
>
> \[
> |WU|=|WV|=R.
> \]

### Proof

Let `B` be the other boundary neighbour of `U` and `C` the other boundary
neighbour of `V`. Normalize `R=1` and choose coordinates

\[
U=(0,0),\quad V=(1,0),\quad
A=(1/2,\sqrt3/2).
\]

Because `A` is at unit distance from both `U,V`, any distinct common unit
witness is the other intersection of the two unit circles:

\[
W=(1/2,-\sqrt3/2).
\]

The boundary-neighbour hypothesis gives `|UB|=|VC|=1`. In the polygon order,
`B,U,A,V,C` are consecutive, while `W` lies on the complementary boundary
chain from `C` to `B`.

Ray order at the strictly convex vertex `U` places the direction of `UB`
strictly between angles `-2pi/3` and `-pi/3`; otherwise the open interior cone
at `U` could not contain both the rays to `V` and `W` while having angular
width less than `pi`. Consequently

\[
x(B)<1/2,\qquad y(B)<-\sqrt3/2.
\]

The symmetric ray-order statement at `V` gives

\[
x(C)>1/2,\qquad y(C)<-\sqrt3/2.
\]

Thus the vertical line `x=1/2` meets the segment `BC` at a point strictly below
`W`, while it meets the vertex `A` strictly above `W`. Therefore `W` lies in
the interior of the triangle `ABC`, contradicting that every polygon vertex
is extreme. `QED`

This removes the shortest return motif when its radius-level tree edge is also
an edge between consecutive alternate centres. A distance-`R` path edge whose
endpoints are separated by other alternate centres remains outside this local
argument.

## 5. Remaining gap

Within the alternating boundary-neighbour branch, a surviving radius level now
has the following form:

1. its same-level graph is a union of paths;
2. path angles exceed `60` degrees;
3. every path endpoint exports at least one non-boundary witness;
4. a general outside target has fan-in at most three;
5. at the minimum `E`-radius, an extra target has fan-in at most two;
6. one target cannot reconnect tree vertices at distance four or more; and
7. it cannot form the consecutive-edge double-apex motif above.

The unresolved local returns have tree distance one with nonconsecutive
centres, or tree distance two or three. Globally, the larger extraction gap
also remains: an arbitrary hypothetical counterexample has not been shown to
contain an alternating set whose rich classes all contain both boundary
neighbours.

## 6. Arithmetic replay

The exact replay in `src/erdos97/sparse_minimum_distance_forest.py` records the
coefficient facts used here:

```text
2*(1/3) + (1/2-alpha/(2*pi)) < 1
    implies alpha/(2*pi) > 1/6,
2*(1/3) + 2*(1/2) - (alpha_1+alpha_2)/(2*pi) > 1
    when alpha_1+alpha_2 < pi.
```

Run:

```bash
python scripts/check_sparse_minimum_distance_forest.py \
  --max-cycle-length 512 \
  --assert-expected \
  --summary-json
```

The replay checks only this arithmetic spine. The ray-order, projection, and
strict-convexity arguments remain paper-proof steps requiring independent
review.
