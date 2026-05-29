from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_81_3_repeated_support_catalogue_audit import (
    SUMMARY_KEYS,
    summary_json_payload,
)
from erdos97.bootstrap_t12_81_3_repeated_support_catalogue_audit import (
    DEFAULT_ARTIFACT,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_3_repeated_support_catalogue_audit_payload,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_3_repeated_support_catalogue_audit_payload()


def test_bootstrap_t12_81_3_repeated_support_expected_payload(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_81_3_REPEATED_SUPPORT_CATALOGUE_AUDIT_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "one repeated-support layer" in claim_scope
    assert "not a proof of support existence" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope

    summary = payload["summary"]
    assert summary["scan_status"] == SCAN_STATUS
    assert summary["source_prefix_survivor_count"] == 4
    assert summary["repeated_support_candidate_count"] == 5
    assert summary["supply_extension_candidate_count"] == 464
    assert summary["supply_extension_initially_compatible_count"] == 1
    assert summary["supply_extension_survivor_count"] == 0


def test_bootstrap_t12_81_3_repeated_support_shapes(
    payload: dict[str, object],
) -> None:
    repeated_scan = payload["repeated_support_catalogue_scan"]
    repeated_records = repeated_scan["records"]
    assert [
        (
            record["prefix_survivor_index"],
            record["repeated_center"],
            record["repeated_support"],
        )
        for record in repeated_records
    ] == [
        (0, 8, [2, 3, 5, 6]),
        (1, 2, [0, 5, 6, 7]),
        (1, 8, [2, 3, 5, 6]),
        (2, 8, [2, 3, 5, 6]),
        (3, 8, [2, 3, 6, 7]),
    ]

    supply_scan = payload["supply_extension_scan"]
    compatible = supply_scan["initially_compatible_catalogues"]
    assert len(compatible) == 1
    assert compatible[0]["prefix_survivor_index"] == 1
    assert compatible[0]["repeated_center"] == 8
    assert compatible[0]["repeated_support"] == [2, 3, 5, 6]
    assert compatible[0]["center_6_supply_support"] == [2, 4, 7, 8]
    assert compatible[0]["detected_solution_count"] == 0
    assert supply_scan["survivors"] == []


def test_bootstrap_t12_81_3_repeated_support_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_bootstrap_t12_81_3_repeated_support_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["supply_extension_survivor_count"] = 1

    with pytest.raises(AssertionError, match="supply_extension_survivor_count"):
        assert_expected_payload(bad)


def test_bootstrap_t12_81_3_repeated_support_summary_json_payload(
    payload: dict[str, object],
) -> None:
    summary_payload = summary_json_payload(payload)

    assert tuple(summary_payload) == SUMMARY_KEYS
    assert summary_payload["summary"]["supply_extension_candidate_count"] == 464
    assert "repeated_support_catalogue_scan" not in summary_payload
    assert "supply_extension_scan" not in summary_payload


def test_bootstrap_t12_81_3_repeated_support_cli_summary_json(
    payload: dict[str, object],
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_repeated_support_catalogue_audit.py",
            "--check",
            "--assert-expected",
            "--summary-json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stderr == ""
    assert json.loads(result.stdout) == summary_json_payload(payload)
