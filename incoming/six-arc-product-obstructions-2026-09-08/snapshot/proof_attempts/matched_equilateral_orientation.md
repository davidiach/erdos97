# Matched equilateral triangles: orientation and a common center

**Status:** restricted mathematical proof with an exact finite angle certificate;
independent mathematical review pending. This is not a solution of Erdős #97.

## 1. Statement

Let `(p0,p1,p2)` and `(q0,q1,q2)` be nondegenerate equilateral triangles.
Assume their six points are distinct and in strictly convex position, and

\[
|p_i-q_i|=|p_0-p_1|\qquad(i=0,1,2).                 \tag{1}
\]

**Lemma.** The two labelled triangles have the same orientation. Consequently
they have the same center.

The common matched length is the side length of the **source** triangle.
No equality with the target triangle's side length is assumed. Reversing the
source/target relation without checking (1) would change the hypothesis.

## 2. Chord-angle identities

Let six points `v0,...,v5` be in counterclockwise strictly convex order. Rotate
the coordinate system so that `v1-v0` has argument zero. For `i<j` choose
continuous lifts `beta_ij = arg(vj-vi)/pi`. They satisfy, for every `i<j<k`,

\[
\beta_{ij}<\beta_{ik}<\beta_{jk}<\beta_{ij}+1.       \tag{2}
\]

These inequalities are precisely the positivity of the three triangle angles:

\[
\begin{aligned}
\angle v_jv_iv_k/\pi&=\beta_{ik}-\beta_{ij},\\
\angle v_iv_kv_j/\pi&=\beta_{jk}-\beta_{ik},\\
\angle v_iv_jv_k/\pi&=1-\beta_{jk}+\beta_{ij}.
\end{aligned}                                      \tag{3}
\]

For example, the directions of chords issuing from `vi` occur in the boundary
order because all other vertices lie strictly inside its angle of size less
than pi. The three directions in a counterclockwise triangle then have the
lifts in (2). The same lifts work for every triple; they are the ordinary
chord directions along a convex polygon, not independently chosen angles.

An isosceles triangle whose sorted vertex positions are `i<j<k` gives one
of the following equalities, according to its apex:

\[
\begin{array}{c|c}
\text{apex}&\text{equality}\\ \hline
i&\beta_{ij}+\beta_{ik}-2\beta_{jk}=-1\\
j&\beta_{ij}+\beta_{jk}-2\beta_{ik}=0\\
k&\beta_{ik}+\beta_{jk}-2\beta_{ij}=1.
\end{array}                                       \tag{4}
\]

They follow by setting the two base angles in (3) equal. Thus they do not
assume that all distances in the entire six-point set are equal.

For the metric hypotheses of the lemma, use all pairs in these partner lists:

```
apex p0: p1,p2,q0
apex p1: p0,p2,q1
apex p2: p0,p1,q2
apex q0: q1,q2
apex q1: q0,q2
apex q2: q0,q1
```

There are twelve applications of (4): three at each source vertex and one
at each target vertex. All follow from (1) and the two equilateral triangles.

## 3. All opposite-orientation orders

Reflect the alleged realization, if necessary, to make `(p0,p1,p2)`
counterclockwise. Suppose `(q0,q1,q2)` is clockwise. Starting the cyclic
list with `p0`, exactly thirty orders have these orientations: of the 120
permutations of the other five labels, one half have the prescribed source
orientation, and independently one half have the opposite target orientation.

Simultaneously permuting the three subscripts of the `p` and `q` labels
preserves every metric hypothesis. An odd subscript permutation is accompanied
by reversal of the boundary order to keep the source triangle counterclockwise.
The thirty orders split into the following six orbits. The displayed identity
in each case follows from the twelve instances of (4), using (3). Every angle
on its left is strictly positive, so every displayed identity is impossible.

### Case A (six orders)

Boundary order: `p0,p1,p2,q0,q2,q1`.

\[
\angle q_2p_0q_1+\angle p_0q_2q_1+\angle p_2q_1q_0=-\pi/6.
\]

### Case B (three orders)

Boundary order: `p0,p1,p2,q2,q1,q0`.

\[
\angle p_0q_1q_0+\angle p_2q_1q_2=-\pi/2.
\]

### Case C (six orders)

Boundary order: `p0,p1,q0,p2,q2,q1`.

\[
\begin{split}
\angle p_0q_0q_1+2\angle p_0p_2q_1+2\angle q_2p_0q_1
+2\angle p_2q_0q_2+\angle q_0q_2p_2=0.
\end{split}
\]

### Case D (six orders)

Boundary order: `p0,p1,q1,p2,q0,q2`.

\[
\angle p_0q_1q_2+\angle p_2q_1q_0=-\pi/6.
\]

### Case E (six orders)

Boundary order: `p0,p1,q1,q0,p2,q2`.

\[
2\angle p_0p_1q_2+\angle p_0q_0q_2+
2\angle p_1q_0q_1+\angle q_0q_2p_2=0.
\]

### Case F (three orders)

Boundary order: `p0,q0,p1,q2,p2,q1`.

\[
\angle p_0q_0q_1+2\angle p_1q_0q_2+
2\angle q_0q_2p_1+\angle p_2q_2q_1=0.
\]

For fully explicit algebra, let `E_l beta=e_l`, `l=1,...,12`, be (4) in the
following order: list the apices in the order `p0,p1,p2,q0,q1,q2` above, and
at each apex take pairs from its displayed partner list in lexicographic
position order. (For three partners these are positions `(1,2),(1,3),(2,3)`.)
The following vectors `v` verify each identity. Write the left side divided by
pi as `c-L beta` using (3). Direct coefficient collection gives
`L + sum_l v_l E_l=0` and its value is `c+sum_l v_l e_l`.

```
A: (0,0,0, -1/6,-1/2,1/2, -1/3,0,0,  2/3,1/3,0)
B: (0,0,0, -1/6,-1/2,1/2, -1/3,0,0, -2/3,-1/3,0)
C: (0,0,1, -1/3,-1,1,     -2/3,1,0, -1/3,-2/3,0)
D: (0,0,0, -1/6,-1/2,1/2, -1/3,0,0,  2/3,1/3,0)
E: (0,1,0, -1/3,0,0,     -2/3,0,1,   2/3,4/3,0)
F: (-2/3,1,0, -1/3,0,0,   0,0,-1,   -2/3,-1/3,0)
```

No positive lower bound on an angle is needed. Strict positivity alone rules
out the zero right sides as well as the negative right sides. The six cases
exhaust the thirty orders, proving the orientation assertion.

## 4. The common center

Write the equally oriented triples as

\[
p_k=c+u\omega^k,\qquad q_k=d+v\omega^k,
\quad \omega=(-1+i\sqrt3)/2.
\]

Equality of the three matched distances gives

\[
|(d-c)+(v-u)\omega^k|^2
=|d-c|^2+|v-u|^2+
2\operatorname{Re}((d-c)\overline{(v-u)}\omega^{-k}).
\]

The three real parts can be equal only when their common complex coefficient
is zero. Hence `d=c` or `v=u`. In the latter case the triangles are translates
of the same triangle. Their hull is the Minkowski sum of a triangle and a
segment, which has at most five vertices: the three triangle edge directions
and at most two additional segment edge directions. Six distinct hull vertices
are therefore impossible in that case. Thus `d=c`, as claimed.

## 5. Exact certificates and independence

`candidate_counterexamples/opposite_triangle_contradictions.json` is a set of
**contradiction certificates**, not candidate counterexample coordinates. It
contains a separate rational identity for each of the thirty orders; it does
not rely on the symmetry reduction in Section 3.

`verify/check_opposite_triangles.py` reconstructs (2) and (4) using Python's
standard library and `fractions.Fraction`. It checks exhaustive order coverage,
nonnegative nonzero weights on strict inequalities, exact cancellation of every
chord variable, and a nonpositive resulting constant. It imports no search code
and invokes no optimizer. The floating-point LP was used only to discover the
rational identities.

```
python verify/check_opposite_triangles.py --check
```

This verifies a finite necessary-angle contradiction; no numerical-to-exact
transition is implicit. The geometric derivation of the angle relations and
the paper argument remain subject to expert review.
