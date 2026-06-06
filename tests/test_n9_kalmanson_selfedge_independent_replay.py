from __future__ import annotations

import json
import subprocess
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_n9_kalmanson_selfedge_independent_replay.py"
ARTIFACT = ROOT / "data" / "certificates" / "n9_kalmanson_selfedge.json"


def load_replay_module() -> ModuleType:
    spec = spec_from_file_location("n9_kalmanson_selfedge_independent_replay", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_independent_replay_payload_checks_certificate() -> None:
    module = load_replay_module()
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    summary = module.audit_certificate_payload(payload)

    assert summary["status"] == "ok"
    assert summary["certificates_checked"] == 184
    assert summary["unique_assignments_checked"] == 184
    assert summary["self_edge_failures"] == 0
    assert summary["digest_matches"] is True
    assert summary["first_self_edge"]["quadruple"] == [0, 1, 2, 7]
    assert summary["first_self_edge"]["inequality"] == "K1"


def test_independent_replay_summary_json_payload_omits_example() -> None:
    module = load_replay_module()
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    summary = module.summary_json_payload(module.audit_certificate_payload(payload))

    assert summary["status"] == "ok"
    assert summary["certificates_checked"] == 184
    assert summary["unique_assignments_checked"] == 184
    assert summary["digest_matches"] is True
    assert "first_self_edge" not in summary


def test_independent_replay_rejects_mutated_self_edge() -> None:
    module = load_replay_module()
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    payload["certificates"][0]["self_edge"]["inequality"] = "K2"

    try:
        module.audit_certificate_payload(payload)
    except module.AuditError as exc:
        assert "digest" in str(exc) or "stored lhs pairs" in str(exc)
    else:
        raise AssertionError("mutated certificate unexpectedly passed")


def test_independent_replay_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--check",
            "--assert-expected",
            "--json",
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "ok"
    assert payload["certificates_checked"] == 184
    assert payload["unique_assignments_checked"] == 184


def test_independent_replay_cli_summary_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--check",
            "--assert-expected",
            "--summary-json",
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "ok"
    assert payload["certificates_checked"] == 184
    assert payload["unique_assignments_checked"] == 184
    assert "first_self_edge" not in payload


def test_independent_replay_cli_rejects_json_and_summary_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--check",
            "--json",
            "--summary-json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "not allowed with argument --json" in result.stderr
