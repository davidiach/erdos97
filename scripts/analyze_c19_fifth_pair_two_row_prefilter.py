#!/usr/bin/env python3
"""Check a cheap exact two-row Kalmanson prefilter on the C19 fifth frontier.

This diagnostic replays the 7,920 fifth-pair children recorded by the compact
C19 sweep and looks for an LP-free obstruction: either one forced Kalmanson row
is already zero after selected-distance quotienting, or two forced Kalmanson
rows are exact opposites.  Such a one- or two-row positive-integer combination
gives the same strict 0 > 0 contradiction as the larger Farkas certificates,
but it is found by exact vector lookup rather than by an LP.

The report also applies the existing exact Farkas checker to the few children
missed by the two-row lookup.  The scope is only the recorded C19 fifth-pair
frontier; this is not an all-order C19 search and does not settle Erdos
Problem #97.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from analyze_c19_fifth_pair_frontier import (
    _as_list,
    _as_mapping,
    _branch_index,
    _load_sweep,
    _pair_key,
    _prefix_index,
    _source_windows,
    _window_for_prefix,
)
from check_kalmanson_certificate import build_distance_classes
from pilot_c19_kalmanson_prefix_branches import (
    N,
    OFFSETS,
    PATTERN_NAME,
    find_certificate_for_state,
    label_digest,
    prefix_kalmanson_rows,
    state_from_boundary,
)
from refine_c19_kalmanson_sampled_fourth_pair import child_state

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FRONTIER = ROOT / "reports" / "c19_fourth_pair_frontier_classifier.json"
DEFAULT_OUT = ROOT / "reports" / "c19_fifth_pair_two_row_prefilter.json"


def _histogram(counter: Counter[int | str]) -> dict[str, int]:
    def key(value: int | str) -> tuple[int, str]:
        if isinstance(value, int):
            return (0, f"{value:04d}")
        return (1, str(value))

    return {str(item): counter[item] for item in sorted(counter, key=key)}


def _row_payload(row: Any) -> dict[str, object]:
    return {
        "weight": 1,
        "kind": row.kind,
        "quad": list(row.quad),
    }


def _certificate_line(label: str, inequalities: Sequence[Mapping[str, object]]) -> str:
    parts = []
    for item in inequalities:
        quad = ",".join(str(value) for value in item["quad"])
        parts.append(f"{item['weight']}:{item['kind']}:{quad}")
    return f"{label}\t{';'.join(parts)}"


def _certificate_digest(lines: Sequence[str]) -> str:
    payload = "".join(f"{line}\n" for line in lines)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def two_row_certificate_for_state(
    state: Any,
    classes: Mapping[tuple[int, int], int],
) -> tuple[int, list[dict[str, object]]]:
    """Return a deterministic one- or two-row exact certificate if present."""

    rows = prefix_kalmanson_rows(state, classes)
    seen: dict[tuple[int, ...], int] = {}
    for idx, row in enumerate(rows):
        vector = row.vector
        if all(value == 0 for value in vector):
            return len(rows), [_row_payload(row)]
        opposite = tuple(-value for value in vector)
        previous_idx = seen.get(opposite)
        if previous_idx is not None:
            previous = rows[previous_idx]
            if any(a + b != 0 for a, b in zip(previous.vector, vector)):
                raise AssertionError("opposite-row lookup produced a nonzero sum")
            return len(rows), [_row_payload(previous), _row_payload(row)]
        seen.setdefault(vector, idx)
    return len(rows), []


def analyze_two_row_prefilter(
    frontier: Mapping[str, Any],
    *,
    frontier_artifact: str,
) -> dict[str, Any]:
    sweep = _load_sweep(frontier)
    windows = _source_windows(sweep)
    survivor_records = _as_list(frontier["survivor_records"], "survivor_records")
    classes = build_distance_classes(N, OFFSETS)

    fifth_labels: list[str] = []
    certificate_lines: list[str] = []
    sample_certificates: list[dict[str, Any]] = []
    fallback_certificates: list[dict[str, Any]] = []
    fallback_certificate_lines: list[str] = []
    final_unclosed_samples: list[dict[str, Any]] = []
    per_window_labels: dict[tuple[int, int], list[str]] = defaultdict(list)
    per_window_prefilter_certified: Counter[tuple[int, int]] = Counter()
    per_window_final_certified: Counter[tuple[int, int]] = Counter()
    per_prefix_prefilter_certified: Counter[str] = Counter()
    per_prefix_final_certified: Counter[str] = Counter()
    per_prefix_total: Counter[str] = Counter()
    per_fourth_prefilter_certified: Counter[str] = Counter()
    per_fourth_final_certified: Counter[str] = Counter()
    per_fourth_total: Counter[str] = Counter()
    row_count_histogram: Counter[int] = Counter()
    certificate_row_count_histogram: Counter[int] = Counter()
    certificate_kind_histogram: Counter[str] = Counter()
    fallback_support_histogram: Counter[int] = Counter()
    by_fourth_added_pair: Counter[str] = Counter()
    zero_row_count = 0
    two_row_count = 0
    prefilter_miss_count = 0
    fallback_exactified_count = 0
    final_unclosed_count = 0

    for row in survivor_records:
        fourth = _as_mapping(row, "fourth survivor")
        fourth_label = str(fourth["label"])
        prefix_label = str(fourth["prefix_parent_label"])
        prefix_index = _prefix_index(prefix_label)
        window_key = _window_for_prefix(prefix_index, windows)
        fourth_state = state_from_boundary(
            [int(v) for v in fourth["child_boundary_left"]],
            [int(v) for v in fourth["child_boundary_right_reflection_side"]],
        )
        fourth_added_pair = _pair_key(
            int(fourth["added_left"]),
            int(fourth["added_right_reflection_side"]),
        )

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
                per_window_labels[window_key].append(fifth_label)
                per_prefix_total[prefix_label] += 1
                per_fourth_total[fourth_label] += 1
                row_count, inequalities = two_row_certificate_for_state(child, classes)
                row_count_histogram[row_count] += 1
                if not inequalities:
                    prefilter_miss_count += 1
                    fallback_success = False
                    fallback_row_count, fallback_cert, fallback_summary = find_certificate_for_state(
                        label=fifth_label,
                        state=child,
                        classes=classes,
                        tol=1e-9,
                    )
                    if fallback_row_count != row_count:
                        raise AssertionError("fallback row count changed for the same state")
                    if fallback_cert is not None and fallback_summary is not None:
                        fallback_success = True
                        fallback_exactified_count += 1
                        fallback_support_histogram[
                            int(fallback_summary["positive_inequalities"])
                        ] += 1
                        fallback_certificate_lines.append(
                            _certificate_line(
                                fifth_label,
                                _as_list(fallback_cert["inequalities"], "fallback inequalities"),
                            )
                        )
                        fallback_certificates.append(
                            {
                                "label": fifth_label,
                                "prefix_parent_label": prefix_label,
                                "fourth_pair_parent_label": fourth_label,
                                "fifth_added_left": left_label,
                                "fifth_added_right_reflection_side": right_label,
                                "boundary_left": list(child.left),
                                "boundary_right_reflection_side": list(child.right),
                                "certificate_summary": fallback_summary,
                                "certificate": fallback_cert,
                            }
                        )
                    else:
                        final_unclosed_count += 1
                        if len(final_unclosed_samples) < 12:
                            final_unclosed_samples.append(
                                {
                                    "label": fifth_label,
                                    "prefix_parent_label": prefix_label,
                                    "fourth_pair_parent_label": fourth_label,
                                    "fifth_added_left": left_label,
                                    "fifth_added_right_reflection_side": right_label,
                                }
                            )
                    if not fallback_success:
                        fifth_index += 1
                        continue
                    per_window_final_certified[window_key] += 1
                    per_prefix_final_certified[prefix_label] += 1
                    per_fourth_final_certified[fourth_label] += 1
                    fifth_index += 1
                    continue

                if len(inequalities) == 1:
                    zero_row_count += 1
                elif len(inequalities) == 2:
                    two_row_count += 1
                else:
                    raise AssertionError("prefilter emitted a non-small certificate")
                certificate_row_count_histogram[len(inequalities)] += 1
                kind_key = "+".join(str(item["kind"]) for item in inequalities)
                certificate_kind_histogram[kind_key] += 1
                by_fourth_added_pair[fourth_added_pair] += 1
                per_window_prefilter_certified[window_key] += 1
                per_window_final_certified[window_key] += 1
                per_prefix_prefilter_certified[prefix_label] += 1
                per_prefix_final_certified[prefix_label] += 1
                per_fourth_prefilter_certified[fourth_label] += 1
                per_fourth_final_certified[fourth_label] += 1
                certificate_lines.append(_certificate_line(fifth_label, inequalities))
                if len(sample_certificates) < 12:
                    sample_certificates.append(
                        {
                            "label": fifth_label,
                            "prefix_parent_label": prefix_label,
                            "fourth_pair_parent_label": fourth_label,
                            "fifth_added_left": left_label,
                            "fifth_added_right_reflection_side": right_label,
                            "boundary_left": list(child.left),
                            "boundary_right_reflection_side": list(child.right),
                            "forced_inequalities_available": row_count,
                            "inequalities": inequalities,
                        }
                    )
                fifth_index += 1

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
                "source_fifth_pair_child_count": source_count,
                "source_unclosed_fifth_pair_child_count": source_unclosed,
                "prefilter_certified_count": int(per_window_prefilter_certified[key]),
                "prefilter_miss_count": len(labels)
                - int(per_window_prefilter_certified[key]),
                "final_certified_count": int(per_window_final_certified[key]),
                "final_unclosed_count": len(labels) - int(per_window_final_certified[key]),
                "fifth_child_label_digest": generated_digest,
            }
        )

    per_prefix_parent = [
        {
            "prefix_parent_label": label,
            "fifth_pair_child_count": int(per_prefix_total[label]),
            "prefilter_certified_count": int(per_prefix_prefilter_certified[label]),
            "prefilter_miss_count": int(
                per_prefix_total[label] - per_prefix_prefilter_certified[label]
            ),
            "final_certified_count": int(per_prefix_final_certified[label]),
            "final_unclosed_count": int(
                per_prefix_total[label] - per_prefix_final_certified[label]
            ),
        }
        for label in sorted(per_prefix_total)
    ]
    per_fourth_pair_parent = [
        {
            "label": label,
            "branch_index": _branch_index(label),
            "fifth_pair_child_count": int(per_fourth_total[label]),
            "prefilter_certified_count": int(per_fourth_prefilter_certified[label]),
            "prefilter_miss_count": int(
                per_fourth_total[label] - per_fourth_prefilter_certified[label]
            ),
            "final_certified_count": int(per_fourth_final_certified[label]),
            "final_unclosed_count": int(
                per_fourth_total[label] - per_fourth_final_certified[label]
            ),
        }
        for label in sorted(per_fourth_total)
    ]

    top_prefixes = sorted(
        per_prefix_parent,
        key=lambda item: (-int(item["prefilter_certified_count"]), str(item["prefix_parent_label"])),
    )[:12]

    return {
        "type": "c19_fifth_pair_two_row_prefilter_v1",
        "trust": "EXACT_OBSTRUCTION",
        "frontier_artifact": frontier_artifact,
        "source_sweep_artifact": frontier["source_artifact"],
        "source_prefix_label_digest": frontier["source_prefix_label_digest"],
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This checks only the recorded C19 fifth-pair frontier from the compact sweep artifact.",
            "A one-row certificate is a forced Kalmanson inequality whose quotient vector is zero.",
            "A two-row certificate is a pair of forced Kalmanson inequalities whose quotient vectors are exact opposites.",
            "Each listed small certificate is an exact positive-integer strict-inequality contradiction for completions of that one boundary-prefix child.",
            "This does not certify branches beyond the recorded sweep and is not an all-order C19 obstruction.",
        ],
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "aggregate": {
            "fourth_pair_survivor_parent_count": len(survivor_records),
            "fifth_pair_child_count": len(fifth_labels),
            "source_fifth_pair_child_count": total_source_fifth,
            "source_unclosed_fifth_pair_child_count": total_source_unclosed,
            "prefilter_certified_count": len(certificate_lines),
            "prefilter_miss_count": prefilter_miss_count,
            "fallback_exactified_count": fallback_exactified_count,
            "final_certified_count": len(certificate_lines) + fallback_exactified_count,
            "final_unclosed_count": final_unclosed_count,
            "certified_by_zero_row_count": zero_row_count,
            "certified_by_two_row_count": two_row_count,
            "fifth_pair_child_label_digest": label_digest(fifth_labels),
            "two_row_prefilter_certificate_digest": _certificate_digest(certificate_lines),
            "fallback_certificate_digest": _certificate_digest(fallback_certificate_lines),
            "prefix_parent_count_requiring_fifth_pair": len(per_prefix_total),
        },
        "histograms": {
            "forced_row_count": _histogram(row_count_histogram),
            "certificate_row_count": _histogram(certificate_row_count_histogram),
            "certificate_kind_pattern": _histogram(certificate_kind_histogram),
            "fallback_support_size": _histogram(fallback_support_histogram),
            "prefilter_certified_count_by_fourth_added_pair": _histogram(
                by_fourth_added_pair
            ),
        },
        "per_window": per_window,
        "top_prefix_parents_by_prefilter_certified_count": top_prefixes,
        "per_prefix_parent": per_prefix_parent,
        "per_fourth_pair_parent": per_fourth_pair_parent,
        "sample_certificates": sample_certificates,
        "fallback_certificates": fallback_certificates,
        "final_unclosed_samples": final_unclosed_samples,
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
        "prefilter_certified_count": 7917,
        "prefilter_miss_count": 3,
        "fallback_exactified_count": 3,
        "final_certified_count": 7920,
        "final_unclosed_count": 0,
        "certified_by_zero_row_count": 0,
        "certified_by_two_row_count": 7917,
        "fifth_pair_child_label_digest": "33ec807edc96dbd4e529899b34d61f4e57a43798b6d63f31cbac40bd7a3b8033",
        "two_row_prefilter_certificate_digest": "61476c4922821c55986b182a4720280730f97bf78a3b7f1cfb29658331e64b98",
        "prefix_parent_count_requiring_fifth_pair": 33,
    }
    for key, expected in expected_aggregate.items():
        if aggregate[key] != expected:
            raise AssertionError(f"{key} changed: {aggregate[key]} != {expected}")

    histograms = _as_mapping(data["histograms"], "histograms")
    if histograms["forced_row_count"] != {"3300": 7920}:
        raise AssertionError("forced row histogram changed")
    if histograms["certificate_row_count"] != {"2": 7917}:
        raise AssertionError("certificate row-count histogram changed")
    fallback_support_size = _as_mapping(
        histograms["fallback_support_size"],
        "fallback support-size histogram",
    )
    if sum(int(count) for count in fallback_support_size.values()) != int(
        aggregate["fallback_exactified_count"]
    ):
        raise AssertionError("fallback support-size histogram total changed")

    per_window = _as_list(data["per_window"], "per_window")
    expected_windows = [
        (128, 159, 180, 180),
        (160, 191, 630, 630),
        (192, 223, 1350, 1349),
        (224, 255, 810, 810),
        (256, 287, 4950, 4948),
    ]
    for row, expected in zip(per_window, expected_windows):
        window = _as_mapping(row, "window")
        start, end, count, prefilter_count = expected
        if (
            window["start_index"],
            window["end_index"],
            window["prefilter_certified_count"],
            window["prefilter_miss_count"],
            window["final_certified_count"],
            window["final_unclosed_count"],
        ) != (start, end, prefilter_count, count - prefilter_count, count, 0):
            raise AssertionError("per-window prefilter accounting changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier", type=Path, default=DEFAULT_FRONTIER)
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    frontier = _as_mapping(json.loads(args.frontier.read_text(encoding="utf-8")), "frontier")
    data = analyze_two_row_prefilter(
        frontier,
        frontier_artifact=str(args.frontier.relative_to(ROOT))
        if args.frontier.is_absolute() and args.frontier.is_relative_to(ROOT)
        else str(args.frontier),
    )
    if args.assert_expected:
        assert_expected(data)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        aggregate = _as_mapping(data["aggregate"], "aggregate")
        print(
            "C19 fifth-pair two-row prefilter: "
            f"certified={aggregate['prefilter_certified_count']}/"
            f"{aggregate['fifth_pair_child_count']} "
            f"fallback={aggregate['fallback_exactified_count']} "
            f"final_unclosed={aggregate['final_unclosed_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
