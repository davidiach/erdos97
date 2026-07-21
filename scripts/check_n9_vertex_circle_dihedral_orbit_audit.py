#!/usr/bin/env python3
"""Audit stored n=9 dihedral motif orbits from input artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from erdos97.json_io import load_json
from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]

N = 9
ROW_SIZE = 4
DEFAULT_MOTIF_FAMILIES = ROOT / "data" / "certificates" / "n9_vertex_circle_motif_families.json"
DEFAULT_FRONTIER_CLASSIFICATION = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)

SCHEMA = "erdos97.n9_vertex_circle_dihedral_orbit_audit.v1"
STATUS = "REVIEW_PENDING_DIHEDRAL_ORBIT_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Second-source dihedral orbit bookkeeping audit for the review-pending "
    "n=9 vertex-circle frontier. It treats the stored motif-family artifact "
    "and frontier classification artifact as inputs, independently recomputes "
    "the 18 dihedral relabelings, verifies canonical representatives, orbit "
    "sizes, orbit disjointness, and assignment-to-orbit maps. It does not "
    "prove frontier coverage, filter soundness, strict-edge geometry, "
    "selected-distance quotient soundness, n=9, a counterexample, or any "
    "official/global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_dihedral_orbit_audit.py",
    "command": (
        "python scripts/check_n9_vertex_circle_dihedral_orbit_audit.py "
        "--check --assert-expected --json"
    ),
}
SUMMARY_JSON_KEYS = (
    "schema",
    "status",
    "trust",
    "claim_scope",
    "n",
    "row_size",
    "dihedral_map_count",
    "source_artifacts",
    "validation_status",
    "validation_errors",
    "interpretation",
    "provenance",
)
DIHEDRAL_ORBIT_SUMMARY_KEYS = (
    "family_count",
    "classification_assignment_count",
    "unique_classification_row_count",
    "orbit_union_row_count",
    "orbit_union_status_counts",
    "classification_status_counts",
    "family_status_counts",
    "orbit_size_counts",
    "canonical_rep_mismatches",
    "orbit_size_mismatches",
    "orbit_overlap_count",
    "classification_missing_from_orbits",
    "orbit_missing_from_classification",
    "classification_duplicate_rows",
    "classification_family_mismatches",
    "classification_status_mismatches",
    "canonical_label_map_mismatches",
    "assignment_id_mismatches",
    "orbit_union_rows_sha256",
    "classification_rows_sha256",
)

EXPECTED_ASSIGNMENT_COUNT = 184
EXPECTED_FAMILY_COUNT = 16
EXPECTED_FAMILY_STATUS_COUNTS = {"self_edge": 13, "strict_cycle": 3}
EXPECTED_ORBIT_SIZE_COUNTS = {"2": 5, "6": 2, "18": 9}
EXPECTED_STATUS_COUNTS = {"self_edge": 158, "strict_cycle": 26}
EXPECTED_ROWS_SHA256 = "dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55"

Rows = tuple[tuple[int, ...], ...]
LabelMap = tuple[int, ...]


def dihedral_orbit_audit_payload(
    *,
    motif_path: Path = DEFAULT_MOTIF_FAMILIES,
    classification_path: Path = DEFAULT_FRONTIER_CLASSIFICATION,
) -> dict[str, Any]:
    """Return the n=9 dihedral-orbit audit payload."""

    motif = load_json(motif_path)
    classification = load_json(classification_path)
    errors: list[str] = []
    summary = _audit_orbits(motif, classification, errors)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "row_size": ROW_SIZE,
        "dihedral_map_count": len(_dihedral_maps()),
        "dihedral_orbit_audit": summary,
        "source_artifacts": [
            {
                "path": display_path(motif_path, ROOT),
                "type": motif.get("type"),
                "trust": motif.get("trust"),
            },
            {
                "path": display_path(classification_path, ROOT),
                "schema": classification.get("schema"),
                "status": classification.get("status"),
                "trust": classification.get("trust"),
            },
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says the stored 16 motif-family representatives "
            "are canonical under an independently replayed dihedral action, "
            "their labelled orbits are disjoint and total 184 rows, and the "
            "stored 184 frontier-classification rows match those orbits with "
            "stable canonical label maps. This is orbit bookkeeping only."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_dihedral_orbit_audit(payload: Mapping[str, Any]) -> None:
    """Assert stable expected counts for the dihedral orbit audit."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
    if payload.get("claim_scope") != CLAIM_SCOPE:
        raise AssertionError(f"claim_scope mismatch: {payload.get('claim_scope')!r}")
    claim_scope = CLAIM_SCOPE
    for required in (
        "does not prove frontier coverage",
        "filter soundness",
        "strict-edge geometry",
        "selected-distance quotient soundness",
        "n=9",
        "counterexample",
        "official/global status update",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")
    summary = payload.get("dihedral_orbit_audit")
    if not isinstance(summary, Mapping):
        raise AssertionError("dihedral_orbit_audit missing")
    expected = {
        "family_count": EXPECTED_FAMILY_COUNT,
        "classification_assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "unique_classification_row_count": EXPECTED_ASSIGNMENT_COUNT,
        "orbit_union_row_count": EXPECTED_ASSIGNMENT_COUNT,
        "orbit_union_status_counts": EXPECTED_STATUS_COUNTS,
        "classification_status_counts": EXPECTED_STATUS_COUNTS,
        "family_status_counts": EXPECTED_FAMILY_STATUS_COUNTS,
        "orbit_size_counts": EXPECTED_ORBIT_SIZE_COUNTS,
        "canonical_rep_mismatches": 0,
        "orbit_size_mismatches": 0,
        "orbit_overlap_count": 0,
        "classification_missing_from_orbits": 0,
        "orbit_missing_from_classification": 0,
        "classification_family_mismatches": 0,
        "classification_status_mismatches": 0,
        "canonical_label_map_mismatches": 0,
        "assignment_id_mismatches": 0,
        "orbit_union_rows_sha256": EXPECTED_ROWS_SHA256,
        "classification_rows_sha256": EXPECTED_ROWS_SHA256,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(f"{key} mismatch: {summary.get(key)!r} != {value!r}")


def _audit_orbits(
    motif: Mapping[str, Any],
    classification: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    families = _motif_family_rows(motif)
    assignments = _classification_assignment_rows(classification)
    orbit_map: dict[Rows, dict[str, str]] = {}
    family_status_counts: Counter[str] = Counter()
    orbit_size_counts: Counter[int] = Counter()
    orbit_status_counts: Counter[str] = Counter()
    canonical_rep_mismatches = 0
    orbit_size_mismatches = 0
    orbit_overlap_count = 0
    example_mismatches: list[dict[str, Any]] = []

    for expected_index, family in enumerate(families, start=1):
        family_id = str(family.get("family_id"))
        if family_id != f"F{expected_index:02d}":
            _record_error(errors, example_mismatches, "family_id", family_id)
        status = str(family.get("status"))
        family_status_counts[status] += 1
        rows = _rows_from_indexed_rows(family.get("representative_selected_rows"))
        orbit = {_transform_rows(rows, label_map) for label_map in _dihedral_maps()}
        canonical_rows = min(orbit)
        if rows != canonical_rows:
            canonical_rep_mismatches += 1
            _record_error(errors, example_mismatches, "canonical_rep", family_id)
        stored_orbit_size = int(family.get("orbit_size", -1))
        if stored_orbit_size != len(orbit):
            orbit_size_mismatches += 1
            _record_error(errors, example_mismatches, "orbit_size", family_id)
        orbit_size_counts[len(orbit)] += 1
        orbit_status_counts.update({status: len(orbit)})
        status_counts = family.get("status_counts")
        if status_counts != {status: len(orbit)}:
            _record_error(errors, example_mismatches, "family_status_counts", family_id)
        for member_rows in orbit:
            if member_rows in orbit_map:
                orbit_overlap_count += 1
                _record_error(errors, example_mismatches, "orbit_overlap", family_id)
            orbit_map[member_rows] = {"family_id": family_id, "status": status}

    classification_rows: list[Rows] = []
    classification_status_counts: Counter[str] = Counter()
    classification_family_mismatches = 0
    classification_status_mismatches = 0
    canonical_label_map_mismatches = 0
    assignment_id_mismatches = 0

    for expected_index, assignment in enumerate(assignments, start=1):
        assignment_id = str(assignment.get("assignment_id"))
        if assignment_id != f"A{expected_index:03d}":
            assignment_id_mismatches += 1
            _record_error(errors, example_mismatches, "assignment_id", assignment_id)
        rows = _rows_from_compact_rows(assignment.get("selected_rows"))
        classification_rows.append(rows)
        status = str(assignment.get("status"))
        classification_status_counts[status] += 1
        orbit_record = orbit_map.get(rows)
        if orbit_record is None:
            continue
        family_id = str(assignment.get("family_id"))
        if family_id != orbit_record["family_id"]:
            classification_family_mismatches += 1
            _record_error(errors, example_mismatches, "assignment_family", assignment_id)
        if status != orbit_record["status"]:
            classification_status_mismatches += 1
            _record_error(errors, example_mismatches, "assignment_status", assignment_id)
        if not _canonical_label_map_matches(rows, assignment, families):
            canonical_label_map_mismatches += 1
            _record_error(errors, example_mismatches, "canonical_label_map", assignment_id)

    classification_set = set(classification_rows)
    orbit_set = set(orbit_map)
    missing_from_orbits = classification_set - orbit_set
    missing_from_classification = orbit_set - classification_set
    duplicate_classification_rows = len(classification_rows) - len(classification_set)

    _check_equal(errors, "canonical_rep_mismatches", canonical_rep_mismatches, 0)
    _check_equal(errors, "orbit_size_mismatches", orbit_size_mismatches, 0)
    _check_equal(errors, "orbit_overlap_count", orbit_overlap_count, 0)
    _check_equal(errors, "classification_missing_from_orbits", len(missing_from_orbits), 0)
    _check_equal(
        errors,
        "orbit_missing_from_classification",
        len(missing_from_classification),
        0,
    )
    _check_equal(errors, "classification_duplicate_rows", duplicate_classification_rows, 0)
    _check_equal(
        errors,
        "classification_family_mismatches",
        classification_family_mismatches,
        0,
    )
    _check_equal(
        errors,
        "classification_status_mismatches",
        classification_status_mismatches,
        0,
    )
    _check_equal(
        errors,
        "canonical_label_map_mismatches",
        canonical_label_map_mismatches,
        0,
    )
    _check_equal(errors, "assignment_id_mismatches", assignment_id_mismatches, 0)
    _check_equal(errors, "family_count", len(families), EXPECTED_FAMILY_COUNT)
    _check_equal(
        errors,
        "classification_assignment_count",
        len(assignments),
        EXPECTED_ASSIGNMENT_COUNT,
    )
    _check_equal(
        errors,
        "orbit_union_row_count",
        len(orbit_map),
        EXPECTED_ASSIGNMENT_COUNT,
    )
    _check_equal(
        errors,
        "orbit_union_status_counts",
        dict(sorted(orbit_status_counts.items())),
        EXPECTED_STATUS_COUNTS,
    )
    _check_equal(
        errors,
        "classification_status_counts",
        dict(sorted(classification_status_counts.items())),
        EXPECTED_STATUS_COUNTS,
    )
    _check_equal(
        errors,
        "family_status_counts",
        dict(sorted(family_status_counts.items())),
        EXPECTED_FAMILY_STATUS_COUNTS,
    )
    _check_equal(
        errors,
        "orbit_size_counts",
        {str(size): int(orbit_size_counts[size]) for size in sorted(orbit_size_counts)},
        EXPECTED_ORBIT_SIZE_COUNTS,
    )

    return {
        "family_count": len(families),
        "classification_assignment_count": len(assignments),
        "unique_classification_row_count": len(classification_set),
        "orbit_union_row_count": len(orbit_map),
        "orbit_union_status_counts": dict(sorted(orbit_status_counts.items())),
        "classification_status_counts": dict(sorted(classification_status_counts.items())),
        "family_status_counts": dict(sorted(family_status_counts.items())),
        "orbit_size_counts": {
            str(size): int(orbit_size_counts[size])
            for size in sorted(orbit_size_counts)
        },
        "canonical_rep_mismatches": canonical_rep_mismatches,
        "orbit_size_mismatches": orbit_size_mismatches,
        "orbit_overlap_count": orbit_overlap_count,
        "classification_missing_from_orbits": len(missing_from_orbits),
        "orbit_missing_from_classification": len(missing_from_classification),
        "classification_duplicate_rows": duplicate_classification_rows,
        "classification_family_mismatches": classification_family_mismatches,
        "classification_status_mismatches": classification_status_mismatches,
        "canonical_label_map_mismatches": canonical_label_map_mismatches,
        "assignment_id_mismatches": assignment_id_mismatches,
        "orbit_union_rows_sha256": _rows_digest(sorted(orbit_set)),
        "classification_rows_sha256": _rows_digest(sorted(classification_set)),
        "example_mismatches": example_mismatches[:5],
    }


def _motif_family_rows(motif: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    families = motif.get("dihedral_incidence_families", {}).get("families")
    if not isinstance(families, list):
        raise ValueError("motif artifact must contain dihedral incidence families")
    return [_as_mapping(row, "family") for row in families]


def _classification_assignment_rows(classification: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    assignments = classification.get("assignments")
    if not isinstance(assignments, list):
        raise ValueError("classification artifact must contain assignments")
    return [_as_mapping(row, "assignment") for row in assignments]


def _as_mapping(row: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(row, Mapping):
        raise ValueError(f"{label} row must be an object")
    return row


def _dihedral_maps() -> tuple[LabelMap, ...]:
    return tuple(
        tuple((direction * label + shift) % N for label in range(N))
        for direction in (1, -1)
        for shift in range(N)
    )


def _transform_rows(rows: Rows, label_map: Sequence[int]) -> Rows:
    transformed: list[tuple[int, ...] | None] = [None] * N
    for center, witnesses in enumerate(rows):
        mapped_center = int(label_map[center])
        transformed[mapped_center] = tuple(
            sorted(int(label_map[witness]) for witness in witnesses)
        )
    if any(row is None for row in transformed):  # pragma: no cover - defensive
        raise ValueError("label map did not produce complete rows")
    return tuple(row for row in transformed if row is not None)


def _rows_from_indexed_rows(raw_rows: Any) -> Rows:
    if not isinstance(raw_rows, list) or len(raw_rows) != N:
        raise ValueError("indexed selected rows must be a list of 9 rows")
    rows = [_witness_tuple(center, row) for center, row in enumerate(raw_rows)]
    return tuple(rows)


def _rows_from_compact_rows(raw_rows: Any) -> Rows:
    if not isinstance(raw_rows, list):
        raise ValueError("compact selected rows must be a list")
    indexed: list[tuple[int, ...] | None] = [None] * N
    for raw_row in raw_rows:
        if not isinstance(raw_row, list) or len(raw_row) != ROW_SIZE + 1:
            raise ValueError(f"bad compact row: {raw_row!r}")
        center = int(raw_row[0])
        if not 0 <= center < N:
            raise ValueError(f"bad row center: {center!r}")
        if indexed[center] is not None:
            raise ValueError(f"duplicate row center: {center!r}")
        indexed[center] = _witness_tuple(center, raw_row[1:])
    if any(row is None for row in indexed):
        raise ValueError("compact rows must cover all 9 centers")
    return tuple(row for row in indexed if row is not None)


def _witness_tuple(center: int, raw_witnesses: Sequence[Any]) -> tuple[int, ...]:
    witnesses = tuple(sorted(int(witness) for witness in raw_witnesses))
    if len(witnesses) != ROW_SIZE:
        raise ValueError(f"row {center} must contain {ROW_SIZE} witnesses")
    if len(set(witnesses)) != ROW_SIZE:
        raise ValueError(f"row {center} has duplicate witnesses")
    if center in witnesses:
        raise ValueError(f"row {center} selects itself")
    if any(witness < 0 or witness >= N for witness in witnesses):
        raise ValueError(f"row {center} has witness outside 0..{N - 1}")
    return witnesses


def _canonical_label_map_matches(
    rows: Rows,
    assignment: Mapping[str, Any],
    families: Sequence[Mapping[str, Any]],
) -> bool:
    raw_map = assignment.get("to_canonical_label_map")
    if not isinstance(raw_map, list) or len(raw_map) != N:
        return False
    label_map = tuple(int(label) for label in raw_map)
    if sorted(label_map) != list(range(N)):
        return False
    family_index = int(str(assignment.get("family_id", "F00"))[1:]) - 1
    if not 0 <= family_index < len(families):
        return False
    canonical_rows = _rows_from_indexed_rows(
        families[family_index].get("representative_selected_rows")
    )
    if _transform_rows(rows, label_map) != canonical_rows:
        return False
    candidate_maps = [
        current_map
        for current_map in _dihedral_maps()
        if _transform_rows(rows, current_map) == canonical_rows
    ]
    return bool(candidate_maps) and label_map == min(candidate_maps)


def _rows_digest(rows_list: Sequence[Rows]) -> str:
    payload = [[list(row) for row in rows] for rows in rows_list]
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _record_error(
    errors: list[str],
    examples: list[dict[str, Any]],
    kind: str,
    identifier: str,
) -> None:
    errors.append(f"{kind} mismatch at {identifier}")
    if len(examples) < 5:
        examples.append({"kind": kind, "id": identifier})


def _check_equal(errors: list[str], name: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{name} mismatch: {actual!r} != {expected!r}")


def summary_json_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing JSON view without mismatch examples."""

    summary = {key: payload[key] for key in SUMMARY_JSON_KEYS if key in payload}
    audit = payload.get("dihedral_orbit_audit")
    if isinstance(audit, Mapping):
        summary["dihedral_orbit_audit_summary"] = {
            key: audit[key] for key in DIHEDRAL_ORBIT_SUMMARY_KEYS if key in audit
        }
    return summary


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    summary = payload["dihedral_orbit_audit"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"families: {summary['family_count']}",
        f"orbit rows: {summary['orbit_union_row_count']}",
        f"classification rows: {summary['classification_assignment_count']}",
        f"canonical mismatches: {summary['canonical_rep_mismatches']}",
        f"label-map mismatches: {summary['canonical_label_map_mismatches']}",
    ]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--motif-families", type=Path, default=DEFAULT_MOTIF_FAMILIES)
    parser.add_argument(
        "--frontier-classification",
        type=Path,
        default=DEFAULT_FRONTIER_CLASSIFICATION,
    )
    parser.add_argument("--check", action="store_true", help="validate the audit")
    parser.add_argument("--assert-expected", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="emit JSON payload")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="emit compact reviewer-facing JSON without mismatch examples",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = dihedral_orbit_audit_payload(
            motif_path=_resolve(args.motif_families),
            classification_path=_resolve(args.frontier_classification),
        )
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        payload = {
            "schema": SCHEMA,
            "status": STATUS,
            "trust": TRUST,
            "claim_scope": CLAIM_SCOPE,
            "validation_status": "failed",
            "validation_errors": [str(exc)],
            "provenance": dict(PROVENANCE),
        }

    if args.assert_expected:
        assert_expected_dihedral_orbit_audit(payload)

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle dihedral orbit audit")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=9 dihedral orbit audit checks passed")
    else:
        print("FAILED: n=9 dihedral orbit audit", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
