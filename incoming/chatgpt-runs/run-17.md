## 1. Convex-position crossing lemma

**Lemma (convex-position crossing lemma).**
Let (P={p_1,\dots,p_n}) be the vertices of a strictly convex polygon in cyclic order. Suppose two distinct rows (S_i,S_k) share two distinct indices (a,b). Thus

[
|p_a-p_i|=|p_b-p_i|=r_i,\qquad |p_a-p_k|=|p_b-p_k|=r_k.
]

Then the pair ({i,k}) separates the pair ({a,b}) in the cyclic order. Equivalently, the chords (p_ip_k) and (p_ap_b) cross.

**Proof.**
The four indices (i,k,a,b) are distinct: (a,b\in S_i\cap S_k), while (i\notin S_i) and (k\notin S_k).

Consider the two circles

[
C_i={x:|x-p_i|=r_i},\qquad C_k={x:|x-p_k|=r_k}.
]

Both (p_a) and (p_b) lie on both circles. The radical axis of (C_i) and (C_k) is the common chord line (p_ap_b), and the radical-axis equation is obtained by subtracting

[
|x-p_i|^2-r_i^2=0,\qquad |x-p_k|^2-r_k^2=0.
]

Its normal vector is parallel to (p_k-p_i), so the line (p_ap_b) is perpendicular to the line (p_ip_k). Since (p_a,p_b) are also on the circle centered at (p_i), the perpendicular from (p_i) to the chord (p_ap_b) bisects that chord. Hence the line (p_ip_k) is the perpendicular bisector of the segment (p_ap_b). Therefore (p_a) and (p_b) are reflections of one another across the line (p_ip_k).

Because (p_a\neq p_b), the reflected points lie in opposite open half-planes determined by the line (p_ip_k).

Now use strict convexity. The line through two vertices (p_i,p_k) meets the strictly convex polygon only along the chord (p_ip_k), and no other vertex lies on this line. Thus the two open polygonal boundary arcs from (p_i) to (p_k) lie in the two opposite open half-planes determined by the line (p_ip_k). This is the exact step where strict convexity is invoked: it rules out a third vertex on the line (p_ip_k) and makes the half-plane/cyclic-arc correspondence nondegenerate.

Since (p_a) and (p_b) lie in opposite open half-planes, their indices lie on opposite cyclic arcs between (i) and (k). Hence ({i,k}) separates ({a,b}), so the chords (p_ip_k) and (p_ap_b) cross. (\square)

---

## 2. The exact theorem proved

The full contradiction does **not** follow from facts (A) and (B) alone. The strongest sharp matrix consequence obtainable from these two facts is the following.

**Theorem.**
Let (M) be an (n\times n) cyclically indexed (0)-(1) matrix with (M_{ii}=0). Suppose:

1. for every two distinct rows (i,k),

[
|S_i\cap S_k|\le 2;
]

2. if (S_i\cap S_k={a,b}), then ({i,k}) separates ({a,b}) cyclically.

If every row has at least (4) ones, then

[
n\ge 8.
]

This bound is sharp as a theorem about the matrix axioms: for every (n\ge 8), there exists a cyclic (0)-(1) matrix satisfying these axioms with every row sum exactly (4). Therefore facts (A) and (B), even together with the shared cyclic row/column order, cannot by themselves prove that the geometric configuration is impossible.

The unresolved part is geometric: the sharp matrix examples below need not be realizable by strictly convex point sets with actual radii. To eliminate them one would need additional metric input beyond (A) and (B), such as perpendicular-bisector incidences, row-wise semicircle constraints, or length inequalities.

---

## 3. Cyclic-matrix / discharging argument

For a column pair ({a,b}), let

[
\lambda(a,b)=|{i:a,b\in S_i}|
]

be the number of rows containing both columns (a,b).

### Forbidden column-pair capacities

First, facts (A) and (B) imply two useful forbidden submatrices.

**Forbidden configuration 1: noncrossing (2\times 2).**
If rows (i,k) and columns (a,b) satisfy

[
M_{ia}=M_{ib}=M_{ka}=M_{kb}=1,
]

then ({i,k}) must separate ({a,b}). Thus the all-one (2\times 2) pattern is forbidden whenever the row pair and column pair are not cyclically alternating.

In cyclic notation, the pattern

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

is forbidden if, for example, the cyclic order is (i,k,a,b) or (i,a,b,k). It is only allowed when the cyclic order alternates, such as (i,a,k,b).

**Forbidden configuration 2: three rows sharing two columns.**
The pattern

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1\
\ell & 1 & 1
\end{array}
]

is impossible.

Indeed, remove (a,b) from the cyclic order. The remaining vertices lie on two open arcs between (a) and (b). If three row indices (i,k,\ell) all contain both (a,b), then by the pigeonhole principle two of (i,k,\ell) lie on the same arc. Those two rows share the two columns (a,b), but their row pair does not separate ({a,b}), contradicting (B).

Therefore

[
\lambda(a,b)\le 2
]

for every column pair ({a,b}).

There is a stronger bound for adjacent column pairs. If (a,b) are adjacent cyclically, then no two rows can both contain (a,b), because the pair ({a,b}) has an empty open arc between its two vertices and cannot be separated by any row pair. Hence

[
\lambda(a,b)\le 1
]

when (a,b) are adjacent.

### Discharging

Each row (i) sends one unit of charge to every unordered pair of columns contained in (S_i). If (d_i=|S_i|), then row (i) sends

[
\binom{d_i}{2}
]

units of charge. Since (d_i\ge 4), each row sends at least

[
\binom{4}{2}=6
]

units. Hence the total charge is at least

[
\sum_i \binom{d_i}{2}\ge 6n.
]

Now bound how much charge the column pairs can receive.

There are exactly (n) adjacent cyclic column pairs, each of capacity at most (1). There are

[
\binom n2-n
]

nonadjacent column pairs, each of capacity at most (2). Therefore the total capacity is at most

[
n\cdot 1+2\left(\binom n2-n\right)
= n+ n(n-1)-2n
= n(n-2).
]

Thus

[
6n\le n(n-2).
]

Since (n>0), this gives

[
6\le n-2,
]

so

[
n\ge 8.
]

This proves the theorem.

A useful equality observation: if (n=8), equality must hold everywhere. Thus every row has size exactly (4), every adjacent column pair appears in exactly one row, and every nonadjacent column pair appears in exactly two rows. That is the strongest structural conclusion this discharging argument gives at the threshold case.

---

## 4. Configurations that remain unresolved

The following matrices satisfy the cyclic matrix consequences of (A) and (B) with every row sum (4). They show that no contradiction can be derived from those facts alone.

For the examples, index rows and columns by (\mathbb Z/n\mathbb Z).

### Unresolved pattern for (n=8)

Let

[
D_8={1,2,5,7}\subset \mathbb Z/8\mathbb Z
]

and define

[
M_{ij}=1 \iff j-i\in D_8.
]

Equivalently, the rows are

[
\begin{aligned}
S_0&={1,2,5,7},\
S_1&={0,2,3,6},\
S_2&={1,3,4,7},\
S_3&={0,2,4,5},\
S_4&={1,3,5,6},\
S_5&={2,4,6,7},\
S_6&={0,3,5,7},\
S_7&={0,1,4,6}.
\end{aligned}
]

The full (0)-(1) matrix is

[
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

For row difference (t), the common columns of rows (0) and (t) are:

[
\begin{array}{c|c}
t & D_8\cap(D_8+t)\ \hline
1 & {2}\
2 & {1,7}\
3 & {2,5}\
4 & {1,5}\
5 & {2,7}\
6 & {5,7}\
7 & {1}
\end{array}
]

Whenever the intersection has size (2), the two common columns lie on opposite sides of (t) in the cyclic order, so the crossing condition (B) is satisfied. Adjacent rows share only one column.

Thus this matrix satisfies all the derived cyclic forbidden-pattern rules, with every row sum equal to (4).

### Unresolved patterns for every (n\ge 9)

Let

[
D={1,2,4,8}\subset \mathbb Z/n\mathbb Z
]

and define

[
M_{ij}=1 \iff j-i\in D.
]

Then every row and every column has exactly four ones, and (M_{ii}=0).

For (n\ge 15), the nonzero differences among (1,2,4,8) are

[
\pm1,\ \pm2,\ \pm3,\ \pm4,\ \pm6,\ \pm7,
]

which are all distinct modulo (n). Hence two different rows share at most one column. Thus (A) holds and (B) is vacuous.

For (9\le n\le 14), the only row differences producing two common columns are listed below, and in every case the two common columns straddle the row difference (t), so (B) holds.

[
\begin{array}{c|c}
n & \text{two-column intersections } D\cap(D+t)\ \hline
9 &
t=2:{1,4},\
t=3:{2,4},\
t=6:{1,8},\
t=7:{2,8}[2mm]
10 &
t=3:{1,4},\
t=4:{2,8},\
t=6:{4,8},\
t=7:{1,8}[2mm]
11 &
t=4:{1,8},\
t=7:{4,8}[2mm]
12 &
t=6:{2,8}[2mm]
13 &
t=6:{1,8},\
t=7:{2,8}[2mm]
14 &
t=7:{1,8}
\end{array}
]

All other row intersections have size at most (1).

So for every (n\ge 8), there are exact cyclic (0)-(1) patterns satisfying all consequences of (A) and (B) with row sums (4). These are the configurations left unresolved by the matrix/discharging method. They are not asserted to be geometrically realizable; they show precisely where additional geometric input is needed.
