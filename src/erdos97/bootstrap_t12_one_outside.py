"""One-outside-label packet for the bootstrap/T12 target.

This module isolates the row-pressure subcase where a missing T12/F16 row has
two bootstrap-core witnesses and needs one outside label while its row center
remains private in every deletion closure.  It is proof-mining bookkeeping only
and does not prove that any missing row is geometrically forced.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from erdos97.bootstrap_t12_row_pressure import build_t12_row_pressure_payload


SCHEMA = "erdos97.bootstrap_t12_one_outside.v1"
STATUS = "BOOTSTRAP_T12_ONE_OUTSIDE_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "One-outside-label packet for the two tight n=9 bootstrap/T12 records; "
    "isolates the missing T12/F16 row centers that need one outside label "
    "while the row center remains private in every deletion closure. This "
    "does not prove that the missing rows are forced, does not prove n=9, "
    "does not prove the bridge, and does not claim a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = REPO_ROOT / "data" / "certificates" / "bootstrap_t12_one_outside.json"

PRESSURE_CLASS = "NEEDS_ONE_OUTSIDE_LABEL_AND_PRIVATE_CENTER"
PRIVATE_ALL_MODE = "PRIVATE_IN_ALL_DELETION_HALOS"
CLOSURE_INTERNAL_MODE = "INTERNAL_TO_ONE_DELETION_CLOSURE"


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _support_mode(missing_private_halo_core_vertices: list[int]) -> str:
    if missing_private_halo_core_vertices:
        return CLOSURE_INTERNAL_MODE
    return PRIVATE_ALL_MODE


def _support_option(
    *,
    row_record: Mapping[str, Any],
    hit: Mapping[str, Any],
) -> dict[str, object]:
    support = _int_list(hit["support"])
    if len(support) != 1:
        raise AssertionError("one-outside-label packet received non-singleton support")
    support_label = support[0]
    core_witnesses = _int_list(row_record["bootstrap_core_witnesses"])
    row_center_private_core_vertices = _int_list(row_record["row_center_private_core_vertices"])
    private_halo_core_vertices = _int_list(hit["private_halo_core_vertices"])
    missing_private_halo_core_vertices = sorted(
        set(row_center_private_core_vertices) - set(private_halo_core_vertices)
    )
    closure_internal_core_vertices = [
        int(exposure["core_vertex"])
        for exposure in row_record["deletion_closure_exposures"]
        if support_label in set(_int_list(exposure["closure_labels"]))
    ]
    mode = _support_mode(missing_private_halo_core_vertices)

    return {
        "support_label": support_label,
        "activation_witnesses_from_core_plus_support": sorted(
            set(core_witnesses) | {support_label}
        ),
        "activation_witness_count": len(set(core_witnesses) | {support_label}),
        "activation_ready_with_support": len(set(core_witnesses) | {support_label}) >= 3,
        "private_halo_core_vertices": private_halo_core_vertices,
        "private_halo_containment_count": int(hit["private_halo_containment_count"]),
        "missing_private_halo_core_vertices": missing_private_halo_core_vertices,
        "closure_internal_core_vertices": sorted(closure_internal_core_vertices),
        "support_label_mode": mode,
        "ledger_private_pair_core_vertices": _int_list(hit["ledger_private_pair_core_vertices"]),
        "ledger_private_pair_hit": bool(hit["ledger_private_pair_hit"]),
    }


def _one_outside_record(row_record: Mapping[str, Any]) -> dict[str, object]:
    support_options = [
        _support_option(row_record=row_record, hit=hit)
        for hit in row_record["support_hits"]
    ]
    support_options.sort(key=lambda option: int(option["support_label"]))
    support_mode_counts = Counter(str(option["support_label_mode"]) for option in support_options)

    return {
        "source_record_id": int(row_record["source_record_id"]),
        "classification_assignment_id": str(row_record["classification_assignment_id"]),
        "row_center": int(row_record["row_center"]),
        "roles": [str(role) for role in row_record["roles"]],
        "witnesses": _int_list(row_record["witnesses"]),
        "bootstrap_core_witnesses": _int_list(row_record["bootstrap_core_witnesses"]),
        "outside_witnesses": _int_list(row_record["outside_witnesses"]),
        "activation_deficit_from_bootstrap_core": int(
            row_record["activation_deficit_from_bootstrap_core"]
        ),
        "outside_support_kind": str(row_record["outside_support_kind"]),
        "pressure_class": str(row_record["pressure_class"]),
        "row_center_private_core_vertices": _int_list(row_record["row_center_private_core_vertices"]),
        "row_center_private_in_all_deletion_closures": bool(
            row_record["row_center_private_in_all_deletion_closures"]
        ),
        "max_witness_count_in_deletion_closure": int(
            row_record["max_witness_count_in_deletion_closure"]
        ),
        "support_options": support_options,
        "support_option_count": len(support_options),
        "support_label_modes": _json_counter(support_mode_counts),
        "ledger_private_pair_support_hit_count": int(
            row_record["ledger_private_pair_support_hit_count"]
        ),
    }


def _one_outside_records(row_pressure: Mapping[str, Any]) -> list[dict[str, object]]:
    row_records = row_pressure.get("row_records")
    if not isinstance(row_records, list):
        raise AssertionError("row-pressure payload row_records must be a list")
    records = [
        _one_outside_record(row_record)
        for row_record in row_records
        if row_record["pressure_class"] == PRESSURE_CLASS
    ]
    records.sort(key=lambda record: (int(record["source_record_id"]), int(record["row_center"])))
    return records


def build_t12_one_outside_payload() -> dict[str, object]:
    """Return the deterministic one-outside-label bootstrap/T12 packet."""

    row_pressure = build_t12_row_pressure_payload()
    records = _one_outside_records(row_pressure)

    rows_by_source: defaultdict[int, list[int]] = defaultdict(list)
    role_counts = Counter(role for record in records for role in record["roles"])
    support_label_counts: Counter[int] = Counter()
    support_mode_counts: Counter[str] = Counter()
    containment_counts: Counter[int] = Counter()
    for record in records:
        source_id = int(record["source_record_id"])
        row_center = int(record["row_center"])
        rows_by_source[source_id].append(row_center)
        for option in record["support_options"]:
            support_label_counts[int(option["support_label"])] += 1
            support_mode = str(option["support_label_mode"])
            support_mode_counts[support_mode] += 1
            containment_counts[int(option["private_halo_containment_count"])] += 1

    multirow_support_labels = [
        label for label, count in sorted(support_label_counts.items()) if count > 1
    ]

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This packet isolates fixed selected-row one-outside-label gaps; it does not prove the rows are forced.",
            "A singleton outside support is activation bookkeeping, not a Euclidean rich-class certificate.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "source_record_ids": sorted(rows_by_source),
            "one_outside_row_record_count": len(records),
            "row_centers_by_source_id": {
                str(source_id): centers for source_id, centers in sorted(rows_by_source.items())
            },
            "support_option_count": sum(int(record["support_option_count"]) for record in records),
            "support_label_counts": _json_counter(support_label_counts),
            "multirow_support_labels": multirow_support_labels,
            "support_label_mode_counts": _json_counter(support_mode_counts),
            "private_halo_containment_count_distribution": _json_counter(containment_counts),
            "row_center_private_in_all_deletions_count": sum(
                1 for record in records if record["row_center_private_in_all_deletion_closures"]
            ),
            "ledger_private_pair_support_hit_count": sum(
                int(record["ledger_private_pair_support_hit_count"]) for record in records
            ),
            "role_counts": _json_counter(role_counts),
            "activation_deficit_counts": {"1": len(records)},
            "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
            "next_bridge_question": (
                "Can a future bridge force a private row center together with "
                "one of its singleton outside supports from genuine rich-class "
                "geometry?"
            ),
        },
        "records": records,
        "source_artifacts": [
            {
                "path": "data/certificates/bootstrap_t12_row_pressure.json",
                "role": "source row-pressure records and singleton outside-label supports",
                "schema": row_pressure.get("schema"),
                "status": row_pressure.get("status"),
                "trust": row_pressure.get("trust"),
            }
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_one_outside.py",
            "command": "python scripts/check_bootstrap_t12_one_outside.py --write --assert-expected",
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts for the one-outside-label packet."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected bootstrap/T12 one-outside schema")
    if payload.get("status") != STATUS:
        raise AssertionError("unexpected bootstrap/T12 one-outside status")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "source_record_ids": [81, 151],
        "one_outside_row_record_count": 3,
        "row_centers_by_source_id": {"81": [8], "151": [5, 8]},
        "support_option_count": 6,
        "support_label_counts": {"5": 2, "6": 1, "7": 2, "8": 1},
        "multirow_support_labels": [5, 7],
        "support_label_mode_counts": {
            CLOSURE_INTERNAL_MODE: 3,
            PRIVATE_ALL_MODE: 3,
        },
        "private_halo_containment_count_distribution": {"3": 3, "4": 3},
        "row_center_private_in_all_deletions_count": 3,
        "ledger_private_pair_support_hit_count": 0,
        "role_counts": {"equality_connector_row": 3, "strict_edge_row": 1},
        "activation_deficit_counts": {"1": 3},
        "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary {key} is {summary.get(key)!r}, expected {expected!r}")

    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("records must be a list")
    expected_records = {
        (81, 8): {
            "classification_assignment_id": "A082",
            "roles": ["equality_connector_row"],
            "witnesses": [0, 2, 5, 6],
            "bootstrap_core_witnesses": [0, 2],
            "outside_witnesses": [5, 6],
            "support_labels": [5, 6],
            "support_modes": [PRIVATE_ALL_MODE, CLOSURE_INTERNAL_MODE],
        },
        (151, 5): {
            "classification_assignment_id": "A152",
            "roles": ["equality_connector_row"],
            "witnesses": [2, 4, 7, 8],
            "bootstrap_core_witnesses": [2, 4],
            "outside_witnesses": [7, 8],
            "support_labels": [7, 8],
            "support_modes": [CLOSURE_INTERNAL_MODE, PRIVATE_ALL_MODE],
        },
        (151, 8): {
            "classification_assignment_id": "A152",
            "roles": ["strict_edge_row", "equality_connector_row"],
            "witnesses": [1, 2, 5, 7],
            "bootstrap_core_witnesses": [1, 2],
            "outside_witnesses": [5, 7],
            "support_labels": [5, 7],
            "support_modes": [PRIVATE_ALL_MODE, CLOSURE_INTERNAL_MODE],
        },
    }
    by_key = {
        (int(record["source_record_id"]), int(record["row_center"])): record
        for record in records
    }
    if set(by_key) != set(expected_records):
        raise AssertionError("unexpected one-outside record keys")
    for key, expected in expected_records.items():
        record = by_key[key]
        for field in (
            "classification_assignment_id",
            "roles",
            "witnesses",
            "bootstrap_core_witnesses",
            "outside_witnesses",
        ):
            if record.get(field) != expected[field]:
                raise AssertionError(
                    f"one-outside {key} {field} is {record.get(field)!r}, "
                    f"expected {expected[field]!r}"
                )
        if record.get("pressure_class") != PRESSURE_CLASS:
            raise AssertionError(f"one-outside {key} pressure class changed")
        if record.get("activation_deficit_from_bootstrap_core") != 1:
            raise AssertionError(f"one-outside {key} activation deficit changed")
        if not record.get("row_center_private_in_all_deletion_closures"):
            raise AssertionError(f"one-outside {key} row center is no longer private")

        support_options = record.get("support_options")
        if not isinstance(support_options, list):
            raise AssertionError(f"one-outside {key} support_options must be a list")
        labels = [int(option["support_label"]) for option in support_options]
        modes = [str(option["support_label_mode"]) for option in support_options]
        if labels != expected["support_labels"]:
            raise AssertionError(f"one-outside {key} support labels changed")
        if modes != expected["support_modes"]:
            raise AssertionError(f"one-outside {key} support modes changed")
        for option in support_options:
            if not option["activation_ready_with_support"]:
                raise AssertionError(f"one-outside {key} support is not activation-ready")
            if option["ledger_private_pair_hit"]:
                raise AssertionError(f"one-outside {key} unexpectedly has pair-ledger hit")
