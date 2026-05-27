#!/usr/bin/env python3
"""Cross-check the bounded n=10 row0 turn + vertex-circle closure.

This checker joins two existing finite-bookkeeping artifacts:

* data/certificates/n10_turn_row0_pilot.json
* data/certificates/n10_turn_row0_escape_self_edges.json

It verifies that the turn Farkas certificates kill exactly 156 of the 160
row0-index-0 assignments, that the remaining four weak-turn SAT assignments
are exactly the four row0-local vertex-circle self-edge escape records, and
that the union covers the bounded row0-index-0 slice.

It does not prove n=10, does not complete the n=10 singleton-slice draft, does
not claim a counterexample, and does not update the global Erdos #97 status.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PILOT = ROOT / "data" / "certificates" / "n10_turn_row0_pilot.json"
DEFAULT_ESCAPES = (
    ROOT / "data" / "certificates" / "n10_turn_row0_escape_self_edges.json"
)
DEFAULT_OUT = ROOT / "data" / "certificates" / "n10_turn_row0_combined_closure.json"

SCHEMA = "erdos97.n10_turn_row0_combined_closure.v1"
STATUS = "N10_ROW0_TURN_PLUS_VERTEX_CIRCLE_CLOSURE_DIAGNOSTIC"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
CLAIM_SCOPE = (
    "Crosswalk for the bounded n=10 row0-index-0 pilot: 156 assignments are "
    "closed by stored weak-turn Farkas certificates and the four weak-turn SAT "
    "escapes are closed by stored row0-local vertex-circle self-edge templates. "
    "This is finite bookkeeping only: not a proof of n=10, not a complete n=10 "
    "search, not a counterexample, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n10_turn_row0_combined_closure.py",
    "command": (
        "python scripts/check_n10_turn_row0_combined_closure.py "
        "--write --assert-expected"
    ),
    "sources": [
        "data/certificates/n10_turn_row0_pilot.json",
        "data/certificates/n10_turn_row0_escape_self_edges.json",
    ],
}
FORBIDDEN_CLAIMS = [
    "n=10 is proved",
    "turn inequalities close n=10",
    "row0 pilot is a completeness result",
    "source-of-truth strongest result",
    "official/global status update",
    "counterexample to Erdos Problem #97",
    "general proof of Erdos Problem #97",
]
EXPECTED_COVERAGE = {
    "row0_index": 0,
    "full_assignment_count": 160,
    "turn_farkas_unsat_count": 156,
    "turn_sat_escape_count": 4,
    "turn_sat_escape_assignment_indices": [74, 103, 156, 157],
    "vertex_circle_escape_assignment_indices": [74, 103, 156, 157],
    "turn_and_escape_overlap_count": 0,
    "combined_closed_assignment_count": 160,
    "unclosed_assignment_count": 0,
    "turn_status_counts": {"farkas_unsat": 156, "sat": 4},
    "vertex_circle_status_counts": {"self_edge": 160},
    "escape_template_counts": {
        "[1, 3] > [1, 2]": 1,
        "[1, 3] > [2, 3]": 1,
        "[1, 4] > [1, 2]": 1,
        "[2, 4] > [2, 3]": 1,
    },
    "escape_path_length_histogram": {"3": 1, "4": 1, "5": 1, "7": 1},
    "common_escape_witness_order": [1, 2, 3, 4],
    "common_escape_equal_distance_class": [0, 1],
}
EXPECTED_PILOT = {
    "schema": "erdos97.n10_turn_row0_pilot.v1",
    "status": "EXPLORATORY_ROW0_TURN_FRONTIER_PILOT",
    "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
}
EXPECTED_ESCAPES = {
    "schema": "erdos97.n10_turn_row0_escape_self_edges.v1",
    "status": "N10_ROW0_ESCAPE_SELF_EDGE_TEMPLATE_DIAGNOSTIC",
    "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} did not contain a JSON object")
    return payload


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def _as_int(value: Any, name: str, errors: list[str]) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(f"{name} must be an integer, got {value!r}")
        return 0
    return value


def _check_equal(errors: list[str], name: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{name} mismatch: {actual!r} != {expected!r}")


def _source_summary(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": _display(path),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
    }


def _pilot_partition(pilot: Mapping[str, Any], errors: list[str]) -> dict[str, Any]:
    assignments = pilot.get("assignments")
    if not isinstance(assignments, list):
        errors.append("pilot assignments must be a list")
        assignments = []

    turn_counts: Counter[str] = Counter()
    vertex_counts: Counter[str] = Counter()
    farkas_indices: list[int] = []
    sat_indices: list[int] = []
    seen_indices: list[int] = []

    for offset, raw in enumerate(assignments, start=1):
        if not isinstance(raw, Mapping):
            errors.append(f"assignment {offset} must be an object")
            continue
        index = _as_int(raw.get("assignment_index_1based"), "assignment index", errors)
        seen_indices.append(index)
        if index != offset:
            errors.append(f"assignment index {index!r} is not contiguous at {offset}")

        rows = raw.get("rows")
        if not isinstance(rows, list) or len(rows) != 10:
            errors.append(f"assignment {index} rows must be a list of 10 rows")
        elif rows[0] != [1, 2, 3, 4]:
            errors.append(f"assignment {index} row0 is {rows[0]!r}, expected [1, 2, 3, 4]")

        turn_status = str(raw.get("turn_status"))
        vertex_status = str(raw.get("vertex_circle_status"))
        turn_counts[turn_status] += 1
        vertex_counts[vertex_status] += 1
        if turn_status == "farkas_unsat":
            farkas_indices.append(index)
            if "turn_certificate" not in raw:
                errors.append(f"assignment {index} missing turn_certificate")
        elif turn_status == "sat":
            sat_indices.append(index)
            if "turn_model" not in raw:
                errors.append(f"assignment {index} missing turn_model")
        else:
            errors.append(f"assignment {index} has unexpected turn_status {turn_status!r}")
        if vertex_status != "self_edge":
            errors.append(
                f"assignment {index} has unexpected vertex_circle_status {vertex_status!r}"
            )

    expected_indices = list(range(1, len(assignments) + 1))
    if seen_indices != expected_indices:
        errors.append("assignment indices are not the contiguous 1-based range")

    computed_turn_counts = dict(sorted(turn_counts.items()))
    computed_vertex_counts = dict(sorted(vertex_counts.items()))
    _check_equal(
        errors,
        "pilot full_assignment_count",
        pilot.get("full_assignment_count"),
        len(assignments),
    )
    _check_equal(
        errors,
        "pilot turn_farkas_certificate_count",
        pilot.get("turn_farkas_certificate_count"),
        len(farkas_indices),
    )
    _check_equal(
        errors,
        "pilot turn_sat_escape_count",
        pilot.get("turn_sat_escape_count"),
        len(sat_indices),
    )
    _check_equal(
        errors,
        "pilot turn_status_counts",
        pilot.get("turn_status_counts"),
        computed_turn_counts,
    )
    _check_equal(
        errors,
        "pilot vertex_circle_status_counts",
        pilot.get("vertex_circle_status_counts"),
        computed_vertex_counts,
    )

    return {
        "assignment_indices": seen_indices,
        "farkas_indices": farkas_indices,
        "sat_indices": sat_indices,
        "turn_status_counts": computed_turn_counts,
        "vertex_circle_status_counts": computed_vertex_counts,
    }


def _escape_partition(escapes: Mapping[str, Any], errors: list[str]) -> dict[str, Any]:
    records = escapes.get("escape_records")
    if not isinstance(records, list):
        errors.append("escape_records must be a list")
        records = []

    escape_indices: list[int] = []
    templates: Counter[str] = Counter()
    path_lengths: Counter[str] = Counter()
    witness_orders: set[tuple[int, ...]] = set()
    equal_classes: set[tuple[int, ...]] = set()

    for offset, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            errors.append(f"escape record {offset} must be an object")
            continue
        index = _as_int(
            raw.get("assignment_index_1based"),
            f"escape record {offset} assignment_index_1based",
            errors,
        )
        escape_indices.append(index)
        row = raw.get("row")
        if row != 0:
            errors.append(f"escape record {index} row is {row!r}, expected 0")
        witness_order = raw.get("witness_order")
        if not isinstance(witness_order, list):
            errors.append(f"escape record {index} witness_order must be a list")
        else:
            witness_orders.add(tuple(int(value) for value in witness_order))
        outer_class = raw.get("outer_class")
        inner_class = raw.get("inner_class")
        if outer_class != inner_class:
            errors.append(f"escape record {index} outer/inner class mismatch")
        if isinstance(outer_class, list):
            equal_classes.add(tuple(int(value) for value in outer_class))
        outer_span = _as_int(raw.get("outer_span"), f"escape {index} outer_span", errors)
        inner_span = _as_int(raw.get("inner_span"), f"escape {index} inner_span", errors)
        if outer_span <= inner_span:
            errors.append(f"escape record {index} does not have a strict outer span")
        if raw.get("shared_endpoint_count") != 1:
            errors.append(f"escape record {index} must share exactly one endpoint")
        template = str(raw.get("template"))
        templates[template] += 1
        path_length = _as_int(
            raw.get("distance_equality_path_length"),
            f"escape {index} distance_equality_path_length",
            errors,
        )
        path_rows = raw.get("distance_equality_path_rows")
        if not isinstance(path_rows, list) or len(path_rows) != path_length:
            errors.append(f"escape record {index} has inconsistent path length")
        path_lengths[str(path_length)] += 1

    summary = escapes.get("summary")
    if isinstance(summary, Mapping):
        _check_equal(
            errors,
            "escape source_turn_sat_escape_count",
            summary.get("source_turn_sat_escape_count"),
            len(escape_indices),
        )
        _check_equal(
            errors,
            "escape path_length_histogram",
            summary.get("path_length_histogram"),
            dict(sorted(path_lengths.items())),
        )
    else:
        errors.append("escape summary must be an object")

    return {
        "escape_indices": sorted(escape_indices),
        "template_counts": dict(sorted(templates.items())),
        "path_length_histogram": dict(sorted(path_lengths.items())),
        "witness_orders": [list(order) for order in sorted(witness_orders)],
        "equal_classes": [list(cls) for cls in sorted(equal_classes)],
    }


def build_payload(
    *,
    pilot_path: Path = DEFAULT_PILOT,
    escapes_path: Path = DEFAULT_ESCAPES,
) -> dict[str, Any]:
    """Return the combined row0 closure crosswalk payload."""

    errors: list[str] = []
    pilot = _load_json(pilot_path)
    escapes = _load_json(escapes_path)

    for key, expected in EXPECTED_PILOT.items():
        _check_equal(errors, f"pilot {key}", pilot.get(key), expected)
    for key, expected in EXPECTED_ESCAPES.items():
        _check_equal(errors, f"escapes {key}", escapes.get(key), expected)

    pilot_partition = _pilot_partition(pilot, errors)
    escape_partition = _escape_partition(escapes, errors)

    assignment_indices = pilot_partition["assignment_indices"]
    farkas_indices = pilot_partition["farkas_indices"]
    sat_indices = sorted(pilot_partition["sat_indices"])
    escape_indices = escape_partition["escape_indices"]
    combined_closed = sorted(set(farkas_indices) | set(escape_indices))
    overlap = sorted(set(farkas_indices) & set(escape_indices))
    unclosed = sorted(set(assignment_indices) - set(combined_closed))

    _check_equal(errors, "sat-vs-escape assignment indices", sat_indices, escape_indices)

    coverage = {
        "row0_index": pilot.get("row0_index"),
        "full_assignment_count": len(assignment_indices),
        "turn_farkas_unsat_count": len(farkas_indices),
        "turn_sat_escape_count": len(sat_indices),
        "turn_sat_escape_assignment_indices": sat_indices,
        "vertex_circle_escape_assignment_indices": escape_indices,
        "turn_and_escape_overlap_count": len(overlap),
        "combined_closed_assignment_count": len(combined_closed),
        "unclosed_assignment_count": len(unclosed),
        "turn_status_counts": pilot_partition["turn_status_counts"],
        "vertex_circle_status_counts": pilot_partition["vertex_circle_status_counts"],
        "escape_template_counts": escape_partition["template_counts"],
        "escape_path_length_histogram": escape_partition["path_length_histogram"],
        "common_escape_witness_order": (
            escape_partition["witness_orders"][0]
            if len(escape_partition["witness_orders"]) == 1
            else None
        ),
        "common_escape_equal_distance_class": (
            escape_partition["equal_classes"][0]
            if len(escape_partition["equal_classes"]) == 1
            else None
        ),
    }

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifacts": [
            _source_summary(pilot_path, pilot),
            _source_summary(escapes_path, escapes),
        ],
        "coverage_summary": coverage,
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "Within the bounded row0-index-0 n=10 pilot, the stored weak-turn "
            "Farkas certificates and the four stored row0-local vertex-circle "
            "self-edge escape templates form a disjoint closure partition of "
            "the 160 assignments. This is a crosswalk only, not an n=10 proof."
        ),
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "provenance": dict(PROVENANCE),
    }


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert the expected bounded row0 combined-closure crosswalk."""

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
        "not a proof of n=10",
        "not a complete n=10 search",
        "not a counterexample",
        "not a global status update",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")
    if payload.get("coverage_summary") != EXPECTED_COVERAGE:
        raise AssertionError(
            "coverage summary mismatch: "
            f"{payload.get('coverage_summary')!r} != {EXPECTED_COVERAGE!r}"
        )


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    coverage = payload["coverage_summary"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"row0 index: {coverage['row0_index']}",
        f"full assignments: {coverage['full_assignment_count']}",
        f"turn Farkas closures: {coverage['turn_farkas_unsat_count']}",
        f"vertex-circle escape closures: {coverage['turn_sat_escape_count']}",
        f"unclosed assignments: {coverage['unclosed_assignment_count']}",
        f"escape indices: {coverage['turn_sat_escape_assignment_indices']}",
    ]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", type=Path, default=DEFAULT_PILOT)
    parser.add_argument("--escapes", type=Path, default=DEFAULT_ESCAPES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    pilot_path = _resolve(args.pilot)
    escapes_path = _resolve(args.escapes)
    out_path = _resolve(args.out)

    try:
        payload = build_payload(pilot_path=pilot_path, escapes_path=escapes_path)
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
        assert_expected_payload(payload)

    if args.check:
        existing = _load_json(out_path)
        if existing != payload:
            print(f"{_display(out_path)} does not match regenerated payload", file=sys.stderr)
            return 1

    if args.write:
        _write_json(out_path, payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=10 row0 turn + vertex-circle combined closure")
        for line in summary_lines(payload):
            print(line)
        if args.check:
            print(f"OK: {_display(out_path)} matches regenerated payload")
        if args.write:
            print(f"wrote {_display(out_path)}")
    else:
        print("FAILED: n=10 row0 combined closure", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
