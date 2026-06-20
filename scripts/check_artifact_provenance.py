#!/usr/bin/env python3
"""Validate the generated-artifact provenance manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
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
SCHEMA = "erdos97.generated_artifacts.v1"
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
TRACKED_ARTIFACT_COVERAGE_GLOBS = ("data/certificates/*.json", "data/certificates/**/*.json")

KNOWN_TRUST = {
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
    errors.extend(validate_unmanaged_artifacts(payload))
    if check_tracked_coverage:
        errors.extend(validate_tracked_artifact_coverage(payload, seen_paths))
    return errors


def validate_artifact(
    artifact: dict[str, Any],
    label: str,
    seen_ids: set[str],
    seen_paths: set[str],
) -> list[str]:
    errors: list[str] = []
    required_strings = ("id", "path", "kind", "generator", "command", "claim_scope", "trust")
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

    if artifact.get("direct_edit_allowed") is not False:
        errors.append(f"{label}.direct_edit_allowed must be false for generated artifacts")

    provenance_mode = artifact.get("provenance_mode")
    if provenance_mode not in PROVENANCE_MODES:
        errors.append(f"{label}.provenance_mode must be one of {sorted(PROVENANCE_MODES)}")

    trust = artifact.get("trust")
    if trust not in KNOWN_TRUST:
        errors.append(f"{label}.trust {trust!r} is not a known trust value")

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
        errors.append(f"{label}.json_top_level_type must be one of {sorted(JSON_TOP_LEVEL_TYPES)}")
    elif not isinstance(payload, expected_python_type):
        errors.append(f"{label}.path top level is not {expected_type}")

    if artifact.get("provenance_mode") == "embedded":
        if not isinstance(payload, dict) or not isinstance(payload.get("provenance"), dict):
            errors.append(f"{label}.path must contain an embedded provenance object")

    expected_json = artifact.get("expected_json", {})
    if expected_json is None:
        expected_json = {}
    if not isinstance(expected_json, dict):
        errors.append(f"{label}.expected_json must be a mapping when present")
        return errors

    for dotted_key, expected in expected_json.items():
        try:
            actual = dotted_get(payload, str(dotted_key))
        except KeyError:
            errors.append(f"{label}.path is missing expected JSON key {dotted_key!r}")
            continue
        if actual != expected:
            errors.append(f"{label}.path {dotted_key!r} is {actual!r}, expected {expected!r}")
    return errors


def validate_unmanaged_artifacts(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    unmanaged = payload.get("unmanaged_tracked_artifacts", [])
    if unmanaged is None:
        unmanaged = []
    if not isinstance(unmanaged, list):
        return ["unmanaged_tracked_artifacts must be a list when present"]

    seen: set[str] = set()
    for index, item in enumerate(unmanaged):
        label = f"unmanaged_tracked_artifacts[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be a mapping")
            continue
        raw_path = item.get("path")
        reason = item.get("reason")
        if not isinstance(raw_path, str) or not raw_path.strip():
            errors.append(f"{label}.path must be a nonempty string")
            continue
        if raw_path in seen:
            errors.append(f"{label}.path {raw_path!r} is duplicated")
        seen.add(raw_path)
        if not repo_path(raw_path).exists():
            errors.append(f"{label}.path does not exist: {raw_path}")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{label}.reason must be a nonempty string")
    return errors


def tracked_files_for_globs(globs: Sequence[str]) -> set[str]:
    tracked: set[str] = set()
    for pattern in globs:
        try:
            result = subprocess.run(
                ["git", "ls-files", pattern],
                cwd=REPO_ROOT,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            )
        except OSError:
            result = None
        if result is not None and result.returncode == 0:
            tracked.update(line.strip().replace("\\", "/") for line in result.stdout.splitlines())
            continue
        tracked.update(
            path.relative_to(REPO_ROOT).as_posix()
            for path in REPO_ROOT.glob(pattern)
            if path.is_file()
        )
    return {path for path in tracked if path}


def validate_tracked_artifact_coverage(
    payload: dict[str, Any],
    managed_paths: set[str],
) -> list[str]:
    unmanaged = payload.get("unmanaged_tracked_artifacts", [])
    unmanaged_paths = {
        str(item.get("path"))
        for item in unmanaged
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    covered = set(managed_paths) | unmanaged_paths
    errors: list[str] = []
    for path in sorted(tracked_files_for_globs(TRACKED_ARTIFACT_COVERAGE_GLOBS)):
        if path not in covered:
            errors.append(f"tracked artifact is neither managed nor explicitly unmanaged: {path}")
    return errors


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = args.manifest
    if not manifest.is_absolute():
        manifest = REPO_ROOT / manifest
    try:
        payload = load_manifest(manifest)
        errors = validate_manifest(payload, check_tracked_coverage=True)
    except (OSError, ValueError, YAMLError) as exc:
        errors = [str(exc)]

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"artifact provenance manifest is valid: {manifest.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
