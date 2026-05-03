from __future__ import annotations

import json
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_frontier_comparison import (
    assert_expected_frontier_comparison,
    frontier_comparison_summary,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n9_vertex_circle_frontier_comparison.json"


def test_n9_vertex_circle_frontier_comparison_artifact_counts() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_expected_frontier_comparison(payload)
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    embedding_hits = {
        result["pattern"]: result["exact_core_embedding_hits"]
        for result in payload["exact_core_embedding_results"]
    }
    assert embedding_hits == {"P18_parity_balanced": 0, "C19_skew": 0}
    pattern_results = {
        result["pattern"]: result for result in payload["pattern_vertex_circle_results"]
    }
    assert pattern_results["P18_parity_balanced"]["status"] == "strict_cycle"
    assert pattern_results["P18_parity_balanced"]["core_size"] == 6
    assert pattern_results["C19_skew"]["status"] == "passes_vertex_circle_filter"


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_n9_vertex_circle_frontier_comparison_artifact_is_current() -> None:
    checked_in = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert frontier_comparison_summary() == checked_in
