## 1. Convex-position crossing lemma

Let the cyclic order be fixed, and say that two unordered pairs ({x,y}) and ({u,v}) **separate** each other if, going around the polygon, their endpoints alternate; equivalently the chord (p_xp_y) crosses the chord (p_up_v) in its relative interior.

### Lemma B

If (S_i\cap S_k={a,b}) with (i\ne k), then ({i,k}) separates ({a,b}). Equivalently, the chord (p_ip_k) crosses the chord (p_ap_b).

### Proof

Because (a,b\in S_i), we have

[
|p_a-p_i|=|p_b-p_i|=r_i.
]

Because (a,b\in S_k), we also have

[
|p_a-p_k|=|p_b-p_k|=r_k.
]

Thus both (p_i) and (p_k) lie on the perpendicular bisector of the segment (p_ap_b). Since (p_i\ne p_k), the line

[
L=\overleftrightarrow{p_ip_k}
]

is exactly that perpendicular bisector. Equivalently, if (C_i) and (C_k) are the two circles centered at (p_i,p_k), then (p_ap_b) is their common chord, hence their radical axis, and the line of centers (p_ip_k) is perpendicular to that radical axis. Therefore (p_a) and (p_b) are reflections of one another across (L).

So (p_a) and (p_b) lie in opposite open half-planes bounded by (L). They cannot lie on (L), because reflection across (L) fixes points of (L), which would force (p_a=p_b).

Now use strict convexity. For a strictly convex polygon, the line through two vertices (p_i,p_k) contains no other vertex, and the two polygonal boundary chains from (p_i) to (p_k) lie in the two opposite open half-planes bounded by (L). This is the exact point where strict convexity is invoked: without strict convexity, another vertex could lie on the chord line (L), and the open-half-plane separation of the two cyclic arcs could fail.

Since (p_a) and (p_b) are in opposite open half-planes of (L), they belong to opposite cyclic arcs between (i) and (k). Hence the cyclic order alternates:

[
i,\ a,\ k,\ b
]

or

[
i,\ b,\ k,\ a,
]

up to reversal and rotation. Thus ({i,k}) separates ({a,b}), and the chords (p_ip_k) and (p_ap_b) cross. (\square)

---

## 2. Exact theorem proved

Let (M) be any cyclically indexed (0)-(1) matrix with (M_{ii}=0), satisfying:

[
\tag{A} |S_i\cap S_k|\le 2\quad\text{for }i\ne k,
]

and

[
\tag{B} \text{if }S_i\cap S_k={a,b},\text{ then }{i,k}\text{ separates }{a,b}.
]

Then:

[
\boxed{\sum_{i=1}^n \binom{|S_i|}{2}\le n(n-2).}
]

Consequently, if every row has size at least (4), then

[
6n\le \sum_i \binom{|S_i|}{2}\le n(n-2),
]

so necessarily

[
\boxed{n\ge 8.}
]

Moreover, this is sharp at the level of facts (A) and (B): for every (n\ge 8), there exists a cyclic matrix satisfying (A) and (B) with every row having size exactly (4). Thus no contradiction can be derived from (A) and (B) alone. Any proof of geometric nonexistence must use additional metric information beyond the two stated facts.

A useful corollary is the edge bound

[
\boxed{\sum_i |S_i|
\le \frac n2\left(1+\sqrt{8n-15}\right).}
]

This is only an (O(n^{3/2})) bound, so it is far too weak to contradict (\sum_i |S_i|\ge 4n) for large (n).

---

## 3. Cyclic-matrix / discharging argument

For an unordered column-pair ({a,b}), define

[
m_{ab}:=#{i:\ a,b\in S_i}.
]

Think of each row (i) as placing one unit of charge on every unordered pair inside (S_i). Thus row (i) contributes

[
\binom{|S_i|}{2}
]

charges, and the total charge is

[
\sum_i \binom{|S_i|}{2}
=======================

\sum_{{a,b}} m_{ab}.
]

We now bound the capacity of each column-pair ({a,b}).

Fix two columns (a,b). Suppose two distinct rows (i,k) both contain (a,b). Then (S_i\cap S_k) contains ({a,b}), so by (A) their intersection is exactly ({a,b}). By (B), the pair ({i,k}) must separate ({a,b}). Therefore (i) and (k) must lie on opposite cyclic arcs between (a) and (b).

Hence:

[
\boxed{\text{At most one row from each cyclic side of }{a,b}\text{ may contain both }a,b.}
]

So if (a,b) are adjacent columns, one cyclic side is empty, and therefore

[
m_{ab}\le 1.
]

If (a,b) are nonadjacent, both cyclic sides are nonempty, and therefore

[
m_{ab}\le 2.
]

There are exactly (n) adjacent column-pairs and

[
\binom n2-n
]

nonadjacent column-pairs. Therefore

[
\sum_i \binom{|S_i|}{2}
=======================

\sum_{{a,b}}m_{ab}
\le
n+2\left(\binom n2-n\right)
===========================

n(n-2).
]

This proves the main discharging inequality.

If (|S_i|\ge 4) for every (i), then each row contributes at least

[
\binom42=6
]

charges, so

[
6n\le n(n-2),
]

hence (n\ge 8).

For the bound on (\sum_i |S_i|), write

[
E:=\sum_i |S_i|.
]

By Cauchy,

[
\sum_i |S_i|^2\ge \frac{E^2}{n}.
]

Since

[
\sum_i \binom{|S_i|}{2}
=======================

\frac12\left(\sum_i |S_i|^2-E\right),
]

we get

[
\frac12\left(\frac{E^2}{n}-E\right)
\le n(n-2).
]

Solving the resulting quadratic inequality gives

[
E\le \frac n2\left(1+\sqrt{8n-15}\right).
]

---

### Forbidden cyclic (0)-(1) submatrices

The following configurations are forbidden by (A) and (B).

#### Noncrossing (2\times 2) all-one rectangle

If rows (i,k) and columns (a,b) satisfy

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

then ({i,k}) must separate ({a,b}). Thus the only allowed cyclic orders are

[
i,\ a,\ k,\ b
]

or

[
i,\ b,\ k,\ a,
]

up to reversal. The nonalternating orders are forbidden.

In particular:

[
\boxed{\text{Adjacent rows cannot share two columns.}}
]

and

[
\boxed{\text{Adjacent columns cannot occur together in two rows.}}
]

#### (2\times 3) all-one rectangle

Two rows cannot share three columns, because that violates (A):

[
\begin{array}{c|ccc}
& a & b & c\ \hline
i & 1 & 1 & 1\
k & 1 & 1 & 1
\end{array}
]

is forbidden.

#### (3\times 2) all-one rectangle

Three rows cannot all contain the same two columns:

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1\
\ell & 1 & 1
\end{array}
]

Indeed, among three row indices (i,k,\ell), two lie on the same cyclic side of ({a,b}). Those two rows would contain both (a,b), but their pair would not separate ({a,b}), contradicting (B).

---

### Sharpness: a cyclic countermodel for every (n\ge 8)

Index rows and columns by (\mathbb Z_n), cyclically. For (n\ge 8), define

[
S_i={i+1,\ i+2,\ i-1,\ i-3}\pmod n.
]

Equivalently,

[
M_{ij}=1
\quad\Longleftrightarrow\quad
j-i\in {1,2,-1,-3}\pmod n.
]

Every row has size (4), and (M_{ii}=0).

Let

[
D={1,2,-1,-3}.
]

For rows (0) and (t), the common columns are

[
D\cap(t+D).
]

The difference multiset (D-D) has multiplicity at most (2) modulo (n) for (n\ge 8), so every two rows intersect in at most (2) columns. The only offsets (t) giving intersection size (2) are as follows:

[
\begin{array}{c|c|c}
n & t & D\cap(t+D)\ \hline
8 & 2,3,4,5,6
& {1,-1},{2,-3},{1,-3},{2,-1},{-3,-1}\
9 & 2,4,5,7
& {1,-1},{1,-3},{2,-3},{-3,-1}\
10 & 2,5,8
& {1,-1},{2,-3},{-3,-1}\
\ge 11 & 2,n-2
& {1,-1},{-3,-1}
\end{array}
]

In each listed case, one common column lies in the open cyclic interval from (0) to (t), and the other lies in the complementary interval from (t) back to (0). Thus the two common columns are separated by the two row indices. Therefore (B) holds.

So the abstract cyclic-matrix model satisfying (A) and (B) admits row sum (4) for every (n\ge 8). Hence (A) and (B) alone cannot prove the desired contradiction.

---

## 4. Remaining unresolved configurations and exact patterns

The obstruction is that (A) and (B) only control repeated column-pairs. They say almost nothing about rows whose internal pairs are mostly private.

### Unresolved pattern 1: the (n=8) circulant pattern

For (n=8), the sharp countermodel has row template

[
01100101,
]

meaning row (i) has ones in columns

[
i+1,\ i+2,\ i+5,\ i+7
\pmod 8.
]

Explicitly,

[
S_i={i+1,i+2,i-3,i-1}.
]

This satisfies every cyclic consequence of (A) and (B), but it is not automatically geometrically realizable. In fact, ruling it out geometrically requires extra metric information: if this exact pattern came from distances, then each row would force

[
|p_i p_{i+1}|=|p_i p_{i-1}|=|p_i p_{i+2}|,
]

so all side lengths would be equal and every consecutive triple (p_i,p_{i+1},p_{i+2}) would form an equilateral triangle. A strictly convex octagon cannot have all exterior angles (60^\circ), because the total exterior angle sum must be (360^\circ). This argument uses actual distance equalities, not merely (A) and (B).

### Unresolved pattern 2: linear (4)-uniform patterns

Any cyclic matrix with

[
|S_i|=4
]

and

[
|S_i\cap S_k|\le 1
\quad\text{for all }i\ne k
]

automatically satisfies (A), while (B) is vacuous. Thus such patterns are completely invisible to the crossing lemma.

A concrete exact example on (13) cyclic indices is

[
S_i={i+1,\ i+2,\ i+4,\ i+10}\pmod {13}.
]

The row template is

[
0110100000100.
]

The difference set ({1,2,4,10}\subset \mathbb Z_{13}) has the property that every nonzero difference occurs exactly once, so distinct rows intersect in exactly one column. Hence (A) holds and (B) never fires. Whether such a pattern can arise from an actual strictly convex distance configuration requires additional geometry beyond the two supplied facts.

### Unresolved pattern 3: the three-row Pasch-type pattern

The following (3\times 6) pattern is not forbidden by (A) and (B) alone:

[
\begin{array}{c|cccccc}
& a_1&a_2&b_1&b_2&c_1&c_2\ \hline
R_1 & 1&1&0&0&1&1\
R_2 & 1&1&1&1&0&0\
R_3 & 0&0&1&1&1&1
\end{array}
]

Here each pair of rows shares exactly two columns, but the three shared column-pairs are distinct. The crossing lemma merely requires each shared pair to separate the corresponding row-pair. There are cyclic placements satisfying those separation requirements, so this pattern is not eliminated by the current matrix argument.

---

The conclusion is therefore precise: the convex-position crossing lemma gives strong forbidden submatrices and the sharp discharging bound (n\ge 8) under minimum row size (4), but it does not prove geometric nonexistence. Any full contradiction must use further metric structure of equal distances, not just the circle-intersection bound (A) and the crossing rule (B).
