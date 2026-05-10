from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_block6_fragile_sixth_row_survivors import (
    assert_expected,
    survivor_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_block6_sixth_row_survivor_catalog_matches_expected() -> None:
    payload = survivor_payload()

    assert_expected(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert "not a proof" in payload["claim_scope"]
    assert payload["totals"]["clean_fifth_rows"] == 166
    assert payload["totals"]["clean_fifth_rows_with_clean_sixth"] == 166
    assert payload["totals"]["unique_clean_six_row_states"] == 6047
    assert payload["totals"]["clean_center_pairs"] == 28
    assert payload["totals"]["clean_center_pair_block_swap_orbits"] == 16
    assert payload["clean_by_center_pair"]["4,5"] == 28
    assert payload["clean_by_center_pair"]["2,8"] == 1074
    assert payload["clean_by_center_pair_orbit"]["4,5|10,11"] == 56
    assert payload["clean_by_center_pair_orbit"]["2,8"] == 1074
    low_support_forms = payload["low_support_row_content_forms"]
    assert low_support_forms["4,5"]["clean_states"] == 28
    assert low_support_forms["4,5"]["all_disjoint_pool_edges_present"] is True
    assert low_support_forms["10,11"]["clean_states"] == 28
    assert low_support_forms["10,11"]["all_disjoint_pool_edges_present"] is True
    assert low_support_forms["4,5"]["same_block_pair_counts"] == {
        "0,3|0,1": 14,
        "0,3|0,4": 14,
    }
    seventh_audit = payload["low_support_seventh_extension_audit"]
    assert seventh_audit["clean_six_states"] == 56
    assert seventh_audit["clean_six_states_with_clean_seventh"] == 56
    assert seventh_audit["ordered_legal_seventh_rows"] == 5590
    assert seventh_audit["ordered_clean_seventh_rows"] == 2252
    assert seventh_audit["ordered_self_edge_seventh_rows"] == 1560
    assert seventh_audit["ordered_strict_cycle_seventh_rows"] == 1778
    assert seventh_audit["unique_clean_seven_states"] == 2252
    assert seventh_audit["by_center_pair"]["4,5"]["seventh_status_counts"] == {
        "ok": 1126,
        "self_edge": 780,
        "strict_cycle": 889,
    }
    assert seventh_audit["by_center_pair"]["10,11"]["by_seventh_center"]["2"] == {
        "ok": 362,
        "self_edge": 120,
        "strict_cycle": 229,
    }
    eighth_audit = payload["low_support_eighth_extension_audit"]
    assert eighth_audit["clean_seven_states"] == 2252
    assert eighth_audit["clean_seven_states_with_clean_eighth"] == 2240
    assert eighth_audit["terminal_clean_seven_states"] == 12
    assert eighth_audit["ordered_legal_eighth_rows"] == 97982
    assert eighth_audit["ordered_clean_eighth_rows"] == 31636
    assert eighth_audit["ordered_self_edge_eighth_rows"] == 30272
    assert eighth_audit["ordered_strict_cycle_eighth_rows"] == 36074
    assert eighth_audit["unique_clean_eight_states"] == 15740
    assert eighth_audit["by_seven_center_triple"]["4,5,11"] == {
        "clean_seven_states": 155,
        "clean_seven_states_with_clean_eighth": 152,
        "eighth_status_counts": {
            "ok": 1624,
            "self_edge": 1907,
            "strict_cycle": 1947,
        },
    }
    terminal_classification = payload[
        "low_support_terminal_seven_state_classification"
    ]
    assert terminal_classification["terminal_clean_seven_states"] == 12
    assert terminal_classification["block_swap_orbits"] == 6
    assert terminal_classification["block_swap_orbit_sizes"] == {"2": 6}
    assert terminal_classification["row_content_profile_counts"] == {
        (
            "same_u=4,same_i=0,1,1,same_d=1,1,2,2|"
            "opposite_u=5,opposite_i=0,0,1,opposite_d=1,1,1,1,2"
        ): 4,
        (
            "same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        ): 8,
    }
    assert terminal_classification["eighth_status_split_counts"] == {
        "legal=9;self_edge=4;strict_cycle=5": 2,
        "legal=9;self_edge=5;strict_cycle=4": 2,
        "legal=9;self_edge=7;strict_cycle=2": 4,
        "legal=11;self_edge=2;strict_cycle=9": 2,
        "legal=19;self_edge=10;strict_cycle=9": 2,
    }
    assert terminal_classification["block_swap_orbit_representatives"][0] == {
        "representative": [
            {"center": 2, "row": [0, 1, 6, 11]},
            {"center": 10, "row": [0, 4, 6, 9]},
            {"center": 11, "row": [3, 5, 6, 7]},
        ],
        "block_swap_member": [
            {"center": 4, "row": [0, 3, 6, 10]},
            {"center": 5, "row": [0, 1, 9, 11]},
            {"center": 8, "row": [0, 5, 6, 7]},
        ],
        "legal_eighth_rows": 9,
        "eighth_status_counts": {
            "ok": 0,
            "self_edge": 7,
            "strict_cycle": 2,
        },
        "row_content_profile": (
            "same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        ),
    }
    profile_audit = payload["low_support_profile_terminality_audit"]
    assert profile_audit["profile_only_terminality_holds"] is False
    assert profile_audit["clean_seven_states"] == 2252
    assert profile_audit["non_two_two_clean_seven_states"] == 192
    assert profile_audit["non_two_two_terminal_clean_seven_states"] == 0
    assert profile_audit["two_two_clean_seven_states"] == 2060
    assert profile_audit["two_two_profile_classes"] == 6
    assert profile_audit["terminal_profile_classes"] == 2
    assert profile_audit["terminal_profiles_with_extendable_states"] == 2
    assert profile_audit["profile_counts"][
        (
            "same_u=4,same_i=0,1,1,same_d=1,1,2,2|"
            "opposite_u=5,opposite_i=0,0,1,opposite_d=1,1,1,1,2"
        )
    ] == {
        "clean_two_two_seven_states": 320,
        "terminal": 4,
        "extendable": 316,
    }
    assert profile_audit["profile_counts"][
        (
            "same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        )
    ] == {
        "clean_two_two_seven_states": 1230,
        "terminal": 8,
        "extendable": 1222,
    }
    assert profile_audit["first_non_two_two_example"] == [
        {"center": 2, "row": [0, 1, 3, 7]},
        {"center": 4, "row": [0, 3, 6, 9]},
        {"center": 5, "row": [0, 4, 8, 11]},
    ]
    terminal_center_audit = payload["low_support_terminal_eighth_center_audit"]
    assert terminal_center_audit["terminal_clean_seven_states"] == 12
    assert terminal_center_audit["block_swap_orbits"] == 6
    assert terminal_center_audit["aggregate_by_eighth_center"] == {
        "1": {"ok": 0, "self_edge": 7, "strict_cycle": 20},
        "2": {"ok": 0, "self_edge": 14, "strict_cycle": 8},
        "4": {"ok": 0, "self_edge": 12, "strict_cycle": 3},
        "5": {"ok": 0, "self_edge": 2, "strict_cycle": 0},
        "7": {"ok": 0, "self_edge": 7, "strict_cycle": 20},
        "8": {"ok": 0, "self_edge": 14, "strict_cycle": 8},
        "10": {"ok": 0, "self_edge": 12, "strict_cycle": 3},
        "11": {"ok": 0, "self_edge": 2, "strict_cycle": 0},
    }
    assert terminal_center_audit["center_obstruction_profile_counts"] == {
        "self_only_centers=0;strict_only_centers=3;mixed_centers=1": 2,
        "self_only_centers=1;strict_only_centers=0;mixed_centers=4": 2,
        "self_only_centers=1;strict_only_centers=1;mixed_centers=2": 2,
        "self_only_centers=1;strict_only_centers=3;mixed_centers=1": 2,
        "self_only_centers=3;strict_only_centers=1;mixed_centers=0": 4,
    }
    assert terminal_center_audit["block_swap_orbit_representatives"][0][
        "representative_by_eighth_center"
    ] == {
        "1": {"ok": 0, "self_edge": 2, "strict_cycle": 0},
        "4": {"ok": 0, "self_edge": 2, "strict_cycle": 0},
        "7": {"ok": 0, "self_edge": 0, "strict_cycle": 2},
        "8": {"ok": 0, "self_edge": 3, "strict_cycle": 0},
    }
    assert payload["first_clean_sixth_example"] == {
        "fifth": {"center": 1, "row": [0, 2, 6, 7]},
        "sixth": {"center": 2, "row": [0, 1, 3, 8]},
    }


def test_block6_sixth_row_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_fragile_sixth_row_survivors.py",
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
