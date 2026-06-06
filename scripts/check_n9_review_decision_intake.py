#!/usr/bin/env python3
"""Validate n=9 reviewer-decision intake records."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
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

DEFAULT_INTAKE = REPO_ROOT / "metadata" / "n9_review_decision_intake.yaml"
SCHEMA = "erdos97.n9_review_decision_intake.v1"
STATUS = "REVIEW_DECISION_INTAKE_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CANDIDATE_MANIFEST = "metadata/n9_candidate_review.yaml"
REVIEW_GATE_LEDGER = "metadata/n9_review_gate_ledger.yaml"
REVIEW_EVIDENCE_MATRIX = "metadata/n9_review_evidence_matrix.yaml"
REVIEW_DOSSIER = "metadata/n9_review_dossier.yaml"
REVIEW_RUN_BUNDLE = "metadata/n9_review_run_bundle.yaml"
CANONICAL_COMMAND = (
    "python scripts/check_n9_review_decision_intake.py --check --summary-json"
)
TEMPLATE_COMMAND = "python scripts/check_n9_review_decision_intake.py --template"
MARKDOWN_COMMAND = "python scripts/check_n9_review_decision_intake.py --markdown"
REQUIRED_FORBIDDEN_PROMOTIONS = {
    "general proof of Erdos Problem #97",
    "proof of n=9",
    "counterexample to Erdos Problem #97",
    "official/global status update",
    "completed independent review",
    "formal proof of the Euclidean turn lemma",
}
REQUIRED_CLAIM_SCOPE_PHRASES = (
    "does not prove n=9",
    "does not prove Erdos Problem #97",
    "does not claim a counterexample",
    "does not complete independent review",
    "does not update the official/global status",
)
REQUIRED_DECISION_FIELDS = {
    "schema",
    "decision_status",
    "reviewer_name",
    "review_date",
    "reviewed_git_head",
    "run_bundle_digest",
    "recommended_outcome",
    "accepted_gates",
    "rejected_gates",
    "not_reviewed_gates",
    "precise_gaps",
    "acknowledgements",
    "notes",
}
REQUIRED_ACKNOWLEDGEMENTS = {
    "no_general_proof_claimed",
    "no_counterexample_claimed",
    "official_status_unchanged",
    "source_of_truth_pr_required",
}
DECISION_RECORD_SCHEMA = "erdos97.n9_review_decision_record.v1"
DECISION_STATUSES = {"draft", "final"}
GATE_PARTITION_FIELDS = ("accepted_gates", "rejected_gates", "not_reviewed_gates")


def _linked_validators() -> tuple[Any, Any, Any, Any, Any]:
    from scripts.check_n9_candidate_review_manifest import validate_manifest
    from scripts.check_n9_review_dossier import validate_dossier
    from scripts.check_n9_review_evidence_matrix import validate_matrix
    from scripts.check_n9_review_gate_ledger import validate_ledger
    from scripts.check_n9_review_run_bundle import validate_bundle

    return (
        validate_manifest,
        validate_ledger,
        validate_matrix,
        validate_dossier,
        validate_bundle,
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


def load_intake(path: Path = DEFAULT_INTAKE) -> dict[str, Any]:
    return load_yaml_mapping(path, label="metadata/n9_review_decision_intake.yaml")


def load_decision(path: Path) -> dict[str, Any]:
    return load_yaml_mapping(path, label=str(path))


def _load_linked_payloads(
    payload: dict[str, Any],
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    list[str],
]:
    errors: list[str] = []
    linked: list[tuple[str, str]] = [
        ("candidate_manifest", CANDIDATE_MANIFEST),
        ("review_gate_ledger", REVIEW_GATE_LEDGER),
        ("review_evidence_matrix", REVIEW_EVIDENCE_MATRIX),
        ("review_dossier", REVIEW_DOSSIER),
        ("review_run_bundle", REVIEW_RUN_BUNDLE),
    ]
    loaded: dict[str, dict[str, Any]] = {}
    for key, expected in linked:
        value = payload.get(key)
        if value != expected:
            errors.append(f"{key} must be {expected!r}")
            loaded[key] = {}
            continue
        try:
            loaded[key] = load_yaml_mapping(repo_path(expected), label=expected)
        except (OSError, ValueError, YAMLError) as exc:
            errors.append(str(exc))
            loaded[key] = {}
    return (
        loaded["candidate_manifest"],
        loaded["review_gate_ledger"],
        loaded["review_evidence_matrix"],
        loaded["review_dossier"],
        loaded["review_run_bundle"],
        errors,
    )


def _gate_ids(ledger: dict[str, Any]) -> set[str]:
    gate_ids: set[str] = set()
    for key in ("review_gates", "infrastructure_gates"):
        gates = ledger.get(key, [])
        if not isinstance(gates, list):
            continue
        for gate in gates:
            if isinstance(gate, dict) and isinstance(gate.get("id"), str):
                gate_ids.add(gate["id"])
    return gate_ids


def _review_outcome_ids(ledger: dict[str, Any]) -> set[str]:
    outcomes = ledger.get("review_outcomes", [])
    if not isinstance(outcomes, list):
        return set()
    return {
        outcome["id"]
        for outcome in outcomes
        if isinstance(outcome, dict) and isinstance(outcome.get("id"), str)
    }


def _outcome_rules(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rules = payload.get("outcome_rules", [])
    if not isinstance(rules, list):
        return {}
    return {
        rule["id"]: rule
        for rule in rules
        if isinstance(rule, dict) and isinstance(rule.get("id"), str)
    }


def _validate_forbidden_promotions(payload: dict[str, Any]) -> list[str]:
    forbidden = payload.get("forbidden_promotions")
    if not isinstance(forbidden, list) or not forbidden:
        return ["forbidden_promotions must be a nonempty list"]
    missing = REQUIRED_FORBIDDEN_PROMOTIONS - set(forbidden)
    return [
        f"forbidden_promotions missing {phrase!r}"
        for phrase in sorted(missing)
    ]


def _validate_required_documents(payload: dict[str, Any]) -> list[str]:
    docs = payload.get("required_documents")
    if not isinstance(docs, list) or not docs:
        return ["required_documents must be a nonempty list"]
    errors: list[str] = []
    seen: set[str] = set()
    for index, doc in enumerate(docs):
        label = f"required_documents[{index}]"
        if not isinstance(doc, str) or not doc.strip():
            errors.append(f"{label} must be a nonempty string")
            continue
        if doc in seen:
            errors.append(f"{label} duplicates {doc!r}")
        seen.add(doc)
        if not repo_path(doc).exists():
            errors.append(f"{label} does not exist: {doc}")
    return errors


def _validate_template_shape(
    payload: dict[str, Any],
    *,
    gate_ids: set[str],
) -> list[str]:
    template = payload.get("decision_template")
    if not isinstance(template, dict):
        return ["decision_template must be a mapping"]

    errors: list[str] = []
    missing_fields = REQUIRED_DECISION_FIELDS - set(template)
    for field in sorted(missing_fields):
        errors.append(f"decision_template missing {field!r}")
    if template.get("schema") != payload.get("decision_record_schema"):
        errors.append("decision_template.schema must match decision_record_schema")
    if template.get("decision_status") != "draft":
        errors.append("decision_template.decision_status must be 'draft'")
    accepted = set(template.get("accepted_gates", []))
    rejected = set(template.get("rejected_gates", []))
    not_reviewed = set(template.get("not_reviewed_gates", []))
    if accepted or rejected:
        errors.append("decision_template must not pre-accept or pre-reject gates")
    if gate_ids and not_reviewed != gate_ids:
        errors.append("decision_template.not_reviewed_gates must contain every gate")
    acknowledgements = template.get("acknowledgements", {})
    if not isinstance(acknowledgements, dict):
        errors.append("decision_template.acknowledgements must be a mapping")
    else:
        for key in sorted(REQUIRED_ACKNOWLEDGEMENTS):
            if key not in acknowledgements:
                errors.append(f"decision_template.acknowledgements missing {key!r}")
    return errors


def _validate_outcome_rules(
    payload: dict[str, Any],
    *,
    gate_ids: set[str],
    outcome_ids: set[str],
) -> list[str]:
    rules = payload.get("outcome_rules")
    if not isinstance(rules, list) or not rules:
        return ["outcome_rules must be a nonempty list"]

    errors: list[str] = []
    seen: set[str] = set()
    for index, rule in enumerate(rules):
        label = f"outcome_rules[{index}]"
        if not isinstance(rule, dict):
            errors.append(f"{label} must be a mapping")
            continue
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not rule_id.strip():
            errors.append(f"{label}.id must be a nonempty string")
        elif rule_id in seen:
            errors.append(f"{label}.id {rule_id!r} is duplicated")
        else:
            seen.add(rule_id)
        for key in ("required_accepted_gates", "blocks_if_rejected_or_unreviewed"):
            value = rule.get(key)
            if not isinstance(value, list):
                errors.append(f"{label}.{key} must be a list")
                continue
            unknown = {gate for gate in value if isinstance(gate, str)} - gate_ids
            for gate in sorted(unknown):
                errors.append(f"{label}.{key} unknown gate {gate!r}")
            if any(not isinstance(gate, str) for gate in value):
                errors.append(f"{label}.{key} must contain only strings")
        boundary = rule.get("follow_up_boundary")
        if not isinstance(boundary, str) or not boundary.strip():
            errors.append(f"{label}.follow_up_boundary must be a nonempty string")

    missing = outcome_ids - seen
    extra = seen - outcome_ids
    for outcome_id in sorted(missing):
        errors.append(f"outcome_rules missing ledger outcome {outcome_id!r}")
    for outcome_id in sorted(extra):
        errors.append(f"outcome_rules contains unknown outcome {outcome_id!r}")
    return errors


def validate_intake(
    payload: dict[str, Any],
    *,
    candidate_manifest: dict[str, Any] | None = None,
    gate_ledger: dict[str, Any] | None = None,
    evidence_matrix: dict[str, Any] | None = None,
    dossier: dict[str, Any] | None = None,
    run_bundle: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != SCHEMA:
        errors.append(f"schema is {payload.get('schema')!r}, expected {SCHEMA!r}")
    if payload.get("status") != STATUS:
        errors.append(f"status is {payload.get('status')!r}, expected {STATUS!r}")
    if payload.get("trust") != TRUST:
        errors.append(f"trust is {payload.get('trust')!r}, expected {TRUST!r}")
    if payload.get("canonical_command") != CANONICAL_COMMAND:
        errors.append(f"canonical_command must be {CANONICAL_COMMAND!r}")
    if payload.get("template_command") != TEMPLATE_COMMAND:
        errors.append(f"template_command must be {TEMPLATE_COMMAND!r}")
    if payload.get("markdown_command") != MARKDOWN_COMMAND:
        errors.append(f"markdown_command must be {MARKDOWN_COMMAND!r}")

    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str) or not claim_scope.strip():
        errors.append("claim_scope must be a nonempty string")
    else:
        for phrase in REQUIRED_CLAIM_SCOPE_PHRASES:
            if phrase not in claim_scope:
                errors.append(f"claim_scope must include {phrase!r}")

    errors.extend(_validate_forbidden_promotions(payload))
    errors.extend(_validate_required_documents(payload))

    if payload.get("decision_record_schema") != DECISION_RECORD_SCHEMA:
        errors.append(f"decision_record_schema must be {DECISION_RECORD_SCHEMA!r}")
    statuses = payload.get("decision_statuses")
    if not isinstance(statuses, list) or set(statuses) != DECISION_STATUSES:
        errors.append("decision_statuses must be exactly draft and final")
    partitions = payload.get("decision_gate_partitions")
    if not isinstance(partitions, list) or tuple(partitions) != GATE_PARTITION_FIELDS:
        errors.append("decision_gate_partitions must match accepted/rejected/not_reviewed")
    fields = payload.get("required_decision_fields")
    if not isinstance(fields, list) or set(fields) != REQUIRED_DECISION_FIELDS:
        errors.append("required_decision_fields must match the decision schema")
    acknowledgements = payload.get("required_acknowledgements")
    if (
        not isinstance(acknowledgements, list)
        or set(acknowledgements) != REQUIRED_ACKNOWLEDGEMENTS
    ):
        errors.append("required_acknowledgements must match the acknowledgement schema")

    if (
        candidate_manifest is None
        or gate_ledger is None
        or evidence_matrix is None
        or dossier is None
        or run_bundle is None
    ):
        (
            manifest,
            ledger,
            matrix,
            loaded_dossier,
            loaded_run_bundle,
            link_errors,
        ) = _load_linked_payloads(payload)
        errors.extend(link_errors)
        if candidate_manifest is not None:
            manifest = candidate_manifest
        if gate_ledger is not None:
            ledger = gate_ledger
        if evidence_matrix is not None:
            matrix = evidence_matrix
        if dossier is not None:
            loaded_dossier = dossier
        if run_bundle is not None:
            loaded_run_bundle = run_bundle
    else:
        manifest = candidate_manifest
        ledger = gate_ledger
        matrix = evidence_matrix
        loaded_dossier = dossier
        loaded_run_bundle = run_bundle

    validators: tuple[Any, Any, Any, Any, Any] | None = None

    def linked_validators() -> tuple[Any, Any, Any, Any, Any]:
        nonlocal validators
        if validators is None:
            validators = _linked_validators()
        return validators

    gate_ids = _gate_ids(ledger) if ledger else set()
    outcome_ids = _review_outcome_ids(ledger) if ledger else set()

    if manifest:
        if manifest.get("review_decision_intake") != "metadata/n9_review_decision_intake.yaml":
            errors.append(
                "candidate manifest must reference metadata/n9_review_decision_intake.yaml"
            )
        validate_manifest, _, _, _, _ = linked_validators()
        errors.extend(
            f"candidate_manifest: {error}" for error in validate_manifest(manifest)
        )
    if ledger:
        _, validate_ledger, _, _, _ = linked_validators()
        errors.extend(f"review_gate_ledger: {error}" for error in validate_ledger(ledger))
    if matrix:
        _, _, validate_matrix, _, _ = linked_validators()
        errors.extend(
            f"review_evidence_matrix: {error}"
            for error in validate_matrix(
                matrix,
                candidate_manifest=manifest,
                gate_ledger=ledger,
            )
        )
    if loaded_dossier:
        _, _, _, validate_dossier, _ = linked_validators()
        errors.extend(
            f"review_dossier: {error}" for error in validate_dossier(loaded_dossier)
        )
    if loaded_run_bundle:
        _, _, _, _, validate_bundle = linked_validators()
        errors.extend(
            f"review_run_bundle: {error}" for error in validate_bundle(loaded_run_bundle)
        )

    errors.extend(_validate_outcome_rules(payload, gate_ids=gate_ids, outcome_ids=outcome_ids))
    errors.extend(_validate_template_shape(payload, gate_ids=gate_ids))
    return errors


def _string_list(value: Any, *, label: str) -> tuple[set[str], list[str]]:
    if not isinstance(value, list):
        return set(), [f"{label} must be a list"]
    errors = [f"{label} must contain only strings" for item in value if not isinstance(item, str)]
    return {item for item in value if isinstance(item, str)}, errors


def _validate_precise_gaps(value: Any, *, gate_ids: set[str]) -> list[str]:
    if not isinstance(value, list):
        return ["precise_gaps must be a list"]
    errors: list[str] = []
    for index, gap in enumerate(value):
        label = f"precise_gaps[{index}]"
        if not isinstance(gap, dict):
            errors.append(f"{label} must be a mapping")
            continue
        gate_id = gap.get("gate_id")
        if not isinstance(gate_id, str) or not gate_id.strip():
            errors.append(f"{label}.gate_id must be a nonempty string")
        elif gate_id not in gate_ids:
            errors.append(f"{label}.gate_id {gate_id!r} is not a known gate")
        summary = gap.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            errors.append(f"{label}.summary must be a nonempty string")
    return errors


def validate_decision_record(
    decision: dict[str, Any],
    intake: dict[str, Any],
    *,
    gate_ledger: dict[str, Any] | None = None,
) -> list[str]:
    if gate_ledger is None:
        _, gate_ledger, _, _, _, link_errors = _load_linked_payloads(intake)
        errors = list(link_errors)
    else:
        errors = []

    gate_ids = _gate_ids(gate_ledger)
    outcome_rules = _outcome_rules(intake)

    missing_fields = REQUIRED_DECISION_FIELDS - set(decision)
    for field in sorted(missing_fields):
        errors.append(f"decision missing {field!r}")
    if decision.get("schema") != intake.get("decision_record_schema"):
        errors.append("decision.schema must match decision_record_schema")

    decision_status = decision.get("decision_status")
    if decision_status not in DECISION_STATUSES:
        errors.append("decision_status must be draft or final")
    is_final = decision_status == "final"

    for field in ("reviewer_name", "reviewed_git_head", "run_bundle_digest"):
        value = decision.get(field)
        if is_final and (not isinstance(value, str) or not value.strip()):
            errors.append(f"{field} must be nonempty for final decisions")
    review_date = decision.get("review_date")
    if is_final:
        if not isinstance(review_date, str) or not review_date.strip():
            errors.append("review_date must be nonempty for final decisions")
        else:
            try:
                date.fromisoformat(review_date)
            except ValueError:
                errors.append("review_date must be YYYY-MM-DD")

    partitions: dict[str, set[str]] = {}
    for field in GATE_PARTITION_FIELDS:
        values, value_errors = _string_list(decision.get(field), label=field)
        errors.extend(value_errors)
        partitions[field] = values
        unknown = values - gate_ids
        for gate_id in sorted(unknown):
            errors.append(f"{field} contains unknown gate {gate_id!r}")

    overlaps: list[tuple[str, str, set[str]]] = [
        ("accepted_gates", "rejected_gates", partitions["accepted_gates"] & partitions["rejected_gates"]),
        ("accepted_gates", "not_reviewed_gates", partitions["accepted_gates"] & partitions["not_reviewed_gates"]),
        ("rejected_gates", "not_reviewed_gates", partitions["rejected_gates"] & partitions["not_reviewed_gates"]),
    ]
    for left, right, overlap in overlaps:
        for gate_id in sorted(overlap):
            errors.append(f"{gate_id!r} appears in both {left} and {right}")
    covered = set().union(*partitions.values())
    missing = gate_ids - covered
    extra = covered - gate_ids
    for gate_id in sorted(missing):
        errors.append(f"gate {gate_id!r} is not assigned to any decision partition")
    for gate_id in sorted(extra):
        errors.append(f"gate {gate_id!r} is outside the gate ledger")

    acknowledgements = decision.get("acknowledgements")
    if not isinstance(acknowledgements, dict):
        errors.append("acknowledgements must be a mapping")
    else:
        for key in sorted(REQUIRED_ACKNOWLEDGEMENTS):
            if acknowledgements.get(key) is not True:
                errors.append(f"acknowledgements.{key} must be true")

    precise_gaps = decision.get("precise_gaps")
    errors.extend(_validate_precise_gaps(precise_gaps, gate_ids=gate_ids))
    gap_gate_ids: set[str] = set()
    if isinstance(precise_gaps, list):
        gap_gate_ids = {
            gap["gate_id"]
            for gap in precise_gaps
            if isinstance(gap, dict) and isinstance(gap.get("gate_id"), str)
        }

    recommended = decision.get("recommended_outcome")
    if not isinstance(recommended, str) or recommended not in outcome_rules:
        errors.append(f"recommended_outcome {recommended!r} is not allowed")
    else:
        rule = outcome_rules[recommended]
        required = {
            gate for gate in rule.get("required_accepted_gates", []) if isinstance(gate, str)
        }
        blocking = {
            gate
            for gate in rule.get("blocks_if_rejected_or_unreviewed", [])
            if isinstance(gate, str)
        }
        for gate_id in sorted(required - partitions["accepted_gates"]):
            errors.append(
                f"recommended_outcome {recommended!r} requires accepted gate {gate_id!r}"
            )
        for gate_id in sorted(blocking & partitions["rejected_gates"]):
            errors.append(
                f"recommended_outcome {recommended!r} is blocked by rejected gate {gate_id!r}"
            )
        for gate_id in sorted(blocking & partitions["not_reviewed_gates"]):
            errors.append(
                f"recommended_outcome {recommended!r} is blocked by unreviewed gate {gate_id!r}"
            )
        for gate_id in sorted(blocking & gap_gate_ids):
            errors.append(
                f"recommended_outcome {recommended!r} is blocked by precise gap on {gate_id!r}"
            )
        if rule.get("requires_precise_gaps") is True and not precise_gaps:
            errors.append(f"recommended_outcome {recommended!r} requires precise_gaps")

    notes = decision.get("notes")
    if notes is not None and not isinstance(notes, str):
        errors.append("notes must be a string")
    return errors


def build_intake_payload(
    payload: dict[str, Any],
    *,
    gate_ledger: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if gate_ledger is None:
        _, ledger, _, _, _, _ = _load_linked_payloads(payload)
    else:
        ledger = gate_ledger
    rules = _outcome_rules(payload)
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "claim_scope": payload.get("claim_scope"),
        "canonical_command": payload.get("canonical_command"),
        "template_command": payload.get("template_command"),
        "markdown_command": payload.get("markdown_command"),
        "decision_record_schema": payload.get("decision_record_schema"),
        "gate_ids": sorted(_gate_ids(ledger)),
        "review_outcome_ids": sorted(_review_outcome_ids(ledger)),
        "outcome_rules": list(rules.values()),
        "decision_template": payload.get("decision_template", {}),
    }


def summary_payload(
    payload: dict[str, Any],
    errors: Sequence[str],
    *,
    decision_errors: Sequence[str] | None = None,
    decision_loaded: bool = False,
) -> dict[str, Any]:
    intake = build_intake_payload(payload)
    decision_errors = list(decision_errors or [])
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "gate_count": len(intake["gate_ids"]),
        "review_outcome_count": len(intake["review_outcome_ids"]),
        "outcome_rule_count": len(intake["outcome_rules"]),
        "decision_field_count": len(payload.get("required_decision_fields", []))
        if isinstance(payload.get("required_decision_fields"), list)
        else 0,
        "decision_loaded": decision_loaded,
        "decision_validation_status": "passed" if not decision_errors else "failed",
        "decision_validation_error_count": len(decision_errors),
        "first_decision_validation_errors": decision_errors[:5],
        "validation_status": "passed" if not errors and not decision_errors else "failed",
        "validation_error_count": len(errors),
        "first_validation_errors": list(errors[:5]),
        "claim_scope": payload.get("claim_scope"),
    }


def render_markdown(payload: dict[str, Any], errors: Sequence[str]) -> str:
    intake = build_intake_payload(payload)
    lines: list[str] = [
        "# n=9 Review Decision Intake",
        "",
        "Status: `REVIEW_DECISION_INTAKE_ONLY`.",
        "",
        str(payload.get("claim_scope", "")).strip(),
        "",
        "## Commands",
        "",
        f"- Static contract: `{payload.get('canonical_command')}`",
        f"- Decision template: `{payload.get('template_command')}`",
        f"- Markdown renderer: `{payload.get('markdown_command')}`",
        f"- Contract status: `{'passed' if not errors else 'failed'}`",
        "",
        "## Decision Gate Partitions",
        "",
        "A decision record must assign every gate to exactly one partition:",
        "",
    ]
    for field in GATE_PARTITION_FIELDS:
        lines.append(f"- `{field}`")
    lines.extend(["", "## Gates", ""])
    for gate_id in intake["gate_ids"]:
        lines.append(f"- `{gate_id}`")
    lines.extend(["", "## Allowed Outcomes", ""])
    for rule in intake["outcome_rules"]:
        required = ", ".join(rule.get("required_accepted_gates", [])) or "none"
        lines.append(f"- `{rule.get('id')}` requires `{required}`.")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "A passed decision record is intake validation only. It can support "
            "a separate source-of-truth proposal, but it does not itself prove "
            "`n=9`, prove Erdos Problem #97, claim a counterexample, or update "
            "the official/global status.",
            "",
        ]
    )
    return "\n".join(lines)


def dump_template(payload: dict[str, Any]) -> str:
    template = payload.get("decision_template", {})
    if yaml is None:
        return json.dumps(template, indent=2, sort_keys=True)
    return yaml.safe_dump(template, sort_keys=False)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intake", type=Path, default=DEFAULT_INTAKE)
    parser.add_argument(
        "--decision",
        type=Path,
        help="optional reviewer decision YAML file to validate",
    )
    parser.add_argument("--check", action="store_true", help="fail on validation errors")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print compact reviewer-facing JSON",
    )
    output_group.add_argument("--markdown", action="store_true", help="print Markdown")
    output_group.add_argument("--template", action="store_true", help="print YAML template")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    intake_path = args.intake
    if not intake_path.is_absolute():
        intake_path = REPO_ROOT / intake_path
    decision_errors: list[str] = []
    decision_loaded = False

    try:
        payload = load_intake(intake_path)
        errors = validate_intake(payload)
        if args.decision is not None:
            decision_path = args.decision
            if not decision_path.is_absolute():
                decision_path = REPO_ROOT / decision_path
            decision = load_decision(decision_path)
            decision_loaded = True
            decision_errors = validate_decision_record(decision, payload)
        else:
            decision = None
    except (OSError, ValueError, YAMLError) as exc:
        payload = {"schema": SCHEMA, "status": "LOAD_FAILED"}
        errors = [str(exc)]
        decision = None

    if args.template:
        print(dump_template(payload), end="")
    elif args.markdown:
        print(render_markdown(payload, errors))
    elif args.summary_json:
        print(
            json.dumps(
                summary_payload(
                    payload,
                    errors,
                    decision_errors=decision_errors,
                    decision_loaded=decision_loaded,
                ),
                indent=2,
                sort_keys=True,
            )
        )
    elif args.json:
        full_payload = build_intake_payload(payload)
        full_payload["decision_loaded"] = decision_loaded
        full_payload["decision"] = decision
        full_payload["decision_validation_errors"] = decision_errors
        full_payload["decision_validation_status"] = (
            "passed" if not decision_errors else "failed"
        )
        full_payload["validation_errors"] = errors
        full_payload["validation_status"] = (
            "passed" if not errors and not decision_errors else "failed"
        )
        print(json.dumps(full_payload, indent=2, sort_keys=True))
    else:
        print("n=9 review decision intake")
        print(f"status: {payload.get('status')}")
        print(f"decision_loaded: {decision_loaded}")
        print(
            "validation_status: "
            f"{'passed' if not errors and not decision_errors else 'failed'}"
        )

    if args.check and (errors or decision_errors):
        for error in [*errors, *decision_errors]:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
