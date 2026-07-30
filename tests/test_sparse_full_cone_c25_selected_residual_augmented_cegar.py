from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts"
    / "exploration"
    / "run_sparse_full_cone_c25_selected_residual_augmented_cegar.py"
)
SPEC = importlib.util.spec_from_file_location(
    "sparse_full_cone_c25_selected_residual_augmented_cegar",
    SCRIPT,
)
assert SPEC is not None and SPEC.loader is not None
CEGAR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CEGAR
SPEC.loader.exec_module(CEGAR)

ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_selected_residual_augmented_cegar_2026-07-30"
    / "summary.json"
)


def artifact_payload() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_stored_packet_blocks_the_complete_168_order_history() -> None:
    history = artifact_payload()["blocked_history"]

    assert history["order_count"] == 168
    assert history["dihedral_order_count"] == 168
    assert history["packet_histogram"] == {
        "augmentation_probe": 32,
        "first_fresh": 32,
        "persistent_augmented_probe": 16,
        "persistent_augmented_residual": 8,
        "prior": 24,
        "second_fresh": 32,
        "transfer_cegar_probe": 16,
        "transfer_cegar_residual": 8,
    }
    assert len(history["identities"]) == 168
    assert len(
        {record["dihedral_order_sha256"] for record in history["identities"]}
    ) == 168


def test_seed_policy_adds_only_selected_residual_two_width_three() -> None:
    payload = artifact_payload()

    assert [
        record["ordered_quad_count"]
        for record in payload["transferred_seed_templates"]
    ] == [3, 5, 14]
    assert payload["selected_persistent_seed_template"][
        "ordered_quad_count"
    ] == 4
    selected = payload["selected_residual_seed_template"]
    assert selected["source_target_id"] == "residual:2"
    assert selected["source_model_index"] == 2
    assert selected["ordered_quad_count"] == 3
    assert selected["seed_role"] == "EXACT_MINIMUM_ACTIVE_SEED_ESCAPE_COVER"
    assert payload["active_seed_orbit_count"] == 5
    assert payload["active_exact_affine_seed_image_count"] == 125
    assert payload["unique_active_seed_orbit_clause_count"] == 125
    assert len(payload["inactive_seed_templates"]) == 16


def test_selected_width_three_has_no_fresh_probe_marginal_coverage() -> None:
    payload = artifact_payload()
    probe = payload["counterfactual_probe"]
    comparison = payload["counterfactual_seed_packet_coverage"]

    assert probe["status"] == "BOUNDED_HISTORY_DISJOINT_PROBE_ORDER_LIMIT_REACHED"
    assert probe["iterations"] == 497
    assert probe["inverse_pair_clause_count"] == 14485
    assert probe["inverse_pair_escape_order_count"] == 16
    assert all(model["lightweight_filters"]["survives"] for model in probe["models"])
    assert comparison["parent_four_seeds"]["covered_probe_order_count"] == 16
    assert comparison["selected_width3_only"]["covered_probe_order_count"] == 4
    assert comparison["parent_plus_selected_width3"][
        "covered_probe_order_count"
    ] == 16
    assert comparison["selected_width3_covered_probe_model_indices"] == [
        0,
        1,
        2,
        3,
    ]
    assert (
        comparison[
            "selected_width3_marginal_over_parent_probe_model_indices"
        ]
        == []
    )
    assert comparison["active_uncovered_probe_model_indices"] == []


def test_five_seed_cegar_learns_eight_new_exact_wide_certificates() -> None:
    payload = artifact_payload()
    seeded = payload["seeded_cegar"]
    models = seeded["models"]

    assert seeded["status"] == (
        "BOUNDED_C25_SELECTED_RESIDUAL_AUGMENTED_CERTIFICATE_LIMIT_REACHED"
    )
    assert seeded["solver_result"] == "bounded_after_new_exact_certificates"
    assert seeded["iterations"] == 81
    assert seeded["initial_probe_inverse_clause_count"] == 14485
    assert seeded["final_inverse_pair_clause_count"] == 15094
    assert seeded["new_full_certificate_count"] == 8
    assert seeded["new_unique_affine_orbit_clause_count"] == 200
    assert [
        model["full_kalmanson"]["unique_ordered_quad_count"] for model in models
    ] == [219, 220, 214, 216, 211, 217, 219, 210]
    assert all(model["full_kalmanson"]["zero_sum_verified"] for model in models)
    assert all(model["lightweight_filters"]["survives"] for model in models)
    assert all(model["seed_orbit_matches"] == [] for model in models)
    assert payload["decision"] == (
        "COMPRESS_NEW_C25_SELECTED_RESIDUAL_AUGMENTED_ESCAPES"
    )


def test_stored_selected_residual_augmented_cegar_replays_exactly() -> None:
    assert CEGAR.check_payload(artifact_payload()) == {
        "status": "OK",
        "verified_blocked_history_orders": 168,
        "verified_active_seed_certificates": 5,
        "verified_inactive_seed_certificates": 16,
        "verified_counterfactual_probe_orders": 16,
        "verified_new_exact_full_cone_certificates": 8,
        "verified_exact_affine_certificate_images": 325,
        "verified_new_unique_affine_orbit_clauses": 200,
        "decision": "COMPRESS_NEW_C25_SELECTED_RESIDUAL_AUGMENTED_ESCAPES",
    }
