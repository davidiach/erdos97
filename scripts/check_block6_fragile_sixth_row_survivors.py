#!/usr/bin/env python3
"""Catalog sixth-row survivors after clean block-6 fifth rows."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_block6_fragile_vertex_circle_extension import (  # noqa: E402
    N,
    _add_row,
    _initial_state,
    _options,
    _partial_vertex_circle_status,
    _remove_row,
    _valid_options,
)

STATUSES = ("ok", "self_edge", "strict_cycle")
EXPECTED_TOTALS = {
    "clean_fifth_rows": 166,
    "clean_fifth_block_swap_orbits": 83,
    "ordered_legal_sixth_rows_after_clean_fifth": 29844,
    "ordered_clean_sixth_rows": 12094,
    "ordered_self_edge_sixth_rows": 8108,
    "ordered_strict_cycle_sixth_rows": 9642,
    "clean_fifth_rows_with_clean_sixth": 166,
    "unique_clean_six_row_states": 6047,
    "unique_clean_six_row_block_swap_orbits": 3056,
    "clean_center_pairs": 28,
    "clean_center_pair_block_swap_orbits": 16,
}
EXPECTED_CLEAN_SIX_ORBIT_SIZES = {"1": 65, "2": 2991}
EXPECTED_CLEAN_BY_CENTER_PAIR = {
    "1,2": 350,
    "1,4": 98,
    "1,5": 126,
    "1,7": 256,
    "1,8": 508,
    "1,10": 69,
    "1,11": 105,
    "2,4": 182,
    "2,5": 238,
    "2,7": 508,
    "2,8": 1074,
    "2,10": 176,
    "2,11": 325,
    "4,5": 28,
    "4,7": 69,
    "4,8": 176,
    "4,10": 36,
    "4,11": 71,
    "5,7": 105,
    "5,8": 325,
    "5,10": 71,
    "5,11": 129,
    "7,8": 350,
    "7,10": 98,
    "7,11": 126,
    "8,10": 182,
    "8,11": 238,
    "10,11": 28,
}
EXPECTED_CLEAN_BY_CENTER_PAIR_ORBIT = {
    "1,2|7,8": 700,
    "1,4|7,10": 196,
    "1,5|7,11": 252,
    "1,7": 256,
    "1,8|2,7": 1016,
    "1,10|4,7": 138,
    "1,11|5,7": 210,
    "2,4|8,10": 364,
    "2,5|8,11": 476,
    "2,8": 1074,
    "2,10|4,8": 352,
    "2,11|5,8": 650,
    "4,5|10,11": 56,
    "4,10": 36,
    "4,11|5,10": 142,
    "5,11": 129,
}
EXPECTED_LOW_SUPPORT_ROW_CONTENT_FORMS = {
    "4,5": {
        "clean_states": 28,
        "same_block_pair_counts": {
            "0,3|0,1": 14,
            "0,3|0,4": 14,
        },
        "opposite_pair_pool": [
            "6,7",
            "6,9",
            "6,10",
            "7,11",
            "8,11",
            "9,11",
        ],
        "opposite_pair_edge_counts": {
            "6,7|8,11": 2,
            "6,7|9,11": 2,
            "6,9|7,11": 2,
            "6,9|8,11": 2,
            "6,10|7,11": 2,
            "6,10|8,11": 2,
            "6,10|9,11": 2,
            "7,11|6,9": 2,
            "7,11|6,10": 2,
            "8,11|6,7": 2,
            "8,11|6,9": 2,
            "8,11|6,10": 2,
            "9,11|6,7": 2,
            "9,11|6,10": 2,
        },
        "ordered_disjoint_opposite_pair_edges": 14,
        "all_edges_disjoint": True,
        "all_disjoint_pool_edges_present": True,
    },
    "10,11": {
        "clean_states": 28,
        "same_block_pair_counts": {
            "6,9|6,7": 14,
            "6,9|6,10": 14,
        },
        "opposite_pair_pool": [
            "0,1",
            "0,3",
            "0,4",
            "1,5",
            "2,5",
            "3,5",
        ],
        "opposite_pair_edge_counts": {
            "0,1|2,5": 2,
            "0,1|3,5": 2,
            "0,3|1,5": 2,
            "0,3|2,5": 2,
            "0,4|1,5": 2,
            "0,4|2,5": 2,
            "0,4|3,5": 2,
            "1,5|0,3": 2,
            "1,5|0,4": 2,
            "2,5|0,1": 2,
            "2,5|0,3": 2,
            "2,5|0,4": 2,
            "3,5|0,1": 2,
            "3,5|0,4": 2,
        },
        "ordered_disjoint_opposite_pair_edges": 14,
        "all_edges_disjoint": True,
        "all_disjoint_pool_edges_present": True,
    },
}
EXPECTED_BY_FIFTH_CENTER = {
    "1": {
        "clean_fifth": 21,
        "sixth_total": 3973,
        "sixth_ok": 1512,
        "sixth_self_edge": 1185,
        "sixth_strict_cycle": 1276,
    },
    "2": {
        "clean_fifth": 41,
        "sixth_total": 7178,
        "sixth_ok": 2853,
        "sixth_self_edge": 1916,
        "sixth_strict_cycle": 2409,
    },
    "4": {
        "clean_fifth": 7,
        "sixth_total": 1211,
        "sixth_ok": 660,
        "sixth_self_edge": 281,
        "sixth_strict_cycle": 270,
    },
    "5": {
        "clean_fifth": 14,
        "sixth_total": 2560,
        "sixth_ok": 1022,
        "sixth_self_edge": 672,
        "sixth_strict_cycle": 866,
    },
    "7": {
        "clean_fifth": 21,
        "sixth_total": 3973,
        "sixth_ok": 1512,
        "sixth_self_edge": 1185,
        "sixth_strict_cycle": 1276,
    },
    "8": {
        "clean_fifth": 41,
        "sixth_total": 7178,
        "sixth_ok": 2853,
        "sixth_self_edge": 1916,
        "sixth_strict_cycle": 2409,
    },
    "10": {
        "clean_fifth": 7,
        "sixth_total": 1211,
        "sixth_ok": 660,
        "sixth_self_edge": 281,
        "sixth_strict_cycle": 270,
    },
    "11": {
        "clean_fifth": 14,
        "sixth_total": 2560,
        "sixth_ok": 1022,
        "sixth_self_edge": 672,
        "sixth_strict_cycle": 866,
    },
}

RowRecord = tuple[int, tuple[int, ...]]
SixState = tuple[RowRecord, RowRecord]
CenterPair = tuple[int, int]
LabelPair = tuple[int, int]


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _swap_label(label: int) -> int:
    return (label + 6) % N


def _block_swap_row(record: RowRecord) -> RowRecord:
    center, row = record
    return (_swap_label(center), tuple(sorted(_swap_label(label) for label in row)))


def _center_pair_key(pair: CenterPair) -> str:
    return f"{pair[0]},{pair[1]}"


def _pair_edge_key(left: LabelPair, right: LabelPair) -> str:
    return f"{_center_pair_key(left)}|{_center_pair_key(right)}"


def _parse_label_pair(text: str) -> LabelPair:
    left, right = text.split(",")
    return (int(left), int(right))


def _pair_edge_is_disjoint(key: str) -> bool:
    left_text, right_text = key.split("|")
    left = _parse_label_pair(left_text)
    right = _parse_label_pair(right_text)
    return set(left).isdisjoint(right)


def _block_swap_center_pair(pair: CenterPair) -> CenterPair:
    return tuple(sorted((_swap_label(pair[0]), _swap_label(pair[1]))))  # type: ignore[return-value]


def _center_pair_orbit_key(pair: CenterPair) -> str:
    orbit = sorted({pair, _block_swap_center_pair(pair)})
    return "|".join(_center_pair_key(item) for item in orbit)


def _block_swap_six_state(state: SixState) -> SixState:
    return tuple(sorted(_block_swap_row(record) for record in state))  # type: ignore[return-value]


def _split_row_by_center_block(center: int, row: tuple[int, ...]) -> tuple[LabelPair, LabelPair]:
    block_start = 0 if center < N // 2 else N // 2
    block = set(range(block_start, block_start + N // 2))
    same = tuple(label for label in row if label in block)
    opposite = tuple(label for label in row if label not in block)
    if len(same) != 2 or len(opposite) != 2:
        raise AssertionError(
            f"row at center {center} does not split into two-and-two: {row!r}"
        )
    return same, opposite  # type: ignore[return-value]


def _low_support_row_content_forms(
    clean_six_states: set[SixState],
) -> dict[str, dict[str, Any]]:
    forms: dict[str, dict[str, Any]] = {}
    for center_pair in ((4, 5), (10, 11)):
        matching_states = [
            state
            for state in clean_six_states
            if tuple(record[0] for record in state) == center_pair
        ]
        same_block_counts: Counter[str] = Counter()
        opposite_edge_counts: Counter[str] = Counter()
        opposite_pool: set[LabelPair] = set()

        for (left_center, left_row), (right_center, right_row) in matching_states:
            left_same, left_opposite = _split_row_by_center_block(
                left_center,
                left_row,
            )
            right_same, right_opposite = _split_row_by_center_block(
                right_center,
                right_row,
            )
            same_block_counts[_pair_edge_key(left_same, right_same)] += 1
            opposite_edge_counts[
                _pair_edge_key(left_opposite, right_opposite)
            ] += 1
            opposite_pool.add(left_opposite)
            opposite_pool.add(right_opposite)

        disjoint_edge_keys = {
            _pair_edge_key(left, right)
            for left in opposite_pool
            for right in opposite_pool
            if set(left).isdisjoint(right)
        }
        actual_edge_keys = set(opposite_edge_counts)
        forms[_center_pair_key(center_pair)] = {
            "clean_states": len(matching_states),
            "same_block_pair_counts": dict(sorted(same_block_counts.items())),
            "opposite_pair_pool": [
                _center_pair_key(pair) for pair in sorted(opposite_pool)
            ],
            "opposite_pair_edge_counts": dict(
                sorted(opposite_edge_counts.items())
            ),
            "ordered_disjoint_opposite_pair_edges": len(disjoint_edge_keys),
            "all_edges_disjoint": all(
                _pair_edge_is_disjoint(key) for key in actual_edge_keys
            ),
            "all_disjoint_pool_edges_present": actual_edge_keys == disjoint_edge_keys,
        }
    return forms


def _orbit_count(states: set[RowRecord] | set[SixState]) -> tuple[int, Counter[int]]:
    seen: set[Any] = set()
    sizes: Counter[int] = Counter()
    for state in sorted(states):
        if state in seen:
            continue
        if state and isinstance(state[0], int):
            orbit = {state, _block_swap_row(state)}  # type: ignore[arg-type]
        else:
            orbit = {state, _block_swap_six_state(state)}  # type: ignore[arg-type]
        seen.update(orbit)
        sizes[len(orbit)] += 1
    return sum(sizes.values()), sizes


def survivor_payload() -> dict[str, Any]:
    """Classify all legal sixth rows after every clean fifth-row state."""

    assigned, pair_counts, indegrees = _initial_state()
    options = _options()
    clean_fifth_rows: set[RowRecord] = set()
    ordered_sixth_status: Counter[str] = Counter()
    by_fifth_center: dict[str, Counter[str]] = {}
    clean_fifth_with_clean_sixth = 0
    clean_six_states: set[SixState] = set()
    first_clean_sixth_example: dict[str, Any] | None = None

    for fifth_center in range(N):
        if fifth_center in assigned:
            continue
        for fifth_row in _valid_options(
            fifth_center,
            options,
            assigned,
            pair_counts,
            indegrees,
        ):
            _add_row(assigned, pair_counts, indegrees, fifth_center, fifth_row)
            fifth_status, _edge_count = _partial_vertex_circle_status(assigned)
            if fifth_status == "ok":
                fifth_record = (fifth_center, tuple(fifth_row))
                clean_fifth_rows.add(fifth_record)
                center_counts = by_fifth_center.setdefault(
                    str(fifth_center),
                    Counter({"clean_fifth": 0}),
                )
                center_counts["clean_fifth"] += 1
                local_clean_sixth = 0

                for sixth_center in range(N):
                    if sixth_center in assigned:
                        continue
                    for sixth_row in _valid_options(
                        sixth_center,
                        options,
                        assigned,
                        pair_counts,
                        indegrees,
                    ):
                        _add_row(
                            assigned,
                            pair_counts,
                            indegrees,
                            sixth_center,
                            sixth_row,
                        )
                        sixth_status, _edge_count = _partial_vertex_circle_status(
                            assigned
                        )
                        _remove_row(
                            assigned,
                            pair_counts,
                            indegrees,
                            sixth_center,
                            sixth_row,
                        )

                        ordered_sixth_status[sixth_status] += 1
                        center_counts["sixth_total"] += 1
                        center_counts[f"sixth_{sixth_status}"] += 1
                        if sixth_status == "ok":
                            local_clean_sixth += 1
                            six_state: SixState = tuple(
                                sorted((fifth_record, (sixth_center, tuple(sixth_row))))
                            )  # type: ignore[assignment]
                            clean_six_states.add(six_state)
                            if first_clean_sixth_example is None:
                                first_clean_sixth_example = {
                                    "fifth": {
                                        "center": fifth_center,
                                        "row": list(fifth_row),
                                    },
                                    "sixth": {
                                        "center": sixth_center,
                                        "row": list(sixth_row),
                                    },
                                }
                if local_clean_sixth:
                    clean_fifth_with_clean_sixth += 1
            _remove_row(assigned, pair_counts, indegrees, fifth_center, fifth_row)

    clean_fifth_orbits, clean_fifth_orbit_sizes = _orbit_count(clean_fifth_rows)
    clean_six_orbits, clean_six_orbit_sizes = _orbit_count(clean_six_states)
    clean_by_center_pair: Counter[CenterPair] = Counter(
        tuple(sorted((state[0][0], state[1][0]))) for state in clean_six_states
    )
    clean_by_center_pair_orbit: Counter[str] = Counter()
    for center_pair, count in clean_by_center_pair.items():
        clean_by_center_pair_orbit[_center_pair_orbit_key(center_pair)] += count
    totals = {
        "clean_fifth_rows": len(clean_fifth_rows),
        "clean_fifth_block_swap_orbits": clean_fifth_orbits,
        "ordered_legal_sixth_rows_after_clean_fifth": sum(
            ordered_sixth_status.values()
        ),
        "ordered_clean_sixth_rows": int(ordered_sixth_status["ok"]),
        "ordered_self_edge_sixth_rows": int(ordered_sixth_status["self_edge"]),
        "ordered_strict_cycle_sixth_rows": int(ordered_sixth_status["strict_cycle"]),
        "clean_fifth_rows_with_clean_sixth": clean_fifth_with_clean_sixth,
        "unique_clean_six_row_states": len(clean_six_states),
        "unique_clean_six_row_block_swap_orbits": clean_six_orbits,
        "clean_center_pairs": len(clean_by_center_pair),
        "clean_center_pair_block_swap_orbits": len(clean_by_center_pair_orbit),
    }

    return {
        "schema": "erdos97.block6_fragile_sixth_row_survivor_catalog.v1",
        "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
        "claim_scope": (
            "Legal sixth rows after clean one-row extensions of the two-block "
            "block-6 fragile rows in the natural cyclic order; not a proof of "
            "Erdos Problem #97 and not a counterexample."
        ),
        "fixed_centers": sorted(assigned),
        "totals": totals,
        "ordered_sixth_status_counts": {
            status: int(ordered_sixth_status[status]) for status in STATUSES
        },
        "clean_fifth_block_swap_orbit_sizes": _json_counter(
            clean_fifth_orbit_sizes
        ),
        "clean_six_block_swap_orbit_sizes": _json_counter(clean_six_orbit_sizes),
        "clean_by_center_pair": {
            _center_pair_key(center_pair): int(clean_by_center_pair[center_pair])
            for center_pair in sorted(clean_by_center_pair)
        },
        "clean_by_center_pair_orbit": {
            key: int(clean_by_center_pair_orbit[key])
            for key in sorted(clean_by_center_pair_orbit)
        },
        "low_support_row_content_forms": _low_support_row_content_forms(
            clean_six_states
        ),
        "by_fifth_center": {
            center: {key: int(counter[key]) for key in sorted(counter)}
            for center, counter in sorted(by_fifth_center.items(), key=lambda item: int(item[0]))
        },
        "first_clean_sixth_example": first_clean_sixth_example,
    }


def assert_expected(payload: Mapping[str, Any]) -> None:
    if payload["status"] != "REVIEW_PENDING_DIAGNOSTIC_ONLY":
        raise AssertionError("unexpected status")
    if "not a proof" not in payload["claim_scope"]:
        raise AssertionError("claim scope lost no-proof note")
    if payload["totals"] != EXPECTED_TOTALS:
        raise AssertionError(f"unexpected totals: {payload['totals']!r}")
    if payload["clean_six_block_swap_orbit_sizes"] != EXPECTED_CLEAN_SIX_ORBIT_SIZES:
        raise AssertionError(
            "unexpected clean-six orbit sizes: "
            f"{payload['clean_six_block_swap_orbit_sizes']!r}"
        )
    if payload["clean_by_center_pair"] != EXPECTED_CLEAN_BY_CENTER_PAIR:
        raise AssertionError(
            f"unexpected clean center-pair counts: {payload['clean_by_center_pair']!r}"
        )
    if (
        payload["clean_by_center_pair_orbit"]
        != EXPECTED_CLEAN_BY_CENTER_PAIR_ORBIT
    ):
        raise AssertionError(
            "unexpected center-pair orbit counts: "
            f"{payload['clean_by_center_pair_orbit']!r}"
        )
    if (
        payload["low_support_row_content_forms"]
        != EXPECTED_LOW_SUPPORT_ROW_CONTENT_FORMS
    ):
        raise AssertionError(
            "unexpected low-support row-content normal forms: "
            f"{payload['low_support_row_content_forms']!r}"
        )
    if payload["by_fifth_center"] != EXPECTED_BY_FIFTH_CENTER:
        raise AssertionError(
            f"unexpected by-fifth-center counts: {payload['by_fifth_center']!r}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print full JSON payload")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert the current expected survivor counts",
    )
    args = parser.parse_args()

    payload = survivor_payload()
    if args.assert_expected:
        assert_expected(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        totals = payload["totals"]
        print("block6 fragile sixth-row survivor catalog")
        print(
            "totals: "
            f"clean_fifth={totals['clean_fifth_rows']} "
            f"ordered_sixth={totals['ordered_legal_sixth_rows_after_clean_fifth']} "
            f"ordered_clean_sixth={totals['ordered_clean_sixth_rows']} "
            f"unique_clean_six={totals['unique_clean_six_row_states']}"
        )
        if args.assert_expected:
            print("OK: block6 sixth-row survivor catalog matched expected counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
