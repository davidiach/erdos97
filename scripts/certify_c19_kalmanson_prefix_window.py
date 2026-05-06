#!/usr/bin/env python3
"""Certify a deterministic C19 three-boundary-prefix window by subdivision.

The default window covers canonical prefix branch indices 128 through 159 for
the fixed selected-witness pattern `C19_skew`.  It first tries direct
three-boundary-prefix Kalmanson/Farkas certificates.  Any direct survivor is
subdivided by one fourth boundary pair, and any fourth-pair survivor is
subdivided by one fifth boundary pair.

This is a bounded sampled-window artifact, not an all-order C19 search.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import islice
from pathlib import Path
from typing import Mapping

from check_kalmanson_certificate import build_distance_classes
from pilot_c19_kalmanson_prefix_branches import (
    N,
    OFFSETS,
    PATTERN_NAME,
    BoundaryState,
    branch_label,
    count_boundary_states,
    find_certificate_for_state,
    iter_boundary_states,
    label_digest,
)
from refine_c19_kalmanson_sampled_fourth_pair import child_state

DEFAULT_START_INDEX = 128
DEFAULT_WINDOW_SIZE = 32
DEFAULT_CLOSED_EXAMPLE_COUNT = 12


def state_record(label: str, state: BoundaryState) -> dict[str, object]:
    return {
        "label": label,
        "boundary_left": list(state.left),
        "boundary_right_reflection_side": list(state.right),
        "middle_label_count": len(state.remaining),
    }


def child_record(
    *,
    label: str,
    prefix_label: str,
    parent: BoundaryState,
    child: BoundaryState,
    left_label: int,
    right_label: int,
) -> dict[str, object]:
    return {
        "label": label,
        "prefix_parent_label": prefix_label,
        "parent_boundary_left": list(parent.left),
        "parent_boundary_right_reflection_side": list(parent.right),
        "added_left": left_label,
        "added_right_reflection_side": right_label,
        "child_boundary_left": list(child.left),
        "child_boundary_right_reflection_side": list(child.right),
        "middle_label_count": len(child.remaining),
    }


def scan_window(
    *,
    start_index: int,
    window_size: int,
    include_certificates: bool,
    closed_example_count: int,
    tol: float,
) -> dict[str, object]:
    if start_index < 0:
        raise ValueError("start_index must be nonnegative")
    if window_size < 0:
        raise ValueError("window_size must be nonnegative")
    if closed_example_count < 0:
        raise ValueError("closed_example_count must be nonnegative")

    classes = build_distance_classes(N, OFFSETS)
    raw_count, canonical_count = count_boundary_states(3)

    prefix_labels: list[str] = []
    fourth_child_labels: list[str] = []
    fifth_child_labels: list[str] = []
    direct_support_histogram: Counter[int] = Counter()
    fourth_support_histogram: Counter[int] = Counter()
    fifth_support_histogram: Counter[int] = Counter()
    direct_row_count_histogram: Counter[int] = Counter()
    fourth_row_count_histogram: Counter[int] = Counter()
    fifth_row_count_histogram: Counter[int] = Counter()
    direct_closed_examples: list[dict[str, object]] = []
    fourth_closed_examples: list[dict[str, object]] = []
    fifth_closed_examples: list[dict[str, object]] = []
    direct_unclosed_prefixes: list[dict[str, object]] = []
    unclosed_fourth_children: list[dict[str, object]] = []
    unclosed_fifth_children: list[dict[str, object]] = []

    direct_closed = 0
    fourth_child_count = 0
    fourth_closed = 0
    fourth_parent_closed = 0
    fifth_child_count = 0
    fifth_closed = 0
    fifth_parent_closed = 0
    prefix_closed_by_fifth = 0

    states = islice(iter_boundary_states(3), start_index, start_index + window_size)
    for prefix_index, state in enumerate(states, start_index):
        prefix_label = branch_label(prefix_index)
        prefix_labels.append(prefix_label)
        row_count, cert, summary = find_certificate_for_state(
            label=prefix_label,
            state=state,
            classes=classes,
            tol=tol,
        )
        direct_row_count_histogram[row_count] += 1
        if cert is not None and summary is not None:
            direct_closed += 1
            direct_support_histogram[int(summary["positive_inequalities"])] += 1
            if len(direct_closed_examples) < closed_example_count:
                example = state_record(prefix_label, state)
                example["certificate_summary"] = summary
                if include_certificates:
                    example["certificate"] = cert
                direct_closed_examples.append(example)
            continue

        direct_unclosed_prefixes.append(state_record(prefix_label, state))
        fourth_parent_has_unclosed_child = False
        fourth_children_for_prefix: list[tuple[str, BoundaryState, dict[str, object]]] = []
        fourth_index = 0
        for left_label in state.remaining:
            after_left = tuple(label for label in state.remaining if label != left_label)
            for right_label in after_left:
                child = child_state(state, left_label, right_label)
                label = f"c19_window_fourth_child_{prefix_index:04d}_{fourth_index:04d}"
                record = child_record(
                    label=label,
                    prefix_label=prefix_label,
                    parent=state,
                    child=child,
                    left_label=left_label,
                    right_label=right_label,
                )
                fourth_child_labels.append(label)
                row_count, cert, summary = find_certificate_for_state(
                    label=label,
                    state=child,
                    classes=classes,
                    tol=tol,
                )
                fourth_row_count_histogram[row_count] += 1
                fourth_child_count += 1
                if cert is not None and summary is not None:
                    fourth_closed += 1
                    fourth_support_histogram[int(summary["positive_inequalities"])] += 1
                    if len(fourth_closed_examples) < closed_example_count:
                        example = dict(record)
                        example["certificate_summary"] = summary
                        if include_certificates:
                            example["certificate"] = cert
                        fourth_closed_examples.append(example)
                else:
                    fourth_parent_has_unclosed_child = True
                    unclosed_fourth_children.append(record)
                    fourth_children_for_prefix.append((label, child, record))
                fourth_index += 1
        if not fourth_parent_has_unclosed_child:
            fourth_parent_closed += 1
            continue

        all_fourth_survivors_closed_by_fifth = True
        for fourth_label, fourth_state, fourth_record in fourth_children_for_prefix:
            fifth_parent_has_unclosed_child = False
            fifth_index = 0
            for left_label in fourth_state.remaining:
                after_left = tuple(
                    label for label in fourth_state.remaining if label != left_label
                )
                for right_label in after_left:
                    child = child_state(fourth_state, left_label, right_label)
                    label = (
                        f"c19_window_fifth_child_"
                        f"{prefix_index:04d}_{fourth_label[-4:]}_{fifth_index:04d}"
                    )
                    record = child_record(
                        label=label,
                        prefix_label=prefix_label,
                        parent=fourth_state,
                        child=child,
                        left_label=left_label,
                        right_label=right_label,
                    )
                    record["fourth_pair_parent_label"] = fourth_label
                    record["fourth_pair_parent_boundary_left"] = fourth_record[
                        "child_boundary_left"
                    ]
                    record["fourth_pair_parent_boundary_right_reflection_side"] = (
                        fourth_record["child_boundary_right_reflection_side"]
                    )
                    fifth_child_labels.append(label)
                    row_count, cert, summary = find_certificate_for_state(
                        label=label,
                        state=child,
                        classes=classes,
                        tol=tol,
                    )
                    fifth_row_count_histogram[row_count] += 1
                    fifth_child_count += 1
                    if cert is not None and summary is not None:
                        fifth_closed += 1
                        fifth_support_histogram[int(summary["positive_inequalities"])] += 1
                        if len(fifth_closed_examples) < closed_example_count:
                            example = dict(record)
                            example["certificate_summary"] = summary
                            if include_certificates:
                                example["certificate"] = cert
                            fifth_closed_examples.append(example)
                    else:
                        fifth_parent_has_unclosed_child = True
                        unclosed_fifth_children.append(record)
                    fifth_index += 1
            if fifth_parent_has_unclosed_child:
                all_fourth_survivors_closed_by_fifth = False
            else:
                fifth_parent_closed += 1
        if all_fourth_survivors_closed_by_fifth:
            prefix_closed_by_fifth += 1

    prefix_count = len(prefix_labels)
    prefix_closed_after_chain = direct_closed + fourth_parent_closed + prefix_closed_by_fifth
    return {
        "type": "c19_kalmanson_prefix_window_chain_v1",
        "trust": "EXACT_OBSTRUCTION",
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This certifies only one deterministic C19 three-boundary-prefix window.",
            "Closed branches use Kalmanson/Farkas certificates whose order is forced by the recorded boundary prefix.",
            "Unclosed children, if any, are not counterexamples and are not evidence of realizability.",
            "This is not an exhaustive all-order C19 search.",
        ],
        "parameters": {
            "start_index": start_index,
            "window_size": window_size,
            "boundary_pairs": 3,
            "include_certificates_in_examples": include_certificates,
            "closed_example_count": closed_example_count,
            "lp_support_tolerance": tol,
            "anchor_label": 0,
        },
        "global_prefix_space": {
            "raw_three_boundary_state_count": raw_count,
            "canonical_three_boundary_state_count": canonical_count,
        },
        "branch_accounting": {
            "prefix_branch_count": prefix_count,
            "direct_prefix_certified_count": direct_closed,
            "direct_prefix_unclosed_count": len(direct_unclosed_prefixes),
            "fourth_pair_parent_count": len(direct_unclosed_prefixes),
            "fourth_pair_child_branch_count": fourth_child_count,
            "fourth_pair_child_certified_count": fourth_closed,
            "unclosed_fourth_pair_child_branch_count": len(unclosed_fourth_children),
            "prefix_parents_closed_by_fourth_refinement": fourth_parent_closed,
            "fifth_pair_parent_count": len(unclosed_fourth_children),
            "fifth_pair_child_branch_count": fifth_child_count,
            "fifth_pair_child_certified_count": fifth_closed,
            "unclosed_fifth_pair_child_branch_count": len(unclosed_fifth_children),
            "fourth_pair_parents_closed_by_fifth_refinement": fifth_parent_closed,
            "prefix_parents_closed_by_fifth_refinement": prefix_closed_by_fifth,
            "prefix_branches_closed_after_chain": prefix_closed_after_chain,
            "prefix_branches_remaining_after_chain": prefix_count - prefix_closed_after_chain,
            "exhaustive_window_scan": True,
            "exhaustive_all_orders": False,
        },
        "forced_row_count_histograms": {
            "direct_prefix": {
                str(key): direct_row_count_histogram[key]
                for key in sorted(direct_row_count_histogram)
            },
            "fourth_pair": {
                str(key): fourth_row_count_histogram[key]
                for key in sorted(fourth_row_count_histogram)
            },
            "fifth_pair": {
                str(key): fifth_row_count_histogram[key]
                for key in sorted(fifth_row_count_histogram)
            },
        },
        "closed_support_size_histograms": {
            "direct_prefix": {
                str(key): direct_support_histogram[key]
                for key in sorted(direct_support_histogram)
            },
            "fourth_pair": {
                str(key): fourth_support_histogram[key]
                for key in sorted(fourth_support_histogram)
            },
            "fifth_pair": {
                str(key): fifth_support_histogram[key]
                for key in sorted(fifth_support_histogram)
            },
        },
        "label_digests": {
            "prefix": label_digest(prefix_labels),
            "fourth_pair_children": label_digest(fourth_child_labels),
            "fifth_pair_children": label_digest(fifth_child_labels),
        },
        "direct_closed_examples": direct_closed_examples,
        "fourth_pair_closed_examples": fourth_closed_examples,
        "fifth_pair_closed_examples": fifth_closed_examples,
        "direct_unclosed_prefixes": direct_unclosed_prefixes,
        "unclosed_fourth_pair_child_branches": unclosed_fourth_children,
        "unclosed_fifth_pair_child_branches": unclosed_fifth_children,
    }


def assert_expected(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise AssertionError("branch_accounting must be an object")
    expected_accounting = {
        "prefix_branch_count": 32,
        "direct_prefix_certified_count": 31,
        "direct_prefix_unclosed_count": 1,
        "fourth_pair_parent_count": 1,
        "fourth_pair_child_branch_count": 132,
        "fourth_pair_child_certified_count": 130,
        "unclosed_fourth_pair_child_branch_count": 2,
        "prefix_parents_closed_by_fourth_refinement": 0,
        "fifth_pair_parent_count": 2,
        "fifth_pair_child_branch_count": 180,
        "fifth_pair_child_certified_count": 180,
        "unclosed_fifth_pair_child_branch_count": 0,
        "fourth_pair_parents_closed_by_fifth_refinement": 2,
        "prefix_parents_closed_by_fifth_refinement": 1,
        "prefix_branches_closed_after_chain": 32,
        "prefix_branches_remaining_after_chain": 0,
        "exhaustive_window_scan": True,
        "exhaustive_all_orders": False,
    }
    for key, expected in expected_accounting.items():
        if accounting[key] != expected:
            raise AssertionError(f"{key} changed: {accounting[key]} != {expected}")

    row_histograms = data["forced_row_count_histograms"]
    if not isinstance(row_histograms, Mapping):
        raise AssertionError("forced row histograms must be an object")
    expected_rows = {
        "direct_prefix": {"910": 32},
        "fourth_pair": {"1932": 132},
        "fifth_pair": {"3300": 180},
    }
    if row_histograms != expected_rows:
        raise AssertionError("forced row histograms changed")

    support_histograms = data["closed_support_size_histograms"]
    if not isinstance(support_histograms, Mapping):
        raise AssertionError("support histograms must be an object")
    expected_support_totals = {
        "direct_prefix": "direct_prefix_certified_count",
        "fourth_pair": "fourth_pair_child_certified_count",
        "fifth_pair": "fifth_pair_child_certified_count",
    }
    for support_key, count_key in expected_support_totals.items():
        histogram = support_histograms[support_key]
        if not isinstance(histogram, Mapping):
            raise AssertionError(f"{support_key} support histogram must be an object")
        if sum(int(count) for count in histogram.values()) != int(accounting[count_key]):
            raise AssertionError(f"{support_key} support histogram total changed")

    direct_unclosed = data["direct_unclosed_prefixes"]
    if not isinstance(direct_unclosed, list) or len(direct_unclosed) != 1:
        raise AssertionError("direct unclosed prefix list changed")
    if direct_unclosed[0]["label"] != "c19_prefix_branch_0156":
        raise AssertionError("direct unclosed prefix changed")

    fourth_unclosed = data["unclosed_fourth_pair_child_branches"]
    if not isinstance(fourth_unclosed, list) or len(fourth_unclosed) != 2:
        raise AssertionError("fourth unclosed child list changed")
    expected_fourth_labels = [
        "c19_window_fourth_child_0156_0063",
        "c19_window_fourth_child_0156_0065",
    ]
    if [row["label"] for row in fourth_unclosed] != expected_fourth_labels:
        raise AssertionError("fourth unclosed child labels changed")

    fifth_unclosed = data["unclosed_fifth_pair_child_branches"]
    if not isinstance(fifth_unclosed, list) or fifth_unclosed:
        raise AssertionError("all fifth-pair children should close")

    digests = data["label_digests"]
    if not isinstance(digests, Mapping):
        raise AssertionError("label digests must be an object")
    expected_digests = {
        "prefix": "9741d59833d730db662ad850c052d53fc880a6599db363e82175ca318729f3e9",
        "fourth_pair_children": "e2fe7d93069dab13d15fe076e4d114db09c0d75420208f89241fccf26bca1225",
        "fifth_pair_children": "75db70d03330d51835ff7974ec1999eeb8307e3fb5347a8416ee37f7467b51b8",
    }
    if digests != expected_digests:
        raise AssertionError("label digests changed")


def print_table(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise TypeError("branch_accounting must be an object")
    print(
        "C19 prefix window: "
        f"closed={accounting['prefix_branches_closed_after_chain']} "
        f"remaining={accounting['prefix_branches_remaining_after_chain']} "
        f"scanned={accounting['prefix_branch_count']}"
    )
    print(
        "subdivision children: "
        f"fourth={accounting['fourth_pair_child_certified_count']}/"
        f"{accounting['fourth_pair_child_branch_count']} "
        f"fifth={accounting['fifth_pair_child_certified_count']}/"
        f"{accounting['fifth_pair_child_branch_count']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-index", type=int, default=DEFAULT_START_INDEX)
    parser.add_argument("--window-size", type=int, default=DEFAULT_WINDOW_SIZE)
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
        help="number of closed certificate examples to store at each depth",
    )
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    data = scan_window(
        start_index=args.start_index,
        window_size=args.window_size,
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
            print("OK: C19 prefix window matched expected sampled chain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
