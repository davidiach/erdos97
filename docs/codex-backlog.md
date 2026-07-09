# Codex Backlog

Status: operational planning guidance only; not mathematical evidence.

GitHub issues were rechecked on 2026-07-09: the repository had no open GitHub
issues. Legacy issues `#5`, `#81`, `#82`, and `#83` were closed with the
`completed` reason on 2026-05-17. Their historical acceptance-evidence
crosswalk remains in `docs/open-issue-resolution-crosswalk.md`, checked by
`python scripts/check_open_issue_resolution_crosswalk.py --assert-expected --json`.
This backlog is a Codex-facing companion to
`docs/review-priorities.md`; it does not change the repository claims. No
general proof and no counterexample are claimed, and the official/global status
remains falsifiable/open unless manually rechecked and updated from the
official source.

For task-selection discipline, read `docs/codex-strategy-instructions.md`.
Before starting a task, identify which bridge it might strengthen; if it does
not strengthen a bridge, record the audit, provenance, or negative-control value
that justifies doing it anyway.

## Recommended next technical PRs

Use this queue when no more specific issue is selected.

Bridge target map: `docs/lemma-driven-bridge-targets.md` is the current
claim-neutral ledger for choosing bridge work. Prefer PRs that prove one of
its named lemma contracts or reject one of its negative controls under explicit
minimal/rich-class hypotheses.

1. Use the vertex-circle route decision preflight
   `python scripts/check_n9_vertex_circle_route_decision_preflight.py --check --summary-json`
   to hand the 2026-06-09 internal A6/A7, A8, and A10 review notes into an
   explicit vertex-circle route gate decision, keeping any decision scoped as
   repo-local `n=9` review infrastructure rather than a general proof. The
   A6/A7 note records the source-frontier enumeration evidence bundle, the A8
   note records the local nested-chord strict-edge rule and checker-equivalence
   contract, and the A10 note records focused packet soundness plus aggregate
   bookkeeping. None of these notes closes its machine-readable gate without an
   explicit written decision. Start from
   `docs/n9-vertex-circle-local-lemma-review-packet.md`, which records the
   current five-layer audit path and review boundary. The aggregate note
   records the focused T01-T12 packet-soundness notes plus the A10 bookkeeping
   handoff; source-of-truth A10 promotion, `n=9`, and global status remain
   review-pending until an explicit decision record is supplied. The checked
   decision-request packet
   `python scripts/check_n9_vertex_circle_route_decision_request.py --check --summary-json`
   records the exact requested vertex-circle gate partition and reviewer
   commands without accepting any gate or updating source-of-truth status. The
   focused
   packet catalog audit command
   `python scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py --check --assert-expected --summary-json`
   now checks that the focused packet coverage, source template records,
   source catalog records, and aggregate focused-note crosschecks agree before
   packet soundness review; use `--json` when the full packet records are
   needed. The focused mini-replay crosswalk
   `python scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py --check --assert-expected --summary-json`
   joins those same 12 focused packets to their packet-specific mini-replay
   artifacts without promoting the layer to packet soundness or local-lemma
   completeness; use `--json` when the full mini-replay records are needed.
2. Use the stored simple replay artifact
   `data/certificates/n9_vertex_circle_local_lemma_simple_replay.json` as a
   reviewer-facing input for the aggregate local-template coverage. The replay
   checks the packet JSON without sharing the main quotient-replay helper, but
   it is still a packet audit rather than an `n=9` proof. The crosswalk command
   `python scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py --check --assert-expected --summary-json`
   compares that simple replay with the aggregate local-lemma scan
   family-by-family; use `--json` when the full family crosswalk records are
   needed. The follow-up crosswalk
   `python scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py --check --assert-expected --summary-json`
   connects the same local-lemma accounting back to the review-pending
   exhaustive count artifact and motif classification; use `--json` when the
   full family crosswalk records are needed. The relation-skeleton
   crosswalk
   `python scripts/check_relation_skeleton_local_lemma_crosswalk.py --check --assert-expected --summary-json`
   connects the compact 16-skeleton proof-mining catalog to the same
   aggregate/simple-replay family accounting. Use `--json` instead when the
   full family crosswalk records are needed.
   The relation-skeleton/closed-descent crosswalk
   `python scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py --check --assert-expected --summary-json`
   compares the same 16 relation skeletons with the closed-descent packet,
   checking the one-class self-edge and multi-class strict-cycle region split.
   The local-lemma audit-path checker
   `python scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --summary-json`
   runs the focused packet/catalog, focused mini-replay,
   aggregate/simple-replay, exhaustive/local-lemma, and
   relation-skeleton/local-lemma handoffs as one review-pending audit path,
   with the relation-skeleton/closed-descent companion summary and explicit
   adjacent handoff checks that identify where any future count/schema drift
   first appears. Use `--json` instead when the full layer and manifest
   records are needed.
   The compact review run-bundle checker
   `python scripts/check_n9_review_run_bundle.py --check --run --summary-json`
   executes the current compact n=9 manifest command surface and records
   digest-level provenance for one reviewer run. It is drift detection and
   execution evidence only, not independent mathematical review.
   The compact decision-intake checker
   `python scripts/check_n9_review_decision_intake.py --check --summary-json`
   validates the gate/outcome schema for external written-review records; use
   `--template` to print a fillable draft and `--decision <path>` to validate a
   supplied record. It does not accept gates or update source-of-truth status
   files by itself.
   The vertex-circle route decision preflight
   `python scripts/check_n9_vertex_circle_route_decision_preflight.py --check --summary-json`
   is now part of the compact harness. It checks that the internal A6/A7, A8,
   and A10 notes are present and that the route still requires written
   independent review before any source-of-truth proposal.
   The focused mini-replay commands
   `python scripts/check_n9_t01_self_edge_minireplay.py --check --assert-expected --json`,
   `python scripts/check_n9_t02_self_edge_minireplay.py --check --assert-expected --json`,
   `python scripts/check_n9_t03_self_edge_minireplay.py --check --assert-expected --json`,
   `python scripts/check_n9_t04_self_edge_minireplay.py --check --assert-expected --json`,
   `python scripts/check_n9_t05_self_edge_minireplay.py --check --assert-expected --json`,
   `python scripts/check_n9_t06_self_edge_minireplay.py --check --assert-expected --json`,
   `python scripts/check_n9_t07_self_edge_minireplay.py --check --assert-expected --json`,
   `python scripts/check_n9_t08_self_edge_minireplay.py --check --assert-expected --json`,
   `python scripts/check_n9_t09_self_edge_minireplay.py --check --assert-expected --json`,
   `python scripts/check_n9_t10_strict_cycle_minireplay.py --check --assert-expected --json`,
   `python scripts/check_n9_t11_strict_cycle_minireplay.py --check --assert-expected --json`,
   and
   `python scripts/check_n9_t12_strict_cycle_minireplay.py --check --assert-expected --json`
   replay the smallest currently extracted self-edge and strict-cycle packet
   inputs. The T10 paired-square entry audit
   `python scripts/check_n9_t10_paired_square_entry.py --check --assert-expected --json`
   remains a diagnostic companion, not a theorem.
   The turn-inequality indexing audit
   `python scripts/check_turn_inequality_indexing.py --check --assert-expected --summary-json`
   checks the n=9 weak-turn interval indexing convention against the term
   emitter before certificate replay; it does not prove the geometric lemma.
   The turn-inequality frontier replay
   `python scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --summary-json`
   checks stored integer dual certificates for all 184 regenerated
   pair/crossing/count frontier assignments under the candidate weak turn
   system; the geometric turn lemma and indexing remain review bottlenecks.
   Use `--json` instead when the full certificate rows are needed.
   The input-data audit
   `python scripts/check_n9_vertex_circle_input_audit.py --check --assert-expected --summary-json`
   now separately checks the stored row0 witness coverage and summary
   arithmetic for the exhaustive artifact without rerunning the brancher; use
   `--json` when the full expected-count block is needed.
   The branching replay
   `python scripts/check_n9_vertex_circle_mro_branching_replay.py --check --assert-expected --summary-json`
   now reruns the same filters with fixed center order and checks agreement
   with the dynamic minimum-remaining-options artifact; use `--json` when the
   full fixed-order replay sections are needed.
   The strict-edge geometry replay
   `python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --summary-json`
   independently checks the proper-interval strict-edge generator for all
   candidate selected rows; the 2026-06-09 internal A8 review note records the
   corresponding local geometry review without closing the formal gate. Use
   `--json` when the full mismatch example block is needed.
   The quotient-soundness replay
   `python scripts/check_n9_vertex_circle_quotient_soundness.py --check --assert-expected --summary-json`
   checks selected-distance quotient status agreement on the stored local-core
   and frontier rows; use `--json` when the full per-view status and mismatch
   example blocks are needed.
   The Kalmanson self-edge independent replay
   `python scripts/check_n9_kalmanson_selfedge_independent_replay.py --check --assert-expected --summary-json`
   treats the stored `n9_kalmanson_selfedge` certificate as input data and
   replays row shape, pair/crossing filters, witness-pair capacity,
   selected-distance quotienting, stored Kalmanson self-edges, and digest
   agreement without importing the Kalmanson generator module; use `--json`
   when the first stored self-edge example record is needed.
   The fresh-frontier replay
   `python scripts/check_n9_kalmanson_selfedge_frontier_replay.py --check --assert-expected --summary-json`
   regenerates the same 184 terminal selected-witness assignments without
   importing the repo package or reading the stored Kalmanson certificate, then
   finds one strict Kalmanson self-edge for each. Treat it as corroborating
   audit evidence only.
   The three-row compression replay
   `python scripts/check_n9_kalmanson_three_row_core_compression.py --check --assert-expected --summary-json`
   regenerates the same frontier and records that every terminal assignment
   has an optimally chosen row-minimal Kalmanson self-edge core using exactly
   three selected rows. Treat it as proof-mining compression evidence only,
   not as a bridge proof or a status promotion.
   The incidence-filter replay
   `python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --summary-json`
   checks the row-level two-overlap crossing, witness-pair cap, and
   selected-indegree cap tables; use `--json` when the full histogram blocks
   are needed.
   The branch-option audit
   `python scripts/check_n9_vertex_circle_branch_options.py --check --assert-expected --summary-json`
   checks fixed-order no-vertex-circle helper options and maintained count
   arrays against a direct predicate implementation; use `--json` when the
   full mismatch example block is needed.
   The dynamic-MRO choice audit
   `python scripts/check_n9_vertex_circle_dynamic_mro_choices.py --check --assert-expected --summary-json`
   checks the actual minimum-remaining-options center choice against direct
   all-center option counts and first-minimum tie breaking; use `--json` when
   the full depth and tie histograms are needed.
   The frontier-coverage crosswalk
   `python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check --assert-expected --summary-json`
   compares regenerated dynamic no-vertex complete assignments with the
   stored frontier classification artifact; use `--json` when the full
   mismatch example block is needed.
   The dihedral-orbit audit
   `python scripts/check_n9_vertex_circle_dihedral_orbit_audit.py --check --assert-expected --summary-json`
   independently checks the stored 16 motif representatives, their labelled
   dihedral orbits, and the assignment-to-orbit maps in the frontier
   classification artifact; use `--json` when the full mismatch example block
   is needed.
   The motif-obstruction audit
   `python scripts/check_n9_vertex_circle_motif_obstruction_audit.py --check --assert-expected --summary-json`
   checks the stored representative self-edge paths and strict-cycle records
   for those 16 motif families with a small local quotient replay; use
   `--json` when the full example error block is needed.
   The local-core subset audit
   `python scripts/check_n9_vertex_circle_local_core_subset_audit.py --check --assert-expected --summary-json`
   checks that the compact row-local certificates are exact subsets of their
   stored full motif representatives and already obstruct by direct quotient
   replay; use `--json` when the full example error block is needed.
   The frontier-assignment audit
   `python scripts/check_n9_vertex_circle_frontier_assignment_audit.py --check --assert-expected --summary-json`
   checks the stored 184 frontier assignments directly against row shape,
   row-pair crossing, witness-pair capacity, and selected-indegree capacity;
   use `--json` when the full example error block is needed.
   The partial-pruning replay
   `python scripts/check_n9_vertex_circle_partial_pruning.py --check --assert-expected --summary-json`
   checks all nonempty selected-row subsets of the stored 184 frontier
   assignments for monotone obstruction persistence and checker/replay status
   agreement only; use `--json` when the full mismatch example block is
   needed.
3. Continue the minimal fragile-cover bridge after the stored block-6
   vertex-circle full-extension audit
   `data/certificates/block6_fragile_vertex_circle_extension_audit.json`.
   Use `scripts/check_radius_blocker_vertex_circle_pilot.py --check --assert-expected --json`
   as the first exact-four row-option packet replay for radius-blocker shapes,
   then mine true multi-option blocker packets rather than only fixed selected
   rows. The first full packet widening is now
   `python scripts/check_n9_full_radius_blocker_vertex_circle_packet.py --check --assert-expected --json`,
   which checks the natural-order `n=9` blocker `{0,1,2,3}` over all exact
   four-row choices compatible with that blocker and records 90 incidence
   survivors, all vertex-circle obstructed. The next shape widening is now
   `python scripts/check_n9_radius_blocker_shape_sweep.py --check --assert-expected --json`,
   which checks all `10` cyclic-dihedral four-blocker shapes in the natural
   order and records `1,358` incidence survivors, all vertex-circle
   obstructed. The order-reduction crosswalk
   `python scripts/check_n9_radius_blocker_order_reduction_crosswalk.py --check --assert-expected --json`
   records that arbitrary cyclic-order placements of the same exact-four
   four-blocker packet relabel to that natural-order shape sweep. The bounded
   richer-class projection pilot
   `python scripts/check_n9_radius_blocker_rich_projection_pilot.py --check --assert-expected --json`
   expands one synthetic size-five class at each center to all exact
   four-subsets and leaves one vertex-circle-obstructed incidence survivor.
   The full r