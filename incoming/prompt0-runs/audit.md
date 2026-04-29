# Prompt 0 Run 01 Audit

Status: heuristic/audit note. This file records local review of an AI-generated
prompt result. It is not mathematical evidence for the full problem and does
not claim a proof or counterexample.

## Verdict

This run is useful but not a new direction to promote as-is.

Useful pieces:

1. The centered-circle angle inequality is a real local constraint once the
   cone statement is repaired.
2. The row-intersection bound is standard and correct.
3. The 10-point non-convex construction is valid and is already represented in
   the repository's synthesis notes.

Main correction:

- The statement "all other vertices lie strictly inside the open cone" at a
  hull vertex is false as written: the two adjacent vertices lie on the
  boundary rays. The correct statement is that all other vertices lie in the
  closed cone spanned by the two incident edges, only the adjacent vertices lie
  on the boundary rays, and all non-adjacent vertices lie in the open cone.

This correction has been applied to:

- `docs/claims.md`;
- `docs/vertex-circle-order-filter.md`;
- `docs/canonical-synthesis.md`.

## Claim Review

### Lemma 1: Angular Order And Semicircle Containment

The intended conclusion is correct, but the proof needs the boundary-ray
correction above.

Corrected form:

- from a fixed polygon vertex `p`, all other vertices lie in the closed
  interior angle at `p`;
- the angular span is at most `alpha_p`, and `alpha_p < pi`;
- therefore any equal-distance cohort at `p` lies in an open semicircle of the
  circle centered at `p`;
- strict convexity/no-three-collinear gives distinct polar rays;
- boundary order agrees with angular order around `p`, up to reversal.

The run states `delta_1 + delta_2 + delta_3 < alpha_p`. The universally safe
version is

`delta_1 + delta_2 + delta_3 <= alpha_p < pi`.

Strict inequality can fail if the chosen four witnesses include both adjacent
neighbors of `p`. This does not break the later middle-witness corollary,
because `delta_1 + delta_2 < alpha_p` and `delta_2 + delta_3 < alpha_p` still
hold whenever all three gaps are positive.

### Lemma 2: Middle-Witness Angle Constraint

After the Lemma 1 correction, the angle bound is valid:

`epsilon_{q_2} <= (delta_1 + delta_2)/2`

and

`epsilon_{q_3} <= (delta_2 + delta_3)/2`.

The inscribed-angle computation is sound: since the middle witness lies on the
minor arc between its two neighboring witnesses, the angle at the middle
witness sees the complementary major arc.

### Corollary 3: Low-Angle Descent

The corollary remains valid in corrected form. If `alpha_p < 2pi/3`, the two
middle witnesses have strictly larger interior angle than `p`.

This is a useful local obstruction, but it does not close the problem because
large-angle vertices are compatible with convex polygons.

### Lemma 4: Row-Intersection Bound

The bound

`|S_i cap S_j| <= 2`

is correct. It is also already part of the repo's standard A/B matrix
framework. It follows directly from the fact that two distinct circles meet in
at most two points; the radical-axis/no-three-collinear explanation is
compatible but stronger than needed.

## Verified Near-Counterexample

The 10-point construction with an outer regular pentagon and an inner rotated
regular pentagon of radius

`rho = phi^{-2} = (3 - sqrt(5))/2`

was checked locally.

Results:

- each outer point has a distance class of size `4`;
- each inner point has a distance class of size `4`;
- the inner pentagon lies strictly inside the outer pentagon;
- the convex hull has only the five outer vertices.

The two algebraic identities used in the proof simplify to zero under exact
symbolic checking:

`1 + phi^{-3} + phi^{-4} = 2 - phi^{-1}`;

`phi^{-4}(2 + phi) = 1 + phi^{-4} - phi^{-1}`.

This example is not a counterexample to Erdos Problem #97. It is already
represented in `docs/canonical-synthesis.md` as the 10-point concave/inner
pentagon obstruction to dropping convex position.

## Repository Value

Worth keeping:

- the raw run as provenance;
- this audit;
- the corrected cone wording in canonical docs;
- possible future use of the Lemma 2 angle inequality as a finite-pattern
  filter.

Not worth promoting:

- a standalone Prompt 0 proof route;
- the near-counterexample as new evidence;
- the uncorrected strict open-cone statement.

Recommended next action:

Use Prompt 0 only as a source of local filters. The better active path remains
the certified fragile-hypergraph computation route, with metric filters added
only when they can be encoded and tested.
