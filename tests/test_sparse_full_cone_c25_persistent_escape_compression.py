from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts"
    / "exploration"
    / "compress_sparse_full_cone_c25_persistent_escapes.py"
)
SPEC = importlib.util.spec_from_file_location(
    "sparse_full_cone_c25_persistent_escape_compression",
    SCRIPT,
)
assert SPEC is not None and SPEC.loader is not None
COMPRESSION = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMPRESSION
SPEC.loader.exec_module(COMPRESSION)

ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_persistent_escape_compression_2026-07-30"
    / "summary.json"
)


def artifact_payload() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_stored_target_packet_is_the_complete_current_c25_history() -> None:
    payload = artifact_payload()
    targets = payload["target_orders"]

    assert len(targets) == 144
    assert Counter(target["stream"] for target in targets) == {
        "prior": 24,
        "first_fresh": 32,
        "second_fresh": 32,
        "transfer_cegar_probe": 16,
        "transfer_cegar_residual": 8,
        "augmentation_probe": 32,
    }
    assert len({target["dihedral_order_sha256"] for target in targets}) == 144


def test_stored_sources_compress_to_two_new_exact_small_circuits() -> None:
    payload = artifact_payload()
    rows = payload["compressed_models"]

    assert [row["source_target_id"] for row in rows] == [
        "transfer_cegar_probe:0",
        "transfer_cegar_probe:1",
    ]
    assert [row["source_unique_ordered_quad_count"] for row in rows] == [201, 196]
    assert [row["compressed_unique_ordered_quad_count"] for row in rows] == [4, 5]
    assert [row["best_trial"] for row in rows] == [55, 3]
    assert [row["random_objective_seed"] for row in rows] == [20260730, 20261730]
    assert all(row["support_is_exact_positive_circuit"] for row in rows)
    assert all(not row["matches_existing_seed_orbit"] for row in rows)
    assert [row["affine_clause_orbit"]["affine_map_count"] for row in rows] == [
        25,
        25,
    ]
    assert payload["compression_summary"] == {
        "source_count": 2,
        "source_widths": [201, 196],
        "compressed_widths": [4, 5],
        "exact_improvement_count": 2,
        "minimum_compressed_width": 4,
        "maximum_compressed_width": 5,
        "compressed_width_at_most_threshold_count": 2,
        "existing_seed_orbit_match_count": 0,
    }


def test_width_four_orbit_covers_every_new_marginal_target() -> None:
    payload = artifact_payload()
    rows = payload["compressed_models"]
    comparison = payload["coverage_comparison"]
    marginal = set(comparison["new_marginal_target_ids"])
    width_four_targets = {
        target["target_id"]
        for target in rows[0]["clause_coverage"]["translated_orbit_covered_targets"]
    }
    width_five_targets = {
        target["target_id"]
        for target in rows[1]["clause_coverage"]["translated_orbit_covered_targets"]
    }

    assert len(marginal) == 23
    assert width_four_targets == marginal
    assert len(width_five_targets) == 21
    assert width_five_targets < width_four_targets
    assert comparison["existing_seed_covered_target_count"] == 119
    assert comparison["new_compressed_affine_covered_target_count"] == 23
    assert comparison["combined_seed_covered_target_count"] == 142
    assert comparison["combined_seed_uncovered_target_ids"] == [
        "first_fresh:fresh:0",
        "prior:seeded:0",
    ]


def test_minimum_marginal_cover_selects_only_the_width_four_source() -> None:
    payload = artifact_payload()
    comparison = payload["coverage_comparison"]
    covers = comparison["minimum_affine_source_covers"]

    assert covers["persistent_targets"] == {
        "status": "EXACT_MINIMUM_AFFINE_SOURCE_COVER_FOUND",
        "target_count": 2,
        "coverable_target_count": 2,
        "target_ids": [
            "transfer_cegar_probe:0",
            "transfer_cegar_probe:1",
        ],
        "uncovered_target_ids": [],
        "minimum_source_count": 1,
        "minimum_total_width": 4,
        "selected_source_target_ids": ["transfer_cegar_probe:0"],
    }
    assert covers["new_marginal_targets"]["minimum_source_count"] == 1
    assert covers["new_marginal_targets"]["minimum_total_width"] == 4
    assert covers["new_marginal_targets"]["selected_source_target_ids"] == [
        "transfer_cegar_probe:0"
    ]
    assert payload["decision"] == (
        "ADD_MINIMUM_COMPRESSED_MARGINAL_COVER_BEFORE_C25_ORDER_SEARCH"
    )


def test_stored_persistent_escape_compression_replays_exactly() -> None:
    assert COMPRESSION.check_payload(artifact_payload()) == {
        "status": "OK",
        "verified_target_orders": 144,
        "verified_compressed_exact_certificates": 2,
        "verified_exact_affine_certificate_images": 50,
        "verified_direct_cross_coverage_edges": 2,
        "verified_affine_cross_coverage_edges": 42,
        "new_marginal_target_count": 23,
        "minimum_persistent_cover_source_count": 1,
        "minimum_new_marginal_cover_source_count": 1,
        "decision": (
            "ADD_MINIMUM_COMPRESSED_MARGINAL_COVER_BEFORE_C25_ORDER_SEARCH"
        ),
    }
