"""Build a focused T06/F11 n=9 self-edge local lemma packet.

This module is proof-mining scaffolding. It does not prove the full n=9 case,
does not claim a counterexample, and does not promote the review-pending n=9
checker.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

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

SCHEMA = "erdos97.n9_vertex_circle_t06_self_edge_lemma_packet.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Focused T06/F11 self-edge local lemma packet for eighteen n=9 frontier "
    "assignments; proof-mining scaffolding only, not a proof of n=9, not a "
    "counterexample, not an independent review of the exhaustive checker, and "
    "not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_t06_self_edge_lemma_packet.py",
    "command": (
        "python scripts/check_n9_vertex_circle_t06_self_edge_lemma_packet.py "
        "--assert-expected --write"
    ),
}

EXPECTED_TEMPLATE_ID = "T06"
EXPECTED_TEMPLATE_KEY = "self_edge|rows=5|strict_edges=45|conflicts=2:1:1x1,3:1:0x1,3:1:1x1"
EXPECTED_FAMILY_ID = "F11"
EXPECTED_FAMILY_IDS = (EXPECTED_FAMILY_ID,)
EXPECTED_ASSIGNMENT_IDS = (
    "A016",
    "A018",
    "A026",
    "A027",
    "A041",
    "A046",
    "A069",
    "A094",
    "A097",
    "A112",
    "A127",
    "A139",
    "A146",
    "A158",
    "A165",
    "A168",
    "A172",
    "A179",
)
EXPECTED_ASSIGNMENT_COUNT = 18
EXPECTED_FAMILY_COUNT = 1
EXPECTED_ORBIT_SIZE_SUM = 18
EXPECTED_CORE_SIZE = 5
EXPECTED_STRICT_EDGE_COUNT = 45
EXPECTED_SELF_EDGE_CONFLICT_COUNT = 3
EXPECTED_CYCLE_EDGE_COUNT = 0
EXPECTED_FAMILY_ASSIGNMENT_COUNTS = {"F11": 18}
EXPECTED_FAMILY_ORBIT_SIZES = {"F11": 18}
EXPECTED_PATH_LENGTH_COUNTS = {"4": 18}
EXPECTED_SHARED_ENDPOINT_COUNTS = {"1": 18}
EXPECTED_SELECTED_PATH_SHAPE_COUNTS = {"2:1:1:path=4": 18}
EXPECTED_CORE_SELECTED_ROWS = {
    "F11": (
        (1, 0, 3, 5, 8),
        (5, 0, 3, 4, 7),
        (6, 2, 5, 7, 8),
        (7, 0, 1, 5, 6),
        (8, 2, 3, 6, 7),
    ),
}
EXPECTED_STRICT_INEQUALITIES: dict[str, dict[str, Any]] = {
    "F11": {
        "row": 1,
        "witness_order": [3, 5, 8, 0],
        "outer_interval": [0, 2],
        "inner_interval": [0, 1],
        "outer_pair": [3, 8],
        "inner_pair": [3, 5],
        "outer_class": [0, 5],
        "inner_class": [0, 5],
        "outer_span": 2,
        "inner_span": 1,
    },
}
EXPECTED_DISTANCE_EQUALITIES: dict[str, dict[str, Any]] = {
    "F11": {
        "start_pair": [3, 8],
        "end_pair": [3, 5],
        "path": [
            {"row": 8, "next_pair": [6, 8]},
            {"row": 6, "next_pair": [6, 7]},
            {"row": 7, "next_pair": [5, 7]},
            {"row": 5, "next_pair": [3, 5]},
        ],
    },
}
EXPECTED_EQUALITY_CHAINS = {
    "F11": ([3, 8], [6, 8], [6, 7], [5, 7], [3, 5]),
}


def _template_record(packet: dict[str, Any]) -> dict[str, Any]:
    templates = packet.get("templates")
    if not isinstance(templates, list):
        raise ValueError("self-edge template packet must contain templates")
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
        raise ValueError(f"missing T06 families: {missing!r}")
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
    self_edge_packet: dict[str, Any],
    template_catalog: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return embedded source-artifact metadata for the T06 packet."""

    return [
        {
            "path": "data/certificates/n9_vertex_circle_self_edge_template_packet.json",
            "role": "source T06/F11 self-edge template record",
            "schema": self_edge_packet.get("schema"),
            "status": self_edge_packet.get("status"),
            "trust": self_edge_packet.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_template_lemma_catalog.json",
            "role": "catalog crosswalk confirming T06 coverage and shape summary",
            "schema": template_catalog.get("schema"),
            "status": template_catalog.get("status"),
            "trust": template_catalog.get("trust"),
        },
    ]


def _primary_conflict(replay: dict[str, Any], strict: Mapping[str, Any]) -> dict[str, Any]:
    for conflict in replay["self_edge_conflicts"]:
        if (
            conflict["row"] == strict["row"]
            and conflict["outer_pair"] == strict["outer_pair"]
            and conflict["inner_pair"] == strict["inner_pair"]
        ):
            return {
                **conflict,
                "outer_span": strict["outer_span"],
                "inner_span": strict["inner_span"],
            }
    raise AssertionError("primary T06 self-edge conflict not found in replay")


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
        "strict_edge_count": int(template["strict_edge_count"]),
        "path_length_counts": template["path_length_counts"],
        "shared_endpoint_counts": template["shared_endpoint_counts"],
        "selected_path_shape_counts": template["selected_path_shape_counts"],
        "self_edge_shape_counts": template["self_edge_shape_counts"],
    }


def _family_source_summary(family: dict[str, Any]) -> dict[str, Any]:
    return {
        "family_id": str(family["family_id"]),
        "template_id": str(family["template_id"]),
        "status": str(family["status"]),
        "assignment_count": int(family["assignment_count"]),
        "orbit_size": int(family["orbit_size"]),
        "core_size": int(family["core_size"]),
        "path_length": int(family["path_length"]),
        "strict_inequality": family["strict_inequality"],
        "distance_equality": family["distance_equality"],
        "equality_chain": equality_chain(family["distance_equality"]),
    }


def _assert_source_records(
    template: dict[str, Any],
    families: Mapping[str, dict[str, Any]],
    catalog_record: dict[str, Any],
) -> None:
    if template["template_id"] != EXPECTED_TEMPLATE_ID:
        raise AssertionError("unexpected template id")
    if template["template_key"] != EXPECTED_TEMPLATE_KEY:
        raise AssertionError("unexpected T06 template key")
    if template["status"] != "self_edge":
        raise AssertionError("T06 must remain a self-edge template")
    if template["assignment_ids"] != list(EXPECTED_ASSIGNMENT_IDS):
        raise AssertionError("unexpected T06 assignment ids")
    if template["assignment_count"] != EXPECTED_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected T06 assignment count")
    if template["families"] != list(EXPECTED_FAMILY_IDS):
        raise AssertionError("unexpected T06 family list")
    if template["family_count"] != EXPECTED_FAMILY_COUNT:
        raise AssertionError("unexpected T06 family count")
    if template["orbit_size_sum"] != EXPECTED_ORBIT_SIZE_SUM:
        raise AssertionError("unexpected T06 orbit-size sum")
    if template["core_size"] != EXPECTED_CORE_SIZE:
        raise AssertionError("unexpected T06 core size")
    if template["strict_edge_count"] != EXPECTED_STRICT_EDGE_COUNT:
        raise AssertionError("unexpected T06 strict-edge count")
    if template["path_length_counts"] != EXPECTED_PATH_LENGTH_COUNTS:
        raise AssertionError("unexpected T06 path-length counts")
    if template["shared_endpoint_counts"] != EXPECTED_SHARED_ENDPOINT_COUNTS:
        raise AssertionError("unexpected T06 shared-endpoint counts")
    if template["selected_path_shape_counts"] != EXPECTED_SELECTED_PATH_SHAPE_COUNTS:
        raise AssertionError("unexpected T06 selected-path shape counts")

    family = families[EXPECTED_FAMILY_ID]
    rows = _normalize_rows(family["core_selected_rows"])
    equality = family["distance_equality"]
    strict = family["strict_inequality"]
    validate_equality_path(rows, equality)
    if family["family_id"] != EXPECTED_FAMILY_ID:
        raise AssertionError("unexpected family id")
    if family["template_id"] != EXPECTED_TEMPLATE_ID:
        raise AssertionError("family/template mismatch")
    if family["status"] != "self_edge":
        raise AssertionError("F11 must remain a self-edge record")
    if family["assignment_count"] != EXPECTED_FAMILY_ASSIGNMENT_COUNTS[EXPECTED_FAMILY_ID]:
        raise AssertionError("unexpected F11 assignment count")
    if family["orbit_size"] != EXPECTED_FAMILY_ORBIT_SIZES[EXPECTED_FAMILY_ID]:
        raise AssertionError("unexpected F11 orbit size")
    if family["core_size"] != EXPECTED_CORE_SIZE:
        raise AssertionError("unexpected F11 core size")
    if rows != _normalize_rows(EXPECTED_CORE_SELECTED_ROWS[EXPECTED_FAMILY_ID]):
        raise AssertionError("unexpected F11 core rows")
    if strict != EXPECTED_STRICT_INEQUALITIES[EXPECTED_FAMILY_ID]:
        raise AssertionError("unexpected F11 strict inequality")
    if equality != EXPECTED_DISTANCE_EQUALITIES[EXPECTED_FAMILY_ID]:
        raise AssertionError("unexpected F11 equality path")
    expected_chain = [list(item) for item in EXPECTED_EQUALITY_CHAINS[EXPECTED_FAMILY_ID]]
    if equality_chain(equality) != expected_chain:
        raise AssertionError("unexpected F11 equality chain")
    if strict["outer_pair"] != equality["start_pair"]:
        raise AssertionError("F11 strict outer pair must start equality path")
    if strict["inner_pair"] != equality["end_pair"]:
        raise AssertionError("F11 strict inner pair must end equality path")

    if catalog_record["template_id"] != EXPECTED_TEMPLATE_ID:
        raise AssertionError("unexpected catalog template id")
    if catalog_record["status"] != "self_edge":
        raise AssertionError("unexpected catalog T06 status")
    coverage = catalog_record["coverage"]
    if coverage["assignment_count"] != EXPECTED_ASSIGNMENT_COUNT:
        raise AssertionError("catalog T06 assignment count mismatch")
    if coverage["assignment_ids"] != list(EXPECTED_ASSIGNMENT_IDS):
        raise AssertionError("catalog T06 assignment ids mismatch")
    if coverage["families"] != list(EXPECTED_FAMILY_IDS):
        raise AssertionError("catalog T06 family mismatch")
    if coverage["family_count"] != EXPECTED_FAMILY_COUNT:
        raise AssertionError("catalog T06 family count mismatch")
    if coverage["orbit_size_sum"] != EXPECTED_ORBIT_SIZE_SUM:
        raise AssertionError("catalog T06 orbit-size sum mismatch")
    hypothesis = catalog_record["hypothesis_shape"]
    if hypothesis["core_size"] != EXPECTED_CORE_SIZE:
        raise AssertionError("catalog T06 core-size mismatch")
    if hypothesis["strict_edge_count"] != EXPECTED_STRICT_EDGE_COUNT:
        raise AssertionError("catalog T06 strict-edge mismatch")
    if hypothesis["path_length_counts"] != EXPECTED_PATH_LENGTH_COUNTS:
        raise AssertionError("catalog T06 path-length mismatch")
    if hypothesis["shared_endpoint_counts"] != EXPECTED_SHARED_ENDPOINT_COUNTS:
        raise AssertionError("catalog T06 shared-endpoint mismatch")
    if hypothesis["selected_path_shape_counts"] != EXPECTED_SELECTED_PATH_SHAPE_COUNTS:
        raise AssertionError("catalog T06 selected-path shape mismatch")


def _family_local_lemma(strict: Mapping[str, Any], equality: Mapping[str, Any]) -> dict[str, Any]:
    path_rows = [int(step["row"]) for step in equality["path"]]
    return {
        "packet_name": "T06/F11 self-edge local lemma packet",
        "review_status": "review_pending",
        "hypothesis_scope": (
            "Natural cyclic order on labels 0..8 plus the four listed selected "
            "rows; no claim is made about other n=9 templates."
        ),
        "selected_distance_equalities": equality_steps(equality),
        "strict_inequality_statement": (
            f"Row {strict['row']} has witness order {strict['witness_order']}, "
            f"so the outer pair {strict['outer_pair']} strictly contains the "
            f"inner pair {strict['inner_pair']} in that row's vertex-circle order."
        ),
        "equality_statement": (
            f"Rows {path_rows} identify {equality['start_pair']} with "
            f"{equality['end_pair']} in the selected-distance quotient."
        ),
        "contradiction": (
            "The strict graph has a reflexive strict edge after selected-distance "
            "quotienting."
        ),
    }


def _family_packet(family: dict[str, Any]) -> dict[str, Any]:
    rows = _normalize_rows(family["core_selected_rows"])
    equality = family["distance_equality"]
    strict = family["strict_inequality"]
    replay_result = replay_vertex_circle_quotient(
        n9.N,
        list(n9.ORDER),
        parse_selected_rows(rows),
    )
    replay = result_to_json(replay_result)
    primary = _primary_conflict(replay, strict)
    return {
        "family_id": EXPECTED_FAMILY_ID,
        "assignment_count": int(family["assignment_count"]),
        "orbit_size": int(family["orbit_size"]),
        "core_size": int(family["core_size"]),
        "core_selected_rows": rows,
        "strict_inequality": strict,
        "distance_equality": equality,
        "equality_chain": equality_chain(equality),
        "local_lemma": _family_local_lemma(strict, equality),
        "replay": {
            "status": replay["status"],
            "selected_row_count": replay["selected_row_count"],
            "strict_edge_count": replay["strict_edge_count"],
            "self_edge_conflict_count": len(replay["self_edge_conflicts"]),
            "cycle_edge_count": len(replay["cycle_edges"]),
            "primary_self_edge_conflict": primary,
            "self_edge_conflicts": replay["self_edge_conflicts"],
        },
        "source_family_record": _family_source_summary(family),
    }


def t06_self_edge_lemma_packet_payload(
    self_edge_packet: dict[str, Any],
    template_catalog: dict[str, Any],
) -> dict[str, Any]:
    """Return the focused review-pending T06/F11 local lemma packet."""

    if self_edge_packet.get("schema") != SELF_EDGE_TEMPLATE_PACKET_SCHEMA:
        raise ValueError("unexpected self-edge template packet schema")
    if template_catalog.get("schema") != TEMPLATE_LEMMA_CATALOG_SCHEMA:
        raise ValueError("unexpected template lemma catalog schema")

    template = _template_record(self_edge_packet)
    families = _family_records_by_id(template)
    catalog_record = _catalog_record(template_catalog)
    _assert_source_records(template, families, catalog_record)
    family_packets = [_family_packet(families[EXPECTED_FAMILY_ID])]

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
        "strict_edge_count": EXPECTED_STRICT_EDGE_COUNT,
        "path_length_counts": EXPECTED_PATH_LENGTH_COUNTS,
        "shared_endpoint_counts": EXPECTED_SHARED_ENDPOINT_COUNTS,
        "selected_path_shape_counts": EXPECTED_SELECTED_PATH_SHAPE_COUNTS,
        "family_packets": family_packets,
        "source_template_record": _source_template_summary(template),
        "source_catalog_record": catalog_record,
        "interpretation": [
            "This packet isolates the T06/F11 self-edge motif from existing review-pending n=9 diagnostics.",
            "The family record has four local rows that force the displayed equality chain.",
            "The family record has a vertex-circle strict inequality between the same quotient class.",
            "The packet is intended for local lemma review and proof mining, not as a theorem name.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": source_artifacts(self_edge_packet, template_catalog),
        "provenance": PROVENANCE,
    }
    assert_expected_t06_self_edge_lemma_packet(payload)
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


def assert_expected_t06_self_edge_lemma_packet(payload: Mapping[str, Any]) -> None:
    """Assert stable constants for the focused T06/F11 local lemma packet."""

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
        "strict_edge_count": EXPECTED_STRICT_EDGE_COUNT,
        "path_length_counts": EXPECTED_PATH_LENGTH_COUNTS,
        "shared_endpoint_counts": EXPECTED_SHARED_ENDPOINT_COUNTS,
        "selected_path_shape_counts": EXPECTED_SELECTED_PATH_SHAPE_COUNTS,
        "provenance": PROVENANCE,
    }
    for key, expected in expected_top.items():
        if payload.get(key) != expected:
            raise AssertionError(f"{key} mismatch: expected {expected!r}, got {payload.get(key)!r}")

    packet = _family_packets_by_id(payload)[EXPECTED_FAMILY_ID]
    if packet["assignment_count"] != EXPECTED_FAMILY_ASSIGNMENT_COUNTS[EXPECTED_FAMILY_ID]:
        raise AssertionError("F11 assignment count mismatch")
    if packet["orbit_size"] != EXPECTED_FAMILY_ORBIT_SIZES[EXPECTED_FAMILY_ID]:
        raise AssertionError("F11 orbit size mismatch")
    if packet["core_size"] != EXPECTED_CORE_SIZE:
        raise AssertionError("F11 core size mismatch")
    if packet["core_selected_rows"] != _normalize_rows(EXPECTED_CORE_SELECTED_ROWS[EXPECTED_FAMILY_ID]):
        raise AssertionError("F11 core rows mismatch")
    if packet["strict_inequality"] != EXPECTED_STRICT_INEQUALITIES[EXPECTED_FAMILY_ID]:
        raise AssertionError("F11 strict inequality mismatch")
    if packet["distance_equality"] != EXPECTED_DISTANCE_EQUALITIES[EXPECTED_FAMILY_ID]:
        raise AssertionError("F11 equality path mismatch")
    if packet["equality_chain"] != [list(item) for item in EXPECTED_EQUALITY_CHAINS[EXPECTED_FAMILY_ID]]:
        raise AssertionError("F11 equality chain mismatch")

    replay = packet["replay"]
    if replay["status"] != "self_edge":
        raise AssertionError("F11 replay status mismatch")
    if replay["selected_row_count"] != EXPECTED_CORE_SIZE:
        raise AssertionError("F11 selected row count mismatch")
    if replay["strict_edge_count"] != EXPECTED_STRICT_EDGE_COUNT:
        raise AssertionError("F11 strict-edge count mismatch")
    if replay["self_edge_conflict_count"] != EXPECTED_SELF_EDGE_CONFLICT_COUNT:
        raise AssertionError("F11 self-edge conflict count mismatch")
    if replay["cycle_edge_count"] != EXPECTED_CYCLE_EDGE_COUNT:
        raise AssertionError("F11 cycle-edge count mismatch")
    primary = replay["primary_self_edge_conflict"]
    strict = EXPECTED_STRICT_INEQUALITIES[EXPECTED_FAMILY_ID]
    for key in ("row", "witness_order", "outer_pair", "inner_pair", "outer_interval", "inner_interval"):
        if primary[key] != strict[key]:
            raise AssertionError(f"F11 primary conflict {key} mismatch")
    lemma = packet["local_lemma"]
    if lemma["review_status"] != "review_pending":
        raise AssertionError("F11 local lemma review status mismatch")

    if "No proof of the n=9 case is claimed." not in payload.get("interpretation", []):
        raise AssertionError("interpretation must preserve the no-proof statement")
