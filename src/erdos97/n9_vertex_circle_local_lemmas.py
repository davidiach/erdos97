"""Scan n=9 vertex-circle packets for reusable local lemma shapes.

This module is proof-mining scaffolding.  It does not prove the full n=9 case,
does not claim a counterexample, and does not promote the review-pending
vertex-circle checker.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping, Sequence

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
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_local_lemmas.py",
    "command": "python scripts/check_n9_vertex_circle_local_lemmas.py --assert-expected --write",
}

SHARED_ENDPOINT_LEMMA = "shared_endpoint_nested_self_edge"
NESTED_SPOKE_LEMMA = "nested_spoke_quotient_self_edge"
T03_SELECTED_PATH_SELF_EDGE = "t03_selected_path_self_edge"
T04_SELECTED_PATH_SELF_EDGE = "t04_selected_path_self_edge"
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
    T04_SELECTED_PATH_SELF_EDGE: {
        "family_ids": ["F13"],
        "instance_count": 1,
        "covered_assignment_count": 2,
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
EXPECTED_FOCUSED_NOTE_CROSSCHECK = (
    {
        "lemma_id": NESTED_SPOKE_LEMMA,
        "template_id": "T01",
        "family_ids": ["F09"],
        "proof_note_path": "docs/n9-vertex-circle-t01-self-edge-lemma.md",
        "source_kind": "focused_packet",
        "crosscheck_mode": "alternate_self_edge_certificate",
        "packet_key": "T01",
        "packet_path": (
            "data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json"
        ),
    },
    {
        "lemma_id": NESTED_SPOKE_LEMMA,
        "template_id": "T05",
        "family_ids": ["F10"],
        "proof_note_path": "docs/n9-vertex-circle-t05-self-edge-lemma.md",
        "source_kind": "focused_packet",
        "crosscheck_mode": "alternate_self_edge_certificate",
        "packet_key": "T05",
        "packet_path": (
            "data/certificates/n9_vertex_circle_t05_self_edge_lemma_packet.json"
        ),
    },
    {
        "lemma_id": NESTED_SPOKE_LEMMA,
        "template_id": "T06",
        "family_ids": ["F11"],
        "proof_note_path": "docs/n9-vertex-circle-t06-self-edge-lemma.md",
        "source_kind": "focused_packet",
        "crosscheck_mode": "alternate_self_edge_certificate",
        "aggregate_outer_pair_match_required": False,
        "packet_key": "T06",
        "packet_path": (
            "data/certificates/n9_vertex_circle_t06_self_edge_lemma_packet.json"
        ),
    },
    {
        "lemma_id": NESTED_SPOKE_LEMMA,
        "template_id": "T07",
        "family_ids": ["F06"],
        "proof_note_path": "docs/n9-vertex-circle-t07-self-edge-lemma.md",
        "source_kind": "focused_packet",
        "crosscheck_mode": "alternate_self_edge_certificate",
        "packet_key": "T07",
        "packet_path": (
            "data/certificates/n9_vertex_circle_t07_self_edge_lemma_packet.json"
        ),
    },
    {
        "lemma_id": NESTED_SPOKE_LEMMA,
        "template_id": "T08",
        "family_ids": ["F02"],
        "proof_note_path": "docs/n9-vertex-circle-t08-self-edge-lemma.md",
        "source_kind": "focused_packet",
        "crosscheck_mode": "alternate_self_edge_certificate",
        "packet_key": "T08",
        "packet_path": (
            "data/certificates/n9_vertex_circle_t08_self_edge_lemma_packet.json"
        ),
    },
    {
        "lemma_id": NESTED_SPOKE_LEMMA,
        "template_id": "T09",
        "family_ids": ["F03"],
        "proof_note_path": "docs/n9-vertex-circle-t09-self-edge-lemma.md",
        "source_kind": "focused_packet",
        "crosscheck_mode": "alternate_self_edge_certificate",
        "packet_key": "T09",
        "packet_path": (
            "data/certificates/n9_vertex_circle_t09_self_edge_lemma_packet.json"
        ),
    },
    {
        "lemma_id": SHARED_ENDPOINT_LEMMA,
        "template_id": "T02",
        "family_ids": ["F01", "F04", "F08", "F14"],
        "proof_note_path": "docs/n9-vertex-circle-t02-self-edge-lemma.md",
        "source_kind": "focused_packet",
        "packet_key": "T02",
        "packet_path": (
            "data/certificates/n9_vertex_circle_t02_self_edge_lemma_packet.json"
        ),
    },
    {
        "lemma_id": T03_SELECTED_PATH_SELF_EDGE,
        "template_id": "T03",
        "family_ids": ["F05", "F15"],
        "proof_note_path": "docs/n9-vertex-circle-t03-self-edge-lemma.md",
        "source_kind": "focused_packet",
        "packet_key": "T03",
        "packet_path": (
            "data/certificates/n9_vertex_circle_t03_self_edge_lemma_packet.json"
        ),
    },
    {
        "lemma_id": T04_SELECTED_PATH_SELF_EDGE,
        "template_id": "T04",
        "family_ids": ["F13"],
        "proof_note_path": "docs/n9-vertex-circle-t04-self-edge-lemma.md",
        "source_kind": "focused_packet",
        "packet_key": "T04",
        "packet_path": (
            "data/certificates/n9_vertex_circle_t04_self_edge_lemma_packet.json"
        ),
    },
    {
        "lemma_id": T10_STRICT_CYCLE_LEMMA,
        "template_id": "T10",
        "family_ids": ["F12"],
        "proof_note_path": "docs/n9-vertex-circle-t10-strict-cycle-lemma.md",
        "source_kind": "focused_packet",
        "packet_key": "T10",
        "packet_path": (
            "data/certificates/n9_vertex_circle_t10_strict_cycle_lemma_packet.json"
        ),
    },
    {
        "lemma_id": T11_STRICT_CYCLE_LEMMA,
        "template_id": "T11",
        "family_ids": ["F07"],
        "proof_note_path": "docs/n9-vertex-circle-t11-strict-cycle-lemma.md",
        "source_kind": "focused_packet",
        "packet_key": "T11",
        "packet_path": (
            "data/certificates/n9_vertex_circle_t11_strict_cycle_lemma_packet.json"
        ),
    },
    {
        "lemma_id": T12_STRICT_CYCLE_LEMMA,
        "template_id": "T12",
        "family_ids": ["F16"],
        "proof_note_path": "docs/n9-vertex-circle-t12-strict-cycle-lemma.md",
        "source_kind": "focused_packet",
        "packet_key": "T12",
        "packet_path": (
            "data/certificates/n9_vertex_circle_t12_strict_cycle_lemma_packet.json"
        ),
    },
)


def local_lemma_scan_payload(
    self_edge_packet: dict[str, Any],
    strict_cycle_packet: dict[str, Any],
    focused_packets: Mapping[str, dict[str, Any]] | None = None,
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
    t04_selected_path: list[dict[str, Any]] = []
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
            selected_path_lemma_id = _selected_path_self_edge_lemma_id(
                template,
                family,
                edge,
            )
            if selected_path_lemma_id is not None:
                selected_path_instances = {
                    T03_SELECTED_PATH_SELF_EDGE: t03_selected_path,
                    T04_SELECTED_PATH_SELF_EDGE: t04_selected_path,
                }
                selected_path_instances[selected_path_lemma_id].append(
                    _self_edge_instance(
                        lemma_id=selected_path_lemma_id,
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
        T04_SELECTED_PATH_SELF_EDGE: t04_selected_path,
        **strict_cycle_instances,
    }
    focused_note_crosscheck = _focused_note_crosscheck(
        lemma_instances,
        self_edge_packet,
        focused_packets or {},
    )

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
            _lemma_summary(T04_SELECTED_PATH_SELF_EDGE, t04_selected_path),
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
        "focused_note_crosscheck": focused_note_crosscheck,
        "interpretation": (
            "The listed local shapes are reusable obstruction candidates: each "
            "one produces either a reflexive strict edge or a directed strict "
            "cycle after selected-distance quotienting.  The scan only uses "
            "stored template-packet local cores and does not enumerate all n=9 "
            "selected-witness assignments."
        ),
        "provenance": dict(PROVENANCE),
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


def _focused_note_crosscheck(
    lemma_instances: Mapping[str, Sequence[dict[str, Any]]],
    self_edge_packet: Mapping[str, Any],
    focused_packets: Mapping[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Cross-check aggregate records against focused proof-note packets."""

    records = []
    for expected in EXPECTED_FOCUSED_NOTE_CROSSCHECK:
        lemma_id = str(expected["lemma_id"])
        family_ids = list(expected["family_ids"])
        aggregate_instances = _instances_by_family(
            lemma_instances.get(lemma_id, ()),
            family_ids,
        )
        if expected["source_kind"] == "focused_packet":
            packet_key = str(expected["packet_key"])
            focused_packet = focused_packets.get(packet_key)
            if focused_packet is None:
                records.append(
                    {
                        **expected,
                        "check_status": "not_loaded",
                        "families_checked": [],
                        "covered_assignment_count": 0,
                        "note": (
                            "Focused packet was not supplied; aggregate scan "
                            "still derives this lemma from the template packets."
                        ),
                    }
                )
                continue
            check_summary = _check_focused_packet(
                lemma_id,
                expected,
                aggregate_instances,
                focused_packet,
            )
        else:
            check_summary = _check_t04_template_record(
                expected,
                aggregate_instances,
                self_edge_packet,
            )
        records.append(
            {
                **expected,
                "check_status": "checked",
                **check_summary,
            }
        )
    return records


def _instances_by_family(
    instances: Sequence[dict[str, Any]],
    family_ids: Sequence[str],
) -> dict[str, dict[str, Any]]:
    by_family = {
        str(instance["family_id"]): instance
        for instance in instances
        if isinstance(instance, dict) and "family_id" in instance
    }
    missing = [family_id for family_id in family_ids if family_id not in by_family]
    if missing:
        raise AssertionError(f"aggregate scan missing focused families: {missing!r}")
    return {family_id: by_family[family_id] for family_id in family_ids}


def _check_focused_packet(
    lemma_id: str,
    expected: Mapping[str, Any],
    aggregate_instances: Mapping[str, dict[str, Any]],
    focused_packet: Mapping[str, Any],
) -> dict[str, Any]:
    template_id = str(expected["template_id"])
    if focused_packet.get("template_id") != template_id:
        raise AssertionError(f"{template_id} focused packet template mismatch")
    if focused_packet.get("status") != "REVIEW_PENDING_DIAGNOSTIC_ONLY":
        raise AssertionError(f"{template_id} focused packet status mismatch")
    if focused_packet.get("trust") != TRUST:
        raise AssertionError(f"{template_id} focused packet trust mismatch")
    claim_scope = str(focused_packet.get("claim_scope", ""))
    for forbidden in ("proof of n=9", "counterexample", "global status update"):
        if f"not a {forbidden}" not in claim_scope and f"not an {forbidden}" not in claim_scope:
            raise AssertionError(
                f"{template_id} focused packet must explicitly reject {forbidden!r}"
            )

    family_packets = _focused_family_packets(template_id, focused_packet)
    packets_by_family = {
        str(packet["family_id"]): packet
        for packet in family_packets
        if isinstance(packet, dict) and "family_id" in packet
    }

    checked = []
    crosscheck_mode = str(expected.get("crosscheck_mode", "same_instance"))
    for family_id, aggregate in aggregate_instances.items():
        packet = packets_by_family.get(family_id)
        if packet is None:
            raise AssertionError(f"{template_id} focused packet missing {family_id}")
        _assert_family_common_fields(template_id, family_id, aggregate, packet)
        if crosscheck_mode == "alternate_self_edge_certificate":
            _assert_alternate_self_edge_certificate_match(
                template_id,
                family_id,
                aggregate,
                packet,
                require_aggregate_outer_match=bool(
                    expected.get("aggregate_outer_pair_match_required", True)
                ),
            )
        elif lemma_id in {
            SHARED_ENDPOINT_LEMMA,
            T03_SELECTED_PATH_SELF_EDGE,
            T04_SELECTED_PATH_SELF_EDGE,
        }:
            _assert_self_edge_family_match(template_id, family_id, aggregate, packet)
        else:
            _assert_strict_cycle_family_match(template_id, family_id, aggregate, packet)
        checked.append(
            {
                "family_id": family_id,
                "assignment_count": int(aggregate["assignment_count"]),
                "orbit_size": int(aggregate["orbit_size"]),
            }
        )

    return {
        "families_checked": checked,
        "covered_assignment_count": sum(item["assignment_count"] for item in checked),
        "interpretation": (
            _focused_packet_interpretation(
                crosscheck_mode,
                require_aggregate_outer_match=bool(
                    expected.get("aggregate_outer_pair_match_required", True)
                ),
            )
        ),
    }


def _focused_family_packets(
    template_id: str,
    focused_packet: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    family_packets = focused_packet.get("family_packets")
    if isinstance(family_packets, list):
        return [packet for packet in family_packets if isinstance(packet, Mapping)]
    if "family_id" in focused_packet:
        return [focused_packet]
    raise AssertionError(f"{template_id} focused packet must contain family packet data")


def _check_t04_template_record(
    expected: Mapping[str, Any],
    aggregate_instances: Mapping[str, dict[str, Any]],
    self_edge_packet: Mapping[str, Any],
) -> dict[str, Any]:
    family_id = "F13"
    aggregate = aggregate_instances[family_id]
    family = _template_family_record(
        self_edge_packet,
        template_id=str(expected["template_id"]),
        family_id=family_id,
    )
    _assert_family_common_fields(str(expected["template_id"]), family_id, aggregate, family)
    _assert_self_edge_family_match(str(expected["template_id"]), family_id, aggregate, family)
    return {
        "families_checked": [
            {
                "family_id": family_id,
                "assignment_count": int(aggregate["assignment_count"]),
                "orbit_size": int(aggregate["orbit_size"]),
            }
        ],
        "covered_assignment_count": int(aggregate["assignment_count"]),
        "interpretation": (
            "The T04 proof note is backed directly by the self-edge template "
            "packet; the aggregate scan matches that source family record."
        ),
    }


def _template_family_record(
    packet: Mapping[str, Any],
    *,
    template_id: str,
    family_id: str,
) -> Mapping[str, Any]:
    templates = packet.get("templates")
    if not isinstance(templates, list):
        raise AssertionError("self-edge packet must contain templates")
    for template in templates:
        if not isinstance(template, dict) or template.get("template_id") != template_id:
            continue
        records = template.get("family_records")
        if not isinstance(records, list):
            raise AssertionError(f"{template_id} must contain family_records")
        for family in records:
            if isinstance(family, dict) and family.get("family_id") == family_id:
                return family
    raise AssertionError(f"missing {template_id}/{family_id} family record")


def _assert_family_common_fields(
    template_id: str,
    family_id: str,
    aggregate: Mapping[str, Any],
    packet: Mapping[str, Any],
) -> None:
    if aggregate.get("template_id") != template_id:
        raise AssertionError(f"{family_id} aggregate template mismatch")
    if "template_id" in packet and packet.get("template_id") != template_id:
        raise AssertionError(f"{family_id} focused packet template mismatch")
    for key in ("assignment_count", "orbit_size", "core_selected_rows"):
        if aggregate.get(key) != packet.get(key):
            raise AssertionError(f"{family_id} focused packet {key} mismatch")


def _assert_self_edge_family_match(
    template_id: str,
    family_id: str,
    aggregate: Mapping[str, Any],
    packet: Mapping[str, Any],
) -> None:
    aggregate_strict = aggregate.get("strict_inequality")
    packet_strict = packet.get("strict_inequality")
    if not isinstance(aggregate_strict, Mapping) or not isinstance(packet_strict, Mapping):
        raise AssertionError(f"{family_id} focused packet strict_inequality mismatch")
    for key in (
        "row",
        "witness_order",
        "outer_interval",
        "inner_interval",
        "outer_pair",
        "inner_pair",
        "outer_span",
        "inner_span",
    ):
        if aggregate_strict.get(key) != packet_strict.get(key):
            raise AssertionError(f"{family_id} focused packet strict_inequality mismatch")
    if aggregate_strict.get("outer_class") != aggregate_strict.get("inner_class"):
        raise AssertionError(f"{family_id} aggregate strict edge must be reflexive")
    if packet_strict.get("outer_class") != packet_strict.get("inner_class"):
        raise AssertionError(f"{family_id} focused packet strict edge must be reflexive")
    equality = packet.get("distance_equality")
    if aggregate.get("distance_equality") != equality:
        raise AssertionError(f"{family_id} focused packet distance_equality mismatch")
    if aggregate.get("direct_conditions", {}).get("holds") is not True:
        variant = aggregate.get("direct_conditions", {}).get("variant")
        if template_id in {"T03", "T04"} or variant == "selected_path_self_edge":
            raise AssertionError(f"{family_id} selected-path conditions must hold")


def _assert_alternate_self_edge_certificate_match(
    template_id: str,
    family_id: str,
    aggregate: Mapping[str, Any],
    packet: Mapping[str, Any],
    *,
    require_aggregate_outer_match: bool,
) -> None:
    aggregate_strict = aggregate.get("strict_inequality")
    packet_strict = packet.get("strict_inequality")
    equality = packet.get("distance_equality")
    if not isinstance(aggregate_strict, Mapping) or not isinstance(packet_strict, Mapping):
        raise AssertionError(f"{family_id} focused packet strict_inequality mismatch")
    if not isinstance(equality, Mapping):
        raise AssertionError(f"{family_id} focused packet distance_equality mismatch")
    if packet_strict.get("outer_class") != packet_strict.get("inner_class"):
        raise AssertionError(f"{family_id} focused packet strict edge must be reflexive")
    if aggregate_strict.get("outer_class") != aggregate_strict.get("inner_class"):
        raise AssertionError(f"{family_id} aggregate strict edge must be reflexive")
    if packet_strict.get("outer_pair") != equality.get("start_pair"):
        raise AssertionError(f"{family_id} focused strict/equality start mismatch")
    if packet_strict.get("inner_pair") != equality.get("end_pair"):
        raise AssertionError(f"{family_id} focused strict/equality end mismatch")
    _assert_packet_equality_path(family_id, packet, equality)
    if require_aggregate_outer_match:
        if aggregate_strict.get("outer_pair") != packet_strict.get("outer_pair"):
            raise AssertionError(f"{family_id} alternate certificate outer-pair mismatch")
        if aggregate.get("distance_equality", {}).get("start_pair") != equality.get("start_pair"):
            raise AssertionError(f"{family_id} alternate certificate equality-start mismatch")

    replay = packet.get("replay")
    if not isinstance(replay, Mapping) or replay.get("status") != "self_edge":
        raise AssertionError(f"{family_id} focused packet replay status mismatch")
    if replay.get("selected_row_count") != packet.get("core_size"):
        raise AssertionError(f"{family_id} focused packet replay row count mismatch")
    primary = replay.get("primary_self_edge_conflict")
    if not isinstance(primary, Mapping):
        raise AssertionError(f"{family_id} focused packet primary conflict mismatch")
    for key in (
        "row",
        "witness_order",
        "outer_interval",
        "inner_interval",
        "outer_pair",
        "inner_pair",
    ):
        if primary.get(key) != packet_strict.get(key):
            raise AssertionError(f"{family_id} focused packet primary conflict mismatch")
    if template_id not in {"T01", "T05", "T06", "T07", "T08", "T09"}:
        raise AssertionError("alternate self-edge certificate mode is currently T01/T05/T06/T07/T08/T09-only")


def _assert_packet_equality_path(
    family_id: str,
    packet: Mapping[str, Any],
    equality: Mapping[str, Any],
) -> None:
    rows = packet.get("core_selected_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, str):
        raise AssertionError(f"{family_id} focused packet rows mismatch")
    row_map: dict[int, set[int]] = {}
    for raw_row in rows:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, str) or len(raw_row) != 5:
            raise AssertionError(f"{family_id} focused packet rows mismatch")
        center = int(raw_row[0])
        row_map[center] = {int(value) for value in raw_row[1:]}

    current = [int(value) for value in equality.get("start_pair", [])]
    steps = equality.get("path")
    if not isinstance(steps, Sequence) or isinstance(steps, str):
        raise AssertionError(f"{family_id} focused packet equality path mismatch")
    for step in steps:
        if not isinstance(step, Mapping):
            raise AssertionError(f"{family_id} focused packet equality path mismatch")
        row = int(step["row"])
        next_pair = [int(value) for value in step["next_pair"]]
        witnesses = row_map.get(row)
        if witnesses is None:
            raise AssertionError(f"{family_id} focused packet equality path row mismatch")
        if row not in current or row not in next_pair:
            raise AssertionError(f"{family_id} focused packet equality path step mismatch")
        left_other = next(value for value in current if value != row)
        right_other = next(value for value in next_pair if value != row)
        if left_other not in witnesses or right_other not in witnesses:
            raise AssertionError(f"{family_id} focused packet equality path witness mismatch")
        current = next_pair
    if current != equality.get("end_pair"):
        raise AssertionError(f"{family_id} focused packet equality path end mismatch")


def _focused_packet_interpretation(
    crosscheck_mode: str,
    *,
    require_aggregate_outer_match: bool,
) -> str:
    if crosscheck_mode == "alternate_self_edge_certificate":
        if not require_aggregate_outer_match:
            return (
                "Aggregate scan family rows match the focused packet, and the "
                "focused packet supplies a valid alternate reflexive self-edge "
                "certificate for the same family. The proof-facing strict edge "
                "and equality path are checked inside the focused packet; they "
                "are not required to share the aggregate nested-spoke strict "
                "edge endpoint. This remains a packet consistency check, not "
                "an independent n=9 completeness proof."
            )
        return (
            "Aggregate scan family rows match the focused packet, and the "
            "focused packet supplies a valid alternate reflexive self-edge "
            "certificate for the same family. The aggregate nested-spoke "
            "strict edge is not required to be the same strict edge as the "
            "proof-facing note; this remains a packet consistency check, not "
            "an independent n=9 completeness proof."
        )
    return (
        "Aggregate scan instance matches the focused packet used by the "
        "proof-facing note; this is a packet consistency check, not an "
        "independent n=9 completeness proof."
    )


def _assert_strict_cycle_family_match(
    template_id: str,
    family_id: str,
    aggregate: Mapping[str, Any],
    packet: Mapping[str, Any],
) -> None:
    cycle_steps = packet.get("cycle_steps")
    if not isinstance(cycle_steps, list):
        raise AssertionError(f"{family_id} focused packet cycle_steps mismatch")
    if aggregate.get("cycle_steps") != cycle_steps:
        raise AssertionError(f"{family_id} focused packet cycle_steps mismatch")
    if aggregate.get("cycle_length") != packet.get("cycle_length"):
        raise AssertionError(f"{family_id} focused packet cycle_length mismatch")
    if aggregate.get("replay_status") != "strict_cycle":
        raise AssertionError(f"{family_id} aggregate replay_status mismatch")
    replay = packet.get("replay")
    if not isinstance(replay, Mapping) or replay.get("status") != "strict_cycle":
        raise AssertionError(f"{family_id} focused packet replay status mismatch")
    if packet.get("cycle_length") != len(cycle_steps):
        raise AssertionError(f"{family_id} focused packet cycle length mismatch")


def assert_expected_local_lemma_scan(payload: dict[str, Any]) -> None:
    """Assert the current expected local-lemma scan counts."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
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
    if coverage.get("covered_family_count") != 16:
        raise AssertionError("covered_family_count mismatch")
    if coverage.get("covered_assignment_count") != 184:
        raise AssertionError("covered_assignment_count mismatch")
    if coverage.get("uncovered_family_count") != 0:
        raise AssertionError("uncovered_family_count mismatch")
    if coverage.get("uncovered_assignment_count") != 0:
        raise AssertionError("uncovered_assignment_count mismatch")
    if coverage.get("uncovered_family_ids") != []:
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
        "F13",
        "F14",
        "F15",
        "F16",
    ]:
        raise AssertionError("covered_family_ids mismatch")

    crosscheck = payload.get("focused_note_crosscheck")
    if not isinstance(crosscheck, list):
        raise AssertionError("focused_note_crosscheck must be a list")
    expected_by_key = {
        (str(item["lemma_id"]), str(item["template_id"])): item
        for item in EXPECTED_FOCUSED_NOTE_CROSSCHECK
    }
    by_key = {
        (str(item.get("lemma_id")), str(item.get("template_id"))): item
        for item in crosscheck
        if isinstance(item, dict) and "lemma_id" in item and "template_id" in item
    }
    if set(by_key) != set(expected_by_key):
        raise AssertionError(f"focused-note keys mismatch: {sorted(by_key)!r}")
    for key_tuple, expected in expected_by_key.items():
        item = by_key[key_tuple]
        label = "/".join(key_tuple)
        for key in (
            "lemma_id",
            "template_id",
            "family_ids",
            "proof_note_path",
            "source_kind",
            "packet_path",
        ):
            if item.get(key) != expected[key]:
                raise AssertionError(
                    f"{label} focused-note {key} mismatch: "
                    f"expected {expected[key]!r}, got {item.get(key)!r}"
                )
        if item.get("check_status") != "checked":
            raise AssertionError(f"{label} focused-note crosscheck was not checked")
        checked_families = [
            str(checked.get("family_id"))
            for checked in item.get("families_checked", [])
            if isinstance(checked, dict)
        ]
        if checked_families != expected["family_ids"]:
            raise AssertionError(f"{label} checked family ids mismatch")


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


def _selected_path_self_edge_lemma_id(
    template: dict[str, Any],
    family: dict[str, Any],
    edge: StrictInequality,
) -> str | None:
    """Return the selected-path self-edge lemma id for checked packet records."""

    template_to_lemma = {
        "T03": T03_SELECTED_PATH_SELF_EDGE,
        "T04": T04_SELECTED_PATH_SELF_EDGE,
    }
    lemma_id = template_to_lemma.get(str(template.get("template_id")))
    if lemma_id is None:
        return None
    equality = family.get("distance_equality")
    if not isinstance(equality, dict):
        return None
    if (
        edge.outer_class == edge.inner_class
        and _pair_list(edge.outer_pair) == _pair_list(equality.get("start_pair"))
        and _pair_list(edge.inner_pair) == _pair_list(equality.get("end_pair"))
    ):
        return lemma_id
    return None


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
        "distance_equality": family.get("distance_equality"),
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
    cycle_steps = family["cycle_steps"]
    return {
        "lemma_id": lemma_id,
        "template_id": str(template["template_id"]),
        "template_key": str(template["template_key"]),
        "family_id": str(family["family_id"]),
        "assignment_count": int(family["assignment_count"]),
        "orbit_size": int(family["orbit_size"]),
        "core_selected_rows": _rows_to_json(rows),
        "cycle_length": int(family.get("cycle_length", len(cycle_steps))),
        "cycle_steps": cycle_steps,
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
    outer_span = int(edge.outer_interval[1]) - int(edge.outer_interval[0])
    inner_span = int(edge.inner_interval[1]) - int(edge.inner_interval[0])
    return {
        "row": edge.row,
        "witness_order": list(edge.witness_order),
        "outer_interval": list(edge.outer_interval),
        "inner_interval": list(edge.inner_interval),
        "outer_pair": list(edge.outer_pair),
        "inner_pair": list(edge.inner_pair),
        "outer_class": list(edge.outer_class),
        "inner_class": list(edge.inner_class),
        "outer_span": outer_span,
        "inner_span": inner_span,
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
