from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_strict_cycle_path_join import (
    assert_expected_strict_cycle_path_join_counts,
    strict_cycle_path_join_payload,
)
from scripts.check_n9_vertex_circle_strict_cycle_path_join import (
    DEFAULT_ARTIFACT,
    load_artifact,
    load_source_payloads,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_strict_cycle_path_join_artifact_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_strict_cycle_path_join_counts(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an independent review" in payload["claim_scope"]
    assert payload["source_assignment_count"] == 184
    assert payload["self_edge_assignment_count"] == 158
    assert payload["strict_cycle_assignment_count"] == 26
    assert payload["strict_cycle_family_count"] == 3
    assert payload["strict_cycle_template_count"] == 3
    assert payload["cycle_step_count"] == 60
    assert payload["cycle_length_counts"] == {"2": 18, "3": 8}
    assert payload["first_full_assignment_cycle_length_counts"] == {"2": 22, "3": 4}
    assert payload["connector_path_length_counts"] == {"0": 6, "1": 28, "2": 26}
    assert payload["family_assignment_counts"] == {"F07": 6, "F12": 18, "F16": 2}
    assert payload["template_assignment_counts"] == {"T10": 18, "T11": 6, "T12": 2}


def test_strict_cycle_path_join_records_keep_review_maps() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    first = payload["records"][0]

    assert first["assignment_id"] == "A008"
    assert first["family_id"] == "F07"
    assert first["template_id"] == "T11"
    assert first["status"] == "strict_cycle"
    assert first["cycle_length"] == 3
    assert first["connector_path_lengths"] == [0, 1, 2]
    assert first["span_signature"] == "2:1,3:1,3:2"
    assert first["contradiction"]["kind"] == "strict_cycle"
    assert first["contradiction"]["cycle_length"] == first["cycle_length"]
    step = first["cycle_steps"][0]
    next_step = first["cycle_steps"][1]
    assert step["equality_to_next_outer_pair"]["start_pair"] == step[
        "strict_inequality"
    ]["inner_pair"]
    assert step["equality_to_next_outer_pair"]["end_pair"] == next_step[
        "strict_inequality"
    ]["outer_pair"]


def test_strict_cycle_path_join_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["strict_cycle_assignment_count"] == 26


def test_strict_cycle_path_join_rejects_tampered_family_id() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][0]["family_id"] = "F12"

    errors = validate_payload(payload, recompute=False)

    assert any("record A008 mismatch" in error for error in errors)


def test_strict_cycle_path_join_rejects_invalid_label_map() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][0]["to_canonical_label_map"] = [0] * 9

    errors = validate_payload(payload, recompute=False)

    assert any("label map" in error for error in errors)


def test_strict_cycle_path_join_rejects_tampered_connector_path() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][0]["cycle_steps"][1]["equality_to_next_outer_pair"]["path"][0][
        "next_pair"
    ] = [2, 3]

    errors = validate_payload(payload, recompute=False)

    assert any("does not equate" in error or "record A008 mismatch" in error for error in errors)


def test_strict_cycle_path_join_rejects_tampered_cycle_link() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][0]["cycle_steps"][0]["equality_to_next_outer_pair"][
        "start_pair"
    ] = [0, 1]

    errors = validate_payload(payload, recompute=False)

    assert any("cycle equality must start" in error for error in errors)


def test_strict_cycle_path_join_rejects_tampered_source_artifacts() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["source_artifacts"][2]["path"] = "data/certificates/not_the_source.json"

    errors = validate_payload(payload, recompute=False)

    assert any("source_artifacts mismatch" in error for error in errors)


def test_strict_cycle_path_join_rejects_missing_local_cycle_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item
        for item in payload["interpretation"]
        if "not first full-assignment" not in item
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("local-core and full-assignment cycles" in error for error in errors)


def test_strict_cycle_path_join_detects_source_classification_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    strict_assignment = next(
        assignment
        for assignment in sources["classification"]["assignments"]
        if assignment["status"] == "strict_cycle"
    )
    strict_assignment["core_selected_rows"][0][1] = 4

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any("source frontier classification invalid" in error for error in errors)


def test_strict_cycle_path_join_detects_source_template_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    family = next(
        family
        for family in sources["templates"]["families"]
        if family["family_id"] == "F07"
    )
    family["template_id"] = "T10"

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any(
        "source core templates invalid" in error
        or "does not match source template" in error
        for error in errors
    )


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_strict_cycle_path_join_artifact_matches_generator() -> None:
    source_payloads = load_source_payloads()
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == strict_cycle_path_join_payload(
        source_payloads["local_cores"],
        source_payloads["classification"],
        source_payloads["templates"],
        source_payloads["obstruction_shapes"],
    )


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_strict_cycle_path_join_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_strict_cycle_path_join.py",
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
    assert payload["strict_cycle_assignment_count"] == 26


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_strict_cycle_path_join_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "strict_cycle_path_join.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_strict_cycle_path_join.py",
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


def test_strict_cycle_path_join_write_check_rejects_mismatched_paths(
    tmp_path: Path,
) -> None:
    out = tmp_path / "strict_cycle_path_join.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_strict_cycle_path_join.py",
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
