#!/usr/bin/env python3
"""Check block-6 oriented-block closure by cyclic reversal duality."""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_block6_forward_block_two_orientation_closure import (  # noqa: E402
    OUT as FORWARD_TWO_ORIENTATION_OUT,
    assert_expected as assert_forward_two_orientation_expected,
    check_artifact as check_forward_two_orientation_artifact,
)
from scripts.check_block6_terminal_crossing_vertex_circle_sample import (  # noqa: E402
    write_json,
)

OUT = (
    ROOT
    / "data"
    / "certificates"
    / "block6_oriented_block_reversal_closure.json"
)
SCHEMA = "erdos97.block6_oriented_block_reversal_closure.v1"
STATUS = "BOUNDED_ORIENTED_BLOCK_REVERSAL_CLOSURE_DIAGNOSTIC"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
PROVENANCE = {
    "generator": "scripts/check_block6_oriented_block_reversal_closure.py",
    "command": (
        "python scripts/check_block6_oriented_block_reversal_closure.py "
        "--write --assert-expected"
    ),
}
CLAIM_SCOPE = (
    "Cross-artifact fixed-order-family diagnostic for the 1848 normalized "
    "block-6 oriented-block shuffle orders, where each six-label block is "
    "kept internally forward or reversed and the two blocks are shuffled. "
    "It uses the first-block-forward two-orientation packet for 924 direct "
    "closures and exact cyclic reversal duality for the 924 first-block-"
    "reversed orders. This is not arbitrary cyclic-order closure, not all "
    "selected-row systems, not a fragile-bridge proof, not a proof of Erdos "
    "Problem #97, and not a counterexample."
)
EXPECTED_SUMMARY = {
    "orientation_family_count": 4,
    "orders_per_orientation_family": 462,
    "total_oriented_order_count": 1848,
    "direct_source_order_count": 924,
    "reversal_dual_order_count": 924,
    "combined_closed_order_count": 1848,
    "combined_closure_complete": True,
    "reversal_pair_counts": {
        "forward_forward_to_reversed_reversed": 462,
        "forward_reversed_to_reversed_forward": 462,
    },
    "method_counts": {
        "vertex_circle_quotient_direct": 908,
        "kalmanson_after_vertex_circle_escape_direct": 16,
        "vertex_circle_quotient_by_reversal": 908,
        "kalmanson_after_vertex_circle_escape_by_reversal": 16,
        "vertex_circle_quotient_total": 1816,
        "kalmanson_after_vertex_circle_escape_total": 32,
    },
}

FIRST_FORWARD = [1, 2, 3, 4, 5]
FIRST_REVERSED = [5, 4, 3, 2, 1]
SECOND_FORWARD = [6, 7, 8, 9, 10, 11]
SECOND_REVERSED = [11, 10, 9, 8, 7, 6]


def oriented_shuffle_orders(
    *,
    first_tail: Sequence[int],
    second_tail: Sequence[int],
) -> list[dict[str, object]]:
    """Return normalized shuffles for a fixed orientation of each block."""

    records: list[dict[str, object]] = []
    for index, first_block_positions in enumerate(combinations(range(1, 12), 5)):
        first_positions = set(first_block_positions)
        first_iter = iter(first_tail)
        second_iter = iter(second_tail)
        order = [0]
        for position in range(1, 12):
            if position in first_positions:
                order.append(next(first_iter))
            else:
                order.append(next(second_iter))
        records.append({"index": index, "order": order})
    return records


def normalized_cyclic_reverse(order: Sequence[int]) -> list[int]:
    """Reverse a normalized cyclic order while keeping label 0 first."""

    if not order or order[0] != 0:
        raise ValueError(f"expected normalized order beginning with 0: {order!r}")
    return [0, *reversed(order[1:])]


def _order_index(records: Sequence[Mapping[str, object]]) -> dict[tuple[int, ...], int]:
    return {
        tuple(int(label) for label in record["order"]): int(record["index"])
        for record in records
    }


def _reversal_pairs(
    source: Sequence[Mapping[str, object]],
    target: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    target_index = _order_index(target)
    pairs: list[dict[str, object]] = []
    for record in source:
        source_order = [int(label) for label in record["order"]]
        reversed_order = normalized_cyclic_reverse(source_order)
        try:
            target_order_index = target_index[tuple(reversed_order)]
        except KeyError as exc:
            raise AssertionError(
                f"reversed order not found in target family: {reversed_order}"
            ) from exc
        pairs.append(
            {
                "source_index": int(record["index"]),
                "target_index": target_order_index,
                "source_order": source_order,
                "target_order": reversed_order,
            }
        )
    return pairs


def _compact_pair_samples(pairs: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    sample_positions = [0, 1, 2, 50, 214, 275, 461]
    return [dict(pairs[position]) for position in sample_positions]


def _family_record(
    *,
    name: str,
    first_orientation: str,
    second_orientation: str,
    closure_source: str,
    closure_methods: Mapping[str, int],
) -> dict[str, object]:
    return {
        "name": name,
        "first_block_orientation": first_orientation,
        "second_block_orientation": second_orientation,
        "order_count": 462,
        "closed_order_count": sum(int(value) for value in closure_methods.values()),
        "closure_source": closure_source,
        "closure_methods": dict(closure_methods),
    }


def payload() -> dict[str, object]:
    forward_two_orientation = check_forward_two_orientation_artifact()
    assert_forward_two_orientation_expected(forward_two_orientation)
    source_summary = forward_two_orientation["summary"]
    source_methods = source_summary["method_counts"]

    forward_forward = oriented_shuffle_orders(
        first_tail=FIRST_FORWARD, second_tail=SECOND_FORWARD
    )
    forward_reversed = oriented_shuffle_orders(
        first_tail=FIRST_FORWARD, second_tail=SECOND_REVERSED
    )
    reversed_forward = oriented_shuffle_orders(
        first_tail=FIRST_REVERSED, second_tail=SECOND_FORWARD
    )
    reversed_reversed = oriented_shuffle_orders(
        first_tail=FIRST_REVERSED, second_tail=SECOND_REVERSED
    )
    ff_to_rr = _reversal_pairs(forward_forward, reversed_reversed)
    fr_to_rf = _reversal_pairs(forward_reversed, reversed_forward)

    direct_vc = int(source_summary["vertex_circle_closed_order_count"])
    direct_kalmanson = int(source_summary["kalmanson_after_vertex_circle_escape_count"])
    summary = {
        "orientation_family_count": 4,
        "orders_per_orientation_family": 462,
        "total_oriented_order_count": 1848,
        "direct_source_order_count": int(source_summary["total_family_order_count"]),
        "reversal_dual_order_count": len(ff_to_rr) + len(fr_to_rf),
        "combined_closed_order_count": int(source_summary["combined_closed_order_count"])
        + len(ff_to_rr)
        + len(fr_to_rf),
        "combined_closure_complete": (
            int(source_summary["combined_closed_order_count"])
            + len(ff_to_rr)
            + len(fr_to_rf)
            == 1848
        ),
        "reversal_pair_counts": {
            "forward_forward_to_reversed_reversed": len(ff_to_rr),
            "forward_reversed_to_reversed_forward": len(fr_to_rf),
        },
        "method_counts": {
            "vertex_circle_quotient_direct": direct_vc,
            "kalmanson_after_vertex_circle_escape_direct": direct_kalmanson,
            "vertex_circle_quotient_by_reversal": direct_vc,
            "kalmanson_after_vertex_circle_escape_by_reversal": direct_kalmanson,
            "vertex_circle_quotient_total": 2 * direct_vc,
            "kalmanson_after_vertex_circle_escape_total": 2 * direct_kalmanson,
        },
    }
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifacts": {
            "first_block_forward_two_orientation": {
                "path": FORWARD_TWO_ORIENTATION_OUT.relative_to(ROOT).as_posix(),
                "schema": forward_two_orientation["schema"],
                "status": forward_two_orientation["status"],
            }
        },
        "reversal_rule": {
            "description": (
                "Cyclic reversal keeps label 0 first and reverses the remaining "
                "11 labels. The vertex-circle quotient and Kalmanson strict "
                "inequality obstructions used by the source packets are "
                "unchanged by reversing cyclic orientation."
            ),
            "normalized_cyclic_reverse": "[0] + reversed(order[1:])",
        },
        "summary": summary,
        "orientation_family_crosswalk": [
            _family_record(
                name="forward_forward",
                first_orientation="forward",
                second_orientation="forward",
                closure_source="direct_source",
                closure_methods={
                    "vertex_circle_quotient": int(
                        source_methods["forward_second_block_vertex_circle"]
                    )
                },
            ),
            _family_record(
                name="forward_reversed",
                first_orientation="forward",
                second_orientation="reversed",
                closure_source="direct_source",
                closure_methods={
                    "vertex_circle_quotient": int(
                        source_methods["reversed_second_block_vertex_circle"]
                    ),
                    "kalmanson_after_vertex_circle_escape": int(
                        source_methods[
                            "reversed_second_block_kalmanson_after_vertex_circle_escape"
                        ]
                    ),
                },
            ),
            _family_record(
                name="reversed_forward",
                first_orientation="reversed",
                second_orientation="forward",
                closure_source="cyclic_reversal_of_forward_reversed",
                closure_methods={
                    "vertex_circle_quotient": int(
                        source_methods["reversed_second_block_vertex_circle"]
                    ),
                    "kalmanson_after_vertex_circle_escape": int(
                        source_methods[
                            "reversed_second_block_kalmanson_after_vertex_circle_escape"
                        ]
                    ),
                },
            ),
            _family_record(
                name="reversed_reversed",
                first_orientation="reversed",
                second_orientation="reversed",
                closure_source="cyclic_reversal_of_forward_forward",
                closure_methods={
                    "vertex_circle_quotient": int(
                        source_methods["forward_second_block_vertex_circle"]
                    )
                },
            ),
        ],
        "reversal_pair_samples": {
            "forward_forward_to_reversed_reversed": _compact_pair_samples(ff_to_rr),
            "forward_reversed_to_reversed_forward": _compact_pair_samples(fr_to_rf),
        },
        "provenance": PROVENANCE,
        "interpretation": (
            "The first-block-forward packet directly covers the two orientation "
            "families with first block forward. Normalized cyclic reversal "
            "maps the forward-forward family bijectively to the reversed-"
            "reversed family and the forward-reversed family bijectively to "
            "the reversed-forward family. Since reversing polygon orientation "
            "does not change the distance equalities or the local obstruction "
            "certificates, the same bounded closure counts transfer to all "
            "four oriented-block shuffle families."
        ),
    }


def check_artifact() -> dict[str, object]:
    data = json.loads(OUT.read_text(encoding="utf-8"))
    expected = payload()
    if data != expected:
        raise AssertionError("stored oriented-block reversal artifact differs")
    return data


def assert_expected(data: Mapping[str, object]) -> None:
    if data["summary"] != EXPECTED_SUMMARY:
        raise AssertionError("unexpected oriented-block reversal summary")
    if data["provenance"] != PROVENANCE:
        raise AssertionError("unexpected provenance")
    claim_scope = str(data["claim_scope"])
    for guard in (
        "not arbitrary cyclic-order closure",
        "not all selected-row systems",
        "not a fragile-bridge proof",
        "not a proof of Erdos",
        "not a counterexample",
    ):
        if guard not in claim_scope:
            raise AssertionError(f"claim scope lost guard: {guard}")
    records = data["orientation_family_crosswalk"]
    if not isinstance(records, list) or len(records) != 4:
        raise AssertionError("expected four orientation family records")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    data = check_artifact() if args.check else payload()
    if args.assert_expected:
        assert_expected(data)
    if args.write:
        write_json(data, OUT)

    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        summary = data["summary"]
        print("block6 oriented-block reversal closure crosswalk")
        print(f"oriented orders: {summary['total_oriented_order_count']}")
        print(f"combined closed: {summary['combined_closed_order_count']}")
        print(f"method counts: {summary['method_counts']}")
        if args.assert_expected:
            print("OK: expected oriented-block reversal crosswalk verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
