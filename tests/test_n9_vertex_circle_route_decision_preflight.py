from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from scripts.check_n9_review_decision_intake import (
    load_intake,
    validate_decision_record,
)
from scripts.check_n9_review_gate_ledger import load_ledger
from scripts.check_n9_vertex_circle_route_decision_preflight import (
    ACCEPTED_ROUTE_TEMPLATE_COMMAND,
    DECISION_REQUIRED_ACCEPTED_GATES,
    INTERNAL_REVIEW_NOTES,
    VERTEX_CIRCLE_ROUTE_GATES,
    build_accepted_route_decision_template,
    main,
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
    assert payload["accepted_route_template_command"] == ACCEPTED_ROUTE_TEMPLATE_COMMAND


def test_n9_vertex_circle_route_preflight_builds_accepted_route_template() -> None:
    ledger = load_ledger(LEDGER)
    intake = load_intake(INTAKE)

    template = build_accepted_route_decision_template(intake)
    template_errors = validate_decision_record(template, intake, gate_ledger=ledger)

    assert template["decision_status"] == "final"
    assert template["recommended_outcome"] == "accepted_vertex_circle_route"
    assert template["accepted_gates"] == list(DECISION_REQUIRED_ACCEPTED_GATES)
    assert template["rejected_gates"] == []
    assert template["not_reviewed_gates"] == [
        "turn_geometry",
        "turn_arithmetic_replay",
        "kalmanson_geometry",
        "kalmanson_selfedge_replay",
        "kalmanson_corroboration",
        "lean_compilation",
    ]
    assert template["acknowledgements"]["source_of_truth_pr_required"] is True
    assert "does not accept any gate" in template["notes"]
    assert "reviewer_name must be nonempty for final decisions" in template_errors
    assert "review_date must be nonempty for final decisions" in template_errors
    assert "reviewed_git_head must be nonempty for final decisions" in template_errors
    assert "run_bundle_digest must be nonempty for final decisions" in template_errors


def test_n9_vertex_circle_route_preflight_filled_template_validates() -> None:
    ledger = load_ledger(LEDGER)
    intake = load_intake(INTAKE)
    template = build_accepted_route_decision_template(intake)
    template.update(
        {
            "reviewer_name": "Independent Reviewer",
            "review_date": "2026-06-23",
            "reviewed_git_head": "0123456789abcdef0123456789abcdef01234567",
            "run_bundle_digest": "sha256:review-run-bundle-placeholder",
            "notes": (
                "Independent written review notes would be recorded here "
                "before validation."
            ),
        }
    )

    assert validate_decision_record(template, intake, gate_ledger=ledger) == []


def test_n9_vertex_circle_route_preflight_prints_accepted_route_template(
    capsys,
) -> None:
    assert main(["--accepted-route-template"]) == 0

    output = capsys.readouterr().out

    assert "decision_status: final" in output
    assert "recommended_outcome: accepted_vertex_circle_route" in output
    assert "- frontier_enumeration" in output
    assert "- independent_review" in output
    assert "source_of_truth_pr_required: true" in output


def test_n9_vertex_circle_route_preflight_template_failure_is_nonzero(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        "scripts.check_n9_vertex_circle_route_decision_preflight.validate_preflight",
        lambda *, ledger, intake: ({"status": "REVIEW_PREFLIGHT_ONLY"}, ["boom"]),
    )

    assert main(["--accepted-route-template"]) == 1

    captured = capsys.readouterr()

    assert captured.out == ""
    assert "accepted-route template unavailable" in captured.err
    assert "boom" in captured.err


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


def test_n9_vertex_circle_route_preflight_rejects_malformed_gate_lists() -> None:
    ledger = load_ledger(LEDGER)
    intake = deepcopy(load_intake(INTAKE))
    rules = intake.get("outcome_rules")
    assert isinstance(rules, list)
    for rule in rules:
        if isinstance(rule, dict) and rule.get("id") == "accepted_vertex_circle_route":
            rule["required_accepted_gates"] = None
            break
    else:
        raise AssertionError("accepted_vertex_circle_route rule not found")

    _, errors = validate_preflight(ledger=ledger, intake=intake)

    assert (
        "intake accepted_vertex_circle_route.required_accepted_gates must be a list"
        in errors
    )
