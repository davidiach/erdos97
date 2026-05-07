"""Build a focused T01/F09 n=9 self-edge local lemma packet.

This module is proof-mining scaffolding. It does not prove the full n=9 case,
does not claim a counterexample, and does not promote the review-pending n=9
checker.
"""

from __future__ import annotations

from typing import Any, Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.n9_vertex_circle_self_edge_path_join import validate_equality_path
from erdos97.n9_vertex_circle_self_edge_template_packet import (
    SCHEMA as SELF_EDGE_TEMPLATE_PACKET_SCHEMA,
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


SCHEMA = "erdos97.n9_vertex_circle_t01_self_edge_lemma_packet.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Focused T01/F09 self-edge local lemma packet for six n=9 frontier "
    "assignments; proof-mining scaffolding only, not a proof of n=9, not a "
    "counterexample, not an independent review of the exhaustive checker, "
    "and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py",
    "command": (
        "python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py "
        "--assert-expected --write"
    ),
}

EXPECTED_TEMPLATE_ID = "T01"
EXPECTED_FAMILY_ID = "F09"
EXPECTED_ASSIGNMENT_IDS = ("A014", "A024", "A031", "A140", "A166", "A175")
EXPECTED_ASSIGNMENT_COUNT = 6
EXPECTED_FAMILY_COUNT = 1
EXPECTED_ORBIT_SIZE = 6
EXPECTED_CORE_SIZE = 3
EXPECTED_STRICT_EDGE_COUNT = 27
EXPECTED_SELF_EDGE_CONFLICT_COUNT = 2
EXPECTED_CORE_SELECTED_ROWS = (
    (0, 1, 2, 4, 8),
    (1, 0, 3, 5, 8),
    (2, 0, 1, 4, 6),
)
EXPECTED_STRICT_INEQUALITY = {
    "row": 0,
    "witness_order": [1, 2, 4, 8],
    "outer_interval": [0, 3],
    "inner_interval": [0, 1],
    "outer_pair": [1, 8],
    "inner_pair": [1, 2],
    "outer_class": [0, 1],
    "inner_class": [0, 1],
    "outer_span": 3,
    "inner_span": 1,
}
EXPECTED_DISTANCE_EQUALITY = {
    "start_pair": [1, 8],
    "end_pair": [1, 2],
    "path": [
        {"row": 1, "next_pair": [0, 1]},
        {"row": 0, "next_pair": [0, 2]},
        {"row": 2, "next_pair": [1, 2]},
    ],
}
EXPECTED_EQUALITY_CHAIN = ([1, 8], [0, 1], [0, 2], [1, 2])


def _template_record(packet: dict[str, Any]) -> dict[str, Any]:
    templates = packet.get("templates")
    if not isinstance(templates, list):
        raise ValueError("self-edge template packet must contain templates")
    for template in templates:
        if isinstance(template, dict) and template.get("template_id") == EXPECTED_TEMPLATE_ID:
            return template
    raise ValueError(f"missing template {EXPECTED_TEMPLATE_ID}")


def _family_record(template: dict[str, Any]) -> dict[str, Any]:
    records = template.get("family_records")
    if not isinstance(records, list):
        raise ValueError(f"{EXPECTED_TEMPLATE_ID} must contain family_records")
    for record in records:
        if isinstance(record, dict) and record.get("family_id") == EXPECTED_FAMILY_ID:
            return record
    raise ValueError(f"missing family {EXPECTED_FAMILY_ID}")


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


def equality_chain(equality: dict[str, Any]) -> list[list[int]]:
    """Return the pair chain traversed by a selected-distance equality path."""

    chain = [[int(value) for value in pair(*equality["start_pair"])]]
    for step in equality["path"]:
        chain.append([int(value) for value in pair(*step["next_pair"])])
    return chain


def equality_steps(equality: dict[str, Any]) -> list[dict[str, Any]]:
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
    self_edge_packet: dict[str, Any],
    template_catalog: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return embedded source-artifact metadata for the T01 packet."""

    return [
        {
            "path": "data/certificates/n9_vertex_circle_self_edge_template_packet.json",
            "role": "source T01/F09 self-edge template record",
            "schema": self_edge_packet.get("schema"),
            "status": self_edge_packet.get("status"),
            "trust": self_edge_packet.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_template_lemma_catalog.json",
            "role": "catalog crosswalk confirming T01 coverage and shape summary",
            "schema": template_catalog.get("schema"),
            "status": template_catalog.get("status"),
            "trust": template_catalog.get("trust"),
        },
    ]


def _primary_conflict(replay: dict[str, Any]) -> dict[str, Any]:
    for conflict in replay["self_edge_conflicts"]:
        if (
            conflict["row"] == EXPECTED_STRICT_INEQUALITY["row"]
            and conflict["outer_pair"] == EXPECTED_STRICT_INEQUALITY["outer_pair"]
            and conflict["inner_pair"] == EXPECTED_STRICT_INEQUALITY["inner_pair"]
        ):
            return {
                **conflict,
                "outer_span": EXPECTED_STRICT_INEQUALITY["outer_span"],
                "inner_span": EXPECTED_STRICT_INEQUALITY["inner_span"],
            }
    raise AssertionError("primary T01 self-edge conflict not found in replay")


def _source_template_summary(template: dict[str, Any]) -> dict[str, Any]:
    return {
        "template_id": str(template["template_id"]),
        "template_key": str(template["template_key"]),
        "status": str(template["status"]),
        "assignment_count": int(template["assignment_count"]),
        "assignment_ids": list(template["assignment_ids"]),
        "family_count": int(template["family_count"]),
        "families": list(template["families"]),
        "core_size": int(template["core_size"]),
        "strict_edge_count": int(template["strict_edge_count"]),
        "path_length_counts": template["path_length_counts"],
        "selected_path_shape_counts": template["selected_path_shape_counts"],
        "self_edge_shape_counts": template["self_edge_shape_counts"],
    }


def _assert_source_records(
    template: dict[str, Any],
    family: dict[str, Any],
    catalog_record: dict[str, Any],
) -> None:
    rows = _normalize_rows(family["core_selected_rows"])
    equality = family["distance_equality"]
    strict = family["strict_inequality"]
    validate_equality_path(rows, equality)

    if template["template_id"] != EXPECTED_TEMPLATE_ID:
        raise AssertionError("unexpected template id")
    if template["status"] != "self_edge":
        raise AssertionError("T01 must remain a self-edge template")
    if template["assignment_ids"] != list(EXPECTED_ASSIGNMENT_IDS):
        raise AssertionError("unexpected T01 assignment ids")
    if template["assignment_count"] != EXPECTED_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected T01 assignment count")
    if template["families"] != [EXPECTED_FAMILY_ID]:
        raise AssertionError("unexpected T01 family list")
    if family["family_id"] != EXPECTED_FAMILY_ID:
        raise AssertionError("unexpected family id")
    if family["template_id"] != EXPECTED_TEMPLATE_ID:
        raise AssertionError("family/template mismatch")
    if family["orbit_size"] != EXPECTED_ORBIT_SIZE:
        raise AssertionError("unexpected F09 orbit size")
    if family["core_size"] != EXPECTED_CORE_SIZE:
        raise AssertionError("unexpected F09 core size")
    if rows != _normalize_rows(EXPECTED_CORE_SELECTED_ROWS):
        raise AssertionError("unexpected T01/F09 core rows")
    if strict != EXPECTED_STRICT_INEQUALITY:
        raise AssertionError("unexpected T01 strict inequality")
    if equality != EXPECTED_DISTANCE_EQUALITY:
        raise AssertionError("unexpected T01 equality path")
    if equality_chain(equality) != [list(item) for item in EXPECTED_EQUALITY_CHAIN]:
        raise AssertionError("unexpected T01 equality chain")
    if catalog_record["template_id"] != EXPECTED_TEMPLATE_ID:
        raise AssertionError("unexpected catalog template id")
    if catalog_record["status"] != "self_edge":
        raise AssertionError("unexpected catalog T01 status")
    if catalog_record["coverage"]["assignment_ids"] != list(EXPECTED_ASSIGNMENT_IDS):
        raise AssertionError("catalog T01 assignment ids mismatch")
    if catalog_record["coverage"]["families"] != [EXPECTED_FAMILY_ID]:
        raise AssertionError("catalog T01 family mismatch")


def t01_self_edge_lemma_packet_payload(
    self_edge_packet: dict[str, Any],
    template_catalog: dict[str, Any],
) -> dict[str, Any]:
    """Return the focused review-pending T01/F09 local lemma packet."""

    if self_edge_packet.get("schema") != SELF_EDGE_TEMPLATE_PACKET_SCHEMA:
        raise ValueError("unexpected self-edge template packet schema")
    if template_catalog.get("schema") != TEMPLATE_LEMMA_CATALOG_SCHEMA:
        raise ValueError("unexpected template lemma catalog schema")

    template = _template_record(self_edge_packet)
    family = _family_record(template)
    catalog_record = _catalog_record(template_catalog)
    _assert_source_records(template, family, catalog_record)

    rows = _normalize_rows(family["core_selected_rows"])
    equality = family["distance_equality"]
    replay_result = replay_vertex_circle_quotient(
        n9.N,
        list(n9.ORDER),
        parse_selected_rows(rows),
    )
    replay = result_to_json(replay_result)
    primary = _primary_conflict(replay)

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "template_id": EXPECTED_TEMPLATE_ID,
        "family_id": EXPECTED_FAMILY_ID,
        "assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "assignment_ids": list(EXPECTED_ASSIGNMENT_IDS),
        "family_count": EXPECTED_FAMILY_COUNT,
        "orbit_size": EXPECTED_ORBIT_SIZE,
        "core_size": EXPECTED_CORE_SIZE,
        "core_selected_rows": rows,
        "strict_inequality": family["strict_inequality"],
        "distance_equality": equality,
        "equality_chain": equality_chain(equality),
        "local_lemma": {
            "packet_name": "T01/F09 self-edge local lemma packet",
            "review_status": "review_pending",
            "hypothesis_scope": (
                "Natural cyclic order on labels 0..8 plus the three listed "
                "selected rows; no claim is made about other n=9 templates."
            ),
            "selected_distance_equalities": equality_steps(equality),
            "strict_inequality_statement": (
                "Row 0 has witness order [1, 2, 4, 8], so the outer pair "
                "[1, 8] strictly contains the inner pair [1, 2] in the "
                "row-0 vertex-circle order."
            ),
            "equality_statement": (
                "Rows 1, 0, and 2 identify [1, 8] with [1, 2] in the "
                "selected-distance quotient."
            ),
            "contradiction": (
                "The strict graph has a reflexive strict edge after "
                "selected-distance quotienting."
            ),
        },
        "replay": {
            "status": replay["status"],
            "selected_row_count": replay["selected_row_count"],
            "strict_edge_count": replay["strict_edge_count"],
            "self_edge_conflict_count": len(replay["self_edge_conflicts"]),
            "cycle_edge_count": len(replay["cycle_edges"]),
            "primary_self_edge_conflict": primary,
            "self_edge_conflicts": replay["self_edge_conflicts"],
        },
        "source_template_record": _source_template_summary(template),
        "source_catalog_record": catalog_record,
        "interpretation": [
            "This packet isolates the T01/F09 self-edge motif from existing review-pending n=9 diagnostics.",
            "The three local rows force the displayed equality chain of ordinary pair distances.",
            "The row-0 vertex-circle order gives the displayed strict inequality between the same quotient class.",
            "The packet is intended for local lemma review and proof mining, not as a theorem name.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": source_artifacts(self_edge_packet, template_catalog),
        "provenance": PROVENANCE,
    }
    assert_expected_t01_self_edge_lemma_packet(payload)
    return payload


def assert_expected_t01_self_edge_lemma_packet(payload: dict[str, Any]) -> None:
    """Assert stable constants for the focused T01/F09 local lemma packet."""

    if payload["schema"] != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload['schema']}")
    if payload["status"] != STATUS:
        raise AssertionError(f"unexpected status: {payload['status']}")
    if payload["trust"] != TRUST:
        raise AssertionError(f"unexpected trust: {payload['trust']}")
    if payload["claim_scope"] != CLAIM_SCOPE:
        raise AssertionError("claim scope changed")
    if payload["n"] != n9.N or payload["row_size"] != n9.ROW_SIZE:
        raise AssertionError("unexpected n or row size")
    if payload["cyclic_order"] != list(n9.ORDER):
        raise AssertionError("unexpected cyclic order")
    if payload["template_id"] != EXPECTED_TEMPLATE_ID:
        raise AssertionError("unexpected template id")
    if payload["family_id"] != EXPECTED_FAMILY_ID:
        raise AssertionError("unexpected family id")
    if payload["assignment_count"] != EXPECTED_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected assignment count")
    if payload["assignment_ids"] != list(EXPECTED_ASSIGNMENT_IDS):
        raise AssertionError("unexpected assignment ids")
    if payload["family_count"] != EXPECTED_FAMILY_COUNT:
        raise AssertionError("unexpected family count")
    if payload["orbit_size"] != EXPECTED_ORBIT_SIZE:
        raise AssertionError("unexpected orbit size")
    if payload["core_size"] != EXPECTED_CORE_SIZE:
        raise AssertionError("unexpected core size")
    if payload["core_selected_rows"] != _normalize_rows(EXPECTED_CORE_SELECTED_ROWS):
        raise AssertionError("unexpected core rows")
    if payload["strict_inequality"] != EXPECTED_STRICT_INEQUALITY:
        raise AssertionError("unexpected strict inequality")
    if payload["distance_equality"] != EXPECTED_DISTANCE_EQUALITY:
        raise AssertionError("unexpected distance equality")
    if payload["equality_chain"] != [list(item) for item in EXPECTED_EQUALITY_CHAIN]:
        raise AssertionError("unexpected equality chain")
    replay = payload["replay"]
    if replay["status"] != "self_edge":
        raise AssertionError("unexpected replay status")
    if replay["selected_row_count"] != EXPECTED_CORE_SIZE:
        raise AssertionError("unexpected selected row count")
    if replay["strict_edge_count"] != EXPECTED_STRICT_EDGE_COUNT:
        raise AssertionError("unexpected strict edge count")
    if replay["self_edge_conflict_count"] != EXPECTED_SELF_EDGE_CONFLICT_COUNT:
        raise AssertionError("unexpected self-edge conflict count")
    primary = replay["primary_self_edge_conflict"]
    for key in ("row", "witness_order", "outer_pair", "inner_pair"):
        if primary[key] != EXPECTED_STRICT_INEQUALITY[key]:
            raise AssertionError(f"primary conflict {key} mismatch")
    if payload["provenance"] != PROVENANCE:
        raise AssertionError("unexpected provenance")
