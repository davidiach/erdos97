# Alternate-vertex perimeter obstruction and relaxation guardrail

Status: `REVIEW_PENDING_RESTRICTED_THEOREM` plus
`EXACT_CERTIFICATE_DIAGNOSTIC`.

This note records a restricted infinite-family obstruction and one exact
negative control for a collection of necessary-condition relaxations. It is
**not** a proof or disproof of Erdős Problem #97, not a counterexample, and not
a source-of-truth or official/global status update. The geometric argument has
not received independent external review.

## 1. Alternate-vertex perimeter lemma

Let

\[
E_0,Q_0,E_1,Q_1,\ldots,E_{m-1},Q_{m-1}
\]

be the vertices, in cyclic order, of a strictly convex equilateral
\(2m\)-gon with side length \(r>0\). Let \(L_E\) be the perimeter of the
strictly convex polygon on the alternate vertices \(E_0,\ldots,E_{m-1}\).
Then

\[
L_E>2r(m-2).
\]

### Proof

Let \(\tau_i\) be the exterior turn at \(Q_i\). Strict convexity gives

\[
0<\tau_i<\pi,
\qquad
\sum_{i=0}^{m-1}\tau_i<2\pi.
\]

The second inequality is strict because the exterior turns at the omitted
vertices \(E_i\) are positive and all \(2m\) exterior turns sum to \(2\pi\).

The triangle \(E_iQ_iE_{i+1}\) has two sides of length \(r\) and included
angle \(\pi-\tau_i\) at \(Q_i\). Therefore

\[
|E_iE_{i+1}|=2r\cos(\tau_i/2).
\]

Strict concavity of cosine on \([0,\pi/2]\) gives

\[
\cos(t/2)>1-\frac{t}{\pi}
\qquad (0<t<\pi).
\]

Consequently,

\[
\begin{aligned}
L_E
 &=2r\sum_i\cos(\tau_i/2)\\
 &>2r\left(m-\frac1\pi\sum_i\tau_i\right)\\
 &>2r(m-2).
\end{aligned}
\]

This proves the lemma.

A standard companion fact is that any closed polygonal tour through a finite
point set has length at least the perimeter of its convex hull. One proof
projects the tour onto every direction: the total variation of each projection
is at least twice the width of the convex hull. Integrating over directions and
using Cauchy's perimeter formula gives the claim.

Hence, for \(m\ge4\), the alternate vertices cannot admit a Hamiltonian tour
whose \(m\) edges all have length at most \(r\): such a tour would have length
at most \(mr\), whereas

\[
L_E>2r(m-2)\ge mr.
\]

The inequality at \(m=4\) is supplied by the strict lower bound.

## 2. Infinite forbidden selected-witness family

### Restricted theorem

Let \(m\ge4\), let \(1\le k<m\), and suppose \(\gcd(k,m)=1\). There is no
strictly convex \(2m\)-gon in cyclic order

\[
E_0,Q_0,E_1,Q_1,\ldots,E_{m-1},Q_{m-1}
\]

such that, for every \(i\pmod m\), the four vertices

\[
Q_{i-1},\quad Q_i,\quad E_{i-k},\quad E_{i+k}
\]

are equidistant from \(E_i\).

There are no assumptions on distance multiplicities at the \(Q_i\), and no
regularity or rotational symmetry is assumed.

### Proof

Let \(r_i\) be the selected radius at \(E_i\). The chord
\(E_iE_{i+k}\) is selected at both endpoints, because the row at
\(E_{i+k}\) contains \(E_{(i+k)-k}=E_i\). Thus

\[
r_i=|E_iE_{i+k}|=r_{i+k}.
\]

Since \(k\) generates \(\mathbb Z/m\mathbb Z\), all radii have one common
value \(r\). Every boundary edge of the full \(2m\)-gon is incident to an
\(E_i\) and is selected at that endpoint, so the polygon is equilateral with
side length \(r\).

The cyclic step-\(k\) sequence

\[
E_0,E_k,E_{2k},\ldots,E_{(m-1)k},E_0
\]

visits all alternate vertices exactly once. Every tour edge has length \(r\),
so the tour has length \(mr\). The perimeter lemma and tour-perimeter comparison
give

\[
mr\ge L_E>2r(m-2)\ge mr,
\]

a contradiction.

### Twenty-vertex instance

For cyclic labels \(p_0,\ldots,p_{19}\), put \(E_i=p_{2i}\),
\(Q_i=p_{2i+1}\), \(m=10\), and \(k=3\). The theorem forbids the rows

\[
S_i=\{i-1,i+1,i-6,i+6\}\pmod {20}
\]

at every even center \(i\), independently of what happens at odd centers. The
selected alternate-vertex tour would have length \(10r\), while the alternate
polygon has perimeter greater than \(16r\).

## 3. Exact metric-relaxation negative control

The companion verifier constructs an abstract metric on
\(\mathbb Z/20\mathbb Z\). It is not a planar point configuration.

Set

\[
(f_0,\ldots,f_{10})=(0,14,26,37,47,56,64,70,74,76,77),
\]

\[
w_i=\begin{cases}0,&i\text{ even},\\50,&i\text{ odd},\end{cases}
\]

and, for \(i\ne j\),

\[
d_{ij}=f_{\min((i-j)\bmod20,(j-i)\bmod20)}+w_i+w_j,
\qquad d_{ii}=0.
\]

Choose

\[
S_i=
\begin{cases}
\{i-1,i+1,i-6,i+6\},&i\text{ even},\\
\{i-2,i+2,i-9,i+9\},&i\text{ odd}.
\end{cases}
\]

At every even center,

\[
f_1+50=64=f_6,
\]

and at every odd center,

\[
f_2+100=126=f_9+50.
\]

The exact replay verifies that these are the unique distance classes of
multiplicity at least four and that every one has size exactly four.

### Replayed conditions

The stored artifact records the following exact results.

| Check | Exact result |
| --- | ---: |
| Ordered strict triangle inequalities | 6,840; minimum slack 2 |
| Strict Kalmanson inequalities | 9,690; minimum slack 1 |
| Maximum selected-row overlap | 2 |
| Two-overlap row pairs | 20; every required chord pair crosses |
| Witness indegree | 4 at every label |
| Selected digraph | Strongly connected |
| Within-row chord-order comparisons | 160; minimum slack 6 |
| Weak-turn inequalities | 240; minimum slack \(1/10\) |

For the weak-turn replay, use the formal rational vector

\[
t_i=\begin{cases}1/10,&i\text{ even},\\3/10,&i\text{ odd}.
\end{cases}
\qquad \sum_i t_i=4.
\]

These are relaxation variables, not exterior angles of a planar polygon.

The even rows are exactly the \(m=10,k=3\) subsystem excluded by the restricted
theorem. Therefore the listed conditions, even when imposed together, do not
recover the perimeter contradiction. This statement concerns only the
explicitly replayed conditions; it does not say that every stronger repository
filter accepts the object.

## 4. Exact Euclidean diagnostics

### The unshifted metric is not Euclidean

Let \(c_i=1\) on even labels and \(c_i=-1\) on odd labels. Then
\(\sum_i c_i=0\), while the verifier obtains

\[
\sum_{i,j}c_ic_jd_{ij}^2=387780>0.
\]

For squared Euclidean distances, expansion gives

\[
\sum_{i,j}c_ic_j|p_i-p_j|^2
=-2\left\|\sum_i c_ip_i\right\|^2\le0.
\]

Thus the unshifted distance table has no Euclidean realization in any
dimension.

### A uniform shift gives an exact dimension-19 Euclidean metric

This diagnostic separates Euclideanity from planarity. Define

\[
D_{ij}=10000+d_{ij}\quad(i\ne j),
\qquad D_{ii}=0.
\]

For every real vector \(x\) with \(\sum_i x_i=0\), write the off-diagonal
error matrix as

\[
E_{ij}=2\cdot10000\,d_{ij}+d_{ij}^2,
\qquad E_{ii}=0.
\]

Then

\[
x^TD^{\circ2}x=-10000^2\|x\|^2+x^TEx.
\]

The maximum unshifted distance is \(177\), so every error entry is at most

\[
2\cdot10000\cdot177+177^2=3571329.
\]

The maximum absolute row sum is therefore at most

\[
19\cdot3571329=67855251.
\]

Gershgorin's bound gives

\[
x^TD^{\circ2}x
\le-(100000000-67855251)\|x\|^2
=-32144749\|x\|^2<0.
\]

Hence \(D^{\circ2}\) is strictly conditionally negative definite. The standard
Euclidean distance-matrix criterion supplies an exact realization of \(D\) in
affine dimension \(19\). The uniform shift preserves every selected equality
and every Kalmanson slack, but this realization is high-dimensional and gives
no planar convex configuration.

## 5. What remains open

The missing general implication is an extraction theorem. An arbitrary minimal
counterexample has not been shown to contain:

1. an alternating set of centers that select both neighboring polygon vertices;
2. reciprocal selected chords that propagate one radius; and
3. a coprime selected cycle through all alternate centers.

The perimeter terminal is exact once those features are present. This packet
does not prove that they must occur.

## Replay

```bash
python scripts/check_perimeter_relaxation_guardrail.py \
  --check --assert-expected --summary-json
```

Regenerate the stable artifact with:

```bash
python scripts/check_perimeter_relaxation_guardrail.py \
  --assert-expected --write
```
