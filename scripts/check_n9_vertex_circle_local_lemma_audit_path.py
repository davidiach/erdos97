#!/usr/bin/env python3
"""Check the n=9 vertex-circle local-lemma audit path as one chain."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable, Mapping

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPT_DIR = ROOT / "scripts"
for path in (SRC, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_n9_vertex_circle_exhaustive_local_lemma_crosswalk import (  # noqa: E402
    DEFAULT_CLASSIFICATION,
    DEFAULT_EXHAUSTIVE,
    assert_expected_exhaustive_local_lemma_crosswalk,
    exhaustive_local_lemma_crosswalk_payload,
)
from check_n9_vertex_circle_focused_minireplay_crosswalk import (  # noqa: E402
    DEFAULT_MINIREPLAY_PATHS,
    assert_expected_focused_minireplay_crosswalk,
    focused_minireplay_crosswalk_payload,
)
from check_n9_vertex_circle_focused_packet_catalog_audit import (  # noqa: E402
    DEFAULT_LOCAL_LEMMAS as DEFAULT_FOCUSED_LOCAL_LEMMAS,
    DEFAULT_PACKET_PATHS,
    DEFAULT_TEMPLATE_CATALOG,
    DEFAULT_TEMPLATE_PACKET_PATHS,
    assert_expected_focused_packet_catalog_audit,
    focused_packet_catalog_audit_payload,
)
from check_n9_vertex_circle_local_lemma_replay_crosswalk import (  # noqa: E402
    DEFAULT_AGGREGATE,
    DEFAULT_SIMPLE_REPLAY,
    assert_expected_replay_crosswalk,
    crosswalk_payload as local_replay_crosswalk_payload,
    load_artifact,
)
from check_relation_skeleton_local_lemma_crosswalk import (  # noqa: E402
    DEFAULT_RELATION_SKELETONS,
    assert_expected_relation_local_crosswalk,
    crosswalk_payload as relation_local_crosswalk_payload,
)
from erdos97.path_display import display_path  # noqa: E402

SCHEMA = "erdos97.n9_vertex_circle_local_lemma_audit_path.v1"
STATUS = "REVIEW_PENDING_LOCAL_LEMMA_AUDIT_PATH"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Cross-artifact audit path for the review-pending n=9 vertex-circle "
    "local-lemma packets. It joins focused packet/catalog bookkeeping, "
    "focused mini-replays, aggregate/simple replay accounting, the "
    "exhaustive/local-lemma count crosswalk, and the relation-skeleton "
    "crosswalk. It does not prove packet soundness, does not prove "
    "mini-replay soundness, does not prove local-lemma completeness, does "
    "not prove frontier coverage, does not prove n=9, is not a "
    "counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_local_lemma_audit_path.py",
    "command": (
        "python scripts/check_n9_vertex_circle_local_lemma_audit_path.py "
        "--check --assert-expected --json"
    ),
}

EXPECTED_LAYER_IDS = [
    "focused_packet_catalog",
    "focused_minireplay",
    "aggregate_simple_replay",
    "exhaustive_local_lemma",
    "relation_skeleton_local_lemma",
]
EXPECTED_TEMPLATE_IDS = [f"T{index:02d}" for index in range(1, 13)]
EXPECTED_HANDOFF_EDGES = list(zip(EXPECTED_LAYER_IDS, EXPECTED_LAYER_IDS[1:]))
EXPECTED_INPUT_ARTIFACT_COUNT = 32
EXPECTED_LAYER_CONTRACTS = {
    "focused_packet_catalog": {
        "schema": "erdos97.n9_vertex_circle_focused_packet_catalog_audit.v1",
        "status": "REVIEW_PENDING_FOCUSED_PACKET_CATALOG_AUDIT",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "validation_status": "passed",
    },
    "focused_minireplay": {
        "schema": "erdos97.n9_vertex_circle_focused_minireplay_crosswalk.v1",
        "status": "REVIEW_PENDING_FOCUSED_MINIREPLAY_CROSSWALK",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "validation_status": "passed",
    },
    "aggregate_simple_replay": {
        "schema": "erdos97.n9_vertex_circle_local_lemma_replay_crosswalk.v1",
        "status": "REVIEW_PENDING_PACKET_AUDIT",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "validation_status": "passed",
    },
    "exhaustive_local_lemma": {
        "schema": "erdos97.n9_vertex_circle_exhaustive_local_lemma_crosswalk.v1",
        "status": "REVIEW_PENDING_PACKET_AUDIT",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "validation_status": "passed",
    },
    "relation_skeleton_local_lemma": {
        "schema": "erdos97.relation_skeleton_local_lemma_crosswalk.v1",
        "status": "REVIEW_PENDING_PACKET_AUDIT",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "validation_status": "passed",
    },
}
EXPECTED_LAYER_PROVENANCE = {
    "focused_packet_catalog": {
        "generator": "scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py",
        "command": (
            "python scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py "
            "--check --assert-expected --json"
        ),
    },
    "focused_minireplay": {
        "generator": "scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py",
        "command": (
            "python scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py "
            "--check --assert-expected --json"
        ),
    },
    "aggregate_simple_replay": {
        "generator": "scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py",
        "command": (
            "python scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py "
            "--check --assert-expected --json"
        ),
    },
    "exhaustive_local_lemma": {
        "generator": (
            "scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py"
        ),
        "command": (
            "python scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py "
            "--check --assert-expected --json"
        ),
    },
    "relation_skeleton_local_lemma": {
        "generator": "scripts/check_relation_skeleton_local_lemma_crosswalk.py",
        "command": (
            "python scripts/check_relation_skeleton_local_lemma_crosswalk.py "
            "--check --assert-expected --json"
        ),
    },
}
HANDOFF_COMPARE_KEYS = (
    "template_count",
    "template_ids",
    "family_count",
    "assignment_count",
    "self_edge_family_count",
    "self_edge_assignment_count",
    "strict_cycle_family_count",
    "strict_cycle_assignment_count",
)

AssertFn = Callable[[Mapping[str, Any]], None]


def default_layer_payloads() -> dict[str, Mapping[str, Any]]:
    """Build all local-lemma audit layer payloads from checked-in artifacts."""

    aggregate = load_artifact(DEFAULT_AGGREGATE)
    simple_replay = load_artifact(DEFAULT_SIMPLE_REPLAY)
    exhaustive = load_artifact(DEFAULT_EXHAUSTIVE)
    classification = load_artifact(DEFAULT_CLASSIFICATION)
    relation_skeletons = load_artifact(DEFAULT_RELATION_SKELETONS)
    for name, payload in (
        ("aggregate", aggregate),
        ("simple replay", simple_replay),
        ("exhaustive", exhaustive),
        ("classification", classification),
        ("relation skeletons", relation_skeletons),
    ):
        if not isinstance(payload, Mapping):
            raise TypeError(f"{name} artifact top level must be an object")

    return {
        "focused_packet_catalog": focused_packet_catalog_audit_payload(),
        "focused_minireplay": focused_minireplay_crosswalk_payload(),
        "aggregate_simple_replay": local_replay_crosswalk_payload(
            aggregate,
            simple_replay,
        ),
        "exhaustive_local_lemma": exhaustive_local_lemma_crosswalk_payload(
            exhaustive,
            classification,
            aggregate,
            simple_replay,
        ),
        "relation_skeleton_local_lemma": relation_local_crosswalk_payload(
            relation_skeletons,
            aggregate,
            simple_replay,
        ),
    }


def local_lemma_audit_path_payload(
    *,
    focused_packet_catalog_payload: Mapping[str, Any] | None = None,
    focused_minireplay_payload: Mapping[str, Any] | None = None,
    aggregate_simple_replay_payload: Mapping[str, Any] | None = None,
    exhaustive_local_lemma_payload: Mapping[str, Any] | None = None,
    relation_skeleton_local_lemma_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return an audit-path payload tying all local-lemma layers together."""

    provided = {
        "focused_packet_catalog": focused_packet_catalog_payload,
        "focused_minireplay": focused_minireplay_payload,
        "aggregate_simple_replay": aggregate_simple_replay_payload,
        "exhaustive_local_lemma": exhaustive_local_lemma_payload,
        "relation_skeleton_local_lemma": relation_skeleton_local_lemma_payload,
    }
    layers = default_layer_payloads()
    for layer_id, payload in provided.items():
        if payload is not None:
            layers[layer_id] = payload

    errors: list[str] = []
    _append_layer_expected_errors(errors, layers)
    layer_contracts = _layer_contracts(layers, errors)
    layer_provenance = _layer_provenance(layers, errors)
    layer_summaries = [_layer_summary(layer_id, layers[layer_id], errors) for layer_id in EXPECTED_LAYER_IDS]
    handoff_checks = _handoff_checks(layer_summaries, errors)
    coverage = _coverage_summary(layer_summaries, errors)
    input_manifest = _input_manifest()
    manifest_consistency = _manifest_consistency(layers, input_manifest, errors)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "row_size": 4,
        "audit_path": {
            "layer_count": len(layer_summaries),
            "layer_ids": [summary["layer_id"] for summary in layer_summaries],
            "layer_contracts": layer_contracts,
            "layer_provenance": layer_provenance,
            "handoff_count": len(handoff_checks),
            "handoff_checks": handoff_checks,
            "layers": layer_summaries,
        },
        "input_manifest": input_manifest,
        "manifest_consistency": manifest_consistency,
        "coverage_summary": coverage,
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit path says the stored review-pending local-lemma "
            "bookkeeping layers agree on the same 12 templates, 16 families, "
            "and 184 frontier assignments. It does not review the exhaustive "
            "brancher and does not certify packet soundness."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_local_lemma_audit_path(payload: Mapping[str, Any]) -> None:
    """Assert stable counts for the combined local-lemma audit path."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
    claim_scope = str(payload.get("claim_scope", ""))
    for required in (
        "does not prove packet soundness",
        "does not prove mini-replay soundness",
        "does not prove local-lemma completeness",
        "does not prove frontier coverage",
        "does not prove n=9",
        "not a counterexample",
        "not a global status update",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")
    _assert_expected_layer_contracts(payload)
    _assert_expected_layer_provenance(payload)
    _assert_expected_input_manifest(payload)
    _assert_expected_manifest_consistency(payload)

    audit_path = payload.get("audit_path")
    if not isinstance(audit_path, Mapping):
        raise AssertionError("audit_path must be an object")
    if audit_path.get("layer_ids") != EXPECTED_LAYER_IDS:
        raise AssertionError(f"layer ids mismatch: {audit_path.get('layer_ids')!r}")
    if audit_path.get("handoff_count") != len(EXPECTED_HANDOFF_EDGES):
        raise AssertionError(f"handoff count mismatch: {audit_path.get('handoff_count')!r}")
    handoffs = audit_path.get("handoff_checks")
    if not isinstance(handoffs, list):
        raise AssertionError("handoff_checks must be a list")
    expected_edges = [
        {"from_layer": left, "to_layer": right}
        for left, right in EXPECTED_HANDOFF_EDGES
    ]
    observed_edges = [
        {
            "from_layer": handoff.get("from_layer"),
            "to_layer": handoff.get("to_layer"),
        }
        for handoff in handoffs
    ]
    if observed_edges != expected_edges:
        raise AssertionError(f"handoff edge mismatch: {observed_edges!r}")
    for handoff in handoffs:
        if handoff.get("status") != "passed" or handoff.get("mismatches") != []:
            raise AssertionError(f"handoff failed: {handoff!r}")

    coverage = payload.get("coverage_summary")
    if not isinstance(coverage, Mapping):
        raise AssertionError("coverage_summary must be an object")
    expected = {
        "layer_count": 5,
        "template_count": 12,
        "family_count": 16,
        "assignment_count": 184,
        "self_edge_family_count": 13,
        "self_edge_assignment_count": 158,
        "strict_cycle_family_count": 3,
        "strict_cycle_assignment_count": 26,
        "relation_skeleton_count": 16,
    }
    for key, value in expected.items():
        if coverage.get(key) != value:
            raise AssertionError(
                f"coverage_summary[{key!r}] mismatch: expected {value}, "
                f"got {coverage.get(key)!r}"
            )
    if coverage.get("template_ids") != EXPECTED_TEMPLATE_IDS:
        raise AssertionError(f"template ids mismatch: {coverage.get('template_ids')!r}")


def _assert_expected_layer_contracts(payload: Mapping[str, Any]) -> None:
    audit_path = payload.get("audit_path")
    if not isinstance(audit_path, Mapping):
        raise AssertionError("audit_path must be an object")
    contracts = audit_path.get("layer_contracts")
    if not isinstance(contracts, list):
        raise AssertionError("audit_path.layer_contracts must be a list")
    observed_ids = [
        contract.get("layer_id")
        for contract in contracts
        if isinstance(contract, Mapping)
    ]
    if observed_ids != EXPECTED_LAYER_IDS:
        raise AssertionError(f"layer contract ids mismatch: {observed_ids!r}")
    for contract in contracts:
        if not isinstance(contract, Mapping):
            raise AssertionError("layer contract must be an object")
        layer_id = str(contract.get("layer_id"))
        expected = EXPECTED_LAYER_CONTRACTS[layer_id]
        if contract.get("expected") != expected:
            raise AssertionError(f"{layer_id} expected contract mismatch")
        if contract.get("observed") != expected:
            raise AssertionError(f"{layer_id} observed contract mismatch")
        if contract.get("status") != "passed" or contract.get("mismatches") != []:
            raise AssertionError(f"{layer_id} contract failed: {contract!r}")


def _assert_expected_layer_provenance(payload: Mapping[str, Any]) -> None:
    audit_path = payload.get("audit_path")
    if not isinstance(audit_path, Mapping):
        raise AssertionError("audit_path must be an object")
    provenance_checks = audit_path.get("layer_provenance")
    if not isinstance(provenance_checks, list):
        raise AssertionError("audit_path.layer_provenance must be a list")
    observed_ids = [
        check.get("layer_id")
        for check in provenance_checks
        if isinstance(check, Mapping)
    ]
    if observed_ids != EXPECTED_LAYER_IDS:
        raise AssertionError(f"layer provenance ids mismatch: {observed_ids!r}")
    for check in provenance_checks:
        if not isinstance(check, Mapping):
            raise AssertionError("layer provenance check must be an object")
        layer_id = str(check.get("layer_id"))
        expected = EXPECTED_LAYER_PROVENANCE[layer_id]
        if check.get("expected") != expected:
            raise AssertionError(f"{layer_id} expected provenance mismatch")
        if check.get("observed") != expected:
            raise AssertionError(f"{layer_id} observed provenance mismatch")
        if check.get("status") != "passed" or check.get("mismatches") != []:
            raise AssertionError(f"{layer_id} provenance failed: {check!r}")


def _assert_expected_input_manifest(payload: Mapping[str, Any]) -> None:
    manifest = payload.get("input_manifest")
    if not isinstance(manifest, Mapping):
        raise AssertionError("input_manifest must be an object")
    if manifest.get("digest_algorithm") != "sha256":
        raise AssertionError(
            f"digest_algorithm mismatch: {manifest.get('digest_algorithm')!r}"
        )
    if manifest.get("artifact_count") != EXPECTED_INPUT_ARTIFACT_COUNT:
        raise AssertionError(
            f"input artifact count mismatch: {manifest.get('artifact_count')!r}"
        )
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise AssertionError("input_manifest.artifacts must be a list")
    if len(artifacts) != EXPECTED_INPUT_ARTIFACT_COUNT:
        raise AssertionError(f"input artifact list length mismatch: {len(artifacts)}")
    paths = [artifact.get("path") for artifact in artifacts if isinstance(artifact, Mapping)]
    if len(paths) != len(set(paths)):
        raise AssertionError("input_manifest contains duplicate paths")
    required_paths = {
        "data/certificates/n9_vertex_circle_template_lemma_catalog.json",
        "data/certificates/n9_vertex_circle_local_lemmas.json",
        "data/certificates/n9_vertex_circle_exhaustive.json",
        "data/certificates/n9_vertex_circle_frontier_motif_classification.json",
        "data/certificates/relation_skeleton_catalog.json",
        "data/certificates/n9_t12_strict_cycle_minireplay.json",
    }
    missing_paths = sorted(required_paths - set(paths))
    if missing_paths:
        raise AssertionError(f"input_manifest missing paths: {missing_paths!r}")
    for artifact in artifacts:
        if not isinstance(artifact, Mapping):
            raise AssertionError("input_manifest artifact must be an object")
        digest = artifact.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise AssertionError(f"bad sha256 digest for {artifact.get('path')!r}")
        roles = artifact.get("roles")
        if not isinstance(roles, list) or not roles:
            raise AssertionError(f"missing roles for {artifact.get('path')!r}")
        size = artifact.get("size_bytes")
        if not isinstance(size, int) or size <= 0:
            raise AssertionError(f"bad size for {artifact.get('path')!r}")


def _assert_expected_manifest_consistency(payload: Mapping[str, Any]) -> None:
    consistency = payload.get("manifest_consistency")
    if not isinstance(consistency, Mapping):
        raise AssertionError("manifest_consistency must be an object")
    expected = {
        "status": "passed",
        "manifest_artifact_count": EXPECTED_INPUT_ARTIFACT_COUNT,
        "layer_referenced_artifact_count": EXPECTED_INPUT_ARTIFACT_COUNT,
        "missing_from_manifest": [],
        "unreferenced_manifest_paths": [],
    }
    for key, value in expected.items():
        if consistency.get(key) != value:
            raise AssertionError(
                f"manifest_consistency[{key!r}] mismatch: "
                f"{consistency.get(key)!r} != {value!r}"
            )


def _append_layer_expected_errors(
    errors: list[str],
    layers: Mapping[str, Mapping[str, Any]],
) -> None:
    assert_functions: dict[str, AssertFn] = {
        "focused_packet_catalog": assert_expected_focused_packet_catalog_audit,
        "focused_minireplay": assert_expected_focused_minireplay_crosswalk,
        "aggregate_simple_replay": assert_expected_replay_crosswalk,
        "exhaustive_local_lemma": assert_expected_exhaustive_local_lemma_crosswalk,
        "relation_skeleton_local_lemma": assert_expected_relation_local_crosswalk,
    }
    for layer_id in EXPECTED_LAYER_IDS:
        try:
            assert_functions[layer_id](layers[layer_id])
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"{layer_id} expected-check failed: {exc}")


def _layer_contracts(
    layers: Mapping[str, Mapping[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for layer_id in EXPECTED_LAYER_IDS:
        payload = layers[layer_id]
        expected = EXPECTED_LAYER_CONTRACTS[layer_id]
        observed = {
            "schema": payload.get("schema"),
            "status": payload.get("status"),
            "trust": payload.get("trust"),
            "validation_status": payload.get("validation_status"),
        }
        mismatches = []
        for key, expected_value in expected.items():
            observed_value = observed.get(key)
            if observed_value != expected_value:
                mismatches.append(
                    {
                        "key": key,
                        "expected": expected_value,
                        "observed": observed_value,
                    }
                )
                errors.append(
                    f"{layer_id} contract mismatch on {key}: "
                    f"{observed_value!r} != {expected_value!r}"
                )
        contracts.append(
            {
                "layer_id": layer_id,
                "expected": dict(expected),
                "observed": observed,
                "status": "passed" if not mismatches else "failed",
                "mismatches": mismatches,
            }
        )
    return contracts


def _layer_provenance(
    layers: Mapping[str, Mapping[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for layer_id in EXPECTED_LAYER_IDS:
        payload = layers[layer_id]
        expected = EXPECTED_LAYER_PROVENANCE[layer_id]
        provenance = payload.get("provenance")
        observed = _provenance_contract(provenance)
        mismatches = []
        for key, expected_value in expected.items():
            observed_value = observed.get(key)
            if observed_value != expected_value:
                mismatches.append(
                    {
                        "key": key,
                        "expected": expected_value,
                        "observed": observed_value,
                    }
                )
                errors.append(
                    f"{layer_id} provenance mismatch on {key}: "
                    f"{observed_value!r} != {expected_value!r}"
                )
        checks.append(
            {
                "layer_id": layer_id,
                "expected": dict(expected),
                "observed": observed,
                "status": "passed" if not mismatches else "failed",
                "mismatches": mismatches,
            }
        )
    return checks


def _provenance_contract(provenance: Any) -> dict[str, Any]:
    if not isinstance(provenance, Mapping):
        return {"generator": None, "command": None}
    return {
        "generator": provenance.get("generator"),
        "command": provenance.get("command"),
    }


def _input_manifest() -> dict[str, Any]:
    entries: dict[str, dict[str, Any]] = {}

    def add(path: Path, role: str) -> None:
        resolved = path.resolve()
        key = display_path(resolved, ROOT).replace("\\", "/")
        entry = entries.setdefault(
            key,
            {
                "path": key,
                "roles": [],
                "size_bytes": resolved.stat().st_size,
                "sha256": _sha256(resolved),
            },
        )
        roles = entry["roles"]
        if role not in roles:
            roles.append(role)

    add(DEFAULT_TEMPLATE_CATALOG, "focused packet/catalog template catalog")
    add(DEFAULT_FOCUSED_LOCAL_LEMMAS, "aggregate local-lemma scan")
    add(DEFAULT_AGGREGATE, "aggregate/simple replay aggregate source")
    add(DEFAULT_SIMPLE_REPLAY, "aggregate/simple replay simple source")
    add(DEFAULT_EXHAUSTIVE, "exhaustive/local-lemma exhaustive count source")
    add(DEFAULT_CLASSIFICATION, "exhaustive/local-lemma motif classification source")
    add(DEFAULT_RELATION_SKELETONS, "relation-skeleton/local-lemma source")
    for kind, path in sorted(DEFAULT_TEMPLATE_PACKET_PATHS.items()):
        add(path, f"focused packet/catalog {kind.replace('_', '-')} template packet")
    for template_id, path in sorted(DEFAULT_PACKET_PATHS.items()):
        add(path, f"focused local-lemma packet {template_id}")
    for template_id, path in sorted(DEFAULT_MINIREPLAY_PATHS.items()):
        add(path, f"focused mini-replay artifact {template_id}")

    artifacts = sorted(entries.values(), key=lambda item: item["path"])
    for artifact in artifacts:
        artifact["roles"] = sorted(artifact["roles"])
    return {
        "artifact_count": len(artifacts),
        "digest_algorithm": "sha256",
        "artifacts": artifacts,
    }


def _manifest_consistency(
    layers: Mapping[str, Mapping[str, Any]],
    input_manifest: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    manifest_paths = {
        str(artifact.get("path"))
        for artifact in input_manifest.get("artifacts", [])
        if isinstance(artifact, Mapping)
    }
    layer_paths = _layer_referenced_paths(layers)
    missing = sorted(layer_paths - manifest_paths)
    extra = sorted(manifest_paths - layer_paths)
    if missing:
        errors.append(f"input_manifest missing layer-referenced paths: {missing!r}")
    if extra:
        errors.append(f"input_manifest contains unreferenced paths: {extra!r}")
    return {
        "status": "passed" if not missing and not extra else "failed",
        "manifest_artifact_count": len(manifest_paths),
        "layer_referenced_artifact_count": len(layer_paths),
        "missing_from_manifest": missing,
        "unreferenced_manifest_paths": extra,
    }


def _layer_referenced_paths(layers: Mapping[str, Mapping[str, Any]]) -> set[str]:
    paths: set[str] = set()
    for payload in layers.values():
        for item in payload.get("source_artifacts", []):
            _add_path(paths, item.get("path") if isinstance(item, Mapping) else None)
        for item in payload.get("packet_artifacts", []):
            _add_path(paths, item.get("path") if isinstance(item, Mapping) else None)
    focused_minireplay = layers.get("focused_minireplay", {})
    summary = focused_minireplay.get("focused_minireplay_crosswalk")
    if isinstance(summary, Mapping):
        for record in summary.get("records", []):
            if isinstance(record, Mapping):
                _add_path(paths, record.get("source_packet_path"))
                _add_path(paths, record.get("minireplay_path"))
    return paths


def _add_path(paths: set[str], value: Any) -> None:
    if isinstance(value, str) and value:
        paths.add(value.replace("\\", "/"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _layer_summary(
    layer_id: str,
    payload: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    if layer_id == "focused_packet_catalog":
        summary = _required_mapping(payload, "focused_packet_catalog_audit", layer_id, errors)
        status_assignment_counts = _int_map(summary.get("status_assignment_counts"))
        return {
            "layer_id": layer_id,
            "schema": payload.get("schema"),
            "status": payload.get("status"),
            "trust": payload.get("trust"),
            "validation_status": payload.get("validation_status"),
            "template_count": int(summary.get("packet_count", -1)),
            "template_ids": _string_list(summary.get("template_ids")),
            "family_count": int(summary.get("covered_family_count", -1)),
            "assignment_count": int(summary.get("covered_assignment_count", -1)),
            "self_edge_family_count": _record_family_count(summary, "self_edge"),
            "self_edge_assignment_count": int(status_assignment_counts.get("self_edge", -1)),
            "strict_cycle_family_count": _record_family_count(summary, "strict_cycle"),
            "strict_cycle_assignment_count": int(status_assignment_counts.get("strict_cycle", -1)),
        }
    if layer_id == "focused_minireplay":
        summary = _required_mapping(payload, "focused_minireplay_crosswalk", layer_id, errors)
        status_assignment_counts = _int_map(summary.get("status_assignment_counts"))
        return {
            "layer_id": layer_id,
            "schema": payload.get("schema"),
            "status": payload.get("status"),
            "trust": payload.get("trust"),
            "validation_status": payload.get("validation_status"),
            "template_count": int(summary.get("packet_count", -1)),
            "template_ids": _string_list(summary.get("template_ids")),
            "family_count": int(summary.get("source_family_count", -1)),
            "assignment_count": int(summary.get("source_assignment_count", -1)),
            "self_edge_family_count": _record_family_count(summary, "self_edge"),
            "self_edge_assignment_count": int(status_assignment_counts.get("self_edge", -1)),
            "strict_cycle_family_count": _record_family_count(summary, "strict_cycle"),
            "strict_cycle_assignment_count": int(status_assignment_counts.get("strict_cycle", -1)),
        }
    if layer_id == "aggregate_simple_replay":
        coverage = _required_mapping(payload, "coverage_summary", layer_id, errors)
        return {
            "layer_id": layer_id,
            "schema": payload.get("schema"),
            "status": payload.get("status"),
            "trust": payload.get("trust"),
            "validation_status": payload.get("validation_status"),
            "template_count": 12,
            "template_ids": EXPECTED_TEMPLATE_IDS,
            "family_count": int(coverage.get("matched_family_count", -1)),
            "assignment_count": int(coverage.get("matched_assignment_count", -1)),
            "self_edge_family_count": int(coverage.get("self_edge_family_count", -1)),
            "self_edge_assignment_count": int(coverage.get("self_edge_assignment_count", -1)),
            "strict_cycle_family_count": int(coverage.get("strict_cycle_family_count", -1)),
            "strict_cycle_assignment_count": int(coverage.get("strict_cycle_assignment_count", -1)),
        }
    if layer_id == "exhaustive_local_lemma":
        coverage = _required_mapping(payload, "coverage_summary", layer_id, errors)
        return {
            "layer_id": layer_id,
            "schema": payload.get("schema"),
            "status": payload.get("status"),
            "trust": payload.get("trust"),
            "validation_status": payload.get("validation_status"),
            "template_count": 12,
            "template_ids": EXPECTED_TEMPLATE_IDS,
            "family_count": int(coverage.get("family_count", -1)),
            "assignment_count": int(coverage.get("local_matched_assignment_count", -1)),
            "self_edge_family_count": 13,
            "self_edge_assignment_count": int(coverage.get("self_edge_assignment_count", -1)),
            "strict_cycle_family_count": 3,
            "strict_cycle_assignment_count": int(coverage.get("strict_cycle_assignment_count", -1)),
        }
    if layer_id == "relation_skeleton_local_lemma":
        coverage = _required_mapping(payload, "coverage_summary", layer_id, errors)
        return {
            "layer_id": layer_id,
            "schema": payload.get("schema"),
            "status": payload.get("status"),
            "trust": payload.get("trust"),
            "validation_status": payload.get("validation_status"),
            "template_count": 12,
            "template_ids": EXPECTED_TEMPLATE_IDS,
            "family_count": int(coverage.get("matched_family_count", -1)),
            "assignment_count": int(coverage.get("matched_assignment_count", -1)),
            "self_edge_family_count": int(coverage.get("self_edge_family_count", -1)),
            "self_edge_assignment_count": int(coverage.get("self_edge_assignment_count", -1)),
            "strict_cycle_family_count": int(coverage.get("strict_cycle_family_count", -1)),
            "strict_cycle_assignment_count": int(coverage.get("strict_cycle_assignment_count", -1)),
            "relation_skeleton_count": int(coverage.get("relation_skeleton_count", -1)),
        }
    errors.append(f"unknown layer id: {layer_id}")
    return {"layer_id": layer_id, "validation_status": "failed"}


def _coverage_summary(
    layer_summaries: list[Mapping[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    keys = (
        "template_count",
        "family_count",
        "assignment_count",
        "self_edge_family_count",
        "self_edge_assignment_count",
        "strict_cycle_family_count",
        "strict_cycle_assignment_count",
    )
    for key in keys:
        values = tuple(int(summary.get(key, -1)) for summary in layer_summaries)
        if len(set(values)) != 1:
            errors.append(f"{key} mismatch across audit path: {values!r}")
    template_ids = [summary.get("template_ids") for summary in layer_summaries]
    if any(ids != EXPECTED_TEMPLATE_IDS for ids in template_ids):
        errors.append(f"template id mismatch across audit path: {template_ids!r}")
    for summary in layer_summaries:
        if summary.get("validation_status") != "passed":
            errors.append(f"{summary.get('layer_id')} validation_status is not passed")

    relation_summary = layer_summaries[-1]
    return {
        "layer_count": len(layer_summaries),
        "template_count": int(layer_summaries[0].get("template_count", -1)),
        "template_ids": EXPECTED_TEMPLATE_IDS,
        "family_count": int(layer_summaries[0].get("family_count", -1)),
        "assignment_count": int(layer_summaries[0].get("assignment_count", -1)),
        "self_edge_family_count": int(layer_summaries[0].get("self_edge_family_count", -1)),
        "self_edge_assignment_count": int(layer_summaries[0].get("self_edge_assignment_count", -1)),
        "strict_cycle_family_count": int(layer_summaries[0].get("strict_cycle_family_count", -1)),
        "strict_cycle_assignment_count": int(layer_summaries[0].get("strict_cycle_assignment_count", -1)),
        "relation_skeleton_count": int(relation_summary.get("relation_skeleton_count", -1)),
    }


def _handoff_checks(
    layer_summaries: list[Mapping[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    summaries = {str(summary.get("layer_id")): summary for summary in layer_summaries}
    checks: list[dict[str, Any]] = []
    for from_layer, to_layer in EXPECTED_HANDOFF_EDGES:
        left = summaries[from_layer]
        right = summaries[to_layer]
        mismatches = []
        for key in HANDOFF_COMPARE_KEYS:
            left_value = left.get(key)
            right_value = right.get(key)
            if left_value != right_value:
                mismatches.append(
                    {
                        "key": key,
                        "from_value": left_value,
                        "to_value": right_value,
                    }
                )
                errors.append(
                    f"{from_layer}->{to_layer} handoff mismatch on {key}: "
                    f"{left_value!r} != {right_value!r}"
                )
        checks.append(
            {
                "from_layer": from_layer,
                "to_layer": to_layer,
                "compared_keys": list(HANDOFF_COMPARE_KEYS),
                "status": "passed" if not mismatches else "failed",
                "mismatches": mismatches,
            }
        )
    return checks


def _required_mapping(
    payload: Mapping[str, Any],
    key: str,
    layer_id: str,
    errors: list[str],
) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"{layer_id}: {key} must be an object")
        return {}
    return value


def _int_map(value: Any) -> dict[str, int]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): int(item) for key, item in value.items()}


def _record_family_count(summary: Mapping[str, Any], status: str) -> int:
    records = summary.get("packet_records", summary.get("records"))
    if not isinstance(records, list):
        return -1
    family_ids: set[str] = set()
    for record in records:
        if not isinstance(record, Mapping) or record.get("status") != status:
            continue
        family_ids.update(_string_list(record.get("family_ids")))
    return len(family_ids)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _summary_status(items: Any) -> str:
    if not isinstance(items, list):
        return "failed"
    return "passed" if all(item.get("status") == "passed" for item in items) else "failed"


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    coverage = payload["coverage_summary"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"layers: {coverage['layer_count']}",
        "layer contracts: "
        f"{_summary_status(payload['audit_path']['layer_contracts'])}",
        "layer provenance: "
        f"{_summary_status(payload['audit_path']['layer_provenance'])}",
        f"handoffs: {payload['audit_path']['handoff_count']}",
        f"input artifacts: {payload['input_manifest']['artifact_count']}",
        f"manifest consistency: {payload['manifest_consistency']['status']}",
        f"templates: {coverage['template_count']}",
        f"families: {coverage['family_count']}",
        f"assignments: {coverage['assignment_count']}",
        (
            "self-edge: "
            f"{coverage['self_edge_family_count']} families, "
            f"{coverage['self_edge_assignment_count']} assignments"
        ),
        (
            "strict-cycle: "
            f"{coverage['strict_cycle_family_count']} families, "
            f"{coverage['strict_cycle_assignment_count']} assignments"
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the audit path")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload.")
    args = parser.parse_args(argv)

    try:
        payload = local_lemma_audit_path_payload()
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        payload = {
            "schema": SCHEMA,
            "status": STATUS,
            "trust": TRUST,
            "claim_scope": CLAIM_SCOPE,
            "validation_status": "failed",
            "validation_errors": [str(exc)],
            "provenance": dict(PROVENANCE),
        }

    if args.assert_expected:
        assert_expected_local_lemma_audit_path(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle local-lemma audit path")
        for line in summary_lines(payload):
            print(line)
        print("OK: local-lemma audit path checks passed")
    else:
        print("FAILED: local-lemma audit path", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
