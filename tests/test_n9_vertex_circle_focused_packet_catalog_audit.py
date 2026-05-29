from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_focused_packet_catalog_audit import (
    CLAIM_SCOPE,
    DEFAULT_LOCAL_LEMMAS,
    DEFAULT_PACKET_PATHS,
    DEFAULT_TEMPLATE_CATALOG,
    DEFAULT_TEMPLATE_PACKET_PATHS,
    assert_expected_focused_packet_catalog_audit,
    focused_packet_catalog_audit_payload,
    load_json,
    summary_json_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_focused_packet_catalog_audit_counts_and_scope() -> None:
    payload = focused_packet_catalog_audit_payload()

    assert_expected_focused_packet_catalog_audit(payload)
    summary = payload["focused_packet_catalog_audit"]
    assert payload["validation_status"] == "passed"
    assert payload["status"] == "REVIEW_PENDING_FOCUSED_PACKET_CATALOG_AUDIT"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "bookkeeping only" in payload["interpretation"]
    assert "does not prove packet soundness" in payload["claim_scope"]
    assert "counterexample" in payload["claim_scope"]
    assert "official/global status update" in payload["claim_scope"]
    assert summary["template_ids"] == [f"T{index:02d}" for index in range(1, 13)]
    assert summary["covered_assignment_count"] == 184
    assert summary["covered_family_count"] == 16
    assert summary["status_counts"] == {"self_edge": 9, "strict_cycle": 3}
    assert summary["status_assignment_counts"] == {"self_edge": 158, "strict_cycle": 26}
    assert summary["source_template_packet_count"] == 12
    assert summary["source_template_mismatch_count"] == 0
    assert summary["source_template_allowed_omitted_field_count"] == 14


def test_focused_packet_catalog_audit_rejects_top_level_claim_scope_append() -> None:
    payload = focused_packet_catalog_audit_payload()
    payload["claim_scope"] = CLAIM_SCOPE + " This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_focused_packet_catalog_audit(payload)


def test_focused_packet_catalog_audit_rejects_packet_coverage_drift(
    tmp_path: Path,
) -> None:
    t01_path = tmp_path / "t01_packet.json"
    t01_packet = load_json(DEFAULT_PACKET_PATHS["T01"])
    t01_packet["assignment_ids"][0] = "A999"
    _write_json(t01_path, t01_packet)
    packet_paths = dict(DEFAULT_PACKET_PATHS)
    packet_paths["T01"] = t01_path

    payload = focused_packet_catalog_audit_payload(packet_paths=packet_paths)

    assert payload["validation_status"] == "failed"
    assert (
        "T01: packet coverage does not match catalog"
        in payload["validation_errors"]
    )
    summary = payload["focused_packet_catalog_audit"]
    assert summary["catalog_coverage_mismatch_count"] == 1


def test_focused_packet_catalog_audit_rejects_template_catalog_drift(
    tmp_path: Path,
) -> None:
    catalog_path = tmp_path / "template_catalog.json"
    catalog = load_json(DEFAULT_TEMPLATE_CATALOG)
    catalog["templates"][0]["coverage"]["assignment_count"] = 7
    _write_json(catalog_path, catalog)

    payload = focused_packet_catalog_audit_payload(template_catalog_path=catalog_path)

    assert payload["validation_status"] == "failed"
    assert "T01: source_catalog_record mismatch" in payload["validation_errors"]
    assert (
        "T01: packet coverage does not match catalog"
        in payload["validation_errors"]
    )
    summary = payload["focused_packet_catalog_audit"]
    assert summary["source_catalog_mismatch_count"] == 1
    assert summary["catalog_coverage_mismatch_count"] == 1


def test_focused_packet_catalog_audit_rejects_local_lemma_crosscheck_drift(
    tmp_path: Path,
) -> None:
    local_path = tmp_path / "local_lemmas.json"
    local_lemmas = load_json(DEFAULT_LOCAL_LEMMAS)
    local_lemmas["focused_note_crosscheck"][0]["covered_assignment_count"] = 5
    _write_json(local_path, local_lemmas)

    payload = focused_packet_catalog_audit_payload(local_lemmas_path=local_path)

    assert payload["validation_status"] == "failed"
    assert "T01: aggregate focused crosscheck mismatch" in payload["validation_errors"]
    summary = payload["focused_packet_catalog_audit"]
    assert summary["focused_crosscheck_mismatch_count"] == 1


def test_focused_packet_catalog_audit_rejects_source_template_record_drift(
    tmp_path: Path,
) -> None:
    t01_path = tmp_path / "t01_packet.json"
    t01_packet = load_json(DEFAULT_PACKET_PATHS["T01"])
    t01_packet["source_template_record"]["strict_edge_count"] = 999
    _write_json(t01_path, t01_packet)
    packet_paths = dict(DEFAULT_PACKET_PATHS)
    packet_paths["T01"] = t01_path

    payload = focused_packet_catalog_audit_payload(packet_paths=packet_paths)

    assert payload["validation_status"] == "failed"
    assert (
        "T01: source_template_record stored field mismatch: ['strict_edge_count']"
        in payload["validation_errors"]
    )
    summary = payload["focused_packet_catalog_audit"]
    assert summary["source_template_mismatch_count"] == 1
    assert summary["source_template_field_mismatch_count"] == 1


def test_focused_packet_catalog_audit_rejects_source_template_packet_drift(
    tmp_path: Path,
) -> None:
    self_edge_path = tmp_path / "self_edge_template_packet.json"
    self_edge_packet = load_json(DEFAULT_TEMPLATE_PACKET_PATHS["self_edge"])
    self_edge_packet["templates"][0]["strict_edge_count"] = 999
    _write_json(self_edge_path, self_edge_packet)
    template_packet_paths = dict(DEFAULT_TEMPLATE_PACKET_PATHS)
    template_packet_paths["self_edge"] = self_edge_path

    payload = focused_packet_catalog_audit_payload(
        template_packet_paths=template_packet_paths,
    )

    assert payload["validation_status"] == "failed"
    assert (
        "T01: source_template_record stored field mismatch: ['strict_edge_count']"
        in payload["validation_errors"]
    )
    summary = payload["focused_packet_catalog_audit"]
    assert summary["source_template_mismatch_count"] == 1
    assert summary["source_template_field_mismatch_count"] == 1


def test_focused_packet_catalog_audit_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    parsed = json.loads(result.stdout)
    assert parsed["validation_status"] == "passed"
    assert parsed["focused_packet_catalog_audit"]["covered_assignment_count"] == 184
    assert parsed["focused_packet_catalog_audit"]["focused_crosscheck_count"] == 12


def test_focused_packet_catalog_audit_summary_json_payload() -> None:
    payload = focused_packet_catalog_audit_payload()
    summary = summary_json_payload(payload)

    assert summary["schema"] == payload["schema"]
    assert summary["claim_scope"] == payload["claim_scope"]
    assert summary["validation_status"] == "passed"
    assert summary["packet_artifacts"] == payload["packet_artifacts"]
    assert summary["focused_packet_catalog_audit"]["covered_assignment_count"] == 184
    assert summary["focused_packet_catalog_audit"]["focused_crosscheck_count"] == 12
    assert "packet_records" not in summary["focused_packet_catalog_audit"]


def test_focused_packet_catalog_audit_cli_summary_json() -> None:
    payload = focused_packet_catalog_audit_payload()
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py",
            "--check",
            "--assert-expected",
            "--summary-json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout) == summary_json_payload(payload)
