from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (
    CATALOG_STATUS,
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    DEFAULT_SOURCE_PREFLIGHT,
    assert_expected_private_lane_core_catalog,
    build_private_lane_core_catalog_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_full_neighborhood() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_FULL_NEIGHBORHOOD)


@pytest.fixture(scope="module")
def source_preflight() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_PREFLIGHT)


def test_private_lane_core_catalog_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_private_lane_core_catalog(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_PRIVATE_LANE_CORE_CATALOG_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "does not prove outside-pair support existence",
        "does not prove row forcing",
        "does not prove pair [3,5] impossible",
        "does not prove endpoint-8 forcing",
        "does not prove n=9",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_private_lane_core_catalog_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["source_private_lane_survivor_count"] == 12
    assert summary["source_vertex_circle_status_counts"] == {
        "self_edge": 10,
        "strict_cycle": 2,
    }
    assert summary["all_minimal_core_occurrence_count"] == 282
    assert summary["all_minimal_core_size_counts"] == {
        "3": 124,
        "4": 144,
        "5": 14,
    }
    assert summary["row6_minimal_core_occurrence_count"] == 118
    assert summary["row6_minimal_core_size_counts"] == {
        "3": 48,
        "4": 64,
        "5": 6,
    }
    assert summary["assignments_with_row6_three_row_core"] == 12
    assert summary["chosen_row6_core_status_counts"] == {"strict_cycle": 12}
    assert summary["chosen_distinct_exact_core_count"] == 10
    assert summary["catalog_status"] == CATALOG_STATUS


def test_private_lane_core_catalog_records_are_row6_strict_cycles() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["catalog_records"]

    assert len(records) == 12
    for index, record in enumerate(records):
        assert record["assignment_index"] == index
        assert record["chosen_core_status"] == "strict_cycle"
        assert len(record["chosen_core_centers"]) == 3
        assert 6 in record["chosen_core_centers"]
        assert record["chosen_core_self_edge_count"] == 0
        assert record["chosen_core_cycle_edge_count"] > 0
        row6 = [
            row for row in record["chosen_core_rows"] if row["center"] == 6
        ]
        assert row6 == [{"center": 6, "witnesses": [0, 3, 5, 7]}]


def test_private_lane_core_catalog_artifact_matches_generator(
    source_full_neighborhood: dict[str, object],
    source_preflight: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_private_lane_core_catalog_payload(
        source_full_neighborhood,
        source_preflight,
    )


def test_private_lane_core_catalog_rejects_tampered_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["summary"]["assignments_with_row6_three_row_core"] = 11

    errors = validate_payload(payload, recompute=False)

    assert any("assignments_with_row6_three_row_core" in error for error in errors)


def test_private_lane_core_catalog_rejects_source_drift(
    source_full_neighborhood: dict[str, object],
    source_preflight: dict[str, object],
) -> None:
    tampered = json.loads(json.dumps(source_full_neighborhood))
    for record in tampered["per_target_center_class"]:
        if record["target_center_class"] == [0, 3, 5, 7]:
            record["basic_filter_complete_assignment_count"] = 11
            break

    with pytest.raises(AssertionError, match="private target-center class"):
        build_private_lane_core_catalog_payload(tampered, source_preflight)


def test_private_lane_core_catalog_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_private_lane_core_catalog.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["target_row_key"] == "151:6"
    assert payload["source_private_lane_survivor_count"] == 12
    assert payload["assignments_with_row6_three_row_core"] == 12
