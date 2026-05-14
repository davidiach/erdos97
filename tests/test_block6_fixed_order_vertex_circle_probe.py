from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_block6_fixed_order_vertex_circle_probe import (
    OUT,
    assert_expected,
    payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_block6_fixed_order_vertex_circle_probe_payload() -> None:
    data = payload()

    assert_expected(data)
    assert data["summary"]["closed_order_count"] == 4
    assert (
        data["summary"]["non_natural_first_extensions_outside_natural_generator"]
        == 3
    )


def test_block6_fixed_order_vertex_circle_probe_artifact() -> None:
    data = json.loads(OUT.read_text(encoding="utf-8"))

    assert_expected(data)
    assert data["summary"]["vc_prunes"] == {
        "self_edge": 1390,
        "strict_cycle": 1726,
    }


def test_block6_fixed_order_vertex_circle_probe_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_fixed_order_vertex_circle_probe.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
