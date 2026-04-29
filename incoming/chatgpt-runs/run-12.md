I will use indices in (\mathbb Z_n) for the matrix part. Thus “(i+1)” means cyclic successor. This is only notation; it is equivalent to the problem’s (1,\dots,n) indexing.

## 1. Convex-position crossing lemma

**Lemma B.** Let (P={p_1,\dots,p_n}) be the vertices of a strictly convex (n)-gon in cyclic order. Suppose (i\ne k), and suppose two distinct indices (a,b) lie in (S_i\cap S_k). Then the chord (p_i p_k) crosses the chord (p_a p_b). Equivalently, in cyclic order the pair ({i,k}) separates the pair ({a,b}).

**Proof.** Since (a,b\in S_i), we have
[
|p_i-p_a|=|p_i-p_b|.
]
Therefore (p_i) lies on the perpendicular bisector of segment (p_a p_b). Similarly, since (a,b\in S_k),
[
|p_k-p_a|=|p_k-p_b|,
]
so (p_k) also lies on the perpendicular bisector of (p_a p_b). Because (p_i\ne p_k), the line (p_i p_k) is exactly that perpendicular bisector. Hence (p_a) and (p_b) are reflections of each other across the line (p_i p_k). This is the common-chord/radical-axis geometry: the common chord (p_a p_b) is perpendicular to the line of centers (p_i p_k), and here the line of centers bisects the common chord.

So (p_a) and (p_b) lie on opposite sides of the line (p_i p_k), and (p_a p_b) meets (p_i p_k) at the midpoint (m) of (p_a p_b).

It remains to show that (p_i) and (p_k) lie on opposite sides of the line (p_a p_b). Suppose not. Then (p_i,p_k) lie on the same side of the line (p_a p_b). Put coordinates so that
[
p_a=(-1,0),\qquad p_b=(1,0),
]
and the perpendicular bisector is the (y)-axis. Then
[
p_i=(0,s),\qquad p_k=(0,t)
]
with (s,t) on the same side of (0). If (0<t<s), then (p_k) lies strictly inside the triangle with vertices (p_a,p_b,p_i). If (0<s<t), then (p_i) lies strictly inside the triangle with vertices (p_a,p_b,p_k). If one of (s,t) is (0), then one of (p_i,p_k) lies on the segment (p_a p_b).

This is the exact point where strict convexity is used: in a strictly convex polygon, every listed vertex is an extreme point of the convex hull; no vertex may lie in the interior of the triangle formed by three other vertices, and no vertex may lie on the segment between two other vertices. Therefore (p_i,p_k) cannot be on the same side of the line (p_a p_b).

Thus (p_i,p_k) lie on opposite sides of the line (p_a p_b), while (p_a,p_b) lie on opposite sides of the line (p_i p_k). Hence the two segments (p_i p_k) and (p_a p_b) cross. For four vertices of a strictly convex polygon, crossing of the two chords is equivalent to cyclic alternation of the endpoints, so ({i,k}) separates ({a,b}). (\square)

---

## 2. Exact theorem proved here

The full contradiction cannot be derived from facts (A) and (B) alone. In fact, there are cyclic (0)-(1) matrices with all row sums equal to (4) satisfying both (A) and (B). Therefore, any proof of geometric nonexistence must use additional metric information beyond (A) and (B).

Here is the sharp matrix-level theorem.

**Theorem.** Let (R_i\subset \mathbb Z_n\setminus{i}) be row supports of a cyclically indexed (0)-(1) matrix satisfying:

[
\text{(A)}\qquad |R_i\cap R_k|\le 2\quad\text{for }i\ne k,
]
and
[
\text{(B)}\qquad \text{if }R_i\cap R_k={a,b},\text{ then }{i,k}\text{ separates }{a,b}.
]

Let (d_i=|R_i|). Then
[
\sum_i \binom{d_i}{2}\le n(n-2).
]
Consequently, if every (d_i\ge 4), then (n\ge 8).

This is sharp at the level of (A) and (B): for every (n\ge 8), there is such a cyclic matrix with every row sum exactly (4).

A useful incidence bound also follows. If (m=\sum_i d_i), then
[
m\le \frac n2\left(1+\sqrt{8n-15}\right).
]

---

## 3. Cyclic-matrix / discharging argument

For an unordered column pair (e={a,b}), define
[
\lambda(e)=|{i: a,b\in R_i}|.
]
Think of each row (R_i) sending one unit of charge to every unordered pair of columns inside (R_i). Then the total charge is
[
Q=\sum_i \binom{d_i}{2}
=\sum_{{a,b}}\lambda({a,b}).
]

### Forbidden cyclic submatrices

The following are immediate consequences of (A) and (B).

**Forbidden pattern 1: (2\times 3) all-ones.**
For two distinct rows (i,k), three common columns are impossible:
[
\begin{array}{c|ccc}
& a&b&c\ \hline
i&1&1&1\
k&1&1&1
\end{array}
]
because this violates (A).

**Forbidden pattern 2: noncrossing (2\times 2) all-ones.**
If two rows (i,k) share two columns (a,b), then the cyclic order must alternate. Thus the pattern
[
\begin{array}{c|cc}
& a&b\ \hline
i&1&1\
k&1&1
\end{array}
]
is forbidden whenever (a,b) lie in the same open cyclic interval cut out by (i,k). Equivalently, after cyclic rotation, orders such as
[
i<k<a<b
\qquad\text{or}\qquad
i<a<b<k
]
are forbidden. The only allowed case is alternation:
[
i<a<k<b
\quad\text{or}\quad
i<b<k<a.
]

**Forbidden pattern 3: adjacent-column (2\times 2) all-ones.**
If (a,a+1) are adjacent cyclic columns, then no two rows can both contain them:
[
\begin{array}{c|cc}
& a&a+1\ \hline
i&1&1\
k&1&1
\end{array}
]
is forbidden. Indeed, ({a,a+1}) cannot be separated by any pair ({i,k}), because one of the two cyclic intervals between (a) and (a+1) is empty.

**Forbidden pattern 4: (3\times 2) all-ones.**
Three rows cannot all contain the same two columns:
[
\begin{array}{c|cc}
& a&b\ \hline
i&1&1\
k&1&1\
\ell&1&1
\end{array}
]
because the two arcs cut out by (a,b) cannot place three row indices pairwise on opposite sides. Two of (i,k,\ell) must lie in the same arc, and that pair would fail the crossing condition (B).

So every adjacent column pair has capacity at most (1), and every nonadjacent column pair has capacity at most (2). There are (n) adjacent unordered column pairs and (\binom n2-n) nonadjacent unordered column pairs. Therefore
[
Q
=\sum_{{a,b}}\lambda({a,b})
\le n+2\left(\binom n2-n\right)
=n(n-2).
]
Hence
[
\boxed{\sum_i\binom{d_i}{2}\le n(n-2).}
]

If every (d_i\ge 4), then every row sends at least (\binom42=6) units of charge, so
[
6n\le \sum_i\binom{d_i}{2}\le n(n-2).
]
Thus
[
6\le n-2,
]
so
[
\boxed{n\ge 8.}
]

The incidence bound follows from Cauchy:
[
\sum_i\binom{d_i}{2}
=\frac12\left(\sum_i d_i^2-\sum_i d_i\right)
\ge \frac12\left(\frac{m^2}{n}-m\right).
]
Combining this with (\sum_i\binom{d_i}{2}\le n(n-2)) gives
[
\frac12\left(\frac{m^2}{n}-m\right)\le n(n-2),
]
so
[
m^2-nm-2n^2(n-2)\le 0.
]
Solving the quadratic inequality,
[
\boxed{
m\le \frac n2\left(1+\sqrt{8n-15}\right).
}
]

There is also a dual version. If (c_j) is the column sum of column (j), then
[
\sum_j\binom{c_j}{2}
=\sum_{i<k}|R_i\cap R_k|
\le n(n-2),
]
because adjacent row pairs can share at most one column, while nonadjacent row pairs can share at most two.

For (n=8), the inequalities force a strong structure: if all row sums are at least (4), then in fact every row sum and every column sum is exactly (4), every adjacent column pair occurs in exactly one row, every nonadjacent column pair occurs in exactly two rows, every adjacent row pair intersects in exactly one column, and every nonadjacent row pair intersects in exactly two columns.

### Sharpness: matrices satisfying (A), (B), and row sum (4)

For every (n\ge 8), define
[
R_i={i-3,\ i-1,\ i+1,\ i+2}\pmod n.
]
Equivalently,
[
M_{ij}=1
\quad\Longleftrightarrow\quad
j-i\equiv -3,-1,1,2\pmod n.
]
Every row has size (4).

It remains to check (A) and (B). By translation, compare (R_0) with (R_t). Let
[
D={-3,-1,1,2}.
]
Then
[
R_0\cap R_t=D\cap(t+D).
]
For (n\ge 11), the only shifts with intersection size (2) are
[
t=2,\qquad R_0\cap R_2={-1,1},
]
and
[
t=n-2,\qquad R_0\cap R_{n-2}={-3,-1}.
]
In both cases, the two shared columns lie one on each side of the row pair, so the crossing condition holds.

For (n=8,9,10), the exceptional shifts are finite and are checked directly:

[
\begin{array}{c|c|c}
n&t&R_0\cap R_t\ \hline
8&2&{7,1}\
8&3&{2,5}\
8&4&{1,5}\
8&5&{2,7}\
8&6&{5,7}\ \hline
9&2&{8,1}\
9&4&{1,6}\
9&5&{2,6}\
9&7&{6,8}\ \hline
10&2&{9,1}\
10&5&{2,7}\
10&8&{7,9}
\end{array}
]

In every listed case, one common column lies in the open interval from (0) to (t), and the other lies in the complementary open interval. Thus ({0,t}) separates the shared column pair. All omitted shifts have intersection size at most (1). Therefore (A) and (B) both hold.

For (n=8), the matrix is explicitly
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
and it satisfies all matrix-level constraints. Hence no contradiction can follow from (A) and (B) alone.

This particular circulant family is not necessarily geometrically realizable. In fact, if it were realized geometrically, the row condition would give
[
|p_i p_{i-1}|=|p_i p_{i+1}|=|p_i p_{i+2}|
]
for every (i). The first equality forces all side lengths to be equal, and then (|p_i p_{i+2}|=|p_i p_{i+1}|) makes every triangle (p_i p_{i+1}p_{i+2}) equilateral. Thus every interior angle would be (60^\circ), impossible for a strictly convex (n)-gon with (n\ge 4). This uses metric information not contained in (A) or (B).

---

## 4. Configurations still unresolved by the A/B method

The following patterns survive the crossing/discharging argument. I do not claim they are geometrically realizable; the point is that (A) and (B) alone do not rule them out.

### Unresolved pattern 1: linked (2\times2) block

For cyclic order
[
i<a<k<b,
]
the block
[
\begin{array}{c|cc}
&a&b\ \hline
i&1&1\
k&1&1
\end{array}
]
is allowed by (B), because (p_i p_k) crosses (p_a p_b). Any proof must use more than the crossing lemma to eliminate such a block.

### Unresolved pattern 2: alternating four-row block

For cyclic order
[
a<b<c<d,
]
the pattern
[
\begin{array}{c|cccc}
&a&b&c&d\ \hline
a&0&1&0&1\
b&1&0&1&0\
c&0&1&0&1\
d&1&0&1&0
\end{array}
]
is compatible with (A) and (B). The row pair ({a,c}) shares columns ({b,d}), and the row pair ({b,d}) shares columns ({a,c}); both are crossing pairs.

### Unresolved pattern 3: a Sidon-type cyclic pattern where (B) is vacuous

For (n\ge 15), define
[
M_{ij}=1
\quad\Longleftrightarrow\quad
j-i\equiv 1,2,4,8\pmod n.
]
Then every row has size (4), and two distinct rows share at most one column. Indeed, the ordered differences among ({1,2,4,8}) are
[
\pm1,\ \pm2,\ \pm3,\ \pm4,\ \pm6,\ \pm7,
]
all distinct modulo (n) for (n\ge 15). Therefore there is no (2\times2) all-one submatrix at all, so (B) never even triggers. This family is completely invisible to the crossing-discharge argument.

A geometric proof of full nonexistence would need extra input beyond (A) and (B), for example the actual metric equalities
[
|p_i-p_{i+1}|=|p_i-p_{i+2}|=|p_i-p_{i+4}|=|p_i-p_{i+8}|
]
and their interaction with strict convexity.
