#!/usr/bin/env python3
"""Check the radius-blocker plus vertex-circle pilot packet artifact.

The generated payload is a bridge diagnostic only. It does not claim a proof
of the adaptive blocker bridge, Erdos Problem #97, or a counterexample.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from erdos97.adaptive_blockers import first_blocker
from erdos97.bridge_negative_controls import (
    c13_sidon_rows,
    output7_two_block_rows,
)
from erdos97.fragile_hypergraph import block6_family, full_selected_extension
from erdos97.radius_blocker_packets import (
    CLAIM_SCOPE,
    SCHEMA,
    STATUS,
    TRUST,
    PacketConfig,
    analyze_radius_blocker_packet,
    exact_four_rich_classes_from_rows,
    result_to_packet_json,
)

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUT = ROOT / "data" / "certificates" / "radius_blocker_vertex_circle_pilot.json"

EXPECTED_CASES = {
    "C13_sidon_fixed_rows_natural_order": {
        "blocker": [0, 1, 2, 3],
        "incidence_survivors": 1,
        "vertex_circle_status_counts": {"strict_cycle": 1},
    },
    "two_block_no_forward_fixed_rows": {
        "blocker": [0, 1, 2, 5],
        "incidence_survivors": 1,
        "vertex_circle_status_counts": {"self_edge": 1},
    },
    "block6_two_copy_full_extension_fixed_rows": {
        "blocker": [0, 1, 2, 5],
        "incidence_survivors": 1,
        "vertex_circle_status_counts": {"self_edge": 1},
    },
}


def _fixed_rows_case(
    name: str,
    rows: Sequence[Sequence[int]],
    order: Sequence[int],
    blocker_max_size: int = 6,
) -> dict[str, object]:
    rich_classes = exact_four_rich_classes_from_rows(rows)
    blocker = first_blocker(rich_classes, max_size=blocker_max_size)
    if blocker is None:
        raise AssertionError(f"{name} has no radius-blocker through size {blocker_max_size}")
    result = analyze_radius_blocker_packet(
        name,
        rich_classes,
        blocker,
        order,
        PacketConfig(max_nodes=10_000),
    )
    return result_to_packet_json(result)


def _block6_two_copy_extension_case() -> dict[str, object]:
    n, fragile_rows = block6_family(2)
    extension = full_selected_extension(n, fragile_rows)
    if not extension.ok or extension.full_rows is None:
        raise AssertionError("expected the two-block fragile family to extend")
    rows = [extension.full_rows[center] for center in range(n)]
    return _fixed_rows_case(
        "block6_two_copy_full_extension_fixed_rows",
        rows,
        list(range(n)),
    )


def build_payload() -> dict[str, object]:
    """Build the deterministic pilot payload."""

    cases = [
        _fixed_rows_case(
            "C13_sidon_fixed_rows_natural_order",
            c13_sidon_rows(),
            list(range(13)),
        ),
        _fixed_rows_case(
            "two_block_no_forward_fixed_rows",
            output7_two_block_rows(),
            [0, 4, 3, 1, 2, 5, 6, 10, 9, 7, 8, 11],
        ),
        _block6_two_copy_extension_case(),
    ]
    status_totals: dict[str, int] = {}
    for case in cases:
        counts = case["vertex_circle_status_counts"]
        if not isinstance(counts, Mapping):
            raise AssertionError("case status counts should be a mapping")
        for status, count in counts.items():
            status_totals[str(status)] = status_totals.get(str(status), 0) + int(count)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": {
            "case_count": len(cases),
            "all_cases_have_radius_blocker": all(
                bool(case["radius_blocker_ok"]) for case in cases
            ),
            "all_incidence_survivors_obstructed": all(
                bool(case["all_incidence_survivors_obstructed"]) for case in cases
            ),
            "total_incidence_survivors": sum(
                int(case["incidence_survivors"]) for case in cases
            ),
            "vertex_circle_status_totals": dict(sorted(status_totals.items())),
        },
        "cases": cases,
        "interpretation_warnings": [
            "This is a fixed exact-four row-option pilot, not a proof of the blocker bridge.",
            "The C13 case is already retired by a stronger all-order Kalmanson certificate.",
            "The two-block cases are bridge stress controls, not Euclidean counterexamples.",
            "No general proof and no counterexample are claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_radius_blocker_vertex_circle_pilot.py",
            "command": (
                "python scripts/check_radius_blocker_vertex_circle_pilot.py "
                "--write --assert-expected"
            ),
            "sources": [
                "src/erdos97/radius_blocker_packets.py",
                "src/erdos97/adaptive_blockers.py",
                "src/erdos97/vertex_circle_quotient_replay.py",
                "src/erdos97/bridge_negative_controls.py",
            ],
        },
    }


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    """Assert the stable pilot counts."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"unexpected status: {payload.get('status')!r}")
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("summary is missing")
    expected_summary = {
        "case_count": 3,
        "all_cases_have_radius_blocker": True,
        "all_incidence_survivors_obstructed": True,
        "total_incidence_survivors": 3,
        "vertex_circle_status_totals": {"self_edge": 2, "strict_cycle": 1},
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary[{key!r}] is {summary.get(key)!r}, expected {expected!r}"
            )
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise AssertionError("cases should be a list")
    by_name = {
        str(case["name"]): case for case in cases if isinstance(case, Mapping)
    }
    for name, expected in EXPECTED_CASES.items():
        case = by_name.get(name)
        if case is None:
            raise AssertionError(f"missing case {name}")
        for key, value in expected.items():
            if case.get(key) != value:
                raise AssertionError(
                    f"{name}[{key!r}] is {case.get(key)!r}, expected {value!r}"
                )


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("Radius-blocker vertex-circle pilot")
    print(f"claim scope: {CLAIM_SCOPE}")
    print(f"cases: {summary['case_count']}")
    print(f"all blockers: {summary['all_cases_have_radius_blocker']}")
    print(
        "all incidence survivors obstructed: "
        f"{summary['all_incidence_survivors_obstructed']}"
    )
    print(f"status totals: {summary['vertex_circle_status_totals']}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true", help="write the artifact")
    parser.add_argument("--check", action="store_true", help="compare artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print full JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload()
    if args.assert_expected:
        assert_expected_payload(payload)
    if args.check:
        compare_artifact(payload, args.out)
    if args.write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_summary(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
