from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_n12_rich_support_determinant import (  # noqa: E402
    SCHEMA,
    STATUS,
    build_summary,
    check_expected,
    cycle_adjacent,
    is_square,
    pair_capacity,
    tight_size_five_gram,
)


def test_n12_rich_support_determinant_expected_summary() -> None:
    summary = build_summary()

    check_expected(summary)
    assert summary["schema"] == SCHEMA
    assert summary["status"] == STATUS
    assert summary["trust"] == "LEMMA"
    assert summary["counting_bound_is_tight"] is True
    assert summary["forced_column_sums"] == [5] * 12
    assert summary["determinant"] == 2_592_000
    assert summary["is_square"] is False
    assert "does not prove n=12" in str(summary["claim_scope"])


def test_n12_rich_support_determinant_gram_shape() -> None:
    gram = tight_size_five_gram()

    assert gram[0] == [5, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1]
    assert all(row[index] == 5 for index, row in enumerate(gram))
    assert pair_capacity(0, 1, 12) == 1
    assert pair_capacity(0, 11, 12) == 1
    assert pair_capacity(0, 2, 12) == 2
    assert cycle_adjacent(0, 11, 12)
    assert not is_square(2_592_000)


def test_n12_rich_support_determinant_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n12_rich_support_determinant.py",
            "--check",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema"] == SCHEMA
    assert payload["status"] == STATUS
    assert payload["determinant_factorization"] == {"2": 8, "3": 4, "5": 3}
    assert payload["contradiction"] is True
