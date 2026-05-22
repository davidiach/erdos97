from __future__ import annotations

from erdos97.cap_cut_constraints import (
    PairRoleCount,
    cap_cut_report,
    cap_cut_terms,
    open_arc_not_containing_center,
    pair_role_counts,
    unit_chain_superadditivity_certificate,
)


def test_cap_cut_terms_match_centered_inequality() -> None:
    terms = cap_cut_terms(center=0, a=1, b=4, x=2)

    assert terms == (
        ((0, 2), +2),
        ((1, 2), -1),
        ((2, 4), -1),
        ((1, 4), +1),
        ((0, 1), -1),
        ((0, 4), -1),
    )


def test_open_arc_not_containing_center_chooses_cap_side() -> None:
    order = [0, 1, 2, 3, 4, 5]

    assert open_arc_not_containing_center(order, 1, 5, 0) == (2, 3, 4)
    assert open_arc_not_containing_center(order, 5, 1, 0) == (2, 3, 4)


def test_corrected_outer_dominant_types_respect_pair_cap() -> None:
    valid_once = PairRoleCount(pair=(0, 1), outer=1, adjacent=0, skipped=1)
    valid_twice = PairRoleCount(pair=(0, 1), outer=2, adjacent=0, skipped=0)
    invalid_total = PairRoleCount(pair=(0, 1), outer=2, adjacent=1, skipped=0)

    assert valid_once.corrected_outer_dominant_type == (1, 0)
    assert valid_twice.corrected_outer_dominant_type == (2, 0)
    assert invalid_total.pair_cap_compatible is False
    assert invalid_total.corrected_outer_dominant_type is None


def test_all_other_pentagon_has_unit_chain_obstruction() -> None:
    rows = [[j for j in range(5) if j != i] for i in range(5)]

    certificate = unit_chain_superadditivity_certificate(rows, list(range(5)))

    assert certificate.obstructed
    assert certificate.coefficient_positive_count == 0
    assert certificate.strict_row_count == 5


def test_pair_role_counts_expose_outer_dominance() -> None:
    rows = [[j for j in range(5) if j != i] for i in range(5)]

    counts = pair_role_counts(rows, list(range(5)))
    outer_dominant = [row for row in counts if row.outer_dominant]

    assert outer_dominant
    assert all(
        row.corrected_outer_dominant_type in {(1, 0), (2, 0)}
        or not row.pair_cap_compatible
        for row in outer_dominant
    )


def test_cap_cut_report_is_scoped_research_packet() -> None:
    rows = [[j for j in range(5) if j != i] for i in range(5)]

    report = cap_cut_report(rows, list(range(5)), include_cap_cuts=False)

    assert report["schema"] == "erdos97.cap_cut_constraints.v1"
    assert report["trust"] == "RESEARCH_PACKET_LOCAL_NECESSARY_CONDITIONS"
    assert "not a proof" in str(report["claim_scope"])
    assert report["unit_chain_superadditivity"]["obstructed"] is True
