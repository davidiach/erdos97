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
SOURCE_ARTIFACT_KEYS = ("path", "role", "schema", "status", "trust")
EXPECTED_LAYER_SOURCE_ARTIFACTS = {
    "focused_packet_catalog": (
        {
            "path": "data/certificates/n9_vertex_circle_template_lemma_catalog.json",
            "role": "template lemma-candidate catalog",
            "schema": "erdos97.n9_vertex_circle_template_lemma_catalog.v1",
            "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": "data/certificates/n9_vertex_circle_local_lemmas.json",
            "role": "aggregate local-lemma scan",
            "schema": "erdos97.n9_vertex_circle_local_lemmas.v1",
            "status": "REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": "data/certificates/n9_vertex_circle_self_edge_template_packet.json",
            "role": "self-edge template packet",
            "schema": "erdos97.n9_vertex_circle_self_edge_template_packet.v1",
            "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": "data/certificates/n9_vertex_circle_strict_cycle_template_packet.json",
            "role": "strict-cycle template packet",
            "schema": "erdos97.n9_vertex_circle_strict_cycle_template_packet.v1",
            "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
    ),
    "focused_minireplay": (),
    "aggregate_simple_replay": (
        {
            "path": "data/certificates/n9_vertex_circle_local_lemmas.json",
            "role": "aggregate local-lemma scan",
            "schema": "erdos97.n9_vertex_circle_local_lemmas.v1",
            "status": "REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": (
                "data/certificates/"
                "n9_vertex_circle_local_lemma_simple_replay.json"
            ),
            "role": "simple packet replay audit",
            "schema": "erdos97.n9_vertex_circle_local_lemma_simple_replay.v1",
            "status": "REVIEW_PENDING_PACKET_AUDIT",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
    ),
    "exhaustive_local_lemma": (
        {
            "path": "data/certificates/n9_vertex_circle_exhaustive.json",
            "role": "review-pending exhaustive n=9 count artifact",
            "schema": "n9_vertex_circle_exhaustive_v1",
            "status": None,
            "trust": "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
        },
        {
            "path": (
                "data/certificates/"
                "n9_vertex_circle_frontier_motif_classification.json"
            ),
            "role": "frontier assignment motif classification",
            "schema": (
                "erdos97.n9_vertex_circle_frontier_motif_classification.v1"
            ),
            "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": "data/certificates/n9_vertex_circle_local_lemmas.json",
            "role": "aggregate local-lemma scan",
            "schema": "erdos97.n9_vertex_circle_local_lemmas.v1",
            "status": "REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": (
                "data/certificates/"
                "n9_vertex_circle_local_lemma_simple_replay.json"
            ),
            "role": "simple local-lemma replay audit",
            "schema": "erdos97.n9_vertex_circle_local_lemma_simple_replay.v1",
            "status": "REVIEW_PENDING_PACKET_AUDIT",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
    ),
    "relation_skeleton_local_lemma": (
        {
            "path": "data/certificates/relation_skeleton_catalog.json",
            "role": "relation-skeleton catalog",
            "schema": "erdos97.relation_skeleton_catalog.v1",
            "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": "data/certificates/n9_vertex_circle_local_lemmas.json",
            "role": "aggregate local-lemma scan",
            "schema": "erdos97.n9_vertex_circle_local_lemmas.v1",
            "status": "REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": (
                "data/certificates/"
                "n9_vertex_circle_local_lemma_simple_replay.json"
            ),
            "role": "simple local-lemma replay audit",
            "schema": "erdos97.n9_vertex_circle_local_lemma_simple_replay.v1",
            "status": "REVIEW_PENDING_PACKET_AUDIT",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
    ),
}
CLAIM_SCOPE_GUARDS = {
    "mentions_n9_scope": (("n=9",),),
    "denies_proof": (("does not prove",), ("not a proof",)),
    "denies_counterexample": (
        ("not a counterexample",),
        ("does not prove", "counterexample"),
    ),
    "denies_global_status_update": (
        ("not a global status update",),
        ("does not prove", "official/global status update"),
    ),
}
EXPECTED_LAYER_OUTPUT_CONTRACTS = {
    "focused_packet_catalog": {
        "summary_key": "focused_packet_catalog_audit",
        "required_top_level_keys": ("source_artifacts", "packet_artifacts"),
        "required_summary_keys": (
            "packet_count",
            "template_ids",
            "covered_family_count",
            "covered_assignment_count",
            "packet_records",
            "status_counts",
            "status_assignment_counts",
        ),
    },
    "focused_minireplay": {
        "summary_key": "focused_minireplay_crosswalk",
        "required_top_level_keys": (),
        "required_summary_keys": (
            "minireplay_count",
            "packet_count",
            "template_ids",
            "source_family_count",
            "source_assignment_count",
            "records",
            "status_counts",
            "status_assignment_counts",
        ),
    },
    "aggregate_simple_replay": {
        "summary_key": "coverage_summary",
        "required_top_level_keys": (
            "source_artifacts",
            "family_crosswalk",
            "focused_crosscheck_summary",
        ),
        "required_summary_keys": (
            "expected_family_count",
            "expected_assignment_count",
            "matched_family_count",
            "matched_assignment_count",
            "self_edge_family_count",
            "self_edge_assignment_count",
            "strict_cycle_family_count",
            "strict_cycle_assignment_count",
        ),
    },
    "exhaustive_local_lemma": {
        "summary_key": "coverage_summary",
        "required_top_level_keys": (
            "source_artifacts",
            "family_crosswalk",
            "local_replay_crosswalk_summary",
        ),
        "required_summary_keys": (
            "classification_assignment_count",
            "exhaustive_frontier_assignment_count",
            "family_count",
            "local_matched_assignment_count",
            "self_edge_assignment_count",
            "strict_cycle_assignment_count",
        ),
    },
    "relation_skeleton_local_lemma": {
        "summary_key": "coverage_summary",
        "required_top_level_keys": (
            "source_artifacts",
            "family_crosswalk",
            "local_replay_crosswalk_summary",
        ),
        "required_summary_keys": (
            "expected_family_count",
            "expected_assignment_count",
            "local_family_count",
            "matched_family_count",
            "matched_assignment_count",
            "relation_skeleton_count",
            "self_edge_family_count",
            "self_edge_assignment_count",
            "strict_cycle_family_count",
            "strict_cycle_assignment_count",
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
    input_manifest_payload: Mapping[str, Any] | None = None,
    manifest_header_payloads: Mapping[str, Any] | None = None,
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
    layer_source_artifact_contracts = _layer_source_artifact_contracts(
        layers, errors
    )
    claim_scope_guards = _claim_scope_guards(layers, errors)
    layer_output_contracts = _layer_output_contracts(layers, errors)
    layer_input_contracts = _layer_input_contracts(layers, errors)
    focused_record_path_contract = _focused_minireplay_record_path_contract(
        layers["focused_minireplay"], errors
    )
    layer_summaries = [_layer_summary(layer_id, layers[layer_id], errors) for layer_id in EXPECTED_LAYER_IDS]
    handoff_checks = _handoff_checks(layer_summaries, errors)
    coverage = _coverage_summary(layer_summaries, errors)
    input_manifest = (
        dict(input_manifest_payload)
        if input_manifest_payload is not None
        else _input_manifest()
    )
    manifest_role_contract = _manifest_role_contract(input_manifest, errors)
    manifest_digest_contract = _manifest_digest_contract(input_manifest, errors)
    manifest_header_contract = _manifest_header_contract(
        input_manifest,
        errors,
        header_payloads=manifest_header_payloads,
    )
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
            "layer_source_artifact_contracts": layer_source_artifact_contracts,
            "claim_scope_guards": claim_scope_guards,
            "layer_output_contracts": layer_output_contracts,
            "layer_input_contracts": layer_input_contracts,
            "focused_minireplay_record_path_contract": focused_record_path_contract,
            "handoff_count": len(handoff_checks),
            "handoff_checks": handoff_checks,
            "layers": layer_summaries,
        },
        "input_manifest": input_manifest,
        "manifest_role_contract": manifest_role_contract,
        "manifest_digest_contract": manifest_digest_contract,
        "manifest_header_contract": manifest_header_contract,
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
    _assert_expected_layer_source_artifact_contracts(payload)
    _assert_expected_claim_scope_guards(payload)
    _assert_expected_layer_output_contracts(payload)
    _assert_expected_layer_input_contracts(payload)
    _assert_expected_focused_minireplay_record_path_contract(payload)
    _assert_expected_input_manifest(payload)
    _assert_expected_manifest_role_contract(payload)
    _assert_expected_manifest_digest_contract(payload)
    _assert_expected_manifest_header_contract(payload)
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


def _assert_expected_layer_source_artifact_contracts(
    payload: Mapping[str, Any],
) -> None:
    audit_path = payload.get("audit_path")
    if not isinstance(audit_path, Mapping):
        raise AssertionError("audit_path must be an object")
    contracts = audit_path.get("layer_source_artifact_contracts")
    if not isinstance(contracts, list):
        raise AssertionError(
            "audit_path.layer_source_artifact_contracts must be a list"
        )
    observed_ids = [
        contract.get("layer_id")
        for contract in contracts
        if isinstance(contract, Mapping)
    ]
    if observed_ids != EXPECTED_LAYER_IDS:
        raise AssertionError(
            f"layer source artifact contract ids mismatch: {observed_ids!r}"
        )
    for contract in contracts:
        if not isinstance(contract, Mapping):
            raise AssertionError("layer source artifact contract must be an object")
        layer_id = str(contract.get("layer_id"))
        expected = _expected_source_artifacts(layer_id)
        expected_type = "missing" if layer_id == "focused_minireplay" else "list"
        if contract.get("source_artifacts_type") != expected_type:
            raise AssertionError(f"{layer_id} source_artifacts type mismatch")
        if contract.get("expected_artifacts") != expected:
            raise AssertionError(f"{layer_id} expected source artifacts mismatch")
        if contract.get("observed_artifacts") != expected:
            raise AssertionError(f"{layer_id} observed source artifacts mismatch")
        if contract.get("expected_artifact_count") != len(expected):
            raise AssertionError(f"{layer_id} source artifact count mismatch")
        if contract.get("observed_artifact_count") != len(expected):
            raise AssertionError(f"{layer_id} observed source artifact count mismatch")
        if contract.get("status") != "passed":
            raise AssertionError(
                f"{layer_id} source artifact contract failed: {contract!r}"
            )
        for key in (
            "missing_source_artifact_paths",
            "unexpected_source_artifact_paths",
            "duplicate_source_artifact_paths",
            "mismatched_source_artifacts",
        ):
            if contract.get(key) != []:
                raise AssertionError(f"{layer_id} {key} is not empty")
        if contract.get("malformed_source_artifact_count") != 0:
            raise AssertionError(f"{layer_id} malformed source artifacts")


def _assert_expected_claim_scope_guards(payload: Mapping[str, Any]) -> None:
    audit_path = payload.get("audit_path")
    if not isinstance(audit_path, Mapping):
        raise AssertionError("audit_path must be an object")
    guard_checks = audit_path.get("claim_scope_guards")
    if not isinstance(guard_checks, list):
        raise AssertionError("audit_path.claim_scope_guards must be a list")
    observed_ids = [
        check.get("layer_id")
        for check in guard_checks
        if isinstance(check, Mapping)
    ]
    if observed_ids != EXPECTED_LAYER_IDS:
        raise AssertionError(f"claim-scope guard ids mismatch: {observed_ids!r}")
    for check in guard_checks:
        if not isinstance(check, Mapping):
            raise AssertionError("claim-scope guard check must be an object")
        if check.get("status") != "passed" or check.get("missing_guards") != []:
            raise AssertionError(f"claim-scope guard failed: {check!r}")
        results = check.get("guard_results")
        if not isinstance(results, list):
            raise AssertionError("claim-scope guard_results must be a list")
        if [result.get("guard") for result in results] != list(CLAIM_SCOPE_GUARDS):
            raise AssertionError(f"claim-scope guard order mismatch: {results!r}")
        for result in results:
            if result.get("status") != "passed":
                raise AssertionError(f"claim-scope guard result failed: {result!r}")


def _assert_expected_layer_output_contracts(payload: Mapping[str, Any]) -> None:
    audit_path = payload.get("audit_path")
    if not isinstance(audit_path, Mapping):
        raise AssertionError("audit_path must be an object")
    output_contracts = audit_path.get("layer_output_contracts")
    if not isinstance(output_contracts, list):
        raise AssertionError("audit_path.layer_output_contracts must be a list")
    observed_ids = [
        contract.get("layer_id")
        for contract in output_contracts
        if isinstance(contract, Mapping)
    ]
    if observed_ids != EXPECTED_LAYER_IDS:
        raise AssertionError(f"layer output contract ids mismatch: {observed_ids!r}")
    for contract in output_contracts:
        if not isinstance(contract, Mapping):
            raise AssertionError("layer output contract must be an object")
        layer_id = str(contract.get("layer_id"))
        expected = _expected_output_contract(layer_id)
        if contract.get("expected") != expected:
            raise AssertionError(f"{layer_id} expected output contract mismatch")
        if contract.get("status") != "passed":
            raise AssertionError(f"{layer_id} output contract failed: {contract!r}")
        if contract.get("missing_top_level_keys") != []:
            raise AssertionError(f"{layer_id} missing top-level output keys")
        if contract.get("missing_summary_keys") != []:
            raise AssertionError(f"{layer_id} missing summary output keys")
        if contract.get("summary_type") != "object":
            raise AssertionError(f"{layer_id} summary output is not an object")


def _assert_expected_layer_input_contracts(payload: Mapping[str, Any]) -> None:
    audit_path = payload.get("audit_path")
    if not isinstance(audit_path, Mapping):
        raise AssertionError("audit_path must be an object")
    input_contracts = audit_path.get("layer_input_contracts")
    if not isinstance(input_contracts, list):
        raise AssertionError("audit_path.layer_input_contracts must be a list")
    observed_ids = [
        contract.get("layer_id")
        for contract in input_contracts
        if isinstance(contract, Mapping)
    ]
    if observed_ids != EXPECTED_LAYER_IDS:
        raise AssertionError(f"layer input contract ids mismatch: {observed_ids!r}")
    expected_paths = _expected_layer_input_paths()
    for contract in input_contracts:
        if not isinstance(contract, Mapping):
            raise AssertionError("layer input contract must be an object")
        layer_id = str(contract.get("layer_id"))
        expected = sorted(expected_paths[layer_id])
        if contract.get("expected_paths") != expected:
            raise AssertionError(f"{layer_id} expected input paths mismatch")
        if contract.get("observed_paths") != expected:
            raise AssertionError(f"{layer_id} observed input paths mismatch")
        if contract.get("status") != "passed":
            raise AssertionError(f"{layer_id} input contract failed: {contract!r}")
        if contract.get("missing_input_paths") != []:
            raise AssertionError(f"{layer_id} missing input paths")
        if contract.get("unexpected_input_paths") != []:
            raise AssertionError(f"{layer_id} unexpected input paths")


def _assert_expected_focused_minireplay_record_path_contract(
    payload: Mapping[str, Any],
) -> None:
    audit_path = payload.get("audit_path")
    if not isinstance(audit_path, Mapping):
        raise AssertionError("audit_path must be an object")
    contract = audit_path.get("focused_minireplay_record_path_contract")
    if not isinstance(contract, Mapping):
        raise AssertionError(
            "audit_path.focused_minireplay_record_path_contract must be an object"
        )
    expected = _expected_focused_minireplay_records()
    if contract.get("records_type") != "list":
        raise AssertionError("focused minireplay records must be a list")
    if contract.get("expected_record_count") != len(expected):
        raise AssertionError("focused minireplay expected record count mismatch")
    if contract.get("observed_record_count") != len(expected):
        raise AssertionError("focused minireplay observed record count mismatch")
    if contract.get("expected_records") != expected:
        raise AssertionError("focused minireplay expected records mismatch")
    if contract.get("observed_records") != expected:
        raise AssertionError("focused minireplay observed records mismatch")
    if contract.get("status") != "passed":
        raise AssertionError(
            f"focused minireplay record-path contract failed: {contract!r}"
        )
    for key in (
        "missing_template_ids",
        "unexpected_template_ids",
        "duplicate_template_ids",
        "mismatched_record_paths",
    ):
        if contract.get(key) != []:
            raise AssertionError(f"focused minireplay {key} is not empty")
    if contract.get("malformed_record_count") != 0:
        raise AssertionError("focused minireplay malformed records")


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


def _assert_expected_manifest_role_contract(payload: Mapping[str, Any]) -> None:
    contract = payload.get("manifest_role_contract")
    if not isinstance(contract, Mapping):
        raise AssertionError("manifest_role_contract must be an object")
    expected = _manifest_role_records(_expected_manifest_roles())
    if contract.get("status") != "passed":
        raise AssertionError(f"manifest role contract failed: {contract!r}")
    if contract.get("expected_path_count") != len(expected):
        raise AssertionError("manifest role expected path count mismatch")
    if contract.get("observed_path_count") != len(expected):
        raise AssertionError("manifest role observed path count mismatch")
    if contract.get("expected_roles") != expected:
        raise AssertionError("manifest role expected records mismatch")
    if contract.get("observed_roles") != expected:
        raise AssertionError("manifest role observed records mismatch")
    for key in (
        "missing_manifest_role_paths",
        "unexpected_manifest_role_paths",
        "duplicate_manifest_role_paths",
        "mismatched_manifest_roles",
    ):
        if contract.get(key) != []:
            raise AssertionError(f"manifest role {key} is not empty")
    if contract.get("malformed_manifest_role_count") != 0:
        raise AssertionError("manifest role contract has malformed entries")


def _assert_expected_manifest_digest_contract(payload: Mapping[str, Any]) -> None:
    contract = payload.get("manifest_digest_contract")
    if not isinstance(contract, Mapping):
        raise AssertionError("manifest_digest_contract must be an object")
    expected = _manifest_digest_records(_expected_manifest_digests())
    if contract.get("status") != "passed":
        raise AssertionError(f"manifest digest contract failed: {contract!r}")
    if contract.get("expected_path_count") != len(expected):
        raise AssertionError("manifest digest expected path count mismatch")
    if contract.get("observed_path_count") != len(expected):
        raise AssertionError("manifest digest observed path count mismatch")
    if contract.get("expected_digests") != expected:
        raise AssertionError("manifest digest expected records mismatch")
    if contract.get("observed_digests") != expected:
        raise AssertionError("manifest digest observed records mismatch")
    for key in (
        "missing_manifest_digest_paths",
        "unexpected_manifest_digest_paths",
        "duplicate_manifest_digest_paths",
        "mismatched_manifest_digests",
    ):
        if contract.get(key) != []:
            raise AssertionError(f"manifest digest {key} is not empty")
    if contract.get("malformed_manifest_digest_count") != 0:
        raise AssertionError("manifest digest contract has malformed entries")


def _assert_expected_manifest_header_contract(payload: Mapping[str, Any]) -> None:
    contract = payload.get("manifest_header_contract")
    if not isinstance(contract, Mapping):
        raise AssertionError("manifest_header_contract must be an object")
    expected = _manifest_header_records(_expected_manifest_headers())
    if contract.get("status") != "passed":
        raise AssertionError(f"manifest header contract failed: {contract!r}")
    if contract.get("expected_path_count") != len(expected):
        raise AssertionError("manifest header expected path count mismatch")
    if contract.get("observed_path_count") != len(expected):
        raise AssertionError("manifest header observed path count mismatch")
    if contract.get("expected_headers") != expected:
        raise AssertionError("manifest header expected records mismatch")
    if contract.get("observed_headers") != expected:
        raise AssertionError("manifest header observed records mismatch")
    for key in (
        "missing_manifest_header_paths",
        "unexpected_manifest_header_paths",
        "duplicate_manifest_header_paths",
        "mismatched_manifest_headers",
    ):
        if contract.get(key) != []:
            raise AssertionError(f"manifest header {key} is not empty")
    if contract.get("malformed_manifest_header_count") != 0:
        raise AssertionError("manifest header contract has malformed entries")


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


def _layer_source_artifact_contracts(
    layers: Mapping[str, Mapping[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for layer_id in EXPECTED_LAYER_IDS:
        payload = layers[layer_id]
        expected = _expected_source_artifacts(layer_id)
        source_artifacts = payload.get("source_artifacts", [])
        source_artifacts_type = (
            "missing"
            if "source_artifacts" not in payload
            else _source_artifacts_type(source_artifacts)
        )
        observed, malformed_count = _observed_source_artifacts(source_artifacts)
        expected_by_path = {item["path"]: item for item in expected}
        observed_by_path = {item["path"]: item for item in observed}
        observed_paths = [item["path"] for item in observed]
        duplicate_paths = sorted(
            {path for path in observed_paths if observed_paths.count(path) > 1},
            key=str,
        )
        missing = sorted(set(expected_by_path) - set(observed_by_path), key=str)
        unexpected = sorted(set(observed_by_path) - set(expected_by_path), key=str)
        mismatches = _source_artifact_mismatches(expected_by_path, observed_by_path)
        bad_section_type = source_artifacts_type not in {"list", "missing"}

        if bad_section_type:
            errors.append(
                f"{layer_id} source_artifacts has type {source_artifacts_type}"
            )
        if malformed_count:
            errors.append(
                f"{layer_id} source_artifacts has {malformed_count} malformed entries"
            )
        if duplicate_paths:
            errors.append(
                f"{layer_id} source_artifacts duplicate paths: {duplicate_paths!r}"
            )
        if missing:
            errors.append(f"{layer_id} source_artifacts missing paths: {missing!r}")
        if unexpected:
            errors.append(
                f"{layer_id} source_artifacts unexpected paths: {unexpected!r}"
            )
        for mismatch in mismatches:
            errors.append(
                f"{layer_id} source_artifacts mismatch on "
                f"{mismatch['path']} {mismatch['key']}: "
                f"{mismatch['observed']!r} != {mismatch['expected']!r}"
            )

        contracts.append(
            {
                "layer_id": layer_id,
                "source_artifacts_type": source_artifacts_type,
                "expected_artifact_count": len(expected),
                "observed_artifact_count": len(observed),
                "expected_artifacts": expected,
                "observed_artifacts": _sort_source_artifacts(observed),
                "missing_source_artifact_paths": missing,
                "unexpected_source_artifact_paths": unexpected,
                "duplicate_source_artifact_paths": duplicate_paths,
                "mismatched_source_artifacts": mismatches,
                "malformed_source_artifact_count": malformed_count,
                "status": (
                    "passed"
                    if not (
                        bad_section_type
                        or malformed_count
                        or duplicate_paths
                        or missing
                        or unexpected
                        or mismatches
                    )
                    else "failed"
                ),
            }
        )
    return contracts


def _expected_source_artifacts(layer_id: str) -> list[dict[str, Any]]:
    return _sort_source_artifacts(
        [dict(item) for item in EXPECTED_LAYER_SOURCE_ARTIFACTS[layer_id]]
    )


def _observed_source_artifacts(source_artifacts: Any) -> tuple[list[dict[str, Any]], int]:
    if not isinstance(source_artifacts, list):
        return [], 0
    observed: list[dict[str, Any]] = []
    malformed_count = 0
    for item in source_artifacts:
        if isinstance(item, Mapping):
            contract = _source_artifact_contract(item)
            if isinstance(contract["path"], str):
                observed.append(contract)
            else:
                malformed_count += 1
        else:
            malformed_count += 1
    return _sort_source_artifacts(observed), malformed_count


def _source_artifact_contract(item: Mapping[str, Any]) -> dict[str, Any]:
    return {key: item.get(key) for key in SOURCE_ARTIFACT_KEYS}


def _source_artifact_mismatches(
    expected_by_path: Mapping[str, Mapping[str, Any]],
    observed_by_path: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []
    for path in sorted(set(expected_by_path) & set(observed_by_path)):
        expected = expected_by_path[path]
        observed = observed_by_path[path]
        for key in SOURCE_ARTIFACT_KEYS:
            if observed.get(key) != expected.get(key):
                mismatches.append(
                    {
                        "path": path,
                        "key": key,
                        "expected": expected.get(key),
                        "observed": observed.get(key),
                    }
                )
    return mismatches


def _sort_source_artifacts(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(artifacts, key=lambda item: str(item["path"]))


def _source_artifacts_type(source_artifacts: Any) -> str:
    if isinstance(source_artifacts, list):
        return "list"
    if isinstance(source_artifacts, Mapping):
        return "object"
    return type(source_artifacts).__name__


def _claim_scope_guards(
    layers: Mapping[str, Mapping[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for layer_id in EXPECTED_LAYER_IDS:
        claim_scope = str(layers[layer_id].get("claim_scope", ""))
        guard_results = []
        missing_guards = []
        for guard, alternatives in CLAIM_SCOPE_GUARDS.items():
            matched_tokens = _matched_claim_scope_tokens(claim_scope, alternatives)
            status = "passed" if matched_tokens else "failed"
            if not matched_tokens:
                missing_guards.append(guard)
            guard_results.append(
                {
                    "guard": guard,
                    "status": status,
                    "matched_tokens": matched_tokens,
                    "accepted_token_sets": [list(tokens) for tokens in alternatives],
                }
            )
        if missing_guards:
            errors.append(f"{layer_id} claim_scope missing guards: {missing_guards!r}")
        checks.append(
            {
                "layer_id": layer_id,
                "status": "passed" if not missing_guards else "failed",
                "missing_guards": missing_guards,
                "guard_results": guard_results,
            }
        )
    return checks


def _matched_claim_scope_tokens(
    claim_scope: str,
    alternatives: tuple[tuple[str, ...], ...],
) -> list[str]:
    lowered = claim_scope.lower()
    for tokens in alternatives:
        if all(token in lowered for token in tokens):
            return list(tokens)
    return []


def _layer_output_contracts(
    layers: Mapping[str, Mapping[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for layer_id in EXPECTED_LAYER_IDS:
        payload = layers[layer_id]
        expected = _expected_output_contract(layer_id)
        summary_key = str(expected["summary_key"])
        summary = payload.get(summary_key)
        summary_type = "object" if isinstance(summary, Mapping) else type(summary).__name__
        top_level_keys = set(payload)
        summary_keys = set(summary) if isinstance(summary, Mapping) else set()
        missing_top_level_keys = sorted(
            set(expected["required_top_level_keys"]) - top_level_keys
        )
        missing_summary_keys = sorted(
            set(expected["required_summary_keys"]) - summary_keys
        )
        if summary_type != "object":
            errors.append(f"{layer_id} output summary {summary_key!r} is not an object")
        if missing_top_level_keys:
            errors.append(
                f"{layer_id} output missing top-level keys: {missing_top_level_keys!r}"
            )
        if missing_summary_keys:
            errors.append(
                f"{layer_id} output missing summary keys: {missing_summary_keys!r}"
            )
        contracts.append(
            {
                "layer_id": layer_id,
                "expected": expected,
                "summary_type": summary_type,
                "observed_top_level_keys": sorted(top_level_keys),
                "observed_summary_keys": sorted(summary_keys),
                "missing_top_level_keys": missing_top_level_keys,
                "missing_summary_keys": missing_summary_keys,
                "status": (
                    "passed"
                    if summary_type == "object"
                    and not missing_top_level_keys
                    and not missing_summary_keys
                    else "failed"
                ),
            }
        )
    return contracts


def _expected_output_contract(layer_id: str) -> dict[str, Any]:
    contract = EXPECTED_LAYER_OUTPUT_CONTRACTS[layer_id]
    return {
        "summary_key": contract["summary_key"],
        "required_top_level_keys": list(contract["required_top_level_keys"]),
        "required_summary_keys": list(contract["required_summary_keys"]),
    }


def _layer_input_contracts(
    layers: Mapping[str, Mapping[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    expected_paths = _expected_layer_input_paths()
    contracts: list[dict[str, Any]] = []
    for layer_id in EXPECTED_LAYER_IDS:
        observed = _layer_referenced_paths({layer_id: layers[layer_id]})
        expected = expected_paths[layer_id]
        missing = sorted(expected - observed)
        unexpected = sorted(observed - expected)
        if missing:
            errors.append(f"{layer_id} input missing paths: {missing!r}")
        if unexpected:
            errors.append(f"{layer_id} input unexpected paths: {unexpected!r}")
        contracts.append(
            {
                "layer_id": layer_id,
                "expected_path_count": len(expected),
                "observed_path_count": len(observed),
                "expected_paths": sorted(expected),
                "observed_paths": sorted(observed),
                "missing_input_paths": missing,
                "unexpected_input_paths": unexpected,
                "status": "passed" if not missing and not unexpected else "failed",
            }
        )
    return contracts


def _expected_layer_input_paths() -> dict[str, set[str]]:
    return {
        "focused_packet_catalog": _path_set(
            [
                DEFAULT_TEMPLATE_CATALOG,
                DEFAULT_FOCUSED_LOCAL_LEMMAS,
                *DEFAULT_TEMPLATE_PACKET_PATHS.values(),
                *DEFAULT_PACKET_PATHS.values(),
            ]
        ),
        "focused_minireplay": _path_set(
            [
                *DEFAULT_PACKET_PATHS.values(),
                *DEFAULT_MINIREPLAY_PATHS.values(),
            ]
        ),
        "aggregate_simple_replay": _path_set(
            [DEFAULT_AGGREGATE, DEFAULT_SIMPLE_REPLAY]
        ),
        "exhaustive_local_lemma": _path_set(
            [
                DEFAULT_EXHAUSTIVE,
                DEFAULT_CLASSIFICATION,
                DEFAULT_AGGREGATE,
                DEFAULT_SIMPLE_REPLAY,
            ]
        ),
        "relation_skeleton_local_lemma": _path_set(
            [DEFAULT_RELATION_SKELETONS, DEFAULT_AGGREGATE, DEFAULT_SIMPLE_REPLAY]
        ),
    }


def _path_set(paths: list[Path]) -> set[str]:
    return {_artifact_path_key(path) for path in paths}


def _artifact_path_key(path: Path) -> str:
    return display_path(path.resolve(), ROOT).replace("\\", "/")


def _focused_minireplay_record_path_contract(
    focused_minireplay: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    expected = _expected_focused_minireplay_records()
    summary = focused_minireplay.get("focused_minireplay_crosswalk")
    records = summary.get("records", []) if isinstance(summary, Mapping) else []
    records_type = "list" if isinstance(records, list) else type(records).__name__
    observed, malformed_count = _observed_focused_minireplay_records(records)
    expected_by_template = {record["template_id"]: record for record in expected}
    observed_by_template = {record["template_id"]: record for record in observed}
    observed_template_ids = [record["template_id"] for record in observed]
    duplicate_template_ids = sorted(
        {
            template_id
            for template_id in observed_template_ids
            if observed_template_ids.count(template_id) > 1
        }
    )
    missing = sorted(set(expected_by_template) - set(observed_by_template))
    unexpected = sorted(set(observed_by_template) - set(expected_by_template))
    mismatches = _focused_minireplay_record_path_mismatches(
        expected_by_template,
        observed_by_template,
    )
    bad_records_type = records_type != "list"

    if bad_records_type:
        errors.append(f"focused_minireplay records has type {records_type}")
    if malformed_count:
        errors.append(f"focused_minireplay has {malformed_count} malformed records")
    if duplicate_template_ids:
        errors.append(
            f"focused_minireplay duplicate template ids: {duplicate_template_ids!r}"
        )
    if missing:
        errors.append(f"focused_minireplay missing record templates: {missing!r}")
    if unexpected:
        errors.append(
            f"focused_minireplay unexpected record templates: {unexpected!r}"
        )
    for mismatch in mismatches:
        errors.append(
            f"focused_minireplay record path mismatch on "
            f"{mismatch['template_id']} {mismatch['key']}: "
            f"{mismatch['observed']!r} != {mismatch['expected']!r}"
        )

    return {
        "records_type": records_type,
        "expected_record_count": len(expected),
        "observed_record_count": len(observed),
        "expected_records": expected,
        "observed_records": _sort_focused_minireplay_records(observed),
        "missing_template_ids": missing,
        "unexpected_template_ids": unexpected,
        "duplicate_template_ids": duplicate_template_ids,
        "mismatched_record_paths": mismatches,
        "malformed_record_count": malformed_count,
        "status": (
            "passed"
            if not (
                bad_records_type
                or malformed_count
                or duplicate_template_ids
                or missing
                or unexpected
                or mismatches
            )
            else "failed"
        ),
    }


def _expected_focused_minireplay_records() -> list[dict[str, str]]:
    return [
        {
            "template_id": template_id,
            "source_packet_path": _artifact_path_key(DEFAULT_PACKET_PATHS[template_id]),
            "minireplay_path": _artifact_path_key(DEFAULT_MINIREPLAY_PATHS[template_id]),
        }
        for template_id in EXPECTED_TEMPLATE_IDS
    ]


def _observed_focused_minireplay_records(
    records: Any,
) -> tuple[list[dict[str, str]], int]:
    if not isinstance(records, list):
        return [], 0
    observed: list[dict[str, str]] = []
    malformed_count = 0
    for record in records:
        if not isinstance(record, Mapping):
            malformed_count += 1
            continue
        template_id = record.get("template_id")
        source_packet_path = record.get("source_packet_path")
        minireplay_path = record.get("minireplay_path")
        if not all(
            isinstance(value, str)
            for value in (template_id, source_packet_path, minireplay_path)
        ):
            malformed_count += 1
            continue
        observed.append(
            {
                "template_id": template_id,
                "source_packet_path": source_packet_path,
                "minireplay_path": minireplay_path,
            }
        )
    return _sort_focused_minireplay_records(observed), malformed_count


def _focused_minireplay_record_path_mismatches(
    expected_by_template: Mapping[str, Mapping[str, str]],
    observed_by_template: Mapping[str, Mapping[str, str]],
) -> list[dict[str, str]]:
    mismatches: list[dict[str, str]] = []
    for template_id in sorted(set(expected_by_template) & set(observed_by_template)):
        expected = expected_by_template[template_id]
        observed = observed_by_template[template_id]
        for key in ("source_packet_path", "minireplay_path"):
            if observed.get(key) != expected.get(key):
                mismatches.append(
                    {
                        "template_id": template_id,
                        "key": key,
                        "expected": expected[key],
                        "observed": observed[key],
                    }
                )
    return mismatches


def _sort_focused_minireplay_records(
    records: list[dict[str, str]],
) -> list[dict[str, str]]:
    return sorted(records, key=lambda record: record["template_id"])


def _input_manifest() -> dict[str, Any]:
    entries: dict[str, dict[str, Any]] = {}

    def add(path: Path, role: str) -> None:
        resolved = path.resolve()
        key = _artifact_path_key(resolved)
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


def _manifest_role_contract(
    input_manifest: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    expected_roles = _expected_manifest_roles()
    artifacts = input_manifest.get("artifacts", [])
    artifact_records = artifacts if isinstance(artifacts, list) else []
    observed_roles, malformed_count = _observed_manifest_roles(artifacts)
    expected_paths = set(expected_roles)
    observed_paths = set(observed_roles)
    observed_path_list = [
        str(artifact.get("path"))
        for artifact in artifact_records
        if isinstance(artifact, Mapping) and isinstance(artifact.get("path"), str)
    ]
    duplicate_paths = sorted(
        {path for path in observed_path_list if observed_path_list.count(path) > 1}
    )
    missing = sorted(expected_paths - observed_paths)
    unexpected = sorted(observed_paths - expected_paths)
    mismatches = _manifest_role_mismatches(expected_roles, observed_roles)

    if malformed_count:
        errors.append(f"input_manifest has {malformed_count} malformed role entries")
    if duplicate_paths:
        errors.append(f"input_manifest duplicate role paths: {duplicate_paths!r}")
    if missing:
        errors.append(f"input_manifest role contract missing paths: {missing!r}")
    if unexpected:
        errors.append(f"input_manifest role contract unexpected paths: {unexpected!r}")
    for mismatch in mismatches:
        errors.append(
            f"input_manifest role mismatch on {mismatch['path']}: "
            f"{mismatch['observed']!r} != {mismatch['expected']!r}"
        )

    return {
        "status": (
            "passed"
            if not (malformed_count or duplicate_paths or missing or unexpected or mismatches)
            else "failed"
        ),
        "expected_path_count": len(expected_roles),
        "observed_path_count": len(observed_roles),
        "expected_roles": _manifest_role_records(expected_roles),
        "observed_roles": _manifest_role_records(observed_roles),
        "missing_manifest_role_paths": missing,
        "unexpected_manifest_role_paths": unexpected,
        "duplicate_manifest_role_paths": duplicate_paths,
        "mismatched_manifest_roles": mismatches,
        "malformed_manifest_role_count": malformed_count,
    }


def _expected_manifest_roles() -> dict[str, list[str]]:
    roles: dict[str, list[str]] = {}

    def add(path: Path, role: str) -> None:
        key = _artifact_path_key(path)
        path_roles = roles.setdefault(key, [])
        if role not in path_roles:
            path_roles.append(role)

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
    return {path: sorted(path_roles) for path, path_roles in roles.items()}


def _observed_manifest_roles(artifacts: Any) -> tuple[dict[str, list[str]], int]:
    if not isinstance(artifacts, list):
        return {}, 1
    roles_by_path: dict[str, list[str]] = {}
    malformed_count = 0
    for artifact in artifacts:
        if not isinstance(artifact, Mapping):
            malformed_count += 1
            continue
        path = artifact.get("path")
        roles = artifact.get("roles")
        if not isinstance(path, str) or not isinstance(roles, list):
            malformed_count += 1
            continue
        if not all(isinstance(role, str) for role in roles):
            malformed_count += 1
            continue
        roles_by_path[path] = sorted(set(roles))
    return roles_by_path, malformed_count


def _manifest_role_mismatches(
    expected_roles: Mapping[str, list[str]],
    observed_roles: Mapping[str, list[str]],
) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []
    for path in sorted(set(expected_roles) & set(observed_roles)):
        expected = expected_roles[path]
        observed = observed_roles[path]
        if observed != expected:
            mismatches.append(
                {
                    "path": path,
                    "expected": expected,
                    "observed": observed,
                }
            )
    return mismatches


def _manifest_role_records(roles_by_path: Mapping[str, list[str]]) -> list[dict[str, Any]]:
    return [
        {"path": path, "roles": roles_by_path[path]}
        for path in sorted(roles_by_path)
    ]


def _manifest_digest_contract(
    input_manifest: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    expected_digests = _expected_manifest_digests()
    artifacts = input_manifest.get("artifacts", [])
    artifact_records = artifacts if isinstance(artifacts, list) else []
    observed_digests, malformed_count = _observed_manifest_digests(artifacts)
    expected_paths = set(expected_digests)
    observed_paths = set(observed_digests)
    observed_path_list = [
        str(artifact.get("path"))
        for artifact in artifact_records
        if isinstance(artifact, Mapping) and isinstance(artifact.get("path"), str)
    ]
    duplicate_paths = sorted(
        {path for path in observed_path_list if observed_path_list.count(path) > 1}
    )
    missing = sorted(expected_paths - observed_paths)
    unexpected = sorted(observed_paths - expected_paths)
    mismatches = _manifest_digest_mismatches(expected_digests, observed_digests)

    if malformed_count:
        errors.append(f"input_manifest has {malformed_count} malformed digest entries")
    if duplicate_paths:
        errors.append(f"input_manifest duplicate digest paths: {duplicate_paths!r}")
    if missing:
        errors.append(f"input_manifest digest contract missing paths: {missing!r}")
    if unexpected:
        errors.append(f"input_manifest digest contract unexpected paths: {unexpected!r}")
    for mismatch in mismatches:
        errors.append(
            f"input_manifest digest mismatch on {mismatch['path']}: "
            f"{mismatch['observed']!r} != {mismatch['expected']!r}"
        )

    return {
        "status": (
            "passed"
            if not (malformed_count or duplicate_paths or missing or unexpected or mismatches)
            else "failed"
        ),
        "expected_path_count": len(expected_digests),
        "observed_path_count": len(observed_digests),
        "expected_digests": _manifest_digest_records(expected_digests),
        "observed_digests": _manifest_digest_records(observed_digests),
        "missing_manifest_digest_paths": missing,
        "unexpected_manifest_digest_paths": unexpected,
        "duplicate_manifest_digest_paths": duplicate_paths,
        "mismatched_manifest_digests": mismatches,
        "malformed_manifest_digest_count": malformed_count,
    }


def _expected_manifest_digests() -> dict[str, dict[str, Any]]:
    digests: dict[str, dict[str, Any]] = {}
    for path in sorted(_expected_manifest_roles()):
        resolved = (ROOT / path).resolve()
        digests[path] = {
            "size_bytes": resolved.stat().st_size,
            "sha256": _sha256(resolved),
        }
    return digests


def _observed_manifest_digests(
    artifacts: Any,
) -> tuple[dict[str, dict[str, Any]], int]:
    if not isinstance(artifacts, list):
        return {}, 1
    digests_by_path: dict[str, dict[str, Any]] = {}
    malformed_count = 0
    for artifact in artifacts:
        if not isinstance(artifact, Mapping):
            malformed_count += 1
            continue
        path = artifact.get("path")
        size_bytes = artifact.get("size_bytes")
        digest = artifact.get("sha256")
        if (
            not isinstance(path, str)
            or not isinstance(size_bytes, int)
            or size_bytes <= 0
            or not _is_sha256_digest(digest)
        ):
            malformed_count += 1
            continue
        digests_by_path[path] = {
            "size_bytes": size_bytes,
            "sha256": digest.lower(),
        }
    return digests_by_path, malformed_count


def _manifest_digest_mismatches(
    expected_digests: Mapping[str, Mapping[str, Any]],
    observed_digests: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []
    for path in sorted(set(expected_digests) & set(observed_digests)):
        expected = dict(expected_digests[path])
        observed = dict(observed_digests[path])
        if observed != expected:
            mismatches.append(
                {
                    "path": path,
                    "expected": expected,
                    "observed": observed,
                }
            )
    return mismatches


def _manifest_digest_records(
    digests_by_path: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "path": path,
            "size_bytes": digests_by_path[path]["size_bytes"],
            "sha256": digests_by_path[path]["sha256"],
        }
        for path in sorted(digests_by_path)
    ]


def _is_sha256_digest(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value.lower())
    )


def _manifest_header_contract(
    input_manifest: Mapping[str, Any],
    errors: list[str],
    *,
    header_payloads: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    expected_headers = _expected_manifest_headers()
    artifacts = input_manifest.get("artifacts", [])
    artifact_records = artifacts if isinstance(artifacts, list) else []
    observed_headers, malformed_count = _observed_manifest_headers(
        artifact_records,
        set(expected_headers),
        header_payloads=header_payloads,
    )
    expected_paths = set(expected_headers)
    observed_path_list = [
        str(artifact.get("path"))
        for artifact in artifact_records
        if isinstance(artifact, Mapping) and isinstance(artifact.get("path"), str)
    ]
    observed_paths = set(observed_path_list)
    duplicate_paths = sorted(
        {path for path in observed_path_list if observed_path_list.count(path) > 1}
    )
    missing = sorted(expected_paths - set(observed_headers))
    unexpected = sorted(observed_paths - expected_paths)
    mismatches = _manifest_header_mismatches(expected_headers, observed_headers)

    if not isinstance(artifacts, list):
        malformed_count += 1
    if malformed_count:
        errors.append(f"input_manifest has {malformed_count} malformed header entries")
    if duplicate_paths:
        errors.append(f"input_manifest duplicate header paths: {duplicate_paths!r}")
    if missing:
        errors.append(f"input_manifest header contract missing paths: {missing!r}")
    if unexpected:
        errors.append(f"input_manifest header contract unexpected paths: {unexpected!r}")
    for mismatch in mismatches:
        errors.append(
            f"input_manifest header mismatch on {mismatch['path']}: "
            f"{mismatch['observed']!r} != {mismatch['expected']!r}"
        )

    return {
        "status": (
            "passed"
            if not (malformed_count or duplicate_paths or missing or unexpected or mismatches)
            else "failed"
        ),
        "expected_path_count": len(expected_headers),
        "observed_path_count": len(observed_headers),
        "expected_headers": _manifest_header_records(expected_headers),
        "observed_headers": _manifest_header_records(observed_headers),
        "missing_manifest_header_paths": missing,
        "unexpected_manifest_header_paths": unexpected,
        "duplicate_manifest_header_paths": duplicate_paths,
        "mismatched_manifest_headers": mismatches,
        "malformed_manifest_header_count": malformed_count,
    }


def _expected_manifest_headers() -> dict[str, dict[str, Any]]:
    headers: dict[str, dict[str, Any]] = {}

    def add(
        path: Path,
        *,
        schema: str | None = None,
        status: str | None = None,
        trust: str | None = "REVIEW_PENDING_DIAGNOSTIC",
        validation_status: str | None = None,
    ) -> None:
        headers[_artifact_path_key(path)] = {
            "schema": schema,
            "status": status,
            "trust": trust,
            "validation_status": validation_status,
        }

    add(
        DEFAULT_TEMPLATE_CATALOG,
        schema="erdos97.n9_vertex_circle_template_lemma_catalog.v1",
        status="REVIEW_PENDING_DIAGNOSTIC_ONLY",
    )
    add(
        DEFAULT_FOCUSED_LOCAL_LEMMAS,
        schema="erdos97.n9_vertex_circle_local_lemmas.v1",
        status="REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE",
    )
    add(
        DEFAULT_SIMPLE_REPLAY,
        schema="erdos97.n9_vertex_circle_local_lemma_simple_replay.v1",
        status="REVIEW_PENDING_PACKET_AUDIT",
        validation_status="passed",
    )
    add(
        DEFAULT_EXHAUSTIVE,
        trust="MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
    )
    add(
        DEFAULT_CLASSIFICATION,
        schema="erdos97.n9_vertex_circle_frontier_motif_classification.v1",
        status="REVIEW_PENDING_DIAGNOSTIC_ONLY",
    )
    add(
        DEFAULT_RELATION_SKELETONS,
        schema="erdos97.relation_skeleton_catalog.v1",
        status="REVIEW_PENDING_DIAGNOSTIC_ONLY",
    )
    for kind, path in sorted(DEFAULT_TEMPLATE_PACKET_PATHS.items()):
        add(
            path,
            schema=f"erdos97.n9_vertex_circle_{kind}_template_packet.v1",
            status="REVIEW_PENDING_DIAGNOSTIC_ONLY",
        )
    for template_id, path in sorted(DEFAULT_PACKET_PATHS.items()):
        kind = _template_kind(template_id)
        add(
            path,
            schema=f"erdos97.n9_vertex_circle_{template_id.lower()}_{kind}_lemma_packet.v1",
            status="REVIEW_PENDING_DIAGNOSTIC_ONLY",
        )
    for template_id, path in sorted(DEFAULT_MINIREPLAY_PATHS.items()):
        kind = _template_kind(template_id)
        add(
            path,
            schema=f"erdos97.n9_{template_id.lower()}_{kind}_minireplay.v1",
            status=f"REVIEW_PENDING_{template_id}_{kind.upper()}_MINIREPLAY",
        )
    return headers


def _observed_manifest_headers(
    artifacts: list[Any],
    expected_paths: set[str],
    *,
    header_payloads: Mapping[str, Any] | None = None,
) -> tuple[dict[str, dict[str, Any]], int]:
    headers_by_path: dict[str, dict[str, Any]] = {}
    malformed_count = 0
    for artifact in artifacts:
        if not isinstance(artifact, Mapping):
            malformed_count += 1
            continue
        path = artifact.get("path")
        if not isinstance(path, str) or path not in expected_paths:
            continue
        try:
            payload = (
                header_payloads[path]
                if header_payloads is not None and path in header_payloads
                else load_artifact(ROOT / path)
            )
        except (OSError, json.JSONDecodeError):
            malformed_count += 1
            continue
        if not isinstance(payload, Mapping):
            malformed_count += 1
            continue
        headers_by_path[path] = _manifest_header_from_payload(payload)
    return headers_by_path, malformed_count


def _manifest_header_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": _optional_string(payload.get("schema")),
        "status": _optional_string(payload.get("status")),
        "trust": _optional_string(payload.get("trust")),
        "validation_status": _optional_string(payload.get("validation_status")),
    }


def _optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _template_kind(template_id: str) -> str:
    index = int(template_id[1:])
    return "self_edge" if index <= 9 else "strict_cycle"


def _manifest_header_mismatches(
    expected_headers: Mapping[str, Mapping[str, Any]],
    observed_headers: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []
    for path in sorted(set(expected_headers) & set(observed_headers)):
        expected = dict(expected_headers[path])
        observed = dict(observed_headers[path])
        if observed != expected:
            mismatches.append(
                {
                    "path": path,
                    "expected": expected,
                    "observed": observed,
                }
            )
    return mismatches


def _manifest_header_records(
    headers_by_path: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "path": path,
            "schema": headers_by_path[path]["schema"],
            "status": headers_by_path[path]["status"],
            "trust": headers_by_path[path]["trust"],
            "validation_status": headers_by_path[path]["validation_status"],
        }
        for path in sorted(headers_by_path)
    ]


def _manifest_consistency(
    layers: Mapping[str, Mapping[str, Any]],
    input_manifest: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    artifacts = input_manifest.get("artifacts", [])
    artifact_records = artifacts if isinstance(artifacts, list) else []
    manifest_paths = {
        str(artifact.get("path"))
        for artifact in artifact_records
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
        "layer source artifacts: "
        f"{_summary_status(payload['audit_path']['layer_source_artifact_contracts'])}",
        "claim-scope guards: "
        f"{_summary_status(payload['audit_path']['claim_scope_guards'])}",
        "layer output contracts: "
        f"{_summary_status(payload['audit_path']['layer_output_contracts'])}",
        "layer input contracts: "
        f"{_summary_status(payload['audit_path']['layer_input_contracts'])}",
        "focused minireplay record paths: "
        f"{payload['audit_path']['focused_minireplay_record_path_contract']['status']}",
        f"handoffs: {payload['audit_path']['handoff_count']}",
        f"input artifacts: {payload['input_manifest']['artifact_count']}",
        f"manifest roles: {payload['manifest_role_contract']['status']}",
        f"manifest digests: {payload['manifest_digest_contract']['status']}",
        f"manifest headers: {payload['manifest_header_contract']['status']}",
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
