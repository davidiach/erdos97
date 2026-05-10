"""Scan n=9 vertex-circle packets for reusable local lemma shapes.

This module is proof-mining scaffolding.  It does not prove the full n=9 case,
does not claim a counterexample, and does not promote the review-pending
vertex-circle checker.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Sequence

from erdos97.incidence_filters import chords_cross_in_order, normalize_chord
from erdos97.vertex_circle_quotient_replay import (
    SelectedRow,
    StrictInequality,
    parse_selected_rows,
    replay_vertex_circle_quotient,
)

SCHEMA = "erdos97.n9_vertex_circle_local_lemmas.v1"
STATUS = "REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Proof-mining scan for reusable n-independent vertex-circle local lemmas. "
    "This is not a proof of n=9, not a counterexample, not an independent "
    "review of the exhaustive checker, and not a global status update."
)

SHARED_ENDPOINT_LEMMA = "shared_endpoint_nested_self_edge"
NESTED_SPOKE_LEMMA = "nested_spoke_quotient_self_edge"
T03_SELECTED_PATH_SELF_EDGE = "t03_selected_path_self_edge"
T10_STRICT_CYCLE_LEMMA = "t10_two_edge_strict_cycle"
T11_STRICT_CYCLE_LEMMA = "t11_three_edge_strict_cycle"
T12_STRICT_CYCLE_LEMMA = "t12_three_edge_strict_cycle"
DIRECT_TWO_ROW_VARIANT = "nested_spoke_direct_two_row_special_case"
STRICT_CYCLE_LEMMA_BY_TEMPLATE = {
    "T10": T10_STRICT_CYCLE_LEMMA,
    "T11": T11_STRICT_CYCLE_LEMMA,
    "T12": T12_STRICT_CYCLE_LEMMA,
}

EXPECTED_SUMMARY = {
    SHARED_ENDPOINT_LEMMA: {
        "family_ids": ["F01", "F04", "F08", "F14"],
        "instance_count": 4,
        "covered_assignment_count": 40,
    },
    NESTED_SPOKE_LEMMA: {
        "family_ids": ["F02", "F03", "F06", "F09", "F10", "F11"],
        "instance_count": 8,
        "covered_assignment_count": 96,
    },
    T03_SELECTED_PATH_SELF_EDGE: {
        "family_ids": ["F05", "F15"],
        "instance_count": 2,
        "covered_assignment_count": 20,
    },
    T10_STRICT_CYCLE_LEMMA: {
        "family_ids": ["F12"],
        "instance_count": 1,
        "covered_assignment_count": 18,
    },
    T11_STRICT_CYCLE_LEMMA: {
        "family_ids": ["F07"],
        "instance_count": 1,
        "covered_assignment_count": 6,
    },
    T12_STRICT_CYCLE_LEMMA: {
        "family_ids": ["F16"],
        "instance_count": 1,
        "covered_assignment_count": 2,
    },
}
EXPECTED_DIRECT_TWO_ROW_INSTANCE_COUNT = 0


def local_lemma_scan_payload(
    self_edge_packet: dict[str, Any],
    strict_cycle_packet: dict[str, Any],
) -> dict[str, Any]:
    """Return a JSON-safe scan of reusable local-lemma instances."""

    order = _order_from_packet(self_edge_packet)
    strict_order = _order_from_packet(strict_cycle_packet)
    if order != strict_order:
        raise ValueError("source packets must use the same cyclic order")
    n = int(self_edge_packet.get("n", len(order)))
    if n != int(strict_cycle_packet.get("n", len(order))):
        raise ValueError("source packets must use the same n")

    shared_endpoint: list[dict[str, Any]] = []
    nested_spoke: list[dict[str, Any]] = []
    t03_selected_path: list[dict[str, Any]] = []
    direct_two_row: list[dict[str, Any]] = []

    for template, family in _self_edge_family_records(self_edge_packet):
        rows = parse_selected_rows(family["core_selected_rows"])
        row_map = _row_witness_map(rows)
        replay = replay_vertex_circle_quotient(n, order, rows)
        family_context = _family_context(template, family, rows, order)
        for edge in replay.self_edge_conflicts:
            if _is_shared_endpoint_t02_shape(edge, family_context):
                shared_endpoint.append(
                    _self_edge_instance(
                        lemma_id=SHARED_ENDPOINT_LEMMA,
                        template=template,
                        family=family,
                        rows=rows,
                        order=order,
                        edge=edge,
                        direct_conditions=_shared_endpoint_conditions(edge, row_map),
                    )
                )
            if _is_nested_spoke_quotient_shape(edge):
                instance = _self_edge_instance(
                    lemma_id=NESTED_SPOKE_LEMMA,
                    template=template,
                    family=family,
                    rows=rows,
                    order=order,
                    edge=edge,
                    direct_conditions=_direct_nested_spoke_conditions(edge, row_map),
                )
                nested_spoke.append(instance)
                if instance["direct_conditions"]["holds"]:
                    direct_two_row.append(
                        {
                            **instance,
                            "lemma_id": DIRECT_TWO_ROW_VARIANT,
                        }
                    )
            if _is_t03_selected_path_self_edge_shape(template, family, edge):
                t03_selected_path.append(
                    _self_edge_instance(
                        lemma_id=T03_SELECTED_PATH_SELF_EDGE,
                        template=template,
                        family=family,
                        rows=rows,
                        order=order,
                        edge=edge,
                        direct_conditions=_selected_path_conditions(family),
                    )
                )

    strict_cycle_instances: dict[str, list[dict[str, Any]]] = {
        lemma_id: [] for lemma_id in STRICT_CYCLE_LEMMA_BY_TEMPLATE.values()
    }
    for template, family in _strict_cycle_family_records(strict_cycle_packet):
        template_id = str(template.get("template_id"))
        lemma_id = STRICT_CYCLE_LEMMA_BY_TEMPLATE.get(template_id)
        if lemma_id is None:
            continue
        strict_cycle_instances[lemma_id].append(
            _strict_cycle_instance(template, family, order, lemma_id)
        )

    source_family_assignments = _source_family_assignments(
        self_edge_packet,
        strict_cycle_packet,
    )

    lemma_instances = {
        SHARED_ENDPOINT_LEMMA: shared_endpoint,
        NESTED_SPOKE_LEMMA: nested_spoke,
        T03_SELECTED_PATH_SELF_EDGE: t03_selected_path,
        **strict_cycle_instances,
    }

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n,
        "cyclic_order": list(order),
        "source_artifacts": [
            _source_summary(
                self_edge_packet,
                "data/certificates/n9_vertex_circle_self_edge_template_packet.json",
                "source self-edge template packet",
            ),
            _source_summary(
                strict_cycle_packet,
                "data/certificates/n9_vertex_circle_strict_cycle_template_packet.json",
                "source strict-cycle template packet",
            ),
        ],
        "lemmas": [
            _lemma_summary(SHARED_ENDPOINT_LEMMA, shared_endpoint),
            _lemma_summary(NESTED_SPOKE_LEMMA, nested_spoke),
            _lemma_summary(T03_SELECTED_PATH_SELF_EDGE, t03_selected_path),
            *(
                _lemma_summary(lemma_id, strict_cycle_instances[lemma_id])
                for lemma_id in STRICT_CYCLE_LEMMA_BY_TEMPLATE.values()
            ),
        ],
        "direct_two_row_nested_spoke_special_case": {
            "lemma_id": DIRECT_TWO_ROW_VARIANT,
            "interpretation": (
                "The two-row special case proposed in solver output 3 is a "
                "valid proof pattern, but this scan finds no exact direct "
                "instances in the current n=9 template packets.  The packet "
                "instances use the more general selected-distance quotient "
                "version instead."
            ),
            "instance_count": len(direct_two_row),
            "instances": direct_two_row,
        },
        "coverage_summary": _coverage_summary(
            lemma_instances,
            source_family_assignments,
        ),
        "interpretation": (
            "The listed local shapes are reusable obstruction candidates: each "
            "one produces either a reflexive strict edge or a directed strict "
            "cycle after selected-distance quotienting.  The scan only uses "
            "stored template-packet local cores and does not enumerate all n=9 "
            "selected-witness assignments."
        ),
    }


def _source_family_assignments(
    self_edge_packet: dict[str, Any],
    strict_cycle_packet: dict[str, Any],
) -> dict[str, int]:
    """Return source packet family assignment counts keyed by family id."""

    assignments: dict[str, int] = {}
    for _template, family in (
        *_self_edge_family_records(self_edge_packet),
        *_strict_cycle_family_records(strict_cycle_packet),
    ):
        family_id = str(family["family_id"])
        assignment_count = int(family["assignment_count"])
        previous = assignments.setdefault(family_id, assignment_count)
        if previous != assignment_count:
            raise ValueError(
                f"inconsistent assignment count for family {family_id}: "
                f"{previous} != {assignment_count}"
            )
    return assignments


def assert_expected_local_lemma_scan(payload: dict[str, Any]) -> None:
    """Assert the current expected local-lemma scan counts."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    claim_scope = str(payload.get("claim_scope", ""))
    for forbidden in ("proof of n=9", "counterexample", "global status update"):
        if f"not a {forbidden}" not in claim_scope and f"not an {forbidden}" not in claim_scope:
            raise AssertionError(f"claim_scope must explicitly reject {forbidden!r}")

    lemmas = payload.get("lemmas")
    if not isinstance(lemmas, list):
        raise AssertionError("lemmas must be a list")
    by_id = {str(item.get("lemma_id")): item for item in lemmas if isinstance(item, dict)}
    if set(by_id) != set(EXPECTED_SUMMARY):
        raise AssertionError(f"lemma ids mismatch: {sorted(by_id)!r}")
    for lemma_id, expected in EXPECTED_SUMMARY.items():
        item = by_id[lemma_id]
        for key, value in expected.items():
            if item.get(key) != value:
                raise AssertionError(
                    f"{lemma_id} {key} mismatch: expected {value!r}, got {item.get(key)!r}"
                )
        for instance in item.get("instances", []):
            if instance.get("simple_filter_violations") != []:
                raise AssertionError(
                    f"{lemma_id} {instance.get('family_id')} is already killed by simple filters"
                )

    special = payload.get("direct_two_row_nested_spoke_special_case")
    if not isinstance(special, dict):
        raise AssertionError("missing direct two-row nested-spoke special-case summary")
    if special.get("instance_count") != EXPECTED_DIRECT_TWO_ROW_INSTANCE_COUNT:
        raise AssertionError(
            "direct two-row nested-spoke instance count mismatch: "
            f"expected {EXPECTED_DIRECT_TWO_ROW_INSTANCE_COUNT}, "
            f"got {special.get('instance_count')!r}"
        )

    coverage = payload.get("coverage_summary")
    if not isinstance(coverage, dict):
        raise AssertionError("coverage_summary must be an object")
    if coverage.get("source_family_count") != 16:
        raise AssertionError("source_family_count mismatch")
    if coverage.get("source_assignment_count") != 184:
        raise AssertionError("source_assignment_count mismatch")
    if coverage.get("covered_family_count") != 15:
        raise AssertionError("covered_family_count mismatch")
    if coverage.get("covered_assignment_count") != 182:
        raise AssertionError("covered_assignment_count mismatch")
    if coverage.get("uncovered_family_count") != 1:
        raise AssertionError("uncovered_family_count mismatch")
    if coverage.get("uncovered_assignment_count") != 2:
        raise AssertionError("uncovered_assignment_count mismatch")
    if coverage.get("uncovered_family_ids") != ["F13"]:
        raise AssertionError("uncovered_family_ids mismatch")
    if coverage.get("covered_family_ids") != [
        "F01",
        "F02",
        "F03",
        "F04",
        "F05",
        "F06",
        "F07",
        "F08",
        "F09",
        "F10",
        "F11",
        "F12",
        "F14",
        "F15",
        "F16",
    ]:
        raise AssertionError("covered_family_ids mismatch")


def _order_from_packet(packet: dict[str, Any]) -> tuple[int, ...]:
    raw_order = packet.get("cyclic_order")
    if not isinstance(raw_order, Sequence) or isinstance(raw_order, str):
        raise ValueError("packet must contain cyclic_order")
    return tuple(int(label) for label in raw_order)


def _source_summary(packet: dict[str, Any], path: str, role: str) -> dict[str, Any]:
    return {
        "path": path,
        "role": role,
        "schema": packet.get("schema"),
        "status": packet.get("status"),
        "trust": packet.get("trust"),
    }


def _self_edge_family_records(
    packet: dict[str, Any],
) -> Iterable[tuple[dict[str, Any], dict[str, Any]]]:
    templates = packet.get("templates")
    if not isinstance(templates, list):
        raise ValueError("self-edge packet must contain templates")
    for template in templates:
        if not isinstance(template, dict):
            raise ValueError("self-edge template entries must be objects")
        family_records = template.get("family_records")
        if not isinstance(family_records, list):
            raise ValueError(f"{template.get('template_id')} must contain family_records")
        for family in family_records:
            if not isinstance(family, dict):
                raise ValueError("family_records entries must be objects")
            yield template, family


def _strict_cycle_family_records(
    packet: dict[str, Any],
) -> Iterable[tuple[dict[str, Any], dict[str, Any]]]:
    templates = packet.get("templates")
    if not isinstance(templates, list):
        raise ValueError("strict-cycle packet must contain templates")
    for template in templates:
        if not isinstance(template, dict):
            raise ValueError("strict-cycle template entries must be objects")
        family_records = template.get("family_records")
        if not isinstance(family_records, list):
            raise ValueError(f"{template.get('template_id')} must contain family_records")
        for family in family_records:
            if not isinstance(family, dict):
                raise ValueError("family_records entries must be objects")
            yield template, family


def _row_witness_map(rows: Sequence[SelectedRow]) -> dict[int, set[int]]:
    return {row.center: set(row.witnesses) for row in rows}


def _family_context(
    template: dict[str, Any],
    family: dict[str, Any],
    rows: Sequence[SelectedRow],
    order: Sequence[int],
) -> dict[str, Any]:
    return {
        "template_id": str(template.get("template_id")),
        "family_id": str(family.get("family_id")),
        "row_map": _row_witness_map(rows),
        "order": tuple(order),
    }


def _is_shared_endpoint_t02_shape(
    edge: StrictInequality,
    context: dict[str, Any],
) -> bool:
    if edge.outer_class != edge.inner_class:
        return False
    if edge.outer_interval != (0, 3) or edge.inner_interval != (0, 1):
        return False
    return _shared_endpoint_conditions(edge, context["row_map"])["holds"]


def _shared_endpoint_conditions(
    edge: StrictInequality,
    row_map: dict[int, set[int]],
) -> dict[str, Any]:
    center = edge.row
    a, b, _x, d = edge.witness_order
    d_row = sorted(row_map.get(d, set()))
    a_row = sorted(row_map.get(a, set()))
    d_condition = {center, a}.issubset(row_map.get(d, set()))
    a_condition = {center, b}.issubset(row_map.get(a, set()))
    return {
        "variant": "row_d_contains_center_and_a__row_a_contains_center_and_b",
        "labels": {"center": center, "a": a, "b": b, "d": d},
        "row_d_witnesses": d_row,
        "row_a_witnesses": a_row,
        "row_d_condition": d_condition,
        "row_a_condition": a_condition,
        "holds": d_condition and a_condition,
    }


def _is_nested_spoke_quotient_shape(edge: StrictInequality) -> bool:
    return (
        edge.outer_class == edge.inner_class
        and edge.outer_interval == (0, 3)
        and edge.inner_interval == (1, 2)
        and not (set(edge.outer_pair) & set(edge.inner_pair))
    )


def _direct_nested_spoke_conditions(
    edge: StrictInequality,
    row_map: dict[int, set[int]],
) -> dict[str, Any]:
    a, b, c, d = edge.witness_order
    row_a = sorted(row_map.get(a, set()))
    row_b = sorted(row_map.get(b, set()))
    a_condition = {b, d}.issubset(row_map.get(a, set()))
    b_condition = {a, c}.issubset(row_map.get(b, set()))
    return {
        "variant": "output3_direct_two_row_special_case",
        "labels": {"a": a, "b": b, "c": c, "d": d},
        "row_a_witnesses": row_a,
        "row_b_witnesses": row_b,
        "row_a_condition": a_condition,
        "row_b_condition": b_condition,
        "holds": a_condition and b_condition,
    }


def _is_t03_selected_path_self_edge_shape(
    template: dict[str, Any],
    family: dict[str, Any],
    edge: StrictInequality,
) -> bool:
    """Return whether the record is one of the checked T03 self-edge paths."""

    if str(template.get("template_id")) != "T03":
        return False
    equality = family.get("distance_equality")
    if not isinstance(equality, dict):
        return False
    return (
        edge.outer_class == edge.inner_class
        and _pair_list(edge.outer_pair) == _pair_list(equality.get("start_pair"))
        and _pair_list(edge.inner_pair) == _pair_list(equality.get("end_pair"))
    )


def _selected_path_conditions(family: dict[str, Any]) -> dict[str, Any]:
    equality = family["distance_equality"]
    return {
        "variant": "selected_path_self_edge",
        "start_pair": _pair_list(equality["start_pair"]),
        "end_pair": _pair_list(equality["end_pair"]),
        "path": [
            {
                "row": int(step["row"]),
                "next_pair": _pair_list(step["next_pair"]),
            }
            for step in equality["path"]
        ],
        "path_length": int(family["path_length"]),
        "holds": True,
    }


def _self_edge_instance(
    *,
    lemma_id: str,
    template: dict[str, Any],
    family: dict[str, Any],
    rows: Sequence[SelectedRow],
    order: Sequence[int],
    edge: StrictInequality,
    direct_conditions: dict[str, Any],
) -> dict[str, Any]:
    return {
        "lemma_id": lemma_id,
        "template_id": str(template["template_id"]),
        "template_key": str(template["template_key"]),
        "family_id": str(family["family_id"]),
        "assignment_count": int(family["assignment_count"]),
        "orbit_size": int(family["orbit_size"]),
        "core_selected_rows": _rows_to_json(rows),
        "strict_inequality": _edge_to_json(edge),
        "direct_conditions": direct_conditions,
        "simple_filter_violations": _simple_filter_violations(rows, order),
    }


def _strict_cycle_instance(
    template: dict[str, Any],
    family: dict[str, Any],
    order: Sequence[int],
    lemma_id: str,
) -> dict[str, Any]:
    rows = parse_selected_rows(family["core_selected_rows"])
    replay = replay_vertex_circle_quotient(int(template.get("n", 9)), order, rows)
    return {
        "lemma_id": lemma_id,
        "template_id": str(template["template_id"]),
        "template_key": str(template["template_key"]),
        "family_id": str(family["family_id"]),
        "assignment_count": int(family["assignment_count"]),
        "orbit_size": int(family["orbit_size"]),
        "core_selected_rows": _rows_to_json(rows),
        "cycle_steps": family["cycle_steps"],
        "replay_status": replay.status,
        "cycle_edges": [_edge_to_json(edge) for edge in replay.cycle_edges],
        "simple_filter_violations": _simple_filter_violations(rows, order),
    }


def _lemma_summary(lemma_id: str, instances: Sequence[dict[str, Any]]) -> dict[str, Any]:
    family_ids = sorted({str(instance["family_id"]) for instance in instances})
    assignments_by_family: dict[str, int] = {}
    templates_by_family: dict[str, str] = {}
    for instance in instances:
        family_id = str(instance["family_id"])
        assignments_by_family[family_id] = int(instance["assignment_count"])
        templates_by_family[family_id] = str(instance["template_id"])
    return {
        "lemma_id": lemma_id,
        "review_status": "review_pending",
        "instance_count": len(instances),
        "family_ids": family_ids,
        "template_ids": sorted({templates_by_family[family] for family in family_ids}),
        "covered_assignment_count": sum(assignments_by_family.values()),
        "instances": list(instances),
    }


def _coverage_summary(
    lemma_instances: dict[str, Sequence[dict[str, Any]]],
    source_family_assignments: dict[str, int],
) -> dict[str, Any]:
    family_to_assignments: dict[str, int] = {}
    family_to_lemmas: dict[str, list[str]] = defaultdict(list)
    for lemma_id, instances in lemma_instances.items():
        for instance in instances:
            family_id = str(instance["family_id"])
            family_to_assignments[family_id] = int(instance["assignment_count"])
            if lemma_id not in family_to_lemmas[family_id]:
                family_to_lemmas[family_id].append(lemma_id)
    uncovered_family_ids = sorted(
        set(source_family_assignments) - set(family_to_assignments)
    )
    return {
        "source_family_count": len(source_family_assignments),
        "source_assignment_count": sum(source_family_assignments.values()),
        "covered_family_count": len(family_to_assignments),
        "covered_family_ids": sorted(family_to_assignments),
        "covered_assignment_count": sum(family_to_assignments.values()),
        "uncovered_family_count": len(uncovered_family_ids),
        "uncovered_family_ids": uncovered_family_ids,
        "uncovered_assignment_count": sum(
            source_family_assignments[family_id] for family_id in uncovered_family_ids
        ),
        "family_to_lemmas": {
            family_id: sorted(lemmas)
            for family_id, lemmas in sorted(family_to_lemmas.items())
        },
    }


def _rows_to_json(rows: Sequence[SelectedRow]) -> list[list[int]]:
    return [[row.center, *row.witnesses] for row in rows]


def _edge_to_json(edge: StrictInequality) -> dict[str, Any]:
    return {
        "row": edge.row,
        "witness_order": list(edge.witness_order),
        "outer_interval": list(edge.outer_interval),
        "inner_interval": list(edge.inner_interval),
        "outer_pair": list(edge.outer_pair),
        "inner_pair": list(edge.inner_pair),
        "outer_class": list(edge.outer_class),
        "inner_class": list(edge.inner_class),
    }


def _pair_list(raw_pair: Any) -> list[int]:
    if not isinstance(raw_pair, Sequence) or isinstance(raw_pair, str):
        raise ValueError(f"expected pair sequence, got {raw_pair!r}")
    values = [int(value) for value in raw_pair]
    if len(values) != 2:
        raise ValueError(f"expected pair length 2, got {raw_pair!r}")
    return sorted(values)


def _simple_filter_violations(
    rows: Sequence[SelectedRow],
    order: Sequence[int],
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for left_index, left in enumerate(rows):
        for right in rows[left_index + 1 :]:
            shared = sorted(set(left.witnesses) & set(right.witnesses))
            source = normalize_chord(left.center, right.center)
            if len(shared) > 2:
                violations.append(
                    {
                        "kind": "two_circle_cap",
                        "source_pair": list(source),
                        "shared_witnesses": shared,
                    }
                )
            elif len(shared) == 2:
                target = normalize_chord(shared[0], shared[1])
                if not chords_cross_in_order(source, target, order):
                    violations.append(
                        {
                            "kind": "crossing_bisector_order",
                            "source_pair": list(source),
                            "shared_witnesses": shared,
                        }
                    )
    return violations
