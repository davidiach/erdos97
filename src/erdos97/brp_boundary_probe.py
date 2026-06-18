"""Boundary-to-vertex diagnostic for the Barany--Roldan-Pensado seed."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

import math


SCHEMA = "erdos97.brp_boundary_vertexization_probe.v1"
STATUS = "BOUNDARY_VERTEXIZATION_DIAGNOSTIC_ONLY"
TRUST = "NUMERICAL_GEOMETRIC_DIAGNOSTIC"

BASE_POINTS: tuple[tuple[str, int, int], ...] = (
    ("1", 1000, 0),
    ("2", 906, 114),
    ("3", 645, 359),
    ("4", -498, 871),
)
ORBIT_PREFIXES = ("A", "B", "C")
DEFAULT_A5_PARAMETERS: tuple[tuple[Fraction, Fraction], ...] = tuple(
    (Fraction(t, 4), Fraction(sign * h))
    for t in (1, 2, 3)
    for h in (1, 2, 5, 10, 20, 50)
    for sign in (-1, 1)
)
LEMMA31_ROLE_LABELS = ("A3", "A4", "B1", "B2")
LEMMA31_DEFAULT_BPRIME_FRACTION = Fraction(1, 100)
SQRT3 = math.sqrt(3.0)
ROOT_TOL = 1e-9
DISTANCE_TOL = 1e-6
JSON_FLOAT_DIGITS = 9


@dataclass(frozen=True, order=True)
class Quad:
    """Number of the form `a + b*sqrt(3)` with rational coefficients."""

    a: Fraction
    b: Fraction = Fraction(0)

    def __add__(self, other: Quad) -> Quad:
        return Quad(self.a + other.a, self.b + other.b)

    def __sub__(self, other: Quad) -> Quad:
        return Quad(self.a - other.a, self.b - other.b)

    def __neg__(self) -> Quad:
        return Quad(-self.a, -self.b)

    def __mul__(self, other: Quad) -> Quad:
        return Quad(
            self.a * other.a + 3 * self.b * other.b,
            self.a * other.b + self.b * other.a,
        )

    def to_float(self) -> float:
        return float(self.a) + float(self.b) * SQRT3


@dataclass(frozen=True)
class SeedVertex:
    label: str
    exact: tuple[Quad, Quad]
    numeric: tuple[float, float]


@dataclass(frozen=True)
class NumericVertex:
    label: str
    numeric: tuple[float, float]


@dataclass(frozen=True)
class InteriorHit:
    edge: tuple[str, str]
    t: float


@dataclass(frozen=True)
class CircleProfile:
    center: str
    radius_key: Quad
    radius_squared: float
    vertex_hits: tuple[str, ...]
    interior_hits: tuple[InteriorHit, ...]

    @property
    def boundary_hit_count(self) -> int:
        return len(self.vertex_hits) + len(self.interior_hits)


@dataclass(frozen=True)
class Candidate15Summary:
    t_value: Fraction
    normal_offset: Fraction
    strictly_convex: bool
    min_turn_area2: float
    max_vertex_hits: int
    max_boundary_hits: int
    circles_with_at_least_four_vertices: int
    circles_with_at_least_four_boundary_hits: int


def _q(value: int | Fraction, sqrt3: int | Fraction = 0) -> Quad:
    return Quad(Fraction(value), Fraction(sqrt3))


def _format_fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _json_float(value: float) -> float:
    rounded = round(value, JSON_FLOAT_DIGITS)
    if rounded == 0.0:
        return 0.0
    return rounded


def quad_to_json(value: Quad) -> str:
    """Stable compact display for `a + b*sqrt(3)`."""

    if value.b == 0:
        return _format_fraction(value.a)
    if value.a == 0:
        return f"{_format_fraction(value.b)}*sqrt3"
    sign = "+" if value.b > 0 else "-"
    return f"{_format_fraction(value.a)} {sign} {_format_fraction(abs(value.b))}*sqrt3"


def _rotate_exact(x: int, y: int, orbit: int) -> tuple[Quad, Quad]:
    if orbit == 0:
        return (_q(x), _q(y))
    if orbit == 1:
        return (
            _q(Fraction(-x, 2), Fraction(-y, 2)),
            _q(Fraction(-y, 2), Fraction(x, 2)),
        )
    if orbit == 2:
        return (
            _q(Fraction(-x, 2), Fraction(y, 2)),
            _q(Fraction(-y, 2), Fraction(-x, 2)),
        )
    raise ValueError(f"unknown orbit: {orbit}")


def _rotate_numeric(x: int, y: int, orbit: int) -> tuple[float, float]:
    return _rotate_numeric_point((float(x), float(y)), orbit)


def _rotate_numeric_point(point: tuple[float, float], orbit: int) -> tuple[float, float]:
    x, y = point
    angle = 2.0 * math.pi * orbit / 3.0
    return (
        x * math.cos(angle) - y * math.sin(angle),
        x * math.sin(angle) + y * math.cos(angle),
    )


def brp_seed_vertices() -> tuple[SeedVertex, ...]:
    """Return the 12-point 3-fold seed before the paper's A5 insertion."""

    vertices: list[SeedVertex] = []
    for orbit, prefix in enumerate(ORBIT_PREFIXES):
        for suffix, x, y in BASE_POINTS:
            vertices.append(
                SeedVertex(
                    label=f"{prefix}{suffix}",
                    exact=_rotate_exact(x, y, orbit),
                    numeric=_rotate_numeric(x, y, orbit),
                )
            )
    return tuple(vertices)


def brp_seed_numeric_vertices() -> tuple[NumericVertex, ...]:
    return tuple(NumericVertex(label=vertex.label, numeric=vertex.numeric) for vertex in brp_seed_vertices())


def brp_candidate_15gon(t_value: Fraction, normal_offset: Fraction) -> tuple[NumericVertex, ...]:
    """Return a synthetic 15-gon by placing A5 in the A4-B1 edge pocket.

    The source paper proves existence of an A5 near A4 using Lemma 3.1 but does
    not give coordinates. This two-parameter family is a diagnostic stand-in:
    it inserts A5 between A4 and B1, offset on either normal side of that edge,
    then rotates it to B5/C5. It is not claimed to be the paper's chosen point.
    """

    if not Fraction(0) < t_value < Fraction(1):
        raise ValueError("t_value must lie strictly between 0 and 1")
    if normal_offset == 0:
        raise ValueError("normal_offset must be nonzero")
    seed = brp_seed_numeric_vertices()
    by_label = {vertex.label: vertex.numeric for vertex in seed}
    a4 = by_label["A4"]
    b1 = by_label["B1"]
    edge = (b1[0] - a4[0], b1[1] - a4[1])
    normal = (-edge[1], edge[0])
    normal_length = math.hypot(*normal)
    normal_unit = (
        normal[0] / normal_length,
        normal[1] / normal_length,
    )
    t = float(t_value)
    h = float(normal_offset)
    a5 = (
        a4[0] + t * edge[0] + h * normal_unit[0],
        a4[1] + t * edge[1] + h * normal_unit[1],
    )
    vertices: list[NumericVertex] = []
    for orbit, prefix in enumerate(ORBIT_PREFIXES):
        for suffix in ("1", "2", "3", "4"):
            label = f"{prefix}{suffix}"
            if prefix == "A":
                point = by_label[label]
            else:
                source = by_label[f"A{suffix}"]
                point = _rotate_numeric_point(source, orbit)
            vertices.append(NumericVertex(label=label, numeric=point))
        vertices.append(
            NumericVertex(label=f"{prefix}5", numeric=_rotate_numeric_point(a5, orbit))
        )
    return tuple(vertices)


def exact_squared_distance(left: SeedVertex, right: SeedVertex) -> Quad:
    dx = left.exact[0] - right.exact[0]
    dy = left.exact[1] - right.exact[1]
    return dx * dx + dy * dy


def _orientation2(
    left: tuple[float, float],
    middle: tuple[float, float],
    right: tuple[float, float],
) -> float:
    return (middle[0] - left[0]) * (right[1] - left[1]) - (
        middle[1] - left[1]
    ) * (right[0] - left[0])


def seed_convexity_summary(vertices: tuple[SeedVertex, ...]) -> dict[str, object]:
    return numeric_convexity_summary(
        tuple(NumericVertex(label=vertex.label, numeric=vertex.numeric) for vertex in vertices)
    )


def numeric_convexity_summary(vertices: tuple[NumericVertex, ...]) -> dict[str, object]:
    turns = []
    for index, vertex in enumerate(vertices):
        previous = vertices[index - 1]
        following = vertices[(index + 1) % len(vertices)]
        turns.append(_orientation2(previous.numeric, vertex.numeric, following.numeric))
    return {
        "strictly_convex_in_seed_order": all(turn > 0.0 for turn in turns),
        "min_turn_area2": _json_float(min(turns)),
        "max_turn_area2": _json_float(max(turns)),
    }


def _numeric_squared_distance(left: NumericVertex, right: NumericVertex) -> float:
    dx = left.numeric[0] - right.numeric[0]
    dy = left.numeric[1] - right.numeric[1]
    return dx * dx + dy * dy


def _point_squared_distance(
    left: tuple[float, float],
    right: tuple[float, float],
) -> float:
    dx = left[0] - right[0]
    dy = left[1] - right[1]
    return dx * dx + dy * dy


def _same_distance(left: float, right: float, tol: float) -> bool:
    return abs(left - right) <= tol * max(1.0, abs(left), abs(right))


def _edge_roots(
    *,
    center: tuple[float, float],
    radius_squared: float,
    start: tuple[float, float],
    end: tuple[float, float],
    tol: float,
) -> tuple[float, ...]:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    fx = start[0] - center[0]
    fy = start[1] - center[1]
    a = dx * dx + dy * dy
    b = 2.0 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - radius_squared
    discriminant = b * b - 4.0 * a * c
    if discriminant < -tol:
        return ()
    if abs(discriminant) <= tol:
        roots = (-b / (2.0 * a),)
    else:
        sqrt_disc = math.sqrt(discriminant)
        roots = ((-b - sqrt_disc) / (2.0 * a), (-b + sqrt_disc) / (2.0 * a))
    accepted = []
    for root in roots:
        if -tol <= root <= 1.0 + tol:
            accepted.append(min(1.0, max(0.0, root)))
    return tuple(sorted(set(round(root, 12) for root in accepted)))


def _numeric_circle_profiles(
    vertices: tuple[NumericVertex, ...],
    *,
    root_tol: float,
    distance_tol: float,
) -> tuple[CircleProfile, ...]:
    profiles: list[CircleProfile] = []
    seen: set[tuple[str, int]] = set()
    for center_index, center in enumerate(vertices):
        target_radii = [
            _numeric_squared_distance(center, target)
            for target_index, target in enumerate(vertices)
            if target_index != center_index
        ]
        for radius_squared in target_radii:
            radius_bucket = round(radius_squared / distance_tol)
            key = (center.label, radius_bucket)
            if key in seen:
                continue
            seen.add(key)
            vertex_hits = tuple(
                target.label
                for target_index, target in enumerate(vertices)
                if target_index != center_index
                and _same_distance(
                    _numeric_squared_distance(center, target),
                    radius_squared,
                    distance_tol,
                )
            )
            interior_hits: list[InteriorHit] = []
            for edge_index, start in enumerate(vertices):
                end = vertices[(edge_index + 1) % len(vertices)]
                for root in _edge_roots(
                    center=center.numeric,
                    radius_squared=radius_squared,
                    start=start.numeric,
                    end=end.numeric,
                    tol=root_tol,
                ):
                    if root_tol < root < 1.0 - root_tol:
                        interior_hits.append(
                            InteriorHit(edge=(start.label, end.label), t=root)
                        )
            profiles.append(
                CircleProfile(
                    center=center.label,
                    radius_key=Quad(Fraction.from_float(radius_squared).limit_denominator()),
                    radius_squared=radius_squared,
                    vertex_hits=vertex_hits,
                    interior_hits=tuple(interior_hits),
                )
            )
    return tuple(profiles)


def _unique_radii_by_center(vertices: tuple[SeedVertex, ...]) -> dict[int, tuple[Quad, ...]]:
    radii: dict[int, set[Quad]] = defaultdict(set)
    for center_index, center in enumerate(vertices):
        for target_index, target in enumerate(vertices):
            if center_index == target_index:
                continue
            radii[center_index].add(exact_squared_distance(center, target))
    return {
        center_index: tuple(sorted(center_radii))
        for center_index, center_radii in radii.items()
    }


def circle_profile(
    vertices: tuple[SeedVertex, ...],
    *,
    center_index: int,
    radius_key: Quad,
    tol: float = ROOT_TOL,
) -> CircleProfile:
    center = vertices[center_index]
    radius_squared = radius_key.to_float()
    vertex_hits = tuple(
        vertex.label
        for vertex_index, vertex in enumerate(vertices)
        if vertex_index != center_index
        and exact_squared_distance(center, vertex) == radius_key
    )
    interior_hits: list[InteriorHit] = []
    for edge_index, start in enumerate(vertices):
        end = vertices[(edge_index + 1) % len(vertices)]
        for root in _edge_roots(
            center=center.numeric,
            radius_squared=radius_squared,
            start=start.numeric,
            end=end.numeric,
            tol=tol,
        ):
            if tol < root < 1.0 - tol:
                interior_hits.append(
                    InteriorHit(edge=(start.label, end.label), t=root)
                )
    return CircleProfile(
        center=center.label,
        radius_key=radius_key,
        radius_squared=radius_squared,
        vertex_hits=vertex_hits,
        interior_hits=tuple(interior_hits),
    )


def all_circle_profiles(tol: float = ROOT_TOL) -> tuple[CircleProfile, ...]:
    vertices = brp_seed_vertices()
    profiles: list[CircleProfile] = []
    for center_index, radii in _unique_radii_by_center(vertices).items():
        for radius_key in radii:
            profiles.append(
                circle_profile(
                    vertices,
                    center_index=center_index,
                    radius_key=radius_key,
                    tol=tol,
                )
            )
    return tuple(
        sorted(
            profiles,
            key=lambda profile: (
                profile.center,
                profile.boundary_hit_count,
                len(profile.vertex_hits),
                quad_to_json(profile.radius_key),
            ),
        )
    )


def summarize_candidate_15gon(
    t_value: Fraction,
    normal_offset: Fraction,
    *,
    root_tol: float = ROOT_TOL,
    distance_tol: float = DISTANCE_TOL,
) -> Candidate15Summary:
    vertices = brp_candidate_15gon(t_value, normal_offset)
    convexity = numeric_convexity_summary(vertices)
    profiles = _numeric_circle_profiles(
        vertices,
        root_tol=root_tol,
        distance_tol=distance_tol,
    )
    return Candidate15Summary(
        t_value=t_value,
        normal_offset=normal_offset,
        strictly_convex=bool(convexity["strictly_convex_in_seed_order"]),
        min_turn_area2=float(convexity["min_turn_area2"]),
        max_vertex_hits=max(len(profile.vertex_hits) for profile in profiles),
        max_boundary_hits=max(profile.boundary_hit_count for profile in profiles),
        circles_with_at_least_four_vertices=sum(
            1 for profile in profiles if len(profile.vertex_hits) >= 4
        ),
        circles_with_at_least_four_boundary_hits=sum(
            1 for profile in profiles if profile.boundary_hit_count >= 4
        ),
    )


def synthetic_a5_scan(
    parameters: Iterable[tuple[Fraction, Fraction]] = DEFAULT_A5_PARAMETERS,
    *,
    root_tol: float = ROOT_TOL,
    distance_tol: float = DISTANCE_TOL,
) -> tuple[Candidate15Summary, ...]:
    return tuple(
        summarize_candidate_15gon(
            t_value,
            normal_offset,
            root_tol=root_tol,
            distance_tol=distance_tol,
        )
        for t_value, normal_offset in parameters
    )


def _angle_degrees(
    left: tuple[float, float],
    middle: tuple[float, float],
    right: tuple[float, float],
) -> float:
    first = (left[0] - middle[0], left[1] - middle[1])
    second = (right[0] - middle[0], right[1] - middle[1])
    dot = first[0] * second[0] + first[1] * second[1]
    first_len = math.hypot(*first)
    second_len = math.hypot(*second)
    cosine = max(-1.0, min(1.0, dot / (first_len * second_len)))
    return math.degrees(math.acos(cosine))


def _point_on_segment_by_fraction(
    start: tuple[float, float],
    end: tuple[float, float],
    fraction: Fraction,
) -> tuple[float, float]:
    t = float(fraction)
    return (
        start[0] + t * (end[0] - start[0]),
        start[1] + t * (end[1] - start[1]),
    )


def lemma31_preflight() -> dict[str, object]:
    """Check the Lemma 3.1 role mapping used by the BRP construction."""

    seed = brp_seed_numeric_vertices()
    by_label = {vertex.label: vertex for vertex in seed}
    a_label, b_label, c_label, d_label = LEMMA31_ROLE_LABELS
    a_point = by_label[a_label].numeric
    b_point = by_label[b_label].numeric
    c_point = by_label[c_label].numeric
    d_point = by_label[d_label].numeric
    role_vertices = tuple(by_label[label] for label in LEMMA31_ROLE_LABELS)
    role_convexity = numeric_convexity_summary(role_vertices)
    clockwise_target = (d_point, c_point, b_point, a_point)
    clockwise_turns = [
        _orientation2(
            clockwise_target[index - 1],
            clockwise_target[index],
            clockwise_target[(index + 1) % len(clockwise_target)],
        )
        for index in range(len(clockwise_target))
    ]
    ba = (a_point[0] - b_point[0], a_point[1] - b_point[1])
    bc = (c_point[0] - b_point[0], c_point[1] - b_point[1])
    ba_dot_bc = ba[0] * bc[0] + ba[1] * bc[1]
    bprime_fraction_ceiling = _point_squared_distance(c_point, b_point) / (
        2.0 * ba_dot_bc
    )
    bprime = _point_on_segment_by_fraction(
        b_point,
        a_point,
        LEMMA31_DEFAULT_BPRIME_FRACTION,
    )
    bprime_radius_squared = _point_squared_distance(bprime, b_point)
    c_distance_to_bprime_squared = _point_squared_distance(c_point, bprime)
    angle_abc_degrees = _angle_degrees(a_point, b_point, c_point)
    return {
        "status": "LEMMA31_ROLE_PREFLIGHT_ONLY_A5_NOT_CONSTRUCTED",
        "role_mapping": {
            "A": a_label,
            "B": b_label,
            "C": c_label,
            "D": d_label,
            "candidate_C1_name_in_paper_construction": "A5",
        },
        "role_order": {
            "labels_counterclockwise": list(LEMMA31_ROLE_LABELS),
            "strictly_convex_counterclockwise": bool(
                role_convexity["strictly_convex_in_seed_order"]
            ),
            "min_turn_area2": role_convexity["min_turn_area2"],
            "clockwise_target_without_C1": [d_label, c_label, b_label, a_label],
            "clockwise_target_without_C1_verified": all(
                turn < 0.0 for turn in clockwise_turns
            ),
        },
        "angle_ABC": {
            "degrees": _json_float(angle_abc_degrees),
            "acute": angle_abc_degrees < 90.0,
        },
        "bprime_neighbourhood_budget": {
            "definition": "Bprime = B + tau*(A-B)",
            "default_tau": _format_fraction(LEMMA31_DEFAULT_BPRIME_FRACTION),
            "tau_ceiling_for_C_outside_S_Bprime": _json_float(bprime_fraction_ceiling),
            "default_tau_inside_ceiling": (
                float(LEMMA31_DEFAULT_BPRIME_FRACTION) < bprime_fraction_ceiling
            ),
            "default_radius": _json_float(math.sqrt(bprime_radius_squared)),
            "C_distance_to_default_Bprime": _json_float(
                math.sqrt(c_distance_to_bprime_squared)
            ),
            "C_outside_default_S_Bprime": (
                c_distance_to_bprime_squared > bprime_radius_squared
            ),
        },
        "a5_constraints_remaining": [
            "find C1=A5 such that D,C,C1,B,A are extreme and clockwise",
            "place A5 outside the circle centered at A and passing through B",
            "keep angle A-B-A5 acute",
            "make segment C-A5 intersect S_Bprime twice",
            "preserve the final 15-gon convexity after 120-degree rotations",
        ],
        "claim_scope": (
            "Verifies the source Lemma 3.1 role preconditions for the BRP seed "
            "using A=A3, B=A4, C=B1, D=B2 and records a reproducible Bprime "
            "neighbourhood budget. It does not construct A5."
        ),
    }


def _histogram(values: Iterable[int]) -> dict[str, int]:
    return {str(key): value for key, value in sorted(Counter(values).items())}


def _profile_to_json(profile: CircleProfile) -> dict[str, object]:
    return {
        "center": profile.center,
        "radius_squared_exact": quad_to_json(profile.radius_key),
        "radius_squared_float": _json_float(profile.radius_squared),
        "vertex_hit_count": len(profile.vertex_hits),
        "boundary_hit_count": profile.boundary_hit_count,
        "interior_hit_count": len(profile.interior_hits),
        "vertex_hits": list(profile.vertex_hits),
        "interior_hits": [
            {
                "edge": list(hit.edge),
                "t": _json_float(hit.t),
            }
            for hit in profile.interior_hits
        ],
    }


def _candidate_to_json(candidate: Candidate15Summary) -> dict[str, object]:
    return {
        "t": _format_fraction(candidate.t_value),
        "normal_offset": _format_fraction(candidate.normal_offset),
        "normal_side": "left" if candidate.normal_offset > 0 else "right",
        "strictly_convex": candidate.strictly_convex,
        "min_turn_area2": _json_float(candidate.min_turn_area2),
        "max_vertex_hits": candidate.max_vertex_hits,
        "max_boundary_hits": candidate.max_boundary_hits,
        "circles_with_at_least_four_vertices": candidate.circles_with_at_least_four_vertices,
        "circles_with_at_least_four_boundary_hits": (
            candidate.circles_with_at_least_four_boundary_hits
        ),
    }


def build_payload(tol: float = ROOT_TOL) -> dict[str, object]:
    if tol <= 0.0:
        raise ValueError("tol must be positive")
    vertices = brp_seed_vertices()
    profiles = all_circle_profiles(tol=tol)
    candidate_scan = synthetic_a5_scan(root_tol=tol)
    convex_candidate_count = sum(1 for candidate in candidate_scan if candidate.strictly_convex)
    best_candidate_vertex_hits = max(candidate.max_vertex_hits for candidate in candidate_scan)
    best_candidate_boundary_hits = max(candidate.max_boundary_hits for candidate in candidate_scan)
    max_vertex_hits = max(len(profile.vertex_hits) for profile in profiles)
    max_boundary_hits = max(profile.boundary_hit_count for profile in profiles)
    max_interior_hits = max(len(profile.interior_hits) for profile in profiles)
    best_vertex_profiles = [
        profile for profile in profiles if len(profile.vertex_hits) == max_vertex_hits
    ]
    best_boundary_profiles = [
        profile for profile in profiles if profile.boundary_hit_count == max_boundary_hits
    ]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "provenance": {
            "generator": "scripts/check_brp_boundary_probe.py",
            "command": "python scripts/check_brp_boundary_probe.py --write --assert-expected",
            "notes": (
                "Float64 boundary-intersection diagnostic for the quoted "
                "Barany--Roldan-Pensado 12-point seed before A5 insertion."
            ),
        },
        "source": {
            "construction": "Barany--Roldan-Pensado 3-fold seed before A5 insertion",
            "base_points": [
                {"label": f"A{suffix}", "x": x, "y": y}
                for suffix, x, y in BASE_POINTS
            ],
            "rotations_degrees": [0, 120, 240],
            "modeled_vertices": [vertex.label for vertex in vertices],
            "not_modeled": "the A5 insertion and the final 15-gon edge-parameter closure",
        },
        "convexity": seed_convexity_summary(vertices),
        "summary": {
            "seed_vertex_count": len(vertices),
            "seed_edge_count": len(vertices),
            "distinct_centered_vertex_radii": len(profiles),
            "max_vertex_hits_on_seed": max_vertex_hits,
            "max_boundary_hits_on_seed_edges": max_boundary_hits,
            "max_interior_hits_on_one_seed_circle": max_interior_hits,
            "circles_with_at_least_four_seed_vertices": sum(
                1 for profile in profiles if len(profile.vertex_hits) >= 4
            ),
            "circles_with_at_least_four_boundary_hits": sum(
                1 for profile in profiles if profile.boundary_hit_count >= 4
            ),
        },
        "synthetic_a5_scan": {
            "description": (
                "A5(t,h)=A4+t*(B1-A4)+h*unit_left_normal(A4B1), "
                "with signed h and rotations to B5/C5; diagnostic stand-in "
                "only, not the source paper's A5."
            ),
            "parameters": [
                {
                    "t": _format_fraction(t_value),
                    "normal_offset": _format_fraction(normal_offset),
                    "normal_side": "left" if normal_offset > 0 else "right",
                }
                for t_value, normal_offset in DEFAULT_A5_PARAMETERS
            ],
            "candidate_count": len(candidate_scan),
            "strictly_convex_candidate_count": convex_candidate_count,
            "best_max_vertex_hits": best_candidate_vertex_hits,
            "best_max_boundary_hits": best_candidate_boundary_hits,
            "candidates_with_at_least_four_vertices": sum(
                1 for candidate in candidate_scan if candidate.circles_with_at_least_four_vertices
            ),
            "interpretation": (
                "This signed normal-offset scan is a diagnostic stress test "
                "only. It samples nearby synthetic A5 placements but does not "
                "model the source paper's existential A5 constraints."
            ),
            "candidates": [_candidate_to_json(candidate) for candidate in candidate_scan],
        },
        "lemma31_preflight": lemma31_preflight(),
        "histograms": {
            "vertex_hit_count": _histogram(len(profile.vertex_hits) for profile in profiles),
            "boundary_hit_count": _histogram(profile.boundary_hit_count for profile in profiles),
            "interior_hit_count": _histogram(len(profile.interior_hits) for profile in profiles),
        },
        "best_vertex_circles": [_profile_to_json(profile) for profile in best_vertex_profiles],
        "best_boundary_circles": [
            _profile_to_json(profile) for profile in best_boundary_profiles
        ],
        "claim_scope": (
            "Float64 boundary-hit diagnostic for the 12-point three-fold seed "
            "quoted in the Barany--Roldan-Pensado convex-body discussion. It "
            "measures the gap between centered circle hits on polygon edges and "
            "hits at the modeled seed vertices, and includes a limited signed "
            "synthetic A5 edge-pocket closure stress test plus a Lemma 3.1 "
            "role-precondition preflight."
        ),
        "does_not_claim": [
            "proof of Erdos Problem #97",
            "counterexample to Erdos Problem #97",
            "finite-vertex extraction from the Barany--Roldan-Pensado body",
            "model of the source paper's A5 insertion or final 15-gon",
            "construction of the source paper's existential A5",
            "exact or interval certificate for boundary intersections",
        ],
        "next_steps": [
            "solve or parameterize A5 under the recorded Lemma 3.1 constraints",
            "promote edge-interior hits to symbolic edge parameters",
            "iterate the promoted hits as new candidate vertices",
            "replace float boundary intersections by exact algebraic or interval checks",
        ],
    }


def assert_expected_counts(payload: dict[str, object]) -> None:
    summary = payload.get("summary")
    histograms = payload.get("histograms")
    convexity = payload.get("convexity")
    if not isinstance(summary, dict):
        raise AssertionError("payload.summary must be an object")
    if not isinstance(histograms, dict):
        raise AssertionError("payload.histograms must be an object")
    if not isinstance(convexity, dict):
        raise AssertionError("payload.convexity must be an object")

    expected_summary = {
        "seed_vertex_count": 12,
        "seed_edge_count": 12,
        "distinct_centered_vertex_radii": 120,
        "max_vertex_hits_on_seed": 2,
        "max_boundary_hits_on_seed_edges": 5,
        "max_interior_hits_on_one_seed_circle": 4,
        "circles_with_at_least_four_seed_vertices": 0,
        "circles_with_at_least_four_boundary_hits": 45,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary.{key}: expected {expected}, got {summary.get(key)}")

    expected_histograms = {
        "vertex_hit_count": {"1": 108, "2": 12},
        "boundary_hit_count": {"1": 9, "2": 45, "3": 21, "4": 33, "5": 12},
        "interior_hit_count": {"0": 12, "1": 45, "2": 24, "3": 27, "4": 12},
    }
    for key, expected in expected_histograms.items():
        if histograms.get(key) != expected:
            raise AssertionError(
                f"histograms.{key}: expected {expected}, got {histograms.get(key)}"
            )

    if convexity.get("strictly_convex_in_seed_order") is not True:
        raise AssertionError("seed order is expected to be strictly convex")

    preflight = payload.get("lemma31_preflight")
    if not isinstance(preflight, dict):
        raise AssertionError("payload.lemma31_preflight must be an object")
    if preflight.get("status") != "LEMMA31_ROLE_PREFLIGHT_ONLY_A5_NOT_CONSTRUCTED":
        raise AssertionError("unexpected lemma31_preflight.status")
    role_order = preflight.get("role_order")
    angle_abc = preflight.get("angle_ABC")
    bprime_budget = preflight.get("bprime_neighbourhood_budget")
    if not isinstance(role_order, dict):
        raise AssertionError("payload.lemma31_preflight.role_order must be an object")
    if not isinstance(angle_abc, dict):
        raise AssertionError("payload.lemma31_preflight.angle_ABC must be an object")
    if not isinstance(bprime_budget, dict):
        raise AssertionError(
            "payload.lemma31_preflight.bprime_neighbourhood_budget must be an object"
        )
    if role_order.get("strictly_convex_counterclockwise") is not True:
        raise AssertionError("Lemma 3.1 role order is expected to be convex")
    if angle_abc.get("acute") is not True:
        raise AssertionError("Lemma 3.1 role angle ABC is expected to be acute")
    if bprime_budget.get("C_outside_default_S_Bprime") is not True:
        raise AssertionError("C is expected to be outside the default S_Bprime")

    synthetic = payload.get("synthetic_a5_scan")
    if not isinstance(synthetic, dict):
        raise AssertionError("payload.synthetic_a5_scan must be an object")
    expected_synthetic = {
        "candidate_count": 36,
        "strictly_convex_candidate_count": 0,
        "best_max_vertex_hits": 2,
        "best_max_boundary_hits": 8,
        "candidates_with_at_least_four_vertices": 0,
    }
    for key, expected in expected_synthetic.items():
        if synthetic.get(key) != expected:
            raise AssertionError(f"synthetic_a5_scan.{key}: expected {expected}, got {synthetic.get(key)}")
