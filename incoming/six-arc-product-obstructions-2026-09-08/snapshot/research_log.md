# Research log — Erdős #97, 8 September 2026

This is a chronological record of this session, not a claim of an unrestricted
solution. Paper proofs remain subject to independent mathematical review.
Floating-point searches are exploration, never nonexistence certificates.

## 1. Source audit

Read the repository's PR #941 publication audit, exact 27-point product control,
original unbounded six-exception family, and nine-point nonconvex control.
The previously quoted nine-orbit table is rejected by an existing exact
right-angle containment rule. It was not treated as a live candidate.
Public literature searches found the exact problem still listed as open; this
status is context, not an argument against attempting a solution.

## 2. Exact metric product and local dimension

Reconstructed the 27-point seed and its 108 named incidences in float64.
Maximum equation residual: 7.11e-15; computed hull: 18 vertices.
The full 81-by-54 equality Jacobian has numerical rank 48 at threshold 1e-9;
the C3-restricted 18-by-18 Jacobian has numerical rank 14. These are numerical
ranks only. Sources and output: `search/product_probe.py`,
`reports/product_probe.json`.

## 3. Four-arrow product completion

For own-side arrows x->a,b and a,b->c, the two circle-intersection branches are
c=ab/x and c=-2x. The latter places x at the midpoint of two vertices of T(c),
and is impossible in strict convex position. This yielded an exact product
identity under convexity, rather than an assumed product parametrization.

A 20,000-sample diamond probe found many fully convex 12-point same-half-plane
diamonds. Therefore a blanket ban on four-arrow diamonds is false. An additional
60,000-sample mixed-half-plane probe found no full 12-point hull (44,952 hulls
of size 9 and 15,048 of size 6). The latter was motivation only, not proof.
A separate necessary chord-angle LP admitted positive-margin solutions in four
of eight sampled mixed-half-plane cyclic orders. Angle constraints alone did
not establish the geometric obstruction.

## 4. Six-arc carrier, independent of recurrence

Examined all six squared-distance functions from an endpoint z(s), initially
numerically at s=.01,.05,.1,.154,.2,.25,.3. The numerical maximum intersection
count was three in each probe. Derived all functions and derivatives exactly.
Their ranges separate for every 0<s<1/3. Counting shared endpoints as points,
not parametrizations, proves every positive-radius circle about z(s) meets the
entire truncated carrier in at most three points.

Consequently every finite subset of the carrier with parameters below 1/3 has
a good point. No recurrence, symmetry, prescribed radius, or convexity of that
finite subset is needed. This blocks on-carrier multichain, endpoint and
symmetry-breaking repairs, but not off-carrier repairs.
Full proof: `proof_attempts/six_arc_carrier.md`.

## 5. Collision-free product-component obstruction

Derived a mixed-half-plane diamond lemma by explicit strict convex combinations,
including shrinking/growing multiplier cases and real boundary multipliers.
For any convex realization of the labelled 27-point witness equations with all
nine equilateral triples of the same orientation, matched-triangle equations
force a common center. Four-arrow completion then forces product form. The
mixed-half-plane lemma forces both three-step ratio cycles into one open half
plane; their projective closure and modulus constraints contradict this.

An equilateral triple cannot reverse orientation along a collision-free path.
Thus the original seed has no collision-free convexification preserving all
named witnesses, even if the motion initially breaks C3 symmetry. This does
not yet exclude components with mixed triangle orientations, collisions, or
changed witness assignments. Full proof: `proof_attempts/product_component.md`.

## 6. Adversarial controls and failed shortcuts

* Oppositely oriented matched equilateral triangles: numerical scans of all
  real radial roots at 1,800 phases found only 5-vertex unions among valid
  nonsingular samples, including 195 roots of radius greater than one. No
  general theorem was established; the singular radius-one case is unresolved.
* Two equilateral triangles can have all six points exposed without alternating
  triangle labels around the hull. Therefore alternating labels were not used
  in the proof. The matched-circle center-distance relation by itself also
  does not exclude six exposed points.
* A 12,000-trial all-upper six-step cycle sampler found no closed cycles. This
  was a deficient sampling procedure, not an obstruction: a separate scalar
  equation gives algebraically closed all-upper six-step cycles with two
  angles about 66.787679 degrees and four about 176.606160 degrees, total
  840 degrees and multiplier product omega. Their convexity was not certified.
* Upper projected own-side arrows need not be noncrossing. In a 60,000-case
  four-orbit probe, 18,010 sets with crossing projected arrows had all 12 points
  on the hull. An outerplanarity/forest shortcut is therefore false.

Some exploratory probes in this section were run interactively and are not
claimed to have complete saved replay logs. Their negative-control coordinates
and parameters are retained in session notes; no finite exclusion depends on
those counts.

## 7. Other rotation orders

Ran 15,000 sampled product diamonds for every step in rotation orders 3 through
9. Full hulls occurred only for the longest step at odd rotation orders in this
sample. This is not an exhaustive theorem. Source and output:
`search/other_rotation_diamonds.py`, `reports/other_rotation_diamonds.json`.
Potential generalizations were not assumed in the C3 paper proof.

## 8. Independent algebra replay

`verify/symbolic_checks.py` independently expands coordinates and checks 49
identities without importing search code. A first run failed because a
trigonometric identity was not simplified; explicitly applying `trigsimp`
resolved that implementation issue. The subsequent run passed all 49 checks.
This verifies algebraic formulas, not formal correctness of every geometric
argument. Report: `reports/symbolic_checks.json`.

## 9. Unrestricted-coordinate experiments

Next direction: deterministic searches with freely moving planar coordinates,
fixed directed witness patterns, strict supporting-half-plane penalties, and
independent hull and separation checks. No successful candidate is currently
established. The first attempted interactive terminal launch was unavailable;
no search output was produced by that failed launch.
