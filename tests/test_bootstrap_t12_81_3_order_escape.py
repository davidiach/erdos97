from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_3_order_escape import (
    DEFAULT_ARTIFACT,
    FIXED_SINGLETON_ORDER_STATUS,
    GENUINE_ESCAPE_STATUS,
    ORDER_ESCAPE_GAP,
    PRE_3_LABEL_6_SUPPLY_STATUS,
    assert_expected_payload,
    build_t12_81_3_order_escape_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_81_3_order_escape_counts_and_scope() -> None:
    payload = build_t12_81_3_order_escape_payload()

    assert_expected_payload(payload)
    assert payload["status"] == "BOOTSTRAP_T12_81_3_ORDER_ESCAPE_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "Fixed singleton-rich order diagnostic" in claim_scope
    assert "does not prove genuine rich-class order" in claim_scope
    assert "does not prove n=9" in claim_scope
    assert "counterexample" in claim_scope


def test_81_3_order_escape_summary_pins_order() -> None:
    payload = build_t12_81_3_order_escape_payload()
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:3"
    assert summary["source_record_ids"] == [81]
    assert summary["target_row_center"] == 3
    assert summary["target_witnesses"] == [0, 1, 4, 6]
    assert summary["deletion_seed"] == [0, 1, 4]
    assert summary["connector_pair"] == [0, 1]
    assert summary["connector_forcing_triples"] == [[0, 1, 4], [0, 1, 6]]
    assert summary["connector_avoiding_activation_triples"] == [
        [0, 4, 6],
        [1, 4, 6],
    ]
    assert summary["fixed_singleton_order"] == [0, 1, 4, 3, 6]
    assert summary["fixed_singleton_closure"] == [0, 1, 3, 4, 6]
    assert summary["initial_enabled_centers"] == [3]
    assert summary["fixed_singleton_center_3_step_index"] == 0
    assert summary["fixed_singleton_label_6_step_index"] == 1
    assert not summary["fixed_singleton_label_6_before_center_3"]
    assert summary["fixed_singleton_center_3_before_label_6"]
    assert summary["fixed_singleton_center_3_trigger"] == [0, 1, 4]
    assert summary["fixed_singleton_center_3_trigger_forces_connector"]
    assert summary["fixed_singleton_label_6_supply_trigger"] == [0, 3, 4]
    assert summary["fixed_singleton_label_6_supply_depends_on_center_3"]
    assert summary["fixed_singleton_order_status"] == FIXED_SINGLETON_ORDER_STATUS
    assert summary["pre_3_label_6_supply_status"] == PRE_3_LABEL_6_SUPPLY_STATUS
    assert summary["genuine_escape_status"] == GENUINE_ESCAPE_STATUS
    assert summary["order_escape_gap_type"] == ORDER_ESCAPE_GAP


def test_81_3_order_escape_fixed_singleton_audit() -> None:
    payload = build_t12_81_3_order_escape_payload()
    audit = payload["fixed_singleton_order_audit"]

    assert audit["source_record_id"] == 81
    assert audit["classification_assignment_id"] == "A082"
    assert audit["target_row_key"] == "81:3"
    assert audit["rich_class_model"] == "singleton_fixed_selected_rows"
    assert audit["seed"] == [0, 1, 4]
    assert audit["closure"] == [0, 1, 3, 4, 6]
    assert audit["order"] == [0, 1, 4, 3, 6]
    assert not audit["generates_all"]
    assert audit["center_3_step_index"] == 0
    assert audit["label_6_step_index"] == 1
    assert not audit["label_6_before_center_3"]
    assert audit["center_3_before_label_6"]
    assert audit["center_3_trigger"] == [0, 1, 4]
    assert audit["center_3_trigger_forces_connector"]
    assert audit["label_6_supply_trigger"] == [0, 3, 4]
    assert audit["label_6_supply_depends_on_center_3"]
    assert audit["pre_3_label_6_supply_status"] == PRE_3_LABEL_6_SUPPLY_STATUS

    assert audit["selected_rows"][3] == [0, 1, 4, 6]
    assert audit["selected_rows"][6] == [0, 3, 4, 7]
    assert audit["initial_enabled_activations"] == [
        {
            "enabled_center": 3,
            "rich_class_index": 0,
            "rich_class": [0, 1, 4, 6],
            "trigger_witnesses": [0, 1, 4],
            "trigger_contains_connector_pair": True,
            "trigger_uses_label_6": False,
        }
    ]


def test_81_3_order_escape_steps_show_6_depends_on_3() -> None:
    payload = build_t12_81_3_order_escape_payload()
    steps = payload["fixed_singleton_order_audit"]["post_seed_steps"]

    assert len(steps) == 2
    center_3_step, label_6_step = steps
    assert center_3_step["added_center"] == 3
    assert center_3_step["closure_before"] == [0, 1, 4]
    assert center_3_step["trigger_witnesses"] == [0, 1, 4]
    assert center_3_step["trigger_contains_connector_pair"]
    assert not center_3_step["label_6_available_before_step"]

    assert label_6_step["added_center"] == 6
    assert label_6_step["closure_before"] == [0, 1, 3, 4]
    assert label_6_step["trigger_witnesses"] == [0, 3, 4]
    assert not label_6_step["trigger_contains_connector_pair"]
    assert label_6_step["trigger_depends_on_center_3"]


def test_81_3_order_escape_contract_names_remaining_target() -> None:
    payload = build_t12_81_3_order_escape_payload()
    contract = payload["order_resolved_escape_contract"]

    assert contract["status"] == GENUINE_ESCAPE_STATUS
    assert contract["fixed_singleton_status"] == FIXED_SINGLETON_ORDER_STATUS
    assert "Label 6 must be available before center 3" in contract[
        "required_for_connector_avoiding_activation"
    ]
    assert "does not realize that escape" in contract["fixed_singleton_result"]
    assert any(
        "genuine rich class" in item
        for item in contract["genuine_escape_certificate_needed"]
    )


def test_81_3_order_escape_source_rich_triple_contract_matches() -> None:
    payload = build_t12_81_3_order_escape_payload()
    source = payload["source_rich_triple_contract"]

    assert source["source_schema"] == "erdos97.bootstrap_t12_81_3_rich_triple_contract.v1"
    assert (
        source["source_status"]
        == "BOOTSTRAP_T12_81_3_RICH_TRIPLE_CONTRACT_DIAGNOSTIC_ONLY"
    )
    assert source["target_row_key"] == "81:3"
    assert source["target_row_center"] == 3
    assert source["target_witnesses"] == [0, 1, 4, 6]
    assert source["connector_pair"] == [0, 1]
    assert source["connector_forcing_triples"] == [[0, 1, 4], [0, 1, 6]]
    assert source["connector_avoiding_activation_triples"] == [
        [0, 4, 6],
        [1, 4, 6],
    ]
    assert source["rich_class_existence_status"] == "OPEN_TARGET_NOT_PROVED"


def test_81_3_order_escape_artifact_matches_generator() -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == build_t12_81_3_order_escape_payload()


def test_81_3_order_escape_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_order_escape.py",
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
    assert payload["summary"]["genuine_escape_status"] == GENUINE_ESCAPE_STATUS


def test_81_3_order_escape_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "bootstrap_t12_81_3_order_escape.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_order_escape.py",
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
            "scripts/check_bootstrap_t12_81_3_order_escape.py",
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


def test_81_3_order_escape_expected_payload_rejects_drift() -> None:
    payload = build_t12_81_3_order_escape_payload()
    bad = copy.deepcopy(payload)
    bad["summary"]["fixed_singleton_order"] = [0, 1, 4, 6, 3]

    with pytest.raises(AssertionError, match="fixed_singleton_order"):
        assert_expected_payload(bad)
