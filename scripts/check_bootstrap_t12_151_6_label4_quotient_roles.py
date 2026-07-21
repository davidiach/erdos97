#!/usr/bin/env python3
"""Check the bootstrap/T12 151:6 label-4 quotient-role targets."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erdos97.json_io import write_json  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    SelectedRow,
    _distance_class_union_find,
    pair,
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


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_quotient_roles.v1"
STATUS = "BOOTSTRAP_T12_151_6_LABEL4_QUOTIENT_ROLES_DIAGNOSTIC_ONLY"
ROLE_STATUS = "LABEL4_REACHES_EVERY_LABEL8_FREE_RESIDUAL_STRICT_CYCLE"
CLAIM_SCOPE = (
    "Proof-target diagnostic for the source-151 row-6 private-halo-only "
    "outside-pair lane. It classifies how auxiliary label 4 reaches the "
    "strict quotient cycles in the 10 distinct exact label-8-free residual "
    "signatures. Every residual strict cycle has a label-4-bearing quotient "
    "class; 8 signatures reach label 4 directly through cycle-edge endpoints, "
    "and 2 reach label 4 only through selected-distance quotient equalities. "
    "This does not prove outside-pair support existence, does not prove row "
    "forcing, does not prove pair [3,5] impossible, does not prove endpoint-8 "
    "forcing, does not prove n=9, does not prove the bridge, is not a "
    "counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_bootstrap_t12_151_6_label4_quotient_roles.py",
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label4_quotient_roles.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_quotient_roles.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "interpretation",
    "provenance",
    "quotient_role_records",
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
    "signatures_with_label4_cycle_quotient_class": 10,
    "occurrences_with_label4_cycle_quotient_class": 12,
    "direct_cycle_edge_label4_signature_count": 8,
    "direct_cycle_edge_label4_occurrence_count": 10,
    "quotient_equality_only_label4_signature_count": 2,
    "quotient_equality_only_label4_occurrence_count": 2,
    "label4_cycle_quotient_class_signature_incidence_count": 19,
    "label4_cycle_quotient_class_occurrence_incidence_count": 23,
    "label4_cycle_quotient_class_count_signature_counts": {
        "1": 3,
        "2": 5,
        "3": 2,
    },
    "label4_cycle_quotient_class_count_occurrence_counts": {
        "1": 3,
        "2": 7,
        "3": 2,
    },
    "label4_pair_members_per_cycle_class_signature_counts": {
        "1": 16,
        "2": 2,
        "4": 1,
    },
    "label4_pair_members_per_cycle_class_occurrence_counts": {
        "1": 19,
        "2": 3,
        "4": 1,
    },
    "direct_cycle_edge_label4_auxiliary_pair_signature_counts": {
        "2,3": 2,
        "2,5": 1,
        "2,7": 1,
        "3,7": 1,
        "5,8": 3,
    },
    "direct_cycle_edge_label4_auxiliary_pair_occurrence_counts": {
        "2,3": 3,
        "2,5": 1,
        "2,7": 1,
        "3,7": 1,
        "5,8": 4,
    },
    "quotient_equality_only_auxiliary_pair_signature_counts": {
        "3,5": 1,
        "4,5": 1,
    },
    "quotient_equality_only_auxiliary_pair_occurrence_counts": {
        "3,5": 1,
        "4,5": 1,
    },
    "role_status": ROLE_STATUS,
}


def build_label4_quotient_roles_payload(
    source_residual_targets: Mapping[str, Any],
    *,
    source_residual_targets_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGETS,
) -> dict[str, Any]:
    """Return the deterministic label-4 quotient-role payload."""

    errors: list[str] = []
    assert_expected_label8_free_residual_targets(source_residual_targets)
    _validate_source_residual_targets(source_residual_targets, errors)
    records, summary = _quotient_role_records(source_residual_targets)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "quotient_role_records": records,
        "source_artifacts": [
            _source_summary(
                source_residual_targets_path,
                "source 151:6 label-8-free residual targets",
                source_residual_targets,
            )
        ],
        "interpretation": [
            (
                "Label 4 reaches every residual strict cycle at the quotient-"
                "class level, not only at the raw auxiliary-row level."
            ),
            (
                "Eight signatures, covering 10 occurrences, expose label 4 "
                "directly in the chosen strict-cycle edge endpoints."
            ),
            (
                "The remaining two signatures expose label 4 only after "
                "quotienting by selected-distance equalities."
            ),
            (
                "This is a bridge-target ledger only; it does not prove "
                "support existence, row forcing, endpoint-8 forcing, or "
                "impossibility of the private pair."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_label4_quotient_roles(payload)
    return payload


def assert_expected_label4_quotient_roles(payload: Mapping[str, Any]) -> None:
    """Assert the pinned label-4 quotient-role ledger."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    source_residual_targets_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGETS,
) -> list[str]:
    """Return validation errors for a label-4 quotient-role payload."""

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
    records = payload.get("quotient_role_records")
    if not isinstance(records, list):
        errors.append("quotient_role_records must be a list")
    else:
        _validate_quotient_role_records(records, errors)
    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("does not prove support existence" in item for item in interpretation):
        errors.append("interpretation must preserve the support-existence nonclaim")

    if recompute and not errors:
        generated = build_label4_quotient_roles_payload(
            load_artifact(source_residual_targets_path),
            source_residual_targets_path=source_residual_targets_path,
        )
        if dict(payload) != generated:
            errors.append("stored artifact is stale relative to residual targets")
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
        "signatures_with_label4_cycle_quotient_class": summary.get(
            "signatures_with_label4_cycle_quotient_class"
        ),
        "direct_cycle_edge_label4_signature_count": summary.get(
            "direct_cycle_edge_label4_signature_count"
        ),
        "quotient_equality_only_label4_signature_count": summary.get(
            "quotient_equality_only_label4_signature_count"
        ),
        "label4_cycle_quotient_class_signature_incidence_count": summary.get(
            "label4_cycle_quotient_class_signature_incidence_count"
        ),
        "role_status": summary.get("role_status"),
        "validation_errors": list(errors),
    }


def _quotient_role_records(
    source_residual_targets: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    mode_signature_counts: Counter[str] = Counter()
    mode_occurrence_counts: Counter[str] = Counter()
    label4_class_count_signature_counts: Counter[int] = Counter()
    label4_class_count_occurrence_counts: Counter[int] = Counter()
    label4_members_signature_counts: Counter[int] = Counter()
    label4_members_occurrence_counts: Counter[int] = Counter()
    direct_pair_signature_counts: Counter[str] = Counter()
    direct_pair_occurrence_counts: Counter[str] = Counter()
    equality_pair_signature_counts: Counter[str] = Counter()
    equality_pair_occurrence_counts: Counter[str] = Counter()
    signatures_with_label4_cycle_class = 0
    occurrences_with_label4_cycle_class = 0
    label4_class_signature_incidence_count = 0
    label4_class_occurrence_incidence_count = 0
    total_occurrences = 0

    for source_record in source_residual_targets["residual_signature_records"]:
        signature_index = int(source_record["signature_index"])
        multiplicity = int(source_record["multiplicity"])
        total_occurrences += multiplicity
        rows = {
            int(row["center"]): tuple(int(witness) for witness in row["witnesses"])
            for row in source_record["rows"]
        }
        selected_rows = [
            SelectedRow(center=center, witnesses=witnesses)
            for center, witnesses in rows.items()
        ]
        quotient_classes = _distance_classes(9, selected_rows)
        cycle_classes = sorted(
            {
                tuple(edge["outer_class"])
                for edge in source_record["cycle_edges"]
            }
            | {
                tuple(edge["inner_class"])
                for edge in source_record["cycle_edges"]
            }
        )
        label4_cycle_classes = [
            {
                "quotient_class": list(quotient_class),
                "label4_pair_members": [
                    list(pair_member)
                    for pair_member in quotient_classes[quotient_class]
                    if 4 in pair_member
                ],
                "all_class_members": [
                    list(pair_member) for pair_member in quotient_classes[quotient_class]
                ],
            }
            for quotient_class in cycle_classes
            if any(4 in pair_member for pair_member in quotient_classes[quotient_class])
        ]
        label4_touching_edges = [
            edge
            for edge in source_record["cycle_edges"]
            if 4 in edge["outer_pair"] or 4 in edge["inner_pair"]
        ]
        access_mode = (
            "direct_cycle_edge"
            if label4_touching_edges
            else "quotient_equality_only"
        )
        auxiliary_pair = str(source_record["auxiliary_center_pair"])
        mode_signature_counts[access_mode] += 1
        mode_occurrence_counts[access_mode] += multiplicity
        if access_mode == "direct_cycle_edge":
            direct_pair_signature_counts[auxiliary_pair] += 1
            direct_pair_occurrence_counts[auxiliary_pair] += multiplicity
        else:
            equality_pair_signature_counts[auxiliary_pair] += 1
            equality_pair_occurrence_counts[auxiliary_pair] += multiplicity
        if label4_cycle_classes:
            signatures_with_label4_cycle_class += 1
            occurrences_with_label4_cycle_class += multiplicity
        label4_class_count_signature_counts[len(label4_cycle_classes)] += 1
        label4_class_count_occurrence_counts[len(label4_cycle_classes)] += multiplicity
        label4_class_signature_incidence_count += len(label4_cycle_classes)
        label4_class_occurrence_incidence_count += (
            len(label4_cycle_classes) * multiplicity
        )
        for class_record in label4_cycle_classes:
            member_count = len(class_record["label4_pair_members"])
            label4_members_signature_counts[member_count] += 1
            label4_members_occurrence_counts[member_count] += multiplicity
        records.append(
            {
                "signature_index": signature_index,
                "multiplicity": multiplicity,
                "auxiliary_center_pair": auxiliary_pair,
                "access_mode": access_mode,
                "direct_label4_cycle_edge_count": len(label4_touching_edges),
                "label4_cycle_quotient_class_count": len(label4_cycle_classes),
                "cycle_quotient_classes": [
                    list(quotient_class) for quotient_class in cycle_classes
                ],
                "label4_cycle_quotient_classes": label4_cycle_classes,
                "direct_label4_cycle_edges": label4_touching_edges,
            }
        )

    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "label8_free_distinct_exact_signature_count": len(records),
        "label8_free_occurrence_count": total_occurrences,
        "signatures_with_label4_cycle_quotient_class": (
            signatures_with_label4_cycle_class
        ),
        "occurrences_with_label4_cycle_quotient_class": (
            occurrences_with_label4_cycle_class
        ),
        "direct_cycle_edge_label4_signature_count": mode_signature_counts[
            "direct_cycle_edge"
        ],
        "direct_cycle_edge_label4_occurrence_count": mode_occurrence_counts[
            "direct_cycle_edge"
        ],
        "quotient_equality_only_label4_signature_count": mode_signature_counts[
            "quotient_equality_only"
        ],
        "quotient_equality_only_label4_occurrence_count": mode_occurrence_counts[
            "quotient_equality_only"
        ],
        "label4_cycle_quotient_class_signature_incidence_count": (
            label4_class_signature_incidence_count
        ),
        "label4_cycle_quotient_class_occurrence_incidence_count": (
            label4_class_occurrence_incidence_count
        ),
        "label4_cycle_quotient_class_count_signature_counts": _json_counter(
            label4_class_count_signature_counts
        ),
        "label4_cycle_quotient_class_count_occurrence_counts": _json_counter(
            label4_class_count_occurrence_counts
        ),
        "label4_pair_members_per_cycle_class_signature_counts": _json_counter(
            label4_members_signature_counts
        ),
        "label4_pair_members_per_cycle_class_occurrence_counts": _json_counter(
            label4_members_occurrence_counts
        ),
        "direct_cycle_edge_label4_auxiliary_pair_signature_counts": _json_counter(
            direct_pair_signature_counts
        ),
        "direct_cycle_edge_label4_auxiliary_pair_occurrence_counts": _json_counter(
            direct_pair_occurrence_counts
        ),
        "quotient_equality_only_auxiliary_pair_signature_counts": _json_counter(
            equality_pair_signature_counts
        ),
        "quotient_equality_only_auxiliary_pair_occurrence_counts": _json_counter(
            equality_pair_occurrence_counts
        ),
        "role_status": ROLE_STATUS,
    }
    return records, summary


def _distance_classes(
    n: int,
    selected_rows: Sequence[SelectedRow],
) -> dict[tuple[int, int], list[tuple[int, int]]]:
    uf = _distance_class_union_find(n, selected_rows)
    classes: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for a, b in combinations(range(n), 2):
        pair_member = pair(a, b)
        classes[uf.find(pair_member)].append(pair_member)
    return {key: sorted(value) for key, value in classes.items()}


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


def _validate_quotient_role_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != EXPECTED_SUMMARY["label8_free_distinct_exact_signature_count"]:
        errors.append("quotient_role_records length mismatch")
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"quotient_role_records[{index}] must be an object")
            continue
        if record.get("signature_index") != index:
            errors.append(f"quotient_role_records[{index}] signature_index mismatch")
        mode = record.get("access_mode")
        if mode not in {"direct_cycle_edge", "quotient_equality_only"}:
            errors.append(f"quotient_role_records[{index}] invalid access_mode")
        label4_classes = record.get("label4_cycle_quotient_classes")
        if not isinstance(label4_classes, list) or not label4_classes:
            errors.append(
                f"quotient_role_records[{index}] must have label-4 cycle classes"
            )
            continue
        if int(record.get("label4_cycle_quotient_class_count", 0)) != len(
            label4_classes
        ):
            errors.append(
                f"quotient_role_records[{index}] label-4 class count mismatch"
            )
        direct_edges = record.get("direct_label4_cycle_edges")
        if not isinstance(direct_edges, list):
            errors.append(f"quotient_role_records[{index}] direct edges mismatch")
        elif mode == "direct_cycle_edge" and not direct_edges:
            errors.append(f"quotient_role_records[{index}] missing direct label-4 edge")
        elif mode == "quotient_equality_only" and direct_edges:
            errors.append(
                f"quotient_role_records[{index}] equality-only record has direct edge"
            )
        for class_record in label4_classes:
            if not isinstance(class_record, Mapping):
                errors.append(
                    f"quotient_role_records[{index}] label-4 class must be object"
                )
                continue
            if not class_record.get("label4_pair_members"):
                errors.append(
                    f"quotient_role_records[{index}] label-4 class has no pair members"
                )


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
        "target_status": (
            summary.get("target_status") if isinstance(summary, Mapping) else None
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
        "--source-residual-targets",
        type=Path,
        default=DEFAULT_SOURCE_RESIDUAL_TARGETS,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_residual_targets = _resolve(args.source_residual_targets)

    generated = build_label4_quotient_roles_payload(
        load_artifact(source_residual_targets),
        source_residual_targets_path=source_residual_targets,
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
    )
    if args.assert_expected:
        assert_expected_label4_quotient_roles(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 quotient roles")
        print(f"target row: {summary['target_row_key']}")
        print(
            "signatures with label-4 cycle class: "
            f"{summary['signatures_with_label4_cycle_quotient_class']}"
        )
        print(
            "direct label-4 signatures: "
            f"{summary['direct_cycle_edge_label4_signature_count']}"
        )
        print(
            "quotient-equality-only signatures: "
            f"{summary['quotient_equality_only_label4_signature_count']}"
        )
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: 151:6 label-4 quotient roles verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
