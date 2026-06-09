from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from scripts.check_n9_review_decision_intake import load_intake
from scripts.check_n9_review_gate_ledger import load_ledger
from scripts.check_n9_vertex_circle_route_decision_preflight import (
    DECISION_REQUIRED_ACCEPTED_GATES,
    INTERNAL_REVIEW_NOTES,
    VERTEX_CIRCLE_ROUTE_GATES,
    validate_preflight,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "metadata" / "n9_review_gate_ledger.yaml"
INTAKE = ROOT / "metadata" / "n9_review_decision_intake.yaml"


def _set_gate_open(payload: dict[str, object], gate_id: str, value: bool) -> None:
    for key in ("review_gates", "infrastructure_gates"):
        gates = payload.get(key)
        if not isinstance(gates, list):
            continue
        for gate in gates:
            if isinstance(gate, dict) and gate.get("id") == gate_id:
                gate["still_open"] = value
                return
    raise AssertionError(f"gate not found: {gate_id}")


def _remove_rule_gate(payload: dict[str, object], gate_id: str) -> None:
    rules = payload.get("outcome_rules")
    assert isinstance(rules, list)
    for rule in rules:
        if isinstance(rule, dict) and rule.get("id") == "accepted_vertex_circle_route":
            for field in ("required_accepted_gates", "blocks_if_rejected_or_unreviewed"):
                values = rule.get(field)
                assert isinstance(values, list)
                rule[field] = [value for value in values if value != gate_id]
            return
    raise AssertionError("accepted_vertex_circle_route rule not found")


def test_n9_vertex_circle_route_decision_preflight_is_valid() -> None:
    payload, errors = validate_preflight()

    assert errors == []
    assert payload["route_gate_ids"] == list(VERTEX_CIRCLE_ROUTE_GATES)
    assert payload["decision_required_accepted_gates"] == list(
        DECISION_REQUIRED_ACCEPTED_GATES
    )
    assert payload["all_required_gates_still_open"] is True
    assert payload["source_of_truth_update_allowed"] is False
    assert len(payload["internal_review_notes"]) == len(INTERNAL_REVIEW_NOTES)
    assert (
        payload["draft_vertex_circle_decision_shape"]["validation_status"]
        == "passed"
    )


def test_n9_vertex_circle_route_preflight_rejects_closed_route_gate() -> None:
    ledger = deepcopy(load_ledger(LEDGER))
    intake = load_intake(INTAKE)
    _set_gate_open(ledger, "frontier_enumeration", False)

    _, errors = validate_preflight(ledger=ledger, intake=intake)

    assert "gate 'frontier_enumeration' must remain open before review intake" in errors


def test_n9_vertex_circle_route_preflight_requires_independent_review() -> None:
    ledger = load_ledger(LEDGER)
    intake = deepcopy(load_intake(INTAKE))
    _remove_rule_gate(intake, "independent_review")

    _, errors = validate_preflight(ledger=ledger, intake=intake)

    assert any(
        error.startswith(
            "intake accepted_vertex_circle_route must require exactly"
        )
        for error in errors
    )
    assert any(
        error.startswith(
            "intake accepted_vertex_circle_route must be blocked by exactly"
        )
        for error in errors
    )
