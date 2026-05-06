#!/usr/bin/env python3
"""Analyze exact fallback supports in the C19 prefilter-window sweep.

The compact prefilter sweep closes most fifth-pair children by an exact two-row
Kalmanson lookup.  This diagnostic reconstructs only the children that missed
that lookup, verifies that they are still exact Farkas obstructions, and records
their support sizes and full certificates.

This is a diagnostic over recorded sampled windows.  It is not an all-order C19
search and does not settle Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

from analyze_c19_fifth_pair_two_row_prefilter import two_row_certificate_for_state
from check_kalmanson_certificate import build_distance_classes
from pilot_c19_kalmanson_prefix_branches import (
    N,
    OFFSETS,
    PATTERN_NAME,
    BoundaryState,
    check_prefix_certificate_dict,
    find_certificate_for_state,
    label_digest,
    state_from_boundary,
)
from refine_c19_kalmanson_sampled_fourth_pair import child_state

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "certificates"
    / "c19_kalmanson_prefix_window_prefilter_sweep_288_479.json"
)
DEFAULT_OUT = ROOT / "reports" / "c19_prefilter_fallback_supports.json"


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


def _prefix_index(label: str) -> int:
    try:
        return int(label.rsplit("_", 1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"bad prefix label: {label!r}") from exc


def _certificate_line(label: str, inequalities: Sequence[Mapping[str, object]]) -> str:
    parts = []
    for item in inequalities:
        quad = ",".join(str(value) for value in item["quad"])
        parts.append(f"{item['weight']}:{item['kind']}:{quad}")
    return f"{label}\t{';'.join(parts)}"


def _certificate_digest(lines: Sequence[str]) -> str:
    payload = "".join(f"{line}\n" for line in lines)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _fallback_states(source: Mapping[str, Any]) -> Iterator[dict[str, Any]]:
    windows = _as_list(source["windows"], "windows")
    for window in windows:
        window_row = _as_mapping(window, "window")
        fallback_labels = set(
            str(label)
            for label in _as_list(
                window_row["fifth_pair_farkas_fallback_labels"],
                "fifth_pair_farkas_fallback_labels",
            )
        )
        if not fallback_labels:
            continue

        seen: set[str] = set()
        fourth_survivors = _as_list(
            window_row["fourth_pair_survivors"],
            "fourth_pair_survivors",
        )
        for fourth_raw in fourth_survivors:
            fourth = _as_mapping(fourth_raw, "fourth_pair_survivor")
            fourth_label = str(fourth["label"])
            prefix_label = str(fourth["prefix_parent_label"])
            prefix_index = _prefix_index(prefix_label)
            fourth_state = state_from_boundary(
                [int(v) for v in fourth["child_boundary_left"]],
                [int(v) for v in fourth["child_boundary_right_reflection_side"]],
            )
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
                    if label in fallback_labels:
                        seen.add(label)
                        yield {
                            "label": label,
                            "prefix_parent_label": prefix_label,
                            "fourth_pair_parent_label": fourth_label,
                            "fifth_added_left": left_label,
                            "fifth_added_right_reflection_side": right_label,
                            "boundary_left": list(child.left),
                            "boundary_right_reflection_side": list(child.right),
                            "state": child,
                        }
                    fifth_index += 1
        missing = sorted(fallback_labels - seen)
        if missing:
            raise AssertionError(f"could not reconstruct fallback labels: {missing}")


def _kind_counts(inequalities: Sequence[Mapping[str, object]]) -> dict[str, int]:
    return _histogram(Counter(str(item["kind"]) for item in inequalities))


def _weight_counts(inequalities: Sequence[Mapping[str, object]]) -> dict[str, int]:
    return _histogram(Counter(int(item["weight"]) for item in inequalities))


def analyze_fallback_supports(
    source: Mapping[str, Any],
    *,
    source_artifact: str,
    tol: float,
) -> dict[str, Any]:
    if source["type"] != "c19_kalmanson_prefix_window_prefilter_sweep_v1":
        raise ValueError("expected compact C19 prefilter sweep artifact")

    classes = build_distance_classes(N, OFFSETS)
    records: list[dict[str, Any]] = []
    labels: list[str] = []
    certificate_lines: list[str] = []
    support_histogram: Counter[int] = Counter()
    weight_sum_histogram: Counter[int] = Counter()
    max_weight_histogram: Counter[int] = Counter()
    kind_pattern_histogram: Counter[str] = Counter()
    prefix_histogram: Counter[str] = Counter()
    fourth_parent_histogram: Counter[str] = Counter()
    two_row_miss_count = 0
    exact_farkas_count = 0

    for item in _fallback_states(source):
        state = item.pop("state")
        if not isinstance(state, BoundaryState):
            raise TypeError("internal fallback state reconstruction failed")
        label = str(item["label"])
        row_count, two_row = two_row_certificate_for_state(state, classes)
        if two_row:
            raise AssertionError(f"fallback label now has a two-row certificate: {label}")
        two_row_miss_count += 1

        fallback_row_count, cert, summary = find_certificate_for_state(
            label=label,
            state=state,
            classes=classes,
            tol=tol,
        )
        if fallback_row_count != row_count:
            raise AssertionError("fallback row count changed for reconstructed state")
        if cert is None or summary is None:
            raise AssertionError(f"fallback label no longer has an exact certificate: {label}")
        check_prefix_certificate_dict(cert)
        inequalities = _as_list(cert["inequalities"], "inequalities")
        exact_farkas_count += 1
        labels.append(label)
        certificate_lines.append(_certificate_line(label, inequalities))
        support_size = len(inequalities)
        weight_sum = int(summary["weight_sum"])
        max_weight = int(summary["max_weight"])
        kind_counts = _kind_counts(inequalities)
        support_histogram[support_size] += 1
        weight_sum_histogram[weight_sum] += 1
        max_weight_histogram[max_weight] += 1
        kind_pattern = "+".join(
            f"{kind}:{count}" for kind, count in sorted(kind_counts.items())
        )
        kind_pattern_histogram[kind_pattern] += 1
        prefix_histogram[str(item["prefix_parent_label"])] += 1
        fourth_parent_histogram[str(item["fourth_pair_parent_label"])] += 1
        records.append(
            {
                **item,
                "forced_inequalities_available": row_count,
                "two_row_prefilter_certificate_found": False,
                "certificate_summary": summary,
                "certificate_kind_counts": kind_counts,
                "certificate_weight_counts": _weight_counts(inequalities),
                "certificate": cert,
            }
        )

    aggregate = _as_mapping(source["aggregate_accounting"], "aggregate_accounting")
    expected_fallback_count = int(aggregate["fifth_pair_farkas_fallback_certified_count"])
    if len(records) != expected_fallback_count:
        raise AssertionError(
            f"reconstructed {len(records)} fallback records, expected {expected_fallback_count}"
        )

    return {
        "type": "c19_prefilter_fallback_support_diagnostic_v1",
        "trust": "EXACT_OBSTRUCTION",
        "source_artifact": source_artifact,
        "source_prefix_label_digest": source["prefix_label_digest"],
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This diagnostic only reconstructs fallback children already recorded by the compact C19 prefilter-window sweep.",
            "Each fallback child is rechecked as a miss for the exact two-row prefilter.",
            "Each fallback child is then certified by an exact positive-integer Kalmanson/Farkas certificate.",
            "This does not certify branches beyond the recorded sampled windows and is not an all-order C19 obstruction.",
        ],
        "parameters": {
            "lp_support_tolerance": tol,
            "fifth_pair_prefilter": "two_row_kalmanson_prefilter",
        },
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "aggregate": {
            "fallback_child_count": len(records),
            "two_row_prefilter_miss_count": two_row_miss_count,
            "exact_farkas_certified_count": exact_farkas_count,
            "final_unclosed_count": len(records) - exact_farkas_count,
            "fallback_label_digest": label_digest(labels),
            "fallback_certificate_digest": _certificate_digest(certificate_lines),
            "forced_row_count": 3300 if records else 0,
        },
        "histograms": {
            "support_size": _histogram(support_histogram),
            "weight_sum": _histogram(weight_sum_histogram),
            "max_weight": _histogram(max_weight_histogram),
            "kind_pattern": _histogram(kind_pattern_histogram),
            "fallback_count_by_prefix_parent": _histogram(prefix_histogram),
            "fallback_count_by_fourth_pair_parent": _histogram(fourth_parent_histogram),
        },
        "fallback_records": records,
    }


def assert_expected(data: Mapping[str, Any]) -> None:
    aggregate = _as_mapping(data["aggregate"], "aggregate")
    expected_aggregate = {
        "fallback_child_count": 8,
        "two_row_prefilter_miss_count": 8,
        "exact_farkas_certified_count": 8,
        "final_unclosed_count": 0,
        "fallback_label_digest": "2dc4965b208144017b7aba73dba920c8c8f8f1eea93a2f84650eb4f5f484f0c8",
        "forced_row_count": 3300,
    }
    for key, expected in expected_aggregate.items():
        if aggregate[key] != expected:
            raise AssertionError(f"{key} changed: {aggregate[key]} != {expected}")
    histograms = _as_mapping(data["histograms"], "histograms")
    support_size = _as_mapping(histograms["support_size"], "support-size histogram")
    if sum(int(count) for count in support_size.values()) != int(
        aggregate["fallback_child_count"]
    ):
        raise AssertionError("fallback support-size histogram total changed")
    records = _as_list(data["fallback_records"], "fallback_records")
    expected_labels = [
        "c19_window_fifth_child_0430_0081_0011",
        "c19_window_fifth_child_0434_0070_0021",
        "c19_window_fifth_child_0435_0078_0012",
        "c19_window_fifth_child_0435_0078_0085",
        "c19_window_fifth_child_0435_0083_0022",
        "c19_window_fifth_child_0436_0082_0022",
        "c19_window_fifth_child_0436_0083_0022",
        "c19_window_fifth_child_0456_0059_0041",
    ]
    if [row["label"] for row in records] != expected_labels:
        raise AssertionError("fallback label list changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--tol", type=float, default=1e-9, help="LP support threshold")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    source = _as_mapping(json.loads(args.source.read_text(encoding="utf-8")), "source")
    data = analyze_fallback_supports(
        source,
        source_artifact=_relative_path(args.source),
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
        aggregate = _as_mapping(data["aggregate"], "aggregate")
        print(
            "C19 prefilter fallback supports: "
            f"fallback={aggregate['fallback_child_count']} "
            f"exact={aggregate['exact_farkas_certified_count']} "
            f"unclosed={aggregate['final_unclosed_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
