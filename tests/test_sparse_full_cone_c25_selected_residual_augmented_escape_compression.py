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
    / "compress_sparse_full_cone_c25_selected_residual_augmented_escapes.py"
)
SPEC = importlib.util.spec_from_file_location(
    "sparse_full_cone_c25_selected_residual_augmented_escape_compression",
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
    / "sparse_full_cone_c25_selected_residual_augmented_cegar_2026-07-30"
    / "summary.json"
)
ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_selected_residual_augmented_escape_compression_2026-07-30"
    / "summary.json"
)


def source_payload() -> dict[str, object]:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def artifact_payload() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_target_packet_preserves_parent_and_selected_seed_roles() -> None:
    targets = COMPRESSION.target_orders(source_payload())
    probe = [target for target in targets if target["stream"] == "probe"]
    residual = [
        target for target in targets if target["stream"] == "residual"
    ]

    assert len(targets) == 24
    assert len(probe) == 16
    assert len(residual) == 8
    assert all(target["parent_seed_orbit_match_count"] > 0 for target in probe)
    assert sum(
        target["selected_width3_seed_orbit_match_count"] > 0
        for target in probe
    ) == 4
    assert all(target["active_seed_orbit_match_count"] == 0 for target in residual)
    assert all(target["strong_lightweight_survivor"] for target in targets)
    assert len(
        {target["dihedral_order_sha256"] for target in targets}
    ) == 24


def test_stored_compression_finds_eight_new_exact_small_circuits() -> None:
    payload = artifact_payload()
    rows = payload["run"]["compressed_models"]

    assert payload["configuration"]["trial_budgets_by_model_index"] == [
        64,
        64,
        112,
        112,
        112,
        32,
        32,
        64,
    ]
    assert [row["source_unique_ordered_quad_count"] for row in rows] == [
        219,
        220,
        214,
        216,
        211,
        217,
        219,
        210,
    ]
    assert [row["best_trial"] for row in rows] == [
        50,
        47,
        77,
        65,
        67,
        5,
        24,
        37,
    ]
    assert [row["compressed_unique_ordered_quad_count"] for row in rows] == [
        7,
        6,
        4,
        4,
        9,
        6,
        4,
        3,
    ]
    assert all(row["support_is_exact_positive_circuit"] for row in rows)
    assert all(not row["matches_active_seed_orbit"] for row in rows)
    assert {
        row["affine_clause_orbit"]["canonical_clause_sha256"] for row in rows
    }.isdisjoint(COMPRESSION.active_seed_orbit_hashes(source_payload()))


def test_width_four_residual_two_replaces_nonmarginal_old_width_three() -> None:
    run = artifact_payload()["run"]
    comparison = run["coverage_comparison"]
    residual_cover = comparison["minimum_affine_source_covers"][
        "residual_targets"
    ]

    assert comparison["parent_seed_covered_target_count"] == 16
    assert comparison["selected_width3_seed_covered_target_count"] == 4
    assert comparison["selected_width3_marginal_over_parent_target_ids"] == []
    assert comparison["active_seed_covered_target_count"] == 16
    assert comparison["compressed_affine_covered_target_count"] == 20
    assert comparison["parent_plus_compressed_covered_target_count"] == 24
    assert comparison["parent_plus_compressed_uncovered_target_ids"] == []
    assert residual_cover == {
        "status": "EXACT_MINIMUM_AFFINE_SOURCE_COVER_FOUND",
        "target_ids": [f"residual:{index}" for index in range(8)],
        "target_count": 8,
        "coverable_target_count": 8,
        "uncovered_target_ids": [],
        "minimum_source_count": 1,
        "minimum_total_width": 4,
        "selected_source_target_ids": ["residual:2"],
    }
    assert run["stopping_assessment"]["retire_selected_width3_seed"]
    assert run["decision"] == (
        "REPLACE_NONMARGINAL_WIDTH3_WITH_MINIMUM_COMPRESSED_ESCAPE_COVER"
    )


def test_stored_selected_residual_escape_compression_replays_exactly() -> None:
    assert COMPRESSION.check_payload(artifact_payload()) == {
        "status": "OK",
        "verified_target_orders": 24,
        "verified_compressed_exact_certificates": 8,
        "verified_exact_affine_certificate_images": 200,
        "verified_direct_cross_coverage_edges": 31,
        "verified_affine_cross_coverage_edges": 129,
        "selected_width3_marginal_target_count": 0,
        "minimum_residual_cover_source_count": 1,
        "decision": (
            "REPLACE_NONMARGINAL_WIDTH3_WITH_MINIMUM_COMPRESSED_ESCAPE_COVER"
        ),
    }
