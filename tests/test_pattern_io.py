from __future__ import annotations

import pytest

from erdos97.pattern_io import extract_pattern_payload
from erdos97.stuck_sets import find_minimal_stuck_sets, forward_ear_order, result_to_json


TOY_ROWS = [
    [1, 2, 4, 5],
    [0, 2, 4, 5],
    [0, 1, 4, 5],
    [0, 1, 4, 5],
    [0, 1, 2, 3],
    [0, 1, 2, 3],
]


def test_extract_selected_rows_from_stuck_payload() -> None:
    payload = result_to_json(
        "toy",
        TOY_ROWS,
        find_minimal_stuck_sets(TOY_ROWS),
        forward_ear_order(TOY_ROWS),
    )

    name, rows = extract_pattern_payload(payload)

    assert name == "toy"
    assert rows == TOY_ROWS


def test_extract_selected_rows_from_nested_motif_payload() -> None:
    payload = {
        "type": "bounded_stuck_motif_search",
        "motif": {
            "pattern": "nested",
            "selected_rows": TOY_ROWS,
        },
    }

    name, rows = extract_pattern_payload(payload)

    assert name == "nested"
    assert rows == TOY_ROWS


def test_extract_selected_rows_from_zero_one_matrix() -> None:
    matrix = [
        [1 if label in row else 0 for label in range(len(TOY_ROWS))]
        for row in TOY_ROWS
    ]

    name, rows = extract_pattern_payload({"name": "matrix", "rows": matrix})

    assert name == "matrix"
    assert rows == TOY_ROWS


def test_extract_pattern_payload_rejects_missing_rows() -> None:
    with pytest.raises(ValueError, match="selected-witness pattern"):
        extract_pattern_payload({"pattern": "empty"})
