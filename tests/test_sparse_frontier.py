from __future__ import annotations

from erdos97.search import built_in_patterns
from erdos97.sparse_frontier import sparse_frontier_summary, sparse_row_profiles


FRONTIER_PATTERNS = (
    "C19_skew",
    "C13_sidon_1_2_4_10",
    "C25_sidon_2_5_9_14",
    "C29_sidon_1_3_7_15",
)


def test_frontier_patterns_have_trivial_empty_radius_choice() -> None:
    patterns = built_in_patterns()

    for name in FRONTIER_PATTERNS:
        summary = sparse_frontier_summary(name, patterns[name].S)
        assert summary["trivial_empty_radius_choice_exists"] is True
        assert summary["all_rows_have_uncovered_consecutive_pair"] is True
        assert summary["order_free_blocked_rows"] == []


def test_c13_sidon_all_witness_pairs_have_at_most_one_source() -> None:
    pattern = built_in_patterns()["C13_sidon_1_2_4_10"]

    summary = sparse_frontier_summary(pattern.name, pattern.S)

    assert summary["all_pair_source_count_histogram"] == {"0": 26, "1": 52}
    assert summary["consecutive_pair_source_count_histogram"] == {"0": 13, "1": 26}


def test_sparse_row_profile_records_uncovered_consecutive_pairs() -> None:
    pattern = built_in_patterns()["C19_skew"]

    row0 = sparse_row_profiles(pattern.S)[0]

    assert row0.center == 0
    assert [item.pair for item in row0.consecutive_pairs] == [(5, 9), (9, 11), (11, 16)]
    assert [item.pair for item in row0.uncovered_consecutive_pairs] == [(5, 9), (9, 11)]
