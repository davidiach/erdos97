"""Closure-exposed row packet for the bootstrap/T12 target.

This module isolates the easiest row-pressure subcase: missing T12/F16 rows
whose row center and three selected witnesses are already visible in a deletion
closure.  It is proof-mining bookkeeping only and does not prove that any
missing row is geometrically forced.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from erdos97.bootstrap_t12_row_pressure import build_t12_row_pressure_payload


SCHEMA = "erdos97.bootstrap_t12_closure_exposed.v1"
STATUS = "BOOTSTRAP_T12_CLOSURE_EXPOSED_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Closure-exposed-row packet for the two tight n=9 bootstrap/T12 records; "
    "isolates the missing T12/F16 row centers that are already activation-ready "
    "inside a deletion closure. This does not prove that the missing rows are "
    "forced, does not prove n=9, does not prove the bridge, and does not claim "
    "a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = REPO_ROOT / "data" / "certificates" / "bootstrap_t12_closure_exposed.json"

PRESSURE_CLASS = "ALREADY_PRESENT_IN_A_DELETION_CLOSURE"
FULL_ROW_MODE = "CENTER_AND_FULL_ROW_IN_CLOSURE"
CORE_WITNESS_MODE = "CENTER_AND_CORE_WITNESSES_IN_CLOSURE"


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _closure_exposure_mode(*, full_row_contained: bool) -> str:
    if full_row_contained:
        return FULL_ROW_MODE
    return CORE_WITNESS_MODE


def _exposure_record(
    *,
    row_record: Mapping[str, Any],
    exposure: Mapping[str, Any],
) -> dict[str, object]:
    witnesses = set(_int_list(row_record["witnesses"]))
    core_witnesses = set(_int_list(row_record["bootstrap_core_witnesses"]))
    outside_witnesses = set(_int_list(row_record["outside_witnesses"]))
    closure_labels = set(_int_list(exposure["closure_labels"]))

    witnesses_in_closure = sorted(witnesses & closure_labels)
    full_row_contained = witnesses <= closure_labels
    mode = _closure_exposure_mode(full_row_contained=full_row_contained)

    return {
        "source_record_id": int(row_record["source_record_id"]),
        "classification_assignment_id": str(row_record["classification_assignment_id"]),
        "row_center": int(row_record["row_center"]),
        "roles": [str(role) for role in row_record["roles"]],
        "witnesses": sorted(witnesses),
        "bootstrap_core_witnesses": sorted(core_witnesses),
        "outside_witnesses": sorted(outside_witnesses),
        "pressure_class": str(row_record["pressure_class"]),
        "exposed_core_vertex": int(exposure["core_vertex"]),
        "deletion_seed": _int_list(exposure["deletion_seed"]),
        "closure_labels": sorted(closure_labels),
        "closure_size": int(exposure["closure_size"]),
        "row_center_in_closure": bool(exposure["row_center_in_closure"]),
        "witnesses_in_closure": witnesses_in_closure,
        "witness_count_in_closure": len(witnesses_in_closure),
        "core_witnesses_in_closure": sorted(core_witnesses & closure_labels),
        "core_witness_count_in_closure": len(core_witnesses & closure_labels),
        "outside_witnesses_in_closure": sorted(outside_witnesses & closure_labels),
        "outside_witnesses_private": sorted(outside_witnesses - closure_labels),
        "private_witnesses": _int_list(exposure["private_witnesses"]),
        "activation_ready_in_closure": bool(exposure["activation_ready_in_closure"]),
        "full_row_contained_in_exposure_closure": full_row_contained,
        "closure_exposure_mode": mode,
    }


def _closure_exposed_records(row_pressure: Mapping[str, Any]) -> list[dict[str, object]]:
    row_records = row_pressure.get("row_records")
    if not isinstance(row_records, list):
        raise AssertionError("row-pressure payload row_records must be a list")

    records = []
    for row_record in row_records:
        if row_record["pressure_class"] != PRESSURE_CLASS:
            continue
        exposures = [
            exposure
            for exposure in row_record["deletion_closure_exposures"]
            if bool(exposure["row_exposed_in_closure"])
        ]
        if not exposures:
            raise AssertionError("closure-exposed row has no exposed deletion closure")
        for exposure in exposures:
            records.append(_exposure_record(row_record=row_record, exposure=exposure))

    records.sort(
        key=lambda record: (
            int(record["source_record_id"]),
            int(record["row_center"]),
            int(record["exposed_core_vertex"]),
        )
    )
    return records


def build_t12_closure_exposed_payload() -> dict[str, object]:
    """Return the deterministic closure-exposed bootstrap/T12 packet."""

    row_pressure = build_t12_row_pressure_payload()
    records = _closure_exposed_records(row_pressure)

    exposure_mode_counts = Counter(str(record["closure_exposure_mode"]) for record in records)
    role_counts = Counter(role for record in records for role in record["roles"])
    rows_by_source: defaultdict[int, list[int]] = defaultdict(list)
    exposed_core_vertices_by_source: defaultdict[int, list[int]] = defaultdict(list)
    full_row_rows_by_source: defaultdict[int, list[int]] = defaultdict(list)
    core_only_rows_by_source: defaultdict[int, list[int]] = defaultdict(list)
    for record in records:
        source_id = int(record["source_record_id"])
        row_center = int(record["row_center"])
        rows_by_source[source_id].append(row_center)
        exposed_core_vertices_by_source[source_id].append(int(record["exposed_core_vertex"]))
        if record["full_row_contained_in_exposure_closure"]:
            full_row_rows_by_source[source_id].append(row_center)
        else:
            core_only_rows_by_source[source_id].append(row_center)

    core_witness_signatures = sorted(
        {tuple(_int_list(record["core_witnesses_in_closure"])) for record in records}
    )

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This packet isolates fixed selected-row deletion-closure exposures; it does not prove the rows are forced.",
            "A closure exposure is a local activation-ready bookkeeping state, not a Euclidean rich-class certificate.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "source_record_ids": sorted(rows_by_source),
            "closure_exposed_row_record_count": len(records),
            "row_centers_by_source_id": {
                str(source_id): centers for source_id, centers in sorted(rows_by_source.items())
            },
            "exposed_core_vertices_by_source_id": {
                str(source_id): centers
                for source_id, centers in sorted(exposed_core_vertices_by_source.items())
            },
            "exposure_mode_counts": _json_counter(exposure_mode_counts),
            "full_row_contained_count": sum(
                1 for record in records if record["full_row_contained_in_exposure_closure"]
            ),
            "activation_ready_count": sum(
                1 for record in records if record["activation_ready_in_closure"]
            ),
            "row_center_in_closure_count": sum(
                1 for record in records if record["row_center_in_closure"]
            ),
            "core_witness_signatures": [list(signature) for signature in core_witness_signatures],
            "role_counts": _json_counter(role_counts),
            "full_row_contained_rows_by_source_id": {
                str(source_id): centers
                for source_id, centers in sorted(full_row_rows_by_source.items())
            },
            "core_witness_only_rows_by_source_id": {
                str(source_id): centers
                for source_id, centers in sorted(core_only_rows_by_source.items())
            },
            "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
            "next_bridge_question": (
                "Can a future bridge turn deletion-closure activation readiness "
                "into a genuine rich-class row-forcing lemma?"
            ),
        },
        "records": records,
        "source_artifacts": [
            {
                "path": "data/certificates/bootstrap_t12_row_pressure.json",
                "role": "source row-pressure records and deletion-closure exposures",
                "schema": row_pressure.get("schema"),
                "status": row_pressure.get("status"),
                "trust": row_pressure.get("trust"),
            }
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_closure_exposed.py",
            "command": "python scripts/check_bootstrap_t12_closure_exposed.py --write --assert-expected",
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts for the closure-exposed packet."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected bootstrap/T12 closure-exposed schema")
    if payload.get("status") != STATUS:
        raise AssertionError("unexpected bootstrap/T12 closure-exposed status")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "source_record_ids": [81, 151],
        "closure_exposed_row_record_count": 2,
        "row_centers_by_source_id": {"81": [3], "151": [7]},
        "exposed_core_vertices_by_source_id": {"81": [2], "151": [2]},
        "exposure_mode_counts": {
            CORE_WITNESS_MODE: 1,
            FULL_ROW_MODE: 1,
        },
        "full_row_contained_count": 1,
        "activation_ready_count": 2,
        "row_center_in_closure_count": 2,
        "core_witness_signatures": [[0, 1, 4]],
        "role_counts": {"equality_connector_row": 1, "strict_edge_row": 1},
        "full_row_contained_rows_by_source_id": {"81": [3]},
        "core_witness_only_rows_by_source_id": {"151": [7]},
        "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary {key} is {summary.get(key)!r}, expected {expected!r}")

    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("records must be a list")
    expected_records = {
        (81, 3): {
            "classification_assignment_id": "A082",
            "roles": ["equality_connector_row"],
            "witnesses": [0, 1, 4, 6],
            "bootstrap_core_witnesses": [0, 1, 4],
            "outside_witnesses": [6],
            "exposed_core_vertex": 2,
            "deletion_seed": [0, 1, 4],
            "closure_labels": [0, 1, 3, 4, 6],
            "closure_size": 5,
            "witnesses_in_closure": [0, 1, 4, 6],
            "outside_witnesses_in_closure": [6],
            "outside_witnesses_private": [],
            "full_row_contained_in_exposure_closure": True,
            "closure_exposure_mode": FULL_ROW_MODE,
        },
        (151, 7): {
            "classification_assignment_id": "A152",
            "roles": ["strict_edge_row"],
            "witnesses": [0, 1, 4, 6],
            "bootstrap_core_witnesses": [0, 1, 4],
            "outside_witnesses": [6],
            "exposed_core_vertex": 2,
            "deletion_seed": [0, 1, 4],
            "closure_labels": [0, 1, 4, 7],
            "closure_size": 4,
            "witnesses_in_closure": [0, 1, 4],
            "outside_witnesses_in_closure": [],
            "outside_witnesses_private": [6],
            "full_row_contained_in_exposure_closure": False,
            "closure_exposure_mode": CORE_WITNESS_MODE,
        },
    }
    by_key = {
        (int(record["source_record_id"]), int(record["row_center"])): record
        for record in records
    }
    if set(by_key) != set(expected_records):
        raise AssertionError("unexpected closure-exposed record keys")
    for key, expected in expected_records.items():
        record = by_key[key]
        for field, expected_value in expected.items():
            if record.get(field) != expected_value:
                raise AssertionError(
                    f"closure-exposed {key} {field} is {record.get(field)!r}, "
                    f"expected {expected_value!r}"
                )
        if record.get("pressure_class") != PRESSURE_CLASS:
            raise AssertionError(f"closure-exposed {key} pressure class changed")
        if not record.get("row_center_in_closure"):
            raise AssertionError(f"closure-exposed {key} row center not in closure")
        if not record.get("activation_ready_in_closure"):
            raise AssertionError(f"closure-exposed {key} not activation-ready")
        if record.get("core_witnesses_in_closure") != [0, 1, 4]:
            raise AssertionError(f"closure-exposed {key} core witnesses changed")
