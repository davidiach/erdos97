from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_151_6_outside_pair_connector_contract import (
    CONNECTOR_CONTRACT_GAP,
    DEFAULT_ARTIFACT,
    ESCAPE_STATUS,
    LOCAL_CONDITIONAL_STATUS,
    RICH_SUPPORT_EXISTENCE_STATUS,
    assert_expected_payload,
    build_t12_151_6_outside_pair_connector_contract_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_151_6_outside_pair_connector_contract_counts_and_scope() -> None:
    payload = build_t12_151_6_outside_pair_connector_contract_payload()

    assert_expected_payload(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_CONNECTOR_CONTRACT_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "does not prove support existence" in claim_scope
    assert "does not prove row forcing" in claim_scope
    assert "does not prove n=9" in claim_scope
    assert "does not claim a counterexample" in claim_scope


def test_151_6_outside_pair_connector_contract_summary() -> None:
    payload = build_t12_151_6_outside_pair_connector_contract_payload()
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["source_record_ids"] == [151]
    assert summary["target_row_center"] == 6
    assert summary["target_witnesses"] == [0, 3, 5, 8]
    assert summary["bootstrap_core_witnesses"] == [0]
    assert summary["connector_pair"] == [0, 8]
    assert summary["connector_distance_pairs"] == [[0, 6], [8, 6]]
    assert summary["outside_support_pairs"] == [[3, 5], [3, 8], [5, 8]]
    assert summary["connector_forcing_support_pairs"] == [[3, 8], [5, 8]]
    assert summary["connector_avoiding_support_pairs"] == [[3, 5]]
    assert summary["ledger_hit_support_pairs"] == [[3, 8], [5, 8]]
    assert summary["private_halo_only_support_pairs"] == [[3, 5]]
    assert summary["support_pair_count"] == 3
    assert summary["connector_forcing_support_pair_count"] == 2
    assert summary["connector_avoiding_support_pair_count"] == 1
    assert not summary["full_row_forcing_required_for_connector"]
    assert summary["local_conditional_lemma_status"] == LOCAL_CONDITIONAL_STATUS
    assert summary["rich_support_existence_status"] == RICH_SUPPORT_EXISTENCE_STATUS
    assert summary["escape_status"] == ESCAPE_STATUS
    assert summary["connector_contract_gap_type"] == CONNECTOR_CONTRACT_GAP
    assert (
        summary["row_forcing_gap_type"]
        == "OUTSIDE_PAIR_SUPPORT_NEEDS_CONNECTOR_ROW_FORCING"
    )


def test_151_6_outside_pair_connector_contract_local_lemma() -> None:
    payload = build_t12_151_6_outside_pair_connector_contract_payload()
    lemma = payload["local_conditional_lemma"]

    assert lemma["status"] == "EXACT_LOCAL_CONDITIONAL"
    assert "contains witnesses 0 and 8" in lemma["hypothesis"]
    assert lemma["conclusion"] == "The selected-distance equality [0,6]=[8,6] holds."
    assert "|p_6-p_0|=|p_6-p_8|" in lemma["proof"]
    assert any("does not prove any rich class" in item for item in lemma["non_claims"])
    assert any("does not prove either endpoint-8" in item for item in lemma["non_claims"])


def test_151_6_outside_pair_partition_names_escape() -> None:
    payload = build_t12_151_6_outside_pair_connector_contract_payload()
    partition = payload["outside_pair_partition"]

    assert partition["status"] == ESCAPE_STATUS
    assert partition["connector_forcing_support_pairs"] == [[3, 8], [5, 8]]
    assert partition["connector_avoiding_support_pairs"] == [[3, 5]]
    assert partition["ledger_hit_support_pairs"] == [[3, 8], [5, 8]]
    assert partition["private_halo_only_support_pairs"] == [[3, 5]]

    records = partition["records"]
    assert [record["support_pair"] for record in records] == [
        [3, 5],
        [3, 8],
        [5, 8],
    ]
    assert [record["activation_witnesses"] for record in records] == [
        [0, 3, 5],
        [0, 3, 8],
        [0, 5, 8],
    ]
    assert [record["contains_connector_pair"] for record in records] == [
        False,
        True,
        True,
    ]
    assert records[0]["connector_role"] == "connector_avoiding_escape_support"
    assert records[1]["connector_role"] == "connector_forcing_support"
    assert records[2]["connector_role"] == "connector_forcing_support"


def test_151_6_outside_pair_escape_mechanism_names_next_target() -> None:
    payload = build_t12_151_6_outside_pair_connector_contract_payload()
    escape = payload["escape_mechanism"]

    assert escape["status"] == ESCAPE_STATUS
    assert "avoid endpoint 8" in escape["escape_condition"]
    assert escape["connector_avoiding_support_pairs"] == [[3, 5]]
    assert escape["connector_avoiding_activation_witnesses"] == [[0, 3, 5]]
    assert "unique outside-pair support" in escape["why_pair_3_5_matters"]
    assert "endpoint-8 outside support" in escape["next_target"]


def test_151_6_outside_pair_source_packets_match() -> None:
    payload = build_t12_151_6_outside_pair_connector_contract_payload()
    source_outside = payload["source_outside_pair_packet"]
    source_relation = payload["source_relation_sufficient_packet"]

    assert source_outside["source_schema"] == "erdos97.bootstrap_t12_outside_pair.v1"
    assert source_outside["target_row_key"] == "151:6"
    assert source_outside["source_record_id"] == 151
    assert source_outside["row_center"] == 6
    assert source_outside["support_pairs"] == [[3, 5], [3, 8], [5, 8]]
    assert source_outside["ledger_private_pair_support_hit_count"] == 2
    assert source_outside["row_center_private_in_all_deletion_closures"]

    assert (
        source_relation["source_schema"]
        == "erdos97.bootstrap_t12_relation_sufficient_rows.v1"
    )
    assert source_relation["target_row_key"] == "151:6"
    assert source_relation["requirement_id"] == "151:6:connector:2:0"
    assert source_relation["required_witnesses"] == [0, 8]
    assert source_relation["relation_state"] == "SUPPORT_SUFFICIENT"
    assert source_relation["missing_from_bootstrap_core"] == [8]
    assert source_relation["support_sufficient_count"] == 2


def test_151_6_outside_pair_connector_contract_artifact_matches_generator() -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == build_t12_151_6_outside_pair_connector_contract_payload()


def test_151_6_outside_pair_connector_contract_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_outside_pair_connector_contract.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    payload = json.loads(result.stdout)
    assert payload["summary"]["target_row_key"] == "151:6"
    assert payload["summary"]["escape_status"] == ESCAPE_STATUS


def test_151_6_outside_pair_connector_contract_write_check_out(
    tmp_path: Path,
) -> None:
    out = tmp_path / "bootstrap_t12_151_6_outside_pair_connector_contract.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_outside_pair_connector_contract.py",
            "--write",
            "--assert-expected",
            "--artifact",
            str(out),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_outside_pair_connector_contract.py",
            "--check",
            "--assert-expected",
            "--artifact",
            str(out),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )


def test_151_6_outside_pair_connector_contract_rejects_drift() -> None:
    payload = build_t12_151_6_outside_pair_connector_contract_payload()
    bad = copy.deepcopy(payload)
    bad["summary"]["connector_pair"] = [0, 3]

    with pytest.raises(AssertionError, match="connector_pair"):
        assert_expected_payload(bad)
