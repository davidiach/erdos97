from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.incidence_filters import row_ptolemy_product_cancellation_certificates
from scripts.check_n9_row_ptolemy_order_sensitivity import (
    DEFAULT_ARTIFACT,
    DEFAULT_ROW_PTOLEMY_ARTIFACT,
    EXPECTED_REPRESENTATIVES,
    assert_expected_counts,
    load_artifact,
    order_sensitivity_payload,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_row_ptolemy_order_sensitivity_artifact_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_counts(payload)
    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not an all-order obstruction" in payload["claim_scope"]
    assert "not an orderless abstract-incidence obstruction" in payload["claim_scope"]
    assert payload["representative_count"] == 3
    assert payload["examined_order_count"] == 6
    assert payload["zero_challenge_order_count"] == 3
    assert payload["source_fixed_order"]["hit_assignment_count"] == 26
    assert payload["source_fixed_order"]["hit_certificate_count"] == 216


def test_row_ptolemy_order_sensitivity_rows_replay_orders() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert [row["family_id"] for row in payload["rows"]] == ["F02", "F09", "F13"]
    for row, expected in zip(payload["rows"], EXPECTED_REPRESENTATIVES):
        natural = row_ptolemy_product_cancellation_certificates(
            row["selected_rows"],
            row["natural_order"],
        )
        challenge = row_ptolemy_product_cancellation_certificates(
            row["selected_rows"],
            row["challenge_order"],
        )

        assert row["family_id"] == expected["family_id"]
        assert row["assignment_index"] == expected["assignment_index"]
        assert row["natural_certificate_count"] == expected["natural_certificate_count"]
        assert row["stored_certificate_count"] == len(natural)
        assert row["challenge_order"] == expected["challenge_order"]
        assert row["challenge_order_is_dihedral_of_natural_order"] is False
        assert len(challenge) == 0
        assert row["certificate_count_drop"] == len(natural)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_order_sensitivity_artifact_matches_generator() -> None:
    source = load_artifact(DEFAULT_ROW_PTOLEMY_ARTIFACT)
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == order_sensitivity_payload(source)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_order_sensitivity_checker_passes() -> None:
    source = load_artifact(DEFAULT_ROW_PTOLEMY_ARTIFACT)
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, source=source)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["representative_count"] == 3
    assert summary["zero_challenge_order_count"] == 3


def test_row_ptolemy_order_sensitivity_checker_rejects_tampered_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["rows"][0]["challenge_certificate_count"] = 1

    errors = validate_payload(payload, recompute=False)

    assert any("zero-challenge" in error or "challenge certificate" in error for error in errors)


def test_row_ptolemy_order_sensitivity_checker_rejects_tampered_source() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["source_artifacts"][0]["schema"] = (
        "erdos97.n9_row_ptolemy_product_cancellations.v1"
    )

    errors = validate_payload(payload, recompute=False)

    assert any("source_artifacts" in error for error in errors)


def test_row_ptolemy_order_sensitivity_checker_rejects_stale_rows() -> None:
    source = load_artifact(DEFAULT_ROW_PTOLEMY_ARTIFACT)
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["rows"][0]["selected_rows"][0] = [1, 2, 4, 8]

    errors = validate_payload(payload, source=source)

    assert any("order-sensitivity diagnostic" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_order_sensitivity_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_row_ptolemy_order_sensitivity.py",
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
    assert payload["families"] == ["F02", "F09", "F13"]
