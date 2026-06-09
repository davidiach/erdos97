from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_transfer_length_components import (
    COMPONENT_STATUS,
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_OBLIGATIONS,
    assert_expected_label4_transfer_length_components,
    build_label4_transfer_length_components_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_obligations() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_OBLIGATIONS)


def test_label4_transfer_length_components_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_label4_transfer_length_components(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_LABEL4_TRANSFER_LENGTH_COMPONENTS_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "does not prove outside-pair support existence",
        "does not prove row forcing",
        "does not prove pair [3,5] impossible",
        "does not prove endpoint-8 forcing",
        "does not prove n=9",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_label4_transfer_length_components_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["source_unique_edge_obligation_count"] == 7
    assert summary["source_unique_path_motif_count"] == 6
    assert summary["source_positive_transfer_signature_count"] == 8
    assert summary["source_positive_transfer_occurrence_count"] == 9
    assert summary["length_component_count"] == 6
    assert summary["unique_segment_count"] == 9
    assert summary["component_size_counts"] == {"2": 5, "3": 1}
    assert summary["unique_segment_count_by_cyclic_gap"] == {
        "1": 2,
        "2": 1,
        "3": 4,
        "4": 2,
    }
    assert summary["component_count_by_geometry_class"] == {
        "diagonal_only_equality": 2,
        "edge_diagonal_equality": 3,
        "edge_edge_diagonal_chain": 1,
    }
    assert summary["component_with_edge_to_diagonal_equality_count"] == 4
    assert summary["component_with_row6_connector_step_count"] == 1
    assert summary["component_with_target_center_count"] == 1
    assert summary["label8_free_component_count"] == 6
    assert summary["cascade_component_key"] == "D[0,6]=D[4,5]=D[5,6]"
    assert summary["cascade_component_signature_count"] == 3
    assert summary["cascade_component_occurrence_count"] == 4
    assert summary["component_status"] == COMPONENT_STATUS


def test_label4_transfer_length_component_records_are_geometric() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    components = payload["length_component_records"]
    segments = payload["segment_records"]

    assert len(components) == 6
    assert len(segments) == 9
    assert {record["component_key"] for record in components} == {
        "D[0,5]=D[4,5]",
        "D[0,6]=D[4,5]=D[5,6]",
        "D[1,7]=D[4,7]",
        "D[2,5]=D[4,5]",
        "D[2,7]=D[4,7]",
        "D[4,5]=D[5,7]",
    }

    cascade = next(
        record
        for record in components
        if record["component_key"] == "D[0,6]=D[4,5]=D[5,6]"
    )
    assert cascade["geometry_class"] == "edge_edge_diagonal_chain"
    assert cascade["contains_row6_connector_step"] is True
    assert cascade["contains_target_center"] is True
    assert cascade["cyclic_gap_counts"] == {"1": 2, "3": 1}
    assert cascade["segment_kind_counts"] == {
        "cyclic_gap_3_diagonal": 1,
        "hull_edge": 2,
    }

    label4_hull_edge = next(
        record for record in segments if record["segment_key"] == "D[4,5]"
    )
    assert label4_hull_edge["segment_kind"] == "hull_edge"
    assert label4_hull_edge["contains_label4"] is True
    assert label4_hull_edge["component_signature_incidence_count"] == 6
    assert label4_hull_edge["component_occurrence_incidence_count"] == 7


def test_label4_transfer_length_components_artifact_matches_generator(
    source_obligations: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_label4_transfer_length_components_payload(
        source_obligations,
    )


def test_label4_transfer_length_components_rejects_tampered_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["summary"]["length_component_count"] = 5

    errors = validate_payload(payload, recompute=False)

    assert any("length_component_count" in error for error in errors)


def test_label4_transfer_length_components_rejects_bad_segment_gap() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["segment_records"][0]["cyclic_gap"] = 1

    errors = validate_payload(payload, recompute=False)

    assert any("cyclic gap mismatch" in error for error in errors)


def test_label4_transfer_length_components_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_transfer_length_components.py",
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
    assert payload["length_component_count"] == 6
    assert payload["unique_segment_count"] == 9
    assert payload["cascade_component_key"] == "D[0,6]=D[4,5]=D[5,6]"
