#!/usr/bin/env python3
"""Generate or check the bootstrap/T12 singleton full-neighborhood crosswalk."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.path_display import display_path  # noqa: E402

SCHEMA = "erdos97.bootstrap_t12_singleton_full_neighborhood_crosswalk.v1"
STATUS = "BOOTSTRAP_T12_SINGLETON_FULL_NEIGHBORHOOD_CROSSWALK_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Cross-artifact proof-mining diagnostic joining the current bootstrap/T12 "
    "one-outside-label singleton-support full-neighborhood vertex-circle "
    "packets for targets 81:8, 151:5, and 151:8. It checks that the three "
    "target-row scans share the same natural n=9 order and full-neighborhood "
    "semantics, that basic filters leave 84 complete assignments including 63 "
    "non-original target rows, and that exact vertex-circle quotient replay "
    "kills all 84 by self-edge or strict-cycle obstructions. This is not "
    "singleton-support existence, not row forcing, not a proof of n=9, not a "
    "proof of the bridge, not a counterexample, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_bootstrap_t12_singleton_full_neighborhood_crosswalk.py",
    "command": (
        "python scripts/check_bootstrap_t12_singleton_full_neighborhood_crosswalk.py "
        "--write --assert-expected"
    ),
}

DEFAULT_SOURCE_81_8 = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_8_full_neighborhood_vertex_circle.json"
)
DEFAULT_SOURCE_151 = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.json"
)
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_singleton_full_neighborhood_crosswalk.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "cyclic_order",
    "interpretation",
    "n",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "summary",
    "target_crosswalk",
    "trust",
    "validation_errors",
    "validation_status",
}
EXPECTED_TARGET_KEYS = {
    "basic_filter_complete_assignment_count",
    "bootstrap_core_witnesses",
    "empty_domain_count",
    "free_row_replacement_count_per_center",
    "implicit_assignment_space_size",
    "non_original_basic_assignment_count",
    "search_node_count",
    "source_artifact_id",
    "source_record_id",
    "target_center",
    "target_center_candidate_count",
    "target_row_key",
    "vertex_circle_status_counts",
    "vertex_circle_surviving_assignment_count",
}
EXPECTED_TARGET_ROW_KEYS = ["81:8", "151:5", "151:8"]
EXPECTED_CYCLIC_ORDER = list(range(9))
EXPECTED_SCAN_STATUS = "FULL_NEIGHBORHOOD_BASIC_SURVIVORS_ALL_VERTEX_CIRCLE_OBSTRUCTED"


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_singleton_full_neighborhood_crosswalk_payload(
    source_81_8: Mapping[str, Any],
    source_151: Mapping[str, Any],
    *,
    source_81_8_path: Path = DEFAULT_SOURCE_81_8,
    source_151_path: Path = DEFAULT_SOURCE_151,
) -> dict[str, Any]:
    """Return the crosswalk payload for singleton full-neighborhood packets."""

    errors: list[str] = []
    _validate_source_81_8(source_81_8, errors)
    _validate_source_151(source_151, errors)

    target_crosswalk = [
        _target_from_81_8(source_81_8, source_81_8_path, errors),
        *_targets_from_151(source_151, source_151_path, errors),
    ]
    target_crosswalk.sort(key=lambda item: EXPECTED_TARGET_ROW_KEYS.index(item["target_row_key"]))
    summary = _summary(target_crosswalk)
    cyclic_order = _same_cyclic_order(source_81_8, source_151, target_crosswalk, errors)

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "cyclic_order": cyclic_order,
        "summary": summary,
        "target_crosswalk": target_crosswalk,
        "source_artifacts": [
            _source_summary(
                source_81_8_path,
                "source-81 row-8 full-neighborhood vertex-circle packet",
                source_81_8,
            ),
            _source_summary(
                source_151_path,
                "source-151 singleton full-neighborhood vertex-circle packet",
                source_151,
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": [
            "All three one-outside-label singleton-support row targets now have full-neighborhood vertex-circle diagnostics.",
            "Basic incidence/crossing filters do not force the original target rows in the full neighborhood.",
            "The recorded complete basic-filter assignments are all killed by exact vertex-circle quotient replay.",
            "The remaining bridge gap is genuine singleton-support/rich-class existence and row forcing, not this selected-row neighborhood.",
        ],
        "provenance": PROVENANCE,
    }
    assert_expected_singleton_full_neighborhood_crosswalk(payload)
    return payload


def assert_expected_singleton_full_neighborhood_crosswalk(
    payload: Mapping[str, Any],
) -> None:
    """Assert the expected singleton full-neighborhood crosswalk."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    source_81_8_path: Path = DEFAULT_SOURCE_81_8,
    source_151_path: Path = DEFAULT_SOURCE_151,
) -> list[str]:
    """Return validation errors for a crosswalk payload."""

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
        "n": 9,
        "cyclic_order": EXPECTED_CYCLIC_ORDER,
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
            "not singleton-support existence",
            "not row forcing",
            "not a proof of n=9",
            "not a proof of the bridge",
            "not a counterexample",
            "not a global status update",
        ):
            if phrase not in claim_scope:
                errors.append(f"claim_scope must contain {phrase!r}")

    records = payload.get("target_crosswalk")
    if not isinstance(records, list):
        errors.append("target_crosswalk must be a list")
        return errors
    if [
        record.get("target_row_key") for record in records if isinstance(record, Mapping)
    ] != EXPECTED_TARGET_ROW_KEYS:
        errors.append("target row keys mismatch")
    for record in records:
        if not isinstance(record, Mapping):
            errors.append("target_crosswalk entries must be objects")
            continue
        _validate_target_record(record, errors)

    _validate_summary(payload.get("summary"), records, errors)
    if recompute and not errors:
        generated = build_singleton_full_neighborhood_crosswalk_payload(
            load_artifact(source_81_8_path),
            load_artifact(source_151_path),
            source_81_8_path=source_81_8_path,
            source_151_path=source_151_path,
        )
        if dict(payload) != generated:
            errors.append("stored artifact is stale relative to source packets")
    return errors


def summary_payload(path: Path, payload: Mapping[str, Any], errors: Sequence[str]) -> dict[str, Any]:
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
        "target_count": summary.get("target_count"),
        "target_row_keys": summary.get("target_row_keys"),
        "basic_filter_complete_assignment_count": summary.get(
            "basic_filter_complete_assignment_count"
        ),
        "basic_filter_non_original_assignment_count": summary.get(
            "basic_filter_non_original_assignment_count"
        ),
        "vertex_circle_status_counts": summary.get("vertex_circle_status_counts"),
        "vertex_circle_surviving_assignment_count": summary.get(
            "vertex_circle_surviving_assignment_count"
        ),
        "validation_errors": list(errors),
    }


def _validate_source_81_8(source: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "schema": "erdos97.bootstrap_t12_81_8_full_neighborhood_vertex_circle.v1",
        "status": "BOOTSTRAP_T12_81_8_FULL_NEIGHBORHOOD_VERTEX_CIRCLE_DIAGNOSTIC_ONLY",
        "trust": TRUST,
    }
    _validate_source_meta("source 81:8", source, expected, errors)
    summary = source.get("summary")
    if not isinstance(summary, Mapping):
        errors.append("source 81:8 summary must be an object")
        return
    _expect_summary_field("source 81:8", summary, "target_row_key", "81:8", errors)
    _expect_summary_field("source 81:8", summary, "cyclic_order", EXPECTED_CYCLIC_ORDER, errors)
    _expect_summary_field("source 81:8", summary, "scan_status", EXPECTED_SCAN_STATUS, errors)
    _expect_summary_field("source 81:8", summary, "vertex_circle_surviving_assignment_count", 0, errors)
    _expect_summary_field("source 81:8", summary, "non_original_vertex_circle_surviving_assignment_count", 0, errors)


def _validate_source_151(source: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "schema": "erdos97.bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.v1",
        "status": "BOOTSTRAP_T12_151_SINGLETON_FULL_NEIGHBORHOOD_VERTEX_CIRCLE_DIAGNOSTIC_ONLY",
        "trust": TRUST,
    }
    _validate_source_meta("source 151", source, expected, errors)
    summary = source.get("summary")
    if not isinstance(summary, Mapping):
        errors.append("source 151 summary must be an object")
        return
    _expect_summary_field("source 151", summary, "target_row_keys", ["151:5", "151:8"], errors)
    _expect_summary_field("source 151", summary, "cyclic_order", EXPECTED_CYCLIC_ORDER, errors)
    _expect_summary_field("source 151", summary, "scan_status", EXPECTED_SCAN_STATUS, errors)
    _expect_summary_field("source 151", summary, "vertex_circle_surviving_assignment_count", 0, errors)
    _expect_summary_field("source 151", summary, "non_original_vertex_circle_surviving_assignment_count", 0, errors)


def _validate_source_meta(
    label: str,
    source: Mapping[str, Any],
    expected: Mapping[str, str],
    errors: list[str],
) -> None:
    for key, expected_value in expected.items():
        if source.get(key) != expected_value:
            errors.append(
                f"{label} {key} mismatch: expected {expected_value!r}, got {source.get(key)!r}"
            )


def _target_from_81_8(
    source: Mapping[str, Any],
    source_path: Path,
    errors: list[str],
) -> dict[str, Any]:
    summary = _summary_mapping(source, "source 81:8", errors)
    return {
        "target_row_key": "81:8",
        "source_record_id": 81,
        "source_artifact_id": source_path.stem,
        "target_center": _int(summary.get("target_center")),
        "bootstrap_core_witnesses": summary.get("bootstrap_core_witnesses"),
        "target_center_candidate_count": _int(summary.get("target_center_candidate_count")),
        "free_row_replacement_count_per_center": _int(
            summary.get("free_row_replacement_count_per_center")
        ),
        "implicit_assignment_space_size": _int(summary.get("implicit_assignment_space_size")),
        "basic_filter_complete_assignment_count": _int(
            summary.get("basic_filter_complete_assignment_count")
        ),
        "non_original_basic_assignment_count": _int(
            summary.get("basic_filter_non_original_row8_assignment_count")
        ),
        "vertex_circle_status_counts": _status_counts(summary.get("vertex_circle_status_counts")),
        "vertex_circle_surviving_assignment_count": _int(
            summary.get("vertex_circle_surviving_assignment_count")
        ),
        "search_node_count": _int(summary.get("search_node_count")),
        "empty_domain_count": _int(summary.get("empty_domain_count")),
    }


def _targets_from_151(
    source: Mapping[str, Any],
    source_path: Path,
    errors: list[str],
) -> list[dict[str, Any]]:
    target_audits = source.get("target_audits")
    if not isinstance(target_audits, list):
        errors.append("source 151 target_audits must be a list")
        return []
    records = []
    for audit in target_audits:
        if not isinstance(audit, Mapping):
            errors.append("source 151 target_audits entries must be objects")
            continue
        records.append(
            {
                "target_row_key": str(audit.get("target_row_key")),
                "source_record_id": 151,
                "source_artifact_id": source_path.stem,
                "target_center": _int(audit.get("target_center")),
                "bootstrap_core_witnesses": audit.get("bootstrap_core_witnesses"),
                "target_center_candidate_count": _int(
                    audit.get("target_center_candidate_count")
                ),
                "free_row_replacement_count_per_center": 70,
                "implicit_assignment_space_size": 5188320900000000,
                "basic_filter_complete_assignment_count": _int(
                    audit.get("basic_filter_complete_assignment_count")
                ),
                "non_original_basic_assignment_count": _int(
                    audit.get("non_original_target_basic_assignment_count")
                ),
                "vertex_circle_status_counts": _status_counts(
                    audit.get("vertex_circle_status_counts")
                ),
                "vertex_circle_surviving_assignment_count": _int(
                    audit.get("vertex_circle_surviving_assignment_count")
                ),
                "search_node_count": _int(audit.get("search_node_count")),
                "empty_domain_count": _int(audit.get("empty_domain_count")),
            }
        )
    return records


def _summary(targets: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    status_counts: Counter[str] = Counter()
    for target in targets:
        status_counts.update(target["vertex_circle_status_counts"])
    return {
        "target_count": len(targets),
        "target_row_keys": [target["target_row_key"] for target in targets],
        "source_record_ids": sorted({int(target["source_record_id"]) for target in targets}),
        "implicit_assignment_space_size": sum(
            int(target["implicit_assignment_space_size"]) for target in targets
        ),
        "free_row_replacement_count_per_center": 70,
        "target_center_candidate_count": sum(
            int(target["target_center_candidate_count"]) for target in targets
        ),
        "basic_filter_complete_assignment_count": sum(
            int(target["basic_filter_complete_assignment_count"]) for target in targets
        ),
        "basic_filter_non_original_assignment_count": sum(
            int(target["non_original_basic_assignment_count"]) for target in targets
        ),
        "vertex_circle_status_counts": dict(sorted(status_counts.items())),
        "vertex_circle_surviving_assignment_count": sum(
            int(target["vertex_circle_surviving_assignment_count"])
            for target in targets
        ),
        "non_original_vertex_circle_surviving_assignment_count": 0,
        "search_node_count": sum(int(target["search_node_count"]) for target in targets),
        "empty_domain_count": sum(int(target["empty_domain_count"]) for target in targets),
        "scan_status": EXPECTED_SCAN_STATUS,
        "remaining_gap": (
            "The crosswalk does not prove singleton support existence, does "
            "not prove the target rows are forced by minimal or rich-class "
            "geometry, does not model additional auxiliary rich supports, and "
            "does not promote the review-pending n=9 checker."
        ),
    }


def _same_cyclic_order(
    source_81_8: Mapping[str, Any],
    source_151: Mapping[str, Any],
    targets: Sequence[Mapping[str, Any]],
    errors: list[str],
) -> list[int]:
    if not targets:
        errors.append("target_crosswalk is empty")
    source_81_8_summary = _summary_mapping(source_81_8, "source 81:8", errors)
    source_151_summary = _summary_mapping(source_151, "source 151", errors)
    if source_81_8_summary.get("cyclic_order") != EXPECTED_CYCLIC_ORDER:
        errors.append("source 81:8 cyclic_order mismatch")
    if source_151_summary.get("cyclic_order") != EXPECTED_CYCLIC_ORDER:
        errors.append("source 151 cyclic_order mismatch")
    return EXPECTED_CYCLIC_ORDER


def _validate_target_record(record: Mapping[str, Any], errors: list[str]) -> None:
    if set(record) != EXPECTED_TARGET_KEYS:
        errors.append(
            f"{record.get('target_row_key')} target keys mismatch: "
            f"expected {sorted(EXPECTED_TARGET_KEYS)!r}, got {sorted(record)!r}"
        )
        return
    key = record.get("target_row_key")
    if key not in EXPECTED_TARGET_ROW_KEYS:
        errors.append(f"unexpected target row key {key!r}")
    if record.get("free_row_replacement_count_per_center") != 70:
        errors.append(f"{key} free row replacement count mismatch")
    if record.get("target_center_candidate_count") != 9:
        errors.append(f"{key} target candidate count mismatch")
    if record.get("implicit_assignment_space_size") != 5188320900000000:
        errors.append(f"{key} implicit assignment space mismatch")
    if record.get("vertex_circle_surviving_assignment_count") != 0:
        errors.append(f"{key} must have zero vertex-circle survivors")
    status_counts = record.get("vertex_circle_status_counts")
    if not isinstance(status_counts, Mapping):
        errors.append(f"{key} vertex_circle_status_counts must be an object")
    else:
        status_total = sum(int(value) for value in status_counts.values())
        if status_total != record.get("basic_filter_complete_assignment_count"):
            errors.append(f"{key} status counts do not sum to basic survivors")


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
                f"summary.{key} mismatch: expected {expected_value!r}, got {summary.get(key)!r}"
            )
    pinned = {
        "target_count": 3,
        "target_row_keys": EXPECTED_TARGET_ROW_KEYS,
        "source_record_ids": [81, 151],
        "implicit_assignment_space_size": 15564962700000000,
        "target_center_candidate_count": 27,
        "basic_filter_complete_assignment_count": 84,
        "basic_filter_non_original_assignment_count": 63,
        "vertex_circle_status_counts": {"self_edge": 64, "strict_cycle": 20},
        "vertex_circle_surviving_assignment_count": 0,
        "non_original_vertex_circle_surviving_assignment_count": 0,
        "search_node_count": 38719,
        "empty_domain_count": 20395,
        "scan_status": EXPECTED_SCAN_STATUS,
    }
    for key, expected_value in pinned.items():
        if summary.get(key) != expected_value:
            errors.append(
                f"summary.{key} pinned mismatch: expected {expected_value!r}, got {summary.get(key)!r}"
            )


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
    }


def _summary_mapping(source: Mapping[str, Any], label: str, errors: list[str]) -> Mapping[str, Any]:
    summary = source.get("summary")
    if not isinstance(summary, Mapping):
        errors.append(f"{label} summary must be an object")
        return {}
    return summary


def _expect_summary_field(
    label: str,
    summary: Mapping[str, Any],
    key: str,
    expected: object,
    errors: list[str],
) -> None:
    if summary.get(key) != expected:
        errors.append(
            f"{label} summary.{key} mismatch: expected {expected!r}, got {summary.get(key)!r}"
        )


def _status_counts(value: object) -> dict[str, int]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): int(value[key]) for key in sorted(value)}


def _int(value: object) -> int:
    if not isinstance(value, int):
        raise AssertionError(f"expected integer, got {value!r}")
    return value


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--source-81-8", type=Path, default=DEFAULT_SOURCE_81_8)
    parser.add_argument("--source-151", type=Path, default=DEFAULT_SOURCE_151)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_81_8 = _resolve(args.source_81_8)
    source_151 = _resolve(args.source_151)

    generated = build_singleton_full_neighborhood_crosswalk_payload(
        load_artifact(source_81_8),
        load_artifact(source_151),
        source_81_8_path=source_81_8,
        source_151_path=source_151,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale relative to sources")
        payload = stored

    errors = validate_payload(
        payload,
        source_81_8_path=source_81_8,
        source_151_path=source_151,
    )
    if args.assert_expected:
        assert_expected_singleton_full_neighborhood_crosswalk(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 singleton full-neighborhood crosswalk")
        print(f"target rows: {summary['target_row_keys']}")
        print(f"basic survivors: {summary['basic_filter_complete_assignment_count']}")
        print(f"non-original survivors: {summary['basic_filter_non_original_assignment_count']}")
        print(f"vertex-circle statuses: {summary['vertex_circle_status_counts']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: singleton full-neighborhood crosswalk verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
