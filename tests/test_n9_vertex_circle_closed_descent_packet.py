from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_closed_descent_packet import (
    DEFAULT_ARTIFACT,
    closed_descent_packet_summary,
    load_artifact,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


def test_closed_descent_packet_artifact_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a bridge proof" in payload["claim_scope"]
    assert payload["family_count"] == 16
    assert payload["orbit_size_sum"] == 184
    assert payload["source_status_counts"] == {"self_edge": 13, "strict_cycle": 3}
    assert payload["region_class_count_counts"] == {"1": 13, "2": 1, "3": 2}
    assert payload["closed_descent_cycle_length_counts"] == {
        "1": 13,
        "2": 1,
        "3": 2,
    }
    assert payload["max_region_class_count"] == 3


def test_closed_descent_packet_certificates_have_cycles() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert [item["family_id"] for item in payload["certificates"]] == [
        f"F{idx:02d}" for idx in range(1, 17)
    ]
    for certificate in payload["certificates"]:
        cycle = certificate["closed_descent_cycle"]
        assert cycle["type"] == "strict_quotient_closed_descent_cycle"
        assert cycle["class_count"] == certificate["region_class_count"]
        assert 1 <= cycle["cycle_length"] <= cycle["class_count"]
        assert len(cycle["cycle_edges"]) == cycle["cycle_length"]


def test_closed_descent_packet_checker_rejects_tampered_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["region_class_count_counts"] = {"1": 16}

    errors = validate_payload(payload, recompute=False)

    assert any("region class counts" in error for error in errors)


def test_closed_descent_packet_checker_rejects_tampered_cycle_type() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["certificates"][0]["closed_descent_cycle"]["type"] = "not_a_cycle"

    errors = validate_payload(payload, recompute=False)

    assert any("unexpected cycle type" in error for error in errors)


@pytest.mark.exhaustive
def test_closed_descent_packet_artifact_matches_generator() -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == closed_descent_packet_summary()


@pytest.mark.exhaustive
def test_closed_descent_packet_checker_passes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["family_count"] == 16
    assert summary["orbit_size_sum"] == 184


@pytest.mark.exhaustive
def test_closed_descent_packet_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_closed_descent_packet.py",
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
