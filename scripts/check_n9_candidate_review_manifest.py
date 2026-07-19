#!/usr/bin/env python3
"""Validate the n=9 candidate review manifest."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only without dev dependencies.
    yaml = None
    YAMLError = ValueError
else:
    YAMLError = yaml.YAMLError


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "metadata" / "n9_candidate_review.yaml"
SCHEMA = "erdos97.n9_candidate_review.v1"
TARGET = "verify-n9-candidate"
STATUS = "REVIEW_HARNESS_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
REVIEW_GATE_LEDGER = "metadata/n9_review_gate_ledger.yaml"
REVIEW_EVIDENCE_MATRIX = "metadata/n9_review_evidence_matrix.yaml"
REVIEW_DOSSIER = "metadata/n9_review_dossier.yaml"
REVIEW_RUN_BUNDLE = "metadata/n9_review_run_bundle.yaml"
REVIEW_DECISION_INTAKE = "metadata/n9_review_decision_intake.yaml"
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
SUMMARY_JSON_REVIEW_COMMAND_PREFIXES = (
    "python scripts/check_n9_review_gate_ledger.py",
    "python scripts/check_n9_review_evidence_matrix.py",
    "python scripts/check_n9_review_dossier.py",
    "python scripts/check_n9_review_run_bundle.py",
    "python scripts/check_n9_review_decision_intake.py",
    "python scripts/check_n9_vertex_circle_route_decision_preflight.py",
    "python scripts/check_n9_vertex_circle_route_decision_request.py",
    "python scripts/check_n9_vertex_circle_input_audit.py",
    "python scripts/check_n9_vertex_circle_incidence_filters.py",
    "python scripts/check_n9_vertex_circle_mro_branching_replay.py",
    "python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py",
    "python scripts/check_n9_vertex_circle_strict_edge_geometry.py",
    "python scripts/check_n9_vertex_circle_quotient_soundness.py",
    "python scripts/check_n9_vertex_circle_local_lemma_audit_path.py",
    "python scripts/check_turn_inequality_indexing.py",
    "python scripts/check_n9_turn_inequality_frontier.py",
    "python scripts/check_n9_kalmanson_selfedge_independent_replay.py",
    "python scripts/check_n9_kalmanson_selfedge_frontier_replay.py",
)


def repo_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def load_manifest(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise ValueError(
            "PyYAML is required to parse metadata/n9_candidate_review.yaml; "
            "install with `pip install -e .`"
        )
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("manifest top level must be a mapping")
    return payload


def make_target_commands(target: str = TARGET) -> list[str]:
    lines = (REPO_ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
    header = f"{target}:"
    try:
        start = lines.index(header) + 1
    except ValueError:
        return []

    commands: list[str] = []
    for line in lines[start:]:
        if line and not line.startswith("\t"):
            break
        if line.startswith("\t"):
            commands.append(line.strip().replace("$(PYTHON)", "python"))
    return commands


def flatten_route_commands(payload: dict[str, Any]) -> list[str]:
    commands: list[str] = []
    routes = payload.get("routes", [])
    if not isinstance(routes, list):
        return commands
    for route in routes:
        if not isinstance(route, dict):
            continue
        route_commands = route.get("commands", [])
        if not isinstance(route_commands, list):
            continue
        for command in route_commands:
            if isinstance(command, dict) and isinstance(command.get("command"), str):
                commands.append(command["command"])
    return commands


def _validate_path_list(payload: dict[str, Any], key: str) -> list[str]:
    errors: list[str] = []
    values = payload.get(key)
    if not isinstance(values, list) or not values:
        return [f"{key} must be a nonempty list"]
    seen: set[str] = set()
    for index, value in enumerate(values):
        label = f"{key}[{index}]"
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label} must be a nonempty string")
            continue
        if value in seen:
            errors.append(f"{label} duplicates {value!r}")
        seen.add(value)
        if not repo_path(value).exists():
            errors.append(f"{label} does not exist: {value}")
    return errors


def _validate_route_commands(routes: list[Any]) -> list[str]:
    errors: list[str] = []
    seen_route_ids: set[str] = set()
    seen_command_ids: set[str] = set()
    for route_index, route in enumerate(routes):
        route_label = f"routes[{route_index}]"
        if not isinstance(route, dict):
            errors.append(f"{route_label} must be a mapping")
            continue
        route_id = route.get("id")
        if not isinstance(route_id, str) or not route_id.strip():
            errors.append(f"{route_label}.id must be a nonempty string")
        elif route_id in seen_route_ids:
            errors.append(f"{route_label}.id {route_id!r} is duplicated")
        else:
            seen_route_ids.add(route_id)
        for key in ("title", "claim_scope"):
            value = route.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{route_label}.{key} must be a nonempty string")
        commands = route.get("commands")
        if not isinstance(commands, list) or not commands:
            errors.append(f"{route_label}.commands must be a nonempty list")
            continue
        for command_index, command in enumerate(commands):
            command_label = f"{route_label}.commands[{command_index}]"
            if not isinstance(command, dict):
                errors.append(f"{command_label} must be a mapping")
                continue
            command_id = command.get("id")
            command_text = command.get("command")
            if not isinstance(command_id, str) or not command_id.strip():
                errors.append(f"{command_label}.id must be a nonempty string")
            elif command_id in seen_command_ids:
                errors.append(f"{command_label}.id {command_id!r} is duplicated")
            else:
                seen_command_ids.add(command_id)
            if not isinstance(command_text, str) or not command_text.strip():
                errors.append(f"{command_label}.command must be a nonempty string")
                continue
            errors.extend(_validate_command_file(command_text, command_label))
            if command_text.startswith(SUMMARY_JSON_REVIEW_COMMAND_PREFIXES):
                if "--summary-json" not in command_text.split():
                    errors.append(f"{command_label}.command must use --summary-json")
    return errors


def _validate_command_file(command_text: str, label: str) -> list[str]:
    parts = command_text.split()
    if len(parts) < 2 or parts[0] != "python":
        return []
    script = parts[1]
    if script.startswith("scripts/") and not repo_path(script).exists():
        return [f"{label}.command references missing script: {script}"]
    return []


def _validate_review_gates(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    gates = payload.get("review_gates")
    if not isinstance(gates, list) or not gates:
        return ["review_gates must be a nonempty list"]
    seen: set[str] = set()
    for index, gate in enumerate(gates):
        label = f"review_gates[{index}]"
        if not isinstance(gate, dict):
            errors.append(f"{label} must be a mapping")
            continue
        gate_id = gate.get("id")
        if not isinstance(gate_id, str) or not gate_id.strip():
            errors.append(f"{label}.id must be a nonempty string")
        elif gate_id in seen:
            errors.append(f"{label}.id {gate_id!r} is duplicated")
        else:
            seen.add(gate_id)
        requirement = gate.get("review_requirement")
        if not isinstance(requirement, str) or not requirement.strip():
            errors.append(f"{label}.review_requirement must be a nonempty string")
        if gate.get("still_open") is not True:
            errors.append(f"{label}.still_open must be true")
    return errors


def validate_manifest(
    payload: dict[str, Any],
    *,
    makefile_commands: Sequence[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != SCHEMA:
        errors.append(f"schema is {payload.get('schema')!r}, expected {SCHEMA!r}")
    if payload.get("status") != STATUS:
        errors.append(f"status is {payload.get('status')!r}, expected {STATUS!r}")
    if payload.get("trust") != TRUST:
        errors.append(f"trust is {payload.get('trust')!r}, expected {TRUST!r}")
    if payload.get("target") != TARGET:
        errors.append(f"target is {payload.get('target')!r}, expected {TARGET!r}")
    if payload.get("canonical_command") != f"make {TARGET}":
        errors.append(f"canonical_command must be 'make {TARGET}'")
    review_gate_ledger = payload.get("review_gate_ledger")
    if review_gate_ledger != REVIEW_GATE_LEDGER:
        errors.append(f"review_gate_ledger must be {REVIEW_GATE_LEDGER!r}")
    elif not repo_path(REVIEW_GATE_LEDGER).exists():
        errors.append(f"review_gate_ledger does not exist: {REVIEW_GATE_LEDGER}")
    review_evidence_matrix = payload.get("review_evidence_matrix")
    if review_evidence_matrix != REVIEW_EVIDENCE_MATRIX:
        errors.append(f"review_evidence_matrix must be {REVIEW_EVIDENCE_MATRIX!r}")
    elif not repo_path(REVIEW_EVIDENCE_MATRIX).exists():
        errors.append(
            f"review_evidence_matrix does not exist: {REVIEW_EVIDENCE_MATRIX}"
        )
    review_dossier = payload.get("review_dossier")
    if review_dossier != REVIEW_DOSSIER:
        errors.append(f"review_dossier must be {REVIEW_DOSSIER!r}")
    elif not repo_path(REVIEW_DOSSIER).exists():
        errors.append(f"review_dossier does not exist: {REVIEW_DOSSIER}")
    review_run_bundle = payload.get("review_run_bundle")
    if review_run_bundle != REVIEW_RUN_BUNDLE:
        errors.append(f"review_run_bundle must be {REVIEW_RUN_BUNDLE!r}")
    elif not repo_path(REVIEW_RUN_BUNDLE).exists():
        errors.append(f"review_run_bundle does not exist: {REVIEW_RUN_BUNDLE}")
    review_decision_intake = payload.get("review_decision_intake")
    if review_decision_intake != REVIEW_DECISION_INTAKE:
        errors.append(f"review_decision_intake must be {REVIEW_DECISION_INTAKE!r}")
    elif not repo_path(REVIEW_DECISION_INTAKE).exists():
        errors.append(
            f"review_decision_intake does not exist: {REVIEW_DECISION_INTAKE}"
        )

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

    for key in (
        "source_of_truth_files",
        "harness_documents",
        "formalization_files",
    ):
        errors.extend(_validate_path_list(payload, key))

    routes = payload.get("routes")
    if not isinstance(routes, list) or not routes:
        errors.append("routes must be a nonempty list")
    else:
        errors.extend(_validate_route_commands(routes))

    errors.extend(_validate_review_gates(payload))

    manifest_commands = flatten_route_commands(payload)
    target_commands = list(makefile_commands) if makefile_commands is not None else make_target_commands()
    if not target_commands:
        errors.append(f"Makefile target {TARGET!r} has no commands")
    elif manifest_commands != target_commands:
        errors.append("manifest route commands do not match Makefile verify-n9-candidate commands")

    return errors


def summary_payload(payload: dict[str, Any], errors: Sequence[str]) -> dict[str, Any]:
    routes = payload.get("routes", [])
    route_ids = [route.get("id") for route in routes if isinstance(route, dict)]
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "target": payload.get("target"),
        "review_gate_ledger": payload.get("review_gate_ledger"),
        "review_evidence_matrix": payload.get("review_evidence_matrix"),
        "review_dossier": payload.get("review_dossier"),
        "review_run_bundle": payload.get("review_run_bundle"),
        "review_decision_intake": payload.get("review_decision_intake"),
        "route_count": len(routes) if isinstance(routes, list) else 0,
        "route_ids": route_ids,
        "command_count": len(flatten_route_commands(payload)),
        "review_gate_count": (
            len(payload.get("review_gates", []))
            if isinstance(payload.get("review_gates"), list)
            else 0
        ),
        "validation_status": "passed" if not errors else "failed",
        "validation_error_count": len(errors),
        "first_validation_errors": list(errors[:5]),
        "claim_scope": payload.get("claim_scope"),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--check", action="store_true", help="fail when validation fails")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON payload")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print compact reviewer-facing JSON",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = args.manifest
    if not manifest.is_absolute():
        manifest = REPO_ROOT / manifest
    try:
        payload = load_manifest(manifest)
        errors = validate_manifest(payload)
    except (OSError, ValueError, YAMLError) as exc:
        payload = {"schema": SCHEMA, "status": "LOAD_FAILED", "target": TARGET}
        errors = [str(exc)]

    if args.summary_json:
        print(json.dumps(summary_payload(payload, errors), indent=2, sort_keys=True))
    elif args.json:
        full_payload = dict(payload)
        full_payload["validation_errors"] = errors
        full_payload["validation_status"] = "passed" if not errors else "failed"
        print(json.dumps(full_payload, indent=2, sort_keys=True))
    else:
        print("n=9 candidate review manifest")
        print(f"target: {payload.get('target')}")
        print(f"routes: {len(payload.get('routes', [])) if isinstance(payload.get('routes'), list) else 0}")
        print(f"commands: {len(flatten_route_commands(payload))}")
        print(f"validation_status: {'passed' if not errors else 'failed'}")

    if errors and args.check:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
