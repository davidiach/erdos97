I will use indices cyclically, modulo (n). For a row (i), write
[
R_i=S_i={j:M_{ij}=1},\qquad m_i=|R_i|.
]

The full contradiction **does not follow from (A) and (B) alone**. In fact, there are exact cyclic (0)-(1) matrices with zero diagonal and all row sums at least (4) satisfying every consequence of (A) and (B). What can be proved from (A) and (B) is a sharp cyclic discharging theorem: if all rows have size at least (4), then necessarily (n\ge 8), and the (n=8) case is completely tight at the cyclic-matrix level.

---

## 1. Convex-position crossing lemma

**Lemma (B).** Suppose (S_i\cap S_k={a,b}) with (i\ne k). Then the two pairs ({i,k}) and ({a,b}) separate each other in the cyclic order. Equivalently, the chord (p_ip_k) crosses the chord (p_ap_b).

**Proof.** Since (a,b\in S_i\cap S_k), we have
[
|p_a-p_i|=|p_b-p_i|,\qquad |p_a-p_k|=|p_b-p_k|.
]
Thus both (p_i) and (p_k) lie on the perpendicular bisector of the segment (p_ap_b). Since (p_i\ne p_k), the line (p_ip_k) is exactly that perpendicular bisector. Equivalently, (p_a) and (p_b) are reflections of one another across the line (p_ip_k). This is the radical-axis/common-chord property for the two circles centered at (p_i) and (p_k).

Choose coordinates so that
[
p_i=(0,0),\qquad p_k=(d,0),\qquad d>0,
]
and the line (p_ip_k) is the (x)-axis. Since (p_a,p_b) are symmetric across this line, write
[
p_a=(u,v),\qquad p_b=(u,-v),
]
with (v>0). Thus (p_a,p_b) lie on opposite sides of the line (p_ip_k).

Now we prove that (0<u<d). This is where **strict convexity is used**.

If (u<0), then (p_i=(0,0)) lies strictly inside the triangle with vertices (p_k,p_a,p_b). Indeed, the vertical cross-section of that triangle at (x=0) contains a nontrivial interval around (y=0). That contradicts strict convexity, because a vertex of a strictly convex polygon cannot lie inside the triangle spanned by three other vertices.

If (u=0), then (p_i) lies on the segment (p_ap_b), again impossible in a strictly convex polygon.

Similarly, if (u>d), then (p_k) lies strictly inside the triangle (p_i p_a p_b), and if (u=d), then (p_k) lies on (p_ap_b). Both are impossible by strict convexity.

Therefore (0<u<d). Hence the segment (p_ip_k) meets the segment (p_ap_b) at the point ((u,0)), which lies in the relative interior of both segments. Thus the two chords cross.

For four vertices of a strictly convex polygon, two chords cross in their interiors exactly when their endpoints alternate in the cyclic order. Therefore ({i,k}) separates ({a,b}). ∎

The exact strict-convexity step is the exclusion of (u\le 0) and (u\ge d), because otherwise one of (p_i,p_k) lies on or inside the triangle formed by the other three relevant vertices.

---

## 2. The exact theorem proved from (A) and (B)

Let (M) be any cyclic (0)-(1) matrix with zero diagonal satisfying:

[
\tag{A} |R_i\cap R_k|\le 2\quad\text{for }i\ne k,
]
and

[
\tag{B} |R_i\cap R_k|=2,\ R_i\cap R_k={a,b}
\implies {i,k}\text{ separates }{a,b}.
]

Then:

**Theorem.**

1. For every unordered pair of columns ({a,b}), let
   [
   \lambda_{ab}:=#{i:a,b\in R_i}.
   ]
   If (a,b) are adjacent in the cyclic order, then
   [
   \lambda_{ab}\le 1.
   ]
   If (a,b) are nonadjacent, then
   [
   \lambda_{ab}\le 2.
   ]

2. Consequently,
   [
   \sum_i \binom{m_i}{2}\le n(n-2).
   ]

3. Hence if every row has size at least (4), then
   [
   n\ge 8.
   ]

4. If (n=8) and every row has size at least (4), then equality holds everywhere:
   [
   m_i=4\quad\text{for every }i,
   ]
   every adjacent column-pair appears together in exactly one row, and every nonadjacent column-pair appears together in exactly two rows. Moreover every column also has degree (4), adjacent row-pairs intersect in exactly one column, and nonadjacent row-pairs intersect in exactly two columns.

5. This is the strongest contradiction obtainable from (A) and (B) alone: there exist exact cyclic matrices with zero diagonal and all row sums at least (4) satisfying (A) and (B). Therefore the desired full geometric contradiction requires additional metric input beyond (A) and (B).

---

## 3. Cyclic-matrix and discharging argument

### 3.1 Forbidden cyclic submatrices

The first forbidden pattern is just (A):

[
\begin{array}{c|ccc}
& a&b&c\ \hline
i&1&1&1\
k&1&1&1
\end{array}
\qquad\text{is forbidden.}
]

Two distinct rows cannot share three columns.

The second forbidden pattern is the cyclic one coming from (B):

[
\begin{array}{c|cc}
& a&b\ \hline
i&1&1\
k&1&1
\end{array}
]

is forbidden unless the pair ({i,k}) separates the pair ({a,b}). In particular, adjacent rows cannot share two columns, because an adjacent pair of vertices separates no other pair.

Now dualize this observation. Fix two columns (a,b). Suppose two rows (i,k) both contain (a,b). Then (R_i\cap R_k) contains ({a,b}). By (A), it contains exactly ({a,b}). Therefore (B) applies, so ({i,k}) separates ({a,b}).

This gives two useful dual forbidden patterns.

First, no three rows can contain the same two columns:

[
\begin{array}{c|cc}
& a&b\ \hline
i&1&1\
k&1&1\
\ell&1&1
\end{array}
\qquad\text{is forbidden.}
]

Indeed, if three row indices all had to pairwise separate (a,b), two of them would lie on the same side of the cut determined by (a,b), contradiction.

Second, if (a,b) are adjacent columns, then even two rows cannot contain both (a) and (b):

[
\begin{array}{c|cc}
& a&a+1\ \hline
i&1&1\
k&1&1
\end{array}
\qquad\text{is forbidden.}
]

An adjacent column-pair has an empty open arc on one side, so no two row indices can separate it.

More generally, for nonadjacent (a,b), two rows (i,k) may both contain (a,b) only if (i) and (k) lie on opposite arcs between (a) and (b).

---

### 3.2 Discharging on column-pairs

Give one unit of charge to each unordered pair of (1)’s in each row. Thus row (i) sends

[
\binom{m_i}{2}
]

units of charge to column-pairs, and the total charge is

[
\sum_i \binom{m_i}{2}.
]

Now bound how much charge a fixed column-pair can receive.

There are (n) adjacent column-pairs in the cycle. Each adjacent column-pair can appear together in at most one row, so each has capacity (1).

There are

[
\binom n2-n
]

nonadjacent column-pairs. Each nonadjacent column-pair can appear together in at most two rows, so each has capacity (2).

Therefore

[
\sum_i \binom{m_i}{2}
\le n\cdot 1+2\left(\binom n2-n\right)
= n+n(n-1)-2n
= n(n-2).
]

So

[
\boxed{\sum_i \binom{m_i}{2}\le n(n-2).}
]

If every (m_i\ge 4), then (\binom{m_i}{2}\ge 6), hence

[
6n\le \sum_i \binom{m_i}{2}\le n(n-2).
]

Thus

[
6\le n-2,
]

so

[
\boxed{n\ge 8.}
]

This proves that no such cyclic matrix exists for (n\le 7).

---

### 3.3 The tight (n=8) structure

If (n=8) and all rows have size at least (4), then

[
6n=48\le \sum_i\binom{m_i}{2}\le n(n-2)=48.
]

So equality holds. Hence every row has size exactly (4), every adjacent column-pair is used exactly once, and every nonadjacent column-pair is used exactly twice.

Let (d_a) be the degree of column (a). Fix a column (a). It has two adjacent partners and five nonadjacent partners. Therefore

[
\sum_{b\ne a}\lambda_{ab}=2\cdot 1+5\cdot 2=12.
]

But every row containing (a) has three other (1)’s, so

[
\sum_{b\ne a}\lambda_{ab}=3d_a.
]

Thus (3d_a=12), so

[
d_a=4.
]

Therefore every column also has degree (4). Applying the row-pair version of the same capacity count, adjacent row-pairs must intersect in exactly one column, and nonadjacent row-pairs must intersect in exactly two columns.

---

### 3.4 A sharp (8\times 8) cyclic-matrix survivor

The (n=8) lower bound is sharp at the matrix level. Index rows and columns by (\mathbb Z/8\mathbb Z), and set

[
R_i={i-3,\ i-1,\ i+1,\ i+2}\pmod 8.
]

Explicitly:

[
\begin{array}{c|cccccccc}
&0&1&2&3&4&5&6&7\ \hline
0&0&1&1&0&0&1&0&1\
1&1&0&1&1&0&0&1&0\
2&0&1&0&1&1&0&0&1\
3&1&0&1&0&1&1&0&0\
4&0&1&0&1&0&1&1&0\
5&0&0&1&0&1&0&1&1\
6&1&0&0&1&0&1&0&1\
7&1&1&0&0&1&0&1&0
\end{array}
]

Every row has size (4). By rotation, it is enough to compare row (0) with row (t). The intersections are:

[
\begin{array}{c|c}
t & R_0\cap R_t\ \hline
1&{2}\
2&{1,7}\
3&{2,5}\
4&{1,5}\
5&{2,7}\
6&{5,7}\
7&{1}
\end{array}
]

Every two-element intersection has one element on each side of the row-pair ({0,t}). Thus (A) and (B) both hold.

So the cyclic discharging theorem cannot be improved to a contradiction using only (A) and (B).

This particular (8\times 8) survivor is **not** geometrically realizable, but ruling it out uses extra metric information. Indeed, in this pattern row (i) contains (i+1) and (i+2), while row (i+1) contains (i) and (i+2). Therefore

[
|p_i-p_{i+1}|=|p_i-p_{i+2}|,
]
and

[
|p_{i+1}-p_i|=|p_{i+1}-p_{i+2}|.
]

Thus every triangle

[
p_i p_{i+1} p_{i+2}
]

is equilateral. Hence every interior angle of the polygon is (60^\circ), impossible for a strictly convex (n)-gon with (n\ge 4). This argument uses the actual distance equalities inside individual rows, not merely (A) and (B).

---

### 3.5 A total-incidence bound

There is also a row-pair version of the same discharging argument. Let

[
d_j=#{i:j\in R_i}
]

be the column degree of column (j), and let

[
T=\sum_i m_i=\sum_j d_j
]

be the total number of (1)’s.

Adjacent row-pairs can share at most one column, and nonadjacent row-pairs can share at most two columns. Hence

[
\sum_j \binom{d_j}{2}\le n(n-2).
]

By convexity,

[
\sum_j \binom{d_j}{2}
=\frac12\left(\sum_j d_j^2-T\right)
\ge \frac12\left(\frac{T^2}{n}-T\right).
]

Therefore

[
\frac12\left(\frac{T^2}{n}-T\right)\le n(n-2),
]

so

[
T^2-nT-2n^2(n-2)\le 0.
]

Thus

[
\boxed{
T\le \frac n2\left(1+\sqrt{8n-15}\right).
}
]

This is only (O(n^{3/2})), not linear. The next family shows that this order of magnitude cannot be beaten using only (A) and (B).

---

## 4. Remaining unresolved configurations

The main unresolved obstruction is that (A) and (B) say essentially nothing when no two rows share two columns. Here is an exact infinite family of such cyclic matrices.

Let (\mathbb F_q) be a finite field with (q\ge 4). Index both rows and columns by the same set (\mathbb F_q^2), in any fixed cyclic order. For a row indexed by ((m,b)\in\mathbb F_q^2), define

[
R_{(m,b)}
=========

{(x,y)\in\mathbb F_q^2:\ y=mx+b+1-m^2}.
]

Equivalently,

[
M_{(m,b),(x,y)}=1
\quad\Longleftrightarrow\quad
y=mx+b+1-m^2.
]

Then:

[
|R_{(m,b)}|=q.
]

The diagonal is zero, because substituting ((x,y)=(m,b)) gives

[
b=m^2+b+1-m^2=b+1,
]

which is impossible.

Two rows with the same slope (m) are parallel distinct affine lines, so they are disjoint. Two rows with different slopes meet in exactly one point. Hence

[
|R_i\cap R_k|\le 1
]

for every (i\ne k). Thus (A) holds, and (B) is vacuous.

For (q=4), this gives an exact (16\times 16) cyclic (0)-(1) matrix with every row sum exactly (4), zero diagonal, and no double row intersections. For (q=5), it gives a completely concrete (25\times 25) matrix over (\mathbb F_5) with every row sum (5).

This family is not claimed to come from a convex polygon. It shows that the crossing lemma and the discharging argument cannot, by themselves, prove the desired geometric contradiction. Any full nonexistence proof must use additional Euclidean information about equal-distance sets in individual rows, beyond the pairwise circle-intersection facts (A) and (B).
