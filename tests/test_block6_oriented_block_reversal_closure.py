from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_block6_oriented_block_reversal_closure import (
    FIRST_FORWARD,
    FIRST_REVERSED,
    OUT,
    SECOND_FORWARD,
    SECOND_REVERSED,
    assert_expected,
    check_artifact,
    normalized_cyclic_reverse,
    oriented_shuffle_orders,
    payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_oriented_shuffle_families_have_expected_endpoints() -> None:
    ff = oriented_shuffle_orders(
        first_tail=FIRST_FORWARD, second_tail=SECOND_FORWARD
    )
    rr = oriented_shuffle_orders(
        first_tail=FIRST_REVERSED, second_tail=SECOND_REVERSED
    )

    assert len(ff) == 462
    assert len(rr) == 462
    assert ff[0]["order"] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    assert rr[0]["order"] == [0, 5, 4, 3, 2, 1, 11, 10, 9, 8, 7, 6]
    assert normalized_cyclic_reverse(ff[0]["order"]) == rr[461]["order"]


def test_oriented_block_reversal_payload_counts() -> None:
    data = payload()

    assert data["summary"]["total_oriented_order_count"] == 1848
    assert data["summary"]["direct_source_order_count"] == 924
    assert data["summary"]["reversal_dual_order_count"] == 924
    assert data["summary"]["combined_closed_order_count"] == 1848
    assert data["summary"]["method_counts"]["vertex_circle_quotient_total"] == 1816
    assert (
        data["summary"]["method_counts"]["kalmanson_after_vertex_circle_escape_total"]
        == 32
    )


def test_oriented_block_reversal_artifact_replays() -> None:
    data = check_artifact()

    assert_expected(data)
    assert "not arbitrary cyclic-order closure" in data["claim_scope"]
    assert "not a counterexample" in data["claim_scope"]


def test_oriented_block_reversal_artifact_is_compact() -> None:
    data = json.loads(OUT.read_text(encoding="utf-8"))

    assert len(data["orientation_family_crosswalk"]) == 4
    assert len(data["reversal_pair_samples"]["forward_forward_to_reversed_reversed"]) == 7
    assert len(data["reversal_pair_samples"]["forward_reversed_to_reversed_forward"]) == 7
    assert "source_order_records" not in data


def test_oriented_block_reversal_cli_check() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_oriented_block_reversal_closure.py",
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
