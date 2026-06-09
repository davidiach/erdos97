#!/usr/bin/env python3
"""Validate the n=9 vertex-circle route decision-request packet."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only without dependencies.
    yaml = None
    YAMLError = ValueError
else:
    YAMLError = yaml.YAMLError


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_n9_review_decision_intake import (  # noqa: E402
    load_intake,
    validate_decision_record,
    validate_intake,
)
from scripts.check_n9_review_gate_ledger import (  # noqa: E402
    load_ledger,
    validate_ledger,
)
from scripts.check_n9_vertex_circle_route_decision_preflight import (  # noqa: E402
    DECISION_REQUIRED_ACCEPTED_GATES,
    INTERNAL_REVIEW_NOTES,
    validate_preflight,
)


DEFAULT_REQUEST = (
    REPO_ROOT / "metadata" / "n9_vertex_circle_route_decision_request.yaml"
)
SCHEMA = "erdos97.n9_vertex_circle_route_decision_request.v1"
STATUS = "REVIEW_DECISION_REQUEST_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
ACCEPTED_VERTEX_CIRCLE_ROUTE = "accepted_vertex_circle_route"
SOURCE_OF_TRUTH_UPDATE_ALLOWED = False
EXTERNAL_REVIEWER_REQUIRED = True
CANONICAL_COMMAND = (
    "python scripts/check_n9_vertex_circle_route_decision_request.py "
    "--check --summary-json"
)
MARKDOWN_COMMAND = (
    "python scripts/check_n9_vertex_circle_route_decision_request.py --markdown"
)
PREFLIGHT_COMMAND = (
    "python scripts/check_n9_vertex_circle_route_decision_preflight.py "
    "--check --summary-json"
)
RUN_CAPTURE_COMMAND = (
    "python scripts/check_n9_review_run_bundle.py --check --run --summary-json"
)
DECISION_TEMPLATE_COMMAND = (
    "python scripts/check_n9_review_decision_intake.py --template"
)
DECISION_VALIDATION_COMMAND = (
    "python scripts/check_n9_review_decision_intake.py --decision "
    "path/to/decision.yaml --check --summary-json"
)
REVIEWER_STEP_COMMANDS = {
    "preflight": PREFLIGHT_COMMAND,
    "live_run_capture": RUN_CAPTURE_COMMAND,
    "template": DECISION_TEMPLATE_COMMAND,
    "filled_decision_validation": DECISION_VALIDATION_COMMAND,
}
LINKED_FILES = {
    "candidate_manifest": "metadata/n9_candidate_review.yaml",
    "review_gate_ledger": "metadata/n9_review_gate_ledger.yaml",
    "review_evidence_matrix": "metadata/n9_review_evidence_matrix.yaml",
    "review_dossier": "metadata/n9_review_dossier.yaml",
    "review_run_bundle": "metadata/n9_review_run_bundle.yaml",
    "review_decision_intake": "metadata/n9_review_decision_intake.yaml",
    "route_preflight": "docs/n9-vertex-circle-route-decision-preflight.md",
}
REQUIRED_FORBIDDEN_PROMOTIONS = {
    "general proof of Erdos Problem #97",
    "proof of n=9",
    "counterexample to Erdos Problem #97",
    "official/global status update",
    "completed independent review",
    "accepted review gate",
    "formal proof of the Euclidean turn lemma",
}
REQUIRED_CLAIM_SCOPE_PHRASES = (
    "does not prove n=9",
    "does not prove Erdos Problem #97",
    "does not claim a counterexample",
    "does not complete independent review",
    "does not accept any review gate",
    "does not update the official/global status",
)


def repo_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def load_yaml_mapping(path: Path, *, label: str) -> dict[str, Any]:
    if yaml is None:
        raise ValueError(
            f"PyYAML is required to parse {label}; install with `pip install -e .`"
        )
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} top level must be a mapping")
    return payload


def load_request(path: Path = DEFAULT_REQUEST) -> dict[str, Any]:
    return load_yaml_mapping(
        path,
        label="metadata/n9_vertex_circle_route_decision_request.yaml",
    )


def _decision_gate_ids(intake: dict[str, Any]) -> set[str]:
    template = intake.get("decision_template", {})
    if not isinstance(template, dict):
        return set()
    gates = template.get("not_reviewed_gates", [])
    if not isinstance(gates, list):
        return set()
    return {gate for gate in gates if isinstance(gate, str)}


def _string_list(value: Any, *, label: str) -> tuple[list[str], list[str]]:
    if not isinstance(value, list):
        return [], [f"{label} must be a list"]
    strings: list[str] = []
    errors: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{label}[{index}] must be a nonempty string")
        else:
            strings.append(item)
    return strings, errors


def _validate_paths(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, expected in LINKED_FILES.items():
        if payload.get(key) != expected:
            errors.append(f"{key} must be {expected!r}")
            continue
        if not repo_path(expected).exists():
            errors.append(f"{key} does not exist: {expected}")

    docs, doc_errors = _string_list(
        payload.get("request_documents"),
        label="request_documents",
    )
    errors.extend(doc_errors)
    for index, doc in enumerate(docs):
        if not repo_path(doc).exists():
            errors.append(f"request_documents[{index}] does not exist: {doc}")
    return errors


def _validate_claim_scope(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str) or not claim_scope.strip():
        errors.append("claim_scope must be a nonempty string")
    else:
        for phrase in REQUIRED_CLAIM_SCOPE_PHRASES:
            if phrase not in claim_scope:
                errors.append(f"claim_scope must include {phrase!r}")

    forbidden = payload.get("forbidden_promotions")
    if not isinstance(forbidden, list) or not forbidden:
        errors.append("forbidden_promotions must be a nonempty list")
    else:
        missing = REQUIRED_FORBIDDEN_PROMOTIONS - set(forbidden)
        for phrase in sorted(missing):
            errors.append(f"forbidden_promotions missing {phrase!r}")
    return errors


def _validate_commands(payload: dict[str, Any]) -> list[str]:
    expected = {
        "canonical_command": CANONICAL_COMMAND,
        "markdown_command": MARKDOWN_COMMAND,
        "preflight_command": PREFLIGHT_COMMAND,
        "run_capture_command": RUN_CAPTURE_COMMAND,
        "decision_template_command": DECISION_TEMPLATE_COMMAND,
        "decision_validation_command": DECISION_VALIDATION_COMMAND,
    }
    errors = [
        f"{key} must be {command!r}"
        for key, command in expected.items()
        if payload.get(key) != command
    ]
    steps = payload.get("reviewer_steps")
    if not isinstance(steps, list):
        errors.append("reviewer_steps must be a list")
        return errors
    seen: set[str] = set()
    for index, step in enumerate(steps):
        label = f"reviewer_steps[{index}]"
        if not isinstance(step, dict):
            errors.append(f"{label} must be a mapping")
            continue
        step_id = step.get("id")
        if not isinstance(step_id, str) or step_id not in REVIEWER_STEP_COMMANDS:
            errors.append(f"{label}.id is not an expected reviewer step")
            continue
        seen.add(step_id)
        expected_command = REVIEWER_STEP_COMMANDS[step_id]
        if step.get("command") != expected_command:
            errors.append(f"{label}.command must be {expected_command!r}")
        purpose = step.get("purpose")
        if not isinstance(purpose, str) or not purpose.strip():
            errors.append(f"{label}.purpose must be a nonempty string")
    for step_id in sorted(set(REVIEWER_STEP_COMMANDS) - seen):
        errors.append(f"reviewer_steps missing {step_id!r}")
    return errors


def _validate_internal_review_notes(payload: dict[str, Any]) -> list[str]:
    notes = payload.get("internal_review_notes")
    if not isinstance(notes, list):
        return ["internal_review_notes must be a list"]

    errors: list[str] = []
    expected_notes = {
        str(note["id"]): note
        for note in INTERNAL_REVIEW_NOTES
        if isinstance(note.get("id"), str)
    }
    observed_ids: set[str] = set()
    for index, note in enumerate(notes):
        label = f"internal_review_notes[{index}]"
        if not isinstance(note, dict):
            errors.append(f"{label} must be a mapping")
            continue
        note_id = note.get("id")
        if not isinstance(note_id, str) or note_id not in expected_notes:
            errors.append(f"{label}.id is not an expected internal note")
            continue
        observed_ids.add(note_id)
        expected = expected_notes[note_id]
        if note.get("gate_id") != expected["gate_id"]:
            errors.append(f"{label}.gate_id must be {expected['gate_id']!r}")
        if note.get("path") != expected["path"]:
            errors.append(f"{label}.path must be {expected['path']!r}")
        outcomes, outcome_errors = _string_list(
            note.get("expected_outcomes"),
            label=f"{label}.expected_outcomes",
        )
        errors.extend(outcome_errors)
        if set(outcomes) != set(expected["outcomes"]):
            errors.append(f"{label}.expected_outcomes does not match preflight")
    for note_id in sorted(set(expected_notes) - observed_ids):
        errors.append(f"internal_review_notes missing {note_id!r}")
    return errors


def _validate_required_acknowledgements(payload: dict[str, Any]) -> list[str]:
    acknowledgements = payload.get("required_acknowledgements")
    if not isinstance(acknowledgements, dict):
        return ["required_acknowledgements must be a mapping"]
    errors: list[str] = []
    for key in (
        "no_general_proof_claimed",
        "no_counterexample_claimed",
        "official_status_unchanged",
        "source_of_truth_pr_required",
    ):
        if acknowledgements.get(key) is not True:
            errors.append(f"required_acknowledgements.{key} must be true")
    return errors


def _draft_requested_decision(
    payload: dict[str, Any],
    intake: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": intake.get("decision_record_schema"),
        "decision_status": "draft",
        "reviewer_name": "",
        "review_date": "",
        "reviewed_git_head": "",
        "run_bundle_digest": "",
        "recommended_outcome": payload.get("requested_outcome"),
        "accepted_gates": payload.get("requested_accepted_gates", []),
        "rejected_gates": payload.get("requested_rejected_gates", []),
        "not_reviewed_gates": payload.get("requested_not_reviewed_gates", []),
        "precise_gaps": [],
        "acknowledgements": payload.get("required_acknowledgements", {}),
        "notes": (
            "Decision-request shape only. This record is not a written "
            "independent review and does not accept any gate."
        ),
    }


def validate_request(
    payload: dict[str, Any],
    *,
    ledger: dict[str, Any] | None = None,
    intake: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    if payload.get("schema") != SCHEMA:
        errors.append(f"schema is {payload.get('schema')!r}, expected {SCHEMA!r}")
    if payload.get("status") != STATUS:
        errors.append(f"status is {payload.get('status')!r}, expected {STATUS!r}")
    if payload.get("trust") != TRUST:
        errors.append(f"trust is {payload.get('trust')!r}, expected {TRUST!r}")

    errors.extend(_validate_paths(payload))
    errors.extend(_validate_claim_scope(payload))
    errors.extend(_validate_commands(payload))
    errors.extend(_validate_internal_review_notes(payload))
    errors.extend(_validate_required_acknowledgements(payload))

    if ledger is None:
        ledger = load_ledger(repo_path(LINKED_FILES["review_gate_ledger"]))
    if intake is None:
        intake = load_intake(repo_path(LINKED_FILES["review_decision_intake"]))

    errors.extend(f"review_gate_ledger: {error}" for error in validate_ledger(ledger))
    errors.extend(f"review_decision_intake: {error}" for error in validate_intake(intake))

    preflight_payload, preflight_errors = validate_preflight(
        ledger=ledger,
        intake=intake,
    )
    errors.extend(f"route_preflight: {error}" for error in preflight_errors)

    all_gate_ids = _decision_gate_ids(intake)
    accepted_values, accepted_errors = _string_list(
        payload.get("requested_accepted_gates"),
        label="requested_accepted_gates",
    )
    rejected_values, rejected_errors = _string_list(
        payload.get("requested_rejected_gates"),
        label="requested_rejected_gates",
    )
    not_reviewed_values, not_reviewed_errors = _string_list(
        payload.get("requested_not_reviewed_gates"),
        label="requested_not_reviewed_gates",
    )
    errors.extend(accepted_errors)
    errors.extend(rejected_errors)
    errors.extend(not_reviewed_errors)
    accepted = tuple(accepted_values)
    rejected = tuple(rejected_values)
    not_reviewed = tuple(not_reviewed_values)
    expected_not_reviewed = all_gate_ids - set(DECISION_REQUIRED_ACCEPTED_GATES)

    if payload.get("requested_outcome") != ACCEPTED_VERTEX_CIRCLE_ROUTE:
        errors.append(
            f"requested_outcome must be {ACCEPTED_VERTEX_CIRCLE_ROUTE!r}"
        )
    if tuple(accepted) != DECISION_REQUIRED_ACCEPTED_GATES:
        errors.append(
            "requested_accepted_gates must match the vertex-circle "
            "decision-intake gate order"
        )
    if list(rejected) != []:
        errors.append("requested_rejected_gates must be empty for this request")
    if set(not_reviewed) != expected_not_reviewed:
        errors.append(
            "requested_not_reviewed_gates must be the non-vertex-circle "
            "decision gates"
        )
    if payload.get("source_of_truth_update_allowed") is not SOURCE_OF_TRUTH_UPDATE_ALLOWED:
        errors.append("source_of_truth_update_allowed must be false")
    if payload.get("external_reviewer_required") is not EXTERNAL_REVIEWER_REQUIRED:
        errors.append("external_reviewer_required must be true")
    if payload.get("decision_record_status") != "draft_request_only":
        errors.append("decision_record_status must be 'draft_request_only'")

    draft_decision = _draft_requested_decision(payload, intake)
    decision_errors = validate_decision_record(
        draft_decision,
        intake,
        gate_ledger=ledger,
    )
    errors.extend(f"requested decision shape: {error}" for error in decision_errors)

    request_payload = build_request_payload(
        payload,
        preflight_errors=preflight_errors,
        decision_errors=decision_errors,
    )
    return request_payload, errors


def build_request_payload(
    payload: dict[str, Any],
    *,
    preflight_errors: Sequence[str] | None = None,
    decision_errors: Sequence[str] | None = None,
) -> dict[str, Any]:
    preflight_errors = list(preflight_errors or [])
    decision_errors = list(decision_errors or [])
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "claim_scope": payload.get("claim_scope"),
        "requested_outcome": payload.get("requested_outcome"),
        "requested_accepted_gates": payload.get("requested_accepted_gates", []),
        "requested_rejected_gates": payload.get("requested_rejected_gates", []),
        "requested_not_reviewed_gates": payload.get("requested_not_reviewed_gates", []),
        "request_documents": payload.get("request_documents", []),
        "internal_review_notes": payload.get("internal_review_notes", []),
        "preflight_command": payload.get("preflight_command"),
        "run_capture_command": payload.get("run_capture_command"),
        "decision_template_command": payload.get("decision_template_command"),
        "decision_validation_command": payload.get("decision_validation_command"),
        "preflight_validation_status": (
            "passed" if not preflight_errors else "failed"
        ),
        "preflight_validation_error_count": len(preflight_errors),
        "first_preflight_validation_errors": preflight_errors[:5],
        "requested_decision_shape_validation_status": (
            "passed" if not decision_errors else "failed"
        ),
        "requested_decision_shape_validation_error_count": len(decision_errors),
        "first_requested_decision_shape_errors": decision_errors[:5],
        "external_reviewer_required": payload.get("external_reviewer_required"),
        "source_of_truth_update_allowed": payload.get(
            "source_of_truth_update_allowed"
        ),
    }


def summary_payload(
    request_payload: dict[str, Any],
    errors: Sequence[str],
) -> dict[str, Any]:
    return {
        "schema": request_payload.get("schema"),
        "status": request_payload.get("status"),
        "trust": request_payload.get("trust"),
        "requested_outcome": request_payload.get("requested_outcome"),
        "requested_accepted_gate_count": len(
            request_payload.get("requested_accepted_gates", [])
        ),
        "requested_not_reviewed_gate_count": len(
            request_payload.get("requested_not_reviewed_gates", [])
        ),
        "internal_review_note_count": len(
            request_payload.get("internal_review_notes", [])
        ),
        "request_document_count": len(request_payload.get("request_documents", [])),
        "preflight_validation_status": request_payload.get(
            "preflight_validation_status"
        ),
        "requested_decision_shape_validation_status": request_payload.get(
            "requested_decision_shape_validation_status"
        ),
        "external_reviewer_required": request_payload.get(
            "external_reviewer_required"
        ),
        "source_of_truth_update_allowed": request_payload.get(
            "source_of_truth_update_allowed"
        ),
        "validation_status": "passed" if not errors else "failed",
        "validation_error_count": len(errors),
        "first_validation_errors": list(errors[:5]),
    }


def render_markdown(
    request_payload: dict[str, Any],
    errors: Sequence[str],
) -> str:
    status = "passed" if not errors else "failed"
    lines: list[str] = [
        "# n=9 Vertex-circle Route Decision Request",
        "",
        "Status: `REVIEW_DECISION_REQUEST_ONLY`.",
        "",
        str(request_payload.get("claim_scope", "")).strip(),
        "",
        "## Request",
        "",
        f"- Validation status: `{status}`",
        f"- Requested outcome: `{request_payload.get('requested_outcome')}`",
        "- Requested accepted gates: "
        + ", ".join(
            f"`{gate}`"
            for gate in request_payload.get("requested_accepted_gates", [])
        ),
        "- Requested not-reviewed gates: "
        + ", ".join(
            f"`{gate}`"
            for gate in request_payload.get("requested_not_reviewed_gates", [])
        ),
        f"- Source-of-truth update allowed: "
        f"`{request_payload.get('source_of_truth_update_allowed')}`",
        "",
        "## Reviewer Commands",
        "",
        f"- Preflight: `{request_payload.get('preflight_command')}`",
        f"- Live run capture: `{request_payload.get('run_capture_command')}`",
        f"- Decision template: `{request_payload.get('decision_template_command')}`",
        f"- Validate filled decision: "
        f"`{request_payload.get('decision_validation_command')}`",
        "",
        "## Boundary",
        "",
        "This request packet is not a written independent review, does not "
        "accept any gate, and does not update any source-of-truth status file.",
        "",
    ]
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, default=DEFAULT_REQUEST)
    parser.add_argument("--check", action="store_true", help="fail on errors")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print compact reviewer-facing JSON",
    )
    output_group.add_argument("--markdown", action="store_true", help="print Markdown")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    request_path = args.request
    if not request_path.is_absolute():
        request_path = REPO_ROOT / request_path

    try:
        payload = load_request(request_path)
        request_payload, errors = validate_request(payload)
    except (OSError, ValueError, YAMLError) as exc:
        request_payload = {"schema": SCHEMA, "status": "LOAD_FAILED", "trust": TRUST}
        errors = [str(exc)]

    if args.markdown:
        print(render_markdown(request_payload, errors))
    elif args.summary_json:
        print(json.dumps(summary_payload(request_payload, errors), indent=2))
    elif args.json:
        full_payload = dict(request_payload)
        full_payload["validation_status"] = "passed" if not errors else "failed"
        full_payload["validation_errors"] = errors
        print(json.dumps(full_payload, indent=2, sort_keys=True))
    else:
        print("n=9 vertex-circle route decision request")
        print(f"status: {request_payload.get('status')}")
        print(f"validation_status: {'passed' if not errors else 'failed'}")

    if args.check and errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
