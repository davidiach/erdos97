PYTHON ?= python

.PHONY: verify-lint verify-fast verify-pytest-artifacts verify-pytest-all verify-n8 verify-kalmanson verify-n9-review verify-bridge-frontier verify-n10-review verify-artifacts audit-artifacts verify-all

verify-lint:
	$(PYTHON) scripts/check_text_clean.py
	$(PYTHON) scripts/check_status_consistency.py
	$(PYTHON) scripts/check_artifact_provenance.py
	git diff --check
	$(PYTHON) -m ruff check .

verify-fast: verify-lint
	$(PYTHON) -m pytest -q

verify-pytest-artifacts:
	$(PYTHON) -m pytest -q -m "artifact"

verify-pytest-all:
	$(PYTHON) -m pytest -q -o addopts=

verify-n8:
	$(PYTHON) scripts/independent_check_n8_artifacts.py --check --json
	$(PYTHON) scripts/enumerate_n8_incidence.py --summary
	$(PYTHON) scripts/analyze_n8_exact_survivors.py --check --json

verify-kalmanson:
	$(PYTHON) scripts/check_round2_certificates.py
	$(PYTHON) scripts/check_kalmanson_certificate.py data/certificates/round2/c19_kalmanson_known_order_two_unsat.json --summary-json
	$(PYTHON) scripts/check_kalmanson_certificate.py data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json --summary-json
	$(PYTHON) scripts/check_kalmanson_two_order_search.py --name C13_sidon_1_2_4_10 --n 13 --offsets 1,2,4,10 --assert-obstructed --assert-c13-expected --json
	$(PYTHON) scripts/check_kalmanson_two_order_z3.py --certificate data/certificates/c19_skew_all_orders_kalmanson_z3.json --assert-unsat
	$(PYTHON) scripts/analyze_kalmanson_inverse_pair_templates.py --assert-expected --json
	$(PYTHON) scripts/analyze_kalmanson_sparse_frontier_templates.py --assert-expected --json

verify-n9-review:
	$(PYTHON) scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
	$(PYTHON) scripts/analyze_n9_vertex_circle_obstruction_shapes.py --check --assert-expected --json
	$(PYTHON) scripts/analyze_n9_vertex_circle_motif_families.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_inversive_incidence_pilot.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_input_audit.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_branch_options.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_dynamic_mro_choices.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_mro_branching_replay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_kalmanson_selfedge.py --verify-certificate data/certificates/n9_kalmanson_selfedge.json --assert-expected --json
	$(PYTHON) scripts/check_n9_kalmanson_selfedge_independent_replay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_local_core_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_local_core_subset_audit.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_core_templates.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_frontier_motif_classification.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_dihedral_orbit_audit.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_motif_obstruction_audit.py --check --assert-expected --json
	$(PYTHON) scripts/compare_n9_vertex_circle_frontier.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_frontier_assignment_audit.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_quotient_soundness.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_partial_pruning.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_self_edge_path_join.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_self_edge_template_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_strict_cycle_path_join.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_strict_cycle_template_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_local_lemmas.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_local_lemma_simple_replay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_t01_self_edge_minireplay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_t02_self_edge_minireplay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_t03_self_edge_minireplay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t04_self_edge_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_t04_self_edge_minireplay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t05_self_edge_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_t05_self_edge_minireplay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t06_self_edge_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_t06_self_edge_minireplay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t07_self_edge_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_t07_self_edge_minireplay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t08_self_edge_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_t08_self_edge_minireplay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t09_self_edge_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_t09_self_edge_minireplay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_t10_strict_cycle_minireplay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_t10_paired_square_entry.py --check --assert-expected --json
	$(PYTHON) scripts/check_relation_skeleton_catalog.py --check --assert-expected --json
	$(PYTHON) scripts/check_relation_skeleton_local_lemma_crosswalk.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_t11_strict_cycle_minireplay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_t12_strict_cycle_minireplay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_row_ptolemy_product_cancellations.py --check --json
	$(PYTHON) scripts/check_n9_row_ptolemy_family_signatures.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_row_ptolemy_order_sensitivity.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_row_ptolemy_order_admissible_census.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_row_ptolemy_admissible_gap_replay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_row_ptolemy_gap_self_edge_cores.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_base_apex_low_excess_ledgers.py --check --json
	$(PYTHON) scripts/check_n9_base_apex_escape_budget.py --check --json
	$(PYTHON) scripts/check_n9_selected_baseline_escape_budget_overlay.py --check --json
	$(PYTHON) scripts/check_n9_selected_baseline_d3_escape_class_crosswalk.py --check --json
	$(PYTHON) scripts/check_n9_d3_escape_slice.py --check --json
	$(PYTHON) scripts/check_n9_base_apex_d3_escape_frontier_packet.py --check --json
	$(PYTHON) scripts/check_n9_base_apex_low_excess_escape_ladder.py --check --json
	$(PYTHON) scripts/check_n9_base_apex_low_excess_escape_crosswalk.py --check --json
	$(PYTHON) scripts/check_n9_base_apex_d3_p19_incidence_capacity_pilot.py --check --json
	$(PYTHON) scripts/check_n9_base_apex_d3_incidence_capacity_packet.py --check --json
	$(PYTHON) scripts/check_n9_base_apex_d3_artifact_join.py --check --json
	$(PYTHON) scripts/check_n9_base_apex_audit_path.py --check --json

verify-bridge-frontier:
	$(PYTHON) scripts/check_bridge_lemma_frontier.py --check --assert-expected --json
	$(PYTHON) scripts/check_rich_support_counting_bound.py --check --json
	$(PYTHON) scripts/check_bootstrap_core_crosswalk.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_vertex_circle_overlay.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_forcing_targets.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_row_pressure.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_closure_exposed.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_one_outside.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_outside_pair.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_activation_requirements.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_bridge_target_map.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_hard_strict_endpoints.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_open_connector_pair.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_relation_sufficient_rows.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_81_3_closure_target.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_81_3_rich_triple_contract.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_81_3_order_escape.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_81_3_escape_candidates.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_81_3_escape_two_row_drop.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_81_3_escape_full_neighborhood.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_81_3_escape_auxiliary_csp.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_81_3_trigger_uniqueness.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_81_3_escape_rich_support_csp.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_81_8_singleton_support_audit.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_151_6_outside_pair_audit.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_151_singleton_support_audit.py --check --assert-expected --json
	$(PYTHON) scripts/check_closure_activation_wrong_fourth_negative_control.py --check --assert-expected --json
	$(PYTHON) scripts/check_closure_activation_negative_controls.py --check --assert-expected --json
	$(PYTHON) scripts/check_bootstrap_t12_anti_activation_negative_control.py --check --assert-expected --json
	$(PYTHON) scripts/check_closure_visibility_anti_activation_control.py --check --assert-expected --json
	$(PYTHON) scripts/check_block6_fragile_vertex_circle_extension.py --check --assert-expected --json
	$(PYTHON) scripts/check_block6_fragile_sixth_row_survivors.py --assert-expected --json
	$(PYTHON) scripts/check_block6_terminal_crossing_vertex_circle_sample.py --check --assert-expected --json
	$(PYTHON) scripts/check_block6_terminal_crossing_vertex_circle_sample.py --full-sweep --check --assert-expected --json
	$(PYTHON) scripts/check_block6_fixed_order_vertex_circle_probe.py --check --assert-expected --json
	$(PYTHON) scripts/check_block6_shuffle_order_vertex_circle_sweep.py --check --assert-expected --json
	$(PYTHON) scripts/check_block6_reversed_block_shuffle_vertex_circle_escape.py --check --assert-expected --json
	$(PYTHON) scripts/check_block6_reversed_block_clean_kalmanson.py --check --assert-expected --json
	$(PYTHON) scripts/check_block6_reversed_block_two_stage_closure.py --check --assert-expected --json
	$(PYTHON) scripts/check_block6_forward_block_two_orientation_closure.py --check --assert-expected --json
	$(PYTHON) scripts/check_block6_oriented_block_reversal_closure.py --check --assert-expected --json

verify-n10-review:
	$(PYTHON) scripts/check_n10_mixed_rich_support_capacity.py --check --assert-expected --json
	$(PYTHON) scripts/check_n10_turn_row0_pilot.py --check --assert-expected --json
	$(PYTHON) scripts/check_n10_turn_row0_escape_self_edges.py --check --assert-expected --json
	$(PYTHON) scripts/check_n10_singleton_input_audit.py --check --assert-expected --json
	$(PYTHON) scripts/check_n10_vertex_circle_singletons.py --assert-expected --spot-check-row0 0 --spot-check-row0 63 --spot-check-row0 125
	$(PYTHON) scripts/check_n10_secondary_singleton_replay.py --check --assert-expected --json

verify-artifacts: verify-n8 verify-kalmanson verify-n9-review verify-bridge-frontier verify-n10-review

audit-artifacts:
	$(PYTHON) scripts/check_status_consistency.py --max-official-status-age-days 90
	$(PYTHON) scripts/check_artifact_provenance.py
	$(PYTHON) scripts/run_artifact_audit.py --output-dir artifact-audit-results

verify-all: verify-fast verify-artifacts
