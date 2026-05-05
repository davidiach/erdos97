from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
C19_Z3_CERTIFICATE = ROOT / "data" / "certificates" / "c19_skew_all_orders_kalmanson_z3.json"


def test_c19_kalmanson_z3_certificate_shape() -> None:
    payload = json.loads(C19_Z3_CERTIFICATE.read_text(encoding="utf-8"))

    assert payload["type"] == "kalmanson_two_order_z3_refinement_v1"
    assert payload["trust"] == "SMT_EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN"
    assert payload["status"] == "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION"
    assert payload["pattern"] == {
        "circulant_offsets": [-8, -3, 5, 9],
        "n": 19,
        "name": "C19_skew",
    }
    assert payload["solver_result"] == "unsat"
    assert payload["iterations"] == 142
    assert payload["forbidden_clause_count"] == 7981
    assert len(payload["forbidden_order_pairs"]) == 7981
    assert "does not prove Erdos Problem #97" in payload["semantics"]


def test_c19_kalmanson_z3_certificate_replays_unsat() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_kalmanson_two_order_z3.py",
            "--certificate",
            str(C19_Z3_CERTIFICATE),
            "--assert-unsat",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION" in result.stdout
