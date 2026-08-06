# Frontier and failed-route map from the 2026-08-06 conversation

Status: `RESEARCH_NOTE / DIAGNOSTIC_ONLY / OPEN_BRIDGE`

This file records what the conversation learned not to assume, how its paper
arguments line up with the separate Lean formalization project, and the next
proof tasks suggested by the final rounds. It does not change the repository
claim that no general proof and no counterexample are known here.

## 1. Exact refutation of the crossing affine-rigidity shortcut

A proposed completion was:

> For cyclically ordered points, if every selected four-set excludes its center,
> row intersections have size at most two, every two-point overlap crosses the
> center chord, and the selected digraph is strongly connected, then the affine
> circuit matrix has rank `n-3`.

The conversation found the following 12-row cyclic incidence system:

```text
0 : {1,3,9,11}
1 : {0,3,7,10}
2 : {5,6,10,11}
3 : {1,4,8,11}
4 : {0,3,5,8}
5 : {1,2,6,7}
6 : {4,5,7,8}
7 : {2,6,8,10}
8 : {1,4,6,9}
9 : {3,6,8,11}
10: {5,7,9,11}
11: {0,2,4,10}
```

It was reported to have all the proposed combinatorial properties. Put the
points on the parabola

```text
p_j=(j,j^2).
```

The corresponding affine-circuit matrix has reported exact rank

```text
8 = 12-4,
```

not `12-3`. Besides the affine kernel vectors, it annihilates the parity vector

```text
h_j = 0 for even j,
h_j = 1 for odd j.
```

Status: `DIAGNOSTIC_ONLY` in this PR because no independent checker is added.
The example is still important: crossing order and strong connectivity alone
cannot supply the missing rank lower bound.

A future exact verifier could be very small: construct the parabola circuit
coefficients with rational arithmetic, verify all overlap-crossing predicates,
compute rank, and check the parity kernel.

## 2. Local three-cycle geometry is realizable

Another proposed terminal said that three points on one apex circle cannot have
their three pairwise-bisector centers arranged on the same strict convex cap.
The conversation parameterized

```text
a=e^{0i},
b=e^{ui},
c=e^{(u+v)i}
```

and the three bisector-center rays

```text
arg x_ab = u/2,
arg x_bc = u+v/2,
arg x_ac = (u+v)/2.
```

For unequal positive `u,v`, suitable radial positions make the local
configuration strictly convex. This is not a counterexample to Erdős 97; it
only refutes the local claim that convexity automatically kills the directed
three-cycle.

Status: `DIAGNOSTIC_ONLY`; an exact coordinate certificate should be recorded
before reuse.

## 3. First-moment separation is blocked by a positive equilibrium

The stationary six-bisector identity in the companion lemma document proves
that the oriented witness chords admit a positive combination equal to zero.
Therefore the following proof pattern cannot work:

```text
choose one orientation for every relevant bisector/chord
  -> find a linear functional positive on all of them
  -> positive sum cannot vanish.
```

The positive sum does vanish for stationary weights. Any successful global
summation must use nonlinear information.

## 4. Incidence-only capture is formally insufficient upstream

At upstream commit
[`7aef68f8`](https://github.com/mysticflounder/erdos-97-96-formalization/commit/7aef68f8cd91009071b62836398085a045d28047),
a 17-point kernel-checked finite countermodel was added for 39 enumerated
incidence facts reachable at one R-branch capture frontier. The model proves
that those facts are jointly consistent while the proposed capture packet is
empty.

This does not say the geometric branch is realizable. It says that any proof of
the capture packet must use information outside that incidence signature:
Euclidean metric, convex order, MEC/cap geometry, richer exact-row data, or a
new global coupling theorem.

This aligns with the conversation's repeated experience: abstract selected-row
systems often survive until an ordinary-distance or cap-order inequality is
inserted.

## 5. The Rigid221 off-class subsystem remains only diagnostic

The upstream `Rigid221` pentagon oracle reported SAT models for a seven-label
row-trace/apex-circle subsystem with an off-class blocker. Later audit commits
correctly narrowed the interpretation: SAT models only the encoded subsystem,
not the full Lean leaf and not the complete geometric packet.

Relevant commits include:

- [`e317d561`](https://github.com/mysticflounder/erdos-97-96-formalization/commit/e317d56144c33bae46865f41ba29165cc44383cb), exact-oracle mining;
- [`41fda332`](https://github.com/mysticflounder/erdos-97-96-formalization/commit/41fda33228a0f702abd8f975d8da66ce7fd6d0a9), off-class subsystem probe;
- [`52e1e775`](https://github.com/mysticflounder/erdos-97-96-formalization/commit/52e1e775220e38be798e4c811da13b3b71695842), evidence-claim corrections.

Lesson: no future note should infer full-leaf realizability, impossibility, or
route exhaustion from one relaxed SAT/UNSAT probe without proving the exact
logical relation between the encoding and the source hypotheses.

## 6. Other rejected or bounded routes

### Pure local circle geometry

Single two-circle bumps, mutual omissions, and several cap-local crossing
patterns were found to be locally realizable. A contradiction must use more
than one interacting row, global minimality, or all-center information.

### Pure affine rigidity

The rank upper bound is valid, but all attempted combinatorial lower bounds
were either false or lacked a propagation theorem through one-point overlaps.
Strict metric/Kalmanson information is essential.

### Pure cap counting

Several cap-cardinality inequalities become equalities on the hard residuals.
Counting can force small normal forms, but does not by itself close them. The
upstream audit of the Rigid221 pentagon likewise found that the sharp cross-cap
one-hit bound is unavailable when the blocker and class live at the same cap
index.

### Another unconstrained finite incidence search

The repository already has many fixed-cardinality and fixed-halo searches. The
conversation repeatedly converged on the same lesson: the missing step is a
geometric entry lemma or a reusable ordinary-distance terminal, not a larger
unconstrained incidence enumeration.

## 7. Formalization crosswalk for the final paired branch

The separate Lean project added a source-return paired normal form at commit
[`5f2461ab`](https://github.com/mysticflounder/erdos-97-96-formalization/commit/5f2461ab081efff055e2bada2ffae5c2ab389c67).
It splits the paired common-deletion branch into:

```text
PairedApexClassJointDeletion
or
PairedTwoRadiusGrid.
```

The grid packet contains:

- two distinct exact first-apex classes of cardinality four;
- two disjoint exact critical shells;
- each shell meeting each class in exactly two named points;
- the union of the two shells equal to the union of the two classes;
- reflection/separation identities for all four shell-class pairs.

The later cap-placement producer at commit
[`3b71763e`](https://github.com/mysticflounder/erdos-97-96-formalization/commit/3b71763eebc3d9b3e4b9b8333a2027ad15978571)
pins which grid points lie in the strict first-cap interior and which escape to
the adjacent caps.

At the inspected source revision, the two relevant open leaves were:

```text
false_of_pairedCommonDeletion_apexClassJointDeletion_triApexAllLarge_core
false_of_pairedCommonDeletion_twoRadiusGrid_triApexAllLarge_core
```

The conversation's Round 13/14 candidates map directly onto these leaves:

```text
PairedTwoRadiusGrid
  -> radial nesting / two-bridge exclusion
  -> False.

PairedApexClassJointDeletion
  -> second point omitted by both retained shells
  -> same-class two-source common deletion
     or exact 4+4 apex switch.
```

No claim is made here that these paper arguments have been formalized or that
the leaves are closed in the upstream repository.

## 8. The exact frontier after the final round

Let `p` be the first MEC apex and let `K_x,K_y` be the two retained exact
blocker shells.

### Grid child

The proposed radial-nesting theorem should prove:

```text
if each of K_x,K_y takes a pair from each of two concentric p-circles,
then the inner angular interval of K_x strictly contains that of K_y,
and vice versa.
```

That is impossible. This is the most direct next formalization target.

### Joint-deletion child

The packet already gives one source `z` on a rich `p`-class with

```text
z notin K_x,
z notin K_y.
```

The proposed two-shell common-omission theorem should supply a second such
source `w`. Then:

1. If `z,w` lie on the same rich class, deleting both preserves the other rich
   class or leaves four points in a six-point class, while both blocker shells
   remain untouched.
2. Otherwise the hard residue should be exactly two four-point `p`-classes,
   one deleted source from each, with both retained blocker shells surviving.

The remaining theorem is a deletion-semantic or Kalmanson contradiction for
that two-source packet.

## 9. Recommended next proof prompt

The following prompt is the best compressed continuation of the conversation.
It deliberately forbids restarting from weak incidence data.

> **Resolve the paired source-return frontier of Erdős Problem 97.**
>
> Work from the exact geometric packets `PairedTwoRadiusGrid` and
> `PairedApexClassJointDeletion`; do not restart from abstract selected rows.
> Preserve the global status: no proof is complete until both children are
> rigorously eliminated.
>
> First prove or refute the radial-nesting theorem in full generality. Let `O`
> be a hull vertex and let two concentric circles centered at `O` contain polygon
> vertices. If a circle centered at another hull vertex meets each concentric
> circle in a pair of polygon vertices, prove the exact angular confinement of
> every other inner-circle hull vertex. Use only explicit Euclidean equalities,
> convex order, and triangle-containment inequalities. Test every step against
> symbolic and numerical convex configurations before using it.
>
> If the theorem is valid, formalize the symmetric two-bridge contradiction and
> apply it to `PairedTwoRadiusGrid` without using unnecessary all-large
> hypotheses.
>
> Next prove the lopsided variant: a bridge shell cannot coexist with another
> shell taking a pair from one concentric class and one point from the other.
> Use it to prove that two exact retained shells leave at least two common
> omissions in the rich apex-class system.
>
> Feed the second omission into `PairedApexClassJointDeletion`. Derive an
> exhaustive source-clean split into a same-class two-source common deletion or
> an exact `4+4` apex switch. Then close both children by an existing
> Kalmanson/two-circle/minimal-deletion terminal or prove the smallest new
> terminal required.
>
> Do not infer anything from strong connectivity, pairwise intersection bounds,
> or relaxed SAT models alone. Every bridge must explicitly consume metric or
> cap-order information absent from the known incidence countermodels.
>
> Success means a proof of both paired leaves with no new unproved helper. If a
> proposed lemma fails, provide an exact countermodel and immediately replace
> the route.

## 10. Suggested implementation sequence

### Task A: independently audit radial nesting

Acceptance criteria:

- derive the coordinate inequalities without assuming the chord midpoint lies
  on the segment between the two centers unless proved;
- prove the angular confinement for all positions allowed by an open semicircle;
- explicitly handle coincident endpoints, overlapping shell pairs, and blocker
  coincidence with class points;
- produce either a short exact proof or exact coordinates refuting the lemma.

### Task B: formalize the grid contradiction

Acceptance criteria:

- consume only fields actually present in `PairedTwoRadiusGrid`;
- avoid assuming a cyclic order not derived from convexity and separation;
- remove the grid `sorry` without adding another open child;
- record the exact theorem dependency and `#print axioms` output upstream.

### Task C: prove two-shell common omission

Acceptance criteria:

- cover both apex-rich profiles: one class of size at least six, or two classes
  of size at least four;
- use the two-bridge and lopsided exclusions to rule out coverage of all but one
  rich-class point;
- name two distinct omissions and prove their actual blockers differ from the
  two retained blockers.

### Task D: close the two-source deletion packet

Acceptance criteria:

- preserve exact source membership and deletion-survival semantics;
- split exhaustively into same-class survival and exact `4+4` switch;
- connect each branch to a source-valid ordinary-distance or minimal-deletion
  contradiction;
- do not treat a finite fixed-cardinality certificate as universal closure.

## 11. What not to repeat

- Do not reassert crossing affine rigidity.
- Do not claim convexity alone kills a local three-bisector cycle.
- Do not search for a linear functional positive on every oriented witness
  chord.
- Do not treat a SAT relaxed subsystem as a full geometric realization.
- Do not infer the desired capture packet from the 39-fact incidence interface
  refuted by the 17-point formal countermodel.
- Do not enlarge the finite incidence search unless the new layer is tied to a
  named metric bridge and has a precise promotion contract.

## 12. Evidence boundary

The mathematical arguments in the companion files are useful research inputs,
not accepted repository claims. The PR intentionally leaves `README.md`,
`STATE.md`, `RESULTS.md`, `docs/claims.md`, and `metadata/erdos97.yaml`
unchanged.
