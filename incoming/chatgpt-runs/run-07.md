## 1. Convex-position crossing lemma

Let (P={p_1,\dots,p_n}) be the vertices of a strictly convex polygon in cyclic order. Suppose (i\ne k) and

[
S_i\cap S_k={a,b}.
]

Then

[
|p_a-p_i|=|p_b-p_i|=r_i,\qquad |p_a-p_k|=|p_b-p_k|=r_k.
]

So (p_a,p_b) are the two intersection points of the two circles centered at (p_i,p_k).

Let (L) be the line (p_ip_k). Reflection in (L) fixes both circles, because both centers lie on (L). Hence reflection in (L) permutes their two intersection points. Since the intersection points are distinct, reflection swaps (p_a) and (p_b). Equivalently, (p_a,p_b) are mirror images across (L). This is the radical-axis/common-chord property: the line (p_ap_b) is perpendicular to (p_ip_k), and its midpoint lies on (p_ip_k).

It remains to show that the midpoint of (p_ap_b) lies between (p_i) and (p_k). Put coordinates so that

[
p_i=(0,0),\qquad p_k=(d,0),\qquad d>0.
]

Because (p_a,p_b) are reflections across the (x)-axis, write

[
p_a=(t,u),\qquad p_b=(t,-u),\qquad u>0.
]

If (t<0), then (p_i=(0,0)) lies inside the triangle with vertices (p_k,p_a,p_b). Indeed,

[
p_i=\frac{-t}{d-t}p_k+\frac{d}{2(d-t)}p_a+\frac{d}{2(d-t)}p_b,
]

and all coefficients are positive. If (t=0), then (p_i) lies on the segment (p_ap_b). Both cases contradict strict convexity: a vertex of a strictly convex polygon is an extreme point, and no vertex lies in the convex hull of the other vertices; in the boundary case (t=0), strict convexity also excludes collinearity with two other vertices.

Similarly, if (t>d), then (p_k) lies inside the triangle with vertices (p_i,p_a,p_b), and if (t=d), then (p_k) lies on (p_ap_b). Again this contradicts strict convexity.

Thus

[
0<t<d.
]

Therefore the vertical segment (p_ap_b) crosses the horizontal segment (p_ip_k) in their interiors. Hence the chord (p_ip_k) crosses the chord (p_ap_b).

Finally, for four vertices of a strictly convex polygon, two chords cross in their interiors if and only if their endpoints alternate in the cyclic order. Therefore the pair ({i,k}) separates the pair ({a,b}).

The exact use of strict convexity is the step excluding (t\le 0) and (t\ge d): otherwise one of (p_i,p_k) lies inside or on the triangle/segment determined by the other three points, so it is not a strict convex vertex.

---

## 2. The exact theorem proved

Let (M) be a cyclically indexed (0)-(1) matrix with row supports

[
R_i={j:M_{ij}=1}.
]

Assume:

[
|R_i\cap R_k|\le 2
]

for all (i\ne k), and whenever (R_i\cap R_k={a,b}), the pairs ({i,k}) and ({a,b}) separate each other in the cyclic order.

Then the following hold.

**Theorem.**

1. The following cyclic submatrices are forbidden:

   * a (2\times 3) all-one submatrix;
   * a (3\times 2) all-one submatrix;
   * a (2\times 2) all-one submatrix whose two row indices do not separate its two column indices.

2. If (d_i=|R_i|), then

[
\sum_i \binom{d_i}{2}\le n(n-2).
]

Consequently, if (m=\sum_i d_i), then

[
m\le \frac n2\left(1+\sqrt{8n-15}\right).
]

3. In particular, if every row has size at least (4), then

[
n\ge 8.
]

4. For (n=8), the bound is sharp in the matrix sense. If every row has size at least (4), then in fact every row has size exactly (4), every column also has size (4), adjacent row pairs meet in exactly one column, nonadjacent row pairs meet in exactly two columns, adjacent column pairs occur in exactly one row, and nonadjacent column pairs occur in exactly two rows.

5. No contradiction can be derived from facts (A) and (B) alone. There are cyclic (0)-(1) matrices satisfying all the above rules with every row of size (4). Thus any proof of geometric nonexistence must use additional metric geometry beyond (A) and (B).

---

## 3. Cyclic-matrix / discharging argument

Write (R_i) for row (i).

### Forbidden (2\times 3)

If two rows (i,k) had three common columns (a,b,c), then

[
|R_i\cap R_k|\ge 3,
]

contradicting fact (A). Therefore no (2\times 3) all-one submatrix is possible.

### Forbidden noncrossing (2\times 2)

If rows (i,k) both contain columns (a,b), then (R_i\cap R_k) contains ({a,b}). By (A), it contains exactly those two columns. By the crossing lemma, ({i,k}) must separate ({a,b}). Hence a (2\times 2) all-one submatrix is allowed only in the alternating cyclic pattern

[
i,\ a,\ k,\ b
]

up to reversal and rotation. In particular, adjacent rows cannot share two columns, and adjacent columns cannot occur together in two rows.

### Forbidden (3\times 2)

Suppose three rows (i,k,\ell) all contain the same two columns (a,b). Then each pair of rows among (i,k,\ell) shares (a,b), so by (B) each pair among (i,k,\ell) must separate (a,b).

But the two columns (a,b) cut the cyclic order into two arcs. Among three row indices (i,k,\ell), two lie on the same arc. That pair does not separate (a,b), contradiction.

Thus every pair of columns is contained in at most two rows.

### Discharging count

For each row (i), put one unit of charge on every unordered pair of columns inside (R_i). Row (i) contributes

[
\binom{d_i}{2}
]

units of charge. Thus the total charge is

[
X=\sum_i \binom{d_i}{2}.
]

Now fix a column pair ({a,b}). Let

[
\lambda_{ab}=#{i:\ a,b\in R_i}.
]

The previous (3\times 2) argument gives

[
\lambda_{ab}\le 2.
]

A column pair with (\lambda_{ab}=2) corresponds to two rows (i,k) sharing (a,b). By (B), ({i,k}) must separate ({a,b}). Therefore (i,k) cannot be adjacent. Also, two different repeated column pairs cannot correspond to the same row pair, because then that row pair would share at least three columns, contradicting (A).

Hence the number of repeated column pairs is at most the number of nonadjacent row pairs:

[
\binom n2-n.
]

There are (\binom n2) column pairs total. Each column pair can receive one first charge, and at most (\binom n2-n) column pairs can receive a second charge. Therefore

[
X\le \binom n2+\left(\binom n2-n\right)=n(n-2).
]

So

[
\boxed{\sum_i \binom{d_i}{2}\le n(n-2).}
]

If all (d_i\ge 4), then

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

For the total number of ones (m=\sum_i d_i), use convexity:

[
\sum_i \binom{d_i}{2}
=\frac12\left(\sum_i d_i^2-\sum_i d_i\right)
\ge \frac12\left(\frac{m^2}{n}-m\right).
]

Since the left side is at most (n(n-2)),

[
\frac12\left(\frac{m^2}{n}-m\right)\le n(n-2).
]

Solving gives

[
\boxed{m\le \frac n2\left(1+\sqrt{8n-15}\right).}
]

### The extremal (n=8) structure

Assume now (n=8) and all (d_i\ge 4). The inequality gives

[
\sum_i \binom{d_i}{2}\le 8\cdot 6=48.
]

But each row contributes at least (6). Hence equality holds, and every row has size exactly (4).

Equality in the discharging argument forces the following:

* every column pair appears in at least one row;
* exactly (20=\binom82-8) column pairs appear in two rows;
* those (20) repeated column pairs correspond bijectively to the (20) nonadjacent row pairs.

Adjacent column pairs cannot be repeated, because adjacent column indices cannot be separated by any pair of row indices. Since there are exactly (8) singleton column pairs, the singleton column pairs are precisely the adjacent column pairs. Therefore every nonadjacent column pair appears in exactly two rows.

Fix a column (j). The two adjacent column pairs involving (j) occur once, and the five nonadjacent column pairs involving (j) occur twice. Hence the number of pair-incidences involving (j) is

[
2\cdot 1+5\cdot 2=12.
]

Each row containing (j) contributes (3) such pair-incidences, because every row has size (4). Therefore column (j) appears in (4) rows. Thus every column has size (4).

Now count row intersections:

[
\sum_{i<k}|R_i\cap R_k|
=\sum_j \binom{4}{2}
=8\cdot 6
=48.
]

The (20) nonadjacent row pairs each contribute (2), giving (40). The remaining (8) adjacent row pairs can contribute at most (1) each, and therefore each adjacent row pair contributes exactly (1).

Finally, for any (i), rows (i) and (i+2) are nonadjacent and therefore share exactly two columns. By (B), those two columns must separate (i) and (i+2). The open arc from (i) to (i+2) contains only (i+1), so (i+1\in R_i). Similarly, using rows (i) and (i-2), we get (i-1\in R_i). Thus in the extremal (n=8) case every row contains its two cyclic neighbors.

---

## 4. Configurations that remain unresolved by the ((A),(B)) argument

The matrix-only contradiction fails. Here is an exact (8\times 8) cyclic pattern satisfying all constraints, with every row of size (4). Indices are taken modulo (8), and

[
R_i={i+1,\ i+2,\ i+5,\ i+7}.
]

Equivalently,

[
M=
\begin{pmatrix}
0&1&1&0&0&1&0&1\
1&0&1&1&0&0&1&0\
0&1&0&1&1&0&0&1\
1&0&1&0&1&1&0&0\
0&1&0&1&0&1&1&0\
0&0&1&0&1&0&1&1\
1&0&0&1&0&1&0&1\
1&1&0&0&1&0&1&0
\end{pmatrix}.
]

For row difference (d), the common columns of rows (0) and (d) are:

[
\begin{array}{c|c}
d & R_0\cap R_d\
\hline
1 & {2}\
2 & {1,7}\
3 & {2,5}\
4 & {1,5}\
5 & {2,7}\
6 & {5,7}\
7 & {1}
\end{array}
]

Whenever the intersection has size (2), one common column lies on each side of the pair ({0,d}), so the crossing condition (B) is satisfied.

There are also infinite unresolved matrix patterns. For every (n\ge 29), define

[
R_i={i+1,\ i+3,\ i+7,\ i+15}\pmod n.
]

The difference set

[
D={1,3,7,15}
]

has all nonzero pairwise differences distinct modulo (n) for (n\ge 29), because the positive differences are

[
2,4,6,8,12,14
]

and no positive difference equals another or the negative of another modulo (n). Hence two rows share at most one column. Fact (A) holds, and fact (B) is vacuous. Every row still has size (4).

So the cyclic-matrix/discharging method proves a sharp lower bound (n\ge 8), strong forbidden submatrix rules, and a rigid extremal structure at (n=8), but it cannot prove full nonexistence from facts (A) and (B) alone. Any final geometric contradiction must use additional metric input beyond the radical-axis crossing lemma.
