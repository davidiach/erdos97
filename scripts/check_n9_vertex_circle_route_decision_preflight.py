#!/usr/bin/env python3
"""Preflight the n=9 vertex-circle route decision handoff."""
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


SCHEMA = "erdos97.n9_vertex_circle_route_decision_preflight.v1"
STATUS = "REVIEW_PREFLIGHT_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CANONICAL_COMMAND = (
    "python scripts/check_n9_vertex_circle_route_decision_preflight.py "
    "--check --summary-json"
)
ACCEPTED_VERTEX_CIRCLE_ROUTE = "accepted_vertex_circle_route"
VERTEX_CIRCLE_ROUTE_GATES = (
    "frontier_enumeration",
    "vertex_circle_geometry",
    "quotient_obstruction_replay",
)
DECISION_REQUIRED_ACCEPTED_GATES = (
    "frontier_enumeration",
    "vertex_circle_geometry",
    "quotient_obstruction_replay",
    "independent_review",
)
SOURCE_OF_TRUTH_UPDATE_ALLOWED = False


INTERNAL_REVIEW_NOTES: tuple[dict[str, Any], ...] = (
    {
        "id": "a6_a7_source_frontier",
        "gate_id": "frontier_enumeration",
        "path": "docs/n9-vertex-circle-a6-a7-frontier-review-2026-06-09.md",
        "outcomes": ("accepted_A6_A7_source_frontier_internal",),
        "required_phrases": (
            "not an external review-decision record",
            "`frontier_enumeration` gate",
            "open until",
            "does not support any of the following stronger statements",
            "Erdos Problem #97 is proved",
            "any counterexample is produced or certified",
            "the official/global status changes",
        ),
    },
    {
        "id": "a8_strict_edge_geometry",
        "gate_id": "vertex_circle_geometry",
        "path": "docs/n9-vertex-circle-a8-strict-edge-review-2026-06-09.md",
        "outcomes": ("accepted_A8_strict_edge_geometry_internal",),
        "required_phrases": (
            "not an external review-decision record",
            "`vertex_circle_geometry` gate",
            "open until",
            "does not support any of the following stronger statements",
            "Erdos Problem #97 is proved",
            "any counterexample is produced or certified",
            "the official/global status changes",
        ),
    },
    {
        "id": "a10_quotient_obstruction",
        "gate_id": "quotient_obstruction_replay",
        "path": "docs/n9-vertex-circle-a10-aggregate-review-2026-06-09.md",
        "outcomes": (
            "accepted_packet_soundness_T01_T12",
            "accepted_A10_bookkeeping_after_packet_soundness",
        ),
        "required_phrases": (
            "internal review-note outcome",
            "source-of-truth gate",
            "review-decision intake",
            "does not support any of the following stronger statements",
            "Erdos Problem #97 is proved",
            "any counterexample is produced or certified",
        ),
    },
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


def _all_gate_records(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for key in ("review_gates", "infrastructure_gates"):
        gates = ledger.get(key, [])
        if not isinstance(gates, list):
            continue
        for gate in gates:
            if isinstance(gate, dict) and isinstance(gate.get("id"), str):
                records[gate["id"]] = gate
    return records


def _review_outcome(ledger: dict[str, Any], outcome_id: str) -> dict[str, Any]:
    outcomes = ledger.get("review_outcomes", [])
    if not isinstance(outcomes, list):
        return {}
    for outcome in outcomes:
        if isinstance(outcome, dict) and outcome.get("id") == outcome_id:
            return outcome
    return {}


def _outcome_rule(intake: dict[str, Any], outcome_id: str) -> dict[str, Any]:
    rules = intake.get("outcome_rules", [])
    if not isinstance(rules, list):
        return {}
    for rule in rules:
        if isinstance(rule, dict) and rule.get("id") == outcome_id:
            return rule
    return {}


def _gate_list(
    payload: dict[str, Any],
    key: str,
    *,
    label: str,
    errors: list[str],
) -> tuple[str, ...]:
    values = payload.get(key)
    if not isinstance(values, list):
        errors.append(f"{label}.{key} must be a list")
        return ()
    strings: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str):
            errors.append(f"{label}.{key}[{index}] must be a string")
            continue
        strings.append(value)
    return tuple(strings)


def _decision_template_gate_ids(intake: dict[str, Any]) -> set[str]:
    template = intake.get("decision_template", {})
    if not isinstance(template, dict):
        return set()
    gates = template.get("not_reviewed_gates", [])
    if not isinstance(gates, list):
        return set()
    return {gate for gate in gates if isinstance(gate, str)}


def _draft_vertex_circle_decision_record(
    intake: dict[str, Any],
) -> dict[str, Any]:
    accepted = set(DECISION_REQUIRED_ACCEPTED_GATES)
    all_gates = _decision_template_gate_ids(intake)
    return {
        "schema": intake.get("decision_record_schema"),
        "decision_status": "draft",
        "reviewer_name": "",
        "review_date": "",
        "reviewed_git_head": "",
        "run_bundle_digest": "",
        "recommended_outcome": ACCEPTED_VERTEX_CIRCLE_ROUTE,
        "accepted_gates": sorted(accepted),
        "rejected_gates": [],
        "not_reviewed_gates": sorted(all_gates - accepted),
        "precise_gaps": [],
        "acknowledgements": {
            "no_general_proof_claimed": True,
            "no_counterexample_claimed": True,
            "official_status_unchanged": True,
            "source_of_truth_pr_required": True,
        },
        "notes": (
            "Schema preflight only. This draft shape is not a written review "
            "decision and does not accept any gate."
        ),
    }


def _validate_internal_notes() -> tuple[list[dict[str, Any]], list[str]]:
    summaries: list[dict[str, Any]] = []
    errors: list[str] = []
    for note in INTERNAL_REVIEW_NOTES:
        path = repo_path(str(note["path"]))
        summary: dict[str, Any] = {
            "id": note["id"],
            "gate_id": note["gate_id"],
            "path": note["path"],
            "path_exists": path.exists(),
            "expected_outcomes": list(note["outcomes"]),
            "missing_outcomes": [],
            "missing_required_phrases": [],
        }
        if not path.exists():
            errors.append(f"{note['id']} note is missing: {note['path']}")
            summaries.append(summary)
            continue
        text = path.read_text(encoding="utf-8")
        missing_outcomes = [
            outcome for outcome in note["outcomes"] if outcome not in text
        ]
        missing_phrases = [
            phrase for phrase in note["required_phrases"] if phrase not in text
        ]
        summary["missing_outcomes"] = missing_outcomes
        summary["missing_required_phrases"] = missing_phrases
        if missing_outcomes:
            errors.append(
                f"{note['id']} note missing outcomes: "
                + ", ".join(missing_outcomes)
            )
        if missing_phrases:
            errors.append(
                f"{note['id']} note missing required phrases: "
                + ", ".join(missing_phrases)
            )
        summaries.append(summary)
    return summaries, errors


def validate_preflight(
    *,
    ledger: dict[str, Any] | None = None,
    intake: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    if ledger is None:
        ledger = load_ledger(REPO_ROOT / "metadata" / "n9_review_gate_ledger.yaml")
    if intake is None:
        intake = load_intake(REPO_ROOT / "metadata" / "n9_review_decision_intake.yaml")

    errors.extend(f"review_gate_ledger: {error}" for error in validate_ledger(ledger))
    errors.extend(f"review_decision_intake: {error}" for error in validate_intake(intake))

    gate_records = _all_gate_records(ledger)
    gate_open_status: dict[str, bool | None] = {}
    for gate_id in (*VERTEX_CIRCLE_ROUTE_GATES, "independent_review"):
        record = gate_records.get(gate_id)
        gate_open_status[gate_id] = record.get("still_open") if record else None
        if record is None:
            errors.append(f"gate {gate_id!r} is missing from the ledger")
        elif record.get("still_open") is not True:
            errors.append(f"gate {gate_id!r} must remain open before review intake")

    ledger_outcome = _review_outcome(ledger, ACCEPTED_VERTEX_CIRCLE_ROUTE)
    ledger_required = _gate_list(
        ledger_outcome,
        "required_gates",
        label="ledger accepted_vertex_circle_route",
        errors=errors,
    )
    if set(ledger_required) != set(VERTEX_CIRCLE_ROUTE_GATES):
        errors.append(
            "ledger accepted_vertex_circle_route must require exactly "
            + ", ".join(VERTEX_CIRCLE_ROUTE_GATES)
        )

    intake_rule = _outcome_rule(intake, ACCEPTED_VERTEX_CIRCLE_ROUTE)
    intake_required = _gate_list(
        intake_rule,
        "required_accepted_gates",
        label="intake accepted_vertex_circle_route",
        errors=errors,
    )
    intake_blocking = _gate_list(
        intake_rule,
        "blocks_if_rejected_or_unreviewed",
        label="intake accepted_vertex_circle_route",
        errors=errors,
    )
    if set(intake_required) != set(DECISION_REQUIRED_ACCEPTED_GATES):
        errors.append(
            "intake accepted_vertex_circle_route must require exactly "
            + ", ".join(DECISION_REQUIRED_ACCEPTED_GATES)
        )
    if set(intake_blocking) != set(DECISION_REQUIRED_ACCEPTED_GATES):
        errors.append(
            "intake accepted_vertex_circle_route must be blocked by exactly "
            + ", ".join(DECISION_REQUIRED_ACCEPTED_GATES)
        )

    note_summaries, note_errors = _validate_internal_notes()
    errors.extend(note_errors)

    draft_decision = _draft_vertex_circle_decision_record(intake)
    try:
        draft_errors = validate_decision_record(
            draft_decision,
            intake,
            gate_ledger=ledger,
        )
    except TypeError as exc:
        draft_errors = [
            "decision-intake draft shape validation could not run cleanly: "
            f"{exc}"
        ]
    errors.extend(
        f"draft vertex-circle decision shape: {error}" for error in draft_errors
    )

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "canonical_command": CANONICAL_COMMAND,
        "route_outcome": ACCEPTED_VERTEX_CIRCLE_ROUTE,
        "route_gate_ids": list(VERTEX_CIRCLE_ROUTE_GATES),
        "decision_required_accepted_gates": list(DECISION_REQUIRED_ACCEPTED_GATES),
        "gate_open_status": gate_open_status,
        "all_required_gates_still_open": all(
            gate_open_status.get(gate_id) is True
            for gate_id in (*VERTEX_CIRCLE_ROUTE_GATES, "independent_review")
        ),
        "internal_review_notes": note_summaries,
        "draft_vertex_circle_decision_shape": {
            "decision_status": draft_decision["decision_status"],
            "recommended_outcome": draft_decision["recommended_outcome"],
            "accepted_gates": draft_decision["accepted_gates"],
            "not_reviewed_gates": draft_decision["not_reviewed_gates"],
            "validation_status": "passed" if not draft_errors else "failed",
            "validation_error_count": len(draft_errors),
            "first_validation_errors": draft_errors[:5],
            "boundary": draft_decision["notes"],
        },
        "source_of_truth_update_allowed": SOURCE_OF_TRUTH_UPDATE_ALLOWED,
        "next_required_external_artifact": (
            "A written independent review decision record validated by "
            "python scripts/check_n9_review_decision_intake.py --decision "
            "<path> --check --summary-json."
        ),
    }
    return payload, errors


def summary_payload(payload: dict[str, Any], errors: Sequence[str]) -> dict[str, Any]:
    note_summaries = payload.get("internal_review_notes", [])
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "route_outcome": payload.get("route_outcome"),
        "route_gate_ids": payload.get("route_gate_ids"),
        "decision_required_accepted_gates": payload.get(
            "decision_required_accepted_gates"
        ),
        "all_required_gates_still_open": payload.get(
            "all_required_gates_still_open"
        ),
        "internal_review_note_count": len(note_summaries)
        if isinstance(note_summaries, list)
        else 0,
        "draft_vertex_circle_decision_shape_validation_status": payload.get(
            "draft_vertex_circle_decision_shape", {}
        ).get("validation_status"),
        "source_of_truth_update_allowed": payload.get(
            "source_of_truth_update_allowed"
        ),
        "next_required_external_artifact": payload.get(
            "next_required_external_artifact"
        ),
        "validation_status": "passed" if not errors else "failed",
        "validation_error_count": len(errors),
        "first_validation_errors": list(errors[:5]),
    }


def render_markdown(payload: dict[str, Any], errors: Sequence[str]) -> str:
    status = "passed" if not errors else "failed"
    lines: list[str] = [
        "# n=9 Vertex-circle Route Decision Preflight",
        "",
        "Status: `REVIEW_PREFLIGHT_ONLY`.",
        "",
        "This preflight checks that the internal A6/A7, A8, and A10 review "
        "notes are present, that the vertex-circle route gates remain open, "
        "and that the decision-intake schema still requires written "
        "independent review before `accepted_vertex_circle_route` can be "
        "recorded.",
        "",
        "## Result",
        "",
        f"- Validation status: `{status}`",
        f"- Route outcome: `{payload.get('route_outcome')}`",
        "- Required accepted gates: "
        + ", ".join(
            f"`{gate}`"
            for gate in payload.get("decision_required_accepted_gates", [])
        ),
        f"- Source-of-truth update allowed: "
        f"`{payload.get('source_of_truth_update_allowed')}`",
        "",
        "## Internal Notes",
        "",
    ]
    for note in payload.get("internal_review_notes", []):
        lines.append(
            f"- `{note.get('id')}` -> `{note.get('gate_id')}`: "
            f"`{note.get('path')}`"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is not a review decision and does not accept any gate. The "
            "next external artifact remains a written decision record "
            "validated by the decision-intake checker.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail on validation errors")
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
    try:
        payload, errors = validate_preflight()
    except (OSError, ValueError, YAMLError) as exc:
        payload = {"schema": SCHEMA, "status": "LOAD_FAILED", "trust": TRUST}
        errors = [str(exc)]

    if args.markdown:
        print(render_markdown(payload, errors))
    elif args.summary_json:
        print(json.dumps(summary_payload(payload, errors), indent=2, sort_keys=True))
    elif args.json:
        full_payload = dict(payload)
        full_payload["validation_status"] = "passed" if not errors else "failed"
        full_payload["validation_errors"] = errors
        print(json.dumps(full_payload, indent=2, sort_keys=True))
    else:
        print("n=9 vertex-circle route decision preflight")
        print(f"status: {payload.get('status')}")
        print(f"validation_status: {'passed' if not errors else 'failed'}")

    if args.check and errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
