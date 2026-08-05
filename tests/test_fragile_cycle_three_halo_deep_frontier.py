from __future__ import annotations

from pathlib import Path

from erdos97.fragile_cycle_three_halo_deep_frontier import (
    EXPECTED_DEEP_FRONTIER_SHA256,
    EXPECTED_DEPTH_STATUS_PROFILE,
    _counts_for_assignment,
    _option_rejection_ledger,
    assert_expected_payload,
)
from erdos97.generic_vertex_search import GenericVertexSearch
from erdos97.json_io import load_json
from erdos97.vertex_circle_quotient_replay import (
    SelectedRow,
    replay_vertex_circle_quotient,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_three_halo_deep_frontier.json"
)


def _payload() -> dict[str, object]:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    return payload


def _assignment(raw_rows: list[list[int]]) -> dict[int, int]:
    return {
        row[0]: sum(1 << witness for witness in row[1:]) for row in raw_rows
    }


def test_stored_deep_frontier_matches_expected() -> None:
    payload = _payload()
    assert_expected_payload(payload)
    assert payload["depth_status_profile"] == EXPECTED_DEPTH_STATUS_PROFILE
    assert payload["deep_frontier_catalog_sha256"] == EXPECTED_DEEP_FRONTIER_SHA256


def test_first_incidence_dead_state_rejects_all_center_rows() -> None:
    payload = _payload()
    states = payload["deep_frontier_states"]
    assert isinstance(states, list)
    state = next(row for row in states if row["terminal_type"] == "incidence_dead_end")
    engine = GenericVertexSearch(10)
    assignment = _assignment(state["selected_rows_natural_order"])
    columns, pairs = _counts_for_assignment(engine, assignment)
    center = state["certificate_center_natural_order"]
    ledger = _option_rejection_ledger(engine, center, assignment, columns, pairs)
    assert ledger == state["option_rejection_ledger"]
    assert ledger["row_intersection_or_crossing"] == 126
    assert ledger["viable"] == 0


def test_first_minimum_core_replays_independently() -> None:
    payload = _payload()
    cores = payload["minimum_obstruction_cores"]
    assert isinstance(cores, list)
    core = cores[0]
    rows = [
        SelectedRow(
            center=row[0],
            witnesses=(row[1], row[2], row[3], row[4]),
        )
        for row in core["selected_rows"]
    ]
    replay = replay_vertex_circle_quotient(10, tuple(range(10)), rows)
    assert len(rows) == 3
    assert replay.status == core["status"]
    assert replay.obstructed
