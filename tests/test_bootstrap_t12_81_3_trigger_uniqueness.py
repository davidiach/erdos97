from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_3_trigger_uniqueness import (
    DEFAULT_ARTIFACT,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_3_trigger_uniqueness_payload,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_3_trigger_uniqueness_payload()


def test_81_3_trigger_uniqueness_counts_and_scope(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_81_3_TRIGGER_UNIQUENESS_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "Same-center disjointness audit" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope


def test_81_3_trigger_uniqueness_summary(payload: dict[str, object]) -> None:
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:3"
    assert summary["source_record_ids"] == [81]
    assert summary["deletion_seed"] == [0, 1, 4]
    assert summary["connector_pair"] == [0, 1]
    assert summary["supply_center"] == 6
    assert summary["target_center"] == 3
    assert summary["center_6_supply_class_count"] == 5
    assert summary["center_6_supply_pair_count"] == 10
    assert summary["center_6_supply_intersection_size_histogram"] == {"3": 10}
    assert summary["center_6_supply_disjoint_pair_count"] == 0
    assert summary["center_6_supply_max_same_center_pairwise_disjoint_family_size"] == 1
    assert summary["center_6_selected_row_option_count_histogram"] == {"2": 5}
    assert summary["center_3_connector_avoiding_class_count"] == 8
    assert summary["center_3_connector_pair_count"] == 28
    assert summary["center_3_connector_intersection_size_histogram"] == {
        "2": 12,
        "3": 16,
    }
    assert summary["center_3_connector_disjoint_pair_count"] == 0
    assert (
        summary["center_3_connector_max_same_center_pairwise_disjoint_family_size"]
        == 1
    )
    assert summary["center_3_selected_row_option_count_histogram"] == {"2": 8}
    assert summary["same_center_trigger_uniqueness_status"] == SCAN_STATUS


def test_81_3_trigger_uniqueness_family_audits(
    payload: dict[str, object],
) -> None:
    audits = payload["family_audits"]
    supply = audits["center_6_supply"]
    connector = audits["center_3_connector_avoiding"]

    assert supply["all_pairs_intersect"] is True
    assert supply["disjoint_pair_count"] == 0
    assert supply["max_same_center_pairwise_disjoint_family_size"] == 1
    assert {tuple(row) for row in supply["classes"]} == {
        (0, 1, 2, 4),
        (0, 1, 3, 4),
        (0, 1, 4, 5),
        (0, 1, 4, 7),
        (0, 1, 4, 8),
    }

    assert connector["all_pairs_intersect"] is True
    assert connector["disjoint_pair_count"] == 0
    assert connector["max_same_center_pairwise_disjoint_family_size"] == 1
    assert {tuple(row) for row in connector["classes"]} == {
        (0, 2, 4, 6),
        (0, 4, 5, 6),
        (0, 4, 6, 7),
        (0, 4, 6, 8),
        (1, 2, 4, 6),
        (1, 4, 5, 6),
        (1, 4, 6, 7),
        (1, 4, 6, 8),
    }


def test_81_3_trigger_uniqueness_selected_row_options(
    payload: dict[str, object],
) -> None:
    audits = payload["family_audits"]
    for audit in audits.values():
        for record in audit["selected_row_option_records"]:
            rich_class = set(record["auxiliary_class"])
            options = record["selected_row_options_equal_or_disjoint"]
            assert len(options) == 2
            assert set(options[0]) == rich_class
            assert set(options[1]).isdisjoint(rich_class)


def test_81_3_trigger_uniqueness_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_81_3_trigger_uniqueness_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_trigger_uniqueness.py",
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
    assert payload["summary"]["same_center_trigger_uniqueness_status"] == SCAN_STATUS


def test_81_3_trigger_uniqueness_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["center_6_supply_disjoint_pair_count"] = 1

    with pytest.raises(AssertionError, match="center_6_supply_disjoint_pair_count"):
        assert_expected_payload(bad)
