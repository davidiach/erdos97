"""Pinned data and conservative claim scope for the orbit66 partial construction."""

from __future__ import annotations

SCHEMA = "erdos97.orbit66_exact_partial.v1"
STATUS = "EXACT_PARTIAL_CONSTRUCTION_NOT_A_COUNTEREXAMPLE"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact verification of one 66-point strictly convex C3-symmetric set. "
    "Exactly 60 vertices have maximum equal-distance multiplicity four, three "
    "have maximum multiplicity three, and three have maximum multiplicity two. "
    "The six exceptional vertices make this a partial construction, not a "
    "counterexample to Erdos Problem #97. The checker does not establish "
    "optimality, a limiting construction, or a completion mechanism."
)
FORBIDDEN_CLAIMS = (
    "a counterexample to Erdos Problem #97",
    "a proof or disproof of Erdos Problem #97",
    "an exhaustive search of the C3-orbit family",
    "this artifact has completed independent external mathematical and code review",
)
EXPECTED_DISTRIBUTION = {2: 3, 3: 3, 4: 60}
EXPECTED_AT_LEAST_FOUR = 60
EXPECTED_AT_MOST_THREE = 6
EXPECTED_POINT_COUNT = 66
EXPECTED_ORBIT_COUNT = 22
EXPECTED_CONVEXITY_TESTS = 4_224
EXPECTED_DISTINCT_PAIRS = 2_145

# Each history row is
# (first_orbit, second_orbit, second_phase, first_direction,
#  second_direction, branch), where branch 0 adds +h J(b-a) and branch 1
# adds -h J(b-a) in the exact circle-intersection formula.
HISTORY: tuple[tuple[int, int, int, str, str, int], ...] = (
    (1, 2, 1, "in", "in", 0),
    (0, 3, 0, "out", "out", 1),
    (3, 4, 0, "out", "out", 1),
    (2, 5, 2, "out", "out", 0),
    (0, 6, 0, "in", "out", 0),
    (3, 7, 1, "out", "out", 0),
    (1, 8, 0, "out", "out", 0),
    (3, 7, 2, "out", "out", 1),
    (3, 6, 0, "out", "out", 1),
    (2, 11, 2, "out", "out", 1),
    (5, 11, 0, "out", "out", 1),
    (9, 10, 0, "out", "out", 1),
    (8, 14, 1, "out", "out", 1),
    (1, 15, 2, "out", "out", 0),
    (3, 16, 2, "out", "out", 1),
    (11, 17, 0, "out", "out", 0),
    (0, 10, 1, "out", "out", 1),
    (2, 19, 1, "out", "out", 1),
    (11, 20, 2, "out", "out", 0),
)

CYCLIC_ORDER: tuple[int, ...] = (
    22,
    4,
    19,
    60,
    53,
    8,
    36,
    59,
    51,
    1,
    25,
    54,
    61,
    42,
    49,
    2,
    55,
    18,
    28,
    21,
    13,
    34,
    44,
    26,
    41,
    16,
    9,
    30,
    58,
    15,
    7,
    23,
    47,
    10,
    17,
    64,
    5,
    24,
    11,
    40,
    50,
    43,
    35,
    56,
    0,
    48,
    63,
    38,
    31,
    52,
    14,
    37,
    29,
    45,
    3,
    32,
    39,
    20,
    27,
    46,
    33,
    62,
    6,
    65,
    57,
    12,
)
