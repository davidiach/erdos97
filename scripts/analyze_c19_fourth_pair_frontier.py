#!/usr/bin/env python3
"""Classify fourth-pair frontier records in the compact C19 sweep artifact.

This is an exact diagnostic over recorded sweep data.  It reconstructs the
ordered fourth-pair child labels below every direct prefix survivor and marks
the children that required fifth-pair subdivision in the source artifact.  It
does not run LPs and does not certify any new branches.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from pilot_c19_kalmanson_prefix_branches import label_digest, state_from_boundary
from refine_c19_kalmanson_sampled_fourth_pair import child_state

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data" / "certificates" / "c19_kalmanson_prefix_window_sweep_128_287.json"
DEFAULT_OUT = ROOT / "reports" / "c19_fourth_pair_frontier_classifier.json"
FOCUS_PARENT = "c19_prefix_branch_0269"


def _as_mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{label} must be an object")
    return value


def _as_list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise TypeError(f"{label} must be a list")
    return value


def _histogram(counter: Counter[int | str]) -> dict[str, int]:
    def key(value: int | str) -> tuple[int, str]:
        if isinstance(value, int):
            return (0, f"{value:04d}")
        return (1, str(value))

    return {str(item): counter[item] for item in sorted(counter, key=key)}


def _branch_index(label: str) -> int:
    return int(label.rsplit("_", 1)[1])


def _pair_key(left_label: int, right_label: int) -> str:
    return f"{left_label},{right_label}"


def _relative_gap(label: int, boundary: list[int]) -> int:
    return min(abs(label - entry) for entry in boundary)


def _window_records(payload: Mapping[str, Any]) -> tuple[list[Mapping[str, Any]], set[str]]:
    windows = _as_list(payload["windows"], "windows")
    direct_survivors: list[Mapping[str, Any]] = []
    fourth_survivor_labels: set[str] = set()
    for window in windows:
        window_map = _as_mapping(window, "window")
        for row in _as_list(window_map["direct_survivors"], "direct_survivors"):
            direct_survivors.append(_as_mapping(row, "direct survivor"))
        for row in _as_list(window_map["fourth_pair_survivors"], "fourth_pair_survivors"):
            row_map = _as_mapping(row, "fourth survivor")
            fourth_survivor_labels.add(str(row_map["label"]))
    return direct_survivors, fourth_survivor_labels


def analyze_frontier(payload: Mapping[str, Any], *, source_artifact: str) -> dict[str, Any]:
    direct_survivors, fourth_survivor_labels = _window_records(payload)

    all_child_labels: list[str] = []
    generated_survivor_labels: set[str] = set()
    per_parent_records: list[dict[str, Any]] = []
    survivor_records: list[dict[str, Any]] = []
    survivor_count_by_added_left: Counter[int] = Counter()
    survivor_count_by_added_right: Counter[int] = Counter()
    survivor_count_by_added_pair: Counter[str] = Counter()
    survivor_count_by_left_gap: Counter[int] = Counter()
    survivor_count_by_right_gap: Counter[int] = Counter()
    survivor_count_by_parent: Counter[str] = Counter()

    for parent in direct_survivors:
        parent_label = str(parent["label"])
        prefix_index = _branch_index(parent_label)
        boundary_left = [int(v) for v in parent["boundary_left"]]
        boundary_right = [int(v) for v in parent["boundary_right_reflection_side"]]
        state = state_from_boundary(boundary_left, boundary_right)
        child_count = 0
        survivor_count = 0
        parent_survivor_pairs: list[dict[str, int | str]] = []
        fourth_index = 0
        for left_label in state.remaining:
            after_left = tuple(label for label in state.remaining if label != left_label)
            for right_label in after_left:
                child = child_state(state, left_label, right_label)
                child_label = f"c19_window_fourth_child_{prefix_index:04d}_{fourth_index:04d}"
                all_child_labels.append(child_label)
                child_count += 1
                if child_label in fourth_survivor_labels:
                    survivor_count += 1
                    generated_survivor_labels.add(child_label)
                    left_gap = _relative_gap(left_label, boundary_left)
                    right_gap = _relative_gap(right_label, boundary_right)
                    pair_key = _pair_key(left_label, right_label)
                    survivor_count_by_added_left[left_label] += 1
                    survivor_count_by_added_right[right_label] += 1
                    survivor_count_by_added_pair[pair_key] += 1
                    survivor_count_by_left_gap[left_gap] += 1
                    survivor_count_by_right_gap[right_gap] += 1
                    survivor_count_by_parent[parent_label] += 1
                    record = {
                        "label": child_label,
                        "prefix_parent_label": parent_label,
                        "added_left": left_label,
                        "added_right_reflection_side": right_label,
                        "left_gap_to_parent_boundary": left_gap,
                        "right_gap_to_parent_boundary": right_gap,
                        "child_boundary_left": list(child.left),
                        "child_boundary_right_reflection_side": list(child.right),
                        "middle_label_count": len(child.remaining),
                    }
                    survivor_records.append(record)
                    parent_survivor_pairs.append(
                        {
                            "label": child_label,
                            "added_left": left_label,
                            "added_right_reflection_side": right_label,
                            "left_gap_to_parent_boundary": left_gap,
                            "right_gap_to_parent_boundary": right_gap,
                        }
                    )
                fourth_index += 1
        per_parent_records.append(
            {
                "label": parent_label,
                "branch_index": prefix_index,
                "boundary_left": boundary_left,
                "boundary_right_reflection_side": boundary_right,
                "fourth_pair_child_attempt_count": child_count,
                "fourth_pair_survivor_count": survivor_count,
                "fifth_pair_child_attempt_count": survivor_count * 90,
                "closed_by_fourth_pair_only": survivor_count == 0,
                "survivor_pairs": parent_survivor_pairs,
            }
        )

    missing = sorted(fourth_survivor_labels - generated_survivor_labels)
    unexpected = sorted(generated_survivor_labels - fourth_survivor_labels)
    if missing or unexpected:
        raise AssertionError(
            f"generated survivor labels do not match artifact: missing={missing} unexpected={unexpected}"
        )

    per_parent_records.sort(key=lambda row: int(row["branch_index"]))
    survivor_records.sort(key=lambda row: str(row["label"]))
    top_parents = sorted(
        per_parent_records,
        key=lambda row: (
            -int(row["fourth_pair_survivor_count"]),
            int(row["branch_index"]),
        ),
    )[:12]
    focus_parent = next(row for row in per_parent_records if row["label"] == FOCUS_PARENT)

    return {
        "type": "c19_fourth_pair_frontier_classifier_v1",
        "trust": "EXACT_CERTIFICATE_DIAGNOSTIC",
        "source_artifact": source_artifact,
        "source_type": payload["type"],
        "source_prefix_label_digest": payload["prefix_label_digest"],
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This is an exact fourth-pair frontier classifier over the recorded sweep artifact.",
            "The classifier reconstructs branch labels and marks which fourth-pair children required fifth-pair subdivision.",
            "It does not run LPs and does not certify branches beyond the source artifact.",
        ],
        "aggregate": {
            "direct_survivor_parent_count": len(direct_survivors),
            "fourth_pair_child_attempt_count": len(all_child_labels),
            "fourth_pair_survivor_count": len(fourth_survivor_labels),
            "fourth_pair_children_closed_by_fourth_pair_count": len(all_child_labels)
            - len(fourth_survivor_labels),
            "parents_requiring_fifth_pair_count": sum(
                1 for row in per_parent_records if row["fourth_pair_survivor_count"]
            ),
            "parents_closed_by_fourth_pair_only_count": sum(
                1 for row in per_parent_records if not row["fourth_pair_survivor_count"]
            ),
            "all_fourth_pair_child_label_digest": label_digest(all_child_labels),
            "fourth_pair_survivor_label_digest": label_digest(sorted(fourth_survivor_labels)),
        },
        "histograms": {
            "fourth_pair_survivors_per_parent": _histogram(survivor_count_by_parent),
            "survivor_count_by_added_left": _histogram(survivor_count_by_added_left),
            "survivor_count_by_added_right_reflection_side": _histogram(
                survivor_count_by_added_right
            ),
            "survivor_count_by_added_pair": _histogram(survivor_count_by_added_pair),
            "survivor_count_by_left_gap_to_parent_boundary": _histogram(
                survivor_count_by_left_gap
            ),
            "survivor_count_by_right_gap_to_parent_boundary": _histogram(
                survivor_count_by_right_gap
            ),
        },
        "focus_parent_label": FOCUS_PARENT,
        "focus_parent": focus_parent,
        "top_parents_by_fourth_pair_survivor_count": top_parents,
        "survivor_records": survivor_records,
        "per_parent_frontier": per_parent_records,
    }


def assert_expected(data: Mapping[str, Any]) -> None:
    expected_digest = "b18984a2ebd95ffcd6eb2af48fd13c6710b29d9234af18e5966895fa23667879"
    if data["source_prefix_label_digest"] != expected_digest:
        raise AssertionError("source digest changed")
    aggregate = _as_mapping(data["aggregate"], "aggregate")
    expected_aggregate = {
        "direct_survivor_parent_count": 48,
        "fourth_pair_child_attempt_count": 6336,
        "fourth_pair_survivor_count": 88,
        "fourth_pair_children_closed_by_fourth_pair_count": 6248,
        "parents_requiring_fifth_pair_count": 33,
        "parents_closed_by_fourth_pair_only_count": 15,
        "all_fourth_pair_child_label_digest": "63c4cfe44978752598f66ba946f747e4509c3d3fa85b2ffb662317126ebacc0a",
        "fourth_pair_survivor_label_digest": "0c6073d4ef3cc32705263a3bbc0bcaa98c1d644fe81a6e067864a8e4a618be8c",
    }
    for key, expected in expected_aggregate.items():
        if aggregate[key] != expected:
            raise AssertionError(f"{key} changed: {aggregate[key]} != {expected}")

    focus_parent = _as_mapping(data["focus_parent"], "focus_parent")
    if (
        focus_parent["label"],
        focus_parent["fourth_pair_survivor_count"],
        focus_parent["fifth_pair_child_attempt_count"],
    ) != (FOCUS_PARENT, 9, 810):
        raise AssertionError("focus parent changed")
    expected_focus_pairs = [
        (8, 4),
        (8, 7),
        (9, 7),
        (9, 13),
        (10, 7),
        (10, 9),
        (10, 13),
        (17, 4),
        (17, 18),
    ]
    observed_focus_pairs = [
        (int(row["added_left"]), int(row["added_right_reflection_side"]))
        for row in _as_list(focus_parent["survivor_pairs"], "focus survivor_pairs")
    ]
    if observed_focus_pairs != expected_focus_pairs:
        raise AssertionError("focus parent survivor pairs changed")


def print_table(data: Mapping[str, Any]) -> None:
    aggregate = _as_mapping(data["aggregate"], "aggregate")
    focus_parent = _as_mapping(data["focus_parent"], "focus_parent")
    print(
        "C19 fourth-pair frontier classifier: "
        f"parents={aggregate['direct_survivor_parent_count']} "
        f"children={aggregate['fourth_pair_child_attempt_count']} "
        f"survivors={aggregate['fourth_pair_survivor_count']}"
    )
    print(
        "focus parent: "
        f"{focus_parent['label']} "
        f"survivors={focus_parent['fourth_pair_survivor_count']} "
        f"fifth_children={focus_parent['fifth_pair_child_attempt_count']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    payload = json.loads(args.source.read_text(encoding="utf-8"))
    try:
        source_artifact = args.source.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        source_artifact = args.source.as_posix()
    data = analyze_frontier(payload, source_artifact=source_artifact)
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
            print("OK: C19 fourth-pair frontier classifier matched expected accounting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
