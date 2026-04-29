## 1. Fragile-cover lemma

Let (V) be the vertex set. For a surviving vertex (u) and a radius (\rho), write

[
C_P(u,\rho)={v\in V\setminus{u}: |p_v-p_u|=\rho},\qquad c_P(u,\rho)=|C_P(u,\rho)|.
]

Thus

[
m_u(P)=\max_\rho c_P(u,\rho).
]

Fix two distinct vertices (x,u). After deleting (x), the distances from (u) to all other surviving vertices do not change; one entry is merely removed from the distance multiset of (u). Hence

[
c_{P-x}(u,\rho)=
\begin{cases}
c_P(u,\rho)-1,& x\in C_P(u,\rho),\
c_P(u,\rho),& x\notin C_P(u,\rho).
\end{cases}
]

The maximum may shift to another radius, but the following exact characterization handles that.

### Claim

Assume (P) is bad. For (x\neq u), the vertex (u) is not bad in (P-x), i.e.

[
m_u(P-x)\le 3,
]

if and only if (u) is fragile in (P) and (x) lies in the unique four-cohort of (u).

### Proof of the claim

Suppose first that (m_u(P-x)\le 3). Since (P) is bad, (m_u(P)\ge 4). Let (\rho) be any radius with (c_P(u,\rho)\ge 4).

If (x\notin C_P(u,\rho)), then deletion of (x) does not affect that radius, so

[
c_{P-x}(u,\rho)=c_P(u,\rho)\ge 4,
]

contradicting (m_u(P-x)\le 3). Therefore every radius of multiplicity at least (4) must be the single radius

[
\rho=|p_x-p_u|.
]

Moreover, at that radius we must have (c_P(u,\rho)=4), because if (c_P(u,\rho)\ge 5), then after deleting (x) the same radius would still have multiplicity at least (4). Thus (m_u(P)=4), and the radius (|p_x-p_u|) is the unique radius with multiplicity (4). Therefore (u) is fragile, and (x) belongs to its unique four-cohort.

Conversely, if (u) is fragile and (x\in S_u), where (S_u) is the unique four-cohort of (u), then deletion of (x) reduces that unique cohort from size (4) to size (3), while every other radius already had multiplicity at most (3). Hence (m_u(P-x)\le 3).

This proves the claim. (\square)

Now let (v) be any vertex of a minimal bad polygon (P). By minimality, (P-v) is not bad. Therefore some surviving vertex (u\neq v) satisfies

[
m_u(P-v)\le 3.
]

Since (P) itself is bad, the claim applies: (u) is fragile in (P), and (v) lies in the unique four-cohort of (u).

Thus every vertex (v) is contained in the unique four-cohort of at least one fragile center (u). This proves the fragile-cover lemma.

The minimality assumption is used exactly once: to assert that for each deleted vertex (v), the polygon (P-v) is not bad, so some surviving vertex loses badness. The rest is a row-wise deletion characterization. In particular, the proof does not assume that deleting (v) preserves the value of (m) for other vertices; it explicitly allows the maximizing radius to shift.

---

## 2. Hypergraph translation

Let (F\subseteq V) be the set of fragile centers. For each (u\in F), let

[
S_u={v\in V\setminus{u}: |p_v-p_u|=r_u}
]

be its unique four-cohort. Then

[
|S_u|=4.
]

The fragile-cover lemma says

[
V=\bigcup_{u\in F} S_u.
]

Thus the fragile centers define a pointed (4)-uniform hypergraph

[
H={(u;S_u):u\in F}.
]

Let

[
d(v)=|{u\in F:v\in S_u}|
]

be the number of fragile cohorts covering (v). The cover lemma gives

[
d(v)\ge 1\qquad\text{for every }v\in V.
]

Counting incidences,

[
\sum_{v\in V}d(v)=\sum_{u\in F}|S_u|=4|F|.
]

Hence

[
|F|\ge \frac n4.
]

So every minimal bad polygon has at least (n/4) fragile centers.

---

## 3. Row-intersection bounds

For distinct fragile centers (u,w), the two cohort circles

[
\Gamma_u={x:|x-p_u|=r_u},\qquad \Gamma_w={x:|x-p_w|=r_w}
]

are distinct circles. Two distinct circles meet in at most two points, so

[
|S_u\cap S_w|\le 2.
]

If (|S_u\cap S_w|=2), say

[
S_u\cap S_w={a,b},
]

then both (u) and (w) are equidistant from (a) and (b). Thus (p_u,p_w) both lie on the perpendicular bisector of (p_ap_b). By the convex-position crossing lemma, the pair ({u,w}) separates the pair ({a,b}) in the cyclic order of the polygon.

So every double intersection creates an alternating configuration

[
u,\ a,\ w,\ b
]

up to reversal and relabeling.

There is also a useful pair-codegree bound. Fix two vertices (a,b). If both (a,b) lie in (S_u), then (p_u) lies on the perpendicular bisector of (p_ap_b). Since a strictly convex polygon has no three collinear vertices, at most two vertices of (P) can lie on that line. Hence a fixed pair ({a,b}) can occur together in at most two fragile cohorts.

---

## 4. Forced overlap counting

Let

[
O=\sum_{{u,w}\subseteq F}|S_u\cap S_w|
]

be the total row-overlap count. Double-counting triples ((v,u,w)) with (v\in S_u\cap S_w) gives

[
O=\sum_{v\in V}\binom{d(v)}2.
]

Write

[
4|F|=qn+s,\qquad 0\le s<n.
]

Since (x\mapsto \binom{x}{2}) is convex on the nonnegative integers, the minimum possible value of (O) occurs when the cover degrees (d(v)) are as equal as possible. Therefore

[
O\ge (n-s)\binom q2+s\binom{q+1}{2}.
]

Some immediate consequences:

[
|F|\ge \frac n4.
]

If (|F|>n/4), then (O>0), so some two fragile cohorts overlap.

If every vertex is fragile, so (|F|=n), then

[
O\ge n\binom 42=6n.
]

Because every pair of rows intersects in at most two vertices, the number of intersecting pairs of fragile cohorts is at least

[
\left\lceil \frac O2\right\rceil.
]

In particular, if all vertices are fragile, at least (3n) pairs of fragile centers have nonempty cohort intersection.

However, this counting does **not** force a pair of rows to share two vertices. All overlap could, in principle, be made of single intersections. Therefore the crossing lemma alone does not automatically activate.

---

## 5. Forced directed cycle among fragile centers

Now restrict the hypergraph to fragile centers themselves. Define a directed graph (D) on (F) by

[
u\to w \quad\Longleftrightarrow\quad w\in S_u.
]

Since every vertex of (P), in particular every fragile center, is covered by some fragile cohort, every (w\in F) has indegree at least (1) in (D). Therefore (D) contains a directed cycle.

Choose a shortest directed cycle

[
u_0\to u_1\to \cdots \to u_{k-1}\to u_0.
]

Then this cycle is chordless inside (F): if (u_i\to u_j) with (j\not\equiv i+1\pmod k), then following the edge (u_i\to u_j) and then the original cycle from (u_j) back to (u_i) gives a shorter directed cycle, contradiction.

Thus every minimal bad polygon forces a chordless fragile-dependency cycle

[
u_0\to u_1\to \cdots \to u_{k-1}\to u_0,
]

with

[
u_{i+1}\in S_{u_i}
]

and no other cohort-containment relations among those cycle vertices.

This is a genuine structural consequence of minimality plus the fragile-cover lemma.

---

## 6. Why the stated stage-two ingredients do not yet force a contradiction

The cover lemma, the row-intersection bound, and the crossing lemma are strong, but they are not by themselves contradictory.

Here is an abstract pointed (4)-uniform hypergraph showing the obstruction. Let the vertex set be (\mathbb Z_{13}), and define

[
S_i={i+2,\ i+3,\ i+5,\ i+11}\pmod{13}.
]

Then:

[
|S_i|=4,
]

and

[
i\notin S_i.
]

Every vertex lies in exactly four of the sets (S_i). Also, for distinct (i,j),

[
|S_i\cap S_j|=1.
]

Indeed, the difference set

[
{2,3,5,11}
]

has every nonzero residue modulo (13) as a difference exactly once. Thus every pair of rows intersects in exactly one point. The cover condition holds perfectly, but no two rows share two vertices, so the crossing lemma never fires.

This does not prove that such a hypergraph is geometrically realizable by fragile cohorts of a strictly convex polygon. It shows that the purely hypergraph-theoretic constraints obtained so far are insufficient to force contradiction.

There is also a small geometric warning example. Take

[
u=(0,0),\qquad w=(1,0),
]

and the six further points

[
a=(0,1),\quad b=\left(-\frac12,\frac{\sqrt3}{2}\right),\quad c=\left(-\frac{\sqrt3}{2},\frac12\right),
]

[
d=\left(1+\frac{\sqrt3}{2},\frac12\right),\quad e=\left(\frac32,\frac{\sqrt3}{2}\right),\quad f=(1,1).
]

In cyclic order,

[
c,\ u,\ w,\ d,\ e,\ f,\ a,\ b
]

these form a strictly convex octagon. The point (u) has exactly four vertices at distance (1):

[
S_u={w,a,b,c},
]

and (w) has exactly four vertices at distance (1):

[
S_w={u,d,e,f}.
]

Both (u) and (w) are fragile centers, and their two four-cohorts cover all eight vertices. The two cohorts are disjoint, so the crossing lemma is again silent. This octagon is not bad, but it demonstrates that a convex fragile-cover pattern itself need not be contradictory.

Therefore, a full contradiction for minimal bad polygons needs an additional geometric ingredient beyond the fragile-cover lemma plus the double-intersection crossing rule. The strongest forced conclusions from those ingredients are:

[
|F|\ge \frac n4,
]

the fragile cohorts cover (V),

[
|S_u\cap S_w|\le 2,
]

double intersections are cyclically alternating, and the fragile-center dependency digraph contains a chordless directed cycle. These are substantial structural restrictions, but they do not alone rule out a minimal bad polygon.
