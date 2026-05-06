from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.incidence_filters import (
    adjacent_two_overlap_violations,
    crossing_bisector_violations,
    row_ptolemy_product_cancellation_certificates,
)
from erdos97.vertex_circle_quotient_replay import (
    parse_selected_rows,
    replay_vertex_circle_quotient,
    result_to_json,
)
from scripts.check_n9_row_ptolemy_admissible_gap_replay import (
    DEFAULT_ARTIFACT,
    DEFAULT_CENSUS_ARTIFACT,
    DEFAULT_FAMILY_SIGNATURES_ARTIFACT,
    EXPECTED_SELF_EDGE_CONFLICT_HISTOGRAM,
    EXPECTED_STRICT_EDGE_HISTOGRAM,
    EXPECTED_VERTEX_STATUS_COUNTS,
    gap_replay_payload,
    assert_expected_counts,
    load_artifact,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_admissible_gap_replay_scope_and_counts() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_counts(payload)
    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an all-order obstruction" in payload["claim_scope"]
    assert "not an orderless abstract-incidence obstruction" in payload["claim_scope"]
    assert "not a geometric realizability count" in payload["claim_scope"]
    assert payload["record_count"] == 2
    assert payload["assignment_indices"] == [22, 173]
    assert payload["row_ptolemy_certificate_count_histogram"] == {"0": 2}
    assert payload["vertex_circle_status_counts"] == EXPECTED_VERTEX_STATUS_COUNTS
    assert payload["strict_edge_count_histogram"] == EXPECTED_STRICT_EDGE_HISTOGRAM
    assert (
        payload["self_edge_conflict_count_histogram"]
        == EXPECTED_SELF_EDGE_CONFLICT_HISTOGRAM
    )


def test_admissible_gap_replay_records_are_diagnostic_f13_t04_gaps() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert payload["family_signature_source"]["family_id"] == "F13"
    assert payload["family_signature_source"]["template_id"] == "T04"
    assert payload["family_signature_source"]["template_status"] == "self_edge"
    for record in payload["records"]:
        assert record["family_id"] == "F13"
        assert record["template_id"] == "T04"
        assert record["is_natural_order"] is False
        assert record["row_ptolemy_certificate_count"] == 0
        assert record["source_vertex_circle_status"] == "self_edge"
        assert record["vertex_circle_replay"]["status"] == "self_edge"
        assert record["vertex_circle_replay"]["strict_edge_count"] == 81
        assert len(record["vertex_circle_replay"]["self_edge_conflicts"]) == 27


def test_admissible_gap_replay_records_replay_filters() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    for record in payload["records"]:
        selected_rows = record["selected_rows"]
        order = record["order"]
        certificates = row_ptolemy_product_cancellation_certificates(
            selected_rows,
            order,
        )
        replay = result_to_json(
            replay_vertex_circle_quotient(
                9,
                order,
                parse_selected_rows(selected_rows),
            )
        )

        assert adjacent_two_overlap_violations(selected_rows, order) == []
        assert crossing_bisector_violations(selected_rows, order) == []
        assert certificates == []
        assert replay == record["vertex_circle_replay"]


@pytest.mark.artifact
def test_admissible_gap_replay_artifact_matches_generator() -> None:
    census = load_artifact(DEFAULT_CENSUS_ARTIFACT)
    family_signatures = load_artifact(DEFAULT_FAMILY_SIGNATURES_ARTIFACT)
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == gap_replay_payload(census, family_signatures)


def test_admissible_gap_replay_checker_passes_without_recompute() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["record_count"] == 2
    assert summary["vertex_circle_status_counts"] == {"self_edge": 2}


def test_admissible_gap_replay_rejects_tampered_replay_status() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][0]["vertex_circle_replay"]["status"] = "ok"

    errors = validate_payload(payload, recompute=False)

    assert any("vertex_circle_replay" in error for error in errors)


def test_admissible_gap_replay_rejects_stale_selected_rows() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][0]["selected_rows"][0] = [1, 2, 4, 8]

    errors = validate_payload(payload, recompute=False)

    assert any(
        "row_ptolemy_certificate_count" in error
        or "vertex_circle_replay" in error
        or "crossing-bisector" in error
        for error in errors
    )


def test_admissible_gap_replay_rejects_duplicate_record_without_recompute() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"].append(dict(payload["records"][0]))

    errors = validate_payload(payload, recompute=False)

    assert any("record count" in error for error in errors)
    assert any("record assignment indices" in error for error in errors)


def test_admissible_gap_replay_rejects_stale_assignment_set_without_recompute() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][1]["assignment_index"] = 22

    errors = validate_payload(payload, recompute=False)

    assert any("record assignment indices" in error for error in errors)


def test_admissible_gap_replay_rejects_stale_crosswalk_without_recompute() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["family_signature_source"]["hit_certificate_count"] = 35
    payload["records"][0]["family_orbit_size"] = 3
    payload["records"][0]["template_key"] = "stale"

    errors = validate_payload(payload, recompute=False)

    assert any("family_signature_source" in error for error in errors)
    assert any("family_orbit_size" in error for error in errors)
    assert any("template_key" in error for error in errors)


def test_admissible_gap_replay_rejects_stale_census_summary_without_recompute() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["source_admissible_census"]["compatible_order_count"] = 27

    errors = validate_payload(payload, recompute=False)

    assert any("source_admissible_census" in error for error in errors)


def test_admissible_gap_replay_rejects_missing_diagnostic_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if "diagnostic gaps" not in item
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("diagnostic gaps" in error for error in errors)


def test_admissible_gap_replay_rejects_tampered_source_metadata() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["source_artifacts"][0]["schema"] = (
        "erdos97.n9_row_ptolemy_order_admissible_census.v0"
    )

    errors = validate_payload(payload, recompute=False)

    assert any("source_artifacts" in error for error in errors)


@pytest.mark.artifact
def test_admissible_gap_replay_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_row_ptolemy_admissible_gap_replay.py",
            "--check",
            "--assert-expected",
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
    assert payload["record_count"] == 2
