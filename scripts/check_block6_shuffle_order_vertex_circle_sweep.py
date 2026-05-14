#!/usr/bin/env python3
"""Sweep block-6 block-preserving shuffle orders with vertex-circle pruning."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_block6_fixed_order_vertex_circle_probe import (  # noqa: E402
    _crossing_failures,
    _first_terminal_extension,
)
from scripts.check_block6_fragile_vertex_circle_extension import (  # noqa: E402
    ORDER,
    pruned_search_payload,
)
from scripts.check_block6_terminal_crossing_vertex_circle_sample import (  # noqa: E402
    write_json,
)

OUT = ROOT / "data" / "certificates" / "block6_shuffle_order_vertex_circle_sweep.json"
PROVENANCE = {
    "generator": "scripts/check_block6_shuffle_order_vertex_circle_sweep.py",
    "command": (
        "python scripts/check_block6_shuffle_order_vertex_circle_sweep.py "
        "--write --assert-expected"
    ),
}
SAMPLE_INDICES = (0, 1, 2, 3, 4, 20, 50, 100, 200, 214, 215, 232, 456, 457, 461)
EXPECTED_SUMMARY = {
    "shuffle_order_count": 462,
    "orders_with_terminal_extension": 458,
    "orders_without_terminal_extension": 4,
    "closed_order_count": 462,
    "orders_with_clean_pruned_solution": 0,
    "outside_natural_generator_first_extension_count": 457,
    "total_first_terminal_nodes": 56377,
    "total_first_terminal_zero_option_prunes": 30529,
    "first_terminal_nodes_min": 8,
    "first_terminal_nodes_max": 7476,
    "total_pruned_nodes": 735652,
    "total_pruned_zero_option_prunes": 11903,
    "pruned_node_min": 211,
    "pruned_node_max": 12669,
    "pruned_node_max_order_index": 232,
    "vc_prunes": {"self_edge": 276230, "strict_cycle": 316519},
}
EXPECTED_NO_TERMINAL = {
    214: {
        "order": [0, 6, 1, 2, 3, 4, 7, 8, 9, 10, 5, 11],
        "first_terminal_search_nodes": 6726,
        "first_terminal_zero_option_prunes": 4036,
    },
    215: {
        "order": [0, 6, 1, 2, 3, 4, 7, 8, 9, 10, 11, 5],
        "first_terminal_search_nodes": 5251,
        "first_terminal_zero_option_prunes": 3138,
    },
    456: {
        "order": [0, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 11],
        "first_terminal_search_nodes": 5434,
        "first_terminal_zero_option_prunes": 3234,
    },
    457: {
        "order": [0, 6, 7, 8, 9, 10, 1, 2, 3, 4, 11, 5],
        "first_terminal_search_nodes": 6667,
        "first_terminal_zero_option_prunes": 4012,
    },
}
EXPECTED_FAILURE_HISTOGRAM = {
    "0": 1,
    "2": 12,
    "3": 26,
    "4": 76,
    "5": 99,
    "6": 91,
    "7": 58,
    "8": 52,
    "9": 25,
    "10": 15,
    "11": 2,
    "12": 1,
}


Rows = list[list[int]]


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def shuffle_orders() -> list[dict[str, object]]:
    """Return all normalized block-preserving shuffles of two six-label blocks."""

    first_block_tail = [1, 2, 3, 4, 5]
    second_block = [6, 7, 8, 9, 10, 11]
    records: list[dict[str, object]] = []
    for index, first_block_positions in enumerate(combinations(range(1, 12), 5)):
        first_positions = set(first_block_positions)
        first_iter = iter(first_block_tail)
        second_iter = iter(second_block)
        order = [0]
        for position in range(1, 12):
            if position in first_positions:
                order.append(next(first_iter))
            else:
                order.append(next(second_iter))
        records.append({"index": index, "order": order})
    return records


def _selected_order_records(
    *,
    indices: Iterable[int] | None = None,
) -> list[dict[str, object]]:
    records = shuffle_orders()
    if indices is None:
        return records
    selected = set(indices)
    unknown = selected - {int(record["index"]) for record in records}
    if unknown:
        raise ValueError(f"unknown shuffle order indices: {sorted(unknown)}")
    return [record for record in records if int(record["index"]) in selected]


def _order_sweep_record(index: int, order: Sequence[int]) -> dict[str, Any]:
    first_rows, first_nodes, first_zero = _first_terminal_extension(order)
    terminal_record: dict[str, Any] = {
        "has_terminal_extension": first_rows is not None,
        "first_terminal_search_nodes": first_nodes,
        "first_terminal_zero_option_prunes": first_zero,
    }
    if first_rows is not None:
        natural_failures = _crossing_failures(first_rows, ORDER)
        terminal_record.update(
            {
                "first_terminal_rows": first_rows,
                "natural_order_crossing_failure_count": len(natural_failures),
                "natural_order_crossing_failures": natural_failures[:12],
            }
        )

    pruned = pruned_search_payload(order=order)
    return {
        "index": index,
        "order": list(order),
        "first_terminal_extension": terminal_record,
        "pruned_search": pruned,
    }


def payload(*, indices: Iterable[int] | None = None) -> dict[str, Any]:
    order_records = _selected_order_records(indices=indices)
    full_sweep = indices is None
    sample_index_set = set(SAMPLE_INDICES)

    no_terminal_records: list[dict[str, Any]] = []
    sample_records: list[dict[str, Any]] = []
    failure_histogram: Counter[int] = Counter()
    vc_prunes: Counter[str] = Counter()
    first_nodes: list[int] = []
    pruned_nodes: list[tuple[int, int]] = []
    total_first_zero = 0
    total_pruned_zero = 0
    terminal_count = 0
    closed_count = 0
    clean_solution_order_count = 0
    outside_natural_count = 0

    for order_record in order_records:
        index = int(order_record["index"])
        order = [int(label) for label in order_record["order"]]  # type: ignore[index]
        record = _order_sweep_record(index, order)

        first = record["first_terminal_extension"]
        first_nodes.append(int(first["first_terminal_search_nodes"]))
        total_first_zero += int(first["first_terminal_zero_option_prunes"])
        if first["has_terminal_extension"]:
            terminal_count += 1
            failure_count = int(first["natural_order_crossing_failure_count"])
            failure_histogram[failure_count] += 1
            if failure_count > 0:
                outside_natural_count += 1
        else:
            no_terminal_records.append(
                {
                    "index": index,
                    "order": order,
                    "first_terminal_search_nodes": int(
                        first["first_terminal_search_nodes"]
                    ),
                    "first_terminal_zero_option_prunes": int(
                        first["first_terminal_zero_option_prunes"]
                    ),
                }
            )

        pruned = record["pruned_search"]
        pruned_nodes.append((index, int(pruned["nodes"])))
        total_pruned_zero += int(pruned["zero_option_prunes"])
        vc_prunes.update(
            {status: int(count) for status, count in pruned["vc_prunes"].items()}
        )
        if pruned["result"] == "closed" and pruned["solutions"] == 0:
            closed_count += 1
        if int(pruned["solutions"]) > 0:
            clean_solution_order_count += 1

        if (full_sweep and index in sample_index_set) or not full_sweep:
            sample_records.append(record)

    pruned_node_max_index, pruned_node_max = max(pruned_nodes, key=lambda item: item[1])
    summary = {
        "shuffle_order_count": len(order_records),
        "orders_with_terminal_extension": terminal_count,
        "orders_without_terminal_extension": len(no_terminal_records),
        "closed_order_count": closed_count,
        "orders_with_clean_pruned_solution": clean_solution_order_count,
        "outside_natural_generator_first_extension_count": outside_natural_count,
        "total_first_terminal_nodes": sum(first_nodes),
        "total_first_terminal_zero_option_prunes": total_first_zero,
        "first_terminal_nodes_min": min(first_nodes, default=0),
        "first_terminal_nodes_max": max(first_nodes, default=0),
        "total_pruned_nodes": sum(nodes for _index, nodes in pruned_nodes),
        "total_pruned_zero_option_prunes": total_pruned_zero,
        "pruned_node_min": min((nodes for _index, nodes in pruned_nodes), default=0),
        "pruned_node_max": pruned_node_max,
        "pruned_node_max_order_index": pruned_node_max_index,
        "vc_prunes": _json_counter(vc_prunes),
    }
    return {
        "schema": "erdos97.block6_shuffle_order_vertex_circle_sweep.v1",
        "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "provenance": PROVENANCE,
        "family_definition": (
            "All 462 normalized cyclic orders obtained by keeping label 0 "
            "first, preserving the internal order 0,1,2,3,4,5 in the first "
            "block and 6,7,8,9,10,11 in the second block, and shuffling the "
            "remaining labels of the two blocks."
        ),
        "claim_scope": (
            "Exhaustive fixed-order diagnostic over the block-preserving "
            "shuffle family for the two-block block-6 fragile rows. Every "
            "order-specific full-extension search in this bounded family "
            "closes under vertex-circle quotient pruning. This is not an "
            "all-cyclic-order closure, not an all-extension bridge proof, "
            "not a proof of Erdos Problem #97, and not a counterexample."
        ),
        "interpretation": (
            "The sweep widens the fixed-order probe from four hand-picked "
            "orders to every block-preserving shuffle order. It confirms that "
            "many non-natural orders have terminal selected-row extensions "
            "outside the natural-order generator, while the order-specific "
            "vertex-circle gate still closes this entire bounded order family."
        ),
        "summary": summary,
        "first_terminal_natural_failure_histogram": _json_counter(failure_histogram),
        "no_terminal_order_records": no_terminal_records,
        "sample_records": sample_records,
    }


def assert_expected(data: Mapping[str, Any]) -> None:
    if data["status"] != "REVIEW_PENDING_DIAGNOSTIC_ONLY":
        raise AssertionError("unexpected status")
    if data["trust"] != "REVIEW_PENDING_DIAGNOSTIC":
        raise AssertionError("unexpected trust")
    if "not a proof" not in data["claim_scope"]:
        raise AssertionError("claim scope lost no-proof note")
    if data["provenance"] != PROVENANCE:
        raise AssertionError("unexpected provenance")
    if data["summary"] != EXPECTED_SUMMARY:
        raise AssertionError(f"unexpected summary: {data['summary']!r}")
    if (
        data["first_terminal_natural_failure_histogram"]
        != EXPECTED_FAILURE_HISTOGRAM
    ):
        raise AssertionError("unexpected first-terminal failure histogram")
    actual_no_terminal = {
        int(record["index"]): {
            "order": record["order"],
            "first_terminal_search_nodes": record["first_terminal_search_nodes"],
            "first_terminal_zero_option_prunes": record[
                "first_terminal_zero_option_prunes"
            ],
        }
        for record in data["no_terminal_order_records"]
    }
    if actual_no_terminal != EXPECTED_NO_TERMINAL:
        raise AssertionError(f"unexpected no-terminal records: {actual_no_terminal!r}")
    sample_indices = [int(record["index"]) for record in data["sample_records"]]
    if sample_indices != list(SAMPLE_INDICES):
        raise AssertionError(f"unexpected sample indices: {sample_indices!r}")


def _resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _parse_indices(raw_indices: Sequence[str]) -> list[int] | None:
    if not raw_indices:
        return None
    parsed: list[int] = []
    for raw in raw_indices:
        parsed.extend(int(piece) for piece in raw.split(",") if piece)
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print full JSON payload")
    parser.add_argument("--write", action="store_true", help="write the artifact")
    parser.add_argument("--check", action="store_true", help="compare with artifact")
    parser.add_argument("--out", type=Path, default=OUT, help="artifact path")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert the current expected full-sweep counts",
    )
    parser.add_argument(
        "--indices",
        action="append",
        default=[],
        help=(
            "comma-separated shuffle-order indices for a partial diagnostic "
            "payload; incompatible with --write, --check, and --assert-expected"
        ),
    )
    args = parser.parse_args()

    indices = _parse_indices(args.indices)
    if indices is not None and (args.write or args.check or args.assert_expected):
        parser.error("--indices is incompatible with --write, --check, and --assert-expected")

    data = payload(indices=indices)
    if args.assert_expected:
        assert_expected(data)
    artifact_path = _resolve_repo_path(args.out)
    if args.write:
        write_json(data, artifact_path)
    if args.check:
        checked = json.loads(artifact_path.read_text(encoding="utf-8"))
        if checked != data:
            raise AssertionError(f"artifact differs from generated payload: {artifact_path}")

    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        summary = data["summary"]
        print("block6 shuffle-order vertex-circle sweep")
        print(f"shuffle orders: {summary['shuffle_order_count']}")
        print(f"closed orders: {summary['closed_order_count']}")
        print(
            "terminal extensions: "
            f"{summary['orders_with_terminal_extension']} "
            f"(missing {summary['orders_without_terminal_extension']})"
        )
        print(
            "outside natural generator first extensions: "
            f"{summary['outside_natural_generator_first_extension_count']}"
        )
        print(f"vc prunes: {summary['vc_prunes']}")
        if args.assert_expected:
            print("OK: block6 shuffle-order sweep matched expected counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
