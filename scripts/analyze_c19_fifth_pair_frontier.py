#!/usr/bin/env python3
"""Classify the recorded C19 fifth-pair frontier.

This exact diagnostic reconstructs fifth-pair child labels below every
fourth-pair survivor recorded by the compact C19 sweep.  It compares the
generated per-window fifth-child digests against the source sweep artifact and
checks that the source records no fifth-pair survivors.  It does not run LPs
and does not certify any new branches.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

from pilot_c19_kalmanson_prefix_branches import label_digest, state_from_boundary
from refine_c19_kalmanson_sampled_fourth_pair import child_state

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FRONTIER = ROOT / "reports" / "c19_fourth_pair_frontier_classifier.json"
DEFAULT_OUT = ROOT / "reports" / "c19_fifth_pair_frontier_classifier.json"


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


def _prefix_index(label: str) -> int:
    # c19_prefix_branch_0269
    return int(label.rsplit("_", 1)[1])


def _pair_key(left_label: int, right_label: int) -> str:
    return f"{left_label},{right_label}"


def _relative_gap(label: int, boundary: list[int]) -> int:
    return min(abs(label - entry) for entry in boundary)


def _load_sweep(frontier: Mapping[str, Any]) -> Mapping[str, Any]:
    source_artifact = Path(str(frontier["source_artifact"]))
    if not source_artifact.is_absolute():
        source_artifact = ROOT / source_artifact
    return _as_mapping(json.loads(source_artifact.read_text(encoding="utf-8")), "sweep")


def _source_windows(sweep: Mapping[str, Any]) -> dict[tuple[int, int], Mapping[str, Any]]:
    windows: dict[tuple[int, int], Mapping[str, Any]] = {}
    for row in _as_list(sweep["windows"], "windows"):
        window = _as_mapping(row, "window")
        windows[(int(window["start_index"]), int(window["end_index"]))] = window
    return windows


def _window_for_prefix(index: int, windows: Mapping[tuple[int, int], Mapping[str, Any]]) -> tuple[int, int]:
    for start, end in windows:
        if start <= index <= end:
            return (start, end)
    raise AssertionError(f"no source window contains prefix {index}")


def analyze_fifth_frontier(frontier: Mapping[str, Any], *, frontier_artifact: str) -> dict[str, Any]:
    sweep = _load_sweep(frontier)
    windows = _source_windows(sweep)
    survivor_records = _as_list(frontier["survivor_records"], "survivor_records")

    fifth_labels: list[str] = []
    fifth_records: list[dict[str, Any]] = []
    per_fourth_parent: list[dict[str, Any]] = []
    per_prefix_parent_counter: Counter[str] = Counter()
    per_window_labels: dict[tuple[int, int], list[str]] = defaultdict(list)
    by_fourth_added_pair: Counter[str] = Counter()
    by_fifth_added_left: Counter[int] = Counter()
    by_fifth_added_right: Counter[int] = Counter()
    by_fifth_added_pair: Counter[str] = Counter()
    by_left_gap_to_fourth: Counter[int] = Counter()
    by_right_gap_to_fourth: Counter[int] = Counter()

    for row in survivor_records:
        fourth = _as_mapping(row, "fourth survivor")
        fourth_label = str(fourth["label"])
        prefix_label = str(fourth["prefix_parent_label"])
        prefix_index = _prefix_index(prefix_label)
        window_key = _window_for_prefix(prefix_index, windows)
        fourth_left = [int(v) for v in fourth["child_boundary_left"]]
        fourth_right = [int(v) for v in fourth["child_boundary_right_reflection_side"]]
        fourth_state = state_from_boundary(fourth_left, fourth_right)
        fourth_pair = _pair_key(
            int(fourth["added_left"]),
            int(fourth["added_right_reflection_side"]),
        )
        labels_for_fourth: list[str] = []
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
                labels_for_fourth.append(fifth_label)
                per_window_labels[window_key].append(fifth_label)
                per_prefix_parent_counter[prefix_label] += 1
                by_fourth_added_pair[fourth_pair] += 1
                by_fifth_added_left[left_label] += 1
                by_fifth_added_right[right_label] += 1
                by_fifth_added_pair[_pair_key(left_label, right_label)] += 1
                left_gap = _relative_gap(left_label, fourth_left)
                right_gap = _relative_gap(right_label, fourth_right)
                by_left_gap_to_fourth[left_gap] += 1
                by_right_gap_to_fourth[right_gap] += 1
                fifth_records.append(
                    {
                        "label": fifth_label,
                        "prefix_parent_label": prefix_label,
                        "fourth_pair_parent_label": fourth_label,
                        "fourth_added_left": int(fourth["added_left"]),
                        "fourth_added_right_reflection_side": int(
                            fourth["added_right_reflection_side"]
                        ),
                        "fifth_added_left": left_label,
                        "fifth_added_right_reflection_side": right_label,
                        "left_gap_to_fourth_boundary": left_gap,
                        "right_gap_to_fourth_boundary": right_gap,
                        "child_boundary_left": list(child.left),
                        "child_boundary_right_reflection_side": list(child.right),
                        "middle_label_count": len(child.remaining),
                    }
                )
                fifth_index += 1
        per_fourth_parent.append(
            {
                "label": fourth_label,
                "prefix_parent_label": prefix_label,
                "branch_index": _branch_index(fourth_label),
                "fourth_added_pair": fourth_pair,
                "fifth_pair_child_count": len(labels_for_fourth),
                "fifth_child_label_digest": label_digest(labels_for_fourth),
            }
        )

    per_fourth_parent.sort(key=lambda item: str(item["label"]))
    fifth_records.sort(key=lambda item: str(item["label"]))
    per_window: list[dict[str, Any]] = []
    total_source_fifth = 0
    total_source_unclosed = 0
    for key in sorted(windows):
        window = windows[key]
        accounting = _as_mapping(window["branch_accounting"], "branch_accounting")
        labels = per_window_labels.get(key, [])
        source_digest = str(_as_mapping(window["label_digests"], "label_digests")["fifth_pair_children"])
        generated_digest = label_digest(labels)
        if generated_digest != source_digest:
            raise AssertionError(f"fifth-pair label digest changed for window {key}")
        source_count = int(accounting["fifth_pair_child_branch_count"])
        source_unclosed = int(accounting["unclosed_fifth_pair_child_branch_count"])
        if len(labels) != source_count:
            raise AssertionError(f"fifth-pair label count changed for window {key}")
        total_source_fifth += source_count
        total_source_unclosed += source_unclosed
        per_window.append(
            {
                "start_index": key[0],
                "end_index": key[1],
                "fifth_pair_child_count": len(labels),
                "source_fifth_pair_child_count": source_count,
                "source_unclosed_fifth_pair_child_count": source_unclosed,
                "fifth_child_label_digest": generated_digest,
            }
        )

    top_prefixes = sorted(
        (
            {"prefix_parent_label": label, "fifth_pair_child_count": count}
            for label, count in per_prefix_parent_counter.items()
        ),
        key=lambda row: (-int(row["fifth_pair_child_count"]), str(row["prefix_parent_label"])),
    )[:12]

    return {
        "type": "c19_fifth_pair_frontier_classifier_v1",
        "trust": "EXACT_CERTIFICATE_DIAGNOSTIC",
        "frontier_artifact": frontier_artifact,
        "source_sweep_artifact": frontier["source_artifact"],
        "source_prefix_label_digest": frontier["source_prefix_label_digest"],
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This is an exact fifth-pair frontier classifier over the recorded sweep artifact.",
            "The classifier reconstructs branch labels below recorded fourth-pair survivors and compares per-window digests against the source sweep.",
            "It does not run LPs and does not certify branches beyond the source artifact.",
        ],
        "aggregate": {
            "fourth_pair_survivor_parent_count": len(survivor_records),
            "fifth_pair_child_count": len(fifth_labels),
            "source_fifth_pair_child_count": total_source_fifth,
            "source_unclosed_fifth_pair_child_count": total_source_unclosed,
            "fifth_pair_child_label_digest": label_digest(fifth_labels),
            "prefix_parent_count_requiring_fifth_pair": len(per_prefix_parent_counter),
        },
        "histograms": {
            "fifth_child_count_by_fourth_added_pair": _histogram(by_fourth_added_pair),
            "fifth_child_count_by_added_left": _histogram(by_fifth_added_left),
            "fifth_child_count_by_added_right_reflection_side": _histogram(
                by_fifth_added_right
            ),
            "fifth_child_count_by_added_pair": _histogram(by_fifth_added_pair),
            "left_gap_to_fourth_boundary": _histogram(by_left_gap_to_fourth),
            "right_gap_to_fourth_boundary": _histogram(by_right_gap_to_fourth),
        },
        "per_window": per_window,
        "top_prefix_parents_by_fifth_pair_child_count": top_prefixes,
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
    aggregate = _as_mapping(data["aggregate"], "aggregate")
    expected_aggregate = {
        "fourth_pair_survivor_parent_count": 88,
        "fifth_pair_child_count": 7920,
        "source_fifth_pair_child_count": 7920,
        "source_unclosed_fifth_pair_child_count": 0,
        "fifth_pair_child_label_digest": "33ec807edc96dbd4e529899b34d61f4e57a43798b6d63f31cbac40bd7a3b8033",
        "prefix_parent_count_requiring_fifth_pair": 33,
    }
    for key, expected in expected_aggregate.items():
        if aggregate[key] != expected:
            raise AssertionError(f"{key} changed: {aggregate[key]} != {expected}")
    top_prefixes = _as_list(
        data["top_prefix_parents_by_fifth_pair_child_count"],
        "top_prefix_parents_by_fifth_pair_child_count",
    )
    expected_top = [
        ("c19_prefix_branch_0269", 810),
        ("c19_prefix_branch_0278", 630),
        ("c19_prefix_branch_0260", 450),
    ]
    observed_top = [
        (row["prefix_parent_label"], row["fifth_pair_child_count"])
        for row in top_prefixes[:3]
    ]
    if observed_top != expected_top:
        raise AssertionError("top prefix parents changed")


def print_table(data: Mapping[str, Any]) -> None:
    aggregate = _as_mapping(data["aggregate"], "aggregate")
    top = _as_list(
        data["top_prefix_parents_by_fifth_pair_child_count"],
        "top_prefix_parents_by_fifth_pair_child_count",
    )[0]
    print(
        "C19 fifth-pair frontier classifier: "
        f"fourth_parents={aggregate['fourth_pair_survivor_parent_count']} "
        f"fifth_children={aggregate['fifth_pair_child_count']} "
        f"unclosed={aggregate['source_unclosed_fifth_pair_child_count']}"
    )
    print(
        "top prefix: "
        f"{top['prefix_parent_label']} fifth_children={top['fifth_pair_child_count']}"
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
        frontier_artifact = str(args.frontier.resolve().relative_to(ROOT))
    except ValueError:
        frontier_artifact = str(args.frontier)
    data = analyze_fifth_frontier(frontier, frontier_artifact=frontier_artifact)
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
            print("OK: C19 fifth-pair frontier classifier matched expected accounting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
