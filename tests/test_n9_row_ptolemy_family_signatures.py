from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_row_ptolemy_family_signatures import (
    DEFAULT_ARTIFACT,
    DEFAULT_ROW_PTOLEMY_ARTIFACT,
    EXPECTED_SIGNATURE_ROWS,
    assert_expected_signature_counts,
    load_artifact,
    signature_payload,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_row_ptolemy_family_signature_artifact_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_signature_counts(payload)
    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not an orderless abstract-incidence obstruction" in payload["claim_scope"]
    assert payload["family_count"] == 3
    assert payload["hit_assignment_count"] == 26
    assert payload["hit_certificate_count"] == 216
    assert [row["family_id"] for row in payload["signature_rows"]] == [
        "F02",
        "F09",
        "F13",
    ]


def test_row_ptolemy_family_signature_rows_record_stable_shapes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    rows = {row["family_id"]: row for row in payload["signature_rows"]}

    assert rows == {row["family_id"]: row for row in EXPECTED_SIGNATURE_ROWS}
    assert rows["F02"]["hit_row_count_per_assignment"] == 3
    assert rows["F09"]["hit_row_count_per_assignment"] == 6
    assert rows["F13"]["hit_row_count_per_assignment"] == 9
    assert {
        row["family_id"]: row["certificate_count_per_hit_row"]
        for row in payload["signature_rows"]
    } == {"F02": 2, "F09": 2, "F13": 2}
    assert {
        row["family_id"]: row["cancelled_product_counts_per_assignment"]
        for row in payload["signature_rows"]
    } == {"F02": {"d01*d23": 6}, "F09": {"d01*d23": 12}, "F13": {"d01*d23": 18}}


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_family_signature_artifact_matches_generator() -> None:
    source = load_artifact(DEFAULT_ROW_PTOLEMY_ARTIFACT)
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == signature_payload(source)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_family_signature_checker_passes() -> None:
    source = load_artifact(DEFAULT_ROW_PTOLEMY_ARTIFACT)
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, source=source)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["family_count"] == 3
    assert summary["hit_certificate_count"] == 216


def test_row_ptolemy_family_signature_checker_rejects_tampered_signature() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["signature_rows"][0]["hit_row_count_per_assignment"] = 4

    errors = validate_payload(payload, recompute=False)

    assert any("signature_rows" in error for error in errors)


def test_row_ptolemy_family_signature_checker_rejects_missing_no_proof_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if item != "No proof of the n=9 case is claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("No proof" in error for error in errors)


def test_row_ptolemy_family_signature_checker_rejects_tampered_source() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["source_artifact"]["schema"] = "erdos97.n9_row_ptolemy_product_cancellations.v1"

    errors = validate_payload(payload, recompute=False)

    assert any("source_artifact" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_family_signature_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_row_ptolemy_family_signatures.py",
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
    assert payload["hit_certificate_count"] == 216
