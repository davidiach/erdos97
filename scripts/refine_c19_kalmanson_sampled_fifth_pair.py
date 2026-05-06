#!/usr/bin/env python3
"""Refine sampled C19 fourth-pair frontier children by one fifth boundary pair.

This script starts from the 53 unclosed sampled fourth-pair children recorded by
refine_c19_kalmanson_sampled_fourth_pair.py.  It appends one additional ordered
left/right boundary pair to each parent and checks the resulting children with
prefix-forced Kalmanson/Farkas certificates.

The output is a bounded sampled-frontier refinement, not an all-order C19
search.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Mapping

from check_kalmanson_certificate import build_distance_classes
from pilot_c19_kalmanson_prefix_branches import (
    DEFAULT_MAX_BRANCHES,
    N,
    OFFSETS,
    PATTERN_NAME,
    find_certificate_for_state,
    label_digest,
    state_from_boundary,
)
from refine_c19_kalmanson_sampled_fourth_pair import child_state

DEFAULT_FOURTH_PAIR_ARTIFACT = Path(
    "data/certificates/c19_kalmanson_sampled_fourth_pair_refinement.json"
)
DEFAULT_CLOSED_EXAMPLE_COUNT = 12


def load_fourth_pair_frontier(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("type") != "c19_kalmanson_sampled_fourth_pair_refinement_v1":
        raise ValueError("unexpected C19 fourth-pair refinement artifact type")
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise ValueError("branch_accounting must be an object")
    expected = {
        "sampled_prefix_frontier_parent_count": 28,
        "fourth_pair_child_branch_count": 3696,
        "fourth_pair_child_certified_count": 3643,
        "unclosed_fourth_pair_child_branch_count": 53,
        "sampled_prefix_parents_closed_by_fourth_refinement": 13,
        "sampled_prefix_parents_still_unclosed_after_fourth_refinement": 15,
        "exhaustive_refinement_of_sampled_prefix_frontier": True,
        "exhaustive_all_orders": False,
    }
    for key, value in expected.items():
        if accounting.get(key) != value:
            raise ValueError(f"C19 fourth-pair artifact accounting changed at {key}")
    unclosed = data["unclosed_fourth_pair_child_branches"]
    if not isinstance(unclosed, list) or len(unclosed) != 53:
        raise ValueError("C19 fourth-pair artifact must record 53 unclosed children")
    return [dict(record) for record in unclosed]


def fifth_child_record(
    *,
    child_index: int,
    parent: Mapping[str, object],
    left_label: int,
    right_label: int,
) -> dict[str, object]:
    state = state_from_boundary(
        [int(v) for v in parent["child_boundary_left"]],
        [int(v) for v in parent["child_boundary_right_reflection_side"]],
    )
    child = child_state(state, left_label, right_label)
    return {
        "label": f"c19_fifth_pair_child_{child_index:05d}",
        "fourth_pair_parent_label": str(parent["label"]),
        "sampled_parent_label": str(parent["sampled_parent_label"]),
        "parent_boundary_left": list(state.left),
        "parent_boundary_right_reflection_side": list(state.right),
        "added_left": left_label,
        "added_right_reflection_side": right_label,
        "child_boundary_left": list(child.left),
        "child_boundary_right_reflection_side": list(child.right),
    }


def scan_refinement(
    *,
    fourth_pair_artifact: Path,
    max_parents: int | None,
    include_certificates: bool,
    closed_example_count: int,
    tol: float,
) -> dict[str, object]:
    if max_parents is not None and max_parents < 0:
        raise ValueError("max_parents must be nonnegative")
    if closed_example_count < 0:
        raise ValueError("closed_example_count must be nonnegative")

    all_parents = load_fourth_pair_frontier(fourth_pair_artifact)
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
            [int(v) for v in parent["child_boundary_left"]],
            [int(v) for v in parent["child_boundary_right_reflection_side"]],
        )
        parent_has_unclosed_child = False
        for left_label in state.remaining:
            after_left = tuple(label for label in state.remaining if label != left_label)
            for right_label in after_left:
                record = fifth_child_record(
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

    fourth_parents_by_sampled_parent: dict[str, set[str]] = {}
    for parent in all_parents:
        fourth_parents_by_sampled_parent.setdefault(
            str(parent["sampled_parent_label"]),
            set(),
        ).add(str(parent["label"]))
    closed_sampled_parent_labels = {
        sampled_parent
        for sampled_parent, fourth_parents in fourth_parents_by_sampled_parent.items()
        if fourth_parents <= closed_parent_labels
    }
    sampled_prefixes_closed_by_fifth = (
        len(closed_sampled_parent_labels) if max_parents is None else None
    )
    sampled_prefixes_closed_after_fifth = (
        100 + 13 + len(closed_sampled_parent_labels) if max_parents is None else None
    )
    sampled_prefixes_remaining_after_fifth = (
        DEFAULT_MAX_BRANCHES - int(sampled_prefixes_closed_after_fifth)
        if sampled_prefixes_closed_after_fifth is not None
        else None
    )

    return {
        "type": "c19_kalmanson_sampled_fifth_pair_refinement_v1",
        "trust": "EXACT_OBSTRUCTION",
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This refines only sampled C19 fourth-pair children left open by the sampled fourth-pair pass.",
            "Each closed fifth-pair child is certified using only Kalmanson inequalities whose order is forced by the recorded five-pair boundary prefix.",
            "Unclosed children are not counterexamples and are not evidence of realizability.",
            "This is not an exhaustive all-order C19 search.",
        ],
        "parameters": {
            "fourth_pair_artifact": str(fourth_pair_artifact),
            "prefix_pilot_sample_size": DEFAULT_MAX_BRANCHES,
            "parent_boundary_pairs": 4,
            "child_boundary_pairs": 5,
            "max_parents": max_parents,
            "include_certificates_in_examples": include_certificates,
            "closed_example_count": closed_example_count,
            "lp_support_tolerance": tol,
            "anchor_label": 0,
        },
        "branch_accounting": {
            "sampled_fourth_pair_frontier_parent_count": len(all_parents),
            "scanned_parent_count": len(parents),
            "fifth_pair_children_per_parent": 90,
            "fifth_pair_child_branch_count": child_count,
            "fifth_pair_child_certified_count": closed_count,
            "unclosed_fifth_pair_child_branch_count": len(unclosed_children),
            "fourth_pair_parents_closed_by_fifth_refinement": len(closed_parent_labels),
            "fourth_pair_parents_still_unclosed_after_fifth_refinement": (
                len(parents) - len(closed_parent_labels)
            ),
            "sampled_prefix_parents_closed_by_fifth_refinement": (
                sampled_prefixes_closed_by_fifth
            ),
            "exhaustive_refinement_of_sampled_fourth_pair_frontier": max_parents is None,
            "exhaustive_all_orders": False,
        },
        "combined_sample_accounting": {
            "sampled_prefix_branches_in_prior_pilot": DEFAULT_MAX_BRANCHES,
            "sampled_prefix_branches_closed_directly_by_prior_pilot": 100,
            "sampled_prefix_branches_closed_by_fourth_pair_subdivision": 13,
            "sampled_prefix_branches_remaining_after_fourth_pair": 15,
            "sampled_prefix_branches_closed_by_fifth_pair_subdivision": (
                sampled_prefixes_closed_by_fifth
            ),
            "sampled_prefix_branches_closed_after_fifth_pair": (
                sampled_prefixes_closed_after_fifth
            ),
            "sampled_prefix_branches_remaining_after_fifth_pair": (
                sampled_prefixes_remaining_after_fifth
            ),
            "sampled_fourth_pair_children_refined_here": len(all_parents),
            "sampled_fourth_pair_children_closed_by_fifth_pair_subdivision": (
                len(closed_parent_labels) if max_parents is None else None
            ),
            "sampled_fourth_pair_children_remaining_after_fifth_pair": (
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
        "fifth_child_label_digest": label_digest(child_labels),
        "unclosed_fifth_pair_child_branches": unclosed_children,
    }


def assert_expected(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise AssertionError("branch_accounting must be an object")
    expected_accounting = {
        "sampled_fourth_pair_frontier_parent_count": 53,
        "scanned_parent_count": 53,
        "fifth_pair_children_per_parent": 90,
        "fifth_pair_child_branch_count": 4770,
        "fifth_pair_child_certified_count": 4770,
        "unclosed_fifth_pair_child_branch_count": 0,
        "fourth_pair_parents_closed_by_fifth_refinement": 53,
        "fourth_pair_parents_still_unclosed_after_fifth_refinement": 0,
        "sampled_prefix_parents_closed_by_fifth_refinement": 15,
        "exhaustive_refinement_of_sampled_fourth_pair_frontier": True,
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
        "sampled_prefix_branches_closed_by_fourth_pair_subdivision": 13,
        "sampled_prefix_branches_remaining_after_fourth_pair": 15,
        "sampled_prefix_branches_closed_by_fifth_pair_subdivision": 15,
        "sampled_prefix_branches_closed_after_fifth_pair": 128,
        "sampled_prefix_branches_remaining_after_fifth_pair": 0,
        "sampled_fourth_pair_children_refined_here": 53,
        "sampled_fourth_pair_children_closed_by_fifth_pair_subdivision": 53,
        "sampled_fourth_pair_children_remaining_after_fifth_pair": 0,
    }
    for key, expected in expected_combined.items():
        if combined[key] != expected:
            raise AssertionError(f"{key} changed: {combined[key]} != {expected}")

    if data["forced_row_count_histogram"] != {"3300": 4770}:
        raise AssertionError("forced row histogram changed")

    expected_support_histogram = {
        "4": 1,
        "13": 1,
        "18": 1,
        "22": 1,
        "24": 1,
        "26": 1,
        "27": 1,
        "29": 1,
        "30": 2,
        "31": 3,
        "32": 4,
        "33": 3,
        "34": 2,
        "35": 8,
        "36": 3,
        "37": 8,
        "38": 8,
        "39": 8,
        "40": 12,
        "41": 18,
        "42": 21,
        "43": 18,
        "44": 22,
        "45": 27,
        "46": 32,
        "47": 42,
        "48": 52,
        "49": 63,
        "50": 46,
        "51": 68,
        "52": 99,
        "53": 123,
        "54": 134,
        "55": 159,
        "56": 148,
        "57": 207,
        "58": 233,
        "59": 260,
        "60": 300,
        "61": 285,
        "62": 287,
        "63": 305,
        "64": 270,
        "65": 261,
        "66": 282,
        "67": 230,
        "68": 207,
        "69": 169,
        "70": 102,
        "71": 72,
        "72": 71,
        "73": 46,
        "74": 19,
        "75": 13,
        "76": 4,
        "77": 4,
        "78": 2,
    }
    if data["closed_support_size_histogram"] != expected_support_histogram:
        raise AssertionError("closed support-size histogram changed")

    expected_digest = "94c4657efb0253fe566cc7fad12c2401658f0fcdc9f1cdca7b44c3d40d497f0b"
    if data["fifth_child_label_digest"] != expected_digest:
        raise AssertionError("fifth child label digest changed")

    examples = data["closed_certificate_examples"]
    if not isinstance(examples, list) or len(examples) != DEFAULT_CLOSED_EXAMPLE_COUNT:
        raise AssertionError("closed certificate examples changed")
    first = examples[0]
    if not isinstance(first, Mapping):
        raise AssertionError("first closed example must be an object")
    if first["label"] != "c19_fifth_pair_child_00000":
        raise AssertionError("first closed example label changed")
    if first["fourth_pair_parent_label"] != "c19_fourth_pair_child_0044":
        raise AssertionError("first closed example parent changed")

    unclosed = data["unclosed_fifth_pair_child_branches"]
    if not isinstance(unclosed, list) or unclosed:
        raise AssertionError("all fifth-pair children should close")


def print_table(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise TypeError("branch_accounting must be an object")
    print(
        "sampled C19 fifth-pair children: "
        f"closed={accounting['fifth_pair_child_certified_count']} "
        f"unclosed={accounting['unclosed_fifth_pair_child_branch_count']} "
        f"scanned={accounting['fifth_pair_child_branch_count']}"
    )
    print(
        "fourth-pair parents: "
        f"closed={accounting['fourth_pair_parents_closed_by_fifth_refinement']} "
        f"still_open={accounting['fourth_pair_parents_still_unclosed_after_fifth_refinement']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fourth-pair-artifact",
        type=Path,
        default=DEFAULT_FOURTH_PAIR_ARTIFACT,
    )
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
        fourth_pair_artifact=args.fourth_pair_artifact,
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
            print("OK: sampled C19 fifth-pair refinement matched expected frontier")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
