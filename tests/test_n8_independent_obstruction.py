"""Tests for the SymPy-free independent n=8 obstruction recheck."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from erdos97 import n8_independent_obstruction as ind


REPO_ROOT = Path(__file__).resolve().parents[1]
SURVIVOR_PATH = REPO_ROOT / "data" / "incidence" / "n8_reconstructed_15_survivors.json"


def _survivors() -> list[dict]:
    return json.loads(SURVIVOR_PATH.read_text())


def test_polynomial_arithmetic_basic() -> None:
    a = ind.p_var(0)
    b = ind.p_var(1)
    one = ind.p_const(1)
    assert ind.p_add(a, b) == {(0,): Fraction(1), (1,): Fraction(1)}
    assert ind.p_sub(a, a) == {}
    assert ind.p_mul(a, b) == {(0, 1): Fraction(1)}
    assert ind.p_mul(a, a) == {(0, 0): Fraction(1)}
    assert ind.p_add(one, ind.p_neg(one)) == {}


def test_pb_dot_polynomial_simple() -> None:
    poly = ind.pb_dot_polynomial(0, 1, 2, 3)
    expected = ind.p_sub(ind.p_var(ind.x_var(2)), ind.p_var(ind.x_var(3)))
    expected = ind.p_neg(expected)
    assert poly == expected


def test_cyclic_counts_match_expected() -> None:
    for cls in _survivors():
        cid = cls["id"]
        actual = ind.compatible_order_count(cls["rows"])
        assert actual == ind.expected_cyclic_count(cid), (
            f"class {cid}: cyclic-order count {actual} != expected "
            f"{ind.expected_cyclic_count(cid)}"
        )


def test_class12_cyclic_order_kill() -> None:
    rows = next(c["rows"] for c in _survivors() if c["id"] == 12)
    assert ind.cyclic_order_kill(rows)
    assert ind.compatible_order_count(rows) == 0


def test_y2_span_kills_expected_classes() -> None:
    expected_y2 = {0, 1, 2, 6, 7, 8, 9, 10, 11, 13}
    for cls in _survivors():
        cid = cls["id"]
        in_span = ind.y2_in_pb_span(cls["rows"])
        if cid in expected_y2:
            assert in_span, f"class {cid}: y_2 should be in PB span"
        elif cid in {3, 4, 5, 14}:
            assert not in_span, f"class {cid}: y_2 should not be in PB span"


def test_classes_independently_killed() -> None:
    killed = []
    for cls in _survivors():
        info = ind.verify_class(cls["id"], cls["rows"])
        if info.killed_by_some_independent_check:
            killed.append(cls["id"])
    assert sorted(killed) == ind.CLASSES_KILLED_INDEPENDENTLY
    assert sorted(killed) == [0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13]


def test_groebner_required_classes() -> None:
    assert ind.CLASSES_REQUIRING_GROEBNER == [3, 4, 5, 14]


def test_squared_distance_diagnostic_runs() -> None:
    for cls in _survivors():
        sd = ind.squared_distance_diagnostic(cls["rows"])
        assert sd["rank"] >= 0
        assert sd["free_d_count"] == 28 - sd["rank"]
        for chord in sd["forced_zeros"]:
            assert isinstance(chord, tuple) and len(chord) == 2


def test_first_stage_linear_identities_for_typical_classes() -> None:
    """The phi-edge (0,1) <-> (2,3) is shared by most classes; when it
    is present the linear identities x_3 = x_2 and y_3 = -y_2 lie in
    the Q-linear span of the PB polynomials."""
    expected_holds = []
    expected_skips = []
    for cls in _survivors():
        ids = ind.linear_span_identities(cls["rows"])
        if ids["x_3 - x_2"] and ids["y_3 + y_2"]:
            expected_holds.append(cls["id"])
        else:
            expected_skips.append(cls["id"])
    # Class 14 has a different incidence pattern that lacks the
    # (0,1)<->(2,3) phi-edge; first-stage linear identities do not
    # apply.  Every other class includes the identities.
    assert expected_skips == [14]
    assert expected_holds == [c["id"] for c in _survivors() if c["id"] != 14]


def test_pb_polynomials_count_doubles_phi_edges() -> None:
    """Each phi-edge contributes one dot polynomial and one bisector polynomial."""
    for cls in _survivors():
        polys = ind.pb_polynomials(cls["rows"])
        edges = ind.phi_edges(cls["rows"])
        assert len(polys) == 2 * len(edges)


def test_rank_function_basic() -> None:
    rows = [
        {0: Fraction(1), 1: Fraction(2)},
        {0: Fraction(2), 1: Fraction(4)},  # multiple of first
        {0: Fraction(0), 1: Fraction(1)},
    ]
    assert ind.rank(rows, 2) == 2


def test_polynomial_substitute() -> None:
    poly = ind.p_mul(ind.p_var(0), ind.p_var(1))
    poly = ind.p_add(poly, ind.p_const(3))
    replaced = ind.p_substitute(poly, 0, ind.p_const(2))
    assert replaced == {(1,): Fraction(2), (): Fraction(3)}


@pytest.mark.parametrize("class_id", sorted({0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13}))
def test_each_independently_killed_class(class_id: int) -> None:
    rows = next(c["rows"] for c in _survivors() if c["id"] == class_id)
    info = ind.verify_class(class_id, rows)
    assert info.killed_by_some_independent_check, (
        f"class {class_id}: expected independent kill"
    )
