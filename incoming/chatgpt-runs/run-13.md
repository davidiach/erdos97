## 1. Convex-position crossing lemma

Let the vertices be in strictly convex position and let (i\ne k). Suppose

[
a,b\in S_i\cap S_k,\qquad a\ne b.
]

Thus

[
|p_a-p_i|=|p_b-p_i|=r_i,\qquad |p_a-p_k|=|p_b-p_k|=r_k.
]

So (p_a,p_b) are the two common points of the two circles centered at (p_i,p_k).

### Lemma B

If (S_i\cap S_k={a,b}), then the endpoints (i,k,a,b) alternate in the cyclic order. Equivalently, the chord (p_ip_k) crosses the chord (p_ap_b).

### Proof

Let (L) be the line through (p_i,p_k). Reflection in (L) fixes both circle centers (p_i,p_k), hence fixes both circles. Therefore it preserves their intersection set ({p_a,p_b}). Since (p_a\ne p_b), reflection in (L) interchanges them. Thus (p_a,p_b) are mirror images across (L), and the segment (p_ap_b) is perpendicular to (L).

Choose coordinates with

[
p_i=(0,0),\qquad p_k=(d,0),\qquad d>0,
]

and write

[
p_a=(t,h),\qquad p_b=(t,-h),
]

with (h\ne 0). The chord (p_ap_b) crosses the line (L) at ((t,0)). We must show

[
0<t<d.
]

This is the exact place where strict convexity is used.

If (t=0), then (p_i) lies on the segment (p_ap_b), contradicting strict convexity: no vertex of a strictly convex polygon lies on a segment joining two other vertices. Similarly, (t=d) would put (p_k) on the segment (p_ap_b), again impossible.

If (t<0), then (p_i) lies in the interior of the triangle with vertices (p_k,p_a,p_b). Indeed,

[
p_i=\alpha p_k+\beta p_a+\beta p_b
]

with

[
\alpha=\frac{-t}{d-t}>0,\qquad \beta=\frac{d}{2(d-t)}>0,\qquad \alpha+2\beta=1.
]

So (p_i) is a convex combination with all positive coefficients, contradicting that (p_i) is an extreme vertex of the convex polygon.

Likewise, if (t>d), then (p_k) lies in the interior of the triangle with vertices (p_i,p_a,p_b), since

[
p_k=\alpha p_i+\beta p_a+\beta p_b
]

with

[
\beta=\frac{d}{2t}>0,\qquad \alpha=1-\frac dt>0.
]

Again this contradicts strict convexity/convex position.

Therefore (0<t<d). Hence the segment (p_ip_k) crosses the segment (p_ap_b) at ((t,0)). In a strictly convex polygon, two chords cross in their interiors exactly when their endpoints alternate in the cyclic order. Thus the pair ({i,k}) separates the pair ({a,b}). ∎

---

## 2. Exact theorem proved

The full contradiction does **not** follow from facts (A) and (B) alone. The strongest general cyclic-matrix theorem I can prove from them is the following.

Let (M) be a zero-diagonal cyclic (0)-(1) matrix satisfying:

1. for all (i\ne k),

[
|S_i\cap S_k|\le 2;
]

2. if (S_i\cap S_k={a,b}), then ({i,k}) separates ({a,b}) cyclically.

Let

[
m_i=|S_i|
]

be the row sums. Then

[
\boxed{\sum_{i=1}^n \binom{m_i}{2}\le n(n-2).}
]

Consequently, if every row has size at least (4), then

[
6n\le \sum_i \binom{m_i}{2}\le n(n-2),
]

so

[
\boxed{n\ge 8.}
]

More precisely,

[
\boxed{\sum_i (m_i-4)(m_i+3)\le 2n(n-8).}
]

Thus, for (n=8), every row must have size exactly (4), and every capacity in the counting argument below must be saturated.

There is no contradiction for (n\ge 8) from (A) and (B) alone: explicit cyclic matrices satisfying both facts and having all row sums (4) exist.

---

## 3. Cyclic-matrix / discharging argument

Write indices modulo (n). Say that two indices (a,b) are adjacent if they are consecutive in the cyclic order.

### Forbidden submatrices

Facts (A) and (B) imply the following forbidden (0)-(1) patterns.

First, by (A), no two rows can share three columns:

[
\begin{array}{c|ccc}
& a&b&c\ \hline
i&1&1&1\
k&1&1&1
\end{array}
]

is forbidden.

Second, by (B), a (2\times 2) all-one submatrix is allowed only if the row pair crosses the column pair. Thus

[
\begin{array}{c|cc}
& a&b\ \hline
i&1&1\
k&1&1
\end{array}
]

is forbidden whenever ({i,k}) and ({a,b}) do not alternate cyclically.

In particular, adjacent rows cannot share two columns:

[
\begin{array}{c|cc}
& a&b\ \hline
i&1&1\
i+1&1&1
\end{array}
]

is forbidden, because the boundary edge (p_ip_{i+1}) crosses no chord.

Dually, adjacent columns cannot occur together in two rows:

[
\begin{array}{c|cc}
& a&a+1\ \hline
i&1&1\
k&1&1
\end{array}
]

is forbidden, because the boundary edge (p_ap_{a+1}) crosses no chord.

Finally, no three rows can contain the same two columns:

[
\begin{array}{c|cc}
& a&b\ \hline
i&1&1\
k&1&1\
\ell&1&1
\end{array}
]

is forbidden. Indeed, if three rows all contain (a,b), then any two of those row indices must be separated by ({a,b}). But the pair ({a,b}) cuts the remaining vertices into two arcs, and among three row indices two lie on the same arc. Those two are not separated by ({a,b}), contradiction.

### Pair-charge inequality

Charge each row (i) one unit for every unordered pair of columns inside (S_i). The total charge is

[
\sum_i \binom{m_i}{2}.
]

Now fix a column pair ({a,b}). Let

[
d(a,b)=|{i:a,b\in S_i}|.
]

If (a,b) are adjacent, then (d(a,b)\le 1). If they are nonadjacent, then (d(a,b)\le 2), by the forbidden (3\times 2) pattern above.

There are (n) adjacent column pairs and (\binom n2-n) nonadjacent column pairs. Therefore

[
\sum_i \binom{m_i}{2}
=\sum_{{a,b}} d(a,b)
\le n+2\left(\binom n2-n\right)
=n(n-2).
]

This proves the main inequality.

A dual inequality also follows. If (c_j) denotes the column sum of column (j), then

[
\boxed{\sum_j \binom{c_j}{2}\le n(n-2).}
]

Indeed, adjacent row pairs have intersection at most (1), and nonadjacent row pairs have intersection at most (2).

### Consequences for row sums

If (m_i\ge 4) for every (i), then

[
\binom{m_i}{2}\ge 6,
]

so

[
6n\le \sum_i \binom{m_i}{2}\le n(n-2),
]

hence (n\ge 8).

Equivalently,

[
\sum_i\left(\binom{m_i}{2}-6\right)\le n(n-2)-6n=n(n-8),
]

and since

[
\binom{m_i}{2}-6=\frac{(m_i-4)(m_i+3)}2,
]

we get

[
\sum_i (m_i-4)(m_i+3)\le 2n(n-8).
]

Thus for (n=8), every (m_i=4), every adjacent column pair occurs in exactly one row, and every nonadjacent column pair occurs in exactly two rows. By the dual inequality, every column also has sum (4), adjacent row pairs intersect in exactly one column, and nonadjacent row pairs intersect in exactly two columns.

A weaker but sometimes useful bound on the total number of ones (T=\sum_i m_i) is obtained from Jensen/Cauchy:

[
\sum_i \binom{m_i}{2}
=\frac12\left(\sum_i m_i^2-T\right)
\ge \frac12\left(\frac{T^2}{n}-T\right).
]

Together with (\sum_i \binom{m_i}{2}\le n(n-2)), this gives

[
\boxed{T\le \frac n2\left(1+\sqrt{8n-15}\right).}
]

This is only (O(n^{3/2})), not linear.

### A small sharpening for row sums at least (5)

The same counting gives

[
10n\le n(n-2),
]

so (n\ge 12). In fact (n=12) is impossible as a cyclic matrix satisfying (A) and (B).

If (n=12) and all row sums were at least (5), equality would hold everywhere. Thus every row and every column would have sum (5), adjacent row pairs would intersect in (1) column, and nonadjacent row pairs would intersect in (2) columns.

Then the Gram matrix (G=MM^T) would satisfy

[
G=2J+3I-A,
]

where (J) is the all-one matrix and (A) is the adjacency matrix of the (12)-cycle. The eigenvalues of (A) are (2\cos(2\pi k/12)). Hence the eigenvalues of (G) are

[
25
]

on the all-one vector, and

[
3-2\cos(2\pi k/12),\qquad k=1,\dots,11,
]

on the orthogonal complement. Therefore

[
\det G
=25\prod_{k=1}^{11}\left(3-2\cos\frac{2\pi k}{12}\right)
=2^8,3^4,5^3.
]

This is not a perfect square. But (G=MM^T) with (M) an integer square matrix, so

[
\det G=(\det M)^2
]

must be a perfect square integer. Contradiction. Thus all row sums at least (5) force

[
\boxed{n\ge 13}
]

as a purely cyclic-matrix consequence.

---

## 4. Why the full contradiction does not follow from (A) and (B)

The following cyclic (8\times 8) matrix satisfies all consequences of (A) and (B), with every row sum exactly (4). Define

[
M_{ij}=1
\quad\Longleftrightarrow\quad
j-i\pmod 8\in{1,2,5,7}.
]

Equivalently,

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

Because the matrix is circulant, it suffices to compare row (0) with row (h). With (D={1,2,5,7}),

[
S_0\cap S_h=D\cap(h+D).
]

The intersections are

[
\begin{array}{c|c}
h & S_0\cap S_h\ \hline
1&{2}\
2&{1,7}\
3&{2,5}\
4&{1,5}\
5&{2,7}\
6&{5,7}\
7&{1}.
\end{array}
]

For (h=2,3,4,5,6), the two common columns lie on opposite sides of the chord ({0,h}), so condition (B) is satisfied. For (h=1,7), the adjacent rows share only one column. Thus this matrix satisfies (A) and (B), and all row sums are (4).

Its mirror image also works:

[
M_{ij}=1
\quad\Longleftrightarrow\quad
j-i\pmod 8\in{1,3,6,7}.
]

So facts (A) and (B) alone cannot prove the desired contradiction.

There are even larger examples. For row sum (5), define a (13\times 13) circulant matrix by

[
M_{ij}=1
\quad\Longleftrightarrow\quad
j-i\pmod {13}\in{1,2,5,10,12}.
]

The only row differences (h) producing two common columns are

[
\begin{array}{c|c}
h & S_0\cap S_h\ \hline
2&{1,12}\
3&{2,5}\
4&{1,5}\
5&{2,10}\
8&{5,10}\
9&{1,10}\
10&{2,12}\
11&{10,12}.
\end{array}
]

Each listed pair separates ({0,h}), so (B) holds. Thus the (n\ge 13) threshold for row sums at least (5) is sharp as a cyclic-matrix statement.

More strongly, for any (r), choose (n>2^r) and define

[
D_r={1,2,4,\dots,2^{r-1}}\subset \mathbb Z/n\mathbb Z,
]

then set

[
M_{ij}=1
\quad\Longleftrightarrow\quad
j-i\pmod n\in D_r.
]

Every row has sum (r). Moreover, two distinct rows share at most one column. Indeed, a two-column intersection would give two representations of the same nonzero cyclic difference as

[
2^a-2^b\pmod n.
]

Because (n>2^r), this congruence is an equality over the integers, and powers of two have unique nonzero differences: if

[
2^a-2^b=2^c-2^d,
]

then comparing signs and (2)-adic valuations gives (a=c) and (b=d). Hence no row pair has intersection (2), so (B) is vacuous. These matrices satisfy (A) and (B) with arbitrarily large row sums.

Thus the full geometric contradiction, if true, needs additional geometric input beyond (A) and (B).

### Extra geometric input for the (8\times 8) obstruction

The displayed (8\times 8) circulant patterns themselves are not geometrically realizable. For the first one,

[
S_i={i+1,i+2,i+5,i+7}
={i+1,i+2,i-3,i-1}.
]

Since (i-1,i+1\in S_i),

[
|p_i-p_{i-1}|=|p_i-p_{i+1}|.
]

Thus all side lengths of the polygon are equal. Also (i+1,i+2\in S_i), so

[
|p_i-p_{i+1}|=|p_i-p_{i+2}|.
]

But the side (p_{i+1}p_{i+2}) has the same common side length, so every triangle

[
p_i p_{i+1} p_{i+2}
]

is equilateral. Hence every interior angle of the octagon would be (60^\circ), impossible because the interior angle sum of a convex octagon is (6\pi=1080^\circ). The mirror pattern is ruled out similarly.

This argument uses the full metric meaning of the rows, not merely (A) and (B).

---

## 5. Remaining unresolved configurations

The matrix/discharging method leaves the following exact (0)-(1) patterns unresolved as cyclic matrices. They are not asserted to be realizable by convex polygons; they are obstructions to any proof using only (A) and (B).

The cleanest row-sum-(4) unresolved family is

[
M_{ij}=1
\quad\Longleftrightarrow\quad
j-i\pmod n\in{1,2,4,8},
\qquad n>16.
]

Every row has size (4), every two rows share at most one column, and therefore (B) is vacuous.

More generally,

[
M_{ij}=1
\quad\Longleftrightarrow\quad
j-i\pmod n\in{1,2,4,\dots,2^{r-1}},
\qquad n>2^r,
]

gives row sum (r) and satisfies (A) and (B). These Sidon-type circulant patterns show that the crossing lemma and the pair-intersection bound alone cannot yield the desired nonexistence theorem.
