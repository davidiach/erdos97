#!/usr/bin/env python3
"""Validate and optionally capture an n=9 reviewer run bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
import time
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

DEFAULT_BUNDLE = REPO_ROOT / "metadata" / "n9_review_run_bundle.yaml"
SCHEMA = "erdos97.n9_review_run_bundle.v1"
STATUS = "REVIEW_RUN_BUNDLE_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CANDIDATE_MANIFEST = "metadata/n9_candidate_review.yaml"
REVIEW_GATE_LEDGER = "metadata/n9_review_gate_ledger.yaml"
REVIEW_EVIDENCE_MATRIX = "metadata/n9_review_evidence_matrix.yaml"
REVIEW_DOSSIER = "metadata/n9_review_dossier.yaml"
CANONICAL_COMMAND = (
    "python scripts/check_n9_review_run_bundle.py --check --summary-json"
)
LIVE_REPLAY_COMMAND = (
    "python scripts/check_n9_review_run_bundle.py --check --run --summary-json"
)
MARKDOWN_COMMAND = "python scripts/check_n9_review_run_bundle.py --markdown"
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
REQUIRED_CAPTURE_FIELDS = {
    "id",
    "route_id",
    "command_id",
    "command",
    "returncode",
    "duration_seconds",
    "stdout_sha256",
    "stderr_sha256",
    "stdout_preview",
    "stderr_preview",
    "output_format",
    "validation_status",
    "error_count",
    "first_errors",
}
REQUIRED_SUMMARY_FIELDS = {
    "schema",
    "status",
    "trust",
    "route_count",
    "command_count",
    "evidence_record_count",
    "run_capture_enabled",
    "run_record_count",
    "failed_run_record_count",
    "run_record_digest",
    "validation_status",
    "validation_error_count",
}
REQUIRED_OUTPUT_MODES = {"summary-json", "json", "markdown"}
REQUIRED_ROUTE_IDS = {
    "manifest_contract",
    "lean_guardrails",
    "vertex_circle_route",
    "turn_packing_route",
    "kalmanson_corroboration",
    "kalmanson_primary_route",
}


def _linked_validators() -> tuple[Any, Any, Any, Any]:
    from scripts.check_n9_candidate_review_manifest import validate_manifest
    from scripts.check_n9_review_dossier import validate_dossier
    from scripts.check_n9_review_evidence_matrix import validate_matrix
    from scripts.check_n9_review_gate_ledger import validate_ledger

    return validate_manifest, validate_ledger, validate_matrix, validate_dossier


def _expectation_helpers() -> tuple[Any, Any]:
    from scripts.check_n9_review_evidence_matrix import (
        _check_json_expectations,
        _check_text_expectations,
    )

    return _check_json_expectations, _check_text_expectations


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


def load_bundle(path: Path = DEFAULT_BUNDLE) -> dict[str, Any]:
    return load_yaml_mapping(path, label="metadata/n9_review_run_bundle.yaml")


def _load_linked_payloads(
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], list[str]]:
    errors: list[str] = []
    linked: list[tuple[str, str]] = [
        ("candidate_manifest", CANDIDATE_MANIFEST),
        ("review_gate_ledger", REVIEW_GATE_LEDGER),
        ("review_evidence_matrix", REVIEW_EVIDENCE_MATRIX),
        ("review_dossier", REVIEW_DOSSIER),
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
        errors,
    )


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


def _manifest_command_records(manifest: dict[str, Any]) -> list[dict[str, str]]:
    command_records: list[dict[str, str]] = []
    routes = manifest.get("routes", [])
    if not isinstance(routes, list):
        return command_records
    for route in routes:
        if not isinstance(route, dict):
            continue
        route_id = route.get("id")
        route_title = route.get("title", route_id)
        if not isinstance(route_id, str):
            continue
        commands = route.get("commands", [])
        if not isinstance(commands, list):
            continue
        for command in commands:
            if not isinstance(command, dict):
                continue
            command_id = command.get("id")
            command_text = command.get("command")
            if isinstance(command_id, str) and isinstance(command_text, str):
                command_records.append(
                    {
                        "id": command_id,
                        "route_id": route_id,
                        "route_title": str(route_title),
                        "command_id": command_id,
                        "command": command_text,
                    }
                )
    return command_records


def _evidence_records_by_command(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records = matrix.get("evidence_records", [])
    if not isinstance(records, list):
        return {}
    return {
        record["command_id"]: record
        for record in records
        if isinstance(record, dict) and isinstance(record.get("command_id"), str)
    }


def _route_ids(manifest: dict[str, Any]) -> set[str]:
    routes = manifest.get("routes", [])
    if not isinstance(routes, list):
        return set()
    return {
        route["id"]
        for route in routes
        if isinstance(route, dict) and isinstance(route.get("id"), str)
    }


def _validate_capture_contract(payload: dict[str, Any]) -> list[str]:
    contract = payload.get("capture_contract")
    if not isinstance(contract, dict):
        return ["capture_contract must be a mapping"]

    errors: list[str] = []
    expected_true = {
        "executes_manifest_commands",
        "validates_evidence_matrix_expectations",
        "records_stdout_sha256",
        "records_stderr_sha256",
        "records_duration_seconds",
    }
    for key in sorted(expected_true):
        if contract.get(key) is not True:
            errors.append(f"capture_contract.{key} must be true")
    if contract.get("writes_generated_artifacts") is not False:
        errors.append("capture_contract.writes_generated_artifacts must be false")

    preview_chars = contract.get("output_preview_chars")
    if not isinstance(preview_chars, int) or not 80 <= preview_chars <= 1000:
        errors.append("capture_contract.output_preview_chars must be an int in [80, 1000]")

    record_fields = contract.get("required_record_fields")
    if not isinstance(record_fields, list) or not record_fields:
        errors.append("capture_contract.required_record_fields must be a nonempty list")
    else:
        missing = REQUIRED_CAPTURE_FIELDS - set(record_fields)
        for field in sorted(missing):
            errors.append(f"capture_contract.required_record_fields missing {field!r}")

    summary_fields = contract.get("required_summary_fields")
    if not isinstance(summary_fields, list) or not summary_fields:
        errors.append("capture_contract.required_summary_fields must be a nonempty list")
    else:
        missing = REQUIRED_SUMMARY_FIELDS - set(summary_fields)
        for field in sorted(missing):
            errors.append(f"capture_contract.required_summary_fields missing {field!r}")
    return errors


def validate_bundle(
    payload: dict[str, Any],
    *,
    candidate_manifest: dict[str, Any] | None = None,
    gate_ledger: dict[str, Any] | None = None,
    evidence_matrix: dict[str, Any] | None = None,
    dossier: dict[str, Any] | None = None,
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
    if payload.get("live_replay_command") != LIVE_REPLAY_COMMAND:
        errors.append(f"live_replay_command must be {LIVE_REPLAY_COMMAND!r}")
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
    errors.extend(_validate_capture_contract(payload))

    output_modes = payload.get("output_modes")
    if not isinstance(output_modes, list) or set(output_modes) != REQUIRED_OUTPUT_MODES:
        errors.append(
            "output_modes must be exactly "
            f"{', '.join(sorted(REQUIRED_OUTPUT_MODES))}"
        )

    if (
        candidate_manifest is None
        or gate_ledger is None
        or evidence_matrix is None
        or dossier is None
    ):
        manifest, ledger, matrix, loaded_dossier, link_errors = _load_linked_payloads(
            payload
        )
        errors.extend(link_errors)
        if candidate_manifest is not None:
            manifest = candidate_manifest
        if gate_ledger is not None:
            ledger = gate_ledger
        if evidence_matrix is not None:
            matrix = evidence_matrix
        if dossier is not None:
            loaded_dossier = dossier
    else:
        manifest = candidate_manifest
        ledger = gate_ledger
        matrix = evidence_matrix
        loaded_dossier = dossier

    validators: tuple[Any, Any, Any, Any] | None = None

    def linked_validators() -> tuple[Any, Any, Any, Any]:
        nonlocal validators
        if validators is None:
            validators = _linked_validators()
        return validators

    if manifest:
        if manifest.get("review_run_bundle") != "metadata/n9_review_run_bundle.yaml":
            errors.append(
                "candidate manifest must reference metadata/n9_review_run_bundle.yaml"
            )
        validate_manifest, _, _, _ = linked_validators()
        errors.extend(
            f"candidate_manifest: {error}" for error in validate_manifest(manifest)
        )

        expected_route_ids = payload.get("expected_route_ids")
        if not isinstance(expected_route_ids, list):
            errors.append("expected_route_ids must be a list")
        else:
            expected_route_id_set = {
                route_id for route_id in expected_route_ids if isinstance(route_id, str)
            }
            if expected_route_id_set != REQUIRED_ROUTE_IDS:
                errors.append("expected_route_ids does not match required route set")
            observed_route_ids = _route_ids(manifest)
            missing = expected_route_id_set - observed_route_ids
            extra = observed_route_ids - expected_route_id_set
            for route_id in sorted(missing):
                errors.append(f"expected_route_ids missing manifest route {route_id!r}")
            for route_id in sorted(extra):
                errors.append(f"manifest route {route_id!r} is not expected")

    if ledger:
        _, validate_ledger, _, _ = linked_validators()
        errors.extend(f"review_gate_ledger: {error}" for error in validate_ledger(ledger))
    if matrix:
        _, _, validate_matrix, _ = linked_validators()
        errors.extend(
            f"review_evidence_matrix: {error}"
            for error in validate_matrix(
                matrix,
                candidate_manifest=manifest,
                gate_ledger=ledger,
            )
        )
    if loaded_dossier:
        _, _, _, validate_dossier = linked_validators()
        errors.extend(
            f"review_dossier: {error}" for error in validate_dossier(loaded_dossier)
        )

    if manifest and matrix:
        command_ids = {record["command_id"] for record in _manifest_command_records(manifest)}
        matrix_command_ids = set(_evidence_records_by_command(matrix))
        if command_ids != matrix_command_ids:
            errors.append("manifest commands and evidence-matrix commands differ")
    return errors


def _subprocess_args(command: str) -> list[str]:
    parts = shlex.split(command)
    if parts and parts[0] == "python":
        parts[0] = sys.executable
    return parts


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _preview(text: str, limit: int) -> str:
    return text[:limit]


def _preview_limit(payload: dict[str, Any]) -> int:
    contract = payload.get("capture_contract", {})
    if isinstance(contract, dict) and isinstance(contract.get("output_preview_chars"), int):
        return int(contract["output_preview_chars"])
    return 240


def git_head() -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def git_tracked_dirty_count() -> int | None:
    completed = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return len([line for line in completed.stdout.splitlines() if line.strip()])


def run_manifest_commands(
    payload: dict[str, Any],
    *,
    candidate_manifest: dict[str, Any],
    evidence_matrix: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    evidence_by_command = _evidence_records_by_command(evidence_matrix)
    check_json_expectations, check_text_expectations = _expectation_helpers()
    run_records: list[dict[str, Any]] = []
    errors: list[str] = []
    preview_limit = _preview_limit(payload)

    for command_record in _manifest_command_records(candidate_manifest):
        command_id = command_record["command_id"]
        evidence_record = evidence_by_command.get(command_id)
        label = f"command {command_id!r}"
        start = time.perf_counter()
        completed = subprocess.run(
            _subprocess_args(command_record["command"]),
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        duration_seconds = time.perf_counter() - start
        stdout = completed.stdout
        stderr = completed.stderr
        record_errors: list[str] = []
        output_format = (
            evidence_record.get("output_format")
            if isinstance(evidence_record, dict)
            else None
        )

        if evidence_record is None:
            record_errors.append(f"{label} has no evidence-matrix record")
        if completed.returncode != 0:
            record_errors.append(
                f"{label} exited with {completed.returncode}: "
                f"{command_record['command']}"
            )
        elif output_format == "json":
            try:
                output_payload = json.loads(stdout)
            except json.JSONDecodeError as exc:
                record_errors.append(f"{label} output is not JSON: {exc}")
            else:
                expectations = evidence_record.get("expectations", [])
                if isinstance(expectations, list):
                    record_errors.extend(
                        check_json_expectations(
                            output_payload,
                            expectations,
                            label=command_id,
                        )
                    )
        elif output_format == "text":
            text_expectations = evidence_record.get("text_expectations", [])
            if isinstance(text_expectations, list):
                record_errors.extend(
                    check_text_expectations(
                        stdout,
                        text_expectations,
                        label=command_id,
                    )
                )
        elif output_format is not None:
            record_errors.append(f"{label} has unsupported output format {output_format!r}")

        if record_errors:
            errors.extend(record_errors)
        run_records.append(
            {
                "id": command_record["id"],
                "route_id": command_record["route_id"],
                "command_id": command_id,
                "command": command_record["command"],
                "returncode": completed.returncode,
                "duration_seconds": round(duration_seconds, 6),
                "stdout_sha256": _sha256_text(stdout),
                "stderr_sha256": _sha256_text(stderr),
                "stdout_preview": _preview(stdout.strip(), preview_limit),
                "stderr_preview": _preview(stderr.strip(), preview_limit),
                "output_format": output_format,
                "validation_status": "passed" if not record_errors else "failed",
                "error_count": len(record_errors),
                "first_errors": record_errors[:3],
            }
        )
    return run_records, errors


def _run_records_digest(run_records: Sequence[dict[str, Any]]) -> str | None:
    if not run_records:
        return None
    stable_records = []
    stable_keys = (
        "id",
        "route_id",
        "command_id",
        "returncode",
        "stdout_sha256",
        "stderr_sha256",
        "validation_status",
        "error_count",
        "first_errors",
    )
    for record in run_records:
        stable_records.append({key: record.get(key) for key in stable_keys})
    encoded = json.dumps(stable_records, sort_keys=True, separators=(",", ":"))
    return _sha256_text(encoded)


def build_bundle_payload(
    payload: dict[str, Any],
    *,
    candidate_manifest: dict[str, Any] | None = None,
    gate_ledger: dict[str, Any] | None = None,
    evidence_matrix: dict[str, Any] | None = None,
    dossier: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if (
        candidate_manifest is None
        or gate_ledger is None
        or evidence_matrix is None
        or dossier is None
    ):
        manifest, ledger, matrix, loaded_dossier, _ = _load_linked_payloads(payload)
        if candidate_manifest is not None:
            manifest = candidate_manifest
        if gate_ledger is not None:
            ledger = gate_ledger
        if evidence_matrix is not None:
            matrix = evidence_matrix
        if dossier is not None:
            loaded_dossier = dossier
    else:
        manifest = candidate_manifest
        ledger = gate_ledger
        matrix = evidence_matrix
        loaded_dossier = dossier

    command_records = _manifest_command_records(manifest)
    evidence_records = matrix.get("evidence_records", [])
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "claim_scope": payload.get("claim_scope"),
        "canonical_command": payload.get("canonical_command"),
        "live_replay_command": payload.get("live_replay_command"),
        "markdown_command": payload.get("markdown_command"),
        "candidate_manifest": payload.get("candidate_manifest"),
        "review_gate_ledger": payload.get("review_gate_ledger"),
        "review_evidence_matrix": payload.get("review_evidence_matrix"),
        "review_dossier": payload.get("review_dossier"),
        "candidate_claim_under_review": manifest.get("candidate_claim_under_review"),
        "routes": manifest.get("routes", []),
        "command_records": command_records,
        "review_gates": ledger.get("review_gates", []),
        "infrastructure_gates": ledger.get("infrastructure_gates", []),
        "evidence_records": evidence_records if isinstance(evidence_records, list) else [],
        "dossier_sections": loaded_dossier.get("sections", []),
        "capture_contract": payload.get("capture_contract", {}),
    }


def summary_payload(
    payload: dict[str, Any],
    errors: Sequence[str],
    *,
    run_capture_enabled: bool,
    run_records: Sequence[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    bundle = build_bundle_payload(payload)
    run_records = list(run_records or [])
    failed_records = [
        record for record in run_records if record.get("validation_status") != "passed"
    ]
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "route_count": len(bundle.get("routes", [])),
        "command_count": len(bundle.get("command_records", [])),
        "evidence_record_count": len(bundle.get("evidence_records", [])),
        "review_gate_count": len(bundle.get("review_gates", [])),
        "infrastructure_gate_count": len(bundle.get("infrastructure_gates", [])),
        "run_capture_enabled": run_capture_enabled,
        "run_record_count": len(run_records),
        "failed_run_record_count": len(failed_records),
        "failed_run_record_ids": [record.get("id") for record in failed_records[:10]],
        "run_record_digest": _run_records_digest(run_records),
        "git_head": git_head(),
        "git_tracked_dirty_count": git_tracked_dirty_count(),
        "validation_status": "passed" if not errors else "failed",
        "validation_error_count": len(errors),
        "first_validation_errors": list(errors[:5]),
        "claim_scope": payload.get("claim_scope"),
    }


def render_markdown(
    payload: dict[str, Any],
    errors: Sequence[str],
    *,
    run_records: Sequence[dict[str, Any]] | None = None,
) -> str:
    bundle = build_bundle_payload(payload)
    run_records = list(run_records or [])
    lines: list[str] = [
        "# n=9 Review Run Bundle",
        "",
        "Status: `REVIEW_RUN_BUNDLE_ONLY`.",
        "",
        str(payload.get("claim_scope", "")).strip(),
        "",
        "## Commands",
        "",
        f"- Static contract: `{payload.get('canonical_command')}`",
        f"- Live capture: `{payload.get('live_replay_command')}`",
        f"- Markdown renderer: `{payload.get('markdown_command')}`",
        f"- Contract status: `{'passed' if not errors else 'failed'}`",
        "",
        "## Linked Contracts",
        "",
        f"- Candidate manifest: `{payload.get('candidate_manifest')}`",
        f"- Review gate ledger: `{payload.get('review_gate_ledger')}`",
        f"- Evidence matrix: `{payload.get('review_evidence_matrix')}`",
        f"- Reviewer dossier: `{payload.get('review_dossier')}`",
        "",
        "## Run Capture Contract",
        "",
        "- Executes every compact manifest command in order.",
        "- Validates compact outputs against the evidence matrix.",
        "- Captures return codes, durations, stdout/stderr SHA-256 digests, and previews.",
        "- Writes no generated artifact.",
        "",
        "## Manifest Command Surface",
        "",
    ]

    for route in bundle["routes"]:
        if not isinstance(route, dict):
            continue
        lines.append(f"### {route.get('title', route.get('id'))}")
        lines.append("")
        for command in route.get("commands", []):
            if isinstance(command, dict):
                lines.append(f"- `{command.get('id')}`: `{command.get('command')}`")
        lines.append("")

    if run_records:
        lines.extend(["## Captured Run Records", ""])
        for record in run_records:
            lines.append(
                f"- `{record.get('id')}`: `{record.get('validation_status')}`; "
                f"stdout `{str(record.get('stdout_sha256', ''))[:12]}`; "
                f"stderr `{str(record.get('stderr_sha256', ''))[:12]}`"
            )
        lines.append("")
        lines.append(f"Run digest: `{_run_records_digest(run_records)}`")
        lines.append("")

    lines.extend(["## Boundary", ""])
    lines.append(
        "A passed live capture is execution provenance and drift detection. "
        "It does not accept any review gate, prove `n=9`, prove Erdos Problem "
        "#97, claim a counterexample, or update the official/global status."
    )
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--check", action="store_true", help="fail on validation errors")
    parser.add_argument(
        "--run",
        action="store_true",
        help="execute the compact manifest command chain and capture digests",
    )
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
    bundle_path = args.bundle
    if not bundle_path.is_absolute():
        bundle_path = REPO_ROOT / bundle_path

    run_records: list[dict[str, Any]] = []
    try:
        payload = load_bundle(bundle_path)
        errors = validate_bundle(payload)
        if args.run and not errors:
            manifest, _, matrix, _, link_errors = _load_linked_payloads(payload)
            errors.extend(link_errors)
            if not errors:
                run_records, run_errors = run_manifest_commands(
                    payload,
                    candidate_manifest=manifest,
                    evidence_matrix=matrix,
                )
                errors.extend(run_errors)
    except (OSError, ValueError, YAMLError) as exc:
        payload = {"schema": SCHEMA, "status": "LOAD_FAILED"}
        errors = [str(exc)]

    if args.markdown:
        print(render_markdown(payload, errors, run_records=run_records))
    elif args.summary_json:
        print(
            json.dumps(
                summary_payload(
                    payload,
                    errors,
                    run_capture_enabled=args.run,
                    run_records=run_records,
                ),
                indent=2,
                sort_keys=True,
            )
        )
    elif args.json:
        full_payload = build_bundle_payload(payload)
        full_payload["run_capture_enabled"] = args.run
        full_payload["run_records"] = run_records
        full_payload["run_record_digest"] = _run_records_digest(run_records)
        full_payload["git_head"] = git_head()
        full_payload["git_tracked_dirty_count"] = git_tracked_dirty_count()
        full_payload["validation_errors"] = errors
        full_payload["validation_status"] = "passed" if not errors else "failed"
        print(json.dumps(full_payload, indent=2, sort_keys=True))
    else:
        print("n=9 review run bundle")
        print(f"status: {payload.get('status')}")
        print(f"run_capture_enabled: {args.run}")
        print(f"validation_status: {'passed' if not errors else 'failed'}")

    if errors and args.check:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
