from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_full_cone_dual_certificates_check() -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "check_bootstrap_t12_151_6_label4_target_sparse_full_cone_dual_certificates.py"
    result = subprocess.run(
        [sys.executable, str(script), "--check", "--json"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["miss_count"] == 3
    assert payload["distance_class_count_each"] == [28]
    assert payload["strict_row_count_each"] == [255]
    assert payload["minimum_strict_row_dot_each"] == [1, 1, 1]
    assert payload["solves_n9"] is False
    assert payload["solves_erdos97"] is False
