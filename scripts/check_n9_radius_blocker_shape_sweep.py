#!/usr/bin/env python3
"""Check all n=9 natural-order exact-four radius-blocker shapes.

This is a finite bridge diagnostic only. It proves no general theorem about
Erdos Problem #97 and supplies no counterexample.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from math import comb
from pathlib import Path
from typing import Mapping, Sequence

from erdos97.radius_blocker_packets import (
    SCHEMA,
    STATUS,
    TRUST,
    PacketConfig,
    dihedral_subset_images,
    dihedral_subset_representatives,
    analyze_radius_blocker_packet,
    full_exact_four_radius_blocker_rich_classes,
    result_to_packet_json,
)

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_radius_blocker_shape_sweep.json"

N = 9
ORDER = list(range(N))
EXPECTED_SUMMARY = {
    "shape_count": 10,
    "labelled_blocker_count": 126,
    "all_dihedral_labelled_blockers_covered": True,
    "all_cases_have_radius_blocker": True,
    "all_cases_finished": True,
    "all_incidence_survivors_obstructed": True,
    "total_nodes_visited": 754_505,
    "total_incidence_survivors": 1_358,
    "vertex_circle_status_totals": {"self_edge": 1_164, "strict_cycle": 194},
    "dihedral_orbit_size_counts": {"9": 6, "18": 4},
}
EXPECTED_CASES = {
    (0, 1, 2, 3): {
        "dihedral_orbit_size": 9,
        "gap_cycle": [1, 1, 1, 6],
        "nodes_visited": 58_742,
        "incidence_survivors": 90,
        "vertex_circle_status_counts": {"self_edge": 70, "strict_cycle": 20},
        "rejection_counts": {
            "column_pair_cap": 4_679_361,
            "row_pair_cap": 2_637_115,
            "two_overlap_crossing": 4_410_497,
        },
    },
    (0, 1, 2, 4): {
        "dihedral_orbit_size": 18,
        "gap_cycle": [1, 1, 2, 5],
        "nodes_visited": 63_685,
        "incidence_survivors": 118,
        "vertex_circle_status_counts": {"self_edge": 97, "strict_cycle": 21},
        "rejection_counts": {
            "column_pair_cap": 5_216_230,
            "row_pair_cap": 2_791_181,
            "two_overlap_crossing": 4_700_795,
        },
    },
    (0, 1, 2, 5): {
        "dihedral_orbit_size": 18,
        "gap_cycle": [1, 1, 3, 4],
        "nodes_visited": 63_328,
        "incidence_survivors": 111,
        "vertex_circle_status_counts": {"self_edge": 93, "strict_cycle": 18},
        "rejection_counts": {
            "column_pair_cap": 5_116_365,
            "row_pair_cap": 2_797_681,
            "two_overlap_crossing": 4_693_701,
        },
    },
    (0, 1, 3, 4): {
        "dihedral_orbit_size": 9,
        "gap_cycle": [1, 2, 1, 5],
        "nodes_visited": 79_875,
        "incidence_survivors": 148,
        "vertex_circle_status_counts": {"self_edge": 134, "strict_cycle": 14},
        "rejection_counts": {
            "column_pair_cap": 6_742_977,
            "row_pair_cap": 3_202_228,
            "two_overlap_crossing": 5_567_523,
        },
    },
    (0, 1, 3, 5): {
        "dihedral_orbit_size": 18,
        "gap_cycle": [1, 2, 2, 4],
        "nodes_visited": 80_794,
        "incidence_survivors": 142,
        "vertex_circle_status_counts": {"self_edge": 121, "strict_cycle": 21},
        "rejection_counts": {
            "column_pair_cap": 6_798_628,
            "row_pair_cap": 3_255_905,
            "two_overlap_crossing": 5_692_769,
        },
    },
    (0, 1, 3, 6): {
        "dihedral_orbit_size": 18,
        "gap_cycle": [1, 2, 3, 3],
        "nodes_visited": 79_741,
        "incidence_survivors": 141,
        "vertex_circle_status_counts": {"self_edge": 125, "strict_cycle": 16},
        "rejection_counts": {
            "column_pair_cap": 6_707_012,
            "row_pair_cap": 3_220_411,
            "two_overlap_crossing": 5_644_015,
        },
    },
    (0, 1, 3, 7): {
        "dihedral_orbit_size": 9,
        "gap_cycle": [1, 2, 4, 2],
        "nodes_visited": 78_302,
        "incidence_survivors": 136,
        "vertex_circle_status_counts": {"self_edge": 120, "strict_cycle": 16},
        "rejection_counts": {
            "column_pair_cap": 6_626_461,
            "row_pair_cap": 3_154_534,
            "two_overlap_crossing": 5_537_339,
        },
    },
    (0, 1, 4, 5): {
        "dihedral_orbit_size": 9,
        "gap_cycle": [1, 3, 1, 4],
        "nodes_visited": 81_654,
        "incidence_survivors": 168,
        "vertex_circle_status_counts": {"self_edge": 144, "strict_cycle": 24},
        "rejection_counts": {
            "column_pair_cap": 6_780_162,
            "row_pair_cap": 3_350_024,
            "two_overlap_crossing": 5_755_696,
        },
    },
    (0, 1, 4, 6): {
        "dihedral_orbit_size": 9,
        "gap_cycle": [1, 3, 2, 3],
        "nodes_visited": 81_257,
        "incidence_survivors": 158,
        "vertex_circle_status_counts": {"self_edge": 136, "strict_cycle": 22},
        "rejection_counts": {
            "column_pair_cap": 6_788_067,
            "row_pair_cap": 3_317_453,
            "two_overlap_crossing": 5_759_554,
        },
    },
    (0, 2, 4, 6): {
        "dihedral_orbit_size": 9,
        "gap_cycle": [2, 2, 2, 3],
        "nodes_visited": 87_127,
        "incidence_survivors": 146,
        "vertex_circle_status_counts": {"self_edge": 124, "strict_cycle": 22},
        "rejection_counts": {
            "column_pair_cap": 7_198_066,
            "row_pair_cap": 3_502_252,
            "two_overlap_crossing": 6_429_970,
        },
    },
}


def blocker_label(blocker: Sequence[int]) -> str:
    return "U" + "".join(str(label) for label in blocker)


def gap_cycle(blocker: Sequence[int]) -> list[int]:
    labels = list(blocker)
    return [
        int((labels[(index + 1) % len(labels)] - labels[index]) % N)
        for index in range(len(labels))
    ]


def json_counter(counter: Counter[object]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def expected_row_option_counts(blocker: Sequence[int]) -> list[int]:
    blocker_set = set(blocker)
    return [65 if center in blocker_set else 70 for center in range(N)]


def build_case(blocker: Sequence[int]) -> dict[str, object]:
    """Build one deterministic blocker-shape packet payload."""

    blocker_tuple = tuple(int(label) for label in blocker)
    rich_classes = full_exact_four_radius_blocker_rich_classes(N, blocker_tuple)
    result = analyze_radius_blocker_packet(
        f"n9_full_exact_four_radius_blocker_shape_{blocker_label(blocker_tuple)}_natural_order",
        rich_classes,
        blocker_tuple,
        ORDER,
        PacketConfig(
            max_nodes=100_000,
            max_survivor_examples=1,
            max_obstruction_examples_per_status=1,
        ),
    )
    case = result_to_packet_json(result)
    case.update(
        {
            "dihedral_representative": list(blocker_tuple),
            "dihedral_orbit_size": len(dihedral_subset_images(N, blocker_tuple)),
            "gap_cycle": gap_cycle(blocker_tuple),
        }
    )
    return case


def build_payload() -> dict[str, object]:
    """Build the deterministic all-shape n=9 radius-blocker payload."""

    representatives = dihedral_subset_representatives(N, 4)
    cases = [build_case(blocker) for blocker in representatives]
    status_totals: Counter[str] = Counter()
    orbit_sizes: Counter[int] = Counter()
    for case in cases:
        orbit_sizes[int(case["dihedral_orbit_size"])] += 1
        status_totals.update(case["vertex_circle_status_counts"])

    labelled_blocker_count = sum(
        int(case["dihedral_orbit_size"]) for case in cases
    )
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Natural-order n=9 exact-four row-option sweep over all 10 "
            "dihedral classes of four-vertex blockers. This obstructs only "
            "those finite packets under the encoded incidence/order filters "
            "and selected-distance vertex-circle replay; it is not a proof "
            "of Erdos Problem #97 and not a counterexample."
        ),
        "summary": {
            "n": N,
            "order": ORDER,
            "shape_count": len(cases),
            "labelled_blocker_count": labelled_blocker_count,
            "all_dihedral_labelled_blockers_covered": (
                labelled_blocker_count == comb(N, 4)
            ),
            "all_cases_have_radius_blocker": all(
                bool(case["radius_blocker_ok"]) for case in cases
            ),
            "all_cases_finished": all(not bool(case["aborted"]) for case in cases),
            "all_incidence_survivors_obstructed": all(
                bool(case["all_incidence_survivors_obstructed"]) for case in cases
            ),
            "total_nodes_visited": sum(int(case["nodes_visited"]) for case in cases),
            "total_incidence_survivors": sum(
                int(case["incidence_survivors"]) for case in cases
            ),
            "vertex_circle_status_totals": json_counter(status_totals),
            "dihedral_orbit_size_counts": json_counter(orbit_sizes),
        },
        "cases": cases,
        "interpretation_warnings": [
            "The sweep quantifies over exact four-row options only.",
            "The cyclic order is fixed to natural order.",
            "The blocker is varied only up to dihedral shape in that order.",
            "The result does not classify all n=9 rich-class systems.",
            "No general proof and no counterexample are claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_n9_radius_blocker_shape_sweep.py",
            "command": (
                "python scripts/check_n9_radius_blocker_shape_sweep.py "
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
    """Assert the stable blocker-shape sweep counts."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"unexpected status: {payload.get('status')!r}")
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("summary is missing")
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary[{key!r}] is {summary.get(key)!r}, expected {expected!r}"
            )

    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise AssertionError("cases are missing")
    by_blocker: dict[tuple[int, ...], Mapping[str, object]] = {}
    for case in cases:
        if not isinstance(case, Mapping):
            raise AssertionError(f"case is not a mapping: {case!r}")
        blocker = tuple(int(label) for label in case["blocker"])
        by_blocker[blocker] = case
    if set(by_blocker) != set(EXPECTED_CASES):
        raise AssertionError(f"unexpected blockers: {sorted(by_blocker)}")

    for blocker, expected_case in EXPECTED_CASES.items():
        case = by_blocker[blocker]
        if case.get("row_option_counts") != expected_row_option_counts(blocker):
            raise AssertionError(f"unexpected row options for {blocker}")
        if case.get("aborted") is not False:
            raise AssertionError(f"packet search aborted for {blocker}")
        if case.get("radius_blocker_ok") is not True:
            raise AssertionError(f"blocker is not a radius-blocker for {blocker}")
        if case.get("all_incidence_survivors_obstructed") is not True:
            raise AssertionError(f"clean incidence survivor for {blocker}")
        for key, expected in expected_case.items():
            if case.get(key) != expected:
                raise AssertionError(
                    f"case {blocker} [{key!r}] is {case.get(key)!r}, "
                    f"expected {expected!r}"
                )


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=9 radius-blocker shape sweep")
    print(f"claim scope: {payload['claim_scope']}")
    print(f"shape count: {summary['shape_count']}")
    print(f"labelled blockers covered: {summary['labelled_blocker_count']}")
    print(f"nodes visited: {summary['total_nodes_visited']}")
    print(f"incidence survivors: {summary['total_incidence_survivors']}")
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
