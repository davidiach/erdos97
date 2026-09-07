"""Repository-facing tests for immutable research packet publication."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parent


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "erdos97_bridge_publication_candidate", ROOT / "check_candidate.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_replay(*arguments):
    process = subprocess.run(
        [sys.executable, str(ROOT / "replay.py"), *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=360,
        check=False,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    return json.loads(process.stdout)


def test_original_manifests():
    report = run_replay("--manifest-only")
    assert report["manifests"]["preserved_files"] == 41
    assert report["manifests"] == report["post_replay_manifests"]


@pytest.mark.parametrize("packet", ["rank-one", "rank-two", "closure-audit"])
def test_archived_unit_suites(packet):
    report = run_replay("--unit-only", "--packet", packet)
    assert len(report["runs"]) == 1
    assert report["runs"][0]["commands"][0]["returncode"] == 0


@pytest.mark.artifact
@pytest.mark.parametrize(
    "packet", ["chain-conic", "rank-one", "rank-two", "closure-audit"]
)
def test_exact_report_regeneration(packet):
    report = run_replay("--report-only", "--packet", packet)
    assert report["runs"][0]["compared_reports"]


def test_nine_orbit_fixed_pattern_status():
    module = load_checker()
    report = module.verify(module.ROWS)
    assert report == json.loads((ROOT / "nine-orbit-candidate.json").read_text())
    assert report["survives_earlier_filters"] is True
    assert len(report["right_angle_containment_obstructions"]) == 6
    assert [7, 15, 16, 18, 0] in report["right_angle_containment_obstructions"]
    assert report["euclidean_realization_claimed"] is False
    assert report["all_pattern_exhaustion_claimed"] is False


def test_existing_repository_checker_accepts_containment_certificates():
    source = (
        ROOT.parents[1]
        / "incoming/c3-own-side-eight-orbits-2026-09-05/c3_eight_check.py"
    )
    if not source.exists():
        pytest.skip(
            "Isolated packet export lacks the pinned existing repository checker"
        )
    result = run_replay("--candidate-only", "--require-primary")
    assert result["candidate"]["existing_checker_replay"]["certificates"] == 6


@pytest.mark.parametrize("value", [9, -1, True, 1.0, "1"])
def test_candidate_rejects_invalid_target(value):
    module = load_checker()
    rows = [row[:] for row in module.ROWS]
    rows[0][0] = value
    with pytest.raises(ValueError):
        module.verify(rows)


def test_candidate_rejects_duplicate_supplier():
    module = load_checker()
    rows = [row[:] for row in module.ROWS]
    rows[0][2] = rows[0][0]
    with pytest.raises(ValueError):
        module.verify(rows)


def test_candidate_change_is_not_accepted_as_stored():
    module = load_checker()
    rows = [row[:] for row in module.ROWS]
    rows[6][1] = 1
    assert module.verify(rows) != json.loads(
        (ROOT / "nine-orbit-candidate.json").read_text()
    )
