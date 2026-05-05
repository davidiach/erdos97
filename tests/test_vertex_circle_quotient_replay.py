from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from erdos97.search import built_in_patterns
from erdos97.vertex_circle_order_filter import vertex_circle_order_obstruction
from erdos97.vertex_circle_quotient_replay import (
    parse_selected_rows,
    replay_local_core_bundle,
    replay_vertex_circle_quotient,
)


ROOT = Path(__file__).resolve().parents[1]
LOCAL_CORES = ROOT / "data" / "certificates" / "n9_vertex_circle_local_cores.json"

P18_CROSSING_COMPATIBLE_ORDER = [
    0,
    8,
    4,
    15,
    1,
    5,
    11,
    9,
    3,
    7,
    17,
    13,
    2,
    6,
    14,
    10,
    16,
    12,
]

C19_VERTEX_CIRCLE_ACYCLIC_ORDER = [
    18,
    10,
    7,
    17,
    6,
    3,
    5,
    9,
    14,
    11,
    2,
    13,
    4,
    16,
    12,
    15,
    0,
    8,
    1,
]


def test_replay_all_n9_local_cores_match_recorded_statuses() -> None:
    payload = json.loads(LOCAL_CORES.read_text(encoding="utf-8"))

    replays = replay_local_core_bundle(payload)

    assert len(replays) == payload["family_count"] == 16
    assert all(replay.status_matches_expected for replay in replays)
    assert Counter(replay.result.status for replay in replays) == {
        "self_edge": 13,
        "strict_cycle": 3,
    }
    assert max(replay.result.selected_row_count for replay in replays) == 6


def test_first_n9_local_core_replays_the_expected_self_edge() -> None:
    payload = json.loads(LOCAL_CORES.read_text(encoding="utf-8"))
    replay = replay_local_core_bundle(payload)[0]

    assert replay.family_id == "F01"
    assert replay.result.status == "self_edge"
    assert replay.result.self_edge_conflicts
    conflict = replay.result.self_edge_conflicts[0]
    assert conflict.row == 0
    assert conflict.outer_pair == (1, 8)
    assert conflict.inner_pair == (1, 2)
    assert conflict.outer_class == conflict.inner_class


def test_full_pattern_replay_matches_existing_vertex_circle_filter() -> None:
    pattern = built_in_patterns()["P18_parity_balanced"]
    rows = parse_selected_rows(pattern.S)

    replay = replay_vertex_circle_quotient(
        len(pattern.S),
        P18_CROSSING_COMPATIBLE_ORDER,
        rows,
    )
    existing = vertex_circle_order_obstruction(
        pattern.S,
        P18_CROSSING_COMPATIBLE_ORDER,
        pattern.name,
    )

    assert replay.status == "strict_cycle"
    assert replay.strict_edge_count == existing.strict_edge_count == 162
    assert len(replay.cycle_edges) == len(existing.cycle_edges)


def test_replay_allows_known_c19_vertex_circle_survivor_order() -> None:
    pattern = built_in_patterns()["C19_skew"]
    rows = parse_selected_rows(pattern.S)

    replay = replay_vertex_circle_quotient(
        len(pattern.S),
        C19_VERTEX_CIRCLE_ACYCLIC_ORDER,
        rows,
    )

    assert replay.status == "ok"
    assert not replay.obstructed
    assert replay.strict_edge_count == 171
