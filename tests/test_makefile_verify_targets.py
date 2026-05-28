from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _target_commands(target: str) -> list[str]:
    lines = (ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
    commands: list[str] = []
    in_target = False
    for line in lines:
        if line.startswith(f"{target}:"):
            in_target = True
            continue
        if in_target and line and not line.startswith("\t"):
            break
        if in_target and line.startswith("\t$(PYTHON) "):
            commands.append("python " + line.removeprefix("\t$(PYTHON) "))
    return commands


def test_verify_kalmanson_runs_c19_proof_tooling_preflight() -> None:
    commands = _target_commands("verify-kalmanson")

    z3_replay = (
        "python scripts/check_kalmanson_two_order_z3.py --certificate "
        "data/certificates/c19_skew_all_orders_kalmanson_z3.json --assert-unsat"
    )
    z3_clause_diagnostic = (
        "python scripts/analyze_kalmanson_z3_clauses.py --assert-expected "
        "--check-artifact reports/c19_kalmanson_z3_clause_diagnostics.json"
    )
    order_cnf_summary = (
        "python scripts/export_c19_kalmanson_order_cnf.py --assert-expected "
        "--check-artifact reports/c19_kalmanson_order_cnf_summary.json"
    )
    tooling_preflight = (
        "python scripts/probe_c19_proof_tooling.py --check-c19-cnf-summary --json"
    )

    assert z3_replay in commands
    assert z3_clause_diagnostic in commands
    assert order_cnf_summary in commands
    assert tooling_preflight in commands
    assert commands.index(z3_replay) < commands.index(z3_clause_diagnostic)
    assert commands.index(z3_clause_diagnostic) < commands.index(order_cnf_summary)
    assert commands.index(order_cnf_summary) < commands.index(tooling_preflight)
