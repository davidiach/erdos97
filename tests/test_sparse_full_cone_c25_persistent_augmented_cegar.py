from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts"
    / "exploration"
    / "run_sparse_full_cone_c25_persistent_augmented_cegar.py"
)
SPEC = importlib.util.spec_from_file_location(
    "sparse_full_cone_c25_persistent_augmented_cegar",
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
    / "sparse_full_cone_c25_persistent_augmented_cegar_2026-07-30"
    / "summary.json"
)


def artifact_payload() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_stored_packet_blocks_the_complete_144_order_history() -> None:
    history = artifact_payload()["blocked_history"]

    assert history["order_count"] == 144
    assert history["dihedral_order_count"] == 144
    assert history["packet_histogram"] == {
        "augmentation_probe": 32,
        "first_fresh": 32,
        "prior": 24,
        "second_fresh": 32,
        "transfer_cegar_probe": 16,
        "transfer_cegar_residual": 8,
    }
    assert len(history["identities"]) == 144
    assert len(
        {record["dihedral_order_sha256"] for record in history["identities"]}
    ) == 144


def test_seed_policy_activates_only_transferred_plus_selected_width_four() -> None:
    payload = artifact_payload()
    transferred = payload["transferred_seed_templates"]
    selected = payload["selected_persistent_seed_template"]
    inactive = payload["inactive_seed_templates"]

    assert [record["ordered_quad_count"] for record in transferred] == [3, 5, 14]
    assert selected["source_target_id"] == "transfer_cegar_probe:0"
    assert selected["ordered_quad_count"] == 4
    assert selected["seed_role"] == "PRIMARY_MINIMUM_NEW_MARGINAL_COVER"
    assert payload["active_seed_orbit_count"] == 4
    assert payload["active_exact_affine_seed_image_count"] == 100
    assert payload["unique_active_seed_orbit_clause_count"] == 100
    assert [record["seed_id"] for record in inactive] == [
        "persistent_compressed:1",
        "residual:0",
        "residual:1",
        "residual:2",
        "residual:3",
        "residual:4",
        "residual:5",
        "residual:6",
        "residual:7",
    ]
    assert [record["ordered_quad_count"] for record in inactive] == [
        5,
        7,
        9,
        5,
        3,
        7,
        4,
        6,
        4,
    ]


def test_width_four_orbit_covers_all_sixteen_fresh_probe_orders_marginally() -> None:
    payload = artifact_payload()
    probe = payload["counterfactual_probe"]
    comparison = payload["counterfactual_seed_packet_coverage"]

    assert probe["status"] == "BOUNDED_HISTORY_DISJOINT_PROBE_ORDER_LIMIT_REACHED"
    assert probe["iterations"] == 454
    assert probe["inverse_pair_clause_count"] == 14122
    assert probe["inverse_pair_escape_order_count"] == 16
    assert all(model["lightweight_filters"]["survives"] for model in probe["models"])
    assert comparison["transferred_only"]["covered_probe_order_count"] == 0
    assert comparison["selected_width4_only"]["covered_probe_order_count"] == 16
    assert (
        comparison["transferred_plus_selected_width4"][
            "covered_probe_order_count"
        ]
        == 16
    )
    assert comparison[
        "selected_width4_marginal_over_transferred_probe_model_indices"
    ] == list(range(16))
    assert comparison["active_uncovered_probe_model_indices"] == []


def test_augmented_cegar_learns_eight_new_exact_wide_certificates() -> None:
    payload = artifact_payload()
    seeded = payload["seeded_cegar"]
    models = seeded["models"]

    assert seeded["status"] == (
        "BOUNDED_C25_PERSISTENT_AUGMENTED_CERTIFICATE_LIMIT_REACHED"
    )
    assert seeded["solver_result"] == "bounded_after_new_exact_certificates"
    assert seeded["iterations"] == 102
    assert seeded["initial_probe_inverse_clause_count"] == 14122
    assert seeded["final_inverse_pair_clause_count"] == 15006
    assert seeded["new_full_certificate_count"] == 8
    assert seeded["new_unique_affine_orbit_clause_count"] == 200
    assert [
        model["full_kalmanson"]["unique_ordered_quad_count"] for model in models
    ] == [197, 197, 193, 194, 192, 200, 191, 195]
    assert all(
        model["full_kalmanson"]["zero_sum_verified"] for model in models
    )
    assert all(model["lightweight_filters"]["survives"] for model in models)
    assert all(model["seed_orbit_matches"] == [] for model in models)
    assert payload["decision"] == (
        "COMPRESS_NEW_C25_PERSISTENT_AUGMENTED_RESIDUALS"
    )


def test_stored_persistent_augmented_cegar_replays_exactly() -> None:
    assert CEGAR.check_payload(artifact_payload()) == {
        "status": "OK",
        "verified_blocked_history_orders": 144,
        "verified_active_seed_certificates": 4,
        "verified_inactive_seed_certificates": 9,
        "verified_counterfactual_probe_orders": 16,
        "verified_new_exact_full_cone_certificates": 8,
        "verified_exact_affine_certificate_images": 300,
        "verified_new_unique_affine_orbit_clauses": 200,
        "decision": "COMPRESS_NEW_C25_PERSISTENT_AUGMENTED_RESIDUALS",
    }

def test_checker_rejects_substituted_source_artifact(tmp_path: Path) -> None:
    substitute = tmp_path / "summary.json"
    substitute.write_bytes(CEGAR.DEFAULT_SOURCE.read_bytes())
    payload = artifact_payload()
    payload["source_compression_artifact"] = str(substitute)
    payload["source_compression_sha256"] = CEGAR.file_sha256(substitute)

    with pytest.raises(AssertionError, match="source artifact drifted"):
        CEGAR.check_payload(payload)
