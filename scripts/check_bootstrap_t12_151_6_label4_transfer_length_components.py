#!/usr/bin/env python3
"""Check length components induced by the 151:6 label-4 transfer obligations."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.path_display import display_path  # noqa: E402

from scripts.check_bootstrap_t12_151_6_label4_transfer_obligations import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_OBLIGATIONS,
    OBLIGATION_STATUS as SOURCE_OBLIGATION_STATUS,
    SCHEMA as SOURCE_OBLIGATIONS_SCHEMA,
    STATUS as SOURCE_OBLIGATIONS_STATUS,
    assert_expected_label4_transfer_obligations,
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


N = 9
LABEL4 = 4
LABEL8 = 8

SCHEMA = "erdos97.bootstrap_t12_151_6_label4_transfer_length_components.v1"
STATUS = "BOOTSTRAP_T12_151_6_LABEL4_TRANSFER_LENGTH_COMPONENTS_DIAGNOSTIC_ONLY"
COMPONENT_STATUS = "ROW_LOCAL_LABEL4_TRANSFER_LENGTH_COMPONENTS_PINNED"
CLAIM_SCOPE = (
    "Proof-target diagnostic for the source-151 row-6 private-halo-only "
    "outside-pair lane. It collapses the row-local label-4 transfer "
    "obligations into undirected segment-length components and cyclic-gap "
    "profiles. The packet identifies six equal-length component targets, "
    "including the repeated row-5/row-6 connector cascade D[4,5]=D[5,6]=D[0,6]. "
    "This does not prove outside-pair support existence, does not prove row "
    "forcing, does not prove pair [3,5] impossible, does not prove endpoint-8 "
    "forcing, does not prove n=9, does not prove the bridge, is not a "
    "counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/check_bootstrap_t12_151_6_label4_transfer_length_components.py"
    ),
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label4_transfer_length_components.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_transfer_length_components.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "interpretation",
    "length_component_records",
    "provenance",
    "schema",
    "segment_records",
    "source_artifacts",
    "status",
    "summary",
    "trust",
    "validation_errors",
    "validation_status",
}
EXPECTED_SUMMARY = {
    "target_row_key": TARGET_ROW_KEY,
    "target_center": TARGET_CENTER,
    "private_target_center_class": PRIVATE_TARGET_CLASS,
    "private_support_pair": PRIVATE_SUPPORT_PAIR,
    "source_unique_edge_obligation_count": 7,
    "source_unique_path_motif_count": 6,
    "source_positive_transfer_signature_count": 8,
    "source_positive_transfer_occurrence_count": 9,
    "length_component_count": 6,
    "unique_segment_count": 9,
    "component_size_counts": {
        "2": 5,
        "3": 1,
    },
    "unique_segment_count_by_cyclic_gap": {
        "1": 2,
        "2": 1,
        "3": 4,
        "4": 2,
    },
    "unique_segment_count_by_kind": {
        "cyclic_gap_2_diagonal": 1,
        "cyclic_gap_3_diagonal": 4,
        "cyclic_gap_4_diagonal": 2,
        "hull_edge": 2,
    },
    "component_count_by_geometry_class": {
        "diagonal_only_equality": 2,
        "edge_diagonal_equality": 3,
        "edge_edge_diagonal_chain": 1,
    },
    "component_signature_count_by_geometry_class": {
        "diagonal_only_equality": 2,
        "edge_diagonal_equality": 3,
        "edge_edge_diagonal_chain": 3,
    },
    "component_occurrence_count_by_geometry_class": {
        "diagonal_only_equality": 2,
        "edge_diagonal_equality": 3,
        "edge_edge_diagonal_chain": 4,
    },
    "component_count_by_path_shape": {
        "one_edge_row5_label4_spoke_swap": 3,
        "one_edge_row7_label4_spoke_swap": 2,
        "two_edge_row5_row6_connector_cascade": 1,
    },
    "component_signature_count_by_path_shape": {
        "one_edge_row5_label4_spoke_swap": 3,
        "one_edge_row7_label4_spoke_swap": 2,
        "two_edge_row5_row6_connector_cascade": 3,
    },
    "component_occurrence_count_by_path_shape": {
        "one_edge_row5_label4_spoke_swap": 3,
        "one_edge_row7_label4_spoke_swap": 2,
        "two_edge_row5_row6_connector_cascade": 4,
    },
    "component_with_hull_edge_count": 4,
    "component_with_only_diagonals_count": 2,
    "component_with_edge_to_diagonal_equality_count": 4,
    "component_with_target_center_count": 1,
    "component_with_row6_connector_step_count": 1,
    "component_with_label4_segment_count": 6,
    "label8_free_component_count": 6,
    "hull_edge_segment_count": 2,
    "diagonal_segment_count": 7,
    "cascade_component_key": "D[0,6]=D[4,5]=D[5,6]",
    "cascade_component_signature_count": 3,
    "cascade_component_occurrence_count": 4,
    "component_status": COMPONENT_STATUS,
}


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_label4_transfer_length_components_payload(
    source_obligations: Mapping[str, Any],
    *,
    source_obligations_path: Path = DEFAULT_SOURCE_OBLIGATIONS,
) -> dict[str, Any]:
    """Return the deterministic length-component payload."""

    errors: list[str] = []
    assert_expected_label4_transfer_obligations(source_obligations)
    _validate_source_obligations(source_obligations, errors)
    component_records, segment_records, summary = _length_component_records(
        source_obligations
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "length_component_records": component_records,
        "segment_records": segment_records,
        "source_artifacts": [
            _source_summary(
                source_obligations_path,
                "source 151:6 label-4 transfer obligations",
                source_obligations,
            )
        ],
        "interpretation": [
            (
                "Each length component is the undirected segment-length "
                "equality class induced by one unique transfer-path motif."
            ),
            (
                "The only component that reaches row 6 is the connector "
                "cascade D[0,6]=D[4,5]=D[5,6], which contains two hull "
                "edges and one cyclic-gap-3 diagonal."
            ),
            (
                "The remaining positive transfers split into three "
                "edge-to-diagonal row-5 equalities and two diagonal-only "
                "row-7 equalities."
            ),
            (
                "This is a bridge-target geometry ledger only; it does not "
                "prove support existence, row forcing, endpoint-8 forcing, "
                "or impossibility of the private pair."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_label4_transfer_length_components(payload)
    return payload


def assert_expected_label4_transfer_length_components(
    payload: Mapping[str, Any],
) -> None:
    """Assert the pinned length components."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    source_obligations_path: Path = DEFAULT_SOURCE_OBLIGATIONS,
) -> list[str]:
    """Return validation errors for a transfer length-component payload."""

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
    component_records = payload.get("length_component_records")
    if not isinstance(component_records, list):
        errors.append("length_component_records must be a list")
    else:
        _validate_component_records(component_records, errors)
    segment_records = payload.get("segment_records")
    if not isinstance(segment_records, list):
        errors.append("segment_records must be a list")
    else:
        _validate_segment_records(segment_records, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("does not prove support existence" in item for item in interpretation):
        errors.append("interpretation must preserve the support-existence nonclaim")

    if recompute and not errors:
        generated = build_label4_transfer_length_components_payload(
            load_artifact(source_obligations_path),
            source_obligations_path=source_obligations_path,
        )
        if dict(payload) != generated:
            errors.append("stored artifact is stale relative to source artifact")
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
        "length_component_count": summary.get("length_component_count"),
        "unique_segment_count": summary.get("unique_segment_count"),
        "component_count_by_geometry_class": summary.get(
            "component_count_by_geometry_class"
        ),
        "cascade_component_key": summary.get("cascade_component_key"),
        "component_status": summary.get("component_status"),
        "validation_errors": list(errors),
    }


def _length_component_records(
    source_obligations: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    edge_by_key = {
        str(edge["obligation_key"]): edge
        for edge in source_obligations["unique_edge_obligation_records"]
    }
    component_records: list[dict[str, Any]] = []
    segment_buckets: dict[str, dict[str, Any]] = {}
    component_size_counts: Counter[int] = Counter()
    geometry_class_counts: Counter[str] = Counter()
    geometry_class_signature_counts: Counter[str] = Counter()
    geometry_class_occurrence_counts: Counter[str] = Counter()
    path_shape_counts: Counter[str] = Counter()
    path_shape_signature_counts: Counter[str] = Counter()
    path_shape_occurrence_counts: Counter[str] = Counter()

    with_hull_edge = 0
    with_only_diagonals = 0
    with_edge_to_diagonal = 0
    with_target_center = 0
    with_row6_connector = 0
    with_label4_segment = 0
    label8_free = 0
    cascade_signature_count = 0
    cascade_occurrence_count = 0

    for motif in source_obligations["path_motif_records"]:
        path_keys = [str(key) for key in motif["path_obligation_keys"]]
        source_edges = [edge_by_key[key] for key in path_keys]
        segment_map: dict[tuple[int, int], dict[str, Any]] = {}
        for edge in source_edges:
            for pair in (edge["from_pair"], edge["to_pair"]):
                segment = _segment_record(pair)
                segment_map[tuple(segment["pair"])] = segment

        segments = [segment_map[key] for key in sorted(segment_map)]
        component_key = _component_key([segment["pair"] for segment in segments])
        geometry_class = _component_geometry_class(segments)
        signature_count = int(motif["signature_incidence_count"])
        occurrence_count = int(motif["occurrence_incidence_count"])
        path_shape = str(motif["path_shape"])
        has_hull_edge = any(segment["segment_kind"] == "hull_edge" for segment in segments)
        has_diagonal = any(segment["segment_kind"] != "hull_edge" for segment in segments)
        has_target_center = any(TARGET_CENTER in segment["pair"] for segment in segments)
        has_row6_connector = any(edge["row6_connector_step"] for edge in source_edges)
        has_label4_segment = any(LABEL4 in segment["pair"] for segment in segments)
        is_label8_free = all(LABEL8 not in segment["pair"] for segment in segments)
        gap_counts = Counter(segment["cyclic_gap"] for segment in segments)
        kind_counts = Counter(str(segment["segment_kind"]) for segment in segments)
        row_obligation_keys_by_row: dict[str, list[str]] = {}
        for edge in source_edges:
            row_key = str(edge["row"])
            row_obligation_keys_by_row.setdefault(row_key, []).append(
                str(edge["obligation_key"])
            )

        component_records.append(
            {
                "component_key": component_key,
                "source_path_motif_key": motif["path_motif_key"],
                "path_shape": path_shape,
                "geometry_class": geometry_class,
                "signature_incidence_count": signature_count,
                "occurrence_incidence_count": occurrence_count,
                "access_mode_counts": motif["access_mode_counts"],
                "transfer_record_indices": motif["transfer_record_indices"],
                "signature_indices": motif["signature_indices"],
                "source_obligation_keys": path_keys,
                "row_obligation_keys_by_row": row_obligation_keys_by_row,
                "segment_count": len(segments),
                "segments": segments,
                "cyclic_gap_counts": _json_counter(gap_counts),
                "segment_kind_counts": _json_counter(kind_counts),
                "contains_hull_edge": has_hull_edge,
                "contains_diagonal": has_diagonal,
                "contains_edge_to_diagonal_equality": has_hull_edge and has_diagonal,
                "contains_target_center": has_target_center,
                "contains_row6_connector_step": has_row6_connector,
                "contains_label4_segment": has_label4_segment,
                "label8_free": is_label8_free,
            }
        )
        component_size_counts[len(segments)] += 1
        geometry_class_counts[geometry_class] += 1
        geometry_class_signature_counts[geometry_class] += signature_count
        geometry_class_occurrence_counts[geometry_class] += occurrence_count
        path_shape_counts[path_shape] += 1
        path_shape_signature_counts[path_shape] += signature_count
        path_shape_occurrence_counts[path_shape] += occurrence_count
        if has_hull_edge:
            with_hull_edge += 1
        if not has_hull_edge:
            with_only_diagonals += 1
        if has_hull_edge and has_diagonal:
            with_edge_to_diagonal += 1
        if has_target_center:
            with_target_center += 1
        if has_row6_connector:
            with_row6_connector += 1
        if has_label4_segment:
            with_label4_segment += 1
        if is_label8_free:
            label8_free += 1
        if component_key == EXPECTED_SUMMARY["cascade_component_key"]:
            cascade_signature_count += signature_count
            cascade_occurrence_count += occurrence_count

        for segment in segments:
            _add_segment_bucket(
                segment_buckets,
                segment,
                component_key,
                path_shape,
                geometry_class,
                signature_count,
                occurrence_count,
            )

    component_records = sorted(component_records, key=lambda record: record["component_key"])
    segment_records = [
        _finalize_segment_bucket(bucket)
        for _, bucket in sorted(segment_buckets.items(), key=lambda item: item[0])
    ]
    segment_gap_counts = Counter(
        int(record["cyclic_gap"]) for record in segment_records
    )
    segment_kind_counts = Counter(
        str(record["segment_kind"]) for record in segment_records
    )
    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "source_unique_edge_obligation_count": len(
            source_obligations["unique_edge_obligation_records"]
        ),
        "source_unique_path_motif_count": len(
            source_obligations["path_motif_records"]
        ),
        "source_positive_transfer_signature_count": source_obligations["summary"][
            "source_positive_transfer_class_signature_incidence_count"
        ],
        "source_positive_transfer_occurrence_count": source_obligations["summary"][
            "source_positive_transfer_class_occurrence_incidence_count"
        ],
        "length_component_count": len(component_records),
        "unique_segment_count": len(segment_records),
        "component_size_counts": _json_counter(component_size_counts),
        "unique_segment_count_by_cyclic_gap": _json_counter(segment_gap_counts),
        "unique_segment_count_by_kind": _json_counter(segment_kind_counts),
        "component_count_by_geometry_class": _json_counter(geometry_class_counts),
        "component_signature_count_by_geometry_class": _json_counter(
            geometry_class_signature_counts
        ),
        "component_occurrence_count_by_geometry_class": _json_counter(
            geometry_class_occurrence_counts
        ),
        "component_count_by_path_shape": _json_counter(path_shape_counts),
        "component_signature_count_by_path_shape": _json_counter(
            path_shape_signature_counts
        ),
        "component_occurrence_count_by_path_shape": _json_counter(
            path_shape_occurrence_counts
        ),
        "component_with_hull_edge_count": with_hull_edge,
        "component_with_only_diagonals_count": with_only_diagonals,
        "component_with_edge_to_diagonal_equality_count": with_edge_to_diagonal,
        "component_with_target_center_count": with_target_center,
        "component_with_row6_connector_step_count": with_row6_connector,
        "component_with_label4_segment_count": with_label4_segment,
        "label8_free_component_count": label8_free,
        "hull_edge_segment_count": sum(
            1 for record in segment_records if record["segment_kind"] == "hull_edge"
        ),
        "diagonal_segment_count": sum(
            1 for record in segment_records if record["segment_kind"] != "hull_edge"
        ),
        "cascade_component_key": EXPECTED_SUMMARY["cascade_component_key"],
        "cascade_component_signature_count": cascade_signature_count,
        "cascade_component_occurrence_count": cascade_occurrence_count,
        "component_status": COMPONENT_STATUS,
    }
    return component_records, segment_records, summary


def _component_geometry_class(segments: Sequence[Mapping[str, Any]]) -> str:
    kinds = [str(segment["segment_kind"]) for segment in segments]
    hull_edge_count = kinds.count("hull_edge")
    if hull_edge_count == 0:
        return "diagonal_only_equality"
    if len(segments) == 2 and hull_edge_count == 1:
        return "edge_diagonal_equality"
    if hull_edge_count >= 2 and len(segments) >= 3:
        return "edge_edge_diagonal_chain"
    return "mixed_edge_diagonal_component"


def _segment_record(pair: Sequence[int]) -> dict[str, Any]:
    normalized = _normalize_pair(pair)
    gap = _cyclic_gap(normalized)
    return {
        "segment_key": _segment_key(normalized),
        "pair": list(normalized),
        "cyclic_gap": gap,
        "segment_kind": _segment_kind(gap),
        "contains_label4": LABEL4 in normalized,
        "contains_label8": LABEL8 in normalized,
        "contains_target_center": TARGET_CENTER in normalized,
    }


def _add_segment_bucket(
    buckets: dict[str, dict[str, Any]],
    segment: Mapping[str, Any],
    component_key: str,
    path_shape: str,
    geometry_class: str,
    signature_count: int,
    occurrence_count: int,
) -> None:
    key = str(segment["segment_key"])
    if key not in buckets:
        buckets[key] = {
            **segment,
            "component_keys": [],
            "path_shape_counts": Counter(),
            "geometry_class_counts": Counter(),
            "component_signature_incidence_count": 0,
            "component_occurrence_incidence_count": 0,
        }
    bucket = buckets[key]
    bucket["component_keys"].append(component_key)
    bucket["path_shape_counts"][path_shape] += 1
    bucket["geometry_class_counts"][geometry_class] += 1
    bucket["component_signature_incidence_count"] += signature_count
    bucket["component_occurrence_incidence_count"] += occurrence_count


def _finalize_segment_bucket(bucket: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(bucket)
    result["component_keys"] = sorted(result["component_keys"])
    result["path_shape_counts"] = _json_counter(result["path_shape_counts"])
    result["geometry_class_counts"] = _json_counter(result["geometry_class_counts"])
    return result


def _component_key(pairs: Sequence[Sequence[int]]) -> str:
    return "=".join(_segment_key(pair) for pair in sorted(_normalize_pair(pair) for pair in pairs))


def _segment_key(pair: Sequence[int]) -> str:
    normalized = _normalize_pair(pair)
    return f"D[{normalized[0]},{normalized[1]}]"


def _normalize_pair(pair: Sequence[int]) -> tuple[int, int]:
    items = [int(item) for item in pair]
    if len(items) != 2 or items[0] == items[1]:
        raise AssertionError(f"{pair!r} is not a valid unordered pair")
    a, b = sorted(items)
    return a, b


def _cyclic_gap(pair: Sequence[int]) -> int:
    a, b = _normalize_pair(pair)
    delta = abs(b - a)
    return min(delta, N - delta)


def _segment_kind(gap: int) -> str:
    if gap == 1:
        return "hull_edge"
    return f"cyclic_gap_{gap}_diagonal"


def _validate_source_obligations(
    source_obligations: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "schema": SOURCE_OBLIGATIONS_SCHEMA,
        "status": SOURCE_OBLIGATIONS_STATUS,
        "trust": TRUST,
    }
    for key, expected_value in expected.items():
        if source_obligations.get(key) != expected_value:
            errors.append(
                "source obligations "
                f"{key} mismatch: expected {expected_value!r}, "
                f"got {source_obligations.get(key)!r}"
            )
    summary = _mapping(source_obligations.get("summary"), "source summary", errors)
    expected_counts = {
        "unique_edge_obligation_count": 7,
        "unique_path_motif_count": 6,
        "obligation_status": SOURCE_OBLIGATION_STATUS,
    }
    for key, expected_value in expected_counts.items():
        if summary.get(key) != expected_value:
            errors.append(
                "source obligations "
                f"summary.{key} mismatch: expected {expected_value!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, got {summary.get(key)!r}"
            )


def _validate_component_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != EXPECTED_SUMMARY["length_component_count"]:
        errors.append("length_component_records length mismatch")
    seen: set[str] = set()
    cascade_seen = False
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"length_component_records[{index}] must be an object")
            continue
        key = record.get("component_key")
        if not isinstance(key, str) or not key:
            errors.append(f"length_component_records[{index}] component key missing")
            continue
        if key in seen:
            errors.append(f"length_component_records[{index}] duplicate component key")
        seen.add(key)
        segments = record.get("segments")
        if not isinstance(segments, list) or len(segments) != record.get("segment_count"):
            errors.append(f"length_component_records[{index}] segment count mismatch")
            continue
        if any(
            not isinstance(segment, Mapping) or segment.get("contains_label8")
            for segment in segments
        ):
            errors.append(f"length_component_records[{index}] must be label-8-free")
        expected_geometry = _component_geometry_class(
            [segment for segment in segments if isinstance(segment, Mapping)]
        )
        if record.get("geometry_class") != expected_geometry:
            errors.append(f"length_component_records[{index}] geometry class mismatch")
        if key == EXPECTED_SUMMARY["cascade_component_key"]:
            cascade_seen = True
            if not record.get("contains_row6_connector_step"):
                errors.append("cascade component must contain the row-6 connector step")
    if not cascade_seen:
        errors.append("cascade component missing")


def _validate_segment_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != EXPECTED_SUMMARY["unique_segment_count"]:
        errors.append("segment_records length mismatch")
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"segment_records[{index}] must be an object")
            continue
        key = record.get("segment_key")
        if not isinstance(key, str) or not key:
            errors.append(f"segment_records[{index}] segment key missing")
            continue
        if key in seen:
            errors.append(f"segment_records[{index}] duplicate segment key")
        seen.add(key)
        pair = record.get("pair")
        if not isinstance(pair, list):
            errors.append(f"segment_records[{index}] pair must be a list")
            continue
        gap = _cyclic_gap(pair)
        if record.get("cyclic_gap") != gap:
            errors.append(f"segment_records[{index}] cyclic gap mismatch")
        if record.get("segment_kind") != _segment_kind(gap):
            errors.append(f"segment_records[{index}] segment kind mismatch")


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary")
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "obligation_status": (
            summary.get("obligation_status") if isinstance(summary, Mapping) else None
        ),
    }


def _mapping(value: object, name: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be an object")
        return {}
    return value


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--source-obligations",
        type=Path,
        default=DEFAULT_SOURCE_OBLIGATIONS,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_obligations = _resolve(args.source_obligations)

    generated = build_label4_transfer_length_components_payload(
        load_artifact(source_obligations),
        source_obligations_path=source_obligations,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        source_obligations_path=source_obligations,
    )
    if args.assert_expected:
        assert_expected_label4_transfer_length_components(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 transfer length components")
        print(f"target row: {summary['target_row_key']}")
        print(f"length components: {summary['length_component_count']}")
        print(f"unique segments: {summary['unique_segment_count']}")
        print(f"cascade: {summary['cascade_component_key']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
