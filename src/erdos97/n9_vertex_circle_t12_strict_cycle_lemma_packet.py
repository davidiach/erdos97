"""Build a focused T12 n=9 strict-cycle local lemma packet.

This module is proof-mining scaffolding. It does not prove the full n=9 case,
does not claim a counterexample, and does not promote the review-pending n=9
checker.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.n9_vertex_circle_self_edge_path_join import validate_equality_path
from erdos97.n9_vertex_circle_strict_cycle_template_packet import (
    SCHEMA as STRICT_CYCLE_TEMPLATE_PACKET_SCHEMA,
)
from erdos97.n9_vertex_circle_template_lemma_catalog import (
    SCHEMA as TEMPLATE_LEMMA_CATALOG_SCHEMA,
)
from erdos97.vertex_circle_quotient_replay import (
    pair,
    parse_selected_rows,
    replay_vertex_circle_quotient,
    result_to_json,
)

SCHEMA = "erdos97.n9_vertex_circle_t12_strict_cycle_lemma_packet.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Focused T12/F16 strict-cycle local lemma packet for two n=9 "
    "frontier assignments; proof-mining scaffolding only, not a proof of n=9, "
    "not a counterexample, not an independent review of the exhaustive checker, "
    "and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py",
    "command": (
        "python scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py "
        "--assert-expected --write"
    ),
}

EXPECTED_TEMPLATE_ID = "T12"
EXPECTED_TEMPLATE_KEY = (
    "strict_cycle|rows=6|strict_edges=54|cycle=3|spans=3:1x3"
)
EXPECTED_FAMILY_IDS = ("F16",)
EXPECTED_ASSIGNMENT_IDS = ("A082", "A152")
EXPECTED_ASSIGNMENT_COUNT = 2
EXPECTED_FAMILY_COUNT = 1
EXPECTED_ORBIT_SIZE_SUM = 2
EXPECTED_CORE_SIZE = 6
EXPECTED_CYCLE_LENGTH = 3
EXPECTED_STRICT_EDGE_COUNT = 54
EXPECTED_SELF_EDGE_CONFLICT_COUNT = 0
EXPECTED_CYCLE_EDGE_COUNT = 3
EXPECTED_FAMILY_ASSIGNMENT_COUNTS = {"F16": 2}
EXPECTED_FAMILY_ORBIT_SIZES = {"F16": 2}
EXPECTED_CYCLE_LENGTH_COUNTS = {"3": 2}
EXPECTED_CONNECTOR_PATH_LENGTH_COUNTS = {"1": 4, "2": 2}
EXPECTED_SPAN_SIGNATURE_COUNTS = {"3:1,3:1,3:1": 2}
EXPECTED_CYCLE_SPAN_COUNTS = [
    {"count": 3, "inner_span": 1, "outer_span": 3},
]
EXPECTED_CORE_SELECTED_ROWS = (
    (0, 1, 3, 6, 7),
    (1, 2, 4, 7, 8),
    (2, 0, 3, 5, 8),
    (3, 0, 1, 4, 6),
    (4, 1, 2, 5, 7),
    (8, 0, 2, 5, 6),
)
EXPECTED_CYCLE_STEPS: list[dict[str, Any]] = [
    {
        "equality_to_next_outer_pair": {
            "end_pair": [2, 8],
            "path": [{"next_pair": [2, 8], "row": 8}],
            "start_pair": [0, 8],
        },
        "strict_inequality": {
            "inner_class": [0, 2],
            "inner_interval": [2, 3],
            "inner_pair": [0, 8],
            "inner_span": 1,
            "outer_class": [0, 1],
            "outer_interval": [0, 3],
            "outer_pair": [0, 3],
            "outer_span": 3,
            "row": 2,
            "witness_order": [3, 5, 8, 0],
        },
    },
    {
        "equality_to_next_outer_pair": {
            "end_pair": [1, 7],
            "path": [
                {"next_pair": [1, 4], "row": 4},
                {"next_pair": [1, 7], "row": 1},
            ],
            "start_pair": [2, 4],
        },
        "strict_inequality": {
            "inner_class": [1, 2],
            "inner_interval": [0, 1],
            "inner_pair": [2, 4],
            "inner_span": 1,
            "outer_class": [0, 2],
            "outer_interval": [0, 3],
            "outer_pair": [2, 8],
            "outer_span": 3,
            "row": 1,
            "witness_order": [2, 4, 7, 8],
        },
    },
    {
        "equality_to_next_outer_pair": {
            "end_pair": [0, 3],
            "path": [{"next_pair": [0, 3], "row": 3}],
            "start_pair": [1, 3],
        },
        "strict_inequality": {
            "inner_class": [0, 1],
            "inner_interval": [0, 1],
            "inner_pair": [1, 3],
            "inner_span": 1,
            "outer_class": [1, 2],
            "outer_interval": [0, 3],
            "outer_pair": [1, 7],
            "outer_span": 3,
            "row": 0,
            "witness_order": [1, 3, 6, 7],
        },
    },
]


def _template_record(packet: dict[str, Any]) -> dict[str, Any]:
    templates = packet.get("templates")
    if not isinstance(templates, list):
        raise ValueError("strict-cycle template packet must contain templates")
    for template in templates:
        if isinstance(template, dict) and template.get("template_id") == EXPECTED_TEMPLATE_ID:
            return template
    raise ValueError(f"missing template {EXPECTED_TEMPLATE_ID}")


def _family_records_by_id(template: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records = template.get("family_records")
    if not isinstance(records, list):
        raise ValueError(f"{EXPECTED_TEMPLATE_ID} must contain family_records")
    by_id = {
        str(record["family_id"]): record
        for record in records
        if isinstance(record, dict) and "family_id" in record
    }
    missing = [family_id for family_id in EXPECTED_FAMILY_IDS if family_id not in by_id]
    if missing:
        raise ValueError(f"missing T12 families: {missing!r}")
    return {family_id: by_id[family_id] for family_id in EXPECTED_FAMILY_IDS}


def _catalog_record(catalog: dict[str, Any]) -> dict[str, Any]:
    templates = catalog.get("templates")
    if not isinstance(templates, list):
        raise ValueError("template lemma catalog must contain templates")
    for record in templates:
        if isinstance(record, dict) and record.get("template_id") == EXPECTED_TEMPLATE_ID:
            return record
    raise ValueError(f"catalog missing template {EXPECTED_TEMPLATE_ID}")


def _normalize_rows(rows: Sequence[Sequence[int]]) -> list[list[int]]:
    return [[int(value) for value in row] for row in rows]


def equality_chain(equality: Mapping[str, Any]) -> list[list[int]]:
    """Return the pair chain traversed by a selected-distance equality path."""

    chain = [[int(value) for value in pair(*equality["start_pair"])]]
    for step in equality["path"]:
        chain.append([int(value) for value in pair(*step["next_pair"])])
    return chain


def equality_steps(equality: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return row-labelled equality steps for the local lemma packet."""

    current = [int(value) for value in pair(*equality["start_pair"])]
    steps = []
    for step in equality["path"]:
        next_pair = [int(value) for value in pair(*step["next_pair"])]
        steps.append(
            {
                "row": int(step["row"]),
                "left_pair": current,
                "right_pair": next_pair,
            }
        )
        current = next_pair
    return steps


def source_artifacts(
    strict_cycle_packet: dict[str, Any],
    template_catalog: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return embedded source-artifact metadata for the T12 packet."""

    return [
        {
            "path": "data/certificates/n9_vertex_circle_strict_cycle_template_packet.json",
            "role": "source T12/F16 strict-cycle template record",
            "schema": strict_cycle_packet.get("schema"),
            "status": strict_cycle_packet.get("status"),
            "trust": strict_cycle_packet.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_template_lemma_catalog.json",
            "role": "catalog crosswalk confirming T12 coverage and strict-cycle shape summary",
            "schema": template_catalog.get("schema"),
            "status": template_catalog.get("status"),
            "trust": template_catalog.get("trust"),
        },
    ]


def _source_template_summary(template: dict[str, Any]) -> dict[str, Any]:
    return {
        "template_id": str(template["template_id"]),
        "template_key": str(template["template_key"]),
        "status": str(template["status"]),
        "assignment_count": int(template["assignment_count"]),
        "assignment_ids": list(template["assignment_ids"]),
        "family_count": int(template["family_count"]),
        "families": list(template["families"]),
        "orbit_size_sum": int(template["orbit_size_sum"]),
        "core_size": int(template["core_size"]),
        "cycle_length": int(template["cycle_length"]),
        "strict_edge_count": int(template["strict_edge_count"]),
        "cycle_length_counts": template["cycle_length_counts"],
        "connector_path_length_counts": template["connector_path_length_counts"],
        "span_signature_counts": template["span_signature_counts"],
        "cycle_span_counts": template["cycle_span_counts"],
    }


def _family_source_summary(family: dict[str, Any]) -> dict[str, Any]:
    return {
        "family_id": str(family["family_id"]),
        "template_id": str(family["template_id"]),
        "status": str(family["status"]),
        "assignment_count": int(family["assignment_count"]),
        "orbit_size": int(family["orbit_size"]),
        "core_size": int(family["core_size"]),
        "cycle_length": int(family["cycle_length"]),
        "strict_edge_count": int(family["strict_edge_count"]),
        "span_signature": str(family["span_signature"]),
        "cycle_steps": family["cycle_steps"],
        "equality_chains": [
            equality_chain(step["equality_to_next_outer_pair"])
            for step in family["cycle_steps"]
        ],
    }


def _assert_cycle_steps(rows: Sequence[Sequence[int]], steps: Sequence[dict[str, Any]]) -> None:
    if len(steps) != EXPECTED_CYCLE_LENGTH:
        raise AssertionError("unexpected T12 cycle-step count")
    if list(steps) != EXPECTED_CYCLE_STEPS:
        raise AssertionError("unexpected T12 cycle steps")
    for index, step in enumerate(steps):
        edge = step["strict_inequality"]
        equality = step["equality_to_next_outer_pair"]
        next_edge = steps[(index + 1) % len(steps)]["strict_inequality"]
        if pair(*equality["start_pair"]) != pair(*edge["inner_pair"]):
            raise AssertionError("cycle equality must start at current inner pair")
        if pair(*equality["end_pair"]) != pair(*next_edge["outer_pair"]):
            raise AssertionError("cycle equality must end at next outer pair")
        validate_equality_path(rows, equality)


def _assert_source_records(
    template: dict[str, Any],
    family: dict[str, Any],
    catalog_record: dict[str, Any],
) -> None:
    if template["template_id"] != EXPECTED_TEMPLATE_ID:
        raise AssertionError("unexpected template id")
    if template["template_key"] != EXPECTED_TEMPLATE_KEY:
        raise AssertionError("unexpected T12 template key")
    if template["status"] != "strict_cycle":
        raise AssertionError("T12 must remain a strict-cycle template")
    if template["assignment_ids"] != list(EXPECTED_ASSIGNMENT_IDS):
        raise AssertionError("unexpected T12 assignment ids")
    if template["assignment_count"] != EXPECTED_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected T12 assignment count")
    if template["families"] != list(EXPECTED_FAMILY_IDS):
        raise AssertionError("unexpected T12 family list")
    if template["family_count"] != EXPECTED_FAMILY_COUNT:
        raise AssertionError("unexpected T12 family count")
    if template["orbit_size_sum"] != EXPECTED_ORBIT_SIZE_SUM:
        raise AssertionError("unexpected T12 orbit-size sum")
    if template["core_size"] != EXPECTED_CORE_SIZE:
        raise AssertionError("unexpected T12 core size")
    if template["cycle_length"] != EXPECTED_CYCLE_LENGTH:
        raise AssertionError("unexpected T12 cycle length")
    if template["strict_edge_count"] != EXPECTED_STRICT_EDGE_COUNT:
        raise AssertionError("unexpected T12 strict-edge count")
    if template["cycle_length_counts"] != EXPECTED_CYCLE_LENGTH_COUNTS:
        raise AssertionError("unexpected T12 cycle-length counts")
    if template["connector_path_length_counts"] != EXPECTED_CONNECTOR_PATH_LENGTH_COUNTS:
        raise AssertionError("unexpected T12 connector path-length counts")
    if template["span_signature_counts"] != EXPECTED_SPAN_SIGNATURE_COUNTS:
        raise AssertionError("unexpected T12 span-signature counts")
    if template["cycle_span_counts"] != EXPECTED_CYCLE_SPAN_COUNTS:
        raise AssertionError("unexpected T12 cycle-span counts")

    rows = _normalize_rows(family["core_selected_rows"])
    if family["family_id"] != "F16":
        raise AssertionError("unexpected family id")
    if family["template_id"] != EXPECTED_TEMPLATE_ID:
        raise AssertionError("family/template mismatch")
    if family["status"] != "strict_cycle":
        raise AssertionError("F16 must remain a strict-cycle record")
    if family["assignment_count"] != EXPECTED_FAMILY_ASSIGNMENT_COUNTS["F16"]:
        raise AssertionError("unexpected F16 assignment count")
    if family["orbit_size"] != EXPECTED_FAMILY_ORBIT_SIZES["F16"]:
        raise AssertionError("unexpected F16 orbit size")
    if family["core_size"] != EXPECTED_CORE_SIZE:
        raise AssertionError("unexpected F16 core size")
    if family["cycle_length"] != EXPECTED_CYCLE_LENGTH:
        raise AssertionError("unexpected F16 cycle length")
    if family["strict_edge_count"] != EXPECTED_STRICT_EDGE_COUNT:
        raise AssertionError("unexpected F16 strict-edge count")
    if family["span_signature"] != "3:1,3:1,3:1":
        raise AssertionError("unexpected F16 span signature")
    if rows != _normalize_rows(EXPECTED_CORE_SELECTED_ROWS):
        raise AssertionError("unexpected F16 core rows")
    _assert_cycle_steps(rows, family["cycle_steps"])

    if catalog_record["template_id"] != EXPECTED_TEMPLATE_ID:
        raise AssertionError("unexpected catalog template id")
    if catalog_record["status"] != "strict_cycle":
        raise AssertionError("unexpected catalog T12 status")
    if catalog_record["template_key"] != EXPECTED_TEMPLATE_KEY:
        raise AssertionError("catalog T12 template-key mismatch")
    coverage = catalog_record["coverage"]
    if coverage["assignment_count"] != EXPECTED_ASSIGNMENT_COUNT:
        raise AssertionError("catalog T12 assignment count mismatch")
    if coverage["assignment_ids"] != list(EXPECTED_ASSIGNMENT_IDS):
        raise AssertionError("catalog T12 assignment ids mismatch")
    if coverage["families"] != list(EXPECTED_FAMILY_IDS):
        raise AssertionError("catalog T12 family mismatch")
    if coverage["family_count"] != EXPECTED_FAMILY_COUNT:
        raise AssertionError("catalog T12 family count mismatch")
    if coverage["orbit_size_sum"] != EXPECTED_ORBIT_SIZE_SUM:
        raise AssertionError("catalog T12 orbit-size sum mismatch")
    hypothesis = catalog_record["hypothesis_shape"]
    if hypothesis["core_size"] != EXPECTED_CORE_SIZE:
        raise AssertionError("catalog T12 core-size mismatch")
    if hypothesis["cycle_length"] != EXPECTED_CYCLE_LENGTH:
        raise AssertionError("catalog T12 cycle-length mismatch")
    if hypothesis["cycle_length_counts"] != EXPECTED_CYCLE_LENGTH_COUNTS:
        raise AssertionError("catalog T12 cycle-length counts mismatch")
    if hypothesis["strict_edge_count"] != EXPECTED_STRICT_EDGE_COUNT:
        raise AssertionError("catalog T12 strict-edge mismatch")
    if hypothesis["connector_path_length_counts"] != EXPECTED_CONNECTOR_PATH_LENGTH_COUNTS:
        raise AssertionError("catalog T12 connector path-length mismatch")
    if hypothesis["span_signature_counts"] != EXPECTED_SPAN_SIGNATURE_COUNTS:
        raise AssertionError("catalog T12 span-signature mismatch")
    if hypothesis["cycle_span_counts"] != EXPECTED_CYCLE_SPAN_COUNTS:
        raise AssertionError("catalog T12 cycle-span mismatch")
    conclusion = catalog_record["conclusion_shape"]
    if conclusion["kind"] != "strict_cycle":
        raise AssertionError("catalog T12 conclusion kind mismatch")
    if "directed strict cycle" not in conclusion["strict_graph_obstruction"]:
        raise AssertionError("catalog T12 must describe a directed strict cycle")

    summaries = {
        str(summary["family_id"]): summary
        for summary in catalog_record["family_summaries"]
        if isinstance(summary, dict) and "family_id" in summary
    }
    summary = summaries.get("F16")
    if summary is None:
        raise AssertionError("catalog missing F16 summary")
    if summary["assignment_count"] != EXPECTED_FAMILY_ASSIGNMENT_COUNTS["F16"]:
        raise AssertionError("catalog F16 assignment count mismatch")
    if summary["orbit_size"] != EXPECTED_FAMILY_ORBIT_SIZES["F16"]:
        raise AssertionError("catalog F16 orbit size mismatch")
    if summary["cycle_length"] != EXPECTED_CYCLE_LENGTH:
        raise AssertionError("catalog F16 cycle length mismatch")
    if summary["cycle_step_count"] != EXPECTED_CYCLE_LENGTH:
        raise AssertionError("catalog F16 cycle-step count mismatch")
    if summary["contradiction_kind"] != "strict_cycle":
        raise AssertionError("catalog F16 contradiction kind mismatch")


def _cycle_pair_chain(steps: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "cycle_step": index,
            "strict_from_outer_pair": step["strict_inequality"]["outer_pair"],
            "strict_to_inner_pair": step["strict_inequality"]["inner_pair"],
            "equality_chain_to_next_outer_pair": equality_chain(
                step["equality_to_next_outer_pair"]
            ),
            "next_outer_pair": steps[(index + 1) % len(steps)]["strict_inequality"][
                "outer_pair"
            ],
        }
        for index, step in enumerate(steps)
    ]


def _family_local_lemma(steps: Sequence[dict[str, Any]]) -> dict[str, Any]:
    return {
        "packet_name": "T12/F16 strict-cycle local lemma packet",
        "review_status": "review_pending",
        "hypothesis_scope": (
            "Natural cyclic order on labels 0..8 plus the six listed selected "
            "rows; no claim is made about other n=9 templates."
        ),
        "strict_inequality_statements": [
            (
                f"Step {index}: row {step['strict_inequality']['row']} has "
                f"witness order {step['strict_inequality']['witness_order']}, so "
                f"outer pair {step['strict_inequality']['outer_pair']} strictly "
                f"contains inner pair {step['strict_inequality']['inner_pair']}."
            )
            for index, step in enumerate(steps)
        ],
        "selected_distance_equalities": [
            {
                "cycle_step": index,
                "equality_steps": equality_steps(step["equality_to_next_outer_pair"]),
            }
            for index, step in enumerate(steps)
        ],
        "cycle_closure_statement": (
            "Each strict edge's inner pair is identified with the next strict "
            "edge's outer pair, closing a directed three-edge strict cycle in the "
            "selected-distance quotient."
        ),
        "contradiction": (
            "The strict graph has a directed strict cycle of length 3 after "
            "selected-distance quotienting."
        ),
    }


def _cycle_edges(replay: Mapping[str, Any], steps: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    matched = []
    for step in steps:
        strict = step["strict_inequality"]
        for edge in replay["cycle_edges"]:
            if (
                edge["row"] == strict["row"]
                and edge["outer_pair"] == strict["outer_pair"]
                and edge["inner_pair"] == strict["inner_pair"]
            ):
                matched.append(dict(edge))
                break
        else:
            raise AssertionError("T12 strict cycle edge not found in replay")
    return matched


def _family_packet(family: dict[str, Any]) -> dict[str, Any]:
    family_id = str(family["family_id"])
    rows = _normalize_rows(family["core_selected_rows"])
    steps = family["cycle_steps"]
    replay_result = replay_vertex_circle_quotient(
        n9.N,
        list(n9.ORDER),
        parse_selected_rows(rows),
    )
    replay = result_to_json(replay_result)
    return {
        "family_id": family_id,
        "assignment_count": int(family["assignment_count"]),
        "orbit_size": int(family["orbit_size"]),
        "core_size": int(family["core_size"]),
        "cycle_length": int(family["cycle_length"]),
        "strict_edge_count": int(family["strict_edge_count"]),
        "span_signature": str(family["span_signature"]),
        "core_selected_rows": rows,
        "cycle_steps": steps,
        "cycle_pair_chain": _cycle_pair_chain(steps),
        "local_lemma": _family_local_lemma(steps),
        "replay": {
            "status": replay["status"],
            "selected_row_count": replay["selected_row_count"],
            "strict_edge_count": replay["strict_edge_count"],
            "self_edge_conflict_count": len(replay["self_edge_conflicts"]),
            "cycle_edge_count": len(replay["cycle_edges"]),
            "cycle_edges": _cycle_edges(replay, steps),
            "self_edge_conflicts": replay["self_edge_conflicts"],
        },
        "source_family_record": _family_source_summary(family),
    }


def t12_strict_cycle_lemma_packet_payload(
    strict_cycle_packet: dict[str, Any],
    template_catalog: dict[str, Any],
) -> dict[str, Any]:
    """Return the focused review-pending T12 local lemma packet."""

    if strict_cycle_packet.get("schema") != STRICT_CYCLE_TEMPLATE_PACKET_SCHEMA:
        raise ValueError("unexpected strict-cycle template packet schema")
    if template_catalog.get("schema") != TEMPLATE_LEMMA_CATALOG_SCHEMA:
        raise ValueError("unexpected template lemma catalog schema")

    template = _template_record(strict_cycle_packet)
    families = _family_records_by_id(template)
    family = families["F16"]
    catalog_record = _catalog_record(template_catalog)
    _assert_source_records(template, family, catalog_record)
    family_packets = [_family_packet(family)]

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "template_id": EXPECTED_TEMPLATE_ID,
        "template_key": EXPECTED_TEMPLATE_KEY,
        "assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "assignment_ids": list(EXPECTED_ASSIGNMENT_IDS),
        "family_count": EXPECTED_FAMILY_COUNT,
        "family_ids": list(EXPECTED_FAMILY_IDS),
        "family_assignment_counts": EXPECTED_FAMILY_ASSIGNMENT_COUNTS,
        "family_orbit_sizes": EXPECTED_FAMILY_ORBIT_SIZES,
        "orbit_size_sum": EXPECTED_ORBIT_SIZE_SUM,
        "core_size": EXPECTED_CORE_SIZE,
        "cycle_length": EXPECTED_CYCLE_LENGTH,
        "strict_edge_count": EXPECTED_STRICT_EDGE_COUNT,
        "cycle_length_counts": EXPECTED_CYCLE_LENGTH_COUNTS,
        "connector_path_length_counts": EXPECTED_CONNECTOR_PATH_LENGTH_COUNTS,
        "span_signature_counts": EXPECTED_SPAN_SIGNATURE_COUNTS,
        "cycle_span_counts": EXPECTED_CYCLE_SPAN_COUNTS,
        "family_packets": family_packets,
        "source_template_record": _source_template_summary(template),
        "source_catalog_record": catalog_record,
        "interpretation": [
            "This packet isolates the single-family T12 strict-cycle motif from existing review-pending n=9 diagnostics.",
            "The F16 record has six local rows and three directed strict inequalities.",
            "Each strict edge's inner pair is connected by selected-distance equalities to the next strict edge's outer pair.",
            "The packet is intended for local lemma review and proof mining, not as a theorem name.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": source_artifacts(strict_cycle_packet, template_catalog),
        "provenance": PROVENANCE,
    }
    assert_expected_t12_strict_cycle_lemma_packet(payload)
    return payload


def _family_packets_by_id(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    packets = payload.get("family_packets")
    if not isinstance(packets, list):
        raise AssertionError("family_packets must be a list")
    if len(packets) != len(EXPECTED_FAMILY_IDS):
        raise AssertionError(
            f"family_packets length mismatch: expected {len(EXPECTED_FAMILY_IDS)}, got {len(packets)}"
        )
    by_id = {
        str(packet["family_id"]): packet
        for packet in packets
        if isinstance(packet, dict) and "family_id" in packet
    }
    if len(by_id) != len(packets):
        raise AssertionError("family_packets must not contain duplicate family ids")
    if set(by_id) != set(EXPECTED_FAMILY_IDS):
        raise AssertionError(f"unexpected family packet ids: {sorted(by_id)!r}")
    return {family_id: by_id[family_id] for family_id in EXPECTED_FAMILY_IDS}


def assert_expected_t12_strict_cycle_lemma_packet(payload: Mapping[str, Any]) -> None:
    """Assert stable constants for the focused T12 local lemma packet."""

    expected_top = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "template_id": EXPECTED_TEMPLATE_ID,
        "template_key": EXPECTED_TEMPLATE_KEY,
        "assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "assignment_ids": list(EXPECTED_ASSIGNMENT_IDS),
        "family_count": EXPECTED_FAMILY_COUNT,
        "family_ids": list(EXPECTED_FAMILY_IDS),
        "family_assignment_counts": EXPECTED_FAMILY_ASSIGNMENT_COUNTS,
        "family_orbit_sizes": EXPECTED_FAMILY_ORBIT_SIZES,
        "orbit_size_sum": EXPECTED_ORBIT_SIZE_SUM,
        "core_size": EXPECTED_CORE_SIZE,
        "cycle_length": EXPECTED_CYCLE_LENGTH,
        "strict_edge_count": EXPECTED_STRICT_EDGE_COUNT,
        "cycle_length_counts": EXPECTED_CYCLE_LENGTH_COUNTS,
        "connector_path_length_counts": EXPECTED_CONNECTOR_PATH_LENGTH_COUNTS,
        "span_signature_counts": EXPECTED_SPAN_SIGNATURE_COUNTS,
        "cycle_span_counts": EXPECTED_CYCLE_SPAN_COUNTS,
        "provenance": PROVENANCE,
    }
    for key, expected in expected_top.items():
        if payload.get(key) != expected:
            raise AssertionError(f"{key} mismatch: expected {expected!r}, got {payload.get(key)!r}")

    family_packets = _family_packets_by_id(payload)
    packet = family_packets["F16"]
    if packet["assignment_count"] != EXPECTED_FAMILY_ASSIGNMENT_COUNTS["F16"]:
        raise AssertionError("F16 assignment count mismatch")
    if packet["orbit_size"] != EXPECTED_FAMILY_ORBIT_SIZES["F16"]:
        raise AssertionError("F16 orbit size mismatch")
    if packet["core_size"] != EXPECTED_CORE_SIZE:
        raise AssertionError("F16 core size mismatch")
    if packet["cycle_length"] != EXPECTED_CYCLE_LENGTH:
        raise AssertionError("F16 cycle length mismatch")
    if packet["strict_edge_count"] != EXPECTED_STRICT_EDGE_COUNT:
        raise AssertionError("F16 strict-edge count mismatch")
    if packet["span_signature"] != "3:1,3:1,3:1":
        raise AssertionError("F16 span signature mismatch")
    if packet["core_selected_rows"] != _normalize_rows(EXPECTED_CORE_SELECTED_ROWS):
        raise AssertionError("F16 core rows mismatch")
    if packet["cycle_steps"] != EXPECTED_CYCLE_STEPS:
        raise AssertionError("F16 cycle steps mismatch")
    expected_pair_chain = _cycle_pair_chain(EXPECTED_CYCLE_STEPS)
    if packet["cycle_pair_chain"] != expected_pair_chain:
        raise AssertionError("F16 cycle pair chain mismatch")

    replay = packet["replay"]
    if replay["status"] != "strict_cycle":
        raise AssertionError("F16 replay status mismatch")
    if replay["selected_row_count"] != EXPECTED_CORE_SIZE:
        raise AssertionError("F16 selected row count mismatch")
    if replay["strict_edge_count"] != EXPECTED_STRICT_EDGE_COUNT:
        raise AssertionError("F16 strict-edge count mismatch")
    if replay["self_edge_conflict_count"] != EXPECTED_SELF_EDGE_CONFLICT_COUNT:
        raise AssertionError("F16 self-edge conflict count mismatch")
    if replay["cycle_edge_count"] != EXPECTED_CYCLE_EDGE_COUNT:
        raise AssertionError("F16 cycle-edge count mismatch")
    if "primary_self_edge_conflict" in replay:
        raise AssertionError("T12 replay must not carry a primary self-edge conflict")
    cycle_edges = replay["cycle_edges"]
    if len(cycle_edges) != EXPECTED_CYCLE_EDGE_COUNT:
        raise AssertionError("F16 replay cycle-edge list mismatch")
    for index, edge in enumerate(cycle_edges):
        strict = EXPECTED_CYCLE_STEPS[index]["strict_inequality"]
        for key in (
            "row",
            "witness_order",
            "outer_pair",
            "inner_pair",
            "outer_interval",
            "inner_interval",
            "outer_class",
            "inner_class",
        ):
            if edge[key] != strict[key]:
                raise AssertionError(f"F16 cycle edge {index} {key} mismatch")
        if edge["outer_class"] == edge["inner_class"]:
            raise AssertionError("F16 replay cycle edge quotient classes must be distinct")
        if "outer_span" in edge or "inner_span" in edge:
            raise AssertionError("F16 replay cycle edges must not include source-only spans")

    lemma = packet["local_lemma"]
    if lemma["review_status"] != "review_pending":
        raise AssertionError("F16 local lemma review status mismatch")
    contradiction = str(lemma["contradiction"])
    if "directed strict cycle" not in contradiction:
        raise AssertionError("F16 local lemma must describe a directed strict cycle")
    if "reflexive strict edge" in contradiction or "self-edge" in contradiction:
        raise AssertionError("F16 local lemma must not describe a self-edge conflict")

    if "No proof of the n=9 case is claimed." not in payload.get("interpretation", []):
        raise AssertionError("interpretation must preserve the no-proof statement")
