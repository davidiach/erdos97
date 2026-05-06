#!/usr/bin/env python3
"""Refine the sampled C19 prefix-pilot frontier by one fourth boundary pair.

This script starts from the 28 unclosed sampled three-boundary-prefix branches
recorded by pilot_c19_kalmanson_prefix_branches.py.  It appends one additional
ordered left/right boundary pair to each parent and checks the resulting
children with prefix-forced Kalmanson/Farkas certificates.

The output is a bounded sampled-frontier refinement, not an all-order C19
search.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Mapping

from pilot_c19_kalmanson_prefix_branches import (
    DEFAULT_MAX_BRANCHES,
    N,
    OFFSETS,
    PATTERN_NAME,
    BoundaryState,
    find_certificate_for_state,
    label_digest,
    state_from_boundary,
)
from check_kalmanson_certificate import build_distance_classes

DEFAULT_PREFIX_ARTIFACT = Path("data/certificates/c19_kalmanson_prefix_branch_pilot.json")
DEFAULT_CLOSED_EXAMPLE_COUNT = 12


def load_sampled_frontier(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("type") != "c19_kalmanson_prefix_branch_pilot_v1":
        raise ValueError("unexpected C19 prefix-pilot artifact type")
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise ValueError("branch_accounting must be an object")
    expected = {
        "sampled_branch_count": 128,
        "sampled_branch_certified_count": 100,
        "sampled_branch_unclosed_count": 28,
        "exhaustive_prefix_scan": False,
        "exhaustive_all_orders": False,
    }
    for key, value in expected.items():
        if accounting.get(key) != value:
            raise ValueError(f"C19 prefix artifact accounting changed at {key}")
    unclosed = data["unclosed_sampled_branches"]
    if not isinstance(unclosed, list) or len(unclosed) != 28:
        raise ValueError("C19 prefix artifact must record 28 unclosed sampled branches")
    return [dict(record) for record in unclosed]


def child_state(parent: BoundaryState, left_label: int, right_label: int) -> BoundaryState:
    if left_label == right_label:
        raise ValueError("child extension labels must be distinct")
    if left_label not in parent.remaining or right_label not in parent.remaining:
        raise ValueError("child extension labels must come from parent remaining labels")
    after_left = tuple(label for label in parent.remaining if label != left_label)
    return BoundaryState(
        left=parent.left + (left_label,),
        right=parent.right + (right_label,),
        remaining=tuple(label for label in after_left if label != right_label),
    )


def child_record(
    *,
    child_index: int,
    parent: Mapping[str, object],
    left_label: int,
    right_label: int,
) -> dict[str, object]:
    state = state_from_boundary(
        [int(v) for v in parent["boundary_left"]],
        [int(v) for v in parent["boundary_right_reflection_side"]],
    )
    child = child_state(state, left_label, right_label)
    return {
        "label": f"c19_fourth_pair_child_{child_index:04d}",
        "sampled_parent_label": str(parent["label"]),
        "parent_boundary_left": list(state.left),
        "parent_boundary_right_reflection_side": list(state.right),
        "added_left": left_label,
        "added_right_reflection_side": right_label,
        "child_boundary_left": list(child.left),
        "child_boundary_right_reflection_side": list(child.right),
    }


def scan_refinement(
    *,
    prefix_artifact: Path,
    max_parents: int | None,
    include_certificates: bool,
    closed_example_count: int,
    tol: float,
) -> dict[str, object]:
    if max_parents is not None and max_parents < 0:
        raise ValueError("max_parents must be nonnegative")
    if closed_example_count < 0:
        raise ValueError("closed_example_count must be nonnegative")

    all_parents = load_sampled_frontier(prefix_artifact)
    parents = all_parents if max_parents is None else all_parents[:max_parents]
    classes = build_distance_classes(N, OFFSETS)

    support_histogram: Counter[int] = Counter()
    row_count_histogram: Counter[int] = Counter()
    closed_examples: list[dict[str, object]] = []
    unclosed_children: list[dict[str, object]] = []
    closed_parent_labels: set[str] = set()
    child_labels: list[str] = []
    child_count = 0
    closed_count = 0

    for parent in parents:
        state = state_from_boundary(
            [int(v) for v in parent["boundary_left"]],
            [int(v) for v in parent["boundary_right_reflection_side"]],
        )
        parent_has_unclosed_child = False
        for left_label in state.remaining:
            after_left = tuple(label for label in state.remaining if label != left_label)
            for right_label in after_left:
                record = child_record(
                    child_index=child_count,
                    parent=parent,
                    left_label=left_label,
                    right_label=right_label,
                )
                label = str(record["label"])
                child_labels.append(label)
                child = child_state(state, left_label, right_label)
                row_count, cert, summary = find_certificate_for_state(
                    label=label,
                    state=child,
                    classes=classes,
                    tol=tol,
                )
                row_count_histogram[row_count] += 1
                if cert is None or summary is None:
                    parent_has_unclosed_child = True
                    unclosed_children.append(record)
                else:
                    closed_count += 1
                    support_histogram[int(summary["positive_inequalities"])] += 1
                    if len(closed_examples) < closed_example_count:
                        example = dict(record)
                        example["certificate_summary"] = summary
                        if include_certificates:
                            example["certificate"] = cert
                        closed_examples.append(example)
                child_count += 1
        if not parent_has_unclosed_child:
            closed_parent_labels.add(str(parent["label"]))

    return {
        "type": "c19_kalmanson_sampled_fourth_pair_refinement_v1",
        "trust": "EXACT_OBSTRUCTION",
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This refines only the 28 sampled C19 prefix branches left open by the bounded prefix pilot.",
            "Each closed fourth-pair child is certified using only Kalmanson inequalities whose order is forced by the recorded four-pair boundary prefix.",
            "Unclosed children are not counterexamples and are not evidence of realizability.",
            "This is not an exhaustive all-order C19 search.",
        ],
        "parameters": {
            "prefix_artifact": str(prefix_artifact),
            "prefix_pilot_sample_size": DEFAULT_MAX_BRANCHES,
            "parent_boundary_pairs": 3,
            "child_boundary_pairs": 4,
            "max_parents": max_parents,
            "include_certificates_in_examples": include_certificates,
            "closed_example_count": closed_example_count,
            "lp_support_tolerance": tol,
            "anchor_label": 0,
        },
        "branch_accounting": {
            "sampled_prefix_frontier_parent_count": len(all_parents),
            "scanned_parent_count": len(parents),
            "fourth_pair_children_per_parent": 132,
            "fourth_pair_child_branch_count": child_count,
            "fourth_pair_child_certified_count": closed_count,
            "unclosed_fourth_pair_child_branch_count": len(unclosed_children),
            "sampled_prefix_parents_closed_by_fourth_refinement": len(closed_parent_labels),
            "sampled_prefix_parents_still_unclosed_after_fourth_refinement": (
                len(parents) - len(closed_parent_labels)
            ),
            "exhaustive_refinement_of_sampled_prefix_frontier": max_parents is None,
            "exhaustive_all_orders": False,
        },
        "combined_sample_accounting": {
            "sampled_prefix_branches_in_prior_pilot": DEFAULT_MAX_BRANCHES,
            "sampled_prefix_branches_closed_directly_by_prior_pilot": 100,
            "sampled_prefix_branches_refined_here": len(all_parents),
            "sampled_prefix_branches_closed_by_fourth_pair_subdivision": (
                len(closed_parent_labels) if max_parents is None else None
            ),
            "sampled_prefix_branches_remaining_unclosed_after_fourth_pair": (
                len(all_parents) - len(closed_parent_labels) if max_parents is None else None
            ),
        },
        "forced_row_count_histogram": {
            str(key): row_count_histogram[key] for key in sorted(row_count_histogram)
        },
        "closed_support_size_histogram": {
            str(key): support_histogram[key] for key in sorted(support_histogram)
        },
        "closed_certificate_examples": closed_examples,
        "fourth_child_label_digest": label_digest(child_labels),
        "unclosed_fourth_pair_child_branches": unclosed_children,
    }


def assert_expected(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise AssertionError("branch_accounting must be an object")
    expected_accounting = {
        "sampled_prefix_frontier_parent_count": 28,
        "scanned_parent_count": 28,
        "fourth_pair_children_per_parent": 132,
        "fourth_pair_child_branch_count": 3696,
        "fourth_pair_child_certified_count": 3643,
        "unclosed_fourth_pair_child_branch_count": 53,
        "sampled_prefix_parents_closed_by_fourth_refinement": 13,
        "sampled_prefix_parents_still_unclosed_after_fourth_refinement": 15,
        "exhaustive_refinement_of_sampled_prefix_frontier": True,
        "exhaustive_all_orders": False,
    }
    for key, expected in expected_accounting.items():
        if accounting[key] != expected:
            raise AssertionError(f"{key} changed: {accounting[key]} != {expected}")

    combined = data["combined_sample_accounting"]
    if not isinstance(combined, Mapping):
        raise AssertionError("combined_sample_accounting must be an object")
    expected_combined = {
        "sampled_prefix_branches_in_prior_pilot": 128,
        "sampled_prefix_branches_closed_directly_by_prior_pilot": 100,
        "sampled_prefix_branches_refined_here": 28,
        "sampled_prefix_branches_closed_by_fourth_pair_subdivision": 13,
        "sampled_prefix_branches_remaining_unclosed_after_fourth_pair": 15,
    }
    for key, expected in expected_combined.items():
        if combined[key] != expected:
            raise AssertionError(f"{key} changed: {combined[key]} != {expected}")

    if data["forced_row_count_histogram"] != {"1932": 3696}:
        raise AssertionError("forced row histogram changed")

    support_histogram = data["closed_support_size_histogram"]
    if not isinstance(support_histogram, Mapping):
        raise AssertionError("closed support-size histogram must be an object")
    if sum(int(count) for count in support_histogram.values()) != int(
        accounting["fourth_pair_child_certified_count"]
    ):
        raise AssertionError("closed support-size histogram total changed")

    expected_digest = "8a6276f5a27044b79b6ac2bb0d4b88612051d07738633d56a0c966409a923a90"
    if data["fourth_child_label_digest"] != expected_digest:
        raise AssertionError("fourth child label digest changed")
    unclosed = data["unclosed_fourth_pair_child_branches"]
    if not isinstance(unclosed, list) or len(unclosed) != 53:
        raise AssertionError("unclosed fourth-pair child list changed")
    if unclosed[0]["label"] != "c19_fourth_pair_child_0044":
        raise AssertionError("first unclosed fourth-pair child changed")
    if unclosed[-1]["label"] != "c19_fourth_pair_child_3266":
        raise AssertionError("last unclosed fourth-pair child changed")


def print_table(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise TypeError("branch_accounting must be an object")
    print(
        "sampled C19 fourth-pair children: "
        f"closed={accounting['fourth_pair_child_certified_count']} "
        f"unclosed={accounting['unclosed_fourth_pair_child_branch_count']} "
        f"scanned={accounting['fourth_pair_child_branch_count']}"
    )
    print(
        "sampled parents: "
        f"closed={accounting['sampled_prefix_parents_closed_by_fourth_refinement']} "
        f"still_open={accounting['sampled_prefix_parents_still_unclosed_after_fourth_refinement']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix-artifact", type=Path, default=DEFAULT_PREFIX_ARTIFACT)
    parser.add_argument("--max-parents", type=int)
    parser.add_argument("--tol", type=float, default=1e-9, help="LP support threshold")
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument(
        "--include-certificates",
        action="store_true",
        help="include full certificates for stored closed examples",
    )
    parser.add_argument(
        "--closed-example-count",
        type=int,
        default=DEFAULT_CLOSED_EXAMPLE_COUNT,
        help="number of closed certificate examples to store",
    )
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    data = scan_refinement(
        prefix_artifact=args.prefix_artifact,
        max_parents=args.max_parents,
        include_certificates=args.include_certificates,
        closed_example_count=args.closed_example_count,
        tol=args.tol,
    )
    if args.assert_expected:
        assert_expected(data)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_table(data)
        if args.assert_expected:
            print("OK: sampled C19 fourth-pair refinement matched expected frontier")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
