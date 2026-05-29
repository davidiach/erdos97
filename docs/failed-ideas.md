# Failed or unsafe ideas

These entries are kept because their failure modes are structured enough to
prevent repeated work. They are not proof claims.

## 1. Extending 3-neighbor examples automatically

Failure mode: Danzer and Fishburn--Reeds are nearby `k=3` constructions, not
`k=4` constructions. Adding one more selected vertex per center adds another
equality constraint per center and may force new incidence/geometric
obstructions.[^lit]

## 2. End-neighbor / middle-neighbor / forest arguments

Failure mode: the proposed middle-neighbor graph need not be a forest. The
archive records an affine regular 24-gon construction producing a structured
cycle, so the cap regions can overlap or be incomparable rather than nested.[^forest]

## 3. Treating cyclic order as angular order about each center without hypotheses

Failure mode: boundary order gives angular order from a fixed hull vertex only
inside the vertex cone, and it does not imply that an equal-distance class is
one consecutive boundary interval. Bridge arguments using a consecutive-class
assumption need a separate proof.[^rank]

## 4. Assuming selected vertices around one center are limited to two

Failure mode: a circle centered at a polygon vertex can pass through more than
two other vertices of a strictly convex polygon. A local center/witness
configuration can lie in a semicircle without contradicting convexity.[^alg]

## 5. Circumcenter-inside-witness-hull contradiction

Failure mode: the circumcenter of a cyclic convex quadrilateral need not lie
inside the quadrilateral. Witnesses from a hull vertex may lie in a small arc,
placing the center outside their convex hull.[^alg]

## 6. Full coordinate symmetry for circulant patterns

Failure mode: incidence symmetry is not coordinate symmetry. Imposing full
coordinate symmetry often forces a regular-polygon or paired-distance
degeneracy and can kill the intended variable-radius problem.[^repo]

## 7. Mistaking the B12 near-miss for evidence of a counterexample

Failure mode: the best saved `B12_3x4_danzer_lift` residual improves as the
configuration approaches a boundary degeneration with three tight clusters.
It is useful as a diagnostic failure, not as a counterexample candidate.[^repo]

## 8. n=39 circulant branch

Failure mode: the pattern
`S_i={i+18,i-18,i+19,i-19}` mod 39 is equivalently
`S_i={i+18,i+19,i+20,i+21}`. Adjacent rows share three targets, violating the
two-circle cap before any numerical geometry is considered.[^n39]

## 9. Generic Jacobian rank as a proof

Failure mode: rank sampled at generic non-solutions does not control the rank
on the solution variety. At an exact solution, homogeneity adds the scaling
direction to the kernel, so a true solution must lie on a rank-drop locus.[^paper]

## 10. Forced indegree-four regularity outside n=7

Failure mode: Jensen saturation forces all indegrees to be 4 only in the
`n=7` equality case. For `n>=8` the count has slack, so double regularity and
cube-pattern uniqueness do not follow.[^syn]

## 11. n=8 solved by the cube witness pattern

Failure mode: the cube witness pattern is ruled out by an orthocenter
obstruction, but the archive does not prove that it is the only possible
`n=8` selected-witness incidence pattern. This failed route is now superseded
by the checked `n=8` incidence-completeness and exact-obstruction pipeline.

## 12. Direct counting rules out n<=12

Failure mode: the overstrong count missed a factor of two. The valid incidence
count gives only `n>=7`, not `n>=13` or a proof for all `n<=12`.[^syn]

## 13. Weak witness definition

Failure mode: four vertices that each participate in some repeated-distance
pair from a center are not the same thing as four vertices on one circle
centered at that vertex. Drafts using the weak definition cannot be routed as
proofs of Erdos #97.[^syn]

## 14. Counting all centered concyclic quadruples

Failure mode: one center can have many vertices on a single circle, producing
`Theta(n^4)` ordered quadruples from one local event. The corrected program
counts low-rank or critical centered 4-ties instead.[^alg]

## 15. Common-radius reduction

Failure mode: requiring one global radius solves only a stricter subcase. The
actual problem allows each center to choose its own radius, so common-radius
or unit-distance bounds must stay in a separate literature-risk lane.[^syn]

A related rejected shortcut claimed that the `2n-7` unit-distance construction
settles the uniform-radius subcase. The canonical synthesis records this as a
direction-of-bound error: `2n-7` is an Edelsbrunner--Hajnal lower-bound
construction, not the needed `< 2n` upper bound. Furedi's separate
convex-`n`-gon unit-distance work belongs to the upper-bound side of the
common-radius problem.[^canon]

## 16. Metric-linear rank obstruction without convexity

Failure mode: exact selected-distance equations, the strong linear row
condition `|S_i cap S_j| <= 1`, and local Jacobian rigidity modulo
similarities do not by themselves force a strictly convex polygon. The
24-point radial-alternating construction checked by
`scripts/verify_p24_metric_linear_nonconvex.py` satisfies every selected
equal-distance row and has exact Jacobian rank `44` in `48` coordinate
variables, but its signed turns alternate and it is not convex.

Use this as a negative control: a proof route based only on metric equations,
lifted affine circuits, row-linearity, or rank must fail on this construction.
Any successful impossibility proof must use strict convexity, cyclic-order
signs, one-sidedness, or another convexity-specific ingredient.[^p24]

## 17. Half-step two-orbit near-regular ansatz

Failure mode: the two concentric half-step-offset orbit construction can make
the selected four-distance equations hold exactly, but the same equations force
the inner radius below the alternating convexity threshold. In the notation of
`docs/two-orbit-radius-propagation.md`, the equations force
`S/R = sqrt(1 + sin^2 h) - sin h < cos h`, while strict convexity requires
`S/R > cos h`. This is a useful perturbative base, not a live counterexample
candidate.

A later incoming note broadened the lesson: even without the quarter-turn
selected-distance equations, the strictly convex alternating two-radius regular
family has strictly ordered paired distances at every vertex, so it cannot
produce four equal-distance witnesses. The same note also records that the
fixed selected-witness pattern of the exact concave alternating decagon has no
cyclic order satisfying the two-overlap crossing filter. See
`docs/two-orbit-radius-propagation.md`.

## 18. Local endpoint-control shortcut

Failure mode: the endpoint-descent program still needs the global Endpoint
Control Auxiliary Claim. It cannot be replaced by a purely local statement
that the two angular endpoints of a selected local circle class cannot both
have outside-filled equal-distance circles.

There is an exact rational strictly convex 9-point configuration with a
center `O`, four unit witnesses `A={A1,A2,A3,A4}`, and both angular endpoints
failing the local outside bound for the `m=4` case. In cyclic order

```text
O, L0, L1, A1, A2, A3, A4, U1, U0
```

take

```text
O  = (0,0)
L0 = (9/65, -129/130)
L1 = (1/5, -11/10)
A1 = (3/5, -4/5)
A2 = (4/5, -3/5)
A3 = (4/5, 3/5)
A4 = (3/5, 4/5)
U1 = (1/5, 11/10)
U0 = (9/65, 129/130).
```

Then `A1,A2,A3,A4` are exactly the four displayed unit points from `O`.
The endpoints `A1` and `A4` both have two equal-distance points outside
`A union {O}`:

```text
|A1L0|^2 = |A1L1|^2 = 1/4,
|A4U0|^2 = |A4U1|^2 = 1/4.
```

The outside points are not on the unit circle around `O`:

```text
|OL0|^2 = |OU0|^2 = 261/260,
|OL1|^2 = |OU1|^2 = 5/4.
```

The cyclic-order turn determinants are exactly positive:

```text
1161/4225, 3/65, 4/65, 1/50, 6/25,
6/25, 1/50, 4/65, 3/65.
```

This is a genuine local strictly convex obstruction to that shortcut.

This does not disprove the actual Endpoint Control Auxiliary Claim, because
the configuration is not a full counterexample and does not impose the
minimality or global badness hypotheses.

The shortcut remains false even if both endpoints are themselves locally bad.
In cyclic order

```text
O, X1, L0, L1, X2, A1, A2, A3, A4, Y2, U1, U0, Y1
```

take the same `O,A1,A2,A3,A4,L0,L1,U0,U1` and add

```text
X1 = (3/25, -47/50)
X2 = (69/290, -166/145)
Y2 = (69/290, 166/145)
Y1 = (3/25, 47/50).
```

All cyclic-order turn determinants remain exactly positive. The center `O`
has the same exact four-point unit class `A={A1,A2,A3,A4}`, while endpoint
`A1` has four outside points at squared distance `1/4`,

```text
X1, L0, L1, X2,
```

and endpoint `A4` has four outside points at squared distance `1/4`,

```text
Y1, U0, U1, Y2.
```

Thus endpoint badness plus the local critical circle class still does not
supply endpoint control. Any proof must use additional global
minimal-counterexample information, not only these local hypotheses.

## 19. Unproved centered-circle incidence lemmas

Claim attempted: prove the full problem by choosing one rich circle around
each bad vertex and applying a global incidence bound, such as:

- every one-circle-per-center system has at most `3n` incidences;
- every one-circle-per-center system has at most `4n-4` incidences;
- every favorite-distance digraph of a convex `n`-gon has at most `4n-4`
  directed edges;
- end/middle incidence charging gives one of those bounds by assigning middle
  events injectively to polygon sides.

Why it seemed plausible: a selected circle at each center converts a
hypothetical all-bad polygon into at least `4n` directed incidences. Any
unconditional bound below `4n` would immediately prove Erdos Problem #97.

Failure mode: these incidence lemmas are not established in this repository
and should not be quoted as standard without an independent source and exact
hypotheses. The actual Altman theorem used here is the diagonal-order sum
inequality in `docs/altman-diagonal-sums.md`, not a centered-circle incidence
theorem. The attempted sketches typically conflate boundary order with angular
order around arbitrary centers, assume equal-radius vertices form one
controlled boundary interval, or use unsupported middle-incidence
injectivity. Stronger tangent/support versions are explicitly false, as
recorded in the algebraic and semicircle correction notes.[^alg]

Weaker version: a new incidence theorem with a complete proof and precise
strict-convexity hypotheses would be highly valuable. Until then, the
favorite-distance and Perles/Altman-style incidence shortcuts are guardrails,
not proof routes.

Current status: failed proof shortcut / provenance guardrail.

[^lit]: Public consolidation: `public-provenance.md#literature-digest`.
[^forest]: Public consolidation: `public-provenance.md#forest-lemma-failure`.
[^rank]: Public consolidation: `public-provenance.md#rank-and-bridge-status`.
[^alg]: Public consolidation: `public-provenance.md#algebraic-and-semicircle-corrections`.
[^repo]: Public consolidation: `public-provenance.md#repository-handoff-and-claim-taxonomy`.
[^n39]: Public consolidation: `public-provenance.md#n39-circulant-degeneracy`.
[^paper]: Public consolidation: `public-provenance.md#paper-style-verifier-review`.
[^syn]: Public consolidation: `public-provenance.md#canonical-synthesis`.
[^canon]: Source file: `docs/canonical-synthesis.md`.
[^p24]: Public consolidation: `public-provenance.md#p24-metric-linear-negative-control`.
