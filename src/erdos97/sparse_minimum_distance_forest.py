"""Exact arithmetic spine for the boundary-detour forest and fan-in lemmas.

The geometric proofs live in ``docs/sparse-minimum-distance-forest.md``.
This module checks only their normalized turn, cycle-length, and incidence
accounting arithmetic; it does not formalize the projection or angular-order
arguments and does not prove Erdős #97.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

SCHEMA = "erdos97.sparse_minimum_distance_forest.v2"
STATUS = "REVIEW_PENDING_PAPER_LEMMA_ARITHMETIC_REPLAY"
TRUST = "PAPER_PROOF_CANDIDATE"
CLAIM_SCOPE = (
    "Exact arithmetic replay for the review-pending boundary-detour distance "
    "forest, common-target fan-in, and radius-level export lemmas. It checks "
    "the normalized triangle and fan-in turn budgets, the long-cycle "
    "coefficient margin, and the forest-incidence accounting identity after "
    "the geometric projection and angular-order steps. It is not a formal "
    "proof of those geometric steps, not a proof or disproof of Erdős Problem "
    "#97, and not a source-of-truth status update."
)


@dataclass(frozen=True)
class LongCycleArithmetic:
    """Integer coefficient comparison for one cycle length."""

    cycle_length: int
    cycle_tour_coefficient: int
    perimeter_lower_coefficient: int
    margin: int
    contradiction: bool


@dataclass(frozen=True)
class FanInArithmetic:
    """Normalized turn threshold for one common-target fan-in size."""

    source_count: int
    normalized_strict_lower_bound: str
    normalized_total_turn_upper_bound: str
    contradiction: bool


@dataclass(frozen=True)
class ExportArithmetic:
    """Forest-incidence export bound for one radius level."""

    vertex_count: int
    component_count: int
    minimum_additional_witnesses_per_center: int
    maximum_forest_edges: int
    maximum_internal_incidences: int
    minimum_external_incidences: int
    fan_in_cap: int
    minimum_distinct_external_targets: int


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
        "minimum_boundary_detour_multiple": 2,
        "normalized_turn_lower_per_arc": str(per_arc_lower),
        "normalized_internal_turn_lower_sum": str(lower_sum),
        "normalized_internal_turn_strict_upper_bound": "<1",
        "contradiction": lower_sum == 1,
        "reason": (
            "Each r-chord whose corresponding boundary detour has length at "
            "least 2r forces internal turn at least 2*pi/3. The three arcs "
            "omit the positive turns at their endpoints, so their normalized "
            "total is strictly less than 1."
        ),
    }


def fan_in_arithmetic(source_count: int) -> FanInArithmetic:
    """Return the exact common-target turn threshold for ``source_count``."""

    if source_count < 1:
        raise ValueError("source_count must be positive")
    # The paper argument gives a strict lower bound
    #   sum(sigma_i)/(2*pi) > (source_count - 2)/2.
    lower = Fraction(source_count - 2, 2)
    return FanInArithmetic(
        source_count=source_count,
        normalized_strict_lower_bound=f">{lower}",
        normalized_total_turn_upper_bound="<1",
        contradiction=lower >= 1,
    )


def export_arithmetic(
    vertex_count: int,
    component_count: int,
    minimum_additional_witnesses_per_center: int = 2,
    fan_in_cap: int = 3,
) -> ExportArithmetic:
    """Return the exact forest export and distinct-target lower bounds."""

    if vertex_count < 1:
        raise ValueError("vertex_count must be positive")
    if component_count < 1 or component_count > vertex_count:
        raise ValueError("component_count must lie in 1..vertex_count")
    if minimum_additional_witnesses_per_center < 2:
        raise ValueError("minimum additional witness count must be at least 2")
    if fan_in_cap < 1:
        raise ValueError("fan_in_cap must be positive")

    maximum_edges = vertex_count - component_count
    maximum_internal = 2 * maximum_edges
    minimum_external = (
        minimum_additional_witnesses_per_center * vertex_count
        - maximum_internal
    )
    identity_value = (
        (minimum_additional_witnesses_per_center - 2) * vertex_count
        + 2 * component_count
    )
    if minimum_external != identity_value:
        raise AssertionError("forest export identity failed")
    minimum_targets = (minimum_external + fan_in_cap - 1) // fan_in_cap
    return ExportArithmetic(
        vertex_count=vertex_count,
        component_count=component_count,
        minimum_additional_witnesses_per_center=(
            minimum_additional_witnesses_per_center
        ),
        maximum_forest_edges=maximum_edges,
        maximum_internal_incidences=maximum_internal,
        minimum_external_incidences=minimum_external,
        fan_in_cap=fan_in_cap,
        minimum_distinct_external_targets=minimum_targets,
    )


def arithmetic_payload(max_cycle_length: int = 128) -> dict[str, Any]:
    """Return a deterministic reviewer-facing replay payload."""

    if max_cycle_length < 4:
        raise ValueError("max_cycle_length must be at least 4")
    cycle_cases = [
        asdict(long_cycle_arithmetic(length))
        for length in range(4, max_cycle_length + 1)
    ]
    fan_in_cases = [asdict(fan_in_arithmetic(count)) for count in range(1, 9)]
    export_cases = [
        asdict(export_arithmetic(vertices, components, witnesses))
        for vertices in range(1, 17)
        for components in range(1, vertices + 1)
        for witnesses in range(2, 6)
    ]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "triangle_case": triangle_turn_arithmetic(),
        "long_cycle_identity": "2*(g-2)-g=g-4",
        "checked_cycle_length_range": [4, max_cycle_length],
        "long_cycle_cases": cycle_cases,
        "all_checked_long_cycles_close": all(
            bool(case["contradiction"]) for case in cycle_cases
        ),
        "fan_in_identity": (
            "sum(sigma_i)/(2*pi) > (k-2)/2; k>=4 contradicts total <1"
        ),
        "fan_in_cap": 3,
        "fan_in_cases": fan_in_cases,
        "all_checked_fan_in_cases_match_cap": all(
            bool(case["contradiction"]) == (int(case["source_count"]) >= 4)
            for case in fan_in_cases
        ),
        "export_identity": "d*n-2*(n-c)=(d-2)*n+2*c",
        "export_cases": export_cases,
        "all_checked_export_cases_nonnegative": all(
            int(case["minimum_external_incidences"]) >= 0
            for case in export_cases
        ),
        "erdos_threshold_component_export": (
            "For d=2, every forest component contributes at least two "
            "external incidences in aggregate."
        ),
        "general_integer_argument": (
            "For every integer g>=4, g-4>=0; the strict geometric perimeter "
            "bound exceeds the length g*r of an r-edge cycle. For k>=4 "
            "common-target sources, the strict normalized turn lower bound is "
            "at least 1. Forest edge counting gives the export identity for "
            "all n>=c>=1 and d>=2."
        ),
        "limitations": [
            "The projection, angular-order, and convex-hull-perimeter lemmas remain paper proof steps.",
            "The bounded replay tables illustrate unbounded integer identities.",
            "Outside a fixed E-radius level, a target may have opposite parity without changing radius.",
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
        "fan_in_cap": 3,
        "all_checked_fan_in_cases_match_cap": True,
        "export_identity": "d*n-2*(n-c)=(d-2)*n+2*c",
        "all_checked_export_cases_nonnegative": True,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise AssertionError(
                f"{key}: expected {value!r}, got {payload.get(key)!r}"
            )

    triangle = payload.get("triangle_case")
    if not isinstance(triangle, dict):
        raise AssertionError("triangle_case must be an object")
    if triangle.get("minimum_boundary_detour_multiple") != 2:
        raise AssertionError("unexpected minimum boundary detour multiple")
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

    cycle_cases = payload.get("long_cycle_cases")
    if not isinstance(cycle_cases, list):
        raise AssertionError("long_cycle_cases must be a list")
    expected_lengths = list(range(4, raw_range[1] + 1))
    actual_lengths = [case.get("cycle_length") for case in cycle_cases]
    if actual_lengths != expected_lengths:
        raise AssertionError("long-cycle replay range is incomplete")
    for case in cycle_cases:
        length = int(case["cycle_length"])
        if case != asdict(long_cycle_arithmetic(length)):
            raise AssertionError(f"incorrect long-cycle case at g={length}")

    fan_in_cases = payload.get("fan_in_cases")
    if not isinstance(fan_in_cases, list):
        raise AssertionError("fan_in_cases must be a list")
    if fan_in_cases != [
        asdict(fan_in_arithmetic(count)) for count in range(1, 9)
    ]:
        raise AssertionError("fan-in replay cases differ from regeneration")

    export_cases = payload.get("export_cases")
    if not isinstance(export_cases, list):
        raise AssertionError("export_cases must be a list")
    expected_exports = [
        asdict(export_arithmetic(vertices, components, witnesses))
        for vertices in range(1, 17)
        for components in range(1, vertices + 1)
        for witnesses in range(2, 6)
    ]
    if export_cases != expected_exports:
        raise AssertionError("export replay cases differ from regeneration")
