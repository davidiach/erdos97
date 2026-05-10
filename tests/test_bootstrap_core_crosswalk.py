from __future__ import annotations

import copy

import pytest

from erdos97.bootstrap_core_crosswalk import (
    assert_expected_payload,
    build_crosswalk_payload,
    search_first_minimum_generator,
)
from erdos97.adaptive_blockers import singleton_rich_classes_from_pattern
from erdos97.bridge_negative_controls import c13_sidon_rows


def test_bootstrap_core_crosswalk_expected_payload() -> None:
    payload = build_crosswalk_payload()

    assert_expected_payload(payload)
    summary = payload["summary"]
    assert summary["order_case_count"] == 8
    assert summary["rank_gt_3_order_cases"] == 8
    assert summary["weighted_capacity_obstruction_count"] == 0


def test_bootstrap_core_crosswalk_records_order_sensitive_capacity() -> None:
    payload = build_crosswalk_payload()
    by_case = {record["case_id"]: record for record in payload["records"]}

    natural = by_case["C13_sidon_1_2_4_10:natural"]["bootstrap_core_audit"]
    registered = by_case[
        "C13_sidon_1_2_4_10:sample_full_filter_survivor"
    ]["bootstrap_core_audit"]

    assert natural["core"] == registered["core"]
    assert natural["cyclic_capacity_sum"] == 36
    assert registered["cyclic_capacity_sum"] == 56
    assert registered["capacity_margin"] > natural["capacity_margin"]


def test_first_minimum_generator_exhausts_smaller_seeds() -> None:
    rich_classes = singleton_rich_classes_from_pattern(c13_sidon_rows())

    result = search_first_minimum_generator(rich_classes)

    assert result["found"]
    assert result["minimum_rank"] == 4
    assert result["first_generator"] == [0, 1, 2, 3]
    assert result["generating_closure"]["generates_all"]


def test_bootstrap_core_crosswalk_expected_payload_rejects_drift() -> None:
    payload = build_crosswalk_payload()
    bad = copy.deepcopy(payload)
    bad["summary"]["weighted_capacity_obstruction_count"] = 1

    with pytest.raises(AssertionError, match="weighted_capacity_obstruction_count"):
        assert_expected_payload(bad)
