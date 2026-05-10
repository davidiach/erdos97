"""Bootstrap-core / vertex-circle overlay for tight n=9 bridge targets.

This module joins the singleton-rich bootstrap-core crosswalk to the
review-pending n=9 vertex-circle strict-cycle certificate chain.  It is
diagnostic bookkeeping only: it does not prove Erdos Problem #97, does not
promote the n=9 checker, and does not claim a counterexample.
"""

from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA = "erdos97.bootstrap_vertex_circle_overlay.v1"
STATUS = "BOOTSTRAP_VERTEX_CIRCLE_OVERLAY_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Overlay of the two non-ear-orderable n=9 bootstrap-core frontier "
    "assignments with the review-pending vertex-circle strict-cycle chain; "
    "not a proof of n=9, not a proof of the bridge, not a counterexample, "
    "and not a global status update."
)
REPO_ROOT = Path(__file__).resolve().parents[2]

BOOTSTRAP_CROSSWALK_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "bootstrap_core_crosswalk.json"
)
BRIDGE_FRONTIER_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "bridge_lemma_frontier.json"
)
FRONTIER_CLASSIFICATION_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "n9_vertex_circle_frontier_motif_classification.json"
)
STRICT_CYCLE_PATH_JOIN_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "n9_vertex_circle_strict_cycle_path_join.json"
)
STRICT_CYCLE_TEMPLATE_PACKET_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "n9_vertex_circle_strict_cycle_template_packet.json"
)

TARGET_SOURCE_RECORD_IDS = (81, 151)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _pair(values: Sequence[Any]) -> tuple[int, int]:
    a, b = int(values[0]), int(values[1])
    if a == b:
        raise ValueError("pair endpoints must be distinct")
    return tuple(sorted((a, b)))


def _pair_json(values: Sequence[Any]) -> list[int]:
    return list(_pair(values))


def _pair_location(values: Sequence[Any], core: set[int]) -> str:
    hits = sum(1 for value in _pair(values) if value in core)
    if hits == 2:
        return "core_core"
    if hits == 1:
        return "core_outside"
    return "outside_outside"


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _row_signature(rows: Sequence[Sequence[Any]]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(sorted(int(label) for label in row)) for row in rows)


def _witness_rows_from_compact_rows(
    compact_rows: Sequence[Sequence[Any]],
) -> list[list[int]]:
    rows: list[list[int] | None] = [None] * len(compact_rows)
    for raw_row in compact_rows:
        row = _int_list(raw_row)
        if len(row) != 5:
            raise ValueError("compact selected rows must have center plus four witnesses")
        center = row[0]
        if center < 0 or center >= len(compact_rows):
            raise ValueError(f"compact row has out-of-range center {center}")
        if rows[center] is not None:
            raise ValueError(f"duplicate compact row for center {center}")
        rows[center] = sorted(row[1:])
    if any(row is None for row in rows):
        raise ValueError("compact selected rows are missing at least one center")
    return [row for row in rows if row is not None]


def _local_core_rows(compact_rows: Sequence[Sequence[Any]]) -> list[dict[str, object]]:
    out = []
    for raw_row in compact_rows:
        row = _int_list(raw_row)
        out.append({"center": row[0], "witnesses": sorted(row[1:])})
    return sorted(out, key=lambda item: int(item["center"]))


def _source_payloads() -> dict[str, dict[str, Any]]:
    return {
        "bootstrap_crosswalk": _load_json(BOOTSTRAP_CROSSWALK_ARTIFACT),
        "bridge_frontier": _load_json(BRIDGE_FRONTIER_ARTIFACT),
        "frontier_classification": _load_json(FRONTIER_CLASSIFICATION_ARTIFACT),
        "strict_cycle_path_join": _load_json(STRICT_CYCLE_PATH_JOIN_ARTIFACT),
        "strict_cycle_template_packet": _load_json(STRICT_CYCLE_TEMPLATE_PACKET_ARTIFACT),
    }


def _target_bridge_records(bridge_payload: Mapping[str, Any]) -> dict[int, dict[str, Any]]:
    targets = bridge_payload.get("proof_mining_targets")
    if not isinstance(targets, list):
        raise ValueError("bridge frontier artifact must contain proof_mining_targets")
    by_id: dict[int, dict[str, Any]] = {}
    for target in targets:
        if not isinstance(target, dict) or int(target.get("n", -1)) != 9:
            continue
        source_record_id = target.get("source_record_id")
        if not isinstance(source_record_id, int):
            continue
        if source_record_id in TARGET_SOURCE_RECORD_IDS:
            by_id[source_record_id] = target
    missing = [record_id for record_id in TARGET_SOURCE_RECORD_IDS if record_id not in by_id]
    if missing:
        raise AssertionError(f"missing bridge-frontier target records {missing}")
    return by_id


def _crosswalk_records(crosswalk_payload: Mapping[str, Any]) -> dict[int, dict[str, Any]]:
    records = crosswalk_payload.get("records")
    if not isinstance(records, list):
        raise ValueError("bootstrap crosswalk artifact must contain records")
    out: dict[int, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        source_record_id = record.get("source_record_id")
        if isinstance(source_record_id, int) and source_record_id in TARGET_SOURCE_RECORD_IDS:
            out[source_record_id] = record
    missing = [record_id for record_id in TARGET_SOURCE_RECORD_IDS if record_id not in out]
    if missing:
        raise AssertionError(f"missing bootstrap-crosswalk records {missing}")
    return out


def _classification_by_signature(
    classification_payload: Mapping[str, Any],
) -> dict[tuple[tuple[int, ...], ...], dict[str, Any]]:
    assignments = classification_payload.get("assignments")
    if not isinstance(assignments, list):
        raise ValueError("classification artifact must contain assignments")
    out: dict[tuple[tuple[int, ...], ...], dict[str, Any]] = {}
    for assignment in assignments:
        if not isinstance(assignment, dict):
            continue
        selected_rows = assignment.get("selected_rows")
        if not isinstance(selected_rows, list):
            continue
        signature = _row_signature(_witness_rows_from_compact_rows(selected_rows))
        if signature in out:
            raise AssertionError("duplicate selected-row signature in classification artifact")
        out[signature] = assignment
    return out


def _strict_cycle_records_by_assignment_id(
    path_join_payload: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    records = path_join_payload.get("records")
    if not isinstance(records, list):
        raise ValueError("strict-cycle path join must contain records")
    out: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        if record.get("status") != "strict_cycle":
            continue
        assignment_id = str(record["assignment_id"])
        if assignment_id in out:
            raise AssertionError(f"duplicate strict-cycle assignment id {assignment_id}")
        out[assignment_id] = record
    return out


def _deletion_closure_summaries(
    bootstrap_record: Mapping[str, Any],
) -> list[dict[str, object]]:
    audit = bootstrap_record["bootstrap_core_audit"]
    if not isinstance(audit, dict):
        raise AssertionError("bootstrap_core_audit must be a mapping")
    deletion_closures = audit["deletion_closures"]
    if not isinstance(deletion_closures, list):
        raise AssertionError("bootstrap deletion closures must be a list")

    summaries = []
    for deletion in deletion_closures:
        if not isinstance(deletion, dict):
            raise AssertionError("deletion closure must be a mapping")
        rich_slices = deletion.get("rich_class_private_slices")
        if not isinstance(rich_slices, list):
            raise AssertionError("deletion closure must contain rich slices")
        private_pairs: list[list[int]] = []
        private_witnesses_by_class = []
        for rich_slice in rich_slices:
            if not isinstance(rich_slice, dict):
                raise AssertionError("rich slice must be a mapping")
            private_witnesses = sorted(_int_list(rich_slice["private_halo_witnesses"]))
            private_pairs.extend(
                [list(pair) for pair in combinations(private_witnesses, 2)]
            )
            private_witnesses_by_class.append(
                {
                    "rich_class_index": int(rich_slice["rich_class_index"]),
                    "private_halo_witnesses": private_witnesses,
                    "private_pair_count": int(rich_slice["private_pair_count"]),
                }
            )
        summaries.append(
            {
                "core_vertex": int(deletion["core_vertex"]),
                "deletion_seed": _int_list(deletion["deletion_seed"]),
                "closure_size": int(deletion["closure_size"]),
                "private_halo": _int_list(deletion["private_halo"]),
                "private_halo_size": int(deletion["private_halo_size"]),
                "private_pair_count": int(deletion["private_pair_count"]),
                "private_pairs": sorted(private_pairs),
                "private_witnesses_by_rich_class": private_witnesses_by_class,
            }
        )
    return summaries


def _cycle_pair_entries(
    strict_cycle_record: Mapping[str, Any],
    bootstrap_core: Sequence[int],
) -> list[dict[str, object]]:
    core = set(int(label) for label in bootstrap_core)
    entries: list[dict[str, object]] = []
    steps = strict_cycle_record["cycle_steps"]
    if not isinstance(steps, list):
        raise AssertionError("strict-cycle record must contain cycle_steps")

    for step_index, step in enumerate(steps):
        edge = step["strict_inequality"]
        equality = step["equality_to_next_outer_pair"]
        for role, pair_values in (
            ("strict_outer_pair", edge["outer_pair"]),
            ("strict_inner_pair", edge["inner_pair"]),
            ("connector_start_pair", equality["start_pair"]),
            ("connector_end_pair", equality["end_pair"]),
        ):
            entries.append(
                {
                    "step_index": step_index,
                    "role": role,
                    "pair": _pair_json(pair_values),
                    "location": _pair_location(pair_values, core),
                }
            )
        path = equality["path"]
        if not isinstance(path, list):
            raise AssertionError("equality connector path must be a list")
        for path_index, link in enumerate(path):
            entries.append(
                {
                    "step_index": step_index,
                    "path_index": path_index,
                    "role": "connector_path_next_pair",
                    "row": int(link["row"]),
                    "pair": _pair_json(link["next_pair"]),
                    "location": _pair_location(link["next_pair"], core),
                }
            )
    return entries


def _cycle_overlay(
    strict_cycle_record: Mapping[str, Any],
    bootstrap_core: Sequence[int],
) -> dict[str, object]:
    core_set = {int(label) for label in bootstrap_core}
    steps = strict_cycle_record["cycle_steps"]
    if not isinstance(steps, list):
        raise AssertionError("strict-cycle record must contain cycle_steps")

    local_core_rows = _local_core_rows(strict_cycle_record["core_selected_rows"])
    local_core_centers = sorted(int(row["center"]) for row in local_core_rows)
    strict_edge_rows = [
        int(step["strict_inequality"]["row"])
        for step in steps
    ]
    connector_rows = [
        int(link["row"])
        for step in steps
        for link in step["equality_to_next_outer_pair"]["path"]
    ]
    cycle_row_centers = sorted(set(strict_edge_rows) | set(connector_rows))
    if cycle_row_centers != local_core_centers:
        raise AssertionError("cycle rows and compact local-core rows diverge")

    pair_entries = _cycle_pair_entries(strict_cycle_record, bootstrap_core)
    pair_location_counts = Counter(str(entry["location"]) for entry in pair_entries)
    unique_pair_locations = {
        tuple(entry["pair"]): str(entry["location"])
        for entry in pair_entries
    }
    unique_pair_location_counts = Counter(unique_pair_locations.values())

    row_centers_in_core = sorted(set(cycle_row_centers) & core_set)
    row_centers_outside_core = sorted(set(cycle_row_centers) - core_set)
    strict_edge_rows_outside_core = sorted(set(strict_edge_rows) - core_set)
    connector_rows_outside_core = sorted(set(connector_rows) - core_set)

    return {
        "assignment_id": strict_cycle_record["assignment_id"],
        "status": strict_cycle_record["status"],
        "template_id": strict_cycle_record["template_id"],
        "family_id": strict_cycle_record["family_id"],
        "cycle_length": int(strict_cycle_record["cycle_length"]),
        "core_size": int(strict_cycle_record["core_size"]),
        "strict_edge_count": int(strict_cycle_record["strict_edge_count"]),
        "connector_path_lengths": _int_list(strict_cycle_record["connector_path_lengths"]),
        "span_signature": strict_cycle_record["span_signature"],
        "local_core_rows": local_core_rows,
        "strict_edge_rows": strict_edge_rows,
        "equality_connector_rows": connector_rows,
        "cycle_row_centers": cycle_row_centers,
        "cycle_row_centers_in_bootstrap_core": row_centers_in_core,
        "cycle_row_centers_outside_bootstrap_core": row_centers_outside_core,
        "strict_edge_rows_outside_bootstrap_core": strict_edge_rows_outside_core,
        "equality_connector_rows_outside_bootstrap_core": connector_rows_outside_core,
        "cycle_rows_subset_of_bootstrap_core": not row_centers_outside_core,
        "strict_edge_rows_subset_of_bootstrap_core": not strict_edge_rows_outside_core,
        "equality_connector_rows_subset_of_bootstrap_core": not connector_rows_outside_core,
        "cycle_pair_location_counts": _json_counter(pair_location_counts),
        "unique_cycle_pair_location_counts": _json_counter(unique_pair_location_counts),
        "cycle_pair_entries": pair_entries,
        "cycle_steps": strict_cycle_record["cycle_steps"],
    }


def _template_summary(template_packet_payload: Mapping[str, Any], template_id: str) -> dict[str, Any]:
    templates = template_packet_payload.get("templates")
    if not isinstance(templates, list):
        raise ValueError("strict-cycle template packet must contain templates")
    matches = [
        template
        for template in templates
        if isinstance(template, dict) and str(template.get("template_id")) == template_id
    ]
    if len(matches) != 1:
        raise AssertionError(f"expected exactly one template summary for {template_id}")
    template = matches[0]
    return {
        "template_id": template["template_id"],
        "status": template["status"],
        "family_count": template["family_count"],
        "assignment_count": template["assignment_count"],
        "cycle_length": template["cycle_length"],
        "cycle_span_counts": template["cycle_span_counts"],
        "families": template["families"],
    }


def _overlay_record(
    *,
    source_record_id: int,
    bridge_record: Mapping[str, Any],
    bootstrap_record: Mapping[str, Any],
    classification_record: Mapping[str, Any],
    strict_cycle_record: Mapping[str, Any],
    template_packet_payload: Mapping[str, Any],
) -> dict[str, object]:
    audit = bootstrap_record["bootstrap_core_audit"]
    if not isinstance(audit, dict):
        raise AssertionError("bootstrap audit must be a mapping")
    bootstrap_core = _int_list(audit["core"])
    cycle = _cycle_overlay(strict_cycle_record, bootstrap_core)
    return {
        "target_id": bridge_record["target_id"],
        "source_record_id": source_record_id,
        "source_assignment_index": source_record_id,
        "classification_assignment_id": classification_record["assignment_id"],
        "assignment_join_method": "selected_row_signature",
        "crosswalk_case_id": bootstrap_record["case_id"],
        "n": int(bridge_record["n"]),
        "selected_rows": bridge_record["selected_rows"],
        "circulant_offsets": bridge_record.get("circulant_offsets"),
        "ear_order": bridge_record["ear_order"],
        "bootstrap_core": bootstrap_core,
        "bootstrap_minimum_rank": int(bootstrap_record["minimum_generator"]["minimum_rank"]),
        "bootstrap_capacity": {
            "private_pair_count": int(audit["private_pair_count"]),
            "cyclic_capacity_sum": int(audit["cyclic_capacity_sum"]),
            "capacity_margin": int(audit["capacity_margin"]),
            "outside": _int_list(audit["outside"]),
            "outside_run_lengths": _int_list(audit["outside_run_lengths"]),
        },
        "deletion_closures": _deletion_closure_summaries(bootstrap_record),
        "vertex_circle": cycle,
        "template_packet_summary": _template_summary(
            template_packet_payload,
            str(cycle["template_id"]),
        ),
        "interpretation": (
            "The selected-row stuck/bootstrap core and the vertex-circle "
            "strict cycle coexist in this fixed assignment, but the strict "
            "cycle is not a bootstrap-core-only contradiction."
        ),
    }


def build_overlay_payload() -> dict[str, object]:
    """Return the deterministic bootstrap/vertex-circle overlay payload."""

    sources = _source_payloads()
    bridge_records = _target_bridge_records(sources["bridge_frontier"])
    crosswalk_records = _crosswalk_records(sources["bootstrap_crosswalk"])
    classification_by_signature = _classification_by_signature(
        sources["frontier_classification"]
    )
    strict_records_by_id = _strict_cycle_records_by_assignment_id(
        sources["strict_cycle_path_join"]
    )

    records = []
    for source_record_id in TARGET_SOURCE_RECORD_IDS:
        bridge_record = bridge_records[source_record_id]
        selected_rows = bridge_record["selected_rows"]
        if not isinstance(selected_rows, list):
            raise AssertionError("bridge selected rows must be a list")
        signature = _row_signature(selected_rows)
        classification_record = classification_by_signature.get(signature)
        if classification_record is None:
            raise AssertionError(
                f"no vertex-circle classification row matches target {source_record_id}"
            )
        strict_cycle_record = strict_records_by_id.get(
            str(classification_record["assignment_id"])
        )
        if strict_cycle_record is None:
            raise AssertionError(
                "no strict-cycle path-join row matches classification "
                f"{classification_record['assignment_id']}"
            )
        records.append(
            _overlay_record(
                source_record_id=source_record_id,
                bridge_record=bridge_record,
                bootstrap_record=crosswalk_records[source_record_id],
                classification_record=classification_record,
                strict_cycle_record=strict_cycle_record,
                template_packet_payload=sources["strict_cycle_template_packet"],
            )
        )

    template_counts = Counter(str(record["vertex_circle"]["template_id"]) for record in records)
    family_counts = Counter(str(record["vertex_circle"]["family_id"]) for record in records)
    cycle_length_counts = Counter(
        int(record["vertex_circle"]["cycle_length"]) for record in records
    )
    rank_counts = Counter(int(record["bootstrap_minimum_rank"]) for record in records)
    strict_edge_subset_count = sum(
        1
        for record in records
        if record["vertex_circle"]["strict_edge_rows_subset_of_bootstrap_core"]
    )
    connector_subset_count = sum(
        1
        for record in records
        if record["vertex_circle"]["equality_connector_rows_subset_of_bootstrap_core"]
    )
    cycle_row_subset_count = sum(
        1 for record in records if record["vertex_circle"]["cycle_rows_subset_of_bootstrap_core"]
    )
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This overlay joins existing review-pending diagnostics; it is not an independent n=9 proof.",
            "The bridge-frontier source indices and vertex-circle assignment ids are joined by selected-row signature.",
            "The strict-cycle rows are local selected-row cores, not full rich-class data.",
            "No general proof and no counterexample are claimed.",
        ],
        "summary": {
            "target_count": len(records),
            "source_assignment_indices": [int(record["source_record_id"]) for record in records],
            "classification_assignment_ids": [
                str(record["classification_assignment_id"]) for record in records
            ],
            "template_counts": _json_counter(template_counts),
            "family_counts": _json_counter(family_counts),
            "cycle_length_counts": _json_counter(cycle_length_counts),
            "bootstrap_minimum_rank_counts": _json_counter(rank_counts),
            "bootstrap_core": [0, 1, 2, 4],
            "capacity_margins_by_source_id": {
                str(record["source_record_id"]): int(
                    record["bootstrap_capacity"]["capacity_margin"]
                )
                for record in records
            },
            "cycle_rows_subset_of_bootstrap_core_count": cycle_row_subset_count,
            "strict_edge_rows_subset_of_bootstrap_core_count": strict_edge_subset_count,
            "equality_connector_rows_subset_of_bootstrap_core_count": connector_subset_count,
            "overlay_conclusion": "T12_STRICT_CYCLE_SHARED_BUT_NOT_BOOTSTRAP_CORE_ONLY",
        },
        "records": records,
        "source_artifacts": [
            {
                "path": "data/certificates/bootstrap_core_crosswalk.json",
                "role": "singleton-rich bootstrap-core rank/capacity records",
                "schema": sources["bootstrap_crosswalk"].get("schema"),
                "status": sources["bootstrap_crosswalk"].get("status"),
                "trust": sources["bootstrap_crosswalk"].get("trust"),
            },
            {
                "path": "data/certificates/bridge_lemma_frontier.json",
                "role": "bridge proof-mining target ids and selected rows",
                "schema": sources["bridge_frontier"].get("schema"),
                "status": sources["bridge_frontier"].get("status"),
                "trust": sources["bridge_frontier"].get("trust"),
            },
            {
                "path": "data/certificates/n9_vertex_circle_frontier_motif_classification.json",
                "role": "selected-row signature to vertex-circle assignment/template classification",
                "schema": sources["frontier_classification"].get("schema"),
                "status": sources["frontier_classification"].get("status"),
                "trust": sources["frontier_classification"].get("trust"),
            },
            {
                "path": "data/certificates/n9_vertex_circle_strict_cycle_path_join.json",
                "role": "strict-cycle equality connectors and vertex-circle strict edges",
                "schema": sources["strict_cycle_path_join"].get("schema"),
                "status": sources["strict_cycle_path_join"].get("status"),
                "trust": sources["strict_cycle_path_join"].get("trust"),
            },
            {
                "path": "data/certificates/n9_vertex_circle_strict_cycle_template_packet.json",
                "role": "strict-cycle template packet summaries",
                "schema": sources["strict_cycle_template_packet"].get("schema"),
                "status": sources["strict_cycle_template_packet"].get("status"),
                "trust": sources["strict_cycle_template_packet"].get("trust"),
            },
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_vertex_circle_overlay.py",
            "command": (
                "python scripts/check_bootstrap_vertex_circle_overlay.py "
                "--write --assert-expected"
            ),
        },
    }
    assert_expected_payload(payload)
    return payload


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts for the overlay artifact."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected bootstrap/vertex-circle overlay schema")
    if payload.get("status") != STATUS:
        raise AssertionError("unexpected bootstrap/vertex-circle overlay status")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "target_count": 2,
        "source_assignment_indices": [81, 151],
        "classification_assignment_ids": ["A082", "A152"],
        "template_counts": {"T12": 2},
        "family_counts": {"F16": 2},
        "cycle_length_counts": {"3": 2},
        "bootstrap_minimum_rank_counts": {"4": 2},
        "bootstrap_core": [0, 1, 2, 4],
        "capacity_margins_by_source_id": {"81": 8, "151": 6},
        "cycle_rows_subset_of_bootstrap_core_count": 0,
        "strict_edge_rows_subset_of_bootstrap_core_count": 1,
        "equality_connector_rows_subset_of_bootstrap_core_count": 0,
        "overlay_conclusion": "T12_STRICT_CYCLE_SHARED_BUT_NOT_BOOTSTRAP_CORE_ONLY",
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary {key} is {summary.get(key)!r}, expected {expected!r}")

    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("records must be a list")
    expected_records = {
        81: {
            "classification_assignment_id": "A082",
            "capacity_margin": 8,
            "cycle_row_centers": [0, 1, 2, 3, 4, 8],
            "cycle_row_centers_in_bootstrap_core": [0, 1, 2, 4],
            "cycle_row_centers_outside_bootstrap_core": [3, 8],
            "strict_edge_rows_subset_of_bootstrap_core": True,
            "equality_connector_rows_subset_of_bootstrap_core": False,
            "unique_cycle_pair_location_counts": {"core_core": 2, "core_outside": 5},
        },
        151: {
            "classification_assignment_id": "A152",
            "capacity_margin": 6,
            "cycle_row_centers": [0, 1, 5, 6, 7, 8],
            "cycle_row_centers_in_bootstrap_core": [0, 1],
            "cycle_row_centers_outside_bootstrap_core": [5, 6, 7, 8],
            "strict_edge_rows_subset_of_bootstrap_core": False,
            "equality_connector_rows_subset_of_bootstrap_core": False,
            "unique_cycle_pair_location_counts": {
                "core_core": 1,
                "core_outside": 3,
                "outside_outside": 3,
            },
        },
    }
    by_source_id = {int(record["source_record_id"]): record for record in records}
    if set(by_source_id) != set(expected_records):
        raise AssertionError("unexpected overlay source-record ids")
    for source_id, expected in expected_records.items():
        record = by_source_id[source_id]
        vertex_circle = record["vertex_circle"]
        if record["classification_assignment_id"] != expected["classification_assignment_id"]:
            raise AssertionError(f"{source_id} classification assignment id changed")
        if record["bootstrap_capacity"]["capacity_margin"] != expected["capacity_margin"]:
            raise AssertionError(f"{source_id} bootstrap capacity margin changed")
        for key in (
            "cycle_row_centers",
            "cycle_row_centers_in_bootstrap_core",
            "cycle_row_centers_outside_bootstrap_core",
            "strict_edge_rows_subset_of_bootstrap_core",
            "equality_connector_rows_subset_of_bootstrap_core",
            "unique_cycle_pair_location_counts",
        ):
            if vertex_circle[key] != expected[key]:
                raise AssertionError(f"{source_id} vertex-circle {key} changed")
        if vertex_circle["template_id"] != "T12" or vertex_circle["family_id"] != "F16":
            raise AssertionError(f"{source_id} strict-cycle template/family changed")
        if vertex_circle["cycle_length"] != 3:
            raise AssertionError(f"{source_id} strict-cycle length changed")
