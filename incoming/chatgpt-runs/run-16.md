## 1. Convex-position crossing lemma

**Lemma (convex-position crossing lemma).**
Let (P={p_1,\dots,p_n}) be the vertices of a strictly convex (n)-gon in cyclic order. Suppose (i\ne k), and suppose (S_i\cap S_k) contains two indices (a,b). Then, in the cyclic order, the pair ({i,k}) separates the pair ({a,b}). Equivalently, the chord (p_ip_k) crosses the chord (p_ap_b).

**Proof.**
Since (a,b\in S_i\cap S_k), we have

[
|p_a-p_i|=|p_b-p_i|=r_i,\qquad |p_a-p_k|=|p_b-p_k|=r_k.
]

Thus (p_a,p_b) are the two intersection points of the circle centered at (p_i) of radius (r_i) and the circle centered at (p_k) of radius (r_k).

Let (L) be the line through (p_i,p_k). Reflection across (L) fixes both centers (p_i,p_k), and hence preserves both circles. Therefore it permutes their two common intersection points. Since the two points are distinct, reflection across (L) swaps (p_a) and (p_b). Equivalently, the common chord (p_ap_b) is perpendicular to (L), and (L) bisects (p_ap_b). This is the radical-axis/reflection step.

Choose coordinates so that

[
p_i=(0,0),\qquad p_k=(1,0),
]

and hence, for some (t\in\mathbb R) and (h>0),

[
p_a=(t,h),\qquad p_b=(t,-h).
]

The midpoint of (p_ap_b) is (q=(t,0)). We claim that (0<t<1).

If (t=0), then (p_i,q,p_a,p_b) are collinear, so (p_i,p_a,p_b) are three collinear vertices. This is impossible in a strictly convex polygon. This is one use of strict convexity.

Similarly, (t=1) would put (p_k,p_a,p_b) collinear, again impossible by strict convexity.

If (t<0), then (q) lies on the segment (p_ap_b), and (p_i=(0,0)) lies on the segment from (p_k=(1,0)) to (q=(t,0)). Hence

[
p_i\in \operatorname{conv}{p_k,p_a,p_b}.
]

That contradicts the fact that the listed points are vertices of a strictly convex polygon: no vertex may lie in the convex hull of the other vertices. This is the second use of strict convexity/convex-position extremality.

Similarly, if (t>1), then (p_k\in \operatorname{conv}{p_i,p_a,p_b}), again impossible.

Therefore (0<t<1). Hence the segment (p_ip_k), which is the horizontal segment from ((0,0)) to ((1,0)), meets the segment (p_ap_b), which is the vertical segment from ((t,-h)) to ((t,h)), at the interior point ((t,0)). So the chords (p_ip_k) and (p_ap_b) cross.

For four vertices of a strictly convex polygon, two chords cross exactly when their endpoints alternate in the cyclic order. Therefore ({i,k}) separates ({a,b}). (\square)

---

## 2. Exact theorem proved from facts (A) and (B)

Let (R_i=S_i). Abstract away the geometry and keep only the cyclic order plus the two rules:

[
\tag{A'} |R_i\cap R_k|\le 2\quad (i\ne k),
]

and

[
\tag{B'} \text{if }R_i\cap R_k={a,b},\text{ then }{i,k}\text{ separates }{a,b}.
]

The strongest conclusion obtainable from just these two rules is **not** a contradiction. In fact, the cyclic-matrix relaxation has examples with every row sum (4).

Here is the exact theorem I prove.

**Theorem.**
Let (M) be a cyclically indexed (0)-(1) matrix with diagonal zero, row sets (R_i), satisfying ((A')) and ((B')). Then

[
\sum_{i=1}^n \binom{|R_i|}{2}\le n(n-2).
]

Consequently, if every row has size at least (4), then (n\ge 8). Moreover, this is sharp for the cyclic-matrix relaxation: for every (n\ge 8), there exists such a cyclic matrix satisfying ((A')), ((B')), and (|R_i|=4) for all (i).

Thus facts (A) and (B), even with the common cyclic order of rows and columns, do **not** by themselves imply that the assumed matrix is impossible. Any full geometric contradiction would need additional metric information beyond (A) and (B).

---

## 3. Cyclic-matrix forbidden configurations and discharging argument

Write (I(i,k)) for the open cyclic interval from (i) to (k).

### Forbidden (2\times 2) cyclic submatrix

Suppose rows (i,k) both contain columns (a,b). Then, by (A), these are the only two common columns, and by (B), the pairs ({i,k}), ({a,b}) must alternate cyclically.

Therefore the all-one (2\times 2) submatrix

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

is forbidden unless the cyclic order is alternating:

[
i,a,k,b
\quad\text{or}\quad
i,b,k,a.
]

Equivalently,

[
|R_i\cap R_k\cap I(i,k)|\le 1,
\qquad
|R_i\cap R_k\cap I(k,i)|\le 1.
]

In particular, **adjacent rows cannot share two columns**, because if (i,k) are adjacent, one of the two cyclic intervals between them is empty.

Dually, fix two columns (a,b), and let

[
C_{ab}={i:a,b\in R_i}.
]

If two rows (i,k\in C_{ab}), then ({i,k}) must separate ({a,b}). Hence (C_{ab}) contains at most one row in each of the two open arcs determined by (a,b). Therefore

[
|C_{ab}|\le 2.
]

If (a,b) are adjacent columns, then one of those arcs is empty, so

[
|C_{ab}|\le 1.
]

Thus adjacent column pairs cannot occur together in two different rows.

### Forbidden (2\times 3) and (3\times 2) patterns

A (2\times 3) all-one submatrix is forbidden directly by (A), because two rows cannot share three columns.

A (3\times 2) all-one submatrix is also forbidden. Indeed, if three rows all contain the same two columns (a,b), then two of those three rows lie in the same open arc determined by (a,b), so they do not separate (a,b), contradicting (B).

So the following patterns are forbidden:

[
\begin{array}{c|ccc}
& a&b&c\ \hline
i&1&1&1\
k&1&1&1
\end{array}
\qquad\text{and}\qquad
\begin{array}{c|cc}
& a&b\ \hline
i&1&1\
k&1&1\
\ell&1&1
\end{array}.
]

### Pair-count discharging

Let

[
d_i=|R_i|.
]

Each row (i) sends one unit of charge to every unordered pair of columns contained in (R_i). Thus row (i) sends

[
\binom{d_i}{2}
]

units of charge, and the total charge is

[
Q=\sum_{i=1}^n \binom{d_i}{2}.
]

Equivalently,

[
Q=\sum_{{a,b}} c_{ab},
]

where

[
c_{ab}=|{i:a,b\in R_i}|.
]

From the forbidden configurations above:

[
c_{ab}\le 2
]

for every pair ({a,b}), and if (a,b) are adjacent in the cyclic order, then

[
c_{ab}\le 1.
]

There are (n) adjacent column pairs and (\binom n2-n) nonadjacent column pairs. Therefore

[
Q
\le n\cdot 1+2\left(\binom n2-n\right)
= n+n(n-1)-2n
= n(n-2).
]

So

[
\boxed{\sum_{i=1}^n \binom{|R_i|}{2}\le n(n-2).}
]

If every row has size at least (4), then each row contributes at least (\binom42=6), so

[
6n\le n(n-2).
]

Thus

[
n\ge 8.
]

A slightly more global bound follows from convexity:

[
\sum_i \binom{d_i}{2}
=====================

\frac12\left(\sum_i d_i^2-\sum_i d_i\right).
]

Let (m=\sum_i d_i). Since (\sum_i d_i^2\ge m^2/n),

[
\frac12\left(\frac{m^2}{n}-m\right)\le n(n-2),
]

so

[
\boxed{
m\le \frac n2\left(1+\sqrt{8n-15}\right).
}
]

This is far too weak to contradict (m\ge 4n) for large (n), but it proves impossibility for (n\le 7).

### Equality structure when (n=8)

If (n=8) and every row has size at least (4), then the above inequalities force equality everywhere.

Indeed,

[
\sum_i \binom{d_i}{2}\ge 8\binom42=48,
]

while

[
n(n-2)=8\cdot 6=48.
]

Hence every row has size exactly (4), every adjacent column pair occurs together in exactly one row, and every nonadjacent column pair occurs together in exactly two rows.

There is also a dual equality. Let (q_j) be the column sum of column (j). Since the total number of ones is (32), the average column sum is (4). Also,

[
\sum_j \binom{q_j}{2}
=====================

\sum_{i<k}|R_i\cap R_k|.
]

Adjacent row pairs share at most one column, and nonadjacent row pairs share at most two columns, so the same upper bound gives

[
\sum_j \binom{q_j}{2}\le 48.
]

But Jensen gives

[
\sum_j \binom{q_j}{2}\ge 8\binom42=48.
]

Thus every column also has size exactly (4), adjacent row pairs share exactly one column, and nonadjacent row pairs share exactly two columns.

So if (n=8), any abstract extremal matrix satisfying (A) and (B) must be a highly rigid (4)-regular configuration.

### Sharpness: cyclic matrices exist for all (n\ge 8)

Use indices modulo (n).

For (n=8), define

[
R_i={i-3,\ i-1,\ i+1,\ i+2}.
]

Equivalently, the first row is

[
R_0={1,2,5,7}.
]

For (n\ge 9), define

[
R_i={i-1,\ i+1,\ i+2,\ i+4}.
]

Equivalently,

[
R_0={-1,1,2,4}\pmod n.
]

Each row has size (4), and the diagonal is zero.

For (n\ge 9), take rows (0) and (t). The possible intersections are obtained from the difference set of

[
D={-1,1,2,4}.
]

The only two-point intersections occur for

[
t=2,\quad t=3,\quad t=n-2,\quad t=n-3,
]

and, in the special case (n=10), also for (t=5). They are respectively

[
{1,4},\quad {2,4},\quad {-1,2},\quad {-1,1},
]

and, when (n=10,t=5),

[
{-1,4}.
]

In every case, exactly one of the two common columns lies in the open interval from (0) to (t), and the other lies outside. Hence the common columns alternate with the row indices. All other intersections have size at most one. Therefore (A) and (B) hold.

For (n=8), with

[
D={-3,-1,1,2},
]

a direct check gives the two-point intersections

[
\begin{array}{c|c}
t & R_0\cap R_t\ \hline
2 & {-1,1}\
3 & {-3,2}\
4 & {-3,1}\
5 & {-1,2}\
6 & {-3,-1},
\end{array}
]

and each pair again alternates with ({0,t}). Thus (A) and (B) hold.

So the matrix relaxation has examples with all row sums (4) for every (n\ge 8). Therefore the desired contradiction cannot be obtained from (A) and (B) alone.

These matrices are not claimed to be geometrically realizable. In fact, the circulant examples above are ruled out by an additional metric input not contained in (A) or (B): since each row contains (i+1) and (i+2), and row (i+1) contains (i) and (i+2), the triangle

[
p_i p_{i+1} p_{i+2}
]

would be equilateral for every (i). Hence every interior angle would be (\pi/3), contradicting the angle sum ((n-2)\pi) for (n\ge 4). That argument uses actual distance equalities, not merely the intersection/crossing data.

---

## 4. Configurations left unresolved by the crossing/discharging method

The following patterns are not eliminated by facts (A) and (B).

### Circulant (4)-row patterns

For (n\ge 9),

[
\boxed{
M_{ij}=1
\iff
j-i\pmod n\in{-1,1,2,4}.
}
]

For (n=8),

[
\boxed{
M_{ij}=1
\iff
j-i\pmod 8\in{-3,-1,1,2}.
}
]

These satisfy all cyclic crossing restrictions. They are killed only by extra metric input, as explained above.

### A (B)-vacuous (13\times 13) pattern

Here is an exact (13)-row pattern with every row sum (4), diagonal zero, and every pair of rows intersecting in at most one column. Therefore fact (B) never even applies.

Rows are listed by their supports:

[
\begin{array}{c|c}
1 & {2,5,8,10}\
2 & {3,4,8,11}\
3 & {1,4,7,10}\
4 & {1,6,8,12}\
5 & {2,4,9,12}\
6 & {1,5,9,11}\
7 & {1,2,3,13}\
8 & {3,5,7,12}\
9 & {10,11,12,13}\
10 & {4,5,6,13}\
11 & {7,8,9,13}\
12 & {3,6,9,10}\
13 & {2,6,7,11}.
\end{array}
]

Every two listed supports meet in exactly one column, so (A) holds strongly and (B) is vacuous. This shows especially clearly why crossing data alone cannot force a contradiction: a full geometric proof would need to use additional constraints inside individual rows, or metric relations among distances, not just double intersections of rows.
