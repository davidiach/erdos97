#!/usr/bin/env python3
"""Check the generator-independent n=9 mixed rich-support reduction.

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

SCHEMA = "erdos97.n9_mixed_rich_support_reduction.v1"
STATUS = "N9_MIXED_RICH_SUPPORT_REDUCTION_ONLY"
DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_mixed_rich_support_reduction.json"
N = 9
ORDER = tuple(range(N))
SUPPORT_SIZES = (4, 5)
REJECTION_NAMES = {
    1: "row_pair_cap",
    2: "two_overlap_crossing",
    3: "witness_pair_capacity",
}
EXPECTED_SUMMARY = {
    "n": 9,
    "order": list(range(9)),
    "support_sizes": [4, 5],
    "center_count": 9,
    "option_counts": [126, 126, 126, 126, 126, 126, 126, 126, 126],
    "option_size_counts": {"4": 70, "5": 56},
    "raw_assignment_upper_bound": 8004512848309157376,
    "center_pair_count": 36,
    "center_pair_candidate_count_total": 571536,
    "compatible_center_pair_count_total": 206640,
    "center_pair_compatible_count_distribution": {
        "3360": 9,
        "5400": 9,
        "6760": 9,
        "7440": 9,
    },
    "center_pair_rejection_counts": {
        "row_pair_cap": 193536,
        "two_overlap_crossing": 171360,
    },
    "search_nodes_visited": 108018,
    "search_complete_assignments": 184,
    "search_dead_end_count": 58791,
    "search_max_depth": 9,
    "search_aborted": False,
    "terminal_size_five_support_count_distribution": {"0": 184},
    "complete_assignments_with_size_five_supports": 0,
    "all_complete_assignments_exact_four_only": True,
    "search_center_choice_counts": {
        "0": 1,
        "1": 892,
        "2": 3979,
        "3": 8892,
        "4": 11200,
        "5": 8868,
        "6": 6538,
        "7": 4590,
        "8": 4084,
    },
    "search_node_depth_counts": {
        "0": 126,
        "1": 2520,
        "2": 11327,
        "3": 28368,
        "4": 33043,
        "5": 21158,
        "6": 9088,
        "7": 2204,
        "8": 184,
    },
}

Support = tuple[int, ...]
SupportOptions = tuple[tuple[Support, ...], ...]
ReasonMatrix = dict[tuple[int, int], tuple[tuple[int, ...], ...]]


@dataclass(frozen=True)
class PreparedSupportCatalogue:
    options: SupportOptions
    masks: tuple[tuple[int, ...], ...]
    support_sizes: tuple[tuple[int, ...], ...]
    pair_ids: tuple[tuple[tuple[int, ...], ...], ...]
    reason_matrix: ReasonMatrix
    pair_catalog: Mapping[str, object]


@dataclass(frozen=True)
class MixedSupportSearchResult:
    nodes_visited: int
    complete_assignments: int
    dead_end_count: int
    max_depth: int
    aborted: bool
    terminal_size_five_support_count_distribution: Mapping[int, int]
    center_choice_counts: Mapping[int, int]
    node_depth_counts: Mapping[int, int]
    evaluation_rejection_counts: Mapping[str, int]
    first_dead_end: Mapping[str, object] | None
    first_complete_assignment: Mapping[str, object] | None


def counter_to_json(counter: Mapping[object, int]) -> dict[str, int]:
    """Return a stable JSON object for a small counter."""

    return {
        str(key): int(counter[key])
        for key in sorted(counter, key=lambda item: str(item))
    }


def support_options_for_center(
    n: int,
    center: int,
    support_sizes: Sequence[int] = SUPPORT_SIZES,
) -> tuple[Support, ...]:
    """Return all labelled supports of the allowed sizes avoiding ``center``."""

    if center < 0 or center >= n:
        raise ValueError(f"center out of range: {center}")
    rows: list[Support] = []
    labels = tuple(label for label in range(n) if label != center)
    for support_size in support_sizes:
        if support_size <= 0 or support_size > len(labels):
            raise ValueError(f"invalid support size {support_size} for n={n}")
        rows.extend(tuple(row) for row in combinations(labels, support_size))
    return tuple(rows)


def all_support_options(
    n: int = N,
    support_sizes: Sequence[int] = SUPPORT_SIZES,
) -> SupportOptions:
    """Return the generator-independent mixed support catalogue."""

    return tuple(
        support_options_for_center(n, center, support_sizes)
        for center in range(n)
    )


def support_mask(support: Sequence[int]) -> int:
    """Return the bitmask of a support."""

    out = 0
    for label in support:
        out |= 1 << int(label)
    return out


def normalized_pair(left: int, right: int) -> tuple[int, int]:
    """Return a normalized non-loop pair."""

    if left == right:
        raise ValueError("loop pair")
    return (left, right) if left < right else (right, left)


def pair_indices(n: int) -> dict[tuple[int, int], int]:
    """Return deterministic pair indices for witness-pair capacity counts."""

    return {pair: index for index, pair in enumerate(combinations(range(n), 2))}


def support_pair_ids(
    pair_index: Mapping[tuple[int, int], int],
    support: Sequence[int],
) -> tuple[int, ...]:
    """Return indexed unordered pairs contained in one support."""

    return tuple(
        pair_index[normalized_pair(left, right)]
        for left, right in combinations(support, 2)
    )


def row_pair_rejection_code(
    order: Sequence[int],
    left_center: int,
    left_mask: int,
    right_center: int,
    right_mask: int,
) -> int:
    """Return the row-pair rejection code for two support masks."""

    if left_center == right_center:
        raise ValueError("row-pair rejection requires distinct centers")
    if right_center < left_center:
        return row_pair_rejection_code(
            order,
            right_center,
            right_mask,
            left_center,
            left_mask,
        )
    intersection_mask = left_mask & right_mask
    intersection_size = intersection_mask.bit_count()
    if intersection_size > 2:
        return 1
    if intersection_size == 2:
        intersection = [
            label for label in range(len(order)) if (intersection_mask >> label) & 1
        ]
        source = normalize_chord(left_center, right_center)
        target = normalize_chord(intersection[0], intersection[1])
        if not chords_cross_in_order(source, target, order):
            return 2
    return 0


def build_reason_matrix_and_pair_catalog(
    order: Sequence[int],
    options: SupportOptions,
    masks: Sequence[Sequence[int]],
) -> tuple[ReasonMatrix, dict[str, object]]:
    """Precompute row-pair rejection reasons and pair-catalogue counts."""

    n = len(options)
    reason_matrix: ReasonMatrix = {}
    compatible_counts: Counter[int] = Counter()
    compatible_by_gap: dict[int, Counter[int]] = {}
    rejection_counts: Counter[str] = Counter()
    records: list[dict[str, object]] = []
    candidate_total = 0
    compatible_total = 0
    example_rejections: dict[str, dict[str, object]] = {}

    for left, right in combinations(range(n), 2):
        matrix_rows: list[tuple[int, ...]] = []
        compatible_count = 0
        pair_rejections: Counter[str] = Counter()
        for left_index, left_mask in enumerate(masks[left]):
            row_codes: list[int] = []
            for right_index, right_mask in enumerate(masks[right]):
                candidate_total += 1
                code = row_pair_rejection_code(
                    order,
                    left,
                    left_mask,
                    right,
                    right_mask,
                )
                if code == 0:
                    compatible_count += 1
                else:
                    reason = REJECTION_NAMES[code]
                    rejection_counts[reason] += 1
                    pair_rejections[reason] += 1
                    if reason not in example_rejections:
                        intersection = sorted(
                            set(options[left][left_index])
                            & set(options[right][right_index])
                        )
                        example_rejections[reason] = {
                            "centers": [left, right],
                            "left_support": list(options[left][left_index]),
                            "right_support": list(options[right][right_index]),
                            "intersection": intersection,
                        }
                row_codes.append(code)
            matrix_rows.append(tuple(row_codes))
        reason_matrix[(left, right)] = tuple(matrix_rows)
        gap = min((right - left) % n, (left - right) % n)
        compatible_counts[compatible_count] += 1
        compatible_by_gap.setdefault(gap, Counter())[compatible_count] += 1
        compatible_total += compatible_count
        records.append(
            {
                "centers": [left, right],
                "cyclic_gap": gap,
                "candidate_count": len(options[left]) * len(options[right]),
                "compatible_count": compatible_count,
                "rejection_counts": counter_to_json(pair_rejections),
            }
        )

    return reason_matrix, {
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


def prepare_support_catalogue(
    n: int = N,
    order: Sequence[int] = ORDER,
) -> PreparedSupportCatalogue:
    """Prepare mixed support options and row-pair compatibility tables."""

    options = all_support_options(n, SUPPORT_SIZES)
    masks = tuple(tuple(support_mask(row) for row in rows) for rows in options)
    sizes = tuple(tuple(len(row) for row in rows) for rows in options)
    pair_index = pair_indices(n)
    pair_ids = tuple(
        tuple(support_pair_ids(pair_index, row) for row in rows)
        for rows in options
    )
    reason_matrix, pair_catalog = build_reason_matrix_and_pair_catalog(
        order,
        options,
        masks,
    )
    return PreparedSupportCatalogue(
        options=options,
        masks=masks,
        support_sizes=sizes,
        pair_ids=pair_ids,
        reason_matrix=reason_matrix,
        pair_catalog=pair_catalog,
    )


def support_rejection_against_assignment(
    catalogue: PreparedSupportCatalogue,
    assigned: Mapping[int, int],
    pair_counts: Sequence[int],
    center: int,
    support_index: int,
) -> int:
    """Return the first rejection code for adding one support."""

    for pair_id in catalogue.pair_ids[center][support_index]:
        if pair_counts[pair_id] >= 2:
            return 3
    for other_center, other_index in sorted(assigned.items()):
        left, right = (
            (other_center, center)
            if other_center < center
            else (center, other_center)
        )
        left_index, right_index = (
            (other_index, support_index)
            if other_center < center
            else (support_index, other_index)
        )
        code = catalogue.reason_matrix[(left, right)][left_index][right_index]
        if code:
            return code
    return 0


def viable_support_indices(
    catalogue: PreparedSupportCatalogue,
    assigned: Mapping[int, int],
    pair_counts: Sequence[int],
    center: int,
) -> tuple[list[int], Counter[str]]:
    """Return viable support indices and rejection counts for one center."""

    viable: list[int] = []
    rejections: Counter[str] = Counter()
    for support_index in range(len(catalogue.options[center])):
        code = support_rejection_against_assignment(
            catalogue,
            assigned,
            pair_counts,
            center,
            support_index,
        )
        if code == 0:
            viable.append(support_index)
        else:
            rejections[REJECTION_NAMES[code]] += 1
    return viable, rejections


def run_mixed_support_search(
    catalogue: PreparedSupportCatalogue,
    *,
    max_nodes: int | None = None,
) -> MixedSupportSearchResult:
    """Search for complete mixed support assignments."""

    n = len(catalogue.options)
    assigned: dict[int, int] = {}
    pair_counts = [0] * len(pair_indices(n))
    center_choice_counts: Counter[int] = Counter()
    node_depth_counts: Counter[int] = Counter()
    evaluation_rejection_counts: Counter[str] = Counter()
    terminal_size_five_counts: Counter[int] = Counter()
    first_dead_end: dict[str, object] | None = None
    first_complete_assignment: dict[str, object] | None = None
    nodes_visited = 0
    complete_assignments = 0
    dead_end_count = 0
    max_depth = 0
    aborted = False

    def add_support(center: int, support_index: int) -> None:
        for pair_id in catalogue.pair_ids[center][support_index]:
            pair_counts[pair_id] += 1

    def remove_support(center: int, support_index: int) -> None:
        for pair_id in catalogue.pair_ids[center][support_index]:
            pair_counts[pair_id] -= 1

    def assignment_supports() -> dict[str, list[int]]:
        return {
            str(center): list(catalogue.options[center][support_index])
            for center, support_index in sorted(assigned.items())
        }

    def terminal_size_five_count() -> int:
        return sum(
            1
            for center, support_index in assigned.items()
            if catalogue.support_sizes[center][support_index] == 5
        )

    def choose_center() -> tuple[int | None, list[int], Counter[str]]:
        best_center: int | None = None
        best_options: list[int] = []
        best_rejections: Counter[str] = Counter()
        for center in range(n):
            if center in assigned:
                continue
            viable, rejections = viable_support_indices(
                catalogue,
                assigned,
                pair_counts,
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
        nonlocal first_complete_assignment
        nonlocal first_dead_end
        nonlocal max_depth
        nonlocal nodes_visited

        depth = len(assigned)
        max_depth = max(max_depth, depth)
        if depth == n:
            complete_assignments += 1
            size_five_count = terminal_size_five_count()
            terminal_size_five_counts[size_five_count] += 1
            if first_complete_assignment is None:
                first_complete_assignment = {
                    "size_five_support_count": size_five_count,
                    "assigned_supports": assignment_supports(),
                }
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
                    "assigned_supports": assignment_supports(),
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
            add_support(center, support_index)
            search()
            remove_support(center, support_index)
            del assigned[center]
            if aborted:
                return

    search()
    return MixedSupportSearchResult(
        nodes_visited=nodes_visited,
        complete_assignments=complete_assignments,
        dead_end_count=dead_end_count,
        max_depth=max_depth,
        aborted=aborted,
        terminal_size_five_support_count_distribution=dict(
            sorted(terminal_size_five_counts.items())
        ),
        center_choice_counts=dict(sorted(center_choice_counts.items())),
        node_depth_counts=dict(sorted(node_depth_counts.items())),
        evaluation_rejection_counts=dict(sorted(evaluation_rejection_counts.items())),
        first_dead_end=first_dead_end,
        first_complete_assignment=first_complete_assignment,
    )


def option_size_counts(catalogue: PreparedSupportCatalogue) -> dict[str, int]:
    """Return support-size counts for one center catalogue."""

    counts = Counter(catalogue.support_sizes[0])
    return counter_to_json(counts)


def build_summary(
    catalogue: PreparedSupportCatalogue,
    search: MixedSupportSearchResult,
    *,
    max_nodes: int | None,
) -> dict[str, object]:
    """Return the stable summary block for the mixed-support payload."""

    option_counts = [len(center_options) for center_options in catalogue.options]
    terminal_distribution = counter_to_json(
        search.terminal_size_five_support_count_distribution
    )
    size_five_terminals = sum(
        count
        for raw_size_five_count, count in (
            (int(key), value) for key, value in terminal_distribution.items()
        )
        if raw_size_five_count > 0
    )
    pair_catalog = catalogue.pair_catalog
    return {
        "n": N,
        "order": list(ORDER),
        "support_sizes": list(SUPPORT_SIZES),
        "center_count": len(catalogue.options),
        "option_counts": option_counts,
        "option_size_counts": option_size_counts(catalogue),
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
        "terminal_size_five_support_count_distribution": terminal_distribution,
        "complete_assignments_with_size_five_supports": size_five_terminals,
        "all_complete_assignments_exact_four_only": (
            search.complete_assignments > 0
            and size_five_terminals == 0
            and not search.aborted
        ),
        "search_center_choice_counts": counter_to_json(search.center_choice_counts),
        "search_node_depth_counts": counter_to_json(search.node_depth_counts),
        "debug_max_nodes": max_nodes,
    }


def build_payload(*, max_nodes: int | None = None) -> dict[str, object]:
    """Build the generator-independent mixed rich-support payload."""

    catalogue = prepare_support_catalogue(N, ORDER)
    search = run_mixed_support_search(catalogue, max_nodes=max_nodes)
    summary = build_summary(catalogue, search, max_nodes=max_nodes)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Generator-independent n=9 mixed rich-support catalogue. It "
            "enumerates four- and five-witness supports at every center, "
            "applies the two-circle row-pair cap, radical-axis crossing for "
            "two-overlaps, and witness-pair capacity, and finds that every "
            "complete assignment is all-exact-four. Repo-locally, this rules "
            "out any size-at-least-five rich class in an n=9 selected-witness "
            "counterexample, but it does not independently prove the "
            "exact-four vertex-circle exhaustive checker, does not prove n=9, "
            "does not prove Erdos Problem #97, and is not a counterexample."
        ),
        "summary": summary,
        "pair_catalog": catalogue.pair_catalog,
        "search": {
            "nodes_visited": search.nodes_visited,
            "complete_assignments": search.complete_assignments,
            "dead_end_count": search.dead_end_count,
            "max_depth": search.max_depth,
            "aborted": search.aborted,
            "terminal_size_five_support_count_distribution": counter_to_json(
                search.terminal_size_five_support_count_distribution
            ),
            "center_choice_counts": counter_to_json(search.center_choice_counts),
            "node_depth_counts": counter_to_json(search.node_depth_counts),
            "evaluation_rejection_counts": counter_to_json(
                search.evaluation_rejection_counts
            ),
            "first_dead_end": search.first_dead_end,
            "first_complete_assignment": search.first_complete_assignment,
        },
        "support_rule": {
            "support_sizes": list(SUPPORT_SIZES),
            "rule": (
                "For each center, enumerate every four- or five-subset of the "
                "other eight labels. A rich class of size at least five is "
                "represented by an arbitrary five-witness support inside it; "
                "an exact-four rich class is represented by its four labels."
            ),
            "subcase_reduction": (
                "If a genuine nonagon counterexample had any rich class of "
                "size at least five, choosing five witnesses inside that class "
                "and choosing one rich class at every other center would give "
                "a complete mixed support assignment with at least one "
                "size-five support satisfying these necessary filters."
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
            {
                "name": "witness_pair_capacity",
                "meaning": (
                    "Any unordered witness pair can occur together in rich "
                    "classes at at most two centers, since all such centers "
                    "lie on one perpendicular-bisector line."
                ),
            },
        ],
        "interpretation_warnings": [
            "This is a generator-independent four/five support subcase only.",
            "It reduces n=9 support catalogues to exact-four choices before vertex-circle replay.",
            "It does not independently audit the review-pending exact-four n=9 exhaustive checker.",
            "No general proof and no counterexample are claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_n9_mixed_rich_support_reduction.py",
            "command": (
                "python scripts/check_n9_mixed_rich_support_reduction.py "
                "--write --assert-expected"
            ),
            "sources": [
                "src/erdos97/incidence_filters.py",
                "docs/claims.md#circle-intersection-cap",
                "docs/claims.md#radical-axis-crossing--bisection",
                "docs/claims.md#pair-and-triple-sharing",
                "data/certificates/n9_all_five_rich_support_obstruction.json",
            ],
        },
    }


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    """Assert the stable mixed support reduction counts."""

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
    search = payload.get("search")
    if not isinstance(search, Mapping):
        raise AssertionError("search record is missing")
    if search.get("first_complete_assignment") is None:
        raise AssertionError("expected first complete assignment")
    if search.get("first_dead_end") is None:
        raise AssertionError("expected first dead-end record")


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=9 mixed rich-support reduction")
    print(f"claim scope: {payload['claim_scope']}")
    print(f"raw assignments: {summary['raw_assignment_upper_bound']}")
    print(f"complete assignments: {summary['search_complete_assignments']}")
    print(
        "complete assignments with size-five supports: "
        f"{summary['complete_assignments_with_size_five_supports']}"
    )


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
