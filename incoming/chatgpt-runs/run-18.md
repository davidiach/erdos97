## 1. Convex-position crossing lemma

**Lemma (crossing lemma).**
Let (P={p_1,\dots,p_n}) be in strictly convex position. Suppose (i\ne k), and suppose two distinct indices (a,b) lie in (S_i\cap S_k). Then the cyclic pairs ({i,k}) and ({a,b}) separate each other. Equivalently, the chord (p_ip_k) crosses the chord (p_ap_b).

**Proof.**
Since (a,b\in S_i\cap S_k),

[
|p_a-p_i|=|p_b-p_i|=r_i,\qquad |p_a-p_k|=|p_b-p_k|=r_k.
]

Thus both (p_i) and (p_k) are equidistant from (p_a) and (p_b). Therefore the line (L=p_ip_k) is the perpendicular bisector of the segment (p_ap_b). In particular, (p_a) and (p_b) are reflections of each other across (L), so they lie in opposite open half-planes bounded by (L).

It remains to show that (p_i) and (p_k) lie on opposite sides of the line (p_ap_b). Let (m) be the midpoint of (p_ap_b). Since (L) is the perpendicular bisector of (p_ap_b), the points (p_i,p_k,m) are collinear.

Assume for contradiction that (p_i) and (p_k) lie on the same side of the line (p_ap_b). Then one of (p_i,p_k) lies strictly between the other and (m) on the line (L). Say (p_i) lies between (m) and (p_k). Then for some (0<t<1),

[
p_i=(1-t)m+t p_k.
]

But

[
m=\frac{p_a+p_b}{2},
]

so

[
p_i=\frac{1-t}{2}p_a+\frac{1-t}{2}p_b+t p_k.
]

All three coefficients are positive and sum to (1). Hence (p_i) lies in the interior of the triangle (\triangle p_ap_bp_k).

This is the exact point where strict convexity is used: in a strictly convex polygon, every listed vertex is an extreme point of the convex hull, so no vertex may lie in the convex hull, let alone the interior, of three other vertices. Contradiction.

Therefore (p_i) and (p_k) lie on opposite sides of the line (p_ap_b). We already know (p_a) and (p_b) lie on opposite sides of the line (p_ip_k). Hence the two segments (p_ip_k) and (p_ap_b) cross in their interiors. For vertices of a convex polygon, two chords cross in their interiors exactly when their endpoints alternate in the cyclic order. Thus ({i,k}) separates ({a,b}). ∎

---

## 2. Exact theorem proved

The full contradiction does **not** follow from facts (A) and (B) alone. The strongest cyclic-matrix theorem I can prove is the following.

**Theorem.**
Let (V=\mathbb Z/n\mathbb Z) be cyclically ordered, and let (S_i\subseteq V\setminus{i}). Assume:

1. (|S_i\cap S_k|\le 2) for all (i\ne k);
2. if (S_i\cap S_k={a,b}), then ({i,k}) separates ({a,b}) cyclically.

Then

[
\sum_{i=1}^n \binom{|S_i|}{2}\le n(n-2).
]

Consequently, if every (|S_i|\ge 4), then necessarily

[
n\ge 8.
]

Moreover, this is sharp at the cyclic-matrix level: for every (n\ge 8), there exists a cyclic (0)-(1) matrix satisfying (A) and (B) with every row sum exactly (4). Therefore no contradiction can be obtained from (A) and (B) alone.

---

## 3. Cyclic-matrix and discharging argument

Write

[
d_i=|S_i|.
]

For a column-pair ({a,b}), define

[
m(a,b)=|{i:\ a,b\in S_i}|.
]

Counting pairs inside rows gives

[
\sum_i \binom{d_i}{2}=\sum_{{a,b}} m(a,b).
]

Now use the cyclic crossing rule.

If (a,b) are **adjacent** in the cyclic order, then no two rows can both contain (a,b). Indeed, if two rows (i,k) both contained (a,b), then by (B), the chord (p_ip_k) would have to cross the polygon edge (p_ap_b), impossible in cyclic order because an adjacent pair has an empty arc on one side. Hence

[
m(a,b)\le 1
]

for adjacent column-pairs.

If (a,b) are **not adjacent**, then (B) implies at most one row containing both (a,b) can lie on each side of the chord (ab). Thus

[
m(a,b)\le 2
]

for non-adjacent column-pairs.

There are (n) adjacent column-pairs and

[
\binom n2-n
]

non-adjacent column-pairs. Therefore

[
\sum_i \binom{d_i}{2}
=\sum_{{a,b}}m(a,b)
\le n+2\left(\binom n2-n\right)
=n+n(n-1)-2n
=n(n-2).
]

If every (d_i\ge 4), then

[
\sum_i\binom{d_i}{2}\ge n\binom42=6n.
]

Thus

[
6n\le n(n-2),
]

so

[
n\ge 8.
]

This proves the claimed bound.

### Forbidden cyclic submatrices

The following configurations are forbidden by (A) and (B).

#### Forbidden (2\times 3) all-one submatrix

For two distinct rows (i,k), one cannot have three common columns:

[
\begin{array}{c|ccc}
& a&b&c\
\hline
i&1&1&1\
k&1&1&1
\end{array}
]

because this would give (|S_i\cap S_k|\ge 3), contradicting (A).

#### Forbidden (3\times 2) all-one submatrix

For two fixed columns (a,b), at most two rows can contain both (a,b). Thus the following is forbidden:

[
\begin{array}{c|cc}
& a&b\
\hline
i&1&1\
k&1&1\
\ell&1&1
\end{array}
]

Indeed, if three rows contained (a,b), two of those rows would lie on the same side of the chord (ab), contradicting (B).

#### Forbidden non-crossing (2\times 2) all-one submatrix

A (2\times 2) all-one submatrix

[
\begin{array}{c|cc}
& a&b\
\hline
i&1&1\
k&1&1
\end{array}
]

is allowed only when the four cyclic positions alternate as

[
i,\ a,\ k,\ b
]

or the reverse. It is forbidden when the row-pair and column-pair do not alternate cyclically. In type notation, the only allowed cyclic type is

[
R,C,R,C.
]

The forbidden types are

[
R,R,C,C
\qquad\text{and}\qquad
R,C,C,R.
]

In particular:

* adjacent rows cannot share two columns;
* adjacent columns cannot be shared by two rows.

---

## 4. Why the full contradiction fails from (A) and (B)

The cyclic-matrix obstruction is sharp. Here are explicit matrices satisfying all consequences of (A) and (B) with every row sum equal to (4).

### Example for (n=8)

Index rows and columns by (\mathbb Z/8\mathbb Z), and define

[
S_i={i+1,\ i+2,\ i+5,\ i+7}\pmod 8.
]

Thus the row-offset pattern is

[
0\ 1\ 1\ 0\ 0\ 1\ 0\ 1.
]

Explicitly:

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

For row (0), the only shifts (t) for which (|S_0\cap S_t|=2) are:

[
\begin{array}{c|c}
t&S_0\cap S_t\
\hline
2&{1,7}\
3&{2,5}\
4&{1,5}\
5&{2,7}\
6&{5,7}
\end{array}
]

In each case, exactly one of the two common columns lies between (0) and (t) cyclically. Hence the row-pair ({0,t}) separates the common column-pair. By cyclic translation, the same holds for every row-pair. Thus (A) and (B) hold.

This example attains equality in the discharging bound:

[
\sum_i\binom{|S_i|}{2}=8\binom42=48=8(8-2).
]

### Examples for every (n\ge 9)

For (n\ge 9), define

[
S_i={i+1,\ i+2,\ i+4,\ i+8}\pmod n.
]

The row-offset pattern is

[
0\ 1\ 1\ 0\ 1\ 0\ 0\ 0\ 1.
]

For (n\ge 15), the differences among ({1,2,4,8}) are all distinct modulo (n), so two rows intersect in at most one column. Thus (A) holds and (B) is vacuous.

For (9\le n\le 14), the only double intersections for row (0) are:

[
\begin{array}{c|c|c}
n&t&S_0\cap S_t\
\hline
9&2&{1,4}\
9&3&{2,4}\
9&6&{1,8}\
9&7&{2,8}\
\hline
10&3&{1,4}\
10&4&{2,8}\
10&6&{4,8}\
10&7&{1,8}\
\hline
11&4&{1,8}\
11&7&{4,8}\
\hline
12&6&{2,8}\
\hline
13&6&{1,8}\
13&7&{2,8}\
\hline
14&7&{1,8}
\end{array}
]

Again, in every listed case, exactly one common column lies between (0) and (t), so the crossing condition holds. By cyclic translation, (A) and (B) hold for all row-pairs.

Therefore, for every (n\ge 8), there exists a cyclic (0)-(1) matrix satisfying (A) and (B) with every row sum (4). This disproves the hope of obtaining a contradiction from (A) and (B) alone.

---

## 5. Additional geometric input needed

The circulant examples above are not claimed to be geometrically realizable. To rule them out geometrically, one needs more than (A) and (B).

For example, the pattern

[
S_i={i+1,i+2,i+4,i+8}
]

contains (i+1,i+2\in S_i) for every (i). If this came from geometry, then

[
|p_i-p_{i+1}|=|p_i-p_{i+2}|
]

for every (i). Let

[
e_i=p_{i+1}-p_i.
]

Then

[
|e_i|=|e_i+e_{i+1}|.
]

Squaring gives

[
|e_i|^2=|e_i|^2+|e_{i+1}|^2+2e_i\cdot e_{i+1},
]

so

[
e_i\cdot e_{i+1}=-\frac{|e_{i+1}|^2}{2}<0.
]

Thus the exterior angle between consecutive sides (e_i,e_{i+1}) is strictly larger than (\pi/2). Summing over all vertices would give total exterior angle strictly larger than (n\pi/2), impossible for (n\ge 4), since the total exterior angle of a convex polygon is (2\pi).

This argument uses genuine metric information, not just (A) and (B).

---

## 6. Remaining unresolved exact patterns

The following cyclic matrix patterns are not eliminated by the crossing/discharging argument.

### Pattern U1: Sidon-type circulant rows

For (n\ge 43), define

[
S_i={i+2,\ i+5,\ i+11,\ i+23}\pmod n.
]

The row-offset pattern is

[
\text{ones at offsets }2,5,11,23.
]

The pairwise differences among (2,5,11,23) are

[
3,6,9,12,18,21
]

up to sign, all distinct modulo (n) for (n\ge 43). Hence any two rows intersect in at most one column. Therefore (A) holds and (B) is vacuous.

This gives an exact family of cyclic (0)-(1) matrices with all row sums (4) that remains completely untouched by the two-row crossing restrictions.

### Pattern U2: the sharp (n=8) equality pattern

The (n=8) circulant matrix

[
S_i={i+1,i+2,i+5,i+7}
]

is also unresolved by (A) and (B) alone. It realizes equality in the discharging bound and satisfies every forbidden-submatrix condition derived above.

---

**Conclusion.**
The convex-position crossing lemma is valid and follows from strict convexity. From it one obtains strong forbidden (0)-(1) submatrices and the sharp bound

[
\sum_i \binom{|S_i|}{2}\le n(n-2).
]

However, (A) and (B) alone do not imply a contradiction with all row sums at least (4). A full geometric nonexistence proof, if true, must use additional metric information beyond the circle-intersection and crossing facts.
