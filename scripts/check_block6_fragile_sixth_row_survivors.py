#!/usr/bin/env python3
"""Catalog block-6 low-support survivor and terminal-pocket structure."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_block6_fragile_vertex_circle_extension import (  # noqa: E402
    N,
    _add_row,
    _initial_state,
    _indegree_ok,
    _options,
    _pair_cap_ok,
    _paircross_ok,
    _partial_vertex_circle_status,
    _remove_row,
    _valid_options,
)
from erdos97.incidence_filters import chords_cross_in_order, normalize_chord  # noqa: E402

STATUSES = ("ok", "self_edge", "strict_cycle")
EXPECTED_TOTALS = {
    "clean_fifth_rows": 166,
    "clean_fifth_block_swap_orbits": 83,
    "ordered_legal_sixth_rows_after_clean_fifth": 29844,
    "ordered_clean_sixth_rows": 12094,
    "ordered_self_edge_sixth_rows": 8108,
    "ordered_strict_cycle_sixth_rows": 9642,
    "clean_fifth_rows_with_clean_sixth": 166,
    "unique_clean_six_row_states": 6047,
    "unique_clean_six_row_block_swap_orbits": 3056,
    "clean_center_pairs": 28,
    "clean_center_pair_block_swap_orbits": 16,
}
EXPECTED_CLEAN_SIX_ORBIT_SIZES = {"1": 65, "2": 2991}
EXPECTED_CLEAN_BY_CENTER_PAIR = {
    "1,2": 350,
    "1,4": 98,
    "1,5": 126,
    "1,7": 256,
    "1,8": 508,
    "1,10": 69,
    "1,11": 105,
    "2,4": 182,
    "2,5": 238,
    "2,7": 508,
    "2,8": 1074,
    "2,10": 176,
    "2,11": 325,
    "4,5": 28,
    "4,7": 69,
    "4,8": 176,
    "4,10": 36,
    "4,11": 71,
    "5,7": 105,
    "5,8": 325,
    "5,10": 71,
    "5,11": 129,
    "7,8": 350,
    "7,10": 98,
    "7,11": 126,
    "8,10": 182,
    "8,11": 238,
    "10,11": 28,
}
EXPECTED_CLEAN_BY_CENTER_PAIR_ORBIT = {
    "1,2|7,8": 700,
    "1,4|7,10": 196,
    "1,5|7,11": 252,
    "1,7": 256,
    "1,8|2,7": 1016,
    "1,10|4,7": 138,
    "1,11|5,7": 210,
    "2,4|8,10": 364,
    "2,5|8,11": 476,
    "2,8": 1074,
    "2,10|4,8": 352,
    "2,11|5,8": 650,
    "4,5|10,11": 56,
    "4,10": 36,
    "4,11|5,10": 142,
    "5,11": 129,
}
EXPECTED_LOW_SUPPORT_ROW_CONTENT_FORMS = {
    "4,5": {
        "clean_states": 28,
        "same_block_pair_counts": {
            "0,3|0,1": 14,
            "0,3|0,4": 14,
        },
        "opposite_pair_pool": [
            "6,7",
            "6,9",
            "6,10",
            "7,11",
            "8,11",
            "9,11",
        ],
        "opposite_pair_edge_counts": {
            "6,7|8,11": 2,
            "6,7|9,11": 2,
            "6,9|7,11": 2,
            "6,9|8,11": 2,
            "6,10|7,11": 2,
            "6,10|8,11": 2,
            "6,10|9,11": 2,
            "7,11|6,9": 2,
            "7,11|6,10": 2,
            "8,11|6,7": 2,
            "8,11|6,9": 2,
            "8,11|6,10": 2,
            "9,11|6,7": 2,
            "9,11|6,10": 2,
        },
        "ordered_disjoint_opposite_pair_edges": 14,
        "all_edges_disjoint": True,
        "all_disjoint_pool_edges_present": True,
    },
    "10,11": {
        "clean_states": 28,
        "same_block_pair_counts": {
            "6,9|6,7": 14,
            "6,9|6,10": 14,
        },
        "opposite_pair_pool": [
            "0,1",
            "0,3",
            "0,4",
            "1,5",
            "2,5",
            "3,5",
        ],
        "opposite_pair_edge_counts": {
            "0,1|2,5": 2,
            "0,1|3,5": 2,
            "0,3|1,5": 2,
            "0,3|2,5": 2,
            "0,4|1,5": 2,
            "0,4|2,5": 2,
            "0,4|3,5": 2,
            "1,5|0,3": 2,
            "1,5|0,4": 2,
            "2,5|0,1": 2,
            "2,5|0,3": 2,
            "2,5|0,4": 2,
            "3,5|0,1": 2,
            "3,5|0,4": 2,
        },
        "ordered_disjoint_opposite_pair_edges": 14,
        "all_edges_disjoint": True,
        "all_disjoint_pool_edges_present": True,
    },
}
EXPECTED_LOW_SUPPORT_SEVENTH_AUDIT = {
    "clean_six_states": 56,
    "clean_six_states_with_clean_seventh": 56,
    "ordered_legal_seventh_rows": 5590,
    "ordered_clean_seventh_rows": 2252,
    "ordered_self_edge_seventh_rows": 1560,
    "ordered_strict_cycle_seventh_rows": 1778,
    "unique_clean_seven_states": 2252,
    "by_center_pair": {
        "4,5": {
            "clean_six_states": 28,
            "clean_six_states_with_clean_seventh": 28,
            "seventh_status_counts": {
                "ok": 1126,
                "self_edge": 780,
                "strict_cycle": 889,
            },
            "by_seventh_center": {
                "1": {"ok": 160, "self_edge": 0, "strict_cycle": 216},
                "2": {"ok": 283, "self_edge": 280, "strict_cycle": 99},
                "7": {"ok": 71, "self_edge": 117, "strict_cycle": 126},
                "8": {"ok": 362, "self_edge": 120, "strict_cycle": 229},
                "10": {"ok": 95, "self_edge": 163, "strict_cycle": 124},
                "11": {"ok": 155, "self_edge": 100, "strict_cycle": 95},
            },
            "first_clean_seventh_example": {
                "six_state": [
                    {"center": 4, "row": [0, 3, 6, 9]},
                    {"center": 5, "row": [0, 4, 7, 11]},
                ],
                "seventh": {"center": 1, "row": [2, 5, 6, 7]},
            },
        },
        "10,11": {
            "clean_six_states": 28,
            "clean_six_states_with_clean_seventh": 28,
            "seventh_status_counts": {
                "ok": 1126,
                "self_edge": 780,
                "strict_cycle": 889,
            },
            "by_seventh_center": {
                "1": {"ok": 71, "self_edge": 117, "strict_cycle": 126},
                "2": {"ok": 362, "self_edge": 120, "strict_cycle": 229},
                "4": {"ok": 95, "self_edge": 163, "strict_cycle": 124},
                "5": {"ok": 155, "self_edge": 100, "strict_cycle": 95},
                "7": {"ok": 160, "self_edge": 0, "strict_cycle": 216},
                "8": {"ok": 283, "self_edge": 280, "strict_cycle": 99},
            },
            "first_clean_seventh_example": {
                "six_state": [
                    {"center": 10, "row": [0, 4, 6, 9]},
                    {"center": 11, "row": [3, 5, 6, 7]},
                ],
                "seventh": {"center": 1, "row": [0, 2, 7, 11]},
            },
        },
    },
}
EXPECTED_LOW_SUPPORT_EIGHTH_AUDIT = {
    "clean_seven_states": 2252,
    "clean_seven_states_with_clean_eighth": 2240,
    "terminal_clean_seven_states": 12,
    "ordered_legal_eighth_rows": 97982,
    "ordered_clean_eighth_rows": 31636,
    "ordered_self_edge_eighth_rows": 30272,
    "ordered_strict_cycle_eighth_rows": 36074,
    "unique_clean_eight_states": 15740,
    "by_seven_center_triple": {
        "1,4,5": {
            "clean_seven_states": 160,
            "clean_seven_states_with_clean_eighth": 160,
            "eighth_status_counts": {
                "ok": 2458,
                "self_edge": 2080,
                "strict_cycle": 2951,
            },
        },
        "1,10,11": {
            "clean_seven_states": 71,
            "clean_seven_states_with_clean_eighth": 71,
            "eighth_status_counts": {
                "ok": 880,
                "self_edge": 1341,
                "strict_cycle": 1125,
            },
        },
        "2,4,5": {
            "clean_seven_states": 283,
            "clean_seven_states_with_clean_eighth": 281,
            "eighth_status_counts": {
                "ok": 4792,
                "self_edge": 3824,
                "strict_cycle": 6583,
            },
        },
        "2,10,11": {
            "clean_seven_states": 362,
            "clean_seven_states_with_clean_eighth": 361,
            "eighth_status_counts": {
                "ok": 4544,
                "self_edge": 5072,
                "strict_cycle": 4286,
            },
        },
        "4,5,7": {
            "clean_seven_states": 71,
            "clean_seven_states_with_clean_eighth": 71,
            "eighth_status_counts": {
                "ok": 880,
                "self_edge": 1341,
                "strict_cycle": 1125,
            },
        },
        "4,5,8": {
            "clean_seven_states": 362,
            "clean_seven_states_with_clean_eighth": 361,
            "eighth_status_counts": {
                "ok": 4544,
                "self_edge": 5072,
                "strict_cycle": 4286,
            },
        },
        "4,5,10": {
            "clean_seven_states": 95,
            "clean_seven_states_with_clean_eighth": 95,
            "eighth_status_counts": {
                "ok": 1520,
                "self_edge": 912,
                "strict_cycle": 1145,
            },
        },
        "4,5,11": {
            "clean_seven_states": 155,
            "clean_seven_states_with_clean_eighth": 152,
            "eighth_status_counts": {
                "ok": 1624,
                "self_edge": 1907,
                "strict_cycle": 1947,
            },
        },
        "4,10,11": {
            "clean_seven_states": 95,
            "clean_seven_states_with_clean_eighth": 95,
            "eighth_status_counts": {
                "ok": 1520,
                "self_edge": 912,
                "strict_cycle": 1145,
            },
        },
        "5,10,11": {
            "clean_seven_states": 155,
            "clean_seven_states_with_clean_eighth": 152,
            "eighth_status_counts": {
                "ok": 1624,
                "self_edge": 1907,
                "strict_cycle": 1947,
            },
        },
        "7,10,11": {
            "clean_seven_states": 160,
            "clean_seven_states_with_clean_eighth": 160,
            "eighth_status_counts": {
                "ok": 2458,
                "self_edge": 2080,
                "strict_cycle": 2951,
            },
        },
        "8,10,11": {
            "clean_seven_states": 283,
            "clean_seven_states_with_clean_eighth": 281,
            "eighth_status_counts": {
                "ok": 4792,
                "self_edge": 3824,
                "strict_cycle": 6583,
            },
        },
    },
    "first_clean_eighth_example": {
        "seven_state": [
            {"center": 1, "row": [0, 2, 7, 11]},
            {"center": 10, "row": [0, 1, 6, 9]},
            {"center": 11, "row": [2, 5, 6, 10]},
        ],
        "eighth": {"center": 8, "row": [0, 5, 7, 9]},
    },
    "first_terminal_seven_state": {
        "seven_state": [
            {"center": 2, "row": [0, 1, 6, 11]},
            {"center": 10, "row": [0, 4, 6, 9]},
            {"center": 11, "row": [3, 5, 6, 7]},
        ],
        "legal_eighth_rows": 9,
        "eighth_status_counts": {
            "ok": 0,
            "self_edge": 7,
            "strict_cycle": 2,
        },
    },
}
EXPECTED_LOW_SUPPORT_TERMINAL_CLASSIFICATION = {
    "terminal_clean_seven_states": 12,
    "block_swap_orbits": 6,
    "block_swap_orbit_sizes": {"2": 6},
    "row_content_profile_counts": {
        (
            "same_u=4,same_i=0,1,1,same_d=1,1,2,2|"
            "opposite_u=5,opposite_i=0,0,1,opposite_d=1,1,1,1,2"
        ): 4,
        (
            "same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        ): 8,
    },
    "eighth_status_split_counts": {
        "legal=9;self_edge=4;strict_cycle=5": 2,
        "legal=9;self_edge=5;strict_cycle=4": 2,
        "legal=9;self_edge=7;strict_cycle=2": 4,
        "legal=11;self_edge=2;strict_cycle=9": 2,
        "legal=19;self_edge=10;strict_cycle=9": 2,
    },
    "block_swap_orbit_representatives": [
        {
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
        },
        {
            "representative": [
                {"center": 2, "row": [1, 5, 6, 7]},
                {"center": 4, "row": [0, 3, 6, 10]},
                {"center": 5, "row": [0, 1, 8, 11]},
            ],
            "block_swap_member": [
                {"center": 8, "row": [0, 1, 7, 11]},
                {"center": 10, "row": [0, 4, 6, 9]},
                {"center": 11, "row": [2, 5, 6, 7]},
            ],
            "legal_eighth_rows": 19,
            "eighth_status_counts": {
                "ok": 0,
                "self_edge": 10,
                "strict_cycle": 9,
            },
            "row_content_profile": (
                "same_u=4,same_i=0,1,1,same_d=1,1,2,2|"
                "opposite_u=5,opposite_i=0,0,1,opposite_d=1,1,1,1,2"
            ),
        },
        {
            "representative": [
                {"center": 2, "row": [1, 5, 6, 7]},
                {"center": 4, "row": [0, 3, 6, 10]},
                {"center": 5, "row": [0, 1, 9, 11]},
            ],
            "block_swap_member": [
                {"center": 8, "row": [0, 1, 7, 11]},
                {"center": 10, "row": [0, 4, 6, 9]},
                {"center": 11, "row": [3, 5, 6, 7]},
            ],
            "legal_eighth_rows": 9,
            "eighth_status_counts": {
                "ok": 0,
                "self_edge": 4,
                "strict_cycle": 5,
            },
            "row_content_profile": (
                "same_u=4,same_i=0,1,1,same_d=1,1,2,2|"
                "opposite_u=5,opposite_i=0,0,1,opposite_d=1,1,1,1,2"
            ),
        },
        {
            "representative": [
                {"center": 4, "row": [0, 3, 6, 10]},
                {"center": 5, "row": [0, 1, 9, 11]},
                {"center": 11, "row": [0, 5, 6, 7]},
            ],
            "block_swap_member": [
                {"center": 5, "row": [0, 1, 6, 11]},
                {"center": 10, "row": [0, 4, 6, 9]},
                {"center": 11, "row": [3, 5, 6, 7]},
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
        },
        {
            "representative": [
                {"center": 4, "row": [0, 3, 8, 11]},
                {"center": 5, "row": [0, 1, 6, 9]},
                {"center": 11, "row": [3, 5, 6, 7]},
            ],
            "block_swap_member": [
                {"center": 5, "row": [0, 1, 9, 11]},
                {"center": 10, "row": [2, 5, 6, 9]},
                {"center": 11, "row": [0, 3, 6, 7]},
            ],
            "legal_eighth_rows": 9,
            "eighth_status_counts": {
                "ok": 0,
                "self_edge": 5,
                "strict_cycle": 4,
            },
            "row_content_profile": (
                "same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
                "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
            ),
        },
        {
            "representative": [
                {"center": 4, "row": [0, 3, 9, 11]},
                {"center": 5, "row": [0, 1, 6, 10]},
                {"center": 11, "row": [3, 5, 6, 7]},
            ],
            "block_swap_member": [
                {"center": 5, "row": [0, 1, 9, 11]},
                {"center": 10, "row": [3, 5, 6, 9]},
                {"center": 11, "row": [0, 4, 6, 7]},
            ],
            "legal_eighth_rows": 11,
            "eighth_status_counts": {
                "ok": 0,
                "self_edge": 2,
                "strict_cycle": 9,
            },
            "row_content_profile": (
                "same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
                "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
            ),
        },
    ],
}
EXPECTED_LOW_SUPPORT_PROFILE_TERMINALITY_AUDIT = {
    "clean_seven_states": 2252,
    "terminal_clean_seven_states": 12,
    "non_two_two_clean_seven_states": 192,
    "non_two_two_terminal_clean_seven_states": 0,
    "two_two_clean_seven_states": 2060,
    "two_two_terminal_clean_seven_states": 12,
    "two_two_profile_classes": 6,
    "terminal_profile_classes": 2,
    "terminal_profiles_with_extendable_states": 2,
    "profile_only_terminality_holds": False,
    "non_two_two_by_center_triple": {
        "2,10,11": 68,
        "2,4,5": 28,
        "4,5,8": 68,
        "8,10,11": 28,
    },
    "profile_counts": {
        (
            "same_u=3,same_i=1,1,1,same_d=2,2,2|"
            "opposite_u=5,opposite_i=0,0,1,opposite_d=1,1,1,1,2"
        ): {
            "clean_two_two_seven_states": 40,
            "terminal": 0,
            "extendable": 40,
        },
        (
            "same_u=4,same_i=0,1,1,same_d=1,1,2,2|"
            "opposite_u=4,opposite_i=0,1,1,opposite_d=1,1,2,2"
        ): {
            "clean_two_two_seven_states": 150,
            "terminal": 0,
            "extendable": 150,
        },
        (
            "same_u=4,same_i=0,1,1,same_d=1,1,2,2|"
            "opposite_u=5,opposite_i=0,0,1,opposite_d=1,1,1,1,2"
        ): {
            "clean_two_two_seven_states": 320,
            "terminal": 4,
            "extendable": 316,
        },
        (
            "same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=4,opposite_i=0,1,1,opposite_d=1,1,2,2"
        ): {
            "clean_two_two_seven_states": 120,
            "terminal": 0,
            "extendable": 120,
        },
        (
            "same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=5,opposite_i=0,0,1,opposite_d=1,1,1,1,2"
        ): {
            "clean_two_two_seven_states": 200,
            "terminal": 0,
            "extendable": 200,
        },
        (
            "same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        ): {
            "clean_two_two_seven_states": 1230,
            "terminal": 8,
            "extendable": 1222,
        },
    },
    "first_non_two_two_example": [
        {"center": 2, "row": [0, 1, 3, 7]},
        {"center": 4, "row": [0, 3, 6, 9]},
        {"center": 5, "row": [0, 4, 8, 11]},
    ],
    "terminal_profile_extendable_examples": {
        (
            "same_u=4,same_i=0,1,1,same_d=1,1,2,2|"
            "opposite_u=5,opposite_i=0,0,1,opposite_d=1,1,1,1,2"
        ): [
            {"center": 1, "row": [3, 5, 6, 7]},
            {"center": 4, "row": [0, 3, 6, 9]},
            {"center": 5, "row": [0, 4, 8, 11]},
        ],
        (
            "same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        ): [
            {"center": 1, "row": [0, 2, 7, 11]},
            {"center": 10, "row": [0, 1, 6, 9]},
            {"center": 11, "row": [2, 5, 6, 10]},
        ],
    },
}
EXPECTED_LOW_SUPPORT_TERMINAL_EIGHTH_CENTER_AUDIT = {
    "terminal_clean_seven_states": 12,
    "block_swap_orbits": 6,
    "aggregate_by_eighth_center": {
        "1": {"ok": 0, "self_edge": 7, "strict_cycle": 20},
        "2": {"ok": 0, "self_edge": 14, "strict_cycle": 8},
        "4": {"ok": 0, "self_edge": 12, "strict_cycle": 3},
        "5": {"ok": 0, "self_edge": 2, "strict_cycle": 0},
        "7": {"ok": 0, "self_edge": 7, "strict_cycle": 20},
        "8": {"ok": 0, "self_edge": 14, "strict_cycle": 8},
        "10": {"ok": 0, "self_edge": 12, "strict_cycle": 3},
        "11": {"ok": 0, "self_edge": 2, "strict_cycle": 0},
    },
    "center_obstruction_profile_counts": {
        "self_only_centers=0;strict_only_centers=3;mixed_centers=1": 2,
        "self_only_centers=1;strict_only_centers=0;mixed_centers=4": 2,
        "self_only_centers=1;strict_only_centers=1;mixed_centers=2": 2,
        "self_only_centers=1;strict_only_centers=3;mixed_centers=1": 2,
        "self_only_centers=3;strict_only_centers=1;mixed_centers=0": 4,
    },
}
EXPECTED_LOW_SUPPORT_TRIPLE_PROFILE_TERMINALITY_AUDIT = {
    "clean_seven_states": 2252,
    "terminal_clean_seven_states": 12,
    "non_two_two_clean_seven_states": 192,
    "non_two_two_terminal_clean_seven_states": 0,
    "two_two_clean_seven_states": 2060,
    "two_two_terminal_clean_seven_states": 12,
    "two_two_triple_profile_classes": 26,
    "terminal_triple_profile_classes": 6,
    "terminal_triple_profiles_with_extendable_states": 6,
    "triple_profile_only_terminality_holds": False,
    "terminal_triple_profile_counts": {
        (
            "2,10,11|same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        ): {
            "clean_two_two_seven_states": 294,
            "terminal": 1,
            "extendable": 293,
        },
        (
            "2,4,5|same_u=4,same_i=0,1,1,same_d=1,1,2,2|"
            "opposite_u=5,opposite_i=0,0,1,opposite_d=1,1,1,1,2"
        ): {
            "clean_two_two_seven_states": 120,
            "terminal": 2,
            "extendable": 118,
        },
        (
            "4,5,8|same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        ): {
            "clean_two_two_seven_states": 294,
            "terminal": 1,
            "extendable": 293,
        },
        (
            "4,5,11|same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        ): {
            "clean_two_two_seven_states": 155,
            "terminal": 3,
            "extendable": 152,
        },
        (
            "5,10,11|same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        ): {
            "clean_two_two_seven_states": 155,
            "terminal": 3,
            "extendable": 152,
        },
        (
            "8,10,11|same_u=4,same_i=0,1,1,same_d=1,1,2,2|"
            "opposite_u=5,opposite_i=0,0,1,opposite_d=1,1,1,1,2"
        ): {
            "clean_two_two_seven_states": 120,
            "terminal": 2,
            "extendable": 118,
        },
    },
}
EXPECTED_LOW_SUPPORT_TERMINAL_EDIT_DISTANCE_AUDIT = {
    "terminal_clean_seven_states": 12,
    "terminal_triple_profile_classes": 6,
    "terminal_states_with_nearest_extendable": 12,
    "min_replacement_distribution": {"1": 12},
    "nearest_transition_count": 56,
    "nearest_extendable_count_distribution": {
        "1": 2,
        "3": 2,
        "5": 2,
        "6": 4,
        "7": 2,
    },
    "changed_row_count_distribution_for_first_nearest": {"1": 12},
    "changed_center_distribution": {
        "2": 7,
        "4": 4,
        "5": 17,
        "8": 7,
        "10": 4,
        "11": 17,
    },
    "changed_center_orbit_distribution": {
        "2,8": 14,
        "4,10": 8,
        "5,11": 34,
    },
    "changed_center_removed_added_distribution": {
        "2:11->10": 1,
        "2:5->4": 2,
        "2:6->7": 1,
        "2:6->8": 1,
        "2:6->9": 1,
        "2:7->9": 1,
        "4:10->9": 1,
        "4:8->7": 1,
        "4:9->7": 1,
        "4:9->8": 1,
        "5:1->4": 5,
        "5:11->10": 1,
        "5:6->8": 1,
        "5:6->9": 1,
        "5:9->10": 1,
        "5:9->6": 2,
        "5:9->7": 3,
        "5:9->8": 3,
        "8:0->1": 1,
        "8:0->2": 1,
        "8:0->3": 1,
        "8:1->3": 1,
        "8:11->10": 2,
        "8:5->4": 1,
        "10:2->1": 1,
        "10:3->1": 1,
        "10:3->2": 1,
        "10:4->3": 1,
        "11:0->2": 1,
        "11:0->3": 1,
        "11:3->0": 2,
        "11:3->1": 3,
        "11:3->2": 3,
        "11:3->4": 1,
        "11:5->4": 1,
        "11:7->10": 5,
    },
    "replacement_side_distribution": {"opposite_block": 42, "same_block": 14},
    "extendable_ok_center_count_distribution": {"1": 28, "2": 24, "3": 4},
    "extendable_ok_row_count_distribution": {
        "1": 18,
        "2": 16,
        "3": 4,
        "4": 4,
        "5": 4,
        "6": 2,
        "7": 2,
        "9": 2,
        "10": 2,
        "13": 2,
    },
    "opened_center_instance_count": 88,
    "opened_center_distribution": {
        "1": 4,
        "2": 23,
        "4": 15,
        "5": 2,
        "7": 4,
        "8": 23,
        "10": 15,
        "11": 2,
    },
    "opened_center_orbit_distribution": {
        "1,7": 8,
        "2,8": 46,
        "4,10": 30,
        "5,11": 4,
    },
    "opened_center_prior_status_distribution": {
        "mixed": 30,
        "not_legal": 6,
        "self_only": 30,
        "strict_only": 22,
    },
    "opened_center_prior_status_by_transition": {
        "mixed:1": 6,
        "mixed:1;not_legal:1": 4,
        "mixed:1;self_only:1": 4,
        "mixed:1;strict_only:1": 10,
        "mixed:1;strict_only:2": 2,
        "mixed:2": 2,
        "not_legal:1;self_only:1;strict_only:1": 2,
        "self_only:1": 18,
        "self_only:1;strict_only:1": 2,
        "self_only:2": 2,
        "strict_only:1": 4,
    },
    "opened_contains_replacement_label_distribution": {
        "added_opened": 4,
        "neither_opened": 48,
        "removed_opened": 4,
    },
    "changed_to_opened_center_orbit_distribution": {
        "2,8->1,7": 2,
        "2,8->2,8": 6,
        "2,8->4,10": 12,
        "2,8->5,11": 2,
        "4,10->2,8": 6,
        "4,10->4,10": 4,
        "4,10->5,11": 2,
        "5,11->1,7": 6,
        "5,11->2,8": 34,
        "5,11->4,10": 14,
    },
    "replacement_side_to_opened_prior_status_distribution": {
        "opposite_block->mixed": 18,
        "opposite_block->not_legal": 4,
        "opposite_block->self_only": 26,
        "opposite_block->strict_only": 12,
        "same_block->mixed": 12,
        "same_block->not_legal": 2,
        "same_block->self_only": 4,
        "same_block->strict_only": 10,
    },
    "not_legal_opened_instance_count": 6,
    "not_legal_opened_center_distribution": {
        "2": 3,
        "8": 3,
    },
    "not_legal_opened_center_orbit_distribution": {
        "2,8": 6,
    },
    "not_legal_opened_changed_center_orbit_distribution": {
        "2,8": 2,
        "4,10": 2,
        "5,11": 2,
    },
    "not_legal_opened_replacement_side_distribution": {
        "opposite_block": 4,
        "same_block": 2,
    },
    "not_legal_opened_paircross_profile_distribution": {
        "before_paircross=0;after_paircross=7;after_valid=7": 2,
        "before_paircross=0;after_paircross=8;after_valid=8": 4,
    },
    "not_legal_opened_before_changed_row_relation_distribution": {
        "noncrossing_two_overlap": 44,
        "three_or_more_overlap": 2,
    },
    "not_legal_opened_after_changed_row_relation_distribution": {
        "crossing_two_overlap": 10,
        "zero_or_one_overlap": 36,
    },
    "not_legal_opened_before_forbidden_overlap_removed_endpoint_distribution": {
        "noncrossing_two_overlap:contains_removed_endpoint": 44,
        "three_or_more_overlap:contains_removed_endpoint": 2,
    },
    "not_legal_opened_noncrossing_target_arc_distribution": {
        "diameter_arc": 14,
        "long_arc": 30,
    },
    "not_legal_opened_noncrossing_switch_distribution": {
        "candidate_contains_added->crossing_two_overlap": 8,
        "candidate_omits_added->zero_or_one_overlap": 36,
    },
    "not_legal_opened_noncrossing_source_target_distribution": {
        "2,10->3,5": 5,
        "2,10->3,6": 2,
        "2,5->0,11": 2,
        "2,5->1,11": 6,
        "2,8->0,11": 2,
        "2,8->1,11": 5,
        "2,8->5,6": 2,
        "2,8->5,7": 5,
        "4,8->0,9": 2,
        "4,8->9,11": 5,
        "8,11->5,6": 2,
        "8,11->5,7": 6,
    },
    "not_legal_opened_three_or_more_switch_distribution": {
        "contains_removed_endpoint->crossing_two_overlap": 2,
    },
    "not_legal_opened_crossing_creation_mechanism_distribution": {
        "noncrossing_removed_to_added_substitution": 8,
        "three_or_more_removed_endpoint_deletion": 2,
    },
    "not_legal_opened_noncrossing_substitution_arc_distribution": {
        "candidate_contains_added:opposite_source_arcs->crossing_two_overlap": 8,
    },
    "not_legal_opened_substitution_layer_arc_distribution": {
        "after_paircross:candidate_contains_added:"
        "opposite_source_arcs->crossing_two_overlap": 8,
        "after_valid:candidate_contains_added:"
        "opposite_source_arcs->crossing_two_overlap": 8,
        "all_options:candidate_contains_added:"
        "opposite_source_arcs->crossing_two_overlap": 36,
        "all_options:candidate_contains_added:"
        "same_source_arc->noncrossing_two_overlap": 60,
    },
    "not_legal_opened_opposite_arc_paircross_context_distribution": {
        "after_paircross:2,10:3,5->1,5": 3,
        "after_paircross:2,10:3,6->1,6": 1,
        "after_paircross:4,8:0,9->0,7": 1,
        "after_paircross:4,8:9,11->7,11": 3,
        "all_options:2,10:3,5->1,5": 6,
        "all_options:2,10:3,6->1,6": 6,
        "all_options:2,10:3,9->1,9": 6,
        "all_options:4,8:0,9->0,7": 6,
        "all_options:4,8:3,9->3,7": 6,
        "all_options:4,8:9,11->7,11": 6,
        "failed_paircross:2,10:3,5->1,5": 3,
        "failed_paircross:2,10:3,6->1,6": 5,
        "failed_paircross:2,10:3,9->1,9": 6,
        "failed_paircross:4,8:0,9->0,7": 5,
        "failed_paircross:4,8:3,9->3,7": 6,
        "failed_paircross:4,8:9,11->7,11": 3,
    },
    "not_legal_opened_opposite_arc_paircross_blocker_count_distribution": {
        "1": 14,
        "2": 14,
    },
    "not_legal_opened_opposite_arc_paircross_blocker_kind_distribution": {
        "noncrossing_two_overlap": 32,
        "three_or_more_overlap": 10,
    },
    "not_legal_opened_opposite_arc_paircross_blocker_role_distribution": {
        "fixed_row": 18,
        "other_added_row": 24,
    },
    "not_legal_opened_opposite_arc_paircross_blocker_center_orbit_distribution": {
        "0,6": 12,
        "3,9": 6,
        "5,11": 24,
    },
    "not_legal_opened_opposite_arc_paircross_blocker_source_target_distribution": {
        "noncrossing_two_overlap:0,8->1,3": 1,
        "noncrossing_two_overlap:0,8->2,3": 1,
        "noncrossing_two_overlap:0,8->3,4": 1,
        "noncrossing_two_overlap:2,11->4,6": 1,
        "noncrossing_two_overlap:2,11->6,7": 1,
        "noncrossing_two_overlap:2,3->0,5": 1,
        "noncrossing_two_overlap:2,3->4,5": 1,
        "noncrossing_two_overlap:2,5->0,1": 2,
        "noncrossing_two_overlap:2,5->1,11": 2,
        "noncrossing_two_overlap:2,5->1,9": 4,
        "noncrossing_two_overlap:2,6->7,9": 1,
        "noncrossing_two_overlap:2,6->8,9": 1,
        "noncrossing_two_overlap:2,6->9,10": 1,
        "noncrossing_two_overlap:2,9->6,8": 1,
        "noncrossing_two_overlap:3,8->0,2": 1,
        "noncrossing_two_overlap:5,8->0,1": 1,
        "noncrossing_two_overlap:5,8->0,10": 1,
        "noncrossing_two_overlap:8,11->3,7": 4,
        "noncrossing_two_overlap:8,11->5,7": 2,
        "noncrossing_two_overlap:8,11->6,7": 2,
        "noncrossing_two_overlap:8,9->10,11": 1,
        "noncrossing_two_overlap:8,9->6,11": 1,
        "three_or_more_overlap:0,2->1,3,4": 3,
        "three_or_more_overlap:2,5->0,1,9": 1,
        "three_or_more_overlap:2,5->1,9,11": 1,
        "three_or_more_overlap:6,8->7,9,10": 3,
        "three_or_more_overlap:8,11->3,5,7": 1,
        "three_or_more_overlap:8,11->3,6,7": 1,
    },
    "not_legal_opened_noncrossing_substitution_target_distribution": {
        "2,10:3,5->1,5": 3,
        "2,10:3,6->1,6": 1,
        "4,8:0,9->0,7": 1,
        "4,8:9,11->7,11": 3,
    },
    "not_legal_opened_noncrossing_deletion_target_distribution": {
        "2,10:3,5->zero_or_one_overlap": 2,
        "2,10:3,6->zero_or_one_overlap": 1,
        "2,5:0,11->zero_or_one_overlap": 2,
        "2,5:1,11->zero_or_one_overlap": 6,
        "2,8:0,11->zero_or_one_overlap": 2,
        "2,8:1,11->zero_or_one_overlap": 5,
        "2,8:5,6->zero_or_one_overlap": 2,
        "2,8:5,7->zero_or_one_overlap": 5,
        "4,8:0,9->zero_or_one_overlap": 1,
        "4,8:9,11->zero_or_one_overlap": 2,
        "8,11:5,6->zero_or_one_overlap": 2,
        "8,11:5,7->zero_or_one_overlap": 6,
    },
    "not_legal_opened_three_or_more_deletion_target_distribution": {
        "2,8:1,5,7->1,7": 1,
        "2,8:1,7,11->1,7": 1,
    },
    "class_summary": {
        (
            "2,10,11|same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        ): {
            "terminal_states": 1,
            "extendable_states": 293,
            "min_replacements_by_terminal": [1],
        },
        (
            "2,4,5|same_u=4,same_i=0,1,1,same_d=1,1,2,2|"
            "opposite_u=5,opposite_i=0,0,1,opposite_d=1,1,1,1,2"
        ): {
            "terminal_states": 2,
            "extendable_states": 118,
            "min_replacements_by_terminal": [1, 1],
        },
        (
            "4,5,8|same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        ): {
            "terminal_states": 1,
            "extendable_states": 293,
            "min_replacements_by_terminal": [1],
        },
        (
            "4,5,11|same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        ): {
            "terminal_states": 3,
            "extendable_states": 152,
            "min_replacements_by_terminal": [1, 1, 1],
        },
        (
            "5,10,11|same_u=5,same_i=0,0,1,same_d=1,1,1,1,2|"
            "opposite_u=6,opposite_i=0,0,0,opposite_d=1,1,1,1,1,1"
        ): {
            "terminal_states": 3,
            "extendable_states": 152,
            "min_replacements_by_terminal": [1, 1, 1],
        },
        (
            "8,10,11|same_u=4,same_i=0,1,1,same_d=1,1,2,2|"
            "opposite_u=5,opposite_i=0,0,1,opposite_d=1,1,1,1,2"
        ): {
            "terminal_states": 2,
            "extendable_states": 118,
            "min_replacements_by_terminal": [1, 1],
        },
    },
}
EXPECTED_BY_FIFTH_CENTER = {
    "1": {
        "clean_fifth": 21,
        "sixth_total": 3973,
        "sixth_ok": 1512,
        "sixth_self_edge": 1185,
        "sixth_strict_cycle": 1276,
    },
    "2": {
        "clean_fifth": 41,
        "sixth_total": 7178,
        "sixth_ok": 2853,
        "sixth_self_edge": 1916,
        "sixth_strict_cycle": 2409,
    },
    "4": {
        "clean_fifth": 7,
        "sixth_total": 1211,
        "sixth_ok": 660,
        "sixth_self_edge": 281,
        "sixth_strict_cycle": 270,
    },
    "5": {
        "clean_fifth": 14,
        "sixth_total": 2560,
        "sixth_ok": 1022,
        "sixth_self_edge": 672,
        "sixth_strict_cycle": 866,
    },
    "7": {
        "clean_fifth": 21,
        "sixth_total": 3973,
        "sixth_ok": 1512,
        "sixth_self_edge": 1185,
        "sixth_strict_cycle": 1276,
    },
    "8": {
        "clean_fifth": 41,
        "sixth_total": 7178,
        "sixth_ok": 2853,
        "sixth_self_edge": 1916,
        "sixth_strict_cycle": 2409,
    },
    "10": {
        "clean_fifth": 7,
        "sixth_total": 1211,
        "sixth_ok": 660,
        "sixth_self_edge": 281,
        "sixth_strict_cycle": 270,
    },
    "11": {
        "clean_fifth": 14,
        "sixth_total": 2560,
        "sixth_ok": 1022,
        "sixth_self_edge": 672,
        "sixth_strict_cycle": 866,
    },
}

RowRecord = tuple[int, tuple[int, ...]]
SixState = tuple[RowRecord, RowRecord]
SevenState = tuple[RowRecord, RowRecord, RowRecord]
CenterPair = tuple[int, int]
LabelPair = tuple[int, int]
TerminalSevenAudit = tuple[SevenState, Counter[str]]


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _swap_label(label: int) -> int:
    return (label + 6) % N


def _block_swap_row(record: RowRecord) -> RowRecord:
    center, row = record
    return (_swap_label(center), tuple(sorted(_swap_label(label) for label in row)))


def _center_pair_key(pair: CenterPair) -> str:
    return f"{pair[0]},{pair[1]}"


def _pair_edge_key(left: LabelPair, right: LabelPair) -> str:
    return f"{_center_pair_key(left)}|{_center_pair_key(right)}"


def _parse_label_pair(text: str) -> LabelPair:
    left, right = text.split(",")
    return (int(left), int(right))


def _pair_edge_is_disjoint(key: str) -> bool:
    left_text, right_text = key.split("|")
    left = _parse_label_pair(left_text)
    right = _parse_label_pair(right_text)
    return set(left).isdisjoint(right)


def _block_swap_center_pair(pair: CenterPair) -> CenterPair:
    return tuple(sorted((_swap_label(pair[0]), _swap_label(pair[1]))))  # type: ignore[return-value]


def _center_pair_orbit_key(pair: CenterPair) -> str:
    orbit = sorted({pair, _block_swap_center_pair(pair)})
    return "|".join(_center_pair_key(item) for item in orbit)


def _block_swap_six_state(state: SixState) -> SixState:
    return tuple(sorted(_block_swap_row(record) for record in state))  # type: ignore[return-value]


def _block_swap_seven_state(state: SevenState) -> SevenState:
    return tuple(sorted(_block_swap_row(record) for record in state))  # type: ignore[return-value]


def _split_row_by_center_block(
    center: int, row: tuple[int, ...]
) -> tuple[LabelPair, LabelPair]:
    block_start = 0 if center < N // 2 else N // 2
    block = set(range(block_start, block_start + N // 2))
    same = tuple(label for label in row if label in block)
    opposite = tuple(label for label in row if label not in block)
    if len(same) != 2 or len(opposite) != 2:
        raise AssertionError(
            f"row at center {center} does not split into two-and-two: {row!r}"
        )
    return same, opposite  # type: ignore[return-value]


def _low_support_row_content_forms(
    clean_six_states: set[SixState],
) -> dict[str, dict[str, Any]]:
    forms: dict[str, dict[str, Any]] = {}
    for center_pair in ((4, 5), (10, 11)):
        matching_states = [
            state
            for state in clean_six_states
            if tuple(record[0] for record in state) == center_pair
        ]
        same_block_counts: Counter[str] = Counter()
        opposite_edge_counts: Counter[str] = Counter()
        opposite_pool: set[LabelPair] = set()

        for (left_center, left_row), (right_center, right_row) in matching_states:
            left_same, left_opposite = _split_row_by_center_block(
                left_center,
                left_row,
            )
            right_same, right_opposite = _split_row_by_center_block(
                right_center,
                right_row,
            )
            same_block_counts[_pair_edge_key(left_same, right_same)] += 1
            opposite_edge_counts[_pair_edge_key(left_opposite, right_opposite)] += 1
            opposite_pool.add(left_opposite)
            opposite_pool.add(right_opposite)

        disjoint_edge_keys = {
            _pair_edge_key(left, right)
            for left in opposite_pool
            for right in opposite_pool
            if set(left).isdisjoint(right)
        }
        actual_edge_keys = set(opposite_edge_counts)
        forms[_center_pair_key(center_pair)] = {
            "clean_states": len(matching_states),
            "same_block_pair_counts": dict(sorted(same_block_counts.items())),
            "opposite_pair_pool": [
                _center_pair_key(pair) for pair in sorted(opposite_pool)
            ],
            "opposite_pair_edge_counts": dict(sorted(opposite_edge_counts.items())),
            "ordered_disjoint_opposite_pair_edges": len(disjoint_edge_keys),
            "all_edges_disjoint": all(
                _pair_edge_is_disjoint(key) for key in actual_edge_keys
            ),
            "all_disjoint_pool_edges_present": actual_edge_keys == disjoint_edge_keys,
        }
    return forms


def _status_counts(counter: Counter[str]) -> dict[str, int]:
    return {status: int(counter[status]) for status in STATUSES}


def _intersection_profile(pairs: list[LabelPair]) -> tuple[int, ...]:
    return tuple(
        sorted(
            len(set(pairs[left]) & set(pairs[right]))
            for left in range(len(pairs))
            for right in range(left + 1, len(pairs))
        )
    )


def _degree_multiset(pairs: list[LabelPair]) -> tuple[int, ...]:
    return tuple(sorted(Counter(label for pair in pairs for label in pair).values()))


def _row_content_profile_key(state: SevenState) -> str:
    same_pairs: list[LabelPair] = []
    opposite_pairs: list[LabelPair] = []
    for center, row in state:
        same, opposite = _split_row_by_center_block(center, row)
        same_pairs.append(same)
        opposite_pairs.append(opposite)

    same_labels = set().union(*(set(pair) for pair in same_pairs))
    opposite_labels = set().union(*(set(pair) for pair in opposite_pairs))
    same_intersections = ",".join(
        str(value) for value in _intersection_profile(same_pairs)
    )
    opposite_intersections = ",".join(
        str(value) for value in _intersection_profile(opposite_pairs)
    )
    same_degrees = ",".join(str(value) for value in _degree_multiset(same_pairs))
    opposite_degrees = ",".join(
        str(value) for value in _degree_multiset(opposite_pairs)
    )
    return (
        f"same_u={len(same_labels)},same_i={same_intersections},"
        f"same_d={same_degrees}|opposite_u={len(opposite_labels)},"
        f"opposite_i={opposite_intersections},opposite_d={opposite_degrees}"
    )


def _optional_row_content_profile_key(state: SevenState) -> str | None:
    try:
        return _row_content_profile_key(state)
    except AssertionError:
        return None


def _status_split_key(counter: Counter[str]) -> str:
    return (
        f"legal={sum(counter.values())};"
        f"self_edge={int(counter['self_edge'])};"
        f"strict_cycle={int(counter['strict_cycle'])}"
    )


def _record_payload(record: RowRecord) -> dict[str, Any]:
    center, row = record
    return {"center": center, "row": list(row)}


def _center_tuple_key(centers: tuple[int, ...]) -> str:
    return ",".join(str(center) for center in centers)


def _initial_state_with_records(
    records: tuple[RowRecord, ...],
) -> tuple[dict[int, tuple[int, ...]], Counter[tuple[int, int]], Counter[int]]:
    assigned, pair_counts, indegrees = _initial_state()
    for center, row in records:
        _add_row(assigned, pair_counts, indegrees, center, row)
    return assigned, pair_counts, indegrees


def _low_support_seventh_extension_scan(
    clean_six_states: set[SixState],
) -> tuple[dict[str, Any], set[SevenState]]:
    options = _options()
    overall_status: Counter[str] = Counter()
    clean_six_with_clean_seventh = 0
    clean_seven_states: set[SevenState] = set()
    by_center_pair: dict[str, dict[str, Any]] = {}

    for center_pair in ((4, 5), (10, 11)):
        matching_states = [
            state
            for state in clean_six_states
            if tuple(record[0] for record in state) == center_pair
        ]
        pair_status: Counter[str] = Counter()
        by_seventh_center: dict[str, Counter[str]] = {}
        pair_clean_six_with_clean = 0
        first_clean_seventh_example: dict[str, Any] | None = None

        for state in matching_states:
            assigned, pair_counts, indegrees = _initial_state_with_records(state)

            local_clean_seventh = 0
            for seventh_center in range(N):
                if seventh_center in assigned:
                    continue
                center_counter = by_seventh_center.setdefault(
                    str(seventh_center),
                    Counter(),
                )
                for seventh_row in _valid_options(
                    seventh_center,
                    options,
                    assigned,
                    pair_counts,
                    indegrees,
                ):
                    _add_row(
                        assigned,
                        pair_counts,
                        indegrees,
                        seventh_center,
                        seventh_row,
                    )
                    seventh_status, _edge_count = _partial_vertex_circle_status(
                        assigned
                    )
                    _remove_row(
                        assigned,
                        pair_counts,
                        indegrees,
                        seventh_center,
                        seventh_row,
                    )

                    pair_status[seventh_status] += 1
                    overall_status[seventh_status] += 1
                    center_counter[seventh_status] += 1
                    if seventh_status == "ok":
                        local_clean_seventh += 1
                        seventh_record = (seventh_center, tuple(seventh_row))
                        clean_seven_state: SevenState = tuple(
                            tuple(sorted((*state, seventh_record)))
                        )  # type: ignore[assignment]
                        clean_seven_states.add(clean_seven_state)
                        if first_clean_seventh_example is None:
                            first_clean_seventh_example = {
                                "six_state": [
                                    _record_payload(record) for record in state
                                ],
                                "seventh": _record_payload(seventh_record),
                            }
            if local_clean_seventh:
                pair_clean_six_with_clean += 1
                clean_six_with_clean_seventh += 1

        by_center_pair[_center_pair_key(center_pair)] = {
            "clean_six_states": len(matching_states),
            "clean_six_states_with_clean_seventh": pair_clean_six_with_clean,
            "seventh_status_counts": _status_counts(pair_status),
            "by_seventh_center": {
                center: _status_counts(counter)
                for center, counter in sorted(
                    by_seventh_center.items(),
                    key=lambda item: int(item[0]),
                )
            },
            "first_clean_seventh_example": first_clean_seventh_example,
        }

    return {
        "clean_six_states": sum(
            item["clean_six_states"] for item in by_center_pair.values()
        ),
        "clean_six_states_with_clean_seventh": clean_six_with_clean_seventh,
        "ordered_legal_seventh_rows": sum(overall_status.values()),
        "ordered_clean_seventh_rows": int(overall_status["ok"]),
        "ordered_self_edge_seventh_rows": int(overall_status["self_edge"]),
        "ordered_strict_cycle_seventh_rows": int(overall_status["strict_cycle"]),
        "unique_clean_seven_states": len(clean_seven_states),
        "by_center_pair": by_center_pair,
    }, clean_seven_states


def _low_support_eighth_extension_audit(
    clean_seven_states: set[SevenState],
) -> tuple[dict[str, Any], list[TerminalSevenAudit]]:
    options = _options()
    overall_status: Counter[str] = Counter()
    clean_seven_with_clean_eighth = 0
    unique_clean_eight_states: set[tuple[RowRecord, ...]] = set()
    by_seven_center_triple: dict[str, dict[str, Any]] = {}
    terminal_seven_state_audits: list[TerminalSevenAudit] = []
    first_clean_eighth_example: dict[str, Any] | None = None
    first_terminal_seven_state: dict[str, Any] | None = None

    for state in sorted(clean_seven_states):
        assigned, pair_counts, indegrees = _initial_state_with_records(state)
        triple_key = _center_tuple_key(tuple(record[0] for record in state))
        triple_entry = by_seven_center_triple.setdefault(
            triple_key,
            {
                "clean_seven_states": 0,
                "clean_seven_states_with_clean_eighth": 0,
                "eighth_status_counts": Counter(),
            },
        )
        triple_entry["clean_seven_states"] += 1
        local_status: Counter[str] = Counter()
        local_clean_eighth = 0

        for eighth_center in range(N):
            if eighth_center in assigned:
                continue
            for eighth_row in _valid_options(
                eighth_center,
                options,
                assigned,
                pair_counts,
                indegrees,
            ):
                _add_row(
                    assigned,
                    pair_counts,
                    indegrees,
                    eighth_center,
                    eighth_row,
                )
                eighth_status, _edge_count = _partial_vertex_circle_status(assigned)
                _remove_row(
                    assigned,
                    pair_counts,
                    indegrees,
                    eighth_center,
                    eighth_row,
                )

                overall_status[eighth_status] += 1
                local_status[eighth_status] += 1
                triple_entry["eighth_status_counts"][eighth_status] += 1
                if eighth_status == "ok":
                    local_clean_eighth += 1
                    eighth_record = (eighth_center, tuple(eighth_row))
                    unique_clean_eight_states.add(
                        tuple(sorted((*state, eighth_record)))
                    )
                    if first_clean_eighth_example is None:
                        first_clean_eighth_example = {
                            "seven_state": [
                                _record_payload(record) for record in state
                            ],
                            "eighth": _record_payload(eighth_record),
                        }

        if local_clean_eighth:
            clean_seven_with_clean_eighth += 1
            triple_entry["clean_seven_states_with_clean_eighth"] += 1
        else:
            terminal_seven_state_audits.append((state, Counter(local_status)))
            if first_terminal_seven_state is None:
                first_terminal_seven_state = {
                    "seven_state": [_record_payload(record) for record in state],
                    "legal_eighth_rows": sum(local_status.values()),
                    "eighth_status_counts": _status_counts(local_status),
                }

    return {
        "clean_seven_states": len(clean_seven_states),
        "clean_seven_states_with_clean_eighth": clean_seven_with_clean_eighth,
        "terminal_clean_seven_states": (
            len(clean_seven_states) - clean_seven_with_clean_eighth
        ),
        "ordered_legal_eighth_rows": sum(overall_status.values()),
        "ordered_clean_eighth_rows": int(overall_status["ok"]),
        "ordered_self_edge_eighth_rows": int(overall_status["self_edge"]),
        "ordered_strict_cycle_eighth_rows": int(overall_status["strict_cycle"]),
        "unique_clean_eight_states": len(unique_clean_eight_states),
        "by_seven_center_triple": {
            key: {
                "clean_seven_states": int(value["clean_seven_states"]),
                "clean_seven_states_with_clean_eighth": int(
                    value["clean_seven_states_with_clean_eighth"]
                ),
                "eighth_status_counts": _status_counts(value["eighth_status_counts"]),
            }
            for key, value in sorted(by_seven_center_triple.items())
        },
        "first_clean_eighth_example": first_clean_eighth_example,
        "first_terminal_seven_state": first_terminal_seven_state,
    }, terminal_seven_state_audits


def _terminal_state_orbit_payload(
    representative: SevenState,
    block_swap_member: SevenState,
    status: Counter[str],
) -> dict[str, Any]:
    return {
        "representative": [_record_payload(record) for record in representative],
        "block_swap_member": [_record_payload(record) for record in block_swap_member],
        "legal_eighth_rows": sum(status.values()),
        "eighth_status_counts": _status_counts(status),
        "row_content_profile": _row_content_profile_key(representative),
    }


def _low_support_terminal_classification(
    terminal_audits: list[TerminalSevenAudit],
) -> dict[str, Any]:
    status_by_state = {state: status for state, status in terminal_audits}
    seen: set[SevenState] = set()
    orbit_sizes: Counter[int] = Counter()
    row_content_profiles: Counter[str] = Counter()
    status_splits: Counter[str] = Counter()
    orbit_representatives: list[dict[str, Any]] = []

    for state, status in sorted(terminal_audits):
        row_content_profiles[_row_content_profile_key(state)] += 1
        status_splits[_status_split_key(status)] += 1
        if state in seen:
            continue

        orbit = sorted({state, _block_swap_seven_state(state)})
        seen.update(orbit)
        orbit_sizes[len(orbit)] += 1
        if len(orbit) != 2:
            raise AssertionError(f"unexpected terminal block-swap orbit: {orbit!r}")
        representative = orbit[0]
        block_swap_member = orbit[1]
        if (
            representative not in status_by_state
            or block_swap_member not in status_by_state
        ):
            raise AssertionError("terminal block-swap orbit left terminal catalog")
        if status_by_state[representative] != status_by_state[block_swap_member]:
            raise AssertionError("terminal block-swap orbit changed status split")
        orbit_representatives.append(
            _terminal_state_orbit_payload(
                representative,
                block_swap_member,
                status_by_state[representative],
            )
        )

    return {
        "terminal_clean_seven_states": len(terminal_audits),
        "block_swap_orbits": sum(orbit_sizes.values()),
        "block_swap_orbit_sizes": _json_counter(orbit_sizes),
        "row_content_profile_counts": {
            key: int(row_content_profiles[key]) for key in sorted(row_content_profiles)
        },
        "eighth_status_split_counts": {
            key: int(status_splits[key]) for key in sorted(status_splits)
        },
        "block_swap_orbit_representatives": orbit_representatives,
    }


def _state_eighth_center_counts(
    state: SevenState,
    options: Mapping[int, list[tuple[int, ...]]],
) -> dict[str, dict[str, int]]:
    assigned, pair_counts, indegrees = _initial_state_with_records(state)
    by_eighth_center: dict[str, dict[str, int]] = {}
    for eighth_center in range(N):
        if eighth_center in assigned:
            continue
        center_status: Counter[str] = Counter()
        for eighth_row in _valid_options(
            eighth_center,
            options,
            assigned,
            pair_counts,
            indegrees,
        ):
            _add_row(
                assigned,
                pair_counts,
                indegrees,
                eighth_center,
                eighth_row,
            )
            eighth_status, _edge_count = _partial_vertex_circle_status(assigned)
            _remove_row(
                assigned,
                pair_counts,
                indegrees,
                eighth_center,
                eighth_row,
            )
            center_status[eighth_status] += 1
        if center_status:
            by_eighth_center[str(eighth_center)] = _status_counts(center_status)
    return by_eighth_center


def _center_obstruction_profile_key(
    by_eighth_center: Mapping[str, Mapping[str, int]],
) -> str:
    self_only = 0
    strict_only = 0
    mixed = 0
    for status_counts in by_eighth_center.values():
        has_self_edge = status_counts["self_edge"] > 0
        has_strict_cycle = status_counts["strict_cycle"] > 0
        if has_self_edge and has_strict_cycle:
            mixed += 1
        elif has_self_edge:
            self_only += 1
        elif has_strict_cycle:
            strict_only += 1
        else:
            raise AssertionError(
                f"terminal eighth center has no obstruction: {status_counts!r}"
            )
    return (
        f"self_only_centers={self_only};"
        f"strict_only_centers={strict_only};mixed_centers={mixed}"
    )


def _block_swap_eighth_center_counts(
    by_eighth_center: Mapping[str, Mapping[str, int]],
) -> dict[str, dict[str, int]]:
    return {
        str(_swap_label(int(center))): dict(status_counts)
        for center, status_counts in by_eighth_center.items()
    }


def _low_support_terminal_eighth_center_audit(
    terminal_audits: list[TerminalSevenAudit],
) -> dict[str, Any]:
    options = _options()
    center_counts_by_state = {
        state: _state_eighth_center_counts(state, options)
        for state, _status in terminal_audits
    }
    status_by_state = {state: status for state, status in terminal_audits}
    aggregate_by_center: dict[str, Counter[str]] = {}
    center_profiles: Counter[str] = Counter()
    seen: set[SevenState] = set()
    orbit_representatives: list[dict[str, Any]] = []

    for state, status in sorted(terminal_audits):
        by_eighth_center = center_counts_by_state[state]
        status_total = Counter()
        for center, center_status in by_eighth_center.items():
            aggregate = aggregate_by_center.setdefault(center, Counter())
            for status_name in STATUSES:
                count = center_status[status_name]
                aggregate[status_name] += count
                status_total[status_name] += count
        if status_total != status:
            raise AssertionError(
                f"terminal center split does not match terminal status: {state!r}"
            )
        if status_total["ok"] != 0:
            raise AssertionError(f"terminal state has a clean eighth row: {state!r}")
        center_profiles[_center_obstruction_profile_key(by_eighth_center)] += 1

        if state in seen:
            continue
        orbit = sorted({state, _block_swap_seven_state(state)})
        seen.update(orbit)
        representative = orbit[0]
        block_swap_member = orbit[1]
        representative_counts = center_counts_by_state[representative]
        block_swap_counts = center_counts_by_state[block_swap_member]
        if _block_swap_eighth_center_counts(representative_counts) != block_swap_counts:
            raise AssertionError("terminal center split is not block-swap equivariant")
        if status_by_state[representative] != status_by_state[block_swap_member]:
            raise AssertionError("terminal block-swap orbit changed status split")
        orbit_representatives.append(
            {
                "representative": [
                    _record_payload(record) for record in representative
                ],
                "block_swap_member": [
                    _record_payload(record) for record in block_swap_member
                ],
                "representative_by_eighth_center": {
                    center: representative_counts[center]
                    for center in sorted(
                        representative_counts,
                        key=lambda value: int(value),
                    )
                },
                "block_swap_by_eighth_center": {
                    center: block_swap_counts[center]
                    for center in sorted(
                        block_swap_counts,
                        key=lambda value: int(value),
                    )
                },
                "center_obstruction_profile": _center_obstruction_profile_key(
                    representative_counts
                ),
            }
        )

    return {
        "terminal_clean_seven_states": len(terminal_audits),
        "block_swap_orbits": len(orbit_representatives),
        "aggregate_by_eighth_center": {
            center: _status_counts(counter)
            for center, counter in sorted(
                aggregate_by_center.items(),
                key=lambda item: int(item[0]),
            )
        },
        "center_obstruction_profile_counts": {
            key: int(center_profiles[key]) for key in sorted(center_profiles)
        },
        "block_swap_orbit_representatives": orbit_representatives,
    }


def _low_support_profile_terminality_audit(
    clean_seven_states: set[SevenState],
    terminal_audits: list[TerminalSevenAudit],
) -> dict[str, Any]:
    terminal_states = {state for state, _status in terminal_audits}
    profile_counts: Counter[str] = Counter()
    profile_terminal: Counter[str] = Counter()
    profile_extendable: Counter[str] = Counter()
    non_two_two_by_triple: Counter[str] = Counter()
    non_two_two_terminal = 0
    first_non_two_two_example: SevenState | None = None
    extendable_examples: dict[str, SevenState] = {}

    for state in sorted(clean_seven_states):
        is_terminal = state in terminal_states
        profile = _optional_row_content_profile_key(state)
        if profile is None:
            non_two_two_by_triple[
                _center_tuple_key(tuple(record[0] for record in state))
            ] += 1
            non_two_two_terminal += int(is_terminal)
            if first_non_two_two_example is None:
                first_non_two_two_example = state
            continue

        profile_counts[profile] += 1
        if is_terminal:
            profile_terminal[profile] += 1
        else:
            profile_extendable[profile] += 1
            extendable_examples.setdefault(profile, state)

    terminal_profile_keys = {
        _row_content_profile_key(state) for state, _status in terminal_audits
    }
    terminal_profiles_with_extendable = sorted(
        profile for profile in terminal_profile_keys if profile_extendable[profile] > 0
    )
    non_two_two_total = sum(non_two_two_by_triple.values())

    return {
        "clean_seven_states": len(clean_seven_states),
        "terminal_clean_seven_states": len(terminal_audits),
        "non_two_two_clean_seven_states": non_two_two_total,
        "non_two_two_terminal_clean_seven_states": non_two_two_terminal,
        "two_two_clean_seven_states": len(clean_seven_states) - non_two_two_total,
        "two_two_terminal_clean_seven_states": len(terminal_audits),
        "two_two_profile_classes": len(profile_counts),
        "terminal_profile_classes": len(terminal_profile_keys),
        "terminal_profiles_with_extendable_states": len(
            terminal_profiles_with_extendable
        ),
        "profile_only_terminality_holds": not terminal_profiles_with_extendable,
        "non_two_two_by_center_triple": {
            key: int(non_two_two_by_triple[key])
            for key in sorted(non_two_two_by_triple)
        },
        "profile_counts": {
            profile: {
                "clean_two_two_seven_states": int(profile_counts[profile]),
                "terminal": int(profile_terminal[profile]),
                "extendable": int(profile_extendable[profile]),
            }
            for profile in sorted(profile_counts)
        },
        "first_non_two_two_example": (
            [_record_payload(record) for record in first_non_two_two_example]
            if first_non_two_two_example is not None
            else None
        ),
        "terminal_profile_extendable_examples": {
            profile: [
                _record_payload(record) for record in extendable_examples[profile]
            ]
            for profile in terminal_profiles_with_extendable
        },
    }


def _triple_profile_key(state: SevenState, profile: str) -> str:
    return f"{_center_tuple_key(tuple(record[0] for record in state))}|{profile}"


def _low_support_triple_profile_terminality_audit(
    clean_seven_states: set[SevenState],
    terminal_audits: list[TerminalSevenAudit],
) -> dict[str, Any]:
    terminal_states = {state for state, _status in terminal_audits}
    triple_profile_counts: Counter[str] = Counter()
    triple_profile_terminal: Counter[str] = Counter()
    triple_profile_extendable: Counter[str] = Counter()
    non_two_two_by_triple: Counter[str] = Counter()
    non_two_two_terminal = 0
    first_terminal_examples: dict[str, SevenState] = {}
    first_extendable_examples: dict[str, SevenState] = {}

    for state in sorted(clean_seven_states):
        is_terminal = state in terminal_states
        profile = _optional_row_content_profile_key(state)
        if profile is None:
            non_two_two_by_triple[
                _center_tuple_key(tuple(record[0] for record in state))
            ] += 1
            non_two_two_terminal += int(is_terminal)
            continue

        key = _triple_profile_key(state, profile)
        triple_profile_counts[key] += 1
        if is_terminal:
            triple_profile_terminal[key] += 1
            first_terminal_examples.setdefault(key, state)
        else:
            triple_profile_extendable[key] += 1
            first_extendable_examples.setdefault(key, state)

    terminal_keys = sorted(triple_profile_terminal)
    terminal_keys_with_extendable = [
        key for key in terminal_keys if triple_profile_extendable[key] > 0
    ]
    non_two_two_total = sum(non_two_two_by_triple.values())

    return {
        "clean_seven_states": len(clean_seven_states),
        "terminal_clean_seven_states": len(terminal_audits),
        "non_two_two_clean_seven_states": non_two_two_total,
        "non_two_two_terminal_clean_seven_states": non_two_two_terminal,
        "two_two_clean_seven_states": len(clean_seven_states) - non_two_two_total,
        "two_two_terminal_clean_seven_states": len(terminal_audits),
        "two_two_triple_profile_classes": len(triple_profile_counts),
        "terminal_triple_profile_classes": len(terminal_keys),
        "terminal_triple_profiles_with_extendable_states": len(
            terminal_keys_with_extendable
        ),
        "triple_profile_only_terminality_holds": not terminal_keys_with_extendable,
        "terminal_triple_profile_counts": {
            key: {
                "clean_two_two_seven_states": int(triple_profile_counts[key]),
                "terminal": int(triple_profile_terminal[key]),
                "extendable": int(triple_profile_extendable[key]),
            }
            for key in terminal_keys
        },
        "terminal_triple_profile_extendable_examples": {
            key: {
                "terminal": [
                    _record_payload(record) for record in first_terminal_examples[key]
                ],
                "extendable": [
                    _record_payload(record) for record in first_extendable_examples[key]
                ],
            }
            for key in terminal_keys_with_extendable
        },
    }


def _row_replacement_distance(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    return len(set(left) ^ set(right)) // 2


def _center_orbit_key(center: int) -> str:
    return ",".join(str(item) for item in sorted({center, _swap_label(center)}))


def _replacement_side(center: int, removed: int, added: int) -> str:
    center_block_start = 0 if center < N // 2 else N // 2
    center_block = set(range(center_block_start, center_block_start + N // 2))
    removed_side = "same_block" if removed in center_block else "opposite_block"
    added_side = "same_block" if added in center_block else "opposite_block"
    if removed_side != added_side:
        raise AssertionError(
            "nearest replacement changed same/opposite side: "
            f"center={center}, removed={removed}, added={added}"
        )
    return removed_side


def _eighth_center_status_kind(status_counts: Mapping[str, int]) -> str:
    if status_counts["ok"] > 0:
        return "ok"
    has_self_edge = status_counts["self_edge"] > 0
    has_strict_cycle = status_counts["strict_cycle"] > 0
    if has_self_edge and has_strict_cycle:
        return "mixed"
    if has_self_edge:
        return "self_only"
    if has_strict_cycle:
        return "strict_only"
    return "none"


def _changed_row_relation(
    changed_center: int,
    opened_center: int,
    changed_row: tuple[int, ...],
    opened_row: tuple[int, ...],
) -> str:
    overlap = sorted(set(changed_row) & set(opened_row))
    if len(overlap) <= 1:
        return "zero_or_one_overlap"
    if len(overlap) > 2:
        return "three_or_more_overlap"
    source = normalize_chord(changed_center, opened_center)
    target = normalize_chord(overlap[0], overlap[1])
    if chords_cross_in_order(source, target, list(range(N))):
        return "crossing_two_overlap"
    return "noncrossing_two_overlap"


def _paircross_blockers(
    center: int,
    row: tuple[int, ...],
    assigned: Mapping[int, tuple[int, ...]],
) -> list[tuple[int, tuple[int, int], tuple[int, ...], str]]:
    blockers = []
    for other_center, other_row in assigned.items():
        overlap = tuple(sorted(set(row) & set(other_row)))
        if len(overlap) <= 1:
            continue
        source = normalize_chord(center, other_center)
        if len(overlap) > 2:
            blockers.append((other_center, source, overlap, "three_or_more_overlap"))
            continue
        target = normalize_chord(*overlap)
        if not chords_cross_in_order(source, target, list(range(N))):
            blockers.append((other_center, source, target, "noncrossing_two_overlap"))
    return blockers


def _chord_key(chord: tuple[int, int]) -> str:
    return f"{chord[0]},{chord[1]}"


def _label_tuple_key(labels: tuple[int, ...]) -> str:
    return ",".join(str(label) for label in labels)


def _source_side(source: tuple[int, int], label: int) -> str:
    a, b = normalize_chord(*source)
    return "inside" if a < label < b else "outside"


def _source_side_relation(source: tuple[int, int], left: int, right: int) -> str:
    if _source_side(source, left) == _source_side(source, right):
        return "same_source_arc"
    return "opposite_source_arcs"


def _source_arc_class(source: tuple[int, int], target: tuple[int, int]) -> str:
    source = normalize_chord(*source)
    target = normalize_chord(*target)
    if set(source) & set(target):
        return "shares_source_endpoint"
    a, b = source
    inside_len = b - a - 1
    outside_len = N - (b - a) - 1
    target_inside = [a < endpoint < b for endpoint in target]
    if target_inside[0] != target_inside[1]:
        return "split_arcs"
    target_side_len = inside_len if target_inside[0] else outside_len
    other_side_len = outside_len if target_inside[0] else inside_len
    if target_side_len > other_side_len:
        return "long_arc"
    if target_side_len < other_side_len:
        return "short_arc"
    return "diameter_arc"


def _not_legal_opened_paircross_profile(
    terminal: SevenState,
    extendable: SevenState,
    opened_center: int,
    changed_center: int,
    terminal_changed_row: tuple[int, ...],
    extendable_changed_row: tuple[int, ...],
    options: Mapping[int, list[tuple[int, ...]]],
) -> dict[str, Any]:
    assigned_before, pair_counts_before, indegrees_before = _initial_state_with_records(
        terminal
    )
    assigned_after, pair_counts_after, indegrees_after = _initial_state_with_records(
        extendable
    )
    center_options = options[opened_center]
    before_paircross_rows = [
        row
        for row in center_options
        if _paircross_ok(opened_center, row, assigned_before)
    ]
    after_paircross_rows = [
        row
        for row in center_options
        if _paircross_ok(opened_center, row, assigned_after)
    ]
    after_valid_rows = [
        row
        for row in after_paircross_rows
        if _pair_cap_ok(row, pair_counts_after) and _indegree_ok(row, indegrees_after)
    ]
    before_valid_rows = [
        row
        for row in before_paircross_rows
        if _pair_cap_ok(row, pair_counts_before) and _indegree_ok(row, indegrees_before)
    ]
    removed_labels = sorted(set(terminal_changed_row) - set(extendable_changed_row))
    added_labels = sorted(set(extendable_changed_row) - set(terminal_changed_row))
    if len(removed_labels) != 1 or len(added_labels) != 1:
        raise AssertionError(
            "not-legal opening audit expects a one-for-one replacement: "
            f"{terminal_changed_row!r} -> {extendable_changed_row!r}"
        )
    removed_label = removed_labels[0]
    added_label = added_labels[0]
    source = normalize_chord(changed_center, opened_center)
    before_forbidden_overlap_removed_endpoint: Counter[str] = Counter()
    noncrossing_target_arcs: Counter[str] = Counter()
    noncrossing_switches: Counter[str] = Counter()
    noncrossing_source_targets: Counter[str] = Counter()
    three_or_more_switches: Counter[str] = Counter()
    crossing_creation_mechanisms: Counter[str] = Counter()
    noncrossing_substitution_arcs: Counter[str] = Counter()
    substitution_layer_arcs: Counter[str] = Counter()
    opposite_arc_paircross_contexts: Counter[str] = Counter()
    opposite_arc_paircross_blocker_counts: Counter[int] = Counter()
    opposite_arc_paircross_blocker_kinds: Counter[str] = Counter()
    opposite_arc_paircross_blocker_roles: Counter[str] = Counter()
    opposite_arc_paircross_blocker_center_orbits: Counter[str] = Counter()
    opposite_arc_paircross_blocker_source_targets: Counter[str] = Counter()
    noncrossing_substitution_targets: Counter[str] = Counter()
    noncrossing_deletion_targets: Counter[str] = Counter()
    three_or_more_deletion_targets: Counter[str] = Counter()
    after_paircross_row_set = set(after_paircross_rows)
    after_valid_row_set = set(after_valid_rows)
    terminal_centers = set(dict(terminal))
    for row in center_options:
        before_relation = _changed_row_relation(
            changed_center,
            opened_center,
            terminal_changed_row,
            row,
        )
        if before_relation != "noncrossing_two_overlap" or added_label not in row:
            continue
        before_overlap = tuple(sorted(set(terminal_changed_row) & set(row)))
        if removed_label not in before_overlap:
            continue
        after_relation = _changed_row_relation(
            changed_center,
            opened_center,
            extendable_changed_row,
            row,
        )
        survivor = next(label for label in before_overlap if label != removed_label)
        side_relation = _source_side_relation(source, survivor, added_label)
        layer_key = f"candidate_contains_added:{side_relation}->{after_relation}"
        substitution_layer_arcs[f"all_options:{layer_key}"] += 1
        if side_relation == "opposite_source_arcs":
            old_target = normalize_chord(*before_overlap)
            after_overlap = tuple(sorted(set(extendable_changed_row) & set(row)))
            new_target = normalize_chord(*after_overlap)
            context_key = (
                f"{_chord_key(source)}:{_chord_key(old_target)}"
                f"->{_chord_key(new_target)}"
            )
            opposite_arc_paircross_contexts[f"all_options:{context_key}"] += 1
            blockers = _paircross_blockers(opened_center, row, assigned_after)
            if blockers:
                opposite_arc_paircross_contexts[f"failed_paircross:{context_key}"] += 1
                opposite_arc_paircross_blocker_counts[len(blockers)] += 1
                for blocker_center, blocker_source, blocker_target, kind in blockers:
                    if blocker_center == changed_center:
                        role = "changed_row"
                    elif blocker_center in terminal_centers:
                        role = "other_added_row"
                    else:
                        role = "fixed_row"
                    target_key = (
                        _chord_key(blocker_target)  # type: ignore[arg-type]
                        if kind == "noncrossing_two_overlap"
                        else _label_tuple_key(blocker_target)
                    )
                    opposite_arc_paircross_blocker_kinds[kind] += 1
                    opposite_arc_paircross_blocker_roles[role] += 1
                    opposite_arc_paircross_blocker_center_orbits[
                        _center_orbit_key(blocker_center)
                    ] += 1
                    opposite_arc_paircross_blocker_source_targets[
                        f"{kind}:{_chord_key(blocker_source)}->{target_key}"
                    ] += 1
            else:
                opposite_arc_paircross_contexts[f"after_paircross:{context_key}"] += 1
        if row in after_paircross_row_set:
            substitution_layer_arcs[f"after_paircross:{layer_key}"] += 1
        if row in after_valid_row_set:
            substitution_layer_arcs[f"after_valid:{layer_key}"] += 1
    for row in after_valid_rows:
        before_relation = _changed_row_relation(
            changed_center,
            opened_center,
            terminal_changed_row,
            row,
        )
        after_relation = _changed_row_relation(
            changed_center,
            opened_center,
            extendable_changed_row,
            row,
        )
        before_overlap = tuple(sorted(set(terminal_changed_row) & set(row)))
        endpoint_status = (
            "contains_removed_endpoint"
            if removed_label in before_overlap
            else "omits_removed_endpoint"
        )
        if before_relation in {"noncrossing_two_overlap", "three_or_more_overlap"}:
            before_forbidden_overlap_removed_endpoint[
                f"{before_relation}:{endpoint_status}"
            ] += 1
        if before_relation == "noncrossing_two_overlap":
            target = normalize_chord(*before_overlap)
            after_overlap = tuple(sorted(set(extendable_changed_row) & set(row)))
            added_status = (
                "candidate_contains_added"
                if added_label in row
                else "candidate_omits_added"
            )
            noncrossing_target_arcs[_source_arc_class(source, target)] += 1
            noncrossing_switches[f"{added_status}->{after_relation}"] += 1
            noncrossing_source_targets[
                f"{_chord_key(source)}->{_chord_key(target)}"
            ] += 1
            source_target = f"{_chord_key(source)}:{_chord_key(target)}"
            if added_label in row:
                survivor = next(
                    label for label in before_overlap if label != removed_label
                )
                side_relation = _source_side_relation(source, survivor, added_label)
                noncrossing_substitution_arcs[
                    f"candidate_contains_added:{side_relation}->{after_relation}"
                ] += 1
                if len(after_overlap) == 2:
                    new_target = normalize_chord(*after_overlap)
                    noncrossing_substitution_targets[
                        f"{source_target}->{_chord_key(new_target)}"
                    ] += 1
                if after_relation == "crossing_two_overlap":
                    crossing_creation_mechanisms[
                        "noncrossing_removed_to_added_substitution"
                    ] += 1
            else:
                noncrossing_deletion_targets[f"{source_target}->{after_relation}"] += 1
        elif before_relation == "three_or_more_overlap":
            three_or_more_switches[f"{endpoint_status}->{after_relation}"] += 1
            after_overlap = tuple(sorted(set(extendable_changed_row) & set(row)))
            if after_relation == "crossing_two_overlap":
                crossing_creation_mechanisms[
                    "three_or_more_removed_endpoint_deletion"
                ] += 1
                three_or_more_deletion_targets[
                    f"{_chord_key(source)}:{_label_tuple_key(before_overlap)}"
                    f"->{_label_tuple_key(after_overlap)}"
                ] += 1
    return {
        "before_paircross": len(before_paircross_rows),
        "before_valid": len(before_valid_rows),
        "after_paircross": len(after_paircross_rows),
        "after_valid": len(after_valid_rows),
        "before_changed_row_relations": Counter(
            _changed_row_relation(
                changed_center,
                opened_center,
                terminal_changed_row,
                row,
            )
            for row in after_valid_rows
        ),
        "after_changed_row_relations": Counter(
            _changed_row_relation(
                changed_center,
                opened_center,
                extendable_changed_row,
                row,
            )
            for row in after_valid_rows
        ),
        "before_forbidden_overlap_removed_endpoint": (
            before_forbidden_overlap_removed_endpoint
        ),
        "noncrossing_target_arcs": noncrossing_target_arcs,
        "noncrossing_switches": noncrossing_switches,
        "noncrossing_source_targets": noncrossing_source_targets,
        "three_or_more_switches": three_or_more_switches,
        "crossing_creation_mechanisms": crossing_creation_mechanisms,
        "noncrossing_substitution_arcs": noncrossing_substitution_arcs,
        "substitution_layer_arcs": substitution_layer_arcs,
        "opposite_arc_paircross_contexts": opposite_arc_paircross_contexts,
        "opposite_arc_paircross_blocker_counts": (
            opposite_arc_paircross_blocker_counts
        ),
        "opposite_arc_paircross_blocker_kinds": (opposite_arc_paircross_blocker_kinds),
        "opposite_arc_paircross_blocker_roles": (opposite_arc_paircross_blocker_roles),
        "opposite_arc_paircross_blocker_center_orbits": (
            opposite_arc_paircross_blocker_center_orbits
        ),
        "opposite_arc_paircross_blocker_source_targets": (
            opposite_arc_paircross_blocker_source_targets
        ),
        "noncrossing_substitution_targets": noncrossing_substitution_targets,
        "noncrossing_deletion_targets": noncrossing_deletion_targets,
        "three_or_more_deletion_targets": three_or_more_deletion_targets,
    }


def _state_replacement_distance(left: SevenState, right: SevenState) -> int:
    right_by_center = {center: row for center, row in right}
    return sum(
        _row_replacement_distance(row, right_by_center[center]) for center, row in left
    )


def _changed_row_payload(left: SevenState, right: SevenState) -> list[dict[str, Any]]:
    right_by_center = {center: row for center, row in right}
    changed_rows = []
    for center, row in left:
        right_row = right_by_center[center]
        removed = sorted(set(row) - set(right_row))
        added = sorted(set(right_row) - set(row))
        if removed or added:
            changed_rows.append(
                {
                    "center": center,
                    "removed": removed,
                    "added": added,
                    "row_replacements": len(removed),
                }
            )
    return changed_rows


def _low_support_terminal_edit_distance_audit(
    clean_seven_states: set[SevenState],
    terminal_audits: list[TerminalSevenAudit],
) -> dict[str, Any]:
    terminal_states = {state for state, _status in terminal_audits}
    by_triple_profile: dict[str, dict[str, list[SevenState]]] = {}
    for state in sorted(clean_seven_states):
        profile = _optional_row_content_profile_key(state)
        if profile is None:
            continue
        key = _triple_profile_key(state, profile)
        entry = by_triple_profile.setdefault(
            key,
            {"terminal": [], "extendable": []},
        )
        if state in terminal_states:
            entry["terminal"].append(state)
        else:
            entry["extendable"].append(state)

    min_replacements: Counter[int] = Counter()
    nearest_counts: Counter[int] = Counter()
    changed_row_counts: Counter[int] = Counter()
    changed_center_counts: Counter[int] = Counter()
    changed_center_orbit_counts: Counter[str] = Counter()
    changed_center_removed_added_counts: Counter[str] = Counter()
    replacement_side_counts: Counter[str] = Counter()
    extendable_ok_center_counts: Counter[int] = Counter()
    extendable_ok_row_counts: Counter[int] = Counter()
    opened_center_counts: Counter[int] = Counter()
    opened_center_orbit_counts: Counter[str] = Counter()
    opened_center_prior_status_counts: Counter[str] = Counter()
    opened_center_prior_status_by_transition: Counter[str] = Counter()
    opened_contains_replacement_label_counts: Counter[str] = Counter()
    changed_to_opened_center_orbit_counts: Counter[str] = Counter()
    replacement_side_to_opened_prior_status_counts: Counter[str] = Counter()
    not_legal_opened_center_counts: Counter[int] = Counter()
    not_legal_opened_center_orbit_counts: Counter[str] = Counter()
    not_legal_opened_changed_center_orbit_counts: Counter[str] = Counter()
    not_legal_opened_replacement_side_counts: Counter[str] = Counter()
    not_legal_opened_paircross_profile_counts: Counter[str] = Counter()
    not_legal_opened_before_relation_counts: Counter[str] = Counter()
    not_legal_opened_after_relation_counts: Counter[str] = Counter()
    not_legal_opened_before_removed_endpoint_counts: Counter[str] = Counter()
    not_legal_opened_noncrossing_arc_counts: Counter[str] = Counter()
    not_legal_opened_noncrossing_switch_counts: Counter[str] = Counter()
    not_legal_opened_noncrossing_source_target_counts: Counter[str] = Counter()
    not_legal_opened_three_or_more_switch_counts: Counter[str] = Counter()
    not_legal_opened_crossing_creation_mechanism_counts: Counter[str] = Counter()
    not_legal_opened_noncrossing_substitution_arc_counts: Counter[str] = Counter()
    not_legal_opened_substitution_layer_arc_counts: Counter[str] = Counter()
    not_legal_opened_opposite_arc_paircross_context_counts: Counter[str] = Counter()
    not_legal_opened_opposite_arc_paircross_blocker_counts: Counter[int] = Counter()
    not_legal_opened_opposite_arc_paircross_blocker_kind_counts: Counter[str] = (
        Counter()
    )
    not_legal_opened_opposite_arc_paircross_blocker_role_counts: Counter[str] = (
        Counter()
    )
    not_legal_opened_opposite_arc_paircross_blocker_center_orbit_counts: Counter[
        str
    ] = Counter()
    not_legal_opened_opposite_arc_paircross_blocker_source_target_counts: Counter[
        str
    ] = Counter()
    not_legal_opened_noncrossing_substitution_target_counts: Counter[str] = Counter()
    not_legal_opened_noncrossing_deletion_target_counts: Counter[str] = Counter()
    not_legal_opened_three_or_more_deletion_target_counts: Counter[str] = Counter()
    nearest_transition_count = 0
    opened_center_instance_count = 0
    not_legal_opened_instance_count = 0
    class_summary: dict[str, dict[str, Any]] = {}
    by_terminal: list[dict[str, Any]] = []
    options = _options()

    for key, entry in sorted(by_triple_profile.items()):
        if not entry["terminal"]:
            continue
        if not entry["extendable"]:
            raise AssertionError(f"terminal class has no extendable state: {key}")
        class_distances = []
        for terminal in entry["terminal"]:
            terminal_eighth_counts = _state_eighth_center_counts(terminal, options)
            terminal_prior_status_by_center = {
                int(center): _eighth_center_status_kind(status_counts)
                for center, status_counts in terminal_eighth_counts.items()
            }
            distances = [
                (_state_replacement_distance(terminal, extendable), extendable)
                for extendable in entry["extendable"]
            ]
            best_distance = min(distance for distance, _state in distances)
            nearest = [
                state for distance, state in distances if distance == best_distance
            ]
            nearest_example = nearest[0]
            changed_rows = _changed_row_payload(terminal, nearest_example)
            min_replacements[best_distance] += 1
            nearest_counts[len(nearest)] += 1
            changed_row_counts[len(changed_rows)] += 1
            class_distances.append(best_distance)
            nearest_transition_count += len(nearest)

            for extendable in nearest:
                nearest_changed_rows = _changed_row_payload(terminal, extendable)
                if len(nearest_changed_rows) != 1:
                    raise AssertionError(
                        "nearest transition changed more than one row: "
                        f"{nearest_changed_rows!r}"
                    )
                changed_row = nearest_changed_rows[0]
                removed = changed_row["removed"]
                added = changed_row["added"]
                if len(removed) != 1 or len(added) != 1:
                    raise AssertionError(
                        f"nearest transition is not one-for-one: {changed_row!r}"
                    )
                center = changed_row["center"]
                removed_label = removed[0]
                added_label = added[0]
                changed_center_counts[center] += 1
                changed_center_orbit_counts[_center_orbit_key(center)] += 1
                changed_center_removed_added_counts[
                    f"{center}:{removed_label}->{added_label}"
                ] += 1
                replacement_side_counts[
                    _replacement_side(center, removed_label, added_label)
                ] += 1
                extendable_eighth_counts = _state_eighth_center_counts(
                    extendable,
                    options,
                )
                ok_center_count = sum(
                    status_counts["ok"] > 0
                    for status_counts in extendable_eighth_counts.values()
                )
                ok_row_count = sum(
                    status_counts["ok"]
                    for status_counts in extendable_eighth_counts.values()
                )
                extendable_ok_center_counts[ok_center_count] += 1
                extendable_ok_row_counts[ok_row_count] += 1
                opened_centers = [
                    int(center)
                    for center, status_counts in sorted(
                        extendable_eighth_counts.items(),
                        key=lambda item: int(item[0]),
                    )
                    if status_counts["ok"] > 0
                ]
                opened_center_instance_count += len(opened_centers)
                relation_parts = []
                if added_label in opened_centers:
                    relation_parts.append("added_opened")
                if removed_label in opened_centers:
                    relation_parts.append("removed_opened")
                if not relation_parts:
                    relation_parts.append("neither_opened")
                opened_contains_replacement_label_counts["+".join(relation_parts)] += 1

                transition_prior_statuses: Counter[str] = Counter()
                changed_center_orbit = _center_orbit_key(center)
                for opened_center in opened_centers:
                    prior_status = terminal_prior_status_by_center.get(
                        opened_center,
                        "not_legal",
                    )
                    opened_center_counts[opened_center] += 1
                    opened_center_orbit_counts[_center_orbit_key(opened_center)] += 1
                    opened_center_prior_status_counts[prior_status] += 1
                    transition_prior_statuses[prior_status] += 1
                    changed_to_opened_center_orbit_counts[
                        f"{changed_center_orbit}->{_center_orbit_key(opened_center)}"
                    ] += 1
                    replacement_side = _replacement_side(
                        center,
                        removed_label,
                        added_label,
                    )
                    replacement_side_to_opened_prior_status_counts[
                        f"{replacement_side}->{prior_status}"
                    ] += 1
                    if prior_status == "not_legal":
                        not_legal_opened_instance_count += 1
                        terminal_changed_row = dict(terminal)[center]
                        extendable_changed_row = dict(extendable)[center]
                        switch_profile = _not_legal_opened_paircross_profile(
                            terminal,
                            extendable,
                            opened_center,
                            center,
                            terminal_changed_row,
                            extendable_changed_row,
                            options,
                        )
                        not_legal_opened_center_counts[opened_center] += 1
                        not_legal_opened_center_orbit_counts[
                            _center_orbit_key(opened_center)
                        ] += 1
                        not_legal_opened_changed_center_orbit_counts[
                            changed_center_orbit
                        ] += 1
                        not_legal_opened_replacement_side_counts[replacement_side] += 1
                        not_legal_opened_paircross_profile_counts[
                            "before_paircross="
                            f"{switch_profile['before_paircross']};"
                            "after_paircross="
                            f"{switch_profile['after_paircross']};"
                            f"after_valid={switch_profile['after_valid']}"
                        ] += 1
                        not_legal_opened_before_relation_counts.update(
                            switch_profile["before_changed_row_relations"]
                        )
                        not_legal_opened_after_relation_counts.update(
                            switch_profile["after_changed_row_relations"]
                        )
                        not_legal_opened_before_removed_endpoint_counts.update(
                            switch_profile["before_forbidden_overlap_removed_endpoint"]
                        )
                        not_legal_opened_noncrossing_arc_counts.update(
                            switch_profile["noncrossing_target_arcs"]
                        )
                        not_legal_opened_noncrossing_switch_counts.update(
                            switch_profile["noncrossing_switches"]
                        )
                        not_legal_opened_noncrossing_source_target_counts.update(
                            switch_profile["noncrossing_source_targets"]
                        )
                        not_legal_opened_three_or_more_switch_counts.update(
                            switch_profile["three_or_more_switches"]
                        )
                        not_legal_opened_crossing_creation_mechanism_counts.update(
                            switch_profile["crossing_creation_mechanisms"]
                        )
                        not_legal_opened_noncrossing_substitution_arc_counts.update(
                            switch_profile["noncrossing_substitution_arcs"]
                        )
                        not_legal_opened_substitution_layer_arc_counts.update(
                            switch_profile["substitution_layer_arcs"]
                        )
                        not_legal_opened_opposite_arc_paircross_context_counts.update(
                            switch_profile["opposite_arc_paircross_contexts"]
                        )
                        not_legal_opened_opposite_arc_paircross_blocker_counts.update(
                            switch_profile["opposite_arc_paircross_blocker_counts"]
                        )
                        not_legal_opened_opposite_arc_paircross_blocker_kind_counts.update(
                            switch_profile["opposite_arc_paircross_blocker_kinds"]
                        )
                        not_legal_opened_opposite_arc_paircross_blocker_role_counts.update(
                            switch_profile["opposite_arc_paircross_blocker_roles"]
                        )
                        not_legal_opened_opposite_arc_paircross_blocker_center_orbit_counts.update(
                            switch_profile[
                                "opposite_arc_paircross_blocker_center_orbits"
                            ]
                        )
                        not_legal_opened_opposite_arc_paircross_blocker_source_target_counts.update(
                            switch_profile[
                                "opposite_arc_paircross_blocker_source_targets"
                            ]
                        )
                        not_legal_opened_noncrossing_substitution_target_counts.update(
                            switch_profile["noncrossing_substitution_targets"]
                        )
                        not_legal_opened_noncrossing_deletion_target_counts.update(
                            switch_profile["noncrossing_deletion_targets"]
                        )
                        not_legal_opened_three_or_more_deletion_target_counts.update(
                            switch_profile["three_or_more_deletion_targets"]
                        )
                opened_center_prior_status_by_transition[
                    ";".join(
                        f"{status}:{transition_prior_statuses[status]}"
                        for status in sorted(transition_prior_statuses)
                    )
                ] += 1

            by_terminal.append(
                {
                    "triple_profile": key,
                    "terminal": [_record_payload(record) for record in terminal],
                    "min_replacements": best_distance,
                    "nearest_extendable_count": len(nearest),
                    "example_extendable": [
                        _record_payload(record) for record in nearest_example
                    ],
                    "example_changed_rows": changed_rows,
                }
            )

        class_summary[key] = {
            "terminal_states": len(entry["terminal"]),
            "extendable_states": len(entry["extendable"]),
            "min_replacements_by_terminal": class_distances,
        }

    return {
        "terminal_clean_seven_states": len(terminal_audits),
        "terminal_triple_profile_classes": len(class_summary),
        "terminal_states_with_nearest_extendable": len(by_terminal),
        "min_replacement_distribution": _json_counter(min_replacements),
        "nearest_transition_count": nearest_transition_count,
        "nearest_extendable_count_distribution": _json_counter(nearest_counts),
        "changed_row_count_distribution_for_first_nearest": _json_counter(
            changed_row_counts
        ),
        "changed_center_distribution": _json_counter(changed_center_counts),
        "changed_center_orbit_distribution": {
            key: int(changed_center_orbit_counts[key])
            for key in sorted(changed_center_orbit_counts)
        },
        "changed_center_removed_added_distribution": {
            key: int(changed_center_removed_added_counts[key])
            for key in sorted(changed_center_removed_added_counts)
        },
        "replacement_side_distribution": {
            key: int(replacement_side_counts[key])
            for key in sorted(replacement_side_counts)
        },
        "extendable_ok_center_count_distribution": _json_counter(
            extendable_ok_center_counts
        ),
        "extendable_ok_row_count_distribution": _json_counter(extendable_ok_row_counts),
        "opened_center_instance_count": opened_center_instance_count,
        "opened_center_distribution": _json_counter(opened_center_counts),
        "opened_center_orbit_distribution": {
            key: int(opened_center_orbit_counts[key])
            for key in sorted(opened_center_orbit_counts)
        },
        "opened_center_prior_status_distribution": {
            key: int(opened_center_prior_status_counts[key])
            for key in sorted(opened_center_prior_status_counts)
        },
        "opened_center_prior_status_by_transition": {
            key: int(opened_center_prior_status_by_transition[key])
            for key in sorted(opened_center_prior_status_by_transition)
        },
        "opened_contains_replacement_label_distribution": {
            key: int(opened_contains_replacement_label_counts[key])
            for key in sorted(opened_contains_replacement_label_counts)
        },
        "changed_to_opened_center_orbit_distribution": {
            key: int(changed_to_opened_center_orbit_counts[key])
            for key in sorted(changed_to_opened_center_orbit_counts)
        },
        "replacement_side_to_opened_prior_status_distribution": {
            key: int(replacement_side_to_opened_prior_status_counts[key])
            for key in sorted(replacement_side_to_opened_prior_status_counts)
        },
        "not_legal_opened_instance_count": not_legal_opened_instance_count,
        "not_legal_opened_center_distribution": _json_counter(
            not_legal_opened_center_counts
        ),
        "not_legal_opened_center_orbit_distribution": {
            key: int(not_legal_opened_center_orbit_counts[key])
            for key in sorted(not_legal_opened_center_orbit_counts)
        },
        "not_legal_opened_changed_center_orbit_distribution": {
            key: int(not_legal_opened_changed_center_orbit_counts[key])
            for key in sorted(not_legal_opened_changed_center_orbit_counts)
        },
        "not_legal_opened_replacement_side_distribution": {
            key: int(not_legal_opened_replacement_side_counts[key])
            for key in sorted(not_legal_opened_replacement_side_counts)
        },
        "not_legal_opened_paircross_profile_distribution": {
            key: int(not_legal_opened_paircross_profile_counts[key])
            for key in sorted(not_legal_opened_paircross_profile_counts)
        },
        "not_legal_opened_before_changed_row_relation_distribution": {
            key: int(not_legal_opened_before_relation_counts[key])
            for key in sorted(not_legal_opened_before_relation_counts)
        },
        "not_legal_opened_after_changed_row_relation_distribution": {
            key: int(not_legal_opened_after_relation_counts[key])
            for key in sorted(not_legal_opened_after_relation_counts)
        },
        "not_legal_opened_before_forbidden_overlap_removed_endpoint_distribution": {
            key: int(not_legal_opened_before_removed_endpoint_counts[key])
            for key in sorted(not_legal_opened_before_removed_endpoint_counts)
        },
        "not_legal_opened_noncrossing_target_arc_distribution": {
            key: int(not_legal_opened_noncrossing_arc_counts[key])
            for key in sorted(not_legal_opened_noncrossing_arc_counts)
        },
        "not_legal_opened_noncrossing_switch_distribution": {
            key: int(not_legal_opened_noncrossing_switch_counts[key])
            for key in sorted(not_legal_opened_noncrossing_switch_counts)
        },
        "not_legal_opened_noncrossing_source_target_distribution": {
            key: int(not_legal_opened_noncrossing_source_target_counts[key])
            for key in sorted(not_legal_opened_noncrossing_source_target_counts)
        },
        "not_legal_opened_three_or_more_switch_distribution": {
            key: int(not_legal_opened_three_or_more_switch_counts[key])
            for key in sorted(not_legal_opened_three_or_more_switch_counts)
        },
        "not_legal_opened_crossing_creation_mechanism_distribution": {
            key: int(not_legal_opened_crossing_creation_mechanism_counts[key])
            for key in sorted(not_legal_opened_crossing_creation_mechanism_counts)
        },
        "not_legal_opened_noncrossing_substitution_arc_distribution": {
            key: int(not_legal_opened_noncrossing_substitution_arc_counts[key])
            for key in sorted(not_legal_opened_noncrossing_substitution_arc_counts)
        },
        "not_legal_opened_substitution_layer_arc_distribution": {
            key: int(not_legal_opened_substitution_layer_arc_counts[key])
            for key in sorted(not_legal_opened_substitution_layer_arc_counts)
        },
        "not_legal_opened_opposite_arc_paircross_context_distribution": {
            key: int(not_legal_opened_opposite_arc_paircross_context_counts[key])
            for key in sorted(not_legal_opened_opposite_arc_paircross_context_counts)
        },
        "not_legal_opened_opposite_arc_paircross_blocker_count_distribution": (
            _json_counter(not_legal_opened_opposite_arc_paircross_blocker_counts)
        ),
        "not_legal_opened_opposite_arc_paircross_blocker_kind_distribution": {
            key: int(not_legal_opened_opposite_arc_paircross_blocker_kind_counts[key])
            for key in sorted(
                not_legal_opened_opposite_arc_paircross_blocker_kind_counts
            )
        },
        "not_legal_opened_opposite_arc_paircross_blocker_role_distribution": {
            key: int(not_legal_opened_opposite_arc_paircross_blocker_role_counts[key])
            for key in sorted(
                not_legal_opened_opposite_arc_paircross_blocker_role_counts
            )
        },
        "not_legal_opened_opposite_arc_paircross_blocker_center_orbit_distribution": {
            key: int(
                not_legal_opened_opposite_arc_paircross_blocker_center_orbit_counts[key]
            )
            for key in sorted(
                not_legal_opened_opposite_arc_paircross_blocker_center_orbit_counts
            )
        },
        "not_legal_opened_opposite_arc_paircross_blocker_source_target_distribution": {
            key: int(
                not_legal_opened_opposite_arc_paircross_blocker_source_target_counts[
                    key
                ]
            )
            for key in sorted(
                not_legal_opened_opposite_arc_paircross_blocker_source_target_counts
            )
        },
        "not_legal_opened_noncrossing_substitution_target_distribution": {
            key: int(not_legal_opened_noncrossing_substitution_target_counts[key])
            for key in sorted(not_legal_opened_noncrossing_substitution_target_counts)
        },
        "not_legal_opened_noncrossing_deletion_target_distribution": {
            key: int(not_legal_opened_noncrossing_deletion_target_counts[key])
            for key in sorted(not_legal_opened_noncrossing_deletion_target_counts)
        },
        "not_legal_opened_three_or_more_deletion_target_distribution": {
            key: int(not_legal_opened_three_or_more_deletion_target_counts[key])
            for key in sorted(not_legal_opened_three_or_more_deletion_target_counts)
        },
        "class_summary": class_summary,
        "by_terminal": by_terminal,
    }


def _orbit_count(states: set[RowRecord] | set[SixState]) -> tuple[int, Counter[int]]:
    seen: set[Any] = set()
    sizes: Counter[int] = Counter()
    for state in sorted(states):
        if state in seen:
            continue
        if state and isinstance(state[0], int):
            orbit = {state, _block_swap_row(state)}  # type: ignore[arg-type]
        else:
            orbit = {state, _block_swap_six_state(state)}  # type: ignore[arg-type]
        seen.update(orbit)
        sizes[len(orbit)] += 1
    return sum(sizes.values()), sizes


def survivor_payload() -> dict[str, Any]:
    """Classify all legal sixth rows after every clean fifth-row state."""

    assigned, pair_counts, indegrees = _initial_state()
    options = _options()
    clean_fifth_rows: set[RowRecord] = set()
    ordered_sixth_status: Counter[str] = Counter()
    by_fifth_center: dict[str, Counter[str]] = {}
    clean_fifth_with_clean_sixth = 0
    clean_six_states: set[SixState] = set()
    first_clean_sixth_example: dict[str, Any] | None = None

    for fifth_center in range(N):
        if fifth_center in assigned:
            continue
        for fifth_row in _valid_options(
            fifth_center,
            options,
            assigned,
            pair_counts,
            indegrees,
        ):
            _add_row(assigned, pair_counts, indegrees, fifth_center, fifth_row)
            fifth_status, _edge_count = _partial_vertex_circle_status(assigned)
            if fifth_status == "ok":
                fifth_record = (fifth_center, tuple(fifth_row))
                clean_fifth_rows.add(fifth_record)
                center_counts = by_fifth_center.setdefault(
                    str(fifth_center),
                    Counter({"clean_fifth": 0}),
                )
                center_counts["clean_fifth"] += 1
                local_clean_sixth = 0

                for sixth_center in range(N):
                    if sixth_center in assigned:
                        continue
                    for sixth_row in _valid_options(
                        sixth_center,
                        options,
                        assigned,
                        pair_counts,
                        indegrees,
                    ):
                        _add_row(
                            assigned,
                            pair_counts,
                            indegrees,
                            sixth_center,
                            sixth_row,
                        )
                        sixth_status, _edge_count = _partial_vertex_circle_status(
                            assigned
                        )
                        _remove_row(
                            assigned,
                            pair_counts,
                            indegrees,
                            sixth_center,
                            sixth_row,
                        )

                        ordered_sixth_status[sixth_status] += 1
                        center_counts["sixth_total"] += 1
                        center_counts[f"sixth_{sixth_status}"] += 1
                        if sixth_status == "ok":
                            local_clean_sixth += 1
                            six_state: SixState = tuple(
                                sorted((fifth_record, (sixth_center, tuple(sixth_row))))
                            )  # type: ignore[assignment]
                            clean_six_states.add(six_state)
                            if first_clean_sixth_example is None:
                                first_clean_sixth_example = {
                                    "fifth": {
                                        "center": fifth_center,
                                        "row": list(fifth_row),
                                    },
                                    "sixth": {
                                        "center": sixth_center,
                                        "row": list(sixth_row),
                                    },
                                }
                if local_clean_sixth:
                    clean_fifth_with_clean_sixth += 1
            _remove_row(assigned, pair_counts, indegrees, fifth_center, fifth_row)

    clean_fifth_orbits, clean_fifth_orbit_sizes = _orbit_count(clean_fifth_rows)
    clean_six_orbits, clean_six_orbit_sizes = _orbit_count(clean_six_states)
    clean_by_center_pair: Counter[CenterPair] = Counter(
        tuple(sorted((state[0][0], state[1][0]))) for state in clean_six_states
    )
    clean_by_center_pair_orbit: Counter[str] = Counter()
    for center_pair, count in clean_by_center_pair.items():
        clean_by_center_pair_orbit[_center_pair_orbit_key(center_pair)] += count
    low_support_seventh_audit, low_support_clean_seven_states = (
        _low_support_seventh_extension_scan(clean_six_states)
    )
    low_support_eighth_audit, low_support_terminal_audits = (
        _low_support_eighth_extension_audit(low_support_clean_seven_states)
    )
    totals = {
        "clean_fifth_rows": len(clean_fifth_rows),
        "clean_fifth_block_swap_orbits": clean_fifth_orbits,
        "ordered_legal_sixth_rows_after_clean_fifth": sum(
            ordered_sixth_status.values()
        ),
        "ordered_clean_sixth_rows": int(ordered_sixth_status["ok"]),
        "ordered_self_edge_sixth_rows": int(ordered_sixth_status["self_edge"]),
        "ordered_strict_cycle_sixth_rows": int(ordered_sixth_status["strict_cycle"]),
        "clean_fifth_rows_with_clean_sixth": clean_fifth_with_clean_sixth,
        "unique_clean_six_row_states": len(clean_six_states),
        "unique_clean_six_row_block_swap_orbits": clean_six_orbits,
        "clean_center_pairs": len(clean_by_center_pair),
        "clean_center_pair_block_swap_orbits": len(clean_by_center_pair_orbit),
    }

    return {
        "schema": "erdos97.block6_fragile_sixth_row_survivor_catalog.v1",
        "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
        "claim_scope": (
            "Legal sixth rows after clean one-row extensions of the two-block "
            "block-6 fragile rows, plus legal seventh rows after the two "
            "minimum-support six-row center pairs and legal eighth rows after "
            "the resulting clean seven-row states, in the natural cyclic "
            "order; not a proof of Erdos Problem #97 and not a counterexample."
        ),
        "fixed_centers": sorted(assigned),
        "totals": totals,
        "ordered_sixth_status_counts": {
            status: int(ordered_sixth_status[status]) for status in STATUSES
        },
        "clean_fifth_block_swap_orbit_sizes": _json_counter(clean_fifth_orbit_sizes),
        "clean_six_block_swap_orbit_sizes": _json_counter(clean_six_orbit_sizes),
        "clean_by_center_pair": {
            _center_pair_key(center_pair): int(clean_by_center_pair[center_pair])
            for center_pair in sorted(clean_by_center_pair)
        },
        "clean_by_center_pair_orbit": {
            key: int(clean_by_center_pair_orbit[key])
            for key in sorted(clean_by_center_pair_orbit)
        },
        "low_support_row_content_forms": _low_support_row_content_forms(
            clean_six_states
        ),
        "low_support_seventh_extension_audit": low_support_seventh_audit,
        "low_support_eighth_extension_audit": low_support_eighth_audit,
        "low_support_terminal_seven_state_classification": (
            _low_support_terminal_classification(low_support_terminal_audits)
        ),
        "low_support_terminal_eighth_center_audit": (
            _low_support_terminal_eighth_center_audit(low_support_terminal_audits)
        ),
        "low_support_profile_terminality_audit": (
            _low_support_profile_terminality_audit(
                low_support_clean_seven_states,
                low_support_terminal_audits,
            )
        ),
        "low_support_triple_profile_terminality_audit": (
            _low_support_triple_profile_terminality_audit(
                low_support_clean_seven_states,
                low_support_terminal_audits,
            )
        ),
        "low_support_terminal_edit_distance_audit": (
            _low_support_terminal_edit_distance_audit(
                low_support_clean_seven_states,
                low_support_terminal_audits,
            )
        ),
        "by_fifth_center": {
            center: {key: int(counter[key]) for key in sorted(counter)}
            for center, counter in sorted(
                by_fifth_center.items(), key=lambda item: int(item[0])
            )
        },
        "first_clean_sixth_example": first_clean_sixth_example,
    }


def assert_expected(payload: Mapping[str, Any]) -> None:
    if payload["status"] != "REVIEW_PENDING_DIAGNOSTIC_ONLY":
        raise AssertionError("unexpected status")
    if "not a proof" not in payload["claim_scope"]:
        raise AssertionError("claim scope lost no-proof note")
    if payload["totals"] != EXPECTED_TOTALS:
        raise AssertionError(f"unexpected totals: {payload['totals']!r}")
    if payload["clean_six_block_swap_orbit_sizes"] != EXPECTED_CLEAN_SIX_ORBIT_SIZES:
        raise AssertionError(
            "unexpected clean-six orbit sizes: "
            f"{payload['clean_six_block_swap_orbit_sizes']!r}"
        )
    if payload["clean_by_center_pair"] != EXPECTED_CLEAN_BY_CENTER_PAIR:
        raise AssertionError(
            f"unexpected clean center-pair counts: {payload['clean_by_center_pair']!r}"
        )
    if payload["clean_by_center_pair_orbit"] != EXPECTED_CLEAN_BY_CENTER_PAIR_ORBIT:
        raise AssertionError(
            "unexpected center-pair orbit counts: "
            f"{payload['clean_by_center_pair_orbit']!r}"
        )
    if (
        payload["low_support_row_content_forms"]
        != EXPECTED_LOW_SUPPORT_ROW_CONTENT_FORMS
    ):
        raise AssertionError(
            "unexpected low-support row-content normal forms: "
            f"{payload['low_support_row_content_forms']!r}"
        )
    if (
        payload["low_support_seventh_extension_audit"]
        != EXPECTED_LOW_SUPPORT_SEVENTH_AUDIT
    ):
        raise AssertionError(
            "unexpected low-support seventh-extension audit: "
            f"{payload['low_support_seventh_extension_audit']!r}"
        )
    if (
        payload["low_support_eighth_extension_audit"]
        != EXPECTED_LOW_SUPPORT_EIGHTH_AUDIT
    ):
        raise AssertionError(
            "unexpected low-support eighth-extension audit: "
            f"{payload['low_support_eighth_extension_audit']!r}"
        )
    if (
        payload["low_support_terminal_seven_state_classification"]
        != EXPECTED_LOW_SUPPORT_TERMINAL_CLASSIFICATION
    ):
        raise AssertionError(
            "unexpected low-support terminal classification: "
            f"{payload['low_support_terminal_seven_state_classification']!r}"
        )
    if (
        payload["low_support_profile_terminality_audit"]
        != EXPECTED_LOW_SUPPORT_PROFILE_TERMINALITY_AUDIT
    ):
        raise AssertionError(
            "unexpected low-support profile terminality audit: "
            f"{payload['low_support_profile_terminality_audit']!r}"
        )
    terminal_center_audit = payload["low_support_terminal_eighth_center_audit"]
    for key, expected in EXPECTED_LOW_SUPPORT_TERMINAL_EIGHTH_CENTER_AUDIT.items():
        if terminal_center_audit[key] != expected:
            raise AssertionError(
                f"unexpected low-support terminal eighth-center {key}: "
                f"{terminal_center_audit[key]!r}"
            )
    triple_profile_audit = payload["low_support_triple_profile_terminality_audit"]
    expected_triple_profile = EXPECTED_LOW_SUPPORT_TRIPLE_PROFILE_TERMINALITY_AUDIT
    for key, expected in expected_triple_profile.items():
        if triple_profile_audit[key] != expected:
            raise AssertionError(
                f"unexpected low-support triple/profile {key}: "
                f"{triple_profile_audit[key]!r}"
            )
    edit_distance_audit = payload["low_support_terminal_edit_distance_audit"]
    for key, expected in EXPECTED_LOW_SUPPORT_TERMINAL_EDIT_DISTANCE_AUDIT.items():
        if edit_distance_audit[key] != expected:
            raise AssertionError(
                f"unexpected low-support terminal edit-distance {key}: "
                f"{edit_distance_audit[key]!r}"
            )
    if payload["by_fifth_center"] != EXPECTED_BY_FIFTH_CENTER:
        raise AssertionError(
            f"unexpected by-fifth-center counts: {payload['by_fifth_center']!r}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print full JSON payload")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert the current expected survivor counts",
    )
    args = parser.parse_args()

    payload = survivor_payload()
    if args.assert_expected:
        assert_expected(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        totals = payload["totals"]
        eighth = payload["low_support_eighth_extension_audit"]
        print("block6 fragile sixth-row survivor catalog")
        print(
            "totals: "
            f"clean_fifth={totals['clean_fifth_rows']} "
            f"ordered_sixth={totals['ordered_legal_sixth_rows_after_clean_fifth']} "
            f"ordered_clean_sixth={totals['ordered_clean_sixth_rows']} "
            f"unique_clean_six={totals['unique_clean_six_row_states']}"
        )
        print(
            "low-support eighth audit: "
            f"clean_seven={eighth['clean_seven_states']} "
            f"clean_eighth={eighth['ordered_clean_eighth_rows']} "
            f"terminal_seven={eighth['terminal_clean_seven_states']}"
        )
        if args.assert_expected:
            print("OK: block6 sixth-row survivor catalog matched expected counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
