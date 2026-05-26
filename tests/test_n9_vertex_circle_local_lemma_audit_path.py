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
    EXPECTED_HANDOFF_EDGES,
    EXPECTED_INPUT_ARTIFACT_COUNT,
    EXPECTED_LAYER_CONTRACTS,
    EXPECTED_LAYER_IDS,
    EXPECTED_LAYER_OUTPUT_CONTRACTS,
    EXPECTED_LAYER_PROVENANCE,
    EXPECTED_LAYER_SOURCE_ARTIFACTS,
    EXPECTED_MANIFEST_CONTRACT_IDS,
    assert_expected_failure_contract_errors,
    assert_expected_local_lemma_audit_path,
    failure_lines,
    local_lemma_audit_path_payload,
    main as audit_path_main,
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
    assert contract["mismatched_manifest_metadata"] == []
    assert contract["malformed_manifest_metadata_count"] == 0
    local_metadata = by_path["data/certificates/n9_vertex_circle_local_lemmas.json"]
    assert local_metadata["id"] == "n9_vertex_circle_local_lemmas"
    assert local_metadata["provenance_mode"] == "embedded"
    assert local_metadata["direct_edit_allowed"] is False
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
        "marks_candidate_scope",
        "denies_global_status_update",
    ]


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


def test_local_lemma_audit_path_manifest_contract_summary() -> None:
    payload = local_lemma_audit_path_payload()
    summary = payload["manifest_contract_summary"]

    assert summary == {
        "status": "passed",
        "contract_count": len(EXPECTED_MANIFEST_CONTRACT_IDS),
        "passed_contract_count": len(EXPECTED_MANIFEST_CONTRACT_IDS),
        "failed_contract_count": 0,
        "failed_contracts": [],
        "contract_statuses": [
            {"contract_id": contract_id, "status": "passed"}
            for contract_id in EXPECTED_MANIFEST_CONTRACT_IDS
        ],
    }


def test_local_lemma_audit_path_audit_contract_summary() -> None:
    payload = local_lemma_audit_path_payload()
    summary = payload["audit_contract_summary"]

    assert summary == {
        "status": "passed",
        "component_count": len(EXPECTED_AUDIT_CONTRACT_COMPONENT_IDS),
        "passed_component_count": len(EXPECTED_AUDIT_CONTRACT_COMPONENT_IDS),
        "failed_component_count": 0,
        "failed_components": [],
        "component_statuses": [
            {"component_id": component_id, "status": "passed"}
            for component_id in EXPECTED_AUDIT_CONTRACT_COMPONENT_IDS
        ],
    }


def test_local_lemma_audit_path_rejects_manifest_role_drift() -> None:
    payload = local_lemma_audit_path_payload()
    tampered_manifest = json.loads(json.dumps(payload["input_manifest"]))
    for artifact in tampered_manifest["artifacts"]:
        if artifact["path"] == "data/certificates/n9_vertex_circle_local_lemmas.json":
            artifact["roles"] = ["aggregate/simple replay aggregate source"]
            break

    tampered_payload = local_lemma_audit_path_payload(
        input_manifest_payload=tampered_manifest,
    )
    contract = tampered_payload["manifest_role_contract"]
    summary = tampered_payload["manifest_contract_summary"]
    audit_summary = tampered_payload["audit_contract_summary"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert summary["status"] == "failed"
    assert summary["contract_count"] == len(EXPECTED_MANIFEST_CONTRACT_IDS)
    assert summary["passed_contract_count"] == (
        len(EXPECTED_MANIFEST_CONTRACT_IDS) - 1
    )
    assert summary["failed_contract_count"] == 1
    assert summary["failed_contracts"] == ["manifest_role_contract"]
    assert audit_summary["status"] == "failed"
    assert audit_summary["failed_component_count"] == 1
    assert audit_summary["failed_components"] == ["manifest_contracts"]
    assert contract["mismatched_manifest_roles"] == [
        {
            "path": "data/certificates/n9_vertex_circle_local_lemmas.json",
            "expected": [
                "aggregate local-lemma scan",
                "aggregate/simple replay aggregate source",
            ],
            "observed": ["aggregate/simple replay aggregate source"],
        }
    ]
    assert any(
        "input_manifest role mismatch on "
        "data/certificates/n9_vertex_circle_local_lemmas.json" in error
        for error in tampered_payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_malformed_manifest_roles() -> None:
    payload = local_lemma_audit_path_payload()
    tampered_manifest = json.loads(json.dumps(payload["input_manifest"]))
    tampered_manifest["artifacts"] = "not a manifest artifact list"

    tampered_payload = local_lemma_audit_path_payload(
        input_manifest_payload=tampered_manifest,
    )
    contract = tampered_payload["manifest_role_contract"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert contract["malformed_manifest_role_count"] == 1
    assert contract["observed_path_count"] == 0
    assert len(contract["missing_manifest_role_paths"]) == EXPECTED_INPUT_ARTIFACT_COUNT
    assert any(
        "input_manifest has 1 malformed role entries" in error
        for error in tampered_payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_manifest_digest_drift() -> None:
    payload = local_lemma_audit_path_payload()
    input_by_path = {
        artifact["path"]: artifact for artifact in payload["input_manifest"]["artifacts"]
    }
    original = input_by_path["data/certificates/n9_vertex_circle_local_lemmas.json"]
    tampered_manifest = json.loads(json.dumps(payload["input_manifest"]))
    for artifact in tampered_manifest["artifacts"]:
        if artifact["path"] == "data/certificates/n9_vertex_circle_local_lemmas.json":
            artifact["sha256"] = "0" * 64
            break

    tampered_payload = local_lemma_audit_path_payload(
        input_manifest_payload=tampered_manifest,
    )
    contract = tampered_payload["manifest_digest_contract"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert contract["mismatched_manifest_digests"] == [
        {
            "path": "data/certificates/n9_vertex_circle_local_lemmas.json",
            "expected": {
                "size_bytes": original["size_bytes"],
                "sha256": original["sha256"],
            },
            "observed": {
                "size_bytes": original["size_bytes"],
                "sha256": "0" * 64,
            },
        }
    ]
    assert any(
        "input_manifest digest mismatch on "
        "data/certificates/n9_vertex_circle_local_lemmas.json" in error
        for error in tampered_payload["validation_errors"]
    )


def test_local_lemma_audit_path_accepts_uppercase_manifest_digest() -> None:
    payload = local_lemma_audit_path_payload()
    tampered_manifest = json.loads(json.dumps(payload["input_manifest"]))
    for artifact in tampered_manifest["artifacts"]:
        if artifact["path"] == "data/certificates/n9_vertex_circle_local_lemmas.json":
            artifact["sha256"] = artifact["sha256"].upper()
            break

    tampered_payload = local_lemma_audit_path_payload(
        input_manifest_payload=tampered_manifest,
    )
    contract = tampered_payload["manifest_digest_contract"]

    assert tampered_payload["validation_status"] == "passed"
    assert contract["status"] == "passed"
    assert contract["mismatched_manifest_digests"] == []


def test_local_lemma_audit_path_rejects_malformed_manifest_digests() -> None:
    payload = local_lemma_audit_path_payload()
    tampered_manifest = json.loads(json.dumps(payload["input_manifest"]))
    for artifact in tampered_manifest["artifacts"]:
        if artifact["path"] == "data/certificates/n9_vertex_circle_local_lemmas.json":
            artifact["sha256"] = "not-a-sha256"
            break

    tampered_payload = local_lemma_audit_path_payload(
        input_manifest_payload=tampered_manifest,
    )
    contract = tampered_payload["manifest_digest_contract"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert contract["malformed_manifest_digest_count"] == 1
    assert "data/certificates/n9_vertex_circle_local_lemmas.json" in contract[
        "missing_manifest_digest_paths"
    ]
    assert any(
        "input_manifest has 1 malformed digest entries" in error
        for error in tampered_payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_manifest_header_drift() -> None:
    path = "data/certificates/n9_vertex_circle_local_lemmas.json"
    tampered_header = dict(load_artifact(ROOT / path))
    tampered_header["status"] = "REVIEW_PENDING_WRONG_STATUS"

    tampered_payload = local_lemma_audit_path_payload(
        manifest_header_payloads={path: tampered_header},
    )
    contract = tampered_payload["manifest_header_contract"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert contract["mismatched_manifest_headers"] == [
        {
            "path": path,
            "expected": {
                "schema": "erdos97.n9_vertex_circle_local_lemmas.v1",
                "status": "REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE",
                "trust": "REVIEW_PENDING_DIAGNOSTIC",
                "validation_status": None,
            },
            "observed": {
                "schema": "erdos97.n9_vertex_circle_local_lemmas.v1",
                "status": "REVIEW_PENDING_WRONG_STATUS",
                "trust": "REVIEW_PENDING_DIAGNOSTIC",
                "validation_status": None,
            },
        }
    ]
    assert any(
        "input_manifest header mismatch on "
        "data/certificates/n9_vertex_circle_local_lemmas.json" in error
        for error in tampered_payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_malformed_manifest_headers() -> None:
    path = "data/certificates/n9_vertex_circle_local_lemmas.json"
    tampered_payload = local_lemma_audit_path_payload(
        manifest_header_payloads={path: ["not", "a", "header"]},
    )
    contract = tampered_payload["manifest_header_contract"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert contract["malformed_manifest_header_count"] == 1
    assert path in contract["missing_manifest_header_paths"]
    assert any(
        "input_manifest has 1 malformed header entries" in error
        for error in tampered_payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_manifest_provenance_drift() -> None:
    path = "data/certificates/n9_vertex_circle_local_lemmas.json"
    tampered_provenance = dict(load_artifact(ROOT / path))
    tampered_provenance["provenance"] = dict(tampered_provenance["provenance"])
    tampered_provenance["provenance"]["command"] = (
        "python scripts/not_the_local_lemma_generator.py --write"
    )

    tampered_payload = local_lemma_audit_path_payload(
        manifest_provenance_payloads={path: tampered_provenance},
    )
    contract = tampered_payload["manifest_provenance_contract"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert contract["mismatched_manifest_provenance"] == [
        {
            "path": path,
            "key": "command",
            "expected": (
                "python scripts/check_n9_vertex_circle_local_lemmas.py "
                "--assert-expected --write"
            ),
            "observed": "python scripts/not_the_local_lemma_generator.py --write",
        }
    ]
    assert any(
        "input_manifest provenance mismatch on "
        "data/certificates/n9_vertex_circle_local_lemmas.json command" in error
        for error in tampered_payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_malformed_manifest_provenance() -> None:
    path = "data/certificates/n9_vertex_circle_local_lemmas.json"
    tampered_payload = local_lemma_audit_path_payload(
        manifest_provenance_payloads={path: ["not", "a", "provenance"]},
    )
    contract = tampered_payload["manifest_provenance_contract"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert contract["malformed_manifest_provenance_count"] == 1
    assert path in contract["missing_manifest_provenance_paths"]
    assert any(
        "input_manifest has 1 malformed provenance entries" in error
        for error in tampered_payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_manifest_metadata_drift() -> None:
    path = "data/certificates/n9_vertex_circle_local_lemmas.json"
    tampered_metadata = load_generated_artifact_manifest(
        DEFAULT_GENERATED_ARTIFACTS_MANIFEST
    )
    tampered_metadata = json.loads(json.dumps(tampered_metadata))
    for artifact in tampered_metadata["artifacts"]:
        if artifact["path"] == path:
            artifact["check_command"] = (
                "python scripts/not_the_local_lemma_checker.py --json"
            )
            break

    tampered_payload = local_lemma_audit_path_payload(
        generated_artifact_metadata_payload=tampered_metadata,
    )
    contract = tampered_payload["manifest_metadata_contract"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert contract["mismatched_manifest_metadata"] == [
        {
            "path": path,
            "key": "check_command",
            "expected": (
                "python scripts/check_n9_vertex_circle_local_lemmas.py "
                "--check --assert-expected --json"
            ),
            "observed": "python scripts/not_the_local_lemma_checker.py --json",
        }
    ]
    assert any(
        "input_manifest metadata mismatch on "
        "data/certificates/n9_vertex_circle_local_lemmas.json check_command"
        in error
        for error in tampered_payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_malformed_manifest_metadata() -> None:
    tampered_payload = local_lemma_audit_path_payload(
        generated_artifact_metadata_payload={"artifacts": "not a metadata list"},
    )
    contract = tampered_payload["manifest_metadata_contract"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert contract["malformed_manifest_metadata_count"] == 1
    assert len(contract["missing_manifest_metadata_paths"]) == (
        EXPECTED_INPUT_ARTIFACT_COUNT
    )
    assert any(
        "input_manifest has 1 malformed metadata entries" in error
        for error in tampered_payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_manifest_claim_drift() -> None:
    path = "data/certificates/n9_vertex_circle_local_lemmas.json"
    tampered_claim = dict(load_artifact(ROOT / path))
    tampered_claim["claim_scope"] = "This packet audit discusses n=9."

    tampered_payload = local_lemma_audit_path_payload(
        manifest_claim_payloads={path: tampered_claim},
    )
    contract = tampered_payload["manifest_claim_contract"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert contract["failed_manifest_claim_guards"] == [
        {
            "path": path,
            "field": "claim_scope",
            "missing_guards": [
                "denies_proof",
                "denies_counterexample",
                "denies_global_status_update",
            ],
        }
    ]
    assert any(
        "input_manifest claim guards failed on "
        "data/certificates/n9_vertex_circle_local_lemmas.json" in error
        for error in tampered_payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_malformed_manifest_claims() -> None:
    path = "data/certificates/n9_vertex_circle_local_lemmas.json"
    tampered_payload = local_lemma_audit_path_payload(
        manifest_claim_payloads={path: ["not", "a", "claim"]},
    )
    contract = tampered_payload["manifest_claim_contract"]

    assert tampered_payload["validation_status"] == "failed"
    assert contract["status"] == "failed"
    assert contract["malformed_manifest_claim_count"] == 1
    assert path in contract["missing_manifest_claim_paths"]
    assert any(
        "input_manifest has 1 malformed claim entries" in error
        for error in tampered_payload["validation_errors"]
    )


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


def test_local_lemma_audit_path_layer_source_artifact_contracts() -> None:
    payload = local_lemma_audit_path_payload()
    contracts = payload["audit_path"]["layer_source_artifact_contracts"]

    assert [contract["layer_id"] for contract in contracts] == EXPECTED_LAYER_IDS
    assert all(contract["status"] == "passed" for contract in contracts)
    for contract in contracts:
        layer_id = contract["layer_id"]
        expected = sorted(
            (dict(item) for item in EXPECTED_LAYER_SOURCE_ARTIFACTS[layer_id]),
            key=lambda item: item["path"],
        )
        expected_type = "missing" if layer_id == "focused_minireplay" else "list"
        assert contract["source_artifacts_type"] == expected_type
        assert contract["expected_artifact_count"] == len(expected)
        assert contract["observed_artifact_count"] == len(expected)
        assert contract["expected_artifacts"] == expected
        assert contract["observed_artifacts"] == expected
        assert contract["missing_source_artifact_paths"] == []
        assert contract["unexpected_source_artifact_paths"] == []
        assert contract["duplicate_source_artifact_paths"] == []
        assert contract["mismatched_source_artifacts"] == []
        assert contract["malformed_source_artifact_count"] == 0


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


def test_local_lemma_audit_path_layer_output_contracts() -> None:
    payload = local_lemma_audit_path_payload()
    output_contracts = payload["audit_path"]["layer_output_contracts"]

    assert [contract["layer_id"] for contract in output_contracts] == EXPECTED_LAYER_IDS
    assert all(contract["status"] == "passed" for contract in output_contracts)
    for contract in output_contracts:
        expected = EXPECTED_LAYER_OUTPUT_CONTRACTS[contract["layer_id"]]
        assert contract["expected"] == {
            "summary_key": expected["summary_key"],
            "required_top_level_keys": list(expected["required_top_level_keys"]),
            "required_summary_keys": list(expected["required_summary_keys"]),
        }
        assert contract["summary_type"] == "object"
        assert contract["missing_top_level_keys"] == []
        assert contract["missing_summary_keys"] == []


def test_local_lemma_audit_path_layer_input_contracts() -> None:
    payload = local_lemma_audit_path_payload()
    input_contracts = payload["audit_path"]["layer_input_contracts"]
    expected_counts = {
        "focused_packet_catalog": 16,
        "focused_minireplay": 24,
        "aggregate_simple_replay": 2,
        "exhaustive_local_lemma": 4,
        "relation_skeleton_local_lemma": 3,
    }

    assert [contract["layer_id"] for contract in input_contracts] == EXPECTED_LAYER_IDS
    assert all(contract["status"] == "passed" for contract in input_contracts)
    for contract in input_contracts:
        expected_count = expected_counts[contract["layer_id"]]
        assert contract["expected_path_count"] == expected_count
        assert contract["observed_path_count"] == expected_count
        assert contract["expected_paths"] == contract["observed_paths"]
        assert contract["missing_input_paths"] == []
        assert contract["unexpected_input_paths"] == []


def test_local_lemma_audit_path_focused_minireplay_record_path_contract() -> None:
    payload = local_lemma_audit_path_payload()
    contract = payload["audit_path"]["focused_minireplay_record_path_contract"]
    by_template = {
        record["template_id"]: record for record in contract["observed_records"]
    }

    assert contract["status"] == "passed"
    assert contract["records_type"] == "list"
    assert contract["expected_record_count"] == 12
    assert contract["observed_record_count"] == 12
    assert contract["expected_records"] == contract["observed_records"]
    assert contract["missing_template_ids"] == []
    assert contract["unexpected_template_ids"] == []
    assert contract["duplicate_template_ids"] == []
    assert contract["mismatched_record_paths"] == []
    assert contract["malformed_record_count"] == 0
    assert by_template["T01"] == {
        "template_id": "T01",
        "source_packet_path": (
            "data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json"
        ),
        "minireplay_path": "data/certificates/n9_t01_self_edge_minireplay.json",
    }


def test_local_lemma_audit_path_rejects_unmanifested_layer_path() -> None:
    focused_minireplay = focused_minireplay_crosswalk_payload()
    tampered = json.loads(json.dumps(focused_minireplay))
    original_path = tampered["focused_minireplay_crosswalk"]["records"][0][
        "minireplay_path"
    ]
    tampered["focused_minireplay_crosswalk"]["records"][0]["minireplay_path"] = (
        "data/certificates/unmanifested_minireplay.json"
    )

    payload = local_lemma_audit_path_payload(focused_minireplay_payload=tampered)
    input_contracts = {
        contract["layer_id"]: contract
        for contract in payload["audit_path"]["layer_input_contracts"]
    }
    focused_contract = input_contracts["focused_minireplay"]
    record_contract = payload["audit_path"]["focused_minireplay_record_path_contract"]

    assert payload["validation_status"] == "failed"
    assert focused_contract["status"] == "failed"
    assert focused_contract["missing_input_paths"] == [original_path]
    assert focused_contract["unexpected_input_paths"] == [
        "data/certificates/unmanifested_minireplay.json"
    ]
    assert record_contract["status"] == "failed"
    assert record_contract["mismatched_record_paths"] == [
        {
            "template_id": "T01",
            "key": "minireplay_path",
            "expected": original_path,
            "observed": "data/certificates/unmanifested_minireplay.json",
        }
    ]
    assert payload["manifest_consistency"]["status"] == "failed"
    assert payload["manifest_consistency"]["missing_from_manifest"] == [
        "data/certificates/unmanifested_minireplay.json"
    ]
    assert any(
        "focused_minireplay input unexpected paths" in error
        for error in payload["validation_errors"]
    )
    assert any(
        "input_manifest missing layer-referenced paths" in error
        for error in payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_malformed_record_path() -> None:
    focused_minireplay = focused_minireplay_crosswalk_payload()
    tampered = json.loads(json.dumps(focused_minireplay))
    tampered["focused_minireplay_crosswalk"]["records"][0][
        "source_packet_path"
    ] = ["not", "string"]

    payload = local_lemma_audit_path_payload(focused_minireplay_payload=tampered)
    record_contract = payload["audit_path"]["focused_minireplay_record_path_contract"]

    assert payload["validation_status"] == "failed"
    assert record_contract["status"] == "failed"
    assert record_contract["malformed_record_count"] == 1
    assert record_contract["missing_template_ids"] == ["T01"]
    assert any(
        "focused_minireplay has 1 malformed records" in error
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
    summary = payload["audit_contract_summary"]

    assert payload["validation_status"] == "failed"
    assert contracts["aggregate_simple_replay"]["status"] == "failed"
    assert summary["status"] == "failed"
    assert summary["failed_component_count"] == 1
    assert summary["failed_components"] == ["layer_contracts"]
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


def test_local_lemma_audit_path_rejects_source_artifact_drift() -> None:
    aggregate = load_artifact(DEFAULT_AGGREGATE)
    simple_replay = load_artifact(DEFAULT_SIMPLE_REPLAY)
    local_replay = local_replay_crosswalk_payload(aggregate, simple_replay)
    tampered = json.loads(json.dumps(local_replay))
    tampered["source_artifacts"][0]["role"] = "renamed aggregate source"

    payload = local_lemma_audit_path_payload(
        aggregate_simple_replay_payload=tampered,
    )
    contracts = {
        contract["layer_id"]: contract
        for contract in payload["audit_path"]["layer_source_artifact_contracts"]
    }
    aggregate_contract = contracts["aggregate_simple_replay"]

    assert payload["validation_status"] == "failed"
    assert aggregate_contract["status"] == "failed"
    assert aggregate_contract["mismatched_source_artifacts"] == [
        {
            "path": "data/certificates/n9_vertex_circle_local_lemmas.json",
            "key": "role",
            "expected": "aggregate local-lemma scan",
            "observed": "renamed aggregate source",
        }
    ]
    assert any(
        "aggregate_simple_replay source_artifacts mismatch" in error
        for error in payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_malformed_source_artifact_path() -> None:
    aggregate = load_artifact(DEFAULT_AGGREGATE)
    simple_replay = load_artifact(DEFAULT_SIMPLE_REPLAY)
    local_replay = local_replay_crosswalk_payload(aggregate, simple_replay)
    tampered = json.loads(json.dumps(local_replay))
    original_path = tampered["source_artifacts"][0]["path"]
    tampered["source_artifacts"][0]["path"] = ["not", "hashable"]

    payload = local_lemma_audit_path_payload(
        aggregate_simple_replay_payload=tampered,
    )
    contracts = {
        contract["layer_id"]: contract
        for contract in payload["audit_path"]["layer_source_artifact_contracts"]
    }
    aggregate_contract = contracts["aggregate_simple_replay"]

    assert payload["validation_status"] == "failed"
    assert aggregate_contract["status"] == "failed"
    assert aggregate_contract["malformed_source_artifact_count"] == 1
    assert aggregate_contract["missing_source_artifact_paths"] == [original_path]
    assert any(
        "aggregate_simple_replay source_artifacts has 1 malformed entries" in error
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


def test_local_lemma_audit_path_rejects_missing_output_section() -> None:
    aggregate = load_artifact(DEFAULT_AGGREGATE)
    simple_replay = load_artifact(DEFAULT_SIMPLE_REPLAY)
    local_replay = local_replay_crosswalk_payload(aggregate, simple_replay)
    tampered = json.loads(json.dumps(local_replay))
    del tampered["family_crosswalk"]

    payload = local_lemma_audit_path_payload(
        aggregate_simple_replay_payload=tampered,
    )
    output_contracts = {
        contract["layer_id"]: contract
        for contract in payload["audit_path"]["layer_output_contracts"]
    }

    assert payload["validation_status"] == "failed"
    aggregate_contract = output_contracts["aggregate_simple_replay"]
    assert aggregate_contract["status"] == "failed"
    assert aggregate_contract["missing_top_level_keys"] == ["family_crosswalk"]
    assert aggregate_contract["missing_summary_keys"] == []
    assert any(
        "aggregate_simple_replay output missing top-level keys" in error
        for error in payload["validation_errors"]
    )


def test_local_lemma_audit_path_rejects_missing_output_summary_key() -> None:
    aggregate = load_artifact(DEFAULT_AGGREGATE)
    simple_replay = load_artifact(DEFAULT_SIMPLE_REPLAY)
    local_replay = local_replay_crosswalk_payload(aggregate, simple_replay)
    tampered = json.loads(json.dumps(local_replay))
    del tampered["coverage_summary"]["matched_assignment_count"]

    payload = local_lemma_audit_path_payload(
        aggregate_simple_replay_payload=tampered,
    )
    output_contracts = {
        contract["layer_id"]: contract
        for contract in payload["audit_path"]["layer_output_contracts"]
    }

    assert payload["validation_status"] == "failed"
    aggregate_contract = output_contracts["aggregate_simple_replay"]
    assert aggregate_contract["status"] == "failed"
    assert aggregate_contract["missing_top_level_keys"] == []
    assert aggregate_contract["missing_summary_keys"] == ["matched_assignment_count"]
    assert any(
        "aggregate_simple_replay output missing summary keys" in error
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


def test_local_lemma_audit_path_summary_lines_include_contract_rollups() -> None:
    payload = local_lemma_audit_path_payload()
    lines = summary_lines(payload)

    expected_lines = [
        "validation: passed",
        "layer contracts: passed",
        "layer provenance: passed",
        "layer source artifacts: passed",
        "claim-scope guards: passed",
        "layer output contracts: passed",
        "layer input contracts: passed",
        "focused minireplay record paths: passed",
        "audit contract summary: passed",
        "manifest roles: passed",
        "manifest digests: passed",
        "manifest headers: passed",
        "manifest provenance: passed",
        "manifest metadata: passed",
        "manifest claims: passed",
        "manifest consistency: passed",
        "manifest contract summary: passed",
    ]

    for line in expected_lines:
        assert line in lines
    assert lines.index("audit contract summary: passed") < lines.index(
        "input artifacts: 32"
    )
    assert lines.index("manifest contract summary: passed") > lines.index(
        "manifest consistency: passed"
    )


def test_local_lemma_audit_path_cli_text_summary_includes_contract_rollups() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_local_lemma_audit_path.py",
            "--check",
            "--assert-expected",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    lines = result.stdout.splitlines()
    assert "validation: passed" in lines
    assert "audit contract summary: passed" in lines
    assert "manifest contract summary: passed" in lines


def test_local_lemma_audit_path_failure_lines_include_contract_rollups() -> None:
    payload = local_lemma_audit_path_payload()
    tampered_manifest = json.loads(json.dumps(payload["input_manifest"]))
    for artifact in tampered_manifest["artifacts"]:
        if artifact["path"] == "data/certificates/n9_vertex_circle_local_lemmas.json":
            artifact["roles"] = ["aggregate/simple replay aggregate source"]
            break

    tampered_payload = local_lemma_audit_path_payload(
        input_manifest_payload=tampered_manifest,
    )
    lines = failure_lines(tampered_payload)

    assert lines[0] == "FAILED: local-lemma audit path"
    assert "validation: failed" in lines
    assert "audit contract summary: failed" in lines
    assert "manifest roles: failed" in lines
    assert "manifest contract summary: failed" in lines
    assert any(
        line.startswith(
            "- input_manifest role mismatch on "
            "data/certificates/n9_vertex_circle_local_lemmas.json"
        )
        for line in lines
    )


def test_local_lemma_audit_path_failure_lines_reject_scalar_errors() -> None:
    lines = failure_lines(
        {
            "validation_status": "failed",
            "validation_errors": "malformed contract payload",
        }
    )

    assert lines == [
        "FAILED: local-lemma audit path",
        "- validation_errors is not a list: str",
    ]


def test_local_lemma_audit_path_assert_expected_failure_contract_errors() -> None:
    valid_record = {
        "schema": ASSERT_EXPECTED_FAILURE_SCHEMA,
        "stage": "assert_expected",
        "exception_type": "AssertionError",
        "message": "validation errors: []",
        "validation_error_count": 0,
    }
    assert set(valid_record) == ASSERT_EXPECTED_FAILURE_KEYS
    assert (
        assert_expected_failure_contract_errors(
            valid_record,
            expected_validation_error_count=0,
        )
        == []
    )

    tampered_record = dict(valid_record)
    tampered_record.pop("schema")
    tampered_record["stage"] = "payload_construction"
    tampered_record["validation_error_count"] = True
    tampered_record["extra"] = "surprise"

    errors = assert_expected_failure_contract_errors(
        tampered_record,
        expected_validation_error_count=2,
    )
    assert "assert_expected_failure missing keys: ['schema']" in errors
    assert "assert_expected_failure unexpected keys: ['extra']" in errors
    assert "assert_expected_failure schema mismatch: None" in errors
    assert (
        "assert_expected_failure stage mismatch: 'payload_construction'"
        in errors
    )
    assert (
        "assert_expected_failure validation_error_count must be an int"
        in errors
    )


def test_local_lemma_audit_path_failure_lines_crosscheck_assert_expected_failure() -> None:
    lines = failure_lines(_assert_expected_failure_contract_tamper_payload())

    assert (
        "- assert_expected_failure schema mismatch: "
        "'erdos97.invalid_assert_expected_failure.v1'"
    ) in lines
    assert (
        "- assert_expected_failure stage mismatch: 'payload_construction'"
        in lines
    )
    assert any(
        line.startswith(
            "- assert_expected_failure validation_error_count mismatch: "
        )
        for line in lines
    )


def test_local_lemma_audit_path_cli_failure_summary_includes_contract_rollups(
    monkeypatch,
    capsys,
) -> None:
    payload = local_lemma_audit_path_payload()
    tampered_manifest = json.loads(json.dumps(payload["input_manifest"]))
    for artifact in tampered_manifest["artifacts"]:
        if artifact["path"] == "data/certificates/n9_vertex_circle_local_lemmas.json":
            artifact["roles"] = ["aggregate/simple replay aggregate source"]
            break
    tampered_payload = local_lemma_audit_path_payload(
        input_manifest_payload=tampered_manifest,
    )
    monkeypatch.setattr(
        "scripts.check_n9_vertex_circle_local_lemma_audit_path."
        "local_lemma_audit_path_payload",
        lambda: tampered_payload,
    )

    assert audit_path_main(["--check"]) == 1

    captured = capsys.readouterr()
    lines = captured.err.splitlines()
    assert captured.out == ""
    assert "FAILED: local-lemma audit path" in lines
    assert "validation: failed" in lines
    assert "audit contract summary: failed" in lines
    assert "manifest roles: failed" in lines
    assert "manifest contract summary: failed" in lines


def test_local_lemma_audit_path_cli_json_failure_includes_contract_rollups(
    monkeypatch,
    capsys,
) -> None:
    payload = local_lemma_audit_path_payload()
    tampered_manifest = json.loads(json.dumps(payload["input_manifest"]))
    for artifact in tampered_manifest["artifacts"]:
        if artifact["path"] == "data/certificates/n9_vertex_circle_local_lemmas.json":
            artifact["roles"] = ["aggregate/simple replay aggregate source"]
            break
    tampered_payload = local_lemma_audit_path_payload(
        input_manifest_payload=tampered_manifest,
    )
    monkeypatch.setattr(
        "scripts.check_n9_vertex_circle_local_lemma_audit_path."
        "local_lemma_audit_path_payload",
        lambda: tampered_payload,
    )

    assert audit_path_main(["--check", "--json"]) == 1

    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert captured.err == ""
    assert parsed["validation_status"] == "failed"
    assert parsed["audit_contract_summary"]["status"] == "failed"
    assert parsed["audit_contract_summary"]["failed_components"] == [
        "manifest_contracts",
    ]
    assert parsed["manifest_role_contract"]["status"] == "failed"
    assert parsed["manifest_contract_summary"]["status"] == "failed"
    assert parsed["manifest_contract_summary"]["failed_contracts"] == [
        "manifest_role_contract",
    ]
    assert any(
        "input_manifest role mismatch on "
        "data/certificates/n9_vertex_circle_local_lemmas.json" in error
        for error in parsed["validation_errors"]
    )


def test_local_lemma_audit_path_cli_assert_expected_failure_stays_textual(
    monkeypatch,
    capsys,
) -> None:
    payload = local_lemma_audit_path_payload()
    tampered_manifest = json.loads(json.dumps(payload["input_manifest"]))
    for artifact in tampered_manifest["artifacts"]:
        if artifact["path"] == "data/certificates/n9_vertex_circle_local_lemmas.json":
            artifact["roles"] = ["aggregate/simple replay aggregate source"]
            break
    tampered_payload = local_lemma_audit_path_payload(
        input_manifest_payload=tampered_manifest,
    )
    monkeypatch.setattr(
        "scripts.check_n9_vertex_circle_local_lemma_audit_path."
        "local_lemma_audit_path_payload",
        lambda: tampered_payload,
    )

    assert audit_path_main(["--check", "--assert-expected"]) == 1

    captured = capsys.readouterr()
    lines = captured.err.splitlines()
    assert captured.out == ""
    assert "FAILED: local-lemma audit path" in lines
    assert "manifest contract summary: failed" in lines
    assert (
        f"assert_expected failure schema: {ASSERT_EXPECTED_FAILURE_SCHEMA}"
        in lines
    )
    assert "assert_expected failure type: AssertionError" in lines
    assert "assert_expected failure validation errors: 1" in lines
    assert any(
        line.startswith("- assert_expected failed: validation errors:")
        for line in lines
    )


def test_local_lemma_audit_path_cli_scalar_validation_errors_stays_textual(
    monkeypatch,
    capsys,
) -> None:
    malformed_payload = local_lemma_audit_path_payload()
    malformed_payload["validation_status"] = "failed"
    malformed_payload["validation_errors"] = "malformed contract payload"
    monkeypatch.setattr(
        "scripts.check_n9_vertex_circle_local_lemma_audit_path."
        "local_lemma_audit_path_payload",
        lambda: malformed_payload,
    )

    assert audit_path_main(["--check"]) == 1

    captured = capsys.readouterr()
    lines = captured.err.splitlines()
    assert captured.out == ""
    assert "validation: failed" in lines
    assert "- validation_errors is not a list: str" in lines
    assert "- m" not in lines


def test_local_lemma_audit_path_cli_json_scalar_validation_errors_shape(
    monkeypatch,
    capsys,
) -> None:
    malformed_payload = local_lemma_audit_path_payload()
    malformed_payload["validation_status"] = "failed"
    malformed_payload["validation_errors"] = "malformed contract payload"
    monkeypatch.setattr(
        "scripts.check_n9_vertex_circle_local_lemma_audit_path."
        "local_lemma_audit_path_payload",
        lambda: malformed_payload,
    )

    assert audit_path_main(["--check", "--assert-expected", "--json"]) == 1

    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert captured.err == ""
    assert parsed["validation_status"] == "failed"
    assert parsed["validation_errors"][0] == "validation_errors is not a list: str"
    assert parsed["validation_errors"][1] == (
        "assert_expected failed: validation errors: 'malformed contract payload'"
    )
    assert parsed["assert_expected_failure"] == {
        "schema": ASSERT_EXPECTED_FAILURE_SCHEMA,
        "stage": "assert_expected",
        "exception_type": "AssertionError",
        "message": "validation errors: 'malformed contract payload'",
        "validation_error_count": 1,
    }


def test_local_lemma_audit_path_cli_json_assert_expected_failure_returns_payload(
    monkeypatch,
    capsys,
) -> None:
    payload = local_lemma_audit_path_payload()
    tampered_manifest = json.loads(json.dumps(payload["input_manifest"]))
    for artifact in tampered_manifest["artifacts"]:
        if artifact["path"] == "data/certificates/n9_vertex_circle_local_lemmas.json":
            artifact["roles"] = ["aggregate/simple replay aggregate source"]
            break
    tampered_payload = local_lemma_audit_path_payload(
        input_manifest_payload=tampered_manifest,
    )
    monkeypatch.setattr(
        "scripts.check_n9_vertex_circle_local_lemma_audit_path."
        "local_lemma_audit_path_payload",
        lambda: tampered_payload,
    )

    assert audit_path_main(["--check", "--assert-expected", "--json"]) == 1

    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert captured.err == ""
    assert parsed["validation_status"] == "failed"
    assert parsed["manifest_contract_summary"]["status"] == "failed"
    assert parsed["audit_contract_summary"]["failed_components"] == [
        "manifest_contracts",
    ]
    assert any(
        error.startswith("assert_expected failed: validation errors:")
        for error in parsed["validation_errors"]
    )
    assert parsed["assert_expected_failure"]["stage"] == "assert_expected"
    assert (
        parsed["assert_expected_failure"]["schema"]
        == ASSERT_EXPECTED_FAILURE_SCHEMA
    )
    assert parsed["assert_expected_failure"]["exception_type"] == "AssertionError"
    assert parsed["assert_expected_failure"]["message"].startswith(
        "validation errors:"
    )
    assert parsed["assert_expected_failure"]["validation_error_count"] == len(
        parsed["validation_errors"]
    ) - 1


def test_local_lemma_audit_path_cli_generation_failure_stays_textual(
    monkeypatch,
    capsys,
) -> None:
    def raise_payload_error() -> None:
        raise ValueError("malformed audit fixture")

    monkeypatch.setattr(
        "scripts.check_n9_vertex_circle_local_lemma_audit_path."
        "local_lemma_audit_path_payload",
        raise_payload_error,
    )

    assert audit_path_main(["--check"]) == 1

    captured = capsys.readouterr()
    lines = captured.err.splitlines()
    assert captured.out == ""
    assert lines == [
        "FAILED: local-lemma audit path",
        "failure stage: payload_construction",
        "exception type: ValueError",
        "- payload construction failed: malformed audit fixture",
    ]


def test_local_lemma_audit_path_cli_json_generation_failure_returns_payload(
    monkeypatch,
    capsys,
) -> None:
    def raise_payload_error() -> None:
        raise ValueError("malformed audit fixture")

    monkeypatch.setattr(
        "scripts.check_n9_vertex_circle_local_lemma_audit_path."
        "local_lemma_audit_path_payload",
        raise_payload_error,
    )

    assert audit_path_main(["--check", "--assert-expected", "--json"]) == 1

    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert captured.err == ""
    assert parsed["validation_status"] == "failed"
    assert parsed["failure_stage"] == "payload_construction"
    assert parsed["exception_type"] == "ValueError"
    assert parsed["validation_errors"][0] == (
        "payload construction failed: malformed audit fixture"
    )
    assert any(
        error.startswith("assert_expected failed: validation errors:")
        for error in parsed["validation_errors"]
    )
    assert parsed["assert_expected_failure"] == {
        "schema": ASSERT_EXPECTED_FAILURE_SCHEMA,
        "stage": "assert_expected",
        "exception_type": "AssertionError",
        "message": (
            "validation errors: "
            "['payload construction failed: malformed audit fixture']"
        ),
        "validation_error_count": 1,
    }


def test_local_lemma_audit_path_cli_layer_failure_summary_marks_layer_side(
    monkeypatch,
    capsys,
) -> None:
    tampered_payload = _layer_contract_trust_tamper_payload()
    monkeypatch.setattr(
        "scripts.check_n9_vertex_circle_local_lemma_audit_path."
        "local_lemma_audit_path_payload",
        lambda: tampered_payload,
    )

    assert audit_path_main(["--check"]) == 1

    captured = capsys.readouterr()
    lines = captured.err.splitlines()
    assert captured.out == ""
    assert "layer contracts: failed" in lines
    assert "audit contract summary: failed" in lines
    assert "manifest contract summary: passed" in lines
    assert any(
        line.startswith("- aggregate_simple_replay contract mismatch on trust")
        for line in lines
    )


def test_local_lemma_audit_path_cli_json_layer_failure_marks_layer_side(
    monkeypatch,
    capsys,
) -> None:
    tampered_payload = _layer_contract_trust_tamper_payload()
    monkeypatch.setattr(
        "scripts.check_n9_vertex_circle_local_lemma_audit_path."
        "local_lemma_audit_path_payload",
        lambda: tampered_payload,
    )

    assert audit_path_main(["--check", "--json"]) == 1

    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    layer_contracts = {
        contract["layer_id"]: contract
        for contract in parsed["audit_path"]["layer_contracts"]
    }
    assert captured.err == ""
    assert parsed["validation_status"] == "failed"
    assert parsed["audit_contract_summary"]["status"] == "failed"
    assert parsed["audit_contract_summary"]["failed_components"] == [
        "layer_contracts",
    ]
    assert parsed["manifest_contract_summary"]["status"] == "passed"
    assert layer_contracts["aggregate_simple_replay"]["status"] == "failed"
    assert layer_contracts["aggregate_simple_replay"]["mismatches"] == [
        {
            "key": "trust",
            "expected": "REVIEW_PENDING_DIAGNOSTIC",
            "observed": "EXACT_OBSTRUCTION",
        }
    ]
    assert any(
        "aggregate_simple_replay contract mismatch on trust" in error
        for error in parsed["validation_errors"]
    )


def test_local_lemma_audit_path_cli_json_crosschecks_assert_expected_failure(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        "scripts.check_n9_vertex_circle_local_lemma_audit_path."
        "local_lemma_audit_path_payload",
        _assert_expected_failure_contract_tamper_payload,
    )

    assert audit_path_main(["--check", "--json"]) == 1

    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert captured.err == ""
    assert parsed["validation_status"] == "failed"
    assert any(
        error == (
            "assert_expected_failure schema mismatch: "
            "'erdos97.invalid_assert_expected_failure.v1'"
        )
        for error in parsed["validation_errors"]
    )
    assert any(
        error == "assert_expected_failure stage mismatch: 'payload_construction'"
        for error in parsed["validation_errors"]
    )
    assert any(
        error.startswith(
            "assert_expected_failure validation_error_count mismatch: "
        )
        for error in parsed["validation_errors"]
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
