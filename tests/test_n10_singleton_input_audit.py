from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n10_singleton_input_audit import (
    CLAIM_SCOPE,
    DEFAULT_ARTIFACT,
    EXPECTED_COUNTS,
    EXPECTED_ROW0_CHOICES,
    EXPECTED_TOTAL_FULL,
    EXPECTED_TOTAL_NODES,
    assert_expected_input_audit,
    expected_row0_records,
    load_artifact,
    n10_singleton_input_audit_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def _payload() -> dict[str, object]:
    return load_artifact(DEFAULT_ARTIFACT)


def test_expected_row0_records_are_direct_lexicographic_combinations() -> None:
    records = expected_row0_records()

    assert len(records) == EXPECTED_ROW0_CHOICES
    assert records[0] == {
        "row0_index": 0,
        "row0_range": [0, 1],
        "row0_witnesses": [1, 2, 3, 4],
        "row0_mask": 30,
    }
    assert records[63] == {
        "row0_index": 63,
        "row0_range": [63, 64],
        "row0_witnesses": [2, 3, 5, 8],
        "row0_mask": 300,
    }
    assert records[-1] == {
        "row0_index": 125,
        "row0_range": [125, 126],
        "row0_witnesses": [6, 7, 8, 9],
        "row0_mask": 960,
    }


def test_n10_singleton_input_audit_expected_counts_and_scope() -> None:
    payload = n10_singleton_input_audit_payload(_payload())

    assert_expected_input_audit(payload)
    assert payload["validation_status"] == "passed"
    assert payload["review_independence"] == {
        "uses_generic_vertex_search": False,
        "uses_search_rerun": False,
        "method": (
            "Recomputes the row0 singleton option list directly as the "
            "126 lexicographic 4-subsets of labels 1..9, then checks the "
            "stored JSON rows and aggregate arithmetic."
        ),
    }
    assert payload["coverage_summary"] == {
        "expected_row0_choices": EXPECTED_ROW0_CHOICES,
        "row_count": EXPECTED_ROW0_CHOICES,
        "row0_ranges_cover_singletons": True,
        "row0_witnesses_match_lexicographic_combinations": True,
        "row0_masks_match_witnesses": True,
        "aborted_any": False,
        "total_nodes_from_rows": EXPECTED_TOTAL_NODES,
        "total_full_from_rows": EXPECTED_TOTAL_FULL,
        "counts_from_rows": EXPECTED_COUNTS,
    }
    assert "does not rerun the search" in payload["claim_scope"]
    assert "does not prove n=10" in payload["claim_scope"]
    assert "does not claim a counterexample" in payload["claim_scope"]


def test_n10_singleton_input_audit_rejects_appended_claim_scope_overclaim() -> None:
    payload = n10_singleton_input_audit_payload(_payload())
    payload["claim_scope"] = f"{CLAIM_SCOPE} This proves n=10."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_input_audit(payload)


def test_n10_singleton_input_audit_rejects_missing_row() -> None:
    artifact = _payload()
    artifact["rows"] = artifact["rows"][:-1]  # type: ignore[index]

    payload = n10_singleton_input_audit_payload(artifact)

    assert payload["validation_status"] == "failed"
    assert "rows length mismatch: 125 != 126" in payload["validation_errors"]
    assert payload["coverage_summary"]["row_count"] == 125
    assert payload["coverage_summary"]["row0_ranges_cover_singletons"] is False


def test_n10_singleton_input_audit_rejects_witness_and_mask_drift() -> None:
    artifact = _payload()
    artifact["rows"][63]["row0_witnesses"] = [2, 3, 5, 9]  # type: ignore[index]
    artifact["rows"][63]["row0_mask"] = 999  # type: ignore[index]
    artifact["row0_witnesses"][63] = [2, 3, 5, 9]  # type: ignore[index]

    payload = n10_singleton_input_audit_payload(artifact)

    assert payload["validation_status"] == "failed"
    assert "row 63 row0_witnesses mismatch: [2, 3, 5, 9] != [2, 3, 5, 8]" in payload[
        "validation_errors"
    ]
    assert "row 63 row0_mask mismatch: 999 != 300" in payload["validation_errors"]
    assert payload["coverage_summary"]["row0_witnesses_match_lexicographic_combinations"] is False
    assert payload["coverage_summary"]["row0_masks_match_witnesses"] is False


def test_n10_singleton_input_audit_rejects_count_drift() -> None:
    artifact = _payload()
    artifact = copy.deepcopy(artifact)
    artifact["rows"][0]["counts"]["partial_self_edge"] += 1  # type: ignore[index]
    artifact["rows"][0]["full"] = 1  # type: ignore[index]

    payload = n10_singleton_input_audit_payload(artifact)

    assert payload["validation_status"] == "failed"
    assert "row 0 full mismatch: 1 != 0" in payload["validation_errors"]
    assert "row-derived total_full mismatch: 1 != 0" in payload["validation_errors"]
    assert any(
        error.startswith("row-derived counts mismatch")
        for error in payload["validation_errors"]
    )


def test_n10_singleton_input_audit_rejects_scope_drift() -> None:
    artifact = _payload()
    artifact["notes"] = []

    payload = n10_singleton_input_audit_payload(artifact)

    assert payload["validation_status"] == "failed"
    assert any("source artifact scope/notes missing" in error for error in payload["validation_errors"])


def test_n10_singleton_input_audit_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n10_singleton_input_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    parsed = json.loads(result.stdout)
    assert parsed["validation_status"] == "passed"
    assert parsed["coverage_summary"]["row_count"] == 126
    assert parsed["coverage_summary"]["total_full_from_rows"] == 0
