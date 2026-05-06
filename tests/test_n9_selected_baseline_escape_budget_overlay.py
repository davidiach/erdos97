from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_selected_baseline_escape_budget import (
    selected_baseline_escape_budget_overlay,
)
from scripts.check_n9_selected_baseline_escape_budget_overlay import (
    DEFAULT_ARTIFACT,
    load_artifact,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_selected_baseline_overlay_artifact_summary_is_nonclaiming() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    selected = payload["selected_baseline"]
    frontier = payload["accepted_frontier_overlay"]

    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a geometric realizability test" in payload["claim_scope"]
    assert selected["assignment_count"] == 184
    assert selected["pre_vertex_circle_nodes"] == 100817
    assert selected["selected_baseline_total_deficit_per_assignment"] == 9
    assert selected["overfull_assignment_count"] == 0
    assert selected["relevant_deficit_count_distribution"] == {
        "0": 2,
        "3": 24,
        "4": 36,
        "5": 36,
        "6": 24,
        "8": 18,
        "9": 44,
    }
    assert selected["strict_positive_forced_assignment_count"] == 44
    assert selected["sum_exceeds_forced_assignment_count"] == 2
    assert selected["dihedral_relevant_placement_class_count"] == 13
    assert frontier["selected_baseline"]["deficit_by_cyclic_length"] == {
        "1": 0,
        "2": 3,
        "3": 2,
        "4": 4,
    }
    assert frontier["turn_cover_overlay"]["remaining_minimum_forced_turns"] == 1


def test_selected_baseline_overlay_budget_rows_pin_universal_forcing_counts() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    strict_rows = payload["budget_overlay"]["strict_positive_threshold"]["budget_rows"]
    conservative_rows = payload["budget_overlay"]["sum_exceeds_threshold"]["budget_rows"]

    assert [row["universally_forced_assignment_count"] for row in strict_rows] == [
        184,
        184,
        184,
        48,
        48,
        44,
        44,
        44,
        44,
        44,
    ]
    assert [row["universally_forced_assignment_count"] for row in conservative_rows] == [
        184,
        184,
        6,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
    ]
    assert strict_rows[9]["escaping_final_deficit_placement_count"] == 140
    assert conservative_rows[9]["escaping_final_deficit_placement_count"] == 182


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_overlay_artifact_matches_generator() -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == selected_baseline_escape_budget_overlay()


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_overlay_checker_passes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["strict_selected_baseline_forced_assignment_count"] == 44
    assert summary["conservative_selected_baseline_forced_assignment_count"] == 2


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_overlay_checker_rejects_tampered_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["selected_baseline"]["strict_positive_forced_assignment_count"] = 45

    errors = validate_payload(payload)

    assert any("overlay payload" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_overlay_checker_rejects_unknown_top_level_key() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["unchecked_schema_drift"] = {"ok": False}

    errors = validate_payload(payload)

    assert any("top-level keys" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_overlay_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_selected_baseline_escape_budget_overlay.py",
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
    assert payload["assignment_count"] == 184
