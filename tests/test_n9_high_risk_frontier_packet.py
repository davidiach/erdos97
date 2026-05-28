from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_high_risk_frontier_packet import (
    EXPECTED_NON_EAR_INDICES,
    EXPECTED_SELECTED_FAMILY_COUNTS,
    EXPECTED_SELECTED_STATUS_COUNTS,
    assert_expected_payload,
    build_payload,
)
from scripts.check_n9_high_risk_frontier_packet import (
    DEFAULT_ARTIFACT,
    load_artifact,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_high_risk_frontier_artifact_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_payload(payload)
    assert payload["summary"]["selected_assignment_count"] == 62
    assert payload["summary"]["selected_family_counts"] == EXPECTED_SELECTED_FAMILY_COUNTS
    assert payload["summary"]["selected_status_counts"] == EXPECTED_SELECTED_STATUS_COUNTS
    assert payload["summary"]["non_ear_zero_based_indices"] == EXPECTED_NON_EAR_INDICES
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]


def test_high_risk_frontier_artifact_is_triangle_slice() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert all(
        record["mutual_edge_triangle_count"] > 0 for record in payload["assignments"]
    )
    assert all(
        record["simple_obstruction_a_trigger_count"] == 0
        for record in payload["assignments"]
    )
    assert all(
        len(record["first_radius_blocker"]) == 4 for record in payload["assignments"]
    )
    assert {
        record["kill_reason"] for record in payload["assignments"]
    } == {"vertex_circle_self_edge", "vertex_circle_strict_cycle"}


def test_high_risk_frontier_family_representatives_replay() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    for family in payload["families"]:
        replay = family["representative_radius_blocker_replay"]
        assert replay["radius_blocker_ok"] is True
        assert replay["incidence_survivors"] == 1
        assert replay["all_incidence_survivors_obstructed"] is True
        assert replay["vertex_circle_status_counts"] == {
            family["vertex_circle_status"]: 1
        }


def test_high_risk_frontier_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["selected_assignment_count"] == 62


def test_high_risk_frontier_rejects_missing_no_proof_warning() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item
        for item in payload["interpretation"]
        if item != "No proof of Erdos Problem #97 and no counterexample are claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("no-proof" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_high_risk_frontier_artifact_matches_generator() -> None:
    assert load_artifact(DEFAULT_ARTIFACT) == build_payload()


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_high_risk_frontier_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_high_risk_frontier_packet.py",
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
    assert payload["selected_assignment_count"] == 62
