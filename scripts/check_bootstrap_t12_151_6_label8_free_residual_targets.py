#!/usr/bin/env python3
"""Check the bootstrap/T12 151:6 label-8-free residual targets."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erdos97.json_io import write_json  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402

from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
    _json_counter,
    _replay,
    result_to_json,
)
from scripts.check_bootstrap_t12_151_6_private_lane_strict_core_split import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_STRICT_CORE_SPLIT,
    SCHEMA as SOURCE_STRICT_CORE_SPLIT_SCHEMA,
    SPLIT_STATUS as SOURCE_SPLIT_STATUS,
    STATUS as SOURCE_STRICT_CORE_SPLIT_STATUS,
    assert_expected_private_lane_strict_core_split,
    load_artifact,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_label8_free_residual_targets.v1"
STATUS = "BOOTSTRAP_T12_151_6_LABEL8_FREE_RESIDUAL_TARGETS_DIAGNOSTIC_ONLY"
TARGET_STATUS = "LABEL8_FREE_RESIDUAL_SIGNATURES_REQUIRE_AUXILIARY_LABEL4"
CLAIM_SCOPE = (
    "Proof-target diagnostic for the source-151 row-6 private-halo-only "
    "outside-pair lane. It classifies the 10 distinct exact label-8-free "
    "row-6 strict-core signatures from the private-lane split and records "
    "that every residual signature requires label 4 as an auxiliary-row "
    "witness. This does not prove outside-pair support existence, does not "
    "prove row forcing, does not prove pair [3,5] impossible, does not prove "
    "endpoint-8 forcing, does not prove n=9, does not prove the bridge, is "
    "not a counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_bootstrap_t12_151_6_label8_free_residual_targets.py",
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label8_free_residual_targets.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label8_free_residual_targets.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "interpretation",
    "provenance",
    "residual_signature_records",
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
    "label8_free_distinct_exact_signature_count": 10,
    "label8_free_occurrence_count": 12,
    "auxiliary_row_signature_incidence_count": 20,
    "auxiliary_row_occurrence_count": 24,
    "label4_auxiliary_row_signature_incidence_count": 18,
    "label4_auxiliary_row_occurrence_count": 22,
    "signatures_with_any_label4_auxiliary_row": 10,
    "signatures_with_all_auxiliary_rows_label4": 8,
    "occurrences_with_all_auxiliary_rows_label4": 10,
    "signatures_with_label4_free_strict_cycle_edges": 2,
    "occurrences_with_label4_free_strict_cycle_edges": 2,
    "signatures_with_center8_as_auxiliary_center": 3,
    "occurrences_with_center8_as_auxiliary_center": 4,
    "signatures_without_center8_as_auxiliary_center": 7,
    "occurrences_without_center8_as_auxiliary_center": 8,
    "auxiliary_center_pair_signature_counts": {
        "2,3": 2,
        "2,5": 1,
        "2,7": 1,
        "3,5": 1,
        "3,7": 1,
        "4,5": 1,
        "5,8": 3,
    },
    "auxiliary_center_pair_occurrence_counts": {
        "2,3": 3,
        "2,5": 1,
        "2,7": 1,
        "3,5": 1,
        "3,7": 1,
        "4,5": 1,
        "5,8": 4,
    },
    "all_auxiliary_rows_label4_pair_signature_counts": {
        "2,3": 2,
        "2,5": 1,
        "2,7": 1,
        "3,7": 1,
        "5,8": 3,
    },
    "all_auxiliary_rows_label4_pair_occurrence_counts": {
        "2,3": 3,
        "2,5": 1,
        "2,7": 1,
        "3,7": 1,
        "5,8": 4,
    },
    "target_row_intersection_profile_signature_counts": {
        "1,1": 2,
        "1,2": 6,
        "2,2": 2,
    },
    "target_row_intersection_profile_occurrence_counts": {
        "1,1": 3,
        "1,2": 6,
        "2,2": 3,
    },
    "auxiliary_row_intersection_size_signature_counts": {"1": 4, "2": 6},
    "auxiliary_row_intersection_size_occurrence_counts": {"1": 5, "2": 7},
    "cycle_edge_count_signature_counts": {"2": 2, "3": 7, "4": 1},
    "cycle_edge_count_occurrence_counts": {"2": 2, "3": 9, "4": 1},
    "strict_edge_count_signature_counts": {"27": 10},
    "strict_edge_count_occurrence_counts": {"27": 12},
    "cycle_row_occurrence_counts": {
        "2": 4,
        "3": 7,
        "4": 2,
        "5": 4,
        "6": 7,
        "7": 4,
        "8": 7,
    },
    "target_status": TARGET_STATUS,
}


def build_label8_free_residual_targets_payload(
    source_strict_core_split: Mapping[str, Any],
    *,
    source_strict_core_split_path: Path = DEFAULT_SOURCE_STRICT_CORE_SPLIT,
) -> dict[str, Any]:
    """Return the deterministic label-8-free residual target payload."""

    errors: list[str] = []
    assert_expected_private_lane_strict_core_split(source_strict_core_split)
    _validate_source_strict_core_split(source_strict_core_split, errors)
    records, summary = _residual_target_records(source_strict_core_split)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "residual_signature_records": records,
        "source_artifacts": [
            _source_summary(
                source_strict_core_split_path,
                "source 151:6 private-lane strict-core split",
                source_strict_core_split,
            )
        ],
        "interpretation": [
            (
                "Every exact label-8-free residual signature still uses label "
                "4 in at least one auxiliary row."
            ),
            (
                "Eight of the 10 signatures, covering 10 of the 12 residual "
                "occurrences, use label 4 in both auxiliary rows."
            ),
            (
                "Two signatures have strict-cycle edges that do not directly "
                "mention label 4, so a label-4 bridge must sometimes pass "
                "through selected-distance equalities rather than visible "
                "cycle-edge endpoints."
            ),
            (
                "This is a proof-target ledger only; it does not prove "
                "support existence, row forcing, endpoint-8 forcing, or "
                "impossibility of the private pair."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_label8_free_residual_targets(payload)
    return payload


def assert_expected_label8_free_residual_targets(
    payload: Mapping[str, Any],
) -> None:
    """Assert the pinned label-8-free residual target ledger."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    source_strict_core_split_path: Path = DEFAULT_SOURCE_STRICT_CORE_SPLIT,
) -> list[str]:
    """Return validation errors for a residual target payload."""

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
    records = payload.get("residual_signature_records")
    if not isinstance(records, list):
        errors.append("residual_signature_records must be a list")
    else:
        _validate_residual_signature_records(records, errors)
    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("does not prove support existence" in item for item in interpretation):
        errors.append("interpretation must preserve the support-existence nonclaim")

    if recompute and not errors:
        generated = build_label8_free_residual_targets_payload(
            load_artifact(source_strict_core_split_path),
            source_strict_core_split_path=source_strict_core_split_path,
        )
        if dict(payload) != generated:
            errors.append("stored artifact is stale relative to source split")
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
        "label8_free_distinct_exact_signature_count": summary.get(
            "label8_free_distinct_exact_signature_count"
        ),
        "label8_free_occurrence_count": summary.get(
            "label8_free_occurrence_count"
        ),
        "signatures_with_any_label4_auxiliary_row": summary.get(
            "signatures_with_any_label4_auxiliary_row"
        ),
        "signatures_with_all_auxiliary_rows_label4": summary.get(
            "signatures_with_all_auxiliary_rows_label4"
        ),
        "signatures_with_label4_free_strict_cycle_edges": summary.get(
            "signatures_with_label4_free_strict_cycle_edges"
        ),
        "target_status": summary.get("target_status"),
        "validation_errors": list(errors),
    }


def _residual_target_records(
    source_strict_core_split: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    signatures = source_strict_core_split["label8_free_core_signatures"]
    records: list[dict[str, Any]] = []
    auxiliary_pair_signature_counts: Counter[str] = Counter()
    auxiliary_pair_occurrence_counts: Counter[str] = Counter()
    all_label4_pair_signature_counts: Counter[str] = Counter()
    all_label4_pair_occurrence_counts: Counter[str] = Counter()
    target_profile_signature_counts: Counter[str] = Counter()
    target_profile_occurrence_counts: Counter[str] = Counter()
    auxiliary_intersection_signature_counts: Counter[int] = Counter()
    auxiliary_intersection_occurrence_counts: Counter[int] = Counter()
    cycle_edge_signature_counts: Counter[int] = Counter()
    cycle_edge_occurrence_counts: Counter[int] = Counter()
    strict_edge_signature_counts: Counter[int] = Counter()
    strict_edge_occurrence_counts: Counter[int] = Counter()
    cycle_row_occurrence_counts: Counter[int] = Counter()
    auxiliary_row_signature_incidence_count = 0
    auxiliary_row_occurrence_count = 0
    label4_auxiliary_row_signature_incidence_count = 0
    label4_auxiliary_row_occurrence_count = 0
    signatures_with_any_label4 = 0
    signatures_with_all_label4 = 0
    occurrences_with_all_label4 = 0
    signatures_with_label4_free_cycle_edges = 0
    occurrences_with_label4_free_cycle_edges = 0
    signatures_with_center8 = 0
    occurrences_with_center8 = 0
    total_occurrences = 0

    for index, signature in enumerate(signatures):
        multiplicity = int(signature["multiplicity"])
        total_occurrences += multiplicity
        rows = {
            int(row["center"]): tuple(int(witness) for witness in row["witnesses"])
            for row in signature["rows"]
        }
        centers = tuple(sorted(rows))
        auxiliary_centers = tuple(center for center in centers if center != TARGET_CENTER)
        pair_key = _pair_key(auxiliary_centers)
        target_intersections = [
            sorted(set(rows[center]) & set(rows[TARGET_CENTER]))
            for center in auxiliary_centers
        ]
        target_profile = _profile_key(len(values) for values in target_intersections)
        auxiliary_intersection = sorted(
            set(rows[auxiliary_centers[0]]) & set(rows[auxiliary_centers[1]])
        )
        auxiliary_label4_centers = [
            center for center in auxiliary_centers if 4 in rows[center]
        ]
        center8_as_auxiliary = 8 in auxiliary_centers
        replay_json = result_to_json(_replay(rows, centers))
        cycle_edges = replay_json["cycle_edges"]
        label4_touching_cycle_edge_count = sum(
            1
            for edge in cycle_edges
            if 4 in edge["outer_pair"] or 4 in edge["inner_pair"]
        )
        label4_free_cycle_edges = (
            label4_touching_cycle_edge_count == 0
        )

        auxiliary_pair_signature_counts[pair_key] += 1
        auxiliary_pair_occurrence_counts[pair_key] += multiplicity
        if len(auxiliary_label4_centers) == len(auxiliary_centers):
            all_label4_pair_signature_counts[pair_key] += 1
            all_label4_pair_occurrence_counts[pair_key] += multiplicity
            signatures_with_all_label4 += 1
            occurrences_with_all_label4 += multiplicity
        if auxiliary_label4_centers:
            signatures_with_any_label4 += 1
        if label4_free_cycle_edges:
            signatures_with_label4_free_cycle_edges += 1
            occurrences_with_label4_free_cycle_edges += multiplicity
        if center8_as_auxiliary:
            signatures_with_center8 += 1
            occurrences_with_center8 += multiplicity

        target_profile_signature_counts[target_profile] += 1
        target_profile_occurrence_counts[target_profile] += multiplicity
        auxiliary_intersection_signature_counts[len(auxiliary_intersection)] += 1
        auxiliary_intersection_occurrence_counts[len(auxiliary_intersection)] += (
            multiplicity
        )
        cycle_edge_signature_counts[len(cycle_edges)] += 1
        cycle_edge_occurrence_counts[len(cycle_edges)] += multiplicity
        strict_edge_signature_counts[int(replay_json["strict_edge_count"])] += 1
        strict_edge_occurrence_counts[int(replay_json["strict_edge_count"])] += (
            multiplicity
        )
        for edge in cycle_edges:
            cycle_row_occurrence_counts[int(edge["row"])] += multiplicity
        auxiliary_row_signature_incidence_count += len(auxiliary_centers)
        auxiliary_row_occurrence_count += len(auxiliary_centers) * multiplicity
        label4_auxiliary_row_signature_incidence_count += len(
            auxiliary_label4_centers
        )
        label4_auxiliary_row_occurrence_count += (
            len(auxiliary_label4_centers) * multiplicity
        )

        records.append(
            {
                "signature_index": index,
                "multiplicity": multiplicity,
                "centers": list(centers),
                "auxiliary_centers": list(auxiliary_centers),
                "auxiliary_center_pair": pair_key,
                "center8_as_auxiliary_center": center8_as_auxiliary,
                "rows": [
                    {"center": center, "witnesses": list(rows[center])}
                    for center in centers
                ],
                "target_row_intersections": [
                    {"center": center, "intersection": values}
                    for center, values in zip(
                        auxiliary_centers,
                        target_intersections,
                        strict=True,
                    )
                ],
                "target_row_intersection_profile": target_profile,
                "auxiliary_row_intersection": auxiliary_intersection,
                "auxiliary_row_intersection_size": len(auxiliary_intersection),
                "auxiliary_label4_centers": auxiliary_label4_centers,
                "label4_in_any_auxiliary_row": bool(auxiliary_label4_centers),
                "label4_in_all_auxiliary_rows": (
                    len(auxiliary_label4_centers) == len(auxiliary_centers)
                ),
                "strict_edge_count": replay_json["strict_edge_count"],
                "cycle_edge_count": len(cycle_edges),
                "label4_touching_cycle_edge_count": (
                    label4_touching_cycle_edge_count
                ),
                "label4_free_strict_cycle_edges": label4_free_cycle_edges,
                "cycle_edge_rows": sorted({edge["row"] for edge in cycle_edges}),
                "cycle_edges": cycle_edges,
            }
        )

    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "label8_free_distinct_exact_signature_count": len(signatures),
        "label8_free_occurrence_count": total_occurrences,
        "auxiliary_row_signature_incidence_count": auxiliary_row_signature_incidence_count,
        "auxiliary_row_occurrence_count": auxiliary_row_occurrence_count,
        "label4_auxiliary_row_signature_incidence_count": (
            label4_auxiliary_row_signature_incidence_count
        ),
        "label4_auxiliary_row_occurrence_count": (
            label4_auxiliary_row_occurrence_count
        ),
        "signatures_with_any_label4_auxiliary_row": signatures_with_any_label4,
        "signatures_with_all_auxiliary_rows_label4": signatures_with_all_label4,
        "occurrences_with_all_auxiliary_rows_label4": occurrences_with_all_label4,
        "signatures_with_label4_free_strict_cycle_edges": (
            signatures_with_label4_free_cycle_edges
        ),
        "occurrences_with_label4_free_strict_cycle_edges": (
            occurrences_with_label4_free_cycle_edges
        ),
        "signatures_with_center8_as_auxiliary_center": signatures_with_center8,
        "occurrences_with_center8_as_auxiliary_center": occurrences_with_center8,
        "signatures_without_center8_as_auxiliary_center": (
            len(signatures) - signatures_with_center8
        ),
        "occurrences_without_center8_as_auxiliary_center": (
            total_occurrences - occurrences_with_center8
        ),
        "auxiliary_center_pair_signature_counts": _json_counter(
            auxiliary_pair_signature_counts
        ),
        "auxiliary_center_pair_occurrence_counts": _json_counter(
            auxiliary_pair_occurrence_counts
        ),
        "all_auxiliary_rows_label4_pair_signature_counts": _json_counter(
            all_label4_pair_signature_counts
        ),
        "all_auxiliary_rows_label4_pair_occurrence_counts": _json_counter(
            all_label4_pair_occurrence_counts
        ),
        "target_row_intersection_profile_signature_counts": _json_counter(
            target_profile_signature_counts
        ),
        "target_row_intersection_profile_occurrence_counts": _json_counter(
            target_profile_occurrence_counts
        ),
        "auxiliary_row_intersection_size_signature_counts": _json_counter(
            auxiliary_intersection_signature_counts
        ),
        "auxiliary_row_intersection_size_occurrence_counts": _json_counter(
            auxiliary_intersection_occurrence_counts
        ),
        "cycle_edge_count_signature_counts": _json_counter(
            cycle_edge_signature_counts
        ),
        "cycle_edge_count_occurrence_counts": _json_counter(
            cycle_edge_occurrence_counts
        ),
        "strict_edge_count_signature_counts": _json_counter(
            strict_edge_signature_counts
        ),
        "strict_edge_count_occurrence_counts": _json_counter(
            strict_edge_occurrence_counts
        ),
        "cycle_row_occurrence_counts": _json_counter(cycle_row_occurrence_counts),
        "target_status": TARGET_STATUS,
    }
    return records, summary


def _validate_source_strict_core_split(
    source_strict_core_split: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "schema": SOURCE_STRICT_CORE_SPLIT_SCHEMA,
        "status": SOURCE_STRICT_CORE_SPLIT_STATUS,
        "trust": TRUST,
    }
    for key, expected_value in expected.items():
        if source_strict_core_split.get(key) != expected_value:
            errors.append(
                "source strict-core split "
                f"{key} mismatch: expected {expected_value!r}, "
                f"got {source_strict_core_split.get(key)!r}"
            )
    summary = _mapping(
        source_strict_core_split.get("summary"),
        "source strict-core split summary",
        errors,
    )
    if summary.get("split_status") != SOURCE_SPLIT_STATUS:
        errors.append("source strict-core split status drifted")
    expected_counts = {
        "label8_free_core_count": 12,
        "label8_free_distinct_exact_core_count": 10,
        "split_status": SOURCE_SPLIT_STATUS,
    }
    for key, expected_value in expected_counts.items():
        if summary.get(key) != expected_value:
            errors.append(
                "source strict-core split "
                f"summary.{key} mismatch: expected {expected_value!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_residual_signature_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != EXPECTED_SUMMARY["label8_free_distinct_exact_signature_count"]:
        errors.append("residual_signature_records length mismatch")
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"residual_signature_records[{index}] must be an object")
            continue
        if record.get("signature_index") != index:
            errors.append(
                f"residual_signature_records[{index}] signature_index mismatch"
            )
        centers = record.get("centers")
        if not isinstance(centers, list) or len(centers) != 3:
            errors.append(f"residual_signature_records[{index}] centers mismatch")
            continue
        if TARGET_CENTER not in centers:
            errors.append(f"residual_signature_records[{index}] must include row 6")
        if 8 in _witnesses(record):
            errors.append(
                f"residual_signature_records[{index}] contains witness label 8"
            )
        if not record.get("label4_in_any_auxiliary_row"):
            errors.append(
                f"residual_signature_records[{index}] must expose auxiliary label 4"
            )
        if int(record.get("strict_edge_count", 0)) != 27:
            errors.append(f"residual_signature_records[{index}] strict edge drift")
        if int(record.get("cycle_edge_count", 0)) <= 0:
            errors.append(f"residual_signature_records[{index}] has no cycle edges")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, got {summary.get(key)!r}"
            )


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary")
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "split_status": (
            summary.get("split_status") if isinstance(summary, Mapping) else None
        ),
    }


def _pair_key(pair: Sequence[int]) -> str:
    return ",".join(str(center) for center in pair)


def _profile_key(values: Sequence[int]) -> str:
    return ",".join(str(value) for value in sorted(values))


def _witnesses(record: Mapping[str, Any]) -> set[int]:
    witnesses: set[int] = set()
    rows = record.get("rows")
    if not isinstance(rows, list):
        return witnesses
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        witnesses.update(int(witness) for witness in row.get("witnesses", []))
    return witnesses


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
        "--source-strict-core-split",
        type=Path,
        default=DEFAULT_SOURCE_STRICT_CORE_SPLIT,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_strict_core_split = _resolve(args.source_strict_core_split)

    generated = build_label8_free_residual_targets_payload(
        load_artifact(source_strict_core_split),
        source_strict_core_split_path=source_strict_core_split,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        source_strict_core_split_path=source_strict_core_split,
    )
    if args.assert_expected:
        assert_expected_label8_free_residual_targets(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-8-free residual targets")
        print(f"target row: {summary['target_row_key']}")
        print(
            "residual signatures: "
            f"{summary['label8_free_distinct_exact_signature_count']}"
        )
        print(f"residual occurrences: {summary['label8_free_occurrence_count']}")
        print(
            "signatures with auxiliary label 4: "
            f"{summary['signatures_with_any_label4_auxiliary_row']}"
        )
        print(
            "label-4-free strict-cycle-edge signatures: "
            f"{summary['signatures_with_label4_free_strict_cycle_edges']}"
        )
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: 151:6 label-8-free residual targets verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
