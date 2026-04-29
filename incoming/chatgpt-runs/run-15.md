I will use indices in (\mathbb Z_n) for the matrix part. Thus (i+1) means the next cyclic index, and (R_i:=S_i).

## 1. Convex-position crossing lemma

**Lemma.** Let (P={p_1,\dots,p_n}) be the vertices of a strictly convex polygon in cyclic order. Suppose (i\ne k), and suppose (S_i\cap S_k) contains two distinct indices (a,b). Then the pairs ({i,k}) and ({a,b}) separate each other in cyclic order. Equivalently, the chord (p_i p_k) crosses the chord (p_a p_b).

**Proof.** Let (C_i) be the circle centered at (p_i) of radius (r_i), and let (C_k) be the circle centered at (p_k) of radius (r_k). Since (a,b\in S_i\cap S_k), the two points (p_a,p_b) lie on both circles.

Let (L) be the line through (p_i) and (p_k). Reflection in (L) fixes both centers (p_i,p_k), and therefore preserves both circles (C_i,C_k). Hence it preserves their intersection. Since two distinct nonconcentric circles meet in at most two points, reflection in (L) must swap (p_a) and (p_b). Equivalently, (p_a) and (p_b) are mirror images across (L). In particular, (p_a) and (p_b) lie in opposite open half-planes bounded by (L), and the segment (p_a p_b) meets (L) at its midpoint.

Now use strict convexity. For any chord (p_i p_k) of a strictly convex polygon, the two open polygonal chains from (p_i) to (p_k) lie in the two opposite open half-planes determined by the line (L=p_i p_k). The strictness is invoked exactly here: no vertex other than (p_i,p_k) is allowed to lie on (L), and no chain can cross to the other side of (L). Thus two vertices lying on opposite sides of (L) must lie on opposite cyclic arcs between (i) and (k).

Since (p_a) and (p_b) are on opposite sides of (L), the indices (a,b) lie on different cyclic arcs between (i) and (k). Therefore ({i,k}) separates ({a,b}). In a convex quadrilateral, alternating endpoints are exactly the condition that the two chords cross, so (p_i p_k) crosses (p_a p_b). (\square)

---

## 2. The exact theorem proved from (A) and (B)

The full desired contradiction does **not** follow from (A) and (B) alone. There are cyclic (0)-(1) matrices with all row sums equal to (4) satisfying both conditions. Therefore any proof of geometric nonexistence must use extra metric geometry beyond (A) and the crossing lemma.

Here is the strongest general statement obtained from (A) and (B).

**Theorem.** Let (M) be a zero-diagonal cyclic (n\times n) (0)-(1) matrix with row supports (R_i), satisfying:

[
|R_i\cap R_k|\le 2
]

for all (i\ne k), and whenever (R_i\cap R_k) contains two indices (a,b), the pair ({i,k}) separates ({a,b}) cyclically. Then:

[
\sum_{i=1}^n \binom{|R_i|}{2}\le n(n-2).
]

Consequently, if every row has size at least (4), then

[
6n\le n(n-2),
]

so necessarily

[
n\ge 8.
]

Moreover, if (n=8) and all row sums are at least (4), then in fact every row has size exactly (4), every column has size exactly (4), adjacent rows meet in exactly one column, nonadjacent rows meet in exactly two columns, and every row contains its two cyclic neighbors.

So (A) and (B) prove nonexistence only for (n\le 7). They do not prove nonexistence in general.

---

## 3. Cyclic-matrix / discharging argument

Write (r_i=|R_i|). Think of row (i) as sending one unit of charge to each unordered pair of columns inside (R_i). Thus the total charge emitted is

[
\sum_i \binom{r_i}{2}.
]

We now bound how much charge any fixed unordered column pair ({a,b}) can receive.

### Forbidden (2\times 2) pattern

Suppose two rows (i,k) both contain two columns (a,b). Then the (2\times 2) submatrix on rows (i,k) and columns (a,b) is all (1)’s. By (B), the cyclic order of the four indices must alternate:

[
i,\ a,\ k,\ b
]

or

[
i,\ b,\ k,\ a.
]

Thus the following is forbidden:

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

whenever the row pair ({i,k}) does **not** separate the column pair ({a,b}).

In particular:

* adjacent rows cannot share two columns;
* adjacent columns cannot occur together in two different rows.

### Forbidden (2\times 3) pattern

Fact (A) gives immediately:

[
\begin{array}{c|ccc}
& a & b & c\ \hline
i & 1 & 1 & 1\
k & 1 & 1 & 1
\end{array}
]

is impossible for (i\ne k). Two rows cannot have three common (1)’s.

### Forbidden (3\times 2) pattern

A second consequence of (B) is that three rows cannot all contain the same two columns. Indeed, suppose rows (i,k,\ell) all contain columns (a,b). Since the diagonal is zero, none of (i,k,\ell) equals (a) or (b). Removing (a,b) from the cycle leaves two arcs. Among three row indices, two must lie on the same arc. Those two rows do not separate (a,b), contradicting (B).

Thus

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1\
\ell & 1 & 1
\end{array}
]

is impossible.

### Capacity count

For a fixed column pair ({a,b}), let (m(a,b)) be the number of rows containing both (a) and (b).

If (a,b) are adjacent cyclically, then (m(a,b)\le 1), because two rows containing both would give a forbidden (2\times2) pattern with adjacent columns.

If (a,b) are nonadjacent, then (m(a,b)\le 2), because (m(a,b)\ge3) would give a forbidden (3\times2) pattern.

There are (n) adjacent column pairs and (\binom n2-n) nonadjacent column pairs. Hence

[
\sum_i \binom{r_i}{2}
=====================

\sum_{{a,b}} m(a,b)
\le
n\cdot 1+\left(\binom n2-n\right)\cdot 2.
]

Therefore

[
\sum_i \binom{r_i}{2}
\le
n+n(n-3)
========

n(n-2).
]

If every (r_i\ge4), then (\binom{r_i}{2}\ge6), so

[
6n\le n(n-2),
]

and therefore (n\ge8).

A useful corollary is the global bound

[
\sum_i |R_i|
\le
\frac n2\left(1+\sqrt{8n-15}\right).
]

Indeed, if (E=\sum_i r_i), convexity of (x\mapsto \binom{x}{2}) gives

[
\sum_i \binom{r_i}{2}
\ge
n\binom{E/n}{2}
===============

\frac{E^2}{2n}-\frac E2.
]

Combining this with (\sum_i \binom{r_i}{2}\le n(n-2)) and solving the resulting quadratic inequality gives the displayed bound.

### The extremal (n=8) structure

If (n=8) and every row has size at least (4), then the inequality is tight:

[
\sum_i \binom{r_i}{2}=8\cdot6=48=8(8-2).
]

Thus every row has size exactly (4), and every column-pair capacity is saturated. A symmetric row-pair count also gives every column size exactly (4), adjacent rows meet in exactly one column, and nonadjacent rows meet in exactly two columns.

Now take rows (i-1) and (i+1). They are nonadjacent, so they share exactly two columns. By (B), one common column must lie on the short arc between (i-1) and (i+1), which consists only of (i). Therefore

[
i\in R_{i-1}\cap R_{i+1}.
]

Reindexing, every row (R_i) contains both (i-1) and (i+1).

This is a genuine structural theorem, but it is still not a contradiction at the cyclic-matrix level.

---

## 4. Configurations left by the matrix argument

The matrix contradiction is false. Here is an explicit family satisfying (A) and (B) with all row sums equal to (4).

For (n\ge8), define

[
R_i={i+1,\ i+2,\ i+5,\ i+7}\pmod n.
]

Equivalently,

[
M_{ij}=1
\quad\Longleftrightarrow\quad
j-i\pmod n\in{1,2,5,7}.
]

Every row has exactly four (1)’s.

Because the construction is cyclic, it suffices to compare (R_0) and (R_t). The positive differences among

[
D={1,2,5,7}
]

are

[
1,2,3,4,5,6,
]

each occurring exactly once. Hence for (n\ge13), no two distinct rows share more than one column. Thus (A) holds, and (B) is vacuous.

For (8\le n\le12), the only two-point intersections are as follows:

[
\begin{array}{c|c}
n & \text{two-point intersections } R_0\cap R_t \ \hline
8 &
t=2:{1,7},
t=3:{2,5},
t=4:{1,5},
t=5:{2,7},
t=6:{5,7}
[2mm]
9 &
t=3:{1,5},
t=4:{2,5},
t=5:{1,7},
t=6:{2,7}
[2mm]
10 &
t=4:{1,5},
t=5:{2,7},
t=6:{1,7}
[2mm]
11 &
t=5:{1,7},
t=6:{2,7}
[2mm]
12 &
t=6:{1,7}.
\end{array}
]

In every listed case, one common column lies in the arc ((0,t)), and the other lies in the complementary arc ((t,0)). Therefore (B) holds. So this is a valid cyclic matrix pattern with all row sums (4).

For (n=8), the row supports are explicitly:

[
\begin{aligned}
R_0&={1,2,5,7},\
R_1&={0,2,3,6},\
R_2&={1,3,4,7},\
R_3&={0,2,4,5},\
R_4&={1,3,5,6},\
R_5&={2,4,6,7},\
R_6&={0,3,5,7},\
R_7&={0,1,4,6}.
\end{aligned}
]

Thus the cyclic-matrix method based only on (A) and (B) cannot prove the desired geometric contradiction.

A second, cleaner “B is completely vacuous” pattern is this: for (n\ge47), set

[
R_i={i+3,\ i+7,\ i+15,\ i+26}\pmod n.
]

The six positive differences among ({3,7,15,26}) are

[
4,8,11,12,19,23,
]

all distinct, and for (n\ge47) no signed differences collide modulo (n). Hence any two rows meet in at most one column. Again all rows have size (4), (A) holds, and (B) is vacuous.

These patterns are not claimed to be geometrically realizable. They show exactly where the matrix argument stops: ruling them out would require additional geometric input, such as angle constraints, perpendicular-bisector constraints from the full radical-axis geometry, or other metric information not encoded in (A) and (B).
