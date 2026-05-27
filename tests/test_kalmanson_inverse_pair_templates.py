from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.analyze_kalmanson_inverse_pair_templates import (
    CLAIM_SCOPE,
    assert_expected,
    diagnostic_payload,
)

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.slow


def test_kalmanson_inverse_pair_template_diagnostic_expected_counts() -> None:
    payload = diagnostic_payload()

    assert_expected(payload)
    assert payload["cross_pattern_summary"] == {
        "shared_coefficient_templates": [
            "one_class_equals_one_class",
            "two_classes_equal_two_classes",
        ],
        "all_coefficient_templates": [
            "one_class_equals_one_class",
            "two_classes_equal_two_classes",
        ],
        "patterns_have_same_template_set": True,
    }
    by_name = {
        summary["pattern"]["name"]: summary
        for summary in payload["pattern_summaries"]
    }
    assert by_name["C13_sidon_1_2_4_10"]["inverse_vector_pair_count"] == 1729
    assert by_name["C13_sidon_1_2_4_10"][
        "inverse_pair_support_size_distribution"
    ] == {"2": 390, "4": 1339}
    assert by_name["C19_skew"]["inverse_vector_pair_count"] == 11172
    assert by_name["C19_skew"]["inverse_pair_support_size_distribution"] == {
        "2": 1387,
        "4": 9785,
    }


def test_kalmanson_inverse_pair_template_rows_are_interpretable() -> None:
    payload = diagnostic_payload(top=2)
    c13 = payload["pattern_summaries"][0]
    rows = {
        row["template"]: row
        for row in c13["coefficient_template_distribution"]
    }

    assert rows["one_class_equals_one_class"] == {
        "template": "one_class_equals_one_class",
        "inverse_vector_pair_count": 390,
        "support_size": 2,
        "positive_coefficients": [1],
        "negative_coefficients": [1],
        "interpretation": (
            "After selected-distance quotienting, one Kalmanson row is "
            "D_A > D_B and its inverse is D_B > D_A."
        ),
    }
    assert rows["two_classes_equal_two_classes"]["support_size"] == 4
    assert rows["two_classes_equal_two_classes"]["positive_coefficients"] == [1, 1]
    assert rows["two_classes_equal_two_classes"]["negative_coefficients"] == [1, 1]
    assert len(c13["top_inverse_vector_pairs_by_potential_count"]) == 2


def test_kalmanson_inverse_pair_template_rejects_tampering() -> None:
    payload = diagnostic_payload()
    payload["pattern_summaries"][1]["inverse_vector_pair_count"] = 11171

    try:
        assert_expected(payload)
    except AssertionError as exc:
        assert "C19_skew inverse_vector_pair_count mismatch" in str(exc)
    else:  # pragma: no cover - defensive assertion shape
        raise AssertionError("tampered inverse-pair diagnostic unexpectedly passed")


def test_kalmanson_inverse_pair_template_rejects_appended_claim_scope_overclaim() -> None:
    payload = diagnostic_payload()
    payload["claim_scope"] = f"{CLAIM_SCOPE} This proves Erdos Problem #97."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected(payload)


def test_kalmanson_inverse_pair_template_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/analyze_kalmanson_inverse_pair_templates.py",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["status"] == "KALMANSON_INVERSE_PAIR_TEMPLATE_DIAGNOSTIC"
    assert payload["pattern_summaries"][0]["pattern"]["name"] == "C13_sidon_1_2_4_10"
    assert payload["pattern_summaries"][1]["pattern"]["name"] == "C19_skew"
