from __future__ import annotations

import json
from pathlib import Path

from erdos97.search import verify_json

ROOT = Path(__file__).resolve().parents[1]


def test_c13_order_survivor_run_records_order_metadata() -> None:
    path = ROOT / "data" / "runs" / "C13_sidon_order_survivor_slsqp_m1e-4_seed20260502.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["source_pattern_name"] == "C13_sidon_1_2_4_10"
    assert data["cyclic_order"] == [5, 0, 10, 8, 9, 7, 4, 6, 2, 11, 12, 3, 1]
    assert data["mode"] == "polar_slsqp_m1e-04"
    assert data["eq_rms"] > 0.6

    diagnostics = verify_json(str(path), tol=1e-8, min_margin=1e-8)
    assert diagnostics["ok_at_tol"] is False
    assert diagnostics["validation_errors"] == []


def test_c19_order_survivor_run_records_order_metadata() -> None:
    path = ROOT / "data" / "runs" / "C19_skew_order_survivor_slsqp_m1e-4_seed20260502.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["source_pattern_name"] == "C19_skew"
    assert data["cyclic_order"] == [
        18,
        10,
        7,
        17,
        6,
        3,
        5,
        9,
        14,
        11,
        2,
        13,
        4,
        16,
        12,
        15,
        0,
        8,
        1,
    ]
    assert data["mode"] == "polar_slsqp_m1e-04"
    assert data["eq_rms"] > 0.9

    diagnostics = verify_json(str(path), tol=1e-8, min_margin=1e-8)
    assert diagnostics["ok_at_tol"] is False
    assert diagnostics["validation_errors"] == []
