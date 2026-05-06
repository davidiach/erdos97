from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_obstruction_shapes import local_core_packet_summary
from erdos97.vertex_circle_quotient_replay import replay_local_core_bundle
from scripts.check_n9_vertex_circle_local_core_packet import (
    DEFAULT_ARTIFACT,
    load_artifact,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_local_core_packet_artifact_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not an independent review" in payload["claim_scope"]
    assert payload["family_count"] == 16
    assert payload["orbit_size_sum"] == 184
    assert payload["core_size_counts"] == {"3": 5, "4": 6, "5": 2, "6": 3}
    assert payload["max_core_size"] == 6


def test_local_core_packet_replays_all_recorded_statuses() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    replays = replay_local_core_bundle(payload)

    assert len(replays) == 16
    assert all(replay.status_matches_expected for replay in replays)
    assert [replay.family_id for replay in replays] == [f"F{idx:02d}" for idx in range(1, 17)]
    assert max(replay.result.selected_row_count for replay in replays) == 6


def test_local_core_packet_checker_rejects_tampered_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["family_count"] = 17

    errors = validate_payload(payload, recompute=False)

    assert any("family_count" in error or "family count" in error for error in errors)


def test_local_core_packet_checker_rejects_tampered_status() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["certificates"][0]["status"] = "strict_cycle"

    errors = validate_payload(payload, recompute=False)

    assert any("replay status mismatches" in error for error in errors)


def test_local_core_packet_checker_rejects_stale_family_rows() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["certificates"][0]["compact_selected_rows"] = payload["certificates"][3][
        "compact_selected_rows"
    ]
    payload["certificates"][0]["core_size"] = payload["certificates"][3]["core_size"]

    errors = validate_payload(payload)

    assert any("compact local-core packet" in error for error in errors)


def test_local_core_packet_checker_reports_malformed_payload_errors() -> None:
    errors = validate_payload({})

    assert errors
    assert any("expected packet counts failed" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_local_core_packet_artifact_matches_generator() -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == local_core_packet_summary()


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_local_core_packet_checker_passes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["family_count"] == 16
    assert summary["orbit_size_sum"] == 184


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_local_core_packet_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_local_core_packet.py",
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
    assert payload["family_count"] == 16
