from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_3_rich_triple_contract import (
    DEFAULT_ARTIFACT,
    ESCAPE_STATUS,
    LOCAL_CONDITIONAL_STATUS,
    RICH_CLASS_EXISTENCE_STATUS,
    RICH_TRIPLE_GAP,
    assert_expected_payload,
    build_t12_81_3_rich_triple_contract_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_81_3_rich_triple_contract_counts_and_scope() -> None:
    payload = build_t12_81_3_rich_triple_contract_payload()

    assert_expected_payload(payload)
    assert payload["status"] == "BOOTSTRAP_T12_81_3_RICH_TRIPLE_CONTRACT_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "does not prove the rich class exists" in claim_scope
    assert "does not prove row forcing" in claim_scope
    assert "does not prove n=9" in claim_scope
    assert "does not claim a counterexample" in claim_scope


def test_81_3_rich_triple_contract_summary() -> None:
    payload = build_t12_81_3_rich_triple_contract_payload()
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:3"
    assert summary["source_record_ids"] == [81]
    assert summary["target_row_center"] == 3
    assert summary["target_witnesses"] == [0, 1, 4, 6]
    assert summary["deletion_seed"] == [0, 1, 4]
    assert summary["connector_pair"] == [0, 1]
    assert summary["connector_distance_pairs"] == [[1, 3], [0, 3]]
    assert summary["connector_forcing_triples"] == [[0, 1, 4], [0, 1, 6]]
    assert summary["connector_avoiding_activation_triples"] == [
        [0, 4, 6],
        [1, 4, 6],
    ]
    assert summary["seed_activation_triple"] == [0, 1, 4]
    assert summary["seed_activation_forces_connector"]
    assert not summary["full_row_forcing_required_for_connector"]
    assert summary["local_conditional_lemma_status"] == LOCAL_CONDITIONAL_STATUS
    assert summary["rich_class_existence_status"] == RICH_CLASS_EXISTENCE_STATUS
    assert summary["escape_status"] == ESCAPE_STATUS
    assert summary["rich_triple_gap_type"] == RICH_TRIPLE_GAP


def test_81_3_rich_triple_contract_local_lemma_is_conditional() -> None:
    payload = build_t12_81_3_rich_triple_contract_payload()
    lemma = payload["local_conditional_lemma"]

    assert lemma["status"] == "EXACT_LOCAL_CONDITIONAL"
    assert "contains witnesses 0 and 1" in lemma["hypothesis"]
    assert lemma["conclusion"] == "The selected-distance equality [1,3]=[0,3] holds."
    assert "|p_3-p_1|=|p_3-p_0|" in lemma["proof"]
    assert any("does not prove any rich class" in item for item in lemma["non_claims"])
    assert any("does not prove the full fixed row" in item for item in lemma["non_claims"])


def test_81_3_rich_triple_activation_triples_partition_escape() -> None:
    payload = build_t12_81_3_rich_triple_contract_payload()
    activation = payload["activation_triple_analysis"]

    assert activation["all_witness_triples"] == [
        [0, 1, 4],
        [0, 1, 6],
        [0, 4, 6],
        [1, 4, 6],
    ]
    assert activation["connector_forcing_triples"] == [[0, 1, 4], [0, 1, 6]]
    assert activation["connector_avoiding_activation_triples"] == [
        [0, 4, 6],
        [1, 4, 6],
    ]
    assert activation["seed_activation_uses_connector_pair"]
    assert not activation["seed_activation_uses_outside_witness_6"]
    assert activation["connector_avoiding_triples_all_use_outside_witness_6"]

    forcing = activation["connector_forcing_triples"]
    avoiding = activation["connector_avoiding_activation_triples"]
    assert all(0 in triple and 1 in triple for triple in forcing)
    assert all(not (0 in triple and 1 in triple) for triple in avoiding)
    assert all(6 in triple for triple in avoiding)


def test_81_3_rich_triple_escape_mechanism_names_next_target() -> None:
    payload = build_t12_81_3_rich_triple_contract_payload()
    escape = payload["escape_mechanism"]

    assert escape["status"] == ESCAPE_STATUS
    assert "avoid containing witnesses 0 and 1 together" in escape["escape_condition"]
    assert escape["available_connector_avoiding_triples_in_fixed_row"] == [
        [0, 4, 6],
        [1, 4, 6],
    ]
    assert escape["outside_label_required_before_connector_avoiding_activation"] == 6
    assert "[0,1,4]" in escape["why_label_6_matters"]
    assert "Order-resolved rich-class closure" in escape["next_target"]


def test_81_3_rich_triple_source_closure_target_matches_previous_packet() -> None:
    payload = build_t12_81_3_rich_triple_contract_payload()
    source = payload["source_closure_target"]

    assert source["source_schema"] == "erdos97.bootstrap_t12_81_3_closure_target.v1"
    assert source["source_status"] == "BOOTSTRAP_T12_81_3_CLOSURE_TARGET_DIAGNOSTIC_ONLY"
    assert source["target_row_key"] == "81:3"
    assert source["target_row_center"] == 3
    assert source["required_connector_pair"] == [0, 1]
    assert source["t12_connector_pair_chain"] == [[1, 3], [0, 3]]
    assert source["row_forcing_gap_type"] == "FIXED_FULL_ROW_CLOSURE_NOT_RICH_CLASS_FORCING"
    assert source["relation_requirement_id"] == "81:3:connector:2:0"


def test_81_3_rich_triple_artifact_matches_generator() -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == build_t12_81_3_rich_triple_contract_payload()


def test_81_3_rich_triple_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_rich_triple_contract.py",
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
    assert payload["summary"]["target_row_key"] == "81:3"
    assert payload["summary"]["escape_status"] == ESCAPE_STATUS


def test_81_3_rich_triple_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "bootstrap_t12_81_3_rich_triple_contract.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_rich_triple_contract.py",
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
            "scripts/check_bootstrap_t12_81_3_rich_triple_contract.py",
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


def test_81_3_rich_triple_expected_payload_rejects_drift() -> None:
    payload = build_t12_81_3_rich_triple_contract_payload()
    bad = copy.deepcopy(payload)
    bad["summary"]["connector_pair"] = [0, 4]

    with pytest.raises(AssertionError, match="connector_pair"):
        assert_expected_payload(bad)
