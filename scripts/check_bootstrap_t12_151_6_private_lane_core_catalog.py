#!/usr/bin/env python3
"""Check the bootstrap/T12 151:6 private-lane core catalogue."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from erdos97.json_io import write_json
from erdos97.path_display import display_path
from erdos97.vertex_circle_quotient_replay import (
    SelectedRow,
    replay_vertex_circle_quotient,
    result_to_json,
)

ROOT = Path(__file__).resolve().parents[1]

SCHEMA = "erdos97.bootstrap_t12_151_6_private_lane_core_catalog.v1"
STATUS = "BOOTSTRAP_T12_151_6_PRIVATE_LANE_CORE_CATALOG_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CATALOG_STATUS = "PRIVATE_HALO_ONLY_LANE_HAS_ROW6_THREE_ROW_STRICT_CYCLE_CORES"
CLAIM_SCOPE = (
    "Proof-mining diagnostic for the source-151 row-6 private-halo-only "
    "outside-pair lane. It extracts minimal vertex-circle obstruction cores "
    "from the 12 basic-filter survivors with target row [0,3,5,7] and records "
    "that every survivor has a three-row strict-cycle core including center 6. "
    "This does not prove outside-pair support existence, does not prove row "
    "forcing, does not prove pair [3,5] impossible, does not prove endpoint-8 "
    "forcing, does not prove n=9, does not prove the bridge, is not a "
    "counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_bootstrap_t12_151_6_private_lane_core_catalog.py",
    "command": (
        "python scripts/check_bootstrap_t12_151_6_private_lane_core_catalog.py "
        "--write --assert-expected"
    ),
}

DEFAULT_SOURCE_FULL_NEIGHBORHOOD = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.json"
)
DEFAULT_SOURCE_PREFLIGHT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_endpoint8_forcing_preflight.json"
)
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_private_lane_core_catalog.json"
)

SOURCE_FULL_SCHEMA = (
    "erdos97.bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.v1"
)
SOURCE_FULL_STATUS = (
    "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_FULL_NEIGHBORHOOD_VERTEX_CIRCLE_"
    "DIAGNOSTIC_ONLY"
)
SOURCE_PREFLIGHT_SCHEMA = (
    "erdos97.bootstrap_t12_151_6_endpoint8_forcing_preflight.v1"
)
SOURCE_PREFLIGHT_STATUS = (
    "BOOTSTRAP_T12_151_6_ENDPOINT8_FORCING_PREFLIGHT_DIAGNOSTIC_ONLY"
)

N = 9
CYCLIC_ORDER = list(range(N))
TARGET_ROW_KEY = "151:6"
TARGET_CENTER = 6
PRIVATE_TARGET_CLASS = [0, 3, 5, 7]
PRIVATE_SUPPORT_PAIR = [3, 5]
EXPECTED_SOURCE_STATUS_COUNTS = {"self_edge": 10, "strict_cycle": 2}
EXPECTED_TOP_LEVEL_KEYS = {
    "catalog_records",
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
}
EXPECTED_SUMMARY = {
    "target_row_key": TARGET_ROW_KEY,
    "target_center": TARGET_CENTER,
    "private_target_center_class": PRIVATE_TARGET_CLASS,
    "private_support_pair": PRIVATE_SUPPORT_PAIR,
    "source_private_lane_survivor_count": 12,
    "source_vertex_circle_status_counts": EXPECTED_SOURCE_STATUS_COUNTS,
    "all_minimal_core_occurrence_count": 282,
    "all_minimal_core_size_counts": {"3": 124, "4": 144, "5": 14},
    "all_minimal_core_status_counts": {"self_edge": 42, "strict_cycle": 240},
    "row6_minimal_core_occurrence_count": 118,
    "row6_minimal_core_size_counts": {"3": 48, "4": 64, "5": 6},
    "row6_minimal_core_status_counts": {"self_edge": 6, "strict_cycle": 112},
    "assignments_with_row6_minimal_core": 12,
    "assignments_with_row6_three_row_core": 12,
    "chosen_row6_core_count": 12,
    "chosen_row6_core_size_counts": {"3": 12},
    "chosen_row6_core_status_counts": {"strict_cycle": 12},
    "chosen_distinct_exact_core_count": 10,
    "catalog_status": CATALOG_STATUS,
}


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def build_private_lane_core_catalog_payload(
    full_neighborhood: Mapping[str, Any],
    preflight: Mapping[str, Any],
    *,
    full_neighborhood_path: Path = DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    preflight_path: Path = DEFAULT_SOURCE_PREFLIGHT,
) -> dict[str, Any]:
    """Return the deterministic private-lane core catalogue payload."""

    errors: list[str] = []
    _validate_source_full_neighborhood(full_neighborhood, errors)
    _validate_source_preflight(preflight, errors)
    survivors = _private_lane_survivors(full_neighborhood, errors)
    records, summary = _catalogue(survivors)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "catalog_records": records,
        "source_artifacts": [
            _source_summary(
                full_neighborhood_path,
                "source 151:6 outside-pair full-neighborhood packet",
                full_neighborhood,
            ),
            _source_summary(
                preflight_path,
                "source 151:6 endpoint-8 forcing preflight",
                preflight,
            ),
        ],
        "interpretation": [
            (
                "The selected-row private lane is sharper than the aggregate "
                "partition: all 12 survivors use row 6 -> [0,3,5,7]."
            ),
            (
                "Each survivor has a three-row strict-cycle core that includes "
                "that row-6 private-lane support."
            ),
            (
                "These cores are local obstruction targets inside the selected-"
                "row diagnostic; they do not prove support existence or row "
                "forcing."
            ),
            (
                "The remaining proof-facing task is still genuine minimal/"
                "rich-class support geometry for endpoint 8 versus [3,5]."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_private_lane_core_catalog(payload)
    return payload


def assert_expected_private_lane_core_catalog(payload: Mapping[str, Any]) -> None:
    """Assert the pinned private-lane core catalogue."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    full_neighborhood_path: Path = DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    preflight_path: Path = DEFAULT_SOURCE_PREFLIGHT,
) -> list[str]:
    """Return validation errors for a private-lane core catalogue payload."""

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
    records = payload.get("catalog_records")
    if not isinstance(records, list):
        errors.append("catalog_records must be a list")
    else:
        _validate_catalog_records(records, errors)
    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("do not prove support existence" in item for item in interpretation):
        errors.append("interpretation must preserve the support-existence nonclaim")

    if recompute and not errors:
        generated = build_private_lane_core_catalog_payload(
            load_artifact(full_neighborhood_path),
            load_artifact(preflight_path),
            full_neighborhood_path=full_neighborhood_path,
            preflight_path=preflight_path,
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
        "source_private_lane_survivor_count": summary.get(
            "source_private_lane_survivor_count"
        ),
        "all_minimal_core_occurrence_count": summary.get(
            "all_minimal_core_occurrence_count"
        ),
        "row6_minimal_core_occurrence_count": summary.get(
            "row6_minimal_core_occurrence_count"
        ),
        "assignments_with_row6_three_row_core": summary.get(
            "assignments_with_row6_three_row_core"
        ),
        "chosen_row6_core_status_counts": summary.get(
            "chosen_row6_core_status_counts"
        ),
        "catalog_status": summary.get("catalog_status"),
        "validation_errors": list(errors),
    }


def _catalogue(
    survivors: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    all_minimal_size_counts: Counter[int] = Counter()
    all_minimal_status_counts: Counter[str] = Counter()
    row6_size_counts: Counter[int] = Counter()
    row6_status_counts: Counter[str] = Counter()
    chosen_size_counts: Counter[int] = Counter()
    chosen_status_counts: Counter[str] = Counter()
    chosen_keys: Counter[tuple[tuple[int, tuple[int, ...]], ...]] = Counter()
    assignments_with_row6_core = 0
    assignments_with_row6_three_row_core = 0

    for index, survivor in enumerate(survivors):
        selected_rows = _selected_rows(survivor)
        minimal = _minimal_cores(selected_rows)
        row6_minimal = [core for core in minimal if TARGET_CENTER in core.centers]
        if row6_minimal:
            assignments_with_row6_core += 1
        if any(len(core.centers) == 3 for core in row6_minimal):
            assignments_with_row6_three_row_core += 1

        for core in minimal:
            all_minimal_size_counts[len(core.centers)] += 1
            all_minimal_status_counts[core.status] += 1
        for core in row6_minimal:
            row6_size_counts[len(core.centers)] += 1
            row6_status_counts[core.status] += 1

        chosen = _choose_row6_core(row6_minimal)
        chosen_size_counts[len(chosen.centers)] += 1
        chosen_status_counts[chosen.status] += 1
        chosen_keys[_core_key(selected_rows, chosen.centers)] += 1
        replay_json = result_to_json(
            _replay(selected_rows, chosen.centers)
        )
        records.append(
            {
                "assignment_index": index,
                "source_vertex_circle_status": str(
                    survivor["vertex_circle_status"]
                ),
                "minimal_core_count": len(minimal),
                "minimal_core_size_counts": _json_counter(
                    Counter(len(core.centers) for core in minimal)
                ),
                "row6_minimal_core_count": len(row6_minimal),
                "row6_minimal_core_size_counts": _json_counter(
                    Counter(len(core.centers) for core in row6_minimal)
                ),
                "chosen_core_centers": list(chosen.centers),
                "chosen_core_status": chosen.status,
                "chosen_core_rows": [
                    {
                        "center": center,
                        "witnesses": list(selected_rows[center]),
                    }
                    for center in chosen.centers
                ],
                "chosen_core_strict_edge_count": replay_json["strict_edge_count"],
                "chosen_core_cycle_edge_count": len(replay_json["cycle_edges"]),
                "chosen_core_self_edge_count": len(
                    replay_json["self_edge_conflicts"]
                ),
                "chosen_core_cycle_edges": replay_json["cycle_edges"],
            }
        )

    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "source_private_lane_survivor_count": len(survivors),
        "source_vertex_circle_status_counts": _json_counter(
            Counter(str(row["vertex_circle_status"]) for row in survivors)
        ),
        "all_minimal_core_occurrence_count": sum(all_minimal_size_counts.values()),
        "all_minimal_core_size_counts": _json_counter(all_minimal_size_counts),
        "all_minimal_core_status_counts": _json_counter(all_minimal_status_counts),
        "row6_minimal_core_occurrence_count": sum(row6_size_counts.values()),
        "row6_minimal_core_size_counts": _json_counter(row6_size_counts),
        "row6_minimal_core_status_counts": _json_counter(row6_status_counts),
        "assignments_with_row6_minimal_core": assignments_with_row6_core,
        "assignments_with_row6_three_row_core": assignments_with_row6_three_row_core,
        "chosen_row6_core_count": len(records),
        "chosen_row6_core_size_counts": _json_counter(chosen_size_counts),
        "chosen_row6_core_status_counts": _json_counter(chosen_status_counts),
        "chosen_distinct_exact_core_count": len(chosen_keys),
        "catalog_status": CATALOG_STATUS,
    }
    return records, summary


class _Core(tuple):
    @property
    def centers(self) -> tuple[int, ...]:
        return self[0]

    @property
    def status(self) -> str:
        return self[1]


def _minimal_cores(selected_rows: Mapping[int, tuple[int, ...]]) -> list[_Core]:
    centers = sorted(selected_rows)
    minimal: list[_Core] = []
    for size in range(2, len(centers) + 1):
        for combo in itertools.combinations(centers, size):
            center_set = set(combo)
            if any(set(core.centers) <= center_set for core in minimal):
                continue
            status = _replay(selected_rows, combo).status
            if status != "ok":
                minimal.append(_Core((tuple(combo), status)))
    return minimal


def _choose_row6_core(cores: Sequence[_Core]) -> _Core:
    if not cores:
        raise AssertionError("private-lane survivor has no row-6 minimal core")
    return min(
        cores,
        key=lambda core: (
            len(core.centers),
            core.status != "strict_cycle",
            core.centers,
        ),
    )


def _replay(
    selected_rows: Mapping[int, tuple[int, ...]],
    centers: Sequence[int],
) -> Any:
    rows = [
        SelectedRow(center=center, witnesses=selected_rows[center])
        for center in centers
    ]
    return replay_vertex_circle_quotient(N, CYCLIC_ORDER, rows)


def _validate_catalog_records(records: Sequence[object], errors: list[str]) -> None:
    if len(records) != EXPECTED_SUMMARY["chosen_row6_core_count"]:
        errors.append("catalog_records length mismatch")
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"catalog_records[{index}] must be an object")
            continue
        if record.get("assignment_index") != index:
            errors.append(f"catalog_records[{index}] assignment_index mismatch")
        if record.get("chosen_core_status") != "strict_cycle":
            errors.append(f"catalog_records[{index}] chosen core must be strict_cycle")
        if record.get("chosen_core_centers") is None:
            errors.append(f"catalog_records[{index}] missing chosen_core_centers")
            continue
        centers = tuple(int(center) for center in record["chosen_core_centers"])
        if len(centers) != 3 or TARGET_CENTER not in centers:
            errors.append(
                f"catalog_records[{index}] chosen core must be a 3-row core with row 6"
            )
        if record.get("chosen_core_self_edge_count") != 0:
            errors.append(f"catalog_records[{index}] chosen core has a self edge")
        if int(record.get("chosen_core_cycle_edge_count", 0)) <= 0:
            errors.append(f"catalog_records[{index}] chosen core has no cycle edges")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, got {summary.get(key)!r}"
            )


def _validate_source_full_neighborhood(
    payload: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "schema": SOURCE_FULL_SCHEMA,
        "status": SOURCE_FULL_STATUS,
        "trust": TRUST,
    }
    _validate_source_meta("full-neighborhood source", payload, expected, errors)
    summary = _mapping(payload.get("summary"), "full-neighborhood summary", errors)
    if not summary:
        return
    expected_summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "outside_support_pairs": [[3, 5], [3, 8], [5, 8]],
        "vertex_circle_surviving_assignment_count": 0,
        "scan_status": "FULL_NEIGHBORHOOD_BASIC_SURVIVORS_ALL_VERTEX_CIRCLE_OBSTRUCTED",
    }
    _expect_fields("full-neighborhood summary", summary, expected_summary, errors)


def _validate_source_preflight(
    payload: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "schema": SOURCE_PREFLIGHT_SCHEMA,
        "status": SOURCE_PREFLIGHT_STATUS,
        "trust": TRUST,
    }
    _validate_source_meta("endpoint-8 preflight source", payload, expected, errors)
    summary = _mapping(payload.get("summary"), "endpoint-8 preflight summary", errors)
    if not summary:
        return
    expected_summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "blocking_escape_support_pairs": [PRIVATE_SUPPORT_PAIR],
        "private_halo_only_basic_survivor_count": 12,
        "endpoint8_forced_by_current_evidence": False,
        "endpoint8_forcing_blocked_by_private_halo_escape": True,
    }
    _expect_fields("endpoint-8 preflight summary", summary, expected_summary, errors)


def _private_lane_survivors(
    payload: Mapping[str, Any],
    errors: list[str],
) -> list[Mapping[str, Any]]:
    per_target = payload.get("per_target_center_class")
    if not isinstance(per_target, list):
        errors.append("source per_target_center_class must be a list")
        return []
    matches = [
        record
        for record in per_target
        if isinstance(record, Mapping)
        and record.get("target_center_class") == PRIVATE_TARGET_CLASS
    ]
    if len(matches) != 1:
        errors.append("expected exactly one private target-center class record")
        return []
    record = matches[0]
    if record.get("basic_filter_complete_assignment_count") != 12:
        errors.append("private target-center class must have 12 survivors")
    if record.get("vertex_circle_status_counts") != EXPECTED_SOURCE_STATUS_COUNTS:
        errors.append("private target-center class status counts drifted")
    survivors = record.get("basic_filter_survivors")
    if not isinstance(survivors, list):
        errors.append("private target-center class survivors must be a list")
        return []
    return [survivor for survivor in survivors if isinstance(survivor, Mapping)]


def _selected_rows(survivor: Mapping[str, Any]) -> dict[int, tuple[int, ...]]:
    raw_rows = survivor.get("selected_rows")
    if not isinstance(raw_rows, Mapping):
        raise AssertionError("survivor selected_rows must be an object")
    rows = {
        int(center): tuple(int(witness) for witness in witnesses)
        for center, witnesses in raw_rows.items()
    }
    target = rows.get(TARGET_CENTER)
    if list(target or ()) != PRIVATE_TARGET_CLASS:
        raise AssertionError("survivor row 6 does not match private target class")
    return rows


def _core_key(
    selected_rows: Mapping[int, tuple[int, ...]],
    centers: Sequence[int],
) -> tuple[tuple[int, tuple[int, ...]], ...]:
    return tuple((center, selected_rows[center]) for center in centers)


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
    }


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


def _expect_fields(
    label: str,
    mapping: Mapping[str, Any],
    expected: Mapping[str, object],
    errors: list[str],
) -> None:
    for key, expected_value in expected.items():
        if mapping.get(key) != expected_value:
            errors.append(
                f"{label}.{key} mismatch: expected {expected_value!r}, "
                f"got {mapping.get(key)!r}"
            )


def _mapping(value: object, name: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be an object")
        return {}
    return value


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


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
        "--source-preflight",
        type=Path,
        default=DEFAULT_SOURCE_PREFLIGHT,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_full_neighborhood = _resolve(args.source_full_neighborhood)
    source_preflight = _resolve(args.source_preflight)

    generated = build_private_lane_core_catalog_payload(
        load_artifact(source_full_neighborhood),
        load_artifact(source_preflight),
        full_neighborhood_path=source_full_neighborhood,
        preflight_path=source_preflight,
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
        preflight_path=source_preflight,
    )
    if args.assert_expected:
        assert_expected_private_lane_core_catalog(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 private-lane core catalogue")
        print(f"target row: {summary['target_row_key']}")
        print(
            "private-lane survivors: "
            f"{summary['source_private_lane_survivor_count']}"
        )
        print(
            "row-6 minimal cores: "
            f"{summary['row6_minimal_core_occurrence_count']}"
        )
        print(
            "assignments with row-6 three-row core: "
            f"{summary['assignments_with_row6_three_row_core']}"
        )
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: 151:6 private-lane core catalogue verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
