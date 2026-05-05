#!/usr/bin/env python3
"""Replay vertex-circle quotient obstructions from JSON input."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    local_core_bundle_to_json,
    replay_local_core_bundle,
    replay_payload,
    result_to_json,
)


def load_payload(path: str) -> dict[str, object]:
    with Path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise SystemExit("input JSON must be an object")
    return payload


def assert_single_expectations(
    row: dict[str, object],
    *,
    assert_obstructed: bool,
    assert_pass: bool,
) -> None:
    if assert_obstructed and not row["obstructed"]:
        raise AssertionError("expected a vertex-circle quotient obstruction")
    if assert_pass and row["obstructed"]:
        raise AssertionError(f"expected no obstruction, got {row['status']}")


def print_single_summary(row: dict[str, object]) -> None:
    result = "OBSTRUCTED" if row["obstructed"] else "PASS"
    print("result  n  selected rows  strict edges  status  self edges  cycle edges")
    print(
        f"{result:<10}  {row['n']}  {row['selected_row_count']}  "
        f"{row['strict_edge_count']}  {row['status']}  "
        f"{len(row['self_edge_conflicts'])}  {len(row['cycle_edges'])}"
    )


def print_bundle_summary(row: dict[str, object]) -> None:
    print("local-core vertex-circle quotient replay")
    print(f"certificates: {row['certificate_count']}")
    print(f"status counts: {row['status_counts']}")
    print(f"expected statuses match: {row['all_expected_statuses_match']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON payload or local-core bundle")
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    parser.add_argument("--assert-obstructed", action="store_true")
    parser.add_argument("--assert-pass", action="store_true")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="for local-core bundles, require replayed statuses to match recorded statuses",
    )
    args = parser.parse_args()

    if args.assert_obstructed and args.assert_pass:
        parser.error("--assert-obstructed and --assert-pass are mutually exclusive")

    payload = load_payload(args.input)
    if "certificates" in payload:
        row = local_core_bundle_to_json(replay_local_core_bundle(payload))
        if args.assert_expected and not row["all_expected_statuses_match"]:
            raise AssertionError("local-core replay status mismatch")
        if args.json:
            print(json.dumps(row, indent=2, sort_keys=True))
        else:
            print_bundle_summary(row)
            if args.assert_expected:
                print("OK: local-core replay statuses match")
        return 0

    row = result_to_json(replay_payload(payload))
    assert_single_expectations(
        row,
        assert_obstructed=args.assert_obstructed,
        assert_pass=args.assert_pass,
    )
    if args.json:
        print(json.dumps(row, indent=2, sort_keys=True))
    else:
        print_single_summary(row)
        if args.assert_obstructed or args.assert_pass:
            print("OK: vertex-circle quotient expectation verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
