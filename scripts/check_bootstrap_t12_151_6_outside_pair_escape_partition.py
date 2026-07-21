#!/usr/bin/env python3
"""Generate or check the bootstrap/T12 151:6 outside-pair escape partition."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from erdos97.json_io import write_json
from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]

SCHEMA = "erdos97.bootstrap_t12_151_6_outside_pair_escape_partition.v1"
STATUS = "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_ESCAPE_PARTITION_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "PRIVATE_HALO_ONLY_AND_ENDPOINT8_SURVIVORS_ALL_VERTEX_CIRCLE_OBSTRUCTED"
CLAIM_SCOPE = (
    "Proof-mining diagnostic partitioning the source-151 row-6 outside-pair "
    "full-neighborhood target rows by support-pair role. It shows that the "
    "private-halo-only connector-avoiding row family has 12 basic-filter "
    "complete assignments, while endpoint-8 connector-available row families "
    "have 16 basic-filter complete assignments, and that exact vertex-circle "
    "quotient replay kills all 28. This does not prove outside-pair support "
    "existence, does not prove row forcing, does not prove the private-halo-only "
    "pair is impossible, does not prove n=9, does not prove the bridge, is not "
    "a counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_bootstrap_t12_151_6_outside_pair_escape_partition.py",
    "command": (
        "python scripts/check_bootstrap_t12_151_6_outside_pair_escape_partition.py "
        "--write --assert-expected"
    ),
}

DEFAULT_SOURCE_FULL_NEIGHBORHOOD = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.json"
)
DEFAULT_SOURCE_CONNECTOR_CONTRACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_outside_pair_connector_contract.json"
)
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_outside_pair_escape_partition.json"
)

SOURCE_FULL_NEIGHBORHOOD_SCHEMA = (
    "erdos97.bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.v1"
)
SOURCE_FULL_NEIGHBORHOOD_STATUS = (
    "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_FULL_NEIGHBORHOOD_VERTEX_CIRCLE_"
    "DIAGNOSTIC_ONLY"
)
SOURCE_CONNECTOR_CONTRACT_SCHEMA = (
    "erdos97.bootstrap_t12_151_6_outside_pair_connector_contract.v1"
)
SOURCE_CONNECTOR_CONTRACT_STATUS = (
    "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_CONNECTOR_CONTRACT_DIAGNOSTIC_ONLY"
)
SOURCE_SCAN_STATUS = "FULL_NEIGHBORHOOD_BASIC_SURVIVORS_ALL_VERTEX_CIRCLE_OBSTRUCTED"

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "interpretation",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "summary",
    "target_row_partition",
    "trust",
    "validation_errors",
    "validation_status",
}
EXPECTED_TARGET_RECORD_KEYS = {
    "basic_filter_complete_assignment_count",
    "contains_endpoint8",
    "contains_private_halo_pair",
    "empty_domain_count",
    "non_original_target_basic_assignment_count",
    "partition",
    "search_node_count",
    "support_pair_roles_present",
    "support_pairs_present",
    "target_center_class",
    "target_center_class_is_original",
    "target_center_class_key",
    "vertex_circle_status_counts",
    "vertex_circle_surviving_assignment_count",
}
PARTITION_ORDER = [
    "private_halo_only_connector_avoiding",
    "endpoint8_connector_available",
    "mixed_private_and_endpoint8",
]
EXPECTED_TARGET_ROW_KEYS_BY_PARTITION = {
    "private_halo_only_connector_avoiding": [
        "0,1,3,5",
        "0,2,3,5",
        "0,3,4,5",
        "0,3,5,7",
    ],
    "endpoint8_connector_available": [
        "0,1,3,8",
        "0,1,5,8",
        "0,2,3,8",
        "0,2,5,8",
        "0,3,4,8",
        "0,3,7,8",
        "0,4,5,8",
        "0,5,7,8",
    ],
    "mixed_private_and_endpoint8": ["0,3,5,8"],
}
EXPECTED_PARTITION_COUNTS = {
    "private_halo_only_connector_avoiding": 4,
    "endpoint8_connector_available": 8,
    "mixed_private_and_endpoint8": 1,
}
EXPECTED_BASIC_BY_PARTITION = {
    "private_halo_only_connector_avoiding": 12,
    "endpoint8_connector_available": 9,
    "mixed_private_and_endpoint8": 7,
}
EXPECTED_STATUS_BY_PARTITION = {
    "private_halo_only_connector_avoiding": {"self_edge": 10, "strict_cycle": 2},
    "endpoint8_connector_available": {"self_edge": 7, "strict_cycle": 2},
    "mixed_private_and_endpoint8": {"self_edge": 3, "strict_cycle": 4},
}
EXPECTED_ZERO_SURVIVORS_BY_PARTITION = {
    "private_halo_only_connector_avoiding": 0,
    "endpoint8_connector_available": 0,
    "mixed_private_and_endpoint8": 0,
}
EXPECTED_CYCLIC_ORDER = list(range(9))
EXPECTED_OUTSIDE_SUPPORT_PAIRS = [[3, 5], [3, 8], [5, 8]]
PRIVATE_HALO_ONLY_PAIR = [3, 5]
ENDPOINT8_SUPPORT_PAIRS = [[3, 8], [5, 8]]
ORIGINAL_TARGET_CLASS = [0, 3, 5, 8]


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def build_escape_partition_payload(
    full_neighborhood: Mapping[str, Any],
    connector_contract: Mapping[str, Any],
    *,
    full_neighborhood_path: Path = DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    connector_contract_path: Path = DEFAULT_SOURCE_CONNECTOR_CONTRACT,
) -> dict[str, Any]:
    """Return the deterministic 151:6 outside-pair escape-partition payload."""

    errors: list[str] = []
    _validate_source_full_neighborhood(full_neighborhood, errors)
    _validate_source_connector_contract(connector_contract, errors)
    _validate_source_alignment(full_neighborhood, connector_contract, errors)

    records = _target_row_records(full_neighborhood, errors)
    summary = _summary(records)
    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "target_row_partition": records,
        "source_artifacts": [
            _source_summary(
                full_neighborhood_path,
                "source 151:6 full-neighborhood vertex-circle packet",
                full_neighborhood,
            ),
            _source_summary(
                connector_contract_path,
                "source 151:6 outside-pair connector contract",
                connector_contract,
            ),
        ],
        "interpretation": [
            (
                "The connector-avoiding private-halo-only target rows are not "
                "eliminated by the basic incidence/crossing filters."
            ),
            (
                "All currently recorded private-halo-only and endpoint-8 "
                "basic-filter survivors are eliminated by exact vertex-circle "
                "quotient replay."
            ),
            (
                "The remaining bridge gap is genuine outside-pair support "
                "existence and row/rich-class forcing, not another selected-row "
                "neighborhood replay for this packet."
            ),
            (
                "The artifact does not prove that pair [3,5] is impossible; "
                "it only records where that escape dies inside this diagnostic."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_escape_partition(payload)
    return payload


def assert_expected_escape_partition(payload: Mapping[str, Any]) -> None:
    """Assert the pinned 151:6 outside-pair escape partition."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    full_neighborhood_path: Path = DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    connector_contract_path: Path = DEFAULT_SOURCE_CONNECTOR_CONTRACT,
) -> list[str]:
    """Return validation errors for an escape-partition payload."""

    errors: list[str] = []
    if set(payload) != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(payload)!r}"
        )
        return errors

    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "validation_status": "passed",
        "validation_errors": [],
        "provenance": PROVENANCE,
    }
    for key, expected in expected_meta.items():
        if payload.get(key) != expected:
            errors.append(
                f"{key} mismatch: expected {expected!r}, got {payload.get(key)!r}"
            )

    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str):
        errors.append("claim_scope must be a string")
    else:
        for phrase in (
            "does not prove outside-pair support existence",
            "does not prove row forcing",
            "does not prove the private-halo-only pair is impossible",
            "does not prove n=9",
            "does not prove the bridge",
            "not a counterexample",
            "not a global status update",
        ):
            if phrase not in claim_scope:
                errors.append(f"claim_scope must contain {phrase!r}")

    records = payload.get("target_row_partition")
    if not isinstance(records, list):
        errors.append("target_row_partition must be a list")
        return errors
    for record in records:
        if not isinstance(record, Mapping):
            errors.append("target_row_partition entries must be objects")
            continue
        _validate_target_record(record, errors)
    _validate_summary(payload.get("summary"), records, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("does not prove that pair [3,5] is impossible" in item for item in interpretation):
        errors.append("interpretation must preserve the [3,5] nonclaim")

    if recompute and not errors:
        generated = build_escape_partition_payload(
            load_artifact(full_neighborhood_path),
            load_artifact(connector_contract_path),
            full_neighborhood_path=full_neighborhood_path,
            connector_contract_path=connector_contract_path,
        )
        if dict(payload) != generated:
            errors.append("stored artifact is stale relative to source packets")
    return errors


def summary_payload(
    path: Path,
    payload: Mapping[str, Any],
    errors: Sequence[str],
) -> dict[str, Any]:
    """Return a compact CLI summary."""

    summary = payload.get("summary", {})
    if not isinstance(summary, Mapping):
        summary = {}
    return {
        "artifact": display_path(path, ROOT),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "ok": not errors,
        "target_row_key": summary.get("target_row_key"),
        "target_center_candidate_count": summary.get("target_center_candidate_count"),
        "target_row_count_by_partition": summary.get("target_row_count_by_partition"),
        "basic_filter_complete_assignment_count_by_partition": summary.get(
            "basic_filter_complete_assignment_count_by_partition"
        ),
        "vertex_circle_status_counts_by_partition": summary.get(
            "vertex_circle_status_counts_by_partition"
        ),
        "connector_avoiding_basic_survivor_count": summary.get(
            "connector_avoiding_basic_survivor_count"
        ),
        "connector_available_basic_survivor_count": summary.get(
            "connector_available_basic_survivor_count"
        ),
        "vertex_circle_surviving_assignment_count": summary.get(
            "vertex_circle_surviving_assignment_count"
        ),
        "validation_errors": list(errors),
    }


def _target_row_records(
    full_neighborhood: Mapping[str, Any],
    errors: list[str],
) -> list[dict[str, Any]]:
    source_records = full_neighborhood.get("per_target_center_class")
    if not isinstance(source_records, list):
        errors.append("source per_target_center_class must be a list")
        return []

    records = []
    for source_record in source_records:
        if not isinstance(source_record, Mapping):
            errors.append("source target-center records must be objects")
            continue
        target_class = _int_list(
            _sequence(source_record.get("target_center_class"), "target_center_class")
        )
        support_pairs_present = _support_pairs_present(target_class)
        records.append(
            {
                "target_center_class_key": _row_key(target_class),
                "target_center_class": target_class,
                "target_center_class_is_original": target_class
                == ORIGINAL_TARGET_CLASS,
                "partition": _target_partition(target_class),
                "support_pairs_present": support_pairs_present,
                "support_pair_roles_present": _support_pair_roles_present(
                    support_pairs_present
                ),
                "contains_private_halo_pair": _contains_pair(
                    target_class, PRIVATE_HALO_ONLY_PAIR
                ),
                "contains_endpoint8": 8 in set(target_class),
                "search_node_count": _int(source_record.get("search_node_count")),
                "empty_domain_count": _int(source_record.get("empty_domain_count")),
                "basic_filter_complete_assignment_count": _int(
                    source_record.get("basic_filter_complete_assignment_count")
                ),
                "non_original_target_basic_assignment_count": _int(
                    source_record.get("non_original_target_basic_assignment_count")
                ),
                "vertex_circle_status_counts": _status_counts(
                    source_record.get("vertex_circle_status_counts")
                ),
                "vertex_circle_surviving_assignment_count": _int(
                    source_record.get("vertex_circle_surviving_assignment_count")
                ),
            }
        )
    return sorted(records, key=lambda record: str(record["target_center_class_key"]))


def _summary(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rows_by_partition: dict[str, list[str]] = {partition: [] for partition in PARTITION_ORDER}
    row_counts: Counter[str] = Counter()
    basic_counts: Counter[str] = Counter()
    vertex_survivor_counts: Counter[str] = Counter()
    status_counts_by_partition: dict[str, Counter[str]] = {
        partition: Counter() for partition in PARTITION_ORDER
    }
    status_counts_total: Counter[str] = Counter()
    search_nodes = 0
    empty_domains = 0
    non_original_basic = 0
    for record in records:
        partition = str(record["partition"])
        row_key = str(record["target_center_class_key"])
        rows_by_partition[partition].append(row_key)
        row_counts[partition] += 1
        basic_counts[partition] += int(record["basic_filter_complete_assignment_count"])
        vertex_survivor_counts[partition] += int(
            record["vertex_circle_surviving_assignment_count"]
        )
        status_counts = _status_counts(record["vertex_circle_status_counts"])
        status_counts_by_partition[partition].update(status_counts)
        status_counts_total.update(status_counts)
        search_nodes += int(record["search_node_count"])
        empty_domains += int(record["empty_domain_count"])
        non_original_basic += int(record["non_original_target_basic_assignment_count"])

    connector_available_basic = (
        basic_counts["endpoint8_connector_available"]
        + basic_counts["mixed_private_and_endpoint8"]
    )
    connector_available_vertex_survivors = (
        vertex_survivor_counts["endpoint8_connector_available"]
        + vertex_survivor_counts["mixed_private_and_endpoint8"]
    )
    return {
        "target_row_key": "151:6",
        "source_record_ids": [151],
        "cyclic_order": EXPECTED_CYCLIC_ORDER,
        "target_center": 6,
        "bootstrap_core_witnesses": [0],
        "outside_support_pairs": EXPECTED_OUTSIDE_SUPPORT_PAIRS,
        "connector_avoiding_support_pairs": [PRIVATE_HALO_ONLY_PAIR],
        "connector_forcing_support_pairs": ENDPOINT8_SUPPORT_PAIRS,
        "original_target_center_class": ORIGINAL_TARGET_CLASS,
        "target_center_candidate_count": len(records),
        "target_row_keys_by_partition": rows_by_partition,
        "target_row_count_by_partition": _ordered_count_dict(row_counts),
        "basic_filter_complete_assignment_count_by_partition": _ordered_count_dict(
            basic_counts
        ),
        "vertex_circle_status_counts_by_partition": {
            partition: dict(sorted(status_counts_by_partition[partition].items()))
            for partition in PARTITION_ORDER
        },
        "vertex_circle_surviving_assignment_count_by_partition": _ordered_count_dict(
            vertex_survivor_counts
        ),
        "connector_avoiding_target_row_count": row_counts[
            "private_halo_only_connector_avoiding"
        ],
        "connector_available_target_row_count": (
            row_counts["endpoint8_connector_available"]
            + row_counts["mixed_private_and_endpoint8"]
        ),
        "connector_avoiding_basic_survivor_count": basic_counts[
            "private_halo_only_connector_avoiding"
        ],
        "connector_available_basic_survivor_count": connector_available_basic,
        "connector_avoiding_vertex_circle_survivor_count": vertex_survivor_counts[
            "private_halo_only_connector_avoiding"
        ],
        "connector_available_vertex_circle_survivor_count": (
            connector_available_vertex_survivors
        ),
        "basic_filter_complete_assignment_count": sum(basic_counts.values()),
        "basic_filter_non_original_row6_assignment_count": non_original_basic,
        "vertex_circle_status_counts": dict(sorted(status_counts_total.items())),
        "vertex_circle_surviving_assignment_count": sum(
            vertex_survivor_counts.values()
        ),
        "search_node_count": search_nodes,
        "empty_domain_count": empty_domains,
        "scan_status": SCAN_STATUS,
        "remaining_gap": (
            "The private-halo-only connector-avoiding family survives basic "
            "filters, so the remaining proof-facing task is support existence "
            "and row/rich-class forcing. This artifact does not prove pair "
            "[3,5] impossible, does not prove an endpoint-8 support is forced, "
            "and does not promote the review-pending n=9 checker."
        ),
    }


def _validate_source_full_neighborhood(
    source: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "schema": SOURCE_FULL_NEIGHBORHOOD_SCHEMA,
        "status": SOURCE_FULL_NEIGHBORHOOD_STATUS,
        "trust": TRUST,
    }
    _validate_source_meta("source full-neighborhood", source, expected, errors)
    summary = _mapping(source.get("summary"), "source full-neighborhood summary", errors)
    if not summary:
        return
    expected_summary = {
        "target_row_key": "151:6",
        "source_record_ids": [151],
        "cyclic_order": EXPECTED_CYCLIC_ORDER,
        "target_center": 6,
        "bootstrap_core_witnesses": [0],
        "outside_support_pairs": EXPECTED_OUTSIDE_SUPPORT_PAIRS,
        "original_target_center_class": ORIGINAL_TARGET_CLASS,
        "target_center_candidate_count": 13,
        "basic_filter_complete_assignment_count": 28,
        "basic_filter_non_original_row6_assignment_count": 21,
        "vertex_circle_status_counts": {"self_edge": 20, "strict_cycle": 8},
        "vertex_circle_surviving_assignment_count": 0,
        "non_original_vertex_circle_surviving_assignment_count": 0,
        "scan_status": SOURCE_SCAN_STATUS,
    }
    for key, expected_value in expected_summary.items():
        _expect_mapping_field(
            "source full-neighborhood summary", summary, key, expected_value, errors
        )


def _validate_source_connector_contract(
    source: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "schema": SOURCE_CONNECTOR_CONTRACT_SCHEMA,
        "status": SOURCE_CONNECTOR_CONTRACT_STATUS,
        "trust": TRUST,
    }
    _validate_source_meta("source connector contract", source, expected, errors)
    summary = _mapping(source.get("summary"), "source connector contract summary", errors)
    if not summary:
        return
    expected_summary = {
        "target_row_key": "151:6",
        "source_record_ids": [151],
        "target_row_center": 6,
        "bootstrap_core_witnesses": [0],
        "outside_support_pairs": EXPECTED_OUTSIDE_SUPPORT_PAIRS,
        "connector_forcing_support_pairs": ENDPOINT8_SUPPORT_PAIRS,
        "connector_avoiding_support_pairs": [PRIVATE_HALO_ONLY_PAIR],
        "escape_status": "CONNECTOR_ESCAPE_REQUIRES_PRIVATE_HALO_ONLY_PAIR_3_5",
        "rich_support_existence_status": "OPEN_TARGET_NOT_PROVED",
    }
    for key, expected_value in expected_summary.items():
        _expect_mapping_field(
            "source connector contract summary", summary, key, expected_value, errors
        )


def _validate_source_alignment(
    full_neighborhood: Mapping[str, Any],
    connector_contract: Mapping[str, Any],
    errors: list[str],
) -> None:
    full_summary = _mapping(
        full_neighborhood.get("summary"), "source full-neighborhood summary", errors
    )
    contract_summary = _mapping(
        connector_contract.get("summary"), "source connector contract summary", errors
    )
    if not full_summary or not contract_summary:
        return
    for key in ("target_row_key", "source_record_ids", "bootstrap_core_witnesses"):
        if full_summary.get(key) != contract_summary.get(key):
            errors.append(f"source alignment mismatch for {key}")
    if full_summary.get("target_center") != contract_summary.get("target_row_center"):
        errors.append("source alignment mismatch for target center")
    if full_summary.get("outside_support_pairs") != contract_summary.get(
        "outside_support_pairs"
    ):
        errors.append("source alignment mismatch for outside support pairs")


def _validate_source_meta(
    label: str,
    source: Mapping[str, Any],
    expected: Mapping[str, str],
    errors: list[str],
) -> None:
    for key, expected_value in expected.items():
        if source.get(key) != expected_value:
            errors.append(
                f"{label} {key} mismatch: expected {expected_value!r}, "
                f"got {source.get(key)!r}"
            )


def _validate_target_record(record: Mapping[str, Any], errors: list[str]) -> None:
    if set(record) != EXPECTED_TARGET_RECORD_KEYS:
        errors.append(
            f"{record.get('target_center_class_key')} target keys mismatch: "
            f"expected {sorted(EXPECTED_TARGET_RECORD_KEYS)!r}, got {sorted(record)!r}"
        )
        return
    row = record.get("target_center_class")
    if not isinstance(row, list) or len(row) != 4:
        errors.append(f"{record.get('target_center_class_key')} target row invalid")
        return
    key = _row_key(_int_list(row))
    if record.get("target_center_class_key") != key:
        errors.append(f"{key} target row key mismatch")
    expected_partition = _target_partition(_int_list(row))
    if record.get("partition") != expected_partition:
        errors.append(f"{key} partition mismatch")
    expected_supports = _support_pairs_present(_int_list(row))
    if record.get("support_pairs_present") != expected_supports:
        errors.append(f"{key} support pairs mismatch")
    status_counts = record.get("vertex_circle_status_counts")
    if not isinstance(status_counts, Mapping):
        errors.append(f"{key} vertex_circle_status_counts must be an object")
    else:
        status_total = sum(int(value) for value in status_counts.values())
        if status_total != record.get("basic_filter_complete_assignment_count"):
            errors.append(f"{key} status counts do not sum to basic survivors")
    if record.get("vertex_circle_surviving_assignment_count") != 0:
        errors.append(f"{key} must have zero vertex-circle survivors")


def _validate_summary(
    summary: object,
    records: Sequence[object],
    errors: list[str],
) -> None:
    if not isinstance(summary, Mapping):
        errors.append("summary must be an object")
        return
    typed_records = [record for record in records if isinstance(record, Mapping)]
    expected = _summary(typed_records)
    for key, expected_value in expected.items():
        if summary.get(key) != expected_value:
            errors.append(
                f"summary.{key} mismatch: expected {expected_value!r}, "
                f"got {summary.get(key)!r}"
            )
    pinned = {
        "target_row_key": "151:6",
        "source_record_ids": [151],
        "cyclic_order": EXPECTED_CYCLIC_ORDER,
        "target_center": 6,
        "target_center_candidate_count": 13,
        "target_row_keys_by_partition": EXPECTED_TARGET_ROW_KEYS_BY_PARTITION,
        "target_row_count_by_partition": EXPECTED_PARTITION_COUNTS,
        "basic_filter_complete_assignment_count_by_partition": (
            EXPECTED_BASIC_BY_PARTITION
        ),
        "vertex_circle_status_counts_by_partition": EXPECTED_STATUS_BY_PARTITION,
        "vertex_circle_surviving_assignment_count_by_partition": (
            EXPECTED_ZERO_SURVIVORS_BY_PARTITION
        ),
        "connector_avoiding_target_row_count": 4,
        "connector_available_target_row_count": 9,
        "connector_avoiding_basic_survivor_count": 12,
        "connector_available_basic_survivor_count": 16,
        "connector_avoiding_vertex_circle_survivor_count": 0,
        "connector_available_vertex_circle_survivor_count": 0,
        "basic_filter_complete_assignment_count": 28,
        "basic_filter_non_original_row6_assignment_count": 21,
        "vertex_circle_status_counts": {"self_edge": 20, "strict_cycle": 8},
        "vertex_circle_surviving_assignment_count": 0,
        "search_node_count": 13_439,
        "empty_domain_count": 7_097,
        "scan_status": SCAN_STATUS,
    }
    for key, expected_value in pinned.items():
        if summary.get(key) != expected_value:
            errors.append(
                f"summary.{key} pinned mismatch: expected {expected_value!r}, "
                f"got {summary.get(key)!r}"
            )


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
    }


def _target_partition(row: Sequence[int]) -> str:
    has_private_pair = _contains_pair(row, PRIVATE_HALO_ONLY_PAIR)
    has_endpoint8 = 8 in set(row)
    has_endpoint8_pair = any(_contains_pair(row, pair) for pair in ENDPOINT8_SUPPORT_PAIRS)
    if has_private_pair and not has_endpoint8:
        return "private_halo_only_connector_avoiding"
    if has_private_pair and has_endpoint8:
        return "mixed_private_and_endpoint8"
    if has_endpoint8_pair:
        return "endpoint8_connector_available"
    raise AssertionError(f"target row {list(row)!r} has no expected support-pair role")


def _support_pairs_present(row: Sequence[int]) -> list[list[int]]:
    return [pair for pair in EXPECTED_OUTSIDE_SUPPORT_PAIRS if _contains_pair(row, pair)]


def _support_pair_roles_present(support_pairs: Sequence[Sequence[int]]) -> list[str]:
    roles = []
    for pair in support_pairs:
        int_pair = _int_list(pair)
        if int_pair == PRIVATE_HALO_ONLY_PAIR:
            roles.append("connector_avoiding_escape_support")
        elif int_pair in ENDPOINT8_SUPPORT_PAIRS:
            roles.append("endpoint8_connector_support")
        else:
            raise AssertionError(f"unexpected support pair {int_pair!r}")
    return roles


def _contains_pair(row: Sequence[int], pair: Sequence[int]) -> bool:
    return set(int(label) for label in pair) <= set(int(label) for label in row)


def _ordered_count_dict(counter: Counter[str]) -> dict[str, int]:
    return {partition: int(counter[partition]) for partition in PARTITION_ORDER}


def _mapping(value: object, name: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be an object")
        return {}
    return value


def _sequence(value: object, name: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise AssertionError(f"{name} must be a sequence")
    return value


def _expect_mapping_field(
    label: str,
    mapping: Mapping[str, Any],
    key: str,
    expected: object,
    errors: list[str],
) -> None:
    if mapping.get(key) != expected:
        errors.append(
            f"{label}.{key} mismatch: expected {expected!r}, got {mapping.get(key)!r}"
        )


def _status_counts(value: object) -> dict[str, int]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): int(value[key]) for key in sorted(value)}


def _int_list(values: Sequence[Any]) -> list[int]:
    return [int(value) for value in values]


def _int(value: object) -> int:
    if not isinstance(value, int):
        raise AssertionError(f"expected integer, got {value!r}")
    return value


def _row_key(row: Sequence[int]) -> str:
    return ",".join(str(label) for label in row)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--source-full-neighborhood",
        type=Path,
        default=DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    )
    parser.add_argument(
        "--source-connector-contract",
        type=Path,
        default=DEFAULT_SOURCE_CONNECTOR_CONTRACT,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_full_neighborhood = _resolve(args.source_full_neighborhood)
    source_connector_contract = _resolve(args.source_connector_contract)

    generated = build_escape_partition_payload(
        load_artifact(source_full_neighborhood),
        load_artifact(source_connector_contract),
        full_neighborhood_path=source_full_neighborhood,
        connector_contract_path=source_connector_contract,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        full_neighborhood_path=source_full_neighborhood,
        connector_contract_path=source_connector_contract,
    )
    if args.assert_expected:
        assert_expected_escape_partition(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 outside-pair escape partition")
        print(f"target row: {summary['target_row_key']}")
        print(f"partitions: {summary['target_row_count_by_partition']}")
        print(
            "basic survivors by partition: "
            f"{summary['basic_filter_complete_assignment_count_by_partition']}"
        )
        print(
            "vertex-circle survivors: "
            f"{summary['vertex_circle_surviving_assignment_count']}"
        )
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: 151:6 outside-pair escape partition verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
