from __future__ import annotations

import json
from pathlib import Path

import pytest

from erdos97.kalmanson_equilateral_hinge import (
    dihedral_orientations,
    find_core_hinge_instances,
    find_hinge_instances,
)

ROOT = Path(__file__).resolve().parents[1]
COMPRESSION_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_kalmanson_three_row_core_compression.json"
)


def test_direct_k2_hinge_and_explanation() -> None:
    rows = {
        10: [20, 30],
        20: [10, 30],
        30: [],
        40: [10, 20],
    }

    instances = find_hinge_instances(rows, [10, 20, 30, 40])

    assert len(instances) == 1
    hinge = instances[0]
    assert (hinge.a, hinge.b, hinge.c, hinge.d) == (10, 20, 30, 40)
    assert hinge.centers == (10, 20, 40)
    assert hinge.required_pairs == ((20, 30), (10, 30), (10, 20))
    assert hinge.kind == hinge.inequality_kind == "K2"
    assert hinge.left_pairs == ((10, 40), (20, 30))
    assert hinge.right_pairs == ((10, 30), (20, 40))
    assert hinge.equalities == (
        ((10, 20), (10, 30)),
        ((10, 20), (20, 30)),
        ((10, 40), (20, 40)),
    )
    assert hinge.as_dict()["inequality_kind"] == "K2"


def test_dihedral_orientation_can_present_the_hinge_as_k1() -> None:
    # This is the generic hinge at (A,B,C,D)=(1,2,3,0), a rotation of the
    # stored cyclic quadruple (0,1,2,3).  Its K2 is stored K1.
    rows = [[1, 2], [2, 3], [1, 3], []]

    instances = find_hinge_instances(rows, [0, 1, 2, 3])

    assert len(dihedral_orientations((0, 1, 2, 3))) == 8
    assert len(set(dihedral_orientations((0, 1, 2, 3)))) == 8
    assert len(instances) == 1
    hinge = instances[0]
    assert (hinge.a, hinge.b, hinge.c, hinge.d) == (1, 2, 3, 0)
    assert hinge.centers == (1, 2, 0)
    assert hinge.inequality_kind == "K1"
    assert hinge.left_pairs == ((0, 1), (2, 3))
    assert hinge.right_pairs == ((0, 2), (1, 3))


def test_missing_required_pair_or_center_excludes_a_hinge() -> None:
    rows = [[1, 2], [0, 2], [], [0]]
    assert find_hinge_instances(rows, [0, 1, 2, 3]) == ()

    complete_rows = [[1, 2], [0, 2], [], [0, 1]]
    assert find_core_hinge_instances(complete_rows, [0, 1, 2, 3], [0, 1, 2]) == ()


def test_record_zero_best_core_has_one_dihedral_hinge() -> None:
    payload = json.loads(COMPRESSION_ARTIFACT.read_text(encoding="utf-8"))
    record = payload["records"][0]

    instances = find_core_hinge_instances(
        record["rows"],
        record["best_kalmanson_self_edge"]["quadrilateral"],
        record["best_kalmanson_minimal_core"]["row_indices"],
    )

    assert len(instances) == 1
    hinge = instances[0]
    assert (hinge.a, hinge.b, hinge.c, hinge.d) == (1, 2, 7, 0)
    assert hinge.centers == (1, 2, 0)
    assert hinge.inequality_kind == record["best_kalmanson_self_edge"]["kind"] == "K1"


@pytest.mark.parametrize(
    ("call", "error"),
    [
        (lambda: dihedral_orientations([0, 1, 2]), ValueError),
        (lambda: dihedral_orientations([0, 1, 2, 2]), ValueError),
        (lambda: dihedral_orientations([0, 1, 2, True]), TypeError),
        (lambda: find_hinge_instances([], [0, 1, 1, 2]), ValueError),
        (lambda: find_hinge_instances({0: [1], 4: []}, [0, 1, 2, 3]), ValueError),
        (lambda: find_hinge_instances({0: [4]}, [0, 1, 2, 3]), ValueError),
        (lambda: find_hinge_instances({0: [0]}, [0, 1, 2, 3]), ValueError),
        (lambda: find_hinge_instances({0: [1, 1]}, [0, 1, 2, 3]), ValueError),
        (lambda: find_hinge_instances({0: [True]}, [0, 1, 2, 3]), TypeError),
        (lambda: find_hinge_instances([[1], [0]], [0, 1, 2]), ValueError),
        (
            lambda: find_core_hinge_instances(
                [[1], [0], [], []],
                [0, 1, 2, 3],
                [0, 1],
            ),
            ValueError,
        ),
        (
            lambda: find_core_hinge_instances(
                [[1], [0], [], []],
                [0, 1, 2, 4],
                [0, 1, 2],
            ),
            ValueError,
        ),
    ],
)
def test_malformed_inputs_are_rejected(call, error) -> None:
    with pytest.raises(error):
        call()
