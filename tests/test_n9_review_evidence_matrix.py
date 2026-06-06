from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from scripts.check_n9_candidate_review_manifest import load_manifest
from scripts.check_n9_review_evidence_matrix import (
    _check_json_expectations,
    _check_text_expectations,
    load_matrix,
    validate_matrix,
)
from scripts.check_n9_review_gate_ledger import load_ledger


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "metadata" / "n9_review_evidence_matrix.yaml"
MANIFEST = ROOT / "metadata" / "n9_candidate_review.yaml"
LEDGER = ROOT / "metadata" / "n9_review_gate_ledger.yaml"


def _manifest_command_ids() -> set[str]:
    payload = load_manifest(MANIFEST)
    ids: set[str] = set()
    for route in payload["routes"]:
        for command in route["commands"]:
            ids.add(command["id"])
    return ids


def test_n9_review_evidence_matrix_is_valid() -> None:
    payload = load_matrix(MATRIX)

    errors = validate_matrix(payload)

    assert errors == []


def test_n9_review_evidence_matrix_covers_manifest_commands() -> None:
    payload = load_matrix(MATRIX)
    record_command_ids = {
        record["command_id"] for record in payload["evidence_records"]
    }

    assert record_command_ids == _manifest_command_ids()


def test_n9_review_evidence_matrix_rejects_missing_manifest_command() -> None:
    payload = deepcopy(load_matrix(MATRIX))
    payload["evidence_records"] = [
        record
        for record in payload["evidence_records"]
        if record["command_id"] != "n9_turn_inequality_frontier"
    ]

    errors = validate_matrix(payload)

    assert "manifest command 'n9_turn_inequality_frontier' is not covered by matrix" in errors


def test_n9_review_evidence_matrix_rejects_unknown_gate_link() -> None:
    payload = deepcopy(load_matrix(MATRIX))
    payload["evidence_records"][5]["ledger_gate_ids"].append("missing_gate")

    errors = validate_matrix(payload)

    assert any("unknown gate 'missing_gate'" in error for error in errors)


def test_n9_review_evidence_matrix_rejects_manifest_without_pointer() -> None:
    payload = load_matrix(MATRIX)
    manifest = deepcopy(load_manifest(MANIFEST))
    manifest.pop("review_evidence_matrix")

    errors = validate_matrix(
        payload,
        candidate_manifest=manifest,
        gate_ledger=load_ledger(LEDGER),
    )

    assert (
        "candidate manifest must reference metadata/n9_review_evidence_matrix.yaml"
        in errors
    )


def test_n9_review_evidence_matrix_checks_json_expectations() -> None:
    errors = _check_json_expectations(
        {"outer": {"count": 184, "status": "passed"}},
        [
            {"path": "outer.count", "equals": 184},
            {"path": "outer.status", "contains": "pass"},
        ],
        label="sample",
    )

    assert errors == []


def test_n9_review_evidence_matrix_reports_json_expectation_mismatch() -> None:
    errors = _check_json_expectations(
        {"outer": {"count": 183}},
        [{"path": "outer.count", "equals": 184}],
        label="sample",
    )

    assert any("expected 'outer.count' == 184" in error for error in errors)


def test_n9_review_evidence_matrix_checks_text_expectations() -> None:
    errors = _check_text_expectations(
        "lake not found; skipped Lean compilation",
        [{"contains_any": ["checked", "lake not found; skipped Lean compilation"]}],
        label="lean_files",
    )

    assert errors == []
