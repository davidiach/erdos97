from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "scripts" / "exploration" / "compress_sparse_full_cone_fresh_certificates.py"
)
SPEC = importlib.util.spec_from_file_location(
    "sparse_full_cone_fresh_compression",
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
    / "sparse_full_cone_fresh_order_screen_2026-07-29"
    / "summary.json"
)
ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_fresh_compression_2026-07-29"
    / "summary.json"
)


def source_payload() -> dict[str, object]:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def test_fresh_targets_collect_exactly_63_source_orders() -> None:
    targets = [COMPRESSION.fresh_targets(run) for run in source_payload()["runs"]]

    assert [len(rows) for rows in targets] == [31, 32]
    assert sum(len(rows) for rows in targets) == 63
    assert all(
        row["target_id"].startswith("fresh:") for rows in targets for row in rows
    )


def test_compression_model_preserves_exact_source_identity() -> None:
    record = source_payload()["runs"][0]["records"][0]

    model = COMPRESSION.compression_model(record)

    assert model["model_index"] == record["fresh_model_index"]
    assert model["order"] == record["order"]

    assert model["full_kalmanson"]["certificate"] == record["certificate"]


def test_stopping_rule_stops_without_small_or_reusable_circuits() -> None:
    rows = [
        {
            "source_target_id": "fresh:1",
            "compressed_unique_ordered_quad_count": 40,
            "matches_prior_compression_clause_orbit": False,
            "clause_coverage": {
                "direct_cross_target_count": 0,
                "translated_orbit_cross_target_count": 0,
            },
        }
    ]

    assessment = COMPRESSION.stopping_assessment(
        rows,
        small_circuit_max_width=12,
    )

    assert assessment["qualifying_small_or_reusable_source_target_ids"] == []
    assert assessment["decision"] == "STOP_CLUSTER_MINING_AFTER_BOUNDED_NEGATIVE_SCREEN"


def test_stopping_rule_continues_for_new_small_or_affine_reuse() -> None:
    rows = [
        {
            "source_target_id": "fresh:1",
            "compressed_unique_ordered_quad_count": 8,
            "matches_prior_compression_clause_orbit": False,
            "clause_coverage": {
                "direct_cross_target_count": 0,
                "translated_orbit_cross_target_count": 0,
            },
        },
        {
            "source_target_id": "fresh:2",
            "compressed_unique_ordered_quad_count": 40,
            "matches_prior_compression_clause_orbit": False,
            "clause_coverage": {
                "direct_cross_target_count": 0,
                "translated_orbit_cross_target_count": 1,
            },
        },
    ]

    assessment = COMPRESSION.stopping_assessment(
        rows,
        small_circuit_max_width=12,
    )

    assert assessment["new_small_source_target_ids"] == ["fresh:1"]
    assert assessment["affine_reusable_source_target_ids"] == ["fresh:2"]
    assert assessment["decision"] == "CONTINUE_CLUSTER_MINING"


def test_stored_fresh_compression_packet_replays_exactly() -> None:
    if not ARTIFACT.exists():
        return
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    result = COMPRESSION.check_payload(payload)

    assert result == {
        "status": "OK",
        "verified_fresh_target_orders": 63,
        "verified_compressed_exact_certificates": 63,
        "verified_exact_affine_certificate_images": 1703,
        "verified_direct_cross_reuse_edges": 64,
        "verified_affine_cross_reuse_edges": 96,
        "qualifying_small_or_reusable_source_count": 13,
        "cluster_mining_decisions": [
            "CONTINUE_CLUSTER_MINING",
            "CONTINUE_CLUSTER_MINING",
        ],
    }


def test_checker_rejects_duplicate_source_model() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(payload)
    rows = mutated["runs"][0]["compressed_models"]
    rows[1] = copy.deepcopy(rows[0])

    with pytest.raises(AssertionError, match="duplicate source model index"):
        COMPRESSION.check_payload(mutated)