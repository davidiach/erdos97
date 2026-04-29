## 1. Convex-position crossing lemma

Let the vertices be (p_1,\dots,p_n) in cyclic order. I will write (i,k,a,b) also for the corresponding vertices when no confusion is possible.

### Lemma B

Suppose (i\neq k) and (S_i\cap S_k) contains two distinct indices (a,b). Then the pair ({i,k}) separates the pair ({a,b}) in the cyclic order. Equivalently, the chord (p_i p_k) crosses the chord (p_a p_b).

### Proof

Because (a,b\in S_i\cap S_k), we have

[
|p_i-p_a|=|p_i-p_b|=r_i,\qquad |p_k-p_a|=|p_k-p_b|=r_k.
]

Thus both (p_i) and (p_k) lie on the perpendicular bisector of the segment (p_a p_b). Since (p_i\neq p_k), the line (L=p_ip_k) is exactly that perpendicular bisector. Equivalently, (p_a) and (p_b) are mirror images across the line (L). This is the radical-axis/common-chord fact: the common chord (p_a p_b) of the two circles is perpendicular to the line of centers (p_ip_k).

Hence (p_a) and (p_b) lie in opposite open half-planes bounded by (L).

Now use strict convexity. In a strictly convex polygon, for the line (L) through two vertices (p_i,p_k), no other vertex lies on (L), and the two polygonal boundary chains from (p_i) to (p_k) lie in the two opposite open half-planes bounded by (L). This is the exact step where strict convexity is invoked: without strict convexity, other vertices could lie on the chord line and the cyclic separation conclusion could fail or become degenerate.

Since (p_a) and (p_b) lie in opposite open half-planes, they lie on opposite boundary chains from (p_i) to (p_k). Therefore the cyclic order alternates:

[
i,\ a,\ k,\ b
]

or

[
i,\ b,\ k,\ a.
]

Thus ({i,k}) separates ({a,b}), and the two chords (p_ip_k) and (p_ap_b) cross. (\square)

---

## 2. The exact theorem proved here

Let (m_i=|S_i|), and let

[
E=\sum_{i=1}^n m_i
]

be the total number of ones in (M). From facts (A) and (B) one gets the following purely cyclic-matrix theorem.

### Theorem

For every cyclic (0)-(1) matrix (M) satisfying (A) and (B),

[
\sum_{i=1}^n \binom{m_i}{2}\le n(n-2).
]

Consequently,

[
E\le \frac n2\Bigl(1+\sqrt{8n-15}\Bigr).
]

In particular, if every row has size at least (4), then (n\ge 8).

For the original geometric problem, the case (n=8) is also impossible. Thus any geometric counterexample to “some row has size at most (3)” must have

[
n\ge 9.
]

However, facts (A) and (B) alone do **not** prove a full contradiction for (n\ge 9): there are explicit cyclic (0)-(1) matrices with all row sums (4) satisfying all consequences of (A) and (B). I list exact unresolved patterns in Section 4.

---

## 3. Cyclic-matrix / discharging argument

Write (I(x,y)) for the open clockwise interval of indices strictly after (x) and strictly before (y).

From (B), we immediately get the forbidden (2\times 2) cyclic pattern:

[
\begin{array}{c|cc}
& a & b\
\hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

is allowed only if (a) and (b) lie on opposite sides of the chord (ik), i.e. only if one of (a,b) lies in (I(i,k)) and the other lies in (I(k,i)).

Equivalently,

[
|S_i\cap S_k\cap I(i,k)|\le 1,
]

and

[
|S_i\cap S_k\cap I(k,i)|\le 1.
]

In particular, adjacent rows satisfy

[
|S_i\cap S_{i+1}|\le 1,
]

because one of the two cyclic intervals is empty.

### Dual forbidden configurations

Now fix two columns (a,b). Ask how many rows can contain both (a) and (b).

If (a,b) are nonadjacent, then at most two rows can contain both columns. Indeed, if three rows (i,k,\ell) all contained both (a) and (b), then among (i,k,\ell), two would lie on the same side of the pair ({a,b}). Those two rows would share the two columns (a,b) without being separated by them, contradicting (B).

If (a,b) are adjacent columns, then at most one row can contain both. For if two rows contained both (a,b), those two row indices would necessarily lie in the single nonempty cyclic interval between (a) and (b), so again the separation required by (B) would fail.

Thus:

* an adjacent column-pair has capacity (1);
* a nonadjacent column-pair has capacity (2).

There are (n) adjacent column-pairs and (\binom n2-n) nonadjacent column-pairs. Therefore the total capacity is

[
n\cdot 1+2\left(\binom n2-n\right)=n(n-2).
]

Now discharge as follows: every row (i) sends one unit of charge to each unordered pair of columns inside (S_i). Row (i) sends

[
\binom{m_i}{2}
]

units of charge. By the capacity bound above,

[
\sum_i \binom{m_i}{2}\le n(n-2).
]

This proves the main discharging inequality.

Using convexity,

[
\sum_i \binom{m_i}{2}
=====================

\frac12\sum_i m_i^2-\frac12E
\ge
\frac{E^2}{2n}-\frac E2.
]

Hence

[
\frac{E^2}{2n}-\frac E2\le n(n-2),
]

so

[
E^2-nE-2n^2(n-2)\le 0.
]

Solving the quadratic inequality gives

[
E\le \frac n2\Bigl(1+\sqrt{8n-15}\Bigr).
]

If every row has size at least (4), then (E\ge 4n). More directly,

[
6n=\sum_i \binom 42\le \sum_i\binom{m_i}{2}\le n(n-2),
]

so

[
6\le n-2,
]

hence

[
n\ge 8.
]

So (A) and (B) already forbid (n\le 7).

### The geometric (n=8) case

Assume now that (n=8) and every row has size at least (4). The discharging inequality forces equality everywhere:

[
m_i=4 \qquad \text{for all }i.
]

A symmetric version of the same counting, now counting common columns of row-pairs, gives:

* adjacent row-pairs intersect in exactly (1) column;
* nonadjacent row-pairs intersect in exactly (2) columns.

Indeed, if (c_j) is the column sum of column (j), then

[
\sum_j \binom{c_j}{2}
=====================

\sum_{i<k}|S_i\cap S_k|.
]

The left side is at least (8\binom42=48), while the row-pair version of the capacity bound gives at most

[
8\cdot 1+2\left(\binom82-8\right)=48.
]

So equality holds.

Now look at rows (i) and (i+2). They are nonadjacent, so they share exactly two columns. By (B), one shared column must lie in the interval

[
I(i,i+2)={i+1}.
]

Therefore

[
i+1\in S_i.
]

Similarly, comparing rows (i) and (i-2) gives

[
i-1\in S_i.
]

Thus every row contains both cyclic neighbours:

[
i-1,\ i+1\in S_i.
]

Geometrically this means

[
r_i=|p_i-p_{i-1}|=|p_i-p_{i+1}|.
]

Let (e_i=|p_i-p_{i+1}|). Then

[
e_{i-1}=r_i=e_i
]

for every (i), so all side lengths are equal, and all radii (r_i) are the same common length (L).

Therefore

[
M_{ij}=1
\iff
|p_i-p_j|=L
\iff
M_{ji}=1.
]

So in the (n=8) geometric equality case, (M) must be symmetric.

Let (C) be the adjacency matrix of the (8)-cycle. Since (M) is symmetric, ((M^2)_{ik}=|S_i\cap S_k|). From the equality conditions,

[
M^2=G,
]

where

[
G_{ii}=4,\qquad G_{i,i\pm1}=1,\qquad G_{ik}=2 \text{ otherwise}.
]

Equivalently,

[
G=2J+2I-C,
]

where (J) is the all-ones matrix.

The eigenvalues of (C) are (2\cos(2\pi k/8)). Hence the eigenvalues of (G) are:

[
16,\quad 4,\quad 2,2,\quad 2-\sqrt2,2-\sqrt2,\quad 2+\sqrt2,2+\sqrt2.
]

Because (M^2=G) and (M) is symmetric, each eigenspace of (G) is (M)-invariant. Since every row of (M) has sum (4), (M) has eigenvalue (4) on the all-ones vector. On the one-dimensional alternating eigenspace, (M) has eigenvalue (\pm 2). On the two-dimensional eigenspaces with (G)-eigenvalues (2), (2-\sqrt2), (2+\sqrt2), the traces of (M) are respectively of the form

[
a\sqrt2,\qquad b\sqrt{2-\sqrt2},\qquad c\sqrt{2+\sqrt2},
]

where (a,b,c\in{-2,0,2}).

But (\operatorname{tr}M=0), because (M) has zero diagonal. Therefore

[
0=4\pm 2+a\sqrt2+b\sqrt{2-\sqrt2}+c\sqrt{2+\sqrt2}.
]

The numbers

[
1,\quad \sqrt2,\quad \sqrt{2-\sqrt2},\quad \sqrt{2+\sqrt2}
]

are linearly independent over (\mathbb Q). For example, if (\alpha=\sqrt{2-\sqrt2}), then (\alpha) has minimal polynomial

[
x^4-4x^2+2,
]

and

[
\sqrt2=2-\alpha^2,\qquad \sqrt{2+\sqrt2}=3\alpha-\alpha^3,
]

so these four numbers form a (\mathbb Q)-basis of the same degree-four field.

Thus the rational part (4\pm 2) would have to vanish. But (4+2=6) and (4-2=2), impossible.

So the geometric (n=8) case cannot occur.

Therefore any genuine geometric example with all rows of size at least (4) would have to satisfy

[
n\ge 9.
]

---

## 4. Unresolved exact cyclic patterns

The discharging argument cannot prove a full contradiction for (n\ge 9). The obstruction is concrete: there are cyclic matrices satisfying all consequences of (A) and (B) with every row sum equal to (4).

### A (9\times 9) unresolved pattern

Work modulo (9), and define

[
S_i={i+1,\ i+2,\ i+5,\ i+7}.
]

Explicitly:

[
\begin{aligned}
S_0&={1,2,5,7},\
S_1&={2,3,6,8},\
S_2&={0,3,4,7},\
S_3&={1,4,5,8},\
S_4&={0,2,5,6},\
S_5&={1,3,6,7},\
S_6&={2,4,7,8},\
S_7&={0,3,5,8},\
S_8&={0,1,4,6}.
\end{aligned}
]

For row (0), the intersections with row-shifts (d=1,\dots,8) are:

[
\begin{array}{c|c}
d & S_0\cap S_d\
\hline
1 & {2}\
2 & {7}\
3 & {1,5}\
4 & {2,5}\
5 & {1,7}\
6 & {2,7}\
7 & {5}\
8 & {1}
\end{array}
]

The double intersections occur only for (d=3,4,5,6), and in each case one common column lies in the interval ((0,d)) and the other lies outside it. By cyclic translation, the same holds for every row-pair. Thus this matrix satisfies (A) and (B), and every row has size (4).

This pattern is not claimed to be geometrically realizable. It is unresolved by the discharging argument above.

### An infinite unresolved family

For every (n\ge 19), work modulo (n), and define

[
S_i={i+1,\ i+2,\ i+5,\ i+10}.
]

The positive differences among

[
D={1,2,5,10}
]

are

[
1,\ 3,\ 4,\ 5,\ 8,\ 9,
]

all distinct. Since (n\ge 19), the signed differences

[
\pm1,\ \pm3,\ \pm4,\ \pm5,\ \pm8,\ \pm9
]

are also distinct modulo (n). Therefore two different rows intersect in at most one column. Fact (A) holds, and fact (B) is vacuous because there are no double intersections.

So this gives exact cyclic (0)-(1) matrices with all row sums (4) satisfying the full ((A),(B)) matrix theory.

### Extra geometric obstruction not captured by (A) and (B)

There is one more elementary geometric input that rules out some such patterns, but not all.

Choose a vertex (i) with minimal radius (r_i). Since the polygon is strictly convex, all other vertices lie in an open cone at (p_i) of angle (<\pi). This is another explicit use of strict convexity.

If (|S_i|\ge 4), list four elements of (S_i) in their angular order around (p_i). Among the three angular gaps, one is (<\pi/3). The chord between the corresponding two vertices has length

[
2r_i\sin(\theta/2)<r_i.
]

Since (r_i) was minimal, those two vertices cannot be joined by an (M)-edge in either direction. Therefore, in a genuine geometric configuration, a minimum-radius row must contain a consecutive pair of selected vertices ((a,b)) such that

[
M_{ab}=M_{ba}=0.
]

The (9\times 9) pattern above and the infinite family (S_i={i+1,i+2,i+5,i+10}) both contain such a consecutive non-edge in every row, so even this additional short-gap obstruction does not eliminate them. More geometry would be needed to decide whether any of these cyclic matrix patterns can actually arise from strictly convex point sets.
