# No convex realization of the labelled 27-point product witness system

**Status:** restricted paper proof; independent review pending. The proof is
not a solution of Erdős #97. Numerical Jacobian ranks are not used in it.

The exact 27-point seed and its named witnesses are recorded in the repository
at `docs/c3-product-27-nonconvex-control.md`. This note treats arbitrary
realizations of those same named equal-distance constraints, not merely
changes of the seed's two numerical parameters.

## 1. The fixed witness system and the theorem

Label the 27 points \(p_{ijk}\), where \(0\le i,j,k<3\). At \(p_{ijk}\), the
four required, equally distant points are

\[
p_{i,j,k+1},\quad p_{i,j,k+2},\quad
p_{i+1,j,k},\quad p_{i,j+1,k}.
\tag{1}
\]

The \(k\) coordinate is reduced modulo three. A wrap of \(i\) from 2 to 0,
or of \(j\) from 2 to 0, increments \(k\) by one. All 27 labelled points are
required to be distinct.

**Theorem.** There is no strictly convex realization of (1), even when the
27 points are allowed arbitrary planar coordinates, the triangle centers are
not prescribed, and the triangle orientations are not assumed equal.

Consequently the exact product seed cannot be deformed into a strictly convex
configuration preserving (1). This is an obstruction to the entire labelled
witness system, not merely its product parametrization or its collision-free
realization component. Changing the witness assignments remains outside it.

The equations (1) force each labelled triple to be equilateral: the first
vertex gives equality of its two incident sides, and the second gives equality
with the third side. Pairwise distinctness makes these triangles nondegenerate.
Each grid match joins corresponding points of two such triangles at the source
triangle's side length. By the six-point lemma in
[`matched_equilateral_orientation.md`](matched_equilateral_orientation.md), a
convex realization forces the two labelled triangles to have the same
orientation. Cyclic phase shifts at wrapped matches preserve orientation.
The match graph is connected, so all nine orientations agree. The remaining
argument below derives, rather than assumes, their common center and product
structure.

## 2. Matched, equally oriented triangles have a common center in a convex realization

Write two nondegenerate, equally oriented equilateral triangles as

\[
p_k=c+u\omega^k,\qquad q_k=d+v\omega^k,
\qquad\omega=e^{2\pi i/3}.
\]

A cyclic phase shift in the matching is absorbed into \(v\). If all three
matched distances \(|p_k-q_k|\) are equal, expansion gives

\[
|(d-c)+\omega^k(v-u)|^2
 =|d-c|^2+|v-u|^2
  +2\operatorname{Re}((d-c)\overline{(v-u)}\omega^{-k}).
\]

The last term is constant at three equally spaced phases only when
\((d-c)\overline{(v-u)}=0\). Hence either \(d=c\) or \(v=u\).

In the second case the triangles are translates of the same triangle. The
convex hull of a triangle \(T\) and its translate \(T+h\) is
\(T+[0,h]\). It has at most five vertices: as a supporting normal turns once,
a triangle has three changes of supporting vertex and a nontrivial segment
has two; the sum has no more changes than their union. Equivalently, adding
a segment adds at most two edge directions to the three of a triangle.
Thus six distinct points in these two triangles cannot all be in strictly
convex position. If \(h=0\), the two triangles instead coincide, contradicting
distinctness.

Therefore any matched pair in a strictly convex realization with equal
orientation has equal centers. The grid of matches in (1) is connected, so
all nine triangles have a common center. After translation and, if needed,
reflection, they have the form

\[
p_{ijk}=z_{ij}\omega^k,\qquad z_{ij}\ne0.
\tag{2}
\]

This is the only step imposing a common center. It is not assumed for an
arbitrary moving realization.

## 3. A four-arrow completion identity

An own-side arrow \(x\to y\) means
\(|y-x|^2=3|x|^2\). Suppose four distinct triangle orbits have representatives
\(x,a,b,c\) and arrows

\[
x\to a,\quad x\to b,\quad a\to c,\quad b\to c.
\tag{3}
\]

Then the two possible common-circle completions are

\[
c=ab/x\quad\hbox{or}\quad c=-2x.
\tag{4}
\]

To check this, divide by \(x\), so \(x=1\). If
\(|a-1|^2=|b-1|^2=3\), then
\(|ab-a|^2=3|a|^2\) and \(|ab-b|^2=3|b|^2\).
Also expansion of \(|a-1|^2=3\) gives \(|a+2|^2=3|a|^2\), and similarly
for \(b\). The two circles with distinct centers \(a,b\) have at most two
common points, establishing (4). If these displayed points coincide, there
is only one common point; no additional branch is introduced.

The second completion cannot occur in a strictly convex union of the four
orbits, because if \(c=-2x\), then

\[
x=\frac{\omega c+\omega^2c}{2}.
\]

It puts \(x\) at the midpoint of two distinct other points. Therefore (3)
forces \(c=ab/x\) under strict convexity.

Apply this identity to the four unwrapped squares of the 3-by-3 grid in (1).
It gives

\[
z_{ij}=z_{i0}z_{0j}/z_{00},\qquad 0\le i,j<3.
\]

After division by \(z_{00}\), we may therefore write

\[
z_{ij}=a_i b_j,\qquad a_0=b_0=1.
\tag{5}
\]

Thus convexity forces the product form; it is not simply retained from the
initial seed.

## 4. A local obstruction to oppositely directed multipliers

Write \(T(x)=\{x,\omega x,\omega^2x\}\).

**Mixed-half-plane diamond lemma.** Suppose
\(|a-1|^2=|b-1|^2=3\), and all 12 points of

\[
T(1)\cup T(a)\cup T(b)\cup T(ab)
\tag{6}
\]

are distinct and in strictly convex position. Then \(\operatorname{Im}a\)
and \(\operatorname{Im}b\) are nonzero and have the same sign.

This lemma does **not** say all diamonds are impossible. An exact convex
same-half-plane diamond is included in the verification controls.

### 4.1 An elementary convex-combination fact

Let

\[
X=\rho e^{i\alpha},\quad Y=\sigma e^{-i\beta},
\qquad0<\rho\le1,\quad 0<\beta\le\alpha\le\pi/3,
\]

and suppose

\[
\sigma(\cos\beta+\sin\beta/\sqrt3)<1.
\tag{7}
\]

Then \(XY\) is a convex combination of \(0,1,X\) with a strictly positive
coefficient at \(0\). Indeed,

\[
XY=x+yX,\quad
x=\frac{\rho\sigma\sin\beta}{\sin\alpha}>0,
\quad y=\frac{\sigma\sin(\alpha-\beta)}{\sin\alpha}\ge0.
\]

Moreover,

\[
\begin{split}
x+y
 &=\sigma\left(\cos\beta+
             \frac{\rho-\cos\alpha}{\sin\alpha}\sin\beta\right)\\
 &\le\sigma(\cos\beta+\tan(\alpha/2)\sin\beta)\\
 &\le\sigma(\cos\beta+\sin\beta/\sqrt3)<1.
\end{split}
\]

Any nonzero point represented this way is nonextreme in a convex set that
contains \(0,1,X\) and has \(0\) in its interior. Similarities and reflection
preserve this conclusion.

### 4.2 The relevant arcs and their supporting lines

In a putative convex set (6), \(|a|,|b|<2\). For if, say, \(|a|\ge2\), the
triangle \(T(a)\) contains the disk of radius \(|a|/2\) about zero, so the
point \(1\) lies inside or on that triangle and cannot be another strict hull
vertex.

On \(|a-1|^2=3\), writing \(a=r e^{i\theta}\) gives

\[
r=\cos\theta+\sqrt{2+\cos^2\theta}.
\tag{8}
\]

The bound \(r<2\) therefore forces \(|\theta|>\pi/3\) for the principal
argument. A multiplier with \(r=1\) is \(\omega\) or \(\omega^2\), which
would alias two orbits and is excluded.

Suppose first that \(a\) is in the closed upper half-plane and \(b\) in the
closed lower half-plane, taking arguments in \((\pi/3,\pi]\) and
\([-\pi,-\pi/3)\). Put

\[
A=\omega^2a,\quad B=\omega b,\quad C=AB=ab.
\]

The principal arguments of \(A,B\) lie in \([-\pi/3,\pi/3]\).
The circles containing \(A,B\) and their inverses give the strict supporting
inequalities

\[
\begin{split}
\operatorname{Re}A+\operatorname{Im}A/\sqrt3&<1,\\
\operatorname{Re}B-\operatorname{Im}B/\sqrt3&<1,\\
\operatorname{Re}(1/B)-\operatorname{Im}(1/B)/\sqrt3&<1.
\end{split}\tag{9}
\]

For the first two, the circle centers are \(\omega^2,\omega\) and the radii
are \(\sqrt3\); each indicated linear functional has maximum 1, attained
only at the point 1. For the third, inversion maps the circle
\(|B-\omega|^2=3\) to the circle of center \(-\omega^2/2\) and radius
\(\sqrt3/2\); the same maximum calculation applies. Equality would mean
\(A=1\) or \(B=1\), and hence aliased orbits, so the inequalities are strict.

Formula (8) shows that, for upper \(a\), \(|a|>1\) corresponds to
\(\arg A<0\), and \(|a|<1\) to \(\arg A>0\). For lower \(b\), the signs
are reversed: \(|b|>1\) gives \(\arg B>0\), and \(|b|<1\) gives
\(\arg B<0\).

### 4.3 Four norm cases

If \(|a|,|b|<1\), write \(A=\rho e^{i\alpha}\),
\(B=\sigma e^{-i\beta}\), where \(0<\alpha,\beta\le\pi/3\).
If \(\alpha\ge\beta\), apply the convex-combination fact to \(X=A,Y=B\),
using (9). It makes \(C=AB\) nonextreme. If \(\beta>\alpha\), reflect and
swap the roles of \(A,B\) to get the same conclusion.

If \(|a|<1<|b|\), write \(A=\rho e^{i\alpha}\),
\(B=\tau e^{i\beta}\), with \(\rho<1<\tau\) and
\(0<\alpha\le\pi/3\), \(0<\beta<\pi/3\).
When \(\beta\le\alpha\), apply the fact to \(X=A,Y=1/B\), using the third
inequality of (9). It expresses \(A/B\) as a convex combination of
\(0,1,A\) with positive weight at zero. Multiplying by \(B\) makes \(A\)
nonextreme in \(\operatorname{conv}\{0,B,AB\}\).
When \(\alpha\le\beta\), instead use
\(X=1/\overline B,Y=\overline A\). The first inequality of (9) is precisely
(7) for this choice of \(Y\). Conjugating the resulting representation and
multiplying by \(B\) makes \(A\) nonextreme in
\(\operatorname{conv}\{0,B,1\}\). Equality of the angles is allowed in the
convex-combination fact and creates no missing boundary case.

The case \(|b|<1<|a|\) follows by interchanging \(a,b\) and conjugating.

Finally suppose \(|a|,|b|>1\). Then
\(A=\rho e^{-i\alpha}\), \(B=\sigma e^{i\beta}\), with
\(0<\alpha,\beta<\pi/3\), and both \(\operatorname{Re}A\) and
\(\operatorname{Re}B\) are strictly greater than 1. For example, the radial
coordinate \(\rho\) of \(A\) is the positive root of

\[
x^2+(\cos\alpha-\sqrt3\sin\alpha)x-2=0.
\]

At \(x=\sec\alpha\), this polynomial equals
\(\tan\alpha(\tan\alpha-\sqrt3)<0\), so \(\rho>\sec\alpha\).
The argument for \(B\) is its reflection. The segment \(AB\) crosses the
positive real axis strictly beyond 1. Hence 1 is a convex combination of
that intersection point and zero, with positive coefficient at zero, and is
nonextreme in \(\operatorname{conv}\{0,A,B\}\).

In every case, all points named as witnesses of nonextremality belong to (6),
and zero is interior to its convex hull because \(T(1)\) is present.
Thus each case contradicts strict convexity.

A real multiplier is either \(1+\sqrt3>2\), already excluded, or
\(1-\sqrt3<0\). The latter can be assigned the upper or lower principal
argument as needed, so the preceding proof also excludes it paired with a
nonreal multiplier. Two negative real multipliers would coincide and violate
distinctness. This completes the mixed-half-plane lemma.

## 5. The projective three-cycles cannot have one common sign

In (5), define the source ratios

\[
r_0=a_1/a_0,\quad r_1=a_2/a_1,\quad r_2=\omega a_0/a_2,
\]

and similarly \(s_0,s_1,s_2\) from the \(b\) factors. Equations (1) imply

\[
|r_i-1|^2=|s_j-1|^2=3,
\qquad r_0r_1r_2=s_0s_1s_2=\omega.
\tag{10}
\]

At each grid vertex, including wrapped ones, its source orbit, its two
successor orbits and their joint successor form a four-orbit diamond. The
mixed-half-plane lemma therefore says that \(\operatorname{Im}r_i\) and
\(\operatorname{Im}s_j\) have the same nonzero sign for every \(i,j\).
All six ratios lie in the same open half-plane. Convexity also gives
\(|r_i|,|s_j|<2\), by applying the triangle inradius argument after
normalization at the corresponding source orbit.

It suffices to consider the three \(r_i\). If they are all upper-half-plane,
put \(\theta_i=\arg r_i\). Then \(\pi/3<\theta_i<\pi\), and the product
condition in (10) forces

\[
\theta_0+\theta_1+\theta_2=8\pi/3.
\]

Each angle must consequently exceed \(2\pi/3\), since the other two are
strictly less than \(2\pi\). Formula (8) then gives \(|r_i|<1\) for every
\(i\), contradicting \(|r_0r_1r_2|=1\).

If they are all lower-half-plane, put \(\phi_i=-\arg r_i\). Again
\(\pi/3<\phi_i<\pi\), and (10) now forces
\(\phi_0+\phi_1+\phi_2=4\pi/3\). Each \(\phi_i<2\pi/3\), because the
other two have sum greater than \(2\pi/3\). Formula (8) gives \(|r_i|>1\)
for every \(i\), the opposite modulus contradiction.

This proves the theorem.

## 6. Scope and hostile-audit notes

* The argument uses the specified 3-by-3 labelled witness system. It is not a
  theorem about every 27-point configuration or every own-side C3 graph.
* Equal orientation in Section 2 is established by the six-point matched-
  triangle lemma, whose thirty opposite-order cases have exact rational
  contradiction certificates. Opposite orientations are not silently
  identified, and no connected-component assumption remains.
* Triangle center equality is derived only for an allegedly convex endpoint;
  it need not hold at every point of a nonconvex deformation.
* The four-arrow completion lemma permits two branches before convexity. The
  midpoint argument explicitly eliminates one; no generic-dimension premise
  or unproved assertion of rigidity is used.
* The projective monodromy is \(\omega\), not 1. Both possible half-plane
  signs are checked with this exact monodromy.
* The three-ratio argument is not asserted for longer cycles. Numerical
  searches of longer cycles are separately labelled exploration.
* The proof does not depend on the exploratory SVD ranks 48 and 14, on a
  tolerance for the seed, or on its particular algebraic coordinates.

The exact and symbolic controls in `verify/` check algebra used in this note
and are intended to retain a genuine convex same-half-plane diamond to falsify an overstrong
"all diamonds are forbidden" variant. They do not constitute formalization
or independent mathematical review of the theorem.
