#!/usr/bin/env python3
"""Crosswalk dynamic n=9 frontier generation against the stored artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97 import n9_vertex_circle_exhaustive as n9  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_FRONTIER_CLASSIFICATION = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)

SCHEMA = "erdos97.n9_vertex_circle_frontier_coverage_crosswalk.v1"
STATUS = "REVIEW_PENDING_FRONTIER_COVERAGE_CROSSWALK"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Dynamic no-vertex-circle frontier coverage crosswalk for the "
    "review-pending n=9 vertex-circle checker. It reruns the dynamic "
    "minimum-remaining-options brancher without vertex-circle pruning and "
    "compares the generated 184 complete selected-witness assignments, as "
    "ordered rows, against the stored frontier motif-classification artifact. "
    "It does not prove filter soundness, dynamic brancher soundness, "
    "strict-edge geometry, selected-distance quotient soundness, n=9, a "
    "counterexample, or any official/global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py",
    "command": (
        "python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py "
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
    "source_artifact",
    "validation_status",
    "validation_errors",
    "interpretation",
    "provenance",
)
FRONTIER_COVERAGE_SUMMARY_KEYS = (
    "row_order_rule",
    "vertex_circle_pruning",
    "nodes_visited",
    "generated_assignment_count",
    "stored_assignment_count",
    "generated_unique_assignment_count",
    "stored_unique_assignment_count",
    "generated_status_counts",
    "stored_status_counts",
    "sequence_matches",
    "set_matches",
    "status_mismatches",
    "missing_from_stored_count",
    "extra_in_stored_count",
    "generated_sorted_rows_sha256",
    "stored_sorted_rows_sha256",
    "generated_sequence_rows_sha256",
    "stored_sequence_rows_sha256",
)

EXPECTED_NODES_VISITED = 100_817
EXPECTED_ASSIGNMENT_COUNT = 184
EXPECTED_STATUS_COUNTS = {"self_edge": 158, "strict_cycle": 26}
EXPECTED_SORTED_ROWS_SHA256 = "dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55"
EXPECTED_SEQUENCE_ROWS_SHA256 = "d7807b69b9de27da17fa851b3325b1e26cfa0b6d86277abeda4bc4e3454b8e01"

Rows = tuple[tuple[int, ...], ...]


def load_json(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def frontier_coverage_crosswalk_payload(
    *,
    frontier_path: Path = DEFAULT_FRONTIER_CLASSIFICATION,
) -> dict[str, Any]:
    """Return the generated-vs-stored n=9 frontier coverage crosswalk."""

    errors: list[str] = []
    frontier = load_json(frontier_path)
    stored = _stored_frontier_rows(frontier)
    generated = _dynamic_no_vertex_frontier()
    summary = _crosswalk_summary(generated, stored)
    _audit_summary(summary, errors)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "frontier_coverage_crosswalk": summary,
        "source_artifact": {
            "path": display_path(frontier_path, ROOT),
            "type": frontier.get("type"),
            "trust": frontier.get("trust"),
        },
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed crosswalk says the dynamic no-vertex-circle brancher "
            "regenerates exactly the same complete selected-row sequence and "
            "the same vertex-circle status labels as the stored n=9 frontier "
            "motif-classification artifact. This is a coverage crosswalk "
            "against the current brancher, not a proof of the pruning rules."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_frontier_coverage_crosswalk(payload: Mapping[str, Any]) -> None:
    """Assert the expected generated-vs-stored frontier crosswalk."""

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
        "does not prove filter soundness",
        "dynamic brancher soundness",
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
    summary = payload.get("frontier_coverage_crosswalk")
    if not isinstance(summary, Mapping):
        raise AssertionError("frontier_coverage_crosswalk missing")
    expected = {
        "row_order_rule": "dynamic_minimum_remaining_options",
        "vertex_circle_pruning": False,
        "nodes_visited": EXPECTED_NODES_VISITED,
        "generated_assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "stored_assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "generated_unique_assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "stored_unique_assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "generated_status_counts": EXPECTED_STATUS_COUNTS,
        "stored_status_counts": EXPECTED_STATUS_COUNTS,
        "sequence_matches": True,
        "set_matches": True,
        "status_mismatches": 0,
        "missing_from_stored_count": 0,
        "extra_in_stored_count": 0,
        "generated_sorted_rows_sha256": EXPECTED_SORTED_ROWS_SHA256,
        "stored_sorted_rows_sha256": EXPECTED_SORTED_ROWS_SHA256,
        "generated_sequence_rows_sha256": EXPECTED_SEQUENCE_ROWS_SHA256,
        "stored_sequence_rows_sha256": EXPECTED_SEQUENCE_ROWS_SHA256,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(f"{key} mismatch: {summary.get(key)!r} != {value!r}")


def _dynamic_no_vertex_frontier() -> dict[str, Any]:
    nodes_visited = 0
    assignments: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()

    def search(
        assignment: n9.Assignment,
        selected_indegrees: list[int],
        witness_pair_counts: list[int],
    ) -> None:
        nonlocal nodes_visited

        nodes_visited += 1
        if len(assignment) == n9.N:
            rows = _rows_from_assignment(assignment)
            status = n9.vertex_circle_status(assignment)
            status_counts[status] += 1
            assignments.append({"rows": rows, "status": status})
            return

        best_center = None
        best_options = None
        for center in range(n9.N):
            if center in assignment:
                continue
            options = n9.valid_options_for_center(
                center,
                assignment,
                selected_indegrees,
                witness_pair_counts,
            )
            if best_options is None or len(options) < len(best_options):
                best_center = center
                best_options = options
                if not options:
                    break
        if not best_options:
            return

        center = best_center
        assert center is not None
        for row_mask in best_options:
            assignment[center] = row_mask
            for target in n9.MASK_BITS[row_mask]:
                selected_indegrees[target] += 1
            for pair_index in n9.ROW_PAIR_INDICES[row_mask]:
                witness_pair_counts[pair_index] += 1

            search(assignment, selected_indegrees, witness_pair_counts)

            for pair_index in n9.ROW_PAIR_INDICES[row_mask]:
                witness_pair_counts[pair_index] -= 1
            for target in n9.MASK_BITS[row_mask]:
                selected_indegrees[target] -= 1
            del assignment[center]

    for row0 in n9.OPTIONS[0]:
        assignment = {0: row0}
        selected_indegrees = [0] * n9.N
        witness_pair_counts = [0] * len(n9.PAIRS)
        for target in n9.MASK_BITS[row0]:
            selected_indegrees[target] += 1
        for pair_index in n9.ROW_PAIR_INDICES[row0]:
            witness_pair_counts[pair_index] += 1
        if n9.vertex_circle_status(assignment) == "ok":
            search(assignment, selected_indegrees, witness_pair_counts)

    return {
        "nodes_visited": nodes_visited,
        "assignments": assignments,
        "status_counts": dict(sorted(status_counts.items())),
    }


def _stored_frontier_rows(frontier: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw_assignments = frontier.get("assignments")
    if not isinstance(raw_assignments, list):
        raise ValueError("frontier classification artifact must contain assignments")
    stored: list[dict[str, Any]] = []
    for index, assignment in enumerate(raw_assignments, start=1):
        if not isinstance(assignment, Mapping):
            raise ValueError(f"stored assignment {index} is not an object")
        stored.append(
            {
                "assignment_id": str(assignment.get("assignment_id", f"A{index:03d}")),
                "rows": _rows_from_compact_selected_rows(assignment.get("selected_rows")),
                "status": str(assignment.get("status")),
            }
        )
    return stored


def _crosswalk_summary(
    generated: Mapping[str, Any],
    stored: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    generated_records = list(generated["assignments"])
    generated_rows = [record["rows"] for record in generated_records]
    stored_rows = [record["rows"] for record in stored]
    generated_status_by_rows = {record["rows"]: str(record["status"]) for record in generated_records}
    stored_status_by_rows = {record["rows"]: str(record["status"]) for record in stored}
    generated_set = set(generated_rows)
    stored_set = set(stored_rows)
    missing = sorted(generated_set - stored_set)
    extra = sorted(stored_set - generated_set)
    status_mismatches = [
        rows
        for rows in sorted(generated_set & stored_set)
        if generated_status_by_rows[rows] != stored_status_by_rows[rows]
    ]
    stored_status_counts = Counter(str(record["status"]) for record in stored)

    return {
        "row_order_rule": "dynamic_minimum_remaining_options",
        "vertex_circle_pruning": False,
        "nodes_visited": int(generated["nodes_visited"]),
        "generated_assignment_count": len(generated_records),
        "stored_assignment_count": len(stored),
        "generated_unique_assignment_count": len(generated_set),
        "stored_unique_assignment_count": len(stored_set),
        "generated_status_counts": dict(generated["status_counts"]),
        "stored_status_counts": dict(sorted(stored_status_counts.items())),
        "sequence_matches": generated_rows == stored_rows,
        "set_matches": generated_set == stored_set,
        "status_mismatches": len(status_mismatches),
        "missing_from_stored_count": len(missing),
        "extra_in_stored_count": len(extra),
        "generated_sorted_rows_sha256": _rows_digest(sorted(generated_rows)),
        "stored_sorted_rows_sha256": _rows_digest(sorted(stored_rows)),
        "generated_sequence_rows_sha256": _rows_digest(generated_rows),
        "stored_sequence_rows_sha256": _rows_digest(stored_rows),
        "example_mismatches": _example_mismatches(missing, extra, status_mismatches),
    }


def _rows_from_assignment(assignment: n9.Assignment) -> Rows:
    return tuple(tuple(n9.MASK_BITS[assignment[center]]) for center in range(n9.N))


def _rows_from_compact_selected_rows(raw_rows: Any) -> Rows:
    if not isinstance(raw_rows, list):
        raise ValueError("selected_rows must be a list")
    rows: list[tuple[int, ...] | None] = [None] * n9.N
    for raw_row in raw_rows:
        if not isinstance(raw_row, list) or len(raw_row) != n9.ROW_SIZE + 1:
            raise ValueError(f"bad selected row: {raw_row!r}")
        center = int(raw_row[0])
        if not 0 <= center < n9.N:
            raise ValueError(f"bad row center: {center!r}")
        witnesses = tuple(int(label) for label in raw_row[1:])
        if len(set(witnesses)) != n9.ROW_SIZE or center in witnesses:
            raise ValueError(f"bad witness row for center {center}: {witnesses!r}")
        rows[center] = witnesses
    if any(row is None for row in rows):
        raise ValueError("stored assignment does not cover every center")
    return tuple(row for row in rows if row is not None)


def _rows_digest(rows_list: Sequence[Rows]) -> str:
    payload = [[list(row) for row in rows] for rows in rows_list]
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _example_mismatches(
    missing: Sequence[Rows],
    extra: Sequence[Rows],
    status_mismatches: Sequence[Rows],
) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for kind, rows_list in (
        ("missing_from_stored", missing),
        ("extra_in_stored", extra),
        ("status_mismatch", status_mismatches),
    ):
        for rows in rows_list[:2]:
            examples.append({"kind": kind, "rows": [[int(label) for label in row] for row in rows]})
    return examples[:5]


def _audit_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "nodes_visited": EXPECTED_NODES_VISITED,
        "generated_assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "stored_assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "generated_unique_assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "stored_unique_assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "generated_status_counts": EXPECTED_STATUS_COUNTS,
        "stored_status_counts": EXPECTED_STATUS_COUNTS,
        "sequence_matches": True,
        "set_matches": True,
        "status_mismatches": 0,
        "missing_from_stored_count": 0,
        "extra_in_stored_count": 0,
        "generated_sorted_rows_sha256": EXPECTED_SORTED_ROWS_SHA256,
        "stored_sorted_rows_sha256": EXPECTED_SORTED_ROWS_SHA256,
        "generated_sequence_rows_sha256": EXPECTED_SEQUENCE_ROWS_SHA256,
        "stored_sequence_rows_sha256": EXPECTED_SEQUENCE_ROWS_SHA256,
    }
    for key, value in expected.items():
        _check_equal(errors, key, summary.get(key), value)
    _check_equal(errors, "example_mismatches", summary.get("example_mismatches"), [])


def _check_equal(errors: list[str], name: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{name} mismatch: {actual!r} != {expected!r}")


def summary_json_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing JSON view."""

    summary = {key: payload[key] for key in SUMMARY_JSON_KEYS if key in payload}
    crosswalk = payload.get("frontier_coverage_crosswalk")
    if isinstance(crosswalk, Mapping):
        summary["frontier_coverage_crosswalk_summary"] = {
            key: crosswalk[key]
            for key in FRONTIER_COVERAGE_SUMMARY_KEYS
            if key in crosswalk
        }
    return summary


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    summary = payload["frontier_coverage_crosswalk"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"nodes visited: {summary['nodes_visited']}",
        f"generated assignments: {summary['generated_assignment_count']}",
        f"stored assignments: {summary['stored_assignment_count']}",
        f"sequence matches: {summary['sequence_matches']}",
        f"status mismatches: {summary['status_mismatches']}",
    ]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier-classification", type=Path, default=DEFAULT_FRONTIER_CLASSIFICATION)
    parser.add_argument("--check", action="store_true", help="validate the crosswalk")
    parser.add_argument("--assert-expected", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="emit JSON payload")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="emit compact reviewer-facing JSON summary",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = frontier_coverage_crosswalk_payload(
            frontier_path=_resolve(args.frontier_classification)
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
        assert_expected_frontier_coverage_crosswalk(payload)

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle frontier coverage crosswalk")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=9 frontier coverage crosswalk checks passed")
    else:
        print("FAILED: n=9 frontier coverage crosswalk", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
