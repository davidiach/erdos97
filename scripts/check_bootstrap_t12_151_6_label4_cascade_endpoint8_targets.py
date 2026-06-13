#!/usr/bin/env python3
"""Check the rich endpoint-8 target for the 151:6 label-4 cascade."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
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
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    RichClassRow,
    replay_vertex_circle_rich_quotient,
)

from scripts.check_bootstrap_t12_151_6_label4_cascade_row_criticality import (  # noqa: E402
    CASCADE_COMPONENT_KEY,
    CRITICALITY_STATUS as SOURCE_CRITICALITY_STATUS,
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_CASCADE_ROW_CRITICALITY,
    REQUIRED_CORE_CENTERS,
    SCHEMA as SOURCE_CASCADE_SCHEMA,
    STATUS as SOURCE_CASCADE_STATUS,
    assert_expected_cascade_row_criticality,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
)


N = 9
CYCLIC_ORDER = tuple(range(N))
ENDPOINT_CENTER = 8
ENDPOINT_TRIPLE = [0, 4, 6]
ENDPOINT_EXTRA_LABEL_POOL = [1, 2, 3, 5, 7]
EXACT_FOUR_ENDPOINT_ROWS = [
    [0, 1, 4, 6],
    [0, 2, 4, 6],
    [0, 3, 4, 6],
    [0, 4, 5, 6],
    [0, 4, 6, 7],
]
SOURCE_RECORDED_ENDPOINT_ROWS = [
    [0, 2, 4, 6],
    [0, 4, 6, 7],
    [0, 1, 4, 6],
]
SOURCE_RECORDED_ENDPOINT_EXTRA_LABELS = [2, 7, 1]

SCHEMA = "erdos97.bootstrap_t12_151_6_label4_cascade_endpoint8_targets.v1"
STATUS = "BOOTSTRAP_T12_151_6_LABEL4_CASCADE_ENDPOINT8_TARGETS_DIAGNOSTIC_ONLY"
TARGET_STATUS = "ENDPOINT8_RICH_TRIPLE_SUFFICES_CONDITIONALLY"
CLAIM_SCOPE = (
    "Proof-target diagnostic for the source-151 row-6 label-4 cascade. For "
    "each of the three stored cascade signature packages, it replaces row 8 "
    "by every rich class on center 8 whose witnesses contain the endpoint "
    "triple [0,4,6], and checks that the quotient replay is still obstructed. "
    "This identifies a conditional rich-class target for row 8, not support "
    "existence, not row forcing, not a proof that [3,5] is impossible, not "
    "endpoint-8 forcing, not n=9, not the bootstrap bridge, not a "
    "counterexample, and not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/check_bootstrap_t12_151_6_label4_cascade_endpoint8_targets.py"
    ),
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label4_cascade_endpoint8_targets.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_cascade_endpoint8_targets.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "cascade_endpoint_records",
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
    "cascade_component_key": CASCADE_COMPONENT_KEY,
    "required_core_centers": REQUIRED_CORE_CENTERS,
    "source_criticality_status": SOURCE_CRITICALITY_STATUS,
    "source_cascade_signature_indices": [7, 8, 9],
    "source_cascade_signature_count": 3,
    "source_cascade_occurrence_count": 4,
    "endpoint_center": ENDPOINT_CENTER,
    "endpoint_triple": ENDPOINT_TRIPLE,
    "endpoint_extra_label_pool": ENDPOINT_EXTRA_LABEL_POOL,
    "source_recorded_endpoint_rows": SOURCE_RECORDED_ENDPOINT_ROWS,
    "source_recorded_endpoint_extra_labels": SOURCE_RECORDED_ENDPOINT_EXTRA_LABELS,
    "source_recorded_endpoint_status_counts": {"strict_cycle": 3},
    "source_recorded_endpoint_occurrence_status_counts": {"strict_cycle": 4},
    "rich_superset_count_per_signature": 31,
    "rich_superset_signature_record_count": 93,
    "rich_superset_occurrence_record_count": 124,
    "rich_superset_obstructed_count": 93,
    "rich_superset_obstructed_occurrence_count": 124,
    "rich_superset_status_counts": {"self_edge": 72, "strict_cycle": 21},
    "rich_superset_occurrence_status_counts": {"self_edge": 96, "strict_cycle": 28},
    "rich_superset_status_counts_by_size": {
        "4": {"self_edge": 6, "strict_cycle": 9},
        "5": {"self_edge": 21, "strict_cycle": 9},
        "6": {"self_edge": 27, "strict_cycle": 3},
        "7": {"self_edge": 15},
        "8": {"self_edge": 3},
    },
    "rich_superset_occurrence_status_counts_by_size": {
        "4": {"self_edge": 8, "strict_cycle": 12},
        "5": {"self_edge": 28, "strict_cycle": 12},
        "6": {"self_edge": 36, "strict_cycle": 4},
        "7": {"self_edge": 20},
        "8": {"self_edge": 4},
    },
    "exact_four_endpoint_rows": EXACT_FOUR_ENDPOINT_ROWS,
    "exact_four_status_counts": {"self_edge": 6, "strict_cycle": 9},
    "exact_four_occurrence_status_counts": {"self_edge": 8, "strict_cycle": 12},
    "target_status": TARGET_STATUS,
}


def load_artifact(path: Path) -> dict[str, Any]:
    """Load a JSON artifact."""

    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{display_path(path, ROOT)} must contain a JSON object")
    return payload


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_cascade_endpoint8_targets_payload(
    cascade_row_criticality: Mapping[str, Any],
    *,
    source_path: Path = DEFAULT_SOURCE_CASCADE_ROW_CRITICALITY,
) -> dict[str, Any]:
    """Return the deterministic cascade endpoint-8 rich-target payload."""

    errors: list[str] = []
    assert_expected_cascade_row_criticality(cascade_row_criticality)
    _validate_source(cascade_row_criticality, errors)
    records, summary = _endpoint_records(cascade_row_criticality)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "cascade_endpoint_records": records,
        "source_artifacts": [
            _source_summary(source_path, cascade_row_criticality),
        ],
        "interpretation": [
            (
                "For each stored cascade package, every center-8 rich class "
                "containing witnesses [0,4,6] keeps the quotient graph "
                "obstructed."
            ),
            (
                "The three row-8 exact rows already present in the cascade "
                "criticality packet are only three of the five exact four-set "
                "extensions of [0,4,6]."
            ),
            (
                "The two additional exact four-set extensions [0,3,4,6] and "
                "[0,4,5,6] are obstructed by self-edges against the same "
                "row-5/row-6 cascade equalities."
            ),
            (
                "The next bridge target is therefore conditional and sharp: "
                "force a genuine center-8 rich class containing [0,4,6] "
                "alongside the row-5/row-6 cascade package, or find a "
                "different support-rich obstruction."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_cascade_endpoint8_targets(payload)
    return payload


def assert_expected_cascade_endpoint8_targets(payload: Mapping[str, Any]) -> None:
    """Assert the pinned cascade endpoint-8 target packet."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    source_path: Path = DEFAULT_SOURCE_CASCADE_ROW_CRITICALITY,
) -> list[str]:
    """Return validation errors for a cascade endpoint-8 target payload."""

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
            "rich class on center 8 whose witnesses contain the endpoint triple [0,4,6]",
            "not support existence",
            "not row forcing",
            "not a proof that [3,5] is impossible",
            "not endpoint-8 forcing",
            "not n=9",
            "not the bootstrap bridge",
            "not a counterexample",
            "not a global status update",
        ):
            if phrase not in claim_scope:
                errors.append(f"claim_scope must contain {phrase!r}")

    summary = _mapping(payload.get("summary"), "summary", errors)
    _validate_summary(summary, errors)
    records = payload.get("cascade_endpoint_records")
    if not isinstance(records, list):
        errors.append("cascade_endpoint_records must be a list")
    else:
        _validate_endpoint_records(records, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("[0,4,6]" in str(item) for item in interpretation):
        errors.append("interpretation must preserve the endpoint triple target")

    if recompute and not errors:
        generated = build_cascade_endpoint8_targets_payload(
            load_artifact(source_path),
            source_path=source_path,
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
        "endpoint_center": summary.get("endpoint_center"),
        "endpoint_triple": summary.get("endpoint_triple"),
        "rich_superset_signature_record_count": summary.get(
            "rich_superset_signature_record_count"
        ),
        "rich_superset_status_counts": summary.get("rich_superset_status_counts"),
        "target_status": summary.get("target_status"),
        "validation_errors": list(errors),
    }


def _endpoint_records(
    cascade_row_criticality: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    occurrence_status_counts: Counter[str] = Counter()
    status_counts_by_size: dict[int, Counter[str]] = {}
    occurrence_status_counts_by_size: dict[int, Counter[str]] = {}
    exact_four_status_counts: Counter[str] = Counter()
    exact_four_occurrence_status_counts: Counter[str] = Counter()
    source_endpoint_status_counts: Counter[str] = Counter()
    source_endpoint_occurrence_status_counts: Counter[str] = Counter()
    total_variant_records = 0
    total_occurrence_records = 0
    total_obstructed_records = 0
    total_obstructed_occurrences = 0

    for source_record in cascade_row_criticality["cascade_signature_records"]:
        signature_index = int(source_record["signature_index"])
        multiplicity = int(source_record["multiplicity"])
        rows = _rows_by_center(source_record)
        variant_records: list[dict[str, Any]] = []
        record_status_counts: Counter[str] = Counter()
        record_status_counts_by_size: dict[int, Counter[str]] = {}
        source_row8 = list(rows[ENDPOINT_CENTER])
        if not set(ENDPOINT_TRIPLE).issubset(source_row8):
            raise AssertionError(
                f"signature {signature_index} row 8 misses endpoint triple"
            )

        for center8_witnesses in _rich_endpoint_supersets():
            result = replay_vertex_circle_rich_quotient(
                N,
                CYCLIC_ORDER,
                [
                    RichClassRow(center=5, witnesses=rows[5]),
                    RichClassRow(center=6, witnesses=rows[6]),
                    RichClassRow(center=ENDPOINT_CENTER, witnesses=center8_witnesses),
                ],
            )
            if not result.obstructed:
                raise AssertionError(
                    f"signature {signature_index} has clean endpoint target "
                    f"{center8_witnesses!r}"
                )
            witness_count = len(center8_witnesses)
            status_counts[result.status] += 1
            occurrence_status_counts[result.status] += multiplicity
            status_counts_by_size.setdefault(witness_count, Counter())[result.status] += 1
            occurrence_status_counts_by_size.setdefault(witness_count, Counter())[
                result.status
            ] += multiplicity
            record_status_counts[result.status] += 1
            record_status_counts_by_size.setdefault(witness_count, Counter())[
                result.status
            ] += 1
            total_variant_records += 1
            total_occurrence_records += multiplicity
            total_obstructed_records += 1
            total_obstructed_occurrences += multiplicity
            if witness_count == 4:
                exact_four_status_counts[result.status] += 1
                exact_four_occurrence_status_counts[result.status] += multiplicity
            if list(center8_witnesses) == source_row8:
                source_endpoint_status_counts[result.status] += 1
                source_endpoint_occurrence_status_counts[result.status] += multiplicity
            variant_records.append(
                {
                    "center8_witnesses": list(center8_witnesses),
                    "witness_count": witness_count,
                    "extra_labels": [
                        label
                        for label in center8_witnesses
                        if label not in ENDPOINT_TRIPLE
                    ],
                    "is_exact_four": witness_count == 4,
                    "is_source_recorded_endpoint_row": list(center8_witnesses)
                    == source_row8,
                    "status": result.status,
                    "obstructed": result.obstructed,
                    "self_edge_count": len(result.self_edge_conflicts),
                    "cycle_edge_count": len(result.cycle_edges),
                    "obstruction_rows": _obstruction_rows(result),
                }
            )

        records.append(
            {
                "signature_index": signature_index,
                "multiplicity": multiplicity,
                "row5_witnesses": list(rows[5]),
                "row6_witnesses": list(rows[6]),
                "source_row8_witnesses": source_row8,
                "source_row8_extra_label": [
                    label for label in source_row8 if label not in ENDPOINT_TRIPLE
                ][0],
                "endpoint_center": ENDPOINT_CENTER,
                "endpoint_triple": ENDPOINT_TRIPLE,
                "rich_superset_count": len(variant_records),
                "status_counts": _json_counter(record_status_counts),
                "status_counts_by_size": _nested_counter(record_status_counts_by_size),
                "all_rich_supersets_obstructed": all(
                    record["obstructed"] for record in variant_records
                ),
                "variant_records": variant_records,
                "next_proof_obligation": (
                    "Force a genuine center-8 rich class containing [0,4,6] "
                    "alongside this row-5/row-6 cascade package, or find a "
                    "different support-rich obstruction."
                ),
            }
        )

    records = sorted(records, key=lambda item: int(item["signature_index"]))
    source_summary = _mapping_or_empty(cascade_row_criticality.get("summary"))
    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "cascade_component_key": CASCADE_COMPONENT_KEY,
        "required_core_centers": REQUIRED_CORE_CENTERS,
        "source_criticality_status": source_summary.get("criticality_status"),
        "source_cascade_signature_indices": source_summary.get(
            "cascade_signature_indices"
        ),
        "source_cascade_signature_count": source_summary.get("cascade_signature_count"),
        "source_cascade_occurrence_count": source_summary.get(
            "cascade_occurrence_count"
        ),
        "endpoint_center": ENDPOINT_CENTER,
        "endpoint_triple": ENDPOINT_TRIPLE,
        "endpoint_extra_label_pool": ENDPOINT_EXTRA_LABEL_POOL,
        "source_recorded_endpoint_rows": SOURCE_RECORDED_ENDPOINT_ROWS,
        "source_recorded_endpoint_extra_labels": SOURCE_RECORDED_ENDPOINT_EXTRA_LABELS,
        "source_recorded_endpoint_status_counts": _json_counter(
            source_endpoint_status_counts
        ),
        "source_recorded_endpoint_occurrence_status_counts": _json_counter(
            source_endpoint_occurrence_status_counts
        ),
        "rich_superset_count_per_signature": len(_rich_endpoint_supersets()),
        "rich_superset_signature_record_count": total_variant_records,
        "rich_superset_occurrence_record_count": total_occurrence_records,
        "rich_superset_obstructed_count": total_obstructed_records,
        "rich_superset_obstructed_occurrence_count": total_obstructed_occurrences,
        "rich_superset_status_counts": _json_counter(status_counts),
        "rich_superset_occurrence_status_counts": _json_counter(
            occurrence_status_counts
        ),
        "rich_superset_status_counts_by_size": _nested_counter(status_counts_by_size),
        "rich_superset_occurrence_status_counts_by_size": _nested_counter(
            occurrence_status_counts_by_size
        ),
        "exact_four_endpoint_rows": EXACT_FOUR_ENDPOINT_ROWS,
        "exact_four_status_counts": _json_counter(exact_four_status_counts),
        "exact_four_occurrence_status_counts": _json_counter(
            exact_four_occurrence_status_counts
        ),
        "target_status": TARGET_STATUS,
    }
    return records, summary


def _rich_endpoint_supersets() -> list[tuple[int, ...]]:
    endpoint_set = set(ENDPOINT_TRIPLE)
    variants: list[tuple[int, ...]] = []
    for size in range(1, len(ENDPOINT_EXTRA_LABEL_POOL) + 1):
        for extra in combinations(ENDPOINT_EXTRA_LABEL_POOL, size):
            variants.append(tuple(sorted(endpoint_set | set(extra))))
    return variants


def _rows_by_center(record: Mapping[str, Any]) -> dict[int, tuple[int, ...]]:
    rows: dict[int, tuple[int, ...]] = {}
    raw_rows = record.get("rows")
    if not isinstance(raw_rows, list):
        raise AssertionError("source cascade record rows missing")
    for row in raw_rows:
        if not isinstance(row, Mapping):
            raise AssertionError("source cascade row must be an object")
        center = int(row["center"])
        rows[center] = tuple(int(item) for item in row["witnesses"])
    if sorted(rows) != REQUIRED_CORE_CENTERS:
        raise AssertionError(f"unexpected cascade core centers: {sorted(rows)!r}")
    return rows


def _obstruction_rows(result: Any) -> list[int]:
    edges = result.self_edge_conflicts if result.self_edge_conflicts else result.cycle_edges
    return sorted({int(edge.row) for edge in edges})


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _nested_counter(counters: Mapping[int, Counter[str]]) -> dict[str, dict[str, int]]:
    return {
        str(key): _json_counter(counter)
        for key, counter in sorted(counters.items(), key=lambda item: item[0])
    }


def _validate_source(source: Mapping[str, Any], errors: list[str]) -> None:
    if source.get("schema") != SOURCE_CASCADE_SCHEMA:
        errors.append("source cascade row-criticality schema mismatch")
    if source.get("status") != SOURCE_CASCADE_STATUS:
        errors.append("source cascade row-criticality status mismatch")
    if source.get("trust") != TRUST:
        errors.append("source cascade row-criticality trust mismatch")
    summary = _mapping(source.get("summary"), "source summary", errors)
    if summary.get("criticality_status") != SOURCE_CRITICALITY_STATUS:
        errors.append("source cascade row-criticality criticality status mismatch")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, got {summary.get(key)!r}"
            )


def _validate_endpoint_records(records: Sequence[object], errors: list[str]) -> None:
    if len(records) != EXPECTED_SUMMARY["source_cascade_signature_count"]:
        errors.append("cascade_endpoint_records length mismatch")
    seen: set[int] = set()
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"cascade_endpoint_records[{index}] must be an object")
            continue
        signature_index = record.get("signature_index")
        if not isinstance(signature_index, int):
            errors.append(f"cascade_endpoint_records[{index}] signature missing")
            continue
        if signature_index in seen:
            errors.append(f"cascade_endpoint_records[{index}] duplicate signature")
        seen.add(signature_index)
        if record.get("endpoint_center") != ENDPOINT_CENTER:
            errors.append(f"cascade_endpoint_records[{index}] endpoint center mismatch")
        if record.get("endpoint_triple") != ENDPOINT_TRIPLE:
            errors.append(f"cascade_endpoint_records[{index}] endpoint triple mismatch")
        source_row8 = record.get("source_row8_witnesses")
        if source_row8 not in SOURCE_RECORDED_ENDPOINT_ROWS:
            errors.append(f"cascade_endpoint_records[{index}] source row8 mismatch")
        if record.get("rich_superset_count") != EXPECTED_SUMMARY[
            "rich_superset_count_per_signature"
        ]:
            errors.append(f"cascade_endpoint_records[{index}] superset count mismatch")
        if record.get("status_counts") != {"self_edge": 24, "strict_cycle": 7}:
            errors.append(f"cascade_endpoint_records[{index}] status count mismatch")
        if record.get("all_rich_supersets_obstructed") is not True:
            errors.append(f"cascade_endpoint_records[{index}] has clean rich superset")
        variants = record.get("variant_records")
        if not isinstance(variants, list):
            errors.append(f"cascade_endpoint_records[{index}] variants missing")
            continue
        if len(variants) != EXPECTED_SUMMARY["rich_superset_count_per_signature"]:
            errors.append(f"cascade_endpoint_records[{index}] variant length mismatch")
        for variant in variants:
            if not isinstance(variant, Mapping):
                errors.append(f"cascade_endpoint_records[{index}] bad variant")
                continue
            witnesses = variant.get("center8_witnesses")
            if not isinstance(witnesses, list) or not set(ENDPOINT_TRIPLE).issubset(
                witnesses
            ):
                errors.append(
                    f"cascade_endpoint_records[{index}] variant misses endpoint triple"
                )
            if variant.get("status") == "ok" or variant.get("obstructed") is not True:
                errors.append(f"cascade_endpoint_records[{index}] variant not obstructed")
    if seen != set(EXPECTED_SUMMARY["source_cascade_signature_indices"]):
        errors.append(
            "cascade signature set mismatch: "
            f"expected {EXPECTED_SUMMARY['source_cascade_signature_indices']!r}, "
            f"got {sorted(seen)!r}"
        )


def _source_summary(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        summary = {}
    return {
        "path": display_path(path, ROOT),
        "role": "source 151:6 label-4 cascade row-criticality",
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "criticality_status": summary.get("criticality_status"),
    }


def _mapping(value: object, name: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be an object")
        return {}
    return value


def _mapping_or_empty(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--source-cascade-row-criticality",
        type=Path,
        default=DEFAULT_SOURCE_CASCADE_ROW_CRITICALITY,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source = _resolve(args.source_cascade_row_criticality)

    generated = build_cascade_endpoint8_targets_payload(
        load_artifact(source),
        source_path=source,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(payload, source_path=source)
    if args.assert_expected:
        assert_expected_cascade_endpoint8_targets(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 cascade endpoint-8 targets")
        print(f"target row: {summary['target_row_key']}")
        print(f"endpoint center: {summary['endpoint_center']}")
        print(f"endpoint triple: {summary['endpoint_triple']}")
        print(
            "rich superset records: "
            f"{summary['rich_superset_signature_record_count']}"
        )
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: cascade endpoint-8 target packet verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
