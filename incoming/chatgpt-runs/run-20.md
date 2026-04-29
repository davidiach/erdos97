## 1. Convex-position crossing lemma

Let the vertices (p_1,\dots,p_n) be in strictly convex cyclic order. Suppose (i\neq k) and

[
a,b\in S_i\cap S_k,\qquad a\neq b.
]

Then

[
|p_a-p_i|=|p_b-p_i|,\qquad |p_a-p_k|=|p_b-p_k|.
]

Thus both (p_i) and (p_k) lie on the perpendicular bisector of segment (p_ap_b). Since (p_i\neq p_k), the line (p_ip_k) is exactly that perpendicular bisector. Equivalently, (p_a) and (p_b) are reflections of one another across the line (p_ip_k). In particular, (p_a,p_b) lie on opposite sides of the line (p_ip_k).

It remains to prove that (p_i,p_k) lie on opposite sides of the line (p_ap_b). Let (m) be the midpoint of (p_ap_b). Since (p_ip_k) is the perpendicular bisector of (p_ap_b), we have

[
m\in p_ip_k\quad\text{as a line.}
]

If (m) is not between (p_i) and (p_k), then (p_i,p_k) lie on the same side of the line (p_ap_b). Assume, for example, that the order on the line (p_ip_k) is

[
p_i,\ p_k,\ m.
]

Because (m) lies in the open segment (p_ap_b), every point of the open segment (p_im) lies in the interior of the triangle (\triangle p_ip_ap_b). Hence (p_k) lies in the interior of (\triangle p_ip_ap_b).

That is impossible.

**Strict convexity is used exactly here:** every vertex of a strictly convex polygon is an extreme point of the convex hull; in particular, no vertex (p_k) can lie in the convex hull, let alone the interior of a triangle, formed by three other vertices (p_i,p_a,p_b).

Therefore (m) lies between (p_i) and (p_k). Since (m) also lies between (p_a) and (p_b), the two chords (p_ip_k) and (p_ap_b) cross in their interiors.

For vertices of a strictly convex polygon, two chords with four distinct endpoints cross in their interiors if and only if their endpoints alternate in the cyclic order. Hence the pair ({i,k}) separates the pair ({a,b}). This proves Fact (B).

---

## 2. The exact theorem proved here

Let (R_i=S_i), and write (s_i=|R_i|). Assume the cyclic matrix (M) satisfies:

[
|R_i\cap R_k|\le 2
]

and the crossing rule from Fact (B). Then:

[
\boxed{\sum_{i=1}^n \binom{s_i}{2}\le n(n-2).}
]

Consequently,

[
\boxed{\sum_i s_i\le \frac n2\bigl(1+\sqrt{8n-15}\bigr).}
]

In particular, if every row has size at least (4), then

[
6n\le \sum_i \binom{s_i}{2}\le n(n-2),
]

so

[
\boxed{n\ge 8.}
]

Moreover, if (n=8) and all row sums are at least (4), then the matrix structure forced by (A) and (B), together with one additional elementary geometric angle argument, gives a contradiction. Therefore:

[
\boxed{\text{No strictly convex octagon can satisfy } |S_i|\ge 4 \text{ for every } i.}
]

Thus any genuine geometric counterexample, if one exists, must have

[
\boxed{n\ge 9.}
]

However, a full contradiction for all (n) **does not follow from (A) and (B) alone**. There are cyclic (0)-(1) matrices with all row sums (4) satisfying every consequence of (A) and (B). An explicit infinite family is given in Section 4.

---

## 3. Cyclic-matrix and discharging argument

Work modulo (n). For distinct indices (x,y), let

[
I(x,y)={x+1,x+2,\dots,y-1}
]

denote the open clockwise interval from (x) to (y).

Two unordered pairs ({x,y}) and ({u,v}) are said to cross cyclically if exactly one of (u,v) lies in (I(x,y)). This is equivalent to the corresponding chords crossing in the strictly convex polygon.

### 3.1 Forbidden (2\times 2) cyclic submatrices

Suppose rows (i,k) both contain columns (a,b). Then

[
a,b\in R_i\cap R_k.
]

If (a,b) lie on the same side of the pair ({i,k}), then ({i,k}) does not separate ({a,b}), contradicting Fact (B).

So the following (2\times 2) all-one pattern is forbidden unless the row-pair and column-pair cross cyclically:

[
\begin{array}{c|cc}
& a & b\
\hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

Forbidden special cases:

* Adjacent rows (i,i+1) cannot share two columns.
* Adjacent columns (a,a+1) cannot occur together in two rows.
* More generally, if (a,b\in I(i,k)) or (a,b\in I(k,i)), then rows (i,k) cannot both contain (a,b).

Fact (A) also forbids every (2\times 3) all-one submatrix:

[
\begin{array}{c|ccc}
& a & b & c\
\hline
i & 1 & 1 & 1\
k & 1 & 1 & 1
\end{array}
]

because two rows may have at most two common (1)’s.

Fact (B) gives the dual-looking forbidden pattern: no (3\times 2) all-one submatrix. Indeed, if three rows all contained columns (a,b), then two of those three row indices would lie on the same cyclic side of ({a,b}), so those two rows would not separate (a,b), contradicting Fact (B).

Thus

[
\boxed{\text{No }2\times 3\text{ or }3\times 2\text{ all-one submatrix is allowed.}}
]

### 3.2 Column-pair codegree bound

Fix two columns (a,b). Let

[
T_{ab}={i: a,b\in R_i}.
]

If (|T_{ab}|\ge 3), then among three row indices in (T_{ab}), two lie on the same cyclic side of ({a,b}). Those two rows both contain (a,b), contradicting Fact (B). Hence

[
\boxed{|T_{ab}|\le 2.}
]

If (a,b) are adjacent cyclically, then one of the two arcs between them is empty, so no two row indices can separate them. Therefore

[
\boxed{|T_{a,a+1}|\le 1.}
]

### 3.3 Discharging bound

For each row (i), distribute one unit of charge to every unordered pair of columns contained in (R_i). Row (i) sends

[
\binom{s_i}{2}
]

units of charge.

A non-adjacent column-pair can receive charge from at most two rows. An adjacent column-pair can receive charge from at most one row.

There are (n) adjacent column-pairs and

[
\binom n2-n
]

non-adjacent column-pairs. Hence

[
\sum_i \binom{s_i}{2}
\le n+2\left(\binom n2-n\right)
= n+n(n-1)-2n
= n(n-2).
]

So

[
\boxed{\sum_i \binom{|S_i|}{2}\le n(n-2).}
]

Now let

[
m=\sum_i |S_i|.
]

By convexity of (x\mapsto \binom{x}{2}),

[
\sum_i \binom{s_i}{2}
\ge n\binom{m/n}{2}
= \frac{m^2}{2n}-\frac m2.
]

Therefore

[
\frac{m^2}{2n}-\frac m2\le n(n-2),
]

so

[
m^2-nm-2n^2(n-2)\le 0.
]

Solving the quadratic gives

[
\boxed{m\le \frac n2\left(1+\sqrt{8n-15}\right).}
]

In particular, if every (s_i\ge 4), then

[
6n\le \sum_i \binom{s_i}{2}\le n(n-2),
]

so

[
n\ge 8.
]

### 3.4 The extremal (n=8) case

Assume (n=8) and every row has size at least (4). Then

[
\sum_i \binom{s_i}{2}\ge 8\binom42=48.
]

But the discharging bound gives

[
\sum_i \binom{s_i}{2}\le 8(8-2)=48.
]

So equality holds everywhere. Therefore:

[
s_i=4\quad\text{for every }i.
]

Also every adjacent column-pair occurs in exactly one row, and every non-adjacent column-pair occurs in exactly two rows.

The same argument applied dually to column degrees shows that every column has degree (4), adjacent row-pairs intersect in exactly one column, and non-adjacent row-pairs intersect in exactly two columns.

Now consider rows (i) and (i+2). They are non-adjacent, so

[
|R_i\cap R_{i+2}|=2.
]

By Fact (B), their two common columns must be separated by the pair ({i,i+2}). But the interval (I(i,i+2)) consists of the single index (i+1). Hence one common column must be (i+1). Therefore

[
i+1\in R_i.
]

Similarly, using rows (i) and (i-2), we get

[
i-1\in R_i.
]

Thus every row contains both neighboring columns:

[
\boxed{i-1,\ i+1\in R_i\quad\text{for every }i.}
]

Now fix a side ({j,j+1}). Consider rows (j-1) and (j+2). They are non-adjacent, so they share exactly two columns. By Fact (B), one of their common columns lies in the interval

[
I(j-1,j+2)={j,j+1}.
]

If the common column is (j), then row (j+2) contains (j). But row (j+2) already contains its neighbor (j+1). Hence row (j+2) contains both (j,j+1).

If the common column is (j+1), then row (j-1) contains (j+1). But row (j-1) already contains its neighbor (j). Hence row (j-1) contains both (j,j+1).

So every side ({j,j+1}) is contained in one of the two rows (j-1) or (j+2).

Now use one additional geometric input beyond (A) and (B):

If row (j-1) contains both (j) and (j+1), then

[
|p_{j-1}p_j|=|p_{j-1}p_{j+1}|.
]

Thus triangle (p_{j-1}p_jp_{j+1}) is isosceles with base (p_jp_{j+1}). Its base angle at (p_j) is strictly less than (90^\circ). But that base angle is exactly the polygon interior angle at (p_j). Hence angle (p_j) is acute.

Similarly, if row (j+2) contains both (j,j+1), then the polygon interior angle at (p_{j+1}) is acute.

Therefore every side of the octagon has at least one acute endpoint. Hence no two non-acute angles can be adjacent. In an (8)-cycle, that means there are at most (4) non-acute angles, so at least (4) acute angles.

Strict convexity gives every interior angle (<180^\circ), and the acute angles are (<90^\circ). Thus the total angle sum is strictly less than

[
4\cdot 90^\circ+4\cdot 180^\circ=1080^\circ.
]

But a convex octagon has interior angle sum

[
(8-2)\cdot 180^\circ=1080^\circ.
]

Contradiction. Therefore no strictly convex octagon realizes the condition (|S_i|\ge 4) for every row.

---

## 4. Remaining unresolved configurations and exact patterns

The matrix/discharging method above cannot prove a contradiction for all (n). In fact, (A) and (B) alone allow many cyclic (0)-(1) matrices with all row sums (4).

### 4.1 A small (n=8) matrix surviving (A) and (B)

Modulo (8), define

[
R_i={i+1,i+2,i+5,i+7}.
]

The matrix is:

[
\begin{array}{c|cccccccc}
&0&1&2&3&4&5&6&7\
\hline
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

This satisfies (A) and (B). It is not geometrically realizable, however, because every row contains (i+1) and (i+2), forcing every polygon interior angle to be acute, impossible for an octagon.

The mirror pattern

[
R_i={i+1,i+3,i+6,i+7}
]

also satisfies (A) and (B), and is ruled out by the same extra angle argument.

### 4.2 Infinite family not ruled out by (A), (B), or the discharging argument

For every (n\ge 25), define indices modulo (n) and set

[
\boxed{R_i={i+2,\ i+5,\ i+9,\ i+14}.}
]

Equivalently,

[
M_{ij}=1
\quad\Longleftrightarrow\quad
j-i\pmod n\in{2,5,9,14}.
]

Every row has size (4).

The positive differences among

[
D={2,5,9,14}
]

are

[
3,4,5,7,9,12,
]

all distinct. Since the largest sum of two of these is (24<n), the ordered differences are also distinct modulo (n). Therefore two shifted copies (i+D) and (k+D) intersect in at most one element. Hence

[
|R_i\cap R_k|\le 1
]

for all (i\neq k). Fact (A) holds, and Fact (B) is vacuous because no two rows ever share two columns.

Thus this is an exact cyclic (0)-(1) pattern with all row sums (4) satisfying all consequences of (A) and (B). Resolving whether such patterns can or cannot arise from actual Euclidean distances in strictly convex position requires additional geometric input beyond the crossing lemma and the discharging argument above.
