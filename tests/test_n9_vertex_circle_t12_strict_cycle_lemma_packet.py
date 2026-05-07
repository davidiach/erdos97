from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_t12_strict_cycle_lemma_packet import (
    EXPECTED_CYCLE_STEPS,
    assert_expected_t12_strict_cycle_lemma_packet,
    t12_strict_cycle_lemma_packet_payload,
)
from scripts.check_n9_vertex_circle_t12_strict_cycle_lemma_packet import (
    DEFAULT_ARTIFACT,
    load_artifact,
    load_source_payloads,
    summary_payload,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def _f16(payload: dict[str, object]) -> dict[str, object]:
    return payload["family_packets"][0]  # type: ignore[index]


def _template_record(source_payloads: dict[str, object]) -> dict[str, object]:
    for template in source_payloads["strict_cycle_packet"]["templates"]:  # type: ignore[index]
        if template["template_id"] == "T12":
            return template
    raise AssertionError("missing T12 template")


def _catalog_record(source_payloads: dict[str, object]) -> dict[str, object]:
    for template in source_payloads["template_catalog"]["templates"]:  # type: ignore[index]
        if template["template_id"] == "T12":
            return template
    raise AssertionError("missing T12 catalog record")


def test_t12_strict_cycle_lemma_packet_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_t12_strict_cycle_lemma_packet(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "proof-mining scaffolding only" in payload["claim_scope"]
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an independent review" in payload["claim_scope"]
    assert payload["template_id"] == "T12"
    assert (
        payload["template_key"]
        == "strict_cycle|rows=6|strict_edges=54|cycle=3|spans=3:1x3"
    )
    assert payload["assignment_count"] == 2
    assert payload["family_count"] == 1
    assert payload["family_ids"] == ["F16"]
    assert payload["family_assignment_counts"] == {"F16": 2}
    assert payload["family_orbit_sizes"] == {"F16": 2}
    assert payload["orbit_size_sum"] == 2
    assert payload["core_size"] == 6
    assert payload["cycle_length"] == 3
    assert payload["strict_edge_count"] == 54
    assert payload["cycle_length_counts"] == {"3": 2}
    assert payload["connector_path_length_counts"] == {"1": 4, "2": 2}
    assert payload["span_signature_counts"] == {"3:1,3:1,3:1": 2}
    assert payload["cycle_span_counts"] == [
        {"count": 3, "inner_span": 1, "outer_span": 3},
    ]


def test_t12_strict_cycle_lemma_packet_records_expected_directed_cycle() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _f16(payload)

    assert packet["core_selected_rows"] == [
        [0, 1, 3, 6, 7],
        [1, 2, 4, 7, 8],
        [2, 0, 3, 5, 8],
        [3, 0, 1, 4, 6],
        [4, 1, 2, 5, 7],
        [8, 0, 2, 5, 6],
    ]
    assert packet["cycle_steps"] == EXPECTED_CYCLE_STEPS
    assert packet["cycle_pair_chain"] == [
        {
            "cycle_step": 0,
            "strict_from_outer_pair": [0, 3],
            "strict_to_inner_pair": [0, 8],
            "equality_chain_to_next_outer_pair": [[0, 8], [2, 8]],
            "next_outer_pair": [2, 8],
        },
        {
            "cycle_step": 1,
            "strict_from_outer_pair": [2, 8],
            "strict_to_inner_pair": [2, 4],
            "equality_chain_to_next_outer_pair": [[2, 4], [1, 4], [1, 7]],
            "next_outer_pair": [1, 7],
        },
        {
            "cycle_step": 2,
            "strict_from_outer_pair": [1, 7],
            "strict_to_inner_pair": [1, 3],
            "equality_chain_to_next_outer_pair": [[1, 3], [0, 3]],
            "next_outer_pair": [0, 3],
        },
    ]
    assert len(packet["cycle_steps"][0]["equality_to_next_outer_pair"]["path"]) == 1  # type: ignore[index]
    assert len(packet["cycle_steps"][1]["equality_to_next_outer_pair"]["path"]) == 2  # type: ignore[index]
    assert len(packet["cycle_steps"][2]["equality_to_next_outer_pair"]["path"]) == 1  # type: ignore[index]
    assert packet["local_lemma"]["review_status"] == "review_pending"  # type: ignore[index]
    assert "six listed selected rows" in packet["local_lemma"]["hypothesis_scope"]  # type: ignore[index]
    assert "directed strict cycle" in packet["local_lemma"]["contradiction"]  # type: ignore[index]
    assert "self-edge" not in packet["local_lemma"]["contradiction"]  # type: ignore[index]
    assert packet["replay"]["status"] == "strict_cycle"  # type: ignore[index]
    assert packet["replay"]["selected_row_count"] == 6  # type: ignore[index]
    assert packet["replay"]["strict_edge_count"] == 54  # type: ignore[index]
    assert packet["replay"]["self_edge_conflict_count"] == 0  # type: ignore[index]
    assert packet["replay"]["cycle_edge_count"] == 3  # type: ignore[index]
    assert "primary_self_edge_conflict" not in packet["replay"]  # type: ignore[operator]
    for edge in packet["replay"]["cycle_edges"]:  # type: ignore[index]
        assert "outer_span" not in edge
        assert "inner_span" not in edge


def test_t12_strict_cycle_lemma_packet_rejects_tampered_replay_classes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _f16(payload)
    packet["replay"]["cycle_edges"][0]["inner_class"] = [0, 1]  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F16 replay cycle edge 0 inner_class mismatch" in error for error in errors)
    assert any("quotient classes must be distinct" in error for error in errors)


def test_t12_strict_cycle_lemma_packet_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["template_id"] == "T12"
    assert summary["family_count"] == 1
    assert summary["assignment_count"] == 2
    assert summary["cycle_length"] == 3
    assert summary["replay_statuses"] == ["strict_cycle"]


def test_t12_strict_cycle_lemma_packet_rejects_tampered_step0_connector() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _f16(payload)
    packet["cycle_steps"][0]["equality_to_next_outer_pair"]["end_pair"] = [0, 5]  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F16 cycle_steps mismatch" in error for error in errors)
    assert any("expected T12 strict-cycle lemma packet" in error for error in errors)


def test_t12_strict_cycle_lemma_packet_rejects_tampered_step1_closure() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _f16(payload)
    packet["cycle_steps"][1]["equality_to_next_outer_pair"]["path"][1]["next_pair"] = [0, 3]  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F16 cycle_steps mismatch" in error for error in errors)


def test_t12_strict_cycle_lemma_packet_rejects_tampered_strict_row() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _f16(payload)
    packet["cycle_steps"][0]["strict_inequality"]["row"] = 0  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F16 cycle_steps mismatch" in error for error in errors)


def test_t12_strict_cycle_lemma_packet_rejects_tampered_core_rows() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _f16(payload)
    packet["core_selected_rows"][0] = [0, 1, 3, 5, 7]  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F16 core_selected_rows mismatch" in error for error in errors)


def test_t12_strict_cycle_lemma_packet_rejects_self_edge_copy_error() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _f16(payload)
    packet["local_lemma"]["contradiction"] = "The strict graph has a reflexive strict edge."  # type: ignore[index]
    packet["replay"]["primary_self_edge_conflict"] = {"row": 8}  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("must mention a directed strict cycle" in error for error in errors)
    assert any("must not include primary_self_edge_conflict" in error for error in errors)


def test_t12_strict_cycle_lemma_packet_rejects_missing_family() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["family_packets"] = []

    errors = validate_payload(payload, recompute=False)

    assert any("family packet ids mismatch" in error for error in errors)


def test_t12_strict_cycle_lemma_packet_rejects_t11_sized_copy_error() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["core_size"] = 4
    payload["strict_edge_count"] = 36
    packet = _f16(payload)
    packet["core_size"] = 4
    packet["replay"]["selected_row_count"] = 4  # type: ignore[index]
    packet["replay"]["strict_edge_count"] = 36  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("core_size mismatch" in error for error in errors)
    assert any("strict_edge_count mismatch" in error for error in errors)


def test_t12_strict_cycle_lemma_packet_rejects_empty_connector_copy_error() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _f16(payload)
    packet["cycle_steps"][0]["equality_to_next_outer_pair"] = {  # type: ignore[index]
        "end_pair": [0, 8],
        "path": [],
        "start_pair": [0, 8],
    }

    errors = validate_payload(payload, recompute=False)

    assert any("F16 cycle_steps mismatch" in error for error in errors)


def test_t12_strict_cycle_lemma_packet_rejects_duplicate_family_packet() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["family_packets"].append(copy.deepcopy(payload["family_packets"][0]))

    errors = validate_payload(payload, recompute=False)

    assert any("family_packets length mismatch" in error for error in errors)
    assert any("duplicate family packet id: F16" in error for error in errors)


def test_t12_strict_cycle_lemma_packet_rejects_extra_family_packet() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    extra = copy.deepcopy(payload["family_packets"][0])
    extra["family_id"] = "F99"
    payload["family_packets"].append(extra)

    errors = validate_payload(payload, recompute=False)

    assert any("family_packets length mismatch" in error for error in errors)
    assert any("family packet ids mismatch" in error for error in errors)


def test_t12_strict_cycle_lemma_packet_rejects_missing_no_proof_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if item != "No proof of the n=9 case is claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("no-proof" in error for error in errors)


def test_t12_strict_cycle_lemma_packet_detects_source_packet_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    template = _template_record(sources)
    template["family_records"][0]["cycle_steps"][0]["strict_inequality"]["row"] = 0  # type: ignore[index]

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any(
        "source strict-cycle template packet invalid" in error
        or "source-bound T12 strict-cycle lemma packet failed" in error
        for error in errors
    )


def test_t12_strict_cycle_lemma_packet_detects_catalog_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    catalog = _catalog_record(sources)
    catalog["hypothesis_shape"]["cycle_length"] = 2  # type: ignore[index]

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any(
        "source template lemma catalog invalid" in error
        or "source-bound T12 strict-cycle lemma packet failed" in error
        for error in errors
    )


@pytest.mark.artifact
def test_t12_strict_cycle_lemma_packet_artifact_matches_generator() -> None:
    source_payloads = load_source_payloads()
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == t12_strict_cycle_lemma_packet_payload(
        source_payloads["strict_cycle_packet"],
        source_payloads["template_catalog"],
    )


@pytest.mark.artifact
def test_t12_strict_cycle_lemma_packet_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py",
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
    assert payload["template_id"] == "T12"
    assert payload["family_count"] == 1
    assert payload["cycle_length"] == 3
    assert payload["replay_statuses"] == ["strict_cycle"]


@pytest.mark.artifact
def test_t12_strict_cycle_lemma_packet_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "t12_strict_cycle_lemma_packet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py",
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


def test_t12_strict_cycle_lemma_packet_write_check_rejects_mismatched_paths(
    tmp_path: Path,
) -> None:
    out = tmp_path / "t12_strict_cycle_lemma_packet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py",
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
