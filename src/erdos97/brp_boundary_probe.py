"""Boundary-to-vertex diagnostic for the Barany--Roldan-Pensado seed."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

import math


SCHEMA = "erdos97.brp_boundary_vertexization_probe.v4"
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
LEMMA31_A5_EDGE_T_VALUES = tuple(Fraction(index, 500) for index in range(1, 101))
LEMMA31_A5_EDGE_NORMAL_OFFSETS = tuple(
    offset
    for denominator in (1000, 500, 200, 100, 50, 20, 10, 5, 2, 1)
    for offset in (Fraction(1, denominator), Fraction(-1, denominator))
)
LEMMA31_A5_WITNESS_T = Fraction(3, 125)
LEMMA31_A5_WITNESS_NORMAL_OFFSET = Fraction(-1, 200)
LEMMA31_A5_INTERVAL_RADIUS = Fraction(1, 10_000_000)
SQRT3 = math.sqrt(3.0)
ROOT_TOL = 1e-9
DISTANCE_TOL = 1e-6
JSON_FLOAT_DIGITS = 9
SAMPLED_A5_BOUNDARY_PROFILE_LIMIT = 12
SAMPLED_A5_BOUNDARY_ROOT_TOL = 1e-7


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


@dataclass(frozen=True)
class Lemma31A5ScanSample:
    t_value: Fraction
    normal_offset: Fraction
    point: tuple[float, float]
    local_clockwise: bool
    outside_s_a: bool
    acute_angle: bool
    segment_crosses_s_bprime_twice: bool
    s_bprime_roots: tuple[float, ...]
    local_clockwise_turns: tuple[float, ...]
    final_15gon: Candidate15Summary | None


@dataclass(frozen=True)
class FloatInterval:
    """Small outward-rounded interval over the checker float64 model."""

    lower: float
    upper: float

    @staticmethod
    def point(value: float) -> FloatInterval:
        return FloatInterval(
            math.nextafter(float(value), -math.inf),
            math.nextafter(float(value), math.inf),
        )

    def __add__(self, other: FloatInterval | float) -> FloatInterval:
        other = _as_interval(other)
        return FloatInterval(
            math.nextafter(self.lower + other.lower, -math.inf),
            math.nextafter(self.upper + other.upper, math.inf),
        )

    __radd__ = __add__

    def __sub__(self, other: FloatInterval | float) -> FloatInterval:
        other = _as_interval(other)
        return FloatInterval(
            math.nextafter(self.lower - other.upper, -math.inf),
            math.nextafter(self.upper - other.lower, math.inf),
        )

    def __rsub__(self, other: FloatInterval | float) -> FloatInterval:
        return _as_interval(other) - self

    def __neg__(self) -> FloatInterval:
        return FloatInterval(
            math.nextafter(-self.upper, -math.inf),
            math.nextafter(-self.lower, math.inf),
        )

    def __mul__(self, other: FloatInterval | float) -> FloatInterval:
        other = _as_interval(other)
        products = (
            self.lower * other.lower,
            self.lower * other.upper,
            self.upper * other.lower,
            self.upper * other.upper,
        )
        return FloatInterval(
            math.nextafter(min(products), -math.inf),
            math.nextafter(max(products), math.inf),
        )

    __rmul__ = __mul__

    def __truediv__(self, other: FloatInterval | float) -> FloatInterval:
        other = _as_interval(other)
        if other.lower <= 0.0 <= other.upper:
            raise ZeroDivisionError("interval division by range containing zero")
        reciprocals = (1.0 / other.lower, 1.0 / other.upper)
        return self * FloatInterval(
            math.nextafter(min(reciprocals), -math.inf),
            math.nextafter(max(reciprocals), math.inf),
        )

    def sqrt(self) -> FloatInterval:
        if self.lower < 0.0:
            raise ValueError("cannot take interval sqrt of a negative lower bound")
        return FloatInterval(
            math.nextafter(math.sqrt(self.lower), -math.inf),
            math.nextafter(math.sqrt(self.upper), math.inf),
        )


def _as_interval(value: FloatInterval | float) -> FloatInterval:
    if isinstance(value, FloatInterval):
        return value
    return FloatInterval.point(float(value))


def _interval_to_json(value: FloatInterval) -> dict[str, float]:
    return {
        "lower": _json_float(value.lower),
        "upper": _json_float(value.upper),
    }


def _interval_square(value: FloatInterval) -> FloatInterval:
    return value * value


def _interval_point(point: tuple[float, float]) -> tuple[FloatInterval, FloatInterval]:
    return (FloatInterval.point(point[0]), FloatInterval.point(point[1]))


def _interval_orientation2(
    left: tuple[FloatInterval, FloatInterval],
    middle: tuple[FloatInterval, FloatInterval],
    right: tuple[FloatInterval, FloatInterval],
) -> FloatInterval:
    return (middle[0] - left[0]) * (right[1] - left[1]) - (
        middle[1] - left[1]
    ) * (right[0] - left[0])


def _interval_squared_distance(
    left: tuple[FloatInterval, FloatInterval],
    right: tuple[FloatInterval, FloatInterval],
) -> FloatInterval:
    return _interval_square(left[0] - right[0]) + _interval_square(left[1] - right[1])


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


def _rotate_interval_point(
    point: tuple[FloatInterval, FloatInterval],
    orbit: int,
) -> tuple[FloatInterval, FloatInterval]:
    if orbit == 0:
        return point
    angle = 2.0 * math.pi * orbit / 3.0
    cosine = FloatInterval.point(math.cos(angle))
    sine = FloatInterval.point(math.sin(angle))
    return (
        point[0] * cosine - point[1] * sine,
        point[0] * sine + point[1] * cosine,
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
    a5 = _a5_edge_pocket_point(t_value, normal_offset, by_label=by_label)
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


def _a5_edge_pocket_point(
    t_value: Fraction,
    normal_offset: Fraction,
    *,
    by_label: dict[str, tuple[float, float]],
) -> tuple[float, float]:
    """Place A5 near the directed edge A4->B1 with a signed normal offset."""

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
    return (
        a4[0] + t * edge[0] + h * normal_unit[0],
        a4[1] + t * edge[1] + h * normal_unit[1],
    )


def _a5_edge_pocket_interval_point(
    t_value: FloatInterval,
    normal_offset: FloatInterval,
    *,
    by_label: dict[str, tuple[FloatInterval, FloatInterval]],
) -> tuple[FloatInterval, FloatInterval]:
    a4 = by_label["A4"]
    b1 = by_label["B1"]
    edge = (b1[0] - a4[0], b1[1] - a4[1])
    normal = (-edge[1], edge[0])
    normal_length = (
        _interval_square(normal[0]) + _interval_square(normal[1])
    ).sqrt()
    normal_unit = (
        normal[0] / normal_length,
        normal[1] / normal_length,
    )
    return (
        a4[0] + t_value * edge[0] + normal_offset * normal_unit[0],
        a4[1] + t_value * edge[1] + normal_offset * normal_unit[1],
    )


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
        "a5_constraints_remaining_after_sampled_scan": [
            "upgrade the sampled C1=A5 witness to exact or interval coordinates",
            "prove a neighbourhood of admissible A5 choices, not only one sample",
            "certify all source-paper boundary-intersection counts for the final 15-gon",
            "separate boundary hits from finite selected-vertex hits",
        ],
        "claim_scope": (
            "Verifies the source Lemma 3.1 role preconditions for the BRP seed "
            "using A=A3, B=A4, C=B1, D=B2 and records a reproducible Bprime "
            "neighbourhood budget. The companion scan records only sampled "
            "float64 A5 candidates."
        ),
    }


def _lemma31_a5_sample(
    t_value: Fraction,
    normal_offset: Fraction,
    *,
    root_tol: float,
    by_label: dict[str, tuple[float, float]],
) -> Lemma31A5ScanSample:
    a_label, b_label, c_label, d_label = LEMMA31_ROLE_LABELS
    a_point = by_label[a_label]
    b_point = by_label[b_label]
    c_point = by_label[c_label]
    d_point = by_label[d_label]
    a5 = _a5_edge_pocket_point(t_value, normal_offset, by_label=by_label)
    local_order = (d_point, c_point, a5, b_point, a_point)
    local_turns = tuple(
        _orientation2(
            local_order[index - 1],
            local_order[index],
            local_order[(index + 1) % len(local_order)],
        )
        for index in range(len(local_order))
    )
    local_clockwise = all(turn < 0.0 for turn in local_turns)
    outside_s_a = _point_squared_distance(a_point, a5) > _point_squared_distance(
        a_point,
        b_point,
    )
    ba = (a_point[0] - b_point[0], a_point[1] - b_point[1])
    ba5 = (a5[0] - b_point[0], a5[1] - b_point[1])
    acute_angle = ba[0] * ba5[0] + ba[1] * ba5[1] > 0.0
    bprime = _point_on_segment_by_fraction(
        b_point,
        a_point,
        LEMMA31_DEFAULT_BPRIME_FRACTION,
    )
    bprime_radius_squared = _point_squared_distance(bprime, b_point)
    roots = _edge_roots(
        center=bprime,
        radius_squared=bprime_radius_squared,
        start=c_point,
        end=a5,
        tol=root_tol,
    )
    segment_crosses_twice = (
        sum(1 for root in roots if root_tol < root < 1.0 - root_tol) == 2
    )
    final_15gon = None
    if local_clockwise and outside_s_a and acute_angle and segment_crosses_twice:
        final_15gon = summarize_candidate_15gon(
            t_value,
            normal_offset,
            root_tol=root_tol,
        )
    return Lemma31A5ScanSample(
        t_value=t_value,
        normal_offset=normal_offset,
        point=a5,
        local_clockwise=local_clockwise,
        outside_s_a=outside_s_a,
        acute_angle=acute_angle,
        segment_crosses_s_bprime_twice=segment_crosses_twice,
        s_bprime_roots=roots,
        local_clockwise_turns=local_turns,
        final_15gon=final_15gon,
    )


def _a5_sample_to_json(sample: Lemma31A5ScanSample) -> dict[str, object]:
    final = sample.final_15gon
    return {
        "t": _format_fraction(sample.t_value),
        "normal_offset": _format_fraction(sample.normal_offset),
        "normal_side": "left" if sample.normal_offset > 0 else "right",
        "point_float": {
            "x": _json_float(sample.point[0]),
            "y": _json_float(sample.point[1]),
        },
        "lemma31_N1_bullets": {
            "D_C_A5_B_A_extreme_clockwise": sample.local_clockwise,
            "A5_outside_S_A": sample.outside_s_a,
            "angle_A_B_A5_acute": sample.acute_angle,
            "segment_C_A5_intersects_default_S_Bprime_twice": (
                sample.segment_crosses_s_bprime_twice
            ),
            "S_Bprime_roots_on_segment_C_A5": [
                _json_float(root) for root in sample.s_bprime_roots
            ],
            "largest_clockwise_turn_area2": _json_float(
                max(sample.local_clockwise_turns)
            ),
        },
        "rotated_15gon": None
        if final is None
        else {
            "strictly_convex": final.strictly_convex,
            "min_turn_area2": _json_float(final.min_turn_area2),
            "max_vertex_hits": final.max_vertex_hits,
            "max_boundary_hits": final.max_boundary_hits,
            "circles_with_at_least_four_vertices": (
                final.circles_with_at_least_four_vertices
            ),
            "circles_with_at_least_four_boundary_hits": (
                final.circles_with_at_least_four_boundary_hits
            ),
        },
    }


def lemma31_a5_constraint_scan(
    parameters: Iterable[tuple[Fraction, Fraction]] | None = None,
    *,
    root_tol: float = ROOT_TOL,
) -> dict[str, object]:
    """Sample A5 candidates against the N=1 Lemma 3.1 construction bullets."""

    seed = brp_seed_numeric_vertices()
    by_label = {vertex.label: vertex.numeric for vertex in seed}
    if parameters is None:
        parameters = (
            (t_value, normal_offset)
            for t_value in LEMMA31_A5_EDGE_T_VALUES
            for normal_offset in LEMMA31_A5_EDGE_NORMAL_OFFSETS
        )
    samples = [
        _lemma31_a5_sample(
            t_value,
            normal_offset,
            root_tol=root_tol,
            by_label=by_label,
        )
        for t_value, normal_offset in parameters
    ]
    local_clockwise = [sample for sample in samples if sample.local_clockwise]
    local_outside = [sample for sample in local_clockwise if sample.outside_s_a]
    local_outside_acute = [sample for sample in local_outside if sample.acute_angle]
    lemma31_samples = [
        sample
        for sample in local_outside_acute
        if sample.segment_crosses_s_bprime_twice
    ]
    final_convex_samples = [
        sample
        for sample in lemma31_samples
        if sample.final_15gon is not None and sample.final_15gon.strictly_convex
    ]
    return {
        "status": "SAMPLED_NUMERICAL_A5_CONSTRAINT_PROBE",
        "source_lemma_scope": (
            "N=1 specialization of Lemma 3.1 with "
            "A=A3, B=A4, C=B1, D=B2, C1=A5, and default "
            f"Bprime fraction {_format_fraction(LEMMA31_DEFAULT_BPRIME_FRACTION)}."
        ),
        "parameterization": {
            "formula": "A5(t,h)=A4+t*(B1-A4)+h*unit_left_normal(A4B1)",
            "t_values": {
                "formula": "i/500 for 1 <= i <= 100",
                "count": len(LEMMA31_A5_EDGE_T_VALUES),
                "min": _format_fraction(LEMMA31_A5_EDGE_T_VALUES[0]),
                "max": _format_fraction(LEMMA31_A5_EDGE_T_VALUES[-1]),
            },
            "normal_offsets": [
                _format_fraction(offset) for offset in LEMMA31_A5_EDGE_NORMAL_OFFSETS
            ],
            "sample_count": len(samples),
        },
        "filter_counts": {
            "D_C_A5_B_A_extreme_clockwise": len(local_clockwise),
            "plus_A5_outside_S_A": len(local_outside),
            "plus_angle_A_B_A5_acute": len(local_outside_acute),
            "plus_segment_C_A5_intersects_default_S_Bprime_twice": len(
                lemma31_samples
            ),
            "plus_rotated_15gon_strictly_convex": len(final_convex_samples),
        },
        "individual_condition_counts": {
            "D_C_A5_B_A_extreme_clockwise": sum(
                1 for sample in samples if sample.local_clockwise
            ),
            "A5_outside_S_A": sum(1 for sample in samples if sample.outside_s_a),
            "angle_A_B_A5_acute": sum(1 for sample in samples if sample.acute_angle),
            "segment_C_A5_intersects_default_S_Bprime_twice": sum(
                1 for sample in samples if sample.segment_crosses_s_bprime_twice
            ),
        },
        "sampled_witnesses": [_a5_sample_to_json(sample) for sample in lemma31_samples],
        "interpretation": (
            "This is a bounded float64 sample of the local Lemma 3.1 A5 "
            "constraints, not an exact coordinate certificate and not a "
            "finite-vertex extraction from the BRP convex-body construction."
        ),
    }


def _interval_box_endpoints(
    center: Fraction,
    radius: Fraction,
) -> dict[str, str]:
    return {
        "lower": _format_fraction(center - radius),
        "center": _format_fraction(center),
        "upper": _format_fraction(center + radius),
        "radius": _format_fraction(radius),
    }


def lemma31_a5_interval_box_probe() -> dict[str, object]:
    """Certify a tiny A5 neighbourhood in the checker float64 interval model."""

    seed = brp_seed_numeric_vertices()
    by_label = {vertex.label: _interval_point(vertex.numeric) for vertex in seed}
    t_center = LEMMA31_A5_WITNESS_T
    h_center = LEMMA31_A5_WITNESS_NORMAL_OFFSET
    radius = LEMMA31_A5_INTERVAL_RADIUS
    t_interval = FloatInterval(
        math.nextafter(float(t_center - radius), -math.inf),
        math.nextafter(float(t_center + radius), math.inf),
    )
    h_interval = FloatInterval(
        math.nextafter(float(h_center - radius), -math.inf),
        math.nextafter(float(h_center + radius), math.inf),
    )
    a5 = _a5_edge_pocket_interval_point(
        t_interval,
        h_interval,
        by_label=by_label,
    )
    a_label, b_label, c_label, d_label = LEMMA31_ROLE_LABELS
    a_point = by_label[a_label]
    b_point = by_label[b_label]
    c_point = by_label[c_label]
    d_point = by_label[d_label]
    local_order = (d_point, c_point, a5, b_point, a_point)
    local_turns = tuple(
        _interval_orientation2(
            local_order[index - 1],
            local_order[index],
            local_order[(index + 1) % len(local_order)],
        )
        for index in range(len(local_order))
    )
    outside_margin = _interval_squared_distance(
        a_point,
        a5,
    ) - _interval_squared_distance(a_point, b_point)
    ba = (a_point[0] - b_point[0], a_point[1] - b_point[1])
    ba5 = (a5[0] - b_point[0], a5[1] - b_point[1])
    acute_dot = ba[0] * ba5[0] + ba[1] * ba5[1]
    tau = FloatInterval.point(float(LEMMA31_DEFAULT_BPRIME_FRACTION))
    bprime = (
        b_point[0] + tau * (a_point[0] - b_point[0]),
        b_point[1] + tau * (a_point[1] - b_point[1]),
    )
    bprime_radius_squared = _interval_squared_distance(bprime, b_point)
    dx = a5[0] - c_point[0]
    dy = a5[1] - c_point[1]
    fx = c_point[0] - bprime[0]
    fy = c_point[1] - bprime[1]
    quadratic_a = _interval_square(dx) + _interval_square(dy)
    quadratic_b = FloatInterval.point(2.0) * (fx * dx + fy * dy)
    quadratic_c = (
        _interval_square(fx) + _interval_square(fy) - bprime_radius_squared
    )
    discriminant = (
        quadratic_b * quadratic_b
        - FloatInterval.point(4.0) * quadratic_a * quadratic_c
    )
    sqrt_discriminant = discriminant.sqrt()
    denominator = FloatInterval.point(2.0) * quadratic_a
    first_root = (-quadratic_b - sqrt_discriminant) / denominator
    second_root = (-quadratic_b + sqrt_discriminant) / denominator
    root_intervals = (first_root, second_root)

    base_vertices = {f"A{suffix}": by_label[f"A{suffix}"] for suffix in ("1", "2", "3", "4")}
    interval_15gon: list[tuple[str, tuple[FloatInterval, FloatInterval]]] = []
    for orbit, prefix in enumerate(ORBIT_PREFIXES):
        for suffix in ("1", "2", "3", "4"):
            source = base_vertices[f"A{suffix}"]
            interval_15gon.append(
                (
                    f"{prefix}{suffix}",
                    source if orbit == 0 else _rotate_interval_point(source, orbit),
                )
            )
        interval_15gon.append((f"{prefix}5", _rotate_interval_point(a5, orbit)))
    rotated_turns = tuple(
        (
            label,
            _interval_orientation2(
                interval_15gon[index - 1][1],
                point,
                interval_15gon[(index + 1) % len(interval_15gon)][1],
            ),
        )
        for index, (label, point) in enumerate(interval_15gon)
    )
    local_clockwise = max(turn.upper for turn in local_turns) < 0.0
    outside_s_a = outside_margin.lower > 0.0
    acute_angle = acute_dot.lower > 0.0
    crosses_twice = (
        discriminant.lower > 0.0
        and first_root.lower > 0.0
        and first_root.upper < 1.0
        and second_root.lower > 0.0
        and second_root.upper < 1.0
        and first_root.upper < second_root.lower
    )
    rotated_strictly_convex = min(turn.lower for _, turn in rotated_turns) > 0.0
    return {
        "status": "FLOAT64_INTERVAL_BOX_DIAGNOSTIC",
        "coordinate_model": (
            "Outward-rounded interval arithmetic over the checker float64 "
            "coordinate model. This is not an exact algebraic certificate for "
            "the source Q(sqrt(3)) coordinates."
        ),
        "box": {
            "t": _interval_box_endpoints(t_center, radius),
            "normal_offset": _interval_box_endpoints(h_center, radius),
            "sampled_witness_center": {
                "t": _format_fraction(t_center),
                "normal_offset": _format_fraction(h_center),
            },
        },
        "a5_coordinate_interval": {
            "x": _interval_to_json(a5[0]),
            "y": _interval_to_json(a5[1]),
        },
        "lemma31_N1_interval_checks": {
            "D_C_A5_B_A_extreme_clockwise": local_clockwise,
            "local_turn_intervals": [
                _interval_to_json(turn) for turn in local_turns
            ],
            "max_local_turn_upper_bound": _json_float(
                max(turn.upper for turn in local_turns)
            ),
            "A5_outside_S_A": outside_s_a,
            "outside_S_A_margin_interval": _interval_to_json(outside_margin),
            "angle_A_B_A5_acute": acute_angle,
            "acute_dot_interval": _interval_to_json(acute_dot),
            "segment_C_A5_intersects_default_S_Bprime_twice": crosses_twice,
            "S_Bprime_quadratic": {
                "a": _interval_to_json(quadratic_a),
                "b": _interval_to_json(quadratic_b),
                "c": _interval_to_json(quadratic_c),
                "discriminant": _interval_to_json(discriminant),
            },
            "S_Bprime_root_intervals_on_segment_C_A5": [
                _interval_to_json(root) for root in root_intervals
            ],
        },
        "rotated_15gon_interval_checks": {
            "strictly_convex": rotated_strictly_convex,
            "min_turn_lower_bound": _json_float(
                min(turn.lower for _, turn in rotated_turns)
            ),
            "turn_intervals": [
                {"label": label, **_interval_to_json(turn)}
                for label, turn in rotated_turns
            ],
        },
        "all_interval_checks_pass": (
            local_clockwise
            and outside_s_a
            and acute_angle
            and crosses_twice
            and rotated_strictly_convex
        ),
        "interpretation": (
            "Certifies a small float64-model box around the sampled A5 "
            "witness for the local Lemma 3.1 bullets and rotated 15-gon "
            "strict convexity. It does not certify BRP boundary-intersection "
            "counts, finite-vertex multiplicities throughout the box, or exact "
            "source-paper coordinates."
        ),
    }


def _sampled_profile_sort_key(profile: CircleProfile) -> tuple[object, ...]:
    return (
        -profile.boundary_hit_count,
        -len(profile.vertex_hits),
        -len(profile.interior_hits),
        profile.center,
        _json_float(profile.radius_squared),
        profile.vertex_hits,
        tuple((hit.edge, hit.t) for hit in profile.interior_hits),
    )


def _sampled_profile_to_json(profile: CircleProfile) -> dict[str, object]:
    return {
        "center": profile.center,
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


def sampled_a5_boundary_support_scan(
    *,
    root_tol: float = ROOT_TOL,
    distance_tol: float = DISTANCE_TOL,
    profile_limit: int = SAMPLED_A5_BOUNDARY_PROFILE_LIMIT,
) -> dict[str, object]:
    """Record boundary-rich centered circles for the sampled synthetic 15-gon."""

    if profile_limit <= 0:
        raise ValueError("profile_limit must be positive")
    effective_root_tol = max(root_tol, SAMPLED_A5_BOUNDARY_ROOT_TOL)
    vertices = brp_candidate_15gon(
        LEMMA31_A5_WITNESS_T,
        LEMMA31_A5_WITNESS_NORMAL_OFFSET,
    )
    profiles = _numeric_circle_profiles(
        vertices,
        root_tol=effective_root_tol,
        distance_tol=distance_tol,
    )
    convexity = numeric_convexity_summary(vertices)
    max_vertex_hits = max(len(profile.vertex_hits) for profile in profiles)
    max_boundary_hits = max(profile.boundary_hit_count for profile in profiles)
    max_interior_hits = max(len(profile.interior_hits) for profile in profiles)
    best_boundary_profiles = sorted(
        (profile for profile in profiles if profile.boundary_hit_count == max_boundary_hits),
        key=_sampled_profile_sort_key,
    )
    rich_boundary_profiles = sorted(
        (profile for profile in profiles if profile.boundary_hit_count >= 4),
        key=_sampled_profile_sort_key,
    )
    return {
        "status": "SAMPLED_A5_BOUNDARY_SUPPORT_DIAGNOSTIC",
        "coordinate_model": (
            "Float64 sampled synthetic 15-gon from the recorded Lemma 3.1 "
            "A5 witness. The serialized radii and edge parameters are "
            "diagnostic approximations, not exact algebraic certificates."
        ),
        "boundary_root_tol": _json_float(effective_root_tol),
        "sampled_witness": {
            "t": _format_fraction(LEMMA31_A5_WITNESS_T),
            "normal_offset": _format_fraction(LEMMA31_A5_WITNESS_NORMAL_OFFSET),
            "normal_side": "right",
        },
        "vertex_order": [vertex.label for vertex in vertices],
        "summary": {
            "profile_count": len(profiles),
            "strictly_convex": bool(convexity["strictly_convex_in_seed_order"]),
            "min_turn_area2": convexity["min_turn_area2"],
            "max_vertex_hits": max_vertex_hits,
            "max_boundary_hits": max_boundary_hits,
            "max_interior_hits": max_interior_hits,
            "circles_with_at_least_four_vertices": sum(
                1 for profile in profiles if len(profile.vertex_hits) >= 4
            ),
            "circles_with_at_least_four_boundary_hits": sum(
                1 for profile in profiles if profile.boundary_hit_count >= 4
            ),
            "circles_with_at_least_six_boundary_hits": sum(
                1 for profile in profiles if profile.boundary_hit_count >= 6
            ),
        },
        "histograms": {
            "vertex_hit_count": _histogram(len(profile.vertex_hits) for profile in profiles),
            "boundary_hit_count": _histogram(profile.boundary_hit_count for profile in profiles),
            "interior_hit_count": _histogram(len(profile.interior_hits) for profile in profiles),
        },
        "best_boundary_circles": [
            _sampled_profile_to_json(profile) for profile in best_boundary_profiles
        ],
        "top_boundary_circles": [
            _sampled_profile_to_json(profile)
            for profile in rich_boundary_profiles[:profile_limit]
        ],
        "interpretation": (
            "The sampled final 15-gon keeps the BRP-style boundary richness "
            "visible at edge interiors: centered circles can hit six boundary "
            "points, while no centered circle hits four modeled vertices. This "
            "does not replay the source paper's continuum proof and does not "
            "turn the sampled polygon into a finite counterexample."
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
    a5_constraint_scan = lemma31_a5_constraint_scan(root_tol=tol)
    a5_interval_box = lemma31_a5_interval_box_probe()
    sampled_boundary_scan = sampled_a5_boundary_support_scan(root_tol=tol)
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
                "Barany--Roldan-Pensado 12-point seed and sampled synthetic "
                "15-gon after one A5 insertion."
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
            "not_modeled": (
                "the A5 insertion from the source paper as exact coordinates "
                "and the final 15-gon edge-parameter closure"
            ),
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
        "lemma31_a5_constraint_scan": a5_constraint_scan,
        "lemma31_a5_interval_box_probe": a5_interval_box,
        "sampled_a5_boundary_support_scan": sampled_boundary_scan,
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
            "synthetic A5 edge-pocket closure stress test, a Lemma 3.1 "
            "role-precondition preflight, and a bounded sampled A5 constraint "
            "probe with a tiny float64 interval-box follow-up plus an explicit "
            "boundary-support scan on the sampled synthetic 15-gon."
        ),
        "does_not_claim": [
            "proof of Erdos Problem #97",
            "counterexample to Erdos Problem #97",
            "finite-vertex extraction from the Barany--Roldan-Pensado body",
            "exact model of the source paper's A5 insertion or final 15-gon",
            "exact construction of the source paper's existential A5",
            "exact algebraic or formal interval certificate for the sampled A5",
            "exact or interval certificate for boundary intersections",
            "replay of the source paper's continuum boundary-intersection proof",
        ],
        "next_steps": [
            "replace the float64 A5 interval box with exact algebraic or directed-decimal coordinates",
            "certify sampled final-15-gon boundary hits with exact algebraic or interval checks",
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

    a5_scan = payload.get("lemma31_a5_constraint_scan")
    if not isinstance(a5_scan, dict):
        raise AssertionError("payload.lemma31_a5_constraint_scan must be an object")
    parameterization = a5_scan.get("parameterization")
    filter_counts = a5_scan.get("filter_counts")
    individual_condition_counts = a5_scan.get("individual_condition_counts")
    witnesses = a5_scan.get("sampled_witnesses")
    if not isinstance(parameterization, dict):
        raise AssertionError("payload.lemma31_a5_constraint_scan.parameterization must be an object")
    if not isinstance(filter_counts, dict):
        raise AssertionError("payload.lemma31_a5_constraint_scan.filter_counts must be an object")
    if not isinstance(individual_condition_counts, dict):
        raise AssertionError(
            "payload.lemma31_a5_constraint_scan.individual_condition_counts must be an object"
        )
    if not isinstance(witnesses, list):
        raise AssertionError("payload.lemma31_a5_constraint_scan.sampled_witnesses must be a list")
    if parameterization.get("sample_count") != 2000:
        raise AssertionError("expected 2000 sampled A5 parameters")
    expected_filter_counts = {
        "D_C_A5_B_A_extreme_clockwise": 700,
        "plus_A5_outside_S_A": 290,
        "plus_angle_A_B_A5_acute": 3,
        "plus_segment_C_A5_intersects_default_S_Bprime_twice": 1,
        "plus_rotated_15gon_strictly_convex": 1,
    }
    for key, expected in expected_filter_counts.items():
        if filter_counts.get(key) != expected:
            raise AssertionError(
                f"lemma31_a5_constraint_scan.filter_counts.{key}: "
                f"expected {expected}, got {filter_counts.get(key)}"
            )
    expected_individual_counts = {
        "D_C_A5_B_A_extreme_clockwise": 700,
        "A5_outside_S_A": 590,
        "angle_A_B_A5_acute": 1413,
        "segment_C_A5_intersects_default_S_Bprime_twice": 41,
    }
    for key, expected in expected_individual_counts.items():
        if individual_condition_counts.get(key) != expected:
            raise AssertionError(
                f"lemma31_a5_constraint_scan.individual_condition_counts.{key}: "
                f"expected {expected}, got {individual_condition_counts.get(key)}"
            )
    if len(witnesses) != 1:
        raise AssertionError(f"expected 1 sampled A5 witness, got {len(witnesses)}")
    witness = witnesses[0]
    if not isinstance(witness, dict):
        raise AssertionError("sampled A5 witness must be an object")
    if witness.get("t") != "3/125" or witness.get("normal_offset") != "-1/200":
        raise AssertionError("unexpected sampled A5 witness parameters")
    rotated_15gon = witness.get("rotated_15gon")
    if not isinstance(rotated_15gon, dict):
        raise AssertionError("sampled A5 witness must include rotated_15gon summary")
    if rotated_15gon.get("strictly_convex") is not True:
        raise AssertionError("sampled A5 witness should keep the rotated 15-gon convex")
    if rotated_15gon.get("circles_with_at_least_four_vertices") != 0:
        raise AssertionError("sampled A5 witness should not create four-vertex circles")

    interval_box = payload.get("lemma31_a5_interval_box_probe")
    if not isinstance(interval_box, dict):
        raise AssertionError("payload.lemma31_a5_interval_box_probe must be an object")
    box = interval_box.get("box")
    interval_checks = interval_box.get("lemma31_N1_interval_checks")
    rotated_interval_checks = interval_box.get("rotated_15gon_interval_checks")
    if not isinstance(box, dict):
        raise AssertionError("payload.lemma31_a5_interval_box_probe.box must be an object")
    if not isinstance(interval_checks, dict):
        raise AssertionError(
            "payload.lemma31_a5_interval_box_probe.lemma31_N1_interval_checks must be an object"
        )
    if not isinstance(rotated_interval_checks, dict):
        raise AssertionError(
            "payload.lemma31_a5_interval_box_probe.rotated_15gon_interval_checks must be an object"
        )
    if interval_box.get("all_interval_checks_pass") is not True:
        raise AssertionError("sampled A5 interval box should pass all interval checks")
    if box.get("t") != {
        "lower": "239999/10000000",
        "center": "3/125",
        "upper": "240001/10000000",
        "radius": "1/10000000",
    }:
        raise AssertionError("unexpected A5 interval t box")
    if box.get("normal_offset") != {
        "lower": "-50001/10000000",
        "center": "-1/200",
        "upper": "-49999/10000000",
        "radius": "1/10000000",
    }:
        raise AssertionError("unexpected A5 interval normal-offset box")
    if interval_checks.get("D_C_A5_B_A_extreme_clockwise") is not True:
        raise AssertionError("A5 interval box should certify local clockwise order")
    if interval_checks.get("A5_outside_S_A") is not True:
        raise AssertionError("A5 interval box should stay outside S_A")
    if interval_checks.get("angle_A_B_A5_acute") is not True:
        raise AssertionError("A5 interval box should keep angle A-B-A5 acute")
    if interval_checks.get("segment_C_A5_intersects_default_S_Bprime_twice") is not True:
        raise AssertionError("A5 interval box should keep two S_Bprime crossings")
    if rotated_interval_checks.get("strictly_convex") is not True:
        raise AssertionError("A5 interval box should keep the rotated 15-gon convex")
    if interval_checks.get("max_local_turn_upper_bound") != -0.026805405:
        raise AssertionError("unexpected A5 interval local-turn bound")
    if rotated_interval_checks.get("min_turn_lower_bound") != 0.026803636:
        raise AssertionError("unexpected A5 interval 15-gon turn bound")

    sampled_support = payload.get("sampled_a5_boundary_support_scan")
    if not isinstance(sampled_support, dict):
        raise AssertionError("payload.sampled_a5_boundary_support_scan must be an object")
    sampled_summary = sampled_support.get("summary")
    sampled_histograms = sampled_support.get("histograms")
    best_sampled_boundary = sampled_support.get("best_boundary_circles")
    if not isinstance(sampled_summary, dict):
        raise AssertionError(
            "payload.sampled_a5_boundary_support_scan.summary must be an object"
        )
    if not isinstance(sampled_histograms, dict):
        raise AssertionError(
            "payload.sampled_a5_boundary_support_scan.histograms must be an object"
        )
    if not isinstance(best_sampled_boundary, list):
        raise AssertionError(
            "payload.sampled_a5_boundary_support_scan.best_boundary_circles must be a list"
        )
    expected_sampled_summary = {
        "profile_count": 195,
        "strictly_convex": True,
        "max_vertex_hits": 2,
        "max_boundary_hits": 6,
        "max_interior_hits": 4,
        "circles_with_at_least_four_vertices": 0,
        "circles_with_at_least_four_boundary_hits": 87,
        "circles_with_at_least_six_boundary_hits": 3,
    }
    for key, expected in expected_sampled_summary.items():
        if sampled_summary.get(key) != expected:
            raise AssertionError(
                f"sampled_a5_boundary_support_scan.summary.{key}: "
                f"expected {expected}, got {sampled_summary.get(key)}"
            )
    expected_sampled_histograms = {
        "vertex_hit_count": {"1": 174, "2": 21},
        "boundary_hit_count": {"1": 12, "2": 75, "3": 21, "4": 69, "5": 15, "6": 3},
        "interior_hit_count": {"0": 15, "1": 75, "2": 30, "3": 57, "4": 18},
    }
    for key, expected in expected_sampled_histograms.items():
        if sampled_histograms.get(key) != expected:
            raise AssertionError(
                f"sampled_a5_boundary_support_scan.histograms.{key}: "
                f"expected {expected}, got {sampled_histograms.get(key)}"
            )
    if [profile.get("center") for profile in best_sampled_boundary] != [
        "A3",
        "B3",
        "C3",
    ]:
        raise AssertionError("unexpected sampled 15-gon best boundary centers")

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
