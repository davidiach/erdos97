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
)
from scripts.check_n9_row_ptolemy_order_admissible_census import (
    DEFAULT_ARTIFACT,
    DEFAULT_ROW_PTOLEMY_ARTIFACT,
    EXPECTED_COMPATIBLE_HISTOGRAM,
    EXPECTED_FAMILY_ROWS,
    EXPECTED_ZERO_COMPATIBLE_ORDER,
    admissible_census_payload,
    assert_expected_counts,
    load_artifact,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_row_ptolemy_admissible_census_scope_and_counts() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_counts(payload)
    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an all-order obstruction" in payload["claim_scope"]
    assert "not an orderless abstract-incidence obstruction" in payload["claim_scope"]
    assert "not a geometric realizability count" in payload["claim_scope"]
    assert payload["normalized_order_count"] == 20160
    assert payload["assignment_order_pair_count"] == 524160
    assert payload["adjacent_ok_order_count"] == 1318
    assert payload["compatible_order_count"] == 28
    assert payload["compatible_certificate_count_histogram"] == EXPECTED_COMPATIBLE_HISTOGRAM
    assert payload["compatible_zero_certificate_order_count"] == 2


def test_row_ptolemy_admissible_census_family_rows() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert payload["family_rows"] == EXPECTED_FAMILY_ROWS
    assert payload["source_fixed_order"]["hit_assignment_count"] == 26
    assert payload["source_fixed_order"]["hit_certificate_count"] == 216
    assert payload["source_fixed_order"]["hit_family_ids"] == ["F02", "F09", "F13"]
    assert payload["compatible_order_count_per_assignment_counts"] == {
        "1": 24,
        "2": 2,
    }
    assert {
        row["family_id"]: row["adjacent_ok_order_count"]
        for row in payload["family_rows"]
    } == {"F02": 990, "F09": 246, "F13": 82}
    assert payload["compatible_vertex_circle_status_counts"] == {"self_edge": 28}


def test_row_ptolemy_admissible_census_records_f13_gap() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    zero_rows = []
    for row in payload["assignment_rows"]:
        for order in row["compatible_orders"]:
            if order["certificate_count"] == 0:
                zero_rows.append((row["assignment_index"], order))

    assert [assignment for assignment, _ in zero_rows] == [22, 173]
    for _, order in zero_rows:
        assert order["order"] == EXPECTED_ZERO_COMPATIBLE_ORDER
        assert order["vertex_circle_status"] == "self_edge"
        assert order["is_natural_order"] is False


def test_row_ptolemy_admissible_census_compatible_orders_replay() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    for row in payload["assignment_rows"]:
        selected_rows = row["selected_rows"]
        for order_row in row["compatible_orders"]:
            order = order_row["order"]
            certificates = row_ptolemy_product_cancellation_certificates(
                selected_rows,
                order,
            )
            vertex_circle_status = replay_vertex_circle_quotient(
                9,
                order,
                parse_selected_rows(selected_rows),
            ).status

            assert adjacent_two_overlap_violations(selected_rows, order) == []
            assert crossing_bisector_violations(selected_rows, order) == []
            assert len(certificates) == order_row["certificate_count"]
            assert vertex_circle_status == order_row["vertex_circle_status"]


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_admissible_census_artifact_matches_generator() -> None:
    source = load_artifact(DEFAULT_ROW_PTOLEMY_ARTIFACT)
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == admissible_census_payload(source)


def test_row_ptolemy_admissible_census_checker_passes_without_recompute() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["compatible_order_count"] == 28
    assert summary["compatible_zero_certificate_order_count"] == 2


def test_row_ptolemy_admissible_census_rejects_tampered_histogram() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["compatible_certificate_count_histogram"]["0"] = 3

    errors = validate_payload(payload, recompute=False)

    assert any("compatible certificate histogram" in error for error in errors)


def test_row_ptolemy_admissible_census_rejects_stale_rows_without_full_recompute() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["assignment_rows"][0]["selected_rows"][0] = [1, 2, 4, 8]

    errors = validate_payload(payload, recompute=False)

    assert any(
        "certificate_count mismatch" in error
        or "does not pass admissible order filters" in error
        for error in errors
    )


def test_row_ptolemy_admissible_census_rejects_missing_gap_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if "diagnostic gaps" not in item
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("diagnostic gaps" in error for error in errors)


def test_row_ptolemy_admissible_census_rejects_bad_order() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["assignment_rows"][0]["compatible_orders"][0]["order"] = [
        0,
        8,
        7,
        6,
        5,
        4,
        3,
        2,
        1,
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("reversal quotient" in error for error in errors)


def test_row_ptolemy_admissible_census_rejects_tampered_source() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["source_artifacts"][0]["schema"] = (
        "erdos97.n9_row_ptolemy_product_cancellations.v1"
    )

    errors = validate_payload(payload, recompute=False)

    assert any("source_artifacts" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_admissible_census_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_row_ptolemy_order_admissible_census.py",
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
    assert payload["compatible_order_count"] == 28
