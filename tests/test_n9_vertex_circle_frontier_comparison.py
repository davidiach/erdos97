from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_frontier_comparison import (
    assert_expected_frontier_comparison,
    frontier_comparison_summary,
)
from scripts.compare_n9_vertex_circle_frontier import (
    artifact_check_errors,
    summary_json_payload,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n9_vertex_circle_frontier_comparison.json"


def test_n9_vertex_circle_frontier_comparison_artifact_counts() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_expected_frontier_comparison(payload)
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    embedding_hits = {
        result["pattern"]: result["exact_core_embedding_hits"]
        for result in payload["exact_core_embedding_results"]
    }
    assert embedding_hits == {"P18_parity_balanced": 0, "C19_skew": 0}
    pattern_results = {
        result["pattern"]: result for result in payload["pattern_vertex_circle_results"]
    }
    assert pattern_results["P18_parity_balanced"]["status"] == "strict_cycle"
    assert pattern_results["P18_parity_balanced"]["core_size"] == 6
    assert pattern_results["C19_skew"]["status"] == "passes_vertex_circle_filter"


def test_n9_vertex_circle_frontier_comparison_summary_json_payload() -> None:
    payload = frontier_comparison_summary()

    summary = summary_json_payload(payload)

    assert "exact_core_embedding_results" not in summary
    assert "pattern_vertex_circle_results" not in summary
    assert summary["type"] == payload["type"]
    assert summary["scope"] == payload["scope"]
    embedding_summary = {
        record["pattern"]: record for record in summary["exact_core_embedding_summary"]
    }
    assert embedding_summary["P18_parity_balanced"]["exact_core_embedding_hits"] == 0
    assert embedding_summary["C19_skew"]["exact_core_embedding_hits"] == 0
    assert "hits" not in embedding_summary["P18_parity_balanced"]
    pattern_summary = {
        record["pattern"]: record for record in summary["pattern_vertex_circle_summary"]
    }
    assert pattern_summary["P18_parity_balanced"]["status"] == "strict_cycle"
    assert pattern_summary["P18_parity_balanced"]["core_size"] == 6
    assert pattern_summary["C19_skew"]["status"] == "passes_vertex_circle_filter"
    assert "cycle_steps" not in pattern_summary["P18_parity_balanced"]
    assert "core_rows" not in pattern_summary["P18_parity_balanced"]


def test_n9_vertex_circle_frontier_comparison_check_rejects_mismatch(
    tmp_path: Path,
) -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    tampered = dict(payload)
    tampered["trust"] = "BROKEN"
    artifact = tmp_path / "tampered.json"
    artifact.write_text(json.dumps(tampered), encoding="utf-8")

    errors = artifact_check_errors(payload, artifact)

    assert len(errors) == 1
    assert "generated payload differs from" in errors[0]
    assert str(artifact) in errors[0]


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_n9_vertex_circle_frontier_comparison_script_check_is_current() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/compare_n9_vertex_circle_frontier.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert_expected_frontier_comparison(payload)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_n9_vertex_circle_frontier_comparison_cli_summary_json() -> None:
    payload = frontier_comparison_summary()
    result = subprocess.run(
        [
            sys.executable,
            "scripts/compare_n9_vertex_circle_frontier.py",
            "--check",
            "--assert-expected",
            "--summary-json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    expected = json.loads(json.dumps(summary_json_payload(payload), sort_keys=True))
    assert json.loads(result.stdout) == expected
