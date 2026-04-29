## 1. Convex-position crossing lemma

Let the vertices (p_1,\dots,p_n) be in cyclic order. I will say that two unordered pairs ({x,y}) and ({u,v}) **separate** each other if, after deleting (x,y) from the cyclic order, the two remaining open arcs contain (u) and (v) in different arcs. Equivalently, in a strictly convex polygon, the chords (p_xp_y) and (p_up_v) cross in their relative interiors.

### Lemma B

If (S_i\cap S_k={a,b}) with (i\neq k), then ({i,k}) separates ({a,b}). Equivalently, the chord (p_ip_k) crosses the chord (p_ap_b).

### Proof

The four indices (i,k,a,b) are distinct: (i\notin S_i), (k\notin S_k), and (a,b\in S_i\cap S_k).

Let (L) be the line through (p_i,p_k). Put coordinates so that

[
p_i=(0,0),\qquad p_k=(d,0),\qquad d>0.
]

A common point (q=(x,y)) of the two circles satisfies

[
x^2+y^2=r_i^2,
]
[
(x-d)^2+y^2=r_k^2.
]

Subtracting gives

[
2dx=d^2+r_i^2-r_k^2,
]

so every common point of the two circles has the same (x)-coordinate. Thus the common chord is a vertical line, perpendicular to (L); this is the radical-axis property. Since the two circles have the two distinct common points (p_a,p_b), they must be

[
p_a=(x_0,h),\qquad p_b=(x_0,-h)
]

for some (h\neq 0), after perhaps swapping (a,b). Therefore (p_a,p_b) are reflections of one another across (L), and they lie in opposite open half-planes bounded by (L).

Now use convexity. The chord (p_ip_k) splits the boundary of the convex polygon into two polygonal chains from (p_i) to (p_k). Convexity puts these two chains in opposite closed half-planes bounded by (L).

**This is the exact point where strict convexity is used:** because the polygon is strictly convex, no vertex other than (p_i,p_k) lies on (L). Hence the two chains actually lie in opposite **open** half-planes, except for their endpoints (p_i,p_k).

Since (p_a) and (p_b) are on opposite sides of (L), they must lie on opposite boundary arcs between (p_i) and (p_k). Therefore ({i,k}) separates ({a,b}), and the chords (p_ip_k) and (p_ap_b) cross. (\square)

---

## 2. Exact theorem proved

Let (M) be a cyclic (n\times n) zero-diagonal (0)-(1) matrix with row supports

[
R_i={j:M_{ij}=1},
]

satisfying:

[
\tag{A} |R_i\cap R_k|\le 2\quad\text{for }i\neq k,
]

and

[
\tag{B} |R_i\cap R_k|=2\implies {i,k}\text{ separates }R_i\cap R_k.
]

Then the following hold.

[
\boxed{\sum_{i=1}^n \binom{|R_i|}{2}\le n(n-2).}
]

Consequently, if every row has size at least (4), then

[
6n\le n(n-2),
]

so

[
\boxed{n\ge 8.}
]

This is the strongest possible conclusion from only (A) and (B): for every (n\ge 8), there exists a cyclic zero-diagonal matrix satisfying (A), (B), and (|R_i|=4) for every row.

Thus a full contradiction cannot be obtained from (A) and (B) alone. Any proof that the original geometric configuration is impossible must use additional metric geometry beyond the crossing lemma.

A general bound on the total number of ones (m=\sum_i |R_i|) is

[
\boxed{
m\le \frac n2\left(1+\sqrt{8n-15}\right).
}
]

For (n=8), equality in the counting argument forces strong structure: every row and every column has sum (4), every adjacent column-pair occurs in exactly one row, every non-adjacent column-pair occurs in exactly two rows, every adjacent row-pair intersects in exactly one column, every non-adjacent row-pair intersects in exactly two columns, and in particular

[
i-1,\ i+1\in R_i
]

for every (i), with indices taken cyclically.

---

## 3. Cyclic-matrix and discharging argument

Work with indices modulo (n).

### Forbidden (2\times 2) cyclic submatrix

Suppose rows (i,k) and columns (a,b) contain the all-one submatrix

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

Then (a,b\in R_i\cap R_k). By (A), this is already the full intersection unless there is an immediate violation. By (B), the only allowed case is that ({i,k}) separates ({a,b}). Therefore the following all-one (2\times 2) pattern is forbidden whenever (a,b) lie on the same cyclic arc between (i) and (k):

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1
\end{array}
\qquad
\text{with }a,b\text{ not separated by }i,k.
]

In particular:

* two adjacent rows cannot have two common (1)’s;
* two adjacent columns cannot be contained together in two different rows.

Also, by (A), the all-one (2\times 3) pattern

[
\begin{array}{c|ccc}
& a & b & c\ \hline
i & 1 & 1 & 1\
k & 1 & 1 & 1
\end{array}
]

is forbidden.

A useful derived forbidden pattern is the all-one (3\times 2) pattern

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1\
\ell & 1 & 1
\end{array}
]

because if three rows all contain (a,b), then any two of those rows would have to be separated by (a,b), but the two arcs between (a,b) can contain at most one such row each.

### Column-pair capacity

For distinct columns (a,b), define

[
q_{ab}=#{i:a,b\in R_i}.
]

If two rows (i,k) both contain (a,b), then by (B), ({i,k}) must be separated by ({a,b}). Therefore one of (i,k) lies on one arc between (a,b), and the other lies on the other arc.

Hence

[
q_{ab}\le 2.
]

If (a,b) are adjacent cyclically, one of the arcs between them is empty, so

[
q_{ab}\le 1.
]

Now count pairs of (1)’s inside rows. Each row (i) contributes (\binom{|R_i|}{2}) unordered column-pairs. On the other hand, each adjacent column-pair can be counted at most once, and each non-adjacent column-pair can be counted at most twice. There are (n) adjacent column-pairs and (\binom n2-n) non-adjacent column-pairs. Thus

[
\sum_i \binom{|R_i|}{2}
=======================

\sum_{{a,b}} q_{ab}
\le
n+2\left(\binom n2-n\right)
===========================

n(n-2).
]

This is the main discharging inequality: every row distributes one unit of charge to each pair of its (1)’s; adjacent column-pairs have capacity (1), and non-adjacent column-pairs have capacity (2).

If (|R_i|\ge 4) for all (i), then

[
\sum_i \binom{|R_i|}{2}\ge 6n.
]

Therefore

[
6n\le n(n-2),
]

so (n\ge 8).

### Bound on the total number of ones

Let

[
m=\sum_i |R_i|.
]

By convexity of (x\mapsto \binom x2),

[
\sum_i \binom{|R_i|}{2}
\ge
n\binom{m/n}{2}
===============

\frac{m^2}{2n}-\frac m2.
]

Together with the upper bound (n(n-2)), this gives

[
\frac{m^2}{2n}-\frac m2\le n(n-2).
]

Solving the quadratic inequality,

[
m\le \frac n2\left(1+\sqrt{8n-15}\right).
]

### Dual row-pair inequality

Let (c_j) be the column sum of column (j). Counting pairs of rows inside columns gives

[
\sum_j \binom{c_j}{2}
=====================

\sum_{{i,k}} |R_i\cap R_k|.
]

By (A), a non-adjacent row-pair has intersection at most (2). If (i,k) are adjacent, then they cannot share two columns, because two common columns would have to be separated by adjacent indices (i,k), impossible. Therefore adjacent row-pairs have intersection at most (1). Hence

[
\sum_j \binom{c_j}{2}\le n(n-2).
]

### Extremal structure when (n=8)

Assume (n=8) and every row has size at least (4). The inequality gives

[
\sum_i \binom{|R_i|}{2}\le 48.
]

But each row contributes at least (6), so equality holds. Therefore every row has size exactly (4).

The total number of ones is (32), so the average column sum is (4). The dual inequality gives

[
\sum_j \binom{c_j}{2}\le 48.
]

Convexity gives

[
\sum_j \binom{c_j}{2}\ge 8\binom 42=48,
]

so equality holds, and every column has sum (4).

Also, every row-pair capacity is saturated: adjacent row-pairs meet in exactly one column, and non-adjacent row-pairs meet in exactly two columns.

Now fix (i). Rows (i) and (i+2) are non-adjacent, so they share exactly two columns. By (B), those two common columns must be separated by ({i,i+2}). The short arc from (i) to (i+2) contains only (i+1), so one of the two common columns must be (i+1). Hence

[
i+1\in R_i.
]

Similarly, applying the same argument to rows (i) and (i-2), we get

[
i-1\in R_i.
]

Thus, in the extremal (n=8) case,

[
\boxed{i-1,\ i+1\in R_i\quad\text{for every }i.}
]

### Why the full contradiction fails at the matrix level

For (n=8), define

[
R_i={i+1,i+2,i+5,i+7}\pmod 8.
]

Every row has size (4). Comparing row (0) with row (t), the intersections of size (2) are:

[
\begin{array}{c|c}
t & R_0\cap R_t\ \hline
2 & {1,7}\
3 & {2,5}\
4 & {1,5}\
5 & {2,7}\
6 & {5,7}
\end{array}
]

In every case, one common column lies on the arc from (0) to (t), and the other lies on the complementary arc. Thus (B) holds. For (t=1,7), the intersection has size (1). Therefore (A) also holds.

For every (n\ge 9), define instead

[
R_i={i+1,i+2,i+4,i+8}\pmod n.
]

Again every row has size (4). For (n\ge 15), the nonzero differences among

[
{1,2,4,8}
]

are

[
\pm1,\ \pm2,\ \pm3,\ \pm4,\ \pm6,\ \pm7,
]

all distinct modulo (n). Hence two different rows share at most one column, so (B) is vacuous and (A) holds.

For (9\le n\le 14), the only row differences producing two common columns are listed below; each listed pair is separated:

[
\begin{array}{c|c}
n & (t,\ R_0\cap R_t)\ \hline
9 & (2,{1,4}),\ (3,{2,4}),\ (6,{1,8}),\ (7,{2,8})\
10 & (3,{1,4}),\ (4,{2,8}),\ (6,{4,8}),\ (7,{1,8})\
11 & (4,{1,8}),\ (7,{4,8})\
12 & (6,{2,8})\
13 & (6,{1,8}),\ (7,{2,8})\
14 & (7,{1,8})
\end{array}
]

In every listed case, if (R_0\cap R_t={x,y}), then

[
0<x<t<y<n,
]

so the two common columns lie on opposite arcs between rows (0) and (t). Thus (B) holds. All other row intersections have size at most (1).

Therefore cyclic matrices satisfying (A), (B), and (|R_i|=4) exist for every (n\ge 8). The desired matrix-level contradiction is false.

---

## 4. Remaining unresolved configurations

The cyclic-matrix argument rules out noncrossing (2\times 2) all-one rectangles, but it does **not** rule out crossing rectangles. The basic allowed local pattern is:

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1
\end{array}
\qquad
\text{with cyclic order } i<a<k<b.
]

The exact formal patterns not eliminated by (A) and (B) include the following.

For (n=8):

[
\boxed{
R_i={i+1,i+2,i+5,i+7}\pmod 8.
}
]

Its reflection is also allowed:

[
\boxed{
R_i={i+1,i+3,i+6,i+7}\pmod 8.
}
]

For every (n\ge 9):

[
\boxed{
R_i={i+1,i+2,i+4,i+8}\pmod n.
}
]

and its reflected version is also allowed.

These are formal cyclic (0)-(1) matrices satisfying all consequences of (A) and (B) used above. They are not asserted to be geometrically realizable as equal-radius data of a strictly convex polygon. To rule them out geometrically, one must use additional metric input, for example actual side-length equalities forced by entries such as (i-1,i+1\in R_i), angle-sum constraints, or other distance consistency conditions not encoded in (A) and (B).
