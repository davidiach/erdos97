from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_support_saturation_obstruction import (  # noqa: E402
    build_summary,
    check_expected,
    forced_turn_units_pi_over_3,
    min_vertex_cover_size_cycle,
    pair_counting_wall,
    saturation_improved_wall,
    turn_cover_contradiction,
)


def test_support_saturation_expected_summary() -> None:
    summary = build_summary()

    check_expected(summary)
    rows = {row["k"]: row for row in summary["threshold_rows"]}
    assert summary["trust"] == "LEMMA"
    assert rows[4]["pair_counting_wall_n"] == 8
    assert rows[4]["saturation_improved_min_n"] == 9
    assert rows[5]["pair_counting_wall_n"] == 12
    assert rows[5]["saturation_improved_min_n"] == 13
    assert rows[7]["cycle_vertex_cover_size_at_wall"] == 12
    assert rows[7]["forced_turn_lower_bound_units_pi_over_3"] == 24


def test_support_saturation_helpers() -> None:
    assert pair_counting_wall(4) == 8
    assert pair_counting_wall(5) == 12
    assert saturation_improved_wall(4) == 9
    assert saturation_improved_wall(5) == 13
    assert min_vertex_cover_size_cycle(8) == 4
    assert min_vertex_cover_size_cycle(9) == 5
    assert forced_turn_units_pi_over_3(8) == 8
    assert turn_cover_contradiction(8)


def test_support_saturation_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_support_saturation_obstruction.py",
            "--check",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema"] == "erdos97.support_saturation_obstruction.v1"
    assert payload["status"] == "PROVED_EQUALITY_WALL_OBSTRUCTION"
    assert payload["threshold_rows"][0]["k"] == 4
    assert payload["threshold_rows"][1]["saturation_improved_min_n"] == 13
