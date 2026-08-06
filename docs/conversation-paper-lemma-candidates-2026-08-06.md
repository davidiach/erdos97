# Paper-lemma candidates extracted from the 2026-08-06 conversation

Status: `PAPER_PROOF_CANDIDATES / REVIEW_PENDING`

This file records the strongest self-contained mathematical arguments produced
in the conversation. None is promoted to the repository claims ledger by this
PR. Every statement should be independently checked before being cited as a
lemma, used in a source-of-truth file, or translated into a formal proof.

## 1. Strong connectivity of a selected-witness system

Assume a counterexample exists and choose one with the minimum number of
vertices. At every vertex `p_i`, choose four equidistant witnesses `S_i` and
draw arcs

```text
i -> j  for j in S_i.
```

### Candidate lemma

The selected digraph is strongly connected.

### Proof

If it were not, its condensation DAG would contain a proper sink strongly
connected component `U`. For every `i in U`, every selected witness of `i`
also lies in `U`; otherwise there would be an outgoing condensation edge.
Hence every vertex of `U` still has four equidistant witnesses inside `U`.
Every subset of a strictly convex point set is again in convex position, so `U`
would be a smaller counterexample. Contradiction.

This reduction is elementary and is useful independently of the more delicate
geometric arguments below.

## 2. Affine-circuit rank upper bound

For a selected four-set

```text
S_i = {a,b,c,d}
```

let `lambda_i` be its nonzero affine-circuit row, extended by zero to all
vertices. Thus

```text
sum_j lambda_ij = 0,
sum_j lambda_ij p_j = 0.
```

Because the four support points are cocircular,

```text
sum_j lambda_ij |p_j|^2 = 0.
```

Let `C` be the matrix of these rows, and define

```text
1 = (1,...,1),
X = (x_j),
Y = (y_j),
Q = (x_j^2+y_j^2).
```

Then

```text
C 1 = C X = C Y = C Q = 0.
```

### Candidate lemma

Unless all polygon vertices are cocircular,

```text
rank C <= n - 4.
```

### Proof

If `1,X,Y,Q` were linearly dependent, then

```text
x_j^2+y_j^2 = alpha + beta x_j + gamma y_j
```

for every vertex. Completing squares places all vertices on one circle. Hence,
outside the cocircular case, the four kernel vectors are independent, giving
the rank bound.

If a future argument proves `rank C >= n-3`, the theorem follows immediately.
Indeed the two inequalities are incompatible. Equivalently, if the circuit rows
span the full affine-dependency space, then `Q` is affine in `X,Y`, so all
vertices are cocircular; a positive-radius circle centered at one vertex of a
global circle meets that circle in at most two points.

The missing lower bound is genuinely nontrivial. A concrete cyclic incidence
countermodel to a tempting combinatorial version is recorded in the failed
routes document.

## 3. Stationary six-bisector equilibrium

For each selected row `S_i`, orient every unordered witness pair `a,b` so that
`(p_i,p_a,p_b)` is counterclockwise. Since

```text
|p_i-p_a| = |p_i-p_b|,
```

the vector `2p_i-p_a-p_b` is perpendicular to `p_b-p_a`, with the sign fixed
by convex order. Therefore

```text
2p_i-p_a-p_b = lambda_{i;ab} R(p_b-p_a),
lambda_{i;ab} > 0,
```

where `R` is counterclockwise rotation by `pi/2`.

Summing over the six pairs in `S_i` gives

```text
12p_i - 3 sum_{j in S_i} p_j
  = sum_{a<b in S_i} lambda_{i;ab} R(p_b-p_a).
```

Let the selected-witness Markov chain move uniformly from `i` to the four
vertices of `S_i`, and let `pi` be a stationary distribution. Stationarity says

```text
pi_j = (1/4) sum_{i: j in S_i} pi_i.
```

Multiplying the displayed row identity by `pi_i` and summing over `i` cancels
the left side exactly. Hence

```text
sum_i pi_i sum_{a<b in S_i}
  lambda_{i;ab} R(p_b-p_a) = 0.
```

Rotating back,

```text
sum_i pi_i sum_{a<b in S_i}
  lambda_{i;ab} (p_b-p_a) = 0.
```

### Consequence

The oriented witness chords already have the origin in their positive cone.
No proof can separate all of them by one linear functional. Any successful
global summation must use second-order information: area, curvature,
Kalmanson inequalities, cap nesting, or an equivalent rank mechanism.

## 4. Variable-radius alternating-cycle theorem

Let

```text
rho_1, ..., rho_k, c_k, ..., c_1
```

occur in this cyclic order in a strictly convex polygon.

### Pattern A

Assume

```text
|rho_i c_{k-i}| = |rho_i c_{k-i+1}| = r_i  for 1 <= i < k,
|rho_k c_1| = |rho_k c_k| = r_k.
```

Define perfect matchings

```text
M_1 = {rho_i c_{k-i}: 1 <= i < k} union {rho_k c_k},
M_2 = {rho_i c_{k-i+1}: 1 <= i <= k}.
```

Each row contributes one edge of length `r_i` to each matching, so

```text
length(M_1) = length(M_2).
```

But `M_2` is the antipodal matching of the cyclically ordered `2k` vertices.
It is the unique maximum-length perfect matching: if a maximum matching had two
noncrossing edges on four cyclic vertices, replacing them by the crossing
pair would strictly increase total length by the strict quadrilateral
inequality. Thus every pair of edges in a maximum matching must cross, and the
only perfect matching with that property is the antipodal matching.

Since `M_1 != M_2`,

```text
length(M_1) < length(M_2),
```

contradiction.

### Pattern B

Assume, with `c_{k+1}=c_1`,

```text
|rho_i c_i| = |rho_i c_{i+1}| = r_i.
```

Put

```text
N_k = sum_i |rho_i c_i|,
F_k = sum_{i=1}^{k-1} |rho_i c_{i+1}| + |rho_k c_1|.
```

For every strictly convex configuration in the displayed order,

```text
F_k > N_k.
```

The case `k=2` is the strict quadrilateral inequality. For the induction step,

```text
(F_k-N_k) - (F_{k-1}-N_{k-1})
 = |rho_{k-1}c_k| + |rho_kc_1|
   - |rho_{k-1}c_1| - |rho_kc_k|,
```

which is positive by applying the other strict quadrilateral inequality to

```text
rho_{k-1} < rho_k < c_k < c_1.
```

The row equalities give `F_k=N_k`, contradiction.

### Value

The theorem is cardinality-independent and the radius may vary by row. The
open issue is not the terminal contradiction but extracting one of these
alternating patterns from an arbitrary minimal counterexample.

## 5. Alternating-rectangle lemma

Let eight vertices occur in cyclic order

```text
A < alpha < beta < u < v < C < p < q.
```

Assume

```text
|Au| = |Av|,
|C alpha| = |C beta|,
|p beta| = |pv|,
|qu| = |q alpha|.
```

### Candidate lemma

The eight points cannot be in strictly convex position.

### Proof

Apply the first strict Kalmanson inequality to `A<u<v<p`:

```text
|Av|+|up| > |Au|+|vp|,
```

so

```text
|up|>|vp|.
```

Apply the second strict Kalmanson inequality to `alpha<beta<C<q`:

```text
|alpha C|+|beta q| > |alpha q|+|beta C|,
```

so

```text
|beta q|>|alpha q|.
```

Apply the second strict Kalmanson inequality to `beta<u<p<q`:

```text
|beta p|+|uq| > |beta q|+|up|.
```

Using the last two row equalities gives

```text
|vp|+|alpha q| > |beta q|+|up|,
```

whereas the previous two strict comparisons give the strict reverse.
Contradiction.

## 6. Delaunay forest lemma

Let `T` be any Delaunay triangulation of the convex point set. Suppose a
selected four-set `S_i` lies on a circle centered at the polygon vertex `p_i`.

### Candidate lemma

The induced graph `T[S_i]` is a forest.

### Proof

No three vertices of `S_i` form a Delaunay face. Their circumcircle is the
circle centered at `p_i`, and `p_i` lies strictly inside that circumdisk,
contradicting the empty-circumdisk property.

The graph of a triangulated convex polygon is chordal: every cycle of length at
least four has a chord. Hence every induced subgraph containing a cycle contains
a triangle. Since `T[S_i]` contains no triangle, it contains no cycle.

Thus at most three of the six witness pairs of one selected row are Delaunay
edges. A complete proof would need a global charging argument using this loss.

## 7. Affine-parabola drift theorem

For the standard parabola

```text
p(t) = (t,t^2),
```

four points `p(s_1),...,p(s_4)` at a common distance from `p(t)` are the roots
of

```text
(s-t)^2(1+(s+t)^2)-r^2 = 0.
```

Expanding in `s` gives

```text
s^4 + (1-2t^2)s^2 - 2ts + constant = 0.
```

Vieta yields

```text
sum_j s_j = 0,
sum_j s_j^2 = 4t^2-2,
```

so

```text
(1/4) sum_j s_j^2 = t^2 - 1/2.
```

Choosing a point in the finite set minimizing `t^2` contradicts this identity.

### Affine-invariant form

After an affine transformation, squared Euclidean distance pulls back to a
positive definite quadratic form

```text
Q(u,v) = A u^2 + 2Buv + Cv^2,
AC-B^2 > 0.
```

For `p(t)=(t,t^2)`, Vieta gives a quadratic potential

```text
Phi(t)=t^2+(B/C)t
```

with

```text
(1/4) sum_j Phi(s_j) = Phi(t) - delta,
delta = (AC-B^2)/(2C^2) > 0.
```

Again a minimum of `Phi` is impossible. Thus the candidate theorem holds for
finite subsets of every affine parabola.

## 8. Conic maximum principle

This is the most algebra-heavy candidate in the conversation.

### Ellipse

After rigid normalization,

```text
x^2/a^2 + y^2/b^2 = 1,  a>b>0.
```

Using the unit-circle parameter `z`, the circle centered at an ellipse point
produces a quartic in `z`. The reported Vieta calculation gives

```text
(1/4) sum_{q in S_p} x(q)
  = [a^2/(a^2-b^2)] x(p).
```

The factor is greater than one. Choosing a point maximizing `|x|` gives a
contradiction.

### Hyperbola

On one branch of

```text
x^2/a^2 - y^2/b^2 = 1,
```

the analogous calculation gives

```text
(1/4) sum_{q in S_p} x(q)
  = [a^2/(a^2+b^2)] x(p),
```

with a factor strictly between zero and one. An extremal `x` coordinate on one
branch gives a contradiction.

### Candidate conclusion

A finite set on one connected component of a nondegenerate real conic contains
a non-4-rich point.

The quartic coefficients and Vieta identities require an independent symbolic
rederivation before this should be treated as a theorem.

## 9. Shortest-side two-center injectivity

Let `P` lie in a closed disk `D(O,R)`. Let `A,B,C` be boundary points forming a
nondegenerate non-obtuse triangle containing `O`, and suppose `AB` is a shortest
side. Normalize

```text
A=(-a,0), B=(a,0), O=(0,h), C=(p,q),
0<=h<=q.
```

The circle equations give

```text
a^2+h^2=R^2,
p^2+q^2-2hq=a^2.
```

Suppose distinct `U,W` satisfy

```text
|AU|=|AW|,
|BU|=|BW|.
```

Subtracting the squared equalities gives

```text
U=(xi,t), W=(xi,-t), t>0.
```

Disk containment of the lower point gives

```text
xi^2+(t+h)^2 <= R^2,
|xi| <= D(t):=sqrt(a^2-2ht-t^2),
t<=R-h.
```

Since `AB` is a shortest side,

```text
(a-|p|)^2+q^2 >= 4a^2.
```

Using the circle relation gives

```text
hq >= a(a+|p|).
```

Let

```text
k=(a+|p|)/q.
```

Then `h>=ak` and `a-kt>0`. Strict convexity says `U` is outside triangle
`ABC`. At height `t`, the triangle cross-section is

```text
[-a+t(p+a)/q, a+t(p-a)/q].
```

Therefore

```text
|xi|>a-kt.
```

But

```text
(a-kt)^2-D(t)^2
 = t[2(h-ak)+(1+k^2)t] > 0,
```

so `D(t)<a-kt`, contradicting the upper and lower bounds on `|xi|`.

### Candidate conclusion

The map

```text
X -> (|AX|,|BX|)
```

is injective on the polygon vertices. In particular, each pair of radius cells
at the endpoints of a shortest MEC side contains at most one vertex.

## 10. Fatal-pair uniqueness

Let `p` be fully deletion-robust. Let `U` meet every complete distance class at
`p` in at most one point. Call `{x,y} subset U` fatal if deleting both points
destroys every four-point class at `p`.

### Candidate lemma

There is at most one fatal pair in `binom(U,2)`.

### Proof

If two fatal pairs are disjoint, every rich class must meet both pairs and hence
contain two points of `U`, impossible.

If two fatal pairs overlap, say `{x,y}` and `{x,z}`, singleton deletion
robustness gives a rich class surviving deletion of `x`. Fatality of the first
pair forces that class to contain `y`; fatality of the second forces it to
contain `z`. Again the class contains two points of `U`.

This lemma gives synchronized pair deletions at two robust centers whenever
`|U|>=3`, because each center forbids at most one pair.

## 11. Maximum-concentration blocker forest

Assume minimality supplies, for every vertex `x`, an exact unique-four row
`F_{f(x)}` containing `x`. Choose the assignment `f` maximizing

```text
Phi(f)=sum_c k_c^2,
k_c=|f^{-1}(c)|.
```

If `x in F_c` but `f(x)=d != c`, moving `x` from `d` to `c` changes `Phi` by

```text
2(k_c-k_d+1).
```

Maximality gives

```text
k_d >= k_c+1.
```

Now fix one complete distance class `K` at a deletion-robust apex `A`. A
unique-four row centered away from `A` meets `K` in at most two points. Partition
`K` into assignment blocks

```text
B_c = K ∩ f^{-1}(c).
```

Join `x,y in K` when one lies in the selected row of the other's assigned
blocker. Contract each nonempty block. Direct a cross-block edge from `c` to
`d` when the row at `c` contains a point assigned to `d`. The load `k` strictly
increases along every directed edge.

A two-point block has no outgoing cross-edge, because its row already uses both
allowed points of `K`. A one-point block has outdegree at most one. An undirected
cycle in an acyclic orientation has a source with two outgoing cycle edges,
contradiction. Expanding the two-point blocks cannot create a cycle.

### Candidate conclusion

The selected blocker-interaction graph on `K` is a forest. On four cap points
it forbids at most three of the six pairs. Adding one possible fatal edge at
each of two robust endpoints still leaves a pair that is both synchronized and
reciprocally omitted by its selected blocker rows.

## 12. Shortest-apex strict radius descent

Let `ABC` be a non-obtuse MEC support triangle and let `BC` be a shortest side.
Let `A` be the opposite apex. Suppose distinct strict-cap points `x,y` lie on an
`A`-circle of radius `rho`, and another polygon vertex `c` is equidistant from
`x,y` with radius `sigma`.

Let `M=(x+y)/2`. Both `A` and `c` lie on the perpendicular bisector of `xy`, and
strict convexity places them on opposite sides of the chord. Write

```text
c=A+lambda(M-A), lambda>1.
```

The proposed MEC support calculation shows that reflecting `A` through `M`,

```text
A*=2M-A,
```

puts `A*` outside the enclosing disk. Since `c` remains inside the disk on the
same ray, `lambda<2`.

Write

```text
v=M-A,
u=(x-y)/2,
u perpendicular to v.
```

Then

```text
rho^2 = |v|^2+|u|^2,
sigma^2 = (lambda-1)^2|v|^2+|u|^2.
```

Because `0<lambda-1<1`,

```text
sigma<rho.
```

A power-of-a-point comparison then shows that the two other points of the exact
row centered at `c`, lying on the `A` side of chord `xy`, satisfy

```text
|Az|<rho.
```

This is the strict inward-descent mechanism used in the later `2+2+2` rounds.

## 13. Radial nesting for two concentric classes

Let `O` be a hull vertex, and let two concentric circles centered at `O` have
radii `1` and `k>1`. Suppose a circle centered at another hull vertex `X` takes
a pair from each circle. Rotate so that

```text
O=(0,0), X=(R,0),
p_±=(cos a, ±sin a),
q_±=k(cos c, ±sin c).
```

The proposed convexity and equal-radius analysis gives

```text
R>k cos c>cos a>0,
a>c,
k sin c>sin a,
k cos(a-c)>1.
```

### Candidate radial-nesting lemma

Every other inner-circle polygon vertex has angle strictly between `-c` and
`c`.

### Proof sketch

For an inner point at angle `gamma` with `c<gamma<a`, compare it with the chord
`q_+p_+`. The chord meets the ray `gamma` beyond radius one because

```text
k sin(a-c)-sin(a-gamma)-k sin(gamma-c) > 0,
```

using `k cos(a-c)>1`. Hence the inner point lies in the triangle
`conv{O,q_+,p_+}`.

For `gamma>a`, compare the ray of `p_+` with chord `q_+w`. The relevant
function

```text
F(t)=k cos(a-c+t)-cos t
```

is decreasing and remains positive up to the semicircle endpoint because
`k sin c>sin a`. Thus `p_+` lies in `conv{O,q_+,w}`. Reflection handles the
left side.

### Consequences proposed in the conversation

1. Two distinct bridge shells cannot each take pairs from both concentric
   circles: each inner interval would strictly contain the other.
2. A bridge shell cannot coexist with a shell taking a pair from one circle and
   even one point from the other. The conversation supplied separate angular
   arguments for the two possible radius orders.
3. For two exact shells centered away from a rich apex, at least two vertices
   in the apex's rich-class system lie outside both shells.

These consequences are the proposed analytic closure of the paired two-radius
grid and the source of a second common omission in the sibling joint-deletion
arm. They are the highest-priority candidates for independent review and formal
translation.

## Secondary candidates not expanded here

The round ledger also records the following paper arguments, which should be
recovered from the conversation transcript before any proof attempt:

- tri-apex double-overlap obstruction;
- two interlaced regular-orbit family exclusion;
- common-`T44` reflection-symmetric certifier classification;
- exact `2+2+2` collision fork;
- cap-eight saturated-triangle exclusion;
- cap-nine common-pair and directed-chain normal forms;
- common-omission `4+4` apex-switch dichotomy.

## Promotion standard

A result in this file should move to `docs/claims.md` only after at least one of:

1. independent line-by-line mathematical review;
2. a compact exact certificate and independent verifier;
3. a source-clean formal proof wired to the relevant theorem; or
4. two genuinely independent derivations with every hidden geometric
   assumption made explicit.
