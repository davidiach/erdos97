#!/usr/bin/env python3
"""Probe block-6 fixed cyclic orders beyond the natural-order generator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erdos97.incidence_filters import (  # noqa: E402
    Chord,
    chords_cross_in_order,
    normalize_chord,
    phi_map,
)
from scripts.check_block6_fragile_vertex_circle_extension import (  # noqa: E402
    N,
    ORDER,
    _add_row,
    _initial_state,
    _options,
    _remove_row,
    _valid_options,
    pruned_search_payload,
)
from scripts.check_block6_terminal_crossing_vertex_circle_sample import (  # noqa: E402
    write_json,
)

OUT = ROOT / "data" / "certificates" / "block6_fixed_order_vertex_circle_probe.json"
PROVENANCE = {
    "generator": "scripts/check_block6_fixed_order_vertex_circle_probe.py",
    "command": (
        "python scripts/check_block6_fixed_order_vertex_circle_probe.py "
        "--write --assert-expected"
    ),
}
PROBE_ORDERS: tuple[dict[str, object], ...] = (
    {
        "name": "natural",
        "order": ORDER,
        "role": "baseline natural cyclic order used by the terminal generator",
    },
    {
        "name": "interleaved_blocks",
        "order": [0, 6, 1, 7, 2, 8, 3, 9, 4, 10, 5, 11],
        "role": "non-natural block-interleaving order",
    },
    {
        "name": "second_block_reversed",
        "order": [0, 1, 2, 3, 4, 5, 6, 11, 10, 9, 8, 7],
        "role": "non-natural order reversing the second block",
    },
    {
        "name": "twisted_pairs",
        "order": [0, 1, 6, 7, 2, 3, 8, 9, 4, 5, 10, 11],
        "role": "non-natural paired twist order",
    },
)
EXPECTED_PRUNED = {
    "natural": {
        "nodes": 1752,
        "zero_option_prunes": 37,
        "vc_prunes": {"self_edge": 645, "strict_cycle": 768},
    },
    "interleaved_blocks": {
        "nodes": 250,
        "zero_option_prunes": 0,
        "vc_prunes": {"self_edge": 109, "strict_cycle": 104},
    },
    "second_block_reversed": {
        "nodes": 1621,
        "zero_option_prunes": 55,
        "vc_prunes": {"self_edge": 510, "strict_cycle": 739},
    },
    "twisted_pairs": {
        "nodes": 294,
        "zero_option_prunes": 5,
        "vc_prunes": {"self_edge": 126, "strict_cycle": 115},
    },
}
EXPECTED_NATURAL_FAILURES = {
    "natural": 0,
    "interleaved_blocks": 8,
    "second_block_reversed": 3,
    "twisted_pairs": 5,
}

Rows = list[list[int]]


def _crossing_failures(rows: Rows, order: Sequence[int]) -> list[dict[str, object]]:
    failures: list[dict[str, object]] = []
    for source, target in sorted(phi_map(rows).items()):
        if not chords_cross_in_order(source, target, order):
            failures.append(
                {
                    "source": list(source),
                    "target": list(target),
                }
            )
    return failures


def _fixed_crossing_failures(order: Sequence[int]) -> list[dict[str, object]]:
    fixed_rows = _initial_state(order)[0]
    rows: Rows = [[] for _ in range(N)]
    for center, row in fixed_rows.items():
        rows[center] = list(row)
    failures: list[dict[str, object]] = []
    for left, left_row in fixed_rows.items():
        for right, right_row in fixed_rows.items():
            if left >= right:
                continue
            inter = sorted(set(left_row) & set(right_row))
            if len(inter) == 2:
                source: Chord = normalize_chord(left, right)
                target: Chord = normalize_chord(inter[0], inter[1])
                if not chords_cross_in_order(source, target, order):
                    failures.append({"source": list(source), "target": list(target)})
    return failures


def _first_terminal_extension(order: Sequence[int]) -> tuple[Rows | None, int, int]:
    assigned, pair_counts, indegrees = _initial_state(order)
    options = _options()
    nodes = 0
    zero_option_prunes = 0
    first_rows: Rows | None = None

    def search() -> bool:
        nonlocal nodes, zero_option_prunes, first_rows
        if len(assigned) == N:
            first_rows = [list(assigned[center]) for center in range(N)]
            return True

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
            return False

        for row in best_options:
            nodes += 1
            _add_row(assigned, pair_counts, indegrees, best_center, row)
            found = search()
            _remove_row(assigned, pair_counts, indegrees, best_center, row)
            if found:
                return True
        return False

    search()
    return first_rows, nodes, zero_option_prunes


def _probe_record(record: Mapping[str, object]) -> dict[str, Any]:
    name = str(record["name"])
    order = [int(label) for label in record["order"]]  # type: ignore[index]
    first_extension, first_nodes, first_zero = _first_terminal_extension(order)
    if first_extension is None:
        raise AssertionError(f"probe order {name!r} has no terminal extension")

    natural_failures = _crossing_failures(first_extension, ORDER)
    pruned = pruned_search_payload(order=order)
    return {
        "name": name,
        "role": record["role"],
        "order": order,
        "fixed_fragile_crossing_failure_count": len(_fixed_crossing_failures(order)),
        "first_terminal_extension": {
            "nodes_to_first": first_nodes,
            "zero_option_prunes_to_first": first_zero,
            "rows": first_extension,
            "natural_order_crossing_failure_count": len(natural_failures),
            "natural_order_crossing_failures": natural_failures[:8],
        },
        "pruned_search": pruned,
    }


def payload() -> dict[str, Any]:
    records = [_probe_record(record) for record in PROBE_ORDERS]
    closed_records = [
        record
        for record in records
        if record["pruned_search"]["result"] == "closed"
        and record["pruned_search"]["solutions"] == 0
    ]
    non_natural_records = [record for record in records if record["name"] != "natural"]
    outside_natural = [
        record
        for record in non_natural_records
        if record["first_terminal_extension"]["natural_order_crossing_failure_count"] > 0
    ]
    status_totals: dict[str, int] = {}
    for record in records:
        for status, count in record["pruned_search"]["vc_prunes"].items():
            status_totals[status] = status_totals.get(status, 0) + int(count)
    return {
        "schema": "erdos97.block6_fixed_order_vertex_circle_probe.v1",
        "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "provenance": PROVENANCE,
        "claim_scope": (
            "Four fixed cyclic-order probes for the two-block block-6 fragile "
            "rows, including three non-natural orders. For each order, the "
            "checker verifies a legal terminal extension exists under that "
            "order's crossing rule and then closes the order-specific full "
            "extension search by vertex-circle quotient pruning. This is a "
            "fixed-order diagnostic only: not an all-order closure, not a "
            "fragile-bridge proof, not a proof of Erdos Problem #97, and not "
            "a counterexample."
        ),
        "interpretation": (
            "The non-natural probes produce terminal selected-row extensions "
            "that fail the natural-order crossing rule, confirming that the "
            "natural-order terminal generator does not cover all fixed-order "
            "possibilities. In all four checked orders, however, the "
            "order-specific vertex-circle-pruned search closes with no clean "
            "full extension."
        ),
        "summary": {
            "probe_order_count": len(records),
            "non_natural_order_count": len(non_natural_records),
            "closed_order_count": len(closed_records),
            "orders_with_terminal_extension": len(records),
            "non_natural_first_extensions_outside_natural_generator": len(
                outside_natural
            ),
            "total_pruned_nodes": sum(
                int(record["pruned_search"]["nodes"]) for record in records
            ),
            "total_zero_option_prunes": sum(
                int(record["pruned_search"]["zero_option_prunes"])
                for record in records
            ),
            "vc_prunes": status_totals,
        },
        "records": records,
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

    expected_summary = {
        "probe_order_count": 4,
        "non_natural_order_count": 3,
        "closed_order_count": 4,
        "orders_with_terminal_extension": 4,
        "non_natural_first_extensions_outside_natural_generator": 3,
        "total_pruned_nodes": 3917,
        "total_zero_option_prunes": 97,
        "vc_prunes": {"self_edge": 1390, "strict_cycle": 1726},
    }
    if data["summary"] != expected_summary:
        raise AssertionError(f"unexpected summary: {data['summary']!r}")

    actual_pruned = {
        record["name"]: {
            "nodes": record["pruned_search"]["nodes"],
            "zero_option_prunes": record["pruned_search"]["zero_option_prunes"],
            "vc_prunes": record["pruned_search"]["vc_prunes"],
        }
        for record in data["records"]
    }
    if actual_pruned != EXPECTED_PRUNED:
        raise AssertionError(f"unexpected pruned counts: {actual_pruned!r}")

    actual_natural_failures = {
        record["name"]: record["first_terminal_extension"][
            "natural_order_crossing_failure_count"
        ]
        for record in data["records"]
    }
    if actual_natural_failures != EXPECTED_NATURAL_FAILURES:
        raise AssertionError(
            f"unexpected natural-order failure counts: {actual_natural_failures!r}"
        )


def _resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print full JSON payload")
    parser.add_argument("--write", action="store_true", help="write the artifact")
    parser.add_argument("--check", action="store_true", help="compare with artifact")
    parser.add_argument("--out", type=Path, default=OUT, help="artifact path")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert the current expected probe counts",
    )
    args = parser.parse_args()

    data = payload()
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
        print("block6 fixed-order vertex-circle probe")
        print(f"probe orders: {summary['probe_order_count']}")
        print(f"closed orders: {summary['closed_order_count']}")
        print(
            "outside natural generator: "
            f"{summary['non_natural_first_extensions_outside_natural_generator']}"
        )
        print(f"vc prunes: {summary['vc_prunes']}")
        if args.assert_expected:
            print("OK: block6 fixed-order probe matched expected counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
