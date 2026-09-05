# A radius-window theorem without independence or parity assumptions

Date: 2026-09-05. Companion to draft PR #931, based on commit
`2825a9bd175f8a7b85ea09488d8c74ecbb241e03`.

Status: **PAPER_PROOF_CANDIDATE / REVIEW_PENDING**.

No complete proof or counterexample to Erdos Problem #97 is claimed. This
packet does not promote the accepted finite-case bound. Its theorem is for
arbitrary polygon size, but only for radii bounded by the original incident
side lengths. It removes the boundary-independence and witness-parity
hypotheses from the preceding radius-descent theorem at the four-witness
threshold. It does not justify removing the radius bound.

## 1. The theorem

For a vertex v of a strictly convex polygon P, write

    ell(v) = min(|v-v^-|, |v-v^+|),

where v^- and v^+ are its neighbors in the original polygon P.

**Theorem (no locally side-bounded four-witness core).** Let X be any nonempty
subset of the vertices of P. Assign each x in X a radius rho_x satisfying

    0 < rho_x <= ell(x).

Then at least one x in X has at most three other members of X at distance
rho_x. No independence, parity, symmetry, reciprocity, common-radius, or
minimal-counterexample hypothesis is imposed on X or on the selected rows.

The side bound refers throughout to P, not to an induced subpolygon.

**Radius-window corollary.** Every nonempty X contains an x such that

    for every 0 < r <= ell(x),
    #{y in X minus {x}: |x-y|=r} <= 3.

In particular this holds with X equal to the entire polygon vertex set.
Negating this conclusion would allow selection of a forbidden rho_x at
every x, proving the corollary from the theorem.

## 2. Geometric input from the preceding packet

We use the equal-leg two-star lemma proved in
`../radius-descent-n11-2026-09-05/proofs.md`, Sections 1-2:

> If O,A,B are pairwise nonconsecutive vertices of a strictly convex polygon
> and |OA|=|OB|=r, at least one of the four original sides incident to A or B
> has length less than r.

For completeness, its proof uses endpoint deviations (alpha_j,beta_j) on
O->A, A->B, B->O, with theta=angle AOB. The endpoint supporting-line
inequalities give nonnegative slacks

    u = 2 alpha_1 + beta_1 - pi,
    v = alpha_3 + 2 beta_3 - pi.

The positive original exterior turns at O,A,B satisfy the exact identity

    pi-theta-(alpha_2+beta_2)
       = 2 tau_O + tau_A + tau_B + u + v > 0.

If both incident sides at A and B were at least r, projection of the A->B
arc onto the bisector of its edge-direction interval would give

    |AB| >= 2r cos((alpha_2+beta_2)/2)
          > 2r sin(theta/2) = |AB|.

All three arcs must contain internal vertices for this input lemma. We do
not drop that assumption: the new argument chooses only triples to which it
applies. The complete endpoint-angle and supporting-half-plane proof remains
in the preceding packet and is part of the review dependency.

## 3. A local four-witness forcing lemma

Fix a vertex O and r>0. Suppose every member of some set W of radius-r
witnesses of O has both incident sides of P of length at least r.

**Lemma.** W has at most four members. If it has four, it consists of both
boundary neighbors of O and exactly two non-neighbor witnesses U,V; those
two are consecutive vertices of P.

Proof. Let T be the witnesses in W that are not boundary neighbors of O.
Two nonconsecutive members A,B of T, together with O, would satisfy all
hypotheses of the two-star lemma, contradicting their incident-side bounds.
Consequently all pairs of vertices in T must be boundary adjacent.

For n>=5, a boundary cycle has no three pairwise adjacent vertices. Thus
|T|<=2. There are at most two boundary neighbors of O, giving |W|<=4. Equality
forces the asserted two boundary neighbors and one adjacent non-neighbor
pair. Cases n<5 have fewer than four possible witnesses and need no argument.

This lemma does NOT bound |W| by three. The exact seven-vertex example in
Section 6 has four such witnesses and even has every polygon side at least r.

### Unconditional short-side witness-count inequality

This part needs NO radius cap on any selected center. For any vertex O and
radius r, let C_O(r) be its complete distance-r class, let b_O(r) be the
number of its boundary neighbors in that class, and put

    q_O(r) = #{w in C_O(r): ell(w)<r}.

Among the witnesses with ell(w)>=r, at most two can be non-neighbors of O:
they must be pairwise boundary adjacent by the same two-star argument.
Consequently

    q_O(r) >= max(0, |C_O(r)| - 2 - b_O(r)).

For a class of four witnesses this forces at least two short-side witnesses
when b_O(r)=0, and at least one when b_O(r)=1. When b_O(r)=2 the bound permits
zero; that equality case is why minimum-radius propagation is needed.
The shortness is relative to the SOURCE radius r; it is not automatically
a comparison with the target's own selected radius.

If L is the shortest boundary-side length of P and 0<r<L, then q_O(r)=0 and
b_O(r)=0 at every O. Thus EVERY vertex has at most TWO witnesses at any such
radius. The bound two is attained by the strictly convex pentagon obtained
from control A below by retaining the vertices O,q,U,V,s. Its shortest side
has length 6/5, while O has the two witnesses U,V at radius 1. This five-point
subthreshold control is also verified exactly.

## 4. Minimum-radius propagation

Suppose the theorem fails, and choose O in X minimizing rho_O=r. Every
x in X has both incident sides at least rho_x>=r. Apply the local lemma to
four radius-r witnesses of O.

Both original boundary neighbors of O belong to X, and their distances to O
are r. For either neighbor y,

    r <= rho_y <= ell(y) <= |y-O| = r.

Therefore rho_y=r. The same reasoning now applies at y, forcing its two
boundary neighbors into X, again with radius r. Following the connected
boundary cycle reaches every vertex. We have proved, not assumed, that

    X = V(P),
    rho_x = r for every x,
    every boundary side has length r,
    every vertex has exactly four radius-r witnesses.

At every vertex the two non-boundary radius-r witnesses are adjacent to one
another on the polygon boundary. This last conclusion uses the local lemma
again; the exact-four conclusion is an upper bound on the COMPLETE radius-r
class, not merely on the four selected witnesses.

## 5. The final geometric contradiction

Choose any O. Write its two non-boundary radius-r witnesses as U,V in their
boundary order, and its boundary neighbors as a,b, so the inherited cyclic
order of these five distinct vertices is

    O, a, U, V, b.

There may be additional vertices in the gaps a->U and V->b. Because U,V
are boundary adjacent, |UV|=r. Thus O,U,V form an equilateral triangle.

At U, the vertex O is a non-boundary radius-r witness. Its other non-boundary
radius-r witness W must be adjacent to O, hence W is a or b. Likewise V has
another non-boundary witness Z in {a,b}.

Here are two equivalent completions of the contradiction.

### Completion A: three successive 60-degree gaps

All four points a,U,V,b lie on the circle centered at O, in that angular
order. Their total angular span is strictly less than pi because O is a
strict hull vertex. Chord length is strictly increasing with central angle
in this interval.

The chord Ub strictly contains the angular interval of UV, so |Ub|>|UV|=r.
Thus W cannot be b and W=a, giving |Ua|=r. Similarly |aV|>|UV|=r, so Z=b
and |Vb|=r. The three successive chords

    aU, UV, Vb

all have length r on a circle of radius r. Each spans pi/3, so the total
angular span is pi, contradicting strict convexity at O.

### Completion B: an exact affine midpoint contradiction

W is distinct from V, since V is a boundary neighbor of U and W is not.
Both V and W are the two possible third vertices of an equilateral triangle
on OU: |OW|=r because W is a boundary neighbor of O. The two third vertices
sum to O+U. Consequently

    W = O+U-V.

Similarly Z is distinct from U and

    Z = O+V-U.

Hence W+Z=2O. Also W-Z=2(U-V) is nonzero, so O is strictly between two other
polygon vertices. It cannot be an extreme point. This again contradicts
strict convexity.

These complete the theorem. The argument is an all-n paper proof candidate;
finite samples in the checker are not its proof of the quantifier over n.

## 6. Exact controls

### A. Four locally admissible witnesses really are possible

The following points are in strictly convex counterclockwise order:

    O = (0,0)
    a = (5/13,-12/13)
    q = (79/100,-47/25)
    U = (4/5,-3/5)
    V = (4/5,3/5)
    s = (79/100,47/25)
    b = (5/13,12/13).

Every side has length at least 1, and O has exactly four witnesses at distance
1: a,U,V,b. U,V are boundary adjacent, exactly as the local forcing lemma
requires. This refutes the overstrong local statement that the two-star
lemma alone limits every such vertex to three witnesses.

The theorem avoids that false step: it needs four witnesses at EVERY retained
center, then uses minimum-radius propagation and a separate terminal proof.

### B. An actual long-radius obstruction to removing the radius cap

Let omega=(-1+i sqrt(3))/2 and form the nine-point C3-symmetric union of the
three orbits generated by

    a = 1,
    b = (-5+i sqrt(3))/7,
    c = (-5-i sqrt(3))/7.

The checker represents all coordinates as (x,sqrt(3)y), x,y rational. It
checks all supporting-edge determinants exactly, all squared distances, and
all multiplicity classes. The exact multiplicity distribution is

    three vertices with maximum multiplicity 4;
    six vertices with maximum multiplicity 2.

At a, the four distance-sqrt(3) witnesses are omega*a, omega^2*a, b, c.
Both original incident sides at a have squared length 3/7. Thus its rich
radius is sqrt(7) times its local cap ell(a). The same is true at its rotations.

This example is NOT a counterexample to Erdos #97: six vertices are good.
It demonstrates why being good throughout the radius window r<=ell(v)
does not imply being good at every radius. It also refutes the proposed C3
shortcut that a maximum-norm orbit can have at most one additional witness
at its own equilateral-triangle side radius: the maximum-norm orbit here
has two such witnesses. The radii of the other two orbits are smaller, with
squared norm 4/7.

The global minimal-counterexample hypothesis is not used in either control.
Neither control is advertised as a minimal counterexample or full bad system.

## 7. What has and has not changed

The preceding theorem needed an independent center set and two witnesses
inside it. The present theorem works with an arbitrary center set and four
witnesses inside it, allowing all boundary adjacencies and witness parities.
Both theorems remain useful: neither statement implies the other by dropping
hypotheses, since their witness-count thresholds differ.

Consequences include:

1. A four-bad polygon cannot select a rich radius <=ell(v) at every vertex.
   In fact, some vertex has ALL of its rich radii greater than ell(v).
2. No selected-witness sink component can consist entirely of centers whose
   selected radii obey the original side caps.
3. Repeatedly removing a radius-window-good vertex gives an ordering in
   which each vertex has at most three later vertices at any one radius
   <=its ORIGINAL local cap. This is not a good-deletion ordering for all radii.

The unresolved task is to control long-radius rich classes, or prove a
valid reduction that supplies the side bounds. Minimality alone has not been
shown to do this. The exact nine-point control warns against replacing that
missing reduction with a largest-orbit or local-goodness assertion.

No n=12 search, new all-n unrestricted result, closure of the 66-point
construction, or independent external review is claimed.

## 8. Replay and provenance

    python check_side_cap_extension.py --write
    python check_side_cap_extension.py --check
    python -m unittest -v test_side_cap_extension.py

The checker is standard-library-only. It verifies the exact coefficient
identity, the equilateral midpoint identity and noncoincidence, bounded
combinatorial calibration, and both exact controls. It does not mechanically
prove the supporting-line/projection geometry or the arbitrary-n induction.
`side_cap_report.json` is generated by the checker, not edited by hand.
Repository-wide CI is separate from these standalone checks.
