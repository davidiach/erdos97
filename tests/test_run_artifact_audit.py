from __future__ import annotations

import sys
from pathlib import Path

import yaml

from scripts.run_artifact_audit import AUDIT_COMMANDS, AuditCommand, command_text, run_audit_command, sha256_bytes


ROOT = Path(__file__).resolve().parents[1]


def test_sha256_bytes_is_stable() -> None:
    assert sha256_bytes(b"erdos97\n") == "d804cace0801472174f9f279439ba930de0123adced9367f0df1dcc8dc996d4b"


def test_run_audit_command_records_metadata(tmp_path: Path) -> None:
    command = AuditCommand(
        ident="smoke",
        command=(sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'ok\\n')"),
        claim_scope="test command only",
    )

    record = run_audit_command(command, tmp_path)

    assert record["id"] == "smoke"
    assert record["exit_code"] == 0
    assert record["claim_scope"] == "test command only"
    assert record["stdout_bytes"] == len(b"ok\n")
    assert (tmp_path / record["stdout_path"]).read_bytes() == b"ok\n"
    assert (tmp_path / record["stderr_path"]).read_bytes() == b""
    assert len(record["combined_output_sha256"]) == 64


def test_audit_commands_cover_generated_artifact_check_commands() -> None:
    metadata = yaml.safe_load((ROOT / "metadata/generated_artifacts.yaml").read_text(encoding="utf-8"))
    audit_commands = {command_text(command.command) for command in AUDIT_COMMANDS}

    missing = []
    for artifact in metadata["artifacts"]:
        check_command = artifact.get("check_command")
        if check_command and check_command not in audit_commands:
            missing.append(f"{artifact['id']}: {check_command}")

    assert missing == []


def test_audit_commands_include_registered_followup_checkers() -> None:
    ordered_command_texts = [command_text(command.command) for command in AUDIT_COMMANDS]
    command_texts = set(ordered_command_texts)

    assert (
        "python scripts/check_kalmanson_two_order_z3.py --certificate "
        "data/certificates/c19_skew_all_orders_kalmanson_z3.json --assert-unsat"
        in command_texts
    )
    assert (
        "python scripts/independent_n8_obstruction_recheck.py --check --json"
        in command_texts
    )
    assert "python scripts/check_n8_class14_certificate.py --check --json" in command_texts
    assert "python scripts/check_n8_residual_certificates.py --check --json" in command_texts
    assert (
        "python scripts/analyze_kalmanson_inverse_pair_templates.py --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/analyze_kalmanson_sparse_frontier_templates.py --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/analyze_kalmanson_inverse_pair_templates.py --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/analyze_kalmanson_sparse_frontier_templates.py --assert-expected --json"
    )
    assert (
        "python scripts/check_speculative_circulant_frontier_obstructions.py "
        "--check --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/analyze_kalmanson_sparse_frontier_templates.py --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_speculative_circulant_frontier_obstructions.py "
        "--check --json"
    )
    assert (
        "python scripts/analyze_kalmanson_z3_clauses.py --assert-expected "
        "--check-artifact reports/c19_kalmanson_z3_clause_diagnostics.json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_low_excess_ledgers.py --check --json"
        in command_texts
    )
    assert "python scripts/check_n9_base_apex_escape_budget.py --check --json" in command_texts
    assert (
        "python scripts/check_n9_selected_baseline_escape_budget_overlay.py --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_selected_baseline_d3_escape_class_crosswalk.py "
        "--check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_selected_baseline_d3_vertex_circle_template_join.py "
        "--check --json"
        in command_texts
    )
    assert "python scripts/check_n9_d3_escape_slice.py --check --json" in command_texts
    assert (
        "python scripts/check_n9_base_apex_d3_escape_frontier_packet.py --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_d3_p19_incidence_capacity_pilot.py --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_d3_incidence_capacity_packet.py --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_d3_artifact_join.py --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_audit_path.py --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_low_excess_escape_ladder.py --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_low_excess_escape_crosswalk.py --check --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_selected_baseline_escape_budget_overlay.py --check --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_d3_escape_slice.py --check --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_d3_escape_slice.py --check --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_selected_baseline_d3_escape_class_crosswalk.py "
        "--check --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_base_apex_low_excess_escape_crosswalk.py --check --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_selected_baseline_d3_escape_class_crosswalk.py "
        "--check --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_selected_baseline_d3_escape_class_crosswalk.py "
        "--check --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_selected_baseline_d3_vertex_circle_template_join.py "
        "--check --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_selected_baseline_d3_vertex_circle_template_join.py "
        "--check --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_base_apex_d3_p19_incidence_capacity_pilot.py --check --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_base_apex_low_excess_escape_crosswalk.py --check --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_base_apex_d3_incidence_capacity_packet.py --check --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_base_apex_d3_incidence_capacity_packet.py --check --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_base_apex_d3_artifact_join.py --check --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_base_apex_d3_artifact_join.py --check --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_base_apex_audit_path.py --check --json"
    )
    assert (
        "python scripts/check_n9_row_ptolemy_product_cancellations.py --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_row_ptolemy_family_signatures.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_row_ptolemy_order_sensitivity.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_row_ptolemy_order_admissible_census.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_row_ptolemy_admissible_gap_replay.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_row_ptolemy_gap_self_edge_cores.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_bridge_lemma_frontier.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_row_ptolemy_gap_self_edge_cores.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_bridge_lemma_frontier.py --check "
        "--assert-expected --json"
    )
    bootstrap_bridge_commands = (
        "python scripts/check_bootstrap_core_crosswalk.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_vertex_circle_overlay.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_forcing_targets.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_row_pressure.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_closure_exposed.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_one_outside.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_outside_pair.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_activation_requirements.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_bridge_target_map.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_hard_strict_endpoints.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_open_connector_pair.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_relation_sufficient_rows.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_81_3_closure_target.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_81_3_rich_triple_contract.py "
        "--check --assert-expected --json",
        "python scripts/check_bootstrap_t12_81_3_order_escape.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_81_3_escape_candidates.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_81_3_escape_two_row_drop.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_81_3_escape_full_neighborhood.py "
        "--check --assert-expected --json",
        "python scripts/check_bootstrap_t12_81_3_escape_auxiliary_csp.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_81_3_trigger_uniqueness.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_81_3_escape_rich_support_csp.py "
        "--check --assert-expected --json",
        "python scripts/check_bootstrap_t12_81_8_singleton_support_audit.py "
        "--check --assert-expected --json",
        "python scripts/check_bootstrap_t12_151_6_outside_pair_audit.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_151_singleton_support_audit.py --check "
        "--assert-expected --json",
        "python scripts/check_closure_activation_wrong_fourth_negative_control.py "
        "--check --assert-expected --json",
        "python scripts/check_closure_activation_negative_controls.py --check "
        "--assert-expected --json",
        "python scripts/check_bootstrap_t12_anti_activation_negative_control.py "
        "--check --assert-expected --json",
        "python scripts/check_closure_visibility_anti_activation_control.py --check "
        "--assert-expected --json",
    )
    for command in bootstrap_bridge_commands:
        assert command in command_texts

    previous_command = (
        "python scripts/check_bridge_lemma_frontier.py --check "
        "--assert-expected --json"
    )
    for command in bootstrap_bridge_commands:
        assert ordered_command_texts.index(previous_command) < ordered_command_texts.index(
            command
        )
        previous_command = command
    assert ordered_command_texts.index(
        bootstrap_bridge_commands[-1]
    ) < ordered_command_texts.index(
        "python scripts/check_block6_fragile_vertex_circle_extension.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_local_core_packet.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/analyze_n9_vertex_circle_obstruction_shapes.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/analyze_n9_vertex_circle_motif_families.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_turn_inequality_frontier.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_input_audit.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_incidence_filters.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_branch_options.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_dynamic_mro_choices.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/analyze_n9_vertex_circle_obstruction_shapes.py --check "
        "--assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/analyze_n9_vertex_circle_obstruction_shapes.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/analyze_n9_vertex_circle_motif_families.py --check "
        "--assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/analyze_n9_vertex_circle_motif_families.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_turn_inequality_frontier.py --check "
        "--assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_turn_inequality_frontier.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_input_audit.py --check "
        "--assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_input_audit.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_incidence_filters.py --check "
        "--assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_incidence_filters.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_branch_options.py --check "
        "--assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_branch_options.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_dynamic_mro_choices.py --check "
        "--assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_dynamic_mro_choices.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_mro_branching_replay.py --check "
        "--assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_mro_branching_replay.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check "
        "--assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check "
        "--assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_local_core_packet.py --check "
        "--assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_local_core_subset_audit.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_local_core_packet.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_local_core_subset_audit.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_local_core_subset_audit.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_core_templates.py --check "
        "--assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_core_templates.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_frontier_motif_classification.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_dihedral_orbit_audit.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_motif_obstruction_audit.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/compare_n9_vertex_circle_frontier.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_frontier_assignment_audit.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_quotient_soundness.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_partial_pruning.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_frontier_motif_classification.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_dihedral_orbit_audit.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_dihedral_orbit_audit.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_motif_obstruction_audit.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_motif_obstruction_audit.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/compare_n9_vertex_circle_frontier.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/compare_n9_vertex_circle_frontier.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_frontier_assignment_audit.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_frontier_assignment_audit.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_quotient_soundness.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_quotient_soundness.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_partial_pruning.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_partial_pruning.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_self_edge_path_join.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_self_edge_path_join.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_self_edge_template_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_strict_cycle_path_join.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_strict_cycle_template_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_template_lemma_catalog.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_local_lemmas.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_local_lemmas.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_relation_skeleton_local_lemma_crosswalk.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_vertex_circle_local_lemma_audit_path.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_relation_skeleton_local_lemma_crosswalk.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_local_lemma_audit_path.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_local_lemma_audit_path.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_t01_self_edge_minireplay.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_t01_self_edge_minireplay.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_t02_self_edge_minireplay.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_t02_self_edge_minireplay.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_t02_self_edge_minireplay.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_t03_self_edge_minireplay.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_t03_self_edge_minireplay.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_t03_self_edge_minireplay.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t04_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_t04_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_t04_self_edge_minireplay.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t04_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_t04_self_edge_minireplay.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_t04_self_edge_minireplay.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t05_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_t05_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_t05_self_edge_minireplay.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t05_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_t05_self_edge_minireplay.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_t05_self_edge_minireplay.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t06_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_t06_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_t06_self_edge_minireplay.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t06_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_t06_self_edge_minireplay.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_t06_self_edge_minireplay.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t07_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_t07_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_t07_self_edge_minireplay.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t07_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_t07_self_edge_minireplay.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_t07_self_edge_minireplay.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t08_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_t08_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_t08_self_edge_minireplay.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t08_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_t08_self_edge_minireplay.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_t08_self_edge_minireplay.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t09_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_t09_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_t09_self_edge_minireplay.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t09_self_edge_lemma_packet.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_t09_self_edge_minireplay.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_t09_self_edge_minireplay.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_t10_strict_cycle_minireplay.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_t10_paired_square_entry.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_t10_strict_cycle_minireplay.py "
        "--check --assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_t10_strict_cycle_minireplay.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_t10_paired_square_entry.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_t11_strict_cycle_minireplay.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_t11_strict_cycle_minireplay.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_t12_strict_cycle_minireplay.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py "
        "--check --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n9_t12_strict_cycle_minireplay.py "
        "--check --assert-expected --json"
    )
    assert (
        "python scripts/check_n10_turn_row0_pilot.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n10_turn_row0_escape_self_edges.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/check_n10_turn_row0_pilot.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n10_turn_row0_escape_self_edges.py --check "
        "--assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_n10_turn_row0_escape_self_edges.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_n10_vertex_circle_singletons.py --assert-expected "
        "--spot-check-row0 0 --spot-check-row0 63 --spot-check-row0 125"
    )
    assert (
        "python scripts/check_n10_vertex_circle_singletons.py --assert-expected "
        "--spot-check-row0 0 --spot-check-row0 63 --spot-check-row0 125"
        in command_texts
    )
    assert (
        "python scripts/check_n10_singleton_input_audit.py --check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n10_secondary_singleton_replay.py --check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_block6_fragile_sixth_row_survivors.py "
        "--assert-expected --json"
        in command_texts
    )
