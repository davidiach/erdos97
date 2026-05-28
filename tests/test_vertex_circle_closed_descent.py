from __future__ import annotations

import json
from pathlib import Path

from erdos97.vertex_circle_closed_descent import (
    closed_descent_cycle_to_json,
    extract_closed_descent_cycle,
)
from erdos97.vertex_circle_quotient_replay import (
    ClosedDescentRegion,
    StrictInequality,
    parse_selected_rows,
    replay_vertex_circle_quotient,
    strict_quotient_edges,
    validate_closed_descent_region,
)

ROOT = Path(__file__).resolve().parents[1]
LOCAL_CORES = ROOT / "data" / "certificates" / "n9_vertex_circle_local_cores.json"


def _strict_edge(
    outer_class: tuple[int, int],
    inner_class: tuple[int, int],
) -> StrictInequality:
    return StrictInequality(
        row=0,
        witness_order=(1, 2, 3, 4),
        outer_interval=(0, 3),
        inner_interval=(1, 2),
        outer_pair=(1, 4),
        inner_pair=(2, 3),
        outer_class=outer_class,
        inner_class=inner_class,
    )


def test_extract_closed_descent_cycle_replays_strict_cycle_core() -> None:
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
    cycle = extract_closed_descent_cycle(region)

    assert replay.status == "strict_cycle"
    assert 1 <= len(cycle) <= len(region.classes)
    assert {edge.outer_class for edge in cycle}.issubset(set(region.classes))
    for index, edge in enumerate(cycle):
        next_edge = cycle[(index + 1) % len(cycle)]
        assert edge.inner_class == next_edge.outer_class


def test_closed_descent_cycle_json_handles_reflexive_self_edge_region() -> None:
    edge = _strict_edge((4, 1), (1, 4))
    region = ClosedDescentRegion(classes=((4, 1),), witness_edges=(edge,))

    certificate = closed_descent_cycle_to_json(region)

    assert certificate["type"] == "strict_quotient_closed_descent_cycle"
    assert certificate["class_count"] == 1
    assert certificate["cycle_length"] == 1
    assert certificate["classes"] == [[1, 4]]
    assert certificate["cycle_classes"] == [[1, 4]]
    assert certificate["cycle_edges"][0]["row"] == 0


def test_extract_closed_descent_cycle_rejects_missing_witness() -> None:
    edge = _strict_edge((1, 2), (1, 2))
    region = ClosedDescentRegion(classes=((1, 2), (3, 4)), witness_edges=(edge,))

    try:
        extract_closed_descent_cycle(region)
    except ValueError as exc:
        assert "missing witness edge" in str(exc)
    else:  # pragma: no cover - defensive clarity
        raise AssertionError("incomplete closed descent region should be rejected")


def test_extract_closed_descent_cycle_rejects_leaking_witness() -> None:
    edge = _strict_edge((1, 2), (3, 4))
    region = ClosedDescentRegion(classes=((1, 2),), witness_edges=(edge,))

    try:
        extract_closed_descent_cycle(region)
    except ValueError as exc:
        assert "leaves region" in str(exc)
    else:  # pragma: no cover - defensive clarity
        raise AssertionError("leaking closed descent witness should be rejected")
