#!/usr/bin/env python3
"""Validate and optionally replay the n=9 review evidence matrix."""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
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
DEFAULT_MATRIX = REPO_ROOT / "metadata" / "n9_review_evidence_matrix.yaml"
SCHEMA = "erdos97.n9_review_evidence_matrix.v1"
STATUS = "REVIEW_EVIDENCE_MATRIX_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CANONICAL_COMMAND = (
    "python scripts/check_n9_review_evidence_matrix.py --check --summary-json"
)
LIVE_REPLAY_COMMAND = (
    "python scripts/check_n9_review_evidence_matrix.py --check --run --summary-json"
)
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
SUPPORTED_OUTPUT_FORMATS = {"json", "text"}


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


def load_matrix(path: Path = DEFAULT_MATRIX) -> dict[str, Any]:
    return load_yaml_mapping(path, label="metadata/n9_review_evidence_matrix.yaml")


def _candidate_manifest_commands(manifest: dict[str, Any]) -> dict[str, dict[str, str]]:
    commands: dict[str, dict[str, str]] = {}
    routes = manifest.get("routes", [])
    if not isinstance(routes, list):
        return commands
    for route in routes:
        if not isinstance(route, dict):
            continue
        route_id = route.get("id")
        if not isinstance(route_id, str):
            continue
        route_commands = route.get("commands", [])
        if not isinstance(route_commands, list):
            continue
        for command in route_commands:
            if not isinstance(command, dict):
                continue
            command_id = command.get("id")
            command_text = command.get("command")
            if isinstance(command_id, str) and isinstance(command_text, str):
                commands[command_id] = {
                    "route_id": route_id,
                    "command": command_text,
                }
    return commands


def _ledger_gate_ids(ledger: dict[str, Any]) -> set[str]:
    gate_ids: set[str] = set()
    for key in ("review_gates", "infrastructure_gates"):
        gates = ledger.get(key, [])
        if not isinstance(gates, list):
            continue
        for gate in gates:
            if isinstance(gate, dict) and isinstance(gate.get("id"), str):
                gate_ids.add(gate["id"])
    return gate_ids


def _ledger_evidence_commands(ledger: dict[str, Any]) -> set[str]:
    command_ids: set[str] = set()
    for key in ("review_gates", "infrastructure_gates"):
        gates = ledger.get(key, [])
        if not isinstance(gates, list):
            continue
        for gate in gates:
            if not isinstance(gate, dict):
                continue
            commands = gate.get("evidence_commands", [])
            if not isinstance(commands, list):
                continue
            for command_id in commands:
                if isinstance(command_id, str):
                    command_ids.add(command_id)
    return command_ids


def _load_linked_manifests(
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    errors: list[str] = []
    manifest_path = payload.get("candidate_manifest")
    ledger_path = payload.get("review_gate_ledger")
    manifest: dict[str, Any] = {}
    ledger: dict[str, Any] = {}

    if not isinstance(manifest_path, str) or not manifest_path.strip():
        errors.append("candidate_manifest must be a nonempty string")
    else:
        try:
            manifest = load_yaml_mapping(repo_path(manifest_path), label=manifest_path)
        except (OSError, ValueError, YAMLError) as exc:
            errors.append(str(exc))

    if not isinstance(ledger_path, str) or not ledger_path.strip():
        errors.append("review_gate_ledger must be a nonempty string")
    else:
        try:
            ledger = load_yaml_mapping(repo_path(ledger_path), label=ledger_path)
        except (OSError, ValueError, YAMLError) as exc:
            errors.append(str(exc))

    return manifest, ledger, errors


def _validate_forbidden_promotions(payload: dict[str, Any]) -> list[str]:
    forbidden = payload.get("forbidden_promotions")
    if not isinstance(forbidden, list) or not forbidden:
        return ["forbidden_promotions must be a nonempty list"]
    missing = REQUIRED_FORBIDDEN_PROMOTIONS - set(forbidden)
    return [
        f"forbidden_promotions missing {phrase!r}"
        for phrase in sorted(missing)
    ]


def _validate_expectation_shape(record: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    output_format = record.get("output_format")
    expectations = record.get("expectations", [])
    text_expectations = record.get("text_expectations", [])

    if output_format == "json":
        if not isinstance(expectations, list) or not expectations:
            errors.append(f"{label}.expectations must be a nonempty list")
        for index, expectation in enumerate(expectations):
            expectation_label = f"{label}.expectations[{index}]"
            if not isinstance(expectation, dict):
                errors.append(f"{expectation_label} must be a mapping")
                continue
            if not isinstance(expectation.get("path"), str) or not expectation["path"]:
                errors.append(f"{expectation_label}.path must be a nonempty string")
            if "equals" not in expectation and "contains" not in expectation:
                errors.append(
                    f"{expectation_label} must define equals or contains"
                )
        if text_expectations:
            errors.append(f"{label}.text_expectations is only valid for text output")
    elif output_format == "text":
        if not isinstance(text_expectations, list) or not text_expectations:
            errors.append(f"{label}.text_expectations must be a nonempty list")
        for index, expectation in enumerate(text_expectations):
            expectation_label = f"{label}.text_expectations[{index}]"
            if not isinstance(expectation, dict):
                errors.append(f"{expectation_label} must be a mapping")
                continue
            has_contains = isinstance(expectation.get("contains"), str)
            contains_any = expectation.get("contains_any")
            has_contains_any = (
                isinstance(contains_any, list)
                and all(isinstance(item, str) for item in contains_any)
                and bool(contains_any)
            )
            if not has_contains and not has_contains_any:
                errors.append(
                    f"{expectation_label} must define contains or contains_any"
                )
        if expectations:
            errors.append(f"{label}.expectations is only valid for JSON output")
    return errors


def validate_matrix(
    payload: dict[str, Any],
    *,
    candidate_manifest: dict[str, Any] | None = None,
    gate_ledger: dict[str, Any] | None = None,
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

    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str) or not claim_scope.strip():
        errors.append("claim_scope must be a nonempty string")
    else:
        for phrase in REQUIRED_CLAIM_SCOPE_PHRASES:
            if phrase not in claim_scope:
                errors.append(f"claim_scope must include {phrase!r}")
    errors.extend(_validate_forbidden_promotions(payload))

    manifest: dict[str, Any]
    ledger: dict[str, Any]
    if candidate_manifest is None or gate_ledger is None:
        manifest, ledger, link_errors = _load_linked_manifests(payload)
        errors.extend(link_errors)
        if candidate_manifest is not None:
            manifest = candidate_manifest
        if gate_ledger is not None:
            ledger = gate_ledger
    else:
        manifest = candidate_manifest
        ledger = gate_ledger

    if manifest:
        if manifest.get("review_evidence_matrix") != "metadata/n9_review_evidence_matrix.yaml":
            errors.append(
                "candidate manifest must reference metadata/n9_review_evidence_matrix.yaml"
            )
        manifest_commands = _candidate_manifest_commands(manifest)
    else:
        manifest_commands = {}

    if ledger:
        gate_ids = _ledger_gate_ids(ledger)
        ledger_evidence_commands = _ledger_evidence_commands(ledger)
    else:
        gate_ids = set()
        ledger_evidence_commands = set()

    records = payload.get("evidence_records")
    if not isinstance(records, list) or not records:
        return errors + ["evidence_records must be a nonempty list"]

    seen_record_ids: set[str] = set()
    record_command_ids: set[str] = set()
    command_to_gates: dict[str, set[str]] = {}
    for index, record in enumerate(records):
        label = f"evidence_records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be a mapping")
            continue

        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id.strip():
            errors.append(f"{label}.id must be a nonempty string")
        elif record_id in seen_record_ids:
            errors.append(f"{label}.id {record_id!r} is duplicated")
        else:
            seen_record_ids.add(record_id)

        command_id = record.get("command_id")
        if not isinstance(command_id, str) or not command_id.strip():
            errors.append(f"{label}.command_id must be a nonempty string")
            continue
        if command_id in record_command_ids:
            errors.append(f"{label}.command_id {command_id!r} is duplicated")
        record_command_ids.add(command_id)

        manifest_command = manifest_commands.get(command_id)
        if manifest_commands and manifest_command is None:
            errors.append(f"{label}.command_id {command_id!r} is not in manifest")
        else:
            route_id = record.get("route_id")
            if not isinstance(route_id, str) or not route_id.strip():
                errors.append(f"{label}.route_id must be a nonempty string")
            elif manifest_command and route_id != manifest_command["route_id"]:
                errors.append(
                    f"{label}.route_id {route_id!r} does not match manifest "
                    f"route {manifest_command['route_id']!r}"
                )

        output_format = record.get("output_format")
        if output_format not in SUPPORTED_OUTPUT_FORMATS:
            errors.append(f"{label}.output_format {output_format!r} is not supported")

        ledger_gate_ids = record.get("ledger_gate_ids")
        if not isinstance(ledger_gate_ids, list):
            errors.append(f"{label}.ledger_gate_ids must be a list")
            ledger_gate_id_set: set[str] = set()
        else:
            ledger_gate_id_set = {
                gate_id for gate_id in ledger_gate_ids if isinstance(gate_id, str)
            }
            if len(ledger_gate_id_set) != len(ledger_gate_ids):
                errors.append(f"{label}.ledger_gate_ids must contain only strings")
            for gate_id in ledger_gate_id_set:
                if gate_ids and gate_id not in gate_ids:
                    errors.append(f"{label}.ledger_gate_ids unknown gate {gate_id!r}")
        command_to_gates.setdefault(command_id, set()).update(ledger_gate_id_set)

        errors.extend(_validate_expectation_shape(record, label))

    missing_manifest_commands = set(manifest_commands) - record_command_ids
    extra_record_commands = record_command_ids - set(manifest_commands)
    for command_id in sorted(missing_manifest_commands):
        errors.append(f"manifest command {command_id!r} is not covered by matrix")
    for command_id in sorted(extra_record_commands):
        errors.append(f"matrix command {command_id!r} is not present in manifest")

    missing_ledger_commands = ledger_evidence_commands - record_command_ids
    for command_id in sorted(missing_ledger_commands):
        errors.append(f"ledger evidence command {command_id!r} is not covered")
    for command_id in sorted(ledger_evidence_commands & record_command_ids):
        if not command_to_gates.get(command_id):
            errors.append(
                f"ledger evidence command {command_id!r} has no matrix gate link"
            )

    return errors


def _extract_path(payload: Any, path: str) -> tuple[bool, Any]:
    current = payload
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False, None
    return True, current


def _check_json_expectations(
    payload: dict[str, Any],
    expectations: Sequence[dict[str, Any]],
    *,
    label: str,
) -> list[str]:
    errors: list[str] = []
    for index, expectation in enumerate(expectations):
        expectation_label = f"{label}.expectations[{index}]"
        path = expectation.get("path")
        if not isinstance(path, str):
            errors.append(f"{expectation_label}.path must be a string")
            continue
        found, actual = _extract_path(payload, path)
        if not found:
            errors.append(f"{expectation_label} missing output path {path!r}")
            continue
        if "equals" in expectation and actual != expectation["equals"]:
            errors.append(
                f"{expectation_label} expected {path!r} == "
                f"{expectation['equals']!r}, got {actual!r}"
            )
        if "contains" in expectation:
            needle = expectation["contains"]
            if isinstance(actual, str):
                ok = isinstance(needle, str) and needle in actual
            elif isinstance(actual, list):
                ok = needle in actual
            else:
                ok = False
            if not ok:
                errors.append(
                    f"{expectation_label} expected {path!r} to contain {needle!r}"
                )
    return errors


def _check_text_expectations(
    text: str,
    expectations: Sequence[dict[str, Any]],
    *,
    label: str,
) -> list[str]:
    errors: list[str] = []
    for index, expectation in enumerate(expectations):
        expectation_label = f"{label}.text_expectations[{index}]"
        if "contains" in expectation:
            needle = expectation["contains"]
            if not isinstance(needle, str) or needle not in text:
                errors.append(
                    f"{expectation_label} expected output to contain {needle!r}"
                )
        if "contains_any" in expectation:
            needles = expectation["contains_any"]
            if not isinstance(needles, list) or not any(
                isinstance(needle, str) and needle in text for needle in needles
            ):
                errors.append(
                    f"{expectation_label} expected output to contain one of "
                    f"{needles!r}"
                )
    return errors


def _command_for_record(record: dict[str, Any], manifest_commands: dict[str, dict[str, str]]) -> str:
    command_id = record["command_id"]
    return manifest_commands[command_id]["command"]


def _subprocess_args(command: str) -> list[str]:
    parts = shlex.split(command)
    if parts and parts[0] == "python":
        parts[0] = sys.executable
    return parts


def run_evidence_records(
    payload: dict[str, Any],
    *,
    candidate_manifest: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    if candidate_manifest is None:
        manifest_path = payload.get("candidate_manifest")
        if not isinstance(manifest_path, str):
            return [], ["candidate_manifest must be a nonempty string"]
        candidate_manifest = load_yaml_mapping(repo_path(manifest_path), label=manifest_path)

    manifest_commands = _candidate_manifest_commands(candidate_manifest)
    records = payload.get("evidence_records", [])
    if not isinstance(records, list):
        return [], ["evidence_records must be a list before live replay"]

    run_records: list[dict[str, Any]] = []
    errors: list[str] = []
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("command_id"), str):
            continue
        record_id = record.get("id", record.get("command_id"))
        label = f"evidence_record {record_id!r}"
        command_id = record["command_id"]
        if command_id not in manifest_commands:
            errors.append(f"{label} references missing manifest command")
            continue
        command = _command_for_record(record, manifest_commands)
        completed = subprocess.run(
            _subprocess_args(command),
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        record_errors: list[str] = []
        if completed.returncode != 0:
            record_errors.append(
                f"{label} command exited with {completed.returncode}: {command}"
            )
        output_format = record.get("output_format")
        if output_format == "json" and completed.returncode == 0:
            try:
                output_payload = json.loads(stdout)
            except json.JSONDecodeError as exc:
                record_errors.append(f"{label} output is not JSON: {exc}")
            else:
                expectations = record.get("expectations", [])
                if isinstance(expectations, list):
                    record_errors.extend(
                        _check_json_expectations(
                            output_payload,
                            expectations,
                            label=str(record_id),
                        )
                    )
        elif output_format == "text" and completed.returncode == 0:
            text_expectations = record.get("text_expectations", [])
            if isinstance(text_expectations, list):
                record_errors.extend(
                    _check_text_expectations(
                        stdout,
                        text_expectations,
                        label=str(record_id),
                    )
                )
        if record_errors:
            errors.extend(record_errors)
        run_records.append(
            {
                "id": record_id,
                "command_id": command_id,
                "returncode": completed.returncode,
                "validation_status": "passed" if not record_errors else "failed",
                "error_count": len(record_errors),
                "first_errors": record_errors[:3],
                "stdout_preview": stdout[:240],
                "stderr_preview": stderr[:240],
            }
        )
    return run_records, errors


def summary_payload(
    payload: dict[str, Any],
    errors: Sequence[str],
    *,
    live_replay_enabled: bool,
    run_records: Sequence[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    records = payload.get("evidence_records", [])
    run_records = list(run_records or [])
    failed_run_records = [
        record for record in run_records if record.get("validation_status") != "passed"
    ]
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "candidate_manifest": payload.get("candidate_manifest"),
        "review_gate_ledger": payload.get("review_gate_ledger"),
        "evidence_record_count": len(records) if isinstance(records, list) else 0,
        "evidence_record_ids": [
            record.get("id") for record in records if isinstance(record, dict)
        ],
        "live_replay_enabled": live_replay_enabled,
        "live_replay_record_count": len(run_records),
        "failed_live_replay_count": len(failed_run_records),
        "failed_live_replay_ids": [
            record.get("id") for record in failed_run_records[:10]
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_error_count": len(errors),
        "first_validation_errors": list(errors[:5]),
        "claim_scope": payload.get("claim_scope"),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--check", action="store_true", help="fail on validation errors")
    parser.add_argument(
        "--run",
        action="store_true",
        help="execute the matrix command chain and validate live outputs",
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print compact reviewer-facing JSON",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    matrix = args.matrix
    if not matrix.is_absolute():
        matrix = REPO_ROOT / matrix

    run_records: list[dict[str, Any]] = []
    try:
        payload = load_matrix(matrix)
        errors = validate_matrix(payload)
        if args.run and not errors:
            run_records, run_errors = run_evidence_records(payload)
            errors.extend(run_errors)
    except (OSError, ValueError, YAMLError) as exc:
        payload = {"schema": SCHEMA, "status": "LOAD_FAILED"}
        errors = [str(exc)]

    if args.summary_json:
        print(
            json.dumps(
                summary_payload(
                    payload,
                    errors,
                    live_replay_enabled=args.run,
                    run_records=run_records,
                ),
                indent=2,
                sort_keys=True,
            )
        )
    elif args.json:
        full_payload = dict(payload)
        full_payload["live_replay_enabled"] = args.run
        full_payload["live_replay_records"] = run_records
        full_payload["validation_errors"] = errors
        full_payload["validation_status"] = "passed" if not errors else "failed"
        print(json.dumps(full_payload, indent=2, sort_keys=True))
    else:
        print("n=9 review evidence matrix")
        print(f"candidate_manifest: {payload.get('candidate_manifest')}")
        print(
            "evidence_records: "
            f"{len(payload.get('evidence_records', [])) if isinstance(payload.get('evidence_records'), list) else 0}"
        )
        print(f"live_replay_enabled: {args.run}")
        print(f"validation_status: {'passed' if not errors else 'failed'}")

    if errors and args.check:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
