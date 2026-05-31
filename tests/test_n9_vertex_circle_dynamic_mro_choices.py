from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_dynamic_mro_choices import (
    CLAIM_SCOPE,
    EXPECTED_WITH_VERTEX,
    EXPECTED_WITHOUT_VERTEX,
    assert_expected_dynamic_mro_choice_payload,
    dynamic_mro_choice_payload,
    summary_json_payload,
)

pytestmark = pytest.mark.slow
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return dynamic_mro_choice_payload()


def test_dynamic_mro_choice_payload_scope_and_counts(payload: dict[str, object]) -> None:
    assert_expected_dynamic_mro_choice_payload(payload)
    assert payload["validation_status"] == "passed"
    audits = payload["dynamic_mro_audits"]
    with_vertex = audits["with_vertex_circle_pruning"]
    without_vertex = audits["without_vertex_circle_pruning"]
    assert with_vertex["nodes_visited"] == EXPECTED_WITH_VERTEX["nodes_visited"]
    assert without_vertex["nodes_visited"] == EXPECTED_WITHOUT_VERTEX["nodes_visited"]
    assert with_vertex["chosen_center_mismatches"] == 0
    assert without_vertex["chosen_center_mismatches"] == 0
    assert with_vertex["helper_direct_option_mismatches"] == 0
    assert without_vertex["helper_direct_option_mismatches"] == 0
    assert with_vertex["example_mismatches"] == []
    assert without_vertex["example_mismatches"] == []
    assert "does not prove the geometric filters" in payload["claim_scope"]
    assert "counterexample" in payload["claim_scope"]


def test_dynamic_mro_rejects_top_level_claim_scope_append(
    payload: dict[str, object],
) -> None:
    tampered = dict(payload)
    tampered["claim_scope"] = CLAIM_SCOPE + " This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_dynamic_mro_choice_payload(tampered)


def test_dynamic_mro_summary_json_payload(payload: dict[str, object]) -> None:
    summary = summary_json_payload(payload)

    assert "dynamic_mro_audits" not in summary
    assert summary["schema"] == payload["schema"]
    assert summary["claim_scope"] == payload["claim_scope"]
    audits = summary["dynamic_mro_audit_summaries"]
    with_vertex = audits["with_vertex_circle_pruning"]
    without_vertex = audits["without_vertex_circle_pruning"]
    assert with_vertex["nodes_visited"] == EXPECTED_WITH_VERTEX["nodes_visited"]
    assert without_vertex["nodes_visited"] == EXPECTED_WITHOUT_VERTEX["nodes_visited"]
    assert with_vertex["helper_direct_option_mismatches"] == 0
    assert without_vertex["helper_direct_option_mismatches"] == 0
    assert "assigned_depth_histogram" not in with_vertex
    assert "minimum_option_count_histogram" not in without_vertex
    assert "example_mismatches" not in with_vertex


def test_dynamic_mro_cli_summary_json(payload: dict[str, object]) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_dynamic_mro_choices.py",
            "--check",
            "--assert-expected",
            "--summary-json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout) == summary_json_payload(payload)
