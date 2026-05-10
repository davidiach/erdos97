# n=8 Selected-Witness Reviewer Packet

Status: claim-neutral reviewer packet; not mathematical evidence by itself.
Claim scope: repo-local selected-witness finite case for `n=8`, supporting
the current repo-local `n <= 8` machine-checked result.
Source of truth: `STATE.md`, `RESULTS.md`, `docs/claims.md`,
`metadata/erdos97.yaml`.
Last reviewed: unreviewed packet draft, 2026-05-10.

This packet packages the current `n=8` selected-witness finite-case artifacts
for independent review. It does not change the repository status. No general
proof and no counterexample are claimed, and the official/global status remains
falsifiable/open. The repository's `n <= 8` result is repo-local,
machine-checked, and pending independent review before any paper-style or
public theorem-style claim.

## Non-Claims

- This packet does not prove Erdos Problem #97.
- This packet does not claim or certify a counterexample.
- This packet does not update the official/global status.
- This packet does not promote `n=9`, `n=10`, fixed-pattern, or all-order
  fixed-pattern artifacts.
- This packet does not replace `STATE.md`, `RESULTS.md`, `docs/claims.md`, or
  `metadata/erdos97.yaml` as source-of-truth files.
- This packet does not claim independent external review has already happened.
- Numerical near-misses, including historical B12 artifacts, are not used.

## Claim Being Reviewed

Scoped claim: within the selected-witness formulation, there is no strictly
convex `n=8` counterexample satisfying one chosen 4-witness row at every
center. The incidence layer derives all necessary `n=8` selected-witness
survivors and reduces them to 15 canonical classes. The exact survivor layer
then kills all 15 by finite cyclic-order constraints, exact
perpendicular-bisector algebra, selected equal-distance algebra, duplicate
vertices, collinearity, or strict-convexity failure.

This is a finite selected-witness artifact. It is not a bridge to arbitrary
large `n`, not a counterexample, and not a claim that nearby fixed-pattern
obstructions solve the global problem.

## Files To Inspect

- `README.md`, `STATE.md`, `RESULTS.md`, and `metadata/erdos97.yaml` for
  claim status and source-of-truth wording.
- `docs/claims.md`, `docs/reviewer-guide.md`,
  `docs/verification-contract.md`, `docs/glossary.md`, and
  `docs/boundary-atlas.md` for trust labels and review vocabulary.
- `docs/n8-incidence-enumeration.md` for the incidence-completeness argument.
- `docs/n8-exact-survivors.md` for the 15-class exact obstruction pass.
- `data/incidence/n8_incidence_completeness.json` for generated incidence
  counts and canonical survivor classes.
- `data/incidence/n8_reconstructed_15_survivors.json` for the checked-in
  survivor class list.
- `data/incidence/n8_compatible_orders.json` for compatible cyclic orders.
- `certificates/n8_exact_analysis.json` and
  `certificates/n8_polynomial_systems.txt` for exact survivor certificates and
  expanded systems.
- `scripts/enumerate_n8_incidence.py` and `src/erdos97/n8_incidence.py` for
  incidence regeneration.
- `scripts/analyze_n8_exact_survivors.py` for the exact obstruction verifier.
- `scripts/independent_check_n8_incidence_json.py`,
  `scripts/independent_check_n8_artifacts.py`, and
  `scripts/independent_n8_obstruction_recheck.py` for artifact-facing
  cross-checks.
- `tests/test_n8_incidence.py`, `tests/test_n8_exact_survivors_artifact.py`,
  `tests/test_n8_artifact_audit.py`,
  `tests/test_n8_independent_incidence_json.py`, and
  `tests/test_n8_independent_obstruction.py` for regression coverage.

## Reproduction Commands

Install the development environment first, or use the version-matched
dependency snapshot described in `README.md`.

```bash
python scripts/independent_check_n8_artifacts.py --check --json
python scripts/enumerate_n8_incidence.py --summary
python scripts/enumerate_n8_incidence.py --check-data data/incidence/n8_incidence_completeness.json
python scripts/analyze_n8_exact_survivors.py --check --json
python scripts/analyze_n8_exact_survivors.py --check --json --check-compatible-orders-data data/incidence/n8_compatible_orders.json --check-exact-analysis-data certificates/n8_exact_analysis.json
python scripts/independent_check_n8_incidence_json.py --json
python scripts/independent_n8_obstruction_recheck.py --check --json
python -m pytest tests/test_n8_incidence.py tests/test_n8_exact_survivors_artifact.py tests/test_n8_artifact_audit.py tests/test_n8_independent_incidence_json.py tests/test_n8_independent_obstruction.py -q
```

After documentation edits, also run the repository fast tier:

```bash
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
python scripts/check_artifact_provenance.py
git diff --check
python -m ruff check .
python -m pytest -q
```

## Expected Output Invariants

For `python scripts/independent_check_n8_artifacts.py --check --json`:

- `verified` is `true`.
- `overall_status` is
  `n8_artifacts_verified_repo_local_pending_external_review`.
- `survivor_json.record_count` is `15`.
- `completeness_artifact.canonical_class_count` is `15`.
- `exact_obstruction_artifacts.all_reconstructed_15_rejected` is `true`.
- `exact_obstruction_artifacts.compatible_orders_artifact.verified` is `true`.
- `exact_obstruction_artifacts.exact_analysis_artifact.verified` is `true`.
- `does_not_check` includes full independent regeneration of the incidence
  enumeration, independent external review, a general proof, and a
  counterexample.

For `python scripts/enumerate_n8_incidence.py --summary`:

- `n` is `8`.
- `status` is `INCIDENCE_COMPLETENESS`.
- `balanced_cap_matrices_with_row0_fixed` is `117072`.
- `forced_perpendicular_survivors_with_row0_fixed` is `4560`.
- `canonical_survivor_class_count` is `15`.
- `matches_existing_reconstructed_survivors` is `true`.

For `python scripts/analyze_n8_exact_survivors.py --check --json`:

- `status` is `exact_obstruction_artifact_pending_independent_review`.
- `survivor_classes` is `15`.
- `cyclic_order_killed_ids` is `[12]`.
- `cyclic_order_remaining_count` is `14`.
- `pb_y2_span_ids_verified` is
  `[0, 1, 2, 6, 7, 8, 9, 10, 11, 13]`.
- `class3_duplicate_vertex_certificate_verified` is `true`.
- `class4_collinearity_certificate_verified` is `true`.
- `class5_groebner_contains_y2_after_exact_substitution` is `true`.
- `class14_pb_ed_groebner_basis_verified` is `true`.
- `class14_solution_branches_solve_pb_ed` is `true`.
- `class14_strict_interior_certificate_verified` is `true`.

For `python scripts/independent_n8_obstruction_recheck.py --check --json`:

- `verified` is `true`.
- `classes_killed_independently` is
  `[0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13]`.
- `classes_requiring_groebner_machinery` is `[3, 4, 5, 14]`.
- `does_not_check` explicitly lists the Groebner-dependent classes and the
  incidence-completeness step.

## Mathematical Proof Sketch

Assume a selected-witness `n=8` counterexample exists. Each row has four
selected witnesses and excludes its own center. The two-circle cap gives
`|S_i cap S_j| <= 2` for distinct centers. The witness-pair cap says any
unordered pair of labels can co-occur in at most two selected rows, because all
centers seeing that pair lie on one perpendicular bisector line.

For `n=8`, the witness-pair cap forces every witness indegree to be exactly
four: a fixed vertex appearing in `d` rows contributes `3d` witness pairs, at
most two per possible partner, so `3d <= 14` and `d <= 4`; the total indegree
is `32`, hence all eight indegrees equal four.

The incidence enumerator then checks all binary selected-witness matrices with
zero diagonal, row sums four, derived column sums four, row-pair intersections
at most two, column-pair co-occurrences at most two, no odd forced
perpendicularity cycle, and no same-color forced-parallel chord class sharing
an endpoint. With row `0` fixed to witnesses `{1,2,3,4}` by relabeling, the
enumeration leaves 15 canonical classes up to simultaneous relabeling.

For each survivor class, whenever two rows share exactly two witnesses, the
center chord is the perpendicular bisector of the common-witness chord. The
exact survivor checker translates those implications into polynomial
dot-product and midpoint-line equations under the gauge
`p_0=(0,0)`, `p_1=(1,0)`, `y_2 != 0`, then adds full selected equal-distance
equations where needed.

Class `12` has no compatible cyclic order. Ten classes are killed by exact
rational linear algebra because `y_2` lies in the rational span of the
perpendicular-bisector equations, contradicting the gauge. Class `3` forces a
duplicate vertex, class `4` forces three collinear vertices, class `5` has a
Groebner contradiction after exact substitutions, and class `14` has four real
algebraic branches, each with only four hull vertices and four strict interior
points. Therefore all 15 incidence survivors are exactly obstructed within
the selected-witness `n=8` scope.

## Certificate Schema

Trusted input data:

- `data/incidence/n8_reconstructed_15_survivors.json` stores 15 survivor
  records, each with an integer `id` and an `8 x 8` binary `rows` matrix.
- `data/incidence/n8_incidence_completeness.json` stores the regeneration
  counts, the row-0 symmetry break, the column-sum derivation, filter names,
  and canonical survivor classes.
- `data/incidence/n8_compatible_orders.json` stores normalized compatible
  cyclic orders, modulo rotation and reversal.
- `certificates/n8_exact_analysis.json` stores the cyclic filter summary,
  expanded systems for classes not killed by cyclic order, contradiction IDs,
  and final exact-geometry status.

Derived fields to recheck:

- row sums, zero diagonal, column sums, row-pair caps, and column-pair caps;
- brute-force canonical representatives under all `8!` simultaneous
  relabelings;
- forced-perpendicularity graph bipartiteness and same-color endpoint filters;
- compatible cyclic-order counts;
- perpendicular-bisector polynomial equations and selected equal-distance
  equations;
- rational-span certificates, Groebner certificates, duplicate/collinearity
  certificates, and strict-interior branch checks.

Diagnostic or provenance-only fields:

- archive ID mappings, unless the optional archive JSON is supplied;
- long compatible-order lists, except as replay data for the counts;
- explanatory notes and historical reconstruction text;
- any numerical search output, which is not part of this `n=8` exact packet.

## Independent Review Checklist

- Check that the source-of-truth docs still say no general proof and no
  counterexample are claimed.
- Check that the packet's scope is only selected-witness `n=8` finite-case
  review, with `n <= 8` kept repo-local and machine-checked pending
  independent review.
- Verify the two-circle cap, witness-pair cap, and `n=8` indegree regularity
  derivation independently.
- Audit whether fixing row `0` to witnesses `{1,2,3,4}` is only a relabeling
  symmetry break.
- Reproduce the 15 canonical incidence classes from
  `scripts/enumerate_n8_incidence.py`.
- Recheck the survivor JSON without relying on the incidence generator.
- Recheck class `12` cyclic-order noncrossing and the compatible-order counts.
- Recheck the ten `y_2` rational-span certificates over exact rational
  arithmetic.
- Recheck classes `3`, `4`, `5`, and especially `14`, where Groebner machinery
  is required.
- Confirm that all exact obstruction steps avoid floating-point equality and
  numerical optimization.
- Confirm that no `n=9`, `n=10`, fixed-pattern, or all-order fixed-pattern
  result is promoted by this packet.
- Record any failed or partial review outcome in an issue or PR with command,
  environment, artifact path, and exact gap.

## Known Weak Points

- `scripts/independent_check_n8_artifacts.py` treats checked-in artifacts as
  input data and cross-checks them; it does not independently regenerate the
  full incidence enumeration.
- `scripts/independent_n8_obstruction_recheck.py` is SymPy-free but covers
  only class `12` plus the ten `y_2` rational-span kills. It intentionally
  does not cover Groebner-dependent classes `3`, `4`, `5`, and `14`.
- Class `14` is the most delicate survivor: it uses the full
  perpendicular-bisector plus equal-distance system and a strict-interior
  conclusion from four algebraic branches.
- The aggregate `n=8` exclusion is a computer-assisted repo-local artifact,
  not a standalone public proof certificate.
- Literature coverage must still be rechecked before any public theorem-style
  statement about Erdos Problem #97.

## Relation To Source-Of-Truth Docs

This packet supports the existing source-of-truth wording in `STATE.md`,
`RESULTS.md`, `docs/claims.md`, and `metadata/erdos97.yaml`. It does not
supersede those files and should be updated if they change.

The packet refines the audit route already described in `docs/reviewer-guide.md`
and `docs/review-priorities.md`. It is narrower than the proof-note draft
`papers/small-counterexamples-erdos97.md` and `docs/n8-geometric-proof.md`,
which pursue a human-readable geometric small-case route.

The relevant boundary-atlas categories are `INCIDENCE_OVERLAP_BOUNDARY`,
`CYCLIC_ORDER_FORBIDDEN`, `COLLISION_BOUNDARY`,
`COLLINEAR_WITNESS_BOUNDARY`, and `NONSTRICT_CONVEX_BOUNDARY`.

## Status-Update Rules

- A successful review of this packet may justify updating review notes or
  adding a dated review entry, but it does not by itself update the
  official/global status.
- Do not update `metadata/erdos97.yaml` unless the source-of-truth strongest
  result, review status, official-status check date, or artifact inventory
  actually changes.
- Do not update `STATE.md`, `RESULTS.md`, or `docs/claims.md` to stronger
  public theorem-style language unless an independent review explicitly
  accepts the incidence completeness, exact survivor obstructions, claim
  scope, and literature boundary.
- A failed review should preserve the packet and record the precise gap, then
  demote or qualify source-of-truth wording only if the gap affects the current
  repo-local `n <= 8` machine-checked claim.
- Any future promotion must keep separate: official/global status, repo-local
  finite-case artifacts, review-pending `n=9` and `n=10` artifacts,
  fixed-order obstructions, fixed-pattern all-order obstructions, and
  numerical evidence.
