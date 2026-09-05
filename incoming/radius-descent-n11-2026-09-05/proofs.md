# Endpoint-dominated chords and radius descent

Date: 2026-09-05. Base repository commit:
`2aae1262af21a2487e2f534f36968bfa1a3c1002`.

Status: **PAPER_PROOF_CANDIDATE / REVIEW_PENDING**.

This note gives complete paper arguments for restricted geometric statements.
It does not claim a proof or a counterexample to Erdős Problem #97, external
independent review, or a formal verification of the geometry. In particular,
it does not promote the repository's accepted finite-case bound.

The main advance over `docs/sparse-minimum-distance-forest.md` is not just a
forest at more radius levels. The equal-leg two-star lemma below closes the
**whole boundary-independent, locally bounded, two-witness branch**, including
varying radii and one-way witness dependencies. Extraction of such a branch
from an arbitrary hypothetical counterexample remains unproved.

## 1. Definitions and the reusable endpoint-turn inequality

Let P be a strictly convex polygon in counterclockwise boundary order. A set
X of its vertices is **boundary-independent** if no two members are consecutive
vertices of P. All side lengths below refer to the original polygon P, not
the polygon induced by X.

Consider a counterclockwise boundary arc from U to V with at least one
internal vertex. Put d = |UV|. Let

- alpha be the positive counterclockwise angle from the first directed edge
  of the arc to the chord U->V;
- beta be the positive counterclockwise angle from the chord U->V to the
  last directed edge of the arc.

Strict convexity gives 0 < alpha,beta < pi. Their sum sigma = alpha+beta is
the sum of the exterior turns at the internal vertices of this arc.

**Endpoint-turn lemma.** If the last edge of the arc has length at least d,
then

    2 alpha + beta >= pi.                                      (1)

If the first edge has length at least d, then

    alpha + 2 beta >= pi.                                      (2)

### Proof

Use U=(0,0), V=(d,0). Write the last edge as Z->V, of length ell. Its unit
direction is (cos beta, sin beta), and the first edge's unit direction is
(cos alpha, -sin alpha). Because the first edge is a supporting edge of P,
Z lies in its closed left half-plane. Therefore

    d sin(alpha) - ell sin(alpha+beta) >= 0.

If sigma>=pi, (1) is immediate. If sigma<pi and ell>=d, this gives
sin(sigma)<=sin(alpha). Since 0<alpha<sigma<pi, the identity

    sin(sigma)-sin(alpha)
      = 2 cos((sigma+alpha)/2) sin((sigma-alpha)/2)

implies sigma+alpha>=pi. This is (1). Reversing the arc proves (2).
The half-plane inequality may be equality when the arc has only one internal
vertex; the non-strict conclusion is intentional. A one-edge arc is excluded:
alpha=beta=0 in that case, and the conclusion need not hold.

## 2. Equal-leg two-star obstruction

**Theorem.** Let O,A,B be three members of a boundary-independent vertex set
of P. Suppose

    |OA| = |OB| = r > 0.

Then at least one of the four sides of P incident to A or B has length
strictly less than r.

No lower bound is imposed on the sides incident to O. No equality of the
side lengths at A or B is assumed.

### Proof

Reverse A and B if needed so that O,A,B occur in this counterclockwise order.
Assume for contradiction that both sides at A and both sides at B have
length at least r.

Put theta=angle AOB, so 0<theta<pi and the other two angles of triangle OAB
are (pi-theta)/2. Use endpoint-deviation pairs

    (alpha_1,beta_1) on O->A,
    (alpha_2,beta_2) on A->B,
    (alpha_3,beta_3) on B->O.

Every arc has an internal vertex by boundary independence. Comparing the
boundary edge directions with the triangle's chord directions gives the
following *exact* expressions for the exterior turns of P at O,A,B:

    tau_O = pi-theta - alpha_1-beta_3 > 0,
    tau_A = (pi+theta)/2 - beta_1-alpha_2 > 0,
    tau_B = (pi+theta)/2 - beta_2-alpha_3 > 0.                 (3)

The last edge of O->A is incident to A and has length at least |OA|=r.
The first edge of B->O is incident to B and has length at least |BO|=r.
Apply (1) and (2), respectively, and define

    u = 2 alpha_1 + beta_1 - pi >= 0,
    v = alpha_3 + 2 beta_3 - pi >= 0.                         (4)

Combining (3) and (4) yields the exact positive identity

    pi-theta-(alpha_2+beta_2)
       = 2 tau_O + tau_A + tau_B + u + v > 0.                (5)

In particular, the internal turn sigma_2 of the A->B arc satisfies

    0 < sigma_2 < pi-theta < pi.

The first and last edges of this arc are distinct, because A and B are
nonconsecutive. Each has length at least r, so the arc's total length L is
at least 2r. All its edge directions lie in an interval of width sigma_2.
Projection on the bisector of that direction interval gives

    |AB| >= L cos(sigma_2/2)
         >= 2r cos(sigma_2/2)
          > 2r cos((pi-theta)/2)
          = 2r sin(theta/2)
          = |AB|.

The final equality is the chord formula in the isosceles triangle OAB.
This contradiction proves the theorem.

### Exact arithmetic replay and its limitation

`validate.py` expands (5) as a rational coefficient-vector identity after
normalizing pi=1. The multipliers are exactly [2,1,1,1,1] on
[tau_O,tau_A,tau_B,u,v]. This checks the algebraic combination; it does not
replace the geometric justification of the endpoint angles, supporting
half-plane, projection inequality, or strict convexity.

## 3. Radius descent closes the independent-center branch

**Theorem.** Let X be a nonempty boundary-independent set of vertices of P.
For every x in X, suppose a number rho_x>0 is no larger than either side of
P incident to x. It is impossible that every x has two distinct witnesses
in X at distance rho_x.

### Proof

Choose O in X minimizing rho_O. If A and B are its two witnesses, then

    |OA|=|OB|=rho_O.

Both sides incident to A have length at least rho_A>=rho_O, and both sides
incident to B have length at least rho_B>=rho_O. The equal-leg two-star
obstruction contradicts this. No assumption of reciprocal witnesses is used.

Equivalently, for any x with two such witnesses, at least one witness y has
rho_y<rho_x. This strict descent is available at **every** center, not just
at leaves of a same-radius forest. Finiteness then gives the contradiction.

### Alternating-polygon corollary

There is no strictly convex polygon in cyclic order

    E_0,Q_0,E_1,Q_1,...,E_(m-1),Q_(m-1)

such that every E_i has a distance class containing both Q_(i-1),Q_i and at
least two other E-vertices. Indeed, put

    rho_i = |E_i Q_(i-1)| = |E_i Q_i|.

The E-vertices are boundary-independent and satisfy the theorem's local
side-length bounds. Thus the variable-radius alternating subbranch with two other E-witnesses
at every E-center is excluded, without a Hamiltonian, reciprocal, equal-radius, or fixed-step
assumption. No badness conditions at the Q-vertices are required.

### Same-length matching corollary

For any boundary-independent X whose two incident sides at every member
have length at least r, the graph of distance-r edges on X is a matching,
not merely a forest: a vertex of degree two would give the forbidden
same-length two-star. This is a strict strengthening of the minimum-side
corollary in `docs/sparse-minimum-distance-forest.md`.

## 4. A separate variable-length noncrossing forest theorem

**Theorem.** Assign a positive threshold r_x to every member x of a
boundary-independent X, no larger than either incident side of P. Join x,y
when

    |xy| <= min(r_x,r_y).

This full short-chord graph F is a noncrossing forest. Its edges need not
have one common length, and need not be selected equal-distance witnesses.

### Boundary-detour perimeter bound

Suppose Y is a boundary-independent s-vertex subset, s>=3, and every boundary
detour between consecutive members of Y has length at least L>0. Write
sigma_j>0 for each arc's internal turn. If sigma_j<pi, projection gives

    chord_j >= L cos(sigma_j/2) > L(1-sigma_j/pi).

Here cos(t/2)>1-t/pi for 0<t<pi. For sigma_j>=pi the right-hand side is
nonpositive, while the chord is positive, so the same strict lower bound
holds. The internal turns omit the positive turns at Y, hence their sum is
less than 2pi. Summing gives

    per(Y) > L(s-2).                                         (6)

### Crossing edges are impossible

If AC and BD cross, write A,B,C,D in inherited cyclic order and put

    a=|AC|, b=|BD|.

At A,C both incident sides are at least a; at B,D both are at least b.
Each of the four boundary arcs between these vertices has two distinct
endpoint edges whose lengths sum to at least a+b. Apply (6) with L=a+b:

    per(ABCD) > 2(a+b).

On the other hand, if T is the diagonal intersection, the four triangle
inequalities through T give

    per(ABCD) < 2(AT+BT+CT+DT) = 2(a+b),

a contradiction.

### Cycles are impossible

A noncrossing simple cycle on points in strictly convex position follows
the inherited cyclic order: any non-boundary-order edge in a Hamiltonian
cycle of a convex subset separates vertices on both sides and forces a
crossing elsewhere. Let Y be the vertices of such a cycle in F, of length
g>=3. For every cycle edge xy of length d, the P-arc between consecutive
vertices x,y of Y has first and last edges of lengths at least r_x>=d and
r_y>=d. Thus its total length is at least 2d.

If its internal turn sigma<pi, projection gives d>=2d cos(sigma/2), so
sigma>=2pi/3. If sigma>=pi, the same lower bound is automatic. All g arcs
therefore have total internal turn at least g*2pi/3>=2pi. But they omit the
positive turns at Y, so their total is less than 2pi. Contradiction.

The two-star lemma adds that edges of any *one* length in F form a matching.
It does not say the entire variable-length forest is a matching.

## 5. Exact controls and scope boundaries

The companion verifier checks three geometric/algebraic controls.

**A permitted unequal-radius edge.** In the rational strictly convex kite

    P = [(0,0),(5/13,-12/13),(1,0),(5/13,12/13)],
    X = {0,2},  r_0^2=1,  r_2^2=16/13,

the chord 0--2 has length 1 and belongs to F across two distinct thresholds.
This demonstrates why same-radius-only analysis omits valid short edges.
It does not supply two witnesses at every center.

**Boundary independence is necessary.** In a unit square, take X to be all
four vertices and rho_x=1. Every vertex has two witnesses at rho_x and both
incident sides have length rho_x. This does not contradict the theorem:
X is not boundary-independent.

**The local side cap is necessary.** In a regular unit-side hexagon, take X
to be the three alternate vertices and rho_x=sqrt(3). Each has two X
witnesses at that radius, but rho_x exceeds its incident side lengths.
This does not contradict the theorem. The checker represents the coordinates
as (x,sqrt(3)y) with rational x,y and uses exact squared distances.

A further five-label abstract metric explains why the earlier forest-only
descent did not close the branch. Give label i the radius 100+i and outgoing
rows

    0: {3,4}; 1: {0,4}; 2: {0,1}; 3: {1,2}; 4: {2,3}.

Exactly one direction is present on each unordered pair; assign that pair
the source's radius as its symmetric distance. All triangle inequalities
are strict. The threshold graph is {03,04,14}, noncrossing in order
[3,0,4,1,2], and is a forest. Its leaves have downward exports, while vertex
0 has two upward witnesses. Thus a forest plus leaf-only descent is not
enough. The new two-star lemma would exclude an attempted realization with
the required boundary-independent local side bounds at 3 and 4.

This object is not a planar counterexample. Its four-by-four distance Gram
matrix has positive leading principal determinants

    10201,
    320464415/4,
    2227125383159/4,
    3647257216075788.

It is Euclidean of affine dimension four, not two. The example is a control
for the explicitly stated weaker metric/graph conditions, not a survivor
of all repository filters or a full four-witness system.

## 6. The unresolved general bridge

A counterexample to Erdős #97 supplies four witnesses at each center, but it
has not been shown to supply a nonempty boundary-independent X and radii
rho_x such that simultaneously

    (i)   rho_x <= both incident side lengths in the original polygon;
    (ii)  each x retains two rho_x-witnesses inside X.

A rich radius may be larger than one or both incident sides. Passing to
alternate vertices can lose the needed witnesses. Passing to a subpolygon
changes adjacency and may destroy the local side caps. No step here is
licensed to ignore those losses.

The new theorem is a complete obstruction once this branch is reached. It
is **not** an extraction theorem for arbitrary or minimal counterexamples.
The exact 66-point partial construction on main also remains a partial
construction; this note neither completes nor rules out its unrestricted
construction lane.

## 7. Review checklist

A mathematical reviewer should independently check the positive-angle
convention for arcs whose internal turn exceeds pi, the supporting-half-plane
proof of (1), the exact turn identities (3), and the distinct endpoint edges
in the A->B projection. The assumption that O,A,B are pairwise
nonconsecutive is used at all three arcs and must not be dropped.

The finite n=11 replay in `finite-search.md` is independent of these new
geometric lemmas: it uses only the pre-existing incidence, strict Kalmanson,
and strict pi/2 turn-packing constraints.
