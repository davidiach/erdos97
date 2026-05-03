from __future__ import annotations

import json
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_exhaustive import (
    EXPECTED_CROSS_CHECK_FULL,
    EXPECTED_CROSS_CHECK_NODES,
    EXPECTED_CROSS_CHECK_STATUSES,
    EXPECTED_MAIN_FULL,
    EXPECTED_MAIN_NODES,
    EXPECTED_MAIN_PRUNES,
    assert_expected_counts,
    summary_payload,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n9_vertex_circle_exhaustive.json"
pytestmark = [pytest.mark.artifact, pytest.mark.exhaustive]


@pytest.fixture(scope="module")
def n9_payload() -> dict[str, object]:
    return summary_payload()


def test_n9_vertex_circle_exhaustive_counts_match_review_artifact(
    n9_payload: dict[str, object],
) -> None:
    payload = n9_payload

    assert_expected_counts(payload)
    assert payload["trust"] == "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING"
    assert payload["main_search"]["nodes_visited"] == EXPECTED_MAIN_NODES
    assert payload["main_search"]["full_assignments"] == EXPECTED_MAIN_FULL
    assert payload["main_search"]["counts"] == EXPECTED_MAIN_PRUNES
    assert (
        payload["cross_check_without_vertex_circle_pruning"]["nodes_visited"]
        == EXPECTED_CROSS_CHECK_NODES
    )
    assert (
        payload["cross_check_without_vertex_circle_pruning"]["full_assignments"]
        == EXPECTED_CROSS_CHECK_FULL
    )
    assert (
        payload["cross_check_without_vertex_circle_pruning"]["counts"]
        == EXPECTED_CROSS_CHECK_STATUSES
    )


def test_n9_vertex_circle_exhaustive_artifact_is_current(
    n9_payload: dict[str, object],
) -> None:
    checked_in = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_expected_counts(checked_in)
    assert checked_in == n9_payload
