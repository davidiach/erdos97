from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from scripts.check_n9_vertex_circle_input_audit import (
    DEFAULT_ARTIFACT,
    EXPECTED_CROSS_FULL,
    EXPECTED_MAIN_FULL,
    EXPECTED_ROW0_CHOICES,
    assert_expected_input_audit,
    expected_row0_records,
    load_artifact,
    n9_vertex_circle_input_audit_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def _payload() -> dict[str, object]:
    return load_artifact(DEFAULT_ARTIFACT)


def test_expected_row0_records_are_direct_lexicographic_combinations() -> None:
    records = expected_row0_records()

    assert len(records) == EXPECTED_ROW0_CHOICES
    assert records[0] == {
        "row0_index": 0,
        "row0_witnesses": [1, 2, 3, 4],
        "row0_mask": 30,
    }
    assert records[34] == {
        "row0_index": 34,
        "row0_witnesses": [1, 6, 7, 8],
        "row0_mask": 450,
    }
    assert records[-1] == {
        "row0_index": 69,
        "row0_witnesses": [5, 6, 7, 8],
        "row0_mask": 480,
    }


def test_n9_vertex_circle_input_audit_expected_counts_and_scope() -> None:
    payload = n9_vertex_circle_input_audit_payload(_payload())

    assert_expected_input_audit(payload)
    assert payload["validation_status"] == "passed"
    assert payload["review_independence"] == {
        "uses_exhaustive_brancher": False,
        "uses_vertex_circle_replay": False,
        "method": (
            "Recomputes row0 options directly as the 70 lexicographic "
            "4-subsets of labels 1..8, then checks the stored JSON "
            "witness lists, masks, and count arithmetic."
        ),
    }
    assert payload["coverage_summary"] == {
        "expected_row0_choices": EXPECTED_ROW0_CHOICES,
        "row0_choice_count_expected": EXPECTED_ROW0_CHOICES,
        "row0_witnesses_match_lexicographic_combinations": True,
        "row0_masks_match_witnesses": True,
        "main_row0_choices": EXPECTED_ROW0_CHOICES,
        "cross_check_row0_choices": EXPECTED_ROW0_CHOICES,
        "main_full_assignments": EXPECTED_MAIN_FULL,
        "cross_check_full_assignments": EXPECTED_CROSS_FULL,
        "cross_check_status_total": EXPECTED_CROSS_FULL,
    }
    assert "does not rerun the brancher" in payload["claim_scope"]
    assert "does not prove n=9" in payload["claim_scope"]
    assert "does not claim a counterexample" in payload["claim_scope"]


def test_n9_vertex_circle_input_audit_rejects_row0_witness_drift() -> None:
    artifact = copy.deepcopy(_payload())
    artifact["row0_witnesses"][34] = [1, 6, 7, 9]  # type: ignore[index]

    payload = n9_vertex_circle_input_audit_payload(artifact)

    assert payload["validation_status"] == "failed"
    assert any(error.startswith("row0_witnesses mismatch") for error in payload["validation_errors"])
    assert payload["coverage_summary"]["row0_witnesses_match_lexicographic_combinations"] is False


def test_n9_vertex_circle_input_audit_rejects_row0_mask_drift() -> None:
    artifact = copy.deepcopy(_payload())
    artifact["row0_masks"][34] = 999  # type: ignore[index]

    payload = n9_vertex_circle_input_audit_payload(artifact)

    assert payload["validation_status"] == "failed"
    assert any(error.startswith("row0_masks mismatch") for error in payload["validation_errors"])
    assert payload["coverage_summary"]["row0_masks_match_witnesses"] is False


def test_n9_vertex_circle_input_audit_rejects_count_drift() -> None:
    artifact = copy.deepcopy(_payload())
    artifact["cross_check_without_vertex_circle_pruning"]["counts"]["self_edge"] += 1  # type: ignore[index]

    payload = n9_vertex_circle_input_audit_payload(artifact)

    assert payload["validation_status"] == "failed"
    assert "cross counts mismatch" in "\n".join(payload["validation_errors"])
    assert "cross status total mismatch: 185 != 184" in payload["validation_errors"]


def test_n9_vertex_circle_input_audit_rejects_scope_drift() -> None:
    artifact = copy.deepcopy(_payload())
    artifact["notes"] = []  # type: ignore[index]

    payload = n9_vertex_circle_input_audit_payload(artifact)

    assert payload["validation_status"] == "failed"
    assert any("source artifact scope/notes missing" in error for error in payload["validation_errors"])


def test_n9_vertex_circle_input_audit_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_input_audit.py",
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
    assert parsed["coverage_summary"]["row0_choice_count_expected"] == 70
    assert parsed["coverage_summary"]["main_full_assignments"] == 0
