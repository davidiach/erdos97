from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.analyze_kalmanson_sparse_frontier_templates import (
    CHECKED_PILOT_TEMPLATE_SET,
    assert_expected,
    diagnostic_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_kalmanson_sparse_frontier_template_availability_expected_counts() -> None:
    payload = diagnostic_payload(top=2)

    assert_expected(payload)
    assert payload["frontier_cross_pattern_summary"] == {
        "shared_coefficient_templates": CHECKED_PILOT_TEMPLATE_SET,
        "all_coefficient_templates": CHECKED_PILOT_TEMPLATE_SET,
        "patterns_have_same_template_set": True,
    }
    assert payload["comparison_to_checked_c13_c19_pilots"] == {
        "checked_pilot_template_set": CHECKED_PILOT_TEMPLATE_SET,
        "frontier_template_set": CHECKED_PILOT_TEMPLATE_SET,
        "frontier_exposes_only_checked_pilot_templates": True,
        "frontier_exposes_all_checked_pilot_templates": True,
    }

    by_name = {
        summary["pattern"]["name"]: summary
        for summary in payload["frontier_pattern_summaries"]
    }
    assert by_name["C25_sidon_2_5_9_14"]["inverse_vector_pair_count"] == 37475
    assert by_name["C25_sidon_2_5_9_14"][
        "potential_ordered_quad_pair_count_by_template"
    ] == {
        "one_class_equals_one_class": 284800,
        "two_classes_equal_two_classes": 2220800,
    }
    assert by_name["C29_sidon_1_3_7_15"]["inverse_vector_pair_count"] == 70702
    assert by_name["C29_sidon_1_3_7_15"][
        "inverse_pair_support_size_distribution"
    ] == {"2": 3973, "4": 66729}


def test_kalmanson_sparse_frontier_template_claim_scope_is_guarded() -> None:
    payload = diagnostic_payload(top=1)

    claim_scope = payload["claim_scope"]
    assert "does not search cyclic orders" in claim_scope
    assert "does not prove an all-order obstruction" in claim_scope
    assert "does not prove Erdos Problem #97" in claim_scope
    assert "does not claim a counterexample" in claim_scope
    assert "availability" in payload["interpretation"]
    assert "does not obstruct C25 or C29" in payload["interpretation"]


def test_kalmanson_sparse_frontier_template_rejects_tampering() -> None:
    payload = diagnostic_payload(top=1)
    payload["frontier_pattern_summaries"][0]["inverse_vector_pair_count"] = 37474

    try:
        assert_expected(payload)
    except AssertionError as exc:
        assert "C25_sidon_2_5_9_14 inverse_vector_pair_count mismatch" in str(exc)
    else:  # pragma: no cover - defensive assertion shape
        raise AssertionError("tampered sparse-frontier diagnostic unexpectedly passed")


def test_kalmanson_sparse_frontier_template_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/analyze_kalmanson_sparse_frontier_templates.py",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["status"] == "KALMANSON_SPARSE_FRONTIER_TEMPLATE_AVAILABILITY_DIAGNOSTIC"
    assert [
        summary["pattern"]["name"]
        for summary in payload["frontier_pattern_summaries"]
    ] == ["C25_sidon_2_5_9_14", "C29_sidon_1_3_7_15"]
