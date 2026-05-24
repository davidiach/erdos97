"""Probe local tooling for C19 order-CNF proof replay experiments.

This is an environment diagnostic only. It does not check a mathematical
certificate, prove UNSAT, or alter the status of any Erdos Problem #97 claim.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from export_c19_kalmanson_order_cnf import (  # noqa: E402
    assert_expected as assert_c19_cnf_expected,
)
from export_c19_kalmanson_order_cnf import check_artifact as check_c19_cnf  # noqa: E402
from export_c19_kalmanson_order_cnf import diagnostic_payload  # noqa: E402

DEFAULT_C19_CNF_SUMMARY = ROOT / "reports" / "c19_kalmanson_order_cnf_summary.json"
DEFAULT_COMMANDS = ("kissat", "cadical", "drat-trim", "lrat-check")
DEFAULT_MODULES = ("pysat", "z3")
SAT_SOLVER_COMMANDS = ("kissat", "cadical")
PROOF_CHECKER_COMMANDS = ("drat-trim", "lrat-check")


def dedupe(items: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _command_payload(
    command_names: Sequence[str],
    which: Callable[[str], str | None],
) -> dict[str, dict[str, str | bool | None]]:
    commands: dict[str, dict[str, str | bool | None]] = {}
    for name in command_names:
        path = which(name)
        commands[name] = {"found": path is not None, "path": path}
    return commands


def _module_payload(
    module_names: Sequence[str],
    find_spec: Callable[[str], Any],
) -> dict[str, dict[str, bool]]:
    modules: dict[str, dict[str, bool]] = {}
    for name in module_names:
        try:
            found = find_spec(name) is not None
        except (ImportError, AttributeError, ValueError):
            found = False
        modules[name] = {"found": found}
    return modules


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def c19_cnf_summary_payload(artifact: Path) -> dict[str, Any]:
    payload = diagnostic_payload()
    try:
        assert_c19_cnf_expected(payload)
        check_c19_cnf(artifact, payload)
    except (AssertionError, OSError, json.JSONDecodeError) as exc:
        return {
            "checked": True,
            "ok": False,
            "artifact": _display_path(artifact),
            "error": str(exc),
        }

    return {
        "checked": True,
        "ok": True,
        "artifact": _display_path(artifact),
        "variables": payload["encoding"]["variable_count"],
        "clauses": payload["encoding"]["clause_count"],
        "dimacs_sha256": payload["validation"]["dimacs_sha256"],
    }


def tooling_probe(
    *,
    command_names: Sequence[str] = DEFAULT_COMMANDS,
    module_names: Sequence[str] = DEFAULT_MODULES,
    required_commands: Sequence[str] = (),
    required_modules: Sequence[str] = (),
    check_c19_cnf_summary: bool = False,
    c19_cnf_summary_artifact: Path = DEFAULT_C19_CNF_SUMMARY,
    which: Callable[[str], str | None] = shutil.which,
    find_spec: Callable[[str], Any] = importlib.util.find_spec,
) -> dict[str, Any]:
    command_names = dedupe((*command_names, *required_commands))
    module_names = dedupe((*module_names, *required_modules))
    commands = _command_payload(command_names, which)
    modules = _module_payload(module_names, find_spec)

    solver_found = [
        name for name in SAT_SOLVER_COMMANDS if commands.get(name, {}).get("found")
    ]
    checker_found = [
        name for name in PROOF_CHECKER_COMMANDS if commands.get(name, {}).get("found")
    ]
    missing_commands = [
        name for name in required_commands if not commands[name]["found"]
    ]
    missing_modules = [name for name in required_modules if not modules[name]["found"]]
    missing_toolchain_groups: list[str] = []
    if not solver_found:
        missing_toolchain_groups.append("sat_solver_with_proof_logging")
    if not checker_found:
        missing_toolchain_groups.append("proof_checker")

    return {
        "status": "C19_PROOF_TOOLING_ENVIRONMENT_DIAGNOSTIC_ONLY",
        "claim_scope": {
            "changes_mathematical_status": False,
            "proves_c19_order_cnf_unsat": False,
            "proves_erdos97": False,
            "counterexample_claimed": False,
        },
        "checked_inputs": [
            "data/certificates/c19_skew_all_orders_kalmanson_z3.json",
            "reports/c19_kalmanson_order_cnf_summary.json",
            "scripts/export_c19_kalmanson_order_cnf.py",
        ],
        "commands": commands,
        "python_modules": modules,
        "c19_cnf_summary": (
            c19_cnf_summary_payload(c19_cnf_summary_artifact)
            if check_c19_cnf_summary
            else {"checked": False}
        ),
        "requirements": {
            "missing_commands": missing_commands,
            "missing_modules": missing_modules,
            "c19_solver_independent_replay": {
                "ready": not missing_toolchain_groups,
                "accepted_solver_commands": list(SAT_SOLVER_COMMANDS),
                "accepted_checker_commands": list(PROOF_CHECKER_COMMANDS),
                "found_solver_commands": solver_found,
                "found_checker_commands": checker_found,
                "missing_groups": missing_toolchain_groups,
            },
        },
        "next_steps": [
            "pin a SAT solver that can emit a checkable proof",
            "pin a DRAT/LRAT or equivalent proof checker",
            "byte-check the generated C19 DIMACS before validating any proof object",
        ],
    }


def print_human(payload: dict[str, Any]) -> None:
    replay = payload["requirements"]["c19_solver_independent_replay"]
    c19_cnf = payload["c19_cnf_summary"]
    print("C19 proof tooling probe")
    print(f"status: {payload['status']}")
    if c19_cnf["checked"]:
        print(f"C19 CNF summary checked: {c19_cnf['ok']}")
        if not c19_cnf["ok"]:
            print(f"C19 CNF summary error: {c19_cnf['error']}")
    print(f"solver-independent replay ready: {replay['ready']}")
    if replay["missing_groups"]:
        print("missing toolchain groups: " + ", ".join(replay["missing_groups"]))
    print("commands:")
    for name, row in payload["commands"].items():
        marker = row["path"] if row["found"] else "not found"
        print(f"  {name}: {marker}")
    print("python modules:")
    for name, row in payload["python_modules"].items():
        print(f"  {name}: {row['found']}")
    print("claim scope: environment diagnostic only")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    parser.add_argument("--out", type=Path, help="write the stable JSON payload")
    parser.add_argument(
        "--command",
        action="append",
        default=[],
        help="extra executable name to include in the probe",
    )
    parser.add_argument(
        "--module",
        action="append",
        default=[],
        help="extra Python module name to include in the probe",
    )
    parser.add_argument(
        "--require-command",
        action="append",
        default=[],
        help="return nonzero if this executable is not found",
    )
    parser.add_argument(
        "--require-module",
        action="append",
        default=[],
        help="return nonzero if this Python module is not importable",
    )
    parser.add_argument(
        "--require-c19-proof-toolchain",
        action="store_true",
        help=(
            "return nonzero unless at least one supported SAT solver and one "
            "supported proof checker are found"
        ),
    )
    parser.add_argument(
        "--check-c19-cnf-summary",
        action="store_true",
        help="check the stored C19 order-CNF summary before reporting tooling",
    )
    parser.add_argument(
        "--c19-cnf-summary-artifact",
        type=Path,
        default=DEFAULT_C19_CNF_SUMMARY,
        help="C19 order-CNF summary artifact to check",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = tooling_probe(
        command_names=(*DEFAULT_COMMANDS, *args.command),
        module_names=(*DEFAULT_MODULES, *args.module),
        required_commands=args.require_command,
        required_modules=args.require_module,
        check_c19_cnf_summary=args.check_c19_cnf_summary,
        c19_cnf_summary_artifact=args.c19_cnf_summary_artifact,
    )

    if args.out:
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_human(payload)

    missing = (
        payload["requirements"]["missing_commands"]
        or payload["requirements"]["missing_modules"]
    )
    if args.require_c19_proof_toolchain:
        missing = (
            missing
            or payload["requirements"]["c19_solver_independent_replay"][
                "missing_groups"
            ]
        )
    c19_cnf_failed = (
        payload["c19_cnf_summary"]["checked"] and not payload["c19_cnf_summary"]["ok"]
    )
    if c19_cnf_failed:
        print("C19 CNF summary check failed", file=sys.stderr)
    if missing:
        print("required proof tooling is not available", file=sys.stderr)
    if missing or c19_cnf_failed:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
