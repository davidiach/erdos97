"""Hard strict-endpoint packet for the bootstrap/T12 target.

This module isolates the strict-edge endpoint requirements that remain hard in
the T12 bridge-target map. It is proof-mining bookkeeping only; it does not
prove that any missing row or endpoint is forced.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from erdos97.bootstrap_t12_activation_requirements import (
    KIND_STRICT,
    build_t12_activation_requirements_payload,
)
from erdos97.bootstrap_t12_bridge_target_map import (
    RELATION_HARD_STRICT,
    build_t12_bridge_target_map_payload,
)


SCHEMA = "erdos97.bootstrap_t12_hard_strict_endpoints.v1"
STATUS = "BOOTSTRAP_T12_HARD_STRICT_ENDPOINTS_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Hard strict-endpoint diagnostic for the two tight n=9 bootstrap/T12 "
    "records; isolates the strict-edge endpoint-set requirements that remain "
    "unmet after bootstrap-core, support, and deletion-closure checks. This "
    "does not prove that the missing rows or endpoints are forced, does not "
    "prove n=9, does not prove the bridge, and does not claim a "
    "counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_hard_strict_endpoints.json"
)

GAP_CLOSURE_MISSING_OUTSIDE = "CLOSURE_EXPOSED_MISSING_OUTSIDE_ENDPOINT"
GAP_SPLIT_SINGLETON = "SINGLETON_SUPPORTS_SPLIT_STRICT_ENDPOINTS"


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _record_key(record: Mapping[str, Any]) -> tuple[int, int]:
    return int(record["source_record_id"]), int(record["row_center"])


def _index_records(records: Iterable[Mapping[str, Any]]) -> dict[tuple[int, int], Mapping[str, Any]]:
    return {_record_key(record): record for record in records}


def _available_required_witnesses(
    requirement: Mapping[str, Any],
    evaluation: Mapping[str, Any],
) -> list[int]:
    required = set(_int_list(requirement["required_witnesses"]))
    available = set(_int_list(evaluation["available_witnesses"]))
    return sorted(required & available)


def _closure_eval_record(
    requirement: Mapping[str, Any],
    evaluation: Mapping[str, Any],
) -> dict[str, object]:
    return {
        "core_vertex": int(evaluation["core_vertex"]),
        "row_exposed_in_closure": bool(evaluation["row_exposed_in_closure"]),
        "activation_ready_in_closure": bool(evaluation["activation_ready_in_closure"]),
        "available_required_witnesses": _available_required_witnesses(
            requirement, evaluation
        ),
        "missing_required_witnesses": _int_list(
            evaluation["missing_required_witnesses"]
        ),
        "status": str(evaluation["status"]),
    }


def _support_eval_record(
    requirement: Mapping[str, Any],
    evaluation: Mapping[str, Any],
) -> dict[str, object]:
    return {
        "support": _int_list(evaluation["support"]),
        "available_required_witnesses": _available_required_witnesses(
            requirement, evaluation
        ),
        "missing_required_witnesses": _int_list(
            evaluation["missing_required_witnesses"]
        ),
        "status": str(evaluation["status"]),
        "ledger_private_pair_hit": bool(evaluation["ledger_private_pair_hit"]),
        "private_halo_core_vertices": _int_list(
            evaluation["private_halo_core_vertices"]
        ),
    }


def _gap_type(bridge_record: Mapping[str, Any]) -> str:
    row_target_status = str(bridge_record["row_target_status"])
    if row_target_status == "CLOSURE_EXPOSED_HARD_STRICT_ENDPOINT":
        return GAP_CLOSURE_MISSING_OUTSIDE
    if row_target_status == "MIXED_SINGLETON_CONNECTOR_AND_HARD_STRICT":
        return GAP_SPLIT_SINGLETON
    raise AssertionError(f"unexpected hard strict target status {row_target_status!r}")


def _other_requirements(bridge_record: Mapping[str, Any]) -> list[dict[str, object]]:
    out = []
    for requirement in bridge_record["requirements"]:
        if requirement["kind"] == KIND_STRICT:
            continue
        out.append(
            {
                "requirement_id": str(requirement["requirement_id"]),
                "kind": str(requirement["kind"]),
                "required_witnesses": _int_list(requirement["required_witnesses"]),
                "relation_state": str(requirement["relation_state"]),
                "missing_from_bootstrap_core": _int_list(
                    requirement["missing_from_bootstrap_core"]
                ),
            }
        )
    return out


def _hard_strict_record(
    *,
    activation_record: Mapping[str, Any],
    strict_requirement: Mapping[str, Any],
    bridge_record: Mapping[str, Any],
) -> dict[str, object]:
    required = set(_int_list(strict_requirement["required_witnesses"]))
    witnesses = set(_int_list(activation_record["witnesses"]))
    closure_evaluations = [
        _closure_eval_record(strict_requirement, evaluation)
        for evaluation in strict_requirement["closure_evaluations"]
    ]
    support_evaluations = [
        _support_eval_record(strict_requirement, evaluation)
        for evaluation in strict_requirement["support_evaluations"]
    ]
    exposed_closure_evaluations = [
        evaluation
        for evaluation in closure_evaluations
        if bool(evaluation["row_exposed_in_closure"])
    ]
    partial_supports = [
        evaluation
        for evaluation in support_evaluations
        if evaluation["status"] == "PARTIAL"
    ]
    missing_labels = _int_list(strict_requirement["missing_from_bootstrap_core"])
    gap_type = _gap_type(bridge_record)

    return {
        "source_record_id": int(activation_record["source_record_id"]),
        "classification_assignment_id": str(
            activation_record["classification_assignment_id"]
        ),
        "row_center": int(activation_record["row_center"]),
        "roles": [str(role) for role in activation_record["roles"]],
        "pressure_class": str(activation_record["pressure_class"]),
        "row_target_status": str(bridge_record["row_target_status"]),
        "hard_strict_gap_type": gap_type,
        "strict_requirement_id": str(strict_requirement["requirement_id"]),
        "step_index": int(strict_requirement["step_index"]),
        "outer_pair": _int_list(strict_requirement["outer_pair"]),
        "inner_pair": _int_list(strict_requirement["inner_pair"]),
        "required_witnesses": sorted(required),
        "requirement_size": int(strict_requirement["requirement_size"]),
        "witnesses": sorted(witnesses),
        "bootstrap_core_witnesses": _int_list(
            activation_record["bootstrap_core_witnesses"]
        ),
        "outside_witnesses": _int_list(activation_record["outside_witnesses"]),
        "non_required_row_witnesses": sorted(witnesses - required),
        "missing_from_bootstrap_core": missing_labels,
        "missing_endpoint_count": len(missing_labels),
        "closure_sufficient_count": int(strict_requirement["closure_sufficient_count"]),
        "support_sufficient_count": int(strict_requirement["support_sufficient_count"]),
        "closure_evaluations": closure_evaluations,
        "exposed_closure_evaluations": exposed_closure_evaluations,
        "support_evaluations": support_evaluations,
        "partial_support_count": len(partial_supports),
        "partial_supports": partial_supports,
        "other_row_requirements": _other_requirements(bridge_record),
        "bridge_lemma_target": str(bridge_record["bridge_lemma_target"]),
    }


def build_t12_hard_strict_endpoints_payload() -> dict[str, object]:
    """Return the deterministic hard strict-endpoint packet."""

    activation = build_t12_activation_requirements_payload()
    bridge_map = build_t12_bridge_target_map_payload()
    bridge_by_key = _index_records(bridge_map["records"])

    records = []
    for activation_record in activation["records"]:
        key = _record_key(activation_record)
        bridge_record = bridge_by_key[key]
        for requirement in activation_record["requirements"]:
            if requirement["kind"] != KIND_STRICT:
                continue
            if RELATION_HARD_STRICT not in bridge_record["relation_state_counts"]:
                continue
            records.append(
                _hard_strict_record(
                    activation_record=activation_record,
                    strict_requirement=requirement,
                    bridge_record=bridge_record,
                )
            )
    records.sort(key=lambda record: (int(record["source_record_id"]), int(record["row_center"])))

    rows_by_source: defaultdict[int, list[int]] = defaultdict(list)
    gap_type_counts: Counter[str] = Counter()
    pressure_counts: Counter[str] = Counter()
    target_status_counts: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    missing_endpoint_counts: Counter[int] = Counter()
    other_relation_counts: Counter[str] = Counter()
    for record in records:
        rows_by_source[int(record["source_record_id"])].append(int(record["row_center"]))
        gap_type_counts[str(record["hard_strict_gap_type"])] += 1
        pressure_counts[str(record["pressure_class"])] += 1
        target_status_counts[str(record["row_target_status"])] += 1
        role_counts.update(str(role) for role in record["roles"])
        missing_endpoint_counts.update(_int_list(record["missing_from_bootstrap_core"]))
        for requirement in record["other_row_requirements"]:
            other_relation_counts[str(requirement["relation_state"])] += 1

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This packet isolates fixed selected-row strict-edge endpoint gaps; it does not prove endpoints or rows are forced.",
            "Partial closure or singleton support is bookkeeping, not a Euclidean rich-class certificate.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "source_record_ids": sorted(rows_by_source),
            "hard_strict_row_count": len(records),
            "row_centers_by_source_id": {
                str(source_id): centers for source_id, centers in sorted(rows_by_source.items())
            },
            "hard_strict_requirement_ids": [
                str(record["strict_requirement_id"]) for record in records
            ],
            "hard_strict_gap_type_counts": _json_counter(gap_type_counts),
            "pressure_class_counts": _json_counter(pressure_counts),
            "row_target_status_counts": _json_counter(target_status_counts),
            "role_counts": _json_counter(role_counts),
            "missing_endpoint_label_counts": _json_counter(missing_endpoint_counts),
            "closure_sufficient_requirement_count": sum(
                int(record["closure_sufficient_count"]) for record in records
            ),
            "support_sufficient_requirement_count": sum(
                int(record["support_sufficient_count"]) for record in records
            ),
            "partial_support_count": sum(
                int(record["partial_support_count"]) for record in records
            ),
            "other_relation_state_counts": _json_counter(other_relation_counts),
            "exposed_closure_partial_rows": [
                f"{record['source_record_id']}:{record['row_center']}"
                for record in records
                if record["hard_strict_gap_type"] == GAP_CLOSURE_MISSING_OUTSIDE
            ],
            "split_singleton_partial_rows": [
                f"{record['source_record_id']}:{record['row_center']}"
                for record in records
                if record["hard_strict_gap_type"] == GAP_SPLIT_SINGLETON
            ],
            "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
            "next_bridge_question": (
                "Can strict-edge endpoint sets be forced as complete rich-class "
                "subsets, rather than one endpoint at a time, in the T12/F16 "
                "bootstrap target?"
            ),
        },
        "records": records,
        "source_artifacts": [
            {
                "path": "data/certificates/bootstrap_t12_activation_requirements.json",
                "role": "source strict-edge endpoint requirements and evaluations",
                "schema": activation.get("schema"),
                "status": activation.get("status"),
                "trust": activation.get("trust"),
            },
            {
                "path": "data/certificates/bootstrap_t12_bridge_target_map.json",
                "role": "source hard strict row targets and bridge obligations",
                "schema": bridge_map.get("schema"),
                "status": bridge_map.get("status"),
                "trust": bridge_map.get("trust"),
            },
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_hard_strict_endpoints.py",
            "command": (
                "python scripts/check_bootstrap_t12_hard_strict_endpoints.py "
                "--write --assert-expected"
            ),
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts for the hard strict-endpoint packet."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected bootstrap/T12 hard-strict schema")
    if payload.get("status") != STATUS:
        raise AssertionError("unexpected bootstrap/T12 hard-strict status")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "source_record_ids": [151],
        "hard_strict_row_count": 2,
        "row_centers_by_source_id": {"151": [7, 8]},
        "hard_strict_requirement_ids": ["151:7:strict:0", "151:8:strict:1"],
        "hard_strict_gap_type_counts": {
            GAP_CLOSURE_MISSING_OUTSIDE: 1,
            GAP_SPLIT_SINGLETON: 1,
        },
        "pressure_class_counts": {
            "ALREADY_PRESENT_IN_A_DELETION_CLOSURE": 1,
            "NEEDS_ONE_OUTSIDE_LABEL_AND_PRIVATE_CENTER": 1,
        },
        "row_target_status_counts": {
            "CLOSURE_EXPOSED_HARD_STRICT_ENDPOINT": 1,
            "MIXED_SINGLETON_CONNECTOR_AND_HARD_STRICT": 1,
        },
        "role_counts": {"equality_connector_row": 1, "strict_edge_row": 2},
        "missing_endpoint_label_counts": {"5": 1, "6": 1, "7": 1},
        "closure_sufficient_requirement_count": 0,
        "support_sufficient_requirement_count": 0,
        "partial_support_count": 2,
        "other_relation_state_counts": {"SUPPORT_SUFFICIENT": 1},
        "exposed_closure_partial_rows": ["151:7"],
        "split_singleton_partial_rows": ["151:8"],
        "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary {key} is {summary.get(key)!r}, expected {expected!r}")

    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("records must be a list")
    by_key = {_record_key(record): record for record in records}
    if set(by_key) != {(151, 7), (151, 8)}:
        raise AssertionError("unexpected hard strict record keys")

    row_7 = by_key[(151, 7)]
    if row_7["required_witnesses"] != [0, 1, 6]:
        raise AssertionError("151:7 required witnesses changed")
    if row_7["missing_from_bootstrap_core"] != [6]:
        raise AssertionError("151:7 missing endpoint changed")
    if row_7["exposed_closure_evaluations"][0]["missing_required_witnesses"] != [6]:
        raise AssertionError("151:7 exposed closure no longer misses endpoint 6")

    row_8 = by_key[(151, 8)]
    if row_8["required_witnesses"] != [1, 5, 7]:
        raise AssertionError("151:8 required witnesses changed")
    support_missing = {
        tuple(item["support"]): item["missing_required_witnesses"]
        for item in row_8["support_evaluations"]
    }
    if support_missing != {(5,): [7], (7,): [5]}:
        raise AssertionError("151:8 singleton support split changed")
    if row_8["other_row_requirements"][0]["relation_state"] != "SUPPORT_SUFFICIENT":
        raise AssertionError("151:8 connector support state changed")
