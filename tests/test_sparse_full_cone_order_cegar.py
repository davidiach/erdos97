from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from z3 import sat, unsat

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "exploration"
    / "pilot_sparse_full_cone_order_cegar.py"
)
SPEC = importlib.util.spec_from_file_location("sparse_full_cone_order_cegar", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
PILOT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PILOT
SPEC.loader.exec_module(PILOT)


C25_ESCAPE = [
    0,
    7,
    14,
    21,
    3,
    10,
    17,
    24,
    6,
    13,
    20,
    2,
    9,
    16,
    23,
    5,
    12,
    19,
    1,
    8,
    15,
    22,
    4,
    11,
    18,
]


def test_certificate_order_quads_deduplicates_and_validates() -> None:
    order = [0, 2, 1, 3, 4]
    certificate = {
        "cyclic_order": order,
        "inequalities": [
            {"quad": [0, 2, 1, 3], "kind": "K1", "weight": 1},
            {"quad": [0, 2, 1, 3], "kind": "K2", "weight": 2},
            {"quad": [2, 1, 3, 4], "kind": "K1", "weight": 1},
        ],
    }

    assert PILOT.certificate_order_quads(certificate, order) == [
        (0, 2, 1, 3),
        (2, 1, 3, 4),
    ]


def test_full_certificate_clause_blocks_the_supported_order_family() -> None:
    solver, positions = PILOT._make_solver(5, 3)
    PILOT.add_full_certificate_clause(solver, positions, [(0, 1, 2, 3)])
    solver.push()
    solver.add(*[positions[label] == index for index, label in enumerate(range(5))])
    assert solver.check() == unsat
    solver.pop()

    allowed_order = [0, 2, 1, 3, 4]
    solver.add(*[positions[label] == index for index, label in enumerate(allowed_order)])
    assert solver.check() == sat


def test_checker_independently_replays_inverse_pair_escape() -> None:
    payload = {
        "runs": [
            {
                "pattern": "C25_sidon_2_5_9_14",
                "models": [
                    {
                        "order": C25_ESCAPE,
                        "full_kalmanson": {
                            "status": "NO_EXACT_FIXED_ORDER_CERTIFICATE_FOUND"
                        },
                    }
                ],
            }
        ]
    }

    assert PILOT.check_payload(payload) == {
        "status": "OK",
        "verified_inverse_pair_escape_orders": 1,
        "verified_exact_full_cone_certificates": 0,
    }
