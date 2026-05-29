from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_local_lemma_replay_crosswalk import (
    CLAIM_SCOPE,
    DEFAULT_AGGREGATE,
    DEFAULT_SIMPLE_REPLAY,
    assert_expected_replay_crosswalk,
    crosswalk_payload,
    load_artifact,
    summary_json_payload,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def aggregate() -> dict[str, object]:
    return load_artifact(DEFAULT_AGGREGATE)


@pytest.fixture(scope="module")
def simple_replay() -> dict[str, object]:
    return load_artifact(DEFAULT_SIMPLE_REPLAY)


def test_replay_crosswalk_expected_counts_and_scope(
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = crosswalk_payload(aggregate, simple_replay)

    assert_expected_replay_crosswalk(payload)
    assert payload["validation_status"] == "passed"
    assert payload["coverage_summary"] == {
        "aggregate_family_count": 16,
        "simple_replay_family_count": 16,
        "matched_family_count": 16,
        "matched_assignment_count": 184,
        "self_edge_family_count": 13,
        "self_edge_assignment_count": 158,
        "strict_cycle_family_count": 3,
        "strict_cycle_assignment_count": 26,
        "expected_family_count": 16,
        "expected_assignment_count": 184,
    }
    assert payload["focused_crosscheck_summary"] == {
        "focused_template_count": 12,
        "focused_family_count": 16,
        "focused_assignment_count": 184,
        "focused_family_ids": [f"F{index:02d}" for index in range(1, 17)],
    }
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not a global status update" in payload["claim_scope"]


def test_replay_crosswalk_rejects_top_level_claim_scope_append(
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = crosswalk_payload(aggregate, simple_replay)
    payload["claim_scope"] = CLAIM_SCOPE + " This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_replay_crosswalk(payload)


def test_replay_crosswalk_family_records(
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = crosswalk_payload(aggregate, simple_replay)
    by_family = {item["family_id"]: item for item in payload["family_crosswalk"]}

    assert by_family["F09"] == {
        "family_id": "F09",
        "lemma_id": "nested_spoke_quotient_self_edge",
        "obstruction_group": "self_edge",
        "template_id": "T01",
        "assignment_count": 6,
        "orbit_size": 6,
        "aggregate_instance_count": 1,
        "simple_obstruction_kind": "reflexive_strict_edge",
        "simple_replayed_step_count": 3,
    }
    assert by_family["F12"] == {
        "family_id": "F12",
        "lemma_id": "t10_two_edge_strict_cycle",
        "obstruction_group": "strict_cycle",
        "template_id": "T10",
        "assignment_count": 18,
        "orbit_size": 18,
        "aggregate_instance_count": 1,
        "simple_obstruction_kind": "directed_strict_cycle",
        "simple_replayed_step_count": 2,
    }


def test_replay_crosswalk_rejects_simple_assignment_drift(
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    tampered = json.loads(json.dumps(simple_replay))
    tampered["self_edge"]["records"][0]["assignment_count"] = 7

    payload = crosswalk_payload(aggregate, tampered)

    assert payload["validation_status"] == "failed"
    assert (
        "F09 assignment_count mismatch: aggregate 6 != simple 7"
        in payload["validation_errors"]
    )


def test_replay_crosswalk_rejects_focused_assignment_drift(
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    tampered = json.loads(json.dumps(aggregate))
    tampered["focused_note_crosscheck"][0]["families_checked"][0][
        "assignment_count"
    ] = 5

    payload = crosswalk_payload(tampered, simple_replay)

    assert payload["validation_status"] == "failed"
    assert (
        "F09 focused assignment mismatch: 5 != simple 6"
        in payload["validation_errors"]
    )


def test_replay_crosswalk_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py",
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
    assert parsed["coverage_summary"]["matched_assignment_count"] == 184
    assert parsed["focused_crosscheck_summary"]["focused_family_count"] == 16


def test_replay_crosswalk_summary_json_payload(
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = crosswalk_payload(aggregate, simple_replay)
    summary = summary_json_payload(payload)

    assert "family_crosswalk" not in summary
    assert summary["schema"] == payload["schema"]
    assert summary["claim_scope"] == payload["claim_scope"]
    assert summary["coverage_summary"]["matched_assignment_count"] == 184
    assert summary["focused_crosscheck_summary"]["focused_family_count"] == 16
    assert summary["validation_status"] == "passed"


def test_replay_crosswalk_cli_summary_json(
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = crosswalk_payload(aggregate, simple_replay)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py",
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
