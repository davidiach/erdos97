from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_n9_regular_tournament_kalmanson import (
    N,
    audit_regular_tournaments,
    has_strict_cycle,
    is_strongly_connected,
    strict_implication_graph,
    tails_from_selected_rows,
)


ROOT = Path(__file__).resolve().parents[1]


def test_cyclic_regular_tournament_has_kalmanson_cycle() -> None:
    rows = tuple(
        tuple((center + step) % N for step in (1, 2, 3, 4))
        for center in range(N)
    )
    tails = tails_from_selected_rows(rows)
    graph = strict_implication_graph(tails)

    assert has_strict_cycle(graph)
    assert is_strongly_connected(graph)


def test_limited_regular_tournament_audit() -> None:
    audit = audit_regular_tournaments(limit=250)

    assert audit.total_regular_tournaments == 250
    assert audit.strong_connectivity_failures == 0
    assert audit.acyclic_implication_failures == 0
    assert audit.first_strong_failure_rows is None
    assert audit.first_acyclic_failure_rows is None
    assert audit.checked_all is False


def test_regular_tournament_audit_cli_limited_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_regular_tournament_kalmanson.py",
            "--limit",
            "25",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert '"total_regular_tournaments": 25' in result.stdout
    assert '"strong_connectivity_failures": 0' in result.stdout
    assert '"acyclic_implication_failures": 0' in result.stdout
