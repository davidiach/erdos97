from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_endpoint8_forcing_preflight import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_CONNECTOR_CONTRACT,
    DEFAULT_SOURCE_ESCAPE_PARTITION,
    GATE_STATUS,
    PRIVATE_ESCAPE_STATUS,
    assert_expected_endpoint8_forcing_preflight,
    build_endpoint8_forcing_preflight_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_connector_contract() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_CONNECTOR_CONTRACT)


@pytest.fixture(scope="module")
def source_escape_partition() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_ESCAPE_PARTITION)


def test_endpoint8_forcing_preflight_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_endpoint8_forcing_preflight(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_ENDPOINT8_FORCING_PREFLIGHT_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "does not prove endpoint-8 support existence",
        "does not prove row forcing",
        "does not prove pair [3,5] impossible",
        "does not prove n=9",
        "does not prove the bridge",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_endpoint8_forcing_preflight_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["connector_pair"] == [0, 8]
    assert summary["endpoint8_support_pairs"] == [[3, 8], [5, 8]]
    assert summary["blocking_escape_support_pairs"] == [[3, 5]]
    assert summary["connector_conditional_available"] is True
    assert summary["private_halo_only_target_row_count"] == 4
    assert summary["private_halo_only_basic_survivor_count"] == 12
    assert summary["private_halo_only_vertex_circle_survivor_count"] == 0
    assert summary["endpoint8_connector_available_basic_survivor_count"] == 16
    assert summary["gate_status"] == GATE_STATUS
    assert summary["endpoint8_forced_by_current_evidence"] is False
    assert summary["endpoint8_forcing_blocked_by_private_halo_escape"] is True
    assert summary["private_halo_escape_status"] == PRIVATE_ESCAPE_STATUS
    assert "[3,5]" in summary["next_required_lemma"]


def test_endpoint8_forcing_preflight_decision_blocks_overclaim() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    decision = payload["decision"]

    assert decision["answer"] == "do_not_accept_endpoint8_forcing_claim"
    assert decision["gate_status"] == GATE_STATUS
    assert decision["endpoint8_forced_by_current_evidence"] is False
    assert decision["can_use_connector_if_endpoint8_support_hypothesis_supplied"] is True
    assert decision["blocking_escape_support_pairs"] == [[3, 5]]
    assert decision["blocking_basic_survivor_count"] == 12


def test_endpoint8_forcing_preflight_artifact_matches_generator(
    source_connector_contract: dict[str, object],
    source_escape_partition: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_endpoint8_forcing_preflight_payload(
        source_connector_contract,
        source_escape_partition,
    )


def test_endpoint8_forcing_preflight_rejects_tampered_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["summary"]["endpoint8_forced_by_current_evidence"] = True

    errors = validate_payload(payload, recompute=False)

    assert any("endpoint8_forced_by_current_evidence" in error for error in errors)


def test_endpoint8_forcing_preflight_rejects_source_drift(
    source_connector_contract: dict[str, object],
    source_escape_partition: dict[str, object],
) -> None:
    tampered = json.loads(json.dumps(source_escape_partition))
    tampered["summary"]["connector_avoiding_basic_survivor_count"] = 0

    with pytest.raises(AssertionError, match="connector_avoiding_basic_survivor_count"):
        build_endpoint8_forcing_preflight_payload(
            source_connector_contract,
            tampered,
        )


def test_endpoint8_forcing_preflight_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_endpoint8_forcing_preflight.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["target_row_key"] == "151:6"
    assert payload["gate_status"] == GATE_STATUS
    assert payload["endpoint8_forced_by_current_evidence"] is False
