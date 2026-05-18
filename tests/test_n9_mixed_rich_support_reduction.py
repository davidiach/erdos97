from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_n9_mixed_rich_support_reduction import (  # noqa: E402
    ORDER,
    all_support_options,
    build_payload,
    prepare_support_catalogue,
    row_pair_rejection_code,
    support_mask,
)


def test_n9_mixed_support_options_cover_four_and_five_sets() -> None:
    options = all_support_options()

    assert len(options) == 9
    assert [len(center_options) for center_options in options] == [126] * 9
    assert options[0][0] == (1, 2, 3, 4)
    assert options[0][69] == (5, 6, 7, 8)
    assert options[0][70] == (1, 2, 3, 4, 5)
    assert options[0][-1] == (4, 5, 6, 7, 8)


def test_n9_mixed_pair_filter_rejection_codes() -> None:
    assert (
        row_pair_rejection_code(
            ORDER,
            0,
            support_mask((1, 2, 3, 4)),
            1,
            support_mask((0, 2, 3, 4)),
        )
        == 1
    )
    assert (
        row_pair_rejection_code(
            ORDER,
            0,
            support_mask((1, 2, 3, 4)),
            1,
            support_mask((0, 2, 3, 5)),
        )
        == 2
    )
    assert (
        row_pair_rejection_code(
            ORDER,
            0,
            support_mask((1, 2, 3, 4)),
            1,
            support_mask((0, 2, 6, 7)),
        )
        == 0
    )


def test_n9_mixed_pair_catalog_counts() -> None:
    catalogue = prepare_support_catalogue()
    pair_catalog = catalogue.pair_catalog

    assert pair_catalog["center_pair_count"] == 36
    assert pair_catalog["candidate_count_total"] == 571536
    assert pair_catalog["compatible_count_total"] == 206640
    assert pair_catalog["compatible_count_distribution"] == {
        "3360": 9,
        "5400": 9,
        "6760": 9,
        "7440": 9,
    }
    assert pair_catalog["rejection_counts"] == {
        "row_pair_cap": 193536,
        "two_overlap_crossing": 171360,
    }


def test_n9_mixed_payload_debug_limit_is_explicit() -> None:
    payload = build_payload(max_nodes=100)
    summary = payload["summary"]

    assert summary["debug_max_nodes"] == 100
    assert summary["search_aborted"] is True
    assert summary["search_nodes_visited"] == 100
    assert summary["search_complete_assignments"] == 0
