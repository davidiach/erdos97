from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

from erdos97.vertex_circle_quotient_replay import (
    RichClassRow,
    replay_vertex_circle_rich_quotient,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_n10_q2_rich_vertex_circle import (  # noqa: E402
    N,
    ORDER,
    assert_expected_payload,
    build_payload,
    dihedral_representatives,
)


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    return build_payload()


def test_dihedral_representatives_are_pinned() -> None:
    assert dihedral_representatives(2, N) == (
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (0, 5),
    )


def test_expected_payload_counts(payload: dict[str, Any]) -> None:
    assert_expected_payload(payload)

    summary = payload["summary"]
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert summary["complete_assignments_found"] == 0
    assert summary["total_nodes_visited"] == 320924
    assert (
        summary["max_size_five_centers_surviving_support_plus_vertex_circle_filters"]
        == 1
    )
    assert (
        summary["min_exact_four_only_centers_surviving_support_plus_vertex_circle_filters"]
        == 9
    )


def test_first_obstruction_matches_shared_rich_replay(payload: dict[str, Any]) -> None:
    representative_results = payload["representative_results"]
    obstruction = representative_results["0,1"]["first_obstruction"]
    partial_rows = obstruction["partial_rows"]

    rows = [
        RichClassRow(center=int(center), witnesses=tuple(witnesses))
        for center, witnesses in sorted(partial_rows.items())
    ]
    result = replay_vertex_circle_rich_quotient(N, ORDER, rows)

    assert result.status == obstruction["status"]
    assert result.obstructed
