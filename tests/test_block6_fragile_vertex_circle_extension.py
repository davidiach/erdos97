from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_block6_fragile_vertex_circle_extension import (
    assert_expected,
    audit_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_block6_pruned_audit_matches_expected() -> None:
    payload = audit_payload(include_terminal=False)

    assert_expected(payload, include_terminal=False)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert "not a proof" in payload["claim_scope"]
    assert payload["pruned_search"]["solutions"] == 0
    assert payload["pruned_search"]["vc_prunes"] == {
        "self_edge": 645,
        "strict_cycle": 768,
    }


def test_block6_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_fragile_vertex_circle_extension.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
