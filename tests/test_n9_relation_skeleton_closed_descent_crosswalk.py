from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_relation_skeleton_closed_descent_crosswalk import (
    DEFAULT_ARTIFACT,
    DEFAULT_CLOSED_DESCENT,
    DEFAULT_RELATION_SKELETONS,
    assert_expected_relation_closed_descent_crosswalk,
    load_artifact,
    relation_closed_descent_crosswalk_payload,
    summary_payload,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def relation_skeletons() -> dict[str, object]:
    return load_artifact(DEFAULT_RELATION_SKELETONS)


@pytest.fixture(scope="module")
def closed_descent() -> dict[str, object]:
    return load_artifact(DEFAULT_CLOSED_DESCENT)


def test_relation_closed_descent_crosswalk_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_relation_closed_descent_crosswalk(payload)
    assert payload["status"] == "REVIEW_PENDING_PACKET_AUDIT"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert payload["family_count"] == 16
    assert payload["orbit_size_sum"] == 184
    assert payload["contradiction_type_counts"] == {
        "strict_directed_cycle": 3,
        "strict_self_edge": 13,
    }
    assert payload["region_class_count_counts"] == {"1": 13, "2": 1, "3": 2}
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not local-lemma completeness" in payload["claim_scope"]
    assert "not a bridge proof" in payload["claim_scope"]


def test_relation_closed_descent_crosswalk_family_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    by_family = {item["family_id"]: item for item in payload["family_crosswalk"]}

    assert by_family["F09"] == {
        "assignment_count": 6,
        "descent_core_size": 3,
        "descent_cycle_length": 1,
        "descent_orbit_size": 6,
        "descent_region_class_count": 1,
        "descent_source_status": "self_edge",
        "descent_strict_edge_count": 27,
        "family_id": "F09",
        "relation_contradiction_type": "strict_self_edge",
        "relation_equality_chain_count": 1,
        "relation_source_packet": (
            "data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json"
        ),
        "relation_strict_edge_count": 1,
        "skeleton_id": "VC-T01-F09-strict-self-edge",
        "template_id": "T01",
    }
    assert by_family["F12"] == {
        "assignment_count": 18,
        "descent_core_size": 4,
        "descent_cycle_length": 2,
        "descent_orbit_size": 18,
        "descent_region_class_count": 2,
        "descent_source_status": "strict_cycle",
        "descent_strict_edge_count": 36,
        "family_id": "F12",
        "relation_contradiction_type": "strict_directed_cycle",
        "relation_equality_chain_count": 2,
        "relation_source_packet": (
            "data/certificates/n9_vertex_circle_t10_strict_cycle_lemma_packet.json"
        ),
        "relation_strict_edge_count": 2,
        "skeleton_id": "VC-T10-F12-strict-directed-cycle",
        "template_id": "T10",
    }


def test_relation_closed_descent_crosswalk_rejects_tampered_status() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["family_crosswalk"][0]["descent_source_status"] = "strict_cycle"

    errors = validate_payload(payload, recompute=False)

    assert any("status mismatch" in error for error in errors)


def test_relation_closed_descent_crosswalk_rejects_tampered_cycle_length() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["family_crosswalk"][11]["descent_cycle_length"] = 3

    errors = validate_payload(payload, recompute=False)

    assert any("region class count must match cycle length" in error for error in errors)


def test_relation_closed_descent_crosswalk_rejects_source_assignment_drift(
    relation_skeletons: dict[str, object],
    closed_descent: dict[str, object],
) -> None:
    tampered = json.loads(json.dumps(relation_skeletons))
    tampered["skeletons"][0]["coverage"]["assignment_count"] = 5

    with pytest.raises(AssertionError, match="assignment count"):
        relation_closed_descent_crosswalk_payload(tampered, closed_descent)


def test_relation_closed_descent_crosswalk_rejects_source_region_drift(
    relation_skeletons: dict[str, object],
    closed_descent: dict[str, object],
) -> None:
    tampered = json.loads(json.dumps(closed_descent))
    by_family = {item["family_id"]: item for item in tampered["certificates"]}
    by_family["F07"]["region_class_count"] = 2
    by_family["F07"]["closed_descent_cycle"]["class_count"] = 2
    by_family["F12"]["region_class_count"] = 3
    by_family["F12"]["closed_descent_cycle"]["class_count"] = 3

    with pytest.raises(AssertionError, match="F07 region class count mismatch"):
        relation_closed_descent_crosswalk_payload(relation_skeletons, tampered)


@pytest.mark.exhaustive
def test_relation_closed_descent_crosswalk_artifact_matches_generator(
    relation_skeletons: dict[str, object],
    closed_descent: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == relation_closed_descent_crosswalk_payload(
        relation_skeletons,
        closed_descent,
    )


@pytest.mark.exhaustive
def test_relation_closed_descent_crosswalk_checker_passes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["family_count"] == 16
    assert summary["orbit_size_sum"] == 184


@pytest.mark.exhaustive
def test_relation_closed_descent_crosswalk_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py",
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
