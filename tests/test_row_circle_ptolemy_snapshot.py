from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_c19_row_circle_ptolemy_snapshot_records_active_set() -> None:
    artifact = json.loads(
        (ROOT / "data" / "certificates" / "c19_row_circle_ptolemy_active_set.json")
        .read_text(encoding="utf-8")
    )

    assert artifact["type"] == "row_circle_ptolemy_nlp_solution_snapshot_v1"
    assert artifact["trust"] == "NUMERICAL_NONLINEAR_DIAGNOSTIC"
    assert artifact["case"] == "C19_skew:vertex_circle_survivor"
    assert artifact["status"] == "ROW_CIRCLE_PTOLEMY_NLP_NUMERICAL_OBSTRUCTION"
    assert artifact["gamma"] < -0.001
    assert artifact["row_ptolemy_max_abs_residual"] < 1e-12
    assert artifact["counts"] == {
        "distance_classes": 114,
        "linear_rows": 3086,
        "ptolemy_rows": 3876,
        "row_ptolemy_rows": 19,
        "tight_linear_rows": 22,
        "tight_ptolemy_rows": 74,
    }
    assert len(artifact["distance_classes"]) == 114
    assert len(artifact["tight_linear_rows"]) == 22
    assert len(artifact["tight_ptolemy_rows"]) == 74
    assert len(artifact["row_ptolemy_rows"]) == 19
    assert artifact["multipliers"]["type"] == "scipy_slsqp_multipliers_v1"
    assert artifact["multipliers"]["total_count"] == 6982
    assert artifact["multipliers"]["linear_nonzero_count"] == 19
    assert artifact["multipliers"]["ptolemy_nonzero_count"] == 57
    assert artifact["multipliers"]["row_ptolemy_nonzero_count"] == 19
    assert any("not exact certificates" in note for note in artifact["notes"])


def test_row_circle_ptolemy_snapshot_cli_import_smoke() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/dump_row_circle_ptolemy_snapshot.py", "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "active-set snapshot" in result.stdout
