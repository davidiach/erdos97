from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_rigid_n15_shortest_side_grid import (  # noqa: E402
    DEFAULT_ARTIFACT,
    EXPECTED,
    SCHEMA,
    STATUS,
    TRUST,
    build_report,
    check_artifact,
    checkerboard_records,
    endpoint_count_records,
)


def test_endpoint_capacity_cases_are_complete() -> None:
    rows = endpoint_count_records()
    assert len(rows) == 4
    assert sum(row["status"] == "count_contradiction" for row in rows) == 3
    assert [
        (row["k_A"], row["k_B"], row["capacity_slack"])
        for row in rows
        if row["status"] == "checkerboard"
    ] == [(2, 2, 0)]


def test_checkerboard_vectors_cancel_in_both_orbits() -> None:
    rows = checkerboard_records()
    assert len(rows) == 2
    for row in rows:
        first, second = row["strict_vectors"]
        assert first == [-entry for entry in second]
        assert row["sum"] == [0, 0, 0, 0]


def test_report_scope_and_checked_artifact() -> None:
    report = build_report()
    assert report["schema"] == SCHEMA
    assert report["status"] == STATUS
    assert report["trust"] == TRUST
    assert report["summary"] == EXPECTED
    check_artifact(report, ROOT / DEFAULT_ARTIFACT)


def test_artifact_mismatch_is_rejected(tmp_path: Path) -> None:
    artifact = tmp_path / "wrong.json"
    artifact.write_text(json.dumps({"schema": SCHEMA}), encoding="utf-8")
    with pytest.raises(AssertionError, match="does not match"):
        check_artifact(build_report(), artifact)


def test_cli_checks_the_stored_artifact() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_rigid_n15_shortest_side_grid.py",
            "--artifact",
            str(DEFAULT_ARTIFACT),
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["schema"] == SCHEMA
    assert payload["summary"] == EXPECTED
