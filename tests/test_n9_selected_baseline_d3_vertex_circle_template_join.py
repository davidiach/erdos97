from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from erdos97.n9_selected_baseline_d3_vertex_circle_template_join import (
    EXPECTED_ESCAPE_LANDING_COUNTS,
    EXPECTED_STATUS_LANDING_COUNTS,
    EXPECTED_TEMPLATE_LANDING_COUNTS,
    SOURCE_ARTIFACTS,
    selected_baseline_d3_vertex_circle_template_join_payload,
)
from scripts.check_n9_selected_baseline_d3_vertex_circle_template_join import (
    DEFAULT_ARTIFACT,
    DEFAULT_CLASSIFICATION,
    DEFAULT_TEMPLATE_CATALOG,
    PROVENANCE,
    compare_json,
    load_artifact,
    load_source_payloads,
    summary_payload,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


def test_selected_baseline_d3_template_join_artifact_is_nonclaiming() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an incidence-completeness result" in payload["claim_scope"]
    assert "not a geometric realizability test" in payload["claim_scope"]
    assert payload["source_assignment_count"] == 184
    assert payload["escaping_assignment_slot_choice_landing_count"] == 1746
    assert payload["vertex_circle_status_landing_counts"] == EXPECTED_STATUS_LANDING_COUNTS
    assert payload["vertex_circle_template_landing_counts"] == (
        EXPECTED_TEMPLATE_LANDING_COUNTS
    )
    assert payload["escape_class_landing_counts"] == EXPECTED_ESCAPE_LANDING_COUNTS


def test_selected_baseline_d3_template_join_records_are_labelled_landings() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["landing_records"]

    assert len(records) == 1746
    assert records[0]["landing_id"] == "L0001"
    assert records[-1]["landing_id"] == "L1746"
    assert all(record["assignment_id"].startswith("A") for record in records)
    assert all(len(record["budget3_slot_choice_indices"]) == 3 for record in records)
    assert all(
        len(record["relevant_escape_placement"]["spoiled_length2"])
        + len(record["relevant_escape_placement"]["spoiled_length3"])
        == 3
        for record in records
    )


def test_selected_baseline_d3_template_join_pins_zero_landing_templates() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert payload["vertex_circle_template_landing_counts"]["T05"] == 0
    assert payload["vertex_circle_template_landing_counts"]["T09"] == 0
    assert payload["vertex_circle_template_landing_counts"]["T11"] == 0
    assert {row["template_id"] for row in payload["vertex_circle_template_summaries"]} == {
        f"T{index:02d}" for index in range(1, 13)
    }


def test_selected_baseline_d3_template_join_pins_source_contracts() -> None:
    assert SOURCE_ARTIFACTS == [
        {
            "path": "data/certificates/n9_selected_baseline_d3_escape_class_crosswalk.json",
            "role": "aggregate selected-baseline D=3 escape-class crosswalk",
            "schema": "erdos97.n9_selected_baseline_d3_escape_class_crosswalk.v1",
            "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
        },
        {
            "path": "data/certificates/n9_vertex_circle_frontier_motif_classification.json",
            "role": "assignment_id to vertex-circle family/template diagnostics",
            "schema": "erdos97.n9_vertex_circle_frontier_motif_classification.v1",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": "data/certificates/n9_vertex_circle_template_lemma_catalog.json",
            "role": "vertex-circle template status and coverage diagnostics",
            "schema": "erdos97.n9_vertex_circle_template_lemma_catalog.v1",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
    ]
    assert PROVENANCE == {
        "generator": "scripts/check_n9_selected_baseline_d3_vertex_circle_template_join.py",
        "command": (
            "python scripts/check_n9_selected_baseline_d3_vertex_circle_template_join.py "
            "--assert-expected --write"
        ),
    }


def test_selected_baseline_d3_template_join_compare_json_rejects_bool_as_int() -> None:
    errors: list[str] = []

    compare_json(
        errors,
        "payload",
        {"vertex_circle_template_landing_counts": {"T05": False}},
        {"vertex_circle_template_landing_counts": {"T05": 0}},
    )

    assert any("payload.vertex_circle_template_landing_counts.T05 must be int 0" in error for error in errors)


def test_selected_baseline_d3_template_join_checker_rejects_bool_as_int_count() -> None:
    payload = deepcopy(load_artifact(DEFAULT_ARTIFACT))
    payload["vertex_circle_template_landing_counts"]["T05"] = False

    errors = validate_payload(payload, recompute=False)

    assert any("vertex_circle_template_landing_counts.T05 must be int" in error for error in errors)


def test_selected_baseline_d3_template_join_checker_rejects_malformed_placement() -> None:
    payload = deepcopy(load_artifact(DEFAULT_ARTIFACT))
    payload["landing_records"][0]["relevant_escape_placement"]["spoiled_length2"] = None

    errors = validate_payload(payload, recompute=False)

    assert any("relevant placement lists must be JSON ints" in error for error in errors)


def test_selected_baseline_d3_template_join_checker_rejects_source_drift() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    source_payloads = load_source_payloads()
    source_payloads["crosswalk"] = deepcopy(source_payloads["crosswalk"])
    source_payloads["crosswalk"]["escaping_budget3_slot_choice_count"] = 1747

    errors = validate_payload(payload, source_payloads=source_payloads, recompute=False)

    assert any("source selected-baseline D=3 crosswalk invalid" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_d3_template_join_artifact_matches_generator() -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)
    classification = load_artifact(DEFAULT_CLASSIFICATION)
    template_catalog = load_artifact(DEFAULT_TEMPLATE_CATALOG)

    assert checked_in == selected_baseline_d3_vertex_circle_template_join_payload(
        classification,
        template_catalog,
    )


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_d3_template_join_checker_passes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["escaping_assignment_slot_choice_landing_count"] == 1746


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_d3_template_join_checker_rejects_tampered_count() -> None:
    payload = deepcopy(load_artifact(DEFAULT_ARTIFACT))
    payload["vertex_circle_status_landing_counts"]["self_edge"] = 1027

    errors = validate_payload(payload, recompute=False)

    assert any("vertex_circle_status_landing_counts" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_d3_template_join_checker_rejects_bad_record() -> None:
    payload = deepcopy(load_artifact(DEFAULT_ARTIFACT))
    payload["landing_records"][0]["vertex_circle_template_id"] = "T05"

    errors = validate_payload(payload, recompute=False)

    assert any("vertex_circle_template_landing_counts" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_selected_baseline_d3_template_join_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_selected_baseline_d3_vertex_circle_template_join.py",
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
    assert payload["escaping_assignment_slot_choice_landing_count"] == 1746
    assert payload["vertex_circle_status_landing_counts"] == {
        "self_edge": 1026,
        "strict_cycle": 720,
    }
