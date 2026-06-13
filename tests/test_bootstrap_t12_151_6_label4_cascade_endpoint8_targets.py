from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_cascade_endpoint8_targets import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_CASCADE_ROW_CRITICALITY,
    ENDPOINT_TRIPLE,
    TARGET_STATUS,
    assert_expected_cascade_endpoint8_targets,
    build_cascade_endpoint8_targets_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_cascade_row_criticality() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_CASCADE_ROW_CRITICALITY)


def test_label4_cascade_endpoint8_targets_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_cascade_endpoint8_targets(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_LABEL4_CASCADE_ENDPOINT8_TARGETS_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "rich class on center 8 whose witnesses contain the endpoint triple [0,4,6]",
        "not support existence",
        "not row forcing",
        "not a proof that [3,5] is impossible",
        "not endpoint-8 forcing",
        "not n=9",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_label4_cascade_endpoint8_targets_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["cascade_component_key"] == "D[0,6]=D[4,5]=D[5,6]"
    assert summary["required_core_centers"] == [5, 6, 8]
    assert summary["source_criticality_status"] == (
        "CASCADE_CORES_ARE_THREE_ROW_CRITICAL_FOR_VERTEX_CIRCLE_REPLAY"
    )
    assert summary["endpoint_center"] == 8
    assert summary["endpoint_triple"] == ENDPOINT_TRIPLE
    assert summary["endpoint_extra_label_pool"] == [1, 2, 3, 5, 7]
    assert summary["source_recorded_endpoint_rows"] == [
        [0, 2, 4, 6],
        [0, 4, 6, 7],
        [0, 1, 4, 6],
    ]
    assert summary["source_recorded_endpoint_status_counts"] == {"strict_cycle": 3}
    assert summary["rich_superset_count_per_signature"] == 31
    assert summary["rich_superset_signature_record_count"] == 93
    assert summary["rich_superset_occurrence_record_count"] == 124
    assert summary["rich_superset_obstructed_count"] == 93
    assert summary["rich_superset_status_counts"] == {
        "self_edge": 72,
        "strict_cycle": 21,
    }
    assert summary["rich_superset_occurrence_status_counts"] == {
        "self_edge": 96,
        "strict_cycle": 28,
    }
    assert summary["exact_four_endpoint_rows"] == [
        [0, 1, 4, 6],
        [0, 2, 4, 6],
        [0, 3, 4, 6],
        [0, 4, 5, 6],
        [0, 4, 6, 7],
    ]
    assert summary["exact_four_status_counts"] == {
        "self_edge": 6,
        "strict_cycle": 9,
    }
    assert summary["target_status"] == TARGET_STATUS


def test_label4_cascade_endpoint8_targets_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["cascade_endpoint_records"]

    assert [record["signature_index"] for record in records] == [7, 8, 9]
    assert [record["multiplicity"] for record in records] == [1, 1, 2]
    for record in records:
        assert record["endpoint_center"] == 8
        assert record["endpoint_triple"] == [0, 4, 6]
        assert record["rich_superset_count"] == 31
        assert record["status_counts"] == {"self_edge": 24, "strict_cycle": 7}
        assert record["all_rich_supersets_obstructed"] is True
        assert len(record["variant_records"]) == 31
        assert {
            tuple(variant["center8_witnesses"])
            for variant in record["variant_records"]
            if variant["is_exact_four"]
        } == {
            (0, 1, 4, 6),
            (0, 2, 4, 6),
            (0, 3, 4, 6),
            (0, 4, 5, 6),
            (0, 4, 6, 7),
        }
        assert all(variant["obstructed"] for variant in record["variant_records"])


def test_label4_cascade_endpoint8_targets_artifact_matches_generator(
    source_cascade_row_criticality: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_cascade_endpoint8_targets_payload(
        source_cascade_row_criticality,
    )


def test_label4_cascade_endpoint8_targets_rejects_clean_variant() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["cascade_endpoint_records"][0]["variant_records"][0]["status"] = "ok"
    payload["cascade_endpoint_records"][0]["variant_records"][0][
        "obstructed"
    ] = False

    errors = validate_payload(payload, recompute=False)

    assert any("variant not obstructed" in error for error in errors)


def test_label4_cascade_endpoint8_targets_rejects_missing_triple() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["cascade_endpoint_records"][0]["variant_records"][0][
        "center8_witnesses"
    ] = [0, 1, 2, 6]

    errors = validate_payload(payload, recompute=False)

    assert any("variant misses endpoint triple" in error for error in errors)


def test_label4_cascade_endpoint8_targets_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_cascade_endpoint8_targets.py",
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
    assert payload["endpoint_center"] == 8
    assert payload["endpoint_triple"] == [0, 4, 6]
    assert payload["rich_superset_signature_record_count"] == 93
    assert payload["rich_superset_status_counts"] == {
        "self_edge": 72,
        "strict_cycle": 21,
    }
