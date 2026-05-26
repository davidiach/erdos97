from __future__ import annotations

import copy
import json

import pytest

from erdos97.bootstrap_t12_81_3_chain_closure_csp import (
    DEFAULT_ARTIFACT,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_3_chain_closure_csp_payload,
)


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_3_chain_closure_csp_payload()


def test_bootstrap_t12_81_3_chain_closure_expected_payload(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == "BOOTSTRAP_T12_81_3_CHAIN_CLOSURE_CSP_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "sequential support-chain model" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope

    summary = payload["summary"]
    assert summary["scan_status"] == SCAN_STATUS
    assert summary["prefix_survivor_count"] == 4
    assert summary["supply_chain_survivor_count"] == 0


def test_bootstrap_t12_81_3_chain_closure_survivor_shapes(
    payload: dict[str, object],
) -> None:
    survivors = payload["prefix_survivors"]
    assert [record["chain_centers"] for record in survivors] == [
        [8],
        [8, 2],
        [8],
        [8],
    ]
    assert payload["supply_chain_survivors"] == []


def test_bootstrap_t12_81_3_chain_closure_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_bootstrap_t12_81_3_chain_closure_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["supply_chain_survivor_count"] = 1

    with pytest.raises(AssertionError, match="supply_chain_survivor_count"):
        assert_expected_payload(bad)
