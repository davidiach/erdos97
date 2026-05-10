from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from erdos97.bootstrap_t12_activation_requirements import (
    DEFAULT_ARTIFACT,
    KIND_CONNECTOR,
    KIND_STRICT,
    assert_expected_payload,
    build_t12_activation_requirements_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def _requirements(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    out = {}
    for record in payload["records"]:
        for requirement in record["requirements"]:
            out[requirement["requirement_id"]] = requirement
    return out


def test_activation_requirement_counts_and_scope() -> None:
    payload = build_t12_activation_requirements_payload()
    assert_expected_payload(payload)
    assert payload["status"] == "BOOTSTRAP_T12_ACTIVATION_REQUIREMENTS_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "does not prove that the missing rows are forced" in claim_scope
    assert "does not prove n=9" in claim_scope


def test_activation_requirements_separate_connectors_from_strict_edges() -> None:
    payload = build_t12_activation_requirements_payload()
    requirements = _requirements(payload)
    assert requirements["81:3:connector:2:0"]["kind"] == KIND_CONNECTOR
    assert requirements["81:3:connector:2:0"]["required_witnesses"] == [0, 1]
    assert requirements["151:7:strict:0"]["kind"] == KIND_STRICT
    assert requirements["151:7:strict:0"]["required_witnesses"] == [0, 1, 6]


def test_activation_requirements_keep_closure_negative_control() -> None:
    payload = build_t12_activation_requirements_payload()
    requirements = _requirements(payload)
    strict_151_7 = requirements["151:7:strict:0"]
    assert strict_151_7["missing_from_bootstrap_core"] == [6]
    assert strict_151_7["closure_sufficient_count"] == 0
    exposed = [
        item
        for item in strict_151_7["closure_evaluations"]
        if item["row_exposed_in_closure"]
    ]
    assert len(exposed) == 1
    assert exposed[0]["available_witnesses"] == [0, 1, 4]
    assert exposed[0]["missing_required_witnesses"] == [6]
    assert exposed[0]["status"] == "PARTIAL"


def test_activation_requirements_distinguish_outside_pair_supports() -> None:
    payload = build_t12_activation_requirements_payload()
    requirements = _requirements(payload)
    connector_151_6 = requirements["151:6:connector:2:0"]
    support_statuses = {
        tuple(item["support"]): item["status"]
        for item in connector_151_6["support_evaluations"]
    }
    assert support_statuses[(3, 5)] == "PARTIAL"
    assert support_statuses[(3, 8)] == "SUFFICIENT"
    assert support_statuses[(5, 8)] == "SUFFICIENT"


def test_activation_requirements_artifact_matches_generator() -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == build_t12_activation_requirements_payload()


def test_activation_requirement_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_activation_requirements.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    payload = json.loads(result.stdout)
    assert payload["summary"]["requirement_count"] == 7


def test_activation_requirement_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "bootstrap_t12_activation_requirements.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_activation_requirements.py",
            "--write",
            "--assert-expected",
            "--artifact",
            str(out),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_activation_requirements.py",
            "--check",
            "--assert-expected",
            "--artifact",
            str(out),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
