# Review priorities

Status: planning guidance only; not mathematical evidence.

This file turns current review feedback into concrete work items. It does not
change the repository claims: no general proof and no counterexample are
claimed, the official/global status remains falsifiable/open, and the local
`n <= 8` selected-witness result remains repo-local and machine-checked pending
independent review.

For a Codex-ready task list with issue links, commands, acceptance criteria,
trust deltas, and forbidden overclaiming text, see `docs/codex-backlog.md`.

## Priority 1 - review the octagon proof note

Target: `docs/n8-geometric-proof.md`.

Proof trail: `docs/n8-proof-trail.md` joins the geometric proof note, the
machine-checked selected-witness artifact route, and the literature-backed
Dumitrescu shortcut into one claim-neutral reviewer map.

Ask independent geometry reviewers to check:

- the base-apex lemma and its strict-convexity use;
- the isosceles-triangle count `T(A) <= n(n-2)`;
- equality saturation in the octagon case;
- the length-2 diagonal step forcing all side lengths equal;
- the length-3 diagonal step forcing a cover of adjacent exterior-turn pairs;
- the final vertex-cover and total-turn contradiction.

Acceptance standard: a written review should identify every accepted lemma and
any exact gap. If the note survives review, keep it as the main human-readable
small-case proof route, with the computational pipeline as an audit appendix.

## Priority 2 - audit and extend the n=8 checker

Proof trail: `docs/n8-proof-trail.md` records how the selected-witness artifact
route, independent artifact audit, SymPy-free partial recheck, residual
checker, and class `14` checker fit together.

Audit the current checker, and extend it toward a more independent `n=8`
finite-artifact check that treats the checked-in JSON and certificate data as
inputs, not as generated truth. Any extension should avoid reusing the current
canonicalization and algebra-helper code except where the input format forces
it.

Suggested inputs:

- `data/incidence/n8_reconstructed_15_survivors.json`;
- `data/incidence/n8_incidence_completeness.json`;
- `certificates/n8_exact_analysis.json`.

Suggested checks:

- the 15 survivor classes are valid selected-witness incidence systems;
- claimed cyclic-order eliminations are reproducible;
- named exact certificates for classes `3`, `4`, `5`, and `14` verify from the
  certificate data;
- the checker reports only `EXACT_OBSTRUCTION` or explicit uncertainty.

Current audit entrypoint:

```bash
python scripts/independent_check_n8_artifacts.py --check --json
```

This command checks the checked-in survivor, completeness, compatible-order,
and exact-analysis artifacts as input data. It is an artifact-consistency and
exact-obstruction audit entrypoint, not an independent regeneration of the full
incidence enumeration.

Partial SymPy-free independent cross-check:

```bash
python scripts/independent_n8_obstruction_recheck.py --check --json
```

This command independently replays the compatible cyclic-order counts, the
class `12` cyclic-order kill, and the `y_2`-in-PB-span kill for ten classes
using pure-Python rational arithmetic. It does not verify the Groebner-based
classes `3`, `4`, `5`, or `14`.

## Priority 3 - isolate class 14

Class `14` is the most delicate current survivor obstruction because it uses
PB+ED Groebner reasoning plus a strict-interior conclusion. Move toward a short,
standalone certificate file with a minimal verifier that checks:

- the polynomial system under the stated normalization;
- the claimed Groebner basis or an equivalent exact contradiction;
- every solution branch used in the argument;
- the strict-interior or non-strict-convexity conclusion.

This should be small enough for an external reviewer to audit without reading
the full search pipeline.

Current focused entrypoint:

```bash
python scripts/check_n8_class14_certificate.py --check --json
python scripts/check_n8_residual_certificates.py --check --json
```

The class `14` checker rebuilds only the class `14` `PB+ED` system from the
checked-in survivor rows, compares the stored Groebner basis, derives the four
real branches, and verifies exact strict-interior failure. The residual checker
does the analogous focused replay for classes `3`, `4`, and `5`. Both remain
repo-local audits pending external review.

## Priority 4 - pin literature coverage

Before any paper-style or public theorem-style claim, run a literature sweep
covering repeated distances in convex polygons, isosceles-triangle counts,
metric oriented matroids, and order-k Voronoi degeneracies. Record both found
references and negative search results in `docs/literature-risk.md`.

Do not use unchecked literature summaries to alter the official/global status.
Recheck the official Erdos Problems page before any status update.

## Priority 5 - audit the n=9 vertex-circle exhaustive checker

Target: `docs/n9-vertex-circle-exhaustive.md`.

Reviewer packet: `docs/n9-review-packet.md` collects the current dependency
map, reproduction commands, expected invariants, and acceptance outcomes for
the review. It is a worksheet only and does not promote any `n=9` claim.
The run-capture aid `docs/n9-review-run-bundle.md` records digest-level
provenance for one execution of the compact command surface; it is drift
detection only and does not replace written independent review.
The decision-intake aid `docs/n9-review-decision-intake.md` validates any
external written-review record against the open gate ledger and allowed
outcomes; it is still intake validation only.
The vertex-circle route preflight
`docs/n9-vertex-circle-route-decision-preflight.md` checks that the internal
A6/A7, A8, and A10 notes are ready to hand to the decision intake while the
route gates remain open and independent written review remains required.

The 2026-05-03 archive bundle has been refactored into a repo-native checker
that leaves 0 full `n=9` selected-witness assignments after exact
vertex-circle pruning. Treat this as review-pending until an independent audit
checks:

- the necessity of the two-overlap crossing, witness-pair cap, indegree cap,
  and vertex-circle strict-cycle filters;
- the absence of a hidden symmetry quotient in the 70 row0 choices;
- that minimum-remaining-options branching changes only search order;
- that the raw 184/16 and 102-certificate archive variants agree with the
  repo-native counts after their conventions are documented.

Acceptance standard: a written review should either promote the checker to the
same repo-local finite-case status as `n <= 8`, or identify the exact
mathematical or implementation gap.

Audit aid: `docs/n9-vertex-circle-independent-recheck.md` records a separate
implementation-level recheck. Its scripts reproduce the 184 pre-vertex-circle
frontier, match the stored frontier set and labels, and catalog 219 minimal
obstruction cores covering all 184 systems. This is useful evidence for the
Priority 5 review, but it does not by itself close the review or promote the
`n=9` artifact.

Current input-data audit:

```bash
python scripts/check_n9_vertex_circle_input_audit.py --check --assert-expected --summary-json
```

This command recomputes the row-0 coverage directly as the 70 lexicographic
4-subsets of labels `1..8`, checks the stored row-0 witness lists and masks,
and verifies summary arithmetic from the checked-in JSON. It is a small audit
of the "no hidden row0 quotient" checklist item only; it does not rerun the
brancher, replay vertex-circle certificates, prove `n=9`, or complete
independent review. Use `--json` instead when the full expected-count block is
needed.

Current incidence-filter audit:

```bash
python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --summary-json
```

This command recomputes the row-level two-overlap crossing table,
witness-pair cap predicate, and selected-indegree cap predicate. It does not
rerun the brancher, audit strict-edge geometry, review selected-distance
quotient soundness, prove `n=9`, or complete review. Use `--json` instead
when the full histogram blocks are needed.

Current branch-option audit:

```bash
python scripts/check_n9_vertex_circle_branch_options.py --check --assert-expected --summary-json
```

This command walks the no-vertex-circle fixed-order search states and compares
the helper `valid_options_for_center` predicate and maintained count arrays
against a direct implementation. It does not prove dynamic-MRO branch coverage,
strict-edge geometry, selected-distance quotient soundness, `n=9`, or complete
review. Use `--json` instead when the full mismatch example block is needed.

Current dynamic-MRO choice audit:

```bash
python scripts/check_n9_vertex_circle_dynamic_mro_choices.py --check --assert-expected --summary-json
```

This command replays the actual minimum-remaining-options branch choice with
and without vertex-circle pruning. It recomputes all unassigned-center option
lists directly at every reached state and checks first-minimum tie breaking.
It does not prove filter soundness, strict-edge geometry, selected-distance
quotient soundness, `n=9`, or complete review. Use `--json` instead when the
full depth and tie histograms are needed.

Current frontier-coverage crosswalk:

```bash
python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check --assert-expected --summary-json
```

This command reruns the dynamic no-vertex-circle brancher and compares the 184
generated complete selected-row assignments with the stored frontier
classification artifact. It does not prove filter soundness, strict-edge
geometry, selected-distance quotient soundness, `n=9`, or complete review. Use
`--json` instead when the full mismatch example block is needed.

The 2026-06-09 internal A6/A7 review note records
`accepted_A6_A7_source_frontier_internal` for the row0, incidence-filter,
branch-option, dynamic-MRO, frontier-coverage, fixed-order replay, compact
brancher, and mixed-rich landing evidence bundle. Treat it as input to a
formal review-decision record, not as a source-of-truth gate closure.

Current Kalmanson self-edge replay:

```bash
python scripts/check_n9_kalmanson_selfedge.py --verify-certificate data/certificates/n9_kalmanson_selfedge.json --assert-expected --summary-json
```

This command treats the stored 184 terminal assignments as certificate inputs
and checks that each has one strict Kalmanson inequality whose two sides reduce
to the same selected-distance quotient multiset. It is a compact certificate
replay only; it does not independently audit brancher coverage, the
pair/crossing filters, the Kalmanson geometric convention, `n=9`, or complete
review. Use `--json` when the full replay payload is needed.

Independent Kalmanson self-edge input replay:

```bash
python scripts/check_n9_kalmanson_selfedge_independent_replay.py --check --assert-expected --summary-json
```

This command intentionally avoids importing the Kalmanson self-edge generator
module. It treats `data/certificates/n9_kalmanson_selfedge.json` as input and
rechecks row shape, row-pair crossing, witness-pair capacity,
selected-distance quotienting, stored strict Kalmanson self-edges, assignment
uniqueness, and the certificate digest. It is still a stored-certificate audit:
it does not regenerate the 184 frontier, audit brancher coverage, prove `n=9`,
or complete independent review. Use `--json` when the first stored self-edge
example record is needed.

Current dihedral-orbit audit:

```bash
python scripts/check_n9_vertex_circle_dihedral_orbit_audit.py --check --assert-expected --summary-json
```

This command treats the stored motif-family artifact and frontier
classification as inputs. It independently replays the cyclic/reflection
dihedral relabelings, checks canonical representatives and orbit sizes, and
crosswalks the 184 stored classification rows back to the disjoint motif
orbits. It is orbit bookkeeping only, not frontier coverage, filter soundness,
or a proof of `n=9`. Use `--json` when the full mismatch example block is
needed.

Current motif-obstruction audit:

```bash
python scripts/check_n9_vertex_circle_motif_obstruction_audit.py --check --assert-expected --summary-json
```

This command treats the stored 16 motif representatives as inputs, recomputes
selected-distance quotient classes and vertex-circle strict interval edges,
and checks the stored representative self-edge equality paths or strict-cycle
edge chains. It is stored-certificate bookkeeping only, not frontier coverage,
brancher soundness, incidence-filter soundness, dihedral orbit bookkeeping, or
a proof of `n=9`. Use `--json` when the full example error block is needed.

Current frontier comparison:

```bash
python scripts/compare_n9_vertex_circle_frontier.py --check --assert-expected --summary-json
```

This command checks the stored P18/C19 comparison artifact against the current
local-core and vertex-circle helpers. It records zero exact n=9 local-core
embeddings into the recorded P18 and C19 patterns, preserves the P18
strict-cycle and C19 fixed-order pass guardrails, and does not prove `n=9`,
provide a counterexample, or supply a transfer theorem. Use `--json` when the
full pattern records are needed.

Current frontier-assignment audit:

```bash
python scripts/check_n9_vertex_circle_frontier_assignment_audit.py --check --assert-expected --summary-json
```

This command checks the stored 184 frontier assignments directly for row
shape, center coverage, pairwise row-intersection caps, two-overlap crossing,
witness-pair capacity, and selected-indegree capacity. It does not prove
frontier coverage, brancher soundness, strict-edge geometry, selected-distance
quotient soundness, `n=9`, or complete review. Use `--json` when the full
example error block is needed.

Current branching-order replay:

```bash
python scripts/check_n9_vertex_circle_mro_branching_replay.py --check --assert-expected --summary-json
```

This command reruns the search with a fixed center order `0,1,...,8` after row
`0`, reusing the same necessary-filter helpers. It checks that the fixed order
also closes the vertex-circle-pruned search and reaches the same `184`
pre-vertex-circle frontier classification as the dynamic MRO artifact. It does
not prove the filters, independently replay vertex-circle geometry, prove
`n=9`, or complete review. Use `--json` when the full fixed-order replay
sections are needed.

Current strict-edge geometry audit:

```bash
python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --summary-json
```

This command independently enumerates all proper interval containments for the
630 candidate selected rows and compares them with the checker strict-edge
table. It addresses the vertex-circle strict-edge generator only; it does not
review selected-distance quotient soundness, branch coverage, the crossing
filters, prove `n=9`, or complete review. Use `--json` instead when the full
mismatch example block is needed.

The 2026-06-09 internal A8 review note records
`accepted_A8_strict_edge_geometry_internal` for the local nested-chord rule
and checker-equivalence contract. Treat it as input to a formal
review-decision record, not as a source-of-truth gate closure.

Current quotient-soundness audit:

```bash
python scripts/check_n9_vertex_circle_quotient_soundness.py --check --assert-expected --summary-json
```

This command checks stored local-core rows, stored full frontier assignments,
and stored transformed frontier cores against three quotient/status views: the
exhaustive checker, the reusable quotient replay helper, and a small direct
quotient/status replay. It does not audit branch coverage, strict-edge
geometry, prove `n=9`, or complete review. Use `--json` instead when the full
per-view status and mismatch example blocks are needed.

Current partial-pruning audit:

```bash
python scripts/check_n9_vertex_circle_partial_pruning.py --check --assert-expected --summary-json
```

This command scans all nonempty selected-row subsets of the 184 stored
pre-vertex-circle frontier assignments. It checks monotone obstruction
persistence and checker/replay status agreement on those stored subsets only.
It does not prove frontier coverage, brancher soundness, strict-edge geometry,
selected-distance quotient soundness, `n=9`, or complete review. Use `--json`
when the full mismatch example block is needed.

## Priority 6 - mine a reusable vertex-circle lemma

Target: `docs/n9-vertex-circle-obstruction-shapes.md` and
`docs/n9-vertex-circle-motif-families.md`.

Local-lemma reviewer packet:
`docs/n9-vertex-circle-local-lemma-review-packet.md`.

The n=9 obstruction-shape diagnostic shows that the 184 pre-vertex-circle
frontier assignments are killed by 158 self-edges and 26 strict cycles, all
strict cycles having length 2 or 3. This makes the most promising proof push a
quotient-graph lemma: selected-distance equalities collapse ordinary pair
distances into classes, vertex-circle interval containment orients strict
edges between classes, and realizability requires the resulting strict graph to
be irreflexive and acyclic.

Next steps:

The focused T01--T12 packet notes and checkers are already extracted as
review-pending diagnostic/local lemma candidates. New work in this priority
should review packet soundness, local-lemma hypotheses, and aggregate
handoffs rather than re-extracting T01 or T10.

- classify the 13 self-edge dihedral incidence families into local lemmas;
- review the 3 strict-cycle dihedral incidence families as directed
  quotient-cycle local templates, using the focused T10/T11/T12 notes;
- use `docs/n9-vertex-circle-local-cores.md` as the row-local certificate list
  to keep those lemmas small;
- use
  `scripts/check_n9_vertex_circle_local_core_subset_audit.py --check --assert-expected --summary-json`
  to compare the compact row-local certificates against the full motif
  representatives and verify that the compact rows alone still obstruct; use
  `--json` when the full example error block is needed;
- use `data/certificates/n9_vertex_circle_self_edge_path_join.json` as the
  assignment-level replay aid for transformed self-edge equality paths;
- use `data/certificates/n9_vertex_circle_self_edge_template_packet.json` to
  review the 9 self-edge template packets before attempting reusable local
  lemmas;
- use `data/certificates/n9_vertex_circle_strict_cycle_path_join.json` as the
  assignment-level replay aid for transformed strict-cycle local-core
  quotient cycles, keeping its local-core cycle counts separate from first
  full-assignment obstruction-shape counts;
- use `data/certificates/n9_vertex_circle_strict_cycle_template_packet.json`
  to review the 3 strict-cycle template packets before attempting reusable
  quotient-cycle lemmas;
- use `data/certificates/n9_vertex_circle_template_lemma_catalog.json` as a
  single 12-template lemma-candidate crosswalk before writing proof-facing
  local lemmas;
- use `data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json` as
  the first focused review-pending T01/F09 self-edge local lemma packet;
- use `data/certificates/n9_vertex_circle_t02_self_edge_lemma_packet.json` as
  the next focused review-pending T02 multi-family self-edge local lemma packet;
- use `data/certificates/n9_vertex_circle_t03_self_edge_lemma_packet.json` to
  replay the focused review-pending T03 multi-family self-edge local lemma
  packet;
- use `data/certificates/n9_vertex_circle_t04_self_edge_lemma_packet.json` to
  replay the focused review-pending T04/F13 four-row selected-path self-edge
  proof note;
- use `data/certificates/n9_vertex_circle_t05_self_edge_lemma_packet.json` to
  replay the focused review-pending T05/F10 nested-spoke alternate self-edge
  proof note;
- use `data/certificates/n9_vertex_circle_t06_self_edge_lemma_packet.json` to
  replay the focused review-pending T06/F11 nested-spoke alternate self-edge
  proof note;
- use `data/certificates/n9_vertex_circle_t07_self_edge_lemma_packet.json` to
  replay the focused review-pending T07/F06 nested-spoke alternate self-edge
  proof note;
- use `data/certificates/n9_vertex_circle_t08_self_edge_lemma_packet.json` to
  replay the focused review-pending T08/F02 nested-spoke alternate self-edge
  proof note;
- use `data/certificates/n9_vertex_circle_t09_self_edge_lemma_packet.json` to
  replay the focused review-pending T09/F03 nested-spoke alternate self-edge
  proof note;
- use `data/certificates/n9_vertex_circle_t10_strict_cycle_lemma_packet.json`
  to replay the focused review-pending T10/F12 strict-cycle local lemma packet;
- use `data/certificates/n9_vertex_circle_t11_strict_cycle_lemma_packet.json`
  to replay the focused review-pending T11/F07 strict-cycle local lemma packet;
- use `data/certificates/n9_vertex_circle_t12_strict_cycle_lemma_packet.json`
  to replay the focused review-pending T12/F16 strict-cycle local lemma packet;
- use the 2026-06-09 aggregate A10 review note as the current internal review
  record for the T01/T02/T03/T04/T05/T06/T07/T08/T09 self-edge and
  T10/T11/T12 strict-cycle integrations, keeping it scoped as proof-mining
  coverage of stored packets rather than an independent `n=9` proof or
  source-of-truth A10 promotion;
- use
  `scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py --check --assert-expected --summary-json`
  to cross-check the 12 focused packet JSON files against the source template
  packets, template catalog, and aggregate focused-note ledger before reviewing
  packet soundness; use `--json` when the full packet records are needed;
- use
  `scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py --check --assert-expected --summary-json`
  to join the same 12 focused packets to their packet-specific mini-replay
  artifacts, checking identity, source schemas, families, obstruction flags,
  and compact shape counts only; use `--json` when the full mini-replay
  records are needed;
- use `data/certificates/n9_vertex_circle_local_lemma_simple_replay.json` to
  replay the aggregate local-template coverage from stored packet JSON without
  sharing the main quotient-replay helper;
- use
  `scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py --check --assert-expected --summary-json`
  to compare the aggregate local-lemma scan and simple replay
  family-by-family; use `--json` when the full family crosswalk records are
  needed;
- use
  `scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py --check --assert-expected --summary-json`
  to compare the review-pending exhaustive counts, motif classification, and
  local-lemma replay chain without rerunning the brancher; use `--json` when
  the full family crosswalk records are needed;
- use
  `scripts/check_relation_skeleton_local_lemma_crosswalk.py --check --assert-expected --summary-json`
  to compare the 16-entry relation-skeleton catalog with the same
  aggregate/simple-replay local-lemma family accounting; use `--json` when
  the full family crosswalk records are needed;
- use
  `scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py --check --assert-expected --summary-json`
  to compare those 16 relation skeletons with the closed-descent packet's
  one-class self-edge and multi-class strict-cycle regions;
- use
  `scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --summary-json`
  to run the focused packet/catalog, focused mini-replay,
  aggregate/simple-replay, exhaustive/local-lemma, and
  relation-skeleton/local-lemma handoffs as one review-pending audit path,
  with the relation-skeleton/closed-descent companion summary and adjacent
  handoff checks that localize future drift between layers; use `--json`
  when the full layer and manifest records are needed;
- use the focused mini-replay commands
  `scripts/check_n9_t01_self_edge_minireplay.py --check --assert-expected --json`,
  `scripts/check_n9_t02_self_edge_minireplay.py --check --assert-expected --json`,
  `scripts/check_n9_t03_self_edge_minireplay.py --check --assert-expected --json`,
  `scripts/check_n9_t04_self_edge_minireplay.py --check --assert-expected --json`,
  `scripts/check_n9_t05_self_edge_minireplay.py --check --assert-expected --json`,
  `scripts/check_n9_t06_self_edge_minireplay.py --check --assert-expected --json`,
  `scripts/check_n9_t07_self_edge_minireplay.py --check --assert-expected --json`,
  `scripts/check_n9_t08_self_edge_minireplay.py --check --assert-expected --json`,
  `scripts/check_n9_t09_self_edge_minireplay.py --check --assert-expected --json`,
  `scripts/check_n9_t10_strict_cycle_minireplay.py --check --assert-expected --json`,
  `scripts/check_n9_t11_strict_cycle_minireplay.py --check --assert-expected --json`,
  and
  `scripts/check_n9_t12_strict_cycle_minireplay.py --check --assert-expected --json`
  as minimal input-data replays for the currently extracted self-edge and
  strict-cycle packets;
- use
  `scripts/check_n9_t10_paired_square_entry.py --check --assert-expected --json`
  as a T10/F12 diagnostic companion only, not a theorem;
- use
  `scripts/check_turn_inequality_indexing.py --check --assert-expected --summary-json`
  to audit the n=9 weak-turn offset/indexing convention against the current
  term emitter; this is implementation-convention scaffolding only, not a
  proof of the geometric turn lemma;
- use
  `scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --summary-json`
  to audit the stored integer dual certificates for the candidate weak
  turn-inequality system on all 184 regenerated n=9 frontier assignments,
  while keeping the geometric turn lemma and indexing conventions
  review-pending; use `--json` when the full certificate rows are needed;
- test whether the same motifs appear in the P18 obstruction and fail in the
  recorded `C19_skew` vertex-circle-only survivor, which is now retired as a
  fixed abstract pattern by the separate Z3 Kalmanson certificate;
- use `docs/n9-vertex-circle-frontier-comparison.md` as the current guardrail:
  exact n=9 cores do not embed into P18 or C19, although P18 shares a loose
  strict-cycle span shape;
- identify the extra exact ingredient needed for `C19_skew`, likely
  Altman/Kalmanson or stronger radius propagation.

Acceptance standard: a reusable lemma should state precise incidence/order
hypotheses and produce a self-edge or strict cycle without enumerating all n=9
selected-witness assignments.

## Priority 6b - audit the n=10 singleton-slice draft

Target: `docs/n10-vertex-circle-singleton-slices.md` and
`data/certificates/n10_vertex_circle_singleton_slices.json`.

Reviewer packet: `docs/n10-vertex-circle-singleton-review-packet.md` collects
the current evidence layers, reproduction commands, missing promotion evidence,
and safe acceptance outcomes. It is a worksheet only and does not promote the
n=10 singleton artifact beyond draft.

The incoming n=10 continuation covers all 126 row0 singleton slices and records
zero full selected-witness assignments under the pair/crossing/count plus
vertex-circle filters. Treat this as a draft until an independent audit checks:

- the generic checker source against the exact pruning lemmas;
- the row0 singleton coverage `[0,126)` and absence of hidden symmetry
  quotienting;
- the input-data audit
  `scripts/check_n10_singleton_input_audit.py --check --assert-expected --json`,
  which recomputes row0 choices as lexicographic 4-subsets of labels `1..9`
  and checks stored ranges, witnesses, masks, and aggregate arithmetic without
  rerunning the search;
- the secondary first-five replay in
  `data/certificates/2026-05-05/n10_secondary.json`, which cross-checks only
  rows `0..4` under an extra triple-intersection necessary filter;
- that minimum-remaining-options branching changes only search order;
- that partial vertex-circle pruning uses only already-fixed selected rows and
  selected-distance equalities;
- that a second implementation or replayable terminal-conflict certificate
  agrees with all 126 slices, not only the current selected row0 spot-checks.

Acceptance standard: a reviewer should either promote the artifact to the same
review-pending finite-case status as n=9, or identify the exact implementation,
coverage, or certificate gap. This may not update the official/global status or
the repo source-of-truth strongest result without a broader review decision.

## Priority 7 - review the C19 all-order Kalmanson SMT certificate

Target: `data/certificates/c19_skew_all_orders_kalmanson_z3.json` and
`scripts/check_kalmanson_two_order_z3.py`.

The C19 sparse fixed-pattern lead is now killed across all cyclic orders by a
Z3 refinement certificate. Keep this separate from the small-case claim and
from the global Erdos #97 status.

Review checklist:

- every stored forbidden ordered-quadrilateral pair is validated as a genuine
  inverse pair of Kalmanson row vectors after selected-distance quotienting;
- label `0` at position `0` is only a cyclic-order representation choice, not a
  hidden loss of cases;
- the Z3 constraints encode exactly "not both ordered quadrilaterals occur";
- replaying the stored clauses gives UNSAT without relying on the refinement
  search history;
- the all-order UNSAT step is replayed by at least one Z3-independent route,
  such as a DIMACS/DRAT/LRAT proof, another SMT solver with a checkable proof,
  or a pure finite-order proof checker for the stored clauses;
- `scripts/export_c19_kalmanson_order_cnf.py` now provides the DIMACS CNF
  target and checked summary hash for that replay, but no DRAT/LRAT or
  equivalent proof object is checked yet;
- `scripts/probe_c19_proof_tooling.py --json` records whether the local
  environment has a supported SAT proof solver/checker pair, and
  `--check-c19-cnf-summary` also checks the stored CNF summary against the
  deterministic exporter, but this is still an environment/preflight
  diagnostic only and not proof evidence;
- an UNSAT core alone is not treated as a proof object unless a separate
  checker verifies it;
- the claim remains scoped to the fixed abstract `C19_skew` selected-witness
  pattern.

Acceptance standard: a reviewer should either accept the certificate as an
exact all-order obstruction for fixed abstract `C19_skew` with an independent
UNSAT replay path, or identify a specific encoding, solver-trust, or verifier
gap. Until then, the stored artifact remains a checked Z3 certificate rather
than a solver-independent proof object.

## Priority 7b - audit the C19 sampled-prefix catalog prefilter

Target:
`data/certificates/c19_kalmanson_prefix_window_catalog_prefilter_sweep_288_479.json`,
`reports/c19_prefilter_catalog_unit_supports.json`, and
`scripts/sweep_c19_kalmanson_prefix_windows_catalog_prefilter.py`.

The catalog-prefilter sweep is exact for sampled C19 prefix windows 288-479
and should remain separate from the all-order Z3 certificate above. It applies
the two-row prefilter first, then three cataloged unit supports for the eight
recorded two-row misses, leaving zero ordinary fifth-pair Farkas fallbacks in
that sampled range.

Review checklist:

- the three catalog supports sum to zero after selected-distance quotienting;
- each catalog support row is forced by the recorded fallback child state;
- the sweep records the same 192 sampled prefixes and 10,350 fifth-pair
  children as the two-row-only compact sweep;
- catalog support use is limited to children missed by the two-row lookup;
- the claim remains scoped to sampled prefix indices 288-479.

Acceptance standard: a reviewer should either accept the catalog prefilter as
an exact sampled-window replay optimization, or identify a specific mismatch
between the catalog support artifact and the sweep accounting.

## Priority 8 - extend the two-certificate search beyond retired sparse leads

The C13 Sidon pattern and C19 skew pattern are now both killed across all cyclic
orders by exact two-inequality Kalmanson inverse-pair methods. Use them as
benchmarks for the larger frontier:

- classify the inverse-pair templates that prune C13 and C19;
- use
  `scripts/analyze_kalmanson_inverse_pair_templates.py --assert-expected --json`
  as the current C13/C19 coefficient-template diagnostic: both fixed pilots
  expose only the one-class-vs-one-class and two-classes-vs-two-classes
  quotient-vector inverse templates;
- use
  `scripts/analyze_kalmanson_sparse_frontier_templates.py --assert-expected --json`
  as the current C25/C29 sparse-frontier template-availability diagnostic:
  both larger Sidon patterns expose the same two quotient-vector inverse
  templates, but this is not cyclic-order coverage or an obstruction;
- use
  `scripts/check_sparse_frontier_kalmanson_escapes.py --check --assert-expected --json`
  as the fixed-order C25/C29 negative-control audit showing that the stored
  sparse-frontier orders still escape the direct two-inequality inverse-pair
  filter when all strict Kalmanson rows are replayed;
- use the recorded C29 fixed-order certificate
  `data/certificates/c29_sidon_fixed_order_kalmanson_165_unsat.json` as the
  benchmark for full-cone Kalmanson/Farkas certificates that are not visible to
  the two-inequality inverse-pair filter;
- try to turn full-cone fixed-order certificates into reusable order-search
  clauses for larger sparse/Sidon patterns;
- look for a bridge from arbitrary selected-witness counterexamples to a
  classified family where Kalmanson/SMT certificates can be applied.

## Priority 8b - strengthen the fragile-cover bridge

Target: `docs/minimal-fragile-cover-bridge.md` and
`src/erdos97/fragile_hypergraph.py`.

Bridge target map: `docs/lemma-driven-bridge-targets.md` summarizes the
current proved footholds, finite targets, candidate bridge-lemma contracts, and
negative controls. Use it to choose a lemma that would strengthen the bridge
rather than another fixed selected-row neighborhood replay.

Minimality proves that every minimal counterexample has a fragile-cover
witness system, but the block-6 abstract family shows the current hypergraph
axioms are too weak. The current checker now also has an optional full-row
extension diagnostic: it rejects the single six-vertex block but still permits
two disjoint blocks. The next useful bridge work is to add a geometric
condition that the surviving multi-block family does not automatically satisfy:

- dependency-cycle restrictions for the witness map `pi`;
- critical-radius ordering or deletion-dependency inequalities;
- exact row-circle constraints on the fragile rows;
- interaction between fragile-cover rows and stuck-set/ear-orderability
  failures.
- adaptive radius-blocker analysis, as recorded in
  `docs/adaptive-radius-blocker-bridge.md`, which keeps all rich distance
  classes visible instead of fixing one selected row per center.
- the exact-four-row radius-blocker/vertex-circle pilot recorded in
  `docs/radius-blocker-vertex-circle-pilot.md`, as a first replayable packet
  format for testing blocker shapes against quotient self-edges and strict
  cycles.
- the full `n=9` exact-four radius-blocker packet recorded in
  `docs/n9-full-radius-blocker-vertex-circle-packet.md`, where the fixed
  natural-order blocker `{0,1,2,3}` has 90 incidence survivors and all are
  vertex-circle obstructed.
- the natural-order `n=9` radius-blocker shape sweep recorded in
  `docs/n9-radius-blocker-shape-sweep.md`, where all `10` cyclic-dihedral
  four-blocker shapes have obstructed incidence survivors. This is finite
  packet evidence only.
- the order-reduction crosswalk recorded in
  `docs/n9-radius-blocker-order-reduction.md`, which reduces arbitrary
  cyclic-order placements of the same exact-four four-blocker packet to the
  natural-order shape sweep.
- the bounded richer-class projection pilot recorded in
  `docs/n9-radius-blocker-rich-projection-pilot.md`, which expands one
  synthetic size-five class at each center to exact four-subset row options.
- the full rich-class quotient replay pilot recorded in
  `docs/n9-radius-blocker-rich-quotient-pilot.md`, which checks the same
  synthetic size-five family without choosing four-subsets. This is finite
  packet evidence only.
- the generated full rich-class quotient sweep recorded in
  `docs/n9-radius-blocker-rich-quotient-sweep.md`, which quantifies that
  replay over `20` synthetic size-five packets derived from the stored
  self-edge and strict-cycle obstruction examples for all `10` four-blocker
  shapes. This is still generated finite packet evidence only.
- the bounded rich-extension neighborhood recorded in
  `docs/n9-radius-blocker-rich-extension-neighborhood.md`, which varies the
  added labels around those `20` packets by every Hamming-distance `1` or `2`
  radius-blocker-preserving replacement and checks `5,996` quotient-obstructed
  variants. This is still finite neighborhood evidence only.
- the one-packet full rich-extension product pilot recorded in
  `docs/n9-radius-blocker-rich-extension-product-pilot.md`, which exhausts
  `196,608` radius-blocker-preserving size-five variants for the first
  maximum-size generated packet. This is still finite packet evidence only;
- the all-packet generated rich-extension product sweep recorded in
  `docs/n9-radius-blocker-rich-extension-product-sweep.md`, which exhausts
  `2,899,968` radius-blocker-preserving size-five variants over the `20`
  generated source packets. This is still finite generated-packet evidence
  only; the next review target is a principled rich-class bridge hypothesis
  or a generator-independent catalogue, not another copy of the same product
  replay.
- the generator-independent all-five-rich support obstruction recorded in
  `docs/n9-all-five-rich-support-obstruction.md`, which leaves the generated
  packet family and closes the full `56^9` size-five support assignment space
  using only the two-circle row-pair cap and radical-axis crossing filters.
  This rules out the all-centers-size-at-least-five `n=9` support subcase
  repo-locally. The localized rich-support counting lemma recorded in
  `docs/localized-rich-support-counting.md` now sharpens the support bridge:
  any hypothetical 4-bad nonagon is forced into the all-exact-four,
  selected-indegree-four support frontier by counting alone. This still does
  not prove `n=9` or prove the adaptive blocker bridge.
- the generator-independent mixed rich-support reduction recorded in
  `docs/n9-mixed-rich-support-reduction.md`, which closes the four/five
  support catalogue under the same pair/crossing filters plus witness-pair
  capacity. It is now catalogue provenance for the localized counting
  shortcut: it leaves exactly `184` complete assignments and all are
  all-exact-four. The mixed/frontier crosswalk recorded in
  `docs/n9-mixed-rich-frontier-crosswalk.md` checks that those `184` terminal
  assignments are exactly the stored pre-vertex-circle frontier as a labelled
  row set, so the next review target is the exact-four frontier itself or a
  smaller reusable replacement for the review-pending vertex-circle pipeline.
- bootstrap-core/private-halo analysis, as recorded in
  `docs/bootstrap-core-bridge.md`, which adds a `rho > 3` closure-rank witness,
  deletion closures, and weighted cyclic outside-pair capacity.
- bootstrap-core crosswalk evidence, as recorded in
  `docs/bootstrap-core-crosswalk.md`, showing that the current singleton-rich
  sparse/frontier motifs have rank greater than 3 but retain positive weighted
  capacity margin; any useful next condition should reduce that slack or add
  additional private-pair demand.
- bootstrap / vertex-circle overlay evidence, as recorded in
  `docs/bootstrap-vertex-circle-overlay.md`, showing that the two tight
  non-ear-orderable `n=9` rows both join to the `T12/F16` strict-cycle template
  but not by a bootstrap-core-only contradiction.
- bootstrap/T12 forcing-target evidence, as recorded in
  `docs/bootstrap-t12-forcing-targets.md`, showing that source `81` has no
  direct private-pair hit and source `151` has only partial direct hits, so the
  next useful condition should force missing row centers or equality connectors
  rather than rely on private pairs alone.
- bootstrap/T12 row-pressure evidence, as recorded in
  `docs/bootstrap-t12-row-pressure.md`, splitting the six missing row centers
  into deletion-closure-exposed rows, one-outside-label rows, and one
  outside-pair row with partial private-pair support.
- bootstrap/T12 closure-exposed evidence, as recorded in
  `docs/bootstrap-t12-closure-exposed.md`, isolating the two activation-ready
  deletion-closure rows before attacking the one-outside-label and outside-pair
  cases.
- bootstrap/T12 one-outside-label evidence, as recorded in
  `docs/bootstrap-t12-one-outside.md`, isolating the three singleton-support
  rows where pair-capacity arguments do not directly apply.
- bootstrap/T12 outside-pair evidence, as recorded in
  `docs/bootstrap-t12-outside-pair.md`, isolating the remaining row where the
  private-pair ledger has partial direct support.
- bootstrap/T12 activation-requirement evidence, as recorded in
  `docs/bootstrap-t12-activation-requirements.md`, separating connector-pair
  and strict-edge endpoint requirements from the still-unproved row-forcing
  step.
- bootstrap/T12 bridge-target-map evidence, as recorded in
  `docs/bootstrap-t12-bridge-target-map.md`, joining those packets into six
  explicit next-lemma targets, with `151:7`, `151:8`, and `151:5` as the main
  hard/open rows.
- bootstrap/T12 hard strict-endpoint evidence, as recorded in
  `docs/bootstrap-t12-hard-strict-endpoints.md`, isolating `151:7` and
  `151:8` as the rows where strict-edge endpoint sets are still not supplied
  by closure exposure or singleton support.
- bootstrap/T12 open connector-pair evidence, as recorded in
  `docs/bootstrap-t12-open-connector-pair.md`, isolating `151:5` as the row
  where connector pair `[7,8]` is still split across singleton support and
  partial closure evidence.
- bootstrap/T12 relation-sufficient row evidence, as recorded in
  `docs/bootstrap-t12-relation-sufficient-rows.md`, isolating `81:3`, `81:8`,
  and `151:6` as rows where connector relation evidence is present but
  row/rich-class forcing remains open.
- bootstrap/T12 focused `81:3` closure-target evidence, as recorded in
  `docs/bootstrap-t12-81-3-closure-target.md`, isolating the unique target
  where full-row deletion-closure exposure, relation sufficiency, and the
  final `T12/F16` equality connector role coincide; this is still an open
  row/rich-class forcing target.
- bootstrap/T12 focused `81:3` rich-triple contract evidence, as recorded in
  `docs/bootstrap-t12-81-3-rich-triple-contract.md`, weakening the target to
  the connector pair `[0,1]`: any genuine rich class at center `3` containing
  that pair gives `[1,3]=[0,3]`, while a connector-avoiding activation must
  expose label `6` first.
- bootstrap/T12 focused `81:3` order-escape evidence, as recorded in
  `docs/bootstrap-t12-81-3-order-escape.md`, checking that the fixed
  singleton-rich closure does not expose label `6` before center `3`; any
  successful escape now needs genuine rich-class data that supplies label `6`
  first, or a proof that no such supply exists.
- bootstrap/T12 focused `81:3` escape-CSP evidence, as recorded in
  `docs/bootstrap-t12-81-3-escape-auxiliary-csp.md` and
  `docs/bootstrap-t12-81-3-trigger-uniqueness.md`, ruling out the specified
  one-supply/one-connector auxiliary trigger model and showing each specified
  trigger family is same-center unique. The remaining target is outside those
  specified trigger families or a genuine rich-class/minimality hypothesis,
  not more copies of the same supply or connector trigger at the same center.
- bootstrap/T12 focused `81:3` rich-support evidence, as recorded in
  `docs/bootstrap-t12-81-3-escape-rich-support-csp.md`, extending the auxiliary
  escape CSP from 4-set trigger classes to larger rich supports at centers `3`
  and `6`. The remaining target is now support existence, additional
  auxiliary supports at other centers, or a different bridge target.
- bootstrap/T12 focused `81:3` first-supply-chain evidence, as recorded in
  `docs/bootstrap-t12-81-3-first-supply-chains.md`, allowing the first
  pre-`3` activation from seed `[0,1,4]` to occur at any non-seed, non-`3`
  center. This leaves exactly three basic-filter prefix survivors, all with
  first activation at center `8`, and no immediate center-`6` label-`6` supply
  extension for those prefixes. The next bounded continuation layers are
  recorded in the second-supply-chain, second-step-chain, and post-`8`
  entries below.
- bootstrap/T12 focused `81:3` second-supply-chain prefix evidence, as
  recorded in `docs/bootstrap-t12-81-3-second-supply-chains.md`, allowing one
  further non-target, non-supply activation from closure `[0,1,4,8]`. This
  leaves one center-`8` then center-`2` prefix, with support `[1,3,4,8]`, and
  no immediate center-`6` label-`6` supply extension for that prefix. This is
  an intermediate crosswalk toward the broader distinct-intermediate and
  post-`8` chain audits.
- bootstrap/T12 focused `81:3` second-step-chain evidence, as recorded in
  `docs/bootstrap-t12-81-3-second-step-chains.md`, testing distinct
  intermediate centers from `{2,5,7}` after the three stored center-`8`
  prefixes and before center `6` supplies label `6`. This closes that bounded
  one-support-per-activated-center continuation model under the same basic
  filters, while leaving repeated/multiple supports, richer catalogues, and
  genuine rich-class forcing open.
- bootstrap/T12 focused `81:3` post-`8` supply-chain accounting, as recorded
  in `docs/bootstrap-t12-81-3-post8-supply-chains.md`, giving the raw
  denominator for the same bounded continuation model: `3,918,164,268`
  support catalogues, `58` initially compatible catalogues, and zero
  selected-row survivors.
- bootstrap/T12 focused `81:3` chain-closure and activation negative-control
  evidence, as recorded in
  `docs/bootstrap-t12-81-3-chain-closure-csp.md` and
  `docs/closure-activation-negative-controls.md`. The ordered chain CSP leaves
  four non-supply prefixes and no surviving prefix whose next activated center
  is `6`; the negative controls show that closure exposure, full target-label
  visibility, or full selected-row incidence checks do not by themselves pin
  the named fourth witness. The remaining bridge target needs activation
  provenance, repeated/multiple support analysis, or a genuine
  rich-class/minimality hypothesis.
- bootstrap/T12 focused `81:3` repeated-support evidence, as recorded in
  `docs/bootstrap-t12-81-3-repeated-support-catalogue-audit.md`, attaching one
  disjoint same-center support to each already activated prefix center in the
  four chain-closure survivors. Five repeated-support catalogues generate
  `464` center-`6` supply-extension attempts; one is initially compatible and
  still has no selected-row completion. Broader multiple-support catalogues
  and genuine rich-class forcing remain open.
- bootstrap/T12 focused `81:3` two-repeated-support evidence, as recorded in
  `docs/bootstrap-t12-81-3-two-repeated-support-catalogue-audit.md`, attaching
  two repeated supports to already activated prefix centers in the four
  chain-closure survivors, each disjoint from the supports already present at
  its own center. The single deduplicated two-support catalogue is initially
  incompatible, and all `118` center-`6` supply-extension attempts remain
  initially incompatible. Run
  `scripts/check_bootstrap_t12_81_3_two_repeated_support_catalogue_audit.py --check --assert-expected --summary-json`
  for the compact reviewer payload, or `--json` for the full catalogue record
  and supply-extension scan details. Broader multiple-support catalogues and
  genuine rich-class forcing remain open.
- bootstrap/T12 focused `81:3` repeated-support saturation evidence, as
  recorded in
  `docs/bootstrap-t12-81-3-repeated-support-saturation-audit.md`, enumerating
  all further same-center-disjoint repeated supports in the same stored-prefix
  model. It records four base catalogues, five one-repeated-support
  catalogues, one deduplicated two-repeated-support catalogue, and no
  three-repeated-support catalogue. Run
  `scripts/check_bootstrap_t12_81_3_repeated_support_saturation_audit.py --check --assert-expected --summary-json`
  for the compact reviewer payload, or `--json` for the full level records and
  terminal extension profiles. Genuinely richer catalogues, activation
  provenance, and rich-class forcing remain open.
- bootstrap/T12 focused `81:8` singleton-support evidence, as recorded in
  `docs/bootstrap-t12-81-8-singleton-support-audit.md`, showing that the fixed
  source-`81` neighborhood and one-row-drop relaxation have no non-original
  row-`8` activation survivor under basic incidence/crossing filters. The
  remaining target is still genuine singleton-support or row-forcing
  geometry, not a proof that row `8` is forced.
- bootstrap/T12 focused `151:6` outside-pair evidence, as recorded in
  `docs/bootstrap-t12-151-6-outside-pair-audit.md`, showing that the fixed
  source-`151` neighborhood and one-row-drop relaxation have no non-original
  row-`6` activation survivor under basic incidence/crossing filters. The
  remaining target is still genuine outside-pair support or row-forcing
  geometry, not a proof that row `6` is forced.
- bootstrap/T12 focused `151:6` outside-pair two-row-drop evidence, as
  recorded in `docs/bootstrap-t12-151-6-outside-pair-two-row-drop.md`, showing
  that allowing any two non-target source-`151` rows to move still leaves only
  the `28` trivial original-neighborhood survivors. The remaining target is
  still genuine outside-pair support or row-forcing geometry, not a proof that
  row `6` is forced.
- bootstrap/T12 focused `151:6` outside-pair full-neighborhood vertex-circle
  evidence, as recorded in
  `docs/bootstrap-t12-151-6-outside-pair-full-neighborhood-vertex-circle.md`,
  letting all non-target selected rows move. Basic filters leave `28` complete
  assignments, including `21` with non-original row `6`, and exact
  vertex-circle quotient replay kills all `28`. The remaining target is still
  genuine outside-pair support or row-forcing geometry, not a proof that row
  `6` is forced.
- bootstrap/T12 focused `151:6` outside-pair connector-contract evidence, as
  recorded in
  `docs/bootstrap-t12-151-6-outside-pair-connector-contract.md`, proving only
  the local conditional that a genuine center-`6` rich class containing
  witnesses `0` and `8` supplies `[0,6]=[8,6]`. The remaining target is to
  force an endpoint-`8` support or analyze the private-halo-only pair `[3,5]`;
  this is not support existence, row forcing, or a bridge proof.
- bootstrap/T12 focused `151:6` endpoint-`8` forcing preflight evidence, as
  recorded in
  `docs/bootstrap-t12-151-6-endpoint8-forcing-preflight.md`, checking that
  current connector-contract plus escape-partition evidence is not enough to
  accept endpoint-`8` forcing: the private-halo-only `[3,5]` lane has `12`
  basic-filter survivors. This is a gate-status diagnostic only, not a proof
  that endpoint `8` is forced and not a proof that `[3,5]` is impossible.
- bootstrap/T12 focused `151:6` private-lane core-catalog evidence, as
  recorded in
  `docs/bootstrap-t12-151-6-private-lane-core-catalog.md`, extracting minimal
  vertex-circle cores from those `12` private-lane survivors. Every survivor
  has a three-row strict-cycle core containing row `6 -> [0,3,5,7]`. This is
  local selected-row proof-mining data only; it does not prove the private
  pair `[3,5]` is impossible under genuine rich-class support geometry.
- bootstrap/T12 focused `151:6` private-lane strict-core split evidence, as
  recorded in
  `docs/bootstrap-t12-151-6-private-lane-strict-core-split.md`, splitting all
  `44` row-`6` three-row strict-cycle cores into `32` label-`8`-visible cores
  and `12` label-`8`-free cores. The `10` distinct exact label-`8`-free
  signatures are the concrete residual private-pair targets; this still does
  not prove support existence, row forcing, endpoint-`8` forcing, or that pair
  `[3,5]` is impossible.
- bootstrap/T12 focused `151:6` label-`8`-free residual-target evidence, as
  recorded in
  `docs/bootstrap-t12-151-6-label8-free-residual-targets.md`, showing that all
  `10` distinct exact residual signatures require auxiliary witness label `4`.
  Eight signatures use label `4` in both auxiliary rows, and two signatures
  have strict-cycle edges that do not directly mention label `4`; this is a
  support-geometry target only, not a proof of support existence, row forcing,
  endpoint-`8` forcing, or impossibility of `[3,5]`.
- bootstrap/T12 focused `151:6` label-`4` quotient-role evidence, as recorded
  in `docs/bootstrap-t12-151-6-label4-quotient-roles.md`, showing that every
  label-`8`-free residual strict cycle has a label-`4`-bearing quotient class:
  `8` signatures reach label `4` directly through cycle-edge endpoints, and
  `2` signatures reach label `4` only through selected-distance quotient
  equalities. This is still a bridge target, not a support-existence, row
  forcing, endpoint-`8` forcing, or `[3,5]` impossibility proof.
- bootstrap/T12 focused `151:6` label-`4` transfer-path evidence, as recorded
  in `docs/bootstrap-t12-151-6-label4-transfer-paths.md`, pinning shortest
  selected-distance paths from label-`4` pairs to residual strict-cycle
  endpoint pairs. Among the `19` label-`4` cycle-class incidences, `11` are
  direct endpoint hits, `5` require one equality edge, and `3` require two
  equality edges; the positive transfer-path edges occur only in rows `5`,
  `6`, and `7`. This is still a bridge target, not support existence, row
  forcing, endpoint-`8` forcing, or `[3,5]` impossibility.
- bootstrap/T12 focused `151:6` label-`4` transfer-obligation evidence, as
  recorded in `docs/bootstrap-t12-151-6-label4-transfer-obligations.md`,
  splitting the positive transfer paths into `7` unique row-local equality
  obligations and `6` path motifs. Every positive transfer starts with a
  label-`4` spoke swap at row `5` or row `7`, while the only row-`6`
  obligation is the repeated connector step `[5,6]=[0,6]` after row `5`
  supplies `[4,5]=[5,6]`. This is still a bridge target, not support
  existence, row forcing, endpoint-`8` forcing, or `[3,5]` impossibility.
- bootstrap/T12 focused `151:6` label-`4` transfer length-component evidence,
  as recorded in
  `docs/bootstrap-t12-151-6-label4-transfer-length-components.md`, collapsing
  those row-local obligations into `6` undirected segment-length components
  over `9` distinct segments. The packet splits the components into `3`
  edge-diagonal cases, `2` diagonal-only cases, and the unique row-`6`
  connector cascade `D[0,6]=D[4,5]=D[5,6]`, tying two hull edges to a
  cyclic-gap-`3` diagonal. This is still a support-geometry target, not
  support existence, row forcing, endpoint-`8` forcing, or `[3,5]`
  impossibility.
- bootstrap/T12 focused `151:6` label-`4` transfer component-feasibility
  negative-control evidence, as recorded in
  `docs/bootstrap-t12-151-6-label4-transfer-component-feasibility.md`, giving
  a strict cyclic convex `9`-gon arc witness for each of the six
  length-components considered alone, including a modulus-`13` witness for
  the row-`6` cascade. This rejects component-alone impossibility only; the
  remaining target must use genuine private-support, rich-class, row-forcing,
  or activation-provenance hypotheses.
- bootstrap/T12 focused `151:6` label-`4` support-hypothesis evidence, as
  recorded in
  `docs/bootstrap-t12-151-6-label4-support-hypothesis-ledger.md`, pinning the
  `7` centered support requirements behind those six components. The unique
  row-`6` cascade needs center `5` with witnesses `[4,6]` and center `6` with
  witnesses `[0,5]`, while no label-`4` transfer support requirement is the
  exact private pair `[3,5]`. The remaining target is to inject genuine
  private-pair/rich-class geometry into that support layer.
- bootstrap/T12 focused `151:6` label-`4` cascade row-criticality evidence,
  as recorded in
  `docs/bootstrap-t12-151-6-label4-cascade-row-criticality.md`, checking that
  the three auxiliary-center-`5,8` cascade signatures are strict-cycle
  obstructed with the full local row package `{5,6,8}`, while every nonempty
  proper row truncation is quotient-clean. The remaining target is to force
  row `8` as the strict endpoint row alongside the row-`5`/row-`6` cascade
  equalities, or to find a different genuine support-rich obstruction.
- bootstrap/T12 focused `151:6` label-`4` cascade endpoint-`8` target
  evidence, as recorded in
  `docs/bootstrap-t12-151-6-label4-cascade-endpoint8-targets.md`, replacing
  row `8` by every center-`8` rich class containing `[0,4,6]` for the three
  stored cascade packages. All `93` signature-level rich supersets are
  quotient-obstructed (`72` self-edges and `21` strict cycles). The remaining
  target is to force that center-`8` rich triple from genuine
  private-pair/rich-class geometry, or to find a different support-rich
  obstruction.
- bootstrap/T12 focused `151:6` label-`4` center-`8` rich-triple preflight
  evidence, as recorded in
  `docs/bootstrap-t12-151-6-label4-center8-rich-triple-preflight.md`, checking
  that current support evidence does not yet force the `[0,4,6]` target. The
  support ledger has requirements at centers `5`, `6`, and `7`, no center-`8`
  support requirement, no label-`8` support witness, and no support
  requirement containing the full triple `[0,4,6]`. This is a gate diagnostic
  only, not a proof that the center-`8` rich triple is impossible or forced.
- bootstrap/T12 focused `151:6` label-`4` center-`8` source-crosswalk evidence,
  as recorded in
  `docs/bootstrap-t12-151-6-label4-center8-source-crosswalk.md`, checking that
  the existing source-`151` row-`8` singleton/one-outside packet is not a
  source for the cascade triple. Its candidates use core `[1,2]` plus supports
  `[5,7]`, so no checked row contains a pair or full triple from `[0,4,6]`.
  The remaining target is still a genuine new center-`8` geometric source or
  a different support-rich obstruction.
- bootstrap/T12 focused `151:6` label-`4` center-`8` core-route evidence, as
  recorded in
  `docs/bootstrap-t12-151-6-label4-center8-core-route.md`, checking the
  private-lane strict-core split against the conditional endpoint target. It
  finds `8` of `9` center-`8` cores target-compatible with `[0,4,6]`, but only
  `4` of `32` label-`8`-visible cores are both label-`8`-visible and
  target-compatible, and `6` private-lane assignments still lack any center-`8`
  target core. The remaining target is to force a target-compatible center-`8`
  local core, not merely label-`8` visibility.
- bootstrap/T12 focused `151:6` label-`4` center-`8` residual target-row
  evidence, as recorded in
  `docs/bootstrap-t12-151-6-label4-center8-residual-target-rows.md`, checking
  the six no-center-`8`-target residual assignments. Four residual assignments
  contain `[0,4,6]` only as off-center strict-core rows at centers `2`, `5`,
  or `7`; assignments `0` and `11` are target-sparse. The remaining target is
  a genuine center-migration lemma for the off-center rows, or a separate
  obstruction for the target-sparse assignments.
- bootstrap/T12 focused `151:6` label-`4` center-`8` target-sparse completion
  evidence, as recorded in
  `docs/bootstrap-t12-151-6-label4-center8-target-sparse-completions.md`,
  checking the cheapest one-row repair for target-sparse assignments `0` and
  `11`. All `12` one-row completions of target-pair rows to `[0,4,6]` fail
  basic filters before vertex-circle replay. The remaining target is a
  genuine target-sparse obstruction or a stronger multi-row/center-migration
  mechanism, not a claim that assignments `0` and `11` are already impossible.
- bootstrap/T12 focused `151:6` label-`4` center-`8` target-sparse two-row
  repair evidence, as recorded in
  `docs/bootstrap-t12-151-6-label4-center8-target-sparse-two-row-repairs.md`,
  checking one additional arbitrary non-completion row replacement after each
  target-pair completion. All `6624` repair-extension candidates fail basic
  filters before vertex-circle replay. This motivates the depth-two repair
  packet below; it is still not a proof that assignments `0` and `11` are
  impossible.
- bootstrap/T12 focused `151:6` label-`4` center-`8` target-sparse three-row
  repair evidence, as recorded in
  `docs/bootstrap-t12-151-6-label4-center8-target-sparse-three-row-repairs.md`,
  checking two additional arbitrary non-completion row replacements after each
  target-pair completion. All `1599696` depth-two repair candidates fail
  basic filters before vertex-circle replay. The remaining target must use
  genuine support geometry, center migration, or a mechanism beyond one
  completion plus two arbitrary extra row repairs.
- bootstrap/T12 focused source-`151` singleton-support evidence, as recorded
  in `docs/bootstrap-t12-151-singleton-support-audit.md`, showing that rows
  `151:5` and `151:8` have no non-original activation survivor in the fixed
  source-`151` neighborhood or one-row-drop relaxation. The remaining target
  is still genuine singleton-support or row-forcing geometry, not a proof that
  either row is forced.
- bootstrap/T12 singleton full-neighborhood crosswalk evidence, as recorded
  in `docs/bootstrap-t12-singleton-full-neighborhood-crosswalk.md`, joining
  the source-`81` row-`8` and source-`151` rows `5`/`8` full-neighborhood
  vertex-circle diagnostics. Basic filters leave `84` complete assignments
  across those three one-outside-label singleton-support targets, and the
  source packets kill all `84` by vertex-circle replay. The remaining target
  is still genuine singleton/rich support existence or row-forcing geometry,
  not another selected-row-neighborhood crosswalk.
- block-6 vertex-circle full-extension evidence, as recorded in
  `data/certificates/block6_fragile_vertex_circle_extension_audit.json` and
  `docs/block6-fragile-vertex-circle-extension-audit.md`, showing that the
  two-block block-6 negative control has no natural-order full selected-row
  extension surviving the vertex-circle quotient self-edge / strict-cycle
  gate. This rejects one abstract family that passes fragile-cover hypergraph
  checks, but it remains natural-order and all-order/all-extension bridge work
  is still open.
- block-6 crossing-order sample evidence, as recorded in
  `data/certificates/block6_terminal_crossing_vertex_circle_sample.json`,
  checking two deterministic terminal-extension windows across all of their
  crossing-compatible cyclic orders. The `200` sampled terminal extensions
  yield `796` crossing-compatible orders, all killed by a vertex-circle
  quotient self-edge. This remains a bounded diagnostic sample only, not an
  all-extension or all-order obstruction.
- block-6 crossing-order full-sweep evidence, as recorded in
  `data/certificates/block6_terminal_crossing_vertex_circle_full_sweep.json`,
  checking all `105,978` terminal full extensions generated by the
  natural-order two-block audit across all `385,517` crossing-compatible cyclic
  orders those terminal extensions admit. Every order is killed by a
  vertex-circle quotient obstruction (`384,318` self-edges and `1,199` strict
  cycles). This still does not cover selected-row systems outside the
  natural-order terminal generator, so it remains a bounded diagnostic rather
  than all-extension/all-order closure.
- block-6 fixed-order probe evidence, as recorded in
  `data/certificates/block6_fixed_order_vertex_circle_probe.json`, checking
  the natural order and three non-natural cyclic orders. The non-natural probes
  each have a legal terminal selected-row extension outside the natural-order
  generator, but all four fixed-order searches close by order-specific
  vertex-circle pruning. This is fixed-order diagnostic evidence only, not
  all-order closure.
- block-6 block-preserving shuffle-order evidence, as recorded in
  `data/certificates/block6_shuffle_order_vertex_circle_sweep.json`, checking
  all `462` normalized cyclic orders that preserve internal order inside the
  two six-label blocks while shuffling the blocks. Every order-specific
  full-extension search closes by vertex-circle pruning, but this remains a
  bounded fixed-order-family diagnostic rather than all-order closure.
- block-6 reversed-second-block shuffle evidence, as recorded in
  `data/certificates/block6_reversed_block_shuffle_vertex_circle_escape.json`.
  This companion oriented-block family has `16` vertex-circle-clean fixed-order
  escape rows, so it is a negative control for relying on the vertex-circle
  gate alone. The follow-up
  `data/certificates/block6_reversed_block_clean_kalmanson.json` closes those
  16 stored fixed assignment/order pairs by exact Kalmanson quotient-cone
  certificates. The compact
  `data/certificates/block6_reversed_block_two_stage_closure.json` crosswalk
  verifies the combined `446 + 16 = 462` count for this bounded family, but
  this is still not all-order closure. The next bridge/filter step should
  either widen beyond this oriented-block slice or state a genuine
  minimal/rich-class hypothesis.
- block-6 first-block-forward two-orientation evidence, as recorded in
  `data/certificates/block6_forward_block_two_orientation_closure.json`,
  joins the forward-second-block vertex-circle sweep with the
  reversed-second-block two-stage packet. It checks `924` closed normalized
  shuffle orders when the first block stays forward and the second block is
  forward or reversed.
  This is still not first-block-reversed coverage, arbitrary-order closure, or
  a fragile-bridge proof; the next useful widening should either justify the
  missing orientation symmetry by a checked invariant, replay the missing
  orientations directly, or move to a richer minimal/rich-class bridge
  hypothesis.
- block-6 oriented-block reversal evidence, as recorded in
  `data/certificates/block6_oriented_block_reversal_closure.json`, verifies
  that cyclic reversal maps the two first-block-forward families bijectively
  to the two first-block-reversed families. It therefore transfers the same
  bounded closure counts to `1848` oriented-block shuffle orders. This still
  leaves arbitrary cyclic orders and non-block-preserving selected-row systems
  outside the packet, so the next useful widening should leave the
  block-preserving orientation family or state a genuine minimal/rich-class
  bridge hypothesis.
- block-6 row-depth survivor evidence, as recorded in
  `docs/block6-fragile-sixth-row-survivor-catalog.md` and checked by
  `scripts/check_block6_fragile_sixth_row_survivors.py --assert-expected --json`.
  It shows that fifth-row-only and sixth-row-only closure subclaims fail:
  all `166` clean fifth-row states admit a clean sixth row, and the
  low-support branch still has many clean seventh/eighth continuations. This
  is useful mainly as a negative control for bridge hypotheses that are too
  local.

Acceptance standard: a strengthened bridge should be stated as a necessary
condition for minimal counterexamples and should reject at least one abstract
fragile-cover family that passes the current pairwise/crossing checks.

## Priority 9 - strengthen only productive filters

The minimum-radius short-chord filter in `docs/minimum-radius-filter.md` is a
valid exact necessary condition, but it is weak: it does not kill `C19_skew`.
Treat it as recorded negative information unless it is extended into a genuine
radius-inequality propagation system or combined with cyclic-order search.
