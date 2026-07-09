from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.run_artifact_audit import (
    AUDIT_COMMANDS,
    AUDIT_PREFLIGHT_COMMANDS,
    AuditCommand,
    build_summary,
    command_text,
    list_commands_payload,
    run_audit_command,
    run_verify_commands,
    shard_commands,
    sha256_bytes,
)


ROOT = Path(__file__).resolve().parents[1]


def _verify_artifacts_make_command() -> str:
    make = shutil.which("make")
    if make:
        dry_run = subprocess.run(
            [make, "-n", "verify-artifacts"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        command_lines = [
            line.strip()
            for line in dry_run.stdout.splitlines()
            if line.strip() and not line.startswith("make[")
        ]
        assert len(command_lines) == 1
        command = command_lines[0]
        if command.startswith(".venv/bin/python "):
            command = "python " + command.split(" ", 1)[1]
        return command

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    lines = makefile.splitlines()
    for index, line in enumerate(lines):
        if line == "verify-artifacts:":
            command = lines[index + 1].strip()
            assert command.startswith("$(PYTHON) ")
            return "python " + command.split(" ", 1)[1]
    raise AssertionError("verify-artifacts target not found")


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


def test_run_audit_command_resolves_python_to_current_interpreter(tmp_path: Path) -> None:
    command = AuditCommand(
        ident="python_alias",
        command=("python", "-c", "import sys; print(sys.executable)"),
        claim_scope="test command only",
    )

    record = run_audit_command(command, tmp_path)

    assert record["command"] == "python -c import sys; print(sys.executable)"
    assert record["exit_code"] == 0
    assert (tmp_path / record["stdout_path"]).read_text(encoding="utf-8").strip() == sys.executable


def test_run_verify_commands_resolves_python_to_current_interpreter(capfd) -> None:
    command = AuditCommand(
        ident="python_alias",
        command=("python", "-c", "import sys; print(sys.executable)"),
        claim_scope="test command only",
    )

    exit_code = run_verify_commands([command])

    assert exit_code == 0
    captured = capfd.readouterr()
    assert sys.executable in captured.out


def test_run_verify_commands_stops_on_first_failure(capfd) -> None:
    commands = [
        AuditCommand(
            ident="fail",
            command=("python", "-c", "import sys; sys.exit(7)"),
            claim_scope="test command only",
        ),
        AuditCommand(
            ident="skip",
            command=("python", "-c", "print('should not run')"),
            claim_scope="test command only",
        ),
    ]

    exit_code = run_verify_commands(commands)

    assert exit_code == 7
    captured = capfd.readouterr()
    assert "fail" in captured.out
    assert "skip" not in captured.out
    assert "should not run" not in captured.out


def test_build_summary_runs_preflight_and_audit_commands(tmp_path: Path) -> None:
    preflight = AuditCommand(
        ident="preflight",
        command=("python", "-c", "print('preflight')"),
        claim_scope="test preflight only",
    )
    audit = AuditCommand(
        ident="audit",
        command=("python", "-c", "print('audit')"),
        claim_scope="test audit only",
    )

    summary = build_summary(tmp_path, [audit], preflight_commands=[preflight])

    assert summary["verified"] is True
    assert summary["preflight_command_count"] == 1
    assert summary["audit_command_count"] == 1
    assert summary["command_count"] == 2
    assert [record["id"] for record in summary["commands"]] == ["preflight", "audit"]


def test_audit_commands_cover_generated_artifact_check_commands() -> None:
    metadata = yaml.safe_load((ROOT / "metadata/generated_artifacts.yaml").read_text(encoding="utf-8"))
    audit_commands = {command_text(command.command) for command in AUDIT_COMMANDS}

    missing = []
    for artifact in metadata["artifacts"]:
        check_command = artifact.get("check_command")
        if check_command and check_command not in audit_commands:
            missing.append(f"{artifact['id']}: {check_command}")

    assert missing == []


def test_audit_commands_cover_verify_artifacts_make_target() -> None:
    command = _verify_artifacts_make_command()
    assert command == "python scripts/run_artifact_audit.py --verify-only"


def test_list_commands_payload_is_claim_neutral() -> None:
    payload = list_commands_payload(AUDIT_COMMANDS)

    assert payload["type"] == "erdos97_artifact_audit_command_list_v1"
    assert payload["preflight_command_count"] == len(AUDIT_PREFLIGHT_COMMANDS)
    assert payload["audit_command_count"] == len(AUDIT_COMMANDS)
    assert payload["registered_audit_command_count"] == len(AUDIT_COMMANDS)
    assert payload["command_count"] == len(AUDIT_PREFLIGHT_COMMANDS) + len(AUDIT_COMMANDS)
    assert payload["shard"]["index"] == 0
    assert payload["shard"]["count"] == 1
    assert "does not run checks" in payload["claim_scope"]
    assert "prove Erdos Problem #97" in payload["claim_scope"]
    assert payload["commands"][0] == {
        "id": AUDIT_PREFLIGHT_COMMANDS[0].ident,
        "command": command_text(AUDIT_PREFLIGHT_COMMANDS[0].command),
        "claim_scope": AUDIT_PREFLIGHT_COMMANDS[0].claim_scope,
    }
    assert payload["commands"][len(AUDIT_PREFLIGHT_COMMANDS)] == {
        "id": AUDIT_COMMANDS[0].ident,
        "command": command_text(AUDIT_COMMANDS[0].command),
        "claim_scope": AUDIT_COMMANDS[0].claim_scope,
    }


def test_run_artifact_audit_cli_lists_commands_without_running() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_artifact_audit.py", "--list-commands"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["type"] == "erdos97_artifact_audit_command_list_v1"
    assert payload["command_count"] == len(AUDIT_PREFLIGHT_COMMANDS) + len(AUDIT_COMMANDS)
    assert payload["commands"][0]["command"] == (
        "python scripts/check_status_consistency.py --max-official-status-age-days 90"
    )
    assert payload["commands"][1]["command"] == "python scripts/check_artifact_provenance.py"
    assert "stdout_path" not in payload["commands"][0]


def test_audit_command_shards_are_disjoint_complete_and_stable() -> None:
    shards = [
        shard_commands(AUDIT_COMMANDS, shard_index=index, shard_count=8)
        for index in range(8)
    ]
    flattened = [command.ident for shard in shards for command in shard]

    assert len(flattened) == len(AUDIT_COMMANDS)
    assert len(set(flattened)) == len(AUDIT_COMMANDS)
    assert set(flattened) == {command.ident for command in AUDIT_COMMANDS}
    assert shards == [
        shard_commands(AUDIT_COMMANDS, shard_index=index, shard_count=8)
        for index in range(8)
    ]


def test_run_artifact_audit_cli_lists_only_requested_shard() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_artifact_audit.py",
            "--list-commands",
            "--shard-count",
            "8",
            "--shard-index",
            "3",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    expected = shard_commands(AUDIT_COMMANDS, shard_index=3, shard_count=8)
    assert payload["shard"]["index"] == 3
    assert payload["shard"]["count"] == 8
    assert payload["registered_audit_command_count"] == len(AUDIT_COMMANDS)
    assert payload["audit_command_count"] == len(expected)
    assert [row["id"] for row in payload["commands"][2:]] == [
        command.ident for command in expected
    ]


def test_run_artifact_audit_cli_rejects_invalid_shard() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_artifact_audit.py",
            "--list-commands",
            "--shard-count",
            "4",
            "--shard-index",
            "4",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 2
    assert "0 <= index < 4" in result.stderr


def test_audit_commands_include_registered_followup_checkers() -> None:
    ordered_command_texts = [command_text(command.command) for command in AUDIT_COMMANDS]
    command_texts = set(ordered_command_texts)

    assert (
        "python scripts/check_kalmanson_two_order_z3.py --certificate "
        "data/certificates/c19_skew_all_orders_kalmanson_z3.json --assert-unsat"
        in command_texts
    )
    assert (
        "python scripts/independent_n8_obstruction_recheck.py --check --json"
        in command_texts
    )
    assert "python scripts/check_n8_class14_certificate.py --check --json" in command_texts
    assert "python scripts/check_n8_residual_certificates.py --check --json" in command_texts
    assert (
        "python scripts/analyze_kalmanson_inverse_pair_templates.py --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/analyze_kalmanson_sparse_frontier_templates.py --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_sparse_frontier_kalmanson_escapes.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/analyze_kalmanson_inverse_pair_templates.py --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/analyze_kalmanson_sparse_frontier_templates.py --assert-expected --json"
    )
    assert (
        "python scripts/check_speculative_circulant_frontier_obstructions.py "
        "--check --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/analyze_kalmanson_sparse_frontier_templates.py --assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_sparse_frontier_kalmanson_escapes.py --check "
        "--assert-expected --json"
    )
    assert ordered_command_texts.index(
        "python scripts/check_sparse_frontier_kalmanson_escapes.py --check "
        "--assert-expected --json"
    ) < ordered_command_texts.index(
        "python scripts/check_speculative_circulant_frontier_obstructions.py "
        "--check --json"
    )
    assert (
        "python scripts/analyze_kalmanson_z3_clauses.py --assert-expected "
        "--check-artifact reports/c19_kalmanson_z3_clause_diagnostics.json"
        in command_texts
    )
    assert (
        "python scripts/export_c19_kalmanson_order_cnf.py --assert-expected "
        "--check-artifact reports/c19_kalmanson_order_cnf_summary.json"
        in command_texts
    )
    assert (
        "python scripts/probe_c19_proof_tooling.py --check-c19-cnf-summary --json"
        in command_texts
    )
    assert ordered_command_texts.index(
        "python scripts/analyze_kalmanson_z3_clauses.py --assert-expected "
        "--check-artifact reports/c19_kalmanson_z3_clause_diagnostics.json"
    ) < ordered_command_texts.index(
        "python scripts/export_c19_kalmanson_order_cnf.py --assert-expected "
        "--check-artifact reports/c19_kalmanson_order_cnf_summary.json"
    )
    assert ordered_command_texts.index(
        "python scripts/export_c19_kalmanson_order_cnf.py --assert-expected "
        "--check-artifact reports/c19_kalmanson_order_cnf_summary.json"
    ) < ordered_command_texts.index(
        "python scripts/probe_c19_proof_tooling.py --check-c19-cnf-summary --json"
    )
    assert (
        "python scripts/check_n9_base_apex_low_excess_ledgers.py --artifact "
        "data/certificates/n9_base_apex_low_excess_ledgers.json --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_escape_budget.py --artifact "
        "data/certificates/n9_base_apex_escape_budget_report.json --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_selected_baseline_escape_budget_overlay.py --artifact "
        "data/certificates/n9_selected_baseline_escape_budget_overlay.json --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_selected_baseline_d3_escape_class_crosswalk.py "
        "--artifact data/certificates/n9_selected_baseline_d3_escape_class_crosswalk.json "
        "--check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_selected_baseline_d3_vertex_circle_template_join.py "
        "--check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_d3_escape_slice.py --artifact "
        "data/certificates/n9_base_apex_d3_escape_slice.json --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_d3_escape_frontier_packet.py --artifact "
        "data/certificates/n9_base_apex_d3_escape_frontier_packet.json --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_d3_p19_incidence_capacity_pilot.py --artifact "
        "data/certificates/n9_base_apex_d3_p19_incidence_capacity_pilot.json "
        "--check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_d3_incidence_capacity_packet.py --artifact "
        "data/certificates/n9_base_apex_d3_incidence_capacity_packet.json --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_d3_p19_degree_obstruction.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_d3_p20_residue_obstruction.py --check "
        "--assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_d3_artifact_join.py --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_audit_path.py --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_low_excess_escape_ladder.py --artifact "
        "data/certificates/n9_base_apex_low_excess_escape_ladder.json --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_n9_base_apex_low_excess_escape_crosswalk.py --artifact "
        "data/certificates/n9_base_apex_low_excess_escape_crosswalk.json --check --json"
        in command_texts
    )
    assert (
        "python scripts/check_bootstrap_t12_singleton_full_neighborhood_crosswalk.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_bootstrap_t12_151_6_outside_pair_two_row_drop.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.py "
        "--check --assert-expected --json"
        in command_texts
    )
    assert (
        "python scripts/check_bootstrap_t12_151_6_outside_pair_connector_contract.py "
        "--check --assert-expected --json"
        in command_texts