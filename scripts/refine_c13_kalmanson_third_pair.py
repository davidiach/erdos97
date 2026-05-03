#!/usr/bin/env python3
"""Refine unresolved C13 two-pair prefixes by adding a third boundary pair.

This script starts from the two-boundary-pair frontier produced by
certify_c13_kalmanson_partial_branches.py.  It recomputes the 832 unclosed
two-pair prefixes, appends one additional ordered left/right boundary pair to
each, and checks the resulting third-pair child branches using only
prefix-forced Kalmanson inequalities.

The output is not an exhaustive all-order C13 search.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

from branch_c13_kalmanson_prefix_pilot import (
    BoundaryState,
    BranchCounts,
    generate_boundary_states,
)
from certify_c13_kalmanson_partial_branches import (
    DEFAULT_BOUNDARY_PAIRS,
    N,
    OFFSETS,
    PATTERN_NAME,
    branch_label,
    partial_certificate_payload,
    partial_kalmanson_rows,
    summarize_certificate,
)
from check_kalmanson_certificate import build_distance_classes
from find_kalmanson_certificate import exact_positive_weights, lp_support

DEFAULT_CLOSED_EXAMPLE_COUNT = 12


def label_digest(labels: Sequence[str]) -> str:
    payload = "".join(f"{label}\n" for label in labels)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def find_certificate_for_state(
    *,
    label: str,
    state: BoundaryState,
    classes: Mapping[tuple[int, int], int],
    tol: float,
) -> tuple[int, dict[str, object] | None, dict[str, object] | None]:
    rows = partial_kalmanson_rows(state, classes)
    support = lp_support(rows, tol)
    if support is None:
        return len(rows), None, None
    weights = exact_positive_weights(rows, support)
    if weights is None:
        return len(rows), None, None
    cert = partial_certificate_payload(
        label=label,
        state=state,
        rows=rows,
        support=support,
        weights=weights,
    )
    summary = summarize_certificate(cert)
    return len(rows), cert, summary


def two_pair_unclosed_parents(
    *,
    classes: Mapping[tuple[int, int], int],
    tol: float,
) -> tuple[list[tuple[int, BoundaryState]], BranchCounts]:
    states, counts = generate_boundary_states(DEFAULT_BOUNDARY_PAIRS)
    unclosed: list[tuple[int, BoundaryState]] = []
    for idx, state in enumerate(states):
        _row_count, cert, _summary = find_certificate_for_state(
            label=branch_label(idx),
            state=state,
            classes=classes,
            tol=tol,
        )
        if cert is None:
            unclosed.append((idx, state))
    return unclosed, counts


def child_state(parent: BoundaryState, left_label: int, right_label: int) -> BoundaryState:
    if left_label == right_label:
        raise ValueError("child extension labels must be distinct")
    if left_label not in parent.remaining or right_label not in parent.remaining:
        raise ValueError("child extension labels must come from parent remaining labels")
    return BoundaryState(
        left=parent.left + (left_label,),
        right=parent.right + (right_label,),
        remaining=tuple(
            label
            for label in parent.remaining
            if label not in {left_label, right_label}
        ),
    )


def child_record(
    *,
    child_index: int,
    parent_index: int,
    parent: BoundaryState,
    left_label: int,
    right_label: int,
) -> dict[str, object]:
    child = child_state(parent, left_label, right_label)
    return {
        "label": f"third_pair_child_{child_index:05d}",
        "parent_label": branch_label(parent_index),
        "parent_boundary_left": list(parent.left),
        "parent_boundary_right_reflection_side": list(parent.right),
        "added_left": left_label,
        "added_right_reflection_side": right_label,
        "child_boundary_left": list(child.left),
        "child_boundary_right_reflection_side": list(child.right),
    }


def scan_refinement(
    *,
    max_parents: int | None,
    include_certificates: bool,
    closed_example_count: int,
    tol: float,
) -> dict[str, object]:
    if max_parents is not None and max_parents < 0:
        raise ValueError("max_parents must be nonnegative")
    if closed_example_count < 0:
        raise ValueError("closed_example_count must be nonnegative")

    classes = build_distance_classes(N, OFFSETS)
    all_unclosed_parents, parent_counts = two_pair_unclosed_parents(
        classes=classes, tol=tol
    )
    selected_parents = (
        all_unclosed_parents
        if max_parents is None
        else all_unclosed_parents[:max_parents]
    )

    support_histogram: Counter[int] = Counter()
    row_count_histogram: Counter[int] = Counter()
    closed_examples: list[dict[str, object]] = []
    unclosed_children: list[dict[str, object]] = []
    child_labels: list[str] = []
    child_count = 0
    closed_count = 0

    for parent_index, parent in selected_parents:
        for left_label in parent.remaining:
            after_left = tuple(label for label in parent.remaining if label != left_label)
            for right_label in after_left:
                record = child_record(
                    child_index=child_count,
                    parent_index=parent_index,
                    parent=parent,
                    left_label=left_label,
                    right_label=right_label,
                )
                label = str(record["label"])
                child_labels.append(label)
                state = child_state(parent, left_label, right_label)
                row_count, cert, summary = find_certificate_for_state(
                    label=label,
                    state=state,
                    classes=classes,
                    tol=tol,
                )
                row_count_histogram[row_count] += 1
                if cert is None or summary is None:
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

    raw_two_pair_count = parent_counts.raw_boundary_state_count
    canonical_two_pair_count = parent_counts.canonical_boundary_state_count
    remaining_per_parent = N - 1 - 2 * DEFAULT_BOUNDARY_PAIRS
    child_extensions_per_parent = remaining_per_parent * (remaining_per_parent - 1)
    payload = {
        "type": "c13_kalmanson_third_pair_refinement_v1",
        "trust": "EXACT_OBSTRUCTION",
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This refines only the two-boundary-pair prefixes left open by the previous prefix-forced Kalmanson pass.",
            "Each closed child branch is certified using only Kalmanson inequalities whose order is forced by the recorded third-pair boundary prefix.",
            "Unclosed children are not counterexamples and are not numerical evidence of realizability.",
        ],
        "parameters": {
            "parent_boundary_pairs": DEFAULT_BOUNDARY_PAIRS,
            "child_boundary_pairs": DEFAULT_BOUNDARY_PAIRS + 1,
            "max_parents": max_parents,
            "include_certificates_in_examples": include_certificates,
            "closed_example_count": closed_example_count,
            "lp_support_tolerance": tol,
            "anchor_label": 0,
        },
        "branch_accounting": {
            "raw_two_pair_boundary_state_count": raw_two_pair_count,
            "canonical_two_pair_boundary_state_count": canonical_two_pair_count,
            "two_pair_unclosed_parent_count": len(all_unclosed_parents),
            "scanned_parent_count": len(selected_parents),
            "child_extensions_per_parent": child_extensions_per_parent,
            "third_pair_child_branch_count": child_count,
            "third_pair_child_certified_count": closed_count,
            "unclosed_child_branch_count": len(unclosed_children),
            "exhaustive_refinement_of_two_pair_frontier": max_parents is None,
            "exhaustive_all_orders": False,
        },
        "forced_row_count_histogram": {
            str(key): row_count_histogram[key] for key in sorted(row_count_histogram)
        },
        "closed_support_size_histogram": {
            str(key): support_histogram[key] for key in sorted(support_histogram)
        },
        "closed_certificate_examples": closed_examples,
        "child_label_digest": label_digest(child_labels),
        "unclosed_child_branches": unclosed_children,
    }
    return payload


def assert_expected(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise AssertionError("branch_accounting must be an object")
    expected_accounting = {
        "raw_two_pair_boundary_state_count": 11880,
        "canonical_two_pair_boundary_state_count": 5940,
        "two_pair_unclosed_parent_count": 832,
        "scanned_parent_count": 832,
        "child_extensions_per_parent": 56,
        "third_pair_child_branch_count": 46592,
        "third_pair_child_certified_count": 46567,
        "unclosed_child_branch_count": 25,
        "exhaustive_refinement_of_two_pair_frontier": True,
        "exhaustive_all_orders": False,
    }
    for key, expected in expected_accounting.items():
        if accounting[key] != expected:
            raise AssertionError(f"{key} changed: {accounting[key]} != {expected}")

    if data["forced_row_count_histogram"] != {"490": 46592}:
        raise AssertionError("forced row histogram changed")

    support_histogram = data["closed_support_size_histogram"]
    if not isinstance(support_histogram, Mapping):
        raise AssertionError("closed support-size histogram must be an object")
    support_total = 0
    for key, value in support_histogram.items():
        if int(key) <= 0 or int(value) <= 0:
            raise AssertionError("closed support-size histogram has nonpositive entry")
        support_total += int(value)
    if support_total != accounting["third_pair_child_certified_count"]:
        raise AssertionError("closed support-size histogram total changed")

    expected_digest = "4dfb8111a92c9c8d429fa349acd109d413a586dc6876848ea7a04cd1fd9f8c32"
    if data["child_label_digest"] != expected_digest:
        raise AssertionError("child label digest changed")

    examples = data["closed_certificate_examples"]
    if not isinstance(examples, list) or len(examples) != DEFAULT_CLOSED_EXAMPLE_COUNT:
        raise AssertionError("closed certificate examples changed")

    unclosed = data["unclosed_child_branches"]
    if not isinstance(unclosed, list) or len(unclosed) != 25:
        raise AssertionError("unclosed child branch list changed")
    first_expected = {
        "label": "third_pair_child_07723",
        "parent_label": "partial_branch_1244",
        "added_left": 12,
        "added_right_reflection_side": 6,
    }
    last_expected = {
        "label": "third_pair_child_42595",
        "parent_label": "partial_branch_5284",
        "added_left": 7,
        "added_right_reflection_side": 1,
    }
    for key, expected in first_expected.items():
        if unclosed[0][key] != expected:
            raise AssertionError(f"first unclosed child changed at {key}")
    for key, expected in last_expected.items():
        if unclosed[-1][key] != expected:
            raise AssertionError(f"last unclosed child changed at {key}")


def print_table(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise TypeError("branch_accounting must be an object")
    print(
        "third-pair children: "
        f"closed={accounting['third_pair_child_certified_count']} "
        f"unclosed={accounting['unclosed_child_branch_count']} "
        f"scanned={accounting['third_pair_child_branch_count']}"
    )
    print("support-size histogram:")
    histogram = data["closed_support_size_histogram"]
    if not isinstance(histogram, Mapping):
        raise TypeError("closed_support_size_histogram must be an object")
    for size, count in histogram.items():
        print(f"  {size}: {count}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
            print("OK: C13 third-pair refinement matched expected frontier")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
