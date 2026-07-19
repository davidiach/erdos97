from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from scripts.check_n9_review_decision_intake import (
    build_intake_payload,
    dump_template,
    load_intake,
    render_markdown,
    validate_decision_record,
    validate_intake,
)


ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / "metadata" / "n9_review_decision_intake.yaml"


def _valid_acknowledgements() -> dict[str, bool]:
    return {
        "no_general_proof_claimed": True,
        "no_counterexample_claimed": True,
        "official_status_unchanged": True,
        "source_of_truth_pr_required": True,
    }


def _base_final_decision() -> dict[str, object]:
    return {
        "schema": "erdos97.n9_review_decision_record.v1",
        "decision_status": "final",
        "reviewer_name": "Independent Reviewer",
        "review_date": "2026-06-06",
        "reviewed_git_head": "a" * 40,
        "run_bundle_digest": "b" * 64,
        "recommended_outcome": "gap_found",
        "accepted_gates": [],
        "rejected_gates": ["vertex_circle_geometry"],
        "not_reviewed_gates": [
            "frontier_enumeration",
            "quotient_obstruction_replay",
            "turn_geometry",
            "turn_arithmetic_replay",
            "kalmanson_geometry",
            "kalmanson_selfedge_replay",
            "kalmanson_corroboration",
            "lean_compilation",
            "independent_review",
        ],
        "precise_gaps": [
            {
                "gate_id": "vertex_circle_geometry",
                "summary": "Reviewer did not accept the strict-edge geometry.",
            }
        ],
        "acknowledgements": _valid_acknowledgements(),
        "notes": "",
    }


def test_n9_review_decision_intake_is_valid() -> None:
    payload = load_intake(INTAKE)

    errors = validate_intake(payload)

    assert errors == []


def test_n9_review_decision_intake_payload_contains_expected_layers() -> None:
    payload = load_intake(INTAKE)

    intake = build_intake_payload(payload)

    assert len(intake["gate_ids"]) == 10
    assert len(intake["review_outcome_ids"]) == 5
    assert len(intake["outcome_rules"]) == 5
    assert len(intake["decision_template"]["not_reviewed_gates"]) == 10


def test_n9_review_decision_intake_rejects_missing_acknowledgement() -> None:
    payload = deepcopy(load_intake(INTAKE))
    payload["required_acknowledgements"].remove("official_status_unchanged")

    errors = validate_intake(payload)

    assert "required_acknowledgements must match the acknowledgement schema" in errors


def test_n9_review_decision_record_accepts_gap_found_with_precise_gap() -> None:
    payload = load_intake(INTAKE)
    decision = _base_final_decision()

    errors = validate_decision_record(decision, payload)

    assert errors == []


def test_n9_review_decision_record_rejects_missing_route_gate() -> None:
    payload = load_intake(INTAKE)
    decision = _base_final_decision()
    decision["recommended_outcome"] = "accepted_vertex_circle_route"
    decision["accepted_gates"] = [
        "frontier_enumeration",
        "quotient_obstruction_replay",
        "independent_review",
    ]
    decision["rejected_gates"] = []
    decision["not_reviewed_gates"] = [
        "vertex_circle_geometry",
        "turn_geometry",
        "turn_arithmetic_replay",
        "kalmanson_geometry",
        "kalmanson_selfedge_replay",
        "kalmanson_corroboration",
        "lean_compilation",
    ]
    decision["precise_gaps"] = []

    errors = validate_decision_record(decision, payload)

    assert (
        "recommended_outcome 'accepted_vertex_circle_route' requires accepted gate "
        "'vertex_circle_geometry'"
    ) in errors


def test_n9_review_decision_record_accepts_vertex_circle_route_decision() -> None:
    payload = load_intake(INTAKE)
    decision = _base_final_decision()
    decision["recommended_outcome"] = "accepted_vertex_circle_route"
    decision["accepted_gates"] = [
        "frontier_enumeration",
        "vertex_circle_geometry",
        "quotient_obstruction_replay",
        "independent_review",
    ]
    decision["rejected_gates"] = []
    decision["not_reviewed_gates"] = [
        "turn_geometry",
        "turn_arithmetic_replay",
        "kalmanson_geometry",
        "kalmanson_selfedge_replay",
        "kalmanson_corroboration",
        "lean_compilation",
    ]
    decision["precise_gaps"] = []

    errors = validate_decision_record(decision, payload)

    assert errors == []


def test_n9_review_decision_record_accepts_kalmanson_route_decision() -> None:
    payload = load_intake(INTAKE)
    decision = _base_final_decision()
    decision["recommended_outcome"] = "accepted_kalmanson_route"
    decision["accepted_gates"] = [
        "frontier_enumeration",
        "kalmanson_geometry",
        "kalmanson_selfedge_replay",
        "independent_review",
    ]
    decision["rejected_gates"] = []
    decision["not_reviewed_gates"] = [
        "vertex_circle_geometry",
        "quotient_obstruction_replay",
        "turn_geometry",
        "turn_arithmetic_replay",
        "kalmanson_corroboration",
        "lean_compilation",
    ]
    decision["precise_gaps"] = []

    errors = validate_decision_record(decision, payload)

    assert errors == []


def test_n9_review_decision_intake_renders_markdown_and_template() -> None:
    payload = load_intake(INTAKE)

    markdown = render_markdown(payload, [])
    template = dump_template(payload)

    assert "# n=9 Review Decision Intake" in markdown
    assert "`accepted_vertex_circle_route`" in markdown
    assert "decision_status: draft" in template
