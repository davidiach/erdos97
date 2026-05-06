from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_frontier_motif_classification import (
    assert_expected_classification_counts,
    frontier_motif_classification_payload,
)
from scripts.check_n9_vertex_circle_frontier_motif_classification import (
    DEFAULT_ARTIFACT,
    load_artifact,
    load_source_payloads,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_frontier_motif_classification_artifact_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_classification_counts(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not an independent review" in payload["claim_scope"]
    assert payload["assignment_count"] == 184
    assert payload["status_counts"] == {"self_edge": 158, "strict_cycle": 26}
    assert payload["family_count"] == 16
    assert payload["template_count"] == 12


def test_frontier_motif_classification_assignments_have_known_templates() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    source_payloads = load_source_payloads()
    template_ids = {
        template["template_id"]
        for template in source_payloads["templates"]["templates"]
    }

    assert {row["template_id"] for row in payload["assignments"]} <= template_ids
    assert [row["assignment_id"] for row in payload["assignments"][:3]] == [
        "A001",
        "A002",
        "A003",
    ]
    assert payload["families"][0] == {
        "assignment_count": 18,
        "core_size": 3,
        "family_id": "F01",
        "orbit_size": 18,
        "status": "self_edge",
        "template_id": "T02",
    }


def test_frontier_motif_classification_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["assignment_count"] == 184


def test_frontier_motif_classification_rejects_tampered_family_id() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["assignments"][0]["family_id"] = "F02"

    errors = validate_payload(payload, recompute=False)

    assert any("family_id mismatch" in error for error in errors)


def test_frontier_motif_classification_rejects_valid_but_wrong_template_id() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["assignments"][0]["template_id"] = "T03"

    errors = validate_payload(payload, recompute=False)

    assert any("template_id mismatch" in error for error in errors)


def test_frontier_motif_classification_rejects_tampered_core_row() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["assignments"][0]["core_selected_rows"][0][1] = 4

    errors = validate_payload(payload, recompute=False)

    assert any("core rows" in error or "core replay" in error for error in errors)


def test_frontier_motif_classification_rejects_tampered_source_artifacts() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["source_artifacts"][0]["path"] = "data/certificates/not_the_source.json"

    errors = validate_payload(payload, recompute=False)

    assert any("source_artifacts mismatch" in error for error in errors)


def test_frontier_motif_classification_rejects_missing_no_proof_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if item != "No proof of the n=9 case is claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("no-proof" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_frontier_motif_classification_artifact_matches_generator() -> None:
    source_payloads = load_source_payloads()
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == frontier_motif_classification_payload(
        source_payloads["motif"],
        source_payloads["packet"],
        source_payloads["templates"],
    )


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_frontier_motif_classification_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_frontier_motif_classification.py",
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
    assert payload["assignment_count"] == 184


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_frontier_motif_classification_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "classification.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_frontier_motif_classification.py",
            "--write",
            "--check",
            "--assert-expected",
            "--out",
            str(out),
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
    assert payload["artifact"] == str(out.resolve())


def test_frontier_motif_classification_write_check_rejects_mismatched_paths(
    tmp_path: Path,
) -> None:
    out = tmp_path / "classification.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_frontier_motif_classification.py",
            "--write",
            "--check",
            "--assert-expected",
            "--artifact",
            str(DEFAULT_ARTIFACT),
            "--out",
            str(out),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 2
    assert "--write --check requires matching --artifact/--out" in result.stderr
