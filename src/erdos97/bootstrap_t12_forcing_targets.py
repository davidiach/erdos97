"""T12 forcing-target diagnostic for tight bootstrap-core rows.

This module is proof-mining bookkeeping only.  It refines the
bootstrap-core / vertex-circle overlay by recording exactly which T12/F16
strict-cycle rows and pair contacts are not already supplied by the bootstrap
core or by direct private-pair hits.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_vertex_circle_overlay import build_overlay_payload


SCHEMA = "erdos97.bootstrap_t12_forcing_targets.v1"
STATUS = "BOOTSTRAP_T12_FORCING_TARGET_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Second-pass diagnostic on the two tight n=9 bootstrap-core rows that "
    "land on the review-pending T12/F16 vertex-circle strict-cycle template; "
    "records row-center and private-pair forcing targets only, not a proof of "
    "n=9, not a proof of the bridge, not a counterexample, and not a global "
    "status update."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = REPO_ROOT / "data" / "certificates" / "bootstrap_t12_forcing_targets.json"

TARGET_TEMPLATE_ID = "T12"
TARGET_FAMILY_ID = "F16"
EXPECTED_BOOTSTRAP_CORE = [0, 1, 2, 4]


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _pair(values: Sequence[Any]) -> tuple[int, int]:
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


def _unique_cycle_pairs(
    cycle_pair_entries: Sequence[Mapping[str, Any]],
) -> list[dict[str, object]]:
    """Return first-seen unique cycle pairs with all recorded roles attached."""

    first_seen: dict[tuple[int, int], dict[str, object]] = {}
    roles_by_pair: defaultdict[tuple[int, int], list[str]] = defaultdict(list)
    rows_by_pair: defaultdict[tuple[int, int], set[int]] = defaultdict(set)
    steps_by_pair: defaultdict[tuple[int, int], set[int]] = defaultdict(set)

    for entry in cycle_pair_entries:
        pair = _pair(entry["pair"])
        location = str(entry["location"])
        role = str(entry["role"])
        if pair not in first_seen:
            first_seen[pair] = {
                "pair": list(pair),
                "location": location,
            }
        roles_by_pair[pair].append(role)
        if "row" in entry:
            rows_by_pair[pair].add(int(entry["row"]))
        if "step_index" in entry:
            steps_by_pair[pair].add(int(entry["step_index"]))

    out = []
    for pair, record in first_seen.items():
        enriched = dict(record)
        enriched["roles"] = sorted(set(roles_by_pair[pair]))
        enriched["rows"] = sorted(rows_by_pair[pair])
        enriched["steps"] = sorted(steps_by_pair[pair])
        out.append(enriched)
    return out


def _private_pair_records(
    deletion_closures: Sequence[Mapping[str, Any]],
) -> list[dict[str, object]]:
    out = []
    for closure in deletion_closures:
        core_vertex = int(closure["core_vertex"])
        for pair in closure["private_pairs"]:
            out.append({"pair": _pair_json(pair), "core_vertex": core_vertex})
    return sorted(out, key=lambda item: (item["pair"], item["core_vertex"]))


def _private_halo_labels(
    deletion_closures: Sequence[Mapping[str, Any]],
) -> list[int]:
    labels: set[int] = set()
    for closure in deletion_closures:
        labels.update(_int_list(closure["private_halo"]))
    return sorted(labels)


def _cycle_outside_labels(
    unique_cycle_pairs: Sequence[Mapping[str, object]],
    bootstrap_core: set[int],
) -> list[int]:
    labels: set[int] = set()
    for pair_record in unique_cycle_pairs:
        for label in _int_list(pair_record["pair"]):
            if label not in bootstrap_core:
                labels.add(label)
    return sorted(labels)


def _private_pair_hits(
    unique_cycle_pairs: Sequence[Mapping[str, object]],
    private_pairs: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    private_core_vertices: defaultdict[tuple[int, int], set[int]] = defaultdict(set)
    for record in private_pairs:
        private_core_vertices[_pair(record["pair"])].add(int(record["core_vertex"]))

    hits = []
    for pair_record in unique_cycle_pairs:
        pair = _pair(pair_record["pair"])
        core_vertices = sorted(private_core_vertices.get(pair, set()))
        if core_vertices:
            hits.append(
                {
                    "pair": list(pair),
                    "location": str(pair_record["location"]),
                    "private_core_vertices": core_vertices,
                }
            )
    return hits


def _row_gap_records(
    vertex_circle: Mapping[str, Any],
    bootstrap_core: set[int],
) -> list[dict[str, object]]:
    strict_rows = set(_int_list(vertex_circle["strict_edge_rows"]))
    connector_rows = set(_int_list(vertex_circle["equality_connector_rows"]))
    local_rows = {
        int(row["center"]): _int_list(row["witnesses"])
        for row in vertex_circle["local_core_rows"]
    }
    gap_rows = sorted(set(_int_list(vertex_circle["cycle_row_centers"])) - bootstrap_core)
    out = []
    for center in gap_rows:
        roles = []
        if center in strict_rows:
            roles.append("strict_edge_row")
        if center in connector_rows:
            roles.append("equality_connector_row")
        out.append(
            {
                "center": center,
                "roles": roles,
                "witnesses": local_rows[center],
            }
        )
    return out


def _target_record(overlay_record: Mapping[str, Any]) -> dict[str, object]:
    source_id = int(overlay_record["source_record_id"])
    bootstrap_core = _int_list(overlay_record["bootstrap_core"])
    bootstrap_core_set = set(bootstrap_core)
    vertex_circle = overlay_record["vertex_circle"]
    if vertex_circle["template_id"] != TARGET_TEMPLATE_ID:
        raise AssertionError(f"source {source_id} is not a T12 record")
    if vertex_circle["family_id"] != TARGET_FAMILY_ID:
        raise AssertionError(f"source {source_id} is not an F16 record")

    unique_pairs = _unique_cycle_pairs(vertex_circle["cycle_pair_entries"])
    private_pairs = _private_pair_records(overlay_record["deletion_closures"])
    private_hits = _private_pair_hits(unique_pairs, private_pairs)
    row_gaps = _row_gap_records(vertex_circle, bootstrap_core_set)
    row_gap_centers = [int(record["center"]) for record in row_gaps]
    row_gap_role_counts = Counter(
        role for record in row_gaps for role in record["roles"]
    )
    unique_pair_location_counts = Counter(
        str(record["location"]) for record in unique_pairs
    )
    private_labels = _private_halo_labels(overlay_record["deletion_closures"])
    cycle_outside = _cycle_outside_labels(unique_pairs, bootstrap_core_set)

    return {
        "source_record_id": source_id,
        "classification_assignment_id": overlay_record["classification_assignment_id"],
        "template_id": TARGET_TEMPLATE_ID,
        "family_id": TARGET_FAMILY_ID,
        "cycle_length": int(vertex_circle["cycle_length"]),
        "bootstrap_core": bootstrap_core,
        "capacity_margin": int(overlay_record["bootstrap_capacity"]["capacity_margin"]),
        "outside": _int_list(overlay_record["bootstrap_capacity"]["outside"]),
        "cycle_row_centers": _int_list(vertex_circle["cycle_row_centers"]),
        "row_gap_centers": row_gap_centers,
        "row_gap_count": len(row_gap_centers),
        "row_gap_role_counts": _json_counter(row_gap_role_counts),
        "row_gaps": row_gaps,
        "strict_edge_rows_subset_of_bootstrap_core": bool(
            vertex_circle["strict_edge_rows_subset_of_bootstrap_core"]
        ),
        "equality_connector_rows_subset_of_bootstrap_core": bool(
            vertex_circle["equality_connector_rows_subset_of_bootstrap_core"]
        ),
        "unique_cycle_pairs": unique_pairs,
        "unique_cycle_pair_location_counts": _json_counter(unique_pair_location_counts),
        "cycle_outside_labels": cycle_outside,
        "private_halo_labels": private_labels,
        "cycle_outside_labels_in_private_halos": sorted(
            set(cycle_outside) & set(private_labels)
        ),
        "private_pair_hits": private_hits,
        "private_pair_hit_count": len(private_hits),
        "private_pair_hit_pairs": [hit["pair"] for hit in private_hits],
        "private_pair_records": private_pairs,
        "diagnosis": {
            "core_only_target_status": "BLOCKED_BY_ROW_GAPS",
            "private_pair_only_target_status": (
                "NO_DIRECT_HITS"
                if not private_hits
                else "PARTIAL_DIRECT_HITS_ONLY"
            ),
            "recommended_next_target": (
                "Prove a row-center or equality-connector forcing condition "
                "that supplies the missing T12/F16 local rows from the "
                "bootstrap-core/private-halo geometry."
            ),
        },
    }


def build_t12_forcing_targets_payload() -> dict[str, object]:
    """Return the deterministic T12 forcing-target diagnostic payload."""

    overlay = build_overlay_payload()
    records = [
        _target_record(record)
        for record in overlay["records"]
        if record["vertex_circle"]["template_id"] == TARGET_TEMPLATE_ID
        and record["vertex_circle"]["family_id"] == TARGET_FAMILY_ID
    ]
    records.sort(key=lambda record: int(record["source_record_id"]))
    if any(record["bootstrap_core"] != EXPECTED_BOOTSTRAP_CORE for record in records):
        raise AssertionError("T12 forcing-target records no longer share the expected bootstrap core")

    template_counts = Counter(str(record["template_id"]) for record in records)
    family_counts = Counter(str(record["family_id"]) for record in records)
    row_gap_counts = {
        str(record["source_record_id"]): int(record["row_gap_count"])
        for record in records
    }
    private_hit_counts = {
        str(record["source_record_id"]): int(record["private_pair_hit_count"])
        for record in records
    }
    zero_private_hit_sources = [
        int(record["source_record_id"])
        for record in records
        if int(record["private_pair_hit_count"]) == 0
    ]

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This is a proof-mining target ledger, not a proof of the bridge.",
            "The input overlay is fixed selected-row data, not full geometric rich-class data.",
            "Direct private-pair hits are diagnostic contacts, not Euclidean realizability evidence.",
            "No general proof and no counterexample are claimed.",
        ],
        "summary": {
            "target_count": len(records),
            "source_record_ids": [int(record["source_record_id"]) for record in records],
            "classification_assignment_ids": [
                str(record["classification_assignment_id"]) for record in records
            ],
            "template_counts": _json_counter(template_counts),
            "family_counts": _json_counter(family_counts),
            "bootstrap_core": EXPECTED_BOOTSTRAP_CORE,
            "capacity_margins_by_source_id": {
                str(record["source_record_id"]): int(record["capacity_margin"])
                for record in records
            },
            "row_gap_counts_by_source_id": row_gap_counts,
            "row_gap_centers_by_source_id": {
                str(record["source_record_id"]): record["row_gap_centers"]
                for record in records
            },
            "private_pair_hit_counts_by_source_id": private_hit_counts,
            "zero_private_pair_hit_source_ids": zero_private_hit_sources,
            "all_records_have_row_gaps": all(
                int(record["row_gap_count"]) > 0 for record in records
            ),
            "all_records_have_direct_private_pair_hits": all(
                int(record["private_pair_hit_count"]) > 0 for record in records
            ),
            "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
            "primary_next_target": (
                "bootstrap core [0,1,2,4] plus tight private-halo geometry "
                "should force the missing T12/F16 row centers or equivalent "
                "equality connectors"
            ),
        },
        "records": records,
        "source_artifacts": [
            {
                "path": "data/certificates/bootstrap_vertex_circle_overlay.json",
                "role": "source overlay joining tight bootstrap rows to T12/F16",
                "schema": overlay.get("schema"),
                "status": overlay.get("status"),
                "trust": overlay.get("trust"),
            }
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_forcing_targets.py",
            "command": (
                "python scripts/check_bootstrap_t12_forcing_targets.py "
                "--write --assert-expected"
            ),
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts for the T12 forcing-target diagnostic."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected bootstrap/T12 forcing-target schema")
    if payload.get("status") != STATUS:
        raise AssertionError("unexpected bootstrap/T12 forcing-target status")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "target_count": 2,
        "source_record_ids": [81, 151],
        "classification_assignment_ids": ["A082", "A152"],
        "template_counts": {"T12": 2},
        "family_counts": {"F16": 2},
        "bootstrap_core": [0, 1, 2, 4],
        "capacity_margins_by_source_id": {"81": 8, "151": 6},
        "row_gap_counts_by_source_id": {"81": 2, "151": 4},
        "row_gap_centers_by_source_id": {"81": [3, 8], "151": [5, 6, 7, 8]},
        "private_pair_hit_counts_by_source_id": {"81": 0, "151": 2},
        "zero_private_pair_hit_source_ids": [81],
        "all_records_have_row_gaps": True,
        "all_records_have_direct_private_pair_hits": False,
        "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary {key} is {summary.get(key)!r}, expected {expected!r}")

    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("records must be a list")
    expected_records = {
        81: {
            "row_gap_centers": [3, 8],
            "row_gap_role_counts": {"equality_connector_row": 2},
            "unique_cycle_pair_location_counts": {"core_core": 2, "core_outside": 5},
            "cycle_outside_labels": [3, 7, 8],
            "cycle_outside_labels_in_private_halos": [3, 7, 8],
            "private_pair_hit_pairs": [],
        },
        151: {
            "row_gap_centers": [5, 6, 7, 8],
            "row_gap_role_counts": {
                "equality_connector_row": 3,
                "strict_edge_row": 2,
            },
            "unique_cycle_pair_location_counts": {
                "core_core": 1,
                "core_outside": 3,
                "outside_outside": 3,
            },
            "cycle_outside_labels": [5, 6, 7, 8],
            "cycle_outside_labels_in_private_halos": [5, 6, 7, 8],
            "private_pair_hit_pairs": [[5, 8], [6, 8]],
        },
    }
    by_source = {int(record["source_record_id"]): record for record in records}
    if set(by_source) != set(expected_records):
        raise AssertionError("unexpected source-record ids")
    for source_id, expected in expected_records.items():
        record = by_source[source_id]
        for key, value in expected.items():
            if record.get(key) != value:
                raise AssertionError(f"{source_id} {key} is {record.get(key)!r}, expected {value!r}")
        if record["template_id"] != TARGET_TEMPLATE_ID or record["family_id"] != TARGET_FAMILY_ID:
            raise AssertionError(f"{source_id} template/family changed")
