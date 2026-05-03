from __future__ import annotations

import json
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_obstruction_shapes import (
    assert_expected_local_core_counts,
    local_core_summary,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n9_vertex_circle_local_cores.json"


def test_n9_vertex_circle_local_core_artifact_counts() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_expected_local_core_counts(payload)
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert payload["family_count"] == 16
    assert payload["core_size_counts"] == {"3": 5, "4": 6, "5": 2, "6": 3}
    assert payload["status_core_size_counts"] == {
        "self_edge": {"3": 5, "4": 4, "5": 2, "6": 2},
        "strict_cycle": {"4": 2, "6": 1},
    }
    assert payload["max_core_size"] == 6


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_n9_vertex_circle_local_core_artifact_is_current() -> None:
    checked_in = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert local_core_summary() == checked_in
