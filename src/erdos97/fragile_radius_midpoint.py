"""Exact critical-radius branch diagnostics for two-overlap selected rows."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Mapping, Sequence

from erdos97.incidence_filters import forced_equal_classes_from_matrix


@dataclass(frozen=True, order=True)
class TwoOverlapRelation:
    """Two selected rows and their two common witnesses."""

    centers: tuple[int, int]
    witnesses: tuple[int, int]

    def as_dict(self) -> dict[str, list[int]]:
        return {
            "centers": list(self.centers),
            "common_witnesses": list(self.witnesses),
        }


def _sympy():
    try:
        import sympy as sp  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dev dependency
        raise RuntimeError("SymPy is required for midpoint diagnostics") from exc
    return sp


def two_overlap_relations(
    rows: Mapping[int, Sequence[int]],
) -> list[TwoOverlapRelation]:
    """Return every row pair having exactly two common witnesses."""

    normalized = {int(center): tuple(int(v) for v in row) for center, row in rows.items()}
    relations: list[TwoOverlapRelation] = []
    for left, right in combinations(sorted(normalized), 2):
        common = tuple(sorted(set(normalized[left]) & set(normalized[right])))
        if len(common) == 2:
            relations.append(TwoOverlapRelation((left, right), common))
    return relations


def midpoint_equation_row(n: int, relation: TwoOverlapRelation) -> list[int]:
    """Return ``X_y + X_z - X_u - X_v = 0`` for one equal-radius branch."""

    labels = (*relation.centers, *relation.witnesses)
    if n <= 0 or any(label < 0 or label >= n for label in labels):
        raise ValueError("relation label outside 0,...,n-1")
    row = [0] * n
    for center in relation.centers:
        row[center] += 1
    for witness in relation.witnesses:
        row[witness] -= 1
    return row


def midpoint_matrix(n: int, relations: Sequence[TwoOverlapRelation]):
    """Return the exact integer midpoint matrix for chosen equal branches."""

    sp = _sympy()
    rows = [midpoint_equation_row(n, relation) for relation in relations]
    return sp.Matrix(rows) if rows else sp.zeros(0, n)


def verify_radius_midpoint_identity() -> dict[str, object]:
    """Replay the polynomial identity behind the radius-midpoint lemma."""

    sp = _sympy()
    yx, yy, zx, zy, ux, uy, vx, vy = sp.symbols(
        "yx yy zx zy ux uy vx vy"
    )
    y = (yx, yy)
    z = (zx, zy)
    u = (ux, uy)
    v = (vx, vy)
    m = ((ux + vx) / 2, (uy + vy) / 2)

    def dist2(left, right):
        return sum((a - b) ** 2 for a, b in zip(left, right, strict=True))

    perpendicular_bisector_y = sp.expand(dist2(y, u) - dist2(y, v))
    perpendicular_bisector_z = sp.expand(dist2(z, u) - dist2(z, v))
    radius_difference = sp.expand(dist2(y, u) - dist2(z, u))
    midpoint_distance_difference = sp.expand(dist2(y, m) - dist2(z, m))
    certificate = sp.expand(
        2 * (radius_difference - midpoint_distance_difference)
        - perpendicular_bisector_y
        + perpendicular_bisector_z
    )

    h, s, t = sp.symbols("h s t")
    normalized_factorization = sp.expand(
        (h**2 + s**2) - (h**2 + t**2) - (s - t) * (s + t)
    )
    return {
        "polynomial_identity": (
            "2*(r_y^2-r_z^2-(|y-m|^2-|z-m|^2)) "
            "= (|y-u|^2-|y-v|^2)-(|z-u|^2-|z-v|^2)"
        ),
        "polynomial_identity_verified": certificate == 0,
        "normalized_radius_factorization": "r_y^2-r_z^2=(s-t)(s+t)",
        "normalized_factorization_verified": normalized_factorization == 0,
        "equal_radius_crossing_conclusion": (
            "When y and z are distinct and m lies between them on the "
            "perpendicular bisector, r_y=r_z iff s+t=0; hence m is also "
            "the midpoint of yz and the alternating four-point figure is a rhombus."
        ),
    }


def _relation_key(relation: TwoOverlapRelation) -> tuple[int, int]:
    return relation.centers


def radius_midpoint_branch_certificate(
    n: int,
    relations: Sequence[TwoOverlapRelation],
    equal_center_pairs: Sequence[Sequence[int]],
) -> dict[str, object]:
    """Certify one equality/strict branch of the two-overlap trichotomy.

    Equal branches impose midpoint equations. Every remaining relation is
    oriented by a displayed total order of the equal-radius components, which
    supplies an acyclic strict-radius branch witness. The routine proves only
    survival of this local diagnostic, never Euclidean realizability.
    """

    relation_by_key = {_relation_key(relation): relation for relation in relations}
    if len(relation_by_key) != len(relations):
        raise ValueError("duplicate two-overlap center pair")
    equal_keys = {
        tuple(sorted(int(label) for label in pair)) for pair in equal_center_pairs
    }
    if any(len(pair) != 2 for pair in equal_center_pairs):
        raise ValueError("equal-radius center pairs must have size two")
    unknown = sorted(equal_keys - set(relation_by_key))
    if unknown:
        raise ValueError(f"equal-radius pair is not a two-overlap relation: {unknown}")

    equal_relations = [
        relation for relation in relations if _relation_key(relation) in equal_keys
    ]
    matrix = midpoint_matrix(n, equal_relations)
    forced_point_equal_classes = forced_equal_classes_from_matrix(matrix, n)

    active_centers = sorted({center for relation in relations for center in relation.centers})
    parent = {center: center for center in active_centers}

    def find(center: int) -> int:
        while parent[center] != center:
            parent[center] = parent[parent[center]]
            center = parent[center]
        return center

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for relation in equal_relations:
        union(*relation.centers)

    equality_closed = all(
        (_relation_key(relation) in equal_keys)
        == (find(relation.centers[0]) == find(relation.centers[1]))
        for relation in relations
    )
    components_by_root: dict[int, list[int]] = {}
    for center in active_centers:
        components_by_root.setdefault(find(center), []).append(center)
    components = sorted(tuple(component) for component in components_by_root.values())
    component_index = {
        center: index for index, component in enumerate(components) for center in component
    }

    strict_relations: list[dict[str, object]] = []
    strict_edges: list[tuple[int, int]] = []
    for relation in relations:
        if _relation_key(relation) in equal_keys:
            continue
        left, right = relation.centers
        if component_index[left] == component_index[right]:
            continue
        smaller, larger = (
            (left, right)
            if component_index[left] < component_index[right]
            else (right, left)
        )
        strict_edges.append((component_index[smaller], component_index[larger]))
        strict_relations.append(
            {
                **relation.as_dict(),
                "radius_order": [smaller, larger],
                "midpoint_distance_order": [smaller, larger],
            }
        )

    strict_acyclic = all(left < right for left, right in strict_edges)
    survives = equality_closed and not forced_point_equal_classes and strict_acyclic
    return {
        "branch_semantics": {
            "equal": (
                "r_y=r_z; the common-witness midpoint is also the center-chord "
                "midpoint, giving X_y+X_z-X_u-X_v=0 on each coordinate axis"
            ),
            "strict": (
                "radius_order [y,z] means r_y<r_z and therefore "
                "|y-m|<|z-m| for the common-witness midpoint m"
            ),
        },
        "equal_relation_count": len(equal_relations),
        "strict_relation_count": len(strict_relations),
        "equal_relations": [relation.as_dict() for relation in equal_relations],
        "strict_relations": strict_relations,
        "radius_equal_components": [list(component) for component in components],
        "radius_equality_closed": equality_closed,
        "midpoint_equation_rows": [list(map(int, matrix.row(i))) for i in range(matrix.rows)],
        "midpoint_matrix_rank": int(matrix.rank()),
        "forced_point_equal_classes": forced_point_equal_classes,
        "coordinate_collision_obstruction": bool(forced_point_equal_classes),
        "strict_radius_component_order": [list(component) for component in components],
        "strict_radius_acyclic": strict_acyclic,
        "survives_local_diagnostic": survives,
    }
