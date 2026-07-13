#!/usr/bin/env python3
"""Check an exact local negative control for canonical-chord noncrossing.

The rational decagon has exactly two bad centers.  At each center, the unique rich
distance class has four witnesses and a unique shortest witness chord.  The
two resulting canonical chords cross.  This refutes a purely local
noncrossing rule; it is not a counterexample to Erdos Problem #97.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import json
from pathlib import Path
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
OUT = (
    ROOT
    / "data"
    / "certificates"
    / "canonical_shortest_chord_crossing_control.json"
)

SCHEMA = "erdos97.canonical_shortest_chord_crossing_control.v1"
STATUS = "EXACT_LOCAL_NEGATIVE_CONTROL"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact rational strictly convex decagon with exactly two bad centers; every "
    "other center has all nine distances distinct. At each bad center, the "
    "unique distance class of size at least four has exactly four "
    "witnesses and a unique shortest witness chord; the two canonical chords "
    "cross. This refutes noncrossing as a consequence of the local bad-center "
    "hypotheses and this deterministic rule only. It does not refute "
    "canonical-chord injectivity, impose global badness or minimality, prove "
    "Erdos Problem #97, or give a counterexample."
)
PROVENANCE = {
    "generator": "scripts/check_canonical_shortest_chord_crossing.py",
    "command": (
        "python scripts/check_canonical_shortest_chord_crossing.py --write "
        "--assert-expected --summary-json"
    ),
    "source_attachment_sha256": (
        "205b468cf9dce4af5c20a04d3d5537c2d2e70fd90c8ad97ac4ce9b231f9f1a2c"
    ),
}

Point = tuple[Fraction, Fraction]
Chord = tuple[int, int]

EXPECTED_WITNESSES = {0: (2, 4, 6, 8), 1: (3, 5, 7, 9)}
EXPECTED_CHORDS = {0: (2, 4), 1: (3, 5)}
EXPECTED_SHORTEST_SQUARED = {
    0: Fraction(695556, 13584133),
    1: Fraction(13510836652681, 273978475879725),
}
EXPECTED_MINIMUM_DETERMINANT = Fraction(
    4166275382872427, 4803025334488832400
)


def rational_text(value: Fraction) -> str:
    """Return one canonical JSON-safe rational representation."""

    return str(value.numerator) if value.denominator == 1 else str(value)


def unit_circle(t: Fraction) -> Point:
    """Rational parametrization of the unit circle."""

    denominator = 1 + t * t
    return ((1 - t * t) / denominator, 2 * t / denominator)


def add(first: Point, second: Point) -> Point:
    return (first[0] + second[0], first[1] + second[1])


def scale(value: Fraction, point: Point) -> Point:
    return (value * point[0], value * point[1])


def squared_distance(first: Point, second: Point) -> Fraction:
    dx = first[0] - second[0]
    dy = first[1] - second[1]
    return dx * dx + dy * dy


def left_turn(first: Point, second: Point, third: Point) -> Fraction:
    return (second[0] - first[0]) * (third[1] - first[1]) - (
        second[1] - first[1]
    ) * (third[0] - first[0])


def points() -> tuple[Point, ...]:
    """Build the ten rational points in their claimed cyclic order."""

    result: list[Point | None] = [None] * 10
    result[0] = (Fraction(0), Fraction(0))
    result[1] = (Fraction(1, 800), -Fraction(1, 76))
    radius = Fraction(223, 222)

    first_parameters = {
        2: Fraction(11, 280),
        4: Fraction(2, 13),
        6: Fraction(108, 347),
        8: Fraction(219, 409),
    }
    second_parameters = {
        3: Fraction(43, 354),
        5: Fraction(96, 407),
        7: Fraction(95, 239),
        9: Fraction(201, 197),
    }
    for index, parameter in first_parameters.items():
        result[index] = unit_circle(parameter)
    for index, parameter in second_parameters.items():
        assert result[1] is not None
        result[index] = add(result[1], scale(radius, unit_circle(parameter)))

    if any(point is None for point in result):
        raise AssertionError("point construction left an uninitialized entry")
    return tuple(point for point in result if point is not None)


def distance_classes(configuration: tuple[Point, ...], center: int) -> dict[Fraction, tuple[int, ...]]:
    classes: defaultdict[Fraction, list[int]] = defaultdict(list)
    for index, point in enumerate(configuration):
        if index != center:
            classes[squared_distance(configuration[center], point)].append(index)
    return {distance: tuple(indices) for distance, indices in classes.items()}


def chord_lengths(
    configuration: tuple[Point, ...], witnesses: Iterable[int]
) -> tuple[tuple[Fraction, Chord], ...]:
    witness_tuple = tuple(witnesses)
    lengths = []
    for offset, first in enumerate(witness_tuple):
        for second in witness_tuple[offset + 1 :]:
            lengths.append(
                (squared_distance(configuration[first], configuration[second]), (first, second))
            )
    return tuple(sorted(lengths))


def chords_cross(first: Chord, second: Chord, order: tuple[int, ...]) -> bool:
    """Check strict endpoint alternation for two chords in a cyclic order."""

    if set(first) & set(second):
        return False
    positions = {vertex: index for index, vertex in enumerate(order)}
    a, b = sorted((positions[first[0]], positions[first[1]]))
    c, d = sorted((positions[second[0]], positions[second[1]]))
    return (a < c < b < d) or (c < a < d < b)


def convexity_certificate(
    configuration: tuple[Point, ...],
) -> tuple[tuple[Fraction, int, int], ...]:
    checks = []
    n = len(configuration)
    for edge_start in range(n):
        edge_end = (edge_start + 1) % n
        for point_index in range(n):
            if point_index not in (edge_start, edge_end):
                checks.append(
                    (
                        left_turn(
                            configuration[edge_start],
                            configuration[edge_end],
                            configuration[point_index],
                        ),
                        edge_start,
                        point_index,
                    )
                )
    return tuple(sorted(checks))


def build_payload() -> dict[str, object]:
    configuration = points()
    order = tuple(range(len(configuration)))
    convexity = convexity_certificate(configuration)
    classes_by_center = tuple(
        distance_classes(configuration, center)
        for center in range(len(configuration))
    )
    max_multiplicities = [
        max(len(indices) for indices in classes.values())
        for classes in classes_by_center
    ]
    exact_bad_centers = [
        center
        for center, multiplicity in enumerate(max_multiplicities)
        if multiplicity >= 4
    ]
    centers: list[dict[str, object]] = []
    selected_chords: list[Chord] = []

    for center in (0, 1):
        classes = classes_by_center[center]
        rich_classes = [
            (distance, witnesses)
            for distance, witnesses in classes.items()
            if len(witnesses) >= 4
        ]
        rich_classes.sort()
        if len(rich_classes) != 1:
            raise AssertionError(
                f"center {center} has {len(rich_classes)} rich distance classes"
            )
        rich_distance, witnesses = rich_classes[0]
        lengths = chord_lengths(configuration, witnesses)
        shortest_squared, selected_chord = lengths[0]
        if len(lengths) < 2 or not shortest_squared < lengths[1][0]:
            raise AssertionError(f"center {center} has no unique shortest chord")
        selected_chords.append(selected_chord)
        centers.append(
            {
                "center": center,
                "unique_rich_class": True,
                "rich_distance_squared": rational_text(rich_distance),
                "witnesses": list(witnesses),
                "distance_class_multiplicities": sorted(
                    (len(indices) for indices in classes.values()), reverse=True
                ),
                "unique_shortest_witness_chord": list(selected_chord),
                "shortest_chord_squared": rational_text(shortest_squared),
                "other_chord_squared_lengths": [
                    {
                        "chord": list(chord),
                        "squared_length": rational_text(length),
                    }
                    for length, chord in lengths[1:]
                ],
                "all_other_chords_strictly_longer": all(
                    shortest_squared < length for length, _ in lengths[1:]
                ),
            }
        )

    minimum_determinant, minimum_edge_start, minimum_point = convexity[0]
    crossing = chords_cross(selected_chords[0], selected_chords[1], order)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "provenance": PROVENANCE,
        "n": len(configuration),
        "cyclic_order": list(order),
        "points": [
            [rational_text(coordinate) for coordinate in point]
            for point in configuration
        ],
        "strict_convexity": {
            "orientation": "counterclockwise",
            "half_plane_checks": len(convexity),
            "all_positive": all(determinant > 0 for determinant, _, _ in convexity),
            "minimum_determinant": rational_text(minimum_determinant),
            "minimum_attained_at": {
                "directed_edge": [minimum_edge_start, (minimum_edge_start + 1) % 10],
                "point": minimum_point,
            },
        },
        "canonical_rule": (
            "smallest radius with at least four witnesses, then unique shortest "
            "chord in that rich class"
        ),
        "bad_centers": centers,
        "center_max_distance_multiplicities": max_multiplicities,
        "exact_bad_centers": exact_bad_centers,
        "all_other_centers_good": exact_bad_centers == [0, 1],
        "erdos97_counterexample": all(
            multiplicity >= 4 for multiplicity in max_multiplicities
        ),
        "selected_chords": [list(chord) for chord in selected_chords],
        "selected_chords_cross": crossing,
        "endpoint_alternation": [2, 3, 4, 5],
        "verdict": (
            "local bad-center hypotheses do not force canonical shortest chords "
            "to be noncrossing"
        ),
        "non_claims": [
            "not a counterexample to Erdos Problem #97",
            "does not refute canonical-chord injectivity",
            "does not address a theorem with extra global badness or minimality hypotheses",
            "no official/global status update",
            "no source-of-truth strongest-result update",
        ],
    }


def validate_payload(payload: dict[str, object]) -> list[str]:
    errors = []
    expected = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "provenance": PROVENANCE,
        "n": 10,
        "cyclic_order": list(range(10)),
        "center_max_distance_multiplicities": [4, 4, 1, 1, 1, 1, 1, 1, 1, 1],
        "exact_bad_centers": [0, 1],
        "all_other_centers_good": True,
        "erdos97_counterexample": False,
        "selected_chords": [[2, 4], [3, 5]],
        "selected_chords_cross": True,
        "endpoint_alternation": [2, 3, 4, 5],
    }
    for key, wanted in expected.items():
        if payload.get(key) != wanted:
            errors.append(f"{key} = {payload.get(key)!r}, expected {wanted!r}")

    convexity = payload.get("strict_convexity")
    if not isinstance(convexity, dict):
        errors.append("strict_convexity must be an object")
    else:
        if convexity.get("half_plane_checks") != 80:
            errors.append("strict_convexity must contain all 80 half-plane checks")
        if convexity.get("all_positive") is not True:
            errors.append("strict_convexity determinants must all be positive")
        if convexity.get("minimum_determinant") != rational_text(
            EXPECTED_MINIMUM_DETERMINANT
        ):
            errors.append("unexpected minimum strict-convexity determinant")
        if convexity.get("minimum_attained_at") != {
            "directed_edge": [3, 4],
            "point": 5,
        }:
            errors.append("unexpected minimum determinant location")

    centers = payload.get("bad_centers")
    if not isinstance(centers, list) or len(centers) != 2:
        errors.append("bad_centers must contain exactly two records")
    else:
        for record in centers:
            if not isinstance(record, dict) or not isinstance(record.get("center"), int):
                errors.append("invalid bad-center record")
                continue
            center = record["center"]
            if center not in EXPECTED_WITNESSES:
                errors.append(f"unexpected bad center {center}")
                continue
            if record.get("witnesses") != list(EXPECTED_WITNESSES[center]):
                errors.append(f"unexpected witnesses at center {center}")
            if record.get("distance_class_multiplicities") != [4, 1, 1, 1, 1, 1]:
                errors.append(f"unexpected distance multiplicities at center {center}")
            if record.get("unique_shortest_witness_chord") != list(
                EXPECTED_CHORDS[center]
            ):
                errors.append(f"unexpected canonical chord at center {center}")
            if record.get("shortest_chord_squared") != rational_text(
                EXPECTED_SHORTEST_SQUARED[center]
            ):
                errors.append(f"unexpected shortest chord length at center {center}")
            if record.get("all_other_chords_strictly_longer") is not True:
                errors.append(f"shortest chord is not strict at center {center}")
    return errors


def summary(payload: dict[str, object]) -> dict[str, object]:
    return {
        key: payload[key]
        for key in (
            "schema",
            "status",
            "trust",
            "claim_scope",
            "strict_convexity",
            "canonical_rule",
            "bad_centers",
            "center_max_distance_multiplicities",
            "exact_bad_centers",
            "all_other_centers_good",
            "erdos97_counterexample",
            "selected_chords",
            "selected_chords_cross",
            "verdict",
        )
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--summary-json", action="store_true")
    args = parser.parse_args(argv)

    payload = build_payload()
    errors = validate_payload(payload) if args.assert_expected else []

    if args.check:
        if not OUT.exists():
            errors.append(f"missing stored artifact: {OUT.relative_to(ROOT)}")
        elif json.loads(OUT.read_text(encoding="utf-8")) != payload:
            errors.append("stored artifact does not match recomputation")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if args.write:
        OUT.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif args.summary_json or not (args.write or args.check or args.assert_expected):
        print(json.dumps(summary(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
