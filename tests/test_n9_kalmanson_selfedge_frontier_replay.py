from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_n9_kalmanson_selfedge_frontier_replay.py"


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_n9_kalmanson_selfedge_frontier_replay",
        SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload():
    checker = load_checker()
    return checker, checker.build_result(9)


@pytest.mark.artifact
def test_n9_kalmanson_selfedge_frontier_replay_expected_payload(payload):
    checker, result = payload

    checker.assert_expected_payload(result)
    assert result["terminal_assignments_after_filters"] == 184
    assert result["terminal_assignments_killed_by_kalmanson_self_edge"] == 184
    assert result["unkilled_terminal_assignments"] == 0
    assert (
        result["frontier_assignment_sha256"]
        == "dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55"
    )
    assert result["review_independence"]["regenerates_frontier"] is True


@pytest.mark.artifact
def test_n9_kalmanson_selfedge_frontier_replay_rejects_claim_scope_append(payload):
    checker, result = payload
    edited = dict(result)
    edited["claim_scope"] = checker.CLAIM_SCOPE + " This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope"):
        checker.assert_expected_payload(edited)
