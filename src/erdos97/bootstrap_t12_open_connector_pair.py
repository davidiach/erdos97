"""Open connector-pair packet for the bootstrap/T12 target.

This module isolates the equality-connector pair requirement that remains open
in the T12 bridge-target map. It is proof-mining bookkeeping only; it does not
prove that any missing row or connector endpoint is forced.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from erdos97.bootstrap_t12_activation_requirements import (
    KIND_CONNECTOR,
    build_t12_activation_requirements_payload,
)
from erdos97.bootstrap_t12_bridge_target_map import (
    RELATION_OPEN_CONNECTOR,
    build_t12_bridge_target_map_payload,
)


SCHEMA = "erdos97.bootstrap_t12_open_connector_pair.v1"
STATUS = "BOOTSTRAP_T12_OPEN_CONNECTOR_PAIR_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Open connector-pair diagnostic for the two tight n=9 bootstrap/T12 "
    "records; isolates the equality-connector pair requirement that remains "
    "unmet after bootstrap-core, support, and deletion-closure checks. This "
    "does not prove that the missing row or connector endpoints are forced, "
    "does not prove n=9, does not prove the bridge, and does not claim a "
    "counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_open_connector_pair.json"
)

GAP_SINGLETON_SPLIT_PAIR = "SINGLETON_SUPPORTS_SPLIT_CONNECTOR_PAIR"


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
        "row_center_in_closure": bool(evaluation["row_center_in_closure"]),
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


def _connector_gap_type(bridge_record: Mapping[str, Any]) -> str:
    row_target_status = str(bridge_record["row_target_status"])
    if row_target_status == "SINGLETON_ROW_OPEN_CONNECTOR_PAIR":
        return GAP_SINGLETON_SPLIT_PAIR
    raise AssertionError(f"unexpected open connector target status {row_target_status!r}")


def _open_connector_record(
    *,
    activation_record: Mapping[str, Any],
    connector_requirement: Mapping[str, Any],
    bridge_record: Mapping[str, Any],
) -> dict[str, object]:
    required = set(_int_list(connector_requirement["required_witnesses"]))
    witnesses = set(_int_list(activation_record["witnesses"]))
    closure_evaluations = [
        _closure_eval_record(connector_requirement, evaluation)
        for evaluation in connector_requirement["closure_evaluations"]
    ]
    support_evaluations = [
        _support_eval_record(connector_requirement, evaluation)
        for evaluation in connector_requirement["support_evaluations"]
    ]
    partial_closures = [
        evaluation
        for evaluation in closure_evaluations
        if evaluation["status"] == "PARTIAL"
    ]
    partial_supports = [
        evaluation
        for evaluation in support_evaluations
        if evaluation["status"] == "PARTIAL"
    ]
    missing_labels = _int_list(connector_requirement["missing_from_bootstrap_core"])

    return {
        "source_record_id": int(activation_record["source_record_id"]),
        "classification_assignment_id": str(
            activation_record["classification_assignment_id"]
        ),
        "row_center": int(activation_record["row_center"]),
        "roles": [str(role) for role in activation_record["roles"]],
        "pressure_class": str(activation_record["pressure_class"]),
        "row_target_status": str(bridge_record["row_target_status"]),
        "open_connector_gap_type": _connector_gap_type(bridge_record),
        "connector_requirement_id": str(connector_requirement["requirement_id"]),
        "step_index": int(connector_requirement["step_index"]),
        "path_index": int(connector_requirement["path_index"]),
        "from_pair": _int_list(connector_requirement["from_pair"]),
        "to_pair": _int_list(connector_requirement["to_pair"]),
        "required_witnesses": sorted(required),
        "requirement_size": int(connector_requirement["requirement_size"]),
        "witnesses": sorted(witnesses),
        "bootstrap_core_witnesses": _int_list(
            activation_record["bootstrap_core_witnesses"]
        ),
        "outside_witnesses": _int_list(activation_record["outside_witnesses"]),
        "non_required_row_witnesses": sorted(witnesses - required),
        "missing_from_bootstrap_core": missing_labels,
        "missing_connector_endpoint_count": len(missing_labels),
        "closure_sufficient_count": int(
            connector_requirement["closure_sufficient_count"]
        ),
        "support_sufficient_count": int(
            connector_requirement["support_sufficient_count"]
        ),
        "closure_evaluations": closure_evaluations,
        "partial_closure_count": len(partial_closures),
        "partial_closures": partial_closures,
        "support_evaluations": support_evaluations,
        "partial_support_count": len(partial_supports),
        "partial_supports": partial_supports,
        "support_packet_summary": bridge_record["support_packet_summary"],
        "bridge_lemma_target": str(bridge_record["bridge_lemma_target"]),
    }


def build_t12_open_connector_pair_payload() -> dict[str, object]:
    """Return the deterministic open connector-pair packet."""

    activation = build_t12_activation_requirements_payload()
    bridge_map = build_t12_bridge_target_map_payload()
    bridge_by_key = _index_records(bridge_map["records"])

    records = []
    for activation_record in activation["records"]:
        key = _record_key(activation_record)
        bridge_record = bridge_by_key[key]
        for requirement in activation_record["requirements"]:
            if requirement["kind"] != KIND_CONNECTOR:
                continue
            if RELATION_OPEN_CONNECTOR not in bridge_record["relation_state_counts"]:
                continue
            records.append(
                _open_connector_record(
                    activation_record=activation_record,
                    connector_requirement=requirement,
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
    support_status_counts: Counter[str] = Counter()
    closure_status_counts: Counter[str] = Counter()
    for record in records:
        rows_by_source[int(record["source_record_id"])].append(int(record["row_center"]))
        gap_type_counts[str(record["open_connector_gap_type"])] += 1
        pressure_counts[str(record["pressure_class"])] += 1
        target_status_counts[str(record["row_target_status"])] += 1
        role_counts.update(str(role) for role in record["roles"])
        missing_endpoint_counts.update(_int_list(record["missing_from_bootstrap_core"]))
        support_status_counts.update(
            str(evaluation["status"]) for evaluation in record["support_evaluations"]
        )
        closure_status_counts.update(
            str(evaluation["status"]) for evaluation in record["closure_evaluations"]
        )

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This packet isolates a fixed selected-row equality-connector pair gap; it does not prove endpoints or rows are forced.",
            "Singleton or deletion-closure partial visibility is bookkeeping, not a Euclidean rich-class certificate.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "source_record_ids": sorted(rows_by_source),
            "open_connector_row_count": len(records),
            "row_centers_by_source_id": {
                str(source_id): centers for source_id, centers in sorted(rows_by_source.items())
            },
            "open_connector_requirement_ids": [
                str(record["connector_requirement_id"]) for record in records
            ],
            "open_connector_gap_type_counts": _json_counter(gap_type_counts),
            "pressure_class_counts": _json_counter(pressure_counts),
            "row_target_status_counts": _json_counter(target_status_counts),
            "role_counts": _json_counter(role_counts),
            "missing_connector_endpoint_label_counts": _json_counter(
                missing_endpoint_counts
            ),
            "closure_sufficient_requirement_count": sum(
                int(record["closure_sufficient_count"]) for record in records
            ),
            "support_sufficient_requirement_count": sum(
                int(record["support_sufficient_count"]) for record in records
            ),
            "partial_closure_count": sum(
                int(record["partial_closure_count"]) for record in records
            ),
            "partial_support_count": sum(
                int(record["partial_support_count"]) for record in records
            ),
            "support_evaluation_status_counts": _json_counter(support_status_counts),
            "closure_evaluation_status_counts": _json_counter(closure_status_counts),
            "split_singleton_partial_rows": [
                f"{record['source_record_id']}:{record['row_center']}"
                for record in records
                if record["open_connector_gap_type"] == GAP_SINGLETON_SPLIT_PAIR
            ],
            "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
            "next_bridge_question": (
                "Can a singleton-activated row be forced to carry both "
                "outside endpoints of an equality-connector pair, rather than "
                "only one endpoint at a time?"
            ),
        },
        "records": records,
        "source_artifacts": [
            {
                "path": "data/certificates/bootstrap_t12_activation_requirements.json",
                "role": "source equality-connector pair requirements and evaluations",
                "schema": activation.get("schema"),
                "status": activation.get("status"),
                "trust": activation.get("trust"),
            },
            {
                "path": "data/certificates/bootstrap_t12_bridge_target_map.json",
                "role": "source open connector row target and bridge obligation",
                "schema": bridge_map.get("schema"),
                "status": bridge_map.get("status"),
                "trust": bridge_map.get("trust"),
            },
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_open_connector_pair.py",
            "command": (
                "python scripts/check_bootstrap_t12_open_connector_pair.py "
                "--write --assert-expected"
            ),
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts for the open connector-pair packet."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected bootstrap/T12 open-connector schema")
    if payload.get("status") != STATUS:
        raise AssertionError("unexpected bootstrap/T12 open-connector status")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "source_record_ids": [151],
        "open_connector_row_count": 1,
        "row_centers_by_source_id": {"151": [5]},
        "open_connector_requirement_ids": ["151:5:connector:1:0"],
        "open_connector_gap_type_counts": {GAP_SINGLETON_SPLIT_PAIR: 1},
        "pressure_class_counts": {
            "NEEDS_ONE_OUTSIDE_LABEL_AND_PRIVATE_CENTER": 1,
        },
        "row_target_status_counts": {
            "SINGLETON_ROW_OPEN_CONNECTOR_PAIR": 1,
        },
        "role_counts": {"equality_connector_row": 1},
        "missing_connector_endpoint_label_counts": {"7": 1, "8": 1},
        "closure_sufficient_requirement_count": 0,
        "support_sufficient_requirement_count": 0,
        "partial_closure_count": 1,
        "partial_support_count": 2,
        "support_evaluation_status_counts": {"PARTIAL": 2},
        "closure_evaluation_status_counts": {"DISJOINT": 3, "PARTIAL": 1},
        "split_singleton_partial_rows": ["151:5"],
        "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary {key} is {summary.get(key)!r}, expected {expected!r}")

    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("records must be a list")
    by_key = {_record_key(record): record for record in records}
    if set(by_key) != {(151, 5)}:
        raise AssertionError("unexpected open connector record keys")

    row_5 = by_key[(151, 5)]
    if row_5["required_witnesses"] != [7, 8]:
        raise AssertionError("151:5 required connector pair changed")
    if row_5["missing_from_bootstrap_core"] != [7, 8]:
        raise AssertionError("151:5 missing connector endpoints changed")
    if row_5["bootstrap_core_witnesses"] != [2, 4]:
        raise AssertionError("151:5 bootstrap core witnesses changed")
    if row_5["non_required_row_witnesses"] != [2, 4]:
        raise AssertionError("151:5 non-required row witnesses changed")
    support_missing = {
        tuple(item["support"]): item["missing_required_witnesses"]
        for item in row_5["support_evaluations"]
    }
    if support_missing != {(7,): [8], (8,): [7]}:
        raise AssertionError("151:5 singleton support split changed")
    partial_closures = row_5["partial_closures"]
    if len(partial_closures) != 1:
        raise AssertionError("151:5 should have exactly one partial closure")
    if partial_closures[0]["core_vertex"] != 2:
        raise AssertionError("151:5 partial closure core vertex changed")
    if partial_closures[0]["missing_required_witnesses"] != [8]:
        raise AssertionError("151:5 partial closure missing endpoint changed")
    if partial_closures[0]["row_center_in_closure"]:
        raise AssertionError("151:5 partial closure should not contain row center")
