# Long-radius orbit obstructions: algebraic units and convex power quotients

Date: 2026-09-05. Continuation of draft PR #931 after commit
`bbd46f23e5e81f258f478a35c3e3e7ff52e98711`.

Status: **PAPER_PROOF_CANDIDATES / REVIEW_PENDING**, with exact algebraic and
geometric controls. No unrestricted solution of Erdos Problem #97, new
accepted finite-case bound, or independent external review is claimed.

The side-cap theorem from the preceding packet concerns short selected radii.
This packet instead handles arbitrarily long own-triangle-side radii in
concentric equilateral-triangle orbits. It proves an all-size obstruction
when the angular phases are commensurable, and two further necessary
conditions that do not require angular commensurability. The irrational-angle
branch remains; an exact convex three-orbit directed cycle explicitly shows
why the commensurability hypothesis cannot simply be deleted.

## 1. Orbit notation and the distinction from the full problem

Set omega = (-1+i sqrt(3))/2. For nonzero complex representatives z_i let

    T_i = {z_i, omega*z_i, omega^2*z_i},
    r_i = |z_i|,  s_i = r_i^2,  w_i = z_i^3.

Distinct representatives are understood to describe distinct orbits, so
w_i != w_j. An **own-side arrow** i -> j means that for some k in {0,1,2},

    |z_i - omega^k*z_j|^2 = 3*s_i.                     (1)

The other two members of T_i already supply two witnesses at radius
sqrt(3)*r_i. An own-side four-tie needs additional witnesses from other
orbits. For a strictly convex union, one target orbit supplies at most one
extra witness at that radius, as proved in the repository's
`docs/orbit66-exact-partial-construction.md`. The theorem below does not
need that last fact: it already obstructs a directed graph of minimum
outdegree ONE on distinct orbits under its angular hypothesis.

A general four-tie in a C3-symmetric set need not use the two orbit-mates.
Four cross-orbit singleton witnesses, and other-radius half-step rows, are
outside the own-side hypothesis. This is not a proof of #97 for all
commensurable-angle point sets.

## 2. New all-size theorem: no commensurable-angle directed cycle

**Theorem.** A directed cycle of own-side arrows through distinct C3 orbits
cannot have all of its selected source-to-witness angles rational multiples
of pi. No convexity or bound on the radii is needed.

In particular, if all the orbit phase differences are rational multiples of
pi, the own-side arrow graph is acyclic. Every nonempty induced orbit family
then has a vertex with no outgoing own-side arrow. At each point in that
orbit the distance sqrt(3)*r_i occurs exactly twice, at its two orbit-mates.
It is therefore impossible that every orbit has an own-side four-tie.

### Proof

Consider a proposed cycle z_0 -> z_1 -> ... -> z_(h-1) -> z_0, incorporating
its chosen rotations into the edge angles theta_i. Write

    u_i = r_(i+1)/r_i > 0,   X_i = 2*cos(theta_i).

Subscripts on the radii are cyclic. Dividing (1) by r_i^2 gives

    u_i^2 - X_i*u_i - 2 = 0,                          (2)
    product_i u_i = 1.                               (3)

If theta_i/pi is rational, X_i is the sum of a root of unity and its
inverse. Thus X_i is an algebraic integer, and every field conjugate of X_i
is real and belongs to [-2,2]. Equation (2), being monic over algebraic
integers, makes u_i an algebraic integer too. In a common number field,
(3) gives

    u_i^(-1) = product_(j != i) u_j,

so every u_i is an algebraic unit.

Every conjugate t of u_i is real: under any embedding, (2) becomes

    t^2 - x*t - 2 = 0,   -2 <= x <= 2,

whose two roots are real and nonzero. Define the algebraic integer

    v_i = u_i^(-2) - 1.

The following exact identity is decisive:

    u_i^(-2) * (4 - X_i^2) = 3 - 4*v_i^2.            (4)

Under every embedding the left side is nonnegative, because t is real,
t != 0, and x^2 <= 4. Hence every conjugate v of v_i satisfies

    |v| <= sqrt(3)/2 < 1.                            (5)

A nonzero algebraic integer cannot have all its conjugates of absolute
value less than one: its field norm would be a nonzero integer of absolute
value less than one. Thus v_i=0, u_i^2=1, and positivity gives u_i=1.
Substitution in (2) gives X_i=-1, so theta_i is +2*pi/3 or -2*pi/3 modulo
2*pi. The source and target therefore belong to the same C3 orbit, contrary
to distinctness. This proves the theorem.

The use of the cycle is essential. A single edge need not have a unit radius
ratio. The proof does not turn arbitrary algebraic angles into roots of
unity. Rational Cartesian coordinates, or coordinates in Q(sqrt(3)), do
NOT imply rational multiples of pi for their polar angles.

### A genuine increasing potential, not just a cycle test

The same proof yields a strict arithmetic potential on the entire graph.
For one arrow with rational theta/pi, equation (2) makes u an algebraic
integer. If u were a unit, (4)-(5) would force u=1 and identify the two
orbits. Thus for DISTINCT orbits the ratio u is a nonunit algebraic integer.
In every number field K containing it,

    |Norm_(K/Q)(u)| is an integer at least 2.          (8)

In one weakly connected component, choose an orbit o. Every r_i/r_o is
algebraic, since along an undirected path it is a product of the algebraic
edge ratios or their inverses. Choose a common number field K and define

    H_i = |Norm_(K/Q)(r_i/r_o)| > 0.

Every arrow i->j then satisfies H_j >= 2*H_i. A maximum-H orbit has no
outgoing arrow. Unlike physical radius ordering, this potential is valid
for all edges in the stated commensurable-angle family, however long their
selected radii are. It is not asserted for the irrational-angle family.

## 3. An exact control: irrational-angle cycles really do occur

In coordinates z=x+i sqrt(3)*y, take

    a_0 = 1,
    a_1 = (-26503 + 8991*i*sqrt(3))/21854,
    a_2 = (-44665 + 10753*i*sqrt(3))/37058.

These are the three seeds of the existing orbit66 construction, after the
common similarity z -> z/(2i). They satisfy exactly

    a_0 -> omega*a_1,
    a_1 -> omega*a_2,
    a_2 -> a_0.

The checker certifies all nine points as distinct vertices of a strictly
convex polygon. It calculates every distance class, rather than checking
only the three chosen equalities. Each vertex has maximum multiplicity
three, not four. This is not a counterexample to #97.

For each selected edge, the checker computes the rational number

    2*cos(2*theta)
      = 4*(Re(a*conj(b)))^2 / (|a|^2*|b|^2) - 2,

using the actual rotated witness b. None is an integer. If theta/pi were
rational, this number would be an algebraic integer because it is the sum
of a root of unity and its inverse. A rational algebraic integer is an
integer, a contradiction. Thus all three displayed edge angles are
irrational multiples of pi.

This control prevents extending the cycle theorem by silently replacing
"rational angle" with "exact algebraic coordinates". It also explains why
the theorem does not dispose of the existing 66-point construction lane.

## 4. Convexity survives the power quotient

**Theorem.** Let P be a strictly convex polygon invariant under rotation by
2*pi/k around the origin, k>=2. Choose one representative z_i from each
rotation orbit. The distinct points z_i^k are in strictly convex position.
For fewer than three orbits, use the ordinary convex-independence convention.

This is a statement about the convex independence of the sampled image
points. The origin need NOT lie inside their convex hull, and the converse
is false.

### Proof

The origin is strictly inside P. Traverse a fundamental 2*pi/k boundary
portion and apply f(z)=z^k. The argument of z strictly increases along the
boundary, so the image is a simple closed radial curve traversed once.

On an original directed edge z(t)=a+t*e,

    f'(z(t)) = k*z(t)^(k-1)*e,
    d arg(f'(z(t)))/dt
       = (k-1)*Im(e/z(t))
       = (k-1)*cross(z(t),e)/|z(t)|^2 > 0.

The last inequality holds because the origin is strictly on the left side
of each original directed supporting edge. At an original vertex, the
image tangent has the same positive jump as the original tangent: the
factor z^(k-1) is continuous there.

On one fundamental portion the original tangent turns by 2*pi/k and arg(z)
increases by 2*pi/k. Therefore the total turn of the image tangent is

    2*pi/k + (k-1)*2*pi/k = 2*pi.

A simple closed curve with this increasing tangent direction is convex.
For an elementary supporting-line verification, fix a smooth tangent
vector t_0. The signed distance from the curve to that tangent line has
derivative proportional to sin(phi-phi_0). It increases until the tangent
has turned pi, then decreases back to zero by the time it turns 2*pi.
It is strictly positive between the two visits to the starting point.
At corners one uses a direction in the positive tangent jump. This gives
supporting lines and excludes straight boundary segments.

Thus the image bounds a strictly convex body. Its sampled points z_i^k
are distinct boundary points and are consequently in strictly convex
position. No claim is made that the image of an edge is a straight segment.

### Exact geometric fixtures and non-converses

The checker uses a 21-vertex rational C3-symmetric fixture. For j=0,...,6,
t=j/7, choose

    z_j = (1 - 3*t^2/2) + i*sqrt(3)*(2*t - 3*t^2/2),

and include their two rotations. All supporting-edge determinant checks
are exact. The seven cubes likewise pass all supporting-edge checks.
These are bounded checks of the statement, not its arbitrary-size proof.

The three-orbit cycle in Section 3 also shows that the origin can be outside
the convex hull of the cubed representatives, even though it is inside the
original nine-vertex polygon. Separately, representatives 1, 2, i*sqrt(3)
have noncollinear cubes 1, 8, -3*i*sqrt(3), but their original orbit union
is not convexly independent: 1 is strictly inside the triangle generated
by 2. Thus convexity of the cube quotient is necessary, not sufficient.

## 5. A radius-only no-shortcut theorem, including irrational phases

The cubic identity already recorded in the orbit66 note is

    product_(k=0,1,2) (|a-omega^k*b|^2 - 3*s)
       = |a^3-b^3|^2 - 9*s*(s-t)^2,
    s=|a|^2, t=|b|^2.                                (6)

In particular every own-side arrow i->j gives an ordinary Euclidean
length in the cube quotient:

    |w_i-w_j| = 3*r_i*|s_i-s_j|.                     (7)

Distinct equal-norm orbits have no arrow; arrows in both directions would
force s_i=s_j and w_i=w_j, so they too are impossible. These latter two
consequences are already in the repository. The following path consequence
is the new part.

**Monotone-radius no-shortcut theorem.** Suppose the underlying undirected
own-side graph contains a path

    v_0, v_1, ..., v_h,  h>=2,
    r_(v_0) < r_(v_1) < ... < r_(v_h).

Then the downward arrow v_h -> v_0 is impossible. The path edges can point
either way. No convexity or rational-angle assumption is needed.

Proof. Let R=r_(v_h). For an edge between v_j and v_(j+1), its source radius
is at most r_(v_(j+1)) <= R. At least one of the h edges has source radius
strictly smaller than R. Equation (7) and strict increase of the squared
radii therefore give

    sum_j |w_(v_(j+1))-w_(v_j)|
       < 3*R * sum_j (s_(v_(j+1))-s_(v_j))
       = 3*R*(s_(v_h)-s_(v_0)).

If the downward shortcut existed, its cubed length would equal the last
quantity, contradicting the triangle inequality along the path.

For a complete triangle of interacting orbits, the edge joining its
minimum- and maximum-radius orbits must consequently point upward.
This is a constraint on radial order, not a claimed ordering of the
original boundary labels.

### A precise limit of this rule

On six abstract labels in increasing radial order 0<1<...<5, take

    0 -> {4,5}, 1 -> {4,5},
    2 -> {0,1}, 3 -> {0,1},
    4 -> {2,3}, 5 -> {2,3}.

Every label has two outgoing arrows, there are no reciprocal pairs, and
there is no downward edge with an alternative increasing-radius path.
The checker exhaustively tests that last property on this finite graph.
This is only an abstract graph negative control. No distances, angles,
coordinates, or Euclidean realization are asserted. It shows that the
no-shortcut rule by itself is not a proof of the own-side branch.

## 6. Convex metric inequalities in the quotient

When the original C3 union is strictly convex, Section 4 makes the w_i
strictly convex as well. Hence for four representatives in their inherited
quotient boundary order a,b,c,d,

    |w_a-w_c| + |w_b-w_d| > |w_a-w_b| + |w_c-w_d|,
    |w_a-w_c| + |w_b-w_d| > |w_a-w_d| + |w_b-w_c|.

These follow by splitting the crossing diagonals at their intersection and
applying strict triangle inequalities. Any known arrow can be replaced by
its exact expression (7). This adds a convex metric layer to the radial
no-shortcut rule, including configurations with irrational angles.

It is not proved that every minimum-outdegree-two own-side system violates
one of these inequalities. Nor is any claim made that the abstract six-label
control satisfies them for some set of radii. This is an additional
necessary-condition framework, not a sufficiency or extraction theorem.

## 7. Validation, repository scope, and the remaining problem

Run from this directory with Python 3.10+; no third-party modules are needed:

    python check_long_radius.py --write
    python check_long_radius.py --check
    python -m unittest -v test_long_radius.py

The report is generated, not hand-edited. It checks (4) and the coefficient
identity behind (6), exact selected distances and all distance classes of
the convex cycle, its irrational-angle certificates, convexity of a variable-
norm power fixture, and the abstract no-shortcut control. Unit tests also
exercise rejection of a genuine forbidden shortcut and invalid fixtures.

These checks do not formalize the algebraic-integer norm argument or the
continuous supporting-tangent proof. Both paper proofs remain review
pending. Repository-wide tests and artifact audits are separate.

**Remaining gap.** The unrestricted long-radius case is not closed. In the
own-side C3 lane, irrational angular cycles are possible, and the path rule
alone does not exclude a finite two-out core. For arbitrary polygons there
is additionally no reduction to C3 symmetry or to own-side radii. No completed
counterexample, general extraction theorem, or solution of #97 is claimed.
