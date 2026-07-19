from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "independent_n9_vertex_circle_recheck.py"


def load_rechecker():
    spec = importlib.util.spec_from_file_location(
        "independent_n9_vertex_circle_recheck",
        SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def independent_frontier():
    rechecker = load_rechecker()
    return rechecker, rechecker.enumerate_frontier()


@pytest.mark.artifact
def test_independent_frontier_has_kalmanson_self_edge_at_every_assignment(
    independent_frontier,
) -> None:
    rechecker, frontier = independent_frontier

    kinds = Counter(rechecker.kalmanson_self_edge_kind(rows) for rows in frontier)

    assert len(frontier) == 184
    assert rechecker.frontier_digest(frontier) == rechecker.EXPECTED_FRONTIER_SHA256
    assert kinds[None] == 0
    assert {kind: kinds[kind] for kind in ("K1", "K2")} == (
        rechecker.EXPECTED_KALMANSON_KIND_COUNTS
    )
