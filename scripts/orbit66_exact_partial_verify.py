"""Exact certificate builder for the orbit66 partial construction."""

from __future__ import annotations

from collections import Counter
from typing import Any

from scripts import orbit66_exact_partial_geometry as geometry
from scripts.orbit66_exact_partial_data import (
    CLAIM_SCOPE,
    CYCLIC_ORDER,
    EXPECTED_ORBIT_COUNT,
    EXPECTED_POINT_COUNT,
    FORBIDDEN_CLAIMS,
    HISTORY,
    SCHEMA,
    STATUS,
    TRUST,
)
from scripts.orbit66_exact_partial_geometry import (
    build_representatives,
    check_seed_equalities,
    configure_precision,
    dyadic_lower_bound,
    interval_self_test,
    norm_squared,
    orientation,
    rotate,
    squared_distance,
)


def build_payload(bits: int = 256) -> dict[str, Any]:
    """Build and validate the exact partial-construction certificate."""

    configure_precision(bits)
    errors: list[str] = []
    try:
        check_seed_equalities()
        interval_self_test()
        representatives, arcs, radicands = build_representatives()

        orbit_count = len(representatives)
        points = [
            rotate(representative, phase)
            for phase in range(3)
            for representative in representatives
        ]
        point_count = len(points)
        if orbit_count != EXPECTED_ORBIT_COUNT:
            errors.append(f"unexpected orbit count: {orbit_count}")
        if point_count != EXPECTED_POINT_COUNT:
            errors.append(f"unexpected point count: {point_count}")
        if sorted(CYCLIC_ORDER) != list(range(point_count)):
            errors.append("cyclic order is not a permutation")

        minimum_determinant: int | None = None
        convexity_tests = 0
        for position, left_index in enumerate(CYCLIC_ORDER):
            right_index = CYCLIC_ORDER[(position + 1) % point_count]
            for other_index in range(point_count):
                if other_index in (left_index, right_index):
                    continue
                turn = orientation(
                    points[left_index], points[right_index], points[other_index]
                )
                convexity_tests += 1
                if turn.lo <= 0:
                    errors.append(
                        "strict convexity not certified at "
                        f"({left_index}, {right_index}, {other_index})"
                    )
                minimum_determinant = (
                    turn.lo
                    if minimum_determinant is None
                    else min(minimum_determinant, turn.lo)
                )

        minimum_separation_squared: int | None = None
        distinct_pairs = 0
        for left_index in range(point_count):
            for right_index in range(left_index):
                separation = squared_distance(
                    points[left_index], points[right_index]
                )
                distinct_pairs += 1
                if separation.lo <= 0:
                    errors.append(
                        f"distinctness not certified for {left_index}, {right_index}"
                    )
                minimum_separation_squared = (
                    separation.lo
                    if minimum_separation_squared is None
                    else min(minimum_separation_squared, separation.lo)
                )

        cross_witnesses: list[set[tuple[int, int]]] = [
            set() for _ in range(orbit_count)
        ]
        for source, target, phase in arcs:
            if source == target:
                errors.append("cross-orbit edge unexpectedly internal")
            cross_witnesses[source].add((target, phase))

        distribution: Counter[int] = Counter()
        rows: list[dict[str, Any]] = []
        expanded_witness_table: list[dict[str, Any]] = []
        for orbit in range(orbit_count):
            cross_witness_indices = sorted(
                target + phase * orbit_count
                for target, phase in cross_witnesses[orbit]
            )
            witnesses = [
                orbit + orbit_count,
                orbit + 2 * orbit_count,
                *cross_witness_indices,
            ]
            if len(witnesses) != len(set(witnesses)):
                errors.append(f"repeated witness for orbit {orbit}")

            selected_radius_squared = 3 * norm_squared(representatives[orbit])
            if selected_radius_squared.lo <= 0:
                errors.append(f"nonpositive selected radius for orbit {orbit}")

            distance_intervals = sorted(
                (
                    squared_distance(representatives[orbit], points[vertex]).lo,
                    squared_distance(representatives[orbit], points[vertex]).hi,
                    vertex,
                )
                for vertex in range(point_count)
                if vertex != orbit
            )
            overlap_components: list[list[int]] = []
            current_component: list[int] = []
            current_upper: int | None = None
            for lower, upper, vertex in distance_intervals:
                if current_upper is None or lower <= current_upper:
                    current_component.append(vertex)
                    current_upper = (
                        upper if current_upper is None else max(current_upper, upper)
                    )
                else:
                    overlap_components.append(current_component)
                    current_component = [vertex]
                    current_upper = upper
            if current_component:
                overlap_components.append(current_component)

            upper_bound = max(map(len, overlap_components))
            guaranteed_lower_bound = len(witnesses)
            if upper_bound != guaranteed_lower_bound:
                errors.append(
                    f"orbit {orbit}: exact maximum not isolated: "
                    f"{guaranteed_lower_bound} <= M <= {upper_bound}"
                )
            exact_maximum = guaranteed_lower_bound
            distribution[exact_maximum] += 3
            rows.append(
                {
                    "orbit": orbit,
                    "exact_maximum_multiplicity": exact_maximum,
                    "selected_radius_squared": f"3 * squared_norm(z[{orbit}])",
                    "representative_witness_indices": witnesses,
                    "outgoing_cross_orbit_witnesses": [
                        list(witness) for witness in sorted(cross_witnesses[orbit])
                    ],
                }
            )
            for phase in range(3):
                shifted_witnesses = [
                    (witness % orbit_count)
                    + ((witness // orbit_count + phase) % 3) * orbit_count
                    for witness in witnesses
                ]
                expanded_witness_table.append(
                    {
                        "vertex": orbit + phase * orbit_count,
                        "witnesses": shifted_witnesses,
                        "exact_maximum_multiplicity": exact_maximum,
                    }
                )

        distribution_dict = dict(sorted(distribution.items()))
        vertices_at_least_four = sum(
            count for multiplicity, count in distribution.items() if multiplicity >= 4
        )
        vertices_at_most_three = sum(
            count for multiplicity, count in distribution.items() if multiplicity <= 3
        )

        summary = {
            "point_count": point_count,
            "orbit_count": orbit_count,
            "dyadic_precision_bits": geometry.BITS,
            "vertices_with_maximum_multiplicity_at_least_four": (
                vertices_at_least_four
            ),
            "vertices_with_maximum_multiplicity_at_most_three": (
                vertices_at_most_three
            ),
            "exact_maximum_multiplicity_distribution": distribution_dict,
            "strict_hull_edge_point_determinants_certified": convexity_tests,
            "distinct_pairs_certified": distinct_pairs,
            "minimum_certified_edge_point_determinant_lower_bound": (
                dyadic_lower_bound(minimum_determinant)
                if minimum_determinant is not None
                else None
            ),
            "minimum_certified_squared_separation_lower_bound": (
                dyadic_lower_bound(minimum_separation_squared)
                if minimum_separation_squared is not None
                else None
            ),
            "intersection_radicand_count": len(radicands),
            "all_intersection_radicands_strictly_positive": all(
                radicand.lo > 0 for radicand in radicands
            ),
            "exceptional_orbits": [
                row["orbit"]
                for row in rows
                if row["exact_maximum_multiplicity"] <= 3
            ],
            "exceptional_vertices": sorted(
                row["vertex"]
                for row in expanded_witness_table
                if row["exact_maximum_multiplicity"] <= 3
            ),
        }

        coordinate_intervals = [
            {
                "vertex": index,
                "x_lower_numerator": str(point[0].lo),
                "x_upper_numerator": str(point[0].hi),
                "y_lower_numerator": str(point[1].lo),
                "y_upper_numerator": str(point[1].hi),
                "common_denominator_power_of_two": geometry.BITS,
            }
            for index, point in enumerate(points)
        ]
    except (ArithmeticError, AssertionError, ValueError, ZeroDivisionError) as exc:
        errors.append(f"verification exception: {exc}")
        summary = {}
        rows = []
        expanded_witness_table = []
        coordinate_intervals = []

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "validation_status": "passed" if not errors else "failed",
        "errors": errors,
        "construction": {
            "symmetry": "C3",
            "rotation": "omega=(-1+i*sqrt(3))/2",
            "seed": (
                "z0=2i; z1=(-8991*sqrt(3)-26503i)/10927; "
                "z2=(-10753*sqrt(3)-44665i)/18529"
            ),
            "history": [list(row) for row in HISTORY],
            "cyclic_order": list(CYCLIC_ORDER),
            "branch_convention": (
                "0 adds +h*J(b-a); 1 adds -h*J(b-a)"
            ),
        },
        "provenance": {
            "generator": "scripts/check_orbit66_exact_partial.py",
            "command": (
                "python scripts/check_orbit66_exact_partial.py "
                "--assert-expected --summary-json"
            ),
            "arithmetic": (
                "exact Q(sqrt(3)) seed equalities and defining circle identities; "
                "standard-library outward-rounded dyadic interval certificates "
                "for strict inequalities and distance separation"
            ),
        },
        "summary": summary,
        "rows": rows,
        "expanded_witness_table": sorted(
            expanded_witness_table, key=lambda row: row["vertex"]
        ),
        "coordinate_intervals": coordinate_intervals,
    }
    return payload

