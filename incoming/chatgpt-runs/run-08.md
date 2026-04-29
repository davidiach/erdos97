## 1. Convex-position crossing lemma

Let (C_i) be the circle centered at (p_i) with radius (r_i). Suppose (i\ne k) and

[
S_i\cap S_k={a,b}.
]

Thus (p_a,p_b) lie on both circles (C_i) and (C_k).

**Lemma.** The chord (p_ip_k) crosses the chord (p_ap_b). Equivalently, in the cyclic order of the strictly convex polygon, the pair ({i,k}) separates the pair ({a,b}).

**Proof.** Let (L) be the line through (p_i) and (p_k). Reflection in (L) fixes the two centers (p_i,p_k), hence preserves both circles (C_i,C_k). Since two distinct circles have at most two intersection points and (p_a,p_b) are two distinct common points, reflection in (L) swaps (p_a) and (p_b). Thus (p_a,p_b) are mirror images across (L).

Choose coordinates with

[
p_i=(0,0),\qquad p_k=(d,0),\qquad d>0.
]

By the reflection property,

[
p_a=(x,h),\qquad p_b=(x,-h)
]

for some (h>0). The chord (p_ap_b) is vertical, and its midpoint is (q=(x,0)).

We claim

[
0<x<d.
]

If (x<0), then (q) lies to the left of (p_i), so (p_i) lies on the segment joining (q) to (p_k). Since (q\in p_ap_b), this places (p_i) inside the triangle (\operatorname{conv}{p_a,p_b,p_k}). If (x=0), then (p_i) lies on the segment (p_ap_b). Both are impossible because the vertices of a strictly convex polygon are extreme points and no vertex lies on a segment determined by two other vertices. This is the first exact use of strict convexity.

Similarly, if (x>d), then (p_k\in \operatorname{conv}{p_a,p_b,p_i}), and if (x=d), then (p_k\in p_ap_b). Again this contradicts strict convexity. Hence (0<x<d).

Therefore (q=(x,0)) lies in the relative interior of both segments (p_ip_k) and (p_ap_b). Thus the two chords cross. For vertices in strictly convex position, two chords cross in their interiors exactly when their endpoints alternate in the cyclic order; this uses strict convexity again to exclude boundary or collinearity degeneracies. Hence ({i,k}) separates ({a,b}). (\square)

The important point is that the radical-axis/reflection argument gives the symmetry of (p_a,p_b) across (p_ip_k), while strict convexity forces the radical axis to meet the segment (p_ip_k), not merely its supporting line.

---

## 2. The exact theorem proved here

Call a cyclic (0)-(1) matrix (M) an **AB-matrix** if:

1. (M_{ii}=0);
2. any two rows have at most two common (1)’s;
3. if rows (i,k) have exactly two common (1)’s in columns (a,b), then ({i,k}) separates ({a,b}) cyclically.

Every geometric matrix in the problem is an AB-matrix by Fact (A) and the crossing lemma above.

**Theorem.** Let (d_i=|S_i|). For every AB-matrix,

[
\sum_i \binom{d_i}{2}\le n(n-2).
]

Consequently,

[
\sum_i d_i\le \frac n2\left(1+\sqrt{8n-15}\right).
]

In particular, if every row has size at least (4), then necessarily

[
n\ge 8.
]

This is sharp for the AB-axioms alone: for every (n\ge 8) there exists a cyclic AB-matrix with every row sum equal to (4). Therefore no contradiction for all (n) can be derived from Facts (A) and (B) alone. Any full geometric contradiction would need additional metric input beyond (A) and (B).

---

## 3. Cyclic-matrix / discharging argument

For an unordered column-pair (q={a,b}), define its **codegree**

[
\lambda(q)=|{i:\ a,b\in S_i}|.
]

Equivalently, (\lambda(q)) is the number of rows containing (1)’s in both columns (a,b).

### Forbidden submatrices

The AB-axioms immediately forbid the following.

**F1. No (2\times 3) all-one submatrix.**
This is exactly Fact (A): two rows cannot share three columns.

**F2. No noncrossing (2\times 2) all-one submatrix.**
If rows (i,k) and columns (a,b) form

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

then the cyclic order must alternate:

[
i,\ a,\ k,\ b
]

or

[
i,\ b,\ k,\ a.
]

After rotating so that (i=0<k), this means one of (a,b) must lie in the open arc ((i,k)), and the other must lie in the complementary open arc.

**F3. No (3\times 2) all-one submatrix.**
Indeed, suppose three rows all contain the same two columns (a,b). Those three row-indices lie in the two open arcs determined by (a,b). Two of them must lie in the same arc, so those two rows do not separate (a,b), contradicting F2.

A useful refinement is this:

[
\lambda({a,b})\le
\begin{cases}
1, & a,b \text{ adjacent cyclically},\
2, & a,b \text{ nonadjacent}.
\end{cases}
]

For adjacent (a,b), one of the two arcs between them is empty, so two rows could not possibly separate them.

### Discharging

Put one unit of charge on every unordered pair of (1)’s inside a row. Thus row (i) contributes

[
\binom{d_i}{2}
]

units of charge. Now discharge each such unit to the corresponding unordered column-pair ({a,b}).

The total charge is

[
Q=\sum_i \binom{d_i}{2}.
]

There are (n) adjacent column-pairs, each with capacity at most (1), and

[
\binom n2-n
]

nonadjacent column-pairs, each with capacity at most (2). Therefore

[
Q\le n+2\left(\binom n2-n\right)=n(n-2).
]

So

[
\boxed{\sum_i \binom{d_i}{2}\le n(n-2)}.
]

If every (d_i\ge 4), then

[
\binom{d_i}{2}\ge 6,
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
E=\sum_i d_i.
]

By Cauchy,

[
\sum_i d_i^2\ge \frac{E^2}{n}.
]

Therefore

[
\sum_i \binom{d_i}{2}
=\frac12\left(\sum_i d_i^2-E\right)
\ge \frac12\left(\frac{E^2}{n}-E\right).
]

Combining with the discharging bound gives

[
\frac12\left(\frac{E^2}{n}-E\right)\le n(n-2),
]

so

[
E^2-nE-2n^2(n-2)\le 0.
]

Solving the quadratic inequality,

[
\boxed{E\le \frac n2\left(1+\sqrt{8n-15}\right)}.
]

### Sharpness of the AB-axioms

For (n\ge 8), index rows and columns by (\mathbb Z/n\mathbb Z), and define

[
S_i={i+1,\ i+2,\ i-3,\ i-1}.
]

Every row has size (4), and (i\notin S_i).

Let

[
D={1,2,-3,-1}.
]

Rows (0) and (t) intersect in

[
D\cap (t+D).
]

For (n\ge 11), the only repeated nonzero differences inside (D-D) are (\pm 2). Thus the only two-column intersections are:

[
t=2:\quad {1,-1},
]

and

[
t=n-2:\quad {-3,-1}.
]

In both cases, one common column lies in the open arc ((0,t)), and the other lies in the complementary arc.

For (n=8,9,10), the modular coincidences create a few more two-column intersections, all still crossing:

[
\begin{array}{c|c}
n & \text{two-column intersections for rows }0,t\ \hline
8 &
\begin{array}{l}
t=2:{1,-1}\
t=3:{2,-3}\
t=4:{1,-3}\
t=5:{2,-1}\
t=6:{-3,-1}
\end{array}
[2em]
9 &
\begin{array}{l}
t=2:{1,-1}\
t=4:{1,-3}\
t=5:{2,-3}\
t=7:{-3,-1}
\end{array}
[2em]
10 &
\begin{array}{l}
t=2:{1,-1}\
t=5:{2,-3}\
t=8:{-3,-1}
\end{array}
\end{array}
]

In each listed case, after representing (0<t<n), one of the two shared columns lies between (0) and (t), and the other lies outside. Hence every (2\times 2) all-one submatrix is crossing. Therefore these matrices satisfy (A) and (B), with every row sum equal to (4).

So the AB-axioms alone cannot prove the desired contradiction for (n\ge 8).

---

## 4. Remaining unresolved configurations

The following patterns survive all consequences of (A) and (B). Eliminating them requires additional geometric information, such as the metric fact that all (1)’s in row (i) lie on one circle centered at (p_i).

### U1. A crossing (2\times 2)

If the cyclic order is

[
i,\ a,\ k,\ b,
]

then the submatrix

[
\begin{array}{c|cc}
& a & b\ \hline
i & 1 & 1\
k & 1 & 1
\end{array}
]

is allowed by (B). Geometrically, this corresponds to an orthogonal kite configuration: (p_a,p_b) are mirror images across (p_ip_k), and the two chords cross.

### U2. A pairwise-linear four-row block

The following local pattern has row sums (4), but every pair of rows intersects in only one column, so (B) never activates:

[
\begin{array}{c|cccccccccc}
& a&b&c&d&e&f&g&h&\ell&m\ \hline
r_1&1&1&1&1&0&0&0&0&0&0\
r_2&1&0&0&0&1&1&1&0&0&0\
r_3&0&1&0&0&1&0&0&1&1&0\
r_4&0&0&1&0&0&1&0&1&0&1
\end{array}
]

Facts (A) and (B) do not rule this out. A geometric proof would need to use that each row’s four columns are concyclic with a prescribed center.

### U3. The full (8\times 8) AB-pattern

Using the construction

[
S_i={i+1,i+2,i-3,i-1}
]

modulo (8), one obtains the matrix

[
\begin{array}{c|cccccccc}
&1&2&3&4&5&6&7&8\ \hline
1&0&1&1&0&0&1&0&1\
2&1&0&1&1&0&0&1&0\
3&0&1&0&1&1&0&0&1\
4&1&0&1&0&1&1&0&0\
5&0&1&0&1&0&1&1&0\
6&0&0&1&0&1&0&1&1\
7&1&0&0&1&0&1&0&1\
8&1&1&0&0&1&0&1&0
\end{array}
]

This satisfies every forbidden-submatrix rule derived from (A) and (B), and every row has size (4). The reversed cyclic pattern

[
S_i={i+1,i+3,i-2,i-1}
]

also survives the AB-axioms.

These are not asserted to be geometrically realizable. In fact, to eliminate even this example one must use metric information not present in (A) and (B): in the displayed pattern, each row contains its two cyclic neighbors and also (i+2), which would force all sides equal and every triangle (p_i p_{i+1}p_{i+2}) to be equilateral, impossible for a strictly convex (n)-gon with (n\ge 8). That argument uses the actual distance equalities row-by-row, not just the cyclic crossing rule.

Thus the strongest conclusion from the prescribed matrix axioms is the sharp bound above and the nonexistence for (n\le 7). A full contradiction for all (n), if true, must use additional geometric constraints beyond Facts (A) and (B).
