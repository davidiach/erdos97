# Exact C3 nonconvex control and structured search handoff

Status: `EXACT_NONCONVEX_NEGATIVE_CONTROL` plus one restricted exact
obstruction and one conditional construction template.

This note retains the independently checkable part of the July 23, 2026
counterexample-search session. It does **not** claim a counterexample, a proof
of Erdos Problem #97, or a change to the official/global open status.

## 1. A nine-point common-distance control

Let

\[
\omega=e^{2\pi i/3}
\]

and let `a`, `b`, and `c` be distinct nonzero real numbers satisfying

\[
a+b+c=0.
\]

Define

\[
X(a,b,c)=\{\omega^j a,\omega^j b,\omega^j c: j=0,1,2\}.
\]

For the point `a`, the four points

\[
\omega b,\quad \omega^2b,\quad \omega c,\quad \omega^2c
\]

are all at the same distance. Indeed,

\[
|a-\omega b|^2=|a-\omega^2b|^2=a^2+ab+b^2,
\]

while

\[
|a-\omega c|^2=|a-\omega^2c|^2=a^2+ac+c^2.
\]

Their difference is

\[
(a^2+ab+b^2)-(a^2+ac+c^2)
=(b-c)(a+b+c)=0.
\]

Rotation and cyclic permutation of `a,b,c` give the same conclusion at every
point. In fact all named incidences have one global squared distance

\[
R^2=a^2+ab+b^2=b^2+bc+c^2=c^2+ca+a^2.
\]

Thus every point in `X(a,b,c)` has four companions at the common distance
`R`.

The smallest concrete version used by the checker is

\[
(a,b,c)=(1,2,-3).
\]

It has nine distinct points and exactly eighteen unordered pairs at squared
distance `7`. Every point has degree four in that distance graph. The exact
full pair-distance histogram is

```text
squared distance:  1  3   7  12  16  25  27
pair count:        3  3  18   3   3   3   3
```

Replay with:

```bash
python scripts/check_c3_nonconvex_control.py
```

## 2. Why the family is necessarily nonconvex

Among three nonzero reals summing to zero, two have the same sign. Their
three-point `C3` orbits are concentric, equally oriented equilateral triangles.
The orbit with smaller absolute value is a strict homothetic copy inside the
larger triangle, so its three points are not hull vertices.

For `(1,2,-3)`, the checker computes the convex hull in exact
`Q(sqrt(3))` arithmetic and finds exactly six hull vertices. The construction
therefore satisfies the distance requirement but fails the convex-position
requirement in a transparent way.

This makes it a useful negative control for solvers: a distance-only optimizer
can converge to this configuration with zero equality residual while remaining
far from a counterexample.

## 3. Rigidity of the obvious deformation

For arbitrary complex `z,u`, direct expansion gives

\[
|z-\omega u|^2-|z-\omega^2u|^2
=-2\sqrt3\,\operatorname{Im}(z\overline u).
\]

Consequently,

\[
|z-\omega u|=|z-\omega^2u|
\quad\Longleftrightarrow\quad
\operatorname{Im}(z\overline u)=0.
\]

Thus any deformation preserving the conjugate-pair witness assignment forces
`z` and `u` to remain radially collinear. The simple plan of perturbing the
three real orbit representatives off their common line cannot preserve these
same four named witnesses.

## 4. Fixed-step equilateral circulants are impossible

### Lemma

Let `v_0,...,v_{n-1}` be the vertices of a strictly convex polygon in cyclic
order. Suppose, for one fixed

\[
b\not\equiv 0,\pm1\pmod n,
\]

that

\[
|v_{i+1}-v_i|=|v_{i+b}-v_i|=r>0
\]

for every `i`. Then no such polygon exists.

### Proof

Fix `i` and set

\[
A=v_i,\quad B=v_{i+1},\quad C=v_{i+b},\quad D=v_{i+b+1}.
\]

The assumptions give

\[
|A-B|=|A-C|=|D-B|=|D-C|=r.
\]

Hence `A` and `D` are the two intersections of the equal-radius circles
centered at `B` and `C`. Reflection in the perpendicular bisector of `BC`
exchanges them, so

\[
A+D=B+C.
\]

Therefore

\[
D-C=B-A,
\]

or

\[
v_{i+b+1}-v_{i+b}=v_{i+1}-v_i.
\]

Two distinct boundary edges have the same directed vector. This is impossible
in a strictly convex polygon, whose directed edge angles turn strictly once
around the circle. Contradiction.

This excludes the construction in which every vertex obtains four common-unit
neighbors from the boundary cycle and one fixed circulant step. It does not
exclude variable steps, varying row radii, multiple step types, or
noncirculant witness assignments.

## 5. A conditional product template

The session also produced an exact way to satisfy the four distance equations
before convexity is imposed.

Let `x_0,...,x_{m-1}` and `y_0,...,y_{k-1}` be nonzero cyclic complex
sequences satisfying

\[
|x_{a+1}-x_a|=\sqrt3|x_a|,
\qquad
|y_{b+1}-y_b|=\sqrt3|y_b|
\]

for all cyclic indices. Form

\[
P=\{\omega^s x_a y_b:
0\leq s<3,\ 0\leq a<m,\ 0\leq b<k\}.
\]

At

\[
p=\omega^s x_a y_b,
\]

the four named points

\[
\omega p,\quad \omega^2p,\quad
\omega^s x_{a+1}y_b,\quad
\omega^s x_a y_{b+1}
\]

all lie at distance `sqrt(3)|p|` from `p`.

This is only a conditional algebraic template. It becomes a counterexample
route only after proving all of the following:

1. both ratio cycles close;
2. all product points and all four witnesses are distinct;
3. no product aliases a rotated copy of another product;
4. every product point is a strict convex-hull vertex.

The trivial ratios `x_{a+1}/x_a` or `y_{b+1}/y_b` equal to `omega` or
`omega^2` collapse the successor with a rotated companion and must be excluded.
A useful next search is therefore an exact cycle search on

\[
|r-1|^2=3,\qquad \prod r=1,
\]

followed by exact alias and convex-hull checks on the product configuration.

## 6. Session triage

The session also revisited parabola/ellipse samples, concentric two-orbit
families, five `C3`-orbit tournaments, and doubled-Danzer continuation. Those
routes already have stronger or more reproducible records elsewhere in this
repository, so they are not duplicated here. Numerical residuals without
retained coordinates and replay code are deliberately omitted.

The retained contribution is therefore narrow:

- one exact all-four-rich common-distance configuration showing the distance
  equations alone are easy to satisfy;
- one exact rigidity identity explaining its collapse;
- one short obstruction eliminating a broad fixed-step circulant design;
- one exact product template defining a concrete future search space.
