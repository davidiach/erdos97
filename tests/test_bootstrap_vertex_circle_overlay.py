from __future__ import annotations

import copy

import pytest

from erdos97.bootstrap_vertex_circle_overlay import (
    assert_expected_payload,
    build_overlay_payload,
)


def test_bootstrap_vertex_circle_overlay_expected_payload() -> None:
    payload = build_overlay_payload()

    assert_expected_payload(payload)
    summary = payload["summary"]
    assert summary["source_assignment_indices"] == [81, 151]
    assert summary["classification_assignment_ids"] == ["A082", "A152"]
    assert summary["template_counts"] == {"T12": 2}
    assert summary["cycle_rows_subset_of_bootstrap_core_count"] == 0


def test_bootstrap_vertex_circle_overlay_signature_join() -> None:
    payload = build_overlay_payload()
    by_source = {record["source_record_id"]: record for record in payload["records"]}

    assert by_source[81]["classification_assignment_id"] == "A082"
    assert by_source[151]["classification_assignment_id"] == "A152"
    assert all(
        record["assignment_join_method"] == "selected_row_signature"
        for record in by_source.values()
    )


def test_bootstrap_vertex_circle_overlay_rows_are_not_core_only() -> None:
    payload = build_overlay_payload()

    for record in payload["records"]:
        vertex_circle = record["vertex_circle"]
        assert vertex_circle["cycle_rows_subset_of_bootstrap_core"] is False
        assert vertex_circle["equality_connector_rows_subset_of_bootstrap_core"] is False

    by_source = {record["source_record_id"]: record for record in payload["records"]}
    assert by_source[81]["vertex_circle"]["strict_edge_rows_subset_of_bootstrap_core"]
    assert not by_source[151]["vertex_circle"]["strict_edge_rows_subset_of_bootstrap_core"]


def test_bootstrap_vertex_circle_overlay_expected_payload_rejects_drift() -> None:
    payload = build_overlay_payload()
    bad = copy.deepcopy(payload)
    bad["summary"]["classification_assignment_ids"] = ["A081", "A151"]

    with pytest.raises(AssertionError, match="classification_assignment_ids"):
        assert_expected_payload(bad)
