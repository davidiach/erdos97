from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_registered_metric_order_lp_survivors_match_artifact() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_metric_order_lp.py",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    artifact = json.loads(
        (ROOT / "data" / "certificates" / "metric_order_lp_survivors.json")
        .read_text(encoding="utf-8")
    )

    assert artifact == payload
    by_case = {row["case"]: row for row in payload["cases"]}
    c13 = by_case["C13_sidon_1_2_4_10:sample_full_filter_survivor"]
    c19 = by_case["C19_skew:vertex_circle_survivor"]

    assert c13["status"] == "PASS_METRIC_ORDER_LP_RELAXATION"
    assert c13["triangle_inequality_count"] == 858
    assert c13["max_margin"] > 0.002
    assert c19["status"] == "PASS_METRIC_ORDER_LP_RELAXATION"
    assert c19["triangle_inequality_count"] == 2907
    assert c19["max_margin"] > 0.001
