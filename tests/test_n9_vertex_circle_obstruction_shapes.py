from __future__ import annotations

import json
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_obstruction_shapes import (
    assert_expected_counts,
    obstruction_shape_summary,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n9_vertex_circle_obstruction_shapes.json"


def test_n9_vertex_circle_obstruction_shape_artifact_counts() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_expected_counts(payload)
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert payload["obstruction_status_counts"] == {
        "self_edge": 158,
        "strict_cycle": 26,
    }
    assert payload["strict_cycle_summary"]["cycle_length_counts"] == {
        "2": 22,
        "3": 4,
    }
    assert payload["self_edge_summary"]["max_equality_path_length"] == 8


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_n9_vertex_circle_obstruction_shape_artifact_is_current() -> None:
    checked_in = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert obstruction_shape_summary() == checked_in
