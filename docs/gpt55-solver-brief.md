# GPT-5.5 Solver Brief

Status: solver-steering prompt context only; not mathematical evidence.

Use this brief before asking GPT-5.5 Pro, or any other LLM solver, to work on
Erdos Problem #97. Its job is to prevent repeated attempts at already-covered
routes and to steer the model toward genuinely new progress. The longer
repository synthesis and ledgers remain the source for details; this file is
the short anti-loop layer to put first in the context window.

## Mission

Try to make real progress on Erdos Problem #97:

```text
Does every strictly convex polygon have a vertex with no other 4 vertices
equidistant from it?
```

No general proof is currently claimed. No counterexample is currently claimed.
The official/global status remains falsifiable/open unless it is manually
rechecked and updated from the official page.

A useful solver response should produce one of:

- a precise new lemma with hypotheses, proof, and failure modes;
- a bridge theorem candidate reducing arbitrary or minimal counterexamples to
  a restricted witness structure;
- a reusable local obstruction template extracted from an existing finite
  artifact;
- an independent verifier or audit plan for an important finite artifact;
- a new selected-witness family that survives the current filters and has a
  concrete exactification plan;
- a negative result showing that a current live route cannot work.

Do not return broad motivational discussion. Do not re-prove already recorded
small cases unless the task is explicitly an audit or formalization task.

## Mandatory Novelty Check

Before proposing a proof attempt, answer these questions explicitly:

```text
1. Which known failed route does this resemble?
2. What new ingredient avoids that route's known failure mode?
3. What exact lemma, certificate, or computation would make the idea real?
4. What would falsify this idea quickly?
```

If the answer to question 2 is "nothing new", abandon the route and choose a
different one.

## Hard Status Boundaries

- Treat `n <= 8` as closed in the repo-local, machine-checked selected-witness
  sense. It is still recommended for independent audit before public
  theorem-style use, but it is not a live target for a new proof attempt.
- Treat `n=9` as heavily attacked and review-pending. Do not try to re-solve it
  from scratch unless auditing the checker or mining reusable vertex-circle
  templates.
- Treat `n=10` as a draft review-pending singleton-slice artifact. Do not
  promote it beyond an audit target.
- Treat B12, C13 Sidon, C19 skew, P18, P24, and the recorded C25/C29 fixed
  orders as retired or diagnostic fixed-pattern leads, not live counterexample
  candidates.
- Numerical near-misses are not counterexamples. A counterexample claim needs
  exact coordinates, algebraic certificates, interval certificates, SMT
  certificates, or a formal proof verifying selected equal distances and strict
  convexity.

## Selected-witness Framework

A hypothetical counterexample with vertices `p_0,...,p_{n-1}` induces selected
4-witness rows

```text
S_i subset {0,...,n-1} \ {i},   |S_i| = 4,
```

such that all squared distances `|p_i-p_j|^2`, `j in S_i`, are equal. The
radius and selected witnesses may depend on `i`. The relation `i -> S_i` need
not be symmetric: `0 in S_1` does not imply `1 in S_0`.

This formulation is safe for impossibility proofs: if no selected-witness
system of a certain type can be realized by a strictly convex polygon, then no
counterexample of that type exists.

## Core Facts To Reuse

Do not re-discover these as new ideas.

### Two-circle cap

For distinct centers `a,b`,

```text
|S_a cap S_b| <= 2.
```

Otherwise two distinct Euclidean circles would share three selected vertices.

### Pair-sharing cap

For a fixed unordered witness pair `{u,v}`, at most two centers can select both
`u` and `v`. All such centers lie on the perpendicular bisector of segment
`uv`, and a line meets the boundary of a strictly convex polygon in at most two
vertices.

### Crossing-bisector lemma

If

```text
S_x cap S_y = {a,b},
```

then line `xy` is the perpendicular bisector of segment `ab`. The midpoint of
`ab` lies on line `xy`; because it also lies inside the polygon and a non-edge
chord line meets a strictly convex polygon in its chord segment, the chords
`xy` and `ab` cross. In particular, adjacent row-pairs in the cyclic order have
intersection size at most `1`.

### Sharpened incidence lower bound

Let `d_v = #{i : v in S_i}`. Since every row has size 4,

```text
sum_v d_v = 4n.
```

Convexity of `binom(d,2)` gives

```text
sum_v binom(d_v,2) >= 6n.
```

Double-counting row intersections gives

```text
sum_v binom(d_v,2) = sum_{i<j} |S_i cap S_j|.
```

The `n` adjacent row-pairs contribute at most `1` each, and the remaining
`n(n-3)/2` nonadjacent row-pairs contribute at most `2` each. Thus

```text
6n <= n + 2*(n(n-3)/2) = n(n-2),
```

so any selected-witness counterexample has `n >= 8`.

## Already Covered Finite Cases

- `n <= 6`: excluded by direct two-circle cap arguments.
- `n=7`: excluded. The Fano/perpendicularity-cycle enumeration is retained as
  a structural artifact, but the sharpened crossing count already gives a
  shorter exclusion of `n=7`.
- `n=8`: repo-local machine-checked finite artifact. Incidence enumeration
  reduces to 15 canonical classes; exact cyclic-order, perpendicular-bisector,
  equal-distance, duplicate-vertex, collinearity, Groebner, and strict-convexity
  checks kill all 15. Class `14` remains the delicate audit target.
- `n=9`: review-pending vertex-circle exhaustive checker. It finds 184 complete
  selected-witness assignments after pair/crossing/count filters, then kills
  all 184 by exact vertex-circle self-edge or strict-cycle obstructions.
- `n=10`: draft review-pending singleton-slice artifact. All 126 row0
  singleton slices report zero full assignments under the same necessary
  filters, but the package needs independent audit or compact replayable
  certificates.

## Named Failure Modes

These are not merely old ideas. They are traps a strong solver will naturally
fall into unless it names the new ingredient that avoids the trap.

### F1. The `k=3` Transfer Trap

Seductive idea: Danzer and Fishburn-Reeds show nearby `k=3` constructions, so
try to add one more equidistant witness at each vertex.

Failure mode: adding the fourth selected witness adds a genuine new equality
constraint at every center. The known `k=3` examples do not automatically
extend, and their geometry can be killed by exact selected-witness constraints.

Only revisit if: the argument explains why a `k=3` construction family has an
exact `k=4` extension, with selected rows and strict convexity verified.

### F2. The Middle-neighbor Forest Trap

Seductive idea: choose middle witnesses or nearest arcs around each center and
form a graph that should be acyclic by nesting or monotonicity.

Failure mode: the proposed middle-neighbor graph need not be a forest. The
archive records affine regular examples producing structured cycles. Cap
regions can overlap or be incomparable rather than nested.

Only revisit if: the graph has a new convexity-specific invariant that forbids
the known affine-regular cycle behavior.

### F3. The Boundary-order Equals Local-consecutive Order Trap

Seductive idea: because all vertices are in cyclic boundary order, assume that
selected equal-distance witnesses around a center form one consecutive interval
or that every boundary-order comparison is a valid angular comparison.

Failure mode: boundary order agrees with angular order from a hull vertex only
under the correct vertex-cone hypotheses. Equal-distance classes need not be
consecutive boundary intervals.

Only revisit if: the proof supplies a separate lemma forcing consecutiveness or
valid angular containment for the specific selected row.

### F4. The At-most-two-on-a-centered-circle Trap

Seductive idea: a circle centered at a polygon vertex should meet a convex
polygon in at most two other vertices.

Failure mode: false. A circle centered at a hull vertex can pass through more
than two other vertices of a strictly convex polygon.

Only revisit if: the argument uses two different circles, a line/perpendicular
bisector, or another exact locus with the right intersection bound.

### F5. The Circumcenter-hull Fallacy

Seductive idea: if four witnesses lie on a circle centered at a polygon vertex,
then the center should lie inside the convex hull of the witnesses, producing a
hull contradiction.

Failure mode: the circumcenter of a cyclic convex quadrilateral need not lie
inside that quadrilateral. Witnesses from a hull vertex may lie in a small arc,
placing the center outside their convex hull.

Only revisit if: the proof establishes a no-semicircle condition, or another
exact reason the center lies in the witness hull.

### F6. The Incidence-symmetry Implies Coordinate-symmetry Trap

Seductive idea: for circulant or symmetric incidence patterns, impose matching
coordinate symmetry and solve a lower-dimensional ansatz.

Failure mode: incidence symmetry is not coordinate symmetry. Imposing full
coordinate symmetry often forces a regular-polygon or paired-distance
degeneracy and can erase the variable-radius problem.

Only revisit if: the ansatz is proved forced for every realization, not merely
convenient.

### F7. The Numerical Near-miss Trap

Seductive idea: a tiny residual with positive-looking convexity margin is close
to a counterexample, so continue optimizing or exactify it.

Failure mode: the historical best `B12_3x4_danzer_lift` near-miss improves by
degenerating into clusters and is exactly killed as a fixed selected-witness
pattern by mutual-rhombus midpoint equations.

Only revisit if: the candidate satisfies the verification contract and has an
exactification path; otherwise it is diagnostic data only.

### F8. The Generic Rank Trap

Seductive idea: show the distance-equality Jacobian has too much rank at a
generic configuration, so the equations cannot have a solution.

Failure mode: rank at generic non-solutions does not rule out special rank-drop
solutions. At an exact solution, homogeneity adds a scaling direction to the
kernel, so a true solution lies on a rank-deficient locus.

Only revisit if: the proof controls the rank on the actual solution variety or
uses convexity to rule out the rank-drop locus.

### F9. The Indegree-four Overgeneralization Trap

Seductive idea: since small saturated cases force selected indegree 4, assume
all vertices have selected indegree 4 in general.

Failure mode: sum of indegrees is always `4n`, but uniform indegree 4 follows
only in special saturated cases such as `n=8` after the sharpened count and
pair-sharing cap. It is not automatic for larger `n`.

Only revisit if: the proof identifies a new saturation condition or minimality
argument forcing regularity.

### F10. The Cube-pattern-only Octagon Trap

Seductive idea: the cube witness pattern for `n=8` is beautiful and obstructed,
so it must represent the octagon case.

Failure mode: the cube pattern is only one pattern. The complete `n=8` result
requires the 15-class incidence enumeration and exact survivor obstruction.

Only revisit if: the task is to audit or simplify the complete 15-class
pipeline, not to substitute the cube pattern for it.

### F11. The Naive Concyclic-quadruple Count Trap

Seductive idea: count all centered concyclic quadruples globally and compare to
convexity/incidence upper bounds.

Failure mode: one large distance class at one center can create `Theta(n^4)`
quadruples. The corrected route must count critical 4-ties, low-rank events,
or selected rows, not all quadruples indiscriminately.

Only revisit if: the counted object cannot blow up from one large distance
class.

### F12. The Common-radius Trap

Seductive idea: reduce to unit-distance or one common radius and apply convex
polygon unit-distance bounds.

Failure mode: Erdos #97 allows a different radius at each center. A
common-radius theorem solves only a stricter subproblem.

Only revisit if: the proof explains why a hypothetical counterexample can be
converted to one with a common radius, or explicitly stays in the subproblem.

### F13. The Pure Fragile-cover Hypergraph Trap

Seductive idea: minimality gives a fragile-cover witness system, so prove no
such hypergraph exists.

Failure mode: pure fragile-cover hypergraph constraints are too weak. A
block-6 abstract family passes the current cover and crossing checks, and two
disjoint blocks still pass the full-row extension diagnostic.

Only revisit if: the new condition is genuinely geometric, such as critical
radius ordering, row-circle constraints, vertex-circle monotonicity, or
interaction between fragile rows and full selected rows.

### F14. The More-fixed-patterns Trap

Seductive idea: kill one more attractive sparse, circulant, or fixed-order
selected-witness pattern.

Failure mode: exact fixed-pattern obstructions are valuable for retiring leads
but do not solve the global problem unless a bridge shows arbitrary
counterexamples reduce to that family.

Only revisit if: the obstruction produces a reusable template or strengthens a
bridge from arbitrary counterexamples.

## Retired Or Diagnostic Leads

Do not treat these as live counterexample leads.

- `B12_3x4_danzer_lift`: historical near-miss; exactly killed as a fixed
  selected pattern by mutual-rhombus midpoint equations.
- `C13_sidon_1_2_4_10`: fixed abstract pattern killed across all cyclic orders
  by exact two-inequality Kalmanson order search.
- `C19_skew`: fixed abstract pattern killed across all cyclic orders by the Z3
  Kalmanson certificate.
- `P18_parity_balanced`: killed by crossing constraints plus vertex-circle
  strict-cycle obstruction.
- `P24_parity_balanced`: killed by finite cyclic crossing CSP.
- `C25_sidon_2_5_9_14`: recorded fixed-order survivor is killed by
  vertex-circle and Altman filters; use as a diagnostic for weaker filters.
- `C29_sidon_1_3_7_15`: one fixed order escaped weaker diagnostics but is now
  killed by a 165-inequality fixed-order Kalmanson/Farkas certificate. This is
  not an all-order C29 obstruction.

The sparse/Sidon record is useful mainly as a negative-control family for new
filters. Avoid saying that every Sidon-style counterexample is exhausted unless
a precise family and exact all-order certificate are named.

## Current Live Frontiers

Prefer work that changes:

```text
This selected-witness pattern or finite slice is impossible.
```

into:

```text
Every hypothetical counterexample must contain or reduce to one of these
impossible structures.
```

### L1. Extract reusable vertex-circle lemmas

The `n=9` vertex-circle checker is review-pending, but its 184 obstructions
compress into 9 self-edge templates and 3 strict-cycle templates. This is a
promising source of small local lemmas.

Good output: a proof-facing statement with explicit incidence and cyclic-order
hypotheses that forces a selected-distance quotient self-edge or strict cycle.

Bad output: "the `n=9` checker proves the theorem" or another full enumeration.

Start from:

- `docs/n9-vertex-circle-template-lemma-catalog.md`
- `data/certificates/n9_vertex_circle_template_lemma_catalog.json`
- focused T01/T02/T03/T04/T05/T06/T07/T08 self-edge packets and T10/T11/T12
  strict-cycle packets.

### L2. Strengthen the minimal fragile-cover bridge

Every minimal counterexample admits a fragile-cover witness system, but current
hypergraph constraints are insufficient. The block-6 family is the standing
negative control.

Good output: a new necessary geometric condition for fragile covers, tested
against block-6 controls and full-row extension survivors.

Bad output: another purely hypergraph contradiction that fails on the known
block-6 escape.

Start from:

- `docs/minimal-fragile-cover-bridge.md`
- `src/erdos97/fragile_hypergraph.py`
- `scripts/check_fragile_hypergraph.py`

### L3. Turn Kalmanson certificates into templates

C13 and C19 all-order Kalmanson certificates are fixed-pattern results, but the
inverse-pair clauses may contain reusable local order obstructions.

Good output: a classified template explaining which selected-distance quotient
structures make the Kalmanson inequalities cancel.

Bad output: a smaller certificate for one already-retired fixed order unless it
reveals a reusable lemma.

Start from:

- `docs/kalmanson-two-order-search.md`
- `scripts/check_kalmanson_two_order_search.py`
- `scripts/check_kalmanson_two_order_z3.py`

### L4. Audit important finite artifacts

Independent audit is real progress when it treats checked-in JSON/certificates
as input data instead of generated truth.

Best targets:

- `n=8` class `14` strict-convexity obstruction;
- `n=8` incidence and exact survivor artifacts;
- review-pending `n=9` vertex-circle checker;
- draft `n=10` singleton-slice package.

Good output: a standalone verifier, smaller certificate, or independent
replay path.

Bad output: rerunning the same generator and calling it independent.

### L5. Find a new survivor family with exactification value

A new family is useful only if it survives current exact filters and teaches
something about missing bridge conditions.

Required output:

- selected rows;
- cyclic order or order family;
- which current filters it passes;
- why it is not one of the retired leads;
- exactification plan or a reason it is a negative control.

Numerical optimization alone is not progress.

## Counterexample Claim Gate

Do not claim a counterexample unless all of the following exist:

- exact coordinates or exact algebraic parameterization;
- exact verification of every selected equal-distance row;
- exact verification of strict convexity and distinct vertices;
- selected 4-sets `S_i` for every center;
- reproducible independent checker;
- explanation of how the incidence pattern avoids the known exact filters.

Floating-point coordinates, small residuals, failed optimizers, or positive
convexity margins are not enough.

## Recommended Prompt Wrapper

Use wording like this when giving the model the long synthesis after this
brief:

```text
Read the solver brief first. Then use the synthesis as reference.

Your task is not to summarize the repository. Your task is to propose one
genuinely new route toward Erdos Problem #97 or one precise reason a live route
cannot work.

Before proposing any proof, run the mandatory novelty check. If your idea
resembles a named failure mode and you do not have a new ingredient, stop and
choose another route.

Do not claim a proof or counterexample. Output a concrete lemma, bridge
candidate, verifier plan, obstruction template, or survivor family, with exact
hypotheses and a falsification test.
```

## Useful Source Files

- Current status: `STATE.md`, `RESULTS.md`, `metadata/erdos97.yaml`
- Claim taxonomy: `docs/claims.md`
- Failed routes: `docs/failed-ideas.md`
- Strategy: `docs/codex-strategy-instructions.md`
- Review priorities: `docs/review-priorities.md`
- Verification contract: `docs/verification-contract.md`
- `n=8`: `docs/n8-incidence-enumeration.md`,
  `docs/n8-exact-survivors.md`
- `n=9`: `docs/n9-vertex-circle-exhaustive.md`,
  `docs/n9-vertex-circle-template-lemma-catalog.md`
- `n=10`: `docs/n10-vertex-circle-singleton-slices.md`
- Fragile cover: `docs/minimal-fragile-cover-bridge.md`
- Kalmanson: `docs/kalmanson-two-order-search.md`,
  `docs/round2/kalmanson_distance_filter.md`
