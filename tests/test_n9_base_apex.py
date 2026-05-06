from __future__ import annotations

import json
from pathlib import Path

from erdos97.n9_base_apex import (
    base_apex_slack,
    canonical_deficit_placement,
    capacity_deficit_forces_turn_cover,
    cyclic_base_families,
    deficit_placement_classes,
    distance_profiles,
    excess_distributions,
    guaranteed_full_bases,
    ledger_summary,
    low_excess_ledger_report,
    minimum_capacity_deficit_to_escape_turn_cover,
    minimum_escape_motif_summary,
    profile_assumption_summaries,
    profile_assumption_summary,
    profile_ledger_cases,
    profiles_by_excess,
    turn_cover_distribution_summary,
    turn_cover_diagnostic,
)


def test_n9_profile_table_matches_corrected_slack_ledger() -> None:
    rows = [(profile.excess, profile.parts) for profile in distance_profiles()]

    assert rows == [
        (0, (4, 1, 1, 1, 1)),
        (1, (4, 2, 1, 1)),
        (2, (4, 2, 2)),
        (3, (4, 3, 1)),
        (4, (5, 1, 1, 1)),
        (5, (5, 2, 1)),
        (6, (4, 4)),
        (7, (5, 3)),
        (9, (6, 1, 1)),
        (10, (6, 2)),
        (15, (7, 1)),
        (22, (8,)),
    ]


def test_n9_ledger_separates_profile_excess_from_capacity_deficit() -> None:
    assert base_apex_slack(9) == 9

    distributions = excess_distributions()
    by_excesses = {row.excesses: row for row in distributions}

    all_baseline = by_excesses[(0, 0, 0, 0, 0, 0, 0, 0, 0)]
    assert all_baseline.total_profile_excess == 0
    assert all_baseline.capacity_deficit == 9

    all_one_excess = by_excesses[(1, 1, 1, 1, 1, 1, 1, 1, 1)]
    assert all_one_excess.total_profile_excess == 9
    assert all_one_excess.capacity_deficit == 0


def test_n9_profiles_with_excess_above_budget_are_listed_but_not_distributable() -> None:
    grouped = profiles_by_excess()
    assert 10 in grouped
    assert 15 in grouped
    assert 22 in grouped

    used_values = {value for row in excess_distributions() for value in row.excesses}
    assert 10 not in used_values
    assert 15 not in used_values
    assert 22 not in used_values


def test_n9_cyclic_family_saturation_bounds_are_conservative() -> None:
    families = [
        (
            family.cyclic_length,
            family.base_count,
            family.capacity_per_base,
            family.total_capacity,
        )
        for family in cyclic_base_families()
    ]

    assert families == [
        (1, 9, 1, 9),
        (2, 9, 2, 18),
        (3, 9, 2, 18),
        (4, 9, 2, 18),
    ]

    assert guaranteed_full_bases(capacity_deficit=0, cyclic_length=2) == 9
    assert guaranteed_full_bases(capacity_deficit=4, cyclic_length=2) == 5
    assert guaranteed_full_bases(capacity_deficit=9, cyclic_length=2) == 0


def test_n9_summary_is_explicitly_nonclaiming() -> None:
    summary = ledger_summary()

    assert summary["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert summary["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert summary["base_apex_slack"] == 9
    assert "No proof of the n=9 case is claimed." in summary["notes"]


def test_full_saturation_turn_cover_has_odd_cycle_vertex_cover_size() -> None:
    diagnostic = turn_cover_diagnostic()

    assert diagnostic.turn_clauses == (
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 5),
        (5, 6),
        (6, 7),
        (7, 8),
        (8, 0),
        (0, 1),
    )
    assert diagnostic.minimum_forced_turns == 5
    assert diagnostic.forces_turn_contradiction


def test_three_length2_length3_deficits_escape_strict_turn_cover_diagnostic() -> None:
    escape = minimum_capacity_deficit_to_escape_turn_cover()

    assert escape.contradiction_threshold == 3
    assert escape.minimum_capacity_deficit == 3
    assert escape.remaining_minimum_forced_turns == 2
    assert capacity_deficit_forces_turn_cover(2)
    assert not capacity_deficit_forces_turn_cover(3)


def test_two_deficits_escape_more_conservative_turn_cover_threshold() -> None:
    escape = minimum_capacity_deficit_to_escape_turn_cover(contradiction_threshold=4)

    assert escape.minimum_capacity_deficit == 2
    assert escape.remaining_minimum_forced_turns == 3


def test_turn_cover_distribution_summary_counts_closed_profile_ledgers() -> None:
    strict_summary = turn_cover_distribution_summary()
    conservative_summary = turn_cover_distribution_summary(contradiction_threshold=4)

    assert strict_summary["distribution_count"] == 95
    assert strict_summary["forced_by_turn_cover_count"] == 65
    assert strict_summary["unresolved_by_turn_cover_count"] == 30
    assert strict_summary["capacity_deficit_counts"]["0"] == 29
    assert strict_summary["capacity_deficit_counts"]["2"] == 15

    assert conservative_summary["forced_by_turn_cover_count"] == 50
    assert conservative_summary["unresolved_by_turn_cover_count"] == 45


def test_unresolved_profile_ledgers_are_exactly_low_excess_under_strict_threshold() -> None:
    unresolved = profile_ledger_cases(forced_by_turn_cover=False)

    assert len(unresolved) == 30
    assert {case.capacity_deficit for case in unresolved} == {3, 4, 5, 6, 7, 8, 9}
    assert max(case.total_profile_excess for case in unresolved) == 6
    assert unresolved[0].excesses == (0, 0, 0, 0, 0, 0, 0, 0, 0)
    assert unresolved[0].profile_multiset == ((4, 1, 1, 1, 1),) * 9


def test_profile_assumption_summary_shows_anti_concentration_is_not_enough() -> None:
    summary = profile_assumption_summary((0, 1))

    assert summary.distribution_count == 10
    assert summary.forced_by_turn_cover_count == 3
    assert summary.unresolved_by_turn_cover_count == 7
    assert summary.minimum_total_profile_excess == 0
    assert summary.maximum_total_profile_excess == 9


def test_standard_profile_assumption_summaries_are_monotone() -> None:
    summaries = profile_assumption_summaries()

    assert [row.allowed_excesses for row in summaries] == [
        (0, 1),
        (0, 1, 2),
        (0, 1, 2, 3),
        (0, 1, 2, 3, 4, 5, 6),
    ]
    assert [row.distribution_count for row in summaries] == [10, 30, 53, 90]
    assert [row.unresolved_by_turn_cover_count for row in summaries] == [
        7,
        16,
        23,
        30,
    ]


def test_deficit_placement_canonicalization_respects_dihedral_symmetry() -> None:
    key = canonical_deficit_placement(9, [0, 2], [3])
    rotated_key = canonical_deficit_placement(9, [4, 6], [7])
    reflected_key = canonical_deficit_placement(9, [5, 7], [3])

    assert key == ((0, 2), (3,))
    assert rotated_key == key
    assert reflected_key == key


def test_strict_minimum_escape_motifs_are_classified_up_to_dihedral_symmetry() -> None:
    classes = deficit_placement_classes()

    assert len(classes) == 8
    assert sum(row.placement_count for row in classes) == 108
    assert {row.remaining_minimum_forced_turns for row in classes} == {2}
    assert [(row.spoiled_length2, row.spoiled_length3) for row in classes] == [
        ((0, 2), (3,)),
        ((0, 2), (5,)),
        ((0, 3), (1,)),
        ((0, 4), (5,)),
        ((0, 1, 3), ()),
        ((0, 1, 5), ()),
        ((0, 2, 4), ()),
        ((0, 2, 5), ()),
    ]


def test_conservative_minimum_escape_motifs_are_classified_up_to_dihedral_symmetry() -> None:
    classes = deficit_placement_classes(contradiction_threshold=4)

    assert len(classes) == 6
    assert sum(row.placement_count for row in classes) == 72
    assert {row.remaining_minimum_forced_turns for row in classes} == {3}
    assert [(row.spoiled_length2, row.spoiled_length3) for row in classes] == [
        ((0,), (1,)),
        ((0,), (3,)),
        ((0, 1), ()),
        ((0, 2), ()),
        ((0, 3), ()),
        ((0, 4), ()),
    ]


def test_minimum_escape_motif_summary_is_included_in_ledger_summary() -> None:
    summary = minimum_escape_motif_summary()
    ledger = ledger_summary()

    assert summary["relevant_deficit_count"] == 3
    assert summary["raw_escaping_placement_count"] == 108
    assert summary["dihedral_class_count"] == 8
    assert ledger["minimum_escape_motif_summary"]["strict_positive_threshold"] == summary


def test_low_excess_ledger_report_records_unresolved_counts() -> None:
    report = low_excess_ledger_report()

    assert report["schema"] == "erdos97.n9_base_apex_low_excess_ledgers.v1"
    assert report["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert report["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert report["strict_unresolved_profile_ledger_count"] == 30
    assert report["strict_unresolved_count_by_total_profile_excess"] == {
        "0": 1,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 5,
        "5": 7,
        "6": 11,
    }
    assert report["strict_unresolved_count_by_capacity_deficit"] == {
        "3": 11,
        "4": 7,
        "5": 5,
        "6": 3,
        "7": 2,
        "8": 1,
        "9": 1,
    }
    assert len(report["strict_minimum_escape_motif_classes"]) == 8
    assert len(report["conservative_minimum_escape_motif_classes"]) == 6
    assert "No proof of the n=9 case is claimed." in report["notes"]


def test_checked_low_excess_ledger_artifact_matches_generator() -> None:
    repo = Path(__file__).resolve().parents[1]
    artifact = repo / "data" / "certificates" / "n9_base_apex_low_excess_ledgers.json"

    payload = json.loads(artifact.read_text(encoding="utf-8"))

    assert payload == low_excess_ledger_report()
