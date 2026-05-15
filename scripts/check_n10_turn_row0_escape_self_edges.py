#!/usr/bin/env python3
"""Generate or check the n=10 row0 weak-turn escape self-edge template."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data" / "certificates" / "n10_turn_row0_pilot.json"
DEFAULT_OUT = ROOT / "data" / "certificates" / "n10_turn_row0_escape_self_edges.json"

SCHEMA = "erdos97.n10_turn_row0_escape_self_edges.v1"
STATUS = "N10_ROW0_ESCAPE_SELF_EDGE_TEMPLATE_DIAGNOSTIC"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
CLAIM_SCOPE = (
    "Derived diagnostic for the four weak-turn SAT escapes in the bounded "
    "n=10 row0-index-0 pilot; records only their row0-local vertex-circle "
    "self-edge templates, not a proof of n=10, not a complete n=10 search, "
    "not a counterexample, and not a global status update."
)
EXPECTED_SUMMARY = {
    "source_turn_sat_escape_count": 4,
    "row0_self_edge_count": 4,
    "distinct_template_count": 4,
    "common_witness_order": [1, 2, 3, 4],
    "common_equal_distance_class": [0, 1],
    "row_counts": {"0": 4},
    "shared_endpoint_count_distribution": {"1": 4},
    "path_length_histogram": {"3": 1, "4": 1, "5": 1, "7": 1},
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


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} did not contain a JSON object")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
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


def _template_key(edge: dict[str, Any]) -> str:
    return f"{edge['outer_pair']} > {edge['inner_pair']}"


def _escape_record(raw: dict[str, Any]) -> dict[str, Any]:
    self_edge = raw.get("self_edge")
    if not isinstance(self_edge, dict):
        raise ValueError("escape record is missing self_edge object")

    path = self_edge.get("distance_equality_path")
    if not isinstance(path, list):
        raise ValueError("escape self_edge is missing distance_equality_path")

    row = self_edge.get("row")
    witness_order = self_edge.get("witness_order")
    outer_class = self_edge.get("outer_class")
    inner_class = self_edge.get("inner_class")
    shared_endpoint_count = self_edge.get("shared_endpoint_count")
    if row != 0:
        raise ValueError(f"expected row0 self-edge, got row {row!r}")
    if witness_order != EXPECTED_SUMMARY["common_witness_order"]:
        raise ValueError(f"unexpected witness order {witness_order!r}")
    if outer_class != EXPECTED_SUMMARY["common_equal_distance_class"]:
        raise ValueError(f"unexpected outer class {outer_class!r}")
    if inner_class != EXPECTED_SUMMARY["common_equal_distance_class"]:
        raise ValueError(f"unexpected inner class {inner_class!r}")
    if shared_endpoint_count != 1:
        raise ValueError(f"unexpected shared endpoint count {shared_endpoint_count!r}")

    outer_span = self_edge.get("outer_span")
    inner_span = self_edge.get("inner_span")
    if not isinstance(outer_span, int) or not isinstance(inner_span, int):
        raise ValueError("missing integer span data")
    if outer_span <= inner_span:
        raise ValueError("self-edge template does not have a strict outer span")

    return {
        "assignment_index_1based": raw["assignment_index_1based"],
        "row": row,
        "witness_order": witness_order,
        "outer_pair": self_edge["outer_pair"],
        "inner_pair": self_edge["inner_pair"],
        "outer_span": outer_span,
        "inner_span": inner_span,
        "outer_class": outer_class,
        "inner_class": inner_class,
        "shared_endpoint_count": shared_endpoint_count,
        "distance_equality_path_length": len(path),
        "distance_equality_path_rows": [step["row"] for step in path],
        "template": _template_key(self_edge),
    }


def build_payload(source: Path = DEFAULT_SOURCE) -> dict[str, Any]:
    source_payload = _load_json(source)
    raw_escapes = source_payload.get("turn_sat_escape_self_edges")
    if not isinstance(raw_escapes, list):
        raise ValueError("source artifact is missing turn_sat_escape_self_edges")

    records = [_escape_record(raw) for raw in raw_escapes]
    row_counts = Counter(str(record["row"]) for record in records)
    shared_endpoint_counts = Counter(
        str(record["shared_endpoint_count"]) for record in records
    )
    path_lengths = Counter(
        str(record["distance_equality_path_length"]) for record in records
    )
    templates = sorted({str(record["template"]) for record in records})

    summary = {
        "source_turn_sat_escape_count": source_payload.get("turn_sat_escape_count"),
        "row0_self_edge_count": len(records),
        "distinct_template_count": len(templates),
        "common_witness_order": EXPECTED_SUMMARY["common_witness_order"],
        "common_equal_distance_class": EXPECTED_SUMMARY["common_equal_distance_class"],
        "row_counts": dict(sorted(row_counts.items())),
        "shared_endpoint_count_distribution": dict(
            sorted(shared_endpoint_counts.items())
        ),
        "path_length_histogram": dict(sorted(path_lengths.items())),
    }

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifact": _display(source),
        "summary": summary,
        "templates": templates,
        "escape_records": records,
        "interpretation": (
            "The bounded row0-index-0 turn pilot has four weak-turn SAT "
            "escapes. In all four, the first vertex-circle contradiction is a "
            "row0 self-edge on witness order [1,2,3,4], with equal-distance "
            "class [0,1] forced to be both the outer and inner chord class."
        ),
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "provenance": {
            "generator": "scripts/check_n10_turn_row0_escape_self_edges.py",
            "command": (
                "python scripts/check_n10_turn_row0_escape_self_edges.py "
                "--write --assert-expected"
            ),
            "source": _display(source),
        },
    }


def assert_expected_payload(payload: dict[str, Any]) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected schema")
    if payload.get("status") != STATUS:
        raise AssertionError("unexpected status")
    if payload.get("trust") != TRUST:
        raise AssertionError("unexpected trust")
    if payload.get("summary") != EXPECTED_SUMMARY:
        raise AssertionError("unexpected summary")
    templates = payload.get("templates")
    if not isinstance(templates, list) or len(templates) != 4:
        raise AssertionError("unexpected templates")
    records = payload.get("escape_records")
    if not isinstance(records, list) or len(records) != 4:
        raise AssertionError("unexpected escape records")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    source = _resolve(args.source)
    out = _resolve(args.out)
    payload = build_payload(source)

    if args.assert_expected:
        assert_expected_payload(payload)

    if args.check:
        existing = _load_json(out)
        if existing != payload:
            print(f"{_display(out)} does not match regenerated payload", file=sys.stderr)
            return 1

    if args.write:
        _write_json(out, payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("n=10 row0 weak-turn escape self-edge template")
        print(f"source escapes: {payload['summary']['source_turn_sat_escape_count']}")
        print(f"row0 self-edges: {payload['summary']['row0_self_edge_count']}")
        print(f"templates: {payload['summary']['distinct_template_count']}")
        if args.check:
            print(f"OK: {_display(out)} matches regenerated payload")
        if args.write:
            print(f"wrote {_display(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
