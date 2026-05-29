from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_81_3_repeated_support_saturation_audit import (
    SUMMARY_KEYS,
    summary_json_payload,
)
from erdos97.bootstrap_t12_81_3_repeated_support_saturation_audit import (
    DEFAULT_ARTIFACT,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_3_repeated_support_saturation_audit_payload,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_3_repeated_support_saturation_audit_payload()


def test_bootstrap_t12_81_3_repeated_support_saturation_expected_payload(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_81_3_REPEATED_SUPPORT_SATURATION_AUDIT_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "no three-repeated-support catalogue" in claim_scope
    assert "not a proof of support existence" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope

    summary = payload["summary"]
    assert summary["scan_status"] == SCAN_STATUS
    assert summary["source_prefix_survivor_count"] == 4
    assert summary["unique_catalogue_count_by_repeated_support_count"] == {
        "0": 4,
        "1": 5,
        "2": 1,
        "3": 0,
    }
    assert summary["ordered_generation_path_count_by_repeated_support_count"] == {
        "0": 4,
        "1": 5,
        "2": 2,
        "3": 0,
    }
    assert summary["max_repeated_support_count"] == 2
    assert summary["terminal_catalogue_count"] == 4
    assert summary["three_repeated_support_catalogue_count"] == 0


def test_bootstrap_t12_81_3_repeated_support_saturation_records(
    payload: dict[str, object],
) -> None:
    scan = payload["repeated_support_saturation_scan"]
    records = scan["level_records"]
    assert records["3"] == []
    assert len(records["2"]) == 1
    two_record = records["2"][0]
    assert two_record["prefix_survivor_index"] == 1
    assert two_record["ordered_generation_path_count"] == 2
    assert two_record["repeated_supports"] == [
        {"center": 2, "support": [0, 5, 6, 7], "support_size": 4},
        {"center": 8, "support": [2, 3, 5, 6], "support_size": 4},
    ]
    assert (
        two_record["extension_profile"]["next_repeated_support_candidate_count"] == 0
    )
    assert len(scan["terminal_records"]) == 4
    assert all(
        record["extension_profile"]["next_repeated_support_candidate_count"] == 0
        for record in scan["terminal_records"]
    )


def test_bootstrap_t12_81_3_repeated_support_saturation_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_bootstrap_t12_81_3_repeated_support_saturation_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["three_repeated_support_catalogue_count"] = 1

    with pytest.raises(AssertionError, match="three_repeated_support_catalogue_count"):
        assert_expected_payload(bad)


def test_bootstrap_t12_81_3_repeated_support_saturation_summary_json_payload(
    payload: dict[str, object],
) -> None:
    summary_payload = summary_json_payload(payload)

    assert tuple(summary_payload) == SUMMARY_KEYS
    assert summary_payload["summary"]["three_repeated_support_catalogue_count"] == 0
    assert "repeated_support_saturation_scan" not in summary_payload


def test_bootstrap_t12_81_3_repeated_support_saturation_cli_summary_json(
    payload: dict[str, object],
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_repeated_support_saturation_audit.py",
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
