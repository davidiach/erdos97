from __future__ import annotations

from erdos97.fragile_cycle_three_halo_vertex_circle import (
    EXPECTED_ESSENTIAL_COVER_COUNT,
    EXPECTED_PLACEMENT_COUNT,
    _placement_scan,
    assert_expected_payload,
)
from erdos97.generic_vertex_search import GenericVertexSearch


def test_single_three_halo_placement_is_vertex_circle_closed() -> None:
    representatives: dict[str, dict[str, object]] = {}
    result = _placement_scan(GenericVertexSearch(10), (0, 0, 0), representatives)
    assert result["raw_row_combination_count"] == 194_481
    assert result["essential_cover_count"] == 1_476
    assert result["retained_cover_ok_count"] == 1_254
    assert result["retained_cover_self_edge_count"] == 63
    assert result["retained_cover_strict_cycle_count"] == 159
    assert result["extension_candidate_count"] == 7_445
    assert result["full_vertex_circle_survivor_count"] == 0
    assert set(representatives) == {"self_edge", "strict_cycle"}


def test_expected_constants_capture_complete_catalog() -> None:
    assert EXPECTED_PLACEMENT_COUNT == 84
    assert EXPECTED_ESSENTIAL_COVER_COUNT == 141_750


def test_assert_expected_payload_rejects_survivor() -> None:
    payload = {
        "schema": "wrong",
    }
    try:
        assert_expected_payload(payload)
    except AssertionError:
        pass
    else:
        raise AssertionError("malformed payload was accepted")
