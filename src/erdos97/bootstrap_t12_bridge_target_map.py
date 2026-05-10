"""Bridge-target map for the bootstrap/T12 diagnostic packets.

This module joins the T12 row-pressure, subpacket, and activation-requirement
ledgers into one reviewer-facing target map. It is proof-mining bookkeeping
only: it does not prove that any missing row is forced.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_activation_requirements import (
    KIND_CONNECTOR,
    KIND_STRICT,
    build_t12_activation_requirements_payload,
)
from erdos97.bootstrap_t12_closure_exposed import (
    FULL_ROW_MODE,
    build_t12_closure_exposed_payload,
)
from erdos97.bootstrap_t12_one_outside import build_t12_one_outside_payload
from erdos97.bootstrap_t12_outside_pair import build_t12_outside_pair_payload
from erdos97.bootstrap_t12_row_pressure import build_t12_row_pressure_payload


SCHEMA = "erdos97.bootstrap_t12_bridge_target_map.v1"
STATUS = "BOOTSTRAP_T12_BRIDGE_TARGET_MAP_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Bridge-target map for the two tight n=9 bootstrap/T12 records; joins "
    "row-pressure classes, focused support packets, and role-sensitive "
    "activation requirements into explicit next-lemma targets. This does not "
    "prove that the missing rows are forced, does not prove n=9, does not "
    "prove the bridge, and does not claim a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "bootstrap_t12_bridge_target_map.json"
)

PRESSURE_CLOSURE = "ALREADY_PRESENT_IN_A_DELETION_CLOSURE"
PRESSURE_ONE_OUTSIDE = "NEEDS_ONE_OUTSIDE_LABEL_AND_PRIVATE_CENTER"
PRESSURE_OUTSIDE_PAIR = "NEEDS_OUTSIDE_PAIR_AND_PRIVATE_CENTER"

PACKET_CLOSURE = "bootstrap_t12_closure_exposed"
PACKET_ONE_OUTSIDE = "bootstrap_t12_one_outside"
PACKET_OUTSIDE_PAIR = "bootstrap_t12_outside_pair"

RELATION_BOOTSTRAP_CORE = "BOOTSTRAP_CORE_SUFFICIENT"
RELATION_SUPPORT = "SUPPORT_SUFFICIENT"
RELATION_CLOSURE = "CLOSURE_SUFFICIENT"
RELATION_HARD_STRICT = "HARD_STRICT_ENDPOINT_REQUIREMENT"
RELATION_OPEN_CONNECTOR = "OPEN_CONNECTOR_REQUIREMENT"
RELATION_OPEN = "OPEN_REQUIREMENT"

ROW_TARGETS: dict[tuple[int, int], dict[str, str]] = {
    (81, 3): {
        "target_status": "CLOSURE_FULL_ROW_CONNECTOR",
        "bridge_lemma_target": (
            "Turn a full-row deletion-closure exposure into a genuine "
            "equality-connector rich class."
        ),
    },
    (81, 8): {
        "target_status": "CORE_CONNECTOR_WITH_SINGLETON_ROW_ACTIVATION",
        "bridge_lemma_target": (
            "Force the private row center plus one singleton outside support; "
            "the connector pair itself is already bootstrap-core visible."
        ),
    },
    (151, 5): {
        "target_status": "SINGLETON_ROW_OPEN_CONNECTOR_PAIR",
        "bridge_lemma_target": (
            "Explain how a singleton-activated row can also supply both "
            "outside endpoints of its equality-connector pair."
        ),
    },
    (151, 6): {
        "target_status": "OUTSIDE_PAIR_CONNECTOR_PARTIAL_LEDGER",
        "bridge_lemma_target": (
            "Promote the outside-pair support, with partial private-pair "
            "ledger contact, to an equality-connector row-forcing lemma."
        ),
    },
    (151, 7): {
        "target_status": "CLOSURE_EXPOSED_HARD_STRICT_ENDPOINT",
        "bridge_lemma_target": (
            "Add the missing strict-edge endpoint to a closure-exposed row; "
            "this is the main negative control."
        ),
    },
    (151, 8): {
        "target_status": "MIXED_SINGLETON_CONNECTOR_AND_HARD_STRICT",
        "bridge_lemma_target": (
            "Separate the connector support, which one singleton can supply, "
            "from the strict-edge endpoint set, which remains unforced."
        ),
    },
}


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _record_key(record: Mapping[str, Any]) -> tuple[int, int]:
    return int(record["source_record_id"]), int(record["row_center"])


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _index_records(records: Sequence[Mapping[str, Any]]) -> dict[tuple[int, int], Mapping[str, Any]]:
    return {_record_key(record): record for record in records}


def _relation_state(requirement: Mapping[str, Any]) -> str:
    if requirement["bootstrap_core_status"] == "SUFFICIENT":
        return RELATION_BOOTSTRAP_CORE
    if int(requirement["support_sufficient_count"]) > 0:
        return RELATION_SUPPORT
    if int(requirement["closure_sufficient_count"]) > 0:
        return RELATION_CLOSURE
    if requirement["kind"] == KIND_STRICT:
        return RELATION_HARD_STRICT
    if requirement["kind"] == KIND_CONNECTOR:
        return RELATION_OPEN_CONNECTOR
    return RELATION_OPEN


def _requirement_record(requirement: Mapping[str, Any]) -> dict[str, object]:
    relation_state = _relation_state(requirement)
    return {
        "requirement_id": str(requirement["requirement_id"]),
        "kind": str(requirement["kind"]),
        "required_witnesses": _int_list(requirement["required_witnesses"]),
        "bootstrap_core_status": str(requirement["bootstrap_core_status"]),
        "support_sufficient_count": int(requirement["support_sufficient_count"]),
        "closure_sufficient_count": int(requirement["closure_sufficient_count"]),
        "missing_from_bootstrap_core": _int_list(
            requirement["missing_from_bootstrap_core"]
        ),
        "relation_state": relation_state,
    }


def _support_packet_name(pressure_class: str) -> str:
    if pressure_class == PRESSURE_CLOSURE:
        return PACKET_CLOSURE
    if pressure_class == PRESSURE_ONE_OUTSIDE:
        return PACKET_ONE_OUTSIDE
    if pressure_class == PRESSURE_OUTSIDE_PAIR:
        return PACKET_OUTSIDE_PAIR
    raise AssertionError(f"unknown pressure class {pressure_class!r}")


def _closure_support_summary(record: Mapping[str, Any]) -> dict[str, object]:
    return {
        "closure_exposure_mode": str(record["closure_exposure_mode"]),
        "exposed_core_vertex": int(record["exposed_core_vertex"]),
        "full_row_contained_in_exposure_closure": bool(
            record["full_row_contained_in_exposure_closure"]
        ),
        "outside_witnesses_private": _int_list(record["outside_witnesses_private"]),
        "witnesses_in_closure": _int_list(record["witnesses_in_closure"]),
    }


def _one_outside_support_summary(record: Mapping[str, Any]) -> dict[str, object]:
    options = record["support_options"]
    return {
        "support_labels": [int(option["support_label"]) for option in options],
        "support_label_modes": [
            str(option["support_label_mode"]) for option in options
        ],
        "private_halo_containment_counts": [
            int(option["private_halo_containment_count"]) for option in options
        ],
        "ledger_private_pair_support_hit_count": int(
            record["ledger_private_pair_support_hit_count"]
        ),
    }


def _outside_pair_support_summary(record: Mapping[str, Any]) -> dict[str, object]:
    options = record["support_pair_options"]
    return {
        "support_pairs": [_int_list(option["support_pair"]) for option in options],
        "support_pair_modes": [
            str(option["support_pair_mode"]) for option in options
        ],
        "ledger_hit_support_pairs": [
            _int_list(option["support_pair"])
            for option in options
            if bool(option["ledger_private_pair_hit"])
        ],
        "ledger_miss_support_pairs": [
            _int_list(option["support_pair"])
            for option in options
            if not bool(option["ledger_private_pair_hit"])
        ],
        "ledger_private_pair_support_hit_count": int(
            record["ledger_private_pair_support_hit_count"]
        ),
    }


def _packet_summary(
    *,
    key: tuple[int, int],
    pressure_class: str,
    closure_records: Mapping[tuple[int, int], Mapping[str, Any]],
    one_outside_records: Mapping[tuple[int, int], Mapping[str, Any]],
    outside_pair_records: Mapping[tuple[int, int], Mapping[str, Any]],
) -> dict[str, object]:
    packet_name = _support_packet_name(pressure_class)
    if packet_name == PACKET_CLOSURE:
        return {
            "support_packet": packet_name,
            **_closure_support_summary(closure_records[key]),
        }
    if packet_name == PACKET_ONE_OUTSIDE:
        return {
            "support_packet": packet_name,
            **_one_outside_support_summary(one_outside_records[key]),
        }
    return {
        "support_packet": packet_name,
        **_outside_pair_support_summary(outside_pair_records[key]),
    }


def _target_record(
    *,
    row_record: Mapping[str, Any],
    activation_record: Mapping[str, Any],
    closure_records: Mapping[tuple[int, int], Mapping[str, Any]],
    one_outside_records: Mapping[tuple[int, int], Mapping[str, Any]],
    outside_pair_records: Mapping[tuple[int, int], Mapping[str, Any]],
) -> dict[str, object]:
    key = _record_key(row_record)
    target = ROW_TARGETS[key]
    requirements = [
        _requirement_record(requirement)
        for requirement in activation_record["requirements"]
    ]
    relation_state_counts = Counter(
        str(requirement["relation_state"]) for requirement in requirements
    )
    pressure_class = str(row_record["pressure_class"])

    return {
        "source_record_id": key[0],
        "classification_assignment_id": str(row_record["classification_assignment_id"]),
        "row_center": key[1],
        "roles": [str(role) for role in row_record["roles"]],
        "witnesses": _int_list(row_record["witnesses"]),
        "bootstrap_core_witnesses": _int_list(row_record["bootstrap_core_witnesses"]),
        "outside_witnesses": _int_list(row_record["outside_witnesses"]),
        "activation_deficit_from_bootstrap_core": int(
            row_record["activation_deficit_from_bootstrap_core"]
        ),
        "row_center_private_in_all_deletion_closures": bool(
            row_record["row_center_private_in_all_deletion_closures"]
        ),
        "pressure_class": pressure_class,
        "support_packet_summary": _packet_summary(
            key=key,
            pressure_class=pressure_class,
            closure_records=closure_records,
            one_outside_records=one_outside_records,
            outside_pair_records=outside_pair_records,
        ),
        "requirement_count": len(requirements),
        "requirements": requirements,
        "relation_state_counts": _json_counter(relation_state_counts),
        "row_target_status": target["target_status"],
        "bridge_lemma_target": target["bridge_lemma_target"],
    }


def build_t12_bridge_target_map_payload() -> dict[str, object]:
    """Return the deterministic bootstrap/T12 bridge-target map."""

    row_pressure = build_t12_row_pressure_payload()
    activation = build_t12_activation_requirements_payload()
    closure = build_t12_closure_exposed_payload()
    one_outside = build_t12_one_outside_payload()
    outside_pair = build_t12_outside_pair_payload()

    row_records = _index_records(row_pressure["row_records"])
    activation_records = _index_records(activation["records"])
    closure_records = _index_records(closure["records"])
    one_outside_records = _index_records(one_outside["records"])
    outside_pair_records = _index_records(outside_pair["records"])

    records = [
        _target_record(
            row_record=row_records[key],
            activation_record=activation_records[key],
            closure_records=closure_records,
            one_outside_records=one_outside_records,
            outside_pair_records=outside_pair_records,
        )
        for key in sorted(row_records)
    ]

    pressure_counts = Counter(str(record["pressure_class"]) for record in records)
    support_packet_counts = Counter(
        str(record["support_packet_summary"]["support_packet"]) for record in records
    )
    row_target_counts = Counter(str(record["row_target_status"]) for record in records)
    role_counts = Counter(role for record in records for role in record["roles"])
    relation_state_counts = Counter(
        str(requirement["relation_state"])
        for record in records
        for requirement in record["requirements"]
    )
    requirement_kind_counts = Counter(
        str(requirement["kind"])
        for record in records
        for requirement in record["requirements"]
    )
    rows_by_source: defaultdict[int, list[int]] = defaultdict(list)
    for record in records:
        rows_by_source[int(record["source_record_id"])].append(
            int(record["row_center"])
        )

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This map is a join of fixed selected-row diagnostics; it does not prove any missing T12 row is forced.",
            "A bridge-lemma target is an open proof obligation, not a theorem or Euclidean certificate.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "source_record_ids": sorted(rows_by_source),
            "row_target_count": len(records),
            "row_centers_by_source_id": {
                str(source_id): centers for source_id, centers in sorted(rows_by_source.items())
            },
            "pressure_class_counts": _json_counter(pressure_counts),
            "support_packet_counts": _json_counter(support_packet_counts),
            "row_target_status_counts": _json_counter(row_target_counts),
            "role_counts": _json_counter(role_counts),
            "requirement_count": sum(
                int(record["requirement_count"]) for record in records
            ),
            "requirement_kind_counts": _json_counter(requirement_kind_counts),
            "relation_state_counts": _json_counter(relation_state_counts),
            "hard_strict_row_targets": [
                f"{record['source_record_id']}:{record['row_center']}"
                for record in records
                if RELATION_HARD_STRICT in record["relation_state_counts"]
            ],
            "open_connector_row_targets": [
                f"{record['source_record_id']}:{record['row_center']}"
                for record in records
                if RELATION_OPEN_CONNECTOR in record["relation_state_counts"]
            ],
            "bridge_target_status": "OPEN_TARGET_NOT_PROVED",
            "next_bridge_question": (
                "Can a role-aware geometric bridge force the listed row "
                "targets, or prove a real blocker escape, using rich-class "
                "geometry rather than fixed selected-row bookkeeping?"
            ),
        },
        "records": records,
        "source_artifacts": [
            {
                "path": "data/certificates/bootstrap_t12_row_pressure.json",
                "role": "row pressure classes and core/outside witness deficits",
                "schema": row_pressure.get("schema"),
                "status": row_pressure.get("status"),
                "trust": row_pressure.get("trust"),
            },
            {
                "path": "data/certificates/bootstrap_t12_activation_requirements.json",
                "role": "role-sensitive connector-pair and strict-edge endpoint requirements",
                "schema": activation.get("schema"),
                "status": activation.get("status"),
                "trust": activation.get("trust"),
            },
            {
                "path": "data/certificates/bootstrap_t12_closure_exposed.json",
                "role": "closure-exposed support packet",
                "schema": closure.get("schema"),
                "status": closure.get("status"),
                "trust": closure.get("trust"),
            },
            {
                "path": "data/certificates/bootstrap_t12_one_outside.json",
                "role": "one-outside-label support packet",
                "schema": one_outside.get("schema"),
                "status": one_outside.get("status"),
                "trust": one_outside.get("trust"),
            },
            {
                "path": "data/certificates/bootstrap_t12_outside_pair.json",
                "role": "outside-pair support packet",
                "schema": outside_pair.get("schema"),
                "status": outside_pair.get("status"),
                "trust": outside_pair.get("trust"),
            },
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_bridge_target_map.py",
            "command": (
                "python scripts/check_bootstrap_t12_bridge_target_map.py "
                "--write --assert-expected"
            ),
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts for the bridge-target map."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected bootstrap/T12 bridge-target-map schema")
    if payload.get("status") != STATUS:
        raise AssertionError("unexpected bootstrap/T12 bridge-target-map status")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "source_record_ids": [81, 151],
        "row_target_count": 6,
        "row_centers_by_source_id": {"81": [3, 8], "151": [5, 6, 7, 8]},
        "pressure_class_counts": {
            PRESSURE_CLOSURE: 2,
            PRESSURE_ONE_OUTSIDE: 3,
            PRESSURE_OUTSIDE_PAIR: 1,
        },
        "support_packet_counts": {
            PACKET_CLOSURE: 2,
            PACKET_ONE_OUTSIDE: 3,
            PACKET_OUTSIDE_PAIR: 1,
        },
        "row_target_status_counts": {
            "CLOSURE_EXPOSED_HARD_STRICT_ENDPOINT": 1,
            "CLOSURE_FULL_ROW_CONNECTOR": 1,
            "CORE_CONNECTOR_WITH_SINGLETON_ROW_ACTIVATION": 1,
            "MIXED_SINGLETON_CONNECTOR_AND_HARD_STRICT": 1,
            "OUTSIDE_PAIR_CONNECTOR_PARTIAL_LEDGER": 1,
            "SINGLETON_ROW_OPEN_CONNECTOR_PAIR": 1,
        },
        "role_counts": {"equality_connector_row": 5, "strict_edge_row": 2},
        "requirement_count": 7,
        "requirement_kind_counts": {KIND_CONNECTOR: 5, KIND_STRICT: 2},
        "relation_state_counts": {
            RELATION_BOOTSTRAP_CORE: 2,
            RELATION_HARD_STRICT: 2,
            RELATION_OPEN_CONNECTOR: 1,
            RELATION_SUPPORT: 2,
        },
        "hard_strict_row_targets": ["151:7", "151:8"],
        "open_connector_row_targets": ["151:5"],
        "bridge_target_status": "OPEN_TARGET_NOT_PROVED",
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary {key} is {summary.get(key)!r}, expected {expected!r}")

    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("records must be a list")
    expected_statuses = {
        (81, 3): "CLOSURE_FULL_ROW_CONNECTOR",
        (81, 8): "CORE_CONNECTOR_WITH_SINGLETON_ROW_ACTIVATION",
        (151, 5): "SINGLETON_ROW_OPEN_CONNECTOR_PAIR",
        (151, 6): "OUTSIDE_PAIR_CONNECTOR_PARTIAL_LEDGER",
        (151, 7): "CLOSURE_EXPOSED_HARD_STRICT_ENDPOINT",
        (151, 8): "MIXED_SINGLETON_CONNECTOR_AND_HARD_STRICT",
    }
    by_key = {_record_key(record): record for record in records}
    if set(by_key) != set(expected_statuses):
        raise AssertionError("unexpected bridge-target record keys")
    for key, expected_status in expected_statuses.items():
        record = by_key[key]
        if record["row_target_status"] != expected_status:
            raise AssertionError(f"row target {key} status changed")
        if not record["bridge_lemma_target"]:
            raise AssertionError(f"row target {key} must name a bridge lemma target")

    record_151_7 = by_key[(151, 7)]
    if record_151_7["support_packet_summary"]["closure_exposure_mode"] == FULL_ROW_MODE:
        raise AssertionError("151:7 must remain the closure strict-endpoint negative control")
    if RELATION_HARD_STRICT not in record_151_7["relation_state_counts"]:
        raise AssertionError("151:7 must retain a hard strict endpoint requirement")
