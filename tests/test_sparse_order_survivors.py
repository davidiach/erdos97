from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_registered_sparse_order_survivors_match_artifact() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_sparse_order_survivors.py",
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
        (ROOT / "data" / "certificates" / "sparse_order_survivors.json")
        .read_text(encoding="utf-8")
    )

    assert artifact == payload
    by_case = {row["case"]: row for row in payload["cases"]}
    c13 = by_case["C13_sidon_1_2_4_10:sample_full_filter_survivor"]
    c19 = by_case["C19_skew:vertex_circle_survivor"]

    assert c13["survives_current_exact_filters"] is True
    assert c13["vertex_circle"]["obstructed"] is False
    assert c13["radius_propagation"]["acyclic_choice_edge_count"] == 4
    assert c19["survives_current_exact_filters"] is True
    assert c19["sparse_frontier"]["trivial_empty_radius_choice_exists"] is True
