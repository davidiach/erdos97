from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from scripts.check_artifact_provenance import (
    DEFAULT_MANIFEST as DEFAULT_GENERATED_ARTIFACTS_MANIFEST,
    load_manifest as load_generated_artifact_manifest,
)
from scripts.check_n9_vertex_circle_local_lemma_audit_path import (
    ASSERT_EXPECTED_FAILURE_KEYS,
    ASSERT_EXPECTED_FAILURE_SCHEMA,
    CLAIM_SCOPE,
    CLAIM_SCOPE_GUARDS,
    EXPECTED_AUDIT_CONTRACT_COMPONENT_IDS,
    EXPECTED_CLOSED_DESCENT_COMPANION_SUMMARY,
    EXPECTED_HANDOFF_EDGES,
    EXPECTED_INPUT_ARTIFACT_COUNT,
    EXPECTED_LAYER_CONTRACTS,
    EXPECTED_LAYER_IDS,
    EXPECTED_LAYER_OUTPUT_CONTRACTS,
    EXPECTED_LAYER_PROVENANCE,
    EXPECTED_LAYER_SOURCE_ARTIFACTS,
    EXPECTED_MANIFEST_CONTRACT_IDS,
    EXPECTED_SUMMARY_LINES,
    SUMMARY_JSON_KEYS,
    assert_expected_failure_contract_errors,
    assert_expected_local_lemma_audit_path,
    failure_lines,
    local_lemma_audit_path_payload,
    main as audit_path_main,
    reviewer_command_plan,
    summary_json_payload,
    summary_lines,
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


def _layer_contract_trust_tamper_payload() -> dict[str, Any]:
    aggregate = load_artifact(DEFAULT_AGGREGATE)
    simple_replay = load_artifact(DEFAULT_SIMPLE_REPLAY)
    local_replay = local_replay_crosswalk_payload(aggregate, simple_replay)
    tampered = json.loads(json.dumps(local_replay))
    # Only the in-memory layer payload is tampered; the input manifest and
    # stored artifacts stay canonical, so this isolates layer-contract failure.
    tampered["trust"] = "EXACT_OBSTRUCTION"
    return local_lemma_audit_path_payload(
        aggregate_simple_replay_payload=tampered,
    )


def _assert_expected_failure_contract_tamper_payload() -> dict[str, Any]:
    payload = _layer_contract_trust_tamper_payload()
    payload["assert_expected_failure"] = {
        "schema": "erdos97.invalid_assert_expected_failure.v1",
        "stage": "payload_construction",
        "exception_type": "AssertionError",
        "message": "validation errors: []",
        "validation_error_count": 0,
    }
    return payload


def test_local_lemma_audit_path_counts_and_scope() -> None:
    payload = local_lemma_audit_path_payload()

    assert_expected_local_lemma_audit_path(payload)
    assert payload["validation_status"] == "passed"
    assert payload["audit_path"]["layer_ids"] == EXPECTED_LAYER_IDS
    assert payload["audit_path"]["handoff_count"] == len(EXPECTED_HANDOFF_EDGES)
    assert (
        payload["closed_descent_companion"]
        == EXPECTED_CLOSED_DESCENT_COMPANION_SUMMARY
    )
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


def test_local_lemma_audit_path_rejects_top_level_claim_scope_append() -> None:
    payload = local_lemma_audit_path_payload()
    payload["claim_scope"] = CLAIM_SCOPE + " This proves n=9."

    try:
        assert_expected_local_lemma_audit_path(payload)
    except AssertionError as exc:
        assert "claim_scope mismatch" in str(exc)
    else:
        raise AssertionError("expected top-level claim_scope mismatch")


def test_local_lemma_audit_path_rejects_coverage_summary_extra_key() -> None:
    payload = local_lemma_audit_path_payload()
    payload["coverage_summary"]["unreviewed_layer_count"] = 5

    try:
        assert_expected_local_lemma_audit_path(payload)
    except AssertionError as exc:
        assert "coverage_summary mismatch" in str(exc)
    else:
        raise AssertionError("expected coverage_summary mismatch")


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
        "data/certificates/n9_vertex_circle_closed_descent_packet.json" in by_path
    )
    assert (
        "data/certificates/n9_t12_strict_cycle_minireplay.json" in by_path
    )
    local_roles = by_path[
        "data/certificates/n9_vertex_circle_local_lemmas.json"
    ]["roles"]
    assert "aggregate local-lemma scan" in local_roles
    assert "aggregate/simple replay aggregate source" in local_roles


def test_local_lemma_audit_path_manifest_role_contract() -> None:
    payload = local_lemma_audit_path_payload()
    contract = payload["manifest_role_contract"]
    by_path = {record["path"]: record for record in contract["observed_roles"]}

    assert contract["status"] == "passed"
    assert contract["expected_path_count"] == EXPECTED_INPUT_ARTIFACT_COUNT
    assert contract["observed_path_count"] == EXPECTED_INPUT_ARTIFACT_COUNT
    assert contract["expected_roles"] == contract["observed_roles"]
    assert contract["missing_manifest_role_paths"] == []
    assert contract["unexpected_manifest_role_paths"] == []
    assert contract["duplicate_manifest_role_paths"] == []
    assert contract["mismatched_manifest_roles"] == []
    assert contract["malformed_manifest_role_count"] == 0
    assert by_path["data/certificates/n9_vertex_circle_local_lemmas.json"][
        "roles"
    ] == [
        "aggregate local-lemma scan",
        "aggregate/simple replay aggregate source",
    ]


def test_local_lemma_audit_path_manifest_digest_contract() -> None:
    payload = local_lemma_audit_path_payload()
    contract = payload["manifest_digest_contract"]
    by_path = {record["path"]: record for record in contract["observed_digests"]}

    assert contract["status"] == "passed"
    assert contract["expected_path_count"] == EXPECTED_INPUT_ARTIFACT_COUNT
    assert contract["observed_path_count"] == EXPECTED_INPUT_ARTIFACT_COUNT
    assert contract["expected_digests"] == contract["observed_digests"]
    assert contract["missing_manifest_digest_paths"] == []
    assert contract["unexpected_manifest_digest_paths"] == []
    assert contract["duplicate_manifest_digest_paths"] == []
    assert contract["mismatched_manifest_digests"] == []
    assert contract["malformed_manifest_digest_count"] == 0
    local_digest = by_path["data/certificates/n9_vertex_circle_local_lemmas.json"]
    assert local_digest["size_bytes"] > 0
    assert len(local_digest["sha256"]) == 64


def test_local_lemma_audit_path_manifest_header_contract() -> None:
    payload = local_lemma_audit_path_payload()
    contract = payload["manifest_header_contract"]
    by_path = {record["path"]: record for record in contract["observed_headers"]}

    assert contract["status"] == "passed"
    assert contract["expected_path_count"] == EXPECTED_INPUT_ARTIFACT_COUNT
    assert contract["observed_path_count"] == EXPECTED_INPUT_ARTIFACT_COUNT
    assert contract["expected_headers"] == contract["observed_headers"]
    assert contract["missing_manifest_header_paths"] == []
    assert contract["unexpected_manifest_header_paths"] == []
    assert contract["duplicate_manifest_header_paths"] == []
    assert contract["mismatched_manifest_headers"] == []
    assert contract["malformed_manifest_header_count"] == 0
    assert by_path["data/certificates/n9_vertex_circle_exhaustive.json"] == {
        "path": "data/certificates/n9_vertex_circle_exhaustive.json",
        "schema": None,
        "status": None,
        "trust": "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
        "validation_status": None,
    }
    assert by_path["data/certificates/n9_t12_strict_cycle_minireplay.json"][
        "status"
    ] == "REVIEW_PENDING_T12_STRICT_CYCLE_MINIREPLAY"


def test_local_lemma_audit_path_manifest_provenance_contract() -> None:
    payload = local_lemma_audit_path_payload()
    contract = payload["manifest_provenance_contract"]
    by_path = {
        record["path"]: record for record in contract["observed_provenance"]
    }

    assert contract["status"] == "passed"
    assert contract["expected_path_count"] == EXPECTED_INPUT_ARTIFACT_COUNT
    assert contract["observed_path_count"] == EXPECTED_INPUT_ARTIFACT_COUNT
    assert contract["expected_provenance"] == contract["observed_provenance"]
    assert contract["missing_manifest_provenance_paths"] == []
    assert contract["unexpected_manifest_provenance_paths"] == []
    assert contract["duplicate_manifest_provenance_paths"] == []
    assert contract["mismatched_manifest_provenance"] == []
    assert contract["malformed_manifest_provenance_count"] == 0
    local_provenance = by_path[
        "data/certificates/n9_vertex_circle_local_lemmas.json"
    ]
    assert local_provenance == {
        "path": "data/certificates/n9_vertex_circle_local_lemmas.json",
        "generator": "scripts/check_n9_vertex_circle_local_lemmas.py",
        "command": (
            "python scripts/check_n9_vertex_circle_local_lemmas.py "
            "--assert-expected --write"
        ),
    }
    assert by_path["data/certificates/n9_vertex_circle_exhaustive.json"] == {
        "path": "data/certificates/n9_vertex_circle_exhaustive.json",
        "generator": None,
        "command": None,
    }
    assert by_path["data/certificates/n9_t12_strict_cycle_minireplay.json"][
        "command"
    ] == (
        "python scripts/check_n9_t12_strict_cycle_minireplay.py "
        "--write --assert-expected"
    )


def test_local_lemma_audit_path_manifest_metadata_contract() -> None:
    payload = local_lemma_audit_path_payload()
    contract = payload["manifest_metadata_contract"]
    by_path = {record["path"]: record for record in contract["observed_metadata"]}

    assert contract["status"] == "passed"
    assert contract["metadata_manifest_path"] == "metadata/generated_artifacts.yaml"
    assert contract["expected_path_count"] == EXPECTED_INPUT_ARTIFACT_COUNT
    assert contract["observed_path_count"] == EXPECTED_INPUT_ARTIFACT_COUNT
    assert contract["expected_metadata"] == contract["observed_metadata"]
    assert contract["missing_manifest_metadata_paths"] == []
    assert contract["unexpected_manifest_metadata_paths"] == []
    assert contract["duplicate_manifest_metadata_paths"] == []
    assert contract["duplicate_generated_metadata_paths"] == []
    assert contract["native_trust_policy_status"] == "passed"
    assert contract["native_trust_policy_errors"] == []
    assert contract["mismatched_manifest_metadata"] == []
    assert contract["malformed_manifest_metadata_count"] == 0
    local_metadata = by_path["data/certificates/n9_vertex_circle_local_lemmas.json"]
    assert local_metadata["id"] == "n9_vertex_circle_local_lemmas"
    assert local_metadata["provenance_mode"] == "embedded"
    assert local_metadata["direct_edit_allowed"] is False
    assert local_metadata["trust_class"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "trust" not in local_metadata
    assert local_metadata["checker"] == "scripts/check_n9_vertex_circle_local_lemmas.py"
    assert local_metadata["check_command"] == (
        "python scripts/check_n9_vertex_circle_local_lemmas.py "
        "--check --assert-expected --json"
    )
    assert local_metadata["size_bytes"] > 0
    assert len(local_metadata["sha256"]) == 64
    assert by_path["data/certificates/n9_vertex_circle_exhaustive.json"][
        "provenance_mode"
    ] == "manifest_only_legacy"
    assert by_path["data/certificates/n9_vertex_circle_exhaustive.json"][
        "check_command"
    ] is None
    assert by_path["data/certificates/n9_t12_strict_cycle_minireplay.json"][
        "kind"
    ] == "proof_mining_diagnostic_artifact"


def test_local_lemma_audit_path_rejects_native_trust_override_drift() -> None:
    tampered_metadata = load_generated_artifact_manifest(
        DEFAULT_GENERATED_ARTIFACTS_MANIFEST
    )
    tampered_metadata = json.loads(json.dumps(tampered_metadata))
    override = tampered_metadata["native_trust_policy"]["mismatch_overrides"][
        "n9_vertex_circle_minimal_cores"
    ]
    override["native_value"] = "WRONG_NATIVE_TRUST"

    tampered_payload = local_lemma_audit_path_payload(
        generated_artifact_metadata_payload=tampered_metadata,
    )
    contract = tampered_payload["manifest_metadata_contract"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert contract["native_trust_policy_status"] == "failed"
    assert any(
        "n9_vertex_circle_minimal_cores.native_value" in error
        and "does not match payload value" in error
        for error in contract["native_trust_policy_errors"]
    )


def test_local_lemma_audit_path_rejects_missing_native_trust_override() -> None:
    tampered_metadata = load_generated_artifact_manifest(
        DEFAULT_GENERATED_ARTIFACTS_MANIFEST
    )
    tampered_metadata = json.loads(json.dumps(tampered_metadata))
    del tampered_metadata["native_trust_policy"]["missing_overrides"][
        "n8_reconstructed_survivors"
    ]

    tampered_payload = local_lemma_audit_path_payload(
        generated_artifact_metadata_payload=tampered_metadata,
    )
    contract = tampered_payload["manifest_metadata_contract"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert contract["native_trust_policy_status"] == "failed"
    assert any(
        "n8_reconstructed_survivors" in error
        and "has no top-level native trust" in error
        for error in contract["native_trust_policy_errors"]
    )


def test_local_lemma_audit_path_manifest_claim_contract() -> None:
    payload = local_lemma_audit_path_payload()
    contract = payload["manifest_claim_contract"]
    by_path = {record["path"]: record for record in contract["observed_claims"]}

    assert contract["status"] == "passed"
    assert contract["expected_path_count"] == EXPECTED_INPUT_ARTIFACT_COUNT
    assert contract["observed_path_count"] == EXPECTED_INPUT_ARTIFACT_COUNT
    assert contract["missing_manifest_claim_paths"] == []
    assert contract["unexpected_manifest_claim_paths"] == []
    assert contract["duplicate_manifest_claim_paths"] == []
    assert contract["failed_manifest_claim_guards"] == []
    assert contract["malformed_manifest_claim_count"] == 0
    local_claim = by_path["data/certificates/n9_vertex_circle_local_lemmas.json"]
    assert local_claim["field"] == "claim_scope"
    assert local_claim["status"] == "passed"
    assert [result["guard"] for result in local_claim["guard_results"]] == [
        "mentions_n9_scope",
        "denies_proof",
        "denies_counterexample",
        "denies_global_status_update",
    ]
    exhaustive_claim = by_path["data/certificates/n9_vertex_circle_exhaustive.json"]
    assert exhaustive_claim["field"] == "scope"
    assert exhaustive_claim["status"] == "passed"
    assert [result["guard"] for result in exhaustive_claim["guard_results"]] == [
        "marks_repo_local_finite_case",
        "marks