from __future__ import annotations

import sys
from pathlib import Path

from scripts.run_artifact_audit import AUDIT_COMMANDS, AuditCommand, command_text, run_audit_command, sha256_bytes


def test_sha256_bytes_is_stable() -> None:
    assert sha256_bytes(b"erdos97\n") == "d804cace0801472174f9f279439ba930de0123adced9367f0df1dcc8dc996d4b"


def test_run_audit_command_records_metadata(tmp_path: Path) -> None:
    command = AuditCommand(
        ident="smoke",
        command=(sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'ok\\n')"),
        claim_scope="test command only",
    )

    record = run_audit_command(command, tmp_path)

    assert record["id"] == "smoke"
    assert record["exit_code"] == 0
    assert record["claim_scope"] == "test command only"
    assert record["stdout_bytes"] == len(b"ok\n")
    assert (tmp_path / record["stdout_path"]).read_bytes() == b"ok\n"
    assert (tmp_path / record["stderr_path"]).read_bytes() == b""
    assert len(record["combined_output_sha256"]) == 64


def test_audit_commands_include_registered_followup_checkers() -> None:
    command_texts = {command_text(command.command) for command in AUDIT_COMMANDS}

    assert (
        "python scripts/check_kalmanson_two_order_z3.py --certificate "
        "data/certificates/c19_skew_all_orders_kalmanson_z3.json --assert-unsat"
        in command_texts
    )
    assert (
        "python scripts/analyze_kalmanson_z3_clauses.py --assert-expected "
        "--check-artifact reports/c19_kalmanson_z3_clause_diagnostics.json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_low_excess_ledgers.py --check --json"
        in command_texts
    )
    assert "python scripts/check_n9_base_apex_escape_budget.py --check --json" in command_texts
    assert (
        "python scripts/check_n9_selected_baseline_escape_budget_overlay.py --check --json"
        in command_texts
    )
    assert "python scripts/check_n9_d3_escape_slice.py --check --json" in command_texts
