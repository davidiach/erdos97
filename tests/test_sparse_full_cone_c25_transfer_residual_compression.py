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
    / "compress_sparse_full_cone_c25_transfer_residuals.py"
)
SPEC = importlib.util.spec_from_file_location(
    "sparse_full_cone_c25_transfer_residual_compression",
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
    / "sparse_full_cone_c25_transfer_cegar_2026-07-29"
    / "summary.json"
)
ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_transfer_residual_compression_2026-07-29"
    / "summary.json"
)


def source_payload() -> dict[str, object]:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def artifact_payload() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_residual_target_packet_has_16_probe_and_8_seeded_orders() -> None:
    targets = COMPRESSION.target_orders(source_payload())

    assert len(targets) == 24
    assert sum(target["stream"] == "probe" for target in targets) == 16
    assert sum(target["stream"] == "seeded" for target in targets) == 8
    assert [
        target["target_id"]
        for target in targets
        if target["stream"] == "probe"
        and target["transferred_seed_orbit_match_count"] == 0
    ] == ["probe:0", "probe:1"]


def test_stored_residual_compression_finds_eight_new_small_orbits() -> None:
    rows = artifact_payload()["run"]["compressed_models"]

    assert [row["source_unique_ordered_quad_count"] for row in rows] == [
        199,
        190,
        200,
        193,
        194,
        197,
        191,
        199,
    ]
    assert [row["compressed_unique_ordered_quad_count"] for row in rows] == [
        7,
        9,
        5,
        3,
        7,
        4,
        6,
        4,
    ]
    assert all(not row["matches_active_transferred_seed_orbit"] for row in rows)
    assert {
        row["affine_clause_orbit"]["canonical_clause_sha256"] for row in rows
    }.isdisjoint(COMPRESSION.active_seed_orbit_hashes(source_payload()))


def test_width_three_orbit_is_exact_minimum_residual_cover() -> None:
    run = artifact_payload()["run"]
    covers = run["minimum_affine_source_covers"]

    assert covers["residual_targets"] == {
        "status": "EXACT_MINIMUM_AFFINE_SOURCE_COVER_FOUND",
        "target_ids": [f"seeded:{index}" for index in range(8)],
        "target_count": 8,
        "coverable_target_count": 8,
        "uncovered_target_ids": [],
        "minimum_source_count": 1,
        "minimum_total_width": 3,
        "selected_source_target_ids": ["seeded:3"],
    }
    assert covers["all_probe_and_residual_targets"]["coverable_target_count"] == 22
    assert covers["all_probe_and_residual_targets"]["uncovered_target_ids"] == [
        "probe:0",
        "probe:1",
    ]
    assert (
        run["coverage_by_stream"][
            "compressed_affine_covered_seed_uncovered_probe_target_ids"
        ]
        == []
    )


def test_stored_c25_residual_compression_replays_exactly() -> None:
    result = COMPRESSION.check_payload(artifact_payload())

    assert result == {
        "status": "OK",
        "verified_target_orders": 24,
        "verified_compressed_exact_certificates": 8,
        "verified_exact_affine_certificate_images": 200,
        "verified_direct_cross_coverage_edges": 16,
        "verified_affine_cross_coverage_edges": 150,
        "small_or_reusable_source_count": 8,
        "decision": "CONTINUE_C25_CLAUSE_EXPANSION_WITH_COMPRESSED_RESIDUALS",
    }


def test_checker_rejects_duplicate_residual_source_model() -> None:
    payload = artifact_payload()
    mutated = copy.deepcopy(payload)
    rows = mutated["run"]["compressed_models"]
    rows[1] = copy.deepcopy(rows[0])

    with pytest.raises(AssertionError, match="duplicate residual source model index"):
        COMPRESSION.check_payload(mutated)


def test_checker_rejects_fabricated_search_provenance() -> None:
    payload = artifact_payload()
    mutated = copy.deepcopy(payload)
    row = mutated["run"]["compressed_models"][0]
    row["best_trial"] = -999

    with pytest.raises(AssertionError, match="best trial drifted"):
        COMPRESSION.check_payload(mutated)