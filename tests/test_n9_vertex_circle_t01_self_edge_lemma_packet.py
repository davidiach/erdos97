from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_t01_self_edge_lemma_packet import (
    assert_expected_t01_self_edge_lemma_packet,
    t01_self_edge_lemma_packet_payload,
)
from scripts.check_n9_vertex_circle_t01_self_edge_lemma_packet import (
    DEFAULT_ARTIFACT,
    load_artifact,
    load_source_payloads,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_t01_self_edge_lemma_packet_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_t01_self_edge_lemma_packet(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "proof-mining scaffolding only" in payload["claim_scope"]
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an independent review" in payload["claim_scope"]
    assert payload["template_id"] == "T01"
    assert payload["family_id"] == "F09"
    assert payload["assignment_count"] == 6
    assert payload["assignment_ids"] == ["A014", "A024", "A031", "A140", "A166", "A175"]
    assert payload["family_count"] == 1
    assert payload["orbit_size"] == 6
    assert payload["core_size"] == 3


def test_t01_self_edge_lemma_packet_records_expected_local_shape() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert payload["core_selected_rows"] == [
        [0, 1, 2, 4, 8],
        [1, 0, 3, 5, 8],
        [2, 0, 1, 4, 6],
    ]
    assert payload["strict_inequality"]["row"] == 0
    assert payload["strict_inequality"]["witness_order"] == [1, 2, 4, 8]
    assert payload["strict_inequality"]["outer_pair"] == [1, 8]
    assert payload["strict_inequality"]["inner_pair"] == [1, 2]
    assert payload["strict_inequality"]["outer_span"] == 3
    assert payload["strict_inequality"]["inner_span"] == 1
    assert payload["distance_equality"] == {
        "start_pair": [1, 8],
        "end_pair": [1, 2],
        "path": [
            {"row": 1, "next_pair": [0, 1]},
            {"row": 0, "next_pair": [0, 2]},
            {"row": 2, "next_pair": [1, 2]},
        ],
    }
    assert payload["equality_chain"] == [[1, 8], [0, 1], [0, 2], [1, 2]]
    assert payload["local_lemma"]["review_status"] == "review_pending"
    assert payload["replay"]["status"] == "self_edge"
    assert payload["replay"]["strict_edge_count"] == 27
    assert payload["replay"]["self_edge_conflict_count"] == 2


def test_t01_self_edge_lemma_packet_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["template_id"] == "T01"
    assert summary["family_id"] == "F09"
    assert summary["assignment_count"] == 6


def test_t01_self_edge_lemma_packet_rejects_tampered_equality_path() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["distance_equality"]["path"][0]["next_pair"] = [2, 3]

    errors = validate_payload(payload, recompute=False)

    assert any("equality path mismatch" in error for error in errors)
    assert any("expected T01 self-edge lemma packet" in error for error in errors)


def test_t01_self_edge_lemma_packet_rejects_tampered_core_row() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["core_selected_rows"][0] = [0, 1, 2, 3, 8]

    errors = validate_payload(payload, recompute=False)

    assert any("core_selected_rows mismatch" in error for error in errors)


def test_t01_self_edge_lemma_packet_rejects_missing_no_proof_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if item != "No proof of the n=9 case is claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("no-proof" in error for error in errors)


def test_t01_self_edge_lemma_packet_detects_source_packet_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    sources["self_edge_packet"]["templates"][0]["assignment_ids"][0] = "A999"

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any("source self-edge template packet invalid" in error for error in errors)


@pytest.mark.artifact
def test_t01_self_edge_lemma_packet_artifact_matches_generator() -> None:
    source_payloads = load_source_payloads()
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == t01_self_edge_lemma_packet_payload(
        source_payloads["self_edge_packet"],
        source_payloads["template_catalog"],
    )


@pytest.mark.artifact
def test_t01_self_edge_lemma_packet_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py",
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
    assert payload["template_id"] == "T01"
    assert payload["replay_status"] == "self_edge"


@pytest.mark.artifact
def test_t01_self_edge_lemma_packet_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "t01_self_edge_lemma_packet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py",
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


def test_t01_self_edge_lemma_packet_write_check_rejects_mismatched_paths(
    tmp_path: Path,
) -> None:
    out = tmp_path / "t01_self_edge_lemma_packet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py",
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
