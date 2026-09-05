"""Exact arithmetic for advanced radius-level proof candidates.

This module checks only coefficient and algebraic identities used by the paper
arguments in ``docs/radius-level-linear-forest.md``,
``docs/radius-level-return-locality.md``, and
``docs/triple-fanin-radius-descent.md``. It does not formalize their geometric
projection, ray-order, or strict-convexity steps.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

SCHEMA = "erdos97.radius_level_advanced_arithmetic.v1"
STATUS = "REVIEW_PENDING_PAPER_LEMMA_ARITHMETIC_REPLAY"
TRUST = "PAPER_PROOF_CANDIDATE"
CLAIM_SCOPE = (
    "Exact arithmetic replay for review-pending radius-level linear-forest, "
    "weak-arc return, component-cycle locality, and triple-fan-in radius "
    "descent lemmas. It is not a formal proof of the geometric steps, not a "
    "proof or disproof of Erdős Problem #97, and not a source-of-truth update."
)


@dataclass(frozen=True)
class WeakArcCycleArithmetic:
    """Coefficient comparison for a cycle with ``h`` weak detour gaps."""

    cycle_length: int
    weak_arc_count: int
    cycle_tour_coefficient: int
    perimeter_lower_coefficient: int
    margin: int
    contradiction: bool


@dataclass(frozen=True)
class ComponentCycleArithmetic:
    """Worst-case margin for a lifted component-target cycle."""

    component_count: int
    total_path_length: int
    lifted_cycle_length: int
    weak_arc_upper_bound: int
    worst_case_margin: int
    contradiction: bool


def weak_arc_cycle_arithmetic(
    cycle_length: int,
    weak_arc_count: int,
) -> WeakArcCycleArithmetic:
    """Return the exact identity ``(2g-h-4)-g=g-h-4``."""

    if cycle_length < 3:
        raise ValueError("cycle_length must be at least 3")
    if weak_arc_count < 0 or weak_arc_count > cycle_length:
        raise ValueError("weak_arc_count must lie in 0..cycle_length")
    perimeter = 2 * cycle_length - weak_arc_count - 4
    margin = perimeter - cycle_length
    return WeakArcCycleArithmetic(
        cycle_length=cycle_length,
        weak_arc_count=weak_arc_count,
        cycle_tour_coefficient=cycle_length,
        perimeter_lower_coefficient=perimeter,
        margin=margin,
        contradiction=margin >= 0,
    )


def component_cycle_arithmetic(
    component_count: int,
    total_path_length: int,
) -> ComponentCycleArithmetic:
    """Return the worst-case lifted-cycle margin ``L-4``."""

    if component_count < 2:
        raise ValueError("component_count must be at least 2")
    if total_path_length < 0:
        raise ValueError("total_path_length must be nonnegative")
    cycle_length = 2 * component_count + total_path_length
    weak_upper = 2 * component_count
    margin = cycle_length - weak_upper - 4
    return ComponentCycleArithmetic(
        component_count=component_count,
        total_path_length=total_path_length,
        lifted_cycle_length=cycle_length,
        weak_arc_upper_bound=weak_upper,
        worst_case_margin=margin,
        contradiction=margin >= 0,
    )


def linear_forest_angle_arithmetic() -> dict[str, Any]:
    """Return normalized turn arithmetic for degree at most two."""

    end_total = 2 * Fraction(1, 3)
    middle_constant = Fraction(1, 2)
    angle_threshold = end_total + middle_constant - 1
    degree_three_lower = end_total + 2 * middle_constant - Fraction(1, 2)
    return {
        "two_neighbor_end_arc_total": str(end_total),
        "middle_arc_lower_form": "1/2-alpha/(2*pi)",
        "forced_angle_normalized_lower_bound": str(angle_threshold),
        "forced_angle_radians": ">pi/3",
        "degree_three_normalized_strict_lower_bound": f">{degree_three_lower}",
        "normalized_total_turn_upper_bound": "<1",
        "degree_three_contradiction": degree_three_lower > 1,
    }


def _quadratic_pair_multiply(
    left: tuple[int, int],
    right: tuple[int, int],
) -> tuple[int, int]:
    """Multiply exact pairs representing ``a+b*sqrt(2)``."""

    a, b = left
    c, d = right
    return (a * c + 2 * b * d, a * d + b * c)


def triple_fanin_radius_arithmetic() -> dict[str, Any]:
    """Return exact algebra for the ``sqrt(2)-1`` descent threshold."""

    root = (-1, 1)
    square = _quadratic_pair_multiply(root, root)
    polynomial = (square[0] + 2 * root[0] - 1, square[1] + 2 * root[1])
    return {
        "angular_condition": "acos(x)+acos(y)<pi/2",
        "equivalent_asymmetric_condition": "x^2+y^2>1",
        "substitution": "x=R/(R+a), y=R/(R+b)",
        "symmetric_condition": "2/(1+s)^2>1",
        "equivalent_quadratic": "s^2+2*s-1<0",
        "positive_threshold": "sqrt(2)-1",
        "threshold_quadratic_value": [polynomial[0], polynomial[1]],
        "threshold_identity_verified": polynomial == (0, 0),
        "descent_conclusion": "min(a,b)<(sqrt(2)-1)*R",
    }


def payload(max_cycle_length: int = 128) -> dict[str, Any]:
    """Return a deterministic reviewer-facing arithmetic payload."""

    if max_cycle_length < 6:
        raise ValueError("max_cycle_length must be at least 6")
    weak_cases = [
        asdict(weak_arc_cycle_arithmetic(length, weak))
        for length in range(3, max_cycle_length + 1)
        for weak in range(0, min(length, 12) + 1)
    ]
    component_cases = [
        asdict(component_cycle_arithmetic(components, path_length))
        for components in range(2, 17)
        for path_length in range(0, 13)
    ]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "linear_forest_angle": linear_forest_angle_arithmetic(),
        "weak_arc_identity": "(2*g-h-4)-g=g-h-4",
        "checked_cycle_length_range": [3, max_cycle_length],
        "weak_arc_cases": weak_cases,
        "all_weak_arc_cases_match_threshold": all(
            bool(case["contradiction"])
            == (
                int(case["cycle_length"])
                >= int(case["weak_arc_count"]) + 4
            )
            for case in weak_cases
        ),
        "component_cycle_identity": "g-h-4 >= L-4",
        "component_cycle_cases": component_cases,
        "component_cycle_first_forbidden_total_path_length": 4,
        "all_component_cycle_cases_match_threshold": all(
            bool(case["contradiction"])
            == (int(case["total_path_length"]) >= 4)
            for case in component_cases
        ),
        "triple_fanin_radius_descent": triple_fanin_radius_arithmetic(),
        "limitations": [
            "Projection, angular-order, and convexity steps remain paper mathematics.",
            "The bounded tables replay unbounded integer identities only.",
            "Component cycles with total path length at most three remain open.",
            "No proof, disproof, or counterexample for Erdős #97 is claimed.",
        ],
    }


def assert_expected_payload(candidate: dict[str, Any]) -> None:
    """Assert exact fields and complete deterministic regeneration."""

    raw_range = candidate.get("checked_cycle_length_range")
    if not (
        isinstance(raw_range, list)
        and len(raw_range) == 2
        and raw_range[0] == 3
        and isinstance(raw_range[1], int)
        and raw_range[1] >= 6
    ):
        raise AssertionError("invalid checked cycle-length range")
    expected = payload(raw_range[1])
    if candidate != expected:
        raise AssertionError("advanced arithmetic payload differs from regeneration")
