#!/usr/bin/env python3
"""Check the generator-independent n=9 all-five-rich support subcase.

This is a finite support-catalogue diagnostic only. It proves no general
theorem about Erdos Problem #97 and supplies no counterexample.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from math import prod
from pathlib import Path
from typing import Mapping, Sequence

from erdos97.incidence_filters import (
    chords_cross_in_order,
    normalize_chord,
)
from erdos97.radius_blocker_packets import TRUST

ROOT = Path(__file__).resolve().parents[1]

SCHEMA = "erdos97.n9_all_five_rich_support_obstruction.v1"
STATUS = "N9_ALL_FIVE_RICH_SUPPORT_OBSTRUCTION_ONLY"
DEFAULT_OUT = (
    ROOT / "data" / "certificates" / "n9_all_five_rich_support_obstruction.json"
)
N = 9
ORDER = tuple(range(N))
SUPPORT_SIZE = 5
EXPECTED_SUMMARY = {
    "n": 9,
    "order": list(range(9)),
    "support_size": 5,
    "center_count": 9,
    "option_counts": [56, 56, 56, 56, 56, 56, 56, 56, 56],
    "raw_assignment_upper_bound": 5416169448144896,
    "center_pair_count": 36,
    "center_pair_candidate_count_total": 112896,
    "compatible_center_pair_count_total": 17640,
    "center_pair_compatible_count_distribution": {
        "140": 9,
        "440": 9,
        "640": 9,
        "740": 9,
    },
    "center_pair_rejection_counts": {
        "row_pair_cap": 70056,
        "two_overlap_crossing": 25200,
    },
    "search_nodes_visited": 136,
    "search_complete_assignments": 0,
    "search_dead_end_count": 116,
    "search_max_depth": 2,
    "search_aborted": False,
    "search_center_choice_counts": {"0": 1, "1": 20},
    "search_node_depth_counts": {"0": 56, "1": 80},
    "no_pair_filter_survivors": True,
}

Support = tuple[int, ...]
SupportOptions = tuple[tuple[Support, ...], ...]


@dataclass(frozen=True)
class SupportSearchResult:
    nodes_visited: int
    complete_assignments: int
    dead_end_count: int
    max_depth: int
    aborted: bool
    center_choice_counts: Mapping[int, int]
    node_depth_counts: Mapping[int, int]
    evaluation_rejection_counts: Mapping[str, int]
    first_dead_end: Mapping[str, object] | None


def counter_to_json(counter: Mapping[object, int]) -> dict[str, int]:
    """Return a stable JSON object for a small counter."""

    return {
        str(key): int(counter[key])
        for key in sorted(counter, key=lambda item: str(item))
    }


def support_options_for_center(
    n: int,
    center: int,
    support_size: int = SUPPORT_SIZE,
) -> tuple[Support, ...]:
    """Return all labelled supports of ``support_size`` avoiding ``center``."""

    if n <= support_size:
        raise ValueError(f"support size {support_size} is too large for n={n}")
    if center < 0 or center >= n:
        raise ValueError(f"center out of range: {center}")
    return tuple(
        tuple(row)
        for row in combinations(
            (label for label in range(n) if label != center),
            support_size,
        )
    )


def all_support_options(
    n: int = N,
    support_size: int = SUPPORT_SIZE,
) -> SupportOptions:
    """Return the generator-independent support catalogue for every center."""

    return tuple(
        support_options_for_center(n, center, support_size)
        for center in range(n)
    )


def row_pair_rejection(
    order: Sequence[int],
    left_center: int,
    left_support: Sequence[int],
    right_center: int,
    right_support: Sequence[int],
) -> str | None:
    """Return the first exact row-pair reason rejecting two supports.

    The filters are necessary geometric conditions for two exact distance
    classes in a strict convex polygon: two distinct circles share at most two
    points, and a two-overlap forces the source chord and shared-witness chord
    to cross.
    """

    if left_center == right_center:
        raise ValueError("row-pair rejection requires distinct centers")
    if right_center < left_center:
        return row_pair_rejection(
            order,
            right_center,
            right_support,
            left_center,
            left_support,
        )
    intersection = sorted(set(left_support) & set(right_support))
    if len(intersection) > 2:
        return "row_pair_cap"
    if len(intersection) == 2:
        source = normalize_chord(left_center, right_center)
        target = normalize_chord(intersection[0], intersection[1])
        if not chords_cross_in_order(source, target, order):
            return "two_overlap_crossing"
    return None


def build_pair_catalog(
    order: Sequence[int],
    options: SupportOptions,
) -> dict[str, object]:
    """Build a compact catalogue of pairwise support compatibility."""

    n = len(options)
    compatible_counts: Counter[int] = Counter()
    compatible_by_gap: dict[int, Counter[int]] = {}
    rejection_counts: Counter[str] = Counter()
    records: list[dict[str, object]] = []
    candidate_total = 0
    compatible_total = 0
    example_rejections: dict[str, dict[str, object]] = {}

    for left, right in combinations(range(n), 2):
        pair_compatible = 0
        pair_rejections: Counter[str] = Counter()
        for left_support in options[left]:
            for right_support in options[right]:
                candidate_total += 1
                reason = row_pair_rejection(
                    order,
                    left,
                    left_support,
                    right,
                    right_support,
                )
                if reason is None:
                    pair_compatible += 1
                    continue
                rejection_counts[reason] += 1
                pair_rejections[reason] += 1
                if reason not in example_rejections:
                    example_rejections[reason] = {
                        "centers": [left, right],
                        "left_support": list(left_support),
                        "right_support": list(right_support),
                        "intersection": sorted(
                            set(left_support) & set(right_support)
                        ),
                    }
        gap = min((right - left) % n, (left - right) % n)
        compatible_counts[pair_compatible] += 1
        compatible_by_gap.setdefault(gap, Counter())[pair_compatible] += 1
        compatible_total += pair_compatible
        records.append(
            {
                "centers": [left, right],
                "cyclic_gap": gap,
                "candidate_count": len(options[left]) * len(options[right]),
                "compatible_count": pair_compatible,
                "rejection_counts": counter_to_json(pair_rejections),
            }
        )

    return {
        "center_pair_count": len(records),
        "candidate_count_total": candidate_total,
        "compatible_count_total": compatible_total,
        "compatible_count_distribution": counter_to_json(compatible_counts),
        "compatible_count_by_cyclic_gap": {
            str(gap): counter_to_json(counter)
            for gap, counter in sorted(compatible_by_gap.items())
        },
        "rejection_counts": counter_to_json(rejection_counts),
        "example_rejections": example_rejections,
        "records": records,
    }


def support_compatible_with_assignment(
    order: Sequence[int],
    options: SupportOptions,
    assigned: Mapping[int, int],
    center: int,
    support_index: int,
) -> str | None:
    """Return the first row-pair rejection against an assigned partial state."""

    support = options[center][support_index]
    for other_center in sorted(assigned):
        other_support = options[other_center][assigned[other_center]]
        reason = row_pair_rejection(
            order,
            other_center,
            other_support,
            center,
            support,
        )
        if reason is not None:
            return reason
    return None


def viable_support_indices(
    order: Sequence[int],
    options: SupportOptions,
    assigned: Mapping[int, int],
    center: int,
) -> tuple[list[int], Counter[str]]:
    """Return viable support indices and rejection counts for one center."""

    viable: list[int] = []
    rejections: Counter[str] = Counter()
    for support_index in range(len(options[center])):
        reason = support_compatible_with_assignment(
            order,
            options,
            assigned,
            center,
            support_index,
        )
        if reason is None:
            viable.append(support_index)
        else:
            rejections[reason] += 1
    return viable, rejections


def run_support_search(
    order: Sequence[int],
    options: SupportOptions,
    *,
    max_nodes: int | None = None,
) -> SupportSearchResult:
    """Search for a complete all-five-rich support assignment."""

    n = len(options)
    assigned: dict[int, int] = {}
    center_choice_counts: Counter[int] = Counter()
    node_depth_counts: Counter[int] = Counter()
    evaluation_rejection_counts: Counter[str] = Counter()
    first_dead_end: dict[str, object] | None = None
    nodes_visited = 0
    complete_assignments = 0
    dead_end_count = 0
    max_depth = 0
    aborted = False

    def choose_center() -> tuple[int | None, list[int], Counter[str]]:
        best_center: int | None = None
        best_options: list[int] = []
        best_rejections: Counter[str] = Counter()
        for center in range(n):
            if center in assigned:
                continue
            viable, rejections = viable_support_indices(
                order,
                options,
                assigned,
                center,
            )
            if best_center is None or len(viable) < len(best_options):
                best_center = center
                best_options = viable
                best_rejections = rejections
            if not viable:
                break
        return best_center, best_options, best_rejections

    def search() -> None:
        nonlocal aborted
        nonlocal complete_assignments
        nonlocal dead_end_count
        nonlocal first_dead_end
        nonlocal max_depth
        nonlocal nodes_visited

        depth = len(assigned)
        max_depth = max(max_depth, depth)
        if depth == n:
            complete_assignments += 1
            return
        center, center_options, rejections = choose_center()
        evaluation_rejection_counts.update(rejections)
        if center is None:
            complete_assignments += 1
            return
        if not center_options:
            dead_end_count += 1
            if first_dead_end is None:
                first_dead_end = {
                    "depth": depth,
                    "next_center": center,
                    "assigned_supports": {
                        str(assigned_center): list(
                            options[assigned_center][support_index]
                        )
                        for assigned_center, support_index in sorted(
                            assigned.items()
                        )
                    },
                    "rejection_counts": counter_to_json(rejections),
                }
            return

        center_choice_counts[center] += 1
        node_depth_counts[depth] += len(center_options)
        for support_index in center_options:
            if max_nodes is not None and nodes_visited >= max_nodes:
                aborted = True
                return
            nodes_visited += 1
            assigned[center] = support_index
            search()
            del assigned[center]
            if aborted:
                return

    search()
    return SupportSearchResult(
        nodes_visited=nodes_visited,
        complete_assignments=complete_assignments,
        dead_end_count=dead_end_count,
        max_depth=max_depth,
        aborted=aborted,
        center_choice_counts=dict(sorted(center_choice_counts.items())),
        node_depth_counts=dict(sorted(node_depth_counts.items())),
        evaluation_rejection_counts=dict(sorted(evaluation_rejection_counts.items())),
        first_dead_end=first_dead_end,
    )


def build_summary(
    pair_catalog: Mapping[str, object],
    search: SupportSearchResult,
    options: SupportOptions,
    *,
    max_nodes: int | None,
) -> dict[str, object]:
    """Return the stable summary block for the support obstruction payload."""

    option_counts = [len(center_options) for center_options in options]
    return {
        "n": N,
        "order": list(ORDER),
        "support_size": SUPPORT_SIZE,
        "center_count": len(options),
        "option_counts": option_counts,
        "raw_assignment_upper_bound": prod(option_counts),
        "center_pair_count": pair_catalog["center_pair_count"],
        "center_pair_candidate_count_total": pair_catalog["candidate_count_total"],
        "compatible_center_pair_count_total": pair_catalog["compatible_count_total"],
        "center_pair_compatible_count_distribution": pair_catalog[
            "compatible_count_distribution"
        ],
        "center_pair_rejection_counts": pair_catalog["rejection_counts"],
        "search_nodes_visited": search.nodes_visited,
        "search_complete_assignments": search.complete_assignments,
        "search_dead_end_count": search.dead_end_count,
        "search_max_depth": search.max_depth,
        "search_aborted": search.aborted,
        "search_center_choice_counts": counter_to_json(search.center_choice_counts),
        "search_node_depth_counts": counter_to_json(search.node_depth_counts),
        "no_pair_filter_survivors": (
            search.complete_assignments == 0 and not search.aborted
        ),
        "debug_max_nodes": max_nodes,
    }


def build_payload(*, max_nodes: int | None = None) -> dict[str, object]:
    """Build the generator-independent n=9 all-five-rich payload."""

    options = all_support_options(N, SUPPORT_SIZE)
    pair_catalog = build_pair_catalog(ORDER, options)
    search = run_support_search(ORDER, options, max_nodes=max_nodes)
    summary = build_summary(
        pair_catalog,
        search,
        options,
        max_nodes=max_nodes,
    )
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Generator-independent n=9 all-five-rich support catalogue. It "
            "enumerates every choice of one size-five support at each center "
            "in the natural cyclic order and applies only the two-circle "
            "row-pair cap plus the radical-axis crossing rule for "
            "two-overlaps. The checked catalogue has no complete support "
            "assignment. Repo-locally, this rules out the subcase where every "
            "center has some rich distance class of size at least five, but "
            "it does not handle mixed exact-four/size-five catalogues, does "
            "not prove n=9, does not prove Erdos Problem #97, and is not a "
            "counterexample."
        ),
        "summary": summary,
        "pair_catalog": pair_catalog,
        "search": {
            "nodes_visited": search.nodes_visited,
            "complete_assignments": search.complete_assignments,
            "dead_end_count": search.dead_end_count,
            "max_depth": search.max_depth,
            "aborted": search.aborted,
            "center_choice_counts": counter_to_json(search.center_choice_counts),
            "node_depth_counts": counter_to_json(search.node_depth_counts),
            "evaluation_rejection_counts": counter_to_json(
                search.evaluation_rejection_counts
            ),
            "first_dead_end": search.first_dead_end,
        },
        "support_rule": {
            "support_size": SUPPORT_SIZE,
            "rule": (
                "For each center, enumerate all five-subsets of the other "
                "eight labels. These supports are not generated from stored "
                "selected-row packets."
            ),
            "subcase_reduction": (
                "If a genuine nonagon counterexample had a rich class of "
                "size at least five at every center, choosing any five "
                "witnesses inside each such class would give a complete "
                "support assignment satisfying the checked pair filters."
            ),
        },
        "filters": [
            {
                "name": "row_pair_cap",
                "meaning": (
                    "Two distinct distance circles can share at most two "
                    "witness vertices."
                ),
            },
            {
                "name": "two_overlap_crossing",
                "meaning": (
                    "When two centers share exactly two witnesses in their "
                    "rich classes, the center chord and shared-witness chord "
                    "must cross in the cyclic order."
                ),
            },
        ],
        "interpretation_warnings": [
            "This is a generator-independent size-five support subcase only.",
            "It does not enumerate mixed exact-four and size-five rich catalogues.",
            "It does not use or prove the adaptive radius-blocker bridge.",
            "No general proof and no counterexample are claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_n9_all_five_rich_support_obstruction.py",
            "command": (
                "python scripts/check_n9_all_five_rich_support_obstruction.py "
                "--write --assert-expected"
            ),
            "sources": [
                "src/erdos97/incidence_filters.py",
                "docs/claims.md#radical-axis-crossing--bisection",
            ],
        },
    }


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    """Assert the stable all-five-rich support obstruction counts."""

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
    if summary.get("debug_max_nodes") is not None:
        raise AssertionError("expected payload must not use debug limits")
    pair_catalog = payload.get("pair_catalog")
    if not isinstance(pair_catalog, Mapping):
        raise AssertionError("pair catalog is missing")
    records = pair_catalog.get("records")
    if not isinstance(records, list) or len(records) != EXPECTED_SUMMARY[
        "center_pair_count"
    ]:
        raise AssertionError("unexpected pair-catalog record count")
    search = payload.get("search")
    if not isinstance(search, Mapping):
        raise AssertionError("search record is missing")
    if search.get("first_dead_end") is None:
        raise AssertionError("expected first dead-end certificate")


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=9 all-five-rich support obstruction")
    print(f"claim scope: {payload['claim_scope']}")
    print(f"raw assignments: {summary['raw_assignment_upper_bound']}")
    print(f"search nodes: {summary['search_nodes_visited']}")
    print(f"complete assignments: {summary['search_complete_assignments']}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true", help="write the artifact")
    parser.add_argument("--check", action="store_true", help="compare artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print full JSON")
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=None,
        help="debug/testing node limit; do not use for checked artifacts",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload(max_nodes=args.max_nodes)
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
