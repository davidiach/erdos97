from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from erdos97.n9_selected_baseline_d3_escape_class_crosswalk import (
    selected_baseline_d3_escape_class_crosswalk_report,
)
from scripts.check_n9_selected_baseline_d3_escape_class_crosswalk import (
    DEFAULT_ARTIFACT,
    EXPECTED_PROVENANCE,
    EXPECTED_SOURCE_ARTIFACTS,
    compare_json,
    load_artifact,
    summary_payload,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_selected_baseline_d3_crosswalk_artifact_is_nonclaiming() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["crosswalk_summary"]

    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not an incidence-completeness result" in payload["claim_scope"]
    assert "not a geometric realizability test" in payload["claim_scope"]
    assert payload["assignment_count"] == 184
    assert payload["selected_baseline_class_count"] == 13
    assert payload["escape_class_count"] == 8
    assert payload["total_budget3_slot_choice_count"] == 15456
    assert payload["forced_budget3_slot_choice_count"] == 13710
    assert payload["escaping_budget3_slot_choice_count"] == 1746
    assert payload["every_escaping_placement_relevant_count"] is True
    assert summary["nonzero_crosswalk_cell_count"] == 36
    assert (
        summary["not_comparable_reference_common_dihedral_profile_escape_class_count"]
        == 18088
    )


def test_selected_baseline_d3_crosswalk_pins_relevant_count_distribution() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert payload["relevant_count_distribution"] == {
        "0": 1176,
        "1": 4032,
        "2": 4536,
        "3": 5712,
    }
    assert payload["forced_relevant_count_distribution"] == {
        "0": 1176,
        "1": 4032,
        "2": 4536,
        "3": 3966,
    }
    assert payload["escaping_relevant_count_distribution"] == {"3": 1746}


def test_selected_baseline_d3_crosswalk_rows_sum_to_escaping_landings() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    rows = payload["crosswalk_rows"]

    assert len(rows) == 36
    assert (
        sum(row["escaping_assignment_slot_choice_landing_count"] for row in rows)
        == 1746
    )
    assert {row["selected_baseline_class_id"] for row in rows} == {
        "B02",
        "B04",
        "B05",
        "B06",
        "B07",
        "B08",
        "B10",
        "B11",
        "B12",
    }
    assert {row["escape_class_id"] for row in rows} == {
        f"X{index:02d}" for index in range(8)
    }


def test_selected_baseline_d3_crosswalk_compare_json_rejects_bool_as_int() -> None:
    errors: list[str] = []

    compare_json(
        errors,
        "payload",
        {"counts": [False], "ok": True},
        {"counts": [0], "ok": True},
    )

    assert any("payload.counts[0] must be int 0" in error for error in errors)


def test_selected_baseline_d3_crosswalk_checker_pins_source_contracts() -> None:
    assert EXPECTED_SOURCE_ARTIFACTS == {
        "pre_vertex_circle_assignments": "data/certificates/n9_vertex_circle_exhaustive.json",
        "selected_baseline_overlay": (
            "data/certificates/n9_selected_baseline_escape_budget_overlay.json"
        ),
        "d3_escape_slice": "data/certificates/n9_base_apex_d3_escape_slice.json",
        "low_excess_escape_crosswalk": (
            "data/certificates/n9_base_apex_low_excess_escape_crosswalk.json"
        ),
    }
    assert EXPECTED_PROVENANCE == {
        "generator": "scripts/analyze_n9_selected_baseline_d3_escape_class_crosswalk.py",
        "command": (
            "python scripts/analyze_n9_selected_baseline_d3_escape_class_crosswalk.py "
            "--assert-expected --out "
            "data/certificates/n9_selected_baseline_d3_escape_class_crosswalk.json"
        ),
    }


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_d3_crosswalk_artifact_matches_generator() -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == selected_baseline_d3_escape_class_crosswalk_report()


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_d3_crosswalk_checker_passes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["escaping_budget3_slot_choice_count"] == 1746
    assert summary["nonzero_crosswalk_cell_count"] == 36


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_d3_crosswalk_checker_rejects_tampered_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["escaping_budget3_slot_choice_count"] = 1747

    errors = validate_payload(payload)

    assert any("crosswalk payload" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_d3_crosswalk_checker_rejects_nested_bool_as_int() -> None:
    payload = deepcopy(load_artifact(DEFAULT_ARTIFACT))
    payload["escape_classes"][0]["canonical_escape_placement"]["spoiled_length2"][0] = (
        False
    )

    errors = validate_payload(payload)

    assert any("must be int" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_d3_crosswalk_checker_rejects_matrix_bool_as_int() -> None:
    payload = deepcopy(load_artifact(DEFAULT_ARTIFACT))
    payload["crosswalk_matrix"]["rows"][0]["escaping_landing_counts"]["X00"] = False

    errors = validate_payload(payload)

    assert any("must be int" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_d3_crosswalk_checker_rejects_source_drift() -> None:
    payload = deepcopy(load_artifact(DEFAULT_ARTIFACT))
    payload["source_artifacts"]["d3_escape_slice"] = "data/certificates/other.json"

    errors = validate_payload(payload)

    assert any("source_artifacts mismatch" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_d3_crosswalk_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_selected_baseline_d3_escape_class_crosswalk.py",
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
    assert payload["escaping_budget3_slot_choice_count"] == 1746
