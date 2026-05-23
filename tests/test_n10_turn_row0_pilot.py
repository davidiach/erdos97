from __future__ import annotations

import pytest

from erdos97.n10_turn_row0_pilot import (
    ROW0_INDEX,
    classify_assignment,
    first_self_edge_conflict,
    validate_payload,
)

pytestmark = pytest.mark.slow


def test_known_turn_sat_escape_is_vertex_circle_self_edge() -> None:
    rows = [
        [1, 2, 3, 4],
        [0, 4, 5, 7],
        [1, 3, 5, 6],
        [2, 4, 6, 8],
        [3, 5, 8, 9],
        [0, 4, 6, 9],
        [1, 5, 7, 9],
        [0, 1, 6, 8],
        [2, 6, 7, 9],
        [0, 3, 7, 8],
    ]

    record = classify_assignment(rows, assignment_index_1based=1)

    assert ROW0_INDEX == 0
    assert record["turn_status"] == "sat"
    assert record["vertex_circle_status"] == "self_edge"
    assert record["turn_model"] == ["0", "1", "0", "0", "1", "0", "0", "1", "1", "0"]
    assert first_self_edge_conflict(rows) == {
        "row": 0,
        "witness_order": [1, 2, 3, 4],
        "outer_interval": [0, 3],
        "inner_interval": [0, 1],
        "outer_pair": [1, 4],
        "inner_pair": [1, 2],
        "outer_class": [0, 1],
        "inner_class": [0, 1],
        "outer_span": 3,
        "inner_span": 1,
        "shared_endpoint_count": 1,
        "distance_equality_path": [
            {"row": 1, "next_pair": [1, 7]},
            {"row": 7, "next_pair": [6, 7]},
            {"row": 6, "next_pair": [5, 6]},
            {"row": 5, "next_pair": [4, 5]},
            {"row": 4, "next_pair": [3, 4]},
            {"row": 3, "next_pair": [2, 3]},
            {"row": 2, "next_pair": [1, 2]},
        ],
    }


def test_tiny_payload_validation_checks_stored_fields() -> None:
    rows = [
        [1, 2, 3, 4],
        [0, 4, 5, 7],
        [1, 3, 5, 6],
        [2, 4, 6, 8],
        [3, 5, 8, 9],
        [0, 4, 6, 9],
        [1, 5, 7, 9],
        [0, 1, 6, 8],
        [2, 6, 7, 9],
        [0, 3, 7, 8],
    ]
    record = classify_assignment(rows, assignment_index_1based=1)
    payload = {
        "schema": "erdos97.n10_turn_row0_pilot.v1",
        "assignments": [record],
        "full_assignment_count": 1,
        "assignment_sha256": "wrong",
        "turn_status_counts": {"sat": 1},
        "vertex_circle_status_counts": {"self_edge": 1},
        "turn_farkas_certificate_count": 0,
        "turn_farkas_certificate_sha256": "wrong",
    }

    errors = validate_payload(payload)

    assert any("assignment_sha256 mismatch" in error for error in errors)
    assert any("turn_sat_escape_count mismatch" in error for error in errors)
    assert any("turn_sat_escape_self_edges mismatch" in error for error in errors)
