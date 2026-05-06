from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_row_ptolemy_product_cancellations import (
    row_ptolemy_product_cancellation_report,
)
from scripts.check_n9_row_ptolemy_product_cancellations import (
    DEFAULT_ARTIFACT,
    load_artifact,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_row_ptolemy_product_artifact_summary_is_nonclaiming() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a geometric realizability test" in payload["claim_scope"]
    assert any(
        "not an orderless abstract-incidence obstruction" in item
        for item in payload["interpretation"]
    )
    assert payload["source_frontier"]["assignment_count"] == 184
    assert payload["hit_summary"]["hit_assignment_count"] == 26
    assert payload["hit_summary"]["hit_certificate_count"] == 216
    assert payload["hit_summary"]["hit_family_count"] == 3


def test_row_ptolemy_product_artifact_records_family_counts() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    family_counts = {
        row["family_id"]: row["hit_assignment_count"]
        for row in payload["hit_summary"]["hit_family_counts"]
    }

    assert family_counts == {"F02": 18, "F09": 6, "F13": 2}
    assert payload["hit_summary"]["hit_assignment_vertex_circle_status_counts"] == {
        "self_edge": 26,
    }
    assert payload["hit_summary"]["certificates_per_hit_assignment_counts"] == {
        "6": 18,
        "12": 6,
        "18": 2,
    }
    assert payload["hit_summary"]["certificate_count_by_center"] == {
        str(center): 24 for center in range(9)
    }


def test_row_ptolemy_product_certificate_shape_is_exact_and_ordered() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    cert = payload["hit_records"][0]["certificates"][0]

    assert cert["type"] == "row_ptolemy_product_cancellation"
    assert cert["status"] == "EXACT_OBSTRUCTION_FOR_FIXED_PATTERN_AND_FIXED_ROW_ORDER"
    assert cert["ptolemy_identity"] == "d02*d13 = d01*d23 + d03*d12"
    assert cert["zero_product"]["expression"] == "d03*d12"
    assert "supplied/certified row order" in cert["scope"]


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_product_artifact_matches_generator() -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == row_ptolemy_product_cancellation_report()


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_product_checker_passes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["hit_assignment_count"] == 26
    assert summary["hit_certificate_count"] == 216


def test_row_ptolemy_product_checker_rejects_tampered_provenance() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["provenance"]["command"] = (
        "python scripts/analyze_n9_row_ptolemy_product_cancellations.py"
    )

    errors = validate_payload(payload, recompute=False)

    assert any("provenance" in error for error in errors)


def test_row_ptolemy_product_checker_rejects_unknown_top_level_key() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["unchecked_schema_drift"] = {"ok": False}

    errors = validate_payload(payload, recompute=False)

    assert any("top-level keys" in error for error in errors)


def test_row_ptolemy_product_checker_rejects_tampered_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["hit_summary"]["hit_assignment_count"] = 27

    errors = validate_payload(payload, recompute=False)

    assert any("hit assignment count" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_product_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_row_ptolemy_product_cancellations.py",
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
    assert payload["hit_certificate_count"] == 216
