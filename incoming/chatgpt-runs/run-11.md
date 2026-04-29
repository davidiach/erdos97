## 1. Convex-position crossing lemma

Let (P={p_1,\dots,p_n}) be in strictly convex position, indexed cyclically. Suppose two distinct rows (i\ne k) share two indices (a,b), so

[
a,b\in S_i\cap S_k.
]

Then

[
|p_a-p_i|=|p_b-p_i|,\qquad |p_a-p_k|=|p_b-p_k|.
]

Thus both (p_i) and (p_k) lie on the perpendicular bisector of the segment (p_ap_b). Since (p_i\ne p_k), the line (p_ip_k) is exactly that perpendicular bisector. Equivalently, (p_a) and (p_b) are mirror images across the line (p_ip_k). Let (m) be the midpoint of (p_ap_b). Then

[
m\in p_ip_k,\qquad p_ap_b\perp p_ip_k.
]

It remains to show that (m) lies between (p_i) and (p_k). If not, then (p_i) and (p_k) lie on the same side of the line (p_ap_b), or one of them equals (m).

If one of (p_i,p_k) equals (m), then that vertex lies on the segment (p_ap_b), so three vertices are collinear. **This is impossible by strict convexity.**

Otherwise, assume without loss of generality that the points on the line (p_ip_k) occur in the order

[
p_i,\ p_k,\ m.
]

Then (p_k) lies strictly inside the triangle (\triangle p_ip_ap_b): indeed, the median from (p_i) to the base (p_ap_b) is the segment (p_im), and every point of the open segment ((p_i,m)) lies in the interior of that triangle. Hence (p_k) is in the convex hull of three other vertices. **This is the main strict-convexity step:** in a strictly convex polygon, every listed point is an extreme point of the convex hull, so no vertex may lie in the interior of a triangle formed by three other vertices.

Therefore (m) must lie in the open segment (p_ip_k). Since (p_a,p_b) are on opposite sides of the line (p_ip_k), and (p_i,p_k) are on opposite sides of the line (p_ap_b), the segments (p_ip_k) and (p_ap_b) cross at (m). For four vertices of a strictly convex polygon, two chords cross if and only if their endpoints alternate in the cyclic order. Thus the pair ({i,k}) separates the pair ({a,b}).

That proves Fact (B).

---

## 2. Exact theorem proved

The full contradiction does **not** follow from Facts (A) and (B). The strongest clean theorem obtainable from those two facts alone is the following sharp cyclic-matrix statement.

**Theorem.** Let (M) be a cyclically indexed zero-diagonal (0)-(1) matrix satisfying:

[
\tag{A} |S_i\cap S_k|\le 2\quad\text{for all }i\ne k,
]

and

[
\tag{B} \text{if }S_i\cap S_k={a,b},\text{ then }{i,k}\text{ separates }{a,b}.
]

Let (s_i=|S_i|). Then

[
\sum_i \binom{s_i}{2}\le n(n-2).
]

Consequently,

[
\sum_i s_i\le \frac n2\left(1+\sqrt{8n-15}\right).
]

In particular, if every (s_i\ge 4), then necessarily

[
n\ge 8.
]

This is sharp for the matrix problem determined by (A) and (B): for every (n\ge 8), there exists a cyclically indexed zero-diagonal (0)-(1) matrix satisfying (A), (B), and (s_i=4) for every row.

Therefore no proof using only (A) and (B) can rule out all row sums being at least (4). Any genuine geometric contradiction would need additional metric information beyond (A) and (B), such as the actual row-wise concyclicity constraints.

---

## 3. Cyclic-matrix and discharging argument

Write cyclic intervals as

[
(x,y)={z:\ z\text{ occurs after }x\text{ and before }y\text{ in cyclic order}}.
]

### Forbidden (2\times 3) pattern

Fact (A) immediately forbids a (2\times 3) all-one submatrix:

[
\begin{array}{c|ccc}
& a&b&c\ \hline
i&1&1&1\
k&1&1&1
\end{array}
]

because that would give (|S_i\cap S_k|\ge 3).

### Forbidden noncrossing (2\times 2) pattern

If two rows (i,k) share two columns (a,b), then by (B), the four labels must alternate cyclically. Thus the all-one submatrix

[
\begin{array}{c|cc}
& a&b\ \hline
i&1&1\
k&1&1
\end{array}
]

is allowed only when the cyclic order is one of

[
i,\ a,\ k,\ b
\qquad\text{or}\qquad
i,\ b,\ k,\ a.
]

It is forbidden when the order is nonalternating, for example

[
i,\ k,\ a,\ b
\qquad\text{or}\qquad
i,\ a,\ b,\ k.
]

Equivalently, two rows may share two columns only if one shared column lies in ((i,k)) and the other lies in ((k,i)).

A useful corollary: adjacent rows cannot share two columns. If (k=i+1), then one of the two arcs between (i) and (k) is empty, so no two shared columns can be separated by ({i,k}). Hence

[
|S_i\cap S_{i+1}|\le 1.
]

### Forbidden (3\times 2) pattern

Fix two columns (a,b). Suppose three distinct rows (i,k,\ell) all contain both (a) and (b). Then each pair of those rows would have to separate ({a,b}). But the two columns (a,b) split the cyclic order into two open arcs. At most one of (i,k,\ell) can lie in each arc if every pair is to be separated by ({a,b}). Three rows cannot be placed that way.

Therefore the all-one pattern

[
\begin{array}{c|cc}
& a&b\ \hline
i&1&1\
k&1&1\
\ell&1&1
\end{array}
]

is forbidden.

Even more sharply, if (a,b) are adjacent columns, then no two rows can both contain (a,b). One of the arcs between (a) and (b) is empty, so two rows cannot be separated by the adjacent pair ({a,b}).

### Discharging

Place one unit of charge on every unordered pair of (1)’s in a row. Row (i) contributes

[
\binom{s_i}{2}
]

units of charge, so the total charge is

[
Q=\sum_i \binom{s_i}{2}.
]

Now redistribute that charge to column pairs: a row (i) charges the column pair ({a,b}) whenever (a,b\in S_i).

For a fixed column pair ({a,b}):

* if (a,b) are adjacent cyclically, then at most one row contains both;
* otherwise, at most two rows contain both, and if two do, they must lie on opposite sides of the chord (p_ap_b) in the cyclic sense.

There are (n) adjacent column pairs and

[
\binom n2-n
]

nonadjacent column pairs. Hence

[
Q
\le n\cdot 1+2\left(\binom n2-n\right)
= n+n(n-1)-2n
= n(n-2).
]

Thus

[
\boxed{\sum_i \binom{s_i}{2}\le n(n-2).}
]

If every (s_i\ge 4), then

[
\sum_i \binom{s_i}{2}\ge n\binom42=6n,
]

so

[
6n\le n(n-2),
]

hence

[
n\ge 8.
]

For the bound on total row sum, let

[
m=\sum_i s_i.
]

By Cauchy,

[
\sum_i s_i^2\ge \frac{m^2}{n}.
]

Since

[
\sum_i \binom{s_i}{2}
=\frac12\left(\sum_i s_i^2-\sum_i s_i\right),
]

we get

[
\frac12\left(\frac{m^2}{n}-m\right)\le n(n-2).
]

Solving the quadratic inequality gives

[
\boxed{
m\le \frac n2\left(1+\sqrt{8n-15}\right).
}
]

This is much weaker than (m<4n) for large (n), so it cannot prove the desired contradiction.

### Sharpness: explicit matrices with every row sum (4)

For (n=8), define indices modulo (8) and set

[
S_i={i+1,\ i+2,\ i+5,\ i+7}.
]

Equivalently, the matrix is

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

Every row has sum (4). For row (0), the only double intersections with row (q) are:

[
\begin{array}{c|c}
q & S_0\cap S_q\ \hline
2&{1,7}\
3&{2,5}\
4&{1,5}\
5&{2,7}\
6&{5,7}
\end{array}
]

In every case, one shared column lies in ((0,q)) and the other lies in ((q,0)), so (B) holds. By cyclic symmetry, the same is true for every pair of rows. Thus this (8\times 8) matrix satisfies (A), (B), and all row sums equal (4).

For every (n\ge 9), define indices modulo (n) and set

[
S_i={i+1,\ i+2,\ i+4,\ i+8}.
]

Again every row has sum (4). For (n\ge 15), the nonzero differences among

[
D={1,2,4,8}
]

are

[
\pm1,\ \pm2,\ \pm3,\ \pm4,\ \pm6,\ \pm7,
]

which are all distinct modulo (n). Hence two rows intersect in at most one column, so (A) holds and (B) is vacuous.

For (9\le n\le 14), the only double intersections for row (0) are as follows:

[
\begin{array}{c|c|c}
n&q&S_0\cap S_q\ \hline
9&2&{1,4}\
9&3&{2,4}\
9&6&{1,8}\
9&7&{2,8}\ \hline
10&3&{1,4}\
10&4&{2,8}\
10&6&{4,8}\
10&7&{1,8}\ \hline
11&4&{1,8}\
11&7&{4,8}\ \hline
12&6&{2,8}\ \hline
13&6&{1,8}\
13&7&{2,8}\ \hline
14&7&{1,8}
\end{array}
]

Each listed pair is separated by ({0,q}), and all other intersections have size at most (1). By cyclic symmetry, (A) and (B) hold for all row pairs.

Thus, for every (n\ge 8), there are cyclic matrices satisfying exactly the two allowed facts and having all row sums equal to (4). Therefore the desired contradiction is impossible from (A) and (B) alone.

---

## 4. Remaining unresolved configurations and extra geometric input

The cyclic-matrix method leaves many (4)-regular patterns alive. The simplest exact survivor families are the circulant ones above:

[
\boxed{
S_i={i+1,i+2,i+5,i+7}\pmod 8
}
]

and, for (n\ge 9),

[
\boxed{
S_i={i+1,i+2,i+4,i+8}\pmod n.
}
]

These satisfy every forbidden submatrix rule derived from (A) and (B). Hence they are genuine obstructions to an ((A)+(B))-only proof.

However, these particular circulant patterns are not automatically geometrically realizable. In fact, they contain the metric condition

[
i+1,i+2\in S_i\quad\text{for every }i,
]

so a geometric realization would force

[
|p_i p_{i+1}|=|p_i p_{i+2}|
\quad\text{for every }i.
]

Let (s_i=|p_ip_{i+1}|) and let (\theta_{i+1}) be the interior angle at (p_{i+1}). In triangle (p_ip_{i+1}p_{i+2}),

[
|p_ip_{i+2}|^2
=s_i^2+s_{i+1}^2-2s_is_{i+1}\cos\theta_{i+1}.
]

If (|p_ip_{i+2}|=s_i), then

[
s_i^2=s_i^2+s_{i+1}^2-2s_is_{i+1}\cos\theta_{i+1},
]

so

[
\cos\theta_{i+1}=\frac{s_{i+1}}{2s_i}>0.
]

Hence every interior angle would be acute. That is impossible for a convex (n)-gon with (n\ge 4), since the sum of the interior angles is

[
(n-2)\pi,
]

whose average is at least (\pi/2) for (n\ge 4), and strictly larger for (n>4). This argument uses additional metric geometry, not merely (A) and (B).

A more robust unresolved-by-((A)+(B)) pattern avoids that local acute-angle obstruction. For example, for (n\ge 35), set

[
\boxed{
S_i={i+1,\ i+4,\ i+10,\ i+18}\pmod n.
}
]

The positive differences among ({1,4,10,18}) are

[
3,6,8,9,14,17,
]

all distinct, and for (n\ge 35) their negatives are also distinct modulo (n). Hence any two rows intersect in at most one column. Thus (A) holds and (B) is vacuous. This exact (0)-(1) pattern has every row sum (4), no forbidden (2\times 3), no forbidden noncrossing (2\times 2), and no forbidden (3\times 2).

To eliminate such patterns one must use geometric information not encoded by (A) and (B), for example:

[
\text{for each row }i,\text{ the four marked vertices must lie on one Euclidean circle centered at }p_i,
]

so the perpendicular bisectors of all six chords among those four vertices must concur at the vertex (p_i). That row-wise metric/concurrency constraint is absent from the cyclic-matrix axioms.
