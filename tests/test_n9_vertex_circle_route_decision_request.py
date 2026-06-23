from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from scripts.check_n9_vertex_circle_route_decision_request import (
    ACCEPTED_VERTEX_CIRCLE_ROUTE,
    DECISION_TEMPLATE_COMMAND,
    DECISION_REQUIRED_ACCEPTED_GATES,
    DEFAULT_REQUEST,
    build_request_payload,
    load_request,
    render_markdown,
    summary_payload,
    validate_request,
)


ROOT = Path(__file__).resolve().parents[1]


def test_n9_vertex_circle_route_decision_request_is_valid() -> None:
    payload = load_request(DEFAULT_REQUEST)

    request_payload, errors = validate_request(payload)

    assert errors == []
    assert request_payload["requested_outcome"] == ACCEPTED_VERTEX_CIRCLE_ROUTE
    assert request_payload["requested_accepted_gates"] == list(
        DECISION_REQUIRED_ACCEPTED_GATES
    )
    assert request_payload["requested_rejected_gates"] == []
    assert request_payload["decision_template_command"] == DECISION_TEMPLATE_COMMAND
    assert request_payload["decision_template_command"].endswith(
        "--accepted-route-template"
    )
    assert request_payload["external_reviewer_required"] is True
    assert request_payload["source_of_truth_update_allowed"] is False


def test_n9_vertex_circle_route_decision_request_summary() -> None:
    payload = load_request(DEFAULT_REQUEST)
    request_payload, errors = validate_request(payload)

    summary = summary_payload(request_payload, errors)

    assert summary["validation_status"] == "passed"
    assert summary["requested_outcome"] == ACCEPTED_VERTEX_CIRCLE_ROUTE
    assert summary["requested_accepted_gate_count"] == 4
    assert summary["requested_not_reviewed_gate_count"] == 4
    assert summary["internal_review_note_count"] == 3


def test_n9_vertex_circle_route_decision_request_rejects_gate_acceptance() -> None:
    payload = deepcopy(load_request(DEFAULT_REQUEST))
    payload["source_of_truth_update_allowed"] = True

    _, errors = validate_request(payload)

    assert "source_of_truth_update_allowed must be false" in errors


def test_n9_vertex_circle_route_decision_request_requires_independent_review() -> None:
    payload = deepcopy(load_request(DEFAULT_REQUEST))
    payload["requested_accepted_gates"] = [
        gate
        for gate in payload["requested_accepted_gates"]
        if gate != "independent_review"
    ]
    payload["requested_not_reviewed_gates"].append("independent_review")

    _, errors = validate_request(payload)

    assert (
        "requested_accepted_gates must match the vertex-circle "
        "decision-intake gate order"
    ) in errors
    assert any(error.startswith("requested decision shape:") for error in errors)


def test_n9_vertex_circle_route_decision_request_rejects_note_drift() -> None:
    payload = deepcopy(load_request(DEFAULT_REQUEST))
    payload["internal_review_notes"][0]["expected_outcomes"] = ["wrong"]

    _, errors = validate_request(payload)

    assert (
        "internal_review_notes[0].expected_outcomes does not match preflight"
        in errors
    )


def test_n9_vertex_circle_route_decision_request_rejects_malformed_gate_list() -> None:
    payload = deepcopy(load_request(DEFAULT_REQUEST))
    payload["requested_not_reviewed_gates"] = None

    _, errors = validate_request(payload)

    assert "requested_not_reviewed_gates must be a list" in errors


def test_n9_vertex_circle_route_decision_request_rejects_step_drift() -> None:
    payload = deepcopy(load_request(DEFAULT_REQUEST))
    payload["reviewer_steps"][0]["command"] = "python wrong.py"

    _, errors = validate_request(payload)

    assert any(
        error.startswith("reviewer_steps[0].command must be")
        for error in errors
    )


def test_n9_vertex_circle_route_decision_request_renders_markdown() -> None:
    payload = load_request(DEFAULT_REQUEST)
    request_payload = build_request_payload(payload)

    markdown = render_markdown(request_payload, [])

    assert "# n=9 Vertex-circle Route Decision Request" in markdown
    assert "`accepted_vertex_circle_route`" in markdown
    assert "does not accept any gate" in markdown
    assert str(ROOT) not in markdown
