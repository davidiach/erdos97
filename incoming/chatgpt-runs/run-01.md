## 1. Convex-position crossing lemma

Call two unordered pairs ({x,y}) and ({u,v}) **separated** in the cyclic order if, after deleting (x,y), the two indices (u,v) lie in different open cyclic arcs. Equivalently, up to reversing the cyclic order, the four indices occur as

[
x,\ u,\ y,\ v .
]

Geometrically, for vertices of a strictly convex polygon, this is equivalent to saying that the chords (p_xp_y) and (p_up_v) cross.

### Lemma B

Suppose (i\ne k) and (S_i\cap S_k) contains two distinct indices (a,b). Then ({i,k}) separates ({a,b}). Equivalently, the chord (p_ip_k) crosses the chord (p_ap_b).

### Proof

Let

[
C_i={x: |x-p_i|=r_i},\qquad C_k={x: |x-p_k|=r_k}.
]

Because (a,b\in S_i\cap S_k), the two points (p_a,p_b) lie on both circles (C_i,C_k). Thus the line (p_ap_b) is the common chord, i.e. the radical axis, of the two circles.

The radical axis of two nonconcentric circles is perpendicular to the line of centers. Hence the line (p_ip_k) is perpendicular to the common chord (p_ap_b). Moreover, since (p_i) lies on the perpendicular from the center of (C_i) to the chord (p_ap_b), the intersection point

[
h=p_ip_k\cap p_ap_b
]

is the midpoint of (p_ap_b). Therefore reflection across the line (p_ip_k) swaps (p_a) and (p_b). In particular, since (a\ne b), neither (p_a) nor (p_b) lies on the line (p_ip_k), and the two points (p_a,p_b) lie in opposite open half-planes bounded by (p_ip_k).

Now use convexity. The chord (p_ip_k) splits the boundary cycle of the polygon into two open chains from (p_i) to (p_k). In a convex polygon, each of these two chains lies in one of the two closed half-planes bounded by the line (p_ip_k). The two chains lie on opposite sides unless one chain is empty, i.e. unless (i,k) are adjacent.

Here is the exact use of strict convexity: strict convexity rules out any third vertex lying on the line (p_ip_k). Therefore the vertices on the two open chains lie in the two **open** half-planes bounded by (p_ip_k).

Since (p_a) and (p_b) are on opposite sides of (p_ip_k), they must lie on opposite boundary chains between (i) and (k). Hence ({i,k}) separates ({a,b}) in cyclic order. Equivalently, the chords (p_ip_k) and (p_ap_b) cross. (\square)

---

## 2. Exact theorem proved

The full contradiction “no such matrix exists with every row sum at least (4)” **does not follow from facts (A) and (B) alone**.

The sharp cyclic-matrix theorem obtainable from (A) and (B) is this:

### Theorem

Let (M) be a cyclically indexed (0)-(1) matrix with (M_{ii}=0), satisfying:

1. for distinct rows (i,k),

[
|S_i\cap S_k|\le 2;
]

2. if (|S_i\cap S_k|=2), say (S_i\cap S_k={a,b}), then ({i,k}) separates ({a,b}).

Then:

* all noncrossing (2\times 2) all-one submatrices are forbidden;
* all (2\times 3) and (3\times 2) all-one submatrices are forbidden;
* the pair-counting / discharging bound

[
\sum_i \binom{|S_i|}{2}\le n(n-2)
]

holds;

* therefore no such matrix with all row sums at least (4) exists for (n\le 7);
* but for every (n\ge 8), there exists a cyclic matrix satisfying all of these rules with every row sum exactly (4).

Thus any proof of the original geometric contradiction, if true, must use additional geometry beyond (A) and (B). In particular, it must rule out linear (4)-uniform incidence patterns in which no two rows share two columns; facts (A) and (B) are silent in that case.

---

## 3. Cyclic-matrix and discharging argument

Write (d_i=|S_i|).

### Forbidden (2\times 2) pattern

Suppose rows (i,k) and columns (a,b) form an all-one (2\times 2):

[
M_{ia}=M_{ib}=M_{ka}=M_{kb}=1.
]

Then (a,b\in S_i\cap S_k). By (A), the intersection is exactly ({a,b}). By (B), the pairs ({i,k}) and ({a,b}) must be separated in cyclic order.

Therefore the following pattern is forbidden whenever the four labels are not alternating:

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

with cyclic order, for example,

[
i,\ k,\ a,\ b.
]

The only allowed all-one (2\times 2) pattern is the crossing one, with cyclic order

[
i,\ a,\ k,\ b
]

or its reverse.

A useful interval version is:

> If (R) and (C) are disjoint cyclic intervals, then the submatrix (M[R,C]) contains no all-one (2\times 2).

Indeed, two rows in the same interval and two columns in a disjoint interval cannot alternate.

### Forbidden (2\times 3)

Two rows cannot share three columns, because that would violate (A). Hence no submatrix of the form

[
\begin{array}{c|ccc}
& a & b & c\ \hline
i & 1 & 1 & 1\
k & 1 & 1 & 1
\end{array}
]

is possible.

### Forbidden (3\times 2)

Fix two columns (a,b). Let

[
R_{ab}={i: M_{ia}=M_{ib}=1}.
]

If (i,k\in R_{ab}), then (S_i\cap S_k) contains ({a,b}), so by (A) it equals ({a,b}), and by (B) the pair ({i,k}) separates ({a,b}).

But the cyclic order cut by (a,b) has only two open arcs. At most one row of (R_{ab}) can lie in each arc, because two rows in the same arc would not separate (a,b). Therefore

[
|R_{ab}|\le 2.
]

So no (3\times 2) all-one submatrix is possible:

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1\
\ell & 1 & 1
\end{array}
]

is forbidden.

Moreover, if (a,b) are adjacent in the cyclic order, then one of the two arcs between them is empty. Hence in that case

[
|R_{ab}|\le 1.
]

### Pair-discharge bound

For each row (i), give one unit of charge to each unordered pair of (1)’s in that row. Thus row (i) emits

[
\binom{d_i}{2}
]

units of charge. Discharge each unit to the corresponding unordered column-pair ({a,b}).

For a nonadjacent column-pair ({a,b}), the pair can receive charge from at most two rows. For an adjacent column-pair, it can receive charge from at most one row. There are (n) adjacent unordered column-pairs and (\binom n2-n) nonadjacent unordered column-pairs. Therefore

[
\sum_i \binom{d_i}{2}
\le
1\cdot n+2\left(\binom n2-n\right)
==================================

n(n-2).
]

If every row has size at least (4), then

[
\sum_i \binom{d_i}{2}
\ge
n\binom 42
==========

6n.
]

Thus

[
6n\le n(n-2),
]

so necessarily

[
n\ge 8.
]

This proves that the matrix rules already forbid the desired configuration for (n\le 7). But the next construction shows that the same rules allow row sum (4) for every (n\ge 8).

---

## 4. Explicit cyclic matrices with all row sums (4)

Indices are taken modulo (n), in cyclic order

[
0,1,\dots,n-1.
]

For (n\ge 9), define

[
D={1,2,4,8}\subset \mathbb Z_n,
]

and set

[
M_{ij}=1
\quad\Longleftrightarrow\quad
j-i\in D.
]

Every row has exactly four (1)’s. Since the construction is circulant, every column also has exactly four (1)’s.

It remains to check (A) and (B).

For two rows (0) and (h), the common columns are

[
D\cap (h+D).
]

For (n\ge 15), the nonzero ordered differences of (D={1,2,4,8}) are

[
\pm1,\ \pm2,\ \pm3,\ \pm4,\ \pm6,\ \pm7,
]

which are all distinct modulo (n). Hence two different rows share at most one column. Thus (A) holds, and (B) is vacuous.

For (9\le n\le 14), the only cases where two rows share two columns are listed below. In every case, the two common columns lie on opposite sides of the row-pair ({0,h}), so the crossing condition (B) holds.

[
\begin{array}{c|c}
n & \text{pairs } h:\ D\cap(h+D) \ \hline
9 & 2:{1,4},\ 3:{2,4},\ 6:{1,8},\ 7:{2,8}\
10 & 3:{1,4},\ 4:{2,8},\ 6:{4,8},\ 7:{1,8}\
11 & 4:{1,8},\ 7:{4,8}\
12 & 6:{2,8}\
13 & 6:{1,8},\ 7:{2,8}\
14 & 7:{1,8}
\end{array}
]

For example, when (n=10) and (h=4), the two common columns are (2) and (8), and in cyclic order we have

[
0,\ 2,\ 4,\ 8,
]

so ({0,4}) separates ({2,8}).

For (n=8), with (D={1,2,5,7}), the double intersections are

[
\begin{array}{c|c}
h & D\cap(h+D) \ \hline
2 & {1,7}\
3 & {2,5}\
4 & {1,5}\
5 & {2,7}\
6 & {5,7}
\end{array}
]

and again the two common columns lie on opposite sides of ({0,h}). Therefore (A) and (B) hold.

By rotation, the same verification applies to every pair of rows. Hence for every (n\ge 8), there is a cyclic matrix satisfying all consequences of (A) and (B) with all row sums equal to (4).

So the proposed contradiction cannot be proved from (A) and (B) alone.

---

## 5. Structural theorem for rows of size (4)

Suppose (d_i=4). Then row (i) contains six unordered column-pairs. For each pair ({a,b}\subset S_i), there is at most one other row (k) also containing both (a,b). If such a row (k) exists, then (k) must lie on the opposite side of the chord (p_ap_b) from (i).

Equivalently, define the double-intersection graph (H) on row indices by

[
ik\in E(H)
\quad\Longleftrightarrow\quad
|S_i\cap S_k|=2.
]

Then for a row of size (4),

[
\deg_H(i)\le \binom 42=6.
]

If (H) is empty, the matrix is linear: every two rows meet in at most one column. In that case fact (B) never fires. The circulant examples above are exactly of this type for (n\ge 15).

Thus any geometric proof of impossibility must somehow rule out the case

[
|S_i|=4\quad\text{for all }i,
\qquad
|S_i\cap S_k|\le 1\quad\text{for all }i\ne k.
]

Facts (A) and (B) do not address this case.

---

## 6. Configurations remaining unresolved by (A) and (B)

The following exact patterns are not eliminated by the crossing lemma and the circle-intersection bound.

### Unresolved pattern 1: crossing (2\times 2)

With cyclic order

[
r_1,\ c_1,\ r_2,\ c_2,
]

the all-one submatrix

[
\begin{array}{c|cc}
& c_1 & c_2\ \hline
r_1 & 1 & 1\
r_2 & 1 & 1
\end{array}
]

is allowed by (A) and (B). It is the only possible (2\times 2) all-one pattern.

### Unresolved pattern 2: a three-row triangle of double intersections

Take cyclic order

[
r_1,\ \alpha,\ \beta,\ r_2,\ \gamma,\ \delta,\ r_3,\ \varepsilon,\ \zeta.
]

Consider the submatrix

[
\begin{array}{c|cccccc}
& \alpha & \beta & \gamma & \delta & \varepsilon & \zeta \ \hline
r_1 & 1 & 0 & 0 & 1 & 1 & 1\
r_2 & 1 & 1 & 1 & 0 & 0 & 1\
r_3 & 0 & 1 & 1 & 1 & 1 & 0
\end{array}
]

Then

[
S_{r_1}\cap S_{r_2}={\alpha,\zeta},
]
[
S_{r_2}\cap S_{r_3}={\beta,\gamma},
]
[
S_{r_1}\cap S_{r_3}={\delta,\varepsilon}.
]

Each common pair is separated by its corresponding row-pair, so this pattern is allowed by (A) and (B).

### Unresolved pattern 3: linear (4)-uniform circulant matrices

For (n\ge 15), the pattern

[
S_i={i+1,\ i+2,\ i+4,\ i+8}\pmod n
]

has every row sum equal to (4) and satisfies

[
|S_i\cap S_k|\le 1
\qquad\text{for all }i\ne k.
]

Thus it avoids every forbidden (2\times 2), (2\times 3), and (3\times 2) pattern. Since no two rows share two columns, the crossing lemma is never invoked.

This is the main obstruction to a proof using only (A) and (B). To prove the original geometric impossibility, one needs an additional geometric input that rules out such linear favorite-distance incidence patterns.
