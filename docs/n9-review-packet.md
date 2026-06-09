# n=9 Selected-witness Reviewer Packet

Status: `REVIEW_PACKET_ONLY`.

Claim scope: repo-local `n=9` selected-witness finite-case candidate.

Source of truth: `README.md`, `STATE.md`, `RESULTS.md`, `docs/claims.md`,
`docs/n9-reduction-chain.md`, and `metadata/erdos97.yaml`.

Last assembled: 2026-06-04.

## Non-claims

- This packet does not prove Erdos Problem #97.
- This packet does not claim a counterexample.
- This packet does not update the official/global status.
- This packet does not promote the review-pending `n=9` artifacts.
- Passing every command below is not a substitute for independent mathematical
  review of the geometric and enumeration assumptions.

## Claim being reviewed

The scoped candidate claim is:

```text
No strictly convex 9-gon has a selected 4-witness row at every vertex.
```

Equivalently, after labelling a hypothetical bad nonagon in cyclic order
`0,...,8`, there is no full assignment of selected witness rows
`S_i subset {0,...,8} \ {i}`, `|S_i| = 4`, satisfying the necessary incidence
filters and the accepted geometric obstruction rule.

Even if this review succeeds, it would be a repo-local finite-case result only.
It would not prove the general problem for larger polygons.

## Main files to inspect

- `docs/n9-reduction-chain.md`
- `docs/n9-vertex-circle-exhaustive.md`
- `docs/n9-vertex-circle-independent-recheck.md`
- `docs/n9-vertex-circle-strict-edge-geometry-audit.md`
- `docs/n9-vertex-circle-quotient-soundness-audit.md`
- `docs/n9-vertex-circle-local-lemmas.md`
- `docs/n9-vertex-circle-local-lemma-review-packet.md`
- `docs/relation-skeleton-catalog.md`
- `docs/turn-inequality-lemma.md`
- `docs/turn-packing-bridge.md`
- `docs/n9-groebner-decoders.md`

The canonical dependency map is `docs/n9-reduction-chain.md`. This packet is a
review worksheet for that map, not a replacement for it.

The compact promotion-review harness is
`docs/n9-candidate-promotion-harness.md`. It provides a single command surface
for the Lean pilot guardrails, the vertex-circle route, the turn-packing route,
and the stored-input Kalmanson replay:

```bash
make verify-n9-candidate
```

Passing this target is not a status promotion; it only confirms that the
current compact review harness is internally consistent.

The machine-readable route contract is `metadata/n9_candidate_review.yaml`,
checked by
`python scripts/check_n9_candidate_review_manifest.py --check --summary-json`.
It keeps the Makefile command sequence, referenced review files, and open
review gates synchronized.

The machine-readable gate ledger is `metadata/n9_review_gate_ledger.yaml`,
checked by
`python scripts/check_n9_review_gate_ledger.py --check --summary-json`. It maps
the compact harness commands to the open A6/A7, A8, A10, B1/B3, and
corroborating Kalmanson review gates plus the acceptance outcomes below.

The machine-readable evidence matrix is
`metadata/n9_review_evidence_matrix.yaml`, checked by
`python scripts/check_n9_review_evidence_matrix.py --check --summary-json`.
Run
`python scripts/check_n9_review_evidence_matrix.py --check --run --summary-json`
when a live replay of the compact output invariants is needed.

The machine-readable reviewer dossier is `metadata/n9_review_dossier.yaml`,
checked by
`python scripts/check_n9_review_dossier.py --check --summary-json`. Render the
on-demand Markdown worksheet with
`python scripts/check_n9_review_dossier.py --markdown`.

The machine-readable reviewer run bundle is
`metadata/n9_review_run_bundle.yaml`, checked by
`python scripts/check_n9_review_run_bundle.py --check --summary-json`. Capture
one live run as digest-level provenance with
`python scripts/check_n9_review_run_bundle.py --check --run --summary-json`.

The machine-readable reviewer-decision intake is
`metadata/n9_review_decision_intake.yaml`, checked by
`python scripts/check_n9_review_decision_intake.py --check --summary-json`.
Print a fillable template with
`python scripts/check_n9_review_decision_intake.py --template`, then validate a
filled external decision with
`python scripts/check_n9_review_decision_intake.py --decision path/to/decision.yaml --check --summary-json`.

The vertex-circle route decision preflight is
`docs/n9-vertex-circle-route-decision-preflight.md`, checked by
`python scripts/check_n9_vertex_circle_route_decision_preflight.py --check --summary-json`.
It verifies that the internal A6/A7, A8, and A10 review notes are present,
that the route gates remain open, and that `accepted_vertex_circle_route`
still requires written independent review. It is not a decision record.

## Review routes

### Route A: vertex-circle closure

This is the canonical review-pending route.

1. A hypothetical bad nonagon gives selected rows in cyclic order `0,...,8`.
2. The rows obey the two-circle row-intersection cap, two-overlap crossing
   rule, witness-pair cap, and selected-indegree cap.
3. The brancher enumerates all full row assignments satisfying those necessary
   filters.
4. The pre-vertex-circle frontier contains exactly `184` assignments.
5. Vertex-circle chord nesting gives strict distance inequalities.
6. Selected-distance equalities quotient ordinary pair distances.
7. Every one of the `184` quotient systems has a strict self-edge or strict
   directed cycle.

Live review burden: A6/A7 enumeration coverage, A8 strict-edge geometry, and
A10 quotient replay in `docs/n9-reduction-chain.md`.

### Route B: turn-packing closure

This is a compact arithmetic route over the same `184` frontier.

1. Start from the same pair/crossing/count frontier.
2. Accept the exterior-turn inequality lemma and its indexing convention.
3. Replay the stored integer dual certificates for the resulting weak turn
   systems.

Live review burden: the geometric turn lemma and interval indexing in
`docs/turn-inequality-lemma.md`, plus the arithmetic replay.

### Route C: algebraic cross-audit

This route is corroborating, not currently primary. It uses the 184-to-16
dihedral-family reduction and Groebner/real-root decoder artifacts to close the
same frontier. A reviewer should not treat it as standalone unless the family
reduction and decoder replay are independently audited.

## Minimal reproduction commands

Run these first. They are the shortest current command set that exercises the
main `n=9` route boundaries without running the whole artifact audit.

```bash
make verify-n9-candidate
```

The target expands to the layer-specific commands below and includes
`make verify-lean`-equivalent guardrails for the local Lean pilot.

```bash
python scripts/check_n9_candidate_review_manifest.py --check --summary-json
python scripts/check_n9_review_gate_ledger.py --check --summary-json
python scripts/check_n9_review_evidence_matrix.py --check --summary-json
python scripts/check_n9_review_dossier.py --check --summary-json
python scripts/check_n9_review_run_bundle.py --check --summary-json
python scripts/check_n9_review_decision_intake.py --check --summary-json
python scripts/check_n9_vertex_circle_route_decision_preflight.py --check --summary-json
python scripts/check_lean_sketch_integrity.py
python scripts/check_lean_files.py
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
python scripts/check_n9_vertex_circle_input_audit.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_mro_branching_replay.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_quotient_soundness.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --summary-json
python scripts/check_turn_inequality_indexing.py --check --assert-expected --summary-json
python scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --summary-json
```

Optional corroborating commands:

```bash
python scripts/independent_n9_vertex_circle_recheck.py --json
python scripts/check_n9_vertex_circle_compact_brancher.py --check --assert-expected --json
python scripts/decode_n9_groebner_f07_f13.py
```

## Expected invariants

The exhaustive vertex-circle checker should report:

- `row0_choices: 70`;
- main search with vertex-circle pruning has `full_assignments: 0`;
- no-vertex-circle cross-check has `full_assignments: 184`;
- no-vertex-circle cross-check has `158` self-edge and `26` strict-cycle
  vertex-circle classifications.

The row0/input audit should confirm:

- the 70 row0 choices are the lexicographic 4-subsets of labels `1..8`;
- stored row0 masks and witnesses match the checked-in artifact;
- summary arithmetic and no-overclaiming fields match the review-pending
  claim scope.

The incidence-filter audit should confirm:

- the row-level two-overlap crossing table is directly reproduced;
- witness-pair capacity and selected-indegree predicates are directly
  reproduced;
- no brancher, vertex-circle, or quotient claim is promoted by this audit.

The branch-order/frontier audits should confirm:

- fixed-order and dynamic minimum-remaining-options searches agree on the same
  stored `184` frontier;
- branch ordering changes only search order within the audited implementation
  boundary;
- the stored frontier assignment set and labels agree with regenerated rows.

The 2026-06-09 internal A6/A7 review note records acceptance of the
source-frontier evidence bundle only. It does not close the machine-readable
`frontier_enumeration` gate without an explicit written review decision.

The strict-edge geometry audit should confirm:

- `630` candidate selected rows are checked;
- each row has `9` strict edges under the proper-interval containment rule;
- `5670` strict edges are compared;
- strict-edge mismatches and quotient-replay strict-edge mismatches are both
  `0`.

The 2026-06-09 internal A8 review note records acceptance of that local
nested-chord rule and checker-equivalence contract only. It does not close the
machine-readable `vertex_circle_geometry` gate without an explicit written
review decision.

The quotient/local-lemma audits should confirm:

- the self-edge/strict-cycle split remains `158 + 26`;
- the motif-family count remains `16`;
- the local-lemma template count remains `12`, with IDs `T01` through `T12`;
- focused packets, focused mini-replays, aggregate/simple replay,
  exhaustive/local-lemma crosswalk, and relation-skeleton/local-lemma crosswalk
  pass adjacent handoff checks;
- these checks are still packet bookkeeping, not completed packet soundness or
  local-lemma completeness review.

The turn-packing replay should confirm:

- the indexing audit checks `70` row-offset subsets, `630` row instances, `504`
  unique center/pair/orientation records, and `7560` emitted term records with
  no mismatches;
- source frontier assignment count is `184`;
- integer dual certificate count is `184`;
- all weak turn systems are infeasible by stored integer arithmetic;
- the geometric turn lemma remains a separate proof-facing review dependency.

## Independent review checklist

### Incidence and enumeration

- Check that the selected-witness formulation exactly matches the finite-case
  claim being reviewed.
- Check the two-circle row-intersection cap.
- Check the radical-axis/perpendicular-bisector crossing rule for row pairs
  sharing two witnesses.
- Check the witness-pair cap from perpendicular-bisector line intersections.
- Check the selected-indegree cap `3d <= 16` for `n=9`, hence `d <= 5`.
- Check that no hidden symmetry quotient is used in row0 coverage.
- Check that dynamic minimum-remaining-options branching changes only search
  order.

### Vertex-circle route

- Check the geometric chord-nesting lemma behind strict-edge generation.
- Check that proper interval containment is the exact convention used by both
  the checker and the proof note.
- Check selected-distance quotient construction from selected rows.
- Check that a strict self-edge is impossible.
- Check that a strict directed cycle is impossible.
- Check that local-core and focused-packet records are exact subsets or
  faithful transformations of the full frontier records they cite.

### Turn-packing route

- Check that exterior-turn variables are normalized consistently.
- Check both intervals forced by an equidistant witness pair at offsets
  `1 <= a < b <= 8`.
- Check boundary cases near total turn `pi/2` and confirm strict geometry
  justifies using weak normalized inequalities in the replay.
- Check the integer dual certificate arithmetic without relying on Z3.

### Algebraic cross-audit

- Check the 184-to-16 dihedral-family reduction before using family-level
  algebra.
- Check exact polynomial systems and normalizations.
- Check that real-root decoder conclusions imply degeneracy or
  non-strict-convexity, not merely numerical failure.

## Acceptance standard

A successful review should identify which of these outcomes applies:

- `accepted_vertex_circle_route`: A6/A7, A8, and A10 survive review.
- `accepted_turn_route`: A6/A7, B1, and B3 survive review.
- `accepted_corrob_only`: the artifacts reproduce but at least one proof-facing
  route dependency remains unreviewed.
- `gap_found`: the review identifies a precise mathematical or implementation
  gap.

Only the first two outcomes would justify a follow-up PR proposing
source-of-truth status changes for the repo-local `n=9` finite-case claim. That
follow-up PR must update `README.md`, `STATE.md`, `RESULTS.md`,
`metadata/erdos97.yaml`, and `docs/claims.md` together, and must preserve the
global non-claim: no proof of Erdos Problem #97 and no counterexample are
claimed.

## Known weak points

- The vertex-circle route still depends on human review of the strict-edge
  geometry and quotient obstruction interpretation.
- The turn-packing route is attractive because its final certificates are
  short, but the exterior-turn lemma and indexing are the hinge.
- The algebraic route is strong corroboration only after the family reduction
  and decoder replay are independently audited.
- None of the `n=9` routes supplies a bridge from arbitrary larger
  counterexamples to the `n=9` frontier.

## Reporting review findings

Record a review as a PR or issue containing:

- the exact commit or branch reviewed;
- commands run and their pass/fail status;
- environment details;
- accepted lemmas or precise gaps;
- whether the result supports a repo-local `n=9` finite-case status update, or
  only artifact bookkeeping.
