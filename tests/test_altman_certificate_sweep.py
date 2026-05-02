from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_altman_certificate_sweep_expectations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/sweep_altman_linear_certificates.py",
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
        (ROOT / "data" / "certificates" / "altman_linear_certificate_sweep.json")
        .read_text(encoding="utf-8")
    )
    assert artifact == payload
    by_case = {row["case"]: row for row in payload["cases"]}

    assert by_case["C13_sidon_1_2_4_10:natural"]["obstructed"] is True
    assert by_case["C25_sidon_2_5_9_14:natural"]["obstructed"] is True
    assert by_case["C29_sidon_1_3_7_15:natural"]["obstructed"] is True
    assert (
        by_case["C19_skew:vertex_circle_survivor"]["status"]
        == "NO_EXACT_ALTMAN_LINEAR_CERTIFICATE_FOUND"
    )
