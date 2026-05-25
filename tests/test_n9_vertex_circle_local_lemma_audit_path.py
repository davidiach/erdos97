from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_n9_vertex_circle_local_lemma_audit_path import (
    EXPECTED_HANDOFF_EDGES,
    EXPECTED_INPUT_ARTIFACT_COUNT,
    EXPECTED_LAYER_IDS,
    assert_expected_local_lemma_audit_path,
    local_lemma_audit_path_payload,
)
from scripts.check_n9_vertex_circle_focused_minireplay_crosswalk import (
    focused_minireplay_crosswalk_payload,
)
from scripts.check_n9_vertex_circle_local_lemma_replay_crosswalk import (
    DEFAULT_AGGREGATE,
    DEFAULT_SIMPLE_REPLAY,
    crosswalk_payload as local_replay_crosswalk_payload,
    load_artifact,
)

ROOT = Path(__file__).resolve().parents[1]


def test_local_lemma_audit_path_counts_and_scope() -> None:
    payload = local_lemma_audit_path_payload()

    assert_expected_local_lemma_audit_path(payload)
    assert payload["validation_status"] == "passed"
    assert payload["audit_path"]["layer_ids"] == EXPECTED_LAYER_IDS
    assert payload["audit_path"]["handoff_count"] == len(EXPECTED_HANDOFF_EDGES)
    assert [item["status"] for item in payload["audit_path"]["handoff_checks"]] == [
        "passed"
        for _ in EXPECTED_HANDOFF_EDGES
    ]
    assert payload["coverage_summary"] == {
        "layer_count": 5,
        "template_count": 12,
        "template_ids": [f"T{index:02d}" for index in range(1, 13)],
        "family_count": 16,
        "assignment_count": 184,
        "self_edge_family_count": 13,
        "self_edge_assignment_count": 158,
        "strict_cycle_family_count": 3,
        "strict_cycle_assignment_count": 26,
        "relation_skeleton_count": 16,
    }
    assert "does not prove packet soundness" in payload["claim_scope"]
    assert "does not prove n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not a global status update" in payload["claim_scope"]


def test_local_lemma_audit_path_input_manifest() -> None:
    payload = local_lemma_audit_path_payload()
    manifest = payload["input_manifest"]

    assert manifest["artifact_count"] == EXPECTED_INPUT_ARTIFACT_COUNT
    assert manifest["digest_algorithm"] == "sha256"
    artifacts = manifest["artifacts"]
    assert len(artifacts) == EXPECTED_INPUT_ARTIFACT_COUNT
    by_path = {artifact["path"]: artifact for artifact in artifacts}
    assert len(by_path) == EXPECTED_INPUT_ARTIFACT_COUNT
    assert all(len(artifact["sha256"]) == 64 for artifact in artifacts)
    assert all(artifact["size_bytes"] > 0 for artifact in artifacts)
    assert "data/certificates/n9_vertex_circle_local_lemmas.json" in by_path
    assert "data/certificates/n9_vertex_circle_exhaustive.json" in by_path
    assert (
        "data/certificates/n9_t12_strict_cycle_minireplay.json" in by_path
    )
    local_roles = by_path[
        "data/certificates/n9_vertex_circle_local_lemmas.json"
    ]["roles"]
    assert "aggregate local-lemma scan" in local_roles
    assert "aggregate/simple replay aggregate source" in local_roles


def test_local_lemma_audit_path_manifest_consistency() -> None:
    payload = local_lemma_audit_path_payload()
    consistency = payload["manifest_consistency"]

    assert consistency == {
        "status": "passed",
        "manifest_artifact_count": EXPECTED_INPUT_ARTIFACT_COUNT,
        "layer_referenced_artifact_count": EXPECTED_INPUT_ARTIFACT_COUNT,
        "missing_from_manifest": [],
        "unreferenced_manifest_paths": [],
    }


def test_local_lemma_audit_path_rejects_unmanifested_layer_path() -> None:
    focused_minireplay = focused_minireplay_crosswalk_payload()
    tampered = json.loads(json.dumps(focused_minireplay))
    tampered["focused_minireplay_crosswalk"]["records"][0]["minireplay_path"] = (
        "data/certificates/unmanifested_minireplay.json"
    )

    payload = local_lemma_audit_path_payload(focused_minireplay_payload=tampered)

    assert payload["validation_status"] == "failed"
    assert payload["manifest_consistency"]["status"] == "failed"
    assert payload["manifest_consistency"]["missing_from_manifest"] == [
        "data/certificates/unmanifested_minireplay.json"
    ]
    assert any(
        "input_manifest missing layer-referenced paths" in error
        for error in payload["validation_errors"]
    )


def test_local_lemma_audit_path_layer_summaries() -> None:
    payload = local_lemma_audit_path_payload()
    by_layer = {item["layer_id"]: item for item in payload["audit_path"]["layers"]}

    assert by_layer["focused_packet_catalog"]["template_count"] == 12
    assert by_layer["focused_minireplay"]["assignment_count"] == 184
    assert by_layer["aggregate_simple_replay"]["family_count"] == 16
    assert by_layer["exhaustive_local_lemma"]["strict_cycle_assignment_count"] == 26
    assert by_layer["relation_skeleton_local_lemma"]["relation_skeleton_count"] == 16


def test_local_lemma_audit_path_handoff_summaries() -> None:
    payload = local_lemma_audit_path_payload()
    handoffs = payload["audit_path"]["handoff_checks"]

    assert [
        (handoff["from_layer"], handoff["to_layer"])
        for handoff in handoffs
    ] == EXPECTED_HANDOFF_EDGES
    assert all("assignment_count" in handoff["compared_keys"] for handoff in handoffs)
    assert all(handoff["mismatches"] == [] for handoff in handoffs)


def test_local_lemma_audit_path_rejects_local_replay_drift() -> None:
    aggregate = load_artifact(DEFAULT_AGGREGATE)
    simple_replay = load_artifact(DEFAULT_SIMPLE_REPLAY)
    local_replay = local_replay_crosswalk_payload(aggregate, simple_replay)
    tampered = json.loads(json.dumps(local_replay))
    tampered["coverage_summary"]["matched_assignment_count"] = 183

    payload = local_lemma_audit_path_payload(
        aggregate_simple_replay_payload=tampered,
    )

    assert payload["validation_status"] == "failed"
    assert any(
        "aggregate_simple_replay expected-check failed" in error
        for error in payload["validation_errors"]
    )
    assert (
        "assignment_count mismatch across audit path: (184, 184, 183, 184, 184)"
        in payload["validation_errors"]
    )
    assert any(
        "focused_minireplay->aggregate_simple_replay handoff mismatch "
        "on assignment_count: 184 != 183"
        in error
        for error in payload["validation_errors"]
    )
    assert any(
        "aggregate_simple_replay->exhaustive_local_lemma handoff mismatch "
        "on assignment_count: 183 != 184"
        in error
        for error in payload["validation_errors"]
    )


def test_local_lemma_audit_path_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_local_lemma_audit_path.py",
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
    assert parsed["coverage_summary"]["assignment_count"] == 184
    assert parsed["coverage_summary"]["relation_skeleton_count"] == 16
