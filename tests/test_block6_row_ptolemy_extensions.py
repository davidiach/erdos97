from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_block6_row_ptolemy_extensions import audit


ROOT = Path(__file__).resolve().parents[1]


def test_two_block_audit_finds_product_cancellation_survivor() -> None:
    payload = audit(blocks=2, max_extensions=3, max_nodes=100_000)

    assert payload["extensions_examined"] == 3
    assert payload["extensions_killed_by_row_ptolemy_product_cancellation"] == 2
    assert payload["survivor_found"] is True
    assert payload["hit_node_limit"] is False

    survivor = payload["survivor"]
    assert isinstance(survivor, dict)
    assert survivor["extension_index"] == 3
    assert survivor["row_ptolemy_product_cancellation_count"] == 0
    assert survivor["rows"]["0"] == [1, 2, 3, 4]
    assert survivor["rows"]["3"] == [0, 2, 4, 5]
    assert survivor["rows"]["6"] == [7, 8, 9, 10]
    assert survivor["rows"]["9"] == [6, 8, 10, 11]


def test_block6_row_ptolemy_cli_assert_survivor() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_row_ptolemy_extensions.py",
            "--blocks",
            "2",
            "--max-extensions",
            "3",
            "--assert-survivor",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "survivor found: True" in result.stdout
    assert "OK: survivor expectation verified" in result.stdout
