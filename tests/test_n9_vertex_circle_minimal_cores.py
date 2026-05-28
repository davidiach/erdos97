from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n9_vertex_circle_minimal_cores.json"


def test_n9_vertex_circle_minimal_core_summary_counts() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["schema"] == "erdos97.n9_vertex_circle_minimal_cores.v1"
    assert payload["trust"] == "INDEPENDENT_FINITE_CASE_DIAGNOSTIC_NO_GLOBAL_CLAIM"
    assert payload["frontier_systems"] == 184
    assert payload["frontier_systems_covered_by_a_minimal_core"] == 184
    assert payload["coverage_complete"] is True
    assert payload["distinct_minimal_cores"] == 219
    assert payload["minimal_core_size_counts"] == {
        "3": 105,
        "4": 106,
        "5": 7,
        "6": 1,
    }
    assert payload["minimal_core_status_counts"] == {
        "self_edge": 36,
        "strict_cycle": 183,
    }
    assert payload["isolated_recheck_mismatches"] == 0
