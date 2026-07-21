#!/usr/bin/env python3
"""Run the slower artifact audit commands and record reproducibility metadata.

The command registry itself lives in ``scripts/audit_commands.json``; this
runner loads, validates, shards, and executes it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.ci_sharding import (  # noqa: E402
    SHARD_ALGORITHM,
    select_shard,
    validate_shard,
)


@dataclass(frozen=True)
class AuditCommand:
    """One artifact-audit command and its claim scope."""

    ident: str
    command: tuple[str, ...]
    claim_scope: str



REGISTRY_PATH = REPO_ROOT / "scripts" / "audit_commands.json"
REGISTRY_TYPE = "erdos97_artifact_audit_command_registry_v1"


class RegistryError(ValueError):
    """Raised when the audit command registry data file is invalid."""


def _registry_command(entry: object, *, source: str) -> AuditCommand:
    if not isinstance(entry, dict):
        raise RegistryError(f"{source}: command entries must be JSON objects")
    unknown = sorted(set(entry) - {"id", "command", "claim_scope"})
    if unknown:
        raise RegistryError(f"{source}: unknown keys {unknown}")
    ident = entry.get("id")
    command = entry.get("command")
    claim_scope = entry.get("claim_scope")
    if not isinstance(ident, str) or not ident:
        raise RegistryError(f"{source}: 'id' must be a non-empty string")
    if (
        not isinstance(command, list)
        or not command
        or not all(isinstance(part, str) and part for part in command)
    ):
        raise RegistryError(
            f"{source}: 'command' must be a non-empty list of non-empty strings"
        )
    if not isinstance(claim_scope, str) or not claim_scope:
        raise RegistryError(f"{source}: 'claim_scope' must be a non-empty string")
    return AuditCommand(ident=ident, command=tuple(command), claim_scope=claim_scope)


def load_command_registry(
    path: Path = REGISTRY_PATH,
) -> tuple[
    tuple[AuditCommand, ...],
    tuple[AuditCommand, ...],
    dict[str, tuple[str, ...]],
]:
    """Load and validate the registry data file backing this runner.

    Returns ``(preflight_commands, audit_commands, make_target_command_ids)``.
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError(f"cannot read audit command registry {path}: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("type") != REGISTRY_TYPE:
        raise RegistryError(f"{path}: expected a JSON object with type {REGISTRY_TYPE!r}")

    preflight = tuple(
        _registry_command(entry, source=f"{path}: preflight_commands[{index}]")
        for index, entry in enumerate(payload.get("preflight_commands", []))
    )
    audit = tuple(
        _registry_command(entry, source=f"{path}: audit_commands[{index}]")
        for index, entry in enumerate(payload.get("audit_commands", []))
    )
    if not audit:
        raise RegistryError(f"{path}: audit_commands must not be empty")
    idents = [command.ident for command in (*preflight, *audit)]
    duplicates = sorted({ident for ident in idents if idents.count(ident) > 1})
    if duplicates:
        raise RegistryError(f"{path}: duplicate command ids {duplicates}")

    audit_idents = {command.ident for command in audit}
    raw_targets = payload.get("make_targets", {})
    if not isinstance(raw_targets, dict):
        raise RegistryError(f"{path}: make_targets must be an object")
    make_targets: dict[str, tuple[str, ...]] = {}
    for target, raw_idents in raw_targets.items():
        source = f"{path}: make_targets[{target!r}]"
        if not isinstance(target, str) or not target:
            raise RegistryError(f"{path}: make_targets keys must be non-empty strings")
        if not isinstance(raw_idents, list) or not all(
            isinstance(ident, str) for ident in raw_idents
        ):
            raise RegistryError(f"{source}: must be a list of command id strings")
        unknown_ids = sorted(set(raw_idents) - audit_idents)
        if unknown_ids:
            raise RegistryError(f"{source}: unknown command ids {unknown_ids}")
        if len(raw_idents) != len(set(raw_idents)):
            raise RegistryError(f"{source}: duplicate command ids")
        make_targets[target] = tuple(raw_idents)
    return preflight, audit, make_targets


AUDIT_PREFLIGHT_COMMANDS, AUDIT_COMMANDS, MAKE_TARGET_COMMAND_IDS = load_command_registry()


def make_target_commands(target: str) -> tuple[AuditCommand, ...]:
    """Return the registry commands behind one generated Makefile verify target."""
    if target not in MAKE_TARGET_COMMAND_IDS:
        known = ", ".join(sorted(MAKE_TARGET_COMMAND_IDS))
        raise RegistryError(f"unknown make target {target!r} (known: {known})")
    by_ident = {command.ident: command for command in AUDIT_COMMANDS}
    return tuple(by_ident[ident] for ident in MAKE_TARGET_COMMAND_IDS[target])




def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_git(args: Sequence[str]) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def command_text(command: Sequence[str]) -> str:
    return " ".join(command)


def subprocess_command(command: Sequence[str]) -> tuple[str, ...]:
    """Return the executable argv for a stored audit command."""
    if command and command[0] == "python":
        return (sys.executable, *command[1:])
    return tuple(command)


def run_audit_command(command: AuditCommand, output_dir: Path) -> dict[str, Any]:
    command_dir = output_dir / "commands"
    command_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = command_dir / f"{command.ident}.stdout"
    stderr_path = command_dir / f"{command.ident}.stderr"

    started_at = utc_now()
    start = time.perf_counter()
    result = subprocess.run(
        subprocess_command(command.command),
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    elapsed_seconds = time.perf_counter() - start
    finished_at = utc_now()

    stdout_path.write_bytes(result.stdout)
    stderr_path.write_bytes(result.stderr)
    combined_output = result.stdout + result.stderr

    return {
        "id": command.ident,
        "command": command_text(command.command),
        "claim_scope": command.claim_scope,
        "started_at_utc": started_at,
        "finished_at_utc": finished_at,
        "elapsed_seconds": round(elapsed_seconds, 6),
        "exit_code": result.returncode,
        "stdout_path": stdout_path.relative_to(output_dir).as_posix(),
        "stderr_path": stderr_path.relative_to(output_dir).as_posix(),
        "stdout_sha256": sha256_bytes(result.stdout),
        "stderr_sha256": sha256_bytes(result.stderr),
        "combined_output_sha256": sha256_bytes(combined_output),
        "stdout_bytes": len(result.stdout),
        "stderr_bytes": len(result.stderr),
    }


def run_verify_commands(commands: Sequence[AuditCommand]) -> int:
    for index, command in enumerate(commands, start=1):
        print(
            f"[{index}/{len(commands)}] {command.ident}: {command_text(command.command)}",
            flush=True,
        )
        result = subprocess.run(subprocess_command(command.command), cwd=REPO_ROOT)
        if result.returncode != 0:
            return result.returncode
    return 0


def build_summary(
    output_dir: Path,
    commands: Sequence[AuditCommand],
    *,
    preflight_commands: Sequence[AuditCommand] = AUDIT_PREFLIGHT_COMMANDS,
) -> dict[str, Any]:
    started_at = utc_now()
    listed_commands = (*preflight_commands, *commands)
    command_results = [run_audit_command(command, output_dir) for command in listed_commands]
    finished_at = utc_now()
    dependency_snapshot = REPO_ROOT / "requirements-lock.txt"

    return {
        "type": "erdos97_artifact_audit_run_v1",
        "claim_scope": (
            "Artifact audit for repo-local finite-case and fixed-pattern/fixed-order "
            "certificates; passing does not prove Erdos Problem #97."
        ),
        "does_not_claim": [
            "general proof of Erdos Problem #97",
            "counterexample to Erdos Problem #97",
            "official/global status change",
            "independent external mathematical review",
        ],
        "started_at_utc": started_at,
        "finished_at_utc": finished_at,
        "verified": all(record["exit_code"] == 0 for record in command_results),
        "preflight_command_count": len(preflight_commands),
        "audit_command_count": len(commands),
        "command_count": len(listed_commands),
        "repo": {
            "commit": run_git(("rev-parse", "HEAD")),
            "status_porcelain": run_git(("status", "--porcelain")),
        },
        "python": {
            "executable": sys.executable,
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "dependency_snapshot": {
            "path": dependency_snapshot.relative_to(REPO_ROOT).as_posix(),
            "sha256": sha256_file(dependency_snapshot),
        },
        "commands": command_results,
    }


def _command_list_rows(commands: Sequence[AuditCommand]) -> list[dict[str, str]]:
    return [
        {
            "id": command.ident,
            "command": command_text(command.command),
            "claim_scope": command.claim_scope,
        }
        for command in commands
    ]


def shard_commands(
    commands: Sequence[AuditCommand],
    *,
    shard_index: int,
    shard_count: int,
) -> tuple[AuditCommand, ...]:
    """Select one stable, exhaustive shard of registered audit commands."""
    selected = select_shard(
        commands,
        key=lambda command: command.ident,
        shard_index=shard_index,
        shard_count=shard_count,
    )
    return tuple(selected)


def list_commands_payload(
    commands: Sequence[AuditCommand],
    *,
    preflight_commands: Sequence[AuditCommand] = AUDIT_PREFLIGHT_COMMANDS,
    registered_audit_command_count: int | None = None,
    shard_index: int = 0,
    shard_count: int = 1,
) -> dict[str, Any]:
    validate_shard(shard_index, shard_count)
    listed_commands = (*preflight_commands, *commands)
    return {
        "type": "erdos97_artifact_audit_command_list_v1",
        "claim_scope": (
            "Registered artifact audit command list only; printing this list "
            "does not run checks, prove Erdos Problem #97, or change any "
            "repository claim."
        ),
        "preflight_command_count": len(preflight_commands),
        "audit_command_count": len(commands),
        "registered_audit_command_count": (
            len(commands)
            if registered_audit_command_count is None
            else registered_audit_command_count
        ),
        "command_count": len(listed_commands),
        "shard": {
            "index": shard_index,
            "count": shard_count,
            "algorithm": SHARD_ALGORITHM,
        },
        "commands": _command_list_rows(listed_commands),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--list-commands",
        action="store_true",
        help="Print the registered audit command list as JSON without running it.",
    )
    mode.add_argument(
        "--verify-only",
        action="store_true",
        help="Run registered artifact audit commands without writing metadata.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifact-audit-results"),
        help="Directory for summary.json and per-command stdout/stderr files.",
    )
    parser.add_argument(
        "--shard-count",
        type=int,
        default=1,
        help="Number of deterministic command shards (default: 1).",
    )
    parser.add_argument(
        "--shard-index",
        type=int,
        default=0,
        help="Zero-based deterministic command shard to run (default: 0).",
    )
    args = parser.parse_args(argv)
    try:
        validate_shard(args.shard_index, args.shard_count)
    except ValueError as exc:
        parser.error(str(exc))
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    preflight_commands = AUDIT_PREFLIGHT_COMMANDS if args.shard_index == 0 else ()
    commands = shard_commands(
        AUDIT_COMMANDS,
        shard_index=args.shard_index,
        shard_count=args.shard_count,
    )
    if args.list_commands:
        print(
            json.dumps(
                list_commands_payload(
                    commands,
                    preflight_commands=preflight_commands,
                    registered_audit_command_count=len(AUDIT_COMMANDS),
                    shard_index=args.shard_index,
                    shard_count=args.shard_count,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.verify_only:
        return run_verify_commands(commands)

    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = build_summary(
        output_dir,
        commands,
        preflight_commands=preflight_commands,
    )
    summary["registered_audit_command_count"] = len(AUDIT_COMMANDS)
    summary["shard"] = {
        "index": args.shard_index,
        "count": args.shard_count,
        "algorithm": SHARD_ALGORITHM,
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
