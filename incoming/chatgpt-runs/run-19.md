## 1. Convex-position crossing lemma

**Lemma (crossing lemma).**
Let (P={p_1,\dots,p_n}) be the vertices of a strictly convex polygon in cyclic order. Suppose (i\ne k), and suppose two distinct indices (a,b) satisfy

[
a,b\in S_i\cap S_k.
]

Then the four indices (i,k,a,b) are distinct, and in the cyclic order the pair ({i,k}) separates the pair ({a,b}). Equivalently, the chord (p_i p_k) crosses the chord (p_a p_b).

**Proof.**
Since (a,b\in S_i), neither (a) nor (b) equals (i). Since (a,b\in S_k), neither equals (k). Thus (i,k,a,b) are distinct.

Let (C_i) be the circle centered at (p_i) with radius (r_i), and let (C_k) be the circle centered at (p_k) with radius (r_k). The points (p_a,p_b) lie on both circles.

For any common point (x\in C_i\cap C_k),

[
|x-p_i|^2-r_i^2=0,\qquad |x-p_k|^2-r_k^2=0.
]

Subtracting gives

[
|x-p_i|^2-|x-p_k|^2=r_i^2-r_k^2,
]

which is the equation of a line perpendicular to (p_i p_k). This line is the radical axis of the two circles. Hence (p_a) and (p_b) lie on a line (L) perpendicular to the line (\ell=p_i p_k).

Let

[
q=L\cap \ell.
]

Because (L) is a chord of the circle centered at (p_i), and the perpendicular from the center (p_i) to a chord bisects that chord, (q) is the midpoint of (p_a p_b). Thus (p_a) and (p_b) are reflections of one another across the line (\ell=p_i p_k). In particular, (p_a) and (p_b) lie on opposite sides of the line (p_i p_k), and (q) lies in the open segment (p_a p_b).

It remains to prove that (q) lies in the open segment (p_i p_k). Suppose not.

If (q=p_i), then (p_i) lies in the open segment (p_a p_b), contradicting strict convexity, because a vertex of a strictly convex polygon cannot lie on the segment between two other vertices. Similarly (q=p_k) is impossible.

Now suppose (q) lies on the line (p_i p_k) but outside the segment (p_i p_k). If (q) is beyond (p_i), then (p_i) lies in the open segment (q p_k). Since (q) lies in the open segment (p_a p_b), the point (p_i) lies in the interior of the triangle

[
\triangle p_k p_a p_b.
]

That contradicts strict convexity: every vertex of a strictly convex polygon is an extreme point of the convex hull. The same argument applies if (q) lies beyond (p_k).

This is the exact step where strict convexity is invoked: it rules out the possibility that (p_i) or (p_k) lies in the convex hull of the other three points.

Therefore

[
q\in (p_i p_k)\cap (p_a p_b),
]

so the two chords cross in their interiors. For four vertices of a strictly convex polygon, two chords cross in their interiors exactly when their endpoints alternate in the cyclic order. Hence ({i,k}) separates ({a,b}). (\square)

---

## 2. The exact theorem proved

The full contradiction does **not** follow from facts (A) and (B) alone. In fact, there are cyclic (0)-(1) matrices satisfying all consequences of (A) and (B) with every row sum at least (4).

Here is the strongest matrix theorem I can prove from (A) and (B).

**Theorem.**
Let (M) be an (n\times n) cyclically indexed (0)-(1) matrix with zero diagonal, satisfying:

1. for distinct rows (i,k),

[
|S_i\cap S_k|\le 2;
]

2. if (|S_i\cap S_k|=2), say (S_i\cap S_k={a,b}), then ({i,k}) separates ({a,b}) in the cyclic order.

Let

[
s_i=|S_i|,\qquad m=\sum_i s_i.
]

Then

[
\boxed{\sum_i \binom{s_i}{2}\le n(n-2)}
]

and therefore

[
\boxed{m\le \frac n2\left(1+\sqrt{8n-15}\right)}.
]

In particular, such a matrix cannot have all row sums at least (4) unless

[
n\ge 8.
]

This lower bound (n\ge 8) is sharp at the level of the cyclic matrix axioms: there is an (8\times 8) example with every row sum equal to (4).

Moreover, (A) and (B) cannot even force a constant upper bound on row sums: for every prime (q\ge 5), there is a cyclic matrix with (n=q^2) rows and columns, every row sum equal to (q), and every pair of rows intersecting in at most one column. For those matrices, condition (B) is vacuous.

Thus any genuine geometric contradiction would require additional metric input beyond (A) and (B).

---

## 3. Cyclic-matrix and discharging argument

Write (S_i={j:M_{ij}=1}). All indices are taken cyclically.

### Forbidden submatrices

The crossing lemma gives the following forbidden (0)-(1) patterns.

First, by (A), no two rows may share three columns. Thus the pattern

[
\begin{array}{c|ccc}
& a&b&c\ \hline
i&1&1&1\
k&1&1&1
\end{array}
]

is forbidden for (i\ne k).

Second, a (2\times 2) all-one submatrix is allowed only in the alternating cyclic position. If two rows (i,k) share two columns (a,b), then the cyclic order must alternate:

[
i,\ a,\ k,\ b
]

up to reversal and rotation. Therefore the nonalternating pattern

[
\begin{array}{c|cc}
& a&b\ \hline
i&1&1\
k&1&1
\end{array}
]

is forbidden whenever (a,b) lie on the same side of the chord (ik).

In particular, adjacent rows cannot share two columns. If (k=i+1), then the chord (p_i p_k) is a polygon side and cannot cross any chord (p_a p_b). Hence

[
|S_i\cap S_{i+1}|\le 1.
]

Dually, adjacent columns cannot appear together in two rows. If two rows both contain adjacent columns (a,a+1), then the crossing lemma would require some chord (ik) to cross the polygon side (a(a+1)), impossible.

More generally, fix two columns (a,b), and let

[
T_{ab}={i: a,b\in S_i}.
]

If (|T_{ab}|\ge 3), then among three row indices in (T_{ab}), two lie in the same arc of the cycle cut by (a,b). Those two rows do not separate (a,b), contradicting (B). Therefore

[
|T_{ab}|\le 2.
]

If (a,b) are adjacent, then even (|T_{ab}|=2) is impossible, so

[
|T_{ab}|\le 1
]

for adjacent columns.

Thus the exact column-pair capacity is

[
|T_{ab}|\le
\begin{cases}
1,& a,b\text{ adjacent},\
2,& a,b\text{ nonadjacent}.
\end{cases}
]

### Discharging count

For each row (i), put one unit of charge on every unordered pair of (1)’s in that row. Row (i) contributes

[
\binom{s_i}{2}
]

units of charge.

Now discharge each such unit to the corresponding unordered column pair ({a,b}). By the capacity rule above, an adjacent column pair receives at most (1) unit of charge, and a nonadjacent column pair receives at most (2).

There are (n) adjacent unordered column pairs and

[
\binom n2-n
]

nonadjacent unordered column pairs. Hence

[
\sum_i\binom{s_i}{2}
\le
1\cdot n+2\left(\binom n2-n\right).
]

Simplifying,

[
\sum_i\binom{s_i}{2}
\le
n+n(n-1)-2n
===========

n(n-2).
]

This proves

[
\boxed{\sum_i\binom{s_i}{2}\le n(n-2)}.
]

Now let

[
m=\sum_i s_i.
]

Since

[
\sum_i s_i^2
============

2\sum_i\binom{s_i}{2}+\sum_i s_i,
]

we get

[
\sum_i s_i^2
\le
2n(n-2)+m.
]

By Cauchy–Schwarz,

[
m^2
===

\left(\sum_i s_i\right)^2
\le
n\sum_i s_i^2
\le
n\bigl(2n(n-2)+m\bigr).
]

Thus

[
m^2-nm-2n^2(n-2)\le 0.
]

Solving the quadratic inequality gives

[
\boxed{
m\le \frac n2\left(1+\sqrt{8n-15}\right).
}
]

If every row has size at least (4), then (m\ge 4n). Therefore

[
4n\le \frac n2\left(1+\sqrt{8n-15}\right),
]

so

[
8\le 1+\sqrt{8n-15},
]

hence

[
49\le 8n-15,
]

and therefore

[
n\ge 8.
]

So the discharging argument rules out (n\le 7), but it cannot rule out (n=8).

### Sharp cyclic (8\times 8) matrix

Let the indices be (\mathbb Z/8\mathbb Z), and define

[
S_i={i-1,\ i+1,\ i+2,\ i+5}\pmod 8.
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

Every row has size (4). Because the construction is cyclic, it suffices to compare row (0) with row (d). Let

[
D={-1,1,2,5}\pmod 8={7,1,2,5}.
]

Then

[
S_0=D,\qquad S_d=d+D.
]

The intersections are:

[
\begin{array}{c|c}
d&S_0\cap S_d\ \hline
1&{2}\
2&{1,7}\
3&{2,5}\
4&{1,5}\
5&{2,7}\
6&{5,7}\
7&{1}
\end{array}
]

Thus adjacent rows intersect in one column, and every nonadjacent row pair intersects in two columns. For (d=2,3,4,5,6), the two common columns lie on opposite arcs between (0) and (d), so the crossing condition (B) holds.

Therefore this matrix satisfies all consequences of (A) and (B) and has every row sum equal to (4). So no contradiction can be proved from (A) and (B) alone.

This matrix is not claimed to come from an actual convex polygon. In fact, this particular pattern is ruled out by extra metric information: because it has mutual adjacent entries (M_{i,i+1}=M_{i+1,i}=1), a genuine realization would force all (r_i) equal. Then the entries (M_{i,i+2}=1) would force every consecutive triangle (p_i p_{i+1} p_{i+2}) to be equilateral, making every interior angle (60^\circ), impossible for a convex octagon. That argument uses distance symmetry and angle sums, not merely (A) and (B).

### Larger matrix examples: (A) and (B) cannot bound row sums by a constant

Let (q\ge 5) be a prime, and let the row and column index set be

[
I=\mathbb F_q^2.
]

Choose any cyclic order on (I). Define a bijection

[
\phi:I\to \mathbb F_q^2,\qquad \phi(u,v)=(u,\ v+u^2+1).
]

For a row (i=(a,b)), define

[
S_{(a,b)}
=========

{(u,v)\in I:\ \phi(u,v)\text{ lies on the line }y=ax+b}.
]

Equivalently,

[
(u,v)\in S_{(a,b)}
\iff
v+u^2+1=au+b.
]

For each (u\in\mathbb F_q), there is exactly one (v), namely

[
v=au+b-u^2-1.
]

So every row has size (q).

The diagonal is zero: for ((u,v)=(a,b)), the condition would be

[
b+a^2+1=a^2+b,
]

which is impossible in (\mathbb F_q).

Two distinct rows ((a,b)) and ((a',b')) correspond to two affine lines

[
y=ax+b,\qquad y=a'x+b'.
]

If (a=a') and (b\ne b'), the lines are parallel and disjoint. If (a\ne a'), they meet in exactly one point. Since (\phi) is a bijection, the two rows share at most one column.

Hence condition (A) holds strongly:

[
|S_i\cap S_k|\le 1
]

for all (i\ne k). Condition (B) is vacuous. Thus for (n=q^2), we obtain cyclic matrices with every row sum (q=\sqrt n). This proves that (A) and (B) alone cannot force row sums below (4).

---

## 4. Configurations that remain unresolved by (A) and (B)

The following patterns are not eliminated by the crossing lemma/discharging method.

### Unresolved local pattern: alternating (2\times 2)

If the cyclic order is

[
i,\ a,\ k,\ b,
]

then the crossed rectangle

[
\begin{array}{c|cc}
& a&b\ \hline
i&1&1\
k&1&1
\end{array}
]

is allowed by (A) and (B). It is exactly the configuration produced by two circles meeting in two polygon vertices.

### Unresolved saturated (8\times 8) pattern

The cyclic matrix

[
S_i={i-1,\ i+1,\ i+2,\ i+5}\pmod 8
]

has every row sum (4) and satisfies all matrix consequences of (A) and (B). It remains unresolved by the cyclic crossing/discharging argument, although it is ruled out by extra metric constraints.

### Unresolved sparse-intersection families

Any matrix in which every two rows share at most one column automatically satisfies (A) and makes (B) vacuous. The affine-line construction above gives exact examples with row sum (\sqrt n). Such matrices cannot be attacked by any argument that only uses double intersections and the crossing lemma.

Therefore, to prove a genuine geometric contradiction for the original distance problem, one needs additional geometric input beyond (A) and (B), such as constraints relating opposite directed entries (M_{ij}) and (M_{ji}), propagation of equal radii, angle-sum restrictions, or other metric constraints not visible in the cyclic (0)-(1) matrix alone.
