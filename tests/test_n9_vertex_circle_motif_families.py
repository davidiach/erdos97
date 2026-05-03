from __future__ import annotations

import json
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_obstruction_shapes import (
    assert_expected_motif_family_counts,
    motif_family_summary,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n9_vertex_circle_motif_families.json"


def test_n9_vertex_circle_motif_family_artifact_counts() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_expected_motif_family_counts(payload)
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert payload["obstruction_status_counts"] == {
        "self_edge": 158,
        "strict_cycle": 26,
    }
    families = payload["dihedral_incidence_families"]
    assert families["family_count"] == 16
    assert families["orbit_size_counts"] == {"2": 5, "6": 2, "18": 9}
    assert families["status_family_counts"] == {
        "self_edge": 13,
        "strict_cycle": 3,
    }
    shapes = payload["loose_obstruction_shapes"]
    assert shapes["self_edge_shape_family_count"] == 16
    assert shapes["strict_cycle_span_family_count"] == 8


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_n9_vertex_circle_motif_family_artifact_is_current() -> None:
    checked_in = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert motif_family_summary() == checked_in
