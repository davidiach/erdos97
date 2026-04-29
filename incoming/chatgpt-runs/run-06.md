## 1. Convex-position crossing lemma

Let (P={p_1,\dots,p_n}) be in strictly convex position, and suppose two distinct rows (i\neq k) share two indices (a,b). Thus

[
a,b\in S_i\cap S_k,
]

so

[
|p_a-p_i|=|p_b-p_i|=r_i,\qquad |p_a-p_k|=|p_b-p_k|=r_k.
]

Let (L) be the line through (p_i,p_k).

Because (p_i) is equidistant from (p_a,p_b), it lies on the perpendicular bisector of the segment (p_ap_b). Likewise (p_k) lies on the same perpendicular bisector. Since (p_i\neq p_k), the line (L=p_ip_k) is exactly the perpendicular bisector of (p_ap_b). Equivalently, (p_ap_b) is the radical axis / common chord of the two circles centered at (p_i,p_k), and the line of centers (p_ip_k) is perpendicular to and bisects that common chord.

Therefore (p_a) and (p_b) are reflections of one another across (L). In particular, they lie in opposite open half-planes bounded by (L), and the segment (p_ap_b) meets (L) at its midpoint.

Now let (K=\operatorname{conv}(P)). Since the polygon is strictly convex, every (p_v) is an extreme point of (K), and no third vertex lies on the line through two vertices.

**This is the first explicit use of strict convexity:** for the line (L=p_ip_k), the only vertices of (P) on (L) are (p_i,p_k), and (K\cap L=[p_i,p_k]). If (K\cap L) extended past (p_i) or (p_k), then that endpoint vertex would not be extreme.

The two boundary chains of the convex polygon from (p_i) to (p_k) lie in the two closed half-planes determined by (L). Because of strict convexity, all internal vertices of those two chains lie in the corresponding open half-planes.

**This is the second explicit use of strict convexity:** it rules out a vertex of either chain lying on (L), so “same side” and “opposite side” are nondegenerate.

Since (p_a,p_b) lie on opposite sides of (L), they lie on opposite boundary chains from (p_i) to (p_k). Hence the cyclic order alternates:

[
i,\ a,\ k,\ b
]

or

[
i,\ b,\ k,\ a,
]

up to cyclic reversal. Equivalently, the pair ({i,k}) separates the pair ({a,b}).

Moreover, the midpoint of (p_ap_b) lies on (L) and inside (K), hence inside ([p_i,p_k]). It cannot equal (p_i) or (p_k), because then an extreme vertex would lie in the interior of the segment (p_ap_b). Thus the two chords (p_ip_k) and (p_ap_b) cross in their relative interiors.

That proves Fact (B). (\square)

---

## 2. Exact theorem proved here

The full geometric contradiction does **not** follow from Facts (A) and (B) alone. The strongest clean theorem obtainable from those two facts is the following cyclic-matrix theorem.

Write (d_i=|S_i|).

### Theorem

Let (M) be a cyclically indexed (0)-(1) matrix with zero diagonal, satisfying:

1. for every two rows (i\neq k),

[
|S_i\cap S_k|\le 2;
]

2. if (|S_i\cap S_k|=2), say (S_i\cap S_k={a,b}), then the pairs ({i,k}) and ({a,b}) alternate in the cyclic order.

Then

[
\sum_{i=1}^n \binom{d_i}{2}\le n(n-2).
]

Consequently,

[
\sum_{i=1}^n d_i
\le
\frac n2\left(1+\sqrt{8n-15}\right).
]

In particular, if every row has size at least (4), then necessarily

[
n\ge 8.
]

This bound is sharp in the purely cyclic-matrix setting: for every (n\ge 8), there exists an abstract cyclic (0)-(1) matrix satisfying (A) and (B) with every row sum exactly (4). Therefore an impossibility proof for the original geometric problem must use additional metric information beyond (A) and (B).

---

## 3. Cyclic-matrix / discharging argument

### Forbidden (2\times 2) submatrices

Let two rows be (i,k), and suppose they share two columns (a,b). Then the submatrix

[
\begin{array}{c|cc}
& a & b\
\hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

is allowed only if the cyclic order alternates:

[
i,\ a,\ k,\ b
]

or

[
i,\ b,\ k,\ a.
]

Thus a nonalternating all-one (2\times 2) submatrix is forbidden. Equivalently, if (a,b) lie in the same open cyclic interval between (i) and (k), then the above (2\times2) all-one pattern is impossible.

Fact (A) also forbids every all-one (2\times 3) submatrix:

[
\begin{array}{c|ccc}
& a & b & c\
\hline
i & 1 & 1 & 1\
k & 1 & 1 & 1
\end{array}
]

because two rows cannot share three columns.

A useful dual consequence is that every all-one (3\times2) submatrix is also forbidden. Indeed, fix two columns (a,b). Any two rows containing both (a,b) must lie on opposite sides of the pair ({a,b}) in the cyclic order. There are only two sides, so at most two rows can contain both (a,b). Hence

[
\begin{array}{c|cc}
& a & b\
\hline
i & 1 & 1\
k & 1 & 1\
\ell & 1 & 1
\end{array}
]

is impossible.

Also, if (a,b) are adjacent cyclically, then no two rows can contain both (a,b), because the pair ({a,b}) has one empty side and cannot be separated by any row pair. Therefore every adjacent column-pair occurs in at most one row.

### Discharging count

For each row (i), place one token on every unordered pair of (1)’s in that row. Row (i) receives

[
\binom{d_i}{2}
]

tokens. Thus the total number of tokens is

[
T=\sum_i \binom{d_i}{2}.
]

Now move each token to its corresponding unordered pair of columns ({a,b}). Let

[
\lambda_{ab}=#{i:\ a,b\in S_i}
]

be the number of rows containing both columns (a,b). Then

[
T=\sum_{{a,b}}\lambda_{ab}.
]

From the forbidden (3\times2) pattern,

[
\lambda_{ab}\le 2
]

for every column-pair ({a,b}). If (a,b) are adjacent cyclically, then in fact

[
\lambda_{ab}\le 1.
]

There are (n) adjacent column-pairs and

[
\binom n2-n
]

nonadjacent column-pairs. Therefore

[
T
\le
n\cdot 1+2\left(\binom n2-n\right)
==================================

# n+n(n-1)-2n

n(n-2).
]

So

[
\boxed{\sum_i \binom{d_i}{2}\le n(n-2).}
]

If every row has size at least (4), then

[
\sum_i \binom{d_i}{2}\ge n\binom42=6n.
]

Hence

[
6n\le n(n-2),
]

so

[
n\ge 8.
]

For the total row-sum bound, let

[
E=\sum_i d_i.
]

By Cauchy,

[
\sum_i d_i^2\ge \frac{E^2}{n}.
]

Thus

[
2T
==

# \sum_i d_i(d_i-1)

\sum_i d_i^2-\sum_i d_i
\ge
\frac{E^2}{n}-E.
]

Since (T\le n(n-2)),

[
\frac{E^2}{n}-E\le 2n(n-2).
]

Solving the resulting quadratic inequality gives

[
\boxed{
E\le \frac n2\left(1+\sqrt{8n-15}\right).
}
]

### Sharpness of the (n\ge 8) threshold in the abstract matrix setting

Use indices modulo (n).

For (n=8), define

[
S_i={i+1,i+2,i+5,i+7}\pmod 8.
]

Equivalently, the first row has support

[
D_8={1,2,5,7}.
]

For row (0) and row (t), the intersections are:

[
\begin{array}{c|c}
t & S_0\cap S_t\
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

Every intersection has size at most (2), and whenever the intersection has size (2), the two common columns lie on opposite sides of the row-pair ({0,t}). By cyclic translation, Facts (A) and (B) hold for every row-pair. Thus this is an abstract (8\times8) cyclic matrix with every row sum (4).

For (n\ge 9), define

[
S_i={i+1,i+2,i+4,i+8}\pmod n.
]

For (n\ge 15), the signed differences among

[
D={1,2,4,8}
]

are

[
\pm1,\pm2,\pm3,\pm4,\pm6,\pm7,
]

all distinct modulo (n). Hence two shifted copies of (D) intersect in at most one point, so Fact (B) is vacuous.

For (9\le n\le 14), the only double intersections are as follows:

[
\begin{array}{c|c|c}
n & t & S_0\cap S_t\
\hline
9 & 2 & {1,4}\
9 & 3 & {2,4}\
9 & 6 & {1,8}\
9 & 7 & {2,8}\
\hline
10 & 3 & {1,4}\
10 & 4 & {2,8}\
10 & 6 & {4,8}\
10 & 7 & {1,8}\
\hline
11 & 4 & {1,8}\
11 & 7 & {4,8}\
\hline
12 & 6 & {2,8}\
\hline
13 & 6 & {1,8}\
13 & 7 & {2,8}\
\hline
14 & 7 & {1,8}
\end{array}
]

In every listed case, one common column lies in the open cyclic interval ((0,t)), and the other lies in the complementary interval ((t,0)). Thus the required crossing/alternation condition holds. Therefore for every (n\ge 8), the abstract cyclic-matrix axioms permit all row sums to be (4).

So the desired contradiction cannot be obtained from (A) and (B) alone.

---

## 4. Remaining unresolved configurations and exact patterns

The cyclic argument eliminates only repeated column-pairs and noncrossing (2\times2) all-one patterns. It does not control rows that are almost disjoint from all other rows. In particular, any (4)-regular cyclic Sidon-type pattern with no all-one (2\times2) submatrix survives the entire argument.

A clean unresolved abstract pattern is the following. For (n\ge 39), define

[
M_{ij}=1
\quad\Longleftrightarrow\quad
j-i\equiv 1,4,10,20\pmod n.
]

Equivalently,

[
S_i={i+1,i+4,i+10,i+20}\pmod n.
]

The positive differences among

[
{1,4,10,20}
]

are

[
3,6,9,10,16,19,
]

all distinct, and for (n\ge 39) no positive difference is congruent to the negative of another. Hence two rows intersect in at most one column. Thus Fact (A) holds, and Fact (B) is vacuous because no two rows share two columns.

So the exact surviving pattern is:

[
\boxed{
S_i={i+1,i+4,i+10,i+20}\pmod n,\qquad n\ge 39.
}
]

This pattern has every row sum (4), zero diagonal, and no forbidden (2\times2) submatrix at all. It is not claimed to be geometrically realizable; it shows that the cyclic crossing/discharging method alone cannot prove the full geometric impossibility.

The missing geometric input would have to use more than pairwise row intersections. For example, in the original geometry, each row support (S_i) is not just an arbitrary (4)-set: all four points ({p_j:j\in S_i}) must lie on one circle centered at (p_i). Equivalently, for every pair (a,b\in S_i), the point (p_i) lies on the perpendicular bisector of (p_ap_b). That is a strong concurrency/metric condition on the six pairs inside a row of size (4), and it is invisible to Facts (A) and (B).
