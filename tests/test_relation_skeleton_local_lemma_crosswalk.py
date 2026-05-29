from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_local_lemma_replay_crosswalk import (
    DEFAULT_AGGREGATE,
    DEFAULT_SIMPLE_REPLAY,
)
from scripts.check_relation_skeleton_local_lemma_crosswalk import (
    CLAIM_SCOPE,
    DEFAULT_RELATION_SKELETONS,
    assert_expected_relation_local_crosswalk,
    crosswalk_payload,
    load_artifact,
    summary_json_payload,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def relation_skeletons() -> dict[str, object]:
    return load_artifact(DEFAULT_RELATION_SKELETONS)


@pytest.fixture(scope="module")
def aggregate() -> dict[str, object]:
    return load_artifact(DEFAULT_AGGREGATE)


@pytest.fixture(scope="module")
def simple_replay() -> dict[str, object]:
    return load_artifact(DEFAULT_SIMPLE_REPLAY)


def test_relation_local_crosswalk_expected_counts_and_scope(
    relation_skeletons: dict[str, object],
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = crosswalk_payload(relation_skeletons, aggregate, simple_replay)

    assert_expected_relation_local_crosswalk(payload)
    assert payload["validation_status"] == "passed"
    assert payload["coverage_summary"] == {
        "relation_skeleton_count": 16,
        "local_family_count": 16,
        "matched_family_count": 16,
        "matched_assignment_count": 184,
        "self_edge_family_count": 13,
        "self_edge_assignment_count": 158,
        "strict_cycle_family_count": 3,
        "strict_cycle_assignment_count": 26,
        "expected_family_count": 16,
        "expected_assignment_count": 184,
    }
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not a global status update" in payload["claim_scope"]


def test_relation_local_crosswalk_rejects_top_level_claim_scope_append(
    relation_skeletons: dict[str, object],
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = crosswalk_payload(relation_skeletons, aggregate, simple_replay)
    payload["claim_scope"] = CLAIM_SCOPE + " This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_relation_local_crosswalk(payload)


def test_relation_local_crosswalk_family_records(
    relation_skeletons: dict[str, object],
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = crosswalk_payload(relation_skeletons, aggregate, simple_replay)
    by_family = {item["family_id"]: item for item in payload["family_crosswalk"]}

    assert by_family["F02"] == {
        "family_id": "F02",
        "skeleton_id": "VC-T08-F02-strict-self-edge",
        "lemma_id": "nested_spoke_quotient_self_edge",
        "template_id": "T08",
        "relation_contradiction_type": "strict_self_edge",
        "local_obstruction_group": "self_edge",
        "assignment_count": 18,
        "orbit_size": 18,
        "relation_source_packet": (
            "data/certificates/n9_vertex_circle_t08_self_edge_lemma_packet.json"
        ),
        "relation_equality_chain_count": 1,
        "relation_strict_edge_count": 1,
        "simple_obstruction_kind": "reflexive_strict_edge",
        "simple_replayed_step_count": 5,
    }
    assert by_family["F12"] == {
        "family_id": "F12",
        "skeleton_id": "VC-T10-F12-strict-directed-cycle",
        "lemma_id": "t10_two_edge_strict_cycle",
        "template_id": "T10",
        "relation_contradiction_type": "strict_directed_cycle",
        "local_obstruction_group": "strict_cycle",
        "assignment_count": 18,
        "orbit_size": 18,
        "relation_source_packet": (
            "data/certificates/n9_vertex_circle_t10_strict_cycle_lemma_packet.json"
        ),
        "relation_equality_chain_count": 2,
        "relation_strict_edge_count": 2,
        "simple_obstruction_kind": "directed_strict_cycle",
        "simple_replayed_step_count": 2,
    }


def test_relation_local_crosswalk_rejects_relation_assignment_drift(
    relation_skeletons: dict[str, object],
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    tampered = json.loads(json.dumps(relation_skeletons))
    tampered["skeletons"][0]["coverage"]["assignment_count"] = 5

    payload = crosswalk_payload(tampered, aggregate, simple_replay)

    assert payload["validation_status"] == "failed"
    assert (
        "F09 assignment_count mismatch: relation 5 != local 6"
        in payload["validation_errors"]
    )


def test_relation_local_crosswalk_rejects_contradiction_drift(
    relation_skeletons: dict[str, object],
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    tampered = json.loads(json.dumps(relation_skeletons))
    tampered["skeletons"][0]["contradiction_type"] = "strict_directed_cycle"

    payload = crosswalk_payload(tampered, aggregate, simple_replay)

    assert payload["validation_status"] == "failed"
    assert (
        "F09 obstruction group mismatch: relation expects 'strict_cycle', "
        "local has 'self_edge'"
    ) in payload["validation_errors"]


def test_relation_local_crosswalk_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_relation_skeleton_local_lemma_crosswalk.py",
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
    assert parsed["coverage_summary"]["matched_family_count"] == 16


def test_relation_local_crosswalk_summary_json_payload(
    relation_skeletons: dict[str, object],
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = crosswalk_payload(relation_skeletons, aggregate, simple_replay)
    summary = summary_json_payload(payload)

    assert "family_crosswalk" not in summary
    assert summary["schema"] == payload["schema"]
    assert summary["claim_scope"] == payload["claim_scope"]
    assert summary["coverage_summary"]["matched_assignment_count"] == 184
    assert summary["local_replay_crosswalk_summary"]["matched_assignment_count"] == 184
    assert summary["validation_status"] == "passed"


def test_relation_local_crosswalk_cli_summary_json(
    relation_skeletons: dict[str, object],
    aggregate: dict[str, object],
    simple_replay: dict[str, object],
) -> None:
    payload = crosswalk_payload(relation_skeletons, aggregate, simple_replay)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_relation_skeleton_local_lemma_crosswalk.py",
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
