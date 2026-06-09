#!/usr/bin/env python3
"""Check the bootstrap/T12 151:6 label-4 transfer-path targets."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict, deque
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.path_display import display_path  # noqa: E402
from erdos97.vertex_circle_quotient_replay import pair  # noqa: E402

from scripts.check_bootstrap_t12_151_6_label4_quotient_roles import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_LABEL4_QUOTIENT_ROLES,
    ROLE_STATUS as SOURCE_LABEL4_ROLE_STATUS,
    SCHEMA as SOURCE_LABEL4_QUOTIENT_ROLES_SCHEMA,
    STATUS as SOURCE_LABEL4_QUOTIENT_ROLES_STATUS,
    assert_expected_label4_quotient_roles,
)
from scripts.check_bootstrap_t12_151_6_label8_free_residual_targets import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_RESIDUAL_TARGETS,
    SCHEMA as SOURCE_RESIDUAL_TARGETS_SCHEMA,
    STATUS as SOURCE_RESIDUAL_TARGETS_STATUS,
    TARGET_STATUS as SOURCE_RESIDUAL_TARGETS_STATUS_FLAG,
    assert_expected_label8_free_residual_targets,
    load_artifact,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
    _json_counter,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_transfer_paths.v1"
STATUS = "BOOTSTRAP_T12_151_6_LABEL4_TRANSFER_PATHS_DIAGNOSTIC_ONLY"
TRANSFER_STATUS = "LABEL4_TRANSFER_PATHS_PINNED_FOR_EVERY_RESIDUAL_CYCLE_CLASS"
CLAIM_SCOPE = (
    "Proof-target diagnostic for the source-151 row-6 private-halo-only "
    "outside-pair lane. It records shortest selected-distance equality paths "
    "from label-4-bearing pairs to strict-cycle endpoint pairs for every "
    "label-4-bearing residual strict-cycle quotient class. This pins the "
    "direct/equality-only transfer rows but does not prove outside-pair "
    "support existence, does not prove row forcing, does not prove pair [3,5] "
    "impossible, does not prove endpoint-8 forcing, does not prove n=9, does "
    "not prove the bridge, is not a counterexample, and is not a global "
    "status update."
)
PROVENANCE = {
    "generator": "scripts/check_bootstrap_t12_151_6_label4_transfer_paths.py",
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label4_transfer_paths.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_transfer_paths.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "interpretation",
    "provenance",
    "source_artifacts",
    "status",
    "summary",
    "schema",
    "transfer_path_records",
    "trust",
    "validation_errors",
    "validation_status",
}
EXPECTED_SUMMARY = {
    "target_row_key": TARGET_ROW_KEY,
    "target_center": TARGET_CENTER,
    "private_target_center_class": PRIVATE_TARGET_CLASS,
    "private_support_pair": PRIVATE_SUPPORT_PAIR,
    "label4_transfer_path_class_signature_incidence_count": 19,
    "label4_transfer_path_class_occurrence_incidence_count": 23,
    "direct_endpoint_transfer_class_signature_incidence_count": 11,
    "direct_endpoint_transfer_class_occurrence_incidence_count": 14,
    "one_equality_edge_transfer_class_signature_incidence_count": 5,
    "one_equality_edge_transfer_class_occurrence_incidence_count": 5,
    "two_equality_edge_transfer_class_signature_incidence_count": 3,
    "two_equality_edge_transfer_class_occurrence_incidence_count": 4,
    "signatures_with_positive_transfer_class": 8,
    "occurrences_with_positive_transfer_class": 9,
    "transfer_edge_count_signature_counts": {
        "0": 11,
        "1": 5,
        "2": 3,
    },
    "transfer_edge_count_occurrence_counts": {
        "0": 14,
        "1": 5,
        "2": 4,
    },
    "direct_cycle_edge_access_transfer_edge_signature_counts": {
        "0": 11,
        "1": 3,
        "2": 3,
    },
    "direct_cycle_edge_access_transfer_edge_occurrence_counts": {
        "0": 14,
        "1": 3,
        "2": 4,
    },
    "quotient_equality_only_access_transfer_edge_signature_counts": {
        "1": 2,
    },
    "quotient_equality_only_access_transfer_edge_occurrence_counts": {
        "1": 2,
    },
    "positive_transfer_path_edge_signature_counts_by_row": {
        "5": 6,
        "6": 3,
        "7": 2,
    },
    "positive_transfer_path_edge_occurrence_counts_by_row": {
        "5": 7,
        "6": 4,
        "7": 2,
    },
    "transfer_status": TRANSFER_STATUS,
}


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_label4_transfer_paths_payload(
    source_residual_targets: Mapping[str, Any],
    source_label4_quotient_roles: Mapping[str, Any],
    *,
    source_residual_targets_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGETS,
    source_label4_quotient_roles_path: Path = DEFAULT_LABEL4_QUOTIENT_ROLES,
) -> dict[str, Any]:
    """Return the deterministic label-4 transfer-path payload."""

    errors: list[str] = []
    assert_expected_label8_free_residual_targets(source_residual_targets)
    assert_expected_label4_quotient_roles(source_label4_quotient_roles)
    _validate_source_residual_targets(source_residual_targets, errors)
    _validate_source_label4_quotient_roles(source_label4_quotient_roles, errors)
    records, summary = _transfer_path_records(
        source_residual_targets,
        source_label4_quotient_roles,
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "transfer_path_records": records,
        "source_artifacts": [
            _source_summary(
                source_residual_targets_path,
                "source 151:6 label-8-free residual targets",
                source_residual_targets,
            ),
            _source_summary(
                source_label4_quotient_roles_path,
                "source 151:6 label-4 quotient roles",
                source_label4_quotient_roles,
            ),
        ],
        "interpretation": [
            (
                "Each record gives a shortest selected-distance equality path "
                "from a label-4 pair in a residual strict-cycle quotient class "
                "to a strict-cycle endpoint pair in that same class."
            ),
            (
                "Eleven class incidences are already direct endpoint hits; "
                "five need one selected-distance equality edge, and three "
                "need two selected-distance equality edges."
            ),
            (
                "The two quotient-equality-only residual signatures both have "
                "one-edge transfer paths through center 5."
            ),
            (
                "This is a bridge-target path ledger only; it does not prove "
                "support existence, row forcing, endpoint-8 forcing, or "
                "impossibility of the private pair."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_label4_transfer_paths(payload)
    return payload


def assert_expected_label4_transfer_paths(payload: Mapping[str, Any]) -> None:
    """Assert the pinned label-4 transfer-path ledger."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    source_residual_targets_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGETS,
    source_label4_quotient_roles_path: Path = DEFAULT_LABEL4_QUOTIENT_ROLES,
) -> list[str]:
    """Return validation errors for a label-4 transfer-path payload."""

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
            "does not prove pair [3,5] impossible",
            "does not prove endpoint-8 forcing",
            "does not prove n=9",
            "does not prove the bridge",
            "not a counterexample",
            "not a global status update",
        ):
            if phrase not in claim_scope:
                errors.append(f"claim_scope must contain {phrase!r}")

    summary = _mapping(payload.get("summary"), "summary", errors)
    _validate_summary(summary, errors)
    records = payload.get("transfer_path_records")
    if not isinstance(records, list):
        errors.append("transfer_path_records must be a list")
    else:
        _validate_transfer_path_records(records, errors)
    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("does not prove support existence" in item for item in interpretation):
        errors.append("interpretation must preserve the support-existence nonclaim")

    if recompute and not errors:
        generated = build_label4_transfer_paths_payload(
            load_artifact(source_residual_targets_path),
            load_artifact(source_label4_quotient_roles_path),
            source_residual_targets_path=source_residual_targets_path,
            source_label4_quotient_roles_path=source_label4_quotient_roles_path,
        )
        if dict(payload) != generated:
            errors.append("stored artifact is stale relative to source artifacts")
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
        "label4_transfer_path_class_signature_incidence_count": summary.get(
            "label4_transfer_path_class_signature_incidence_count"
        ),
        "direct_endpoint_transfer_class_signature_incidence_count": summary.get(
            "direct_endpoint_transfer_class_signature_incidence_count"
        ),
        "one_equality_edge_transfer_class_signature_incidence_count": summary.get(
            "one_equality_edge_transfer_class_signature_incidence_count"
        ),
        "two_equality_edge_transfer_class_signature_incidence_count": summary.get(
            "two_equality_edge_transfer_class_signature_incidence_count"
        ),
        "transfer_status": summary.get("transfer_status"),
        "validation_errors": list(errors),
    }


def _transfer_path_records(
    source_residual_targets: Mapping[str, Any],
    source_label4_quotient_roles: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_records = source_residual_targets["residual_signature_records"]
    role_records = source_label4_quotient_roles["quotient_role_records"]
    records: list[dict[str, Any]] = []
    transfer_length_signature_counts: Counter[int] = Counter()
    transfer_length_occurrence_counts: Counter[int] = Counter()
    access_length_signature_counts: dict[str, Counter[int]] = {
        "direct_cycle_edge": Counter(),
        "quotient_equality_only": Counter(),
    }
    access_length_occurrence_counts: dict[str, Counter[int]] = {
        "direct_cycle_edge": Counter(),
        "quotient_equality_only": Counter(),
    }
    path_edge_signature_counts_by_row: Counter[int] = Counter()
    path_edge_occurrence_counts_by_row: Counter[int] = Counter()
    positive_transfer_signature_count = 0
    positive_transfer_occurrence_count = 0
    total_occurrence_incidence_count = 0

    for source_record, role_record in zip(source_records, role_records, strict=True):
        signature_index = int(source_record["signature_index"])
        if signature_index != int(role_record["signature_index"]):
            raise AssertionError("source and role signature indices disagree")
        multiplicity = int(source_record["multiplicity"])
        graph = _selected_distance_graph(source_record["rows"])
        has_positive_transfer = False
        for class_record in role_record["label4_cycle_quotient_classes"]:
            quotient_class = _tuple_pair(class_record["quotient_class"])
            label4_pair_members = [
                _tuple_pair(pair_member)
                for pair_member in class_record["label4_pair_members"]
            ]
            cycle_endpoint_pairs = _cycle_endpoint_pairs(
                source_record["cycle_edges"],
                quotient_class,
            )
            chosen_start, chosen_end, transfer_path = _shortest_transfer_path(
                graph,
                label4_pair_members,
                cycle_endpoint_pairs,
            )
            transfer_edge_count = len(transfer_path)
            transfer_mode = _transfer_mode(transfer_edge_count)
            if transfer_edge_count > 0:
                has_positive_transfer = True
            transfer_length_signature_counts[transfer_edge_count] += 1
            transfer_length_occurrence_counts[transfer_edge_count] += multiplicity
            access_mode = str(role_record["access_mode"])
            access_length_signature_counts[access_mode][transfer_edge_count] += 1
            access_length_occurrence_counts[access_mode][
                transfer_edge_count
            ] += multiplicity
            total_occurrence_incidence_count += multiplicity
            for edge in transfer_path:
                row = int(edge["row"])
                path_edge_signature_counts_by_row[row] += 1
                path_edge_occurrence_counts_by_row[row] += multiplicity
            records.append(
                {
                    "transfer_record_index": len(records),
                    "signature_index": signature_index,
                    "multiplicity": multiplicity,
                    "auxiliary_center_pair": role_record["auxiliary_center_pair"],
                    "access_mode": access_mode,
                    "quotient_class": list(quotient_class),
                    "label4_pair_members": [
                        list(pair_member) for pair_member in label4_pair_members
                    ],
                    "cycle_endpoint_pairs": [
                        list(pair_member) for pair_member in cycle_endpoint_pairs
                    ],
                    "chosen_label4_pair": list(chosen_start),
                    "chosen_cycle_endpoint_pair": list(chosen_end),
                    "transfer_mode": transfer_mode,
                    "transfer_edge_count": transfer_edge_count,
                    "transfer_path": transfer_path,
                }
            )
        if has_positive_transfer:
            positive_transfer_signature_count += 1
            positive_transfer_occurrence_count += multiplicity

    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "label4_transfer_path_class_signature_incidence_count": len(records),
        "label4_transfer_path_class_occurrence_incidence_count": (
            total_occurrence_incidence_count
        ),
        "direct_endpoint_transfer_class_signature_incidence_count": (
            transfer_length_signature_counts[0]
        ),
        "direct_endpoint_transfer_class_occurrence_incidence_count": (
            transfer_length_occurrence_counts[0]
        ),
        "one_equality_edge_transfer_class_signature_incidence_count": (
            transfer_length_signature_counts[1]
        ),
        "one_equality_edge_transfer_class_occurrence_incidence_count": (
            transfer_length_occurrence_counts[1]
        ),
        "two_equality_edge_transfer_class_signature_incidence_count": (
            transfer_length_signature_counts[2]
        ),
        "two_equality_edge_transfer_class_occurrence_incidence_count": (
            transfer_length_occurrence_counts[2]
        ),
        "signatures_with_positive_transfer_class": positive_transfer_signature_count,
        "occurrences_with_positive_transfer_class": positive_transfer_occurrence_count,
        "transfer_edge_count_signature_counts": _json_counter(
            transfer_length_signature_counts
        ),
        "transfer_edge_count_occurrence_counts": _json_counter(
            transfer_length_occurrence_counts
        ),
        "direct_cycle_edge_access_transfer_edge_signature_counts": _json_counter(
            access_length_signature_counts["direct_cycle_edge"]
        ),
        "direct_cycle_edge_access_transfer_edge_occurrence_counts": _json_counter(
            access_length_occurrence_counts["direct_cycle_edge"]
        ),
        "quotient_equality_only_access_transfer_edge_signature_counts": _json_counter(
            access_length_signature_counts["quotient_equality_only"]
        ),
        "quotient_equality_only_access_transfer_edge_occurrence_counts": _json_counter(
            access_length_occurrence_counts["quotient_equality_only"]
        ),
        "positive_transfer_path_edge_signature_counts_by_row": _json_counter(
            path_edge_signature_counts_by_row
        ),
        "positive_transfer_path_edge_occurrence_counts_by_row": _json_counter(
            path_edge_occurrence_counts_by_row
        ),
        "transfer_status": TRANSFER_STATUS,
    }
    return records, summary


def _selected_distance_graph(
    rows: Sequence[Mapping[str, object]],
) -> dict[tuple[int, int], list[tuple[tuple[int, int], dict[str, Any]]]]:
    graph: dict[tuple[int, int], list[tuple[tuple[int, int], dict[str, Any]]]] = (
        defaultdict(list)
    )
    for row in rows:
        center = int(row["center"])
        witnesses = sorted(int(witness) for witness in row["witnesses"])
        for left, right in combinations(witnesses, 2):
            left_pair = pair(center, left)
            right_pair = pair(center, right)
            forward = {
                "row": center,
                "row_witness_pair": [left, right],
                "from_pair": list(left_pair),
                "to_pair": list(right_pair),
            }
            backward = {
                "row": center,
                "row_witness_pair": [left, right],
                "from_pair": list(right_pair),
                "to_pair": list(left_pair),
            }
            graph[left_pair].append((right_pair, forward))
            graph[right_pair].append((left_pair, backward))
    return {key: sorted(value, key=_adjacency_key) for key, value in graph.items()}


def _shortest_transfer_path(
    graph: Mapping[tuple[int, int], Sequence[tuple[tuple[int, int], dict[str, Any]]]],
    label4_pair_members: Sequence[tuple[int, int]],
    cycle_endpoint_pairs: Sequence[tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int], list[dict[str, Any]]]:
    starts = sorted(label4_pair_members)
    goals = set(cycle_endpoint_pairs)
    queue: deque[tuple[int, int]] = deque(starts)
    seen: dict[tuple[int, int], tuple[tuple[int, int] | None, dict[str, Any] | None]]
    seen = {start: (None, None) for start in starts}

    while queue:
        current = queue.popleft()
        if current in goals:
            path: list[dict[str, Any]] = []
            cursor = current
            while seen[cursor][0] is not None:
                previous, edge = seen[cursor]
                assert previous is not None
                assert edge is not None
                path.append(edge)
                cursor = previous
            path.reverse()
            return cursor, current, path
        for neighbor, edge in graph.get(current, ()):
            if neighbor not in seen:
                seen[neighbor] = (current, edge)
                queue.append(neighbor)
    raise AssertionError(
        "no selected-distance transfer path from label-4 pair to cycle endpoint"
    )


def _cycle_endpoint_pairs(
    cycle_edges: Sequence[Mapping[str, Any]],
    quotient_class: tuple[int, int],
) -> list[tuple[int, int]]:
    endpoint_pairs: set[tuple[int, int]] = set()
    for edge in cycle_edges:
        if _tuple_pair(edge["outer_class"]) == quotient_class:
            endpoint_pairs.add(_tuple_pair(edge["outer_pair"]))
        if _tuple_pair(edge["inner_class"]) == quotient_class:
            endpoint_pairs.add(_tuple_pair(edge["inner_pair"]))
    if not endpoint_pairs:
        raise AssertionError(f"missing cycle endpoint pairs for {quotient_class!r}")
    return sorted(endpoint_pairs)


def _transfer_mode(transfer_edge_count: int) -> str:
    if transfer_edge_count == 0:
        return "direct_endpoint"
    if transfer_edge_count == 1:
        return "one_equality_edge"
    if transfer_edge_count == 2:
        return "two_equality_edges"
    return "longer_equality_path"


def _adjacency_key(
    item: tuple[tuple[int, int], Mapping[str, Any]],
) -> tuple[tuple[int, int], int, tuple[int, int]]:
    neighbor, edge = item
    return (
        neighbor,
        int(edge["row"]),
        tuple(int(value) for value in edge["row_witness_pair"]),
    )


def _validate_source_residual_targets(
    source_residual_targets: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "schema": SOURCE_RESIDUAL_TARGETS_SCHEMA,
        "status": SOURCE_RESIDUAL_TARGETS_STATUS,
        "trust": TRUST,
    }
    for key, expected_value in expected.items():
        if source_residual_targets.get(key) != expected_value:
            errors.append(
                "source residual targets "
                f"{key} mismatch: expected {expected_value!r}, "
                f"got {source_residual_targets.get(key)!r}"
            )
    summary = _mapping(
        source_residual_targets.get("summary"),
        "source residual targets summary",
        errors,
    )
    expected_counts = {
        "label8_free_distinct_exact_signature_count": 10,
        "label8_free_occurrence_count": 12,
        "signatures_with_any_label4_auxiliary_row": 10,
        "target_status": SOURCE_RESIDUAL_TARGETS_STATUS_FLAG,
    }
    for key, expected_value in expected_counts.items():
        if summary.get(key) != expected_value:
            errors.append(
                "source residual targets "
                f"summary.{key} mismatch: expected {expected_value!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_source_label4_quotient_roles(
    source_label4_quotient_roles: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "schema": SOURCE_LABEL4_QUOTIENT_ROLES_SCHEMA,
        "status": SOURCE_LABEL4_QUOTIENT_ROLES_STATUS,
        "trust": TRUST,
    }
    for key, expected_value in expected.items():
        if source_label4_quotient_roles.get(key) != expected_value:
            errors.append(
                "source label-4 quotient roles "
                f"{key} mismatch: expected {expected_value!r}, "
                f"got {source_label4_quotient_roles.get(key)!r}"
            )
    summary = _mapping(
        source_label4_quotient_roles.get("summary"),
        "source label-4 quotient roles summary",
        errors,
    )
    expected_counts = {
        "label8_free_distinct_exact_signature_count": 10,
        "label8_free_occurrence_count": 12,
        "label4_cycle_quotient_class_signature_incidence_count": 19,
        "label4_cycle_quotient_class_occurrence_incidence_count": 23,
        "role_status": SOURCE_LABEL4_ROLE_STATUS,
    }
    for key, expected_value in expected_counts.items():
        if summary.get(key) != expected_value:
            errors.append(
                "source label-4 quotient roles "
                f"summary.{key} mismatch: expected {expected_value!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, got {summary.get(key)!r}"
            )


def _validate_transfer_path_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    expected_count = EXPECTED_SUMMARY[
        "label4_transfer_path_class_signature_incidence_count"
    ]
    if len(records) != expected_count:
        errors.append("transfer_path_records length mismatch")
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"transfer_path_records[{index}] must be an object")
            continue
        if record.get("transfer_record_index") != index:
            errors.append(f"transfer_path_records[{index}] index mismatch")
        mode = record.get("transfer_mode")
        if mode not in {
            "direct_endpoint",
            "one_equality_edge",
            "two_equality_edges",
        }:
            errors.append(f"transfer_path_records[{index}] invalid transfer_mode")
        path = record.get("transfer_path")
        if not isinstance(path, list):
            errors.append(f"transfer_path_records[{index}] path must be a list")
            continue
        if record.get("transfer_edge_count") != len(path):
            errors.append(f"transfer_path_records[{index}] path length mismatch")
        start = record.get("chosen_label4_pair")
        end = record.get("chosen_cycle_endpoint_pair")
        if not _is_pair_list(start) or 4 not in start:
            errors.append(f"transfer_path_records[{index}] invalid label-4 start")
        if not _is_pair_list(end):
            errors.append(f"transfer_path_records[{index}] invalid endpoint")
        if len(path) == 0:
            if start != end:
                errors.append(
                    f"transfer_path_records[{index}] direct endpoint mismatch"
                )
        else:
            if path[0].get("from_pair") != start:
                errors.append(f"transfer_path_records[{index}] path start mismatch")
            if path[-1].get("to_pair") != end:
                errors.append(f"transfer_path_records[{index}] path end mismatch")
            for path_index, edge in enumerate(path):
                if not isinstance(edge, Mapping):
                    errors.append(
                        f"transfer_path_records[{index}] path edge must be object"
                    )
                    continue
                if path_index > 0 and path[path_index - 1].get("to_pair") != edge.get(
                    "from_pair"
                ):
                    errors.append(
                        f"transfer_path_records[{index}] path edge chain mismatch"
                    )


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary")
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "target_status": (
            summary.get("target_status") if isinstance(summary, Mapping) else None
        ),
        "role_status": (
            summary.get("role_status") if isinstance(summary, Mapping) else None
        ),
    }


def _mapping(value: object, name: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be an object")
        return {}
    return value


def _tuple_pair(value: object) -> tuple[int, int]:
    if not isinstance(value, Sequence) or isinstance(value, str) or len(value) != 2:
        raise AssertionError(f"{value!r} is not a pair")
    return pair(int(value[0]), int(value[1]))


def _is_pair_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, int) for item in value)
    )


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--source-residual-targets",
        type=Path,
        default=DEFAULT_SOURCE_RESIDUAL_TARGETS,
    )
    parser.add_argument(
        "--source-label4-quotient-roles",
        type=Path,
        default=DEFAULT_LABEL4_QUOTIENT_ROLES,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_residual_targets = _resolve(args.source_residual_targets)
    source_label4_quotient_roles = _resolve(args.source_label4_quotient_roles)

    generated = build_label4_transfer_paths_payload(
        load_artifact(source_residual_targets),
        load_artifact(source_label4_quotient_roles),
        source_residual_targets_path=source_residual_targets,
        source_label4_quotient_roles_path=source_label4_quotient_roles,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        source_residual_targets_path=source_residual_targets,
        source_label4_quotient_roles_path=source_label4_quotient_roles,
    )
    if args.assert_expected:
        assert_expected_label4_transfer_paths(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 transfer paths")
        print(f"target row: {summary['target_row_key']}")
        print(
            "label-4 transfer class incidences: "
            f"{summary['label4_transfer_path_class_signature_incidence_count']}"
        )
        print(
            "direct endpoint class incidences: "
            f"{summary['direct_endpoint_transfer_class_signature_incidence_count']}"
        )
        print(
            "one-edge transfer class incidences: "
            f"{summary['one_equality_edge_transfer_class_signature_incidence_count']}"
        )
        print(
            "two-edge transfer class incidences: "
            f"{summary['two_equality_edge_transfer_class_signature_incidence_count']}"
        )
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
