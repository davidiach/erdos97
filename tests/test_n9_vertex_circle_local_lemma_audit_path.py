from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_n9_vertex_circle_local_lemma_audit_path import (
    CLAIM_SCOPE_GUARDS,
    EXPECTED_HANDOFF_EDGES,
    EXPECTED_INPUT_ARTIFACT_COUNT,
    EXPECTED_LAYER_CONTRACTS,
    EXPECTED_LAYER_IDS,
    EXPECTED_LAYER_PROVENANCE,
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


def test_local_lemma_audit_path_layer_contracts() -> None:
    payload = local_lemma_audit_path_payload()
    contracts = payload["audit_path"]["layer_contracts"]

    assert [contract["layer_id"] for contract in contracts] == EXPECTED_LAYER_IDS
    assert all(contract["status"] == "passed" for contract in contracts)
    assert all(contract["mismatches"] == [] for contract in contracts)
    for contract in contracts:
        expected = EXPECTED_LAYER_CONTRACTS[contract["layer_id"]]
        assert contract["expected"] == expected
        assert contract["observed"] == expected


def test_local_lemma_audit_path_layer_provenance() -> None:
    payload = local_lemma_audit_path_payload()
    provenance_checks = payload["audit_path"]["layer_provenance"]

    assert [check["layer_id"] for check in provenance_checks] == EXPECTED_LAYER_IDS
    assert all(check["status"] == "passed" for check in provenance_checks)
    assert all(check["mismatches"] == [] for check in provenance_checks)
    for check in provenance_checks:
        expected = EXPECTED_LAYER_PROVENANCE[check["layer_id"]]
        assert check["expected"] == expected
        assert check["observed"] == expected


def test_local_lemma_audit_path_claim_scope_guards() -> None:
    payload = local_lemma_audit_path_payload()
    guard_checks = payload["audit_path"]["claim_scope_guards"]

    assert [check["layer_id"] for check in guard_checks] == EXPECTED_LAYER_IDS
    assert all(check["status"] == "passed" for check in guard_checks)
    assert all(check["missing_guards"] == [] for check in guard_checks)
    for check in guard_checks:
        results = check["guard_results"]
        assert [result["guard"] for result in results] == list(CLAIM_SCOPE_GUARDS)
        assert all(result["status"] == "passed" for result in results)
        assert all(result["matched_tokens"] for result in results)


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


def test_local_lemma_audit_path_rejects_layer_contract_drift() -> None:
    aggregate = load_artifact(DEFAULT_AGGREGATE)
    simple_replay = load_artifact(DEFAULT_SIMPLE_REPLAY)
    local_replay = local_replay_crosswalk_payload(aggregate, simple_replay)
    tampered = json.loads(json.dumps(local_replay))
    tampered["trust"] = "EXACT_OBSTRUCTION"

    payload = local_lemma_audit_path_payload(
        aggregate_simple_replay_payload=tampered,
    )
    contracts = {
        contract["layer_id"]: contract
        for contract in payload["audit_path"]["layer_contracts"]
    }

    assert payload["validation_status"] == "failed"
    assert contracts["aggregate_simple_replay"]["status"] == "failed"
    assert contracts["aggregate_simple_replay"]["mismatches"] == [
        {
            "key": "trust",
            "expected": "REVIEW_PENDING_DIAGNOSTIC",
            "observed": "EXACT_OBSTRUCTION",
        }
    ]
    assert any(
        "aggregate_simple_replay contract mismatch on trust" in error
        for error in payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_layer_provenance_drift() -> None:
    aggregate = load_artifact(DEFAULT_AGGREGATE)
    simple_replay = load_artifact(DEFAULT_SIMPLE_REPLAY)
    local_replay = local_replay_crosswalk_payload(aggregate, simple_replay)
    tampered = json.loads(json.dumps(local_replay))
    tampered["provenance"]["command"] = "python scripts/not_the_crosswalk.py"

    payload = local_lemma_audit_path_payload(
        aggregate_simple_replay_payload=tampered,
    )
    provenance_checks = {
        check["layer_id"]: check
        for check in payload["audit_path"]["layer_provenance"]
    }

    assert payload["validation_status"] == "failed"
    assert provenance_checks["aggregate_simple_replay"]["status"] == "failed"
    assert provenance_checks["aggregate_simple_replay"]["mismatches"] == [
        {
            "key": "command",
            "expected": (
                "python scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py "
                "--check --assert-expected --json"
            ),
            "observed": "python scripts/not_the_crosswalk.py",
        }
    ]
    assert any(
        "aggregate_simple_replay provenance mismatch on command" in error
        for error in payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_claim_scope_guard_drift() -> None:
    focused_minireplay = focused_minireplay_crosswalk_payload()
    tampered = json.loads(json.dumps(focused_minireplay))
    tampered["claim_scope"] = "This packet audit discusses n=9."

    payload = local_lemma_audit_path_payload(focused_minireplay_payload=tampered)
    guard_checks = {
        check["layer_id"]: check
        for check in payload["audit_path"]["claim_scope_guards"]
    }

    assert payload["validation_status"] == "failed"
    focused_guard = guard_checks["focused_minireplay"]
    assert focused_guard["status"] == "failed"
    assert focused_guard["missing_guards"] == [
        "denies_proof",
        "denies_counterexample",
        "denies_global_status_update",
    ]
    assert any(
        "focused_minireplay claim_scope missing guards" in error
        for error in payload["validation_errors"]
    )


def test_local_lemma_audit_path_global_status_guard_requires_negation() -> None:
    focused_minireplay = focused_minireplay_crosswalk_payload()
    tampered = json.loads(json.dumps(focused_minireplay))
    tampered["claim_scope"] = (
        "This is not a proof of n=9, not a counterexample, and this is an "
        "official/global status update."
    )

    payload = local_lemma_audit_path_payload(focused_minireplay_payload=tampered)
    guard_checks = {
        check["layer_id"]: check
        for check in payload["audit_path"]["claim_scope_guards"]
    }

    assert payload["validation_status"] == "failed"
    focused_guard = guard_checks["focused_minireplay"]
    assert focused_guard["status"] == "failed"
    assert focused_guard["missing_guards"] == ["denies_global_status_update"]
    assert any(
        "focused_minireplay claim_scope missing guards" in error
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
