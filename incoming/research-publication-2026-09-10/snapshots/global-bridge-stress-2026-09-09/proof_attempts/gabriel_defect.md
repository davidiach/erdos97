# Gabriel defect: valid inequality, but not a bounded index

Status: **written proof / review pending**, with exact finite regression checks.
This is not a solution of Erdős Problem #97.

## 1. A local inequality without a rank hypothesis at the root

Let P be a finite set of distinct planar points. Convexity is not assumed here.
The strict Gabriel graph G contains xy if its **closed** diameter disk contains
no other point. Thus z blocks xy precisely when

    |x-z|² + |z-y|² <= |x-y|².

For r>0 define T_p(r)={z != p : |p-z|<r}, b_z(r)=|T_z(r)|,
and a_p(r)=#{z in T_p(r): pz is not a Gabriel edge}. Write M(p,r) for
the number of distance-r witnesses of p. Then

    M(p,r) + a_p(r) <= deg_G(p) + sum_{z in T_p(r)} (b_z(r)-2).       (1)

The summands are signed, not positive parts.

### Proof

Fix p,r. Put T=T_p(r), k=|T|, and let s be the number of Gabriel edges
from p to T. For every z in T with pz non-Gabriel, choose a blocker w of pz.
Distinctness and the blocking inequality imply |p-w|<|p-z| and |w-z|<r.
Give z the parent w. Parent distances strictly decrease, so these edges form
a forest F on T, with s roots and k-s edges. This remains valid for blockers
on the diameter-circle boundary.

Partition the distance-r witnesses into u with Gabriel spokes and L with
blocked spokes. Assign each blocked witness q to one blocker z. Both |p-z|<r
and |z-q|<r. Let L_z count the assignments to z. The following are distinct
r-short neighbors of each z in T: p; its neighbors in F; and its assigned
witnesses q. The last group lies outside T. Therefore

    b_z(r) >= 1 + deg_F(z) + L_z.

Summing gives sum_T b_z >= k+2(k-s)+L. Since deg_G(p)>=u+s,
M=u+L and a_p=k-s, rearrangement proves (1). If T is empty the same formulas
apply with k=s=L=0.

In particular, assuming b_z(r)<=2 only at the short neighbors z in T suffices
to conclude deg_G(p)>=M(p,r). No bound on b_p(r) is needed for that implication.

## 2. Exact slack decomposition

Let ell_p be the number of Gabriel neighbors farther than r, and define

    e_z = b_z(r)-1-deg_F(z)-L_z >= 0.

Every Gabriel neighbor of p is a short root, an unblocked radius-r witness,
or a farther neighbor. Thus deg_G(p)=s+u+ell_p, and the preceding accounting
is the exact identity

    deg_G(p) + sum_T(b_z(r)-2) - a_p(r) - M(p,r)
        = ell_p + sum_T e_z.                                    (2)

Consequently the slack consists of unused local incidences and longer edges.
It is not a conserved topological quantity. The independently reconstructed
forest in `verify/gabriel_defect.py` checks (2), not merely the inequality.
The human proof, not the finite tests, establishes the all-size assertion.

## 3. Convex global accounting

For a strictly convex n-gon with n>=3, G is noncrossing. Indeed, if Gabriel
edges were crossing diagonals of a convex quadrilateral, an angle of that
quadrilateral would be at least pi/2. Its vertex would lie in the opposite
diagonal's closed diameter disk. Noncrossing chords have at most 2n-3 edges
(by adding boundary edges and triangulating).

Assign any positive actual radius r_p to each p and put

    D(P,r) = sum_p [sum_{z in T_p(r_p)}(b_z(r_p)-2) - a_p(r_p)].

Summing (1) yields

    sum_p M(p,r_p) <= 4n-6 + D(P,r).                              (3)

An all-rich assignment would imply D(P,r)>=6. This is necessary, not a
contradiction. The converse is not asserted.

## 4. Cubic growth with only six good vertices

Use the explicit family P_m from the pinned repository's
`incoming/unbounded-six-exception-family-2026-09-06/README.md`, at commit
`047d05149382e48b602b292df4b8fc9e2da560bb`. Its all-size strict-convexity and
exactly-six-good conclusions remain written proof dependencies pending
external review. This packet does not promote their repository status.

For completeness, let omega=(-1+i sqrt(3))/2, D(t)=1+3t², and

    z(t) = -1/2 + 3t/D(t) + i sqrt(3)(1-3t²)/(2D(t)).
    t_0=1/10,
    t_{j+1}=2t_j² / [1-2t_j+3t_j² + sqrt((1-t_j)(1-3t_j)D(t_j))].

Let a_j=z(t_j) for even j and its conjugate for odd j, and

    P_m = {1,omega,omega²} union {omega^k a_j: 0<=j<m, 0<=k<3}.

There are n=3(m+1) points. Choose r_p²=3|p|² at every point, including the
anchors and the initial orbit. These are actual positive distance classes,
since the two other orbit mates are present.

Put q(t)=omega² z(t). Direct algebra gives

    |q(t)-1|² = 9t²/(1+3t²),
    |q(t)|² = 1-3t/(1+3t²),
    |q(t)|²-73/103 = 3(1-10t)(10-3t)/(103(1+3t²)).

For 0<=t<=1/10, every q(t) or its conjugate is within 3/10 of 1, and
|q(t)|²>=73/103. Rotating partitions P_m into three groups of exactly m+1
points, each within 3/10 of an anchor. Each group has diameter at most 3/5.
On the other hand every assigned r_p² is at least 219/103 > 9/25.

It follows that, for every p and every z, b_z(r_p)>=m, and |T_p(r_p)|>=m.
Also a_p(r_p)<=|T_p(r_p)|. For m>=3,

    D_p >= |T_p(r_p)|(m-3) >= m(m-3),

and hence

    D(P_m,r) >= 3(m+1)m(m-3).                                   (4)

The general bound D(P,r)<=n(n-1)(n-3) supplies an O(n³) upper bound,
so this assignment has D=Theta(n³). Nevertheless the cited family has only
six good vertices, independently of m.

Therefore D has neither a universal constant upper bound nor a bound C times
the number of good vertices with fixed C on all convex polygons. This remains
false even along a family with good-vertex proportion tending to zero.

**Quantifier limit:** P_m is not all-rich. Equation (4) does not refute an
upper bound whose proof genuinely uses all-richness at every vertex. It does
show that such a proof cannot be obtained merely by calling D a bounded
curvature defect or an approximately conserved index.

## 5. Dependencies and replay

The local lemma and slack identity use only the elementary closed-disk
criterion and finite forest counting. The convex edge bound uses strict
convexity. The cubic lower bound uses the displayed coordinate identities
and the established properties of the pinned family as explicitly identified
above. No solver result is used in their human arguments.

    python verify/check_defect_algebra.py --check
    python verify/gabriel_defect.py --check

Neither command constitutes independent external mathematical review.
