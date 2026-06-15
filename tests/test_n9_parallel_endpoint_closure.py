"""Tests for the n=9 parity + parallel-endpoint combinatorial closure.

These cover the reusable filter `forced_parallel_endpoint_violation`, the
soundness anchor that the 15 n=8 survivor classes pass both filters, and the
closure of the stored 184-assignment n=9 frontier (22 parity + 162 parallel,
0 survive). No proof of n=9 or Erdos #97 is asserted here.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for sub in ("src", "scripts"):
    p = str(ROOT / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

import check_n9_parallel_endpoint_closure as closure  # noqa: E402
from erdos97.incidence_filters import (  # noqa: E402
    forced_parallel_endpoint_violation,
    odd_forced_perpendicular_cycle,
)


def test_no_two_overlap_system_passes_both() -> None:
    # All-singleton witness sets: no two rows share two witnesses, so there are
    # no forced-perpendicularity edges and neither filter fires.
    S = [[1], [2], [3], [0]]
    assert odd_forced_perpendicular_cycle(S) is None
    assert forced_parallel_endpoint_violation(S) is None


def test_star_forces_parallel_endpoint_violation() -> None:
    # Centers 0,1,2 pairwise share exactly {5,6}, so chords {0,1},{0,2},{1,2}
    # are all forced perpendicular to {5,6} (same color) and pairwise share a
    # vertex => a forced-parallel shared-endpoint obstruction. The graph is a
    # bipartite star, so the parity filter does NOT fire.
    S = [[1, 5, 6], [2, 5, 6], [3, 5, 6], [0], [1], [2], [3]]
    assert odd_forced_perpendicular_cycle(S) is None
    violation = forced_parallel_endpoint_violation(S)
    assert violation is not None
    u, v, shared = violation
    assert shared  # the two forced-parallel chords share a vertex
    assert set(shared) <= set(u) & set(v)


def _n8_survivor_rows_to_S(adjacency: list[list[int]]) -> list[list[int]]:
    return [
        sorted(j for j, val in enumerate(row) if val == 1 and j != i)
        for i, row in enumerate(adjacency)
    ]


def test_n8_survivors_pass_both_filters() -> None:
    # Soundness/regression anchor: the 15 n=8 survivor classes are incidence
    # consistent (they die only to exact metric algebra), so the two
    # necessary-condition filters must NOT kill any of them.
    path = ROOT / "data" / "incidence" / "n8_reconstructed_15_survivors.json"
    survivors = json.loads(path.read_text(encoding="utf-8"))
    killed = 0
    for entry in survivors:
        S = _n8_survivor_rows_to_S(entry["rows"])
        if odd_forced_perpendicular_cycle(S) is not None:
            killed += 1
        elif forced_parallel_endpoint_violation(S) is not None:
            killed += 1
    assert killed == 0


def test_n9_frontier_closes_with_expected_split() -> None:
    payload = closure.build_payload(ROOT)
    summary = payload["summary"]
    assert summary["total"] == 184
    assert summary["killed_by_parity_odd_cycle"] == 22
    assert summary["killed_by_parallel_endpoint"] == 162
    assert summary["survive_both"] == 0
    # every assignment carries a concrete combinatorial obstruction
    assert all(rec["obstruction"] is not None for rec in payload["assignments"])
    # assert_expected_payload agrees and does not raise
    closure.assert_expected_payload(payload)


def test_n9_witness_types_match_obstruction_labels() -> None:
    # Re-derive the raw filter outputs for one parity-killed and one
    # parallel-killed assignment and confirm they match the recorded label.
    frontier = json.loads(
        (
            ROOT / "data" / "certificates"
            / "n9_vertex_circle_frontier_motif_classification.json"
        ).read_text(encoding="utf-8")
    )
    by_id = {a["assignment_id"]: a for a in frontier["assignments"]}
    payload = closure.build_payload(ROOT)
    seen_parity = seen_parallel = False
    for rec in payload["assignments"]:
        S = closure.selected_rows_to_S(by_id[rec["assignment_id"]]["selected_rows"], 9)
        odd = odd_forced_perpendicular_cycle(S)
        par = forced_parallel_endpoint_violation(S)
        if rec["obstruction"] == "parity_odd_cycle":
            assert odd is not None
            seen_parity = True
        elif rec["obstruction"] == "parallel_endpoint":
            assert odd is None and par is not None
            seen_parallel = True
    assert seen_parity and seen_parallel


@pytest.mark.artifact
def test_stored_artifact_is_fresh() -> None:
    payload = closure.build_payload(ROOT)
    closure.compare_artifact(payload, closure.DEFAULT_OUT)
