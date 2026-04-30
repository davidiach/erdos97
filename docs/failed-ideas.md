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

[^lit]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/01_USEFUL_FINDINGS_DIGEST.md`.
[^forest]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/11_forest_lemma_counterexample_review.md`.
[^rank]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/03_RANK_AND_BRIDGE_STATUS.md`.
[^alg]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/04_algebraic_and_semicircle_corrections.md`.
[^repo]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/16_repo_handoff_and_claim_taxonomy.md`.
[^n39]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/12_n39_circulant_degeneracy.md`.
[^paper]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/05_rank_scaling_and_verifier_review.md`.
[^syn]: Source file: `erd archive/outputs/erdos97_synthesis.md`.
[^canon]: Source file: `docs/canonical-synthesis.md`.
[^p24]: Source files: `erd archive/outputs/data/1/linear_case_geometry_handoff.md` and `erd archive/outputs/data/1/verify_24_point_near_counterexample.py`.
