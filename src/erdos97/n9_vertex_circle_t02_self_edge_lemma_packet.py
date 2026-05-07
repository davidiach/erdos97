"""Build a focused T02 n=9 self-edge local lemma packet.

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


SCHEMA = "erdos97.n9_vertex_circle_t02_self_edge_lemma_packet.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Focused T02 multi-family self-edge local lemma packet for forty n=9 "
    "frontier assignments; proof-mining scaffolding only, not a proof of n=9, "
    "not a counterexample, not an independent review of the exhaustive checker, "
    "and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py",
    "command": (
        "python scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py "
        "--assert-expected --write"
    ),
}

EXPECTED_TEMPLATE_ID = "T02"
EXPECTED_TEMPLATE_KEY = "self_edge|rows=3|strict_edges=27|conflicts=3:1:1x1"
EXPECTED_FAMILY_IDS = ("F01", "F04", "F08", "F14")
EXPECTED_ASSIGNMENT_IDS = (
    "A001",
    "A004",
    "A006",
    "A009",
    "A011",
    "A019",
    "A022",
    "A025",
    "A034",
    "A035",
    "A045",
    "A051",
    "A056",
    "A058",
    "A060",
    "A061",
    "A063",
    "A065",
    "A070",
    "A076",
    "A078",
    "A087",
    "A092",
    "A099",
    "A101",
    "A103",
    "A114",
    "A115",
    "A118",
    "A119",
    "A121",
    "A136",
    "A138",
    "A145",
    "A163",
    "A173",
    "A176",
    "A178",
    "A182",
    "A184",
)
EXPECTED_ASSIGNMENT_COUNT = 40
EXPECTED_FAMILY_COUNT = 4
EXPECTED_ORBIT_SIZE_SUM = 40
EXPECTED_CORE_SIZE = 3
EXPECTED_STRICT_EDGE_COUNT = 27
EXPECTED_SELF_EDGE_CONFLICT_COUNT = 1
EXPECTED_CYCLE_EDGE_COUNT = 0
EXPECTED_FAMILY_ASSIGNMENT_COUNTS = {"F01": 18, "F04": 18, "F08": 2, "F14": 2}
EXPECTED_FAMILY_ORBIT_SIZES = {"F01": 18, "F04": 18, "F08": 2, "F14": 2}
EXPECTED_PATH_LENGTH_COUNTS = {"3": 40}
EXPECTED_SHARED_ENDPOINT_COUNTS = {"1": 40}
EXPECTED_SELECTED_PATH_SHAPE_COUNTS = {"3:1:1:path=3": 40}
EXPECTED_CORE_SELECTED_ROWS = {
    "F01": (
        (0, 1, 2, 3, 8),
        (1, 0, 2, 4, 7),
        (8, 0, 1, 4, 5),
    ),
    "F04": (
        (0, 1, 2, 4, 6),
        (1, 0, 2, 3, 5),
        (2, 1, 3, 4, 8),
    ),
    "F08": (
        (0, 1, 2, 4, 8),
        (1, 0, 2, 3, 5),
        (8, 0, 1, 3, 7),
    ),
    "F14": (
        (0, 1, 2, 6, 8),
        (1, 0, 2, 3, 7),
        (8, 0, 1, 5, 7),
    ),
}
EXPECTED_STRICT_INEQUALITIES: dict[str, dict[str, Any]] = {
    "F01": {
        "row": 0,
        "witness_order": [1, 2, 3, 8],
        "outer_interval": [0, 3],
        "inner_interval": [0, 1],
        "outer_pair": [1, 8],
        "inner_pair": [1, 2],
        "outer_class": [0, 1],
        "inner_class": [0, 1],
        "outer_span": 3,
        "inner_span": 1,
    },
    "F04": {
        "row": 1,
        "witness_order": [2, 3, 5, 0],
        "outer_interval": [0, 3],
        "inner_interval": [0, 1],
        "outer_pair": [0, 2],
        "inner_pair": [2, 3],
        "outer_class": [0, 1],
        "inner_class": [0, 1],
        "outer_span": 3,
        "inner_span": 1,
    },
    "F08": {
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
    },
    "F14": {
        "row": 0,
        "witness_order": [1, 2, 6, 8],
        "outer_interval": [0, 3],
        "inner_interval": [0, 1],
        "outer_pair": [1, 8],
        "inner_pair": [1, 2],
        "outer_class": [0, 1],
        "inner_class": [0, 1],
        "outer_span": 3,
        "inner_span": 1,
    },
}
EXPECTED_DISTANCE_EQUALITIES: dict[str, dict[str, Any]] = {
    "F01": {
        "start_pair": [1, 8],
        "end_pair": [1, 2],
        "path": [
            {"row": 8, "next_pair": [0, 8]},
            {"row": 0, "next_pair": [0, 1]},
            {"row": 1, "next_pair": [1, 2]},
        ],
    },
    "F04": {
        "start_pair": [0, 2],
        "end_pair": [2, 3],
        "path": [
            {"row": 0, "next_pair": [0, 1]},
            {"row": 1, "next_pair": [1, 2]},
            {"row": 2, "next_pair": [2, 3]},
        ],
    },
    "F08": {
        "start_pair": [1, 8],
        "end_pair": [1, 2],
        "path": [
            {"row": 8, "next_pair": [0, 8]},
            {"row": 0, "next_pair": [0, 1]},
            {"row": 1, "next_pair": [1, 2]},
        ],
    },
    "F14": {
        "start_pair": [1, 8],
        "end_pair": [1, 2],
        "path": [
            {"row": 8, "next_pair": [0, 8]},
            {"row": 0, "next_pair": [0, 1]},
            {"row": 1, "next_pair": [1, 2]},
        ],
    },
}
EXPECTED_EQUALITY_CHAINS = {
    "F01": ([1, 8], [0, 8], [0, 1], [1, 2]),
    "F04": ([0, 2], [0, 1], [1, 2], [2, 3]),
    "F08": ([1, 8], [0, 8], [0, 1], [1, 2]),
    "F14": ([1, 8], [0, 8], [0, 1], [1, 2]),
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
        raise ValueError(f"missing T02 families: {missing!r}")
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
    """Return embedded source-artifact metadata for the T02 packet."""

    return [
        {
            "path": "data/certificates/n9_vertex_circle_self_edge_template_packet.json",
            "role": "source T02 multi-family self-edge template record",
            "schema": self_edge_packet.get("schema"),
            "status": self_edge_packet.get("status"),
            "trust": self_edge_packet.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_template_lemma_catalog.json",
            "role": "catalog crosswalk confirming T02 coverage and shape summary",
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
    raise AssertionError("primary T02 self-edge conflict not found in replay")


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
        raise AssertionError("unexpected T02 template key")
    if template["status"] != "self_edge":
        raise AssertionError("T02 must remain a self-edge template")
    if template["assignment_ids"] != list(EXPECTED_ASSIGNMENT_IDS):
        raise AssertionError("unexpected T02 assignment ids")
    if template["assignment_count"] != EXPECTED_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected T02 assignment count")
    if template["families"] != list(EXPECTED_FAMILY_IDS):
        raise AssertionError("unexpected T02 family list")
    if template["family_count"] != EXPECTED_FAMILY_COUNT:
        raise AssertionError("unexpected T02 family count")
    if template["orbit_size_sum"] != EXPECTED_ORBIT_SIZE_SUM:
        raise AssertionError("unexpected T02 orbit-size sum")
    if template["core_size"] != EXPECTED_CORE_SIZE:
        raise AssertionError("unexpected T02 core size")
    if template["strict_edge_count"] != EXPECTED_STRICT_EDGE_COUNT:
        raise AssertionError("unexpected T02 strict-edge count")
    if template["path_length_counts"] != EXPECTED_PATH_LENGTH_COUNTS:
        raise AssertionError("unexpected T02 path-length counts")
    if template["shared_endpoint_counts"] != EXPECTED_SHARED_ENDPOINT_COUNTS:
        raise AssertionError("unexpected T02 shared-endpoint counts")
    if template["selected_path_shape_counts"] != EXPECTED_SELECTED_PATH_SHAPE_COUNTS:
        raise AssertionError("unexpected T02 selected-path shape counts")

    for family_id in EXPECTED_FAMILY_IDS:
        family = families[family_id]
        rows = _normalize_rows(family["core_selected_rows"])
        equality = family["distance_equality"]
        strict = family["strict_inequality"]
        validate_equality_path(rows, equality)
        if family["family_id"] != family_id:
            raise AssertionError("unexpected family id")
        if family["template_id"] != EXPECTED_TEMPLATE_ID:
            raise AssertionError("family/template mismatch")
        if family["status"] != "self_edge":
            raise AssertionError(f"{family_id} must remain a self-edge record")
        if family["assignment_count"] != EXPECTED_FAMILY_ASSIGNMENT_COUNTS[family_id]:
            raise AssertionError(f"unexpected {family_id} assignment count")
        if family["orbit_size"] != EXPECTED_FAMILY_ORBIT_SIZES[family_id]:
            raise AssertionError(f"unexpected {family_id} orbit size")
        if family["core_size"] != EXPECTED_CORE_SIZE:
            raise AssertionError(f"unexpected {family_id} core size")
        if rows != _normalize_rows(EXPECTED_CORE_SELECTED_ROWS[family_id]):
            raise AssertionError(f"unexpected {family_id} core rows")
        if strict != EXPECTED_STRICT_INEQUALITIES[family_id]:
            raise AssertionError(f"unexpected {family_id} strict inequality")
        if equality != EXPECTED_DISTANCE_EQUALITIES[family_id]:
            raise AssertionError(f"unexpected {family_id} equality path")
        if equality_chain(equality) != [list(item) for item in EXPECTED_EQUALITY_CHAINS[family_id]]:
            raise AssertionError(f"unexpected {family_id} equality chain")
        if strict["outer_pair"] != equality["start_pair"]:
            raise AssertionError(f"{family_id} strict outer pair must start equality path")
        if strict["inner_pair"] != equality["end_pair"]:
            raise AssertionError(f"{family_id} strict inner pair must end equality path")

    if catalog_record["template_id"] != EXPECTED_TEMPLATE_ID:
        raise AssertionError("unexpected catalog template id")
    if catalog_record["status"] != "self_edge":
        raise AssertionError("unexpected catalog T02 status")
    coverage = catalog_record["coverage"]
    if coverage["assignment_count"] != EXPECTED_ASSIGNMENT_COUNT:
        raise AssertionError("catalog T02 assignment count mismatch")
    if coverage["assignment_ids"] != list(EXPECTED_ASSIGNMENT_IDS):
        raise AssertionError("catalog T02 assignment ids mismatch")
    if coverage["families"] != list(EXPECTED_FAMILY_IDS):
        raise AssertionError("catalog T02 family mismatch")
    if coverage["family_count"] != EXPECTED_FAMILY_COUNT:
        raise AssertionError("catalog T02 family count mismatch")
    if coverage["orbit_size_sum"] != EXPECTED_ORBIT_SIZE_SUM:
        raise AssertionError("catalog T02 orbit-size sum mismatch")
    hypothesis = catalog_record["hypothesis_shape"]
    if hypothesis["core_size"] != EXPECTED_CORE_SIZE:
        raise AssertionError("catalog T02 core-size mismatch")
    if hypothesis["strict_edge_count"] != EXPECTED_STRICT_EDGE_COUNT:
        raise AssertionError("catalog T02 strict-edge mismatch")
    if hypothesis["path_length_counts"] != EXPECTED_PATH_LENGTH_COUNTS:
        raise AssertionError("catalog T02 path-length mismatch")
    if hypothesis["shared_endpoint_counts"] != EXPECTED_SHARED_ENDPOINT_COUNTS:
        raise AssertionError("catalog T02 shared-endpoint mismatch")

    summaries = {
        str(summary["family_id"]): summary
        for summary in catalog_record["family_summaries"]
        if isinstance(summary, dict) and "family_id" in summary
    }
    for family_id in EXPECTED_FAMILY_IDS:
        summary = summaries.get(family_id)
        if summary is None:
            raise AssertionError(f"catalog missing {family_id} summary")
        strict = EXPECTED_STRICT_INEQUALITIES[family_id]
        if summary["assignment_count"] != EXPECTED_FAMILY_ASSIGNMENT_COUNTS[family_id]:
            raise AssertionError(f"catalog {family_id} assignment count mismatch")
        if summary["orbit_size"] != EXPECTED_FAMILY_ORBIT_SIZES[family_id]:
            raise AssertionError(f"catalog {family_id} orbit size mismatch")
        if summary["outer_pair"] != strict["outer_pair"]:
            raise AssertionError(f"catalog {family_id} outer pair mismatch")
        if summary["inner_pair"] != strict["inner_pair"]:
            raise AssertionError(f"catalog {family_id} inner pair mismatch")


def _family_local_lemma(family_id: str, strict: Mapping[str, Any], equality: Mapping[str, Any]) -> dict[str, Any]:
    path_rows = [int(step["row"]) for step in equality["path"]]
    return {
        "packet_name": f"T02/{family_id} self-edge local lemma packet",
        "review_status": "review_pending",
        "hypothesis_scope": (
            "Natural cyclic order on labels 0..8 plus the three listed selected "
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
    family_id = str(family["family_id"])
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
        "family_id": family_id,
        "assignment_count": int(family["assignment_count"]),
        "orbit_size": int(family["orbit_size"]),
        "core_size": int(family["core_size"]),
        "core_selected_rows": rows,
        "strict_inequality": strict,
        "distance_equality": equality,
        "equality_chain": equality_chain(equality),
        "local_lemma": _family_local_lemma(family_id, strict, equality),
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


def t02_self_edge_lemma_packet_payload(
    self_edge_packet: dict[str, Any],
    template_catalog: dict[str, Any],
) -> dict[str, Any]:
    """Return the focused review-pending T02 local lemma packet."""

    if self_edge_packet.get("schema") != SELF_EDGE_TEMPLATE_PACKET_SCHEMA:
        raise ValueError("unexpected self-edge template packet schema")
    if template_catalog.get("schema") != TEMPLATE_LEMMA_CATALOG_SCHEMA:
        raise ValueError("unexpected template lemma catalog schema")

    template = _template_record(self_edge_packet)
    families = _family_records_by_id(template)
    catalog_record = _catalog_record(template_catalog)
    _assert_source_records(template, families, catalog_record)
    family_packets = [_family_packet(families[family_id]) for family_id in EXPECTED_FAMILY_IDS]

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
            "This packet isolates the multi-family T02 self-edge motif from existing review-pending n=9 diagnostics.",
            "Each family record has three local rows that force the displayed equality chain.",
            "Each family record has one vertex-circle strict inequality between the same quotient class.",
            "The packet is intended for local lemma review and proof mining, not as a theorem name.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": source_artifacts(self_edge_packet, template_catalog),
        "provenance": PROVENANCE,
    }
    assert_expected_t02_self_edge_lemma_packet(payload)
    return payload


def _family_packets_by_id(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    packets = payload.get("family_packets")
    if not isinstance(packets, list):
        raise AssertionError("family_packets must be a list")
    by_id = {
        str(packet["family_id"]): packet
        for packet in packets
        if isinstance(packet, dict) and "family_id" in packet
    }
    if set(by_id) != set(EXPECTED_FAMILY_IDS):
        raise AssertionError(f"unexpected family packet ids: {sorted(by_id)!r}")
    return {family_id: by_id[family_id] for family_id in EXPECTED_FAMILY_IDS}


def assert_expected_t02_self_edge_lemma_packet(payload: Mapping[str, Any]) -> None:
    """Assert stable constants for the focused T02 local lemma packet."""

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

    family_packets = _family_packets_by_id(payload)
    for family_id, packet in family_packets.items():
        if packet["assignment_count"] != EXPECTED_FAMILY_ASSIGNMENT_COUNTS[family_id]:
            raise AssertionError(f"{family_id} assignment count mismatch")
        if packet["orbit_size"] != EXPECTED_FAMILY_ORBIT_SIZES[family_id]:
            raise AssertionError(f"{family_id} orbit size mismatch")
        if packet["core_size"] != EXPECTED_CORE_SIZE:
            raise AssertionError(f"{family_id} core size mismatch")
        if packet["core_selected_rows"] != _normalize_rows(EXPECTED_CORE_SELECTED_ROWS[family_id]):
            raise AssertionError(f"{family_id} core rows mismatch")
        if packet["strict_inequality"] != EXPECTED_STRICT_INEQUALITIES[family_id]:
            raise AssertionError(f"{family_id} strict inequality mismatch")
        if packet["distance_equality"] != EXPECTED_DISTANCE_EQUALITIES[family_id]:
            raise AssertionError(f"{family_id} equality path mismatch")
        if packet["equality_chain"] != [list(item) for item in EXPECTED_EQUALITY_CHAINS[family_id]]:
            raise AssertionError(f"{family_id} equality chain mismatch")

        replay = packet["replay"]
        if replay["status"] != "self_edge":
            raise AssertionError(f"{family_id} replay status mismatch")
        if replay["selected_row_count"] != EXPECTED_CORE_SIZE:
            raise AssertionError(f"{family_id} selected row count mismatch")
        if replay["strict_edge_count"] != EXPECTED_STRICT_EDGE_COUNT:
            raise AssertionError(f"{family_id} strict-edge count mismatch")
        if replay["self_edge_conflict_count"] != EXPECTED_SELF_EDGE_CONFLICT_COUNT:
            raise AssertionError(f"{family_id} self-edge conflict count mismatch")
        if replay["cycle_edge_count"] != EXPECTED_CYCLE_EDGE_COUNT:
            raise AssertionError(f"{family_id} cycle-edge count mismatch")
        primary = replay["primary_self_edge_conflict"]
        strict = EXPECTED_STRICT_INEQUALITIES[family_id]
        for key in ("row", "witness_order", "outer_pair", "inner_pair"):
            if primary[key] != strict[key]:
                raise AssertionError(f"{family_id} primary conflict {key} mismatch")
        lemma = packet["local_lemma"]
        if lemma["review_status"] != "review_pending":
            raise AssertionError(f"{family_id} local lemma review status mismatch")

    if "No proof of the n=9 case is claimed." not in payload.get("interpretation", []):
        raise AssertionError("interpretation must preserve the no-proof statement")
