from __future__ import annotations

import pytest

from scripts.check_n9_vertex_circle_dynamic_mro_choices import (
    EXPECTED_WITH_VERTEX,
    EXPECTED_WITHOUT_VERTEX,
    assert_expected_dynamic_mro_choice_payload,
    dynamic_mro_choice_payload,
)

pytestmark = pytest.mark.slow


def test_dynamic_mro_choice_payload_scope_and_counts() -> None:
    payload = dynamic_mro_choice_payload()

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
