"""Relation-sufficient row packet for the bootstrap/T12 target.

This module isolates the T12 bridge-target rows whose role-sensitive relation
requirements are already supplied by bootstrap-core or support diagnostics,
while the actual row/rich-class forcing step remains open. It is proof-mining
bookkeeping only; it does not prove that any missing row is forced.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from erdos97.bootstrap_t12_bridge_target_map import (
    RELATION_BOOTSTRAP_CORE,
    RELATION_CLOSURE,
    RELATION_HARD_STRICT,
    RELATION_OPEN,
    RELATION_OPEN_CONNECTOR,
    RELATION_SUPPORT,
    build_t12_bridge_target_map_payload,
)


SCHEMA = "erdos97.bootstrap_t12_relation_sufficient_rows.v1"
STATUS = "BOOTSTRAP_T12_RELATION_SUFFICIENT_ROWS_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Relation-sufficient row diagnostic for the two tight n=9 bootstrap/T12 "
    "records; isolates rows whose connector requirements are already supplied "
    "by bootstrap-core or support diagnostics, while row/rich-class forcing "
    "remains an open bridge target. This does not prove that the missing rows "
    "are forced, does not prove n=9, does not prove the bridge, and does not "
    "claim a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_relation_sufficient_rows.json"
)

RELATION_SUFFICIENT_STATES = {
    RELATION_BOOTSTRAP_CORE,
    RELATION_CLOSURE,
    RELATION_SUPPORT,
}
RELATION_BLOCKER_STATES = {
    RELATION_HARD_STRICT,
    RELATION_OPEN,
    RELATION_OPEN_CONNECTOR,
}

GAP_FULL_ROW_CLOSURE = "FULL_ROW_CLOSURE_EXPOSURE_NEEDS_RICH_CLASS_FORCING"
GAP_SINGLETON_ACTIVATION = "CORE_CONNECTOR_VISIBLE_NEEDS_PRIVATE_ROW_ACTIVATION"
GAP_OUTSIDE_PAIR_SUPPORT = "OUTSIDE_PAIR_SUPPORT_NEEDS_CONNECTOR_ROW_FORCING"

ROW_FORCING_GAP_TYPES = {
    "CLOSURE_FULL_ROW_CONNECTOR": GAP_FULL_ROW_CLOSURE,
    "CORE_CONNECTOR_WITH_SINGLETON_ROW_ACTIVATION": GAP_SINGLETON_ACTIVATION,
    "OUTSIDE_PAIR_CONNECTOR_PARTIAL_LEDGER": GAP_OUTSIDE_PAIR_SUPPORT,
}


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


def _row_key_string(record: Mapping[str, Any]) -> str:
    return f"{record['source_record_id']}:{record['row_center']}"


def _relation_sufficient_requirements(
    record: Mapping[str, Any],
) -> list[dict[str, object]]:
    requirements = []
    for requirement in record["requirements"]:
        relation_state = str(requirement["relation_state"])
        if relation_state not in RELATION_SUFFICIENT_STATES:
            continue
        requirements.append(
            {
                "requirement_id": str(requirement["requirement_id"]),
                "kind": str(requirement["kind"]),
                "required_witnesses": _int_list(
                    requirement["required_witnesses"]
                ),
                "relation_state": relation_state,
                "bootstrap_core_status": str(requirement["bootstrap_core_status"]),
                "support_sufficient_count": int(
                    requirement["support_sufficient_count"]
                ),
                "closure_sufficient_count": int(
                    requirement["closure_sufficient_count"]
                ),
                "missing_from_bootstrap_core": _int_list(
                    requirement["missing_from_bootstrap_core"]
                ),
            }
        )
    return requirements


def _is_relation_sufficient_row(record: Mapping[str, Any]) -> bool:
    relation_states = set(str(state) for state in record["relation_state_counts"])
    return bool(relation_states) and relation_states <= RELATION_SUFFICIENT_STATES


def _has_blocker_state(record: Mapping[str, Any]) -> bool:
    relation_states = set(str(state) for state in record["relation_state_counts"])
    return bool(relation_states & RELATION_BLOCKER_STATES)


def _gap_type(record: Mapping[str, Any]) -> str:
    row_target_status = str(record["row_target_status"])
    try:
        return ROW_FORCING_GAP_TYPES[row_target_status]
    except KeyError as exc:
        raise AssertionError(
            f"unexpected relation-sufficient target status {row_target_status!r}"
        ) from exc


def _relation_sufficient_record(record: Mapping[str, Any]) -> dict[str, object]:
    relation_requirements = _relation_sufficient_requirements(record)
    return {
        "source_record_id": int(record["source_record_id"]),
        "classification_assignment_id": str(record["classification_assignment_id"]),
        "row_center": int(record["row_center"]),
        "roles": [str(role) for role in record["roles"]],
        "witnesses": _int_list(record["witnesses"]),
        "bootstrap_core_witnesses": _int_list(record["bootstrap_core_witnesses"]),
        "outside_witnesses": _int_list(record["outside_witnesses"]),
        "activation_deficit_from_bootstrap_core": int(
            record["activation_deficit_from_bootstrap_core"]
        ),
        "row_center_private_in_all_deletion_closures": bool(
            record["row_center_private_in_all_deletion_closures"]
        ),
        "pressure_class": str(record["pressure_class"]),
        "support_packet_summary": record["support_packet_summary"],
        "requirement_count": int(record["requirement_count"]),
        "relation_sufficient_requirement_count": len(relation_requirements),
        "relation_sufficient_requirements": relation_requirements,
        "relation_state_counts": {
            str(state): int(count)
            for state, count in record["relation_state_counts"].items()
        },
        "row_target_status": str(record["row_target_status"]),
        "row_forcing_gap_type": _gap_type(record),
        "bridge_lemma_target": str(record["bridge_lemma_target"]),
    }


def build_t12_relation_sufficient_rows_payload() -> dict[str, object]:
    """Return the deterministic relation-sufficient row packet."""

    bridge_map = build_t12_bridge_target_map_payload()
    all_records = bridge_map["records"]
    records = [
        _relation_sufficient_record(record)
        for record in all_records
        if _is_relation_sufficient_row(record)
    ]
    records.sort(key=lambda record: (int(record["source_record_id"]), int(record["row_center"])))

    excluded_hard_or_open = [
        _row_key_string(record) for record in all_records if _has_blocker_state(record)
    ]
    rows_by_source: defaultdict[int, list[int]] = defaultdict(list)
    gap_type_counts: Counter[str] = Counter()
    pressure_counts: Counter[str] = Counter()
    target_status_counts: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    support_packet_counts: Counter[str] = Counter()
    relation_state_counts: Counter[str] = Counter()
    requirement_kind_counts: Counter[str] = Counter()
    for record in records:
        rows_by_source[int(record["source_record_id"])].append(int(record["row_center"]))
        gap_type_counts[str(record["row_forcing_gap_type"])] += 1
        pressure_counts[str(record["pressure_class"])] += 1
        target_status_counts[str(record["row_target_status"])] += 1
        role_counts.update(str(role) for role in record["roles"])
        support_packet_counts[str(record["support_packet_summary"]["support_packet"])] += 1
        for requirement in record["relation_sufficient_requirements"]:
            relation_state_counts[str(requirement["relation_state"])] += 1
            requirement_kind_counts[str(requirement["kind"])] += 1

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This packet isolates relation-sufficient fixed selected rows; it does not prove row or rich-class forcing.",
            "Bootstrap-core or support sufficiency for a role requirement is not a Euclidean certificate that the whole row is forced.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "source_record_ids": sorted(rows_by_source),
            "relation_sufficient_row_count": len(records),
            "row_centers_by_source_id": {
                str(source_id): centers for source_id, centers in sorted(rows_by_source.items())
            },
            "relation_sufficient_requirement_ids": [
                str(requirement["requirement_id"])
                for record in records
                for requirement in record["relation_sufficient_requirements"]
            ],
            "relation_state_counts": _json_counter(relation_state_counts),
            "requirement_kind_counts": _json_counter(requirement_kind_counts),
            "row_forcing_gap_type_counts": _json_counter(gap_type_counts),
            "pressure_class_counts": _json_counter(pressure_counts),
            "row_target_status_counts": _json_counter(target_status_counts),
            "role_counts": _json_counter(role_counts),
            "support_packet_counts": _json_counter(support_packet_counts),
            "excluded_hard_or_open_rows": sorted(excluded_hard_or_open),
            "row_forcing_target_status": "OPEN_TARGET_NOT_PROVED",
            "next_bridge_question": (
                "Can relation-sufficient connector evidence be upgraded to "
                "genuine row/rich-class forcing for these three T12 targets?"
            ),
        },
        "records": records,
        "source_artifacts": [
            {
                "path": "data/certificates/bootstrap_t12_bridge_target_map.json",
                "role": "source relation states, support packets, and bridge targets",
                "schema": bridge_map.get("schema"),
                "status": bridge_map.get("status"),
                "trust": bridge_map.get("trust"),
            }
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_relation_sufficient_rows.py",
            "command": (
                "python scripts/check_bootstrap_t12_relation_sufficient_rows.py "
                "--write --assert-expected"
            ),
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts for the relation-sufficient row packet."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected bootstrap/T12 relation-sufficient schema")
    if payload.get("status") != STATUS:
        raise AssertionError("unexpected bootstrap/T12 relation-sufficient status")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "source_record_ids": [81, 151],
        "relation_sufficient_row_count": 3,
        "row_centers_by_source_id": {"81": [3, 8], "151": [6]},
        "relation_sufficient_requirement_ids": [
            "81:3:connector:2:0",
            "81:8:connector:0:0",
            "151:6:connector:2:0",
        ],
        "relation_state_counts": {
            RELATION_BOOTSTRAP_CORE: 2,
            RELATION_SUPPORT: 1,
        },
        "requirement_kind_counts": {"equality_connector_pair": 3},
        "row_forcing_gap_type_counts": {
            GAP_FULL_ROW_CLOSURE: 1,
            GAP_OUTSIDE_PAIR_SUPPORT: 1,
            GAP_SINGLETON_ACTIVATION: 1,
        },
        "pressure_class_counts": {
            "ALREADY_PRESENT_IN_A_DELETION_CLOSURE": 1,
            "NEEDS_ONE_OUTSIDE_LABEL_AND_PRIVATE_CENTER": 1,
            "NEEDS_OUTSIDE_PAIR_AND_PRIVATE_CENTER": 1,
        },
        "row_target_status_counts": {
            "CLOSURE_FULL_ROW_CONNECTOR": 1,
            "CORE_CONNECTOR_WITH_SINGLETON_ROW_ACTIVATION": 1,
            "OUTSIDE_PAIR_CONNECTOR_PARTIAL_LEDGER": 1,
        },
        "role_counts": {"equality_connector_row": 3},
        "support_packet_counts": {
            "bootstrap_t12_closure_exposed": 1,
            "bootstrap_t12_one_outside": 1,
            "bootstrap_t12_outside_pair": 1,
        },
        "excluded_hard_or_open_rows": ["151:5", "151:7", "151:8"],
        "row_forcing_target_status": "OPEN_TARGET_NOT_PROVED",
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary {key} is {summary.get(key)!r}, expected {expected!r}")

    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("records must be a list")
    by_key = {_record_key(record): record for record in records}
    if set(by_key) != {(81, 3), (81, 8), (151, 6)}:
        raise AssertionError("unexpected relation-sufficient record keys")

    row_81_3 = by_key[(81, 3)]
    if row_81_3["row_forcing_gap_type"] != GAP_FULL_ROW_CLOSURE:
        raise AssertionError("81:3 gap type changed")
    if not row_81_3["support_packet_summary"]["full_row_contained_in_exposure_closure"]:
        raise AssertionError("81:3 must remain full-row closure exposed")
    if row_81_3["relation_sufficient_requirements"][0]["relation_state"] != RELATION_BOOTSTRAP_CORE:
        raise AssertionError("81:3 relation state changed")

    row_81_8 = by_key[(81, 8)]
    if row_81_8["row_forcing_gap_type"] != GAP_SINGLETON_ACTIVATION:
        raise AssertionError("81:8 gap type changed")
    if row_81_8["support_packet_summary"]["support_labels"] != [5, 6]:
        raise AssertionError("81:8 singleton support labels changed")
    if not row_81_8["row_center_private_in_all_deletion_closures"]:
        raise AssertionError("81:8 private row-center flag changed")

    row_151_6 = by_key[(151, 6)]
    if row_151_6["row_forcing_gap_type"] != GAP_OUTSIDE_PAIR_SUPPORT:
        raise AssertionError("151:6 gap type changed")
    requirement = row_151_6["relation_sufficient_requirements"][0]
    if requirement["relation_state"] != RELATION_SUPPORT:
        raise AssertionError("151:6 relation state changed")
    if requirement["required_witnesses"] != [0, 8]:
        raise AssertionError("151:6 connector witnesses changed")
    support_summary = row_151_6["support_packet_summary"]
    if support_summary["ledger_hit_support_pairs"] != [[3, 8], [5, 8]]:
        raise AssertionError("151:6 ledger hit support pairs changed")
    if support_summary["ledger_miss_support_pairs"] != [[3, 5]]:
        raise AssertionError("151:6 ledger miss support pairs changed")
