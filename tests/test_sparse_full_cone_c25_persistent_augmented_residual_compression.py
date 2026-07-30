from __future__ import annotations

import copy
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
    / "compress_sparse_full_cone_c25_persistent_augmented_residuals.py"
)
SPEC = importlib.util.spec_from_file_location(
    "sparse_full_cone_c25_persistent_augmented_residual_compression",
    SCRIPT,
)
assert SPEC is not None and SPEC.loader is not None
COMPRESSION = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMPRESSION
SPEC.loader.exec_module(COMPRESSION)

SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_persistent_augmented_cegar_2026-07-30"
    / "summary.json"
)
ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_persistent_augmented_residual_compression_2026-07-30"
    / "summary.json"
)


def source_payload() -> dict[str, object]:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def artifact_payload() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_target_packet_separates_probe_hits_from_active_seed_escapes() -> None:
    targets = COMPRESSION.target_orders(source_payload())
    probe = [target for target in targets if target["stream"] == "probe"]
    residual = [
        target for target in targets if target["stream"] == "residual"
    ]

    assert len(targets) == 24
    assert len(probe) == 16
    assert len(residual) == 8
    assert all(target["active_seed_orbit_match_count"] > 0 for target in probe)
    assert all(
        target["active_seed_orbit_match_count"] == 0 for target in residual
    )
    assert all(target["strong_lightweight_survivor"] for target in targets)
    assert len(
        {target["dihedral_order_sha256"] for target in targets}
    ) == 24


def test_stored_compression_finds_eight_new_exact_small_circuits() -> None:
    payload = artifact_payload()
    rows = payload["run"]["compressed_models"]

    assert payload["configuration"]["trial_budgets_by_model_index"] == [
        32,
        32,
        32,
        64,
        32,
        32,
        32,
        112,
    ]
    assert [row["source_unique_ordered_quad_count"] for row in rows] == [
        197,
        197,
        193,
        194,
        192,
        200,
        191,
        195,
    ]
    assert [row["best_trial"] for row in rows] == [
        20,
        14,
        3,
        56,
        11,
        20,
        4,
        104,
    ]
    assert [row["compressed_unique_ordered_quad_count"] for row in rows] == [
        6,
        6,
        3,
        8,
        4,
        7,
        3,
        4,
    ]
    assert all(row["support_is_exact_positive_circuit"] for row in rows)
    assert all(not row["matches_active_seed_orbit"] for row in rows)
    assert {
        row["affine_clause_orbit"]["canonical_clause_sha256"] for row in rows
    }.isdisjoint(COMPRESSION.active_seed_orbit_hashes(source_payload()))


def test_width_three_residual_two_orbit_is_exact_minimum_new_cover() -> None:
    run = artifact_payload()["run"]
    comparison = run["coverage_comparison"]
    residual_cover = comparison["minimum_affine_source_covers"][
        "residual_targets"
    ]

    assert comparison["active_seed_covered_target_count"] == 16
    assert comparison["active_seed_uncovered_target_ids"] == [
        f"residual:{index}" for index in range(8)
    ]
    assert comparison["compressed_affine_covered_target_count"] == 8
    assert comparison["new_marginal_target_ids"] == [
        f"residual:{index}" for index in range(8)
    ]
    assert comparison["combined_seed_covered_target_count"] == 24
    assert comparison["combined_seed_uncovered_target_ids"] == []
    assert residual_cover == {
        "status": "EXACT_MINIMUM_AFFINE_SOURCE_COVER_FOUND",
        "target_ids": [f"residual:{index}" for index in range(8)],
        "target_count": 8,
        "coverable_target_count": 8,
        "uncovered_target_ids": [],
        "minimum_source_count": 1,
        "minimum_total_width": 3,
        "selected_source_target_ids": ["residual:2"],
    }
    assert run["stopping_assessment"][
        "minimum_residual_cover_sources_are_new_and_small"
    ]
    assert run["decision"] == (
        "ADD_MINIMUM_COMPRESSED_RESIDUAL_COVER_BEFORE_NEXT_C25_ORDER_SEARCH"
    )


def test_stored_persistent_residual_compression_replays_exactly() -> None:
    assert COMPRESSION.check_payload(artifact_payload()) == {
        "status": "OK",
        "verified_target_orders": 24,
        "verified_compressed_exact_certificates": 8,
        "verified_exact_affine_certificate_images": 200,
        "verified_direct_cross_coverage_edges": 22,
        "verified_affine_cross_coverage_edges": 54,
        "new_marginal_target_count": 8,
        "minimum_residual_cover_source_count": 1,
        "decision": (
            "ADD_MINIMUM_COMPRESSED_RESIDUAL_COVER_BEFORE_NEXT_C25_ORDER_SEARCH"
        ),
    }


def test_checker_rejects_fabricated_search_provenance() -> None:
    mutated = copy.deepcopy(artifact_payload())
    mutated["run"]["compressed_models"][0]["best_trial"] = -999

    with pytest.raises(
        AssertionError,
        match="persistent compression best trial drifted",
    ):
        COMPRESSION.check_payload(mutated)
