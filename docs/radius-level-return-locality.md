# Radius-level return locality

Status: `PAPER_PROOF_CANDIDATE / REVIEW_PENDING`.

This note extends the boundary-detour machinery in
`docs/sparse-minimum-distance-forest.md`. It is a restricted local theorem, not
a proof or disproof of Erdős Problem #97 and not a source-of-truth status
update.

## 1. A detour-cycle lemma with weak arcs

Let `Y` be `g` vertices of a strictly convex polygon, listed in inherited
cyclic order, and fix `r>0`. Suppose every boundary arc between consecutive
members of `Y` has length at least `r`, while all but `h` of those arcs have
length at least `2r`.

Assume there is a closed polygonal cycle through the vertices of `Y`, in any
order, all of whose `g` edges have length exactly `r`.

> **Weak-arc detour-cycle lemma.** If `g>=h+4`, this is impossible.

The graph cycle need not follow the polygon's boundary order.

### Proof

For the boundary arc from `y_i` to `y_{i+1}`, let

- `a_i=1` for one of the `h` weak arcs and `a_i=2` otherwise; and
- `sigma_i` be the sum of the exterior turns strictly inside that arc.

Thus its boundary length is at least `a_i r`. If `sigma_i<pi`, projection onto
the bisector of the arc's edge-direction interval gives

\[
|y_i y_{i+1}|\ge a_i r\cos(\sigma_i/2)
              \ge a_i r\left(1-\frac{\sigma_i}{\pi}\right).
\]

For `0<sigma_i<pi` the second inequality is strict. If `sigma_i>=pi`, the
right-hand side is nonpositive and the same displayed weak inequality remains
valid.

Summing over the boundary-order chords gives

\[
\begin{aligned}
\operatorname{per}(Y)
&\ge r\sum_i a_i
   -\frac r\pi\sum_i a_i\sigma_i\\
&>r(2g-h)-4r\\
&=r(2g-h-4).
\end{aligned}
\]

Indeed,

\[
\sum_i a_i=2g-h,
\qquad
\sum_i a_i\sigma_i\le2\sum_i\sigma_i<4\pi,
\]

because the open-arc turn sums omit the positive exterior turns at the
vertices of `Y`.

The convex-hull perimeter of `Y` is no greater than the length of any closed
tour visiting `Y`. The assumed `r`-edge cycle has length `gr`, so

\[
\operatorname{per}(Y)\le gr.
\]

When `g>=h+4`, however,

\[
2g-h-4\ge g,
\]

and the strict perimeter lower bound contradicts the cycle tour. `QED`

### Boundary cases

- `h=0` recovers the long-cycle part of the boundary-detour forest lemma for
  every `g>=4`. The equilateral triangle case still needs the separate
  `2pi/3` turn argument recorded there.
- `h=2` rules out every such `r`-edge cycle of length at least six.
- The inequality deliberately leaves the `h=2` cycle lengths three, four, and
  five unresolved.

## 2. One outside target can return only locally

Use the alternating setup

\[
E_0,Q_0,E_1,Q_1,\ldots,E_{m-1},Q_{m-1}
\]

from `docs/sparse-minimum-distance-forest.md`. Fix a selected-radius value `R`
and let

\[
X_R=\{E_i:\rho_i=R\}.
\]

The distance-`R` graph `H_R(X_R)` is a forest.

Let `W` be any polygon vertex outside `X_R`, and suppose `W` is at distance
`R` from two vertices `U,V` in the same component of `H_R(X_R)`. Let

\[
U=X_0,X_1,\ldots,X_\ell=V
\]

be their unique path in that tree. Every path edge and both edges `WU,WV` have
length `R`, so these vertices support an `R`-edge cycle of length

\[
g=\ell+2.
\]

Consider them in inherited boundary order. The two boundary arcs incident to
`W` each have length at least `R`: their other endpoint lies in `X_R`, and the
last boundary edge entering that endpoint has length `R`. Every other arc has
both endpoints in `X_R` and has length at least `2R` by the radius-level detour
property.

The weak-arc lemma applies with `h=2`. Hence `g<=5`, or equivalently

\[
\ell\le3.
\]

> **Same-component return-locality corollary.** One outside radius-`R` target
> cannot attach to two vertices of the same radius-level tree at tree distance
> four or more.

This supplements the global fan-in cap of three. If one target absorbs several
exports from one same-radius component, all of its attachment vertices must
lie in a tree neighbourhood of diameter at most three.

## 3. Why this is useful

The forest/export bound alone permits a large tree component to send its two
mandatory external incidences to one common target. The return-locality
corollary shows that such reuse cannot join remote parts of the component.
Consequently any high-reuse export pattern must be concentrated around a
bounded local tree motif.

This is a genuine strengthening, but it does not close the alternating branch:

- two attachments at tree distance one, two, or three remain possible;
- attachments to different same-radius components create no return cycle; and
- opposite-parity targets need not change selected radius.

The next finite proof-mining target is therefore the collection of short return
motifs: a target attached across a tree edge, a length-two path, or a
length-three path. The consecutive-three common-witness lemma already removes
one subcase when three equal-radius centres occur consecutively on the polygon
boundary.

## 4. Arithmetic replay

The existing replay now includes the exact `h=2` coefficient identity

```text
(2*g-6)-g = g-6.
```

Run:

```bash
python scripts/check_sparse_minimum_distance_forest.py \
  --max-cycle-length 512 \
  --assert-expected \
  --summary-json
```

The replay records the first excluded one-defect cycle length as six. It does
not formalize the geometric projection step or settle the three shorter return
motifs.
