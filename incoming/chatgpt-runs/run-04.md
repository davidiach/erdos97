I will use indices modulo (n) in the matrix part, writing (0,1,\dots,n-1). Translate back to the problem’s notation by adding (1) to every index.

## 1. Convex-position crossing lemma

### Lemma B

Let (P={p_0,\dots,p_{n-1}}) be the vertices of a strictly convex polygon in cyclic order. Suppose (i\ne k), and suppose two distinct indices (a,b) satisfy
[
a,b\in S_i\cap S_k.
]
Then the pair ({i,k}) separates the pair ({a,b}) in the cyclic order. Equivalently, the chord (p_ip_k) crosses the chord (p_ap_b).

### Proof

Since (a,b\in S_i\cap S_k),
[
|p_a-p_i|=|p_b-p_i|,\qquad |p_a-p_k|=|p_b-p_k|.
]
Thus both (p_i) and (p_k) lie on the perpendicular bisector of the segment (p_ap_b). Since (p_i\ne p_k), the line
[
L:=p_ip_k
]
is exactly that perpendicular bisector. Equivalently, using the radical-axis/common-chord property for the two circles centered at (p_i,p_k), the common chord (p_ap_b) is perpendicular to the line of centers (p_ip_k), and (p_ip_k) bisects (p_ap_b).

Let
[
m=\frac{p_a+p_b}{2}.
]
Then (m\in L), (p_ap_b\perp L), and reflection across (L=p_ip_k) sends (p_a) to (p_b). Hence (p_a,p_b) lie in opposite open half-planes bounded by (L).

It remains to prove that (m) lies on the segment (p_ip_k), not merely on the infinite line (p_ip_k). Suppose not. Then (m) lies outside the open segment (p_ip_k), so one of (p_i,p_k) lies on the segment joining the other one to (m). Say (p_k) lies between (p_i) and (m). Then for some (0<t<1),
[
p_k=(1-t)p_i+t m
=(1-t)p_i+\frac t2p_a+\frac t2p_b.
]
Thus (p_k) is a strict convex combination of (p_i,p_a,p_b), so (p_k) lies inside the triangle (\operatorname{conv}{p_i,p_a,p_b}).

**This is the exact step where strict convexity is used:** in a strictly convex polygon, every listed vertex is an extreme point of the convex hull; no vertex may lie in the convex hull of the other vertices, and no three vertices are collinear. Therefore the above containment is impossible. The endpoint cases (m=p_i) or (m=p_k) are also impossible, since then a polygon vertex would lie on the segment (p_ap_b), contradicting strict convexity.

Hence (m) lies in the open segment (p_ip_k). Since (m) is also the midpoint of (p_ap_b), the two segments (p_ip_k) and (p_ap_b) cross at (m). For four vertices of a convex polygon, two chords cross exactly when their endpoints alternate in the cyclic order. Therefore ({i,k}) separates ({a,b}). (\square)

---

## 2. Exact theorem proved

Call a cyclic (0)-(1) matrix (M) **admissible** if its row sets (R_i={j:M_{ij}=1}) satisfy:

1. (i\notin R_i);
2. (|R_i\cap R_k|\le 2) for (i\ne k);
3. if (R_i\cap R_k={a,b}), then ({i,k}) separates ({a,b}) cyclically.

Every matrix arising from the geometric problem is admissible by Fact (A) and the lemma above.

### Theorem

For admissible cyclic matrices:

1. The following cyclic submatrices are forbidden:

   * any (2\times 3) all-one submatrix;
   * any noncrossing (2\times 2) all-one submatrix;
   * in particular, two adjacent rows have at most one common (1);
   * no (3\times 2) all-one submatrix is possible.

2. If every row has size at least (4), then (n\ge 8).

3. If (n=8) and every row has size at least (4), then in fact every row has size exactly (4).

4. The matrix-only contradiction cannot be proved from (A) and (B) alone: for every (n\ge 8) there exists an admissible cyclic matrix with every row sum exactly (4).

Thus a full geometric contradiction, if true, requires additional metric information beyond (A) and (B).

---

## 3. Cyclic-matrix and discharging argument

### Forbidden (2\times 2) patterns

Let rows (i,k) share two columns (a,b). By admissibility, the four indices must alternate cyclically. Equivalently, if (a,b) lie in the same open arc of the cycle after removing (i,k), then the submatrix

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

is forbidden.

So a (2\times 2) all-one submatrix is allowed only when it is a crossing pattern.

In particular, if (k=i+1), then one arc between (i) and (k) is empty. Hence two adjacent rows cannot share two columns:

[
|R_i\cap R_{i+1}|\le 1.
]

More generally, if (k=i+2), then a two-column intersection must use the unique middle vertex (i+1).

### Forbidden (2\times 3) and (3\times 2) patterns

Fact (A) immediately forbids any (2\times 3) all-one submatrix, because two rows cannot share three columns.

A (3\times 2) all-one submatrix is also impossible. Suppose rows (x,y,z) all contain columns (a,b). By Fact (A), each pair of those rows has intersection exactly ({a,b}). By the crossing lemma, every pair among (x,y,z) must be separated by (a,b). But deleting (a,b) leaves two arcs, and three row indices cannot be pairwise placed in opposite arcs. Contradiction.

So every column pair can occur together in at most two rows.

### Adjacent-row discharging inequality

Let
[
m_i=|R_i|,\qquad T=\sum_i m_i.
]
Because adjacent rows share at most one column,
[
m_i+m_{i+1}
=|R_i\cup R_{i+1}|+|R_i\cap R_{i+1}|
\le n+1.
]
Summing over all (i),
[
2T=\sum_i(m_i+m_{i+1})\le n(n+1),
]
so
[
T\le \frac{n(n+1)}2.
]

If every (m_i\ge 4), then (T\ge 4n). Hence
[
4n\le \frac{n(n+1)}2,
]
so (n\ge 7). This already rules out (n\le 6).

### The (n=7) case

For (n=7), the inequality gives
[
T\le 28,
]
while row sums at least (4) give
[
T\ge 28.
]
Thus equality holds everywhere. Therefore every row has size exactly (4), and every adjacent pair of rows has intersection exactly (1).

Let
[
Z_i=[7]\setminus R_i.
]
Then (|Z_i|=3). Since (|R_i\cap R_{i+1}|=1), we have
[
|Z_i\cup Z_{i+1}|=6,
]
so
[
Z_i\cap Z_{i+1}=\varnothing.
]

Now fix (i). Both (Z_i) and (Z_{i+2}) are disjoint from (Z_{i+1}), so both are (3)-subsets of the (4)-element set ([7]\setminus Z_{i+1}). Therefore
[
|Z_i\cap Z_{i+2}|\ge 2.
]
But then
[
|R_i\cap R_{i+2}|
=7-|Z_i\cup Z_{i+2}|
=7-(6-|Z_i\cap Z_{i+2}|)
=1+|Z_i\cap Z_{i+2}|
\ge 3,
]
contradicting Fact (A). Hence no admissible matrix with all row sums at least (4) exists for (n=7).

Therefore (n\ge 8).

### The (n=8) row-size structure

For (n=8), adjacent rows satisfy
[
m_i+m_{i+1}\le 9.
]
Since every (m_i\ge 4), every row has size (4) or (5), and no two adjacent rows can both have size (5).

Suppose some row (R_i) has size (5). Then its neighbors (R_{i-1},R_{i+1}) have size (4). The adjacent-row bound forces
[
|R_i\cap R_{i-1}|=|R_i\cap R_{i+1}|=1.
]
Let (Z_j=[8]\setminus R_j). Then
[
|Z_i|=3,\qquad |Z_{i-1}|=|Z_{i+1}|=4,
]
and the equations above imply
[
Z_i\cap Z_{i-1}=Z_i\cap Z_{i+1}=\varnothing.
]
Thus both (Z_{i-1}) and (Z_{i+1}) are (4)-subsets of the same (5)-element set ([8]\setminus Z_i). Hence
[
|Z_{i-1}\cup Z_{i+1}|\le 5.
]
Therefore
[
|R_{i-1}\cap R_{i+1}|
=8-|Z_{i-1}\cup Z_{i+1}|
\ge 3,
]
again contradicting Fact (A). Thus no row has size (5), and every row has size exactly (4).

### Why the matrix contradiction stops here

The preceding argument is sharp as a matrix argument. For (n=8), define

[
R_i=i+{1,2,5,7}\pmod 8.
]

Explicitly:

[
\begin{array}{c|c}
i & R_i\ \hline
0 & {1,2,5,7}\
1 & {0,2,3,6}\
2 & {1,3,4,7}\
3 & {0,2,4,5}\
4 & {1,3,5,6}\
5 & {2,4,6,7}\
6 & {0,3,5,7}\
7 & {0,1,4,6}
\end{array}
]

This matrix has row sum (4). For row difference (d=1,\dots,7),

[
{1,2,5,7}\cap(d+{1,2,5,7})
]

is respectively

[
{2},\ {1,7},\ {2,5},\ {1,5},\ {2,7},\ {5,7},\ {1}.
]

Whenever the intersection has size (2), one common column lies in the clockwise interval from (i) to (i+d), and the other lies outside it. Hence every (2\times 2) all-one submatrix is crossing. So this is an admissible cyclic matrix with all row sums (4).

For every (n\ge 9), another admissible construction is

[
R_i=i+{1,2,4,8}\pmod n.
]

For (n\ge 15), no two rows share more than one column, so Fact (B) is vacuous. For (9\le n\le 14), the only two-column intersections are:

[
\begin{array}{c|c}
n & (d,\ {1,2,4,8}\cap(d+{1,2,4,8}))\ \hline
9 & (2,{1,4}),\ (3,{2,4}),\ (6,{1,8}),\ (7,{2,8})\
10 & (3,{1,4}),\ (4,{2,8}),\ (6,{4,8}),\ (7,{1,8})\
11 & (4,{1,8}),\ (7,{4,8})\
12 & (6,{2,8})\
13 & (6,{1,8}),\ (7,{2,8})\
14 & (7,{1,8})
\end{array}
]

In each case, one shared column lies inside the interval from (i) to (i+d), and the other lies outside. Hence the crossing rule holds.

So (A) and (B) alone do not imply the desired contradiction.

---

## 4. Configurations remaining after the matrix argument

Using the notation

[
C_n(D):\qquad R_i=i+D\pmod n,
]

the following exact patterns are not eliminated by the cyclic-matrix rules (A) and (B):

[
C_8({1,2,5,7}),
]

and, for every (n\ge 9),

[
C_n({1,2,4,8}).
]

There is also a sparse family for which the crossing lemma is completely vacuous. For (n\ge 29), let

[
R_i=i+{1,3,7,15}\pmod n.
]

The positive differences among ({1,3,7,15}) are

[
2,4,6,8,12,14,
]

all distinct. Since (n\ge 29), no two nonzero differences become congruent modulo (n). Hence two rows share at most one column. This gives an admissible row-sum-(4) matrix with no (2\times 2) all-one submatrix at all.

These are not claimed to be geometrically realizable. They show only that the matrix consequences of (A) and (B) are insufficient.

One example of an additional geometric obstruction is this: if a geometric matrix had

[
M_{i,i+1}=M_{i,i+2}=1
]

for every (i), then

[
|p_i-p_{i+1}|=|p_i-p_{i+2}|.
]

Let (\alpha_{i+1}) be the interior angle at (p_{i+1}). By the law of cosines in triangle (p_i p_{i+1}p_{i+2}),

[
|p_i-p_{i+2}|^2
===============

|p_i-p_{i+1}|^2+|p_{i+1}-p_{i+2}|^2
-2|p_i-p_{i+1}||p_{i+1}-p_{i+2}|\cos\alpha_{i+1}.
]

Since (|p_i-p_{i+2}|=|p_i-p_{i+1}|), this gives

[
\cos\alpha_{i+1}
================

\frac{|p_{i+1}-p_{i+2}|}{2|p_i-p_{i+1}|}>0,
]

so every interior angle would be (<\pi/2), impossible for a convex (n)-gon with (n\ge 4). This extra angle argument rules out the simple circulant patterns above geometrically, but it is not a consequence of (A) and (B). The sparse pattern (C_n({1,3,7,15})) remains a genuine unresolved matrix pattern under the methods developed here.
