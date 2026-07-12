from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.reduce_row_circle_multipliers import resolve_output_path

ROOT = Path(__file__).resolve().parents[1]


def test_posix_tmp_output_is_mapped_to_windows_temp() -> None:
    resolved = resolve_output_path(
        "/tmp/c19_multiplier_reduction.json",
        os_name="nt",
        temp_dir="C:/Users/test/AppData/Local/Temp",
    )

    assert resolved.as_posix().endswith(
        "Users/test/AppData/Local/Temp/c19_multiplier_reduction.json"
    )


def test_posix_tmp_output_is_unchanged_on_posix() -> None:
    assert resolve_output_path(
        "/tmp/c19_multiplier_reduction.json",
        os_name="posix",
    ) == Path("/tmp/c19_multiplier_reduction.json")


def test_c19_multiplier_reduction_records_duplicate_cancellations() -> None:
    payload = json.loads(
        (ROOT / "data" / "certificates" / "c19_row_circle_multiplier_reduction.json")
        .read_text(encoding="utf-8")
    )

    assert payload["type"] == "row_circle_ptolemy_multiplier_reduction_v1"
    assert payload["trust"] == "NUMERICAL_NONLINEAR_DIAGNOSTIC"
    assert payload["case"] == "C19_skew:vertex_circle_survivor"
    assert payload["row_global_duplicate_count"] == 19
    assert payload["unmatched_rows"] == []
    assert payload["max_abs_original_row_multiplier"] > 1e16
    assert payload["max_abs_original_global_multiplier"] > 1e16
    assert payload["max_abs_combined_multiplier"] <= 25
    assert len(payload["reductions"]) == 19


def test_row_circle_multiplier_reduction_cli_import_smoke() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/reduce_row_circle_multipliers.py", "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Reduce duplicate" in result.stdout
