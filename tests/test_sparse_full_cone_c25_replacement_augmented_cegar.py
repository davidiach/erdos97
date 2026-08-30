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
    / "run_sparse_full_cone_c25_replacement_augmented_cegar.py"
)
SPEC = importlib.util.spec_from_file_location(
    "sparse_full_cone_c25_replacement_augmented_cegar",
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
    / "sparse_full_cone_c25_replacement_augmented_cegar_2026-07-31"
    / "summary.json"
)


def artifact_payload() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_checker_rejects_substituted_source_artifact(tmp_path: Path) -> None:
    substitute = tmp_path / "summary.json"
    substitute.write_bytes(CEGAR.DEFAULT_SOURCE.read_bytes())
    payload = artifact_payload()
    payload["source_artifact"] = str(substitute)
    payload["source_sha256"] = CEGAR.file_sha256(substitute)

    with pytest.raises(AssertionError, match="source artifact drifted"):
        CEGAR.check_payload(payload)


def test_checker_rejects_tampered_pattern_metadata() -> None:
    mutations = (
        ("pattern", "C25_wrong", "pattern drifted"),
        ("n", 24, "pattern drifted"),
        ("circulant_offsets", [1, 2, 3, 4], "offsets drifted"),
    )
    for field, value, message in mutations:
        payload = artifact_payload()
        payload[field] = value
        with pytest.raises(AssertionError, match=message):
            CEGAR.check_payload(payload)


def test_stored_packet_blocks_the_complete_192_order_history() -> None:
    history = artifact_payload()["blocked_history"]

    assert history["order_count"] == 192
    assert history["dihedral_order_count"] == 192
    assert history["packet_histogram"] == {
        "augmentation_probe": 32,
        "first_fresh": 32,
        "persistent_augmented_probe": 16,
        "persistent_augmented_residual": 8,
        "prior": 24,
        "second_fresh": 32,
        "selected_residual_escape": 8,
        "selected_residual_probe": 16,
        "transfer_cegar_probe": 16,
        "transfer_cegar_residual": 8,
    }
    assert len(history["identities"]) == 192
    assert len(
        {record["dihedral_order_sha256"] for record in history["identities"]}
    ) == 192


def test_seed_policy_replaces_the_old_width_three_with_width_four() -> None:
    payload = artifact_payload()

    assert [
        record["ordered_quad_count"]
        for record in payload["transferred_seed_templates"]
    ] == [3, 5, 14]
    assert payload["selected_persistent_seed_template"][
        "ordered_quad_count"
    ] == 4
    selected = payload["selected_replacement_seed_template"]
    assert selected["source_target_id"] == "residual:2"
    assert selected["source_model_index"] == 2
    assert selected["ordered_quad_count"] == 4
    assert selected["seed_role"] == "EXACT_MINIMUM_FIVE_SEED_ESCAPE_COVER"
    assert payload["active_seed_orbit_count"] == 5
    assert payload["active_exact_affine_seed_image_count"] == 125
    assert payload["unique_active_seed_orbit_clause_count"] == 125
    assert len(payload["inactive_seed_templates"]) == 24


def test_replacement_width_four_has_no_fresh_probe_marginal_coverage() -> None:
    payload = artifact_payload()
    probe = payload["counterfactual_probe"]
    comparison = payload["counterfactual_seed_packet_coverage"]

    assert probe["status"] == "BOUNDED_HISTORY_DISJOINT_PROBE_ORDER_LIMIT_REACHED"
    assert probe["iterations"] == 421
    assert probe["inverse_pair_clause_count"] == 13708
    assert probe["inverse_pair_escape_order_count"] == 16
    assert all(model["lightweight_filters"]["survives"] for model in probe["models"])
    assert comparison["parent_four_seeds"]["covered_probe_order_count"] == 16
    assert comparison["replacement_width4_only"]["covered_probe_order_count"] == 16
    assert comparison["parent_plus_replacement"]["covered_probe_order_count"] == 16
    assert comparison["replacement_covered_probe_model_indices"] == list(range(16))
    assert comparison[
        "replacement_marginal_over_parent_probe_model_indices"
    ] == []
    assert comparison["replacement_overlap_with_parent_probe_model_indices"] == list(
        range(16)
    )
    assert comparison["active_uncovered_probe_model_indices"] == []


def test_replacement_cegar_learns_eight_new_exact_wide_certificates() -> None:
    payload = artifact_payload()
    seeded = payload["seeded_cegar"]
    models = seeded["models"]

    assert seeded["status"] == (
        "BOUNDED_C25_REPLACEMENT_AUGMENTED_CERTIFICATE_LIMIT_REACHED"
    )
    assert seeded["solver_result"] == "bounded_after_new_exact_certificates"
    assert seeded["iterations"] == 53
    assert seeded["initial_probe_inverse_clause_count"] == 13708
    assert seeded["final_inverse_pair_clause_count"] == 14178
    assert seeded["new_full_certificate_count"] == 8
    assert seeded["new_unique_affine_orbit_clause_count"] == 200
    assert [
        model["full_kalmanson"]["unique_ordered_quad_count"] for model in models
    ] == [198, 193, 195, 195, 196, 200, 199, 201]
    assert all(model["full_kalmanson"]["zero_sum_verified"] for model in models)
    assert all(model["lightweight_filters"]["survives"] for model in models)
    assert all(model["seed_orbit_matches"] == [] for model in models)
    assert payload["decision"] == (
        "COMPRESS_NEW_C25_REPLACEMENT_AUGMENTED_ESCAPES"
    )


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_stored_replacement_augmented_cegar_replays_exactly() -> None:
    assert CEGAR.check_payload(artifact_payload()) == {
        "status": "OK",
        "verified_blocked_history_orders": 192,
        "verified_active_seed_certificates": 5,
        "verified_inactive_seed_certificates": 24,
        "verified_counterfactual_probe_orders": 16,
        "verified_new_exact_full_cone_certificates": 8,
        "verified_exact_affine_certificate_images": 325,
        "verified_new_unique_affine_orbit_clauses": 200,
        "decision": "COMPRESS_NEW_C25_REPLACEMENT_AUGMENTED_ESCAPES",
    }
