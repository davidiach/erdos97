from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_n9_base_apex_escape_budget import (
    DEFAULT_ARTIFACT,
    load_artifact,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_escape_budget_artifact_passes_independent_checker() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)

    assert errors == []


def test_escape_budget_checker_summary_is_nonclaiming() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert summary["ok"] is True
    assert summary["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert summary["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert summary["strict_minimum_relevant_deficit_count_to_spoil"] == 3
    assert summary["conservative_minimum_relevant_deficit_count_to_spoil"] == 2
    assert summary["strict_minimum_escape_motif_class_count"] == 8
    assert summary["conservative_minimum_escape_motif_class_count"] == 6


def test_escape_budget_checker_rejects_tampered_escape_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["strict_positive_threshold"]["budget_rows"][3][
        "escaping_labelled_relevant_placement_count_by_relevant_deficit"
    ]["3"] = 109

    errors = validate_payload(payload)

    assert any("strict_positive_threshold" in error for error in errors)


def test_escape_budget_checker_rejects_unknown_top_level_key() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["unchecked_schema_drift"] = {"ok": False}

    errors = validate_payload(payload)

    assert any("top-level keys" in error for error in errors)


def test_escape_budget_checker_rejects_tampered_provenance_command() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["provenance"]["command"] = "python scripts/explore_n9_base_apex.py --escape-budget-report"

    errors = validate_payload(payload)

    assert any("provenance" in error for error in errors)


def test_escape_budget_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_base_apex_escape_budget.py",
            "--check",
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
    assert payload["strict_minimum_relevant_deficit_count_to_spoil"] == 3
