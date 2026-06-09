from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_outside_pair_escape_partition import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_CONNECTOR_CONTRACT,
    DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    SCAN_STATUS,
    assert_expected_escape_partition,
    build_escape_partition_payload,
    load_artifact,
    summary_payload,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_full_neighborhood() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_FULL_NEIGHBORHOOD)


@pytest.fixture(scope="module")
def source_connector_contract() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_CONNECTOR_CONTRACT)


def test_151_6_outside_pair_escape_partition_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_escape_partition(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_ESCAPE_PARTITION_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert payload["summary"] == {
        "basic_filter_complete_assignment_count": 28,
        "basic_filter_complete_assignment_count_by_partition": {
            "endpoint8_connector_available": 9,
            "mixed_private_and_endpoint8": 7,
            "private_halo_only_connector_avoiding": 12,
        },
        "basic_filter_non_original_row6_assignment_count": 21,
        "bootstrap_core_witnesses": [0],
        "connector_available_basic_survivor_count": 16,
        "connector_available_target_row_count": 9,
        "connector_available_vertex_circle_survivor_count": 0,
        "connector_avoiding_basic_survivor_count": 12,
        "connector_avoiding_support_pairs": [[3, 5]],
        "connector_avoiding_target_row_count": 4,
        "connector_avoiding_vertex_circle_survivor_count": 0,
        "connector_forcing_support_pairs": [[3, 8], [5, 8]],
        "cyclic_order": list(range(9)),
        "empty_domain_count": 7097,
        "original_target_center_class": [0, 3, 5, 8],
        "outside_support_pairs": [[3, 5], [3, 8], [5, 8]],
        "remaining_gap": (
            "The private-halo-only connector-avoiding family survives basic "
            "filters, so the remaining proof-facing task is support existence "
            "and row/rich-class forcing. This artifact does not prove pair "
            "[3,5] impossible, does not prove an endpoint-8 support is forced, "
            "and does not promote the review-pending n=9 checker."
        ),
        "scan_status": SCAN_STATUS,
        "search_node_count": 13439,
        "source_record_ids": [151],
        "target_center": 6,
        "target_center_candidate_count": 13,
        "target_row_count_by_partition": {
            "endpoint8_connector_available": 8,
            "mixed_private_and_endpoint8": 1,
            "private_halo_only_connector_avoiding": 4,
        },
        "target_row_key": "151:6",
        "target_row_keys_by_partition": {
            "endpoint8_connector_available": [
                "0,1,3,8",
                "0,1,5,8",
                "0,2,3,8",
                "0,2,5,8",
                "0,3,4,8",
                "0,3,7,8",
                "0,4,5,8",
                "0,5,7,8",
            ],
            "mixed_private_and_endpoint8": ["0,3,5,8"],
            "private_halo_only_connector_avoiding": [
                "0,1,3,5",
                "0,2,3,5",
                "0,3,4,5",
                "0,3,5,7",
            ],
        },
        "vertex_circle_status_counts": {"self_edge": 20, "strict_cycle": 8},
        "vertex_circle_status_counts_by_partition": {
            "endpoint8_connector_available": {"self_edge": 7, "strict_cycle": 2},
            "mixed_private_and_endpoint8": {"self_edge": 3, "strict_cycle": 4},
            "private_halo_only_connector_avoiding": {
                "self_edge": 10,
                "strict_cycle": 2,
            },
        },
        "vertex_circle_surviving_assignment_count": 0,
        "vertex_circle_surviving_assignment_count_by_partition": {
            "endpoint8_connector_available": 0,
            "mixed_private_and_endpoint8": 0,
            "private_halo_only_connector_avoiding": 0,
        },
    }
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "does not prove outside-pair support existence",
        "does not prove row forcing",
        "does not prove the private-halo-only pair is impossible",
        "does not prove n=9",
        "does not prove the bridge",
        "not a counterexample",
        "not a global status update",
    ):
        assert phrase in claim_scope


def test_151_6_outside_pair_escape_partition_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    by_key = {
        record["target_center_class_key"]: record
        for record in payload["target_row_partition"]
    }

    assert by_key["0,3,5,7"]["partition"] == (
        "private_halo_only_connector_avoiding"
    )
    assert by_key["0,3,5,7"]["support_pairs_present"] == [[3, 5]]
    assert by_key["0,3,5,7"]["basic_filter_complete_assignment_count"] == 12
    assert by_key["0,3,5,7"]["vertex_circle_status_counts"] == {
        "self_edge": 10,
        "strict_cycle": 2,
    }

    assert by_key["0,2,5,8"]["partition"] == "endpoint8_connector_available"
    assert by_key["0,2,5,8"]["contains_endpoint8"] is True
    assert by_key["0,2,5,8"]["support_pairs_present"] == [[5, 8]]
    assert by_key["0,2,5,8"]["basic_filter_complete_assignment_count"] == 3

    assert by_key["0,3,5,8"]["partition"] == "mixed_private_and_endpoint8"
    assert by_key["0,3,5,8"]["target_center_class_is_original"] is True
    assert by_key["0,3,5,8"]["support_pairs_present"] == [
        [3, 5],
        [3, 8],
        [5, 8],
    ]
    assert by_key["0,3,5,8"]["basic_filter_complete_assignment_count"] == 7
    assert by_key["0,3,5,8"]["vertex_circle_status_counts"] == {
        "self_edge": 3,
        "strict_cycle": 4,
    }


def test_151_6_outside_pair_escape_partition_rejects_tampered_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["summary"]["connector_avoiding_basic_survivor_count"] = 11

    errors = validate_payload(payload, recompute=False)

    assert any("connector_avoiding_basic_survivor_count" in error for error in errors)


def test_151_6_outside_pair_escape_partition_rejects_tampered_status_sum() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["target_row_partition"][8]["vertex_circle_status_counts"]["self_edge"] = 9

    errors = validate_payload(payload, recompute=False)

    assert any("status counts do not sum" in error for error in errors)


def test_151_6_outside_pair_escape_partition_rejects_source_drift(
    source_full_neighborhood: dict[str, object],
    source_connector_contract: dict[str, object],
) -> None:
    tampered = json.loads(json.dumps(source_connector_contract))
    tampered["summary"]["connector_avoiding_support_pairs"] = []

    with pytest.raises(AssertionError, match="connector_avoiding_support_pairs"):
        build_escape_partition_payload(source_full_neighborhood, tampered)


def test_151_6_outside_pair_escape_partition_artifact_matches_generator(
    source_full_neighborhood: dict[str, object],
    source_connector_contract: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_escape_partition_payload(
        source_full_neighborhood,
        source_connector_contract,
    )


def test_151_6_outside_pair_escape_partition_checker_passes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["target_center_candidate_count"] == 13
    assert summary["connector_avoiding_basic_survivor_count"] == 12
    assert summary["connector_available_basic_survivor_count"] == 16


def test_151_6_outside_pair_escape_partition_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_outside_pair_escape_partition.py",
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
    assert payload["connector_avoiding_basic_survivor_count"] == 12
