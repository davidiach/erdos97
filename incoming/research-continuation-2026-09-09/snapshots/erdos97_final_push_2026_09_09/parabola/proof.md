# Finite closure is impossible for the opposite-chain two-parabola scaffold

9 September 2026. Written proof; independent mathematical review pending.
This is an all-size **restricted** theorem, not a resolution of Erdős #97.

## 1. The exact repository scaffold is now excluded, without convexity

The repository note `docs/two-parabola-lens-closure.md` at commit
`047d05149382e48b602b292df4b8fc9e2da560bb` considers finite parameter sets A,B,

    L_a=(a,a^2),    U_b=(b,H-b^2),    c=1-2H,

with every lower center choosing four distinct upper witnesses and every
upper center choosing four distinct lower witnesses. Radii may differ by center.
The note derives, for each chosen row W_t, the necessary identity

    (1/4) sum_{q in W_t} q^2 = -c/2-t^2.                (1)

The following argument excludes every finite nonempty closure satisfying (1).
No radius bounds, symmetry of A and B, rationality, convexity, or size cutoff
are required.

**Theorem 1.** The stated opposite-chain two-parabola closure does not exist.

**Proof.** Define the potential

    g(t)=t^2+c/4.

Equation (1) becomes

    (1/4) sum_{q in W_t} g(q) = -g(t).                  (2)

Choose a center t for which |g(t)| is largest in the finite tagged union of
A and B, and call this largest value M. Every witness has g-value in [-M,M].
Its row average in (2) is one of the endpoints -M or M. All four terms must
therefore equal that endpoint. Thus all four witness parameters have the same
square. There are at most two distinct real numbers with a specified square,
contradicting four distinct witnesses in the opposite chain. The case M=0
has the same conclusion. QED.

The previously stored finite-grid failures and eight-per-chain size floor are
not needed for this proof. The theorem excludes their entire exact
opposite-chain scaffold, including arbitrary real or algebraic parameters.
It does not exclude a mixed same-chain/opposite-chain four-witness row.

## 2. Independent derivation of the moment identity

For a center (u,v), intersect its radius-r circle with the nondegenerate
vertical parabola

    q(t)=(h+t, a t^2+c),    a!=0.

The circle equation is

    a^2 t^4 + [1+2a(c-v)]t^2 + 2(h-u)t
        +(h-u)^2+(c-v)^2-r^2 = 0.                      (3)

If there are four distinct intersection parameters t_1,...,t_4, they are all
four roots. Vieta and the missing cubic term give

    sum t_j=0,
    sum t_j^2=4(v-c)/a-2/a^2.

Consequently their actual height coordinates satisfy

    (1/4) sum_j (a t_j^2+c) = v-1/(2a).                (4)

Substitution of the two scaffold curves into this formula recovers (1).
Circles cannot have five distinct intersections with this parabola because
(3) is a nonzero quartic. Thus selecting any four equidistant witnesses from
one such parabola legitimately invokes the complete root identity.

## 3. Stronger result: any finite deterministic cycle of parallel parabolas

**Theorem 2.** Let P be a finite nonempty set of distinct planar points,
partitioned into nonempty subsets P_1,...,P_m. Each P_i lies on a
nondegenerate parabola with an axis parallel to one fixed direction. Fix a
function sigma:{1,...,m}->{1,...,m}. It is impossible that every p in P_i has
four distinct equidistant witnesses in P_sigma(i)\{p}.

No convexity is assumed. The parabolas may have different horizontal and
vertical offsets, different nonzero curvatures, and either opening direction.
A point at the intersection of two parabolas is assigned one part in the
partition, not counted as two points. The target part must be fixed for each
source part; target choices depending on the individual source vertex are
not included in this theorem.

**Proof.** Choose Euclidean coordinates with the common axis direction
vertical. Write each parabola as y=a_i(x-h_i)^2+c_i, where a_i!=0. Formula
(4) says that the selected row average of witness heights equals the source
height plus

    delta_sigma(i)=-1/(2a_sigma(i)).

The finite functional graph of sigma has a directed cycle. All parts are
nonempty, so take a cycle i_0 -> i_1 -> ... -> i_(ell-1) -> i_0.
Starting at p in P_i0, average over all 4^ell selected witness walks of length
ell, retaining repetitions with their positive multiplicities. Repeated use
of (4) gives

    average endpoint height = height(p)+Delta,
    Delta=sum_{j=0}^{ell-1} (-1/(2a_ij)).               (5)

Every endpoint lies in the same finite part P_i0. If Delta>0, choosing a
maximum-height starting point contradicts (5). If Delta<0, choose a
minimum-height starting point.

If Delta=0, choose a maximum-height starting point. Every endpoint height is
at most that maximum, and their average equals it, so every endpoint has
exactly that height. Choose any selected walk of length ell-1. The final
center on that walk has four distinct witnesses in P_i0, and all four must
have the maximum height. A horizontal line meets a nondegenerate vertical
parabola in at most two points. This is impossible. For ell=1 the same
argument uses the starting point as the final center; in fact Delta is then
nonzero. QED.

Two arbitrarily positioned parabolas with parallel axes and opposite-chain
witness assignments form a two-cycle, so are included. More than two
parabolas are also covered when their target-part assignment is fixed.

## 4. The finite averaging principle used in the proof

More generally, suppose a finite typed directed system has a real-valued
height function, each row consists of k distinct witnesses in a deterministic
target type, and the row's height average equals its source height plus a
constant depending only on that type transition. If every level set inside
each type contains fewer than k points, the same cycle-drift/maximum argument
excludes a nonempty closed system. All averaging weights may be positive
instead of equal, provided the asserted affine average identity still holds.

This principle is not automatically available for arbitrary convex polygons.
For the parabolas, the four roots of a quartic supply precisely the needed
identity. No corresponding identity for an arbitrary four-witness row is
established in this packet.

## 5. Positive control and verification scope

A single rich row on a parabola is possible, even in a strictly convex set.
Take

    p=(9,12),
    q_1=(-4,16), q_2=(-2,4), q_3=(1,1), q_4=(5,25).

All four q_j lie on y=x^2, and all four squared distances from p are 185.
The five points are strictly convex in order p,q_4,q_1,q_2,q_3. Their maximum
multiplicities are 4 at p and 1 at each q_j. Point p also lies on the other
parabola y=93-x^2, but the other four points do not have four opposite-chain
witnesses. Thus this control does not satisfy the theorem's global richness
hypothesis.

`verify.py` reconstructs this control, checks all 15 supporting-half-plane
signs and all distance classes, and compares the Vieta-derived circumcenter
to a separately solved three-point circumcenter on 96 rational translated
and rescaled rows. Its coefficient and finite-cycle checks are regressions,
not a substitute for the arbitrary-real finite maximum argument above.
No external review or formalization is claimed.
