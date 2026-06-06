#!/usr/bin/env python3
"""Validate and render the n=9 reviewer dossier contract."""
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

DEFAULT_DOSSIER = REPO_ROOT / "metadata" / "n9_review_dossier.yaml"
SCHEMA = "erdos97.n9_review_dossier.v1"
STATUS = "REVIEW_DOSSIER_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CANONICAL_COMMAND = "python scripts/check_n9_review_dossier.py --check --summary-json"
MARKDOWN_COMMAND = "python scripts/check_n9_review_dossier.py --markdown"
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
    "reviewer_name",
    "review_date",
    "accepted_gates",
    "rejected_gates",
    "precise_gaps",
    "recommended_outcome",
    "notes",
}


def _linked_validators() -> tuple[Any, Any, Any]:
    from scripts.check_n9_candidate_review_manifest import validate_manifest
    from scripts.check_n9_review_evidence_matrix import validate_matrix
    from scripts.check_n9_review_gate_ledger import validate_ledger

    return validate_manifest, validate_matrix, validate_ledger


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


def load_dossier(path: Path = DEFAULT_DOSSIER) -> dict[str, Any]:
    return load_yaml_mapping(path, label="metadata/n9_review_dossier.yaml")


def _load_linked_payloads(
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[str]]:
    errors: list[str] = []
    linked: list[tuple[str, str]] = [
        ("candidate_manifest", "metadata/n9_candidate_review.yaml"),
        ("review_gate_ledger", "metadata/n9_review_gate_ledger.yaml"),
        ("review_evidence_matrix", "metadata/n9_review_evidence_matrix.yaml"),
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
        errors,
    )


def _ids_from_path(payload: dict[str, Any], source: str) -> set[str]:
    parts = source.split(".")
    current: Any = payload
    for part in parts[1:]:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return set()
    if not isinstance(current, list):
        return set()
    return {item["id"] for item in current if isinstance(item, dict) and "id" in item}


def _payload_for_source(
    source: str,
    *,
    manifest: dict[str, Any],
    ledger: dict[str, Any],
    matrix: dict[str, Any],
) -> dict[str, Any]:
    if source.startswith("candidate_manifest."):
        return manifest
    if source.startswith("review_gate_ledger."):
        return ledger
    if source.startswith("review_evidence_matrix."):
        return matrix
    return {}


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


def _validate_sections(
    payload: dict[str, Any],
    *,
    manifest: dict[str, Any],
    ledger: dict[str, Any],
    matrix: dict[str, Any],
) -> list[str]:
    sections = payload.get("sections")
    if not isinstance(sections, list) or not sections:
        return ["sections must be a nonempty list"]

    errors: list[str] = []
    seen: set[str] = set()
    for index, section in enumerate(sections):
        label = f"sections[{index}]"
        if not isinstance(section, dict):
            errors.append(f"{label} must be a mapping")
            continue
        section_id = section.get("id")
        if not isinstance(section_id, str) or not section_id.strip():
            errors.append(f"{label}.id must be a nonempty string")
        elif section_id in seen:
            errors.append(f"{label}.id {section_id!r} is duplicated")
        else:
            seen.add(section_id)
        title = section.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{label}.title must be a nonempty string")
        source = section.get("source")
        if not isinstance(source, str) or "." not in source:
            errors.append(f"{label}.source must be a dotted source path")
            continue
        source_payload = _payload_for_source(
            source,
            manifest=manifest,
            ledger=ledger,
            matrix=matrix,
        )
        if not source_payload:
            errors.append(f"{label}.source {source!r} is not recognized")
            continue

        required_ids = section.get("required_ids", [])
        if required_ids:
            if not isinstance(required_ids, list):
                errors.append(f"{label}.required_ids must be a list")
            else:
                observed = _ids_from_path(source_payload, source)
                missing = set(required_ids) - observed
                for missing_id in sorted(missing):
                    errors.append(
                        f"{label}.required_ids missing {missing_id!r} from {source}"
                    )

        required_phrases = section.get("required_phrases", [])
        if required_phrases:
            if not isinstance(required_phrases, list):
                errors.append(f"{label}.required_phrases must be a list")
            else:
                current: Any = source_payload
                for part in source.split(".")[1:]:
                    current = current.get(part) if isinstance(current, dict) else None
                if not isinstance(current, str):
                    errors.append(f"{label}.source must resolve to text")
                else:
                    for phrase in required_phrases:
                        if phrase not in current:
                            errors.append(
                                f"{label}.required_phrases missing {phrase!r}"
                            )
    return errors


def _validate_review_questions(
    payload: dict[str, Any],
    *,
    ledger: dict[str, Any],
) -> list[str]:
    questions = payload.get("review_questions")
    if not isinstance(questions, list) or not questions:
        return ["review_questions must be a nonempty list"]
    gate_ids = _ids_from_path(ledger, "review_gate_ledger.review_gates")
    errors: list[str] = []
    seen: set[str] = set()
    for index, question in enumerate(questions):
        label = f"review_questions[{index}]"
        if not isinstance(question, dict):
            errors.append(f"{label} must be a mapping")
            continue
        gate_id = question.get("gate_id")
        if not isinstance(gate_id, str) or not gate_id.strip():
            errors.append(f"{label}.gate_id must be a nonempty string")
        elif gate_id in seen:
            errors.append(f"{label}.gate_id {gate_id!r} is duplicated")
        else:
            seen.add(gate_id)
        if gate_id not in gate_ids:
            errors.append(f"{label}.gate_id {gate_id!r} is not a review gate")
        prompt = question.get("worksheet_prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{label}.worksheet_prompt must be a nonempty string")

    missing = gate_ids - seen
    for gate_id in sorted(missing):
        errors.append(f"review_questions missing gate {gate_id!r}")
    return errors


def validate_dossier(
    payload: dict[str, Any],
    *,
    candidate_manifest: dict[str, Any] | None = None,
    gate_ledger: dict[str, Any] | None = None,
    evidence_matrix: dict[str, Any] | None = None,
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

    if (
        candidate_manifest is None
        or gate_ledger is None
        or evidence_matrix is None
    ):
        manifest, ledger, matrix, link_errors = _load_linked_payloads(payload)
        errors.extend(link_errors)
        if candidate_manifest is not None:
            manifest = candidate_manifest
        if gate_ledger is not None:
            ledger = gate_ledger
        if evidence_matrix is not None:
            matrix = evidence_matrix
    else:
        manifest = candidate_manifest
        ledger = gate_ledger
        matrix = evidence_matrix

    validators: tuple[Any, Any, Any] | None = None

    def linked_validators() -> tuple[Any, Any, Any]:
        nonlocal validators
        if validators is None:
            validators = _linked_validators()
        return validators

    if manifest:
        if manifest.get("review_dossier") != "metadata/n9_review_dossier.yaml":
            errors.append(
                "candidate manifest must reference metadata/n9_review_dossier.yaml"
            )
        validate_manifest, _, _ = linked_validators()
        errors.extend(
            f"candidate_manifest: {error}" for error in validate_manifest(manifest)
        )
    if ledger:
        _, _, validate_ledger = linked_validators()
        errors.extend(f"review_gate_ledger: {error}" for error in validate_ledger(ledger))
    if matrix:
        _, validate_matrix, _ = linked_validators()
        errors.extend(
            f"review_evidence_matrix: {error}"
            for error in validate_matrix(
                matrix,
                candidate_manifest=manifest,
                gate_ledger=ledger,
            )
        )

    errors.extend(
        _validate_sections(
            payload,
            manifest=manifest,
            ledger=ledger,
            matrix=matrix,
        )
    )
    errors.extend(_validate_review_questions(payload, ledger=ledger))

    decision_fields = payload.get("decision_fields")
    if not isinstance(decision_fields, list) or not decision_fields:
        errors.append("decision_fields must be a nonempty list")
    else:
        missing = REQUIRED_DECISION_FIELDS - set(decision_fields)
        for field in sorted(missing):
            errors.append(f"decision_fields missing {field!r}")
    return errors


def _records_by_id(items: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    return {
        item["id"]: item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def build_dossier_payload(
    payload: dict[str, Any],
    *,
    candidate_manifest: dict[str, Any] | None = None,
    gate_ledger: dict[str, Any] | None = None,
    evidence_matrix: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if (
        candidate_manifest is None
        or gate_ledger is None
        or evidence_matrix is None
    ):
        manifest, ledger, matrix, _ = _load_linked_payloads(payload)
        if candidate_manifest is not None:
            manifest = candidate_manifest
        if gate_ledger is not None:
            ledger = gate_ledger
        if evidence_matrix is not None:
            matrix = evidence_matrix
    else:
        manifest = candidate_manifest
        ledger = gate_ledger
        matrix = evidence_matrix

    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "claim_scope": payload.get("claim_scope"),
        "canonical_command": payload.get("canonical_command"),
        "markdown_command": payload.get("markdown_command"),
        "candidate_claim_under_review": manifest.get("candidate_claim_under_review"),
        "routes": manifest.get("routes", []),
        "review_gates": ledger.get("review_gates", []),
        "infrastructure_gates": ledger.get("infrastructure_gates", []),
        "review_outcomes": ledger.get("review_outcomes", []),
        "evidence_records": matrix.get("evidence_records", []),
        "review_questions": payload.get("review_questions", []),
        "decision_fields": payload.get("decision_fields", []),
    }


def render_markdown(
    payload: dict[str, Any],
    errors: Sequence[str],
) -> str:
    dossier = build_dossier_payload(payload)
    evidence_by_id = _records_by_id(dossier["evidence_records"])
    question_by_gate = {
        question["gate_id"]: question
        for question in dossier["review_questions"]
        if isinstance(question, dict) and isinstance(question.get("gate_id"), str)
    }
    lines: list[str] = [
        "# n=9 Reviewer Dossier",
        "",
        "Status: `REVIEW_DOSSIER_ONLY`.",
        "",
        dossier.get("claim_scope", "").strip(),
        "",
        "## Validation",
        "",
        f"- Dossier checker: `{payload.get('canonical_command')}`",
        f"- Markdown renderer: `{payload.get('markdown_command')}`",
        f"- Contract status: `{'passed' if not errors else 'failed'}`",
        "",
        "## Candidate Claim Under Review",
        "",
        dossier.get("candidate_claim_under_review", "").strip(),
        "",
        "## Compact Command Surface",
        "",
    ]

    for route in dossier["routes"]:
        if not isinstance(route, dict):
            continue
        lines.append(f"### {route.get('title', route.get('id'))}")
        lines.append("")
        lines.append(str(route.get("claim_scope", "")).strip())
        lines.append("")
        for command in route.get("commands", []):
            if not isinstance(command, dict):
                continue
            lines.append(f"- `{command.get('command')}`")
        lines.append("")

    lines.extend(["## Review Gate Worksheet", ""])
    for gate in dossier["review_gates"]:
        if not isinstance(gate, dict):
            continue
        gate_id = gate.get("id")
        lines.append(f"### {gate.get('title', gate_id)}")
        lines.append("")
        lines.append(f"- Gate ID: `{gate_id}`")
        lines.append(f"- Status: `{gate.get('status')}`")
        lines.append(f"- Still open: `{gate.get('still_open')}`")
        lines.append(f"- Reduction steps: `{', '.join(gate.get('reduction_steps', []))}`")
        prompt = question_by_gate.get(gate_id, {}).get("worksheet_prompt", "")
        if prompt:
            lines.append(f"- Review prompt: {str(prompt).strip()}")
        evidence_ids = gate.get("evidence_commands", [])
        if evidence_ids:
            lines.append("- Evidence records:")
            for evidence_id in evidence_ids:
                record = evidence_by_id.get(evidence_id, {})
                lines.append(
                    f"  - `{evidence_id}`: `{record.get('output_format', 'unknown')}`"
                )
        blockers = gate.get("blockers", [])
        if blockers:
            lines.append("- Open blockers:")
            for blocker in blockers:
                lines.append(f"  - {blocker}")
        lines.append("")

    lines.extend(["## Infrastructure Gates", ""])
    for gate in dossier["infrastructure_gates"]:
        if not isinstance(gate, dict):
            continue
        lines.append(f"- `{gate.get('id')}`: {str(gate.get('requirement', '')).strip()}")
    lines.append("")

    lines.extend(["## Acceptance Outcomes", ""])
    for outcome in dossier["review_outcomes"]:
        if not isinstance(outcome, dict):
            continue
        required = ", ".join(outcome.get("required_gates", [])) or "none"
        lines.append(f"- `{outcome.get('id')}` requires `{required}`.")
        lines.append(f"  {str(outcome.get('claim_boundary', '')).strip()}")
    lines.append("")

    lines.extend(["## Reviewer Decision Fields", ""])
    for field in dossier["decision_fields"]:
        lines.append(f"- `{field}`:")
    lines.append("")
    return "\n".join(lines)


def summary_payload(payload: dict[str, Any], errors: Sequence[str]) -> dict[str, Any]:
    dossier = build_dossier_payload(payload)
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "section_count": len(payload.get("sections", []))
        if isinstance(payload.get("sections"), list)
        else 0,
        "review_gate_count": len(dossier.get("review_gates", [])),
        "infrastructure_gate_count": len(dossier.get("infrastructure_gates", [])),
        "evidence_record_count": len(dossier.get("evidence_records", [])),
        "review_question_count": len(payload.get("review_questions", []))
        if isinstance(payload.get("review_questions"), list)
        else 0,
        "decision_field_count": len(payload.get("decision_fields", []))
        if isinstance(payload.get("decision_fields"), list)
        else 0,
        "validation_status": "passed" if not errors else "failed",
        "validation_error_count": len(errors),
        "first_validation_errors": list(errors[:5]),
        "claim_scope": payload.get("claim_scope"),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dossier", type=Path, default=DEFAULT_DOSSIER)
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
    dossier_path = args.dossier
    if not dossier_path.is_absolute():
        dossier_path = REPO_ROOT / dossier_path
    try:
        payload = load_dossier(dossier_path)
        errors = validate_dossier(payload)
    except (OSError, ValueError, YAMLError) as exc:
        payload = {"schema": SCHEMA, "status": "LOAD_FAILED"}
        errors = [str(exc)]

    if args.markdown:
        print(render_markdown(payload, errors))
    elif args.summary_json:
        print(json.dumps(summary_payload(payload, errors), indent=2, sort_keys=True))
    elif args.json:
        full_payload = build_dossier_payload(payload)
        full_payload["validation_errors"] = errors
        full_payload["validation_status"] = "passed" if not errors else "failed"
        print(json.dumps(full_payload, indent=2, sort_keys=True))
    else:
        print("n=9 reviewer dossier")
        print(f"status: {payload.get('status')}")
        print(f"validation_status: {'passed' if not errors else 'failed'}")

    if errors and args.check:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
