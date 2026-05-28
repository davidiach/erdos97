from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from erdos97.search import built_in_patterns
from erdos97.vertex_circle_order_filter import vertex_circle_order_obstruction
from erdos97.vertex_circle_quotient_replay import (
    RichClassRow,
    StrictInequality,
    parse_selected_rows,
    replay_local_core_bundle,
    replay_vertex_circle_rich_quotient,
    replay_vertex_circle_quotient,
    strict_quotient_edges,
    strict_rich_quotient_edges,
    validate_closed_descent_region,
)


ROOT = Path(__file__).resolve().parents[1]
LOCAL_CORES = ROOT / "data" / "certificates" / "n9_vertex_circle_local_cores.json"
RICH_PROJECTION_PILOT = (
    ROOT / "data" / "certificates" / "n9_radius_blocker_rich_projection_pilot.json"
)

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


def test_compact_selected_rows_parse_with_explicit_centers() -> None:
    rows = parse_selected_rows(
        [
            [0, 1, 2, 3, 8],
            [1, 0, 2, 4, 7],
            [8, 0, 1, 4, 5],
        ]
    )

    assert [row.center for row in rows] == [0, 1, 8]
    assert rows[0].witnesses == (1, 2, 3, 8)


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


def test_closed_descent_region_validates_cycle_certificate() -> None:
    payload = json.loads(LOCAL_CORES.read_text(encoding="utf-8"))
    certificate = next(
        item for item in payload["certificates"] if item["status"] == "strict_cycle"
    )
    rows = parse_selected_rows(certificate["core_selected_rows"])
    replay = replay_vertex_circle_quotient(payload["n"], payload["cyclic_order"], rows)
    edges = strict_quotient_edges(payload["n"], payload["cyclic_order"], rows)

    region = validate_closed_descent_region(
        edges,
        [edge.outer_class for edge in replay.cycle_edges],
    )

    assert replay.status == "strict_cycle"
    assert region.classes == tuple(sorted({edge.outer_class for edge in replay.cycle_edges}))
    assert len(region.witness_edges) == len(region.classes)
    assert all(edge.inner_class in set(region.classes) for edge in region.witness_edges)


def test_closed_descent_region_rejects_sink_class() -> None:
    pattern = built_in_patterns()["C19_skew"]
    rows = parse_selected_rows(pattern.S)
    edges = strict_quotient_edges(
        len(pattern.S),
        C19_VERTEX_CIRCLE_ACYCLIC_ORDER,
        rows,
    )

    sink = min({edge.inner_class for edge in edges} - {edge.outer_class for edge in edges})

    try:
        validate_closed_descent_region(edges, [sink])
    except ValueError as exc:
        assert "sink class" in str(exc)
    else:  # pragma: no cover - defensive clarity
        raise AssertionError("sink-only descent region should be rejected")


def test_closed_descent_region_normalizes_supplied_edge_classes() -> None:
    edge = StrictInequality(
        row=0,
        witness_order=(1, 2, 3, 4),
        outer_interval=(0, 3),
        inner_interval=(1, 2),
        outer_pair=(1, 4),
        inner_pair=(2, 3),
        outer_class=(4, 1),
        inner_class=(4, 1),
    )

    region = validate_closed_descent_region([edge], [(1, 4)])

    assert region.classes == ((1, 4),)
    assert region.witness_edges == (edge,)


def test_rich_quotient_matches_exact_four_selected_rows() -> None:
    pattern = built_in_patterns()["P18_parity_balanced"]
    rows = parse_selected_rows(pattern.S)
    rich_rows = [
        RichClassRow(center=row.center, witnesses=row.witnesses)
        for row in rows
    ]

    selected_replay = replay_vertex_circle_quotient(
        len(pattern.S),
        P18_CROSSING_COMPATIBLE_ORDER,
        rows,
    )
    rich_replay = replay_vertex_circle_rich_quotient(
        len(pattern.S),
        P18_CROSSING_COMPATIBLE_ORDER,
        rich_rows,
    )

    assert rich_replay.status == selected_replay.status == "strict_cycle"
    assert rich_replay.strict_edge_count == selected_replay.strict_edge_count
    assert len(rich_replay.cycle_edges) == len(selected_replay.cycle_edges)


def test_rich_quotient_obstructs_size_five_projection_pilot_classes() -> None:
    payload = json.loads(RICH_PROJECTION_PILOT.read_text(encoding="utf-8"))
    rich_rows = [
        RichClassRow(center=center, witnesses=tuple(center_classes[0]))
        for center, center_classes in enumerate(payload["projected_rich_classes"])
    ]

    replay = replay_vertex_circle_rich_quotient(9, payload["summary"]["order"], rich_rows)

    assert replay.status == "self_edge"
    assert replay.strict_edge_count == 225
    assert replay.self_edge_conflicts
    assert replay.self_edge_conflicts[0].row == 0


def test_closed_descent_region_accepts_rich_self_edge_certificate() -> None:
    payload = json.loads(RICH_PROJECTION_PILOT.read_text(encoding="utf-8"))
    rich_rows = [
        RichClassRow(center=center, witnesses=tuple(center_classes[0]))
        for center, center_classes in enumerate(payload["projected_rich_classes"])
    ]
    replay = replay_vertex_circle_rich_quotient(9, payload["summary"]["order"], rich_rows)
    edges = strict_rich_quotient_edges(9, payload["summary"]["order"], rich_rows)
    conflict = replay.self_edge_conflicts[0]

    region = validate_closed_descent_region(edges, [conflict.outer_class])

    assert replay.status == "self_edge"
    assert region.classes == (conflict.outer_class,)
    assert len(region.witness_edges) == 1
    assert region.witness_edges[0].outer_class == conflict.outer_class
    assert region.witness_edges[0].inner_class == conflict.outer_class


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
