from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ptolemy_order_nlp_artifact_records_registered_survivors() -> None:
    artifact = json.loads(
        (ROOT / "data" / "certificates" / "ptolemy_order_nlp_survivors.json")
        .read_text(encoding="utf-8")
    )

    assert artifact["type"] == "ptolemy_order_nlp_registered_survivor_sweep_v1"
    assert artifact["trust"] == "NUMERICAL_NONLINEAR_DIAGNOSTIC"
    by_case = {row["case"]: row for row in artifact["cases"]}
    assert set(by_case) == {
        "C13_sidon_1_2_4_10:sample_full_filter_survivor",
        "C19_skew:vertex_circle_survivor",
    }

    c13 = by_case["C13_sidon_1_2_4_10:sample_full_filter_survivor"]
    assert c13["status"] == "PASS_PTOLEMY_ORDER_NLP_RELAXATION"
    assert c13["ptolemy_inequality_count"] == 715
    assert c13["max_margin"] > 0.001

    c19 = by_case["C19_skew:vertex_circle_survivor"]
    assert c19["status"] == "PASS_PTOLEMY_ORDER_NLP_RELAXATION"
    assert c19["ptolemy_inequality_count"] == 3876
    assert c19["max_margin"] > 0.0009

def test_ptolemy_order_nlp_cli_import_smoke() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_ptolemy_order_nlp.py", "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Ptolemy-strengthened" in result.stdout
