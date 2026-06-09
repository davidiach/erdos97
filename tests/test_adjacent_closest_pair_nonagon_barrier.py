from __future__ import annotations

from scripts.check_adjacent_closest_pair_nonagon_barrier import (
    EXPECTED_SUMMARY,
    build_payload,
    render_markdown,
    row_pair_rejection,
    summary_payload,
    validate_payload,
)


def test_adjacent_closest_pair_nonagon_barrier_matches_expected() -> None:
    payload = build_payload()

    errors = validate_payload(payload)

    assert errors == []
    assert payload["summary"]["complete_assignment_count"] == 0
    assert payload["summary"]["final_pair_rejection_counts"] == {
        "row_pair_cap": 3120,
        "two_overlap_crossing": 2640,
    }


def test_adjacent_closest_pair_nonagon_barrier_forces_boundary_rows() -> None:
    payload = build_payload()
    summary = payload["summary"]

    assert summary["endpoint_pair_count"] == EXPECTED_SUMMARY["endpoint_pair_count"]
    assert (
        summary["endpoint_pair_union_saturation_count"]
        == summary["endpoint_pair_count"]
    )
    assert (
        summary["v2_candidate_count"]
        == summary["v2_forced_closest_pair_endpoint_count"]
    )
    assert (
        summary["v8_candidate_count"]
        == summary["v8_forced_closest_pair_endpoint_count"]
    )


def test_adjacent_closest_pair_nonagon_barrier_summary_payload() -> None:
    payload = build_payload()
    summary = summary_payload(payload, [])

    assert summary["validation_status"] == "passed"
    assert summary["endpoint_pair_count"] == 140
    assert summary["partial_frontier_count_before_final_pair"] == 5760
    assert summary["complete_assignment_count"] == 0


def test_adjacent_closest_pair_nonagon_barrier_rejects_final_pair_examples() -> None:
    payload = build_payload()
    examples = payload["first_final_rejection_examples"]

    cap_example = examples["row_pair_cap"]
    crossing_example = examples["two_overlap_crossing"]

    assert row_pair_rejection(2, cap_example["S2"], 8, cap_example["S8"]) == (
        "row_pair_cap"
    )
    assert row_pair_rejection(
        2,
        crossing_example["S2"],
        8,
        crossing_example["S8"],
    ) == "two_overlap_crossing"
    assert crossing_example["S2_cap_S8"] == [0, 1]


def test_adjacent_closest_pair_nonagon_barrier_markdown_keeps_scope() -> None:
    payload = build_payload()
    markdown = render_markdown(payload, [])

    assert "# Adjacent Closest-Pair Nonagon Barrier Check" in markdown
    assert "Complete assignments: `0`" in markdown
    assert "only the adjacent closest-pair nonagon subcase" in markdown
