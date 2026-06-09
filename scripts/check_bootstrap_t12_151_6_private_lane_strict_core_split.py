#!/usr/bin/env python3
"""Check the bootstrap/T12 151:6 private-lane strict-core split."""

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

from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_CORE_CATALOG,
    DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    EXPECTED_SUMMARY as SOURCE_CORE_CATALOG_SUMMARY,
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    SCHEMA as SOURCE_CORE_CATALOG_SCHEMA,
    STATUS as SOURCE_CORE_CATALOG_STATUS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
    _core_key,
    _json_counter,
    _minimal_cores,
    _private_lane_survivors,
    _replay,
    _selected_rows,
    assert_expected_private_lane_core_catalog,
    load_artifact,
    result_to_json,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_private_lane_strict_core_split.v1"
STATUS = "BOOTSTRAP_T12_151_6_PRIVATE_LANE_STRICT_CORE_SPLIT_DIAGNOSTIC_ONLY"
SPLIT_STATUS = "PRIVATE_LANE_ROW6_STRICT_CORES_SPLIT_BY_LABEL8_VISIBILITY"
CLAIM_SCOPE = (
    "Proof-target diagnostic for the source-151 row-6 private-halo-only "
    "outside-pair lane. It splits the 44 row-6 three-row strict-cycle "
    "minimal cores by whether label 8 appears as an auxiliary-row witness. "
    "The split records 32 label-8-visible cores and 12 label-8-free cores. "
    "This does not prove outside-pair support existence, does not prove row "
    "forcing, does not prove pair [3,5] impossible, does not prove endpoint-8 "
    "forcing, does not prove n=9, does not prove the bridge, is not a "
    "counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_bootstrap_t12_151_6_private_lane_strict_core_split.py",
    "command": (
        "python scripts/check_bootstrap_t12_151_6_private_lane_strict_core_split.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_private_lane_strict_core_split.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "assignment_records",
    "claim_scope",
    "interpretation",
    "label8_free_core_signatures",
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
    "row6_three_row_strict_core_count": 44,
    "assignments_with_row6_three_row_strict_core": 12,
    "label8_visible_core_count": 32,
    "label8_free_core_count": 12,
    "assignments_with_label8_visible_core": 12,
    "assignments_with_label8_free_core": 8,
    "assignments_without_label8_free_core": 4,
    "center8_core_count": 9,
    "assignments_with_center8_core": 7,
    "label8_free_center8_core_count": 4,
    "distinct_exact_core_count": 36,
    "label8_visible_distinct_exact_core_count": 26,
    "label8_free_distinct_exact_core_count": 10,
    "auxiliary_center_pair_counts": {
        "0,1": 5,
        "0,2": 1,
        "0,3": 2,
        "0,5": 1,
        "0,7": 1,
        "0,8": 2,
        "1,3": 1,
        "1,5": 3,
        "1,7": 1,
        "2,3": 5,
        "2,5": 1,
        "2,7": 3,
        "3,4": 2,
        "3,5": 1,
        "3,7": 1,
        "4,5": 2,
        "4,7": 5,
        "5,8": 5,
        "7,8": 2,
    },
    "label8_visible_auxiliary_center_pair_counts": {
        "0,1": 5,
        "0,2": 1,
        "0,3": 2,
        "0,5": 1,
        "0,7": 1,
        "0,8": 2,
        "1,3": 1,
        "1,5": 3,
        "1,7": 1,
        "2,3": 2,
        "2,7": 2,
        "3,4": 2,
        "4,5": 1,
        "4,7": 5,
        "5,8": 1,
        "7,8": 2,
    },
    "label8_free_auxiliary_center_pair_counts": {
        "2,3": 3,
        "2,5": 1,
        "2,7": 1,
        "3,5": 1,
        "3,7": 1,
        "4,5": 1,
        "5,8": 4,
    },
    "split_status": SPLIT_STATUS,
}


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_private_lane_strict_core_split_payload(
    full_neighborhood: Mapping[str, Any],
    source_core_catalog: Mapping[str, Any],
    *,
    full_neighborhood_path: Path = DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    source_core_catalog_path: Path = DEFAULT_SOURCE_CORE_CATALOG,
) -> dict[str, Any]:
    """Return the deterministic private-lane strict-core split payload."""

    errors: list[str] = []
    assert_expected_private_lane_core_catalog(source_core_catalog)
    _validate_source_core_catalog(source_core_catalog, errors)
    survivors = _private_lane_survivors(full_neighborhood, errors)
    assignment_records, label8_free_core_signatures, summary = _split_catalogue(
        survivors
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "assignment_records": assignment_records,
        "label8_free_core_signatures": label8_free_core_signatures,
        "source_artifacts": [
            _source_summary(
                full_neighborhood_path,
                "source 151:6 outside-pair full-neighborhood packet",
                full_neighborhood,
            ),
            _source_summary(
                source_core_catalog_path,
                "source 151:6 private-lane core catalog",
                source_core_catalog,
            ),
        ],
        "interpretation": [
            (
                "Every private-lane survivor still has at least one row-6 "
                "three-row strict-cycle core."
            ),
            (
                "All 12 survivors have a label-8-visible auxiliary-row core, "
                "but 8 survivors also have label-8-free alternatives."
            ),
            (
                "The bridge split is therefore not simply endpoint-8 visibility "
                "versus no obstruction: the residual label-8-free signatures "
                "are the concrete private-pair proof targets."
            ),
            (
                "This is a proof-target map only; it does not prove support "
                "existence, row forcing, endpoint-8 forcing, or impossibility "
                "of the private pair."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_private_lane_strict_core_split(payload)
    return payload


def assert_expected_private_lane_strict_core_split(
    payload: Mapping[str, Any],
) -> None:
    """Assert the pinned private-lane strict-core split."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    full_neighborhood_path: Path = DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    source_core_catalog_path: Path = DEFAULT_SOURCE_CORE_CATALOG,
) -> list[str]:
    """Return validation errors for a private-lane strict-core split payload."""

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
    assignment_records = payload.get("assignment_records")
    if not isinstance(assignment_records, list):
        errors.append("assignment_records must be a list")
    else:
        _validate_assignment_records(assignment_records, errors)
    label8_free_core_signatures = payload.get("label8_free_core_signatures")
    if not isinstance(label8_free_core_signatures, list):
        errors.append("label8_free_core_signatures must be a list")
    else:
        _validate_label8_free_core_signatures(
            label8_free_core_signatures, errors
        )
    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("does not prove support existence" in item for item in interpretation):
        errors.append("interpretation must preserve the support-existence nonclaim")

    if recompute and not errors:
        generated = build_private_lane_strict_core_split_payload(
            load_artifact(full_neighborhood_path),
            load_artifact(source_core_catalog_path),
            full_neighborhood_path=full_neighborhood_path,
            source_core_catalog_path=source_core_catalog_path,
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
        "row6_three_row_strict_core_count": summary.get(
            "row6_three_row_strict_core_count"
        ),
        "label8_visible_core_count": summary.get("label8_visible_core_count"),
        "label8_free_core_count": summary.get("label8_free_core_count"),
        "assignments_with_label8_free_core": summary.get(
            "assignments_with_label8_free_core"
        ),
        "label8_free_distinct_exact_core_count": summary.get(
            "label8_free_distinct_exact_core_count"
        ),
        "split_status": summary.get("split_status"),
        "validation_errors": list(errors),
    }


def _split_catalogue(
    survivors: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    assignment_records: list[dict[str, Any]] = []
    all_keys: Counter[tuple[tuple[int, tuple[int, ...]], ...]] = Counter()
    label8_visible_keys: Counter[
        tuple[tuple[int, tuple[int, ...]], ...]
    ] = Counter()
    label8_free_keys: Counter[tuple[tuple[int, tuple[int, ...]], ...]] = Counter()
    auxiliary_pair_counts: Counter[str] = Counter()
    label8_visible_auxiliary_pair_counts: Counter[str] = Counter()
    label8_free_auxiliary_pair_counts: Counter[str] = Counter()
    label8_visible_core_count = 0
    label8_free_core_count = 0
    center8_core_count = 0
    label8_free_center8_core_count = 0
    assignments_with_row6_three = 0
    assignments_with_label8_visible = 0
    assignments_with_label8_free = 0
    assignments_with_center8 = 0

    for index, survivor in enumerate(survivors):
        selected_rows = _selected_rows(survivor)
        row6_three = [
            core
            for core in _minimal_cores(selected_rows)
            if TARGET_CENTER in core.centers
            and len(core.centers) == 3
            and core.status == "strict_cycle"
        ]
        if row6_three:
            assignments_with_row6_three += 1
        assignment_label8_visible_count = 0
        assignment_label8_free_count = 0
        assignment_center8_count = 0
        assignment_core_records: list[dict[str, Any]] = []

        for core in row6_three:
            auxiliary_centers = tuple(
                center for center in core.centers if center != TARGET_CENTER
            )
            pair_key = _pair_key(auxiliary_centers)
            label8_visible = any(
                8 in selected_rows[center]
                for center in core.centers
                if center != TARGET_CENTER
            )
            center8_in_core = 8 in core.centers
            key = _core_key(selected_rows, core.centers)
            all_keys[key] += 1
            auxiliary_pair_counts[pair_key] += 1
            if label8_visible:
                label8_visible_core_count += 1
                assignment_label8_visible_count += 1
                label8_visible_keys[key] += 1
                label8_visible_auxiliary_pair_counts[pair_key] += 1
            else:
                label8_free_core_count += 1
                assignment_label8_free_count += 1
                label8_free_keys[key] += 1
                label8_free_auxiliary_pair_counts[pair_key] += 1
            if center8_in_core:
                center8_core_count += 1
                assignment_center8_count += 1
                if not label8_visible:
                    label8_free_center8_core_count += 1

            replay_json = result_to_json(_replay(selected_rows, core.centers))
            assignment_core_records.append(
                {
                    "centers": list(core.centers),
                    "auxiliary_centers": list(auxiliary_centers),
                    "auxiliary_center_pair": pair_key,
                    "label8_visible": label8_visible,
                    "center8_in_core": center8_in_core,
                    "rows": [
                        {
                            "center": center,
                            "witnesses": list(selected_rows[center]),
                        }
                        for center in core.centers
                    ],
                    "cycle_edge_count": len(replay_json["cycle_edges"]),
                    "strict_edge_count": replay_json["strict_edge_count"],
                    "cycle_edges": replay_json["cycle_edges"],
                }
            )

        if assignment_label8_visible_count:
            assignments_with_label8_visible += 1
        if assignment_label8_free_count:
            assignments_with_label8_free += 1
        if assignment_center8_count:
            assignments_with_center8 += 1
        assignment_records.append(
            {
                "assignment_index": index,
                "row6_three_row_strict_core_count": len(row6_three),
                "label8_visible_core_count": assignment_label8_visible_count,
                "label8_free_core_count": assignment_label8_free_count,
                "center8_core_count": assignment_center8_count,
                "cores": assignment_core_records,
            }
        )

    label8_free_core_signatures = [
        {
            "multiplicity": int(label8_free_keys[key]),
            "rows": [
                {"center": center, "witnesses": list(witnesses)}
                for center, witnesses in key
            ],
        }
        for key in sorted(label8_free_keys)
    ]
    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "source_private_lane_survivor_count": len(survivors),
        "row6_three_row_strict_core_count": (
            label8_visible_core_count + label8_free_core_count
        ),
        "assignments_with_row6_three_row_strict_core": assignments_with_row6_three,
        "label8_visible_core_count": label8_visible_core_count,
        "label8_free_core_count": label8_free_core_count,
        "assignments_with_label8_visible_core": assignments_with_label8_visible,
        "assignments_with_label8_free_core": assignments_with_label8_free,
        "assignments_without_label8_free_core": (
            len(survivors) - assignments_with_label8_free
        ),
        "center8_core_count": center8_core_count,
        "assignments_with_center8_core": assignments_with_center8,
        "label8_free_center8_core_count": label8_free_center8_core_count,
        "distinct_exact_core_count": len(all_keys),
        "label8_visible_distinct_exact_core_count": len(label8_visible_keys),
        "label8_free_distinct_exact_core_count": len(label8_free_keys),
        "auxiliary_center_pair_counts": _json_counter(auxiliary_pair_counts),
        "label8_visible_auxiliary_center_pair_counts": _json_counter(
            label8_visible_auxiliary_pair_counts
        ),
        "label8_free_auxiliary_center_pair_counts": _json_counter(
            label8_free_auxiliary_pair_counts
        ),
        "split_status": SPLIT_STATUS,
    }
    return assignment_records, label8_free_core_signatures, summary


def _validate_source_core_catalog(
    source_core_catalog: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "schema": SOURCE_CORE_CATALOG_SCHEMA,
        "status": SOURCE_CORE_CATALOG_STATUS,
        "trust": TRUST,
    }
    for key, expected_value in expected.items():
        if source_core_catalog.get(key) != expected_value:
            errors.append(
                "source core catalog "
                f"{key} mismatch: expected {expected_value!r}, "
                f"got {source_core_catalog.get(key)!r}"
            )
    summary = _mapping(
        source_core_catalog.get("summary"), "source core catalog summary", errors
    )
    if not summary:
        return
    for key, expected_value in SOURCE_CORE_CATALOG_SUMMARY.items():
        if summary.get(key) != expected_value:
            errors.append(
                "source core catalog "
                f"summary.{key} mismatch: expected {expected_value!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_assignment_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != EXPECTED_SUMMARY["source_private_lane_survivor_count"]:
        errors.append("assignment_records length mismatch")
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"assignment_records[{index}] must be an object")
            continue
        if record.get("assignment_index") != index:
            errors.append(f"assignment_records[{index}] assignment_index mismatch")
        total = int(record.get("row6_three_row_strict_core_count", -1))
        visible = int(record.get("label8_visible_core_count", -1))
        free = int(record.get("label8_free_core_count", -1))
        if total != visible + free:
            errors.append(f"assignment_records[{index}] split count mismatch")
        cores = record.get("cores")
        if not isinstance(cores, list):
            errors.append(f"assignment_records[{index}].cores must be a list")
            continue
        if len(cores) != total:
            errors.append(f"assignment_records[{index}].cores length mismatch")
        if visible == 0:
            errors.append(
                f"assignment_records[{index}] must have a label-8-visible core"
            )
        for core_index, core in enumerate(cores):
            if not isinstance(core, Mapping):
                errors.append(
                    f"assignment_records[{index}].cores[{core_index}] must be an object"
                )
                continue
            centers = core.get("centers")
            if not isinstance(centers, list) or len(centers) != 3:
                errors.append(
                    f"assignment_records[{index}].cores[{core_index}] "
                    "must have three centers"
                )
            elif TARGET_CENTER not in centers:
                errors.append(
                    f"assignment_records[{index}].cores[{core_index}] "
                    "must include row 6"
                )
            if int(core.get("cycle_edge_count", 0)) <= 0:
                errors.append(
                    f"assignment_records[{index}].cores[{core_index}] "
                    "has no cycle edges"
                )


def _validate_label8_free_core_signatures(
    signatures: Sequence[object],
    errors: list[str],
) -> None:
    if len(signatures) != EXPECTED_SUMMARY["label8_free_distinct_exact_core_count"]:
        errors.append("label8_free_core_signatures length mismatch")
    for index, signature in enumerate(signatures):
        if not isinstance(signature, Mapping):
            errors.append(f"label8_free_core_signatures[{index}] must be an object")
            continue
        rows = signature.get("rows")
        if not isinstance(rows, list) or len(rows) != 3:
            errors.append(f"label8_free_core_signatures[{index}].rows mismatch")
            continue
        if int(signature.get("multiplicity", 0)) <= 0:
            errors.append(
                f"label8_free_core_signatures[{index}] must have multiplicity"
            )
        for row in rows:
            if not isinstance(row, Mapping):
                errors.append(f"label8_free_core_signatures[{index}] row mismatch")
                continue
            if 8 in list(row.get("witnesses", [])):
                errors.append(
                    f"label8_free_core_signatures[{index}] contains witness 8"
                )


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, got {summary.get(key)!r}"
            )


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "catalog_status": (
            payload.get("summary", {}).get("catalog_status")
            if isinstance(payload.get("summary"), Mapping)
            else None
        ),
    }


def _pair_key(pair: Sequence[int]) -> str:
    return ",".join(str(center) for center in pair)


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
        "--source-full-neighborhood",
        type=Path,
        default=DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    )
    parser.add_argument(
        "--source-core-catalog",
        type=Path,
        default=DEFAULT_SOURCE_CORE_CATALOG,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_full_neighborhood = _resolve(args.source_full_neighborhood)
    source_core_catalog = _resolve(args.source_core_catalog)

    generated = build_private_lane_strict_core_split_payload(
        load_artifact(source_full_neighborhood),
        load_artifact(source_core_catalog),
        full_neighborhood_path=source_full_neighborhood,
        source_core_catalog_path=source_core_catalog,
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
        source_core_catalog_path=source_core_catalog,
    )
    if args.assert_expected:
        assert_expected_private_lane_strict_core_split(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 private-lane strict-core split")
        print(f"target row: {summary['target_row_key']}")
        print(
            "row-6 three-row strict cores: "
            f"{summary['row6_three_row_strict_core_count']}"
        )
        print(f"label-8-visible cores: {summary['label8_visible_core_count']}")
        print(f"label-8-free cores: {summary['label8_free_core_count']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: 151:6 private-lane strict-core split verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
