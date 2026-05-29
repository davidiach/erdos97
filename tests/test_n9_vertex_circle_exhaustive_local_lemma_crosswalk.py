from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_exhaustive_local_lemma_crosswalk import (
    CLAIM_SCOPE,
    DEFAULT_CLASSIFICATION,
    DEFAULT_EXHAUSTIVE,
    DEFAULT_LOCAL_LEMMAS,
    DEFAULT_SIMPLE_REPLAY,
    assert_expected_exhaustive_local_lemma_crosswalk,
    exhaustive_local_lemma_crosswalk_payload,
    load_artifact,
    summary_json_payload,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def exhaustive() -> dict[str, object]:
    return load_artifact(DEFAULT_EXHAUSTIVE)


@pytest.fixture(scope="module")
def classification() -> dict[str, object]:
    return load_artifact(DEFAULT_CLASSIFICATION)


@pytest.fixture(scope="module")
def local_lemmas() -> dict[str, object]:
    return load_artifact(DEFAULT_LOCAL_LEMMAS)


@pytest.fixture(scope="module")
def simple_replay() -> dict[str, object]:
    return load_artifact(DEFAULT_SIMPLE_REPLAY)


def test_exhaustive_local_lemma_crosswalk_counts_and_scope(
    exhaustive: dict[str, object],
    classification: dict[str, object],
    local_lemmas: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = exhaustive_local_lemma_crosswalk_payload(
        exhaustive,
        classification,
        local_lemmas,
        simple_replay,
    )

    assert_expected_exhaustive_local_lemma_crosswalk(payload)
    assert payload["validation_status"] == "passed"
    assert payload["coverage_summary"] == {
        "exhaustive_frontier_assignment_count": 184,
        "classification_assignment_count": 184,
        "local_matched_assignment_count": 184,
        "family_count": 16,
        "self_edge_assignment_count": 158,
        "strict_cycle_assignment_count": 26,
    }
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not a global status update" in payload["claim_scope"]


def test_exhaustive_local_lemma_crosswalk_rejects_top_level_claim_scope_append(
    exhaustive: dict[str, object],
    classification: dict[str, object],
    local_lemmas: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = exhaustive_local_lemma_crosswalk_payload(
        exhaustive,
        classification,
        local_lemmas,
        simple_replay,
    )
    payload["claim_scope"] = CLAIM_SCOPE + " This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_exhaustive_local_lemma_crosswalk(payload)


def test_exhaustive_local_lemma_family_crosswalk(
    exhaustive: dict[str, object],
    classification: dict[str, object],
    local_lemmas: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = exhaustive_local_lemma_crosswalk_payload(
        exhaustive,
        classification,
        local_lemmas,
        simple_replay,
    )
    by_family = {item["family_id"]: item for item in payload["family_crosswalk"]}

    assert by_family["F09"] == {
        "family_id": "F09",
        "status": "self_edge",
        "template_id": "T01",
        "assignment_count": 6,
        "orbit_size": 6,
        "local_lemma_id": "nested_spoke_quotient_self_edge",
        "local_obstruction_group": "self_edge",
        "local_aggregate_instance_count": 1,
    }
    assert by_family["F12"] == {
        "family_id": "F12",
        "status": "strict_cycle",
        "template_id": "T10",
        "assignment_count": 18,
        "orbit_size": 18,
        "local_lemma_id": "t10_two_edge_strict_cycle",
        "local_obstruction_group": "strict_cycle",
        "local_aggregate_instance_count": 1,
    }


def test_exhaustive_local_lemma_crosswalk_rejects_status_count_drift(
    exhaustive: dict[str, object],
    classification: dict[str, object],
    local_lemmas: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    tampered = json.loads(json.dumps(classification))
    tampered["status_counts"]["self_edge"] = 157

    payload = exhaustive_local_lemma_crosswalk_payload(
        exhaustive,
        tampered,
        local_lemmas,
        simple_replay,
    )

    assert payload["validation_status"] == "failed"
    assert any(
        "classification expected-check failed" in error
        for error in payload["validation_errors"]
    )
    assert (
        "self_edge assignment-count mismatch across artifacts: (158, 157, 158)"
        in payload["validation_errors"]
    )


def test_exhaustive_local_lemma_crosswalk_rejects_family_drift(
    exhaustive: dict[str, object],
    classification: dict[str, object],
    local_lemmas: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    tampered = json.loads(json.dumps(classification))
    tampered["families"][0]["assignment_count"] = 17

    payload = exhaustive_local_lemma_crosswalk_payload(
        exhaustive,
        tampered,
        local_lemmas,
        simple_replay,
    )

    assert payload["validation_status"] == "failed"
    assert any(
        "classification expected-check failed" in error
        for error in payload["validation_errors"]
    )
    assert (
        "F01 assignment_count mismatch: classification 17 != local 18"
        in payload["validation_errors"]
    )


def test_exhaustive_local_lemma_crosswalk_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py",
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
    assert parsed["coverage_summary"]["exhaustive_frontier_assignment_count"] == 184
    assert parsed["coverage_summary"]["strict_cycle_assignment_count"] == 26


def test_exhaustive_local_lemma_crosswalk_summary_json_payload(
    exhaustive: dict[str, object],
    classification: dict[str, object],
    local_lemmas: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = exhaustive_local_lemma_crosswalk_payload(
        exhaustive,
        classification,
        local_lemmas,
        simple_replay,
    )
    summary = summary_json_payload(payload)

    assert "family_crosswalk" not in summary
    assert summary["schema"] == payload["schema"]
    assert summary["claim_scope"] == payload["claim_scope"]
    assert summary["coverage_summary"]["exhaustive_frontier_assignment_count"] == 184
    assert summary["local_replay_crosswalk_summary"]["matched_assignment_count"] == 184
    assert summary["validation_status"] == "passed"


def test_exhaustive_local_lemma_crosswalk_cli_summary_json(
    exhaustive: dict[str, object],
    classification: dict[str, object],
    local_lemmas: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = exhaustive_local_lemma_crosswalk_payload(
        exhaustive,
        classification,
        local_lemmas,
        simple_replay,
    )
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py",
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
