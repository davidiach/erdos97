from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts import n9_vertex_circle_minimal_cores


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n9_vertex_circle_minimal_cores.json"


def test_n9_vertex_circle_minimal_core_summary_counts() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["schema"] == "erdos97.n9_vertex_circle_minimal_cores.v1"
    assert payload["trust"] == "INDEPENDENT_FINITE_CASE_DIAGNOSTIC_NO_GLOBAL_CLAIM"
    assert payload["frontier_systems"] == 184
    assert payload["frontier_systems_covered_by_a_minimal_core"] == 184
    assert payload["coverage_complete"] is True
    assert payload["distinct_minimal_cores"] == 219
    assert payload["minimal_core_size_counts"] == {
        "3": 105,
        "4": 106,
        "5": 7,
        "6": 1,
    }
    assert payload["minimal_core_status_counts"] == {
        "self_edge": 36,
        "strict_cycle": 183,
    }
    assert payload["isolated_recheck_mismatches"] == 0


def _patch_minimal_core_runner(monkeypatch) -> None:
    frontier = [object() for _ in range(184)]
    monkeypatch.setattr(
        n9_vertex_circle_minimal_cores.rec,
        "enumerate_frontier",
        lambda: frontier,
    )
    monkeypatch.setattr(
        n9_vertex_circle_minimal_cores,
        "minimal_cores",
        lambda assign: [{0}],
    )
    monkeypatch.setattr(
        n9_vertex_circle_minimal_cores,
        "canon_core",
        lambda assign, centers: ((0, 1, 2, 3, 4),),
    )
    monkeypatch.setattr(
        n9_vertex_circle_minimal_cores,
        "status_of_subset",
        lambda assign, centers: "self_edge",
    )
    monkeypatch.setattr(
        n9_vertex_circle_minimal_cores,
        "core_status_isolated",
        lambda rows: "self_edge",
    )
    monkeypatch.setattr(n9_vertex_circle_minimal_cores, "EXPECTED_SUMMARY", {})


def test_n9_vertex_circle_minimal_cores_json_does_not_write_by_default(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    _patch_minimal_core_runner(monkeypatch)
    out = tmp_path / "minimal_cores.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "n9_vertex_circle_minimal_cores.py",
            "--json",
            "--out",
            str(out),
        ],
    )

    result = n9_vertex_circle_minimal_cores.main()
    captured = capsys.readouterr()

    assert result == 0
    assert captured.err == ""
    assert not out.exists()
    payload = json.loads(captured.out)
    assert payload["schema"] == "erdos97.n9_vertex_circle_minimal_cores.v1"


def test_n9_vertex_circle_minimal_cores_write_is_explicit(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    _patch_minimal_core_runner(monkeypatch)
    out = tmp_path / "minimal_cores.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "n9_vertex_circle_minimal_cores.py",
            "--write",
            "--json",
            "--out",
            str(out),
        ],
    )

    result = n9_vertex_circle_minimal_cores.main()
    captured = capsys.readouterr()

    assert result == 0
    assert captured.err == ""
    assert out.exists()
    stored = json.loads(out.read_text(encoding="utf-8"))
    printed = json.loads(captured.out)
    assert stored["schema"] == "erdos97.n9_vertex_circle_minimal_cores.v1"
    assert printed["schema"] == stored["schema"]
