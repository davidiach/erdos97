#!/usr/bin/env python3
"""Check the full n=9 exact-four radius-blocker packet.

This is a finite bridge diagnostic only.  It proves no general theorem about
Erdos Problem #97 and supplies no counterexample.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from erdos97.radius_blocker_packets import (
    SCHEMA,
    STATUS,
    TRUST,
    PacketConfig,
    analyze_radius_blocker_packet,
    full_exact_four_radius_blocker_rich_classes,
    result_to_packet_json,
)

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUT = (
    ROOT / "data" / "certificates" / "n9_full_radius_blocker_vertex_circle_packet.json"
)

PACKET_NAME = "n9_full_exact_four_radius_blocker_U0123_natural_order"
N = 9
ORDER = list(range(N))
BLOCKER = [0, 1, 2, 3]
EXPECTED = {
    "row_option_counts": [65, 65, 65, 65, 70, 70, 70, 70, 70],
    "nodes_visited": 58_742,
    "incidence_survivors": 90,
    "vertex_circle_status_counts": {"self_edge": 70, "strict_cycle": 20},
    "rejection_counts": {
        "column_pair_cap": 4_679_361,
        "row_pair_cap": 2_637_115,
        "two_overlap_crossing": 4_410_497,
    },
}


def build_payload() -> dict[str, object]:
    """Build the deterministic n=9 full-blocker packet payload."""

    rich_classes = full_exact_four_radius_blocker_rich_classes(N, BLOCKER)
    result = analyze_radius_blocker_packet(
        PACKET_NAME,
        rich_classes,
        BLOCKER,
        ORDER,
        PacketConfig(max_nodes=100_000),
    )
    case = result_to_packet_json(result)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Full exact-four row-option packet for n=9, natural cyclic order, "
            "and blocker {0,1,2,3}. This obstructs only that finite packet "
            "under the encoded incidence/order filters and selected-distance "
            "vertex-circle replay; it is not a proof of Erdos Problem #97 and "
            "not a counterexample."
        ),
        "summary": {
            "case_count": 1,
            "all_cases_have_radius_blocker": bool(case["radius_blocker_ok"]),
            "all_incidence_survivors_obstructed": bool(
                case["all_incidence_survivors_obstructed"]
            ),
            "total_incidence_survivors": int(case["incidence_survivors"]),
            "vertex_circle_status_totals": dict(
                case["vertex_circle_status_counts"]
            ),
        },
        "case": case,
        "interpretation_warnings": [
            "The packet quantifies over exact four-row options only.",
            "The cyclic order and blocker subset are fixed.",
            "The result does not classify all n=9 rich-class systems.",
            "No general proof and no counterexample are claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_n9_full_radius_blocker_vertex_circle_packet.py",
            "command": (
                "python scripts/check_n9_full_radius_blocker_vertex_circle_packet.py "
                "--write --assert-expected"
            ),
            "sources": [
                "src/erdos97/radius_blocker_packets.py",
                "src/erdos97/adaptive_blockers.py",
                "src/erdos97/vertex_circle_quotient_replay.py",
            ],
        },
    }


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    """Assert the stable full-blocker packet counts."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"unexpected status: {payload.get('status')!r}")
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("summary is missing")
    expected_summary = {
        "case_count": 1,
        "all_cases_have_radius_blocker": True,
        "all_incidence_survivors_obstructed": True,
        "total_incidence_survivors": 90,
        "vertex_circle_status_totals": {"self_edge": 70, "strict_cycle": 20},
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary[{key!r}] is {summary.get(key)!r}, expected {expected!r}"
            )
    case = payload.get("case")
    if not isinstance(case, Mapping):
        raise AssertionError("case is missing")
    if case.get("name") != PACKET_NAME:
        raise AssertionError(f"unexpected packet name: {case.get('name')!r}")
    for key, expected in EXPECTED.items():
        if case.get(key) != expected:
            raise AssertionError(
                f"case[{key!r}] is {case.get(key)!r}, expected {expected!r}"
            )
    if case.get("aborted") is not False:
        raise AssertionError(f"packet search aborted: {case.get('aborted')!r}")


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    case = payload["case"]
    assert isinstance(summary, Mapping)
    assert isinstance(case, Mapping)
    print("n=9 full radius-blocker vertex-circle packet")
    print(f"claim scope: {payload['claim_scope']}")
    print(f"row options: {case['row_option_counts']}")
    print(f"nodes visited: {case['nodes_visited']}")
    print(f"incidence survivors: {case['incidence_survivors']}")
    print(f"all incidence survivors obstructed: {summary['all_incidence_survivors_obstructed']}")
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
