#!/usr/bin/env python3
"""Certify a C19 prefix window with a fifth-pair two-row prefilter.

This is the same prefix/fourth/fifth chain as
certify_c19_kalmanson_prefix_window.py, except fifth-pair child branches first
try the exact two-row Kalmanson lookup from
analyze_c19_fifth_pair_two_row_prefilter.py.  Only prefilter misses call the
ordinary LP/exact Farkas routine.

The default target is the next deterministic C19 window after the recorded
128-287 sweep: branch indices 288 through 319.  This is a bounded sampled
window, not an all-order C19 search.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import islice
from pathlib import Path
from typing import Any, Mapping, Sequence

from analyze_c19_prefilter_catalog_unit_supports import catalog_unit_certificate_for_state
from analyze_c19_fifth_pair_two_row_prefilter import two_row_certificate_for_state
from check_kalmanson_certificate import build_distance_classes
from certify_c19_kalmanson_prefix_window import child_record, state_record
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

DEFAULT_START_INDEX = 288
DEFAULT_WINDOW_SIZE = 32
DEFAULT_CLOSED_EXAMPLE_COUNT = 12


def _histogram(counter: Counter[int | str]) -> dict[str, int]:
    def key(value: int | str) -> tuple[int, str]:
        if isinstance(value, int):
            return (0, f"{value:04d}")
        return (1, str(value))

    return {str(item): counter[item] for item in sorted(counter, key=key)}


def _as_mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{label} must be an object")
    return value


def prefilter_summary(
    *,
    row_count: int,
    inequalities: list[dict[str, object]],
    method: str = "two_row_kalmanson_prefilter",
    catalog_id: str | None = None,
) -> dict[str, object]:
    summary: dict[str, object] = {
        "status": "EXACT_OBSTRUCTION_FOR_PREFIX_BRANCH_COMPLETIONS",
        "method": method,
        "positive_inequalities": len(inequalities),
        "forced_inequalities_available": row_count,
        "weight_sum": len(inequalities),
        "max_weight": 1,
        "zero_sum_verified": True,
        "claim_strength": (
            "Exact obstruction for every completion of this one fixed C19 "
            "boundary-prefix child; not an all-order C19 obstruction."
        ),
    }
    if catalog_id is not None:
        summary["catalog_id"] = catalog_id
    return summary


def scan_window_with_prefilter(
    *,
    start_index: int,
    window_size: int,
    include_certificates: bool,
    closed_example_count: int,
    tol: float,
    catalog_unit_supports: Sequence[Mapping[str, object]] | None = None,
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
    fifth_fallback_support_histogram: Counter[int] = Counter()
    fifth_prefilter_row_histogram: Counter[int] = Counter()
    direct_row_count_histogram: Counter[int] = Counter()
    fourth_row_count_histogram: Counter[int] = Counter()
    fifth_row_count_histogram: Counter[int] = Counter()
    direct_closed_examples: list[dict[str, object]] = []
    fourth_closed_examples: list[dict[str, object]] = []
    fifth_closed_examples: list[dict[str, object]] = []
    fifth_fallback_examples: list[dict[str, object]] = []
    direct_unclosed_prefixes: list[dict[str, object]] = []
    unclosed_fourth_children: list[dict[str, object]] = []
    unclosed_fifth_children: list[dict[str, object]] = []

    direct_closed = 0
    fourth_child_count = 0
    fourth_closed = 0
    fourth_parent_closed = 0
    fifth_child_count = 0
    fifth_closed = 0
    fifth_prefilter_closed = 0
    fifth_two_row_prefilter_closed = 0
    fifth_catalog_prefilter_closed = 0
    fifth_fallback_attempts = 0
    fifth_fallback_closed = 0
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
                    row_count, inequalities = two_row_certificate_for_state(child, classes)
                    fifth_row_count_histogram[row_count] += 1
                    fifth_child_count += 1
                    prefilter_method = "two_row_kalmanson_prefilter"
                    catalog_id = None
                    if not inequalities and catalog_unit_supports is not None:
                        catalog_certificate = catalog_unit_certificate_for_state(
                            child,
                            classes,
                            catalog_unit_supports,
                        )
                        if catalog_certificate is not None:
                            inequalities = [
                                dict(_as_mapping(item, "catalog prefilter row"))
                                for item in catalog_certificate["inequalities"]
                            ]
                            prefilter_method = "cataloged_unit_support_prefilter"
                            catalog_id = str(catalog_certificate["catalog_id"])
                    if inequalities:
                        fifth_closed += 1
                        fifth_prefilter_closed += 1
                        if prefilter_method == "two_row_kalmanson_prefilter":
                            fifth_two_row_prefilter_closed += 1
                        elif prefilter_method == "cataloged_unit_support_prefilter":
                            fifth_catalog_prefilter_closed += 1
                        else:
                            raise AssertionError(f"unknown prefilter method: {prefilter_method}")
                        fifth_prefilter_row_histogram[len(inequalities)] += 1
                        if len(fifth_closed_examples) < closed_example_count:
                            example = dict(record)
                            example["certificate_summary"] = prefilter_summary(
                                row_count=row_count,
                                inequalities=inequalities,
                                method=prefilter_method,
                                catalog_id=catalog_id,
                            )
                            example["prefilter_inequalities"] = inequalities
                            fifth_closed_examples.append(example)
                        fifth_index += 1
                        continue

                    fifth_fallback_attempts += 1
                    fallback_row_count, cert, summary = find_certificate_for_state(
                        label=label,
                        state=child,
                        classes=classes,
                        tol=tol,
                    )
                    if fallback_row_count != row_count:
                        raise AssertionError("fallback row count changed for fifth child")
                    if cert is not None and summary is not None:
                        fifth_closed += 1
                        fifth_fallback_closed += 1
                        fifth_fallback_support_histogram[
                            int(summary["positive_inequalities"])
                        ] += 1
                        if len(fifth_fallback_examples) < closed_example_count:
                            example = dict(record)
                            example["certificate_summary"] = summary
                            if include_certificates:
                                example["certificate"] = cert
                            fifth_fallback_examples.append(example)
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
    fifth_pair_prefilter_name = "two_row_kalmanson_prefilter"
    if catalog_unit_supports is not None:
        fifth_pair_prefilter_name = "two_row_then_cataloged_unit_support"
    branch_accounting: dict[str, object] = {
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
        "fifth_pair_prefilter_certified_count": fifth_prefilter_closed,
        "fifth_pair_farkas_fallback_attempt_count": fifth_fallback_attempts,
        "fifth_pair_farkas_fallback_certified_count": fifth_fallback_closed,
        "unclosed_fifth_pair_child_branch_count": len(unclosed_fifth_children),
        "fourth_pair_parents_closed_by_fifth_refinement": fifth_parent_closed,
        "prefix_parents_closed_by_fifth_refinement": prefix_closed_by_fifth,
        "prefix_branches_closed_after_chain": prefix_closed_after_chain,
        "prefix_branches_remaining_after_chain": prefix_count - prefix_closed_after_chain,
        "exhaustive_window_scan": True,
        "exhaustive_all_orders": False,
    }
    parameters: dict[str, object] = {
        "start_index": start_index,
        "window_size": window_size,
        "boundary_pairs": 3,
        "include_certificates_in_examples": include_certificates,
        "closed_example_count": closed_example_count,
        "lp_support_tolerance": tol,
        "anchor_label": 0,
        "fifth_pair_prefilter": fifth_pair_prefilter_name,
    }
    if catalog_unit_supports is not None:
        parameters["catalog_unit_support_count"] = len(catalog_unit_supports)
        branch_accounting["fifth_pair_two_row_prefilter_certified_count"] = (
            fifth_two_row_prefilter_closed
        )
        branch_accounting["fifth_pair_catalog_prefilter_certified_count"] = (
            fifth_catalog_prefilter_closed
        )
    notes = [
        "No general proof of Erdos Problem #97 is claimed.",
        "No counterexample is claimed.",
        "This certifies only one deterministic C19 three-boundary-prefix window.",
        "Direct and fourth-pair closures use ordinary prefix-forced Kalmanson/Farkas certificates.",
        "Fifth-pair closures first try exact two-row Kalmanson cancellations; only misses use ordinary Farkas fallback.",
        "Unclosed children, if any, are not counterexamples and are not evidence of realizability.",
        "This is not an exhaustive all-order C19 search.",
    ]
    if catalog_unit_supports is not None:
        notes[4] = (
            "Fifth-pair closures first try exact two-row Kalmanson cancellations, "
            "then cataloged unit supports; only misses use ordinary "
            "Farkas fallback."
        )
    return {
        "type": "c19_kalmanson_prefix_window_prefilter_chain_v1",
        "trust": "EXACT_OBSTRUCTION",
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "notes": notes,
        "parameters": parameters,
        "global_prefix_space": {
            "raw_three_boundary_state_count": raw_count,
            "canonical_three_boundary_state_count": canonical_count,
        },
        "branch_accounting": branch_accounting,
        "forced_row_count_histograms": {
            "direct_prefix": _histogram(direct_row_count_histogram),
            "fourth_pair": _histogram(fourth_row_count_histogram),
            "fifth_pair": _histogram(fifth_row_count_histogram),
        },
        "closed_support_size_histograms": {
            "direct_prefix": _histogram(direct_support_histogram),
            "fourth_pair": _histogram(fourth_support_histogram),
            "fifth_pair_prefilter": _histogram(fifth_prefilter_row_histogram),
            "fifth_pair_farkas_fallback": _histogram(fifth_fallback_support_histogram),
        },
        "label_digests": {
            "prefix": label_digest(prefix_labels),
            "fourth_pair_children": label_digest(fourth_child_labels),
            "fifth_pair_children": label_digest(fifth_child_labels),
        },
        "direct_closed_examples": direct_closed_examples,
        "fourth_pair_closed_examples": fourth_closed_examples,
        "fifth_pair_closed_examples": fifth_closed_examples,
        "fifth_pair_farkas_fallback_examples": fifth_fallback_examples,
        "direct_unclosed_prefixes": direct_unclosed_prefixes,
        "unclosed_fourth_pair_child_branches": unclosed_fourth_children,
        "unclosed_fifth_pair_child_branches": unclosed_fifth_children,
    }


def assert_expected(data: Mapping[str, object]) -> None:
    parameters = _as_mapping(data["parameters"], "parameters")
    key = (int(parameters["start_index"]), int(parameters["window_size"]))
    if key == (288, 32):
        assert_expected_288_319(data)
        return
    if key == (320, 32):
        assert_expected_320_351(data)
        return
    if key == (352, 32):
        assert_expected_352_383(data)
        return
    if key == (384, 32):
        assert_expected_384_415(data)
        return
    if key == (416, 32):
        assert_expected_416_447(data)
        return
    if key == (448, 32):
        assert_expected_448_479(data)
        return
    raise AssertionError(f"no expected counts registered for window {key}")


def assert_expected_288_319(data: Mapping[str, object]) -> None:
    accounting = _as_mapping(data["branch_accounting"], "branch_accounting")
    expected_accounting = {
        "prefix_branch_count": 32,
        "direct_prefix_certified_count": 32,
        "direct_prefix_unclosed_count": 0,
        "fourth_pair_child_branch_count": 0,
        "fourth_pair_child_certified_count": 0,
        "unclosed_fourth_pair_child_branch_count": 0,
        "fifth_pair_child_branch_count": 0,
        "fifth_pair_child_certified_count": 0,
        "fifth_pair_prefilter_certified_count": 0,
        "fifth_pair_farkas_fallback_attempt_count": 0,
        "fifth_pair_farkas_fallback_certified_count": 0,
        "unclosed_fifth_pair_child_branch_count": 0,
        "prefix_branches_closed_after_chain": 32,
        "prefix_branches_remaining_after_chain": 0,
        "exhaustive_window_scan": True,
        "exhaustive_all_orders": False,
    }
    for key, expected in expected_accounting.items():
        if accounting[key] != expected:
            raise AssertionError(f"{key} changed: {accounting[key]} != {expected}")
    digests = _as_mapping(data["label_digests"], "label_digests")
    expected_digests = {
        "prefix": "cc83bf55e54627845ea5a3bb9d7588cbe6442d9bf6bdaae0c26ab356beb2dfef",
        "fourth_pair_children": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "fifth_pair_children": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    }
    if digests != expected_digests:
        raise AssertionError("window 288-319 label digests changed")
    rows = _as_mapping(data["forced_row_count_histograms"], "forced_row_count_histograms")
    if rows != {"direct_prefix": {"910": 32}, "fourth_pair": {}, "fifth_pair": {}}:
        raise AssertionError("window 288-319 forced-row histograms changed")


def assert_expected_320_351(data: Mapping[str, object]) -> None:
    accounting = _as_mapping(data["branch_accounting"], "branch_accounting")
    expected_accounting = {
        "prefix_branch_count": 32,
        "direct_prefix_certified_count": 26,
        "direct_prefix_unclosed_count": 6,
        "fourth_pair_child_branch_count": 792,
        "fourth_pair_child_certified_count": 786,
        "unclosed_fourth_pair_child_branch_count": 6,
        "prefix_parents_closed_by_fourth_refinement": 3,
        "fifth_pair_child_branch_count": 540,
        "fifth_pair_child_certified_count": 540,
        "fifth_pair_prefilter_certified_count": 540,
        "fifth_pair_farkas_fallback_attempt_count": 0,
        "fifth_pair_farkas_fallback_certified_count": 0,
        "unclosed_fifth_pair_child_branch_count": 0,
        "fourth_pair_parents_closed_by_fifth_refinement": 6,
        "prefix_parents_closed_by_fifth_refinement": 3,
        "prefix_branches_closed_after_chain": 32,
        "prefix_branches_remaining_after_chain": 0,
        "exhaustive_window_scan": True,
        "exhaustive_all_orders": False,
    }
    for key, expected in expected_accounting.items():
        if accounting[key] != expected:
            raise AssertionError(f"{key} changed: {accounting[key]} != {expected}")
    digests = _as_mapping(data["label_digests"], "label_digests")
    expected_digests = {
        "prefix": "55a45bf59a7a16a4e29d5d4155984eba17d243e0244682cbd3f2f1cd66ea1c81",
        "fourth_pair_children": "c1a6edd266a6180ea2b9240f82a5ebc42a030d791b68a1fc8758fa643abfd5a9",
        "fifth_pair_children": "6ab6c98099e75576601c19e86962d9d7b0c49e2bc77fdbcb3c55ca9c106f43e7",
    }
    if digests != expected_digests:
        raise AssertionError("window 320-351 label digests changed")
    rows = _as_mapping(data["forced_row_count_histograms"], "forced_row_count_histograms")
    expected_rows = {
        "direct_prefix": {"910": 32},
        "fourth_pair": {"1932": 792},
        "fifth_pair": {"3300": 540},
    }
    if rows != expected_rows:
        raise AssertionError("window 320-351 forced-row histograms changed")
    supports = _as_mapping(data["closed_support_size_histograms"], "closed support histograms")
    if supports["fifth_pair_prefilter"] != {"2": 540}:
        raise AssertionError("window 320-351 fifth prefilter histogram changed")
    if supports["fifth_pair_farkas_fallback"] != {}:
        raise AssertionError("window 320-351 should not need fifth fallback")

    direct_unclosed = data["direct_unclosed_prefixes"]
    if not isinstance(direct_unclosed, list):
        raise AssertionError("direct_unclosed_prefixes must be a list")
    expected_direct = [
        "c19_prefix_branch_0338",
        "c19_prefix_branch_0343",
        "c19_prefix_branch_0344",
        "c19_prefix_branch_0348",
        "c19_prefix_branch_0349",
        "c19_prefix_branch_0350",
    ]
    if [row["label"] for row in direct_unclosed] != expected_direct:
        raise AssertionError("window 320-351 direct survivor labels changed")

    fourth_unclosed = data["unclosed_fourth_pair_child_branches"]
    if not isinstance(fourth_unclosed, list):
        raise AssertionError("unclosed_fourth_pair_child_branches must be a list")
    expected_fourth = [
        "c19_window_fourth_child_0338_0063",
        "c19_window_fourth_child_0338_0065",
        "c19_window_fourth_child_0348_0066",
        "c19_window_fourth_child_0348_0073",
        "c19_window_fourth_child_0348_0076",
        "c19_window_fourth_child_0350_0075",
    ]
    if [row["label"] for row in fourth_unclosed] != expected_fourth:
        raise AssertionError("window 320-351 fourth survivor labels changed")


def assert_expected_352_383(data: Mapping[str, object]) -> None:
    accounting = _as_mapping(data["branch_accounting"], "branch_accounting")
    expected_accounting = {
        "prefix_branch_count": 32,
        "direct_prefix_certified_count": 23,
        "direct_prefix_unclosed_count": 9,
        "fourth_pair_child_branch_count": 1188,
        "fourth_pair_child_certified_count": 1180,
        "unclosed_fourth_pair_child_branch_count": 8,
        "prefix_parents_closed_by_fourth_refinement": 5,
        "fifth_pair_child_branch_count": 720,
        "fifth_pair_child_certified_count": 720,
        "fifth_pair_prefilter_certified_count": 720,
        "fifth_pair_farkas_fallback_attempt_count": 0,
        "fifth_pair_farkas_fallback_certified_count": 0,
        "unclosed_fifth_pair_child_branch_count": 0,
        "fourth_pair_parents_closed_by_fifth_refinement": 8,
        "prefix_parents_closed_by_fifth_refinement": 4,
        "prefix_branches_closed_after_chain": 32,
        "prefix_branches_remaining_after_chain": 0,
        "exhaustive_window_scan": True,
        "exhaustive_all_orders": False,
    }
    for key, expected in expected_accounting.items():
        if accounting[key] != expected:
            raise AssertionError(f"{key} changed: {accounting[key]} != {expected}")
    digests = _as_mapping(data["label_digests"], "label_digests")
    expected_digests = {
        "prefix": "b3abe1633018ac764f4403ec50b38de5913e6ae1d80f9146bc4dc9b0d156364b",
        "fourth_pair_children": "f624e0ee444f5ed9cfeb3df205ba5c7a40bc9d3ee44c4c33962004dd55d036aa",
        "fifth_pair_children": "03dea0992a7d673d821075723e01359e65487dfecd5c8141c7b3035ebf7875fb",
    }
    if digests != expected_digests:
        raise AssertionError("window 352-383 label digests changed")
    rows = _as_mapping(data["forced_row_count_histograms"], "forced_row_count_histograms")
    expected_rows = {
        "direct_prefix": {"910": 32},
        "fourth_pair": {"1932": 1188},
        "fifth_pair": {"3300": 720},
    }
    if rows != expected_rows:
        raise AssertionError("window 352-383 forced-row histograms changed")
    supports = _as_mapping(data["closed_support_size_histograms"], "closed support histograms")
    if supports["fifth_pair_prefilter"] != {"2": 720}:
        raise AssertionError("window 352-383 fifth prefilter histogram changed")
    if supports["fifth_pair_farkas_fallback"] != {}:
        raise AssertionError("window 352-383 should not need fifth fallback")

    direct_unclosed = data["direct_unclosed_prefixes"]
    if not isinstance(direct_unclosed, list):
        raise AssertionError("direct_unclosed_prefixes must be a list")
    expected_direct = [
        "c19_prefix_branch_0352",
        "c19_prefix_branch_0357",
        "c19_prefix_branch_0362",
        "c19_prefix_branch_0363",
        "c19_prefix_branch_0364",
        "c19_prefix_branch_0368",
        "c19_prefix_branch_0369",
        "c19_prefix_branch_0374",
        "c19_prefix_branch_0376",
    ]
    if [row["label"] for row in direct_unclosed] != expected_direct:
        raise AssertionError("window 352-383 direct survivor labels changed")

    fourth_unclosed = data["unclosed_fourth_pair_child_branches"]
    if not isinstance(fourth_unclosed, list):
        raise AssertionError("unclosed_fourth_pair_child_branches must be a list")
    expected_fourth = [
        "c19_window_fourth_child_0357_0010",
        "c19_window_fourth_child_0364_0003",
        "c19_window_fourth_child_0364_0119",
        "c19_window_fourth_child_0368_0025",
        "c19_window_fourth_child_0368_0048",
        "c19_window_fourth_child_0368_0115",
        "c19_window_fourth_child_0369_0011",
        "c19_window_fourth_child_0369_0025",
    ]
    if [row["label"] for row in fourth_unclosed] != expected_fourth:
        raise AssertionError("window 352-383 fourth survivor labels changed")


def assert_expected_384_415(data: Mapping[str, object]) -> None:
    accounting = _as_mapping(data["branch_accounting"], "branch_accounting")
    expected_accounting = {
        "prefix_branch_count": 32,
        "direct_prefix_certified_count": 20,
        "direct_prefix_unclosed_count": 12,
        "fourth_pair_child_branch_count": 1584,
        "fourth_pair_child_certified_count": 1569,
        "unclosed_fourth_pair_child_branch_count": 15,
        "prefix_parents_closed_by_fourth_refinement": 4,
        "fifth_pair_child_branch_count": 1350,
        "fifth_pair_child_certified_count": 1350,
        "fifth_pair_prefilter_certified_count": 1350,
        "fifth_pair_farkas_fallback_attempt_count": 0,
        "fifth_pair_farkas_fallback_certified_count": 0,
        "unclosed_fifth_pair_child_branch_count": 0,
        "fourth_pair_parents_closed_by_fifth_refinement": 15,
        "prefix_parents_closed_by_fifth_refinement": 8,
        "prefix_branches_closed_after_chain": 32,
        "prefix_branches_remaining_after_chain": 0,
        "exhaustive_window_scan": True,
        "exhaustive_all_orders": False,
    }
    for key, expected in expected_accounting.items():
        if accounting[key] != expected:
            raise AssertionError(f"{key} changed: {accounting[key]} != {expected}")
    digests = _as_mapping(data["label_digests"], "label_digests")
    expected_digests = {
        "prefix": "e95b6ddab91d2acfc2e3cd12a1defedc685d5dc7b0e82885aa063adf4329c87c",
        "fourth_pair_children": "277a6662622d58e3d89ad827aca8024354116889616e8db4aa6ab69b998c0808",
        "fifth_pair_children": "d5705c5aa1b7db8d4170a7fc18eccf8424887df55b5781688640e5e0ae6e5de0",
    }
    if digests != expected_digests:
        raise AssertionError("window 384-415 label digests changed")
    rows = _as_mapping(data["forced_row_count_histograms"], "forced_row_count_histograms")
    expected_rows = {
        "direct_prefix": {"910": 32},
        "fourth_pair": {"1932": 1584},
        "fifth_pair": {"3300": 1350},
    }
    if rows != expected_rows:
        raise AssertionError("window 384-415 forced-row histograms changed")
    supports = _as_mapping(data["closed_support_size_histograms"], "closed support histograms")
    if supports["fifth_pair_prefilter"] != {"2": 1350}:
        raise AssertionError("window 384-415 fifth prefilter histogram changed")
    if supports["fifth_pair_farkas_fallback"] != {}:
        raise AssertionError("window 384-415 should not need fifth fallback")

    direct_unclosed = data["direct_unclosed_prefixes"]
    if not isinstance(direct_unclosed, list):
        raise AssertionError("direct_unclosed_prefixes must be a list")
    expected_direct = [
        "c19_prefix_branch_0391",
        "c19_prefix_branch_0393",
        "c19_prefix_branch_0395",
        "c19_prefix_branch_0396",
        "c19_prefix_branch_0397",
        "c19_prefix_branch_0403",
        "c19_prefix_branch_0404",
        "c19_prefix_branch_0405",
        "c19_prefix_branch_0406",
        "c19_prefix_branch_0407",
        "c19_prefix_branch_0408",
        "c19_prefix_branch_0412",
    ]
    if [row["label"] for row in direct_unclosed] != expected_direct:
        raise AssertionError("window 384-415 direct survivor labels changed")

    fourth_unclosed = data["unclosed_fourth_pair_child_branches"]
    if not isinstance(fourth_unclosed, list):
        raise AssertionError("unclosed_fourth_pair_child_branches must be a list")
    expected_fourth = [
        "c19_window_fourth_child_0391_0003",
        "c19_window_fourth_child_0391_0046",
        "c19_window_fourth_child_0395_0000",
        "c19_window_fourth_child_0396_0056",
        "c19_window_fourth_child_0403_0045",
        "c19_window_fourth_child_0403_0051",
        "c19_window_fourth_child_0405_0044",
        "c19_window_fourth_child_0406_0044",
        "c19_window_fourth_child_0406_0046",
        "c19_window_fourth_child_0406_0047",
        "c19_window_fourth_child_0406_0051",
        "c19_window_fourth_child_0407_0044",
        "c19_window_fourth_child_0407_0047",
        "c19_window_fourth_child_0407_0051",
        "c19_window_fourth_child_0412_0055",
    ]
    if [row["label"] for row in fourth_unclosed] != expected_fourth:
        raise AssertionError("window 384-415 fourth survivor labels changed")


def assert_expected_416_447(data: Mapping[str, object]) -> None:
    accounting = _as_mapping(data["branch_accounting"], "branch_accounting")
    expected_accounting = {
        "prefix_branch_count": 32,
        "direct_prefix_certified_count": 19,
        "direct_prefix_unclosed_count": 13,
        "fourth_pair_child_branch_count": 1716,
        "fourth_pair_child_certified_count": 1669,
        "unclosed_fourth_pair_child_branch_count": 47,
        "prefix_parents_closed_by_fourth_refinement": 2,
        "fifth_pair_child_branch_count": 4230,
        "fifth_pair_child_certified_count": 4230,
        "fifth_pair_prefilter_certified_count": 4223,
        "fifth_pair_farkas_fallback_attempt_count": 7,
        "fifth_pair_farkas_fallback_certified_count": 7,
        "unclosed_fifth_pair_child_branch_count": 0,
        "fourth_pair_parents_closed_by_fifth_refinement": 47,
        "prefix_parents_closed_by_fifth_refinement": 11,
        "prefix_branches_closed_after_chain": 32,
        "prefix_branches_remaining_after_chain": 0,
        "exhaustive_window_scan": True,
        "exhaustive_all_orders": False,
    }
    for key, expected in expected_accounting.items():
        if accounting[key] != expected:
            raise AssertionError(f"{key} changed: {accounting[key]} != {expected}")
    digests = _as_mapping(data["label_digests"], "label_digests")
    expected_digests = {
        "prefix": "fec4c7e26b7102f187757b7d305f3b8418f8e134489e8d1455e253b0d0536509",
        "fourth_pair_children": "cfe62a882119a7cf20ad51d062e4c99a83bea2655483ae3ec930589f4db106e1",
        "fifth_pair_children": "bbfcd3e9bf8bf86c900df30cc38a6a6918669c791266f85bf6b3c62d7abfe7e9",
    }
    if digests != expected_digests:
        raise AssertionError("window 416-447 label digests changed")
    rows = _as_mapping(data["forced_row_count_histograms"], "forced_row_count_histograms")
    expected_rows = {
        "direct_prefix": {"910": 32},
        "fourth_pair": {"1932": 1716},
        "fifth_pair": {"3300": 4230},
    }
    if rows != expected_rows:
        raise AssertionError("window 416-447 forced-row histograms changed")
    supports = _as_mapping(data["closed_support_size_histograms"], "closed support histograms")
    if supports["fifth_pair_prefilter"] != {"2": 4223}:
        raise AssertionError("window 416-447 fifth prefilter histogram changed")
    expected_fallback = {"7": 1, "8": 1, "19": 1, "47": 1, "52": 1, "54": 1, "58": 1}
    if supports["fifth_pair_farkas_fallback"] != expected_fallback:
        raise AssertionError("window 416-447 fallback histogram changed")

    direct_unclosed = data["direct_unclosed_prefixes"]
    if not isinstance(direct_unclosed, list):
        raise AssertionError("direct_unclosed_prefixes must be a list")
    expected_direct = [
        "c19_prefix_branch_0429",
        "c19_prefix_branch_0430",
        "c19_prefix_branch_0431",
        "c19_prefix_branch_0433",
        "c19_prefix_branch_0434",
        "c19_prefix_branch_0435",
        "c19_prefix_branch_0436",
        "c19_prefix_branch_0439",
        "c19_prefix_branch_0442",
        "c19_prefix_branch_0443",
        "c19_prefix_branch_0444",
        "c19_prefix_branch_0446",
        "c19_prefix_branch_0447",
    ]
    if [row["label"] for row in direct_unclosed] != expected_direct:
        raise AssertionError("window 416-447 direct survivor labels changed")

    fallback_examples = data["fifth_pair_farkas_fallback_examples"]
    if not isinstance(fallback_examples, list):
        raise AssertionError("fallback examples must be a list")
    expected_fallback_labels = [
        "c19_window_fifth_child_0430_0081_0011",
        "c19_window_fifth_child_0434_0070_0021",
        "c19_window_fifth_child_0435_0078_0012",
        "c19_window_fifth_child_0435_0078_0085",
        "c19_window_fifth_child_0435_0083_0022",
        "c19_window_fifth_child_0436_0082_0022",
        "c19_window_fifth_child_0436_0083_0022",
    ]
    if [row["label"] for row in fallback_examples] != expected_fallback_labels:
        raise AssertionError("window 416-447 fallback labels changed")


def assert_expected_448_479(data: Mapping[str, object]) -> None:
    accounting = _as_mapping(data["branch_accounting"], "branch_accounting")
    expected_accounting = {
        "prefix_branch_count": 32,
        "direct_prefix_certified_count": 16,
        "direct_prefix_unclosed_count": 16,
        "fourth_pair_child_branch_count": 2112,
        "fourth_pair_child_certified_count": 2073,
        "unclosed_fourth_pair_child_branch_count": 39,
        "prefix_parents_closed_by_fourth_refinement": 3,
        "fifth_pair_child_branch_count": 3510,
        "fifth_pair_child_certified_count": 3510,
        "fifth_pair_prefilter_certified_count": 3509,
        "fifth_pair_farkas_fallback_attempt_count": 1,
        "fifth_pair_farkas_fallback_certified_count": 1,
        "unclosed_fifth_pair_child_branch_count": 0,
        "fourth_pair_parents_closed_by_fifth_refinement": 39,
        "prefix_parents_closed_by_fifth_refinement": 13,
        "prefix_branches_closed_after_chain": 32,
        "prefix_branches_remaining_after_chain": 0,
        "exhaustive_window_scan": True,
        "exhaustive_all_orders": False,
    }
    for key, expected in expected_accounting.items():
        if accounting[key] != expected:
            raise AssertionError(f"{key} changed: {accounting[key]} != {expected}")
    digests = _as_mapping(data["label_digests"], "label_digests")
    expected_digests = {
        "prefix": "08f9153dbc2a36397525a0800d0427b532874651401199d236dd24c26f2001be",
        "fourth_pair_children": "05d0de33b3f793e81d35433a2d52c432396a4e7c9096aeef0bce85309e71cb60",
        "fifth_pair_children": "78b0380c84676cf1f336898277e8f0f5c683ac2d958ea34c0410eb00623a0da6",
    }
    if digests != expected_digests:
        raise AssertionError("window 448-479 label digests changed")
    rows = _as_mapping(data["forced_row_count_histograms"], "forced_row_count_histograms")
    expected_rows = {
        "direct_prefix": {"910": 32},
        "fourth_pair": {"1932": 2112},
        "fifth_pair": {"3300": 3510},
    }
    if rows != expected_rows:
        raise AssertionError("window 448-479 forced-row histograms changed")
    supports = _as_mapping(data["closed_support_size_histograms"], "closed support histograms")
    if supports["fifth_pair_prefilter"] != {"2": 3509}:
        raise AssertionError("window 448-479 fifth prefilter histogram changed")
    if supports["fifth_pair_farkas_fallback"] != {"50": 1}:
        raise AssertionError("window 448-479 fallback histogram changed")

    direct_unclosed = data["direct_unclosed_prefixes"]
    if not isinstance(direct_unclosed, list):
        raise AssertionError("direct_unclosed_prefixes must be a list")
    expected_direct = [
        "c19_prefix_branch_0448",
        "c19_prefix_branch_0451",
        "c19_prefix_branch_0454",
        "c19_prefix_branch_0456",
        "c19_prefix_branch_0457",
        "c19_prefix_branch_0460",
        "c19_prefix_branch_0461",
        "c19_prefix_branch_0462",
        "c19_prefix_branch_0464",
        "c19_prefix_branch_0465",
        "c19_prefix_branch_0467",
        "c19_prefix_branch_0470",
        "c19_prefix_branch_0472",
        "c19_prefix_branch_0474",
        "c19_prefix_branch_0475",
        "c19_prefix_branch_0477",
    ]
    if [row["label"] for row in direct_unclosed] != expected_direct:
        raise AssertionError("window 448-479 direct survivor labels changed")

    fallback_examples = data["fifth_pair_farkas_fallback_examples"]
    if not isinstance(fallback_examples, list):
        raise AssertionError("fallback examples must be a list")
    if [row["label"] for row in fallback_examples] != [
        "c19_window_fifth_child_0456_0059_0041"
    ]:
        raise AssertionError("window 448-479 fallback labels changed")


def print_table(data: Mapping[str, object]) -> None:
    accounting = _as_mapping(data["branch_accounting"], "branch_accounting")
    print(
        "C19 prefix window with fifth-pair prefilter: "
        f"closed={accounting['prefix_branches_closed_after_chain']} "
        f"remaining={accounting['prefix_branches_remaining_after_chain']} "
        f"scanned={accounting['prefix_branch_count']}"
    )
    print(
        "subdivision children: "
        f"fourth={accounting['fourth_pair_child_certified_count']}/"
        f"{accounting['fourth_pair_child_branch_count']} "
        f"fifth={accounting['fifth_pair_child_certified_count']}/"
        f"{accounting['fifth_pair_child_branch_count']} "
        f"prefilter={accounting['fifth_pair_prefilter_certified_count']} "
        f"fallback={accounting['fifth_pair_farkas_fallback_certified_count']}/"
        f"{accounting['fifth_pair_farkas_fallback_attempt_count']}"
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
        help="include full Farkas certificates for stored closed fallback examples",
    )
    parser.add_argument(
        "--closed-example-count",
        type=int,
        default=DEFAULT_CLOSED_EXAMPLE_COUNT,
        help="number of closed certificate examples to store at each depth",
    )
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    data = scan_window_with_prefilter(
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
