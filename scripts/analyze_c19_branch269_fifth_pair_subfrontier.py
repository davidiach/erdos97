#!/usr/bin/env python3
"""Classify the fifth-pair sub-frontier below C19 prefix branch 269.

This is an exact diagnostic over recorded C19 sweep artifacts.  It reconstructs
the ordered fifth-pair child labels below the nine fourth-pair survivors of
`c19_prefix_branch_0269` and checks that the source sweep records no surviving
fifth-pair child in the containing window.  It does not run LPs and does not
certify any new branches.
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
DEFAULT_FRONTIER = ROOT / "reports" / "c19_fourth_pair_frontier_classifier.json"
DEFAULT_OUT = ROOT / "reports" / "c19_branch269_fifth_pair_subfrontier.json"
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


def _relative_gap(label: int, boundary: list[int]) -> int:
    return min(abs(label - entry) for entry in boundary)


def _pair_key(left_label: int, right_label: int) -> str:
    return f"{left_label},{right_label}"


def _load_sweep(frontier: Mapping[str, Any]) -> Mapping[str, Any]:
    source_artifact = Path(str(frontier["source_artifact"]))
    if not source_artifact.is_absolute():
        source_artifact = ROOT / source_artifact
    return _as_mapping(json.loads(source_artifact.read_text(encoding="utf-8")), "sweep")


def _source_window_for_focus(sweep: Mapping[str, Any]) -> Mapping[str, Any]:
    for row in _as_list(sweep["windows"], "windows"):
        window = _as_mapping(row, "window")
        if int(window["start_index"]) <= 269 <= int(window["end_index"]):
            return window
    raise AssertionError("source sweep has no window containing branch 269")


def analyze_subfrontier(frontier: Mapping[str, Any], *, frontier_artifact: str) -> dict[str, Any]:
    focus = _as_mapping(frontier["focus_parent"], "focus_parent")
    if focus["label"] != FOCUS_PARENT:
        raise AssertionError("frontier focus parent changed")

    sweep = _load_sweep(frontier)
    source_window = _source_window_for_focus(sweep)
    source_accounting = _as_mapping(source_window["branch_accounting"], "source accounting")
    if int(source_accounting["unclosed_fifth_pair_child_branch_count"]) != 0:
        raise AssertionError("source sweep now has unclosed fifth-pair children")

    prefix_index = int(focus["branch_index"])
    base_left = [int(v) for v in focus["boundary_left"]]
    base_right = [int(v) for v in focus["boundary_right_reflection_side"]]
    base_state = state_from_boundary(base_left, base_right)

    fifth_labels: list[str] = []
    fifth_records: list[dict[str, Any]] = []
    per_fourth_parent: list[dict[str, Any]] = []
    by_added_left: Counter[int] = Counter()
    by_added_right: Counter[int] = Counter()
    by_added_pair: Counter[str] = Counter()
    by_left_gap_to_fourth: Counter[int] = Counter()
    by_right_gap_to_fourth: Counter[int] = Counter()
    by_fourth_added_pair: Counter[str] = Counter()

    for fourth in _as_list(focus["survivor_pairs"], "focus survivor_pairs"):
        fourth_map = _as_mapping(fourth, "fourth survivor")
        fourth_label = str(fourth_map["label"])
        fourth_added_left = int(fourth_map["added_left"])
        fourth_added_right = int(fourth_map["added_right_reflection_side"])
        fourth_state = child_state(base_state, fourth_added_left, fourth_added_right)
        fourth_boundary_left = list(fourth_state.left)
        fourth_boundary_right = list(fourth_state.right)
        records_for_fourth: list[dict[str, Any]] = []
        fifth_index = 0
        for left_label in fourth_state.remaining:
            after_left = tuple(label for label in fourth_state.remaining if label != left_label)
            for right_label in after_left:
                child = child_state(fourth_state, left_label, right_label)
                fifth_label = (
                    f"c19_window_fifth_child_"
                    f"{prefix_index:04d}_{fourth_label[-4:]}_{fifth_index:04d}"
                )
                fifth_labels.append(fifth_label)
                left_gap_to_fourth = _relative_gap(left_label, fourth_boundary_left)
                right_gap_to_fourth = _relative_gap(right_label, fourth_boundary_right)
                by_added_left[left_label] += 1
                by_added_right[right_label] += 1
                by_added_pair[_pair_key(left_label, right_label)] += 1
                by_left_gap_to_fourth[left_gap_to_fourth] += 1
                by_right_gap_to_fourth[right_gap_to_fourth] += 1
                by_fourth_added_pair[_pair_key(fourth_added_left, fourth_added_right)] += 1
                record = {
                    "label": fifth_label,
                    "prefix_parent_label": FOCUS_PARENT,
                    "fourth_pair_parent_label": fourth_label,
                    "fourth_added_left": fourth_added_left,
                    "fourth_added_right_reflection_side": fourth_added_right,
                    "fifth_added_left": left_label,
                    "fifth_added_right_reflection_side": right_label,
                    "left_gap_to_fourth_boundary": left_gap_to_fourth,
                    "right_gap_to_fourth_boundary": right_gap_to_fourth,
                    "child_boundary_left": list(child.left),
                    "child_boundary_right_reflection_side": list(child.right),
                    "middle_label_count": len(child.remaining),
                }
                fifth_records.append(record)
                records_for_fourth.append(record)
                fifth_index += 1
        per_fourth_parent.append(
            {
                "label": fourth_label,
                "fourth_added_left": fourth_added_left,
                "fourth_added_right_reflection_side": fourth_added_right,
                "fifth_pair_child_count": len(records_for_fourth),
                "fifth_child_label_digest": label_digest(
                    [str(row["label"]) for row in records_for_fourth]
                ),
            }
        )

    fifth_records.sort(key=lambda row: str(row["label"]))
    per_fourth_parent.sort(key=lambda row: str(row["label"]))
    return {
        "type": "c19_branch269_fifth_pair_subfrontier_v1",
        "trust": "EXACT_CERTIFICATE_DIAGNOSTIC",
        "frontier_artifact": frontier_artifact,
        "source_sweep_artifact": frontier["source_artifact"],
        "source_prefix_label_digest": frontier["source_prefix_label_digest"],
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This is an exact fifth-pair sub-frontier classifier below C19 prefix branch 269.",
            "The classifier reconstructs branch labels below the recorded fourth-pair survivors and checks the source sweep records no fifth-pair survivors in the containing window.",
            "It does not run LPs and does not certify branches beyond the source artifact.",
        ],
        "source_window": {
            "start_index": int(source_window["start_index"]),
            "end_index": int(source_window["end_index"]),
            "fifth_pair_child_branch_count": int(
                source_accounting["fifth_pair_child_branch_count"]
            ),
            "fifth_pair_child_certified_count": int(
                source_accounting["fifth_pair_child_certified_count"]
            ),
            "unclosed_fifth_pair_child_branch_count": int(
                source_accounting["unclosed_fifth_pair_child_branch_count"]
            ),
        },
        "focus_parent": {
            "label": FOCUS_PARENT,
            "boundary_left": base_left,
            "boundary_right_reflection_side": base_right,
            "fourth_pair_survivor_count": len(per_fourth_parent),
            "fifth_pair_child_count": len(fifth_records),
            "fifth_pair_child_label_digest": label_digest(fifth_labels),
        },
        "histograms": {
            "fifth_child_count_by_fourth_added_pair": _histogram(by_fourth_added_pair),
            "fifth_survivor_count_by_added_left": _histogram(by_added_left),
            "fifth_survivor_count_by_added_right_reflection_side": _histogram(
                by_added_right
            ),
            "fifth_survivor_count_by_added_pair": _histogram(by_added_pair),
            "left_gap_to_fourth_boundary": _histogram(by_left_gap_to_fourth),
            "right_gap_to_fourth_boundary": _histogram(by_right_gap_to_fourth),
        },
        "per_fourth_pair_parent": per_fourth_parent,
        "fifth_pair_child_record_samples": {
            "first": fifth_records[:12],
            "last": fifth_records[-12:],
        },
    }


def assert_expected(data: Mapping[str, Any]) -> None:
    expected_source_digest = "b18984a2ebd95ffcd6eb2af48fd13c6710b29d9234af18e5966895fa23667879"
    if data["source_prefix_label_digest"] != expected_source_digest:
        raise AssertionError("source digest changed")
    source_window = _as_mapping(data["source_window"], "source_window")
    if (
        source_window["start_index"],
        source_window["end_index"],
        source_window["fifth_pair_child_branch_count"],
        source_window["fifth_pair_child_certified_count"],
        source_window["unclosed_fifth_pair_child_branch_count"],
    ) != (256, 287, 4950, 4950, 0):
        raise AssertionError("source window accounting changed")
    focus = _as_mapping(data["focus_parent"], "focus_parent")
    expected_focus = {
        "label": FOCUS_PARENT,
        "boundary_left": [1, 3, 11],
        "boundary_right_reflection_side": [2, 5, 15],
        "fourth_pair_survivor_count": 9,
        "fifth_pair_child_count": 810,
        "fifth_pair_child_label_digest": "65690f03459851d0f3dafc19d2d0a4a1a6797d4e033f455e39b17810d2e2cf08",
    }
    for key, expected in expected_focus.items():
        if focus[key] != expected:
            raise AssertionError(f"focus {key} changed: {focus[key]} != {expected}")

    per_fourth = _as_list(data["per_fourth_pair_parent"], "per_fourth_pair_parent")
    expected_fourth_labels = [
        "c19_window_fourth_child_0269_0033",
        "c19_window_fourth_child_0269_0035",
        "c19_window_fourth_child_0269_0046",
        "c19_window_fourth_child_0269_0050",
        "c19_window_fourth_child_0269_0057",
        "c19_window_fourth_child_0269_0059",
        "c19_window_fourth_child_0269_0061",
        "c19_window_fourth_child_0269_0110",
        "c19_window_fourth_child_0269_0120",
    ]
    if [row["label"] for row in per_fourth] != expected_fourth_labels:
        raise AssertionError("fourth-pair parent labels changed")
    if any(row["fifth_pair_child_count"] != 90 for row in per_fourth):
        raise AssertionError("fifth child count per fourth parent changed")


def print_table(data: Mapping[str, Any]) -> None:
    focus = _as_mapping(data["focus_parent"], "focus_parent")
    source_window = _as_mapping(data["source_window"], "source_window")
    print(
        "C19 branch 269 fifth-pair sub-frontier: "
        f"fourth_parents={focus['fourth_pair_survivor_count']} "
        f"fifth_children={focus['fifth_pair_child_count']} "
        f"unclosed={source_window['unclosed_fifth_pair_child_branch_count']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier", type=Path, default=DEFAULT_FRONTIER)
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    frontier = json.loads(args.frontier.read_text(encoding="utf-8"))
    try:
        frontier_artifact = args.frontier.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        frontier_artifact = args.frontier.as_posix()
    data = analyze_subfrontier(frontier, frontier_artifact=frontier_artifact)
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
            print("OK: C19 branch 269 fifth-pair sub-frontier matched expected accounting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
