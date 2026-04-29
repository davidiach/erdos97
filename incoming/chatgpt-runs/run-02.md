## 1. Convex-position crossing lemma

Let (P=(p_1,\dots,p_n)) be a strictly convex polygon in cyclic order. I use “strictly convex” in the standard discrete sense needed here: no three vertices are collinear, and every vertex is an extreme point of the convex hull.

### Lemma B

Suppose (i\ne k) and

[
a,b\in S_i\cap S_k,\qquad a\ne b.
]

Then the pair ({i,k}) separates the pair ({a,b}) in the cyclic order. Equivalently, the chord (p_ip_k) crosses the chord (p_ap_b).

### Proof

Because (a,b\in S_i\cap S_k),

[
|p_a-p_i|=|p_b-p_i|=r_i,
\qquad
|p_a-p_k|=|p_b-p_k|=r_k.
]

Thus both (p_i) and (p_k) lie on the perpendicular bisector of the segment (p_ap_b). Since (p_i\ne p_k), the line

[
L:=p_ip_k
]

is exactly that perpendicular bisector. Therefore reflection across (L) swaps (p_a) and (p_b). This is the radical-axis/common-chord property of two circles: the two common points of the circles centered at (p_i,p_k) are mirror images across the line of centers.

In particular, since (p_a\ne p_b), neither (p_a) nor (p_b) lies on (L), and they lie in opposite open half-planes bounded by (L).

Now use convexity. Consider the two boundary chains of the polygon from (p_i) to (p_k). The line (L) meets the convex polygon in the segment ([p_i,p_k]). Hence the two open boundary chains cannot cross (L). Therefore each open chain lies entirely in one open half-plane bounded by (L).

This is the exact point where strict convexity is invoked: strict convexity rules out any third vertex lying on (L). Without that, a boundary chain could touch (L) at another vertex, and the clean “one chain = one open half-plane” conclusion could fail.

Since (p_a) and (p_b) lie in opposite open half-planes, they must lie on opposite cyclic chains between (i) and (k). Hence the cyclic order is alternating:

[
i,\ a,\ k,\ b
\quad\text{or}\quad
i,\ b,\ k,\ a
]

up to rotation and reversal. Thus ({i,k}) separates ({a,b}), equivalently the chords (p_ip_k) and (p_ap_b) cross. (\square)

---

## 2. Exact theorem proved from (A) and (B)

Let (R_i=S_i) be the support of row (i), and let

[
s_i=|R_i|,\qquad m=\sum_i s_i.
]

Call a cyclic (0)-(1) matrix admissible if it has zero diagonal and satisfies:

[
\tag{A} |R_i\cap R_k|\le 2\quad(i\ne k),
]

and

[
\tag{B} |R_i\cap R_k|=2,\ R_i\cap R_k={a,b}
\implies
{i,k}\text{ separates }{a,b}.
]

The strongest general theorem I can prove from only (A) and (B) is the following.

### Theorem

For every admissible cyclic matrix,

[
\sum_{i=1}^n \binom{s_i}{2}\le n(n-2).
]

Consequently,

[
m\le \frac n2\left(1+\sqrt{8n-15}\right).
]

In particular, if every row has size at least (4), then

[
n\ge 8.
]

This is sharp at the matrix level: there exists an admissible cyclic (8\times 8) matrix with every row sum equal to (4). Therefore no contradiction can be proved from (A) and (B) alone.

---

## 3. Cyclic-matrix / discharging argument

### Basic forbidden submatrices

The crossing lemma gives the following cyclic (0)-(1) restrictions.

First, a (2\times 2) all-one submatrix

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

is allowed only if the cyclic order of (i,k,a,b) is alternating:

[
i,\ a,\ k,\ b
\quad\text{or}\quad
i,\ b,\ k,\ a.
]

So the same (2\times 2) pattern is forbidden when (a,b) lie on the same side of the chord (ik), or equivalently when (i,k) lie on the same side of the chord (ab).

Second, by (A), a (2\times 3) all-one submatrix is forbidden:

[
\begin{array}{c|ccc}
& a & b & c\ \hline
i & 1 & 1 & 1\
k & 1 & 1 & 1
\end{array}
]

because then (|R_i\cap R_k|\ge 3).

Third, a (3\times 2) all-one submatrix is forbidden:

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1\
\ell & 1 & 1
\end{array}
]

Indeed, the two columns (a,b) cut the cyclic order into two arcs. Among the three row indices (i,k,\ell), two lie on the same arc. Those two rows share both (a) and (b), but their row indices do not separate (a,b), contradicting (B).

There are also two important adjacent versions.

If (i) and (i+1) are adjacent row indices, then

[
|R_i\cap R_{i+1}|\le 1,
]

because an edge of a convex polygon crosses no chord. Similarly, if (a) and (a+1) are adjacent column indices, then the pair ({a,a+1}) can occur together in at most one row. Two rows containing both adjacent columns would force some chord to cross the boundary edge (p_ap_{a+1}), impossible.

### Discharging on column pairs

For every row (i), distribute one unit of charge to each unordered pair of columns inside (R_i). Thus row (i) sends

[
\binom{s_i}{2}
]

units of charge.

Now fix a column pair ({a,b}).

If (a,b) are adjacent in the cyclic order, then ({a,b}) can occur together in at most one row.

If (a,b) are nonadjacent, then ({a,b}) can occur together in at most two rows. Otherwise three row indices would contain both (a,b), and two of those row indices would lie on the same cyclic side of ({a,b}), contradicting the crossing condition.

There are (n) adjacent column pairs and

[
\binom n2-n
]

nonadjacent column pairs. Therefore the total charge is at most

[
1\cdot n+2\left(\binom n2-n\right)
= n+n(n-1)-2n
= n(n-2).
]

Hence

[
\boxed{\sum_i \binom{s_i}{2}\le n(n-2).}
]

Now let (m=\sum_i s_i). By convexity of (x\mapsto \binom x2),

[
\sum_i \binom{s_i}{2}
\ge
n\binom{m/n}{2}
===============

\frac n2\left(\frac mn\right)\left(\frac mn-1\right).
]

Combining with the upper bound gives

[
\frac n2\left(\frac mn\right)\left(\frac mn-1\right)
\le n(n-2).
]

Writing (x=m/n),

[
x(x-1)\le 2(n-2),
]

so

[
x\le \frac{1+\sqrt{1+8(n-2)}}2
==============================

\frac{1+\sqrt{8n-15}}2.
]

Thus

[
\boxed{
m\le \frac n2\left(1+\sqrt{8n-15}\right).
}
]

If every row has size at least (4), then

[
\sum_i \binom{s_i}{2}\ge 6n.
]

Therefore

[
6n\le n(n-2),
]

so

[
n\ge 8.
]

For (n=8), equality must hold throughout. Thus any admissible (8\times 8) matrix with all row sums at least (4) must have every row sum exactly (4), every adjacent column pair appearing exactly once, and every nonadjacent column pair appearing exactly twice.

### Sharpness: an admissible (8\times 8) matrix

Index rows and columns modulo (8). Define

[
R_i={i+1,\ i+2,\ i+5,\ i+7}\pmod 8.
]

Equivalently, with rows and columns indexed (0,1,\dots,7),

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

Every row has size (4), and the diagonal is zero.

Let (D={1,2,5,7}). Then (R_i=i+D). For (\delta=k-i\pmod 8), the intersections are:

[
\begin{array}{c|c}
\delta & R_i\cap R_{i+\delta}\ \hline
1 & {i+2}\
2 & {i+1,i+7}\
3 & {i+2,i+5}\
4 & {i+1,i+5}\
5 & {i+2,i+7}\
6 & {i+5,i+7}\
7 & {i+1}
\end{array}
]

Thus every intersection has size (1) or (2), so (A) holds.

When the intersection has size (2), one common column lies on the open arc from (i) to (i+\delta), and the other lies on the complementary arc. Hence the row pair ({i,i+\delta}) separates the common column pair. So (B) holds.

Therefore the matrix is admissible and has all row sums (4). This proves that (A) and (B) alone cannot imply a contradiction.

---

## 4. Remaining unresolved configurations and exact patterns

The following patterns survive all consequences of (A) and (B). They are not claimed to be geometrically realizable; they show exactly where the cyclic-matrix method stops.

### Residual pattern 1: the sharp (8\times 8) pattern

The matrix

[
R_i={i+1,i+2,i+5,i+7}\pmod 8
]

is admissible and has every row sum (4). Thus any proof of geometric impossibility must use information beyond (A) and (B).

For example, to rule out this particular matrix geometrically one can use the additional metric fact

[
j\in S_i\ \text{and}\ i\in S_j
\implies r_i=r_j.
]

In this (8\times 8) pattern, adjacent vertices are mutually joined, so a geometric realization would force

[
r_0=r_1=\cdots=r_7.
]

Then each triangle

[
p_i p_{i+1} p_{i+2}
]

would have all three sides equal, because (i+1,i+2\in S_i) and (i,i+2\in S_{i+1}). Hence every three consecutive vertices would form an equilateral triangle, forcing every polygon interior angle to be (60^\circ), impossible for a convex octagon. This extra argument uses metric symmetry of distance, not merely (A) and (B).

### Residual pattern 2: a linear (13\times 13) pattern where (B) is never triggered

Index rows and columns modulo (13), and set

[
R_i={i+2,\ i+3,\ i+5,\ i+11}\pmod{13}.
]

The difference set

[
D={2,3,5,11}
]

has the property that every nonzero residue modulo (13) occurs exactly once as a difference of two elements of (D). Therefore

[
|R_i\cap R_k|=1
\qquad (i\ne k).
]

Thus (A) holds, and (B) is vacuous. Every row has size (4), and the diagonal is zero. This is another exact cyclic (0)-(1) configuration left completely untouched by the crossing obstruction.

So the final conclusion is:

[
\boxed{
\text{The desired contradiction does not follow from (A) and (B) alone.}
}
]

From those two facts one gets the sharp bound

[
\boxed{
\sum_i \binom{|S_i|}{2}\le n(n-2),
}
]

and hence

[
\boxed{
\sum_i |S_i|
\le
\frac n2\left(1+\sqrt{8n-15}\right).
}
]

Any full geometric contradiction must use additional metric input beyond the pairwise circle-intersection bound and the convex-position crossing lemma.
