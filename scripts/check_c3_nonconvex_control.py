#!/usr/bin/env python3
"""Exact checker for a nonconvex C3-symmetric all-four-rich control.

The checked nine-point set is not a counterexample to Erdos Problem #97 because
only six points are vertices of its convex hull. The script records an exact
negative control and does not change the global open status.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import combinations
from typing import Any, Iterable

SCHEMA = "erdos97.c3_nonconvex_control.v1"
STATUS = "EXACT_NONCONVEX_NEGATIVE_CONTROL"
TRUST = "EXACT_RATIONAL_QUADRATIC_ARITHMETIC"
PARAMETERS = (Fraction(1), Fraction(2), Fraction(-3))
EXPECTED_COMMON_SQUARED_DISTANCE = Fraction(7)

# A point is stored as (x, y_coefficient), representing (x, y_coefficient*sqrt(3)).
Point = tuple[Fraction, Fraction]
Label = tuple[int, int]

CLAIM_SCOPE = (
    "Exact verification of a nine-point C3-symmetric configuration in which "
    "every point has exactly four companions at one common positive distance. "
    "The configuration is nonconvex: its convex hull has six vertices. It is "
    "therefore a search negative control, not a counterexample to Erdos "
    "Problem #97 and not a change to the official/global open status."
)


def orbit_point(parameter: Fraction, phase: int) -> Point:
    """Return parameter*omega**phase in the Q(sqrt(3)) coordinate model."""

    phase %= 3
    if phase == 0:
        return (parameter, Fraction(0))
    if phase == 1:
        return (-parameter / 2, parameter / 2)
    return (-parameter / 2, -parameter / 2)


def squared_distance(left: Point, right: Point) -> Fraction:
    """Return the exact squared Euclidean distance."""

    dx = left[0] - right[0]
    dy_coefficient = left[1] - right[1]
    return dx * dx + 3 * dy_coefficient * dy_coefficient


def orientation_coefficient(a: Point, b: Point, c: Point) -> Fraction:
    """Return orientation(a,b,c)/sqrt(3), an exact rational number."""

    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (
        c[0] - a[0]
    )


def selected_witnesses(label: Label) -> tuple[Label, Label, Label, Label]:
    """Return the four prescribed common-distance witnesses for one point."""

    orbit, phase = label
    other_orbits = [candidate for candidate in range(3) if candidate != orbit]
    witnesses = [
        (other_orbit, (phase + phase_shift) % 3)
        for other_orbit in other_orbits
        for phase_shift in (1, 2)
    ]
    if len(witnesses) != 4:
        raise AssertionError("the C3 control must supply exactly four witnesses")
    return (witnesses[0], witnesses[1], witnesses[2], witnesses[3])


def convex_hull(labels: Iterable[Label], points: dict[Label, Point]) -> list[Label]:
    """Return the exact strict monotone-chain hull in counterclockwise order."""

    ordered = sorted(labels, key=lambda label: points[label])

    def build_half(sequence: Iterable[Label]) -> list[Label]:
        half: list[Label] = []
        for label in sequence:
            while len(half) >= 2 and orientation_coefficient(
                points[half[-2]], points[half[-1]], points[label]
            ) <= 0:
                half.pop()
            half.append(label)
        return half

    lower = build_half(ordered)
    upper = build_half(reversed(ordered))
    return lower[:-1] + upper[:-1]


def fraction_json(value: Fraction) -> int | str:
    """Serialize a fraction without losing exactness."""

    if value.denominator == 1:
        return value.numerator
    return f"{value.numerator}/{value.denominator}"


def label_json(label: Label) -> str:
    return f"p{label[0]}_{label[1]}"


def build_payload() -> dict[str, Any]:
    """Build the exact verification payload."""

    labels = [(orbit, phase) for orbit in range(3) for phase in range(3)]
    points = {
        label: orbit_point(PARAMETERS[label[0]], label[1]) for label in labels
    }

    all_pair_distances: dict[Fraction, list[tuple[Label, Label]]] = {}
    for left, right in combinations(labels, 2):
        distance = squared_distance(points[left], points[right])
        all_pair_distances.setdefault(distance, []).append((left, right))

    center_records: list[dict[str, Any]] = []
    selected_degrees = {label: 0 for label in labels}
    selected_edges: set[tuple[Label, Label]] = set()

    for center in labels:
        witnesses = selected_witnesses(center)
        distances = [squared_distance(points[center], points[w]) for w in witnesses]
        for witness in witnesses:
            left, right = sorted((center, witness))
            selected_edges.add((left, right))
        selected_degrees[center] = len(witnesses)
        center_records.append(
            {
                "center": label_json(center),
                "witnesses": [label_json(witness) for witness in witnesses],
                "squared_distances": [fraction_json(value) for value in distances],
            }
        )

    hull = convex_hull(labels, points)
    common_distance_pairs = all_pair_distances[EXPECTED_COMMON_SQUARED_DISTANCE]
    common_distance_degrees = {label: 0 for label in labels}
    for left, right in common_distance_pairs:
        common_distance_degrees[left] += 1
        common_distance_degrees[right] += 1

    point_records = {
        label_json(label): {
            "x": fraction_json(points[label][0]),
            "y_sqrt3_coefficient": fraction_json(points[label][1]),
        }
        for label in labels
    }
    distance_histogram = {
        str(fraction_json(distance)): len(pairs)
        for distance, pairs in sorted(all_pair_distances.items())
    }

    summary = {
        "point_count": len(labels),
        "distinct_point_count": len(set(points.values())),
        "parameter_sum": fraction_json(sum(PARAMETERS, Fraction(0))),
        "common_squared_distance": fraction_json(EXPECTED_COMMON_SQUARED_DISTANCE),
        "common_distance_pair_count": len(common_distance_pairs),
        "common_distance_degree_histogram": {
            str(degree): sum(
                1
                for value in common_distance_degrees.values()
                if value == degree
            )
            for degree in sorted(set(common_distance_degrees.values()))
        },
        "selected_edge_count": len(selected_edges),
        "selected_degree_histogram": {
            str(degree): sum(
                1 for value in selected_degrees.values() if value == degree
            )
            for degree in sorted(set(selected_degrees.values()))
        },
        "convex_hull_vertex_count": len(hull),
        "convex_hull_labels": [label_json(label) for label in hull],
        "distance_pair_histogram": distance_histogram,
    }
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "parameters": [fraction_json(value) for value in PARAMETERS],
        "points": point_records,
        "centers": center_records,
        "summary": summary,
    }


def validate_payload(payload: dict[str, Any]) -> list[str]:
    """Return validation errors for the exact payload."""

    errors: list[str] = []
    summary = payload.get("summary", {})
    expected = {
        "point_count": 9,
        "distinct_point_count": 9,
        "parameter_sum": 0,
        "common_squared_distance": 7,
        "common_distance_pair_count": 18,
        "common_distance_degree_histogram": {"4": 9},
        "selected_edge_count": 18,
        "selected_degree_histogram": {"4": 9},
        "convex_hull_vertex_count": 6,
        "distance_pair_histogram": {
            "1": 3,
            "3": 3,
            "7": 18,
            "12": 3,
            "16": 3,
            "25": 3,
            "27": 3,
        },
    }
    for key, expected_value in expected.items():
        if summary.get(key) != expected_value:
            errors.append(
                f"summary[{key!r}]={summary.get(key)!r}, expected {expected_value!r}"
            )

    for record in payload.get("centers", []):
        if len(record.get("witnesses", [])) != 4:
            errors.append(f"{record.get('center')}: expected four witnesses")
        if record.get("squared_distances") != [7, 7, 7, 7]:
            errors.append(
                f"{record.get('center')}: unexpected squared distances "
                f"{record.get('squared_distances')!r}"
            )
    return errors


def summary_payload(payload: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    """Return a compact CLI summary."""

    return {
        "schema": payload["schema"],
        "status": payload["status"],
        "validation_status": "passed" if not errors else "failed",
        "errors": errors,
        **payload["summary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full-json",
        action="store_true",
        help="print the complete exact payload rather than the compact summary",
    )
    args = parser.parse_args()

    payload = build_payload()
    errors = validate_payload(payload)
    output = payload if args.full_json else summary_payload(payload, errors)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
