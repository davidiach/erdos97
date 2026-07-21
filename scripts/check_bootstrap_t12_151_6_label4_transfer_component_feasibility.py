#!/usr/bin/env python3
"""Check cyclic-arc witnesses for the 151:6 label-4 length components."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erdos97.json_io import write_json  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402

from scripts.check_bootstrap_t12_151_6_label4_transfer_length_components import (  # noqa: E402
    COMPONENT_STATUS as SOURCE_COMPONENT_STATUS,
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_COMPONENTS,
    SCHEMA as SOURCE_COMPONENTS_SCHEMA,
    STATUS as SOURCE_COMPONENTS_STATUS,
    assert_expected_label4_transfer_length_components,
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
MAX_SEARCH_MODULUS = 32

SCHEMA = "erdos97.bootstrap_t12_151_6_label4_transfer_component_feasibility.v1"
STATUS = (
    "BOOTSTRAP_T12_151_6_LABEL4_TRANSFER_COMPONENT_FEASIBILITY_NEGATIVE_CONTROLS"
)
FEASIBILITY_STATUS = "COMPONENT_ALONE_IMPOSSIBILITY_REJECTED"
CLAIM_SCOPE = (
    "Exact negative-control diagnostic for the source-151 row-6 "
    "private-halo-only label-4 transfer length components. For each of the "
    "six components, considered one at a time, the packet gives positive "
    "integer cyclic arc gaps for a strict cyclic convex 9-gon whose listed "
    "segments have equal chord length. This rejects component-alone "
    "impossibility claims only. It does not give one polygon realizing all "
    "six components at once, does not prove outside-pair support existence, "
    "does not prove row forcing, does not prove pair [3,5] impossible, does "
    "not prove endpoint-8 forcing, does not prove n=9, does not prove the "
    "bridge, is not a counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/check_bootstrap_t12_151_6_label4_transfer_component_feasibility.py"
    ),
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label4_transfer_component_feasibility.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_transfer_component_feasibility.json"
)

EXPECTED_WITNESSES = {
    "D[0,5]=D[4,5]": {
        "regular_polygon_modulus": 12,
        "arc_units_by_gap": [1, 1, 1, 1, 4, 1, 1, 1, 1],
        "common_minor_arc_units": 4,
    },
    "D[0,6]=D[4,5]=D[5,6]": {
        "regular_polygon_modulus": 13,
        "arc_units_by_gap": [1, 1, 1, 1, 3, 3, 1, 1, 1],
        "common_minor_arc_units": 3,
    },
    "D[1,7]=D[4,7]": {
        "regular_polygon_modulus": 9,
        "arc_units_by_gap": [1, 1, 1, 1, 1, 1, 1, 1, 1],
        "common_minor_arc_units": 3,
    },
    "D[2,5]=D[4,5]": {
        "regular_polygon_modulus": 14,
        "arc_units_by_gap": [1, 1, 1, 1, 6, 1, 1, 1, 1],
        "common_minor_arc_units": 6,
    },
    "D[2,7]=D[4,7]": {
        "regular_polygon_modulus": 10,
        "arc_units_by_gap": [1, 1, 1, 1, 1, 1, 2, 1, 1],
        "common_minor_arc_units": 4,
    },
    "D[4,5]=D[5,7]": {
        "regular_polygon_modulus": 10,
        "arc_units_by_gap": [1, 1, 1, 1, 2, 1, 1, 1, 1],
        "common_minor_arc_units": 2,
    },
}

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "interpretation",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "summary",
    "trust",
    "validation_errors",
    "validation_status",
    "witness_records",
}
EXPECTED_SUMMARY = {
    "target_row_key": TARGET_ROW_KEY,
    "target_center": TARGET_CENTER,
    "private_target_center_class": PRIVATE_TARGET_CLASS,
    "private_support_pair": PRIVATE_SUPPORT_PAIR,
    "source_length_component_count": 6,
    "source_unique_segment_count": 9,
    "witness_record_count": 6,
    "feasible_component_count": 6,
    "component_alone_obstruction_status": FEASIBILITY_STATUS,
    "simultaneous_component_witness_status": "not_checked",
    "regular_arc_witness_class": "strict_cyclic_convex_9_gon_from_regular_m_gon",
    "min_regular_polygon_modulus": 9,
    "max_regular_polygon_modulus": 14,
    "max_search_modulus": MAX_SEARCH_MODULUS,
    "regular_polygon_modulus_counts": {
        "9": 1,
        "10": 2,
        "12": 1,
        "13": 1,
        "14": 1,
    },
    "common_minor_arc_unit_counts": {
        "2": 1,
        "3": 2,
        "4": 2,
        "6": 1,
    },
    "component_count_by_geometry_class": {
        "diagonal_only_equality": 2,
        "edge_diagonal_equality": 3,
        "edge_edge_diagonal_chain": 1,
    },
    "component_with_row6_connector_step_count": 1,
    "component_with_target_center_count": 1,
    "cascade_component_key": "D[0,6]=D[4,5]=D[5,6]",
    "cascade_witness_modulus": 13,
    "cascade_witness_minor_arc_units": 3,
    "source_component_status": SOURCE_COMPONENT_STATUS,
}


def build_component_feasibility_payload(
    source_components: Mapping[str, Any],
    *,
    source_components_path: Path = DEFAULT_SOURCE_COMPONENTS,
) -> dict[str, Any]:
    """Return the deterministic cyclic-arc feasibility payload."""

    errors: list[str] = []
    assert_expected_label4_transfer_length_components(source_components)
    _validate_source_components(source_components, errors)
    witness_records, summary = _witness_records(source_components)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "witness_records": witness_records,
        "source_artifacts": [
            _source_summary(
                source_components_path,
                "source 151:6 label-4 transfer length components",
                source_components,
            )
        ],
        "interpretation": [
            (
                "Each witness places the nine labels on a common circle at "
                "integer arc positions modulo M, with every adjacent label "
                "gap positive."
            ),
            (
                "On a common circle, chord length is determined by the minor "
                "arc. The checker verifies that all segments in each component "
                "have the same minor arc units."
            ),
            (
                "The six witnesses are component-alone negative controls. "
                "They do not assert that one cyclic polygon realizes all six "
                "components simultaneously."
            ),
            (
                "A successful obstruction for the source-151 row-6 private "
                "lane must therefore use additional private-support, "
                "rich-class, or row-forcing hypotheses."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_component_feasibility(payload)
    return payload


def assert_expected_component_feasibility(payload: Mapping[str, Any]) -> None:
    """Assert the pinned component-alone feasibility negative controls."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    source_components_path: Path = DEFAULT_SOURCE_COMPONENTS,
) -> list[str]:
    """Return validation errors for a component-feasibility payload."""

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
            "rejects component-alone impossibility claims only",
            "does not give one polygon realizing all six components at once",
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
    witness_records = payload.get("witness_records")
    if not isinstance(witness_records, list):
        errors.append("witness_records must be a list")
    else:
        _validate_witness_records(witness_records, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any(
        "do not assert that one cyclic polygon realizes all six" in str(item)
        for item in interpretation
    ):
        errors.append("interpretation must preserve the simultaneous-witness nonclaim")

    if recompute and not errors:
        generated = build_component_feasibility_payload(
            load_artifact(source_components_path),
            source_components_path=source_components_path,
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
        "witness_record_count": summary.get("witness_record_count"),
        "feasible_component_count": summary.get("feasible_component_count"),
        "component_alone_obstruction_status": summary.get(
            "component_alone_obstruction_status"
        ),
        "simultaneous_component_witness_status": summary.get(
            "simultaneous_component_witness_status"
        ),
        "cascade_component_key": summary.get("cascade_component_key"),
        "cascade_witness_modulus": summary.get("cascade_witness_modulus"),
        "validation_errors": list(errors),
    }


def _witness_records(
    source_components: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    geometry_counts: Counter[str] = Counter()
    modulus_counts: Counter[int] = Counter()
    minor_unit_counts: Counter[int] = Counter()
    row6_connector_count = 0
    target_center_count = 0

    for component in source_components["length_component_records"]:
        component_key = str(component["component_key"])
        segments = [
            _component_segment(segment)
            for segment in component["segments"]
            if isinstance(segment, Mapping)
        ]
        witness = _find_regular_arc_witness(segments)
        record = _build_witness_record(component, segments, witness)
        records.append(record)
        geometry_counts[str(component["geometry_class"])] += 1
        modulus_counts[int(record["regular_polygon_modulus"])] += 1
        minor_unit_counts[int(record["common_minor_arc_units"])] += 1
        if component.get("contains_row6_connector_step"):
            row6_connector_count += 1
        if component.get("contains_target_center"):
            target_center_count += 1

        expected = EXPECTED_WITNESSES.get(component_key)
        if expected is None:
            raise AssertionError(f"unexpected component {component_key!r}")
        pinned = {
            "regular_polygon_modulus": record["regular_polygon_modulus"],
            "arc_units_by_gap": record["arc_units_by_gap"],
            "common_minor_arc_units": record["common_minor_arc_units"],
        }
        if pinned != expected:
            raise AssertionError(
                f"{component_key} witness mismatch: expected {expected!r}, "
                f"got {pinned!r}"
            )

    records = sorted(records, key=lambda item: item["component_key"])
    cascade = next(
        record
        for record in records
        if record["component_key"] == EXPECTED_SUMMARY["cascade_component_key"]
    )
    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "source_length_component_count": source_components["summary"][
            "length_component_count"
        ],
        "source_unique_segment_count": source_components["summary"][
            "unique_segment_count"
        ],
        "witness_record_count": len(records),
        "feasible_component_count": sum(
            1 for record in records if record["witness_status"] == "feasible"
        ),
        "component_alone_obstruction_status": FEASIBILITY_STATUS,
        "simultaneous_component_witness_status": "not_checked",
        "regular_arc_witness_class": "strict_cyclic_convex_9_gon_from_regular_m_gon",
        "min_regular_polygon_modulus": min(modulus_counts),
        "max_regular_polygon_modulus": max(modulus_counts),
        "max_search_modulus": MAX_SEARCH_MODULUS,
        "regular_polygon_modulus_counts": _json_counter(modulus_counts),
        "common_minor_arc_unit_counts": _json_counter(minor_unit_counts),
        "component_count_by_geometry_class": _json_counter(geometry_counts),
        "component_with_row6_connector_step_count": row6_connector_count,
        "component_with_target_center_count": target_center_count,
        "cascade_component_key": cascade["component_key"],
        "cascade_witness_modulus": cascade["regular_polygon_modulus"],
        "cascade_witness_minor_arc_units": cascade["common_minor_arc_units"],
        "source_component_status": SOURCE_COMPONENT_STATUS,
    }
    return records, summary


def _build_witness_record(
    component: Mapping[str, Any],
    segments: Sequence[Mapping[str, Any]],
    witness: Mapping[str, Any],
) -> dict[str, Any]:
    modulus = int(witness["regular_polygon_modulus"])
    arcs = list(witness["arc_units_by_gap"])
    positions = _vertex_arc_positions(arcs)
    segment_arc_records = [
        _segment_arc_record(segment, arcs, modulus) for segment in segments
    ]
    common_minor_units = {
        int(record["minor_arc_units"]) for record in segment_arc_records
    }
    if len(common_minor_units) != 1:
        raise AssertionError(f"{component['component_key']} does not have equal arcs")
    common_minor = next(iter(common_minor_units))
    return {
        "component_key": component["component_key"],
        "source_path_motif_key": component["source_path_motif_key"],
        "path_shape": component["path_shape"],
        "geometry_class": component["geometry_class"],
        "contains_row6_connector_step": component["contains_row6_connector_step"],
        "contains_target_center": component["contains_target_center"],
        "component_segments": list(segments),
        "witness_status": "feasible",
        "witness_scope": "component_alone_only",
        "regular_polygon_modulus": modulus,
        "arc_units_by_gap": arcs,
        "vertex_arc_positions": positions,
        "common_minor_arc_units": common_minor,
        "segment_arc_records": segment_arc_records,
        "exact_chord_length_identifier": f"2*sin({common_minor}*pi/{modulus})",
        "strict_convexity_reason": (
            "All adjacent label gaps are positive, so the nine labels are "
            "distinct and cyclically ordered on a common circle."
        ),
        "equal_length_reason": (
            "All listed segments have the same minor arc units on the common "
            "circle, hence the same chord length."
        ),
    }


def _find_regular_arc_witness(
    segments: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    pairs = [tuple(int(item) for item in segment["pair"]) for segment in segments]
    for modulus in range(N, MAX_SEARCH_MODULUS + 1):
        for arcs in _positive_compositions(modulus, N):
            minor_units = [_minor_arc_units(arcs, pair) for pair in pairs]
            if len(set(minor_units)) == 1:
                return {
                    "regular_polygon_modulus": modulus,
                    "arc_units_by_gap": list(arcs),
                    "common_minor_arc_units": minor_units[0],
                }
    raise AssertionError(f"no cyclic-arc witness found for {pairs!r}")


def _positive_compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        if total >= 1:
            yield (total,)
        return
    max_first = total - (parts - 1)
    for first in range(1, max_first + 1):
        for rest in _positive_compositions(total - first, parts - 1):
            yield (first, *rest)


def _component_segment(segment: Mapping[str, Any]) -> dict[str, Any]:
    pair = _normalize_pair(segment["pair"])
    return {
        "segment_key": segment["segment_key"],
        "pair": list(pair),
        "cyclic_gap": segment["cyclic_gap"],
        "segment_kind": segment["segment_kind"],
        "contains_label4": segment["contains_label4"],
        "contains_label8": segment["contains_label8"],
        "contains_target_center": segment["contains_target_center"],
    }


def _segment_arc_record(
    segment: Mapping[str, Any],
    arcs: Sequence[int],
    modulus: int,
) -> dict[str, Any]:
    pair = _normalize_pair(segment["pair"])
    forward = _forward_arc_units(arcs, pair[0], pair[1])
    reverse = modulus - forward
    minor = min(forward, reverse)
    return {
        "segment_key": segment["segment_key"],
        "pair": list(pair),
        "forward_arc_units": forward,
        "reverse_arc_units": reverse,
        "minor_arc_units": minor,
    }


def _vertex_arc_positions(arcs: Sequence[int]) -> list[int]:
    positions = [0]
    current = 0
    for gap in arcs[:-1]:
        current += int(gap)
        positions.append(current)
    return positions


def _minor_arc_units(arcs: Sequence[int], pair: Sequence[int]) -> int:
    pair = _normalize_pair(pair)
    forward = _forward_arc_units(arcs, pair[0], pair[1])
    return min(forward, sum(arcs) - forward)


def _forward_arc_units(arcs: Sequence[int], start: int, stop: int) -> int:
    total = 0
    index = start
    while index != stop:
        total += int(arcs[index])
        index = (index + 1) % N
    return total


def _normalize_pair(pair: Sequence[int]) -> tuple[int, int]:
    items = [int(item) for item in pair]
    if len(items) != 2 or items[0] == items[1]:
        raise AssertionError(f"{pair!r} is not a valid unordered pair")
    return tuple(sorted(items))


def _validate_source_components(
    source_components: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "schema": SOURCE_COMPONENTS_SCHEMA,
        "status": SOURCE_COMPONENTS_STATUS,
        "trust": TRUST,
    }
    for key, expected_value in expected.items():
        if source_components.get(key) != expected_value:
            errors.append(
                "source length components "
                f"{key} mismatch: expected {expected_value!r}, "
                f"got {source_components.get(key)!r}"
            )
    summary = _mapping(source_components.get("summary"), "source summary", errors)
    expected_counts = {
        "length_component_count": 6,
        "unique_segment_count": 9,
        "component_status": SOURCE_COMPONENT_STATUS,
    }
    for key, expected_value in expected_counts.items():
        if summary.get(key) != expected_value:
            errors.append(
                "source length components "
                f"summary.{key} mismatch: expected {expected_value!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, got {summary.get(key)!r}"
            )


def _validate_witness_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != EXPECTED_SUMMARY["witness_record_count"]:
        errors.append("witness_records length mismatch")
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"witness_records[{index}] must be an object")
            continue
        key = record.get("component_key")
        if not isinstance(key, str) or not key:
            errors.append(f"witness_records[{index}] component key missing")
            continue
        if key in seen:
            errors.append(f"witness_records[{index}] duplicate component key")
        seen.add(key)
        _validate_witness_record(index, record, errors)
    if seen != set(EXPECTED_WITNESSES):
        errors.append(
            f"witness component keys mismatch: expected {sorted(EXPECTED_WITNESSES)!r}, "
            f"got {sorted(seen)!r}"
        )


def _validate_witness_record(
    index: int,
    record: Mapping[str, Any],
    errors: list[str],
) -> None:
    key = str(record.get("component_key"))
    expected = EXPECTED_WITNESSES.get(key)
    if expected is None:
        errors.append(f"witness_records[{index}] unexpected component {key!r}")
        return
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(
                f"witness_records[{index}].{field} mismatch: "
                f"expected {expected_value!r}, got {record.get(field)!r}"
            )

    arcs = record.get("arc_units_by_gap")
    modulus = record.get("regular_polygon_modulus")
    if not isinstance(arcs, list) or len(arcs) != N or not all(
        isinstance(item, int) and item > 0 for item in arcs
    ):
        errors.append(f"witness_records[{index}] arc_units_by_gap must be positive")
        return
    if sum(arcs) != modulus:
        errors.append(f"witness_records[{index}] arc units must sum to modulus")

    positions = record.get("vertex_arc_positions")
    if positions != _vertex_arc_positions(arcs):
        errors.append(f"witness_records[{index}] vertex positions mismatch")

    segments = record.get("component_segments")
    segment_arcs = record.get("segment_arc_records")
    if not isinstance(segments, list) or not isinstance(segment_arcs, list):
        errors.append(f"witness_records[{index}] segment records must be lists")
        return
    if len(segments) != len(segment_arcs):
        errors.append(f"witness_records[{index}] segment arc count mismatch")
        return

    minor_units: set[int] = set()
    for arc_record in segment_arcs:
        if not isinstance(arc_record, Mapping):
            errors.append(f"witness_records[{index}] bad segment arc record")
            continue
        pair = arc_record.get("pair")
        if not isinstance(pair, list):
            errors.append(f"witness_records[{index}] segment pair must be a list")
            continue
        expected_forward = _forward_arc_units(arcs, int(pair[0]), int(pair[1]))
        expected_reverse = int(modulus) - expected_forward
        expected_minor = min(expected_forward, expected_reverse)
        if arc_record.get("forward_arc_units") != expected_forward:
            errors.append(f"witness_records[{index}] forward arc mismatch")
        if arc_record.get("reverse_arc_units") != expected_reverse:
            errors.append(f"witness_records[{index}] reverse arc mismatch")
        if arc_record.get("minor_arc_units") != expected_minor:
            errors.append(f"witness_records[{index}] minor arc mismatch")
        minor_units.add(expected_minor)
    if minor_units != {expected["common_minor_arc_units"]}:
        errors.append(f"witness_records[{index}] common minor arc mismatch")


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary")
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "component_status": (
            summary.get("component_status") if isinstance(summary, Mapping) else None
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
        "--source-components",
        type=Path,
        default=DEFAULT_SOURCE_COMPONENTS,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_components = _resolve(args.source_components)

    generated = build_component_feasibility_payload(
        load_artifact(source_components),
        source_components_path=source_components,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        source_components_path=source_components,
    )
    if args.assert_expected:
        assert_expected_component_feasibility(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 transfer component feasibility")
        print(f"target row: {summary['target_row_key']}")
        print(f"witness records: {summary['witness_record_count']}")
        print(f"feasible components: {summary['feasible_component_count']}")
        print(f"cascade: {summary['cascade_component_key']}")
        print(f"cascade modulus: {summary['cascade_witness_modulus']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
