from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_core_templates import (
    DEFAULT_ARTIFACT,
    DEFAULT_PACKET,
    assert_expected_core_template_counts,
    core_template_payload,
    load_artifact,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_local_core_template_artifact_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_core_template_counts(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not an independent review" in payload["claim_scope"]
    assert payload["family_count"] == 16
    assert payload["orbit_size_sum"] == 184
    assert payload["template_count"] == 12
    assert payload["status_template_counts"] == {"self_edge": 9, "strict_cycle": 3}
    assert payload["template_family_count_distribution"] == {"1": 10, "2": 1, "4": 1}


def test_local_core_template_rows_reference_known_templates() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    template_ids = {template["template_id"] for template in payload["templates"]}
    assert len(template_ids) == 12
    assert all(family["template_id"] in template_ids for family in payload["families"])
    assert [family["family_id"] for family in payload["families"]] == [
        f"F{idx:02d}" for idx in range(1, 17)
    ]
    assert {family["status"] for family in payload["families"]} == {
        "self_edge",
        "strict_cycle",
    }


def test_local_core_template_checker_rejects_tampered_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["template_count"] = 13

    errors = validate_payload(payload, recompute=False)

    assert any("template_count" in error or "template count" in error for error in errors)


def test_local_core_template_checker_rejects_missing_no_proof_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if item != "No proof of the n=9 case is claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("no-proof" in error for error in errors)


def test_local_core_template_checker_rejects_stale_template_mapping() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["families"][0]["template_id"] = payload["families"][1]["template_id"]

    errors = validate_payload(payload, recompute=False)

    assert any("template" in error and "family" in error for error in errors)


def test_local_core_template_checker_rejects_invalid_source_packet() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    errors = validate_payload(payload, packet={}, recompute=True)

    assert any("source packet invalid" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_local_core_template_artifact_matches_generator() -> None:
    packet = load_artifact(DEFAULT_PACKET)
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == core_template_payload(packet)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_local_core_template_checker_passes() -> None:
    packet = load_artifact(DEFAULT_PACKET)
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, packet=packet)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["family_count"] == 16
    assert summary["template_count"] == 12


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_local_core_template_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_core_templates.py",
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
    assert payload["family_count"] == 16
    assert payload["template_count"] == 12
