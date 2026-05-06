from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_n9_base_apex_low_excess_ledgers import (
    DEFAULT_ARTIFACT,
    load_artifact,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_low_excess_ledger_artifact_passes_independent_checker() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)

    assert errors == []


def test_low_excess_ledger_checker_summary_is_nonclaiming() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert summary["ok"] is True
    assert summary["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert summary["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert summary["strict_unresolved_profile_ledger_count"] == 30
    assert summary["strict_minimum_escape_motif_class_count"] == 8
    assert summary["conservative_minimum_escape_motif_class_count"] == 6


def test_low_excess_ledger_checker_rejects_tampered_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["strict_unresolved_profile_ledger_count"] = 31

    errors = validate_payload(payload)

    assert any("strict_unresolved_profile_ledger_count" in error for error in errors)


def test_low_excess_ledger_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_base_apex_low_excess_ledgers.py",
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
    assert payload["strict_unresolved_profile_ledger_count"] == 30
