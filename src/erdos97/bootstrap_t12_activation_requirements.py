"""Role-sensitive activation requirements for the bootstrap/T12 target.

This module refines the bootstrap/T12 row-pressure diagnostics by recording
which witness subsets are actually needed for the T12 quotient connectors and
strict vertex-circle edges. It is proof-mining bookkeeping only; it does not
prove that any missing row is forced.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_row_pressure import build_t12_row_pressure_payload
from erdos97.bootstrap_vertex_circle_overlay import build_overlay_payload


SCHEMA = "erdos97.bootstrap_t12_activation_requirements.v1"
STATUS = "BOOTSTRAP_T12_ACTIVATION_REQUIREMENTS_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Role-sensitive activation-requirement diagnostic for the two tight n=9 "
    "bootstrap/T12 records; records the minimal witness subsets needed for "
    "T12/F16 quotient connectors and strict edges only. This does not prove "
    "that the missing rows are forced, does not prove n=9, does not prove the "
    "bridge, and does not claim a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "bootstrap_t12_activation_requirements.json"
)

TARGET_TEMPLATE_ID = "T12"
TARGET_FAMILY_ID = "F16"

KIND_CONNECTOR = "equality_connector_pair"
KIND_STRICT = "strict_edge_endpoint_set"


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _pair(values: Sequence[Any]) -> tuple[int, int]:
    if len(values) != 2:
        raise ValueError("pair must contain exactly two endpoints")
    a, b = int(values[0]), int(values[1])
    if a == b:
        raise ValueError("pair endpoints must be distinct")
    return tuple(sorted((a, b)))


def _pair_json(values: Sequence[Any]) -> list[int]:
    return list(_pair(values))


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _other_endpoint(pair: Sequence[Any], center: int) -> int:
    endpoints = _pair(pair)
    if center == endpoints[0]:
        return endpoints[1]
    if center == endpoints[1]:
        return endpoints[0]
    raise AssertionError(f"row center {center} is not an endpoint of pair {list(endpoints)}")


def _status_for_available(required: set[int], available: set[int]) -> str:
    if required <= available:
        return "SUFFICIENT"
    if required & available:
        return "PARTIAL"
    return "DISJOINT"


def _missing(required: set[int], available: set[int]) -> list[int]:
    return sorted(required - available)


def _row_pressure_by_source_center(row_pressure: Mapping[str, Any]) -> dict[tuple[int, int], dict[str, Any]]:
    rows = row_pressure.get("row_records")
    if not isinstance(rows, list):
        raise AssertionError("row-pressure payload must contain row_records")
    out: dict[tuple[int, int], dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise AssertionError("row-pressure row_records must contain objects")
        key = (int(row["source_record_id"]), int(row["row_center"]))
        out[key] = row
    return out


def _requirements_from_cycle(source_id: int, vertex_circle: Mapping[str, Any]) -> dict[int, list[dict[str, object]]]:
    """Return relation requirements keyed by row center."""

    requirements: defaultdict[int, list[dict[str, object]]] = defaultdict(list)
    steps = vertex_circle.get("cycle_steps")
    if not isinstance(steps, list):
        raise AssertionError("vertex-circle overlay must contain cycle_steps")

    for step_index, step in enumerate(steps):
        strict = step["strict_inequality"]
        strict_row = int(strict["row"])
        outer_pair = _pair_json(strict["outer_pair"])
        inner_pair = _pair_json(strict["inner_pair"])
        strict_required = sorted(set(outer_pair) | set(inner_pair))
        requirements[strict_row].append(
            {
                "requirement_id": f"{source_id}:{strict_row}:strict:{step_index}",
                "kind": KIND_STRICT,
                "step_index": step_index,
                "strict_row": strict_row,
                "outer_pair": outer_pair,
                "inner_pair": inner_pair,
                "required_witnesses": strict_required,
                "requirement_size": len(strict_required),
                "reason": (
                    "strict vertex-circle comparison needs all endpoints of "
                    "the outer and inner witness chords in one rich class"
                ),
            }
        )

        equality = step["equality_to_next_outer_pair"]
        previous_pair = _pair_json(equality["start_pair"])
        path = equality.get("path")
        if not isinstance(path, list):
            raise AssertionError("equality connector path must be a list")
        for path_index, link in enumerate(path):
            row = int(link["row"])
            next_pair = _pair_json(link["next_pair"])
            required = sorted({_other_endpoint(previous_pair, row), _other_endpoint(next_pair, row)})
            requirements[row].append(
                {
                    "requirement_id": f"{source_id}:{row}:connector:{step_index}:{path_index}",
                    "kind": KIND_CONNECTOR,
                    "step_index": step_index,
                    "path_index": path_index,
                    "connector_row": row,
                    "from_pair": previous_pair,
                    "to_pair": next_pair,
                    "required_witnesses": required,
                    "requirement_size": len(required),
                    "reason": (
                        "connector equality needs the two non-center endpoints "
                        "in one rich class at the connector row center"
                    ),
                }
            )
            previous_pair = next_pair
    return dict(requirements)


def _support_evaluations(
    row_record: Mapping[str, Any],
    requirement: Mapping[str, Any],
) -> list[dict[str, object]]:
    required = set(_int_list(requirement["required_witnesses"]))
    bootstrap = set(_int_list(row_record["bootstrap_core_witnesses"]))
    evaluations = []
    for support in row_record.get("support_hits", []):
        if not isinstance(support, dict):
            raise AssertionError("support_hits entries must be objects")
        support_labels = set(_int_list(support["support"]))
        available = bootstrap | support_labels
        evaluations.append(
            {
                "support": sorted(support_labels),
                "available_witnesses": sorted(available),
                "status": _status_for_available(required, available),
                "missing_required_witnesses": _missing(required, available),
                "ledger_private_pair_hit": bool(support.get("ledger_private_pair_hit", False)),
                "private_halo_core_vertices": _int_list(
                    support.get("private_halo_core_vertices", [])
                ),
            }
        )
    return evaluations


def _closure_evaluations(
    row_record: Mapping[str, Any],
    requirement: Mapping[str, Any],
) -> list[dict[str, object]]:
    required = set(_int_list(requirement["required_witnesses"]))
    out = []
    for exposure in row_record.get("deletion_closure_exposures", []):
        if not isinstance(exposure, dict):
            raise AssertionError("deletion_closure_exposures entries must be objects")
        available = set(_int_list(exposure["witnesses_in_closure"]))
        witness_status = _status_for_available(required, available)
        row_center_in_closure = bool(exposure["row_center_in_closure"])
        if witness_status == "SUFFICIENT" and not row_center_in_closure:
            status = "WITNESSES_ONLY"
        else:
            status = witness_status
        out.append(
            {
                "core_vertex": int(exposure["core_vertex"]),
                "closure_labels": _int_list(exposure["closure_labels"]),
                "row_center_in_closure": row_center_in_closure,
                "row_exposed_in_closure": bool(exposure["row_exposed_in_closure"]),
                "activation_ready_in_closure": bool(exposure["activation_ready_in_closure"]),
                "available_witnesses": sorted(available),
                "witness_status": witness_status,
                "status": status,
                "missing_required_witnesses": _missing(required, available),
            }
        )
    return out


def _enrich_requirement(
    row_record: Mapping[str, Any],
    requirement: Mapping[str, Any],
) -> dict[str, object]:
    required = set(_int_list(requirement["required_witnesses"]))
    bootstrap = set(_int_list(row_record["bootstrap_core_witnesses"]))
    support_evaluations = _support_evaluations(row_record, requirement)
    closure_evaluations = _closure_evaluations(row_record, requirement)
    enriched = dict(requirement)
    enriched.update(
        {
            "bootstrap_core_witnesses": sorted(bootstrap),
            "bootstrap_core_status": _status_for_available(required, bootstrap),
            "missing_from_bootstrap_core": _missing(required, bootstrap),
            "support_evaluations": support_evaluations,
            "support_sufficient_count": sum(
                1 for item in support_evaluations if item["status"] == "SUFFICIENT"
            ),
            "closure_evaluations": closure_evaluations,
            "closure_sufficient_count": sum(
                1 for item in closure_evaluations if item["status"] == "SUFFICIENT"
            ),
        }
    )
    return enriched


def _record_for_row(
    *,
    source_id: int,
    row_record: Mapping[str, Any],
    requirements: list[dict[str, object]],
) -> dict[str, object]:
    enriched_requirements = [_enrich_requirement(row_record, req) for req in requirements]
    return {
        "source_record_id": source_id,
        "classification_assignment_id": str(row_record["classification_assignment_id"]),
        "row_center": int(row_record["row_center"]),
        "roles": [str(role) for role in row_record["roles"]],
        "pressure_class": str(row_record["pressure_class"]),
        "witnesses": _int_list(row_record["witnesses"]),
        "bootstrap_core_witnesses": _int_list(row_record["bootstrap_core_witnesses"]),
        "outside_witnesses": _int_list(row_record["outside_witnesses"]),
        "outside_support_kind": str(row_record["outside_support_kind"]),
        "outside_support_subsets": [
            _int_list(subset) for subset in row_record["outside_support_subsets"]
        ],
        "row_center_private_in_all_deletion_closures": bool(
            row_record["row_center_private_in_all_deletion_closures"]
        ),
        "requirement_count": len(enriched_requirements),
        "requirements": enriched_requirements,
        "diagnosis": _row_diagnosis(enriched_requirements),
    }


def _row_diagnosis(requirements: Sequence[Mapping[str, Any]]) -> dict[str, object]:
    strict = [req for req in requirements if req["kind"] == KIND_STRICT]
    connector = [req for req in requirements if req["kind"] == KIND_CONNECTOR]
    all_bootstrap = all(req["bootstrap_core_status"] == "SUFFICIENT" for req in requirements)
    any_support = any(int(req["support_sufficient_count"]) > 0 for req in requirements)
    any_closure = any(int(req["closure_sufficient_count"]) > 0 for req in requirements)
    hard_strict = [
        req["requirement_id"]
        for req in strict
        if req["bootstrap_core_status"] != "SUFFICIENT"
        and int(req["support_sufficient_count"]) == 0
        and int(req["closure_sufficient_count"]) == 0
    ]
    return {
        "connector_requirement_count": len(connector),
        "strict_requirement_count": len(strict),
        "all_requirements_satisfied_by_bootstrap_core": all_bootstrap,
        "any_requirement_satisfied_by_support_option": any_support,
        "any_requirement_satisfied_by_deletion_closure": any_closure,
        "hard_strict_requirement_ids": hard_strict,
    }


def build_t12_activation_requirements_payload() -> dict[str, object]:
    """Return the deterministic bootstrap/T12 activation-requirement packet."""

    overlay = build_overlay_payload()
    row_pressure = build_t12_row_pressure_payload()
    pressure_by_key = _row_pressure_by_source_center(row_pressure)

    records = []
    for overlay_record in overlay["records"]:
        vertex_circle = overlay_record["vertex_circle"]
        if vertex_circle["template_id"] != TARGET_TEMPLATE_ID:
            continue
        if vertex_circle["family_id"] != TARGET_FAMILY_ID:
            continue
        source_id = int(overlay_record["source_record_id"])
        requirements_by_row = _requirements_from_cycle(source_id, vertex_circle)
        gap_centers = sorted(set(_int_list(vertex_circle["cycle_row_centers_outside_bootstrap_core"])))
        for row_center in gap_centers:
            row_record = pressure_by_key[(source_id, row_center)]
            row_requirements = requirements_by_row.get(row_center, [])
            if not row_requirements:
                raise AssertionError(f"missing requirements for source {source_id} row {row_center}")
            records.append(
                _record_for_row(
                    source_id=source_id,
                    row_record=row_record,
                    requirements=row_requirements,
                )
            )

    records.sort(key=lambda row: (int(row["source_record_id"]), int(row["row_center"])))
    requirement_rows = [
        requirement
        for record in records
        for requirement in record["requirements"]
    ]
    kind_counts = Counter(str(req["kind"]) for req in requirement_rows)
    bootstrap_sufficient = [
        str(req["requirement_id"])
        for req in requirement_rows
        if req["bootstrap_core_status"] == "SUFFICIENT"
    ]
    support_sufficient = [
        str(req["requirement_id"])
        for req in requirement_rows
        if int(req["support_sufficient_count"]) > 0
    ]
    closure_sufficient = [
        str(req["requirement_id"])
        for req in requirement_rows
        if int(req["closure_sufficient_count"]) > 0
    ]
    hard_strict = [
        str(req["requirement_id"])
        for req in requirement_rows
        if req["kind"] == KIND_STRICT
        and req["bootstrap_core_status"] != "SUFFICIENT"
        and int(req["support_sufficient_count"]) == 0
        and int(req["closure_sufficient_count"]) == 0
    ]

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This packet classifies fixed selected-row T12 activation requirements; it does not prove the rows are forced.",
            "A connector pair or strict-edge endpoint set is a relation requirement, not a Euclidean rich-class certificate.",
            "Support sufficiency is conditional on the row center/rich class being genuinely activated.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "source_record_ids": sorted({int(row["source_record_id"]) for row in records}),
            "row_record_count": len(records),
            "row_centers_by_source_id": {
                str(source_id): [
                    int(row["row_center"])
                    for row in records
                    if int(row["source_record_id"]) == source_id
                ]
                for source_id in sorted({int(row["source_record_id"]) for row in records})
            },
            "requirement_count": len(requirement_rows),
            "requirement_kind_counts": _json_counter(kind_counts),
            "bootstrap_core_sufficient_requirement_ids": bootstrap_sufficient,
            "bootstrap_core_sufficient_requirement_count": len(bootstrap_sufficient),
            "support_sufficient_requirement_ids": support_sufficient,
            "support_sufficient_requirement_count": len(support_sufficient),
            "closure_sufficient_requirement_ids": closure_sufficient,
            "closure_sufficient_requirement_count": len(closure_sufficient),
            "hard_strict_requirement_ids": hard_strict,
            "hard_strict_requirement_count": len(hard_strict),
            "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
            "main_negative_control": (
                "source 151 row 7 is closure-exposed through witnesses [0,1,4], "
                "but its T12 strict edge needs endpoint set [0,1,6]"
            ),
        },
        "records": records,
        "source_artifacts": [
            {
                "path": "data/certificates/bootstrap_vertex_circle_overlay.json",
                "role": "source T12/F16 strict-cycle rows and cycle steps",
                "schema": overlay.get("schema"),
                "status": overlay.get("status"),
                "trust": overlay.get("trust"),
            },
            {
                "path": "data/certificates/bootstrap_t12_row_pressure.json",
                "role": "source row-pressure records and support options",
                "schema": row_pressure.get("schema"),
                "status": row_pressure.get("status"),
                "trust": row_pressure.get("trust"),
            },
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_activation_requirements.py",
            "command": (
                "python scripts/check_bootstrap_t12_activation_requirements.py "
                "--write --assert-expected"
            ),
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts for the activation-requirement packet."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected bootstrap/T12 activation-requirements schema")
    if payload.get("status") != STATUS:
        raise AssertionError("unexpected bootstrap/T12 activation-requirements status")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "source_record_ids": [81, 151],
        "row_record_count": 6,
        "row_centers_by_source_id": {"81": [3, 8], "151": [5, 6, 7, 8]},
        "requirement_count": 7,
        "requirement_kind_counts": {
            KIND_CONNECTOR: 5,
            KIND_STRICT: 2,
        },
        "bootstrap_core_sufficient_requirement_ids": [
            "81:3:connector:2:0",
            "81:8:connector:0:0",
        ],
        "bootstrap_core_sufficient_requirement_count": 2,
        "support_sufficient_requirement_ids": [
            "81:8:connector:0:0",
            "151:6:connector:2:0",
            "151:8:connector:1:1",
        ],
        "support_sufficient_requirement_count": 3,
        "closure_sufficient_requirement_ids": [
            "81:3:connector:2:0",
        ],
        "closure_sufficient_requirement_count": 1,
        "hard_strict_requirement_ids": [
            "151:7:strict:0",
            "151:8:strict:1",
        ],
        "hard_strict_requirement_count": 2,
        "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary {key} is {summary.get(key)!r}, expected {expected!r}")

    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("records must be a list")
    if len(records) != 6:
        raise AssertionError("expected six row activation-requirement records")
    for record in records:
        if not isinstance(record, dict):
            raise AssertionError("records must contain objects")
        for requirement in record["requirements"]:
            required = set(_int_list(requirement["required_witnesses"]))
            if not required:
                raise AssertionError("requirements must have required witnesses")
            if requirement["kind"] == KIND_CONNECTOR and len(required) != 2:
                raise AssertionError("connector requirements must be witness pairs")
            if requirement["kind"] == KIND_STRICT and len(required) < 3:
                raise AssertionError("strict-edge requirements must have at least three endpoints")
