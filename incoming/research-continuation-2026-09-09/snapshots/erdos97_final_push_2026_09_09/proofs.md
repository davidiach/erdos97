# Erdős #97: an all-size obstruction to a metric-only proof, and a clustered-family theorem

For the later all-size parallel-parabola closure theorem, see
[`parabola/proof.md`](parabola/proof.md). For the stronger locally planar
metric control, see [`star_metric_theorem.md`](star_metric_theorem.md).

Date: 9 September 2026. Repository baseline: `047d05149382e48b602b292df4b8fc9e2da560bb`.

**Status.** This packet does not resolve Erdős #97. It contains a self-contained
all-size theorem about *abstract metrics*, a restricted theorem about actual
strictly convex polygons, two necessary-order lemmas, and bounded exploratory
records. The written arguments are pending independent mathematical review.
The exact finite checks are not external review or a Lean formalization.

The original target remains: for a finite nonempty strictly convex planar point
set P, find a vertex p such that every positive-distance fiber at p has size at
most three, or exhibit an exact finite counterexample in which every vertex is
rich. Here rich means that some positive-distance fiber has size at least four.

## 1. A proof using only the listed metric inequalities cannot settle the target

### Theorem A — arbitrary multiplicity in strict Kalmanson, strict Ptolemy metrics

For every integer k >= 4 there exists a finite rational metric (X,d), with a
specified cyclic order, such that:

1. Every vertex has at least k other vertices at one common radius R > 0.
2. Every triangle inequality on three distinct vertices is strict.
3. Both ordinary-distance Kalmanson inequalities are strict on every cyclically
   ordered quadruple a,b,c,d:

       d_ac + d_bd > d_ab + d_cd,
       d_ac + d_bd > d_ad + d_bc.

4. All three Ptolemy inequalities are strict on every four distinct vertices;
   for example

       d_ac d_bd < d_ab d_cd + d_ad d_bc.

5. The full radius-R fibers of any two distinct vertices intersect in at most
   one vertex. Thus even the stronger linear-incidence version of the
   two-circle overlap restriction holds.
6. The metric does not embed isometrically in the Euclidean plane.

In particular, selected equal-distance identities, triangle inequalities,
strict Kalmanson inequalities, Ptolemy inequalities, and the two-circle overlap
cap, even imposed *all at once and at every applicable tuple*, do not imply the
conclusion of Erdős #97. This is an obstruction to that relaxation of the
problem, **not a counterexample to the problem with its actual planar geometry**.

### 1.1 A finite point-line configuration of minimum incidence k

Let N = 2(k-1)^2 + 1 and take all integer points in the N-by-N square grid.
Retain every line containing at least k grid points.

Each grid point belongs to at least k retained lines. To see this, choose the
sign of each coordinate direction toward the farther side of the square. In
that quadrant use the k directions

    (1,0), (0,1), (1,1), (1,2), ..., (1,k-2),

with the chosen coordinate signs. Starting at the point, k-1 steps in any one
of these directions change either coordinate by at most (k-1)^2. That is no
more than the available distance to the farther side. The starting point and
these k-1 steps give k grid points on each of k distinct lines.

Both sides of the resulting finite point-line incidence graph therefore have
minimum degree at least k. Two points determine at most one retained line;
two retained lines share at most one retained point.

### 1.2 Put the incidence equations into a strict Monge rectangle

Apply a rational projective transformation whose new line at infinity avoids
all retained points and every intersection of two retained lines. Such a choice
exists: it must avoid only a finite list of projective points. In the resulting
affine chart all retained lines have distinct directions. A further rational
choice of coordinate axes makes none of the lines vertical and gives distinct
x-coordinates to the retained points. Again the forbidden choices form only a
finite list.

Write the transformed points as (x_j,y_j) and the transformed lines as

    y = m_i x + b_i.

Set alpha_i = -m_i, beta_i = -b_i, and

    B_ij = alpha_i x_j + beta_i + y_j.

Then B_ij = 0 exactly at the retained incidences. Order the lines by strictly
increasing alpha_i and the points by strictly increasing x_j. For i < h and
j < l,

    B_ij + B_hl - B_il - B_hj
      = (alpha_h-alpha_i)(x_l-x_j) > 0.                 (A1)

This is the strict rectangle inequality needed below. It is not a claim that
the points or line labels form a convex planar polygon.

### 1.3 Complete the rectangle to a metric

Let a be the number of line labels, b the number of point labels, and n=a+b.
Put all line labels first and all point labels second in the cyclic order.
Choose

    K = 4n+10,    R = 10Kn,    f(s) = Ks-s^2.

Choose a positive rational epsilon so small that

    U := max_ij |epsilon B_ij| < 1/(100R).

Distances within either label block are f(s), where s is the difference of
indices *inside that block*. Cross-block distances are

    d(i,j) = R + epsilon B_ij.

Set d(i,i)=0 and make d symmetric. All entries are rational. Every retained
incidence has distance R. No within-block distance is R, since f(s) < Kn < R.
The full radius-R fibers are exactly the point-line incidence fibers. The
minimum multiplicity and pair-sharing assertions follow immediately.

Here are complete verifications of the inequalities. In all estimates below,
1 <= s < n, f is strictly increasing, and

    K-1 <= f(s) < Kn.

**Triangles within one block.** For positive gaps p,q,

    f(p)+f(q)-f(p+q)=2pq>0.

The other two triangle inequalities are strict by monotonicity and positivity.

**Mixed triangles.** The difference of the two long cross distances has
absolute value at most 2U < K-1. Their sum is at least 2(R-U) > Kn.

**Four labels within one block.** For successive positive gaps p,q,r, direct
expansion gives the two Kalmanson margins

    2q(K-p-q-r),    2pr,

both positive.

**Three labels in one block and one in the other.** Each Kalmanson margin is
a difference of two increasing f-values, plus a difference of two cross
perturbations. It is bounded below by K-2n-2U > 0.

**Two labels in each block.** One Kalmanson inequality is precisely epsilon
times (A1). The other has margin at least 2(R-U)-2Kn > 0.

This proves all triangle and all Kalmanson assertions.

### 1.4 All three Ptolemy inequalities

**Four labels within one block.** With successive gaps p,q,r, the crossing
product f(p+q)f(q+r) exceeds each of the other two products. For comparison with
f(p)f(r), this follows by monotonicity. Its difference from f(p+q+r)f(q) is

    pr [K^2-K(p+2q+r)+2pq+pr+2q^2+2qr] > 0,

because K > 2n > p+2q+r. Finally,

    f(p)f(r)+f(p+q+r)f(q)-f(p+q)f(q+r)
      = 2pqr(K-p-q-r) > 0.

Thus the largest product is less than the sum of the other two, which gives
all three strict Ptolemy inequalities.

**Three labels in one block.** Each product has one cross factor R+e with
|e|<=U and one within-block factor. The unperturbed inequalities are R times
the triangle inequalities for those three within-block distances. Every such
triangle margin is at least 2, so every Ptolemy margin is at least

    2R-3KnU > 0.

**Two labels in each block.** Let A be the product of the two within-block
distances, and C_1,C_2 the two products of cross distances. Then

    (K-1)^2 <= A < (Kn)^2,
    |C_1-C_2| <= 4RU+2U^2 < (K-1)^2,
    C_1+C_2 >= 2(R-U)^2 > (Kn)^2.

Hence A+C_1>C_2, A+C_2>C_1, and C_1+C_2>A. This completes the proof of all
Ptolemy inequalities.

### 1.5 Why this is not planar Euclidean geometry

Take four consecutive line labels 0,1,2,3. For i,j in {1,2,3}, let

    G_ij = [f(i)^2+f(j)^2-f(|i-j|)^2]/2.

This would be the Gram matrix of three displacement vectors from vertex 0 in
any Euclidean realization. Direct expansion gives

    det G = 4(K-3)^2(3K-4)(5K-12) > 0.

Three vectors in the plane have Gram determinant zero. Thus these four
specified distances already prevent a planar Euclidean realization. Theorem A
is proved. Dividing every distance by R makes the common witness radius one
without changing any conclusion.

### 1.6 The explicit 138-label instance

The delivered finite instance uses an 8-by-8 grid rather than the larger
sufficient grid in the general existence proof. Exact enumeration retains 74
lines through at least four of the 64 grid points. Every grid point belongs
to at least four of those lines.

The rational projectivity is

    (x,y) -> ((x+11y)/(10^6+x+97y), y/(10^6+x+97y)).

For a primitive old line Ax+By+C=0, its transformed coefficients are

    U = 10^6 A-C,
    V = 10^6(B-11A)-86C,
    W = C.

Thus alpha=U/V and beta=W/V. Every V is nonzero; all 74 alpha-values and all
64 transformed x-coordinates are distinct. The perturbation B_ij has exact
maximum absolute value 7/1000602. The explicit instance uses epsilon=1,
K=566, R=781100. It satisfies the more general positive-margin bounds displayed
in `grid_metric_certificate.json`; the unnecessarily small epsilon bound from
the existence proof is not needed for this instance.

The common-radius degree distribution is

| Degree | Number of labels |
|---:|---:|
| 4 | 52 |
| 5 | 20 |
| 6 | 20 |
| 7 | 12 |
| 8 | 34 |

There are 784 directed common-radius incidences. The normalized Gram
determinant for labels 0,1,2,3 is exactly 6,052,449,518,192, and the corresponding
Cayley--Menger determinant is 48,419,596,145,536.

In addition to the proof above, `check_metric.cpp` directly checks the entire
finite metric after scaling all entries to integers. It verifies 1,285,608
strict triangle inequalities, 28,926,180 strict Kalmanson inequalities, and
43,389,270 strict Ptolemy inequalities. These are exhaustive checks of this one
metric, not an exhaustive search over Euclidean polygons. `grid_oracle.py`
reconstructs all 19,044 matrix entries using a different line enumeration and
independently computes the Cayley--Menger determinant.

### 1.7 A stronger control preserves all geometry inside each rich star

See `star_metric_theorem.md` for a second arbitrary-k construction. It preserves
all Ptolemy inequalities, including the exact equalities forced by witness
circles, and makes every center together with its entire rich fiber an exact
strictly convex planar configuration. Every nonunit row distance is distinct.
The separate star charts are not globally compatible: the full metric still
has no planar Euclidean realization. The 138-label instance additionally
satisfies the specified scalar turn inequalities, without claiming that those
values match actual geometric angles. This strengthens the relaxation control;
it is still not a counterexample to Erdős #97.

## 2. Three small consecutive clusters cannot support every rich row externally

### Theorem B

Partition the vertices of a strictly convex polygon into three nonempty
consecutive cyclic blocks A,B,C, each of size at most five. It is impossible to
choose four equally distant witnesses at every vertex with all four witnesses
outside the center's own block.

Radii may differ by center. There is no coordinate symmetry, congruence, or
small-perturbation assumption. The same conclusion holds for any three-block partition of a polygon with at
most 16 vertices, without a separate upper bound on each block size (see
Section 2.5). This does not rule out arbitrary 16-point polygons: the
external-witness block condition is an extra hypothesis.

### 2.1 Pair capacity

For two fixed points a,b in one consecutive block, at most one vertex outside
that block can be equidistant from a and b. Two such centers would lie on the
perpendicular bisector of ab and on the same side of the line ab. The nearer
center would lie strictly inside the triangle formed by a,b and the farther
center, contradicting strict convex position.

The same argument says that two centers in one block cannot share two selected
witnesses outside that block. Equivalently, the source chord and common-witness
chord would have to cross, but their endpoints cannot alternate in this order.

### 2.2 Saturation forces three blocks of size five and 2+2 rows

Four witnesses in two target blocks use at least two within-target-block pairs:
2+2 uses two pairs, 3+1 uses three, and 4+0 uses six. Every internal pair is
available to at most one outside center by the pair-capacity argument.

If the three block sizes are s_1,s_2,s_3 and n=s_1+s_2+s_3, then

    2n <= sum_t binom(s_t,2) <= sum_t 2s_t = 2n.

Equality in the second inequality, with 1<=s_t<=5, forces every s_t=5.
Equality in the first forces every selected row to split 2+2, and every one of
the thirty within-block pairs to be used exactly once by an outside center.

### 2.3 A forced five-cycle

Consider the five centers in A and their selected rows in B union C. These
five rows have 20 incidences on ten possible targets. Let d_v be a target's
number of incidences. Any two source rows intersect in at most one target, so

    sum_v d_v = 20,    sum_v binom(d_v,2) <= binom(5,2)=10.

Consequently

    sum_v (d_v-2)^2 = 2 sum_v binom(d_v,2)-20 <= 0.

Every d_v is therefore exactly two.

Make a graph on the five vertices of B by inserting the pair chosen by each
center of A. These are five distinct edges, and every B vertex has degree two.
The graph is a simple five-cycle. Its complementary five pairs are exactly
those owned by centers of C.

### 2.4 The owner graph must instead be an inversion graph

Take a point t in the open boundary edge separating C from A. List the B
vertices as b_0,...,b_4 in boundary order and put d_i=|t-b_i|.

For i<j, the difference |x-b_i|-|x-b_j| is strictly decreasing as x traverses
the complementary boundary from the end of B through C, then t, then A. This
is the strict Kalmanson inequality for b_i,b_j and two such centers. It remains
strict when one of the centers is t: each of the four-point configurations is
strictly convex even though t is on an edge of the larger polygon.

If the pair b_i,b_j is owned by an A center, its zero occurs after t, so
 d_i>d_j. If it is owned by a C center, its zero occurs before t, so d_i<d_j.
Every pair has an owner, and hence all five d_i are distinct.

The A-owned graph thus has edge ij, for i<j, exactly when d_i>d_j: it is the
inversion graph of an ordering of five distinct numbers. Orient every edge
from its smaller to its larger boundary index. This orientation is transitive:
i->j and j->k imply i->k, because d_i>d_j>d_k.

A triangle-free five-cycle cannot have such an orientation. Any directed path
of two edges would force a triangle. Thus at each cycle vertex both edges
would have to point in or both out, making sources and sinks alternate around
an odd cycle. That is impossible. Theorem B is proved.

`blocks.py` independently enumerates all 1,024 simple graphs on five labelled
vertices, all twelve 2-regular ones, and all 120 inversion orders. None of the
twelve five-cycles occurs. The four-cycle from permutation (2,3,0,1) is retained
as a positive control: the inversion-graph restriction does not prohibit all
cycles.

### 2.5 Extension to all three-block external-witness systems through sixteen vertices

Suppose there are s centers in one block and v=n-s possible outside targets.
Their chosen four-element rows intersect pairwise in at most one target.
If d_j counts rows using target j, then

    sum_j d_j=4s,    sum_j binom(d_j,2)<=binom(s,2).

Thus sum_j d_j^2<=s^2+3s. Cauchy--Schwarz gives

    16s^2 <= v(s^2+3s),  hence 16s <= v(s+3).

For n<=16 and s>=6 this is impossible, because

    v(s+3)-16s <= (16-s)(s+3)-16s = 48-s^2-3s < 0.

Consequently every block has size at most five, reducing to Theorem B. At n=16
three such blocks cannot even cover all vertices. This corollary uses no
numerical search. It is a restriction on the external witness locations, not
a new lower bound for arbitrary Erdős #97 counterexamples.

## 3. Two additional median constraints for tripled witness systems

These lemmas apply to the necessary ordinary-distance Kalmanson inequalities;
they do not establish a Euclidean realization.

### Source median

Let p_0,p_1,p_2 lie in one consecutive source block, with selected radii r_i.
Suppose their rows have three distinct pairwise common witnesses w_01,w_02,w_12,
all outside that block. In the complementary boundary order,

    w_02 lies strictly between w_01 and w_12.

For an outside label x define

    F_ij(x)=d(p_i,x)-d(p_j,x)-(r_i-r_j).

For i<j this is strictly decreasing along the complementary order, by
Kalmanson. It vanishes at w_ij and F_02=F_01+F_12. If w_02 were before both
other zeros, both summands there would be positive; if it were after both,
both would be negative. Either possibility contradicts F_02(w_02)=0.

### Target median

Let b_0,b_1,b_2 be a consecutive target block. Suppose its three internal pairs
have distinct outside owners u_01,u_02,u_12, each equidistant from its assigned
pair. Then u_02 lies strictly between u_01 and u_12 in the complementary order.
Use the same proof with

    G_ij(x)=d(x,b_i)-d(x,b_j),    G_02=G_01+G_12.

### Consequence for the recorded three-copy Danzer pools

Each source block has three centers. Each center selects four witnesses from
the same nine targets in three other blocks. Pair capacity gives pairwise row
intersections of size at most one. Inclusion-exclusion then gives

    9 >= |S_0 union S_1 union S_2|
      = 12 - sum_{i<j}|S_i intersection S_j| + |S_0 intersection S_1 intersection S_2|
      >= 9.

Thus the rows cover all nine targets, each pair intersects exactly once, and
there is no triple intersection. The three common targets are distinct, and
the source-median lemma applies.

The inherited three-copy pair budget also forces each selected row to split
2+1+1, and every internal target pair to be used exactly once. The target-median
lemma therefore applies as well.

For each of the nine fixed source pools in the recorded order, exact row
enumeration gives 81^3 = 531,441 ordered row triples, 13,122 satisfying the
pair/cover saturation conditions, and 4,374 satisfying the additional source
median. These are row domains, not realizable point sets.

The subsequent bounded mixed-integer search imposed both source and target
medians and all same-side pair capacities. It obtained five full assignments;
all five have independently checkable exact Kalmanson obstructions (54 stored
certificates in total). The next solver attempt hit its stated time limit
without a candidate. Neither that timeout nor the five exclusions is a complete
exclusion of the tripled family. No new numerical Euclidean optimization was
run on these already-obstructed assignments.

## 4. Other bounded investigations and the remaining original gap

The records retain five alternating linear-program metric searches at sizes
18,24,30,39,48. None produced an all-rich metric. This numerical failure does
not support nonexistence; Theorem A explicitly shows that all-rich metrics in
the relaxation do exist at larger sizes.

The C3 incoming-repair/old-supplier probe examined 26 real numerical circle
intersection branches. Four passed its numerical single-orbit hull test, with
no cross-supplier equality detected among those four under the stored tolerance.
This is not an exact exclusion or an exhaustive repair search.

The same-half-plane product-cycle probe tried 10,000 samples at each orbit count
from three through ten. It found no fully convex cycle. Its failures do not
exclude longer cycles or untested parameters. The stored trial family does not
itself make every vertex four-rich.

The previous one-internally-supported-vertex cap exclusion and its exact inputs
were replayed with all 101 inherited tests passing. This run does **not** extend
that fixed-seed theorem to two internally supported vertices. It also supplies
no reduction of an arbitrary all-rich convex polygon to one of the restricted
families above.

An unrestricted resolution still requires an exact all-rich strictly convex
planar construction, or an argument that forces a good vertex while retaining
arbitrary radii and arbitrary witness assignments. Neither is claimed here.
