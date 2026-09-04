"""Exact arithmetic spine for the sparse minimum-distance forest lemma.

The geometric proof lives in ``docs/sparse-minimum-distance-forest.md``.
This module checks only the final normalized turn and cycle-length arithmetic;
it does not formalize the projection argument and does not prove Erdős #97.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

SCHEMA = "erdos97.sparse_minimum_distance_forest.v1"
STATUS = "REVIEW_PENDING_PAPER_LEMMA_ARITHMETIC_REPLAY"
TRUST = "PAPER_PROOF_CANDIDATE"
CLAIM_SCOPE = (
    "Exact arithmetic replay for the review-pending sparse minimum-distance "
    "forest lemma. It checks the normalized triangle turn budget and the "
    "long-cycle coefficient margin after the geometric projection steps. "
    "It is not a formal proof of those projection steps, not a proof or "
    "disproof of Erdős Problem #97, and not a source-of-truth status update."
)


@dataclass(frozen=True)
class LongCycleArithmetic:
    """Integer coefficient comparison for one cycle length."""

    cycle_length: int
    cycle_tour_coefficient: int
    perimeter_lower_coefficient: int
    margin: int
    contradiction: bool


def long_cycle_arithmetic(cycle_length: int) -> LongCycleArithmetic:
    """Return the exact coefficient comparison for ``cycle_length >= 4``."""

    if cycle_length < 4:
        raise ValueError("long-cycle arithmetic requires cycle_length >= 4")
    tour = cycle_length
    perimeter = 2 * (cycle_length - 2)
    margin = perimeter - tour
    return LongCycleArithmetic(
        cycle_length=cycle_length,
        cycle_tour_coefficient=tour,
        perimeter_lower_coefficient=perimeter,
        margin=margin,
        contradiction=margin >= 0,
    )


def triangle_turn_arithmetic() -> dict[str, Any]:
    """Return the exact normalized three-arc turn contradiction."""

    per_arc_lower = Fraction(1, 3)
    lower_sum = 3 * per_arc_lower
    return {
        "arc_count": 3,
        "minimum_boundary_edges_per_arc": 2,
        "normalized_turn_lower_per_arc": str(per_arc_lower),
        "normalized_internal_turn_lower_sum": str(lower_sum),
        "normalized_internal_turn_strict_upper_bound": "<1",
        "contradiction": lower_sum == 1,
        "reason": (
            "Each r-chord over at least two boundary edges of length at least "
            "r forces internal turn at least 2*pi/3. The three arcs omit the "
            "positive turns at their endpoints, so their normalized total is "
            "strictly less than 1."
        ),
    }


def arithmetic_payload(max_cycle_length: int = 128) -> dict[str, Any]:
    """Return a deterministic reviewer-facing replay payload."""

    if max_cycle_length < 4:
        raise ValueError("max_cycle_length must be at least 4")
    cases = [
        asdict(long_cycle_arithmetic(length))
        for length in range(4, max_cycle_length + 1)
    ]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "triangle_case": triangle_turn_arithmetic(),
        "long_cycle_identity": "2*(g-2)-g=g-4",
        "checked_cycle_length_range": [4, max_cycle_length],
        "long_cycle_cases": cases,
        "all_checked_long_cycles_close": all(
            bool(case["contradiction"]) for case in cases
        ),
        "general_integer_argument": (
            "For every integer g>=4, g-4>=0; the strict geometric perimeter "
            "bound therefore exceeds the length g*r of an r-edge cycle."
        ),
        "limitations": [
            "The projection and convex-hull-perimeter lemmas remain paper proof steps.",
            "The bounded replay table illustrates an unbounded integer identity.",
            "No general proof, disproof, or counterexample for Erdős #97 is claimed.",
        ],
    }


def assert_expected_payload(payload: dict[str, Any]) -> None:
    """Assert the stable exact fields and every replayed comparison."""

    expected = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "long_cycle_identity": "2*(g-2)-g=g-4",
        "all_checked_long_cycles_close": True,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise AssertionError(
                f"{key}: expected {value!r}, got {payload.get(key)!r}"
            )

    triangle = payload.get("triangle_case")
    if not isinstance(triangle, dict):
        raise AssertionError("triangle_case must be an object")
    if triangle.get("normalized_internal_turn_lower_sum") != "1":
        raise AssertionError("unexpected normalized triangle lower sum")
    if triangle.get("contradiction") is not True:
        raise AssertionError("triangle arithmetic did not close")

    raw_range = payload.get("checked_cycle_length_range")
    if not (
        isinstance(raw_range, list)
        and len(raw_range) == 2
        and raw_range[0] == 4
        and isinstance(raw_range[1], int)
        and raw_range[1] >= 4
    ):
        raise AssertionError("invalid checked cycle-length range")

    cases = payload.get("long_cycle_cases")
    if not isinstance(cases, list):
        raise AssertionError("long_cycle_cases must be a list")
    expected_lengths = list(range(4, raw_range[1] + 1))
    actual_lengths = [case.get("cycle_length") for case in cases]
    if actual_lengths != expected_lengths:
        raise AssertionError("long-cycle replay range is incomplete")

    for case in cases:
        length = int(case["cycle_length"])
        expected_case = asdict(long_cycle_arithmetic(length))
        if case != expected_case:
            raise AssertionError(f"incorrect long-cycle case at g={length}")
