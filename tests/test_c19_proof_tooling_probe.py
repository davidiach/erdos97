from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from scripts.probe_c19_proof_tooling import c19_cnf_summary_payload, tooling_probe


ROOT = Path(__file__).resolve().parents[1]


def test_probe_reports_missing_toolchain_groups_with_mocked_lookup() -> None:
    def fake_which(name: str) -> str | None:
        return {"kissat": "/opt/kissat/bin/kissat"}.get(name)

    def fake_find_spec(name: str) -> object | None:
        return SimpleNamespace(name=name) if name == "z3" else None

    payload = tooling_probe(which=fake_which, find_spec=fake_find_spec)

    assert payload["status"] == "C19_PROOF_TOOLING_ENVIRONMENT_DIAGNOSTIC_ONLY"
    assert not payload["claim_scope"]["changes_mathematical_status"]
    assert payload["commands"]["kissat"]["found"]
    assert not payload["commands"]["drat-trim"]["found"]
    assert payload["python_modules"]["z3"]["found"]
    assert not payload["python_modules"]["pysat"]["found"]
    replay = payload["requirements"]["c19_solver_independent_replay"]
    assert replay["ready"] is False
    assert replay["found_solver_commands"] == ["kissat"]
    assert replay["missing_groups"] == ["proof_checker"]


def test_probe_reports_ready_with_mocked_solver_and_checker() -> None:
    def fake_which(name: str) -> str | None:
        return {
            "cadical": "C:/sat/cadical.exe",
            "lrat-check": "C:/sat/lrat-check.exe",
        }.get(name)

    payload = tooling_probe(which=fake_which, find_spec=lambda _name: None)

    replay = payload["requirements"]["c19_solver_independent_replay"]
    assert replay["ready"] is True
    assert replay["found_solver_commands"] == ["cadical"]
    assert replay["found_checker_commands"] == ["lrat-check"]
    assert replay["missing_groups"] == []


def test_probe_treats_missing_dotted_module_parent_as_not_found() -> None:
    def raising_find_spec(_name: str) -> object | None:
        raise ModuleNotFoundError("missing parent")

    payload = tooling_probe(
        module_names=("missing_parent.child",),
        find_spec=raising_find_spec,
    )

    assert payload["python_modules"]["missing_parent.child"] == {"found": False}


def test_probe_cli_json_is_claim_neutral() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/probe_c19_proof_tooling.py", "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["status"] == "C19_PROOF_TOOLING_ENVIRONMENT_DIAGNOSTIC_ONLY"
    assert payload["claim_scope"] == {
        "changes_mathematical_status": False,
        "counterexample_claimed": False,
        "proves_c19_order_cnf_unsat": False,
        "proves_erdos97": False,
    }
    assert payload["c19_cnf_summary"] == {"checked": False}


def test_probe_can_check_c19_cnf_summary() -> None:
    payload = tooling_probe(check_c19_cnf_summary=True)

    assert payload["c19_cnf_summary"] == {
        "checked": True,
        "ok": True,
        "artifact": "reports/c19_kalmanson_order_cnf_summary.json",
        "variables": 171,
        "clauses": 13813,
        "dimacs_sha256": (
            "dd4b8f429fea232bf09ff878342d7a28f4e9b6e743c99cd1b48f681d0f9ec450"
        ),
    }


def test_probe_reports_bad_c19_cnf_summary_without_traceback(tmp_path: Path) -> None:
    bad_artifact = tmp_path / "bad_c19_summary.json"
    bad_artifact.write_text("{}\n", encoding="utf-8")

    payload = c19_cnf_summary_payload(bad_artifact)

    assert payload["checked"] is True
    assert payload["ok"] is False
    assert payload["artifact"] == str(bad_artifact)
    assert "does not match regenerated payload" in payload["error"]


def test_probe_cli_requirement_failure_is_explicit() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/probe_c19_proof_tooling.py",
            "--require-command",
            "erdos97-definitely-missing-proof-tool",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 1
    assert "required proof tooling is not available" in result.stderr
    payload = json.loads(result.stdout)
    assert payload["requirements"]["missing_commands"] == [
        "erdos97-definitely-missing-proof-tool"
    ]


def test_probe_cli_dotted_missing_module_still_emits_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/probe_c19_proof_tooling.py",
            "--module",
            "erdos97_definitely_missing_parent.child",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["python_modules"]["erdos97_definitely_missing_parent.child"] == {
        "found": False
    }


def test_probe_cli_c19_cnf_summary_preflight() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/probe_c19_proof_tooling.py",
            "--check-c19-cnf-summary",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["c19_cnf_summary"]["ok"] is True
    assert payload["c19_cnf_summary"]["artifact"] == (
        "reports/c19_kalmanson_order_cnf_summary.json"
    )


def test_probe_cli_bad_c19_cnf_summary_fails_with_json(tmp_path: Path) -> None:
    bad_artifact = tmp_path / "bad_c19_summary.json"
    bad_artifact.write_text("{}\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/probe_c19_proof_tooling.py",
            "--check-c19-cnf-summary",
            "--c19-cnf-summary-artifact",
            str(bad_artifact),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 1
    assert "C19 CNF summary check failed" in result.stderr
    payload = json.loads(result.stdout)
    assert payload["c19_cnf_summary"]["ok"] is False
