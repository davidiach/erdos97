#!/usr/bin/env python3
"""Check bounded rational-grid closure for the two-parabola lens ansatz."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.two_parabola_lens_closure import (  # noqa: E402
    SCHEMA,
    default_grid_cases,
    grid_search_summary,
)


DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "two_parabola_lens_grid_search.json"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def check_payload(payload: dict[str, Any], *, assert_expected: bool) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("trust") != "FINITE_BOOKKEEPING_NOT_A_PROOF":
        raise AssertionError(f"unexpected trust label: {payload.get('trust')!r}")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise AssertionError("artifact must contain a nonempty cases list")

    case_count = payload.get("case_count")
    if case_count != len(cases):
        raise AssertionError(f"case_count {case_count!r} does not match cases")
    closure_case_count = sum(1 for case in cases if case.get("closure_found"))
    if payload.get("closure_case_count") != closure_case_count:
        raise AssertionError("closure_case_count does not match case rows")
    if payload.get("closure_found") != bool(closure_case_count):
        raise AssertionError("closure_found does not match closure_case_count")

    if assert_expected:
        expected_cases = len(default_grid_cases())
        if case_count != expected_cases:
            raise AssertionError(f"expected {expected_cases} default grid cases")
        if payload.get("status") != "NO_GRID_CLOSURE_IN_BOUNDED_RATIONAL_GRIDS":
            raise AssertionError(f"unexpected status: {payload.get('status')!r}")
        if payload.get("closure_found") is not False:
            raise AssertionError("default artifact should record no closure")
        floor = payload.get("opposite_chain_size_floor")
        if not isinstance(floor, dict) or floor.get("min_total_points") != 16:
            raise AssertionError("expected a 16-point opposite-chain size floor")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write-artifact", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.write_artifact:
        payload = grid_search_summary()
        args.artifact.parent.mkdir(parents=True, exist_ok=True)
        with args.artifact.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    else:
        payload = load_json(args.artifact)

    if args.check or args.assert_expected:
        check_payload(payload, assert_expected=args.assert_expected)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            f"{payload['status']} cases={payload['case_count']} "
            f"closures={payload['closure_case_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
