from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_strict_cycle_template_packet import (
    assert_expected_strict_cycle_template_packet_counts,
    strict_cycle_template_packet_payload,
)
from scripts.check_n9_vertex_circle_strict_cycle_template_packet import (
    DEFAULT_ARTIFACT,
    load_artifact,
    load_source_payloads,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_strict_cycle_template_packet_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_strict_cycle_template_packet_counts(payload)
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
    assert payload["local_core_cycle_step_count"] == 60
    assert payload["local_core_cycle_length_counts"] == {"2": 18, "3": 8}
    assert payload["first_full_assignment_cycle_length_counts"] == {"2": 22, "3": 4}
    assert payload["connector_path_length_counts"] == {"0": 6, "1": 28, "2": 26}
    assert payload["template_assignment_counts"] == {"T10": 18, "T11": 6, "T12": 2}
    assert payload["template_cycle_length_counts"] == {
        "T10": {"2": 18},
        "T11": {"3": 6},
        "T12": {"3": 2},
    }


def test_strict_cycle_template_packet_first_template_record() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    first = payload["templates"][0]

    assert first["template_id"] == "T10"
    assert first["status"] == "strict_cycle"
    assert first["families"] == ["F12"]
    assert first["assignment_count"] == 18
    assert first["orbit_size_sum"] == 18
    assert first["assignment_ids"] == [
        "A020",
        "A040",
        "A047",
        "A071",
        "A080",
        "A081",
        "A083",
        "A093",
        "A095",
        "A111",
        "A126",
        "A147",
        "A151",
        "A153",
        "A154",
        "A157",
        "A164",
        "A180",
    ]
    assert first["cycle_length_counts"] == {"2": 18}
    assert first["connector_path_length_counts"] == {"1": 18, "2": 18}
    assert first["span_signature_counts"] == {"2:1,2:1": 18}
    family = first["family_records"][0]
    assert family["family_id"] == "F12"
    assert family["template_id"] == "T10"
    assert family["contradiction"]["kind"] == "strict_cycle"
    assert family["cycle_length"] == len(family["cycle_steps"])


def test_strict_cycle_template_packet_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["strict_cycle_template_count"] == 3


def test_strict_cycle_template_packet_rejects_tampered_family_list() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["templates"][0]["families"] = ["F07"]

    errors = validate_payload(payload, recompute=False)

    assert any("family list mismatch" in error for error in errors)


def test_strict_cycle_template_packet_rejects_tampered_template_source_fields() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["templates"][0]["template_key"] = "bogus"
    payload["templates"][0]["cycle_length"] = 99
    payload["templates"][0]["connector_path_length_counts"] = {"bogus": 1}
    payload["templates"][0]["cycle_span_counts"] = [{"count": 1}]

    errors = validate_payload(payload, recompute=False)

    assert any("template T10 template_key mismatch" in error for error in errors)
    assert any("template T10 cycle_length mismatch" in error for error in errors)
    assert any(
        "template T10 connector_path_length_counts mismatch" in error
        for error in errors
    )
    assert any("template T10 cycle_span_counts mismatch" in error for error in errors)


def test_strict_cycle_template_packet_rejects_tampered_assignment_id() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["templates"][0]["assignment_ids"][0] = "A999"

    errors = validate_payload(payload, recompute=False)

    assert any("template T10 assignment_ids mismatch" in error for error in errors)


def test_strict_cycle_template_packet_rejects_tampered_family_source_fields() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    family = payload["templates"][0]["family_records"][0]
    family["template_id"] = "T11"
    family["span_signature"] = "bogus"

    errors = validate_payload(payload, recompute=False)

    assert any("template T10 family F12 template_id mismatch" in error for error in errors)
    assert any("template T10 family F12 span_signature mismatch" in error for error in errors)


def test_strict_cycle_template_packet_rejects_tampered_cycle_connector() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["templates"][0]["family_records"][0]["cycle_steps"][0][
        "equality_to_next_outer_pair"
    ]["end_pair"] = [0, 8]

    errors = validate_payload(payload, recompute=False)

    assert any("cycle equality must end" in error for error in errors)


def test_strict_cycle_template_packet_rejects_missing_no_proof_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if item != "No proof of the n=9 case is claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("no-proof" in error for error in errors)


def test_strict_cycle_template_packet_rejects_missing_cycle_distinction() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item
        for item in payload["interpretation"]
        if "not first full-assignment" not in item
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("distinguish local-core and full cycles" in error for error in errors)


def test_strict_cycle_template_packet_detects_source_path_join_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    sources["path_join"]["records"][0]["cycle_length"] = 99

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any("source strict-cycle path join invalid" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_strict_cycle_template_packet_artifact_matches_generator() -> None:
    source_payloads = load_source_payloads()
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == strict_cycle_template_packet_payload(
        source_payloads["local_cores"],
        source_payloads["path_join"],
        source_payloads["templates"],
    )


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_strict_cycle_template_packet_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_strict_cycle_template_packet.py",
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
    assert payload["strict_cycle_template_count"] == 3


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_strict_cycle_template_packet_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "strict_cycle_template_packet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_strict_cycle_template_packet.py",
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


def test_strict_cycle_template_packet_write_check_rejects_mismatched_paths(
    tmp_path: Path,
) -> None:
    out = tmp_path / "strict_cycle_template_packet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_strict_cycle_template_packet.py",
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
