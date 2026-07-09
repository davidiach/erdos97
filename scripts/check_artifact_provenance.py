#!/usr/bin/env python3
"""Validate the generated-artifact provenance manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
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
DEFAULT_MANIFEST = REPO_ROOT / "metadata" / "generated_artifacts.yaml"
SCHEMA = "erdos97.generated_artifacts.v2"
ARCHIVE_DIGEST_SCHEMA = "erdos97.archived_tracked_artifacts.v1"
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
TRACKED_ARTIFACT_COVERAGE_GLOBS = (
    "data/certificates/*.json",
    "data/certificates/**/*.json",
    "certificates/*.json",
    "certificates/**/*.json",
)

KNOWN_TRUST_CLASSES = {
    "EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN",
    "EXACT_CERTIFICATE_DIAGNOSTIC",
    "EXACT_OBSTRUCTION",
    "EXACT_ROUTE_PRUNING_CERTIFICATE",
    "FINITE_BOOKKEEPING_NOT_A_PROOF",
    "INCIDENCE_COMPLETENESS",
    "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
    "MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING",
    "MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING_SECONDARY",
    "REVIEW_PENDING_DIAGNOSTIC",
    "REVIEW_PENDING_PROVENANCE",
    "SMT_EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN",
}
PROVENANCE_MODES = {"embedded", "manifest_only_legacy"}
JSON_TOP_LEVEL_TYPES = {
    "object": dict,
    "list": list,
}
AMBIGUOUS_FORBIDDEN_CLAIMS = {
    "external independent review",
    "independent external review",
}
PATH_REPLAY_FLAGS = {
    "--artifact",
    "--certificate",
    "--check-artifact",
    "--check-compatible-orders-data",
    "--check-exact-analysis-data",
    "--verify-certificate",
}
PATH_OUTPUT_FLAGS = {
    "--out",
    "--output",
    "--write",
    "--write-artifact",
}
PATH_OUTPUT_SWITCHES_WITH_TARGET_FLAGS = {
    "--write-artifact": {"--artifact"},
}
PATH_DEFAULT_OUTPUT_SWITCHES = {
    "--write",
    "--write-artifact",
}


def repo_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def load_manifest(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise ValueError(
            "PyYAML is required to parse metadata/generated_artifacts.yaml; "
            "install with `pip install -e .`"
        )
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("manifest top level must be a mapping")
    return payload


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def archive_inventory_digest(items: Sequence[dict[str, Any]]) -> str:
    """Digest the archive inventory independently of YAML formatting/order."""

    digest = hashlib.sha256()
    digest.update(f"{ARCHIVE_DIGEST_SCHEMA}\n".encode())
    rows: list[tuple[str, str, int, str]] = []
    for item in items:
        raw_path = item.get("path")
        sha256 = item.get("sha256")
        size_bytes = item.get("size_bytes")
        json_type = item.get("json_top_level_type")
        if (
            isinstance(raw_path, str)
            and isinstance(sha256, str)
            and isinstance(size_bytes, int)
            and not isinstance(size_bytes, bool)
            and isinstance(json_type, str)
        ):
            rows.append((raw_path, sha256.lower(), size_bytes, json_type))
    for row in sorted(rows):
        digest.update("\0".join(map(str, row)).encode())
        digest.update(b"\n")
    return digest.hexdigest()


def dotted_get(payload: Any, dotted_key: str) -> Any:
    current = payload
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(dotted_key)
        current = current[part]
    return current


def validate_manifest(payload: dict[str, Any], *, check_tracked_coverage: bool = False) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != SCHEMA:
        errors.append(f"schema is {payload.get('schema')!r}, expected {SCHEMA!r}")
    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str) or not claim_scope.strip():
        errors.append("claim_scope must be a nonempty string")

    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifacts must be a nonempty list")
        return errors

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for index, artifact in enumerate(artifacts):
        label = f"artifacts[{index}]"
        if not isinstance(artifact, dict):
            errors.append(f"{label} must be a mapping")
            continue
        errors.extend(validate_artifact(artifact, label, seen_ids, seen_paths))
    if check_tracked_coverage or "native_trust_policy" in payload:
        errors.extend(validate_native_trust_policy(payload, artifacts))
    archived_paths: set[str] = set()
    if check_tracked_coverage or "archived_tracked_artifacts" in payload:
        archive_errors, archived_paths = validate_archived_artifacts(payload, seen_paths)
        errors.extend(archive_errors)
    if check_tracked_coverage or "source_of_truth_surfaces" in payload:
        errors.extend(validate_source_of_truth_archive_boundary(payload, archived_paths))
    if "unmanaged_tracked_artifacts" in payload:
        errors.append(
            "unmanaged_tracked_artifacts is obsolete; classify entries as managed "
            "or archived with pinned byte metadata"
        )
    if check_tracked_coverage:
        errors.extend(validate_tracked_artifact_coverage(seen_paths, archived_paths))
    return errors


def validate_artifact(
    artifact: dict[str, Any],
    label: str,
    seen_ids: set[str],
    seen_paths: set[str],
) -> list[str]:
    errors: list[str] = []
    required_strings = (
        "id",
        "path",
        "kind",
        "generator",
        "command",
        "claim_scope",
        "trust_class",
    )
    for key in required_strings:
        value = artifact.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}.{key} must be a nonempty string")

    ident = artifact.get("id")
    if isinstance(ident, str):
        if ident in seen_ids:
            errors.append(f"{label}.id {ident!r} is duplicated")
        seen_ids.add(ident)

    raw_path = artifact.get("path")
    if isinstance(raw_path, str):
        if raw_path in seen_paths:
            errors.append(f"{label}.path {raw_path!r} is duplicated")
        seen_paths.add(raw_path)
        path = repo_path(raw_path)
        if not path.exists():
            errors.append(f"{label}.path does not exist: {raw_path}")
            payload = None
        else:
            errors.extend(validate_file_metadata(artifact, path, label))
            try:
                payload = load_json(path)
            except json.JSONDecodeError as exc:
                errors.append(f"{label}.path is not valid JSON: {exc}")
                payload = None
    else:
        payload = None

    generator = artifact.get("generator")
    if isinstance(generator, str) and not repo_path(generator).exists():
        errors.append(f"{label}.generator does not exist: {generator}")

    checker = artifact.get("checker")
    if checker is not None:
        if not isinstance(checker, str) or not checker.strip():
            errors.append(f"{label}.checker must be a nonempty string when present")
        elif not repo_path(checker).exists():
            errors.append(f"{label}.checker does not exist: {checker}")

    check_command = artifact.get("check_command")
    if check_command is not None and (
        not isinstance(check_command, str) or not check_command.strip()
    ):
        errors.append(f"{label}.check_command must be a nonempty string when present")
    errors.extend(validate_check_command_for_generated_write(artifact, label))

    if artifact.get("direct_edit_allowed") is not False:
        errors.append(f"{label}.direct_edit_allowed must be false for generated artifacts")

    provenance_mode = artifact.get("provenance_mode")
    if provenance_mode not in PROVENANCE_MODES:
        errors.append(f"{label}.provenance_mode must be one of {sorted(PROVENANCE_MODES)}")

    trust_class = artifact.get("trust_class")
    if trust_class not in KNOWN_TRUST_CLASSES:
        errors.append(
            f"{label}.trust_class {trust_class!r} is not a known canonical trust class"
        )

    forbidden_claims = artifact.get("forbidden_claims")
    if not isinstance(forbidden_claims, list) or not forbidden_claims:
        errors.append(f"{label}.forbidden_claims must be a nonempty list")
    else:
        for phrase in forbidden_claims:
            if not isinstance(phrase, str) or not phrase.strip():
                errors.append(f"{label}.forbidden_claims entries must be nonempty strings")
                continue
            if phrase.strip().lower() in AMBIGUOUS_FORBIDDEN_CLAIMS:
                errors.append(
                    f"{label}.forbidden_claims entry {phrase!r} is ambiguous; "
                    "name a false completed-review claim instead"
                )

    if payload is not None:
        errors.extend(validate_json_payload(artifact, payload, label))
    return errors


def command_tokens(command: str) -> list[str]:
    if os.name == "nt":
        # POSIX shlex treats backslashes as escapes, which collapses Windows
        # absolute paths like C:\repo\artifact.json before path matching.
        command = command.replace("\\", "\\\\")
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def path_variants(raw_path: str) -> set[str]:
    normalized = raw_path.replace("\\", "/")
    stripped = normalized
    while stripped.startswith("./"):
        stripped = stripped[2:]
    variants = {normalized, stripped, repo_path(raw_path).resolve().as_posix()}
    if stripped and not Path(stripped).is_absolute():
        variants.add(f"./{stripped}")
    return variants


def token_matches_path(token: str, variants: set[str]) -> bool:
    normalized = token.replace("\\", "/")
    return normalized in variants


def token_value_matches_path(token: str, variants: set[str]) -> bool:
    if "=" not in token:
        return False
    return token_matches_path(token.split("=", 1)[1], variants)


def redirection_value(token: str) -> str | None:
    match = re.fullmatch(r"\d?>{1,2}(.+)", token)
    if match is None:
        return None
    return match.group(1)


def command_mentions_path(command: str, raw_path: str) -> bool:
    variants = path_variants(raw_path)
    previous: str | None = None
    for token in command_tokens(command):
        redirect_target = redirection_value(token)
        if (
            token_matches_path(token, variants)
            or token_value_matches_path(token, variants)
            or (
                previous is not None
                and re.fullmatch(r"\d?>{1,2}", previous)
                and token_matches_path(token, variants)
            )
            or (
                redirect_target is not None
                and token_matches_path(redirect_target, variants)
            )
        ):
            return True
        previous = token
    return False


def command_outputs_path(command: str, raw_path: str) -> bool:
    tokens = command_tokens(command)
    variants = path_variants(raw_path)
    output_target_flags: set[str] = set()
    previous: str | None = None
    for token in tokens:
        redirect_target = redirection_value(token)
        output_target_flags.update(PATH_OUTPUT_SWITCHES_WITH_TARGET_FLAGS.get(token, set()))
        if token_matches_path(token, variants):
            # A path token written by a space-separated redirection (`> path`,
            # `2>> path`) or piped into `tee path` is an output, even though the
            # previous token is not an --out-style flag.
            if previous is not None and (
                re.fullmatch(r"\d?>{1,2}", previous) or previous == "tee"
            ):
                return True
            return previous in PATH_OUTPUT_FLAGS or previous in output_target_flags
        if any(
            token.startswith(f"{flag}=")
            and token_matches_path(token.split("=", 1)[1], variants)
            for flag in PATH_OUTPUT_FLAGS
        ):
            return True
        if any(
            token.startswith(f"{flag}=")
            and token_matches_path(token.split("=", 1)[1], variants)
            for flag in output_target_flags
        ):
            return True
        if redirect_target is not None and token_matches_path(redirect_target, variants):
            return True
        previous = token
    return False


def command_uses_default_output_path(command: str, raw_path: str) -> bool:
    if command_outputs_path(command, raw_path):
        return False
    return any(token in PATH_DEFAULT_OUTPUT_SWITCHES for token in command_tokens(command))


def command_replays_path(command: str, raw_path: str) -> bool:
    tokens = command_tokens(command)
    variants = path_variants(raw_path)
    previous: str | None = None
    for token in tokens:
        if token_matches_path(token, variants):
            return previous in PATH_REPLAY_FLAGS
        if any(
            token.startswith(f"{flag}=")
            and token_matches_path(token.split("=", 1)[1], variants)
            for flag in PATH_REPLAY_FLAGS
        ):
            return True
        previous = token
    return False


def validate_check_command_for_generated_write(
    artifact: dict[str, Any],
    label: str,
) -> list[str]:
    raw_path = artifact.get("path")
    command = artifact.get("command")
    check_command = artifact.get("check_command")
    if not (
        isinstance(raw_path, str)
        and isinstance(command, str)
    ):
        return []
    if command_uses_default_output_path(command, raw_path) and (
        not isinstance(check_command, str) or not check_command.strip()
    ):
        return [
            f"{label}.check_command must be present for default-path artifact write "
            f"command {raw_path!r}"
        ]
    if not command_outputs_path(command, raw_path):
        return []
    if not isinstance(check_command, str) or not check_command.strip():
        return [
            f"{label}.check_command must replay explicitly generated artifact path "
            f"{raw_path!r}"
        ]
    if command_replays_path(check_command, raw_path):
        return []
    return [
        f"{label}.check_command must replay explicitly generated artifact path "
        f"{raw_path!r}"
    ]


def validate_file_metadata(artifact: dict[str, Any], path: Path, label: str) -> list[str]:
    """Validate byte-for-byte artifact metadata."""
    errors: list[str] = []

    expected_sha = artifact.get("sha256")
    if not isinstance(expected_sha, str) or not SHA256_RE.fullmatch(expected_sha):
        errors.append(f"{label}.sha256 must be a 64-character hex string")
    else:
        actual_sha = sha256_file(path)
        if actual_sha != expected_sha.lower():
            errors.append(f"{label}.sha256 is {actual_sha!r}, expected {expected_sha!r}")

    expected_size = artifact.get("size_bytes")
    if not isinstance(expected_size, int) or isinstance(expected_size, bool) or expected_size < 0:
        errors.append(f"{label}.size_bytes must be a nonnegative integer")
    else:
        actual_size = path.stat().st_size
        if actual_size != expected_size:
            errors.append(f"{label}.size_bytes is {actual_size!r}, expected {expected_size!r}")

    return errors


def validate_json_payload(artifact: dict[str, Any], payload: Any, label: str) -> list[str]:
    errors: list[str] = []
    expected_type = artifact.get("json_top_level_type")
    expected_python_type = JSON_TOP_LEVEL_TYPES.get(expected_type)
    if expected_python_type is None:
        errors.append(f"{label}.json_top_level_type must be one of {