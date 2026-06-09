from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _make_target_commands(target: str) -> list[str]:
    lines = (ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
    header = f"{target}:"
    start = lines.index(header) + 1
    commands: list[str] = []
    for line in lines[start:]:
        if line and not line.startswith("\t"):
            break
        if line.startswith("\t"):
            commands.append(line.strip().replace("$(PYTHON)", "python"))
    return commands


def test_verify_n9_candidate_is_compact_promotion_review_harness() -> None:
    commands = _make_target_commands("verify-n9-candidate")
    expected_chain = [
        "python scripts/check_n9_candidate_review_manifest.py --check --summary-json",
        "python scripts/check_n9_review_gate_ledger.py --check --summary-json",
        "python scripts/check_n9_review_evidence_matrix.py --check --summary-json",
        "python scripts/check_n9_review_dossier.py --check --summary-json",
        "python scripts/check_n9_review_run_bundle.py --check --summary-json",
        "python scripts/check_n9_review_decision_intake.py --check --summary-json",
        (
            "python scripts/check_n9_vertex_circle_route_decision_preflight.py "
            "--check --summary-json"
        ),
        (
            "python scripts/check_n9_vertex_circle_route_decision_request.py "
            "--check --summary-json"
        ),
        "python scripts/check_lean_sketch_integrity.py",
        "python scripts/check_lean_files.py",
        "python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json",
        (
            "python scripts/check_n9_vertex_circle_input_audit.py "
            "--check --assert-expected --summary-json"
        ),
        (
            "python scripts/check_n9_vertex_circle_incidence_filters.py "
            "--check --assert-expected --summary-json"
        ),
        (
            "python scripts/check_n9_vertex_circle_mro_branching_replay.py "
            "--check --assert-expected --summary-json"
        ),
        (
            "python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py "
            "--check --assert-expected --summary-json"
        ),
        (
            "python scripts/check_n9_vertex_circle_strict_edge_geometry.py "
            "--check --assert-expected --summary-json"
        ),
        (
            "python scripts/check_n9_vertex_circle_quotient_soundness.py "
            "--check --assert-expected --summary-json"
        ),
        (
            "python scripts/check_n9_vertex_circle_local_lemma_audit_path.py "
            "--check --assert-expected --summary-json"
        ),
        (
            "python scripts/check_turn_inequality_indexing.py "
            "--check --assert-expected --summary-json"
        ),
        (
            "python scripts/check_n9_turn_inequality_frontier.py "
            "--check --assert-expected --summary-json"
        ),
        (
            "python scripts/check_n9_kalmanson_selfedge_independent_replay.py "
            "--check --assert-expected --summary-json"
        ),
    ]

    assert commands == expected_chain


def test_verify_n9_review_includes_documented_frontier_audits() -> None:
    commands = _make_target_commands("verify-n9-review")
    expected_chain = [
        "python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json",
        (
            "python scripts/check_n9_vertex_circle_compact_brancher.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/analyze_n9_vertex_circle_obstruction_shapes.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/analyze_n9_vertex_circle_motif_families.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_turn_inequality_indexing.py "
            "--check --assert-expected --summary-json"
        ),
        (
            "python scripts/check_n9_turn_inequality_frontier.py "
            "--check --assert-expected --summary-json"
        ),
        (
            "python scripts/check_n9_vertex_circle_input_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_incidence_filters.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_branch_options.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_dynamic_mro_choices.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_mro_branching_replay.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_strict_edge_geometry.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_local_core_packet.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_local_core_subset_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_core_templates.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_frontier_motif_classification.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_dihedral_orbit_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_motif_obstruction_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/compare_n9_vertex_circle_frontier.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_frontier_assignment_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_quotient_soundness.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_closed_descent_packet.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_partial_pruning.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_self_edge_path_join.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_relation_skeleton_catalog.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_relation_skeleton_local_lemma_crosswalk.py "
            "--check --assert-expected --json"
        ),
    ]

    for command in expected_chain:
        assert command in commands

    positions = [commands.index(command) for command in expected_chain]
    assert positions == sorted(positions)


def test_verify_bridge_frontier_includes_bootstrap_audits() -> None:
    commands = _make_target_commands("verify-bridge-frontier")
    expected_chain = [
        "python scripts/check_bridge_lemma_frontier.py --check --assert-expected --json",
        "python scripts/check_rich_support_counting_bound.py --check --json",
        "python scripts/check_support_saturation_obstruction.py --check --json",
        "python scripts/check_n12_rich_support_determinant.py --check --json",
        "python scripts/check_localized_rich_support_counting.py --check --json",
        (
            "python scripts/check_adjacent_closest_pair_nonagon_barrier.py "
            "--check --summary-json"
        ),
        (
            "python scripts/check_bootstrap_core_crosswalk.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_vertex_circle_overlay.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_forcing_targets.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_row_pressure.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_closure_exposed.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_one_outside.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_outside_pair.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_activation_requirements.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_bridge_target_map.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_hard_strict_endpoints.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_open_connector_pair.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_relation_sufficient_rows.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_151_6_outside_pair_connector_contract.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_closure_target.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_rich_triple_contract.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_order_escape.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_escape_candidates.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_escape_two_row_drop.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_escape_full_neighborhood.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_escape_auxiliary_csp.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_trigger_uniqueness.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_escape_rich_support_csp.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_first_supply_chains.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_second_supply_chains.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_second_step_chains.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_post8_supply_chains.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_chain_closure_csp.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_repeated_support_catalogue_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_two_repeated_support_catalogue_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_3_repeated_support_saturation_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_8_singleton_support_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_8_singleton_support_two_row_drop.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_81_8_full_neighborhood_vertex_circle.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_151_6_outside_pair_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_151_6_outside_pair_two_row_drop.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_151_6_outside_pair_escape_partition.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_151_6_endpoint8_forcing_preflight.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_151_singleton_support_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_151_singleton_two_row_drop.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_singleton_full_neighborhood_crosswalk.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_closure_activation_wrong_fourth_negative_control.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_closure_activation_negative_controls.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_bootstrap_t12_anti_activation_negative_control.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_closure_visibility_anti_activation_control.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_block6_fragile_vertex_circle_extension.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_block6_fragile_sixth_row_survivors.py "
            "--assert-expected --json"
        ),
        (
            "python scripts/check_block6_terminal_crossing_vertex_circle_sample.py "
            "--check --assert-expected --json"
        ),
    ]

    for command in expected_chain:
        assert command in commands

    positions = [commands.index(command) for command in expected_chain]
    assert positions == sorted(positions)


def test_verify_n10_review_includes_turn_audits() -> None:
    commands = _make_target_commands("verify-n10-review")
    expected_chain = [
        (
            "python scripts/check_n10_mixed_rich_support_capacity.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n10_q2_rich_vertex_circle.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n10_q1_rich_vertex_circle.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n10_turn_row0_pilot.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n10_turn_row0_escape_self_edges.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n10_singleton_input_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n10_vertex_circle_singletons.py "
            "--assert-expected --spot-check-row0 0 --spot-check-row0 63 "
            "--spot-check-row0 125"
        ),
        (
            "python scripts/check_n10_secondary_singleton_replay.py "
            "--check --assert-expected --json"
        ),
    ]

    for command in expected_chain:
        assert command in commands

    positions = [commands.index(command) for command in expected_chain]
    assert positions == sorted(positions)
