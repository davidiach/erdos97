#!/usr/bin/env python3
"""Validate the n=9 independent-review gate ledger."""
from __future__ import annotations

import argparse
import json
import re
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
DEFAULT_LEDGER = REPO_ROOT / "metadata" / "n9_review_gate_ledger.yaml"
SCHEMA = "erdos97.n9_review_gate_ledger.v1"
STATUS = "REVIEW_GATE_LEDGER_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CANONICAL_COMMAND = (
    "python scripts/check_n9_review_gate_ledger.py --check --summary-json"
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
REQUIRED_REVIEW_GATES = {
    "frontier_enumeration",
    "vertex_circle_geometry",
    "quotient_obstruction_replay",
    "turn_geometry",
    "turn_arithmetic_replay",
    "kalmanson_corroboration",
}
REQUIRED_INFRASTRUCTURE_GATES = {
    "lean_compilation",
    "independent_review",
}
REQUIRED_OUTCOMES = {
    "accepted_vertex_circle_route": {
        "frontier_enumeration",
        "vertex_circle_geometry",
        "quotient_obstruction_replay",
    },
    "accepted_turn_route": {
        "frontier_enumeration",
        "turn_geometry",
        "turn_arithmetic_replay",
    },
    "accepted_corrob_only": {"kalmanson_corroboration"},
    "gap_found": set(),
}
ALLOWED_ROUTES = {
    "shared_source_frontier",
    "vertex_circle",
    "turn_packing",
    "corroboration",
}
ALLOWED_STATUSES = {
    "machine_checked_review_pending",
    "proof_facing_review_pending",
}


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


def load_ledger(path: Path = DEFAULT_LEDGER) -> dict[str, Any]:
    return load_yaml_mapping(path, label="metadata/n9_review_gate_ledger.yaml")


def _validate_path_list(payload: dict[str, Any], key: str) -> list[str]:
    values = payload.get(key)
    if not isinstance(values, list) or not values:
        return [f"{key} must be a nonempty list"]

    errors: list[str] = []
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


def _candidate_manifest_command_ids(manifest: dict[str, Any]) -> set[str]:
    command_ids: set[str] = set()
    routes = manifest.get("routes", [])
    if not isinstance(routes, list):
        return command_ids
    for route in routes:
        if not isinstance(route, dict):
            continue
        commands = route.get("commands", [])
        if not isinstance(commands, list):
            continue
        for command in commands:
            if isinstance(command, dict) and isinstance(command.get("id"), str):
                command_ids.add(command["id"])
    return command_ids


def _candidate_manifest_review_gate_ids(manifest: dict[str, Any]) -> set[str]:
    gate_ids: set[str] = set()
    gates = manifest.get("review_gates", [])
    if not isinstance(gates, list):
        return gate_ids
    for gate in gates:
        if isinstance(gate, dict) and isinstance(gate.get("id"), str):
            gate_ids.add(gate["id"])
    return gate_ids


def _reduction_chain_step_ids() -> set[str]:
    text = (REPO_ROOT / "docs" / "n9-reduction-chain.md").read_text(
        encoding="utf-8"
    )
    step_ids: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"\| (A\d+|B\d+|C\d+) \|", line)
        if match:
            step_ids.add(match.group(1))
    return step_ids


def _review_packet_outcome_ids() -> set[str]:
    text = (REPO_ROOT / "docs" / "n9-review-packet.md").read_text(
        encoding="utf-8"
    )
    outcome_ids: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"- `([^`]+)`:", line)
        if match:
            outcome_ids.add(match.group(1))
    return outcome_ids


def _string_list(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list):
        return []
    strings: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            strings.append(item)
    if allow_empty or strings:
        return strings
    return []


def _validate_forbidden_promotions(payload: dict[str, Any]) -> list[str]:
    forbidden = payload.get("forbidden_promotions")
    if not isinstance(forbidden, list) or not forbidden:
        return ["forbidden_promotions must be a nonempty list"]
    missing = REQUIRED_FORBIDDEN_PROMOTIONS - set(forbidden)
    return [
        f"forbidden_promotions missing {phrase!r}"
        for phrase in sorted(missing)
    ]


def _validate_review_gates(
    payload: dict[str, Any],
    *,
    manifest_command_ids: set[str],
    manifest_review_gate_ids: set[str],
    reduction_step_ids: set[str],
) -> tuple[list[str], set[str], set[str]]:
    errors: list[str] = []
    gate_ids: set[str] = set()
    manifest_gate_refs: set[str] = set()
    gates = payload.get("review_gates")
    if not isinstance(gates, list) or not gates:
        return ["review_gates must be a nonempty list"], gate_ids, manifest_gate_refs

    for index, gate in enumerate(gates):
        label = f"review_gates[{index}]"
        if not isinstance(gate, dict):
            errors.append(f"{label} must be a mapping")
            continue

        gate_id = gate.get("id")
        if not isinstance(gate_id, str) or not gate_id.strip():
            errors.append(f"{label}.id must be a nonempty string")
        elif gate_id in gate_ids:
            errors.append(f"{label}.id {gate_id!r} is duplicated")
        else:
            gate_ids.add(gate_id)

        for key in ("title", "review_question"):
            value = gate.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}.{key} must be a nonempty string")

        route = gate.get("route")
        if route not in ALLOWED_ROUTES:
            errors.append(f"{label}.route {route!r} is not recognized")

        status = gate.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{label}.status {status!r} is not recognized")

        if gate.get("still_open") is not True:
            errors.append(f"{label}.still_open must be true")

        manifest_gate = gate.get("manifest_gate")
        if not isinstance(manifest_gate, str) or not manifest_gate.strip():
            errors.append(f"{label}.manifest_gate must be a nonempty string")
        elif manifest_gate not in manifest_review_gate_ids:
            errors.append(
                f"{label}.manifest_gate {manifest_gate!r} is not in "
                "metadata/n9_candidate_review.yaml"
            )
        else:
            manifest_gate_refs.add(manifest_gate)

        steps = _string_list(gate.get("reduction_steps"), f"{label}.reduction_steps")
        if not steps:
            errors.append(f"{label}.reduction_steps must be a nonempty list")
        for step in steps:
            if step not in reduction_step_ids:
                errors.append(f"{label}.reduction_steps references missing {step!r}")

        commands = _string_list(gate.get("evidence_commands"), f"{label}.commands")
        if not commands:
            errors.append(f"{label}.evidence_commands must be a nonempty list")
        for command_id in commands:
            if command_id not in manifest_command_ids:
                errors.append(
                    f"{label}.evidence_commands references unknown command "
                    f"{command_id!r}"
                )

        docs = _string_list(gate.get("referenced_docs"), f"{label}.referenced_docs")
        if not docs:
            errors.append(f"{label}.referenced_docs must be a nonempty list")
        for doc in docs:
            if not repo_path(doc).exists():
                errors.append(f"{label}.referenced_docs missing {doc}")

        blockers = _string_list(gate.get("blockers"), f"{label}.blockers")
        if not blockers:
            errors.append(f"{label}.blockers must be a nonempty list")

    missing_gates = REQUIRED_REVIEW_GATES - gate_ids
    extra_gates = gate_ids - REQUIRED_REVIEW_GATES
    for gate_id in sorted(missing_gates):
        errors.append(f"review_gates missing required gate {gate_id!r}")
    for gate_id in sorted(extra_gates):
        errors.append(f"review_gates contains unknown gate {gate_id!r}")

    return errors, gate_ids, manifest_gate_refs


def _validate_infrastructure_gates(
    payload: dict[str, Any],
    *,
    manifest_command_ids: set[str],
    manifest_review_gate_ids: set[str],
) -> tuple[list[str], set[str], set[str]]:
    errors: list[str] = []
    gate_ids: set[str] = set()
    manifest_gate_refs: set[str] = set()
    gates = payload.get("infrastructure_gates")
    if not isinstance(gates, list) or not gates:
        return ["infrastructure_gates must be a nonempty list"], gate_ids, manifest_gate_refs

    for index, gate in enumerate(gates):
        label = f"infrastructure_gates[{index}]"
        if not isinstance(gate, dict):
            errors.append(f"{label} must be a mapping")
            continue
        gate_id = gate.get("id")
        if not isinstance(gate_id, str) or not gate_id.strip():
            errors.append(f"{label}.id must be a nonempty string")
        elif gate_id in gate_ids:
            errors.append(f"{label}.id {gate_id!r} is duplicated")
        else:
            gate_ids.add(gate_id)

        for key in ("title", "requirement"):
            value = gate.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}.{key} must be a nonempty string")

        if gate.get("still_open") is not True:
            errors.append(f"{label}.still_open must be true")

        manifest_gate = gate.get("manifest_gate")
        if not isinstance(manifest_gate, str) or not manifest_gate.strip():
            errors.append(f"{label}.manifest_gate must be a nonempty string")
        elif manifest_gate not in manifest_review_gate_ids:
            errors.append(
                f"{label}.manifest_gate {manifest_gate!r} is not in "
                "metadata/n9_candidate_review.yaml"
            )
        else:
            manifest_gate_refs.add(manifest_gate)

        docs = _string_list(gate.get("referenced_docs"), f"{label}.referenced_docs")
        if not docs:
            errors.append(f"{label}.referenced_docs must be a nonempty list")
        for doc in docs:
            if not repo_path(doc).exists():
                errors.append(f"{label}.referenced_docs missing {doc}")

        commands = _string_list(
            gate.get("evidence_commands"),
            f"{label}.evidence_commands",
            allow_empty=True,
        )
        for command_id in commands:
            if command_id not in manifest_command_ids:
                errors.append(
                    f"{label}.evidence_commands references unknown command "
                    f"{command_id!r}"
                )

    missing_gates = REQUIRED_INFRASTRUCTURE_GATES - gate_ids
    extra_gates = gate_ids - REQUIRED_INFRASTRUCTURE_GATES
    for gate_id in sorted(missing_gates):
        errors.append(f"infrastructure_gates missing required gate {gate_id!r}")
    for gate_id in sorted(extra_gates):
        errors.append(f"infrastructure_gates contains unknown gate {gate_id!r}")

    return errors, gate_ids, manifest_gate_refs


def _validate_outcomes(
    payload: dict[str, Any],
    *,
    gate_ids: set[str],
    documented_outcome_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    outcomes = payload.get("review_outcomes")
    if not isinstance(outcomes, list) or not outcomes:
        return ["review_outcomes must be a nonempty list"]

    seen: set[str] = set()
    for index, outcome in enumerate(outcomes):
        label = f"review_outcomes[{index}]"
        if not isinstance(outcome, dict):
            errors.append(f"{label} must be a mapping")
            continue
        outcome_id = outcome.get("id")
        if not isinstance(outcome_id, str) or not outcome_id.strip():
            errors.append(f"{label}.id must be a nonempty string")
            continue
        if outcome_id in seen:
            errors.append(f"{label}.id {outcome_id!r} is duplicated")
        seen.add(outcome_id)

        for key in ("title", "claim_boundary"):
            value = outcome.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}.{key} must be a nonempty string")

        required = set(
            _string_list(
                outcome.get("required_gates"),
                f"{label}.required_gates",
                allow_empty=True,
            )
        )
        if outcome_id in REQUIRED_OUTCOMES:
            expected = REQUIRED_OUTCOMES[outcome_id]
            if required != expected:
                errors.append(
                    f"{label}.required_gates for {outcome_id!r} must be "
                    f"{sorted(expected)!r}"
                )
        for gate_id in required:
            if gate_id not in gate_ids:
                errors.append(
                    f"{label}.required_gates references unknown gate {gate_id!r}"
                )
        if outcome_id not in documented_outcome_ids:
            errors.append(
                f"{label}.id {outcome_id!r} is not documented in "
                "docs/n9-review-packet.md"
            )

    missing = set(REQUIRED_OUTCOMES) - seen
    extra = seen - set(REQUIRED_OUTCOMES)
    for outcome_id in sorted(missing):
        errors.append(f"review_outcomes missing required outcome {outcome_id!r}")
    for outcome_id in sorted(extra):
        errors.append(f"review_outcomes contains unknown outcome {outcome_id!r}")

    return errors


def validate_ledger(
    payload: dict[str, Any],
    *,
    candidate_manifest: dict[str, Any] | None = None,
    reduction_step_ids: set[str] | None = None,
    documented_outcome_ids: set[str] | None = None,
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

    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str) or not claim_scope.strip():
        errors.append("claim_scope must be a nonempty string")
    else:
        for phrase in REQUIRED_CLAIM_SCOPE_PHRASES:
            if phrase not in claim_scope:
                errors.append(f"claim_scope must include {phrase!r}")

    errors.extend(_validate_forbidden_promotions(payload))
    errors.extend(_validate_path_list(payload, "source_of_truth_files"))

    manifest_path = payload.get("candidate_manifest")
    if not isinstance(manifest_path, str) or not manifest_path.strip():
        errors.append("candidate_manifest must be a nonempty string")
        manifest_payload = {}
    elif candidate_manifest is not None:
        manifest_payload = candidate_manifest
    else:
        try:
            manifest_payload = load_yaml_mapping(
                repo_path(manifest_path),
                label=manifest_path,
            )
        except (OSError, ValueError, YAMLError) as exc:
            manifest_payload = {}
            errors.append(str(exc))

    if manifest_payload:
        if manifest_payload.get("review_gate_ledger") != "metadata/n9_review_gate_ledger.yaml":
            errors.append(
                "candidate manifest must reference metadata/n9_review_gate_ledger.yaml"
            )
        manifest_command_ids = _candidate_manifest_command_ids(manifest_payload)
        manifest_review_gate_ids = _candidate_manifest_review_gate_ids(manifest_payload)
        if "n9_review_gate_ledger" not in manifest_command_ids:
            errors.append("candidate manifest missing n9_review_gate_ledger command")
    else:
        manifest_command_ids = set()
        manifest_review_gate_ids = set()

    steps = reduction_step_ids if reduction_step_ids is not None else _reduction_chain_step_ids()
    outcomes = (
        documented_outcome_ids
        if documented_outcome_ids is not None
        else _review_packet_outcome_ids()
    )

    gate_errors, gate_ids, gate_manifest_refs = _validate_review_gates(
        payload,
        manifest_command_ids=manifest_command_ids,
        manifest_review_gate_ids=manifest_review_gate_ids,
        reduction_step_ids=steps,
    )
    errors.extend(gate_errors)
    infra_errors, infra_ids, infra_manifest_refs = _validate_infrastructure_gates(
        payload,
        manifest_command_ids=manifest_command_ids,
        manifest_review_gate_ids=manifest_review_gate_ids,
    )
    errors.extend(infra_errors)

    covered_manifest_gates = gate_manifest_refs | infra_manifest_refs
    missing_manifest_gates = manifest_review_gate_ids - covered_manifest_gates
    extra_manifest_refs = covered_manifest_gates - manifest_review_gate_ids
    for gate_id in sorted(missing_manifest_gates):
        errors.append(f"candidate manifest review gate {gate_id!r} is not covered")
    for gate_id in sorted(extra_manifest_refs):
        errors.append(f"ledger references unknown manifest review gate {gate_id!r}")

    errors.extend(
        _validate_outcomes(
            payload,
            gate_ids=gate_ids | infra_ids,
            documented_outcome_ids=outcomes,
        )
    )

    return errors


def summary_payload(payload: dict[str, Any], errors: Sequence[str]) -> dict[str, Any]:
    gates = payload.get("review_gates", [])
    infra = payload.get("infrastructure_gates", [])
    outcomes = payload.get("review_outcomes", [])
    gate_ids = [gate.get("id") for gate in gates if isinstance(gate, dict)]
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "candidate_manifest": payload.get("candidate_manifest"),
        "review_gate_count": len(gates) if isinstance(gates, list) else 0,
        "infrastructure_gate_count": len(infra) if isinstance(infra, list) else 0,
        "review_gate_ids": gate_ids,
        "review_outcome_count": len(outcomes) if isinstance(outcomes, list) else 0,
        "review_outcome_ids": [
            outcome.get("id") for outcome in outcomes if isinstance(outcome, dict)
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_error_count": len(errors),
        "first_validation_errors": list(errors[:5]),
        "claim_scope": payload.get("claim_scope"),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--check", action="store_true", help="fail on validation errors")
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
    ledger = args.ledger
    if not ledger.is_absolute():
        ledger = REPO_ROOT / ledger

    try:
        payload = load_ledger(ledger)
        errors = validate_ledger(payload)
    except (OSError, ValueError, YAMLError) as exc:
        payload = {"schema": SCHEMA, "status": "LOAD_FAILED"}
        errors = [str(exc)]

    if args.summary_json:
        print(json.dumps(summary_payload(payload, errors), indent=2, sort_keys=True))
    elif args.json:
        full_payload = dict(payload)
        full_payload["validation_errors"] = errors
        full_payload["validation_status"] = "passed" if not errors else "failed"
        print(json.dumps(full_payload, indent=2, sort_keys=True))
    else:
        print("n=9 review gate ledger")
        print(f"candidate_manifest: {payload.get('candidate_manifest')}")
        print(
            "review_gates: "
            f"{len(payload.get('review_gates', [])) if isinstance(payload.get('review_gates'), list) else 0}"
        )
        print(f"validation_status: {'passed' if not errors else 'failed'}")

    if errors and args.check:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
