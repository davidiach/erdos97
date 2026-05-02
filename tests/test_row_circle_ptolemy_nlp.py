from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_row_circle_ptolemy_artifact_records_sparse_order_diagnostics() -> None:
    artifact = json.loads(
        (ROOT / "data" / "certificates" / "row_circle_ptolemy_nlp_sparse_orders.json")
        .read_text(encoding="utf-8")
    )

    assert artifact["type"] == "row_circle_ptolemy_nlp_registered_sparse_order_sweep_v1"
    assert artifact["trust"] == "NUMERICAL_NONLINEAR_DIAGNOSTIC"
    by_case = {row["case"]: row for row in artifact["cases"]}
    assert set(by_case) == {
        "C13_sidon_1_2_4_10:sample_full_filter_survivor",
        "C19_skew:vertex_circle_survivor",
    }

    c13 = by_case["C13_sidon_1_2_4_10:sample_full_filter_survivor"]
    assert c13["status"] == "ROW_CIRCLE_PTOLEMY_NLP_FAILED"
    assert c13["obstructed"] is None
    assert c13["row_ptolemy_equality_count"] == 13

    c19 = by_case["C19_skew:vertex_circle_survivor"]
    assert c19["status"] == "ROW_CIRCLE_PTOLEMY_NLP_NUMERICAL_OBSTRUCTION"
    assert c19["obstructed"] is True
    assert c19["row_ptolemy_equality_count"] == 19
    assert c19["max_margin"] < -0.001
    assert c19["row_ptolemy_max_abs_residual"] < 1e-12


def test_row_circle_ptolemy_cli_import_smoke() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_row_circle_ptolemy_nlp.py", "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "row-circle Ptolemy" in result.stdout
