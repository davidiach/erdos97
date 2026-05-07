from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_self_edge_template_packet import (
    assert_expected_self_edge_template_packet_counts,
    self_edge_template_packet_payload,
)
from scripts.check_n9_vertex_circle_self_edge_template_packet import (
    DEFAULT_ARTIFACT,
    load_artifact,
    load_source_payloads,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_self_edge_template_packet_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_self_edge_template_packet_counts(payload)
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
    assert payload["assignment_core_size_counts"] == {"3": 46, "4": 40, "5": 36, "6": 36}
    assert payload["template_assignment_counts"] == {
        "T01": 6,
        "T02": 40,
        "T03": 20,
        "T04": 2,
        "T05": 18,
        "T06": 18,
        "T07": 18,
        "T08": 18,
        "T09": 18,
    }
    assert payload["template_family_counts"] == {
        "T01": 1,
        "T02": 4,
        "T03": 2,
        "T04": 1,
        "T05": 1,
        "T06": 1,
        "T07": 1,
        "T08": 1,
        "T09": 1,
    }


def test_self_edge_template_packet_first_template_record() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    first = payload["templates"][0]

    assert first["template_id"] == "T01"
    assert first["status"] == "self_edge"
    assert first["families"] == ["F09"]
    assert first["assignment_count"] == 6
    assert first["orbit_size_sum"] == 6
    assert first["assignment_ids"] == ["A014", "A024", "A031", "A140", "A166", "A175"]
    assert first["path_length_counts"] == {"3": 6}
    assert first["selected_path_shape_counts"] == {"3:1:1:path=3": 6}
    family = first["family_records"][0]
    assert family["family_id"] == "F09"
    assert family["template_id"] == "T01"
    assert family["contradiction"]["kind"] == "self_edge"
    assert family["distance_equality"]["start_pair"] == family["strict_inequality"][
        "outer_pair"
    ]
    assert family["distance_equality"]["end_pair"] == family["strict_inequality"][
        "inner_pair"
    ]


def test_self_edge_template_packet_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["self_edge_template_count"] == 9


def test_self_edge_template_packet_rejects_tampered_family_list() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["templates"][1]["families"] = ["F01"]

    errors = validate_payload(payload, recompute=False)

    assert any("family list mismatch" in error for error in errors)


def test_self_edge_template_packet_rejects_tampered_template_source_fields() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["templates"][0]["template_key"] = "bogus"
    payload["templates"][0]["core_size"] = 99
    payload["templates"][0]["selected_path_shape_counts"] = {"bogus": 6}
    payload["templates"][0]["self_edge_shape_counts"] = {"bogus": 1}

    errors = validate_payload(payload, recompute=False)

    assert any("template T01 template_key mismatch" in error for error in errors)
    assert any("template T01 core_size mismatch" in error for error in errors)
    assert any("template T01 selected_path_shape_counts mismatch" in error for error in errors)
    assert any("template T01 self_edge_shape_counts mismatch" in error for error in errors)


def test_self_edge_template_packet_rejects_tampered_assignment_id() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["templates"][0]["assignment_ids"][0] = "A999"

    errors = validate_payload(payload, recompute=False)

    assert any("template T01 assignment_ids mismatch" in error for error in errors)


def test_self_edge_template_packet_rejects_tampered_family_source_fields() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    family = payload["templates"][0]["family_records"][0]
    family["template_id"] = "T02"
    family["core_size"] = 99

    errors = validate_payload(payload, recompute=False)

    assert any("template T01 family F09 template_id mismatch" in error for error in errors)
    assert any("template T01 family F09 core_size mismatch" in error for error in errors)


def test_self_edge_template_packet_rejects_tampered_equality_path() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["templates"][0]["family_records"][0]["distance_equality"]["path"][0][
        "next_pair"
    ] = [2, 3]

    errors = validate_payload(payload, recompute=False)

    assert any("does not equate" in error or "template T01 family invalid" in error for error in errors)


def test_self_edge_template_packet_rejects_missing_no_proof_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if item != "No proof of the n=9 case is claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("no-proof" in error for error in errors)


def test_self_edge_template_packet_detects_source_path_join_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    sources["path_join"]["records"][0]["path_length"] = 99

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any("source self-edge path join invalid" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_self_edge_template_packet_artifact_matches_generator() -> None:
    source_payloads = load_source_payloads()
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == self_edge_template_packet_payload(
        source_payloads["local_cores"],
        source_payloads["path_join"],
        source_payloads["templates"],
    )


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_self_edge_template_packet_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_self_edge_template_packet.py",
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
    assert payload["self_edge_template_count"] == 9


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_self_edge_template_packet_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "self_edge_template_packet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_self_edge_template_packet.py",
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


def test_self_edge_template_packet_write_check_rejects_mismatched_paths(
    tmp_path: Path,
) -> None:
    out = tmp_path / "self_edge_template_packet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_self_edge_template_packet.py",
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
