from __future__ import annotations

import pytest

from erdos97.stuck_motif_search import (
    MotifSearchConfig,
    _non_sat_status,
    mine_stuck_motif,
    search_result_to_json,
)


def test_mine_stuck_motif_finds_strict_small_model() -> None:
    result = mine_stuck_motif(MotifSearchConfig(n=9, stuck_size=4, max_models=5))
    payload = search_result_to_json(result)

    assert result.status == "FOUND"
    assert 1 <= result.models_checked <= 5
    assert payload["motif"]["key_peeling_status"] == "STUCK_SET_FOUND"
    assert payload["motif"]["filters"]["adjacent_two_overlap_violations"] == []
    assert payload["motif"]["filters"]["crossing_bisector_violations"] == []
    assert payload["motif"]["filters"]["rectangle_trap_4_cycles"] == 0
    assert payload["motif"]["filters"]["radius_propagation"]["status"] == "PASS_ACYCLIC_CHOICE"
    assert payload["motif"]["filters"]["fragile_cover"]["cover_stats"]["cover_exists"] is True


def test_mine_stuck_motif_relaxed_model_records_search_contract() -> None:
    config = MotifSearchConfig(
        n=8,
        stuck_size=4,
        max_models=5,
        require_adjacent_overlap=False,
        require_crossing=False,
        require_no_odd_cycle=False,
        require_no_rectangle_trap=False,
        require_radius_pass=False,
        require_fragile_cover=False,
    )

    payload = search_result_to_json(mine_stuck_motif(config))

    assert payload["status"] == "FOUND"
    assert payload["fixed_stuck_vertices"] == [0, 1, 2, 3]
    assert payload["filters_required"]["require_crossing"] is False
    assert payload["filters_required"]["require_no_rectangle_trap"] is False
    assert payload["motif"]["motif_search"]["stuck_vertices_forced"] == [0, 1, 2, 3]


def test_mine_stuck_motif_can_require_no_forward_ear_order() -> None:
    result = mine_stuck_motif(
        MotifSearchConfig(
            n=11,
            stuck_size=4,
            max_models=160,
            variable_prefix="test_no_forward_11",
            require_no_forward_ear_order=True,
        )
    )
    payload = search_result_to_json(result)

    assert result.status == "FOUND"
    assert payload["filters_required"]["require_no_forward_ear_order"] is True
    assert payload["motif"]["forward_ear_order"]["exists"] is False


def test_motif_search_rejects_invalid_stuck_size() -> None:
    with pytest.raises(ValueError, match="stuck_size"):
        mine_stuck_motif(MotifSearchConfig(n=9, stuck_size=3))


def test_motif_search_status_keeps_unknown_separate_from_unsat() -> None:
    class FakeZ3:
        sat = "sat"
        unsat = "unsat"

    assert _non_sat_status("sat", checked=0, z3_module=FakeZ3) is None
    assert _non_sat_status("unsat", checked=0, z3_module=FakeZ3) == "UNSAT"
    assert _non_sat_status("unsat", checked=3, z3_module=FakeZ3) == "EXHAUSTED"
    assert _non_sat_status("unknown", checked=0, z3_module=FakeZ3) == "UNKNOWN"
