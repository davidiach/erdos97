from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_mro_branching_replay import (
    CLAIM_SCOPE,
    DEFAULT_ARTIFACT,
    EXPECTED_FIXED_CROSS_COUNTS,
    EXPECTED_FIXED_CROSS_FULL,
    EXPECTED_FIXED_CROSS_NODES,
    EXPECTED_FIXED_MAIN_COUNTS,
    EXPECTED_FIXED_MAIN_FULL,
    EXPECTED_FIXED_MAIN_NODES,
    assert_expected_mro_branching_replay,
    fixed_center_order_search,
    load_artifact,
    mro_branching_replay_payload,
)

ROOT = Path(__file__).resolve().parents[1]
pytestmark = [pytest.mark.artifact, pytest.mark.exhaustive]


def _payload() -> dict[str, object]:
    return load_artifact(DEFAULT_ARTIFACT)


@pytest.fixture(scope="module")
def replay_payload() -> dict[str, object]:
    return mro_branching_replay_payload(_payload())


def test_fixed_center_order_search_matches_expected_counts() -> None:
    main = fixed_center_order_search(use_vertex_circle=True)
    cross = fixed_center_order_search(use_vertex_circle=False)

    assert main["nodes_visited"] == EXPECTED_FIXED_MAIN_NODES
    assert main["full_assignments"] == EXPECTED_FIXED_MAIN_FULL
    assert main["counts"] == EXPECTED_FIXED_MAIN_COUNTS
    assert cross["nodes_visited"] == EXPECTED_FIXED_CROSS_NODES
    assert cross["full_assignments"] == EXPECTED_FIXED_CROSS_FULL
    assert cross["counts"] == EXPECTED_FIXED_CROSS_COUNTS


def test_mro_branching_replay_expected_counts_and_scope(
    replay_payload: dict[str, object],
) -> None:
    assert_expected_mro_branching_replay(replay_payload)
    assert replay_payload["validation_status"] == "passed"
    assert replay_payload["review_independence"] == {
        "uses_dynamic_mro_brancher": False,
        "uses_shared_filter_helpers": True,
        "uses_vertex_circle_status_helper": True,
        "method": (
            "Runs a separate recursive search that always picks the "
            "lowest unassigned center after row 0, then compares full "
            "assignment counts and vertex-circle classifications to the "
            "stored dynamic-MRO artifact."
        ),
    }
    comparison = replay_payload["comparison_summary"]
    assert comparison["row0_choices_match"] is True
    assert comparison["main_full_assignments_match"] is True
    assert comparison["cross_check_full_assignments_match"] is True
    assert comparison["cross_check_status_counts_match"] is True
    assert "does not prove n=9" in replay_payload["claim_scope"]
    assert "does not claim a counterexample" in replay_payload["claim_scope"]


def test_mro_branching_replay_rejects_appended_claim_scope_overclaim(
    replay_payload: dict[str, object],
) -> None:
    replay_payload = dict(replay_payload)
    replay_payload["claim_scope"] = f"{CLAIM_SCOPE} This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_mro_branching_replay(replay_payload)


def test_mro_branching_replay_rejects_dynamic_count_drift() -> None:
    artifact = copy.deepcopy(_payload())
    artifact["cross_check_without_vertex_circle_pruning"]["counts"]["self_edge"] += 1  # type: ignore[index]

    payload = mro_branching_replay_payload(artifact)

    assert payload["validation_status"] == "failed"
    assert any(
        "cross-check status counts mismatch" in error
        for error in payload["validation_errors"]
    )


def test_mro_branching_replay_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_mro_branching_replay.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    parsed = json.loads(result.stdout)
    assert parsed["validation_status"] == "passed"
    assert parsed["comparison_summary"]["cross_check_status_counts_match"] is True
