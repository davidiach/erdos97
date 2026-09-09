# Stronger metric control: every rich neighborhood is itself a convex planar configuration

9 September 2026. Written proof and exact certificates; independent review pending.
No unrestricted proof or counterexample to Erdős #97 is claimed.

## Theorem

For every integer k >= 4 there is a finite rational metric (X,d), together with
a cyclic order, with all of the following properties.

1. Every vertex has at least k witnesses at the same radius 1. Every other
   positive-distance fiber at every vertex is a singleton.
2. All triangle inequalities and both cyclic Kalmanson inequalities are strict.
   All three Ptolemy inequalities hold at every quadruple.
3. Any two distance fibers at distinct centers, allowing different radii,
   intersect in at most one label. All ordinary pair-sharing and same-side
   pair-capacity restrictions therefore hold.
4. For every vertex p, the *whole* metric subspace consisting of p and all its
   unit-distance witnesses has an exact strictly convex planar realization in
   the induced cyclic order. This includes all distances between those witnesses,
   not just the spokes from p. In particular, all Ptolemy equalities forced by
   four concyclic witnesses and all planar equalities internal to that star hold.
5. The full metric has no planar Euclidean realization.

The coordinate charts in item 4 are separate charts for different stars. They
are not claimed to fit together. The result therefore rules out replacing
that global compatibility requirement by this particular combination of
metric inequalities, incidence caps, and one-center geometric realizability.
It does not rule out a proof using additional relations between centers.

Unlike the first control in `proofs.md`, Ptolemy inequalities here cannot all
be strict: the equalities required by actual witness circles are deliberately
preserved. The first control remains a valid, but weaker, obstruction to a
metric-inequality-only argument.

## 1. The incidence rectangle

Use Sections 1.1--1.2 of `proofs.md`. They give a finite rational point-line
configuration of minimum incidence k on both sides, with no two points on two
retained lines and no two lines sharing two points. A rational projectivity
and coordinate choice give distinct, increasingly ordered alpha_i and x_j,
and a rational matrix

    B_ij = alpha_i*x_j + beta_i + y_j,

whose zeros are precisely the incidences and which satisfies

    B_ij+B_hl-B_il-B_hj
      = (alpha_h-alpha_i)(x_l-x_j) > 0   (i<h, j<l).       (1)

Let the two sorts of labels have sizes a and b; put n=a+b. The cyclic order is
all line labels followed by all point labels.

## 2. Rational circle metrics within the blocks

Independently in each block, assign its index j=0,...,s-1 the point

    u_j = (cos(theta_j), sin(theta_j)),
    theta_j = 4 arctan((j+1)/L),    L=10 n^2.

These are rational unit-circle points:

    cos(theta_j) = (L^4-6 L^2(j+1)^2+(j+1)^4)/(L^2+(j+1)^2)^2,
    sin(theta_j) = 4L(j+1)(L^2-(j+1)^2)/(L^2+(j+1)^2)^2.

For i<j the distance is the positive rational number

    c_ij = 4L(j-i)(L^2+(i+1)(j+1)) /
           [(L^2+(i+1)^2)(L^2+(j+1)^2)].                 (2)

The whole arc has angular width less than 4n/L, and all within-block distances
are less than 1/2. Within each block, triangles are nondegenerate, Kalmanson
inequalities are strict, and cyclic Ptolemy is an equality. The other two
Ptolemy inequalities are strict. These facts follow directly from the actual
unit-circle realization.

There are no repeated distances within any one row of a block. Distances on
each side of the center are strictly monotone. A tie from opposite sides,
using integer indices a=s-p, s, c=s+q, would require

    arctan((s-p)/L)+arctan((s+q)/L)=2 arctan(s/L).

The angles lie in a small positive interval, so the tangent addition formula
has no branch ambiguity and implies

    (q-p)(L^2+s^2)=2spq.                                (3)

Here p,q>0 and s,p,q<n. The right side divided by L^2+s^2 lies strictly between
zero and one, whereas q-p is an integer. Thus (3) is impossible.

## 3. Complete the cross distances

Initially set every cross distance to

    d(i,j)=1+epsilon B_ij,

where epsilon is a sufficiently small positive rational. Incidences then have
unit distance. The within-block entries remain (2).

Here is a complete finite-margin argument for choosing epsilon. Let m>0 be the
smallest within-block distance, H<1/2 the largest, delta>0 the smallest
increase of a longer within-block chord over either shorter chord of an
ordered triple, and T>0 the smallest of all within-block triangle margins.
All these numbers are rational and positive. Write

    U=max |epsilon B_ij|.

Choose U so small that

    2U < min(m,delta),
    3HU < T,
    4U+2U^2 < m^2,
    2(1-U)>2H,    2(1-U)^2>H^2.

Mixed triangles are strict because their two cross sides differ by at most
2U and sum to at least 2(1-U). A Kalmanson margin with three labels in one
block is at least delta-2U. With two labels in each block, one margin is
epsilon times (1), and the other is at least 2(1-U)-2H.

For Ptolemy with three labels in one block, the unperturbed margins are
within-block triangle margins, and the perturbation of a margin is at most
3HU. With two labels in each block, the product A of the two within-block
distances is between m^2 and H^2. The difference of the two cross products
has absolute value at most 4U+2U^2, and their sum is at least 2(1-U)^2. Hence
all three mixed Ptolemy inequalities are strict. Quadruples inside one block
retain the circle equalities already established.

Finally, make a further arbitrarily small rational perturbation of each
*nonincidence* cross entry, leaving incidence entries equal to 1. All mixed
inequalities are strict on a finite set of tuples, so there is an open
neighborhood in which they remain strict. Avoiding the finitely many entry
coincidence hyperplanes makes every nonunit cross entry globally distinct
and unequal to 1. This may also be done with one sufficiently small rational
eta times distinct integer codes for those entries: first protect the minimum
nonzero gap among distinct old entry values, then split ties using the codes.
Cross distances remain greater than 1/2, so cannot meet any within-block value.

Every row now has just one nonsingleton fiber: its prescribed unit incidence
fiber. These fibers are linear by the point-line incidence construction.
This proves items 1--3, including the claim about all radii, not only radius 1.

## 4. Realizing every rich star, and rejecting a global realization

Fix a center p in one block. Place it at the origin and put all its unit
witnesses at their unit-circle coordinates u_j in the other block. All center
spokes are 1, and all witness-to-witness distances are exactly (2). The circle
arc has width less than pi. The origin is strictly exposed on the opposite
side, and each circle point has a strictly supporting circle tangent. Thus
these finitely many points are in strict convex position, in the order p
followed by the increasing witness indices. This is exactly the cyclic order
induced from the two label blocks. Item 4 follows for every center and its
entire rich fiber. There are no other rich radii.

For a hypothetical global planar realization, the whole point-label block
has its prescribed unit-circle distance matrix. Three of its vertices are
noncollinear, so those three positions fix a congruence of the entire block:
distances to three noncollinear points determine every other point uniquely.
Every triple in this block has the same circle center and circumradius 1.
Each line-label vertex has at least three unit-distance witnesses in this
block, and must therefore be that same circle center. Distinct line-label
vertices would coincide, contradicting their positive within-block distances.
There are at least two line labels. This proves item 5 and the theorem.

## 5. The explicit 138-label control

The delivered instance uses the 74-line/64-point incidence configuration from
the first metric control. It uses L=1000, epsilon=10^(-8), eta=10^(-60), with
code 64*i+j+1 for nonincident line i and point j (local point index 0..63).
The exact finite checks verify the margins, uniqueness, and equations directly;
the larger L from the arbitrary-k existence proof is not needed here.

Every nonunit distance in every row is distinct. The unit-degree distribution
is 52 vertices at 4, 20 at 5, 20 at 6, 12 at 7, and 34 at 8. All 138 rich stars
have exact local planar coordinates. The primary verifier checks 2,800 local
squared-distance identities, 4,678 strict supporting-half-plane signs, and
3,252 witness-quadruple Ptolemy equalities. The separate oracle reconstructs
all 19,044 matrix entries and checks 5,148 local ordered-triple orientations.

The exhaustive C++/GMP checker verifies 1,285,608 strict triangle inequalities,
28,926,180 strict Kalmanson inequalities, and all 43,389,270 Ptolemy
inequalities. Precisely 1,786,002 of the latter are equalities: one for each
quadruple wholly within one of the two circle blocks. All other Ptolemy
inequalities are strict. A positive exact Gram determinant at labels
0,1,74,75, independently checked using a Cayley--Menger determinant, rejects
global planar realizability.

## 6. What the scalar turn certificate does, and does not, add

The same explicit control also admits positive rational normalized turn values

    t_i = 2*tau_i/pi,    sum_i t_i=4,

satisfying every inequality of the repository's `turn-inequality-lemma.md`
for every pair of equal-distance witnesses. The minimum t_i is 1/83; every
required normalized interval sum is at least 84/83. The integer-matrix checker
verifies all 4,032 such inequalities directly. The first metric control admits
the same vector and passes all 8,686 pair inequalities over its 2,465 repeated
fibers. The vector is a feasible exact certificate, not a certified optimum.

These are only scalar *necessary* constraints. They are not asserted to be
actual turning angles compatible with all distances or local charts. Indeed,
the metric's three consecutive line labels 0,1,2 would force the exterior
turn at 1, in a planar convex realization, to be

    2[arctan(3/1000)-arctan(1/1000)] < 1/250.

The supplied t_1=1/83 instead gives tau_1=pi/166 > 3/166 > 1/250.
This explicitly prevents interpreting the scalar certificate as a compatible
Euclidean angle assignment. Relations that connect different stars, or connect
turns to actual neighboring side lengths, remain available to a proof. The
result excludes only the precise relaxation stated here.
