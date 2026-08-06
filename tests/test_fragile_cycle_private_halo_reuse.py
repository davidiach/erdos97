from __future__ import annotations

from erdos97.fragile_cycle_private_halo_reuse import (
    assert_expected_payload,
    minimum_retained_pair_load,
    pair_budget_obstruction,
    private_halo_reuse_payload,
)


def test_pair_budget_obstructs_too_many_selected_private_halos() -> None:
    assert minimum_retained_pair_load(3) == 15
    assert minimum_retained_pair_load(4) == 12
    assert minimum_retained_pair_load(5) == 10

    four = pair_budget_obstruction(n=11, selected_private_count=3)
    assert four == {
        "n": 11,
        "selected_private_count": 3,
        "nonretained_row_count": 7,
        "nonretained_pair_load": 42,
        "minimum_retained_pair_load": 15,
        "required_pair_load": 57,
        "available_pair_capacity": 56,
        "capacity_deficit": 1,
        "obstructed": True,
    }

    five = pair_budget_obstruction(n=12, selected_private_count=4)
    assert five["required_pair_load"] == 60
    assert five["available_pair_capacity"] == 56
    assert five["capacity_deficit"] == 4
    assert five["obstructed"] is True


def test_guardrails_preserve_selected_private_roles() -> None:
    payload = private_halo_reuse_payload()
    assert_expected_payload(payload)
    four, five = payload["guardrails"]

    assert four["retained_private_halos"] == [7, 8, 9, 10]
    assert four["selected_private_halos"] == [8]
    assert four["reused_retained_private_halos"] == [7, 9, 10]
    assert four["nonempty_proper_seed_count"] == 2046

    assert five["retained_private_halos"] == [7, 8, 9, 10, 11]
    assert five["selected_private_halos"] == [9, 10]
    assert five["reused_retained_private_halos"] == [7, 8, 11]
    assert five["nonempty_proper_seed_count"] == 4094

    for guardrail in (four, five):
        assert guardrail["essential_cover_ok"] is True
        assert guardrail["pair_crossing_ok"] is True
        assert guardrail["all_nonempty_proper_seeds_have_good_survivor"] is True
        assert guardrail["contains_equilateral_hinge"] is True
        assert guardrail["contains_kalmanson_splice"] is True


def test_pair_budget_bounds_are_not_overstated_as_sharp() -> None:
    payload = private_halo_reuse_payload()
    assert "not claimed sharp" in payload["limitations"][3]
    assert payload["pair_budget_lemma"]["four_halos_maximum_selected_private"] == 2
    assert payload["pair_budget_lemma"]["five_halos_maximum_selected_private"] == 3
