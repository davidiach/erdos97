#!/usr/bin/env python3
"""Check quotient-level row-Ptolemy feasibility for the endpoint-control survivor."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction

from erdos97.quotient_cone import pair, selected_distance_quotient

SURVIVOR_ROWS: list[list[int]] = [
    [1, 3, 5, 6],
    [0, 2, 7, 9],
    [1, 3, 4, 10],
    [2, 4, 5, 7],
    [1, 6, 7, 8],
    [0, 2, 3, 6],
    [0, 4, 8, 10],
    [1, 2, 4, 9],
    [3, 7, 9, 10],
    [2, 5, 8, 10],
    [0, 1, 8, 9],
]

EXPECTED_CLASS_COUNT = 25

POSITIVE_CLASS_VALUES: dict[int, Fraction] = {
    0: Fraction(1),
    1: Fraction(1),
    2: Fraction(1, 2),
    3: Fraction(1),
    4: Fraction(3),
    5: Fraction(1),
    6: Fraction(2),
    7: Fraction(3, 4),
    8: Fraction(1),
    9: Fraction(1, 4),
    10: Fraction(1),
    11: Fraction(2),
    12: Fraction(3),
    13: Fraction(1),
    14: Fraction(19, 4),
    15: Fraction(11, 4),
    16: Fraction(1, 2),
    17: Fraction(1),
    18: Fraction(1),
    19: Fraction(1, 2),
    20: Fraction(1),
    21: Fraction(1),
    22: Fraction(1, 2),
    23: Fraction(1),
    24: Fraction(1),
}


def _fraction_json(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _witness_order(center: int, row: list[int], order: list[int]) -> list[int]:
    positions = {label: idx for idx, label in enumerate(order)}
    return sorted(row, key=lambda label: (positions[label] - positions[center]) % len(order))


def audit() -> dict[str, object]:
    order = list(range(len(SURVIVOR_ROWS)))
    quotient = selected_distance_quotient(SURVIVOR_ROWS)
    if quotient.class_count != EXPECTED_CLASS_COUNT:
        raise AssertionError(
            f"expected {EXPECTED_CLASS_COUNT} quotient classes, got {quotient.class_count}"
        )
    if sorted(POSITIVE_CLASS_VALUES) != list(range(quotient.class_count)):
        raise AssertionError("positive assignment does not cover every quotient class")
    if any(value <= 0 for value in POSITIVE_CLASS_VALUES.values()):
        raise AssertionError("positive assignment contains a nonpositive value")

    records = []
    for center, row in enumerate(SURVIVOR_ROWS):
        witnesses = _witness_order(center, row, order)
        w0, w1, w2, w3 = witnesses
        pairs = {
            "d01": pair(w0, w1),
            "d02": pair(w0, w2),
            "d03": pair(w0, w3),
            "d12": pair(w1, w2),
            "d13": pair(w1, w3),
            "d23": pair(w2, w3),
        }
        classes = {name: quotient.pair_class[item] for name, item in pairs.items()}
        values = {name: POSITIVE_CLASS_VALUES[classes[name]] for name in pairs}
        lhs = values["d02"] * values["d13"]
        rhs_terms = (
            values["d01"] * values["d23"],
            values["d03"] * values["d12"],
        )
        rhs = rhs_terms[0] + rhs_terms[1]
        if lhs != rhs:
            raise AssertionError(f"row {center} violates row-Ptolemy")
        records.append(
            {
                "row": center,
                "witness_order": witnesses,
                "classes": {name: int(classes[name]) for name in sorted(classes)},
                "class_values": {
                    name: _fraction_json(values[name]) for name in sorted(values)
                },
                "ptolemy_lhs": _fraction_json(lhs),
                "ptolemy_rhs_terms": [_fraction_json(term) for term in rhs_terms],
                "ptolemy_rhs": _fraction_json(rhs),
                "ptolemy_verified": True,
            }
        )

    return {
        "type": "endpoint_control_survivor_quotient_ptolemy_feasibility",
        "schema": "erdos97.endpoint_control_survivor_quotient_ptolemy_feasibility.v1",
        "cyclic_order": order,
        "rows": {str(center): row for center, row in enumerate(SURVIVOR_ROWS)},
        "distance_class_count": quotient.class_count,
        "distance_class_values": {
            str(class_idx): _fraction_json(value)
            for class_idx, value in sorted(POSITIVE_CLASS_VALUES.items())
        },
        "positive_assignment": True,
        "row_ptolemy_equations_verified": len(records),
        "records": records,
        "interpretation": (
            "Exact positive rational feasibility for the selected-distance quotient "
            "and row-Ptolemy equations of the Cycle 674 endpoint-control survivor. "
            "This is not a metric realization certificate and not a counterexample."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    payload = audit()
    if args.assert_expected:
        if payload["distance_class_count"] != EXPECTED_CLASS_COUNT:
            raise AssertionError("unexpected distance class count")
        if payload["row_ptolemy_equations_verified"] != len(SURVIVOR_ROWS):
            raise AssertionError("unexpected row-Ptolemy verification count")
        if not payload["positive_assignment"]:
            raise AssertionError("expected positive assignment")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("endpoint-control survivor quotient-Ptolemy feasibility")
        print(f"distance classes: {payload['distance_class_count']}")
        print(
            "row-Ptolemy equations verified: "
            f"{payload['row_ptolemy_equations_verified']}"
        )
        print(f"positive assignment: {payload['positive_assignment']}")
        if args.assert_expected:
            print("OK: expected feasibility certificate verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
