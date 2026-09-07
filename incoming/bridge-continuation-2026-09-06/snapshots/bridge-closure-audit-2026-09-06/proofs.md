# Audit of proposed closure steps for Erdős Problem #97

**Date:** 6 September 2026.  
**Status:** the unrestricted problem is **not solved in this packet**. This packet contains a short proof of an already established fixed-radius restriction, a local variable-radius descent corollary, and exact counterexamples to three stronger intermediate statements. None is a counterexample to Erdős #97. No independent mathematical review, formalization, or published novelty is claimed.

## 1. Definitions and logical target

Let P be a finite set in strictly convex position. Set

- C_p(r) = {q in P minus {p}: |p-q| = r};
- b_p(r) = #{q in P minus {p}: |p-q| < r};
- M_P(p) = max over positive r of |C_p(r)|.

Erdős #97 asks whether every such nonempty P has some p with M_P(p) <= 3. To disprove it, *every* vertex must have a class of at least four equidistant other vertices. An assigned-radius theorem with b_p(rho_p) <= 2 is only a restriction of this question; the rank condition has not been extracted from an arbitrary counterexample.

A **strict Gabriel edge** pq means that the closed disk with diameter pq contains no other point of P. Boundary points count as blockers. In the verifier, z blocks pq exactly when

    |p-z|^2 + |z-q|^2 <= |p-q|^2.

The disk terminology can be eliminated entirely in favor of this identity.

## 2. Local degree-lifting lemma

**Lemma.** Fix p and r > 0. Assume b_p(r) <= 2 and b_z(r) <= 2 for every z with |p-z| < r. In the strict Gabriel graph G of the entire point set,

    degree_G(p) >= |C_p(r)|.

This lemma itself needs distinct planar points, not convexity.

**Proof.** Let T = {z: 0 < |p-z| < r}. A blocker z of a distance-r edge pq satisfies

    |p-z|^2 + |z-q|^2 <= r^2.

Since neither distance is zero, both are strictly smaller than r. In particular z belongs to T.

First suppose every edge pz for z in T is Gabriel. For each blocked distance-r edge pq choose one blocker z. A single z cannot block two different such edges pq and pq': it would then have three distinct r-short neighbors p,q,q', contrary to b_z(r) <= 2. Replace each blocked r-edge pq by its distinct Gabriel edge pz. Keep each unblocked r-edge unchanged. The replacement edges have length less than r, so cannot coincide with the unchanged r-edges. This is an injection into the Gabriel edges incident to p.

Otherwise, some edge pz with z in T is blocked by w. Then

    |p-w| < |p-z| < r,     |z-w| < |p-z| < r.

Thus T = {z,w}, since |T| <= 2. Each of z,w already has its two r-short neighbors: p and the other member of T. Neither can block a distance-r edge pq, because that would add the third short neighbor q. Every distance-r edge at p is therefore Gabriel in this case. This again proves the inequality. QED.

### Fixed-radius consequence (same scope as the preceding packet)

Suppose b_p(r) <= 2 at every point. Summing the lemma gives

    2 e_r(P) <= 2 |E(G)|.

For convex P, G is noncrossing. Indeed, if Gabriel edges ac and bd crossed in a convex quadrilateral a,b,c,d, some quadrilateral angle would be at least 90 degrees. Its vertex would be on or inside the closed diameter disk of the opposite diagonal, contradicting that diagonal being Gabriel.

A noncrossing graph on n >= 3 vertices in convex position extends to a triangulation, and thus has at most 2n-3 edges. The n=2 case is immediate. Hence

    e_r(P) <= 2n-3.

It follows that not every vertex can have four distance-r neighbors under the fixed-radius two-closer hypothesis. A unit rhombus with angles 60 and 120 degrees attains e_r = 5 = 2n-3 at n=4, so the displayed bound is sharp there.

This is a shorter proof of the base fixed-radius bound from the preceding packet, **not a newly extended scope**. The preceding packet's additional path/cycle penalties are not rederived here and are not required by this argument.

### Local variable-radius consequence

Assign rho_p > 0 with b_p(rho_p) <= 2 for every p. If p is four-rich at rho_p but degree_G(p) <= 3, there is some z with

    |p-z| < rho_p,     rho_z < rho_p.

Otherwise every r-short neighbor z, for r = rho_p, would have b_z(r) <= 2 and the lemma would force degree_G(p) >= 4. Thus one such z has b_z(r) >= 3. Since b_z(rho_z) <= 2, monotonicity of b_z implies rho_z < r.

**This is not a universal descent.** It applies only at rich vertices of Gabriel degree at most three. The strictly smaller-radius vertex may have Gabriel degree at least four, at which point this implication cannot be iterated. Convexity guarantees low-degree vertices somewhere, not on every resulting descent path.

## 3. The direct global Gabriel-capacity extension is false

A tempting attempt is to replace the common r in Section 2 by the individual rho_p and assert

    sum_p |C_p(rho_p)| <= sum_p degree_G(p).

Even assuming b_p(rho_p) <= 2 everywhere and requiring each rho_p to be an actual distance, this inequality is false.

### Exact 15-point construction

Identify pairs with complex numbers, and write

    u(t) = ((1-t^2)/(1+t^2), 2t/(1+t^2)).

Set

    w = u(1/40),
    q_j = w^j for j = 0,...,11,
    a = u(-1/4)/5,
    b = q_11 u(1/4)/5.

Take the points in the following cyclic order:

    p=0, a, q_0, q_1, ..., q_11, b.

All coordinates are rational. Assign

    rho_p = 1,
    rho_a = rho_b = 1/5,
    rho_qj = |w-1| for every j.

The exact verifier checks strict convexity by every supporting-edge half-plane inequality and calculates every assigned distance class. The source p has 12 witnesses and two strictly closer points. The shields a,b each have one witness and no closer point. The ten internal arc vertices each have two witnesses and no closer point; the two arc endpoints each have one witness and no closer point.

Consequently

    sum_p |C_p(rho_p)| = 12 + 2 + 20 + 2 = 36.

The strict Gabriel graph has exactly the following 16 edges:

    p-a, p-b, a-b, a-q_0, b-q_11,
    q_j-q_(j+1) for j=0,...,10.

Therefore

    36 > 2*16 = 32.

This rejects the proposed global injection/count. It does **not** reject every weighted counting strategy, nor an inequality needing the extra assumption that all vertices are four-rich. Most vertices here have only one or two assigned witnesses. In particular 36 is much less than 4n=60; the example is not an Erdős counterexample.

## 4. Deleting a rich Delaunay ear can destroy another vertex's richness

The following ten rational points form a strictly convex polygon:

    p0 = (0,0)
    p1 = (1/100,-1/2000)
    p2 = (-3/400,7/1000)
    p3 = (1,0)
    p4 = u(23/22)
    p5 = u(153/100)
    p6 = u(7/3)
    p7 = (1,0) + u(3/200)
    p8 = (1,0) + u(2/125)
    p9 = (1,0) + u(17/1000).

Their counterclockwise order is

    6,2,0,1,3,7,8,9,4,5.

Assign each vertex its actual third-nearest distance, counting ties with multiplicity. This guarantees at most two strictly closer points. The two rich rows are exactly

    p0 -> {p3,p4,p5,p6} at radius 1,
    p3 -> {p0,p7,p8,p9} at radius 1.

The all-radius maximum multiplicities in original label order are

    (4,1,1,4,1,1,1,1,1,1).

The only Gabriel neighbors of p0 are p1 and p2. More strongly, the triangle (p0,p1,p2) has circumcenter and squared radius

    c = (1207/212000,2887/212000),
    R^2 = 4895809/22472000000.

Every other point lies strictly outside its circumcircle. The smallest positive circle power is exactly

    104510671/107378000.

Since p1,p2 are p0's two hull neighbors, this strict empty circumcircle certifies a Delaunay ear at p0. The ear triangle is forced in every Delaunay triangulation; p0 has degree two there.

After deleting p0, the maximum multiplicities at original labels 1,...,9 become

    (1,1,3,1,1,1,1,1,1).

Thus p3 becomes good at every radius. Low Delaunay degree does not make a rich vertex dispensable to other rich vertices.

**Scope.** This is not a globally four-rich polygon. Nor is its minimum-radius layer declared wholly rich. The example rejects unconditional deletion-preserves-richness at a rich Delaunay ear, even under the two-closer condition. It does not reject a deletion theorem whose proof genuinely uses richness at every original vertex.

## 5. A low-rank middle-edge forest shortcut also needs its full hypotheses

The following points are stored as (x,y) representing the actual point (x,sqrt(3)*y):

    A = (0,0)
    B = (1,0)
    C = (1/2,1/2)
    a = (397/403,-40/403)
    b = (529/806,437/806)
    c = (-57/403,23/403).

They are strictly convex in order c,A,a,B,b,C. At common radius 1, the rows at A,B,C are

    A -> {a,B,C},
    B -> {b,C,A},
    C -> {c,A,B}.

Each of all six vertices has exactly one strictly closer vertex at radius 1. In each displayed row, the middle angular witness is respectively B,C,A. The undirected middle-edge graph therefore contains the triangle A-B-C-A.

The all-radius multiplicities are

    (3,3,3,2,2,2).

**Important:** this falsifies a proposed forest theorem allowing low-rank rows of size at least three. It does not falsify a theorem restricted to centers with four or more witnesses. No such stronger theorem is proved here. It also does not contradict the earlier rank-one obstruction, which required four witnesses at every assigned center.

## 6. What was verified, and what was not

`verify.py` is a fresh standalone standard-library implementation. It reconstructs the three controls; verifies all supporting-line signs, all assigned and all-radius classes, and every claimed closed-disk Gabriel edge; checks the ear circumcircle and the effect of deletion; and produces `verification.json` deterministically.

It also checks the local degree-lifting inequality and common-radius consequence on a bounded family of rational ellipse subsets and the named controls. These finite cases are regression tests, not the proof of the arbitrary-size lemma. Seventeen tests check the controls and rejection of malformed or inexact inputs. No external independent review is claimed.

The concurrent optimization and floating-point explorations from this attempt are not included as mathematical evidence. Infeasibility was not proved for the unrestricted domain. Search timeouts and absence of a found counterexample are not exclusions.

## 7. Remaining obligations

Even in the assigned two-closer regime, no contradiction has been established from universal four-richness while retaining both upward and returning dependencies. The local descent can terminate at a higher-Gabriel-degree vertex. The direct global capacity inequality and unconditional ear deletion are unavailable for the reasons above.

Separately, arbitrary four-rich polygons have not been reduced to the two-closer regime. A solution must close both obligations or use a different argument that covers arbitrary assigned radii. Neither a complete proof nor a counterexample to Erdős #97 was obtained in this attempt.
