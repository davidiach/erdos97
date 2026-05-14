#!/usr/bin/env python3
"""Record vertex-circle escapes in the reversed-second-block shuffle family."""

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
    N,
    ORDER,
    _add_row,
    _initial_state,
    _options,
    _partial_vertex_circle_status,
    _remove_row,
    _valid_options,
)
from scripts.check_block6_terminal_crossing_vertex_circle_sample import (  # noqa: E402
    write_json,
)

OUT = (
    ROOT
    / "data"
    / "certificates"
    / "block6_reversed_block_shuffle_vertex_circle_escape.json"
)
PROVENANCE = {
    "generator": "scripts/check_block6_reversed_block_shuffle_vertex_circle_escape.py",
    "command": (
        "python scripts/check_block6_reversed_block_shuffle_vertex_circle_escape.py "
        "--write --assert-expected"
    ),
}
SAMPLE_INDICES = (0, 1, 2, 3, 4, 20, 50, 100, 200, 232, 300, 400, 461)
EXPECTED_CLEAN_INDICES = [
    13,
    36,
    43,
    44,
    51,
    91,
    95,
    141,
    149,
    150,
    151,
    157,
    167,
    250,
    267,
    275,
]
EXPECTED_SUMMARY = {
    "shuffle_order_count": 462,
    "orders_with_terminal_extension": 458,
    "orders_without_terminal_extension": 4,
    "closed_order_count": 446,
    "orders_with_clean_pruned_solution": 16,
    "outside_natural_generator_first_extension_count": 458,
    "total_first_terminal_nodes": 30681,
    "total_first_terminal_zero_option_prunes": 16372,
    "first_terminal_nodes_min": 8,
    "first_terminal_nodes_max": 5339,
    "total_pruned_nodes": 1424672,
    "total_pruned_zero_option_prunes": 28366,
    "pruned_node_min": 329,
    "pruned_node_max": 19924,
    "pruned_node_max_order_index": 179,
    "vc_prunes": {"self_edge": 536464, "strict_cycle": 598113},
}
EXPECTED_NO_TERMINAL = {
    214: {
        "order": [0, 11, 1, 2, 3, 4, 10, 9, 8, 7, 5, 6],
        "first_terminal_search_nodes": 2544,
        "first_terminal_zero_option_prunes": 1703,
    },
    215: {
        "order": [0, 11, 1, 2, 3, 4, 10, 9, 8, 7, 6, 5],
        "first_terminal_search_nodes": 4661,
        "first_terminal_zero_option_prunes": 2931,
    },
    456: {
        "order": [0, 11, 10, 9, 8, 7, 1, 2, 3, 4, 5, 6],
        "first_terminal_search_nodes": 2680,
        "first_terminal_zero_option_prunes": 1734,
    },
    457: {
        "order": [0, 11, 10, 9, 8, 7, 1, 2, 3, 4, 6, 5],
        "first_terminal_search_nodes": 5101,
        "first_terminal_zero_option_prunes": 3223,
    },
}
EXPECTED_FAILURE_HISTOGRAM = {
    "2": 2,
    "3": 9,
    "4": 20,
    "5": 51,
    "6": 105,
    "7": 93,
    "8": 73,
    "9": 67,
    "10": 28,
    "11": 7,
    "12": 1,
    "13": 2,
}


Rows = list[list[int]]


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def reversed_second_block_shuffle_orders() -> list[dict[str, object]]:
    """Return shuffles with first block forward and second block reversed."""

    first_block_tail = [1, 2, 3, 4, 5]
    second_block_reversed = [11, 10, 9, 8, 7, 6]
    records: list[dict[str, object]] = []
    for index, first_block_positions in enumerate(combinations(range(1, 12), 5)):
        first_positions = set(first_block_positions)
        first_iter = iter(first_block_tail)
        second_iter = iter(second_block_reversed)
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
    records = reversed_second_block_shuffle_orders()
    if indices is None:
        return records
    selected = set(indices)
    unknown = selected - {int(record["index"]) for record in records}
    if unknown:
        raise ValueError(f"unknown reversed-block shuffle indices: {sorted(unknown)}")
    return [record for record in records if int(record["index"]) in selected]


def _pruned_search_with_first_clean(order: Sequence[int]) -> dict[str, Any]:
    assigned, pair_counts, indegrees = _initial_state(order)
    options = _options()
    initial_status, _edge_count = _partial_vertex_circle_status(assigned, order)
    nodes = 0
    zero_option_prunes = 0
    vc_prunes: Counter[str] = Counter()
    clean_rows: Rows | None = None

    def search() -> str | None:
        nonlocal nodes, zero_option_prunes, clean_rows
        if len(assigned) == N:
            status, _edge_count = _partial_vertex_circle_status(assigned, order)
            if status == "ok":
                clean_rows = [list(assigned[center]) for center in range(N)]
                return "found"
            vc_prunes[status] += 1
            return None

        best_center: int | None = None
        best_options: list[tuple[int, ...]] | None = None
        for center in range(N):
            if center in assigned:
                continue
            viable = _valid_options(
                center,
                options,
                assigned,
                pair_counts,
                indegrees,
                order,
            )
            if best_options is None or len(viable) < len(best_options):
                best_center = center
                best_options = viable
            if not viable:
                break
        if best_center is None or not best_options:
            zero_option_prunes += 1
            return None

        for row in best_options:
            nodes += 1
            _add_row(assigned, pair_counts, indegrees, best_center, row)
            status, _edge_count = _partial_vertex_circle_status(assigned, order)
            if status == "ok":
                result = search()
                if result == "found":
                    return result
            else:
                vc_prunes[status] += 1
            _remove_row(assigned, pair_counts, indegrees, best_center, row)
        return None

    raw_result = search()
    solutions = 1 if raw_result == "found" else 0
    return {
        "result": "closed" if raw_result is None else raw_result,
        "initial_vc": initial_status,
        "nodes": nodes,
        "zero_option_prunes": zero_option_prunes,
        "vc_prunes": _json_counter(vc_prunes),
        "solutions": solutions,
        "first_clean_rows": clean_rows,
    }


def _order_record(index: int, order: Sequence[int]) -> dict[str, Any]:
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
                "natural_order_crossing_failures": natural_failures[:13],
            }
        )

    pruned = _pruned_search_with_first_clean(order)
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
    clean_order_records: list[dict[str, Any]] = []
    sample_records: list[dict[str, Any]] = []
    failure_histogram: Counter[int] = Counter()
    vc_prunes: Counter[str] = Counter()
    first_nodes: list[int] = []
    pruned_nodes: list[tuple[int, int]] = []
    total_first_zero = 0
    total_pruned_zero = 0
    terminal_count = 0
    closed_count = 0
    clean_order_count = 0
    outside_natural_count = 0

    for order_record in order_records:
        index = int(order_record["index"])
        order = [int(label) for label in order_record["order"]]  # type: ignore[index]
        record = _order_record(index, order)

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
            clean_order_count += 1
            clean_order_records.append(record)

        if (full_sweep and index in sample_index_set) or not full_sweep:
            sample_records.append(record)

    pruned_node_max_index, pruned_node_max = max(pruned_nodes, key=lambda item: item[1])
    summary = {
        "shuffle_order_count": len(order_records),
        "orders_with_terminal_extension": terminal_count,
        "orders_without_terminal_extension": len(no_terminal_records),
        "closed_order_count": closed_count,
        "orders_with_clean_pruned_solution": clean_order_count,
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
        "schema": "erdos97.block6_reversed_block_shuffle_vertex_circle_escape.v1",
        "status": "REVIEW_PENDING_NEGATIVE_CONTROL_DIAGNOSTIC_ONLY",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "provenance": PROVENANCE,
        "family_definition": (
            "All 462 normalized cyclic orders obtained by keeping label 0 "
            "first, preserving the first block tail as 1,2,3,4,5, preserving "
            "the second block in reverse order 11,10,9,8,7,6, and shuffling "
            "the remaining labels of the two blocks. By cyclic reversal, this "
            "is the companion orientation family to the first-block-reversed, "
            "second-block-forward shuffles."
        ),
        "claim_scope": (
            "Fixed-order-family negative-control diagnostic for the two-block "
            "block-6 fragile rows. The sweep records 16 orders where the "
            "current vertex-circle quotient gate finds a clean full extension. "
            "This is not a counterexample, not Euclidean realizability, not "
            "all-order closure, not a fragile-bridge proof, and not a proof "
            "of Erdos Problem #97."
        ),
        "interpretation": (
            "Unlike the forward/forward block-preserving shuffle family, this "
            "second-block-reversed family is not closed by the vertex-circle "
            "gate alone. The stored clean rows identify the next fixed-order "
            "escape targets for stronger filters such as Kalmanson, row-circle "
            "Ptolemy, radius propagation, or a minimal/rich-class bridge."
        ),
        "summary": summary,
        "first_terminal_natural_failure_histogram": _json_counter(failure_histogram),
        "no_terminal_order_records": no_terminal_records,
        "clean_order_records": clean_order_records,
        "sample_records": sample_records,
    }


def assert_expected(data: Mapping[str, Any]) -> None:
    if data["status"] != "REVIEW_PENDING_NEGATIVE_CONTROL_DIAGNOSTIC_ONLY":
        raise AssertionError("unexpected status")
    if data["trust"] != "REVIEW_PENDING_DIAGNOSTIC":
        raise AssertionError("unexpected trust")
    if "not a counterexample" not in data["claim_scope"]:
        raise AssertionError("claim scope lost no-counterexample note")
    if "not Euclidean realizability" not in data["claim_scope"]:
        raise AssertionError("claim scope lost non-realizability guard")
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
    clean_indices = [int(record["index"]) for record in data["clean_order_records"]]
    if clean_indices != EXPECTED_CLEAN_INDICES:
        raise AssertionError(f"unexpected clean indices: {clean_indices!r}")
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
            "comma-separated reversed-block shuffle indices for a partial "
            "diagnostic payload; incompatible with --write, --check, and "
            "--assert-expected"
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
        print("block6 reversed-block shuffle vertex-circle escape")
        print(f"shuffle orders: {summary['shuffle_order_count']}")
        print(f"closed orders: {summary['closed_order_count']}")
        print(
            "clean pruned-solution orders: "
            f"{summary['orders_with_clean_pruned_solution']}"
        )
        print(f"vc prunes: {summary['vc_prunes']}")
        if args.assert_expected:
            print("OK: block6 reversed-block shuffle escape matched expected counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
