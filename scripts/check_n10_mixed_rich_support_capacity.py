#!/usr/bin/env python3
"""Check the n=10 mixed rich-support size-five capacity diagnostic.

This finite support-catalogue diagnostic uses only necessary incidence filters:
row-pair cap, radical-axis crossing for two-overlaps, and witness-pair capacity.
It proves no n=10 theorem, no general theorem about Erdos Problem #97, and
supplies no counterexample.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from math import comb, floor
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]

SCHEMA = "erdos97.n10_mixed_rich_support_capacity.v1"
STATUS = "N10_MIXED_RICH_SUPPORT_CAPACITY_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
DEFAULT_OUT = ROOT / "data" / "certificates" / "n10_mixed_rich_support_capacity.json"
N = 10
ORDER = tuple(range(N))
SEARCH_Q_RANGE = tuple(range(3, 8))
SIZE_FIVE_WITNESS = {
    "0": [1, 2, 3, 7, 9],
    "1": [0, 2, 4, 6, 8],
    "2": [1, 3, 5, 8],
    "3": [2, 4, 5, 9],
    "4": [0, 3, 5, 7],
    "5": [1, 4, 6, 7],
    "6": [2, 5, 7, 8],
    "7": [3, 6, 8, 9],
    "8": [0, 4, 7, 9],
    "9": [0, 1, 5, 6],
}
EXPECTED_Q_SUMMARIES = {
    "3": {
        "representatives_checked": 8,
        "complete_assignments_found": 0,
        "max_depth_reached": 8,
    },
    "4": {
        "representatives_checked": 16,
        "complete_assignments_found": 0,
        "max_depth_reached": 5,
    },
    "5": {
        "representatives_checked": 16,
        "complete_assignments_found": 0,
        "max_depth_reached": 4,
    },
    "6": {
        "representatives_checked": 16,
        "complete_assignments_found": 0,
        "max_depth_reached": 2,
    },
    "7": {
        "representatives_checked": 8,
        "complete_assignments_found": 0,
        "max_depth_reached": 1,
    },
}
EXPECTED_CONSEQUENCES = {
    "pair_budget_max_size_five_centers": 7,
    "searched_min_size_five_centers": 3,
    "searched_max_size_five_centers": 7,
    "q2_witness_support_size_counts": {"4": 8, "5": 2},
    "max_size_five_centers_surviving_filters": 2,
    "min_exact_four_only_centers_in_any_counterexample_candidate": 8,
}

Support = tuple[int, ...]
Assignment = dict[int, Support]


def normalized_pair(left: int, right: int) -> tuple[int, int]:
    """Return a normalized non-loop pair."""

    if left == right:
        raise ValueError("loop pair")
    return (left, right) if left < right else (right, left)


def support_mask(support: Sequence[int]) -> int:
    """Return the bitmask of a support."""

    out = 0
    for label in support:
        out |= 1 << int(label)
    return out


def iter_bits(mask: int):
    """Yield set-bit indices of a nonnegative integer bitset."""

    while mask:
        low_bit = mask & -mask
        yield low_bit.bit_length() - 1
        mask ^= low_bit


def chords_cross_in_natural_order(
    first: tuple[int, int],
    second: tuple[int, int],
) -> bool:
    """Return whether two disjoint chords cross in the natural cyclic order."""

    if set(first) & set(second):
        return False
    a, b = normalized_pair(*first)
    c, d = normalized_pair(*second)
    c_inside = a < c < b
    d_inside = a < d < b
    return c_inside != d_inside


def canonical_center_subset(subset: Sequence[int], n: int = N) -> tuple[int, ...]:
    """Return the dihedral canonical representative of a center subset."""

    raw = set(subset)
    variants: list[tuple[int, ...]] = []
    for shift in range(n):
        variants.append(tuple(sorted((label + shift) % n for label in raw)))
        variants.append(tuple(sorted((shift - label) % n for label in raw)))
    return min(variants)


def dihedral_representatives(q: int, n: int = N) -> tuple[tuple[int, ...], ...]:
    """Return dihedral representatives of q-subsets of centers."""

    representatives = {
        canonical_center_subset(subset, n)
        for subset in combinations(range(n), q)
    }
    return tuple(sorted(representatives))


def pair_budget_max_size_five_centers(n: int = N) -> int:
    """Return the pair-budget maximum q in a four/five support catalogue."""

    base_load = n * comb(4, 2)
    capacity = 2 * comb(n, 2)
    if base_load > capacity:
        return -1
    return min(n, floor((capacity - base_load) / (comb(5, 2) - comb(4, 2))))


@dataclass(frozen=True)
class PreparedCatalogue:
    options: Mapping[tuple[int, int], tuple[Support, ...]]
    masks: Mapping[tuple[int, int], tuple[int, ...]]
    pair_ids: Mapping[tuple[int, int], tuple[tuple[int, ...], ...]]
    pair_option_bits: Mapping[tuple[int, int], tuple[int, ...]]
    compatible_option_bits: Mapping[tuple[int, int, int, int], tuple[int, ...]]
    full_domain: Mapping[tuple[int, int], int]
    pair_count: int


def prepare_catalogue(n: int = N) -> PreparedCatalogue:
    """Precompute support options and compatibility bitsets."""

    pair_index = {
        pair: index for index, pair in enumerate(combinations(range(n), 2))
    }
    options: dict[tuple[int, int], tuple[Support, ...]] = {}
    masks: dict[tuple[int, int], tuple[int, ...]] = {}
    pair_ids: dict[tuple[int, int], tuple[tuple[int, ...], ...]] = {}
    pair_option_bits: dict[tuple[int, int], tuple[int, ...]] = {}
    full_domain: dict[tuple[int, int], int] = {}

    for center in range(n):
        labels = tuple(label for label in range(n) if label != center)
        for support_size in (4, 5):
            rows = tuple(tuple(row) for row in combinations(labels, support_size))
            options[(center, support_size)] = rows
            masks[(center, support_size)] = tuple(support_mask(row) for row in rows)
            row_pair_ids = tuple(
                tuple(
                    pair_index[normalized_pair(left, right)]
                    for left, right in combinations(row, 2)
                )
                for row in rows
            )
            pair_ids[(center, support_size)] = row_pair_ids
            full_domain[(center, support_size)] = (1 << len(rows)) - 1

            option_bits = [0] * len(pair_index)
            for row_index, row_pair_id in enumerate(row_pair_ids):
                bit = 1 << row_index
                for pair_id in row_pair_id:
                    option_bits[pair_id] |= bit
            pair_option_bits[(center, support_size)] = tuple(option_bits)

    compatible_option_bits: dict[tuple[int, int, int, int], tuple[int, ...]] = {}
    for left, right in combinations(range(n), 2):
        for left_size in (4, 5):
            for right_size in (4, 5):
                left_to_right: list[int] = []
                right_to_left = [0] * len(options[(right, right_size)])
                for left_index, left_mask in enumerate(masks[(left, left_size)]):
                    bits = 0
                    right_masks = masks[(right, right_size)]
                    for right_index, right_mask in enumerate(right_masks):
                        intersection_mask = left_mask & right_mask
                        intersection_size = intersection_mask.bit_count()
                        compatible = True
                        if intersection_size > 2:
                            compatible = False
                        elif intersection_size == 2:
                            shared = [
                                label
                                for label in range(n)
                                if (intersection_mask >> label) & 1
                            ]
                            compatible = chords_cross_in_natural_order(
                                (left, right),
                                (shared[0], shared[1]),
                            )
                        if compatible:
                            bits |= 1 << right_index
                            right_to_left[right_index] |= 1 << left_index
                    left_to_right.append(bits)
                compatible_option_bits[(left, left_size, right, right_size)] = tuple(
                    left_to_right
                )
                compatible_option_bits[(right, right_size, left, left_size)] = tuple(
                    right_to_left
                )

    return PreparedCatalogue(
        options=options,
        masks=masks,
        pair_ids=pair_ids,
        pair_option_bits=pair_option_bits,
        compatible_option_bits=compatible_option_bits,
        full_domain=full_domain,
        pair_count=len(pair_index),
    )


@dataclass(frozen=True)
class SearchResult:
    found: bool
    nodes_visited: int
    dead_end_count: int
    max_depth: int
    aborted: bool
    first_assignment: Assignment | None


def search_size_five_subset(
    catalogue: PreparedCatalogue,
    size_five_centers: Sequence[int],
    *,
    max_nodes: int | None = None,
) -> SearchResult:
    """Search one fixed set of size-five centers."""

    size_five_set = set(size_five_centers)
    support_sizes = tuple(5 if center in size_five_set else 4 for center in range(N))
    domains = tuple(
        catalogue.full_domain[(center, support_sizes[center])] for center in range(N)
    )
    pair_counts = [0] * catalogue.pair_count
    assigned: list[int | None] = [None] * N
    nodes_visited = 0
    dead_end_count = 0
    max_depth = 0
    aborted = False
    first_assignment: Assignment | None = None

    def recurse(
        depth: int,
        assigned_mask: int,
        current_domains: tuple[int, ...],
    ) -> bool:
        nonlocal aborted
        nonlocal dead_end_count
        nonlocal first_assignment
        nonlocal max_depth
        nonlocal nodes_visited

        if max_nodes is not None and nodes_visited >= max_nodes:
            aborted = True
            return True
        max_depth = max(max_depth, depth)
        if depth == N:
            first_assignment = {
                center: catalogue.options[(center, support_sizes[center])][
                    assigned_index
                ]
                for center, assigned_index in enumerate(assigned)
                if assigned_index is not None
            }
            return True

        best_center: int | None = None
        best_count: int | None = None
        for center in range(N):
            if (assigned_mask >> center) & 1:
                continue
            option_count = current_domains[center].bit_count()
            if best_count is None or option_count < best_count:
                best_center = center
                best_count = option_count
            if option_count == 0:
                break

        if best_center is None:
            return True
        if best_count == 0:
            dead_end_count += 1
            return False

        center = best_center
        center_size = support_sizes[center]
        for option_index in iter_bits(current_domains[center]):
            nodes_visited += 1
            newly_saturated: list[int] = []
            for pair_id in catalogue.pair_ids[(center, center_size)][option_index]:
                old_count = pair_counts[pair_id]
                if old_count >= 2:
                    raise AssertionError("domain allowed an already saturated pair")
                pair_counts[pair_id] = old_count + 1
                if old_count + 1 == 2:
                    newly_saturated.append(pair_id)

            new_domains = list(current_domains)
            new_domains[center] = 1 << option_index
            new_assigned_mask = assigned_mask | (1 << center)
            empty_domain = False
            for other_center in range(N):
                if (new_assigned_mask >> other_center) & 1:
                    continue
                other_size = support_sizes[other_center]
                domain = new_domains[other_center]
                domain &= catalogue.compatible_option_bits[
                    (center, center_size, other_center, other_size)
                ][option_index]
                if newly_saturated:
                    pair_bits = catalogue.pair_option_bits[(other_center, other_size)]
                    for pair_id in newly_saturated:
                        domain &= ~pair_bits[pair_id]
                new_domains[other_center] = domain
                if domain == 0:
                    empty_domain = True
                    break

            assigned[center] = option_index
            if empty_domain:
                dead_end_count += 1
                found = False
            else:
                found = recurse(depth + 1, new_assigned_mask, tuple(new_domains))
            assigned[center] = None
            for pair_id in catalogue.pair_ids[(center, center_size)][option_index]:
                pair_counts[pair_id] -= 1
            if found:
                return True
        return False

    found = recurse(0, 0, domains)
    return SearchResult(
        found=bool(found and first_assignment is not None),
        nodes_visited=nodes_visited,
        dead_end_count=dead_end_count,
        max_depth=max_depth,
        aborted=aborted,
        first_assignment=first_assignment,
    )


def assignment_is_valid(assignment: Mapping[int, Sequence[int]], n: int = N) -> bool:
    """Check the three necessary filters directly for a full assignment."""

    rows = {int(center): tuple(row) for center, row in assignment.items()}
    if set(rows) != set(range(n)):
        return False
    pair_counts: Counter[tuple[int, int]] = Counter()
    masks = {center: support_mask(row) for center, row in rows.items()}
    for center, row in rows.items():
        if (
            len(row) not in (4, 5)
            or center in row
            or len(set(row)) != len(row)
            or any(label < 0 or label >= n for label in row)
        ):
            return False
        for left, right in combinations(row, 2):
            pair_counts[normalized_pair(left, right)] += 1
            if pair_counts[normalized_pair(left, right)] > 2:
                return False
    for left, right in combinations(range(n), 2):
        intersection_mask = masks[left] & masks[right]
        intersection_size = intersection_mask.bit_count()
        if intersection_size > 2:
            return False
        if intersection_size == 2:
            shared = [label for label in range(n) if (intersection_mask >> label) & 1]
            if not chords_cross_in_natural_order((left, right), (shared[0], shared[1])):
                return False
    return True


def assignment_to_json(assignment: Mapping[int, Sequence[int]]) -> dict[str, list[int]]:
    """Return a stable JSON object for an assignment."""

    return {str(center): list(assignment[center]) for center in sorted(assignment)}


def support_size_counts(assignment: Mapping[int, Sequence[int]]) -> dict[str, int]:
    """Return support-size counts for a full assignment."""

    counts = Counter(len(row) for row in assignment.values())
    return {str(size): counts[size] for size in sorted(counts)}


def run_capacity_check(*, max_nodes: int | None = None) -> dict[str, object]:
    """Run the q=3..7 no-survivor searches and return summary records."""

    catalogue = prepare_catalogue(N)
    q_summaries: dict[str, object] = {}
    raw_counts: dict[str, int] = {}
    for q in SEARCH_Q_RANGE:
        representatives = dihedral_representatives(q, N)
        raw_counts[str(q)] = comb(N, q)
        total_nodes = 0
        total_dead_ends = 0
        max_depth = 0
        complete_assignments_found = 0
        aborted_count = 0
        worst: dict[str, object] | None = None
        for representative in representatives:
            result = search_size_five_subset(
                catalogue,
                representative,
                max_nodes=max_nodes,
            )
            total_nodes += result.nodes_visited
            total_dead_ends += result.dead_end_count
            max_depth = max(max_depth, result.max_depth)
            if result.aborted:
                aborted_count += 1
            if result.found:
                complete_assignments_found += 1
            if worst is None or result.nodes_visited > worst["nodes_visited"]:
                worst = {
                    "size_five_centers": list(representative),
                    "nodes_visited": result.nodes_visited,
                    "dead_end_count": result.dead_end_count,
                    "max_depth": result.max_depth,
                    "found": result.found,
                    "aborted": result.aborted,
                }
        q_summaries[str(q)] = {
            "raw_center_subset_count": raw_counts[str(q)],
            "representatives_checked": len(representatives),
            "complete_assignments_found": complete_assignments_found,
            "aborted_count": aborted_count,
            "total_nodes_visited": total_nodes,
            "total_dead_end_count": total_dead_ends,
            "max_depth_reached": max_depth,
            "worst_representative": worst,
        }

    witness = {int(center): tuple(row) for center, row in SIZE_FIVE_WITNESS.items()}
    if not assignment_is_valid(witness, N):
        raise AssertionError("stored q=2 witness failed direct validation")
    witness_size_counts = support_size_counts(witness)
    if witness_size_counts != {"4": 8, "5": 2}:
        raise AssertionError(
            f"stored witness has support-size counts {witness_size_counts!r}"
        )

    return {
        "q_summaries": q_summaries,
        "raw_center_subset_counts": raw_counts,
        "q2_witness": assignment_to_json(witness),
        "q2_witness_support_size_counts": witness_size_counts,
    }


def build_payload(*, max_nodes: int | None = None) -> dict[str, object]:
    """Build the n=10 mixed rich-support capacity payload."""

    capacity = run_capacity_check(max_nodes=max_nodes)
    q_summaries = capacity["q_summaries"]
    assert isinstance(q_summaries, Mapping)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Generator-independent n=10 four/five support-capacity diagnostic. "
            "It checks all dihedral center-set representatives with q=3..7 "
            "size-five supports and finds no full assignments under the "
            "row-pair cap, two-overlap crossing rule, and witness-pair capacity. "
            "A direct q=2 witness shows the bound is sharp for these filters. "
            "This does not prove n=10, does not prove Erdos Problem #97, and "
            "is not a counterexample."
        ),
        "summary": {
            "n": N,
            "order": list(ORDER),
            "support_sizes": [4, 5],
            "searched_size_five_center_counts": list(SEARCH_Q_RANGE),
            "searched_min_size_five_centers": min(SEARCH_Q_RANGE),
            "searched_max_size_five_centers": max(SEARCH_Q_RANGE),
            "pair_budget_max_size_five_centers": pair_budget_max_size_five_centers(N),
            "q_summaries": q_summaries,
            "q2_witness_valid": True,
            "q2_witness_support_size_counts": capacity[
                "q2_witness_support_size_counts"
            ],
            "max_size_five_centers_surviving_filters": 2,
            "min_exact_four_only_centers_in_any_counterexample_candidate": 8,
            "debug_max_nodes": max_nodes,
        },
        "q2_witness": capacity["q2_witness"],
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
        "support_rule": {
            "rule": (
                "A center with a rich class of size at least five is "
                "represented by an arbitrary five-witness sub-support; "
                "every other bad center is represented by an exact "
                "four-witness support."
            ),
            "dihedral_reduction": (
                "The natural cyclic order fixes labels 0..9. The set of "
                "centers represented by size-five supports is reduced by "
                "cyclic rotations and reflection; the support choices "
                "themselves are still labelled and searched for each "
                "representative."
            ),
        },
        "interpretation_warnings": [
            "This is a necessary support-catalogue diagnostic only.",
            (
                "It does not replay vertex-circle, Kalmanson, or Euclidean "
                "realizability filters."
            ),
            (
                "It leaves the q=0, q=1, and q=2 four/five support cases "
                "open to stronger filters."
            ),
            "No n=10 theorem, general proof, or counterexample is claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_n10_mixed_rich_support_capacity.py",
            "command": (
                "python scripts/check_n10_mixed_rich_support_capacity.py "
                "--write --assert-expected"
            ),
            "sources": [
                "docs/claims.md#n9-mixed-rich-support-reduction",
                (
                    "docs/review-priorities.md#priority-6b---audit-the-"
                    "n10-singleton-slice-draft"
                ),
                "docs/codex-backlog.md#recommended-next-technical-prs",
            ],
        },
    }


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    """Assert stable expected n=10 capacity counts."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"unexpected status: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"unexpected trust: {payload.get('trust')!r}")
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("summary is missing")
    if summary.get("debug_max_nodes") is not None:
        raise AssertionError("expected payload must not use debug node limits")
    for key, expected in EXPECTED_CONSEQUENCES.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary[{key!r}] is {summary.get(key)!r}, expected {expected!r}"
            )
    q_summaries = summary.get("q_summaries")
    if not isinstance(q_summaries, Mapping):
        raise AssertionError("q_summaries is missing")
    for q, expected_items in EXPECTED_Q_SUMMARIES.items():
        q_summary = q_summaries.get(q)
        if not isinstance(q_summary, Mapping):
            raise AssertionError(f"missing q={q} summary")
        for key, expected in expected_items.items():
            if q_summary.get(key) != expected:
                raise AssertionError(
                    f"q={q} key {key!r} is {q_summary.get(key)!r}, "
                    f"expected {expected!r}"
                )
        if q_summary.get("aborted_count") != 0:
            raise AssertionError(f"q={q} unexpectedly aborted")
    if payload.get("q2_witness") != assignment_to_json(
        {int(center): tuple(row) for center, row in SIZE_FIVE_WITNESS.items()}
    ):
        raise AssertionError("unexpected q=2 witness")


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    """Compare a checked artifact with a freshly built payload."""

    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    """Print a compact human-readable summary."""

    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=10 mixed rich-support capacity diagnostic")
    print(f"claim scope: {payload['claim_scope']}")
    print(
        "max size-five centers surviving these filters: "
        f"{summary['max_size_five_centers_surviving_filters']}"
    )
    print(
        "minimum exact-four-only centers in any candidate: "
        f"{summary['min_exact_four_only_centers_in_any_counterexample_candidate']}"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true", help="write the artifact")
    parser.add_argument("--check", action="store_true", help="compare the artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print full JSON")
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=None,
        help=(
            "debug/testing node limit per center-set representative; "
            "do not use for checked artifacts"
        ),
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
