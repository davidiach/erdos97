from __future__ import annotations

from scripts.check_n9_vertex_circle_branch_options import (
    EXPECTED_EMPTY_OPTION_CONTEXTS,
    EXPECTED_HELPER_OPTION_TOTAL,
    EXPECTED_NODES_VISITED,
    EXPECTED_OPTION_CONTEXTS,
    assert_expected_branch_option_payload,
    branch_option_payload,
)


def test_branch_option_payload_scope_and_counts() -> None:
    payload = branch_option_payload()

    assert_expected_branch_option_payload(payload)
    assert payload["validation_status"] == "passed"
    summary = payload["branch_option_audit"]
    assert summary["nodes_visited"] == EXPECTED_NODES_VISITED
    assert summary["option_contexts"] == EXPECTED_OPTION_CONTEXTS
    assert summary["helper_option_total"] == EXPECTED_HELPER_OPTION_TOTAL
    assert summary["empty_option_contexts"] == EXPECTED_EMPTY_OPTION_CONTEXTS
    assert summary["option_mismatches"] == 0
    assert summary["count_array_mismatches"] == 0
    assert summary["example_mismatches"] == []
    assert "does not prove dynamic-MRO branch coverage" in payload["claim_scope"]
    assert "counterexample" in payload["claim_scope"]
