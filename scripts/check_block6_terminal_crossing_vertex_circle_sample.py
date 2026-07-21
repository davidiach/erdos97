#!/usr/bin/env python3
"""Sample crossing-order vertex-circle status for block-6 terminal extensions."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erdos97.incidence_filters import (  # noqa: E402
    Chord,
    chords_cross_in_order,
    phi_map,
)
from erdos97.json_io import load_json, write_json  # noqa: E402
from erdos97.sparse_frontier import normalize_cyclic_order  # noqa: E402
from erdos97.vertex_circle_order_filter import (  # noqa: E402
    vertex_circle_order_obstruction,
)
from scripts.check_block6_fragile_vertex_circle_extension import (  # noqa: E402
    N,
    _add_row,
    _initial_state,
    _options,
    _remove_row,
    _valid_options,
)

Rows = list[list[int]]
Constraint = tuple[Chord, Chord]

DEFAULT_LIMIT = 100
DEFAULT_OUT = (
    ROOT
    / "data"
    / "certificates"
    / "block6_terminal_crossing_vertex_circle_sample.json"
)
FULL_SWEEP_OUT = (
    ROOT
    / "data"
    / "certificates"
    / "block6_terminal_crossing_vertex_circle_full_sweep.json"
)
DEFAULT_WINDOWS = ((0, 100), (100, 100))
PROVENANCE = {
    "generator": "scripts/check_block6_terminal_crossing_vertex_circle_sample.py",
    "command": (
        "python scripts/check_block6_terminal_crossing_vertex_circle_sample.py "
        "--write --assert-expected"
    ),
}
FULL_SWEEP_PROVENANCE = {
    "generator": "scripts/check_block6_terminal_crossing_vertex_circle_sample.py",
    "command": (
        "python scripts/check_block6_terminal_crossing_vertex_circle_sample.py "
        "--full-sweep --write --assert-expected"
    ),
}
EXPECTED_WINDOWS = {
    (0, 100): {
        "terminal_extensions_examined": 100,
        "total_crossing_orders": 440,
        "extensions_with_vc_clean_crossing_order": 0,
        "vertex_circle_order_status_counts": {"self_edge": 440},
        "max_crossing_order_count": 15,
        "crossing_search_node_min": 40,
        "crossing_search_node_max": 272,
        "order_count_histogram": {
            "2": 31,
            "3": 18,
            "4": 24,
            "5": 3,
            "6": 5,
            "8": 8,
            "9": 3,
            "10": 2,
            "11": 3,
            "12": 2,
            "15": 1,
        },
        "constraint_order_histogram": {
            "16,2": 1,
            "16,3": 3,
            "16,5": 1,
            "16,8": 1,
            "16,11": 1,
            "16,15": 1,
            "17,2": 3,
            "17,3": 3,
            "17,4": 3,
            "17,5": 2,
            "17,6": 1,
            "17,8": 4,
            "17,9": 1,
            "17,10": 1,
            "17,11": 2,
            "18,2": 11,
            "18,3": 1,
            "18,4": 10,
            "18,6": 1,
            "18,8": 2,
            "18,9": 1,
            "18,10": 1,
            "18,12": 1,
            "19,2": 12,
            "19,3": 4,
            "19,4": 9,
            "19,6": 2,
            "19,8": 1,
            "19,12": 1,
            "20,2": 3,
            "20,3": 5,
            "20,4": 2,
            "20,6": 1,
            "20,9": 1,
            "21,2": 1,
            "21,3": 2,
        },
    },
    (100, 100): {
        "terminal_extensions_examined": 100,
        "total_crossing_orders": 356,
        "extensions_with_vc_clean_crossing_order": 0,
        "vertex_circle_order_status_counts": {"self_edge": 356},
        "max_crossing_order_count": 14,
        "crossing_search_node_min": 26,
        "crossing_search_node_max": 308,
        "order_count_histogram": {
            "1": 27,
            "2": 23,
            "3": 5,
            "4": 25,
            "6": 2,
            "8": 12,
            "9": 4,
            "10": 1,
            "14": 1,
        },
        "constraint_order_histogram": {
            "15,1": 1,
            "15,10": 1,
            "16,1": 3,
            "16,4": 2,
            "16,6": 1,
            "16,9": 3,
            "16,14": 1,
            "17,1": 5,
            "17,2": 5,
            "17,3": 2,
            "17,4": 6,
            "17,6": 1,
            "17,8": 4,
            "17,9": 1,
            "18,1": 10,
            "18,2": 3,
            "18,3": 3,
            "18,4": 13,
            "18,8": 8,
            "19,1": 6,
            "19,2": 9,
            "19,4": 3,
            "20,1": 2,
            "20,2": 4,
            "20,4": 1,
            "21,2": 2,
        },
    },
}


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _json_pair_counter(counter: Counter[tuple[int, int]]) -> dict[str, int]:
    return {
        f"{left},{right}": int(counter[(left, right)])
        for left, right in sorted(counter)
    }


def terminal_extensions(
    limit: int | None,
    *,
    offset: int = 0,
) -> Iterator[tuple[int, Rows]]:
    """Yield a deterministic window of terminal full extensions."""

    assigned, pair_counts, indegrees = _initial_state()
    options = _options()
    seen = 0
    yielded = 0

    def search() -> Iterator[tuple[int, Rows]]:
        nonlocal seen, yielded
        if limit is not None and yielded >= limit:
            return
        if len(assigned) == N:
            seen += 1
            if seen <= offset:
                return
            yielded += 1
            yield seen, [list(assigned[center]) for center in range(N)]
            return

        best_center: int | None = None
        best_options: list[tuple[int, ...]] | None = None
        for center in range(N):
            if center in assigned:
                continue
            viable = _valid_options(center, options, assigned, pair_counts, indegrees)
            if best_options is None or len(viable) < len(best_options):
                best_center = center
                best_options = viable
            if not viable:
                break
        if best_center is None or not best_options:
            return

        for row in best_options:
            _add_row(assigned, pair_counts, indegrees, best_center, row)
            yield from search()
            _remove_row(assigned, pair_counts, indegrees, best_center, row)
            if limit is not None and yielded >= limit:
                return

    yield from search()


def enumerate_crossing_orders(rows: Rows) -> tuple[list[list[int]], int, int]:
    """Enumerate normalized cyclic orders satisfying two-overlap crossings."""

    constraints: list[Constraint] = sorted(phi_map(rows).items())
    labels = set(range(len(rows)))
    constraint_label_sets = [
        set(source) | set(target) for source, target in constraints
    ]
    label_to_constraints: dict[int, list[int]] = {label: [] for label in labels}
    for idx, constraint_labels in enumerate(constraint_label_sets):
        for label in constraint_labels:
            label_to_constraints[label].append(idx)

    orders: set[tuple[int, ...]] = set()
    nodes_visited = 0

    def completed_failure(
        order: Sequence[int],
        placed: set[int],
        affected_labels: set[int] | None = None,
    ) -> bool:
        if affected_labels is None:
            candidate_idxs = range(len(constraints))
        else:
            idxs: set[int] = set()
            for label in affected_labels:
                idxs.update(label_to_constraints[label])
            candidate_idxs = sorted(idxs)
        for idx in candidate_idxs:
            if constraint_label_sets[idx] <= placed:
                source, target = constraints[idx]
                if not chords_cross_in_order(source, target, order):
                    return True
        return False

    def choose_label(placed: set[int]) -> int:
        def score(label: int) -> tuple[int, int, int, int, int]:
            touches = [
                len(constraint_label_sets[idx] & placed)
                for idx in label_to_constraints[label]
            ]
            return (
                sum(count == 3 for count in touches),
                sum(count == 2 for count in touches),
                sum(count == 1 for count in touches),
                len(label_to_constraints[label]),
                -label,
            )

        return max(labels - placed, key=score)

    def search(order: list[int], placed: set[int]) -> None:
        nonlocal nodes_visited
        nodes_visited += 1
        if len(placed) == len(rows):
            if not completed_failure(order, placed):
                orders.add(tuple(normalize_cyclic_order(order)))
            return

        label = choose_label(placed)
        for position in range(1, len(order) + 1):
            candidate_order = order[:position] + [label] + order[position:]
            candidate_placed = placed | {label}
            if not completed_failure(candidate_order, candidate_placed, {label}):
                search(candidate_order, candidate_placed)

    search([0], {0})
    return [list(order) for order in sorted(orders)], nodes_visited, len(constraints)


def _vertex_circle_status(rows: Rows, order: Sequence[int]) -> str:
    result = vertex_circle_order_obstruction(rows, list(order), "block6_sample")
    if result.self_edge_conflicts:
        return "self_edge"
    if result.cycle_edges:
        return "strict_cycle"
    return "ok"


def audit(limit: int | None = DEFAULT_LIMIT, *, offset: int = 0) -> dict[str, Any]:
    """Return the sampled crossing-order vertex-circle audit."""

    status_counts: Counter[str] = Counter()
    order_count_histogram: Counter[int] = Counter()
    constraint_order_histogram: Counter[tuple[int, int]] = Counter()
    crossing_node_counts: list[int] = []
    clean_extension_records: list[dict[str, object]] = []
    sample_records: list[dict[str, object]] = []

    for extension_index, rows in terminal_extensions(limit, offset=offset):
        crossing_orders, nodes, constraint_count = enumerate_crossing_orders(rows)
        crossing_node_counts.append(nodes)
        order_count_histogram[len(crossing_orders)] += 1
        constraint_order_histogram[(constraint_count, len(crossing_orders))] += 1

        local_status_counts: Counter[str] = Counter()
        clean_orders: list[list[int]] = []
        for order in crossing_orders:
            status = _vertex_circle_status(rows, order)
            status_counts[status] += 1
            local_status_counts[status] += 1
            if status == "ok":
                clean_orders.append(order)

        if clean_orders:
            clean_extension_records.append(
                {
                    "extension_index": extension_index,
                    "clean_crossing_orders": clean_orders,
                    "rows": {str(center): row for center, row in enumerate(rows)},
                }
            )
        if len(sample_records) < 5:
            sample_records.append(
                {
                    "extension_index": extension_index,
                    "crossing_constraint_count": constraint_count,
                    "crossing_order_count": len(crossing_orders),
                    "crossing_search_nodes": nodes,
                    "vertex_circle_status_counts": _json_counter(local_status_counts),
                    "first_row1": rows[1],
                }
            )

    examined = sum(order_count_histogram.values())
    total_crossing_orders = sum(status_counts.values())
    summary = {
        "terminal_extensions_examined": examined,
        "total_crossing_orders": total_crossing_orders,
        "extensions_with_vc_clean_crossing_order": len(clean_extension_records),
        "vertex_circle_order_status_counts": _json_counter(status_counts),
        "max_crossing_order_count": max(order_count_histogram, default=0),
        "crossing_search_node_min": min(crossing_node_counts, default=0),
        "crossing_search_node_max": max(crossing_node_counts, default=0),
        "order_count_histogram": _json_counter(order_count_histogram),
        "constraint_order_histogram": _json_pair_counter(constraint_order_histogram),
    }
    return {
        "schema": "erdos97.block6_terminal_crossing_vertex_circle_sample.v1",
        "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "claim_scope": (
            "Deterministic first-terminal-extension sample for the two-block "
            "block-6 fragile family. This is not an all-extension proof, not "
            "a proof of Erdos Problem #97, and not a counterexample."
        ),
        "terminal_extension_limit": limit,
        "terminal_extension_offset": offset,
        "summary": summary,
        "sample_records": sample_records,
        "first_clean_extension_record": (
            clean_extension_records[0] if clean_extension_records else None
        ),
        "interpretation": (
            "The default sample checks the first 100 deterministic terminal "
            "full extensions from the natural-order block-6 audit across all "
            "their two-overlap crossing-compatible cyclic orders. Nonzero "
            "offsets replay later deterministic windows. The checked packets "
            "find no vertex-circle-clean crossing order in their samples."
        ),
    }


def full_sweep_payload() -> dict[str, Any]:
    """Return the full natural-order terminal-extension crossing-order sweep."""

    payload = audit(limit=None, offset=0)
    payload.update(
        {
            "schema": (
                "erdos97.block6_terminal_crossing_vertex_circle_full_sweep.v1"
            ),
            "provenance": FULL_SWEEP_PROVENANCE,
            "claim_scope": (
                "Full sweep over all terminal full selected-row extensions "
                "generated by the natural-order two-block block-6 fragile "
                "audit, checking every crossing-compatible cyclic order each "
                "terminal extension admits by the vertex-circle quotient "
                "filter. This is not a proof for row systems that fail the "
                "natural-order terminal generator, not a fragile-bridge proof, "
                "not a proof of Erdos Problem #97, and not a counterexample."
            ),
            "interpretation": (
                "The sweep exhausts the 105,978 terminal full extensions from "
                "the natural-order block-6 audit and classifies all 385,517 "
                "crossing-compatible cyclic orders they admit. No sampled or "
                "terminal order is vertex-circle-clean: all are killed by a "
                "quotient self-edge or strict cycle. The remaining block-6 "
                "gap is row systems not generated by the natural-order "
                "terminal audit, or a genuine minimal/rich-class bridge."
            ),
        }
    )
    return payload


def sample_packet_payload(
    windows: Sequence[tuple[int, int]] = DEFAULT_WINDOWS,
) -> dict[str, Any]:
    """Return the stored two-window crossing-order sample packet."""

    samples = [audit(limit=limit, offset=offset) for offset, limit in windows]
    status_counts: Counter[str] = Counter()
    total_extensions = 0
    total_crossing_orders = 0
    clean_extensions = 0
    max_crossing_order_count = 0
    node_mins: list[int] = []
    node_maxes: list[int] = []

    for sample in samples:
        summary = sample["summary"]
        total_extensions += int(summary["terminal_extensions_examined"])
        total_crossing_orders += int(summary["total_crossing_orders"])
        clean_extensions += int(summary["extensions_with_vc_clean_crossing_order"])
        max_crossing_order_count = max(
            max_crossing_order_count,
            int(summary["max_crossing_order_count"]),
        )
        node_mins.append(int(summary["crossing_search_node_min"]))
        node_maxes.append(int(summary["crossing_search_node_max"]))
        status_counts.update(
            {
                status: int(count)
                for status, count in summary[
                    "vertex_circle_order_status_counts"
                ].items()
            }
        )

    return {
        "schema": "erdos97.block6_terminal_crossing_vertex_circle_sample_packet.v1",
        "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "claim_scope": (
            "Two deterministic windows of terminal full extensions from the "
            "two-block block-6 fragile family, checked across their "
            "crossing-compatible cyclic orders by the vertex-circle quotient "
            "filter. This is a sample only: not an all-extension proof, not "
            "an all-order proof, not a proof of Erdos Problem #97, and not a "
            "counterexample."
        ),
        "provenance": PROVENANCE,
        "sample_windows": [
            {"terminal_extension_offset": offset, "terminal_extension_limit": limit}
            for offset, limit in windows
        ],
        "summary": {
            "sample_window_count": len(samples),
            "terminal_extensions_examined": total_extensions,
            "total_crossing_orders": total_crossing_orders,
            "extensions_with_vc_clean_crossing_order": clean_extensions,
            "vertex_circle_order_status_counts": _json_counter(status_counts),
            "max_crossing_order_count": max_crossing_order_count,
            "crossing_search_node_min": min(node_mins, default=0),
            "crossing_search_node_max": max(node_maxes, default=0),
        },
        "windows": samples,
        "interpretation": (
            "The packet stores two deterministic 100-extension windows "
            "starting at offsets 0 and 100. Every sampled crossing-compatible "
            "cyclic order is killed by a vertex-circle quotient self-edge, "
            "but the packet remains a bounded diagnostic sample."
        ),
    }


def assert_expected(payload: Mapping[str, Any]) -> None:
    if payload["status"] != "REVIEW_PENDING_DIAGNOSTIC_ONLY":
        raise AssertionError("unexpected status")
    if payload["trust"] != "REVIEW_PENDING_DIAGNOSTIC":
        raise AssertionError("unexpected trust label")
    if "not a proof" not in payload["claim_scope"]:
        raise AssertionError("claim scope lost no-proof note")
    key = (
        int(payload["terminal_extension_offset"]),
        int(payload["terminal_extension_limit"]),
    )
    expected = EXPECTED_WINDOWS.get(key)
    if expected is None:
        raise AssertionError(f"no stored expectation for sample window {key}")
    if payload["summary"] != expected:
        raise AssertionError(f"unexpected summary: {payload['summary']!r}")


def assert_expected_packet(payload: Mapping[str, Any]) -> None:
    if payload["status"] != "REVIEW_PENDING_DIAGNOSTIC_ONLY":
        raise AssertionError("unexpected packet status")
    if payload["trust"] != "REVIEW_PENDING_DIAGNOSTIC":
        raise AssertionError("unexpected packet trust label")
    if "not a proof" not in payload["claim_scope"]:
        raise AssertionError("packet claim scope lost no-proof note")
    if "sample only" not in payload["claim_scope"]:
        raise AssertionError("packet claim scope lost sample-only note")
    if payload["provenance"] != PROVENANCE:
        raise AssertionError("unexpected packet provenance")
    windows = list(payload["windows"])
    expected_windows = [
        (int(window["terminal_extension_offset"]), int(window["terminal_extension_limit"]))
        for window in windows
    ]
    if expected_windows != list(DEFAULT_WINDOWS):
        raise AssertionError(f"unexpected sample windows: {expected_windows!r}")
    for window in windows:
        assert_expected(window)
    expected_summary = {
        "sample_window_count": 2,
        "terminal_extensions_examined": 200,
        "total_crossing_orders": 796,
        "extensions_with_vc_clean_crossing_order": 0,
        "vertex_circle_order_status_counts": {"self_edge": 796},
        "max_crossing_order_count": 15,
        "crossing_search_node_min": 26,
        "crossing_search_node_max": 308,
    }
    if payload["summary"] != expected_summary:
        raise AssertionError(f"unexpected packet summary: {payload['summary']!r}")


def assert_expected_full_sweep(payload: Mapping[str, Any]) -> None:
    if payload["status"] != "REVIEW_PENDING_DIAGNOSTIC_ONLY":
        raise AssertionError("unexpected full-sweep status")
    if payload["trust"] != "REVIEW_PENDING_DIAGNOSTIC":
        raise AssertionError("unexpected full-sweep trust label")
    if "not a proof" not in payload["claim_scope"]:
        raise AssertionError("full-sweep claim scope lost no-proof note")
    if payload["provenance"] != FULL_SWEEP_PROVENANCE:
        raise AssertionError("unexpected full-sweep provenance")
    if payload["terminal_extension_offset"] != 0:
        raise AssertionError("unexpected full-sweep offset")
    if payload["terminal_extension_limit"] is not None:
        raise AssertionError("full-sweep limit should be null")
    expected_summary_subset = {
        "terminal_extensions_examined": 105978,
        "total_crossing_orders": 385517,
        "extensions_with_vc_clean_crossing_order": 0,
        "vertex_circle_order_status_counts": {
            "self_edge": 384318,
            "strict_cycle": 1199,
        },
        "max_crossing_order_count": 380,
        "crossing_search_node_min": 22,
        "crossing_search_node_max": 4046,
    }
    summary = dict(payload["summary"])
    summary_subset = {key: summary[key] for key in expected_summary_subset}
    if summary_subset != expected_summary_subset:
        raise AssertionError(f"unexpected full-sweep summary: {summary_subset!r}")
    if payload["first_clean_extension_record"] is not None:
        raise AssertionError("full sweep unexpectedly found a clean order")


def _resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def compare_artifact(payload: Mapping[str, Any], path: Path) -> None:
    checked = load_json(path)
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print full JSON payload")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument(
        "--packet",
        action="store_true",
        help="emit the stored two-window sample packet instead of one window",
    )
    parser.add_argument(
        "--full-sweep",
        action="store_true",
        help=(
            "emit the full natural-order terminal-extension crossing-order "
            "sweep instead of one sample window"
        ),
    )
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert stored expected sample-window counts",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="artifact path for --write or --check",
    )
    parser.add_argument("--write", action="store_true", help="write the checked packet")
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare the regenerated packet against the checked artifact",
    )
    args = parser.parse_args()

    if args.packet and args.full_sweep:
        parser.error("--packet and --full-sweep are mutually exclusive")
    packet_mode = (args.packet or args.write or args.check) and not args.full_sweep
    if (packet_mode or args.full_sweep) and (
        args.limit != DEFAULT_LIMIT or args.offset != 0
    ):
        parser.error("--limit and --offset apply only to single-window output")

    if args.full_sweep:
        payload = full_sweep_payload()
    elif packet_mode:
        payload = sample_packet_payload()
    else:
        payload = audit(limit=args.limit, offset=args.offset)
    if args.assert_expected:
        if args.full_sweep:
            assert_expected_full_sweep(payload)
        elif packet_mode:
            assert_expected_packet(payload)
        else:
            assert_expected(payload)
    default_out = FULL_SWEEP_OUT if args.full_sweep else DEFAULT_OUT
    artifact_path = _resolve_repo_path(args.out or default_out)
    if args.write:
        write_json(payload, artifact_path)
    if args.check:
        compare_artifact(payload, artifact_path)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        summary = payload["summary"]
        print("block6 terminal crossing vertex-circle sample")
        if args.full_sweep:
            print("mode: full natural-order terminal-extension sweep")
        elif packet_mode:
            print(f"sample windows: {summary['sample_window_count']}")
        else:
            print(
                "window: "
                f"offset={payload['terminal_extension_offset']} "
                f"limit={payload['terminal_extension_limit']}"
            )
        print(f"terminal extensions: {summary['terminal_extensions_examined']}")
        print(f"crossing orders: {summary['total_crossing_orders']}")
        print(
            "vc-clean extensions: "
            f"{summary['extensions_with_vc_clean_crossing_order']}"
        )
        print(f"status counts: {summary['vertex_circle_order_status_counts']}")
        if args.assert_expected:
            print("OK: expected block6 crossing-VC sample counts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
