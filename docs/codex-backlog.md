# Codex Backlog

Status: operational planning guidance only; not mathematical evidence.

Live open issues were rechecked through GitHub on 2026-05-17. The legacy
issues `#5`, `#81`, `#82`, and `#83` now have an explicit repository crosswalk
in `docs/open-issue-resolution-crosswalk.md`, checked by
`python scripts/check_open_issue_resolution_crosswalk.py --assert-expected --json`.
That crosswalk recommends closing those issues as scoped issue-resolution
bookkeeping only. This backlog is a Codex-facing companion to
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

1. Review the aggregate `n=9` vertex-circle local-lemma scan against the
   focused T01/T02/T03/T04/T05/T06/T07/T08/T09 self-edge packets and the focused T10/T11/T12
   strict-cycle packets, keeping it scoped as proof-mining scaffolding rather
   than an `n=9` proof. The focused packet catalog audit command
   `python scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py --check --assert-expected --json`
   now checks that the focused packet coverage, source template records,
   source catalog records, and aggregate focused-note crosschecks agree before
   packet soundness review. The focused mini-replay crosswalk
   `python scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py --check --assert-expected --json`
   joins those same 12 focused packets to their packet-specific mini-replay
   artifacts without promoting the layer to packet soundness or local-lemma
   completeness.
2. Use the stored simple replay artifact
   `data/certificates/n9_vertex_circle_local_lemma_simple_replay.json` as a
   reviewer-facing input for the aggregate local-template coverage. The replay
   checks the packet JSON without sharing the main quotient-replay helper, but
   it is still a packet audit rather than an `n=9` proof. The crosswalk command
   `python scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py --check --assert-expected --json`
   compares that simple replay with the aggregate local-lemma scan
   family-by-family. The follow-up crosswalk
   `python scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py --check --assert-expected --json`
   connects the same local-lemma accounting back to the review-pending
   exhaustive count artifact and motif classification. The relation-skeleton
   crosswalk
   `python scripts/check_relation_skeleton_local_lemma_crosswalk.py --check --assert-expected --json`
   connects the compact 16-skeleton proof-mining catalog to the same
   aggregate/simple-replay family accounting.
   The local-lemma audit-path checker
   `python scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --json`
   runs the focused packet/catalog, focused mini-replay,
   aggregate/simple-replay, exhaustive/local-lemma, and
   relation-skeleton/local-lemma handoffs as one review-pending audit path,
   with explicit adjacent handoff checks that identify where any future
   count/schema drift first appears.
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
   The turn-inequality frontier replay
   `python scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --json`
   checks stored integer dual certificates for all 184 regenerated
   pair/crossing/count frontier assignments under the candidate weak turn
   system; the geometric turn lemma and indexing remain review bottlenecks.
   The input-data audit
   `python scripts/check_n9_vertex_circle_input_audit.py --check --assert-expected --json`
   now separately checks the stored row0 witness coverage and summary
   arithmetic for the exhaustive artifact without rerunning the brancher.
   The branching replay
   `python scripts/check_n9_vertex_circle_mro_branching_replay.py --check --assert-expected --json`
   now reruns the same filters with fixed center order and checks agreement
   with the dynamic minimum-remaining-options artifact.
   The strict-edge geometry replay
   `python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --json`
   independently checks the proper-interval strict-edge generator for all
   candidate selected rows.
   The quotient-soundness replay
   `python scripts/check_n9_vertex_circle_quotient_soundness.py --check --assert-expected --json`
   checks selected-distance quotient status agreement on the stored local-core
   and frontier rows.
   The Kalmanson self-edge independent replay
   `python scripts/check_n9_kalmanson_selfedge_independent_replay.py --check --assert-expected --json`
   treats the stored `n9_kalmanson_selfedge` certificate as input data and
   replays row shape, pair/crossing filters, witness-pair capacity,
   selected-distance quotienting, stored Kalmanson self-edges, and digest
   agreement without importing the Kalmanson generator module.
   The incidence-filter replay
   `python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --json`
   checks the row-level two-overlap crossing, witness-pair cap, and
   selected-indegree cap tables.
   The branch-option audit
   `python scripts/check_n9_vertex_circle_branch_options.py --check --assert-expected --json`
   checks fixed-order no-vertex-circle helper options and maintained count
   arrays against a direct predicate implementation.
   The dynamic-MRO choice audit
   `python scripts/check_n9_vertex_circle_dynamic_mro_choices.py --check --assert-expected --json`
   checks the actual minimum-remaining-options center choice against direct
   all-center option counts and first-minimum tie breaking.
   The frontier-coverage crosswalk
   `python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check --assert-expected --json`
   compares regenerated dynamic no-vertex complete assignments with the
   stored frontier classification artifact.
   The dihedral-orbit audit
   `python scripts/check_n9_vertex_circle_dihedral_orbit_audit.py --check --assert-expected --json`
   independently checks the stored 16 motif representatives, their labelled
   dihedral orbits, and the assignment-to-orbit maps in the frontier
   classification artifact.
   The motif-obstruction audit
   `python scripts/check_n9_vertex_circle_motif_obstruction_audit.py --check --assert-expected --json`
   checks the stored representative self-edge paths and strict-cycle records
   for those 16 motif families with a small local quotient replay.
   The local-core subset audit
   `python scripts/check_n9_vertex_circle_local_core_subset_audit.py --check --assert-expected --json`
   checks that the compact row-local certificates are exact subsets of their
   stored full motif representatives and already obstruct by direct quotient
   replay.
   The frontier-assignment audit
   `python scripts/check_n9_vertex_circle_frontier_assignment_audit.py --check --assert-expected --json`
   checks the stored 184 frontier assignments directly against row shape,
   row-pair crossing, witness-pair capacity, and selected-indegree capacity.
   The partial-pruning replay
   `python scripts/check_n9_vertex_circle_partial_pruning.py --check --assert-expected --json`
   checks all nonempty selected-row subsets of the stored 184 frontier
   assignments for monotone obstruction persistence and checker/replay status
   agreement only.
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
   The full rich-class quotient pilot
   `python scripts/check_n9_radius_blocker_rich_quotient_pilot.py --check --assert-expected --json`
   checks the same synthetic size-five family without choosing four-subsets:
   it generates `225` strict edges and is blocked by `193` self-edge
   conflicts. The generated rich-class quotient sweep
   `python scripts/check_n9_radius_blocker_rich_quotient_sweep.py --check --assert-expected --json`
   repeats the full replay over `20` size-five packets derived from the stored
   self-edge and strict-cycle obstruction examples for all `10` four-blocker
   shapes; all `20` are quotient-obstructed by self-edges. This is still
   finite packet evidence only. The bounded rich-extension neighborhood
   `python scripts/check_n9_radius_blocker_rich_extension_neighborhood.py --check --assert-expected --json`
   varies the added labels by every Hamming-distance `1` or `2`
   radius-blocker-preserving replacement around those packets, checking
   `5,996` variants; all are quotient-obstructed by self-edges. This is still
   finite neighborhood evidence only. The one-packet full rich-extension
   product pilot
   `python scripts/check_n9_radius_blocker_rich_extension_product_pilot.py --check --assert-expected --json`
   exhausts the first maximum-size generated packet, checking `196,608`
   variants; all are quotient-obstructed by self-edges. This is still finite
   packet evidence only. The all-packet generated product sweep
   `python scripts/check_n9_radius_blocker_rich_extension_product_sweep.py --check --assert-expected --json`
   exhausts the full Cartesian product over all `20` generated source packets,
   checking `2,899,968` variants; all are quotient-obstructed by self-edges.
   This is still finite generated-packet evidence only. The next widening
   should be a principled rich-class bridge hypothesis or a
   generator-independent catalogue rather than more product replay over the
   same generated packet family.
   The generator-independent all-five-rich support obstruction
   `python scripts/check_n9_all_five_rich_support_obstruction.py --check --assert-expected --json`
   now closes the full `56^9` size-five support assignment space under only
   the two-circle row-pair cap and radical-axis crossing filters. This rules
   out the all-centers-size-at-least-five support subcase repo-locally. The
   localized rich-support counting lemma
   `python scripts/check_localized_rich_support_counting.py --check --json`
   now gives a proof-facing shortcut for the nonagon support layer itself:
   any hypothetical 4-bad nonagon is forced into the all-exact-four,
   selected-indegree-four support frontier by counting alone.
   The mixed rich-support reduction
   `python scripts/check_n9_mixed_rich_support_reduction.py --check --assert-expected --json`
   remains as catalogue provenance for that reduction: it runs the four/five
   support catalogue with witness-pair capacity and leaves exactly the `184`
   all-exact-four assignments. The mixed/frontier crosswalk
   `python scripts/check_n9_mixed_rich_frontier_crosswalk.py --check --assert-expected --json`
   checks that those `184` terminal assignments are exactly the stored
   pre-vertex-circle frontier as a labelled row set. The next useful PR is
   therefore no longer another size-five catalogue or landing crosswalk; it
   should audit the exact-four vertex-circle frontier itself or replace pieces
   of that review-pending pipeline with reusable local lemmas.
   The stored crossing-order sample
   `data/certificates/block6_terminal_crossing_vertex_circle_sample.json`
   now checks two deterministic terminal-extension windows across all of
   their crossing-compatible cyclic orders, with all `796` sampled orders
   killed by a vertex-circle self-edge. The full crossing-order sweep
   `data/certificates/block6_terminal_crossing_vertex_circle_full_sweep.json`
   now exhausts the `105,978` terminal full extensions generated by the
   natural-order two-block audit across all `385,517` crossing-compatible
   cyclic orders they admit. The current geometric gate still does not cover
   row systems outside that natural-order terminal generator, so the next
   useful widening is a generator-independent all-order closure or a
   minimal/rich-class hypothesis that avoids fixing one selected row at each
   center too early. The fixed-order probe
   `data/certificates/block6_fixed_order_vertex_circle_probe.json` confirms
   this gap is concrete: three non-natural orders have terminal extensions
   outside the natural-order generator, although all four probed fixed orders
   still close under order-specific vertex-circle pruning. The block-preserving
   shuffle-order sweep
   `data/certificates/block6_shuffle_order_vertex_circle_sweep.json` widens
   that check to all `462` normalized shuffles preserving internal order within
   each six-label block; every such fixed-order search closes, while the
   remaining gap is still arbitrary cyclic orders and a genuine
   minimal/rich-class bridge. The reversed-second-block companion sweep
   `data/certificates/block6_reversed_block_shuffle_vertex_circle_escape.json`
   now records the first boundary case for this gate: `16` oriented-block
   fixed orders have vertex-circle-clean full selected-row extensions. The
   follow-up `data/certificates/block6_reversed_block_clean_kalmanson.json`
   closes those 16 stored fixed assignment/order pairs by exact Kalmanson
   quotient-cone certificates, and
   `data/certificates/block6_reversed_block_two_stage_closure.json` records the
   combined `446 + 16 = 462` closure crosswalk. The follow-up
   `data/certificates/block6_forward_block_two_orientation_closure.json` joins
   that packet to the forward-second-block sweep, checking `924` normalized
   first-block-forward shuffle orders. The oriented-block reversal crosswalk
   `data/certificates/block6_oriented_block_reversal_closure.json` then uses
   explicit cyclic reversal to cover the two first-block-reversed orientation
   families as well, for `1848` oriented-block shuffle orders. The next useful
   PR should widen beyond block-preserving shuffles, or explain which richer
   bridge hypothesis would rule out the remaining arbitrary-order gap. The
   row-depth scout
   `python scripts/check_block6_fragile_sixth_row_survivors.py --assert-expected --json`
   records a bounded negative control against fifth-row-only and
   sixth-row-only closure claims before attempting such a bridge.
4. Use the bootstrap-core crosswalk and the bootstrap / vertex-circle overlay
   in `docs/bootstrap-core-crosswalk.md` and
   `docs/bootstrap-vertex-circle-overlay.md` to design a sharper condition.
   The current singleton-rich stuck/frontier motifs all survive the weighted
   ledger, while the two tight `n=9` non-ear rows both land on the `T12/F16`
   strict-cycle template without yielding a bootstrap-core-only contradiction.
   The follow-up `docs/bootstrap-t12-forcing-targets.md` refines this into a
   row-center forcing target: source `81` has no direct private-pair hit, and
   source `151` has only partial direct private-pair hits.
   The row-pressure refinement in `docs/bootstrap-t12-row-pressure.md` splits
   the missing rows into deletion-closure-exposed, one-outside-label, and
   outside-pair cases for the next bridge attempt. The closure-exposed
   subpacket in `docs/bootstrap-t12-closure-exposed.md` isolates the two
   activation-ready deletion-closure rows as the smallest next lemma target.
   The one-outside-label subpacket in `docs/bootstrap-t12-one-outside.md`
   isolates the three singleton-support rows where a future bridge would need
   to force one outside label without relying on private-pair capacity.
   The outside-pair subpacket in `docs/bootstrap-t12-outside-pair.md` isolates
   the remaining pair-supported row, where private-pair capacity makes partial
   direct contact but still does not force the missing equality connector.
   The activation-support requirement ledger in
   `docs/bootstrap-t12-activation-requirements.md` separates the stored T12
   connector-pair and strict-edge endpoint requirements from the still-unproved
   row-forcing step, with source `151` row `7` as the main closure-exposure
   negative control.
   The bridge-target map in `docs/bootstrap-t12-bridge-target-map.md` joins the
   row-pressure, support, and activation ledgers into six explicit next-lemma
   targets: hard strict endpoint rows `151:7` and `151:8`, open connector-pair
   row `151:5`, and three relation-sufficient rows that still need row-forcing
   arguments.
   The hard strict-endpoint subpacket in
   `docs/bootstrap-t12-hard-strict-endpoints.md` isolates rows `151:7` and
   `151:8`, where strict-edge endpoint sets are still incomplete after closure
   and singleton-support checks.
   The open connector-pair subpacket in
   `docs/bootstrap-t12-open-connector-pair.md` isolates row `151:5`, where the
   connector pair `[7,8]` is still split across singleton support and partial
   closure evidence.
   The relation-sufficient row subpacket in
   `docs/bootstrap-t12-relation-sufficient-rows.md` isolates rows `81:3`,
   `81:8`, and `151:6`, where connector relation evidence is already present
   but row/rich-class forcing remains open.
   The focused `81:3` closure-target packet in
   `docs/bootstrap-t12-81-3-closure-target.md` is the first target in this
   loop: full-row closure exposure and relation sufficiency meet there, and
   the row supplies the final `T12/F16` connector only if a future bridge
   proves genuine row/rich-class forcing.
   The follow-up `81:3` rich-triple connector contract in
   `docs/bootstrap-t12-81-3-rich-triple-contract.md` reduces the next target:
   the stored T12 connector only needs witnesses `0` and `1` in one genuine
   rich class at center `3`.
   The order-resolved fixed-row escape audit in
   `docs/bootstrap-t12-81-3-order-escape.md` shows the current singleton-rich
   closure does not expose label `6` first: center `3` is the only initial
   activation from `[0,1,4]`, and label `6` is added later by trigger
   `[0,3,4]`. It now also records the same-center disjointness guard: if the
   source-`81` center-`6` fixed row `[0,3,4,7]` is preserved as a genuine
   class, no additional center-`6` class can contain the seed triple
   `[0,1,4]`. The next useful PR should leave fixed selected-row preservation
   and attack the genuine rich-class question directly: either exhibit a
   pre-`3` rich-class supply of label `6` that avoids the connector without
   preserving that center-`6` row, or prove no such supply can satisfy the
   minimal/rich-class hypotheses.
   The relaxed escape-candidate scan in
   `docs/bootstrap-t12-81-3-escape-candidates.md` now drops preservation of
   the source-`81` center-`3` and center-`6` rows while preserving the other
   seven rows. All `40` one-class replacement candidates fail the basic
   incidence/crossing filters.
   The one-row-drop follow-up in
   `docs/bootstrap-t12-81-3-escape-one-row-drop.md` then allows any one of
   those seven preserved rows to move as an arbitrary 4-set. All `19600`
   candidates still fail the basic row-pair, witness-pair, or crossing
   filters.
   The two-row-drop scan in
   `docs/bootstrap-t12-81-3-escape-two-row-drop.md` allows any pair of those
   seven rows to move. All `4116000` candidates still fail the same basic
   filters.
   The full-neighborhood CSP in
   `docs/bootstrap-t12-81-3-escape-full-neighborhood.md` now lets all seven of
   those rows move simultaneously and proves no complete basic-filter
   assignment exists in the implicit `329417200000000`-assignment space. The
   auxiliary-rich-class CSP in
   `docs/bootstrap-t12-81-3-escape-auxiliary-csp.md` then lets the center-`3`
   connector and center-`6` supply classes exist as auxiliary rich classes
   while selected rows at those centers are free to be equal or disjoint. It
   also has no basic-filter survivor. The trigger-family uniqueness audit in
   `docs/bootstrap-t12-81-3-trigger-uniqueness.md` checks that richer
   catalogues cannot contain two classes from the specified center-`6` supply
   family or two classes from the specified center-`3` connector-avoiding
   family, because the classes pairwise intersect at the same center. The
   rich-support CSP in
   `docs/bootstrap-t12-81-3-escape-rich-support-csp.md` then lets those
   auxiliary objects be supports larger than four labels and still finds no
   complete basic-filter assignment. The first-supply-chain prefix CSP in
   `docs/bootstrap-t12-81-3-first-supply-chains.md` adds those other-center
   auxiliary first steps: among `4650` first-step/support-prefix pairs it finds
   exactly three basic-filter survivor prefixes, all starting at center `8`,
   and none of those admits an immediate center-`6` label-`6` supply support.
   The second-supply-chain prefix crosswalk in
   `docs/bootstrap-t12-81-3-second-supply-chains.md` then allows one further
   non-target, non-supply activation from closure `[0,1,4,8]`; it leaves one
   center-`8` then center-`2` prefix, with support `[1,3,4,8]`, and no
   immediate center-`6` label-`6` supply extension for that prefix.
   The second-step-chain CSP in
   `docs/bootstrap-t12-81-3-second-step-chains.md` attacks the bounded
   distinct-intermediate continuation: after those center-`8` prefixes, no
   chain through distinct centers from `{2,5,7}` followed by one center-`6`
   label-`6` supply support survives the same basic filters. The post-`8`
   supply-chain accounting companion in
   `docs/bootstrap-t12-81-3-post8-supply-chains.md` records the raw
   denominator behind the same closure: `3,918,164,268` support catalogues
   reduce to `58` initially compatible catalogues and no selected-row
   survivor. The ordered chain-closure CSP in
   `docs/bootstrap-t12-81-3-chain-closure-csp.md` then checks `5916`
   sequential support-chain extensions from closure `[0,1,4]`; it leaves four
   non-supply prefixes and no surviving prefix whose next activated center is
   `6`. The next useful PR must therefore either handle repeated/multiple
   supports, introduce a genuine rich-class/minimality hypothesis that forces
   or excludes such a support, or move to a different bridge target. The
   source-`81` row-`8` singleton-support audit in
   `docs/bootstrap-t12-81-8-singleton-support-audit.md` is one such adjacent
   target: it finds no non-original row-`8` activation survivor in the fixed
   source-`81` neighborhood or a one-row-drop relaxation, but still leaves
   genuine singleton-support existence and row forcing open. The
   source-`151` row-`6` outside-pair audit in
   `docs/bootstrap-t12-151-6-outside-pair-audit.md` does the analogous check
   for the remaining relation-sufficient row target: no non-original row-`6`
   activation survivor appears in the fixed source-`151` neighborhood or a
   one-row-drop relaxation, but genuine outside-pair support existence and row
   forcing remain open. The source-`151` singleton-support audit in
   `docs/bootstrap-t12-151-singleton-support-audit.md` applies the same local
   audit shape to rows `151:5` and `151:8`; it also leaves the genuine
   support-existence and row-forcing bridge questions open.
5. Extend the Kalmanson template diagnostics toward order-search coverage:
   C13/C19 template records and C25/C29 availability records now exist, but
   they are not cyclic-order coverage or obstructions for the larger frontier.
   The C19 order-CNF export
   `python scripts/export_c19_kalmanson_order_cnf.py --assert-expected --check-artifact reports/c19_kalmanson_order_cnf_summary.json`
   gives a standard SAT target for the stored Z3 clauses, but the external
   DRAT/LRAT or equivalent UNSAT replay is still open. The same script can
   round-trip an external CNF file with `--write-cnf` and `--check-cnf`.
   The local proof-tooling environment probe
   `python scripts/probe_c19_proof_tooling.py --json` records whether a
   supported SAT solver/checker pair is available. With
   `--check-c19-cnf-summary`, it also checks the stored C19 order-CNF summary
   against the deterministic exporter, but this is environment/preflight
   bookkeeping only and not proof evidence.
6. Audit `n=8` class `14` or the review-pending `n=9` vertex-circle checker
   with an independent input-data replay. The current SymPy-free
   `n=8` replay command,
   `python scripts/independent_n8_obstruction_recheck.py --check --json`,
   covers the cyclic-order counts and 11 non-Groebner survivor-class kills;
   the focused class `14` replay command,
   `python scripts/check_n8_class14_certificate.py --check --json`, now
   isolates the PB+ED Groebner/strict-interior certificate for that class.
   The residual replay command,
   `python scripts/check_n8_residual_certificates.py --check --json`,
   isolates the class `3`, `4`, and `5` duplicate, collinearity, and
   Groebner-y2 certificates. The remaining `n=8` audit gap is now external
   review of these focused checkers and the underlying artifact assumptions.
   The first `n=9` input-data replay command,
   `python scripts/check_n9_vertex_circle_input_audit.py --check --assert-expected --json`,
   covers row0 choices and summary arithmetic only; the brancher, pruning
   lemmas, and vertex-circle certificates still need review.
   The MRO branching replay command,
   `python scripts/check_n9_vertex_circle_mro_branching_replay.py --check --assert-expected --json`,
   covers the branch-order checklist item only; the pruning lemmas and
   vertex-circle certificates still need separate review.
   The strict-edge geometry command,
   `python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --json`,
   covers the local vertex-circle strict-edge generator only; quotient
   soundness and exhaustive coverage still need separate review.
   The quotient-soundness command,
   `python scripts/check_n9_vertex_circle_quotient_soundness.py --check --assert-expected --json`,
   covers selected-distance quotient status agreement on stored local-core and
   frontier rows only; branch coverage and strict-edge geometry remain separate
   review scopes.
   The incidence-filter command,
   `python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --json`,
   covers only row-level two-overlap crossing, witness-pair capacity, and
   selected-indegree capacity; brancher replay and vertex-circle pruning remain
   separate review scopes.
   The branch-option command,
   `python scripts/check_n9_vertex_circle_branch_options.py --check --assert-expected --json`,
   covers only fixed-order no-vertex-circle helper-option agreement and
   maintained count arrays; dynamic-MRO coverage and vertex-circle pruning
   remain separate review scopes.
   The dynamic-MRO choice command,
   `python scripts/check_n9_vertex_circle_dynamic_mro_choices.py --check --assert-expected --json`,
   covers only the actual dynamic center-choice implementation and all-center
   option-count agreement; filter soundness, vertex-circle geometry, and
   quotient soundness remain separate review scopes.
   The frontier-coverage crosswalk command,
   `python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check --assert-expected --json`,
   covers only generated-vs-stored frontier row agreement for the current
   dynamic brancher; filter soundness, vertex-circle geometry, and quotient
   soundness remain separate review scopes.
   The dihedral-orbit audit command,
   `python scripts/check_n9_vertex_circle_dihedral_orbit_audit.py --check --assert-expected --json`,
   covers only stored motif-family orbit bookkeeping and assignment-to-orbit
   agreement; frontier coverage, filter soundness, vertex-circle geometry, and
   quotient soundness remain separate review scopes.
   The motif-obstruction audit command,
   `python scripts/check_n9_vertex_circle_motif_obstruction_audit.py --check --assert-expected --json`,
   covers only stored representative obstruction records for the 16 motif
   families; frontier coverage, brancher soundness, incidence-filter
   soundness, dihedral orbit bookkeeping, and full n=9 review remain separate
   scopes.
   The frontier-comparison command,
   `python scripts/compare_n9_vertex_circle_frontier.py --check --assert-expected --json`,
   covers only the stored P18/C19 comparison against current local-core and
   vertex-circle helpers; exact-core non-embedding, P18 strict-cycle behavior,
   and C19 fixed-order pass behavior remain guardrails, not a proof of `n=9`,
   counterexample, or transfer theorem.
   The local-core subset audit command,
   `python scripts/check_n9_vertex_circle_local_core_subset_audit.py --check --assert-expected --json`,
   covers only the compact-core-to-full-representative subset relation and
   compact-core obstruction replay; local-lemma completeness, frontier
   coverage, brancher soundness, and full n=9 review remain separate scopes.
   The frontier-assignment command,
   `python scripts/check_n9_vertex_circle_frontier_assignment_audit.py --check --assert-expected --json`,
   covers only the stored 184 frontier rows under those base predicates;
   brancher coverage, strict-edge geometry, quotient soundness, and pruning
   remain separate review scopes.

## Task CB-N9-T01 - Extract Vertex-Circle Self-Edge Template

Issue: none yet.

Read first:

- `docs/codex-strategy-instructions.md`
- `docs/n9-vertex-circle-template-lemma-catalog.md`
- `docs/n9-vertex-circle-t01-self-edge-lemma.md`
- `data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json`
- `docs/n9-vertex-circle-exhaustive.md`

Commands:

```bash
python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
```

Expected artifacts:

- a proof-facing lemma note or update that states the exact incidence and
  cyclic-order hypotheses for the T01/F09 self-edge template;
- a minimal checker or checker update that verifies the compact template
  packet independently of the full exhaustive search;
- documentation that distinguishes the local template from any `n=9`
  completeness or global Erdos #97 claim.

Acceptance criteria:

- The lemma candidate does not enumerate all `n=9` selected-witness systems.
- The proof-facing text identifies the selected-distance quotienting and
  vertex-circle monotonicity used to force a self-edge.
- The checker treats the packet as input data and reports explicit uncertainty
  rather than silently accepting unsupported fields.
- The result remains review-pending unless independently reviewed.

Trust delta: may produce a reusable local obstruction template. It may not
promote the full `n=9` selected-witness result or alter global status.

Forbidden overclaiming text:

- "n=9 is proved"
- "the vertex-circle checker is independently reviewed"
- "this proves Erdos #97"

## Task CB-N9-T10 - Extract Vertex-Circle Strict-Cycle Template

Issue: none yet.

Read first:

- `docs/codex-strategy-instructions.md`
- `docs/n9-vertex-circle-template-lemma-catalog.md`
- `docs/n9-vertex-circle-t10-strict-cycle-lemma.md`
- `data/certificates/n9_vertex_circle_t10_strict_cycle_lemma_packet.json`
- `docs/n9-vertex-circle-exhaustive.md`

Commands:

```bash
python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_strict_cycle_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
```

Expected artifacts:

- a proof-facing lemma note or update that states the exact incidence and
  cyclic-order hypotheses for the T10/F12 strict-cycle template;
- a compact verifier that replays the quotient strict-cycle certificate from
  stored data;
- documentation that keeps local-core strict-cycle counts separate from
  full-assignment obstruction-shape counts.

Acceptance criteria:

- The lemma candidate states the directed quotient cycle and the exact local
  hypotheses that force it.
- The verifier is independent of the full exhaustive brancher.
- The result is scoped as a reusable obstruction template, not an `n=9`
  completeness proof.

Trust delta: may produce a reusable local strict-cycle obstruction template. It
may not promote the full `n=9` selected-witness result or alter global status.

Forbidden overclaiming text:

- "all strict cycles are classified" without the review-pending qualifier
- "n=9 is proved"
- "this proves Erdos #97"

## Task CB-FRAGILE-GEO - Add One Geometric Fragile-Cover Condition

Issue: none yet.

Read first:

- `docs/codex-strategy-instructions.md`
- `docs/minimal-fragile-cover-bridge.md`
- `src/erdos97/fragile_hypergraph.py`
- `scripts/check_fragile_hypergraph.py`
- `docs/stuck-set-miner.md`
- `docs/bootstrap-core-bridge.md`
- `src/erdos97/bootstrap_cores.py`

Commands:

```bash
python scripts/check_fragile_hypergraph.py --json
python scripts/check_fragile_hypergraph.py --blocks 2 --assert-ok --json
python scripts/check_bootstrap_core_bridge.py --assert-expected
python -m pytest tests/test_fragile_hypergraph.py -q
```

Expected artifacts:

- one documented geometric necessary condition for minimal counterexamples;
- checker support that can be run against the block-6 family, two disjoint
  block-6 families, and any current full-row extension survivors;
- a short report explaining which abstract family is newly rejected and why the
  condition is geometric rather than an arbitrary SAT filter.

Acceptance criteria:

- The condition is proved necessary for a minimal geometric counterexample.
- It rejects at least one abstract fragile-cover family that currently passes
  the pairwise/crossing checks.
- It remains labeled as a partial bridge unless it proves more.

Trust delta: may strengthen the minimal-counterexample bridge. It may not prove
Erdos #97 unless paired with a complete reduction and exact obstruction.

Forbidden overclaiming text:

- "fragile covers prove the theorem"
- "block-6 is impossible geometrically" without the stated new hypothesis
- "minimal counterexamples are ruled out"

## Task CB-83 - Decompose C19 Kalmanson Certificate

Issue: <https://github.com/davidiach/erdos97/issues/83>

Read first:

- `docs/round2/round2_merged_report.md`
- `docs/round2/kalmanson_distance_filter.md`
- `docs/kalmanson-two-order-search.md`
- `docs/kalmanson-certificate-diagnostics.md`
- `reports/c19_kalmanson_diagnostics.json`
- `data/certificates/round2/c19_kalmanson_known_order_unsat.json`
- `data/certificates/round2/c19_kalmanson_known_order_two_unsat.json`
- `data/certificates/c19_skew_all_orders_kalmanson_z3.json`

Commands:

```bash
python scripts/check_round2_certificates.py
python scripts/check_kalmanson_certificate.py data/certificates/round2/c19_kalmanson_known_order_two_unsat.json --summary-json
python scripts/check_kalmanson_two_order_z3.py --certificate data/certificates/c19_skew_all_orders_kalmanson_z3.json --assert-unsat
python scripts/analyze_kalmanson_certificates.py
python scripts/analyze_kalmanson_inverse_pair_templates.py --assert-expected --json
python scripts/analyze_kalmanson_sparse_frontier_templates.py --assert-expected --json
python scripts/export_c19_kalmanson_order_cnf.py --assert-expected --check-artifact reports/c19_kalmanson_order_cnf_summary.json
python scripts/probe_c19_proof_tooling.py --json
python scripts/probe_c19_proof_tooling.py --check-c19-cnf-summary --json
```

Expected artifacts:

- a reproducible diagnostic script or update to an existing report generator;
- a checked JSON or Markdown report summarizing support groups, smaller
  dependencies, or negative results.
- optional all-order Z3 clause-template diagnostics such as
  `reports/c19_kalmanson_z3_clause_diagnostics.json`, kept separate from the
  underlying SMT replay certificate.
- optional C13/C19 coefficient-template diagnostics such as
  `scripts/analyze_kalmanson_inverse_pair_templates.py`, kept separate from
  any transfer claim to other selected-witness patterns.
- optional C25/C29 sparse-frontier template-availability diagnostics such as
  `scripts/analyze_kalmanson_sparse_frontier_templates.py`, kept separate from
  cyclic-order coverage or all-order obstruction claims.
- optional order-CNF export diagnostics such as
  `reports/c19_kalmanson_order_cnf_summary.json`, kept separate from any
  solver-independent UNSAT proof claim until a DRAT/LRAT or equivalent proof
  artifact is checked.
- optional local proof-tooling environment probes such as
  `scripts/probe_c19_proof_tooling.py`, kept separate from mathematical
  evidence and from any solver-independent proof claim.

Acceptance criteria:

- The compact fixed-order two-inequality certificate, the earlier
  94-inequality certificate, and the all-order Z3 refinement certificate all
  remain valid.
- Any structural decomposition is reproducible without notebooks.
- Documentation keeps the fixed-order certificate, the all-order fixed-pattern
  obstruction, and the global Erdos #97 status separate.

Trust delta: may improve C19 certificate understanding. The all-order
fixed-pattern obstruction is already exact if the stored Z3 certificate
replays, but this may not promote any `n >= 9` finite case or Erdos
Problem #97.

Forbidden overclaiming text:

- "C19_skew proves Erdos #97"
- "all C19-like patterns are impossible"
- "this closes the frontier"

## Task CB-82 - Attack n=9 Base-Apex Low-Excess Ledgers

Issue: <https://github.com/davidiach/erdos97/issues/82>

Read first:

- `docs/n9-base-apex-frontier.md`
- `src/erdos97/n9_base_apex.py`
- `scripts/explore_n9_base_apex.py`
- `data/certificates/n9_vertex_circle_exhaustive.json`
- `docs/n9-vertex-circle-exhaustive.md`

Commands:

```bash
python scripts/explore_n9_base_apex.py
python scripts/check_n9_base_apex_low_excess_ledgers.py --check --json
python scripts/check_n9_base_apex_escape_budget.py --check --json
python scripts/check_n9_selected_baseline_d3_escape_class_crosswalk.py --check --json
python scripts/check_n9_selected_baseline_d3_vertex_circle_template_join.py --check --json
python scripts/check_n9_base_apex_d3_escape_frontier_packet.py --check --json
python scripts/check_n9_base_apex_low_excess_escape_crosswalk.py --check --json
python scripts/check_n9_base_apex_d3_p19_incidence_capacity_pilot.py --check --json
python scripts/check_n9_base_apex_d3_incidence_capacity_packet.py --check --json
python scripts/check_n9_base_apex_d3_artifact_join.py --check --json
python scripts/check_n9_base_apex_audit_path.py --check --json
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
```

Expected artifacts:

- `data/certificates/n9_base_apex_low_excess_ledgers.json`, or an updated
  successor JSON/Markdown report listing which low-excess ledgers remain;
- optional successor diagnostics such as
  `data/certificates/n9_base_apex_escape_budget_report.json` that keep escape
  placement counts separate from geometric realizability;
- optional selected-baseline overlays such as
  `data/certificates/n9_selected_baseline_escape_budget_overlay.json` that
  compare the escape-budget motif map with the 184 pre-vertex-circle
  selected-witness assignments without treating selected-baseline empty slots
  as actual geometric capacity deficits;
- optional selected-baseline D=3 escape-class crosswalks such as
  `data/certificates/n9_selected_baseline_d3_escape_class_crosswalk.json`
  that count assignment/slot-choice landings by selected-baseline class and
  escape class without treating those landings as realizability counts or as
  comparable to common-dihedral profile/escape classes;
- optional selected-baseline D=3 vertex-circle template joins such as
  `data/certificates/n9_selected_baseline_d3_vertex_circle_template_join.json`
  that join assignment/slot-choice landings to vertex-circle template/family
  diagnostics by assignment id without treating templates as theorem names or
  landings as realizability counts;
- optional sharp low-excess slices such as
  `data/certificates/n9_base_apex_d3_escape_slice.json` that couple the
  `E=6, D=3, r=3` profile/escape bookkeeping under common dihedral symmetry
  without claiming the slice is impossible or realizable;
- optional D=3 representative packets such as
  `data/certificates/n9_base_apex_d3_escape_frontier_packet.json` that expose
  compact profile-multiset by escape-class targets without certifying
  realizability or impossibility;
- optional P19 incidence-capacity pilots such as
  `data/certificates/n9_base_apex_d3_p19_incidence_capacity_pilot.json` that
  record the first D=3 packet band as capacity bookkeeping only, with
  realizability and incidence states left `UNKNOWN`;
- optional all-row D=3 incidence-capacity packets such as
  `data/certificates/n9_base_apex_d3_incidence_capacity_packet.json` that
  extend the same bookkeeping to all 88 D=3 packet rows while keeping
  realizability and incidence states `UNKNOWN`;
- optional finite profile-capacity obstructions such as
  `scripts/check_n9_base_apex_d3_p19_degree_obstruction.py` and
  `scripts/check_n9_base_apex_d3_p20_residue_obstruction.py` that close only
  the P19 and P20 slices, respectively, without claiming proof,
  counterexample, incidence-completeness, geometric realizability, or global
  status movement;
- optional cross-artifact D=3 consistency checkers such as
  `scripts/check_n9_base_apex_d3_artifact_join.py` that join the D=3 slice,
  representative packet, low-excess crosswalk, P19 pilot, and all-row
  incidence-capacity packet without claiming proof, counterexample,
  incidence-completeness, geometric realizability, or global status movement;
- optional reviewer-facing audit-path checkers such as
  `scripts/check_n9_base_apex_audit_path.py` that join the low-excess ledger,
  escape budget, low-excess ladder, D=3 artifact stack, selected-baseline D=3
  crosswalk, and review-pending vertex-circle frontier without claiming proof,
  counterexample, incidence-completeness, geometric realizability, or global
  status movement. Its JSON summary exposes named `handoff_checks` for
  adjacent-layer drift localization only;
- optional low-excess profile/escape crosswalks such as
  `data/certificates/n9_base_apex_low_excess_escape_crosswalk.json` that keep
  ledger-to-escape bookkeeping separate from proof, counterexample, and
  geometric-realizability claims;
- checker updates that independently replay generated ledger arithmetic and
  motif counts from stored JSON.

Acceptance criteria:

- Remaining `E <= 6` / `D >= 3` or related low-excess cases are enumerated
  explicitly.
- Any new obstruction states exact incidence/order hypotheses.
- Any n=9 promotion remains review-pending and cannot update the
  source-of-truth or global status without a broader review decision.

Trust delta: may promote a conditional ledger obstruction or a review-pending
n=9 subcase. It may not promote the full n=9 selected-witness case without a
complete checked pipeline and independent review path.

Forbidden overclaiming text:

- "n=9 is proved"
- "the vertex-circle checker is independently reviewed"
- "this updates the official Erdos #97 status"

## Task CB-N10 - Audit n=10 Singleton Slices

Issue: none yet.

Read first:

- `docs/n10-vertex-circle-singleton-slices.md`
- `src/erdos97/generic_vertex_search.py`
- `src/erdos97/n10_vertex_circle_singletons.py`
- `scripts/check_n10_vertex_circle_singletons.py`
- `data/certificates/n10_vertex_circle_singleton_slices.json`

Commands:

```bash
python scripts/check_n10_singleton_input_audit.py --check --assert-expected --json
python scripts/check_n10_vertex_circle_singletons.py --assert-expected --spot-check-row0 0 --spot-check-row0 63 --spot-check-row0 125
python -m pytest tests/test_n10_vertex_circle_singletons.py -q -m "artifact"
```

Expected artifacts:

- independent review notes for the generic checker and the imported singleton rows;
- an input-data audit checking the stored `[0,126)` row0 singleton coverage,
  witness masks/lists, and aggregate arithmetic without rerunning the search;
- selected repo-native spot checks for row0 singletons `0`, `63`, and `125`;
- optional second-implementation counts or a replayable terminal-conflict certificate.

Acceptance criteria:

- Row0 singleton coverage is exactly `[0,126)` with no hidden symmetry quotient.
- Partial vertex-circle pruning is verified to use only fixed rows/equalities.
- A second implementation or certificate replay checks all 126 slices.
- The result remains scoped as a draft review-pending n=10 finite-case artifact.

Trust delta: may promote the n=10 package from draft to review-pending finite
case artifact. It may not update the official/global status or the repo
source-of-truth strongest result by itself.

Forbidden overclaiming text:

- "n=10 is proved"
- "no bad decagon exists" without the review qualifier
- "this updates the official Erdos #97 status"

## Task CB-81 - Pilot Kalmanson Cyclic-Order CSP On C13

Issue: <https://github.com/davidiach/erdos97/issues/81>

Read first:

- `docs/kalmanson-two-order-search.md`
- `docs/c13-kalmanson-order-pilot.md`
- `docs/c13-kalmanson-prefix-branch-pilot.md`
- `scripts/check_kalmanson_two_order_search.py`
- `data/certificates/c13_sidon_all_orders_kalmanson_two_search.json`

Commands:

```bash
python scripts/check_kalmanson_certificate.py data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json --summary-json
python scripts/check_kalmanson_two_order_search.py --name C13_sidon_1_2_4_10 --n 13 --offsets 1,2,4,10 --assert-obstructed --assert-c13-expected --json
```

Expected artifacts:

- deterministic branch/pruning counts;
- exact certificates for closed branches when new branches are added;
- documentation separating fixed-order, all-order-for-one-pattern, and
  heuristic diagnostics.

Acceptance criteria:

- Rotation fixing is justified only by circulant translation symmetry.
- The all-order statement remains scoped to the fixed abstract
  `C13_sidon_1_2_4_10` selected-witness pattern.
- The C13 pilot is used only as a benchmark for larger sparse frontiers.

Trust delta: may improve or reproduce
`EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN` for C13. It may not prove
anything about abstract `C19_skew` or Erdos Problem #97.

Forbidden overclaiming text:

- "C13 proves the method works for C19"
- "Kalmanson closes the sparse frontier"
- "this is evidence of a general proof"

## Task CB-5 - Add Interval-Arithmetic Verifier

Issue: <https://github.com/davidiach/erdos97/issues/5>

Read first:

- `scripts/verify_candidate.py`
- `src/erdos97/search.py`
- `data/runs/best_B12_slsqp_m1e-6.json`
- `certificates/best_B12_certificate_template.json`
- `docs/exactification-plan.md`
- `docs/verification-contract.md`

Commands:

```bash
erdos97-search --verify data/runs/best_B12_slsqp_m1e-6.json --tol 1e-6
python scripts/verify_candidate.py data/runs/best_B12_slsqp_m1e-6.json
python -m pytest tests/test_search_hygiene.py -q
```

Expected artifacts:

- `src/erdos97/interval_verify.py` or an equivalent module;
- `scripts/interval_verify_candidate.py` or an equivalent CLI;
- tests that reject the saved B12 near-miss as a counterexample.

Current entrypoint:

```bash
python scripts/interval_verify_candidate.py data/runs/best_B12_slsqp_m1e-6.json
```

The current entrypoint certifies interval bounds only. It deliberately rejects
the saved B12 near-miss and reserves exact acceptance for rational-coordinate
inputs under `coordinates_exact`.

Acceptance criteria:

- The verifier distinguishes malformed input, floating near-miss,
  interval-certified strict convexity with uncertified equality, and exact or
  algebraic acceptance.
- JSON output includes validation errors, residual bounds, claim strength, and
  failure mode.
- No floating candidate is promoted to a counterexample.

Trust delta: may promote selected candidate checks from numerical evidence to
interval-certified validation only when interval hypotheses are actually met.
It may not certify exact distance equalities from floating residuals alone.

Forbidden overclaiming text:

- "B12 is a counterexample"
- "near miss"
- "intervals prove exact equality" unless the interval certificate really does

## Cross-Cutting Rules

- Run `make verify-fast` or the raw fast tier after code or documentation
  changes.
- Run `make verify-artifacts` or `make audit-artifacts` before finite-case,
  certificate, or public theorem-style updates.
- Update `README.md`, `STATE.md`, `RESULTS.md`, and `metadata/erdos97.yaml`
  together only when a task changes source-of-truth status.
- Keep archived/provenance statements marked when superseded.
- Do not prepare OEIS submissions from AI-generated output.
