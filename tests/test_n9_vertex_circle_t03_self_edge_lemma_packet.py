from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_t03_self_edge_lemma_packet import (
    EXPECTED_FAMILY_IDS,
    assert_expected_t03_self_edge_lemma_packet,
    t03_self_edge_lemma_packet_payload,
)
from scripts.check_n9_vertex_circle_t03_self_edge_lemma_packet import (
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
        if template["template_id"] == "T03":
            return template
    raise AssertionError("missing T03 template")


def _catalog_record(source_payloads: dict[str, object]) -> dict[str, object]:
    for template in source_payloads["template_catalog"]["templates"]:  # type: ignore[index]
        if template["template_id"] == "T03":
            return template
    raise AssertionError("missing T03 catalog record")


def test_t03_self_edge_lemma_packet_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_t03_self_edge_lemma_packet(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "proof-mining scaffolding only" in payload["claim_scope"]
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an independent review" in payload["claim_scope"]
    assert payload["template_id"] == "T03"
    assert payload["template_key"] == "self_edge|rows=4|strict_edges=36|conflicts=2:1:1x1"
    assert payload["assignment_count"] == 20
    assert payload["family_count"] == 2
    assert payload["family_ids"] == ["F05", "F15"]
    assert payload["family_assignment_counts"] == {"F05": 18, "F15": 2}
    assert payload["family_orbit_sizes"] == {"F05": 18, "F15": 2}
    assert payload["orbit_size_sum"] == 20
    assert payload["core_size"] == 4
    assert payload["strict_edge_count"] == 36
    assert payload["path_length_counts"] == {"3": 20}
    assert payload["shared_endpoint_counts"] == {"1": 20}
    assert payload["selected_path_shape_counts"] == {"2:1:1:path=3": 20}


def test_t03_self_edge_lemma_packet_records_expected_local_shapes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packets = _family_packets(payload)

    assert set(packets) == set(EXPECTED_FAMILY_IDS)
    assert packets["F05"]["core_selected_rows"] == [
        [1, 2, 5, 7, 8],
        [2, 1, 3, 4, 8],
        [3, 0, 2, 4, 7],
        [6, 1, 3, 5, 7],
    ]
    assert packets["F05"]["strict_inequality"]["row"] == 6  # type: ignore[index]
    assert packets["F05"]["strict_inequality"]["witness_order"] == [7, 1, 3, 5]  # type: ignore[index]
    assert packets["F05"]["strict_inequality"]["outer_pair"] == [3, 7]  # type: ignore[index]
    assert packets["F05"]["strict_inequality"]["inner_pair"] == [1, 7]  # type: ignore[index]
    assert packets["F05"]["equality_chain"] == [[3, 7], [2, 3], [1, 2], [1, 7]]

    assert packets["F15"]["core_selected_rows"] == [
        [0, 1, 3, 4, 8],
        [1, 0, 2, 4, 5],
        [2, 1, 3, 5, 6],
        [3, 2, 4, 6, 7],
    ]
    assert packets["F15"]["strict_inequality"]["row"] == 0  # type: ignore[index]
    assert packets["F15"]["strict_inequality"]["witness_order"] == [1, 3, 4, 8]  # type: ignore[index]
    assert packets["F15"]["strict_inequality"]["outer_pair"] == [1, 4]  # type: ignore[index]
    assert packets["F15"]["strict_inequality"]["inner_pair"] == [3, 4]  # type: ignore[index]
    assert packets["F15"]["strict_inequality"]["inner_interval"] == [1, 2]  # type: ignore[index]
    assert packets["F15"]["equality_chain"] == [[1, 4], [1, 2], [2, 3], [3, 4]]

    for family_id, packet in packets.items():
        assert packet["local_lemma"]["review_status"] == "review_pending"  # type: ignore[index]
        assert "four listed selected rows" in packet["local_lemma"]["hypothesis_scope"]  # type: ignore[index]
        assert packet["replay"]["status"] == "self_edge"  # type: ignore[index]
        assert packet["replay"]["selected_row_count"] == 4  # type: ignore[index]
        assert packet["replay"]["strict_edge_count"] == 36  # type: ignore[index]
        assert packet["replay"]["self_edge_conflict_count"] == 1  # type: ignore[index]
        assert packet["replay"]["cycle_edge_count"] == 0  # type: ignore[index]
        assert packet["replay"]["primary_self_edge_conflict"]["row"] == packet["strict_inequality"]["row"]  # type: ignore[index]
        assert family_id in {"F05", "F15"}


def test_t03_self_edge_lemma_packet_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["template_id"] == "T03"
    assert summary["family_count"] == 2
    assert summary["assignment_count"] == 20
    assert summary["replay_statuses"] == ["self_edge", "self_edge"]


def test_t03_self_edge_lemma_packet_rejects_tampered_f05_equality_path() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packets = _family_packets(payload)
    packets["F05"]["distance_equality"]["path"][0]["next_pair"] = [2, 4]  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F05 distance_equality mismatch" in error for error in errors)
    assert any("expected T03 self-edge lemma packet" in error for error in errors)


def test_t03_self_edge_lemma_packet_rejects_tampered_f15_equality_path() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packets = _family_packets(payload)
    packets["F15"]["distance_equality"]["path"][1]["next_pair"] = [2, 4]  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F15 distance_equality mismatch" in error for error in errors)


def test_t03_self_edge_lemma_packet_rejects_tampered_f05_strict_row() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packets = _family_packets(payload)
    packets["F05"]["strict_inequality"]["row"] = 0  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F05 strict_inequality mismatch" in error for error in errors)


def test_t03_self_edge_lemma_packet_rejects_tampered_f15_inner_interval() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packets = _family_packets(payload)
    packets["F15"]["strict_inequality"]["inner_interval"] = [0, 1]  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F15 strict_inequality mismatch" in error for error in errors)


def test_t03_self_edge_lemma_packet_rejects_core_size_three_copy_error() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["core_size"] = 3
    packets = _family_packets(payload)
    packets["F05"]["replay"]["selected_row_count"] = 3  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("core_size mismatch" in error for error in errors)
    assert any("F05 replay selected_row_count mismatch" in error for error in errors)


def test_t03_self_edge_lemma_packet_rejects_missing_family() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["family_packets"] = [
        packet for packet in payload["family_packets"] if packet["family_id"] != "F15"
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("family packet ids mismatch" in error for error in errors)


def test_t03_self_edge_lemma_packet_rejects_duplicate_family_packet() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["family_packets"].append(copy.deepcopy(payload["family_packets"][0]))

    errors = validate_payload(payload, recompute=False)

    assert any("family_packets length mismatch" in error for error in errors)
    assert any("duplicate family packet id: F05" in error for error in errors)


def test_t03_self_edge_lemma_packet_rejects_missing_no_proof_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if item != "No proof of the n=9 case is claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("no-proof" in error for error in errors)


def test_t03_self_edge_lemma_packet_detects_source_packet_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    template = _template_record(sources)
    template["family_records"][0]["strict_inequality"]["row"] = 0  # F05 is the first T03 family.

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any(
        "source self-edge template packet invalid" in error
        or "source-bound T03 self-edge lemma packet failed" in error
        for error in errors
    )


def test_t03_self_edge_lemma_packet_detects_catalog_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    catalog = _catalog_record(sources)
    catalog["coverage"]["families"] = ["F05"]

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any(
        "source template lemma catalog invalid" in error
        or "source-bound T03 self-edge lemma packet failed" in error
        for error in errors
    )


@pytest.mark.artifact
def test_t03_self_edge_lemma_packet_artifact_matches_generator() -> None:
    source_payloads = load_source_payloads()
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == t03_self_edge_lemma_packet_payload(
        source_payloads["self_edge_packet"],
        source_payloads["template_catalog"],
    )


@pytest.mark.artifact
def test_t03_self_edge_lemma_packet_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py",
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
    assert payload["template_id"] == "T03"
    assert payload["family_count"] == 2
    assert payload["replay_statuses"] == ["self_edge", "self_edge"]


@pytest.mark.artifact
def test_t03_self_edge_lemma_packet_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "t03_self_edge_lemma_packet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py",
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


def test_t03_self_edge_lemma_packet_write_check_rejects_mismatched_paths(
    tmp_path: Path,
) -> None:
    out = tmp_path / "t03_self_edge_lemma_packet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py",
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
