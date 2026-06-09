from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_private_lane_strict_core_split import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_CORE_CATALOG,
    DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    SPLIT_STATUS,
    assert_expected_private_lane_strict_core_split,
    build_private_lane_strict_core_split_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_full_neighborhood() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_FULL_NEIGHBORHOOD)


@pytest.fixture(scope="module")
def source_core_catalog() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_CORE_CATALOG)


def test_private_lane_strict_core_split_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_private_lane_strict_core_split(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_PRIVATE_LANE_STRICT_CORE_SPLIT_DIAGNOSTIC_ONLY"
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


def test_private_lane_strict_core_split_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["source_private_lane_survivor_count"] == 12
    assert summary["row6_three_row_strict_core_count"] == 44
    assert summary["assignments_with_row6_three_row_strict_core"] == 12
    assert summary["label8_visible_core_count"] == 32
    assert summary["label8_free_core_count"] == 12
    assert summary["assignments_with_label8_visible_core"] == 12
    assert summary["assignments_with_label8_free_core"] == 8
    assert summary["assignments_without_label8_free_core"] == 4
    assert summary["label8_free_distinct_exact_core_count"] == 10
    assert summary["split_status"] == SPLIT_STATUS


def test_private_lane_strict_core_split_records_are_consistent() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["assignment_records"]

    assert len(records) == 12
    visible_total = 0
    free_total = 0
    assignments_with_free = 0
    for index, record in enumerate(records):
        assert record["assignment_index"] == index
        assert record["row6_three_row_strict_core_count"] == len(record["cores"])
        assert record["label8_visible_core_count"] > 0
        visible_total += record["label8_visible_core_count"]
        free_total += record["label8_free_core_count"]
        if record["label8_free_core_count"] > 0:
            assignments_with_free += 1
        for core in record["cores"]:
            assert len(core["centers"]) == 3
            assert 6 in core["centers"]
            assert core["cycle_edge_count"] > 0
            assert core["strict_edge_count"] > 0
            assert core["label8_visible"] == any(
                8 in row["witnesses"] and row["center"] != 6
                for row in core["rows"]
            )

    assert visible_total == 32
    assert free_total == 12
    assert assignments_with_free == 8


def test_private_lane_strict_core_split_label8_free_signatures() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    signatures = payload["label8_free_core_signatures"]

    assert len(signatures) == 10
    assert sum(signature["multiplicity"] for signature in signatures) == 12
    for signature in signatures:
        assert signature["multiplicity"] > 0
        assert len(signature["rows"]) == 3
        assert any(row["center"] == 6 for row in signature["rows"])
        assert all(8 not in row["witnesses"] for row in signature["rows"])


def test_private_lane_strict_core_split_artifact_matches_generator(
    source_full_neighborhood: dict[str, object],
    source_core_catalog: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_private_lane_strict_core_split_payload(
        source_full_neighborhood,
        source_core_catalog,
    )


def test_private_lane_strict_core_split_rejects_tampered_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["summary"]["label8_free_core_count"] = 11

    errors = validate_payload(payload, recompute=False)

    assert any("label8_free_core_count" in error for error in errors)


def test_private_lane_strict_core_split_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_private_lane_strict_core_split.py",
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
    assert payload["row6_three_row_strict_core_count"] == 44
    assert payload["label8_visible_core_count"] == 32
    assert payload["label8_free_core_count"] == 12
