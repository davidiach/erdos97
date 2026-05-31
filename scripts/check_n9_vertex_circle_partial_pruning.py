#!/usr/bin/env python3
"""Replay n=9 vertex-circle partial-pruning monotonicity diagnostics."""

from __future__ import annotations

import argparse
import itertools
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
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    parse_selected_rows,
    replay_vertex_circle_quotient,
)

DEFAULT_FRONTIER_CLASSIFICATION = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)

SCHEMA = "erdos97.n9_vertex_circle_partial_pruning.v1"
STATUS = "REVIEW_PENDING_PARTIAL_PRUNING_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Partial-pruning audit for the review-pending n=9 vertex-circle checker. "
    "It checks stored frontier assignment subsets for monotone obstruction "
    "persistence and checker/replay status agreement. It does not prove "
    "frontier coverage, brancher soundness, strict-edge geometry, "
    "selected-distance quotient soundness, n=9, a counterexample, or any "
    "official/global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_partial_pruning.py",
    "command": (
        "python scripts/check_n9_vertex_circle_partial_pruning.py "
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
FRONTIER_SUBSET_SUMMARY_KEYS = (
    "assignment_count",
    "full_status_counts",
    "subset_count",
    "subset_status_counts",
    "obstructed_subset_count",
    "extension_violations",
    "checker_replay_status_mismatches",
    "min_obstruction_size_counts",
    "stored_row_order_prefix_total",
    "stored_row_order_prefix_status_counts",
)

EXPECTED_ASSIGNMENT_COUNT = 184
EXPECTED_SUBSET_COUNT = 94_024
EXPECTED_SUBSET_STATUS_COUNTS = {
    "ok": 35_418,
    "self_edge": 24_890,
    "strict_cycle": 33_716,
}
EXPECTED_OBSTRUCTED_SUBSETS = 58_606
EXPECTED_MIN_OBSTRUCTION_SIZE_COUNTS = {3: 182, 4: 2}
EXPECTED_PREFIX_TOTAL = 1_656
EXPECTED_PREFIX_STATUS_COUNTS = {
    "ok": 570,
    "self_edge": 758,
    "strict_cycle": 328,
}


def load_json(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def partial_pruning_payload(
    *,
    frontier_path: Path = DEFAULT_FRONTIER_CLASSIFICATION,
) -> dict[str, Any]:
    """Return a stored-frontier partial-pruning replay audit."""

    frontier = load_json(frontier_path)
    errors: list[str] = []
    summary = _audit_frontier_subsets(frontier)
    _check_equal(errors, "assignment count", summary["assignment_count"], EXPECTED_ASSIGNMENT_COUNT)
    _check_equal(errors, "subset count", summary["subset_count"], EXPECTED_SUBSET_COUNT)
    _check_equal(
        errors,
        "subset status counts",
        summary["subset_status_counts"],
        EXPECTED_SUBSET_STATUS_COUNTS,
    )
    _check_equal(
        errors,
        "obstructed subset count",
        summary["obstructed_subset_count"],
        EXPECTED_OBSTRUCTED_SUBSETS,
    )
    _check_equal(
        errors,
        "min obstruction size counts",
        summary["min_obstruction_size_counts"],
        EXPECTED_MIN_OBSTRUCTION_SIZE_COUNTS,
    )
    _check_equal(errors, "prefix total", summary["stored_row_order_prefix_total"], EXPECTED_PREFIX_TOTAL)
    _check_equal(
        errors,
        "prefix status counts",
        summary["stored_row_order_prefix_status_counts"],
        EXPECTED_PREFIX_STATUS_COUNTS,
    )
    _check_equal(errors, "extension violations", summary["extension_violations"], 0)
    _check_equal(errors, "checker/replay status mismatches", summary["checker_replay_status_mismatches"], 0)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "frontier_subset_audit": summary,
        "source_artifact": _source_metadata(frontier_path, frontier),
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says every obstructed nonempty row subset of the "
            "stored 184 n=9 pre-vertex-circle frontier assignments extends to "
            "a stored full assignment that remains vertex-circle obstructed, "
            "and the checker status agrees with the reusable quotient replay "
            "on every such subset. This is a stored-frontier diagnostic only."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_partial_pruning(payload: Mapping[str, Any]) -> None:
    """Assert the expected partial-pruning audit result."""

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
        "brancher soundness",
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
    summary = payload.get("frontier_subset_audit")
    if not isinstance(summary, Mapping):
        raise AssertionError("frontier_subset_audit missing")
    expected = {
        "assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "subset_count": EXPECTED_SUBSET_COUNT,
        "subset_status_counts": EXPECTED_SUBSET_STATUS_COUNTS,
        "obstructed_subset_count": EXPECTED_OBSTRUCTED_SUBSETS,
        "min_obstruction_size_counts": EXPECTED_MIN_OBSTRUCTION_SIZE_COUNTS,
        "stored_row_order_prefix_total": EXPECTED_PREFIX_TOTAL,
        "stored_row_order_prefix_status_counts": EXPECTED_PREFIX_STATUS_COUNTS,
        "extension_violations": 0,
        "checker_replay_status_mismatches": 0,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(f"{key} mismatch: {summary.get(key)!r} != {value!r}")


def summary_json_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing JSON view without mismatch examples."""

    summary = {key: payload[key] for key in SUMMARY_JSON_KEYS if key in payload}
    subset_audit = payload.get("frontier_subset_audit")
    if isinstance(subset_audit, Mapping):
        summary["frontier_subset_audit_summary"] = {
            key: subset_audit[key]
            for key in FRONTIER_SUBSET_SUMMARY_KEYS
            if key in subset_audit
        }
    return summary


def _audit_frontier_subsets(frontier: Mapping[str, Any]) -> dict[str, Any]:
    assignments = frontier.get("assignments")
    if not isinstance(assignments, list):
        raise ValueError("frontier classification artifact must contain assignments")

    subset_status_counts: Counter[str] = Counter()
    full_status_counts: Counter[str] = Counter()
    min_obstruction_size_counts: Counter[int] = Counter()
    prefix_status_counts: Counter[str] = Counter()
    subset_count = 0
    obstructed_subset_count = 0
    extension_violations = 0
    checker_replay_status_mismatches = 0
    example_mismatches: list[dict[str, Any]] = []

    for assignment in assignments:
        if not isinstance(assignment, Mapping):
            raise ValueError("assignment rows must be objects")
        assignment_id = str(assignment["assignment_id"])
        rows = assignment["selected_rows"]
        if not isinstance(rows, list):
            raise ValueError(f"{assignment_id} selected_rows must be a list")
        full_status = _checker_status(rows)
        full_status_counts[full_status] += 1
        min_obstruction_size: int | None = None

        for size in range(1, len(rows) + 1):
            for indices in itertools.combinations(range(len(rows)), size):
                subset = [rows[index] for index in indices]
                subset_count += 1
                checker_status = _checker_status(subset)
                replay_status = _replay_status(subset)
                subset_status_counts[checker_status] += 1
                if checker_status != replay_status:
                    checker_replay_status_mismatches += 1
                    if len(example_mismatches) < 5:
                        example_mismatches.append(
                            {
                                "assignment_id": assignment_id,
                                "indices": list(indices),
                                "checker_status": checker_status,
                                "replay_status": replay_status,
                            }
                        )
                if checker_status != "ok":
                    obstructed_subset_count += 1
                    if full_status == "ok":
                        extension_violations += 1
                    if min_obstruction_size is None:
                        min_obstruction_size = size

        if min_obstruction_size is not None:
            min_obstruction_size_counts[min_obstruction_size] += 1

        for prefix_size in range(1, len(rows) + 1):
            prefix = rows[:prefix_size]
            prefix_status_counts[_checker_status(prefix)] += 1

    return {
        "assignment_count": len(assignments),
        "full_status_counts": dict(sorted(full_status_counts.items())),
        "subset_count": subset_count,
        "subset_status_counts": dict(sorted(subset_status_counts.items())),
        "obstructed_subset_count": obstructed_subset_count,
        "extension_violations": extension_violations,
        "checker_replay_status_mismatches": checker_replay_status_mismatches,
        "example_mismatches": example_mismatches,
        "min_obstruction_size_counts": dict(sorted(min_obstruction_size_counts.items())),
        "stored_row_order_prefix_total": sum(prefix_status_counts.values()),
        "stored_row_order_prefix_status_counts": dict(sorted(prefix_status_counts.items())),
    }


def _checker_status(rows: Sequence[Sequence[int]]) -> str:
    return n9.vertex_circle_status(_assignment_from_compact_rows(rows))


def _replay_status(rows: Sequence[Sequence[int]]) -> str:
    return replay_vertex_circle_quotient(
        n9.N,
        n9.ORDER,
        parse_selected_rows(rows),
    ).status


def _assignment_from_compact_rows(rows: Sequence[Sequence[int]]) -> dict[int, int]:
    return {
        int(row[0]): n9.mask([int(witness) for witness in row[1:]])
        for row in rows
    }


def _source_metadata(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
    }


def _check_equal(errors: list[str], name: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{name} mismatch: {actual!r} != {expected!r}")


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    summary = payload["frontier_subset_audit"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"assignments checked: {summary['assignment_count']}",
        f"subsets checked: {summary['subset_count']}",
        f"extension violations: {summary['extension_violations']}",
        "checker/replay mismatches: "
        f"{summary['checker_replay_status_mismatches']}",
    ]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
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
    frontier_path = (
        args.frontier_classification
        if args.frontier_classification.is_absolute()
        else ROOT / args.frontier_classification
    )
    payload = partial_pruning_payload(frontier_path=frontier_path)

    if args.assert_expected:
        assert_expected_partial_pruning(payload)

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle partial-pruning audit")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=9 partial-pruning audit checks passed")
    else:
        print("FAILED: n=9 partial-pruning audit", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
