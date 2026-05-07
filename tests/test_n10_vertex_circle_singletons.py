from __future__ import annotations

import json
from pathlib import Path

import pytest

from erdos97.generic_vertex_search import GenericVertexSearch
from erdos97.n10_vertex_circle_singletons import (
    EXPECTED_COUNTS,
    EXPECTED_ROW0_CHOICES,
    EXPECTED_TOTAL_FULL,
    EXPECTED_TOTAL_NODES,
    assert_expected_payload,
    assert_generic_spot_check,
    row0_mask_for_index,
    row0_witnesses_for_index,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n10_vertex_circle_singleton_slices.json"
pytestmark = [pytest.mark.artifact, pytest.mark.exhaustive]
SELECTED_GENERIC_SPOT_CHECK_ROWS = {
    0: {
        "row0_witnesses": [1, 2, 3, 4],
        "nodes": 9759,
        "counts": {
            "partial_self_edge": 5256,
            "partial_strict_cycle": 6031,
        },
    },
    63: {
        "row0_witnesses": [2, 3, 5, 8],
        "nodes": 36084,
        "counts": {
            "partial_self_edge": 30431,
            "partial_strict_cycle": 41710,
        },
    },
    125: {
        "row0_witnesses": [6, 7, 8, 9],
        "nodes": 11020,
        "counts": {
            "partial_self_edge": 9087,
            "partial_strict_cycle": 7172,
        },
    },
}


def test_n10_singleton_artifact_expected_counts() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_expected_payload(payload)
    assert payload["trust"] == "MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING"
    assert payload["row0_choices_covered"] == EXPECTED_ROW0_CHOICES
    assert payload["total_nodes"] == EXPECTED_TOTAL_NODES
    assert payload["total_full"] == EXPECTED_TOTAL_FULL
    assert payload["counts"] == EXPECTED_COUNTS


def test_n10_selected_singletons_match_generic_checker() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    for row0_index, expected in SELECTED_GENERIC_SPOT_CHECK_ROWS.items():
        row = payload["rows"][row0_index]
        assert row["row0_witnesses"] == expected["row0_witnesses"]
        assert row["nodes"] == expected["nodes"]
        assert row["full"] == 0
        assert row["aborted"] is False
        assert row["counts"] == expected["counts"]
        assert_generic_spot_check(payload, row0_index=row0_index)


def test_n10_artifact_records_explicit_row0_witnesses() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    rows = payload["rows"]

    assert payload["row0_witnesses"][0] == [1, 2, 3, 4]
    assert payload["row0_witnesses"][-1] == [6, 7, 8, 9]
    for idx, row in enumerate(rows):
        assert row["row0_mask"] == row0_mask_for_index(idx)
        assert row["row0_witnesses"] == row0_witnesses_for_index(idx)
        assert payload["row0_witnesses"][idx] == row["row0_witnesses"]


def test_generic_checker_reproduces_n9_review_pending_counts() -> None:
    search = GenericVertexSearch(9)

    main = search.exhaustive_search(use_vertex_circle=True)
    cross_check = search.exhaustive_search(use_vertex_circle=False)

    assert main.nodes_visited == 16752
    assert main.full_assignments == 0
    assert main.counts == {
        "partial_self_edge": 11271,
        "partial_strict_cycle": 11011,
    }
    assert cross_check.nodes_visited == 100817
    assert cross_check.full_assignments == 184
    assert cross_check.counts == {
        "self_edge": 158,
        "strict_cycle": 26,
    }
