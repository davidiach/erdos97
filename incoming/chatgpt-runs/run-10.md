## 1. Convex-position crossing lemma

Let (P={p_1,\dots,p_n}) be in strictly convex cyclic position. Suppose (i\ne k) and that

[
S_i\cap S_k\supset {a,b},\qquad a\ne b.
]

Thus

[
|p_a-p_i|=|p_b-p_i|=r_i,\qquad |p_a-p_k|=|p_b-p_k|=r_k.
]

In particular, both (p_i) and (p_k) are equidistant from (p_a) and (p_b). Therefore the line (p_i p_k) is the perpendicular bisector of the segment (p_a p_b). Equivalently, (p_a) and (p_b) are reflections of one another across the line (p_i p_k). This is the radical-axis/perpendicular-bisector property.

Let (q) be the midpoint of (p_a p_b). Then (q\in p_i p_k). Choose coordinates with

[
p_i=(0,0),\qquad p_k=(d,0),\qquad d>0,
]

and write

[
q=(t,0),\qquad p_a=(t,h),\qquad p_b=(t,-h),
]

with (h>0). We claim (0<t<d).

If (t=0), then (p_i) lies on the segment (p_a p_b), so (p_a,p_i,p_b) are collinear. If (t=d), then (p_k) lies on the segment (p_a p_b), so (p_a,p_k,p_b) are collinear. Both cases are forbidden by **strict convexity**, namely by the no-three-collinear part of strict convex position.

If (t<0), then (p_i=(0,0)) lies in the interior of the triangle with vertices (p_k,p_a,p_b). Indeed, the vertical cross-section of that triangle at (x=0) has positive length and contains ((0,0)). Thus (p_i) would not be an extreme point of the convex hull, contradicting convex position. Similarly, if (t>d), then (p_k) lies in the interior of the triangle with vertices (p_i,p_a,p_b). This again contradicts convex position.

Hence (0<t<d). Therefore the segment (p_i p_k) meets the segment (p_a p_b) at the interior point (q). So the chords (p_i p_k) and (p_a p_b) cross. For four distinct vertices of a strictly convex polygon, two chords cross if and only if their endpoints alternate in the cyclic order. Therefore the pair ({i,k}) separates the pair ({a,b}).

The exact uses of strict convexity were: first, to exclude the degenerate cases (t=0,d), where three vertices would be collinear; second, to ensure every listed vertex is an extreme point, excluding (t<0) and (t>d).

---

## 2. The exact theorem proved

The full contradiction does **not** follow from facts (A) and (B) alone. The strongest clean theorem I can prove from them is the following.

### Theorem

Let (M) be a cyclically indexed (n\times n) zero-diagonal (0)-(1) matrix satisfying the alternating (K_{2,2}) rule:

[
M_{ia}=M_{ib}=M_{ka}=M_{kb}=1
\quad\Longrightarrow\quad
{i,k}\text{ separates }{a,b}.
]

Let (d_i=|S_i|). Then

[
\sum_{i=1}^n \binom{d_i}{2}\le n(n-2).
]

Consequently, if every row has size at least (4), then necessarily

[
n\ge 8.
]

Moreover,

[
\sum_{i=1}^n d_i
\le
\frac n2\bigl(1+\sqrt{8n-15}\bigr).
]

The condition (n\ge 8) is sharp at the cyclic-matrix level: there are explicit cyclic matrices satisfying all consequences of (A) and (B) with every row sum equal to (4). Hence no contradiction can be derived from (A) and (B) alone.

---

## 3. Cyclic-matrix and discharging argument

Write indices cyclically. A (2\times 2) all-one submatrix using rows (i,k) and columns (a,b) is allowed only when the four indices alternate cyclically:

[
i,a,k,b
\quad\text{or}\quad
i,b,k,a.
]

Equivalently, (a,b) must lie on opposite open arcs between (i) and (k).

Thus the following cyclic (2\times2) pattern is forbidden:

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

whenever (a,b) lie on the same side of the chord (ik).

Several immediate forbidden submatrices follow.

First, no two rows can share three columns. Indeed, if rows (i,k) shared three columns, two of those columns would lie on the same open arc between (i) and (k), contradicting the alternating (K_{2,2}) rule. This recovers fact (A):

[
|S_i\cap S_k|\le 2.
]

Second, dually, no two columns can occur together in three rows. If columns (a,b) occurred together in rows (i,k,\ell), then two of (i,k,\ell) would lie on the same open arc between (a) and (b), again contradicting the alternating rule. Thus every (3\times2) all-one submatrix is forbidden.

Third, if (i,k) are adjacent rows, then no pair of columns can separate them, so

[
|S_i\cap S_k|\le 1.
]

Similarly, if (a,b) are adjacent columns, then at most one row can contain both (a) and (b).

Now discharge as follows. For every row (i), place one token on every unordered pair of columns contained in (S_i). Row (i) emits

[
\binom{d_i}{2}
]

tokens, so the total number of emitted tokens is

[
T=\sum_i \binom{d_i}{2}.
]

Fix an unordered column-pair ({a,b}). If (a,b) are nonadjacent, then the two arcs between (a) and (b) are both nonempty. By the alternating rule, at most one row from each arc can contain both (a) and (b). Hence ({a,b}) receives at most (2) tokens.

If (a,b) are adjacent, then one of the two arcs between them is empty, so ({a,b}) receives at most (1) token.

There are (n) adjacent column-pairs and (\binom n2-n) nonadjacent column-pairs. Therefore

[
T
\le
1\cdot n+2\left(\binom n2-n\right)
==================================

# n+2\left(\frac{n(n-1)}2-n\right)

n(n-2).
]

So

[
\boxed{\sum_i \binom{d_i}{2}\le n(n-2).}
]

If every (d_i\ge 4), then

[
\sum_i \binom{d_i}{2}\ge 6n.
]

Thus

[
6n\le n(n-2),
]

so

[
n\ge 8.
]

For the total number of ones (E=\sum_i d_i), Cauchy gives

[
\sum_i d_i^2\ge \frac{E^2}{n}.
]

Since

[
\sum_i \binom{d_i}{2}
=====================

\frac12\left(\sum_i d_i^2-E\right),
]

we get

[
\frac12\left(\frac{E^2}{n}-E\right)\le n(n-2).
]

Equivalently,

[
E^2-nE-2n^2(n-2)\le 0.
]

Solving the quadratic inequality gives

[
\boxed{
E\le \frac n2\bigl(1+\sqrt{8n-15}\bigr).
}
]

For (n=8), the inequality is tight if all rows have size (4). In that extremal case every adjacent column-pair must occur in exactly one row, and every nonadjacent column-pair must occur in exactly two rows.

---

## 4. Surviving configurations and unresolved patterns

The matrix contradiction fails. Here is an explicit (8\times8) cyclic matrix satisfying all the above forbidden-submatrix rules and having every row sum equal to (4). Index rows and columns by (\mathbb Z_8), and set

[
S_i={i-2,i-1,i+1,i+3}\pmod 8.
]

The matrix is

[
\begin{pmatrix}
0&1&0&1&0&0&1&1\
1&0&1&0&1&0&0&1\
1&1&0&1&0&1&0&0\
0&1&1&0&1&0&1&0\
0&0&1&1&0&1&0&1\
1&0&0&1&1&0&1&0\
0&1&0&0&1&1&0&1\
1&0&1&0&0&1&1&0
\end{pmatrix}.
]

Every row has four (1)’s. A direct cyclic check shows that whenever two rows share two columns, the row-pair separates the column-pair.

For every (n\ge 9), another explicit cyclic family is

[
S_i={i-2,i-1,i+2,i+4}\pmod n.
]

For (n\ge 13), the difference set is Sidon modulo (n), so two rows share at most one column; hence fact (B) is vacuous. For (9\le n\le 12), the only double intersections are the following row separations, checked relative to row (0):

[
\begin{array}{c|c|c}
n & t & S_0\cap S_t\ \hline
9 & 3 & {-2,2}\
9 & 4 & {-1,2}\
9 & 5 & {-2,4}\
9 & 6 & {-1,4}\
10 & 4 & {-2,2}\
10 & 5 & {-1,4}\
10 & 6 & {-2,4}\
11 & 5 & {-2,4}\
11 & 6 & {-1,4}\
12 & 6 & {-2,4}.
\end{array}
]

In every listed case, one common column lies inside the arc ((0,t)) and the other lies outside it, so the crossing/separation rule is satisfied.

These examples show that facts (A) and (B), even with the common cyclic indexing of rows and columns, do not force a contradiction.

Some of these surviving matrix patterns are killed by extra metric geometry. For example, in the pattern

[
S_i={i-2,i-1,i+2,i+4},
]

the row centered at (p_i) contains both (p_{i-2}) and (p_{i-1}). Thus

[
|p_i-p_{i-2}|=|p_i-p_{i-1}|.
]

Applied cyclically, this forces every consecutive triangle (p_{i-2}p_{i-1}p_i) to have the polygon angle at (p_{i-1}) acute. If this happened for every (i), every interior angle of the polygon would be (<90^\circ), impossible for (n\ge 5), since the average interior angle of a convex (n)-gon is

[
\frac{(n-2)180^\circ}{n}>90^\circ.
]

But that argument uses additional metric information beyond (A) and (B).

A genuinely unresolved-by-this-argument exact pattern is any cyclic Sidon translate pattern such as

[
S_i={i+1,i+3,i+7,i+12}\pmod n,\qquad n\ge 23.
]

The six positive differences

[
2,4,5,6,9,11
]

are distinct, and for (n\ge 23) no positive difference is congruent to the negative of another. Therefore two rows share at most one column. All (2\times2) obstructions disappear, so facts (A) and (B) give no further information. Ruling out such a pattern geometrically would require additional distance/angle constraints not contained in (A) and (B).
