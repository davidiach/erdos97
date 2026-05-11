"""Focused 81:3 closure-target packet for the bootstrap/T12 bridge.

This module isolates the cleanest current row-forcing target: source ``81``,
row center ``3``.  The fixed selected row is fully present in one deletion
closure and supplies the final equality connector in the T12/F16 local
strict-cycle packet, but this remains diagnostic bookkeeping only.  The packet
does not prove that the row is geometrically forced.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_closure_exposed import (
    FULL_ROW_MODE,
    SCHEMA as CLOSURE_EXPOSED_SCHEMA,
    STATUS as CLOSURE_EXPOSED_STATUS,
    TRUST as CLOSURE_EXPOSED_TRUST,
    build_t12_closure_exposed_payload,
)
from erdos97.bootstrap_t12_relation_sufficient_rows import (
    GAP_FULL_ROW_CLOSURE,
    SCHEMA as RELATION_SUFFICIENT_SCHEMA,
    STATUS as RELATION_SUFFICIENT_STATUS,
    TRUST as RELATION_SUFFICIENT_TRUST,
    build_t12_relation_sufficient_rows_payload,
)
from erdos97.n9_vertex_circle_t12_strict_cycle_lemma_packet import (
    EXPECTED_CORE_SELECTED_ROWS,
    EXPECTED_CYCLE_STEPS,
    SCHEMA as T12_STRICT_CYCLE_SCHEMA,
    STATUS as T12_STRICT_CYCLE_STATUS,
    TRUST as T12_STRICT_CYCLE_TRUST,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_closure_target.v1"
STATUS = "BOOTSTRAP_T12_81_3_CLOSURE_TARGET_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Focused diagnostic for source 81 row 3: the unique relation-sufficient "
    "T12/F16 target whose full fixed selected row is contained in a deletion "
    "closure, and the row that supplies the final T12 equality connector. "
    "This does not prove the row is forced, does not prove n=9, does not "
    "prove the bridge, and does not claim a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "bootstrap_t12_81_3_closure_target.json"
)

TARGET_SOURCE_RECORD_ID = 81
TARGET_CLASSIFICATION_ASSIGNMENT_ID = "A082"
TARGET_ROW_CENTER = 3
TARGET_ROW_KEY = "81:3"
TARGET_WITNESSES = [0, 1, 4, 6]
TARGET_DELETION_SEED = [0, 1, 4]
TARGET_EXPOSED_CORE_VERTEX = 2
TARGET_CLOSURE_LABELS = [0, 1, 3, 4, 6]
TARGET_REQUIREMENT_ID = "81:3:connector:2:0"
TARGET_REQUIRED_WITNESSES = [0, 1]
ROW_FORCING_GAP = "FIXED_FULL_ROW_CLOSURE_NOT_RICH_CLASS_FORCING"
TARGET_NEXT_STATUS = "OPEN_TARGET_NOT_PROVED"


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _record_key(record: Mapping[str, Any]) -> tuple[int, int]:
    return int(record["source_record_id"]), int(record["row_center"])


def _row_key(record: Mapping[str, Any]) -> str:
    return f"{record['source_record_id']}:{record['row_center']}"


def _records_by_key(payload: Mapping[str, Any]) -> dict[tuple[int, int], Mapping[str, Any]]:
    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("payload records must be a list")
    return {_record_key(record): record for record in records}


def _target_relation_records(
    relation_sufficient: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    records = relation_sufficient.get("records")
    if not isinstance(records, list):
        raise AssertionError("relation-sufficient payload records must be a list")
    return [
        record
        for record in records
        if record["row_forcing_gap_type"] == GAP_FULL_ROW_CLOSURE
        and record["row_target_status"] == "CLOSURE_FULL_ROW_CONNECTOR"
    ]


def _target_row_from_t12() -> list[int]:
    for row in EXPECTED_CORE_SELECTED_ROWS:
        normalized = _int_list(row)
        if normalized[0] == TARGET_ROW_CENTER:
            return normalized
    raise AssertionError("T12/F16 local rows no longer contain row center 3")


def _t12_connector_role() -> dict[str, object]:
    for step_index, step in enumerate(EXPECTED_CYCLE_STEPS):
        equality = step["equality_to_next_outer_pair"]
        path = equality["path"]
        if len(path) == 1 and int(path[0]["row"]) == TARGET_ROW_CENTER:
            left_pair = _int_list(equality["start_pair"])
            right_pair = _int_list(equality["end_pair"])
            return {
                "template_id": "T12",
                "family_id": "F16",
                "assignment_id": TARGET_CLASSIFICATION_ASSIGNMENT_ID,
                "cycle_step": step_index,
                "role": "final_equality_connector",
                "selected_row": _target_row_from_t12(),
                "row_center": TARGET_ROW_CENTER,
                "witnesses": TARGET_WITNESSES,
                "equality_step": {
                    "row": TARGET_ROW_CENTER,
                    "left_pair": left_pair,
                    "right_pair": right_pair,
                },
                "connector_pair_chain": [left_pair, right_pair],
                "strict_inequality_before_connector": step["strict_inequality"],
                "conditional_use": (
                    "Conditional: if a future bridge proves row 81:3 as a "
                    "genuine rich class, this row supplies the T12 equality "
                    "[1,3]=[0,3]."
                ),
            }
    raise AssertionError("T12/F16 cycle no longer uses row 3 as a one-step connector")


def _target_record(
    *,
    closure_record: Mapping[str, Any],
    relation_record: Mapping[str, Any],
) -> dict[str, object]:
    requirements = relation_record["relation_sufficient_requirements"]
    if len(requirements) != 1:
        raise AssertionError("81:3 must have exactly one relation-sufficient requirement")
    requirement = requirements[0]
    return {
        "source_record_id": TARGET_SOURCE_RECORD_ID,
        "classification_assignment_id": TARGET_CLASSIFICATION_ASSIGNMENT_ID,
        "target_row_key": TARGET_ROW_KEY,
        "row_center": TARGET_ROW_CENTER,
        "roles": ["equality_connector_row"],
        "witnesses": TARGET_WITNESSES,
        "deletion_seed": _int_list(closure_record["deletion_seed"]),
        "exposed_core_vertex": int(closure_record["exposed_core_vertex"]),
        "closure_labels": _int_list(closure_record["closure_labels"]),
        "closure_size": int(closure_record["closure_size"]),
        "closure_exposure_mode": str(closure_record["closure_exposure_mode"]),
        "row_center_in_closure": bool(closure_record["row_center_in_closure"]),
        "full_row_contained_in_exposure_closure": bool(
            closure_record["full_row_contained_in_exposure_closure"]
        ),
        "witnesses_in_closure": _int_list(closure_record["witnesses_in_closure"]),
        "outside_witnesses": _int_list(closure_record["outside_witnesses"]),
        "outside_witnesses_in_closure": _int_list(
            closure_record["outside_witnesses_in_closure"]
        ),
        "outside_witnesses_private": _int_list(
            closure_record["outside_witnesses_private"]
        ),
        "relation_requirement": {
            "requirement_id": str(requirement["requirement_id"]),
            "kind": str(requirement["kind"]),
            "required_witnesses": _int_list(requirement["required_witnesses"]),
            "relation_state": str(requirement["relation_state"]),
            "bootstrap_core_status": str(requirement["bootstrap_core_status"]),
            "closure_sufficient_count": int(requirement["closure_sufficient_count"]),
            "support_sufficient_count": int(requirement["support_sufficient_count"]),
            "missing_from_bootstrap_core": _int_list(
                requirement["missing_from_bootstrap_core"]
            ),
        },
        "row_forcing_gap_type": ROW_FORCING_GAP,
        "known_evidence": [
            "row center 3 is in the deletion closure for core vertex 2",
            "all four fixed selected witnesses [0,1,4,6] are in that closure",
            "the connector pair [0,1] is bootstrap-core sufficient",
            "the row is a one-step equality connector in the T12/F16 local packet",
        ],
        "missing_geometric_promotion": [
            "prove that closure membership forces a genuine rich class at center 3",
            "or prove the weaker equality-connector forcing [1,3]=[0,3] at center 3",
            "or exhibit a precise rich-class escape mechanism for this closure state",
        ],
        "t12_strict_cycle_role": _t12_connector_role(),
        "bridge_lemma_target": str(relation_record["bridge_lemma_target"]),
    }


def build_t12_81_3_closure_target_payload() -> dict[str, object]:
    """Return the deterministic focused 81:3 closure-target packet."""

    closure_exposed = build_t12_closure_exposed_payload()
    relation_sufficient = build_t12_relation_sufficient_rows_payload()
    closure_records = _records_by_key(closure_exposed)
    relation_records = _records_by_key(relation_sufficient)
    target_key = (TARGET_SOURCE_RECORD_ID, TARGET_ROW_CENTER)
    target_closure = closure_records[target_key]
    target_relation = relation_records[target_key]
    target_relation_records = _target_relation_records(relation_sufficient)
    target_row_keys = [_row_key(record) for record in target_relation_records]

    target = _target_record(
        closure_record=target_closure,
        relation_record=target_relation,
    )
    excluded_relation_sufficient_rows = sorted(
        _row_key(record)
        for record in relation_sufficient["records"]
        if _record_key(record) != target_key
    )
    excluded_closure_exposed_rows = sorted(
        _row_key(record)
        for record in closure_exposed["records"]
        if _record_key(record) != target_key
    )

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This packet isolates one fixed selected row target; it does not prove row or rich-class forcing.",
            "Full-row containment in a deletion closure is not by itself a Euclidean rich-class certificate.",
            "The T12 connector role is conditional on the row being geometrically available.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_record_ids": [TARGET_SOURCE_RECORD_ID],
            "target_row_center": TARGET_ROW_CENTER,
            "target_witnesses": TARGET_WITNESSES,
            "deletion_seed": TARGET_DELETION_SEED,
            "exposed_core_vertex": TARGET_EXPOSED_CORE_VERTEX,
            "closure_labels": TARGET_CLOSURE_LABELS,
            "full_row_closure_relation_sufficient_target_count": len(
                target_relation_records
            ),
            "full_row_closure_relation_sufficient_targets": target_row_keys,
            "relation_sufficient_requirement_ids": [TARGET_REQUIREMENT_ID],
            "required_connector_pair": TARGET_REQUIRED_WITNESSES,
            "t12_connector_pair_chain": [[1, 3], [0, 3]],
            "excluded_relation_sufficient_rows": excluded_relation_sufficient_rows,
            "excluded_closure_exposed_rows": excluded_closure_exposed_rows,
            "row_forcing_gap_type": ROW_FORCING_GAP,
            "row_forcing_target_status": TARGET_NEXT_STATUS,
            "next_bridge_question": (
                "Can the 81:3 full-row deletion-closure exposure be promoted "
                "to genuine rich-class or equality-connector forcing?"
            ),
        },
        "target_record": target,
        "candidate_lemma_contract": {
            "name": "81:3 full-row closure exposure to equality connector",
            "current_status": "open_diagnostic_target",
            "desired_conclusion": [
                "center 3 has a rich class containing witnesses [0,1,4,6]",
                "or at least center 3 forces the equality connector [1,3]=[0,3]",
            ],
            "known_insufficient_inputs": [
                "fixed selected-row membership in a deletion closure",
                "bootstrap-core sufficiency of the stored connector pair",
            ],
            "escape_packet_if_false": (
                "construct a rich-class catalogue in which the deletion closure "
                "contains the fixed row labels but center 3 can avoid the "
                "required equality connector"
            ),
        },
        "source_artifacts": [
            {
                "path": "data/certificates/bootstrap_t12_closure_exposed.json",
                "role": "source full-row deletion-closure exposure for 81:3",
                "schema": CLOSURE_EXPOSED_SCHEMA,
                "status": CLOSURE_EXPOSED_STATUS,
                "trust": CLOSURE_EXPOSED_TRUST,
            },
            {
                "path": "data/certificates/bootstrap_t12_relation_sufficient_rows.json",
                "role": "source relation-sufficient connector requirement for 81:3",
                "schema": RELATION_SUFFICIENT_SCHEMA,
                "status": RELATION_SUFFICIENT_STATUS,
                "trust": RELATION_SUFFICIENT_TRUST,
            },
            {
                "path": "data/certificates/n9_vertex_circle_t12_strict_cycle_lemma_packet.json",
                "role": "source T12/F16 local strict-cycle connector role",
                "schema": T12_STRICT_CYCLE_SCHEMA,
                "status": T12_STRICT_CYCLE_STATUS,
                "trust": T12_STRICT_CYCLE_TRUST,
            },
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_closure_target.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_closure_target.py "
                "--write --assert-expected"
            ),
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def _assert_t12_role(role: Mapping[str, Any]) -> None:
    expected = {
        "template_id": "T12",
        "family_id": "F16",
        "assignment_id": TARGET_CLASSIFICATION_ASSIGNMENT_ID,
        "cycle_step": 2,
        "role": "final_equality_connector",
        "selected_row": [3, 0, 1, 4, 6],
        "row_center": TARGET_ROW_CENTER,
        "witnesses": TARGET_WITNESSES,
        "equality_step": {
            "row": TARGET_ROW_CENTER,
            "left_pair": [1, 3],
            "right_pair": [0, 3],
        },
        "connector_pair_chain": [[1, 3], [0, 3]],
    }
    for key, expected_value in expected.items():
        if role.get(key) != expected_value:
            raise AssertionError(
                f"T12 role {key} is {role.get(key)!r}, expected {expected_value!r}"
            )
    strict = role.get("strict_inequality_before_connector")
    if not isinstance(strict, dict):
        raise AssertionError("T12 role must contain strict_inequality_before_connector")
    if strict.get("row") != 0:
        raise AssertionError("81:3 connector should close the strict edge from row 0")
    if strict.get("outer_pair") != [1, 7] or strict.get("inner_pair") != [1, 3]:
        raise AssertionError("unexpected T12 strict edge before the 81:3 connector")
    if "conditional" not in str(role.get("conditional_use", "")).lower():
        raise AssertionError("T12 role must remain explicitly conditional")


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts for the focused 81:3 target packet."""

    expected_top = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
    }
    for key, expected in expected_top.items():
        if payload.get(key) != expected:
            raise AssertionError(f"{key} mismatch: expected {expected!r}")

    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "target_row_key": TARGET_ROW_KEY,
        "source_record_ids": [TARGET_SOURCE_RECORD_ID],
        "target_row_center": TARGET_ROW_CENTER,
        "target_witnesses": TARGET_WITNESSES,
        "deletion_seed": TARGET_DELETION_SEED,
        "exposed_core_vertex": TARGET_EXPOSED_CORE_VERTEX,
        "closure_labels": TARGET_CLOSURE_LABELS,
        "full_row_closure_relation_sufficient_target_count": 1,
        "full_row_closure_relation_sufficient_targets": [TARGET_ROW_KEY],
        "relation_sufficient_requirement_ids": [TARGET_REQUIREMENT_ID],
        "required_connector_pair": TARGET_REQUIRED_WITNESSES,
        "t12_connector_pair_chain": [[1, 3], [0, 3]],
        "excluded_relation_sufficient_rows": ["151:6", "81:8"],
        "excluded_closure_exposed_rows": ["151:7"],
        "row_forcing_gap_type": ROW_FORCING_GAP,
        "row_forcing_target_status": TARGET_NEXT_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    target = payload.get("target_record")
    if not isinstance(target, dict):
        raise AssertionError("target_record must be a mapping")
    expected_target = {
        "source_record_id": TARGET_SOURCE_RECORD_ID,
        "classification_assignment_id": TARGET_CLASSIFICATION_ASSIGNMENT_ID,
        "target_row_key": TARGET_ROW_KEY,
        "row_center": TARGET_ROW_CENTER,
        "roles": ["equality_connector_row"],
        "witnesses": TARGET_WITNESSES,
        "deletion_seed": TARGET_DELETION_SEED,
        "exposed_core_vertex": TARGET_EXPOSED_CORE_VERTEX,
        "closure_labels": TARGET_CLOSURE_LABELS,
        "closure_size": 5,
        "closure_exposure_mode": FULL_ROW_MODE,
        "row_center_in_closure": True,
        "full_row_contained_in_exposure_closure": True,
        "witnesses_in_closure": TARGET_WITNESSES,
        "outside_witnesses": [6],
        "outside_witnesses_in_closure": [6],
        "outside_witnesses_private": [],
        "row_forcing_gap_type": ROW_FORCING_GAP,
    }
    for key, expected in expected_target.items():
        if target.get(key) != expected:
            raise AssertionError(
                f"target_record {key} is {target.get(key)!r}, expected {expected!r}"
            )

    requirement = target.get("relation_requirement")
    if not isinstance(requirement, dict):
        raise AssertionError("target relation_requirement must be a mapping")
    expected_requirement = {
        "requirement_id": TARGET_REQUIREMENT_ID,
        "kind": "equality_connector_pair",
        "required_witnesses": TARGET_REQUIRED_WITNESSES,
        "relation_state": "BOOTSTRAP_CORE_SUFFICIENT",
        "bootstrap_core_status": "SUFFICIENT",
        "closure_sufficient_count": 1,
        "support_sufficient_count": 0,
        "missing_from_bootstrap_core": [],
    }
    for key, expected in expected_requirement.items():
        if requirement.get(key) != expected:
            raise AssertionError(
                f"target requirement {key} is {requirement.get(key)!r}, "
                f"expected {expected!r}"
            )

    if "does not prove the row is forced" not in payload.get("claim_scope", ""):
        raise AssertionError("claim scope must preserve the no-row-forcing warning")
    warnings = payload.get("interpretation_warnings")
    if not isinstance(warnings, Sequence):
        raise AssertionError("interpretation_warnings must be a sequence")
    if not any("not prove row or rich-class forcing" in str(warning) for warning in warnings):
        raise AssertionError("warnings must preserve the rich-class forcing gap")

    role = target.get("t12_strict_cycle_role")
    if not isinstance(role, dict):
        raise AssertionError("target must include a T12 strict-cycle role")
    _assert_t12_role(role)
