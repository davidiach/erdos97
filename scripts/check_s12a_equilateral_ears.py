#!/usr/bin/env python3
"""Check the exact equilateral-ear obstruction for the fixed S12A order.

S12A is the selected-witness pattern on cyclic labels 0,...,11 with even
centers using offsets +/-1,+/-2 and odd centers using offsets +/-2,+/-5.
The check is exact, solver-free, and restricted to this pattern in the
natural cyclic order. It is not a proof of Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "certificates" / "s12a_equilateral_ear_obstruction.json"

SCHEMA = "erdos97.s12a_equilateral_ear_obstruction.v1"
STATUS = "EXACT_FIXED_PATTERN_FIXED_ORDER_OBSTRUCTION"
TRUST = "EXACT_OBSTRUCTION"
CLAIM_SCOPE = (
    "Exact solver-free obstruction for the fixed S12A selected-witness pattern "
    "in the natural cyclic order only. Six forced consecutive equilateral ears "
    "require total exterior turn 4*pi, contradicting the 2*pi total for a "
    "strictly convex polygon. This is not an all-order obstruction, a general "
    "proof of Erdos Problem #97, or a counterexample."
)
PROVENANCE = {
    "generator": "scripts/check_s12a_equilateral_ears.py",
    "command": (
        "python scripts/check_s12a_equilateral_ears.py --write "
        "--assert-expected --summary-json"
    ),
    "source_archive_sha256": (
        "284a090a5980f10d0e4826bc3d7d4186985c4d0405f39332f540fd23fd44f20e"
    ),
    "source_reference_commit": "929693a5ce4f3d227bc28b35937ff2703f084d05",
}

N = 12
EVEN_OFFSETS = (1, 2, 10, 11)
ODD_OFFSETS = (2, 5, 7, 10)
EXPECTED_MIDDLES = (1, 3, 5, 7, 9, 11)


def pair(a: int, b: int) -> tuple[int, int]:
    """Return the normalized unordered pair for one distance symbol."""

    if a == b:
        raise ValueError("distance pair must use distinct vertices")
    return (a, b) if a < b else (b, a)


class DisjointSet:
    """Small exact quotient for unordered distance symbols."""

    def __init__(self, items: Iterable[tuple[int, int]]) -> None:
        self.parent = {item: item for item in items}

    def find(self, item: tuple[int, int]) -> tuple[int, int]:
        root = item
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[item] != item:
            next_item = self.parent[item]
            self.parent[item] = root
            item = next_item
        return root

    def union(self, first: tuple[int, int], second: tuple[int, int]) -> None:
        first_root = self.find(first)
        second_root = self.find(second)
        if first_root != second_root:
            self.parent[second_root] = first_root


@dataclass(frozen=True)
class EarCertificate:
    left: int
    middle: int
    right: int
    left_row: tuple[int, ...]
    right_row: tuple[int, ...]

    def to_json(self) -> dict[str, object]:
        return {
            "triple": [self.left, self.middle, self.right],
            "left_center_row": [self.left, list(self.left_row)],
            "right_center_row": [self.right, list(self.right_row)],
            "forced_equalities": [
                f"d({self.left},{self.middle}) = d({self.left},{self.right})",
                f"d({self.right},{self.left}) = d({self.right},{self.middle})",
            ],
            "conclusion": "all three side lengths are equal",
            "forced_middle_exterior_turn_over_pi": [2, 3],
        }


def s12a_rows() -> tuple[tuple[int, ...], ...]:
    rows = []
    for center in range(N):
        offsets = EVEN_OFFSETS if center % 2 == 0 else ODD_OFFSETS
        row = tuple(sorted((center + offset) % N for offset in offsets))
        if center in row or len(set(row)) != 4:
            raise AssertionError(f"invalid row at center {center}: {row}")
        rows.append(row)
    return tuple(rows)


def distance_quotient(rows: tuple[tuple[int, ...], ...]) -> DisjointSet:
    quotient = DisjointSet(
        pair(a, b) for a in range(N) for b in range(a + 1, N)
    )
    for center, witnesses in enumerate(rows):
        spokes = [pair(center, witness) for witness in witnesses]
        for spoke in spokes[1:]:
            quotient.union(spokes[0], spoke)
    return quotient


def forced_equilateral_ears(
    rows: tuple[tuple[int, ...], ...],
) -> tuple[EarCertificate, ...]:
    quotient = distance_quotient(rows)
    certificates = []
    for middle in range(N):
        left = (middle - 1) % N
        right = (middle + 1) % N
        side_classes = {
            quotient.find(pair(left, middle)),
            quotient.find(pair(middle, right)),
            quotient.find(pair(left, right)),
        }
        if len(side_classes) == 1:
            certificates.append(
                EarCertificate(left, middle, right, rows[left], rows[right])
            )
    return tuple(certificates)


def build_payload() -> dict[str, object]:
    rows = s12a_rows()
    ears = forced_equilateral_ears(rows)
    forced_turn = len(ears) * Fraction(2, 3)
    polygon_turn = Fraction(2, 1)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "provenance": PROVENANCE,
        "n": N,
        "cyclic_order": list(range(N)),
        "rows": [list(row) for row in rows],
        "forced_equilateral_ears": [ear.to_json() for ear in ears],
        "forced_ear_count": len(ears),
        "forced_middle_vertices": [ear.middle for ear in ears],
        "forced_turn_over_pi": [forced_turn.numerator, forced_turn.denominator],
        "strictly_convex_total_turn_over_pi": [
            polygon_turn.numerator,
            polygon_turn.denominator,
        ],
        "contradiction": "4*pi > 2*pi",
        "verdict": (
            "S12A has no strictly convex Euclidean realization in the stated order"
        ),
        "non_claims": [
            "not an all-cyclic-order obstruction for the abstract S12A pattern",
            "not a proof of Erdos Problem #97",
            "not a counterexample",
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
        "n": N,
        "forced_ear_count": 6,
        "forced_middle_vertices": list(EXPECTED_MIDDLES),
        "forced_turn_over_pi": [4, 1],
        "strictly_convex_total_turn_over_pi": [2, 1],
        "contradiction": "4*pi > 2*pi",
        "provenance": PROVENANCE,
    }
    for key, wanted in expected.items():
        if payload.get(key) != wanted:
            errors.append(f"{key} = {payload.get(key)!r}, expected {wanted!r}")
    if payload.get("rows") != [list(row) for row in s12a_rows()]:
        errors.append("rows do not match the S12A parity pattern")
    return errors


def summary(payload: dict[str, object]) -> dict[str, object]:
    return {
        key: payload[key]
        for key in (
            "schema",
            "status",
            "trust",
            "claim_scope",
            "forced_ear_count",
            "forced_middle_vertices",
            "forced_turn_over_pi",
            "strictly_convex_total_turn_over_pi",
            "contradiction",
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
