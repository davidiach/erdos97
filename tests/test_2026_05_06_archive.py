from __future__ import annotations

import json
from pathlib import Path

from erdos97.fast_vertex_search import FastVertexSearch


ROOT = Path(__file__).resolve().parents[1]
Q_L9_ARTIFACT = ROOT / "data" / "certificates" / "2026-05-06" / "q_l9_filter_results.json"
TWO_ORBIT_ARTIFACT = ROOT / "data" / "certificates" / "2026-05-06" / "two_orbit_large_m.json"


def test_q_l9_archive_uses_portable_paths_and_records_negative_scan() -> None:
    payload = json.loads(Q_L9_ARTIFACT.read_text(encoding="utf-8"))

    assert payload["summary"] == {
        "n_artifacts": 9,
        "n_blocked": 0,
        "n_pass_filter": 9,
        "threshold": 0.25,
    }
    assert payload["rows"]
    assert all("\\" not in row["file"] for row in payload["rows"])


def test_two_orbit_large_m_archive_records_no_survivors() -> None:
    payload = json.loads(TWO_ORBIT_ARTIFACT.read_text(encoding="utf-8"))

    assert payload["m_values"] == [14, 15, 16, 18, 20, 25, 30]
    for result in payload["results"].values():
        assert result["n_strictly_convex"] == 0
        assert result["survivors"] == []


def test_fast_vertex_search_smoke_row0() -> None:
    search = FastVertexSearch(9)
    result = search.search_one_row0(0, node_limit=10)

    assert search.row0_choice_count == 70
    assert result.n == 9
    assert result.row0_index == 0
    assert result.nodes_visited == 10
    assert result.aborted is True
