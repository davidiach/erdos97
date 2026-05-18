from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_n9_all_five_rich_support_obstruction import (  # noqa: E402
    DEFAULT_OUT,
    ORDER,
    all_support_options,
    build_pair_catalog,
    build_payload,
    row_pair_rejection,
    run_support_search,
)


def test_n9_all_five_support_options_are_generator_independent() -> None:
    options = all_support_options()

    assert len(options) == 9
    assert [len(center_options) for center_options in options] == [56] * 9
    assert options[0][0] == (1, 2, 3, 4, 5)
    assert options[0][-1] == (4, 5, 6, 7, 8)
    assert all(0 not in support for support in options[0])


def test_n9_all_five_pair_filter_rejection_reasons() -> None:
    assert (
        row_pair_rejection(
            ORDER,
            0,
            (1, 2, 3, 4, 5),
            1,
            (0, 2, 3, 4, 5),
        )
        == "row_pair_cap"
    )
    assert (
        row_pair_rejection(
            ORDER,
            0,
            (1, 2, 3, 4, 5),
            1,
            (0, 2, 3, 6, 7),
        )
        == "two_overlap_crossing"
    )
    assert (
        row_pair_rejection(
            ORDER,
            0,
            (1, 2, 3, 4, 5),
            1,
            (0, 2, 6, 7, 8),
        )
        is None
    )


def test_n9_all_five_pair_catalog_counts() -> None:
    catalog = build_pair_catalog(ORDER, all_support_options())

    assert catalog["center_pair_count"] == 36
    assert catalog["candidate_count_total"] == 112896
    assert catalog["compatible_count_total"] == 17640
    assert catalog["compatible_count_distribution"] == {
        "140": 9,
        "440": 9,
        "640": 9,
        "740": 9,
    }
    assert catalog["rejection_counts"] == {
        "row_pair_cap": 70056,
        "two_overlap_crossing": 25200,
    }


def test_n9_all_five_search_closes_without_vertex_circle_replay() -> None:
    search = run_support_search(ORDER, all_support_options())

    assert search.nodes_visited == 136
    assert search.complete_assignments == 0
    assert search.dead_end_count == 116
    assert search.max_depth == 2
    assert not search.aborted
    assert search.center_choice_counts == {0: 1, 1: 20}
    assert search.node_depth_counts == {0: 56, 1: 80}
    assert search.first_dead_end is not None
    assert search.first_dead_end["next_center"] == 6


def test_n9_all_five_payload_matches_checked_artifact() -> None:
    payload = build_payload()

    assert payload["summary"]["no_pair_filter_survivors"] is True
    assert payload == json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
