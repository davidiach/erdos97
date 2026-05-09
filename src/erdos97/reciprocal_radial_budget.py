"""Local reciprocal-radial budget checks.

This module implements the smoke checks for ``docs/reciprocal-radial-budget.md``.
The inequalities are local necessary conditions for one equal-distance row;
they are not a global obstruction by themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

Point = tuple[float, float]

TRUST_LABEL = "RESEARCH_PACKET_LOCAL_NECESSARY_CONDITION"


@dataclass(frozen=True)
class BudgetInequality:
    """One middle-witness reciprocal-radial budget inequality."""

    center: int
    ordered_witnesses: tuple[int, int, int, int]
    middle: int
    left: int
    right: int
    lhs: float
    rhs: float
    margin: float
    positive_denominators: dict[str, float]

    def to_json(self) -> dict[str, object]:
        return {
            "center": self.center,
            "ordered_witnesses": list(self.ordered_witnesses),
            "middle": self.middle,
            "left": self.left,
            "right": self.right,
            "lhs": self.lhs,
            "rhs": self.rhs,
            "margin_rhs_minus_lhs": self.margin,
            "positive_denominators": self.positive_denominators,
            "trust": TRUST_LABEL,
        }


@dataclass(frozen=True)
class JumpFormulaCheck:
    """One reciprocal-radial jump formula check."""

    center: int
    vertex: int
    qprime_minus: float
    qprime_plus: float
    derivative_jump: float
    closed_form_jump: float
    error: float
    incoming_denominator: float
    outgoing_denominator: float
    exterior_turn_cross: float

    def to_json(self) -> dict[str, object]:
        return {
            "center": self.center,
            "vertex": self.vertex,
            "qprime_minus": self.qprime_minus,
            "qprime_plus": self.qprime_plus,
            "derivative_jump": self.derivative_jump,
            "closed_form_jump": self.closed_form_jump,
            "error": self.error,
            "incoming_denominator": self.incoming_denominator,
            "outgoing_denominator": self.outgoing_denominator,
            "exterior_turn_cross": self.exterior_turn_cross,
        }


def cross(u: Point, v: Point) -> float:
    return u[0] * v[1] - u[1] * v[0]


def dot(u: Point, v: Point) -> float:
    return u[0] * v[0] + u[1] * v[1]


def sub(u: Point, v: Point) -> Point:
    return (u[0] - v[0], u[1] - v[1])


def rotate_ccw(u: Point) -> Point:
    return (-u[1], u[0])


def edge_vectors(points: list[Point]) -> list[Point]:
    n = len(points)
    return [sub(points[(j + 1) % n], points[j]) for j in range(n)]


def visible_chain_offset(n: int, center: int, vertex: int) -> int:
    offset = (vertex - center) % n
    if offset == 0:
        raise ValueError("center cannot be a witness")
    return offset


def order_witnesses_on_visible_chain(
    n: int,
    center: int,
    witnesses: Iterable[int],
) -> tuple[int, int, int, int]:
    row = tuple(witnesses)
    if len(row) != 4:
        raise ValueError(f"expected four witnesses, got {len(row)}")
    if len(set(row)) != 4:
        raise ValueError("witnesses must be distinct")
    if center in row:
        raise ValueError("center cannot be included among witnesses")
    return tuple(sorted(row, key=lambda vertex: visible_chain_offset(n, center, vertex)))


def validate_ordered_witnesses(
    n: int,
    center: int,
    ordered_witnesses: tuple[int, int, int, int],
) -> None:
    if len(ordered_witnesses) != 4:
        raise ValueError("ordered_witnesses must have length 4")
    if len(set(ordered_witnesses)) != 4:
        raise ValueError("ordered_witnesses must be distinct")
    offsets = [visible_chain_offset(n, center, vertex) for vertex in ordered_witnesses]
    if offsets != sorted(offsets):
        raise ValueError("witnesses are not ordered on the visible chain")


def half_tan_equal_radius(x: Point, y: Point, r2: float) -> float:
    """Return tan(angle(x,y)/2) for equal-length vectors in span < pi."""

    return cross(x, y) / (r2 + dot(x, y))


def middle_budget_inequalities(
    points: list[Point],
    center: int,
    ordered_witnesses: tuple[int, int, int, int],
) -> list[BudgetInequality]:
    """Evaluate the two middle-witness budget inequalities for one row."""

    n = len(points)
    validate_ordered_witnesses(n, center, ordered_witnesses)
    edges = edge_vectors(points)
    output: list[BudgetInequality] = []

    for left, middle, right in (
        (ordered_witnesses[0], ordered_witnesses[1], ordered_witnesses[2]),
        (ordered_witnesses[1], ordered_witnesses[2], ordered_witnesses[3]),
    ):
        x_left = sub(points[left], points[center])
        x_middle = sub(points[middle], points[center])
        x_right = sub(points[right], points[center])
        r2 = dot(x_middle, x_middle)
        incoming = (middle - 1) % n
        outgoing = middle
        incoming_den = cross(x_middle, edges[incoming])
        outgoing_den = cross(x_middle, edges[outgoing])
        left_dot_den = r2 + dot(x_left, x_middle)
        right_dot_den = r2 + dot(x_middle, x_right)

        lhs = (
            r2
            * cross(edges[incoming], edges[outgoing])
            / (incoming_den * outgoing_den)
        )
        rhs = half_tan_equal_radius(
            x_left,
            x_middle,
            r2,
        ) + half_tan_equal_radius(x_middle, x_right, r2)

        output.append(
            BudgetInequality(
                center=center,
                ordered_witnesses=ordered_witnesses,
                middle=middle,
                left=left,
                right=right,
                lhs=lhs,
                rhs=rhs,
                margin=rhs - lhs,
                positive_denominators={
                    "[x_mid,e_mid-1]": incoming_den,
                    "[x_mid,e_mid]": outgoing_den,
                    "r2+x_left.x_mid": left_dot_den,
                    "r2+x_mid.x_right": right_dot_den,
                },
            )
        )

    return output


def jump_formula_check(points: list[Point], center: int, vertex: int) -> JumpFormulaCheck:
    """Check the derivative-jump formula at one non-adjacent visible vertex."""

    n = len(points)
    if vertex == center:
        raise ValueError("center cannot be the visible vertex")
    offset = visible_chain_offset(n, center, vertex)
    if offset in (1, n - 1):
        raise ValueError("jump formula check expects a non-adjacent visible vertex")

    edges = edge_vectors(points)
    x = sub(points[vertex], points[center])
    radius = math.hypot(x[0], x[1])
    unit = (x[0] / radius, x[1] / radius)
    rotated = rotate_ccw(unit)
    incoming = (vertex - 1) % n
    outgoing = vertex
    incoming_den = cross(x, edges[incoming])
    outgoing_den = cross(x, edges[outgoing])
    qprime_minus = cross(rotated, edges[incoming]) / incoming_den
    qprime_plus = cross(rotated, edges[outgoing]) / outgoing_den
    derivative_jump = qprime_plus - qprime_minus
    closed_form_jump = (
        radius
        * cross(edges[incoming], edges[outgoing])
        / (incoming_den * outgoing_den)
    )

    return JumpFormulaCheck(
        center=center,
        vertex=vertex,
        qprime_minus=qprime_minus,
        qprime_plus=qprime_plus,
        derivative_jump=derivative_jump,
        closed_form_jump=closed_form_jump,
        error=derivative_jump - closed_form_jump,
        incoming_denominator=incoming_den,
        outgoing_denominator=outgoing_den,
        exterior_turn_cross=cross(edges[incoming], edges[outgoing]),
    )


def pentagon_tight_example() -> list[Point]:
    """Return the local tight pentagon with one vertex seeing four unit witnesses."""

    angles = [20.0, 60.0, 120.0, 160.0]
    return [(0.0, 0.0)] + [
        (math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        for angle in angles
    ]


def affine_circle_example(n: int = 12) -> list[Point]:
    """Return a deterministic strictly convex affine image of points on a circle."""

    return [
        (
            math.cos(0.17 + 2.0 * math.pi * k / n)
            + 0.35 * math.sin(0.17 + 2.0 * math.pi * k / n),
            0.4 * math.cos(0.17 + 2.0 * math.pi * k / n)
            + 1.4 * math.sin(0.17 + 2.0 * math.pi * k / n),
        )
        for k in range(n)
    ]


def convex_left_turn_margins(points: list[Point]) -> list[float]:
    n = len(points)
    return [
        cross(
            sub(points[(idx + 1) % n], points[idx]),
            sub(points[(idx + 2) % n], points[(idx + 1) % n]),
        )
        for idx in range(n)
    ]


def cleared_polynomial_template() -> dict[str, object]:
    """Return the denominator-cleared middle-witness inequality template."""

    return {
        "middle_b_lhs": (
            "r2*[e_{b-1},e_b]*(r2+x_a.x_b)*(r2+x_b.x_c)"
        ),
        "middle_b_rhs": (
            "[x_b,e_{b-1}]*[x_b,e_b]*("
            "[x_a,x_b]*(r2+x_b.x_c)+"
            "[x_b,x_c]*(r2+x_a.x_b))"
        ),
        "positive_denominators": [
            "[x_b,e_{b-1}]",
            "[x_b,e_b]",
            "r2+x_a.x_b",
            "r2+x_b.x_c",
        ],
        "middle_c": "replace (a,b,c) by (b,c,d)",
    }


def smoke_report() -> dict[str, object]:
    """Return deterministic checks for the packet's local formulas."""

    pentagon = pentagon_tight_example()
    pentagon_row = middle_budget_inequalities(pentagon, 0, (1, 2, 3, 4))
    affine = affine_circle_example()
    jump_checks = [
        jump_formula_check(affine, center, vertex)
        for center in range(len(affine))
        for vertex in range(len(affine))
        if vertex != center
        and visible_chain_offset(len(affine), center, vertex)
        not in (1, len(affine) - 1)
    ]
    convex_margins = convex_left_turn_margins(affine)
    jump_errors = [abs(item.error) for item in jump_checks]
    jump_denominators = [
        value
        for item in jump_checks
        for value in (item.incoming_denominator, item.outgoing_denominator)
    ]

    return {
        "schema": "reciprocal_radial_budget_smoke_v1",
        "trust": TRUST_LABEL,
        "claim_scope": (
            "local necessary inequality only; not a proof of Erdos Problem #97"
        ),
        "pentagon_tight_example": {
            "center": 0,
            "ordered_witnesses": [1, 2, 3, 4],
            "inequalities": [entry.to_json() for entry in pentagon_row],
            "max_abs_margin": max(abs(entry.margin) for entry in pentagon_row),
        },
        "jump_formula_affine_circle": {
            "polygon_size": len(affine),
            "checked_non_adjacent_vertices": len(jump_checks),
            "max_abs_error": max(jump_errors),
            "min_visible_denominator": min(jump_denominators),
            "min_exterior_turn_cross": min(
                item.exterior_turn_cross for item in jump_checks
            ),
            "min_convex_left_turn": min(convex_margins),
        },
        "cleared_polynomial_template": cleared_polynomial_template(),
    }
