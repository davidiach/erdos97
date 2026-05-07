from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_template_lemma_catalog import (
    assert_expected_template_lemma_catalog_counts,
    template_lemma_catalog_payload,
)
from scripts.check_n9_vertex_circle_template_lemma_catalog import (
    DEFAULT_ARTIFACT,
    load_artifact,
    load_source_payloads,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_template_lemma_catalog_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_template_lemma_catalog_counts(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an independent review" in payload["claim_scope"]
    assert payload["source_assignment_count"] == 184
    assert payload["covered_assignment_count"] == 184
    assert payload["template_count"] == 12
    assert payload["family_count"] == 16
    assert payload["template_status_counts"] == {"self_edge": 9, "strict_cycle": 3}
    assert payload["family_status_counts"] == {"self_edge": 13, "strict_cycle": 3}
    assert payload["status_assignment_counts"] == {"self_edge": 158, "strict_cycle": 26}
    assert payload["template_core_size_counts"] == {"3": 2, "4": 5, "5": 2, "6": 3}
    assert payload["family_core_size_counts"] == {"3": 5, "4": 6, "5": 2, "6": 3}


def test_template_lemma_catalog_records_self_edge_and_strict_cycle_shapes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = {record["template_id"]: record for record in payload["templates"]}

    t01 = records["T01"]
    assert t01["status"] == "self_edge"
    assert t01["coverage"]["assignment_count"] == 6
    assert t01["hypothesis_shape"]["core_size"] == 3
    assert t01["hypothesis_shape"]["path_length_counts"] == {"3": 6}
    assert t01["conclusion_shape"]["kind"] == "self_edge"
    assert t01["family_summaries"] == [
        {
            "assignment_count": 6,
            "contradiction_kind": "self_edge",
            "core_size": 3,
            "equality_path_length": 3,
            "family_id": "F09",
            "inner_pair": [1, 2],
            "inner_span": 1,
            "orbit_size": 6,
            "outer_pair": [1, 8],
            "outer_span": 3,
            "path_length": 3,
            "status": "self_edge",
            "template_id": "T01",
        }
    ]

    t10 = records["T10"]
    assert t10["status"] == "strict_cycle"
    assert t10["coverage"]["assignment_count"] == 18
    assert t10["hypothesis_shape"]["core_size"] == 4
    assert t10["hypothesis_shape"]["cycle_length_counts"] == {"2": 18}
    assert t10["hypothesis_shape"]["connector_path_length_counts"] == {
        "1": 18,
        "2": 18,
    }
    assert t10["conclusion_shape"]["kind"] == "strict_cycle"
    assert t10["family_summaries"][0]["family_id"] == "F12"
    assert t10["family_summaries"][0]["span_signature"] == "2:1,2:1"


def test_template_lemma_catalog_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["covered_assignment_count"] == 184
    assert summary["template_count"] == 12


def test_template_lemma_catalog_rejects_tampered_assignment_id() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["templates"][0]["coverage"]["assignment_ids"][0] = "A999"

    errors = validate_payload(payload, recompute=False)

    assert any("templates mismatch" in error for error in errors)


def test_template_lemma_catalog_rejects_tampered_conclusion_kind() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["templates"][9]["conclusion_shape"]["kind"] = "self_edge"

    errors = validate_payload(payload, recompute=False)

    assert any("conclusion kind mismatch" in error for error in errors)


def test_template_lemma_catalog_rejects_missing_no_proof_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if item != "No proof of the n=9 case is claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("no-proof" in error for error in errors)


def test_template_lemma_catalog_detects_source_packet_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    sources["strict_cycle_packet"]["templates"][0]["assignment_ids"][0] = "A999"

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any("source strict-cycle template packet invalid" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_template_lemma_catalog_artifact_matches_generator() -> None:
    source_payloads = load_source_payloads()
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == template_lemma_catalog_payload(
        source_payloads["self_edge_packet"],
        source_payloads["strict_cycle_packet"],
        source_payloads["core_templates"],
    )


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_template_lemma_catalog_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_template_lemma_catalog.py",
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
    assert payload["template_count"] == 12


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_template_lemma_catalog_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "template_lemma_catalog.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_template_lemma_catalog.py",
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


def test_template_lemma_catalog_write_check_rejects_mismatched_paths(
    tmp_path: Path,
) -> None:
    out = tmp_path / "template_lemma_catalog.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_template_lemma_catalog.py",
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
