# Conversation research rounds for Erdős Problem 97

Date: 2026-08-06

Status: `RESEARCH_NOTE / REVIEW_PENDING`

This document is a structured record of a long proof-search conversation. It is
not a source-of-truth claim update. No general proof and no counterexample are
claimed, and the official/global status remains falsifiable/open.

The arguments below use the repository trust discipline:

- `PAPER_PROOF_CANDIDATE`: a self-contained mathematical argument was written,
  but it has not been independently reviewed or formalized in this repository.
- `CHECKED_REDUCTION_UPSTREAM`: the conversation referred to a theorem or
  reduction compiled in the separate
  `mysticflounder/erdos-97-96-formalization` project. This repository does not
  independently certify that upstream proof.
- `DIAGNOSTIC_ONLY`: a finite model, numerical experiment, symbolic probe, or
  relaxed subsystem was used to reject or prioritize a route. It is not a proof
  of Erdős 97.
- `FALSE_ROUTE`: an attractive proposed bridge was explicitly refuted.
- `OPEN_BRIDGE`: the first implication still missing from a proposed proof
  architecture.

For full statements and proof sketches of the strongest paper candidates, see
`docs/conversation-paper-lemma-candidates-2026-08-06.md`. For failed routes,
countermodels, the formalization crosswalk, and the proposed next prompt, see
`docs/conversation-frontier-and-failed-routes-2026-08-06.md`.

## Problem statement

Let `P = {p_0, ..., p_{n-1}}` be the vertices of a finite strictly convex
polygon. A vertex `p_i` is 4-rich if there is a radius `r > 0` such that at
least four other vertices have distance `r` from `p_i`.

Erdős Problem 97 asks whether every finite strictly convex polygon contains a
vertex that is not 4-rich.

## Executive summary

The conversation did not produce a complete proof. It produced five useful
families of work:

1. **Global algebraic frameworks.** Selected four-point circles give affine
   circuit rows annihilating `1`, the coordinate vectors, and the squared-norm
   vector. This gives the rigorous upper bound `rank C <= n - 4` unless the
   polygon is already cocircular. A separate stationary-distribution argument
   gives a positive six-bisector equilibrium and explains why first-moment
   separation arguments fail.
2. **Reusable terminal contradictions.** Several ordinary-distance/Kalmanson
   cancellation lemmas were isolated, especially the variable-radius
   alternating-cycle theorem and the alternating-rectangle lemma.
3. **MEC/cap geometry.** A sequence of candidates was developed around a
   non-obtuse minimum-enclosing-circle support triangle: shortest-side
   two-center injectivity, tri-apex overlap restrictions, fatal-pair uniqueness,
   synchronized deletions, blocker forests, and strict radius descent.
4. **Highly structured residuals.** The six-point apex arm was reduced to a
   fresh/five-center continuation or an exact `2+2+2` trace pattern. Later
   rounds further reduced saturated `2+2+2` packets, cap-eight/cap-nine packets,
   and the paired two-radius grid.
5. **Route rejection.** Several tempting global lemmas were shown false. The
   most important is the proposed crossing affine-rigidity lemma: a concrete
   12-row cyclic incidence system satisfies the combinatorial hypotheses but
   has circuit rank `n - 4`, not `n - 3`. Upstream kernel-checked finite
   countermodels also show that several frontier packets cannot be closed using
   incidence information alone.

The most promising final route at the end of the conversation was:

```text
minimal counterexample
  -> source-return paired common-deletion normal form
  -> either a two-radius two-shell grid or an apex-class joint deletion
  -> analytically exclude the grid by radial nesting
  -> force a second source omitted by both retained shells
  -> reduce the sibling arm to a two-source common deletion or exact 4+4 switch
  -> close the remaining deletion packet by a genuine Euclidean/Kalmanson
     terminal.
```

The last arrow remains open.

## Round-by-round ledger

### Preliminary phase: circuit rank and stationary equilibrium

Status: mixed `PAPER_PROOF_CANDIDATE`, `FALSE_ROUTE`, and `OPEN_BRIDGE`.

For one selected four-point witness circle at every center, let `C` be the
matrix of affine-circuit rows. Every row annihilates

```text
1, X = (x_i), Y = (y_i), Q = (x_i^2 + y_i^2).
```

Unless all vertices are cocircular, these four vectors are independent, so

```text
rank C <= n - 4.
```

A proof would follow from a lower bound `rank C >= n - 3`. Multiple versions of
that lower bound were proposed and rejected or left open. The cleanest false
version was the crossing affine-rigidity lemma; an exact 12-row countermodel is
recorded in the companion failed-routes document.

For a vertex-minimal counterexample, choosing four witnesses at each vertex
produces a strongly connected selected digraph. Its stationary distribution
`pi` yields the identity

```text
sum_i pi_i sum_{a<b in S_i} lambda_{i;ab} R(p_b - p_a) = 0,
```

where every `lambda_{i;ab} > 0` and `R` is a quarter-turn. This proves that a
simple separating-linear-functional argument on all oriented witness chords
cannot work: the relevant vectors already admit a positive equilibrium.

A projective normalization

```text
(x,y) -> (t,u) = (y/x, 1/x)
```

was also developed. The polygonal chain opposite a fixed vertex becomes the
graph of a strictly convex piecewise-linear function; circles become explicit
conics. This gave a precise two-conic/convex-graph bridge target but not a
contradiction.

### Terminal Kalmanson phase

Status: `PAPER_PROOF_CANDIDATE`.

Two useful contradiction families were isolated.

The **variable-radius alternating-cycle theorem** rules out two monotone
patterns on cyclically ordered vertices

```text
rho_1, ..., rho_k, c_k, ..., c_1.
```

One pattern equates the lengths of two perfect matchings, although one matching
is the unique maximum-length antipodal matching. The other contradicts an
inductively strict quadrilateral inequality. The radii may vary from row to
row.

The **alternating-rectangle lemma** combines four co-radial pairs and three
strict Kalmanson inequalities to derive opposite strict inequalities between
the same two sums. It is a small terminal that can kill configurations not
caught by one- or two-inequality certificates.

A **Delaunay forest lemma** was also noted: for a selected four-point circle
centered at a polygon vertex, the induced subgraph of any Delaunay triangulation
on the four witnesses is a forest. No three of the witnesses can form a
Delaunay face because the center lies strictly inside their circumdisk.

### Round 1: optimize for Euclidean alternating-cycle extraction

Status: `OPEN_BRIDGE`.

The search was refocused on one theorem:

```text
minimal counterexample
  -> a separated alternating center-witness cycle
  -> variable-radius matching contradiction.
```

Strong connectivity, two-circle intersection caps, and crossing order do not
force such a cycle abstractly. The missing theorem must use the full Euclidean
equalities, not only the incidence graph.

### Round 2: stationary drift on affine parabolas

Status: `PAPER_PROOF_CANDIDATE`.

For points `p(t) = (t,t^2)`, four equal-distance witnesses `s_1,...,s_4` of a
center `t` satisfy

```text
(1/4) sum_j s_j^2 = t^2 - 1/2.
```

Choosing a point with minimum `t^2` gives an immediate contradiction. An
affine-invariant form was derived for any affine parabola using a positive
definite quadratic form; the drift is the positive determinant term

```text
delta = (AC - B^2)/(2C^2) > 0.
```

Thus no finite subset of an affine parabola can be all-4-rich.

### Round 3: conic maximum principle

Status: `PAPER_PROOF_CANDIDATE`, high review priority.

The drift idea was extended to nondegenerate conics.

- On an ellipse, Vieta relations for the quartic intersection of the ellipse
  with a circle centered at a point of the ellipse give a coordinate expansion
  factor `lambda > 1`. Maximizing the absolute coordinate contradicts the
  average identity.
- On a parabola, minimizing the quadratic parameter gives the Round 2
  contradiction.
- On one branch of a hyperbola, a coordinate average contracts by a factor
  `0 < alpha < 1`; an extremal coordinate contradicts the average.

Candidate conclusion: a finite all-4-rich set cannot lie on a connected
component of a nondegenerate real conic. The Vieta calculations should be
independently rederived before promotion.

### Round 4: shortest-side two-center injectivity

Status: `PAPER_PROOF_CANDIDATE`, high review priority.

Let `ABC` be a non-obtuse support triangle of the minimum enclosing disk, and
let `AB` be a shortest side. The proposed theorem says that no two distinct
polygon vertices `U,W` can be simultaneously equidistant from both `A` and
`B`.

The proof normalizes

```text
A=(-a,0), B=(a,0), O=(0,h), C=(p,q).
```

The two equal-distance conditions force `U=(xi,t)`, `W=(xi,-t)`. Disk
containment gives an upper bound on `|xi|`. The shortest-side condition gives

```text
h q >= a(a+|p|),
```

and strict convexity puts `U` outside triangle `ABC`, giving an incompatible
lower bound on `|xi|`.

The claimed corollary is a one-point radius-cell law for the map

```text
X -> (|AX|, |BX|).
```

### Round 5: tri-apex double-overlap obstruction

Status: `PAPER_PROOF_CANDIDATE`, requires careful trigonometric review.

For a non-obtuse MEC support triangle, one fixed distance class at an apex was
claimed unable to have two-point overlaps with distance classes at both other
apices. The argument writes exact ray-to-circumcircle and ray-to-opposite-side
distances and shows that the two reflected-pair overlaps force opposite strict
orders between two triangle angles.

The useful intended matrix rule is:

```text
one saturated 2-point overlap through a fixed apex class
  -> every overlap through that same class on the opposite side is a singleton.
```

### Round 6: fatal-pair uniqueness and synchronized deletion

Status: `PAPER_PROOF_CANDIDATE`, elementary combinatorial core.

At a fully deletion-robust center `p`, let `U` be a set meeting every distance
class at `p` in at most one point. A pair `{x,y} subset U` is fatal if deleting
both destroys every four-point class at `p`.

The **fatal-pair uniqueness theorem** says that at most one pair of `U` is
fatal. Two disjoint fatal pairs would force every rich class to contain two
points of `U`; two overlapping fatal pairs are ruled out using singleton
deletion robustness.

Applied simultaneously to two robust cap endpoints, this gives a pair of cap
points whose joint deletion preserves four-richness at both endpoints. In a
six-point apex class, the same pair also preserves the apex. In a two-radius
arm, either a same-radius pair preserves all three apices or all four
cross-radius pairs preserve the other two apices.

### Round 7: symmetric counterexample families and deletion certifiers

Status: mixed `PAPER_PROOF_CANDIDATE` and `DIAGNOSTIC_ONLY`.

The natural family consisting of two interlaced concentric regular `n`-gons was
analyzed. Strict convexity requires

```text
cos(pi/n) < x < sec(pi/n).
```

Within that interval each cross-orbit distance lies strictly between adjacent
same-orbit chord lengths, so no distance multiplicity reaches four. This rules
out the whole two-orbit family as a counterexample source.

For four same-radius cap points, graph counting gives two disjoint pairs whose
deletion preserves two robust apices. A common `T44` certifier for both
deletions was reduced to one reflection-symmetric matching pattern. The
remaining uncontrolled escape was a collection of singleton `T4` blockers.

### Round 8: maximum-concentration blocker forest

Status: `PAPER_PROOF_CANDIDATE`, important structural lemma.

Assign every source point to a unique-four blocker row containing it, maximizing

```text
Phi = sum_c |f^{-1}(c)|^2.
```

If a point assigned to `d` also lies in a competing row centered at `c`, the
exchange inequality gives

```text
|f^{-1}(d)| >= |f^{-1}(c)| + 1.
```

On one robust apex circle, the graph joining two points when one lies in the
selected blocker row of the other contracts to an acyclic orientation with
outdegree at most one. Therefore it is a forest.

Combining the forest bound on four cap points with the two fatal-pair budgets
produces a pair that simultaneously:

- preserves all three physical MEC apices under deletion; and
- is reciprocally omitted by the two extremally selected blocker rows.

The extremal one-pair case becomes a finite tree-cotree normal form.

### Round 9: six-class fork and exact `2+2+2`

Status: `PAPER_PROOF_CANDIDATE` plus a formalization crosswalk.

For a robust apex class `K` of size at least six, a reciprocally omitted pair
was used to produce two further points outside both selected blocker rows.
Either those two points have distinct fresh blockers, in which case the
maximum-concentration inequality forces a one-way cross omission, or every
remaining point has the same blocker.

The collision alternative is possible only when `|K|=6`, and then three
unique-four rows partition `K` into three exact pairs:

```text
K = (F_c ∩ K) dotcup (F_d ∩ K) dotcup (F_e ∩ K),
|F_c ∩ K| = |F_d ∩ K| = |F_e ∩ K| = 2.
```

So the six-class arm reduces to a five-center continuation or an exact
`2+2+2` exception.

### Round 10: strict radius descent

Status: `PAPER_PROOF_CANDIDATE`, high review priority.

At the apex opposite a shortest MEC side, suppose a blocker circle contains two
strict-cap points lying on one apex-centered circle. The proposed **shortest
apex radius-descent theorem** says the blocker-circle radius is strictly smaller
than the apex-circle radius.

Writing the blocker center on the common perpendicular bisector as

```text
c = A + lambda(M-A),
```

where `M` is the midpoint of the shared chord, the MEC geometry is used to
prove `1 < lambda < 2`. Orthogonal decomposition then gives the strict radius
inequality. The two remaining points of the exact blocker row lie strictly
inside the apex circle.

For an exact `2+2+2` partition, every heavy trace therefore exports two row
points to a smaller radial level. In the all-heavy minimum case, the off-class
pairs either produce at least four distinct inward vertices or form a triangle
of three shared inward targets. A maximum-concentration assignment then gives a
closed load hierarchy `2 -> 3 -> 4` or escapes to a new heavier blocker.

### Round 11: saturated `2+2+2` in a cap of size eight

Status: `PAPER_PROOF_CANDIDATE`, long and not independently checked.

If the relevant closed cap has eight points, its strict interior is exactly the
six-point apex class. Hence all three heavy row centers lie on that class. The
center-membership map on the three trace pairs has either a directed 2-cycle or
3-cycle.

- A 2-cycle produces an equilateral target lying inside a hull triangle.
- A 3-cycle was reduced to angular parameters and two circle-intersection
  regimes, each forcing one shared inward target into the convex hull of three
  other vertices.

Candidate conclusion: a saturated inward `2+2+2` triangle forces the closed cap
to have at least nine vertices.

### Round 12: cap-nine semialgebraic normal forms

Status: `OPEN_BRIDGE` after a `PAPER_PROOF_CANDIDATE` reduction.

With a cap of size nine, exactly one row center lies outside the six-point apex
class. The remaining center-membership patterns reduce to:

1. a common-pair side-lobe system with four scalar parameters; or
2. a directed-chain system with four scalar parameters.

The center-membership 2-cycle was eliminated by the same equilateral
convex-hull argument. The two surviving systems were written as explicit
semialgebraic inequalities, but not excluded.

### Round 13: paired two-radius grid

Status: `PAPER_PROOF_CANDIDATE`, highest formalization priority.

The upstream formalization produced a source-return paired normal form with two
children:

- an apex-class joint deletion; or
- a saturated grid of two concentric four-point apex classes and two disjoint
  exact blocker shells, each shell taking two points from each class.

An analytic **two-radius two-shell reflection-grid theorem** was proposed. For
one shell, if the inner pair has angular half-width `a` and the outer pair has
half-width `c`, convexity and equal-radius algebra give

```text
a > c,
k cos(a-c) > 1,
k sin c > sin a.
```

A triangle-containment argument then says the inner pair of every other bridge
shell must lie strictly inside the angular interval of the first shell. Applying
this symmetrically to two shells gives impossible mutual strict containment.

Candidate conclusion: the paired two-radius grid is impossible independently
of the all-large packet.

### Round 14: radial nesting and a second common omission

Status: `PAPER_PROOF_CANDIDATE` plus `OPEN_BRIDGE`.

The Round 13 argument was strengthened into a **radial nesting lemma**:

> If one exact shell takes a pair from each of two concentric circles centered
> at a hull vertex `O`, then every other inner-circle hull vertex lies strictly
> between the two outer-circle shell points in angular order.

Two consequences were proposed:

1. **Two-bridge exclusion.** Two distinct shells cannot each take pairs from
   both concentric circles, because each inner interval would strictly contain
   the other.
2. **Lopsided two-shell exclusion.** A bridge shell cannot coexist with a
   second shell taking a pair from one circle and even one point from the other.

These yield a common-omission counting theorem: for two exact shells centered
away from a rich apex, at least two vertices from the apex's rich class system
lie outside both shells.

Applied to the upstream `PairedApexClassJointDeletion` packet, this produces a
second source omitted by both retained shells. The sibling branch reduces to:

```text
same-class two-source common deletion
or
exact 4+4 apex switch, one deleted source from each class.
```

This is the final frontier reached in the conversation.

## Results deliberately not promoted

The following are not added to `docs/claims.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` by this PR:

- the conic maximum principle;
- shortest-side two-center injectivity;
- tri-apex double-overlap;
- blocker-forest and synchronized-deletion lemmas;
- shortest-apex radius descent;
- cap-eight/cap-nine exclusions;
- two-radius grid and radial-nesting exclusions.

They are paper arguments or research reductions awaiting independent review,
formalization, or exact certificate support.

## Suggested review order

1. Variable-radius alternating-cycle theorem.
2. Alternating-rectangle lemma.
3. Fatal-pair uniqueness and the maximum-concentration blocker forest.
4. Shortest-side two-center injectivity.
5. Shortest-apex radius descent.
6. Two-radius two-shell radial nesting and lopsided exclusion.
7. Conic maximum principle.
8. Cap-eight and cap-nine saturated-triangle arguments.

The first six are the most likely to produce reusable, cardinality-independent
lemmas for the repository's current bridge agenda.
