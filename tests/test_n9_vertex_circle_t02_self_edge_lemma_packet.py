from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_t02_self_edge_lemma_packet import (
    EXPECTED_FAMILY_IDS,
    assert_expected_t02_self_edge_lemma_packet,
    t02_self_edge_lemma_packet_payload,
)
from scripts.check_n9_vertex_circle_t02_self_edge_lemma_packet import (
    DEFAULT_ARTIFACT,
    load_artifact,
    load_source_payloads,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def _family_packets(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {str(packet["family_id"]): packet for packet in payload["family_packets"]}  # type: ignore[index]


def _template_record(source_payloads: dict[str, object]) -> dict[str, object]:
    for template in source_payloads["self_edge_packet"]["templates"]:  # type: ignore[index]
        if template["template_id"] == "T02":
            return template
    raise AssertionError("missing T02 template")


def _catalog_record(source_payloads: dict[str, object]) -> dict[str, object]:
    for template in source_payloads["template_catalog"]["templates"]:  # type: ignore[index]
        if template["template_id"] == "T02":
            return template
    raise AssertionError("missing T02 catalog record")


def test_t02_self_edge_lemma_packet_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_t02_self_edge_lemma_packet(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "proof-mining scaffolding only" in payload["claim_scope"]
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an independent review" in payload["claim_scope"]
    assert payload["template_id"] == "T02"
    assert payload["template_key"] == "self_edge|rows=3|strict_edges=27|conflicts=3:1:1x1"
    assert payload["assignment_count"] == 40
    assert payload["family_count"] == 4
    assert payload["family_ids"] == ["F01", "F04", "F08", "F14"]
    assert payload["family_assignment_counts"] == {"F01": 18, "F04": 18, "F08": 2, "F14": 2}
    assert payload["family_orbit_sizes"] == {"F01": 18, "F04": 18, "F08": 2, "F14": 2}
    assert payload["orbit_size_sum"] == 40
    assert payload["core_size"] == 3
    assert payload["strict_edge_count"] == 27
    assert payload["path_length_counts"] == {"3": 40}
    assert payload["shared_endpoint_counts"] == {"1": 40}


def test_t02_self_edge_lemma_packet_records_expected_local_shapes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packets = _family_packets(payload)

    assert set(packets) == set(EXPECTED_FAMILY_IDS)
    assert packets["F01"]["core_selected_rows"] == [
        [0, 1, 2, 3, 8],
        [1, 0, 2, 4, 7],
        [8, 0, 1, 4, 5],
    ]
    assert packets["F01"]["strict_inequality"]["row"] == 0  # type: ignore[index]
    assert packets["F01"]["strict_inequality"]["outer_pair"] == [1, 8]  # type: ignore[index]
    assert packets["F01"]["strict_inequality"]["inner_pair"] == [1, 2]  # type: ignore[index]
    assert packets["F01"]["equality_chain"] == [[1, 8], [0, 8], [0, 1], [1, 2]]

    assert packets["F04"]["core_selected_rows"] == [
        [0, 1, 2, 4, 6],
        [1, 0, 2, 3, 5],
        [2, 1, 3, 4, 8],
    ]
    assert packets["F04"]["strict_inequality"]["row"] == 1  # type: ignore[index]
    assert packets["F04"]["strict_inequality"]["witness_order"] == [2, 3, 5, 0]  # type: ignore[index]
    assert packets["F04"]["strict_inequality"]["outer_pair"] == [0, 2]  # type: ignore[index]
    assert packets["F04"]["strict_inequality"]["inner_pair"] == [2, 3]  # type: ignore[index]
    assert packets["F04"]["equality_chain"] == [[0, 2], [0, 1], [1, 2], [2, 3]]

    assert packets["F08"]["strict_inequality"]["witness_order"] == [1, 2, 4, 8]  # type: ignore[index]
    assert packets["F08"]["equality_chain"] == [[1, 8], [0, 8], [0, 1], [1, 2]]
    assert packets["F14"]["strict_inequality"]["witness_order"] == [1, 2, 6, 8]  # type: ignore[index]
    assert packets["F14"]["equality_chain"] == [[1, 8], [0, 8], [0, 1], [1, 2]]

    for family_id, packet in packets.items():
        assert packet["local_lemma"]["review_status"] == "review_pending"  # type: ignore[index]
        assert packet["replay"]["status"] == "self_edge"  # type: ignore[index]
        assert packet["replay"]["selected_row_count"] == 3  # type: ignore[index]
        assert packet["replay"]["strict_edge_count"] == 27  # type: ignore[index]
        assert packet["replay"]["self_edge_conflict_count"] == 1  # type: ignore[index]
        assert packet["replay"]["cycle_edge_count"] == 0  # type: ignore[index]
        assert packet["replay"]["primary_self_edge_conflict"]["row"] == packet["strict_inequality"]["row"]  # type: ignore[index]
        assert family_id in {"F01", "F04", "F08", "F14"}


def test_t02_self_edge_lemma_packet_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["template_id"] == "T02"
    assert summary["family_count"] == 4
    assert summary["assignment_count"] == 40
    assert summary["replay_statuses"] == ["self_edge", "self_edge", "self_edge", "self_edge"]


def test_t02_self_edge_lemma_packet_rejects_tampered_f04_equality_path() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packets = _family_packets(payload)
    packets["F04"]["distance_equality"]["path"][0]["next_pair"] = [2, 4]  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F04 distance_equality mismatch" in error for error in errors)
    assert any("expected T02 self-edge lemma packet" in error for error in errors)


def test_t02_self_edge_lemma_packet_rejects_tampered_f04_strict_row() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packets = _family_packets(payload)
    packets["F04"]["strict_inequality"]["row"] = 0  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F04 strict_inequality mismatch" in error for error in errors)


def test_t02_self_edge_lemma_packet_rejects_missing_family() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["family_packets"] = [
        packet for packet in payload["family_packets"] if packet["family_id"] != "F14"
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("family packet ids mismatch" in error for error in errors)


def test_t02_self_edge_lemma_packet_rejects_missing_no_proof_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if item != "No proof of the n=9 case is claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("no-proof" in error for error in errors)


def test_t02_self_edge_lemma_packet_detects_source_packet_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    template = _template_record(sources)
    template["family_records"][1]["strict_inequality"]["row"] = 0  # F04 is the second T02 family.

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any(
        "source self-edge template packet invalid" in error
        or "source-bound T02 self-edge lemma packet failed" in error
        for error in errors
    )


def test_t02_self_edge_lemma_packet_detects_catalog_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    catalog = _catalog_record(sources)
    catalog["coverage"]["families"] = ["F01", "F04", "F08"]

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any(
        "source template lemma catalog invalid" in error
        or "source-bound T02 self-edge lemma packet failed" in error
        for error in errors
    )


@pytest.mark.artifact
def test_t02_self_edge_lemma_packet_artifact_matches_generator() -> None:
    source_payloads = load_source_payloads()
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == t02_self_edge_lemma_packet_payload(
        source_payloads["self_edge_packet"],
        source_payloads["template_catalog"],
    )


@pytest.mark.artifact
def test_t02_self_edge_lemma_packet_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py",
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
    assert payload["template_id"] == "T02"
    assert payload["family_count"] == 4
    assert payload["replay_statuses"] == ["self_edge", "self_edge", "self_edge", "self_edge"]


@pytest.mark.artifact
def test_t02_self_edge_lemma_packet_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "t02_self_edge_lemma_packet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py",
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


def test_t02_self_edge_lemma_packet_write_check_rejects_mismatched_paths(
    tmp_path: Path,
) -> None:
    out = tmp_path / "t02_self_edge_lemma_packet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py",
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
