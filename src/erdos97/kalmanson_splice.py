"""Generic two-inequality Kalmanson splice templates.

Each template consists of two strict Kalmanson inequalities and three
selected-distance equalities.  One ordinary-distance term cancels directly
between the strict rows; the remaining terms cancel in the selected-distance
quotient.  The result is an exact local obstruction for any strictly convex
polygon containing the encoded ordered roles and rich-class pair memberships.

The templates are local lemmas only.  This module does not assert that a
counterexample, fragile cycle, or selected-row system must contain one.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Any, Mapping, Sequence


K1 = "K1_diag_gt_sides"
K2 = "K2_diag_gt_other"

Role = str
RolePair = tuple[Role, Role]
Equality = tuple[Role, Role, Role]


@dataclass(frozen=True)
class TemplateStrictRow:
    """One strict Kalmanson row on ordered formal roles."""

    kind: str
    quad: tuple[Role, Role, Role, Role]


@dataclass(frozen=True)
class KalmansonSpliceTemplate:
    """Two strict rows whose sum is killed by three centered equalities."""

    name: str
    roles: tuple[Role, ...]
    selected_equalities: tuple[Equality, Equality, Equality]
    strict_rows: tuple[TemplateStrictRow, TemplateStrictRow]


@dataclass(frozen=True)
class SpliceEmbedding:
    """One order-preserving occurrence of a splice template."""

    template: str
    role_map: tuple[tuple[Role, int], ...]
    active_equalities: tuple[tuple[int, int, int], ...]
    strict_rows: tuple[tuple[str, tuple[int, int, int, int]], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "template": self.template,
            "role_map": {role: label for role, label in self.role_map},
            "active_equalities": [
                {
                    "center": center,
                    "witness_pair": [left, right],
                }
                for center, left, right in self.active_equalities
            ],
            "strict_rows": [
                {"kind": kind, "quad": list(quad)} for kind, quad in self.strict_rows
            ],
        }


SIX_ROLE_SPLICE = KalmansonSpliceTemplate(
    name="six_role_K1_K2_splice",
    roles=("a", "b", "c", "d", "e", "f"),
    selected_equalities=(
        ("b", "a", "e"),
        ("c", "a", "f"),
        ("d", "e", "f"),
    ),
    strict_rows=(
        TemplateStrictRow(K1, ("a", "b", "c", "e")),
        TemplateStrictRow(K2, ("c", "d", "e", "f")),
    ),
)

FIVE_ROLE_SPLICE = KalmansonSpliceTemplate(
    name="five_role_K2_K1_splice",
    roles=("a", "b", "c", "d", "e"),
    selected_equalities=(
        ("a", "b", "c"),
        ("b", "c", "e"),
        ("d", "b", "e"),
    ),
    strict_rows=(
        TemplateStrictRow(K2, ("a", "b", "c", "d")),
        TemplateStrictRow(K1, ("a", "b", "d", "e")),
    ),
)

SPLICE_TEMPLATES = (FIVE_ROLE_SPLICE, SIX_ROLE_SPLICE)


class _UnionFind:
    def __init__(self, items: Sequence[RolePair]) -> None:
        self.parent = {item: item for item in items}

    def find(self, item: RolePair) -> RolePair:
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left: RolePair, right: RolePair) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        if right_root < left_root:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root


def _pair(left: Role, right: Role) -> RolePair:
    if left == right:
        raise ValueError("distance pair needs distinct roles")
    return (left, right) if left < right else (right, left)


def _strict_terms(row: TemplateStrictRow) -> tuple[tuple[RolePair, int], ...]:
    a, b, c, d = row.quad
    positive = ((_pair(a, c), 1), (_pair(b, d), 1))
    if row.kind == K1:
        negative = ((_pair(a, b), -1), (_pair(c, d), -1))
    elif row.kind == K2:
        negative = ((_pair(a, d), -1), (_pair(b, c), -1))
    else:
        raise ValueError(f"unknown Kalmanson kind: {row.kind}")
    return (*positive, *negative)


def _quotient_vector(
    template: KalmansonSpliceTemplate,
    equalities: Sequence[Equality],
    strict_rows: Sequence[TemplateStrictRow],
) -> dict[RolePair, int]:
    pairs = [_pair(left, right) for left, right in combinations(template.roles, 2)]
    quotient = _UnionFind(pairs)
    for center, left, right in equalities:
        quotient.union(_pair(center, left), _pair(center, right))
    total: Counter[RolePair] = Counter()
    for strict_row in strict_rows:
        for distance_pair, coefficient in _strict_terms(strict_row):
            total[quotient.find(distance_pair)] += coefficient
    return {root: value for root, value in sorted(total.items()) if value}


def verify_splice_template(template: KalmansonSpliceTemplate) -> dict[str, Any]:
    """Verify zero-sum, strict support, and equality-minimality exactly."""

    if len(set(template.roles)) != len(template.roles):
        raise ValueError("splice roles must be distinct")
    position = {role: index for index, role in enumerate(template.roles)}
    for row in template.strict_rows:
        if len(set(row.quad)) != 4 or any(role not in position for role in row.quad):
            raise ValueError("strict quadrilateral has invalid roles")
        if [position[role] for role in row.quad] != sorted(
            position[role] for role in row.quad
        ):
            raise ValueError("strict quadrilateral is not in template cyclic order")
    for center, left, right in template.selected_equalities:
        if len({center, left, right}) != 3 or any(
            role not in position for role in (center, left, right)
        ):
            raise ValueError("selected equality is not a centered three-role tie")

    individual_vectors = [
        _quotient_vector(
            template,
            template.selected_equalities,
            (strict_row,),
        )
        for strict_row in template.strict_rows
    ]
    if any(not vector for vector in individual_vectors):
        raise AssertionError("splice contains a one-row Kalmanson self-edge")
    combined = _quotient_vector(
        template,
        template.selected_equalities,
        template.strict_rows,
    )
    if combined:
        raise AssertionError(f"splice strict rows do not cancel: {combined}")

    omission_vectors = []
    for omitted in range(len(template.selected_equalities)):
        retained = tuple(
            equality
            for index, equality in enumerate(template.selected_equalities)
            if index != omitted
        )
        vector = _quotient_vector(template, retained, template.strict_rows)
        if not vector:
            raise AssertionError("splice equality footprint is not inclusion-minimal")
        omission_vectors.append(
            {
                "omitted_equality_index": omitted,
                "remaining_nonzero_class_count": len(vector),
            }
        )

    raw_counts: Counter[RolePair] = Counter()
    occurrence_counts: Counter[RolePair] = Counter()
    for strict_row in template.strict_rows:
        for distance_pair, coefficient in _strict_terms(strict_row):
            raw_counts[distance_pair] += coefficient
            occurrence_counts[distance_pair] += 1
    direct_cancellations = sorted(
        distance_pair
        for distance_pair, count in occurrence_counts.items()
        if count > 1 and raw_counts[distance_pair] == 0
    )
    if len(direct_cancellations) != 1:
        raise AssertionError("splice must have exactly one direct pair cancellation")

    return {
        "template": template.name,
        "roles": list(template.roles),
        "role_count": len(template.roles),
        "selected_equalities": [
            {"center": center, "witness_pair": [left, right]}
            for center, left, right in template.selected_equalities
        ],
        "strict_rows": [
            {"kind": row.kind, "quad": list(row.quad)}
            for row in template.strict_rows
        ],
        "strict_quad_intersection_size": len(
            set(template.strict_rows[0].quad) & set(template.strict_rows[1].quad)
        ),
        "direct_cancelled_pair": list(direct_cancellations[0]),
        "individual_strict_rows_nonzero": True,
        "combined_zero_sum_verified": True,
        "selected_equality_footprint_inclusion_minimal": True,
        "equality_omission_replays": omission_vectors,
        "claim_scope": (
            "Direct local contradiction for these ordered roles and centered "
            "equalities only; no occurrence or counterexample claim."
        ),
    }


def find_splice_embeddings(
    rows: Mapping[int, Sequence[int]],
    cyclic_order: Sequence[int],
    strict_rows: Sequence[Mapping[str, Any]],
) -> tuple[SpliceEmbedding, ...]:
    """Find exact order-preserving template embeddings in one partial system."""

    order = tuple(int(label) for label in cyclic_order)
    if len(set(order)) != len(order):
        raise ValueError("cyclic order must contain distinct labels")
    normalized_rows = {
        int(center): frozenset(int(witness) for witness in witnesses)
        for center, witnesses in rows.items()
    }
    stored_strict = sorted(
        (
            str(item["kind"]),
            tuple(int(label) for label in item["quad_natural_order"]),
        )
        for item in strict_rows
    )
    found: list[SpliceEmbedding] = []
    for template in SPLICE_TEMPLATES:
        verify_splice_template(template)
        for labels in combinations(order, len(template.roles)):
            role_map = dict(zip(template.roles, labels, strict=True))
            active_equalities = tuple(
                (role_map[center], role_map[left], role_map[right])
                for center, left, right in template.selected_equalities
            )
            if not all(
                center in normalized_rows
                and {left, right} <= normalized_rows[center]
                for center, left, right in active_equalities
            ):
                continue
            mapped_strict = tuple(
                (
                    strict_row.kind,
                    tuple(role_map[role] for role in strict_row.quad),
                )
                for strict_row in template.strict_rows
            )
            if sorted(mapped_strict) != stored_strict:
                continue
            found.append(
                SpliceEmbedding(
                    template=template.name,
                    role_map=tuple((role, role_map[role]) for role in template.roles),
                    active_equalities=active_equalities,
                    strict_rows=mapped_strict,
                )
            )
    return tuple(found)


__all__ = [
    "FIVE_ROLE_SPLICE",
    "KalmansonSpliceTemplate",
    "SIX_ROLE_SPLICE",
    "SPLICE_TEMPLATES",
    "SpliceEmbedding",
    "find_splice_embeddings",
    "verify_splice_template",
]
