from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_self_edge_path_join import (
    assert_expected_self_edge_path_join_counts,
    self_edge_path_join_payload,
)
from scripts.check_n9_vertex_circle_self_edge_path_join import (
    DEFAULT_ARTIFACT,
    load_artifact,
    load_source_payloads,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_self_edge_path_join_artifact_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_self_edge_path_join_counts(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an independent review" in payload["claim_scope"]
    assert payload["source_assignment_count"] == 184
    assert payload["self_edge_assignment_count"] == 158
    assert payload["strict_cycle_assignment_count"] == 26
    assert payload["self_edge_family_count"] == 13
    assert payload["self_edge_template_count"] == 9
    assert payload["path_length_counts"] == {"3": 86, "4": 36, "5": 18, "6": 18}
    assert payload["shared_endpoint_counts"] == {"1": 158}


def test_self_edge_path_join_records_keep_review_maps() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    first = payload["records"][0]

    assert first["assignment_id"] == "A001"
    assert first["family_id"] == "F01"
    assert first["template_id"] == "T02"
    assert first["path_length"] == 3
    assert first["shared_endpoint_count"] == 1
    assert first["to_canonical_label_map"] == list(range(9))
    assert first["contradiction"]["kind"] == "self_edge"
    assert first["contradiction"]["outer_pair"] == first["distance_equality"]["start_pair"]
    assert first["contradiction"]["inner_pair"] == first["distance_equality"]["end_pair"]


def test_self_edge_path_join_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["self_edge_assignment_count"] == 158


def test_self_edge_path_join_rejects_tampered_family_id() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][0]["family_id"] = "F02"

    errors = validate_payload(payload, recompute=False)

    assert any("record A001 mismatch" in error for error in errors)


def test_self_edge_path_join_rejects_invalid_label_map() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][0]["to_canonical_label_map"] = [0] * 9

    errors = validate_payload(payload, recompute=False)

    assert any("label map" in error for error in errors)


def test_self_edge_path_join_rejects_tampered_equality_path() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][0]["distance_equality"]["path"][0]["next_pair"] = [2, 3]

    errors = validate_payload(payload, recompute=False)

    assert any("does not equate" in error or "record A001 mismatch" in error for error in errors)


def test_self_edge_path_join_rejects_tampered_core_row() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][0]["core_selected_rows"][0][1] = 4

    errors = validate_payload(payload, recompute=False)

    assert any("record A001 invalid" in error or "record A001 mismatch" in error for error in errors)


def test_self_edge_path_join_rejects_tampered_source_artifacts() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["source_artifacts"][0]["path"] = "data/certificates/not_the_source.json"

    errors = validate_payload(payload, recompute=False)

    assert any("source_artifacts mismatch" in error for error in errors)


def test_self_edge_path_join_rejects_missing_no_proof_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if item != "No proof of the n=9 case is claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("no-proof" in error for error in errors)


def test_self_edge_path_join_detects_source_classification_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    sources["classification"]["assignments"][0]["core_selected_rows"][0][1] = 4

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any("source frontier classification invalid" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_self_edge_path_join_artifact_matches_generator() -> None:
    source_payloads = load_source_payloads()
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == self_edge_path_join_payload(
        source_payloads["local_cores"],
        source_payloads["classification"],
    )


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_self_edge_path_join_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_self_edge_path_join.py",
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
    assert payload["self_edge_assignment_count"] == 158


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_self_edge_path_join_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "self_edge_path_join.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_self_edge_path_join.py",
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


def test_self_edge_path_join_write_check_rejects_mismatched_paths(
    tmp_path: Path,
) -> None:
    out = tmp_path / "self_edge_path_join.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_self_edge_path_join.py",
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
