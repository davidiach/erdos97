from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_transfer_component_feasibility import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_COMPONENTS,
    EXPECTED_WITNESSES,
    FEASIBILITY_STATUS,
    assert_expected_component_feasibility,
    build_component_feasibility_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_components() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_COMPONENTS)


def test_label4_transfer_component_feasibility_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_component_feasibility(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_LABEL4_TRANSFER_COMPONENT_FEASIBILITY_NEGATIVE_CONTROLS"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "rejects component-alone impossibility claims only",
        "does not give one polygon realizing all six components at once",
        "does not prove outside-pair support existence",
        "does not prove row forcing",
        "does not prove pair [3,5] impossible",
        "does not prove endpoint-8 forcing",
        "does not prove n=9",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_label4_transfer_component_feasibility_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["source_length_component_count"] == 6
    assert summary["source_unique_segment_count"] == 9
    assert summary["witness_record_count"] == 6
    assert summary["feasible_component_count"] == 6
    assert summary["component_alone_obstruction_status"] == FEASIBILITY_STATUS
    assert summary["simultaneous_component_witness_status"] == "not_checked"
    assert summary["regular_polygon_modulus_counts"] == {
        "9": 1,
        "10": 2,
        "12": 1,
        "13": 1,
        "14": 1,
    }
    assert summary["common_minor_arc_unit_counts"] == {
        "2": 1,
        "3": 2,
        "4": 2,
        "6": 1,
    }
    assert summary["component_count_by_geometry_class"] == {
        "diagonal_only_equality": 2,
        "edge_diagonal_equality": 3,
        "edge_edge_diagonal_chain": 1,
    }
    assert summary["component_with_row6_connector_step_count"] == 1
    assert summary["cascade_component_key"] == "D[0,6]=D[4,5]=D[5,6]"
    assert summary["cascade_witness_modulus"] == 13
    assert summary["cascade_witness_minor_arc_units"] == 3


def test_label4_transfer_component_feasibility_witness_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    witnesses = payload["witness_records"]

    assert len(witnesses) == 6
    assert {record["component_key"] for record in witnesses} == set(EXPECTED_WITNESSES)
    for record in witnesses:
        expected = EXPECTED_WITNESSES[record["component_key"]]
        assert record["regular_polygon_modulus"] == expected["regular_polygon_modulus"]
        assert record["arc_units_by_gap"] == expected["arc_units_by_gap"]
        assert record["common_minor_arc_units"] == expected["common_minor_arc_units"]
        assert record["witness_status"] == "feasible"
        assert record["witness_scope"] == "component_alone_only"
        assert {
            item["minor_arc_units"] for item in record["segment_arc_records"]
        } == {record["common_minor_arc_units"]}

    cascade = next(
        record
        for record in witnesses
        if record["component_key"] == "D[0,6]=D[4,5]=D[5,6]"
    )
    assert cascade["contains_row6_connector_step"] is True
    assert cascade["contains_target_center"] is True
    assert cascade["regular_polygon_modulus"] == 13
    assert cascade["arc_units_by_gap"] == [1, 1, 1, 1, 3, 3, 1, 1, 1]
    assert {
        item["segment_key"]: item["minor_arc_units"]
        for item in cascade["segment_arc_records"]
    } == {"D[0,6]": 3, "D[4,5]": 3, "D[5,6]": 3}


def test_label4_transfer_component_feasibility_artifact_matches_generator(
    source_components: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_component_feasibility_payload(source_components)


def test_label4_transfer_component_feasibility_rejects_tampered_arc() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["witness_records"][0]["arc_units_by_gap"][0] += 1

    errors = validate_payload(payload, recompute=False)

    assert any("arc_units_by_gap" in error for error in errors)


def test_label4_transfer_component_feasibility_rejects_bad_minor_arc() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["witness_records"][1]["segment_arc_records"][0]["minor_arc_units"] += 1

    errors = validate_payload(payload, recompute=False)

    assert any("minor arc mismatch" in error for error in errors)


def test_label4_transfer_component_feasibility_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_transfer_component_feasibility.py",
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
    assert payload["witness_record_count"] == 6
    assert payload["feasible_component_count"] == 6
    assert payload["cascade_component_key"] == "D[0,6]=D[4,5]=D[5,6]"
    assert payload["cascade_witness_modulus"] == 13
