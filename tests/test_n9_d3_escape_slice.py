from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_d3_escape_slice import d3_escape_slice_report
from scripts.check_n9_d3_escape_slice import (
    DEFAULT_ARTIFACT,
    load_artifact,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_d3_escape_slice_artifact_summary_is_nonclaiming() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a geometric realizability test" in payload["claim_scope"]
    assert payload["total_profile_excess"] == 6
    assert payload["capacity_deficit"] == 3
    assert payload["relevant_deficit_count"] == 3
    assert payload["profile_slice"]["labelled_profile_sequence_count"] == 3003
    assert payload["profile_slice"]["dihedral_profile_orbit_count"] == 185
    assert payload["escape_slice"]["labelled_escape_placement_count"] == 108
    assert payload["escape_slice"]["dihedral_escape_class_count"] == 8
    assert payload["coupled_slice"]["labelled_profile_escape_pair_count"] == 324324
    assert payload["coupled_slice"]["common_dihedral_pair_class_count"] == 18088


def test_d3_escape_slice_records_burnside_orbit_size_counts() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert payload["profile_slice"]["dihedral_profile_orbit_size_counts"] == {
        "18": 150,
        "3": 2,
        "9": 33,
    }
    assert payload["escape_slice"]["dihedral_escape_orbit_size_counts"] == {
        "18": 4,
        "9": 4,
    }
    assert payload["coupled_slice"]["common_dihedral_pair_orbit_size_counts"] == {
        "18": 17948,
        "9": 140,
    }


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_d3_escape_slice_artifact_matches_generator() -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == d3_escape_slice_report()


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_d3_escape_slice_checker_passes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["labelled_profile_sequence_count"] == 3003
    assert summary["common_dihedral_pair_class_count"] == 18088


def test_d3_escape_slice_checker_rejects_tampered_provenance() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["provenance"]["command"] = "python scripts/analyze_n9_d3_escape_slice.py"

    errors = validate_payload(payload, recompute=False)

    assert any("provenance" in error for error in errors)


def test_d3_escape_slice_checker_rejects_unknown_top_level_key() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["unchecked_schema_drift"] = {"ok": False}

    errors = validate_payload(payload, recompute=False)

    assert any("top-level keys" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_d3_escape_slice_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_d3_escape_slice.py",
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
    assert payload["common_dihedral_pair_class_count"] == 18088
