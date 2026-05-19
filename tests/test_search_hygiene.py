from __future__ import annotations

import sys
from types import SimpleNamespace

import numpy as np
import pytest

from erdos97.search import softplus, z3_incidence_search


def test_softplus_large_positive_values_do_not_overflow() -> None:
    x = np.array([-3.0, 3.0, 1_000.0], dtype=float)

    with np.errstate(over="raise"):
        out = softplus(x)

    assert np.isfinite(out[0])
    assert np.isfinite(out[1])
    assert out[2] == x[2]


def test_z3_incidence_search_rejects_too_small_n_before_importing_z3() -> None:
    with pytest.raises(ValueError, match="requires n >= 5"):
        z3_incidence_search(4)


def test_z3_incidence_search_reports_unknown(monkeypatch) -> None:
    class FakeVar:
        def __init__(self, name: str):
            self.name = name

        def __eq__(self, other: object) -> tuple[str, object, object]:  # type: ignore[override]
            return ("eq", self, other)

    class FakeSolver:
        def add(self, *_constraints: object) -> None:
            return None

        def check(self) -> str:
            return "unknown"

        def reason_unknown(self) -> str:
            return "timeout"

    fake_z3 = SimpleNamespace(
        sat="sat",
        unsat="unsat",
        unknown="unknown",
        Bool=lambda name: FakeVar(name),
        Not=lambda value: ("not", value),
        PbEq=lambda terms, value: ("pbeq", terms, value),
        PbLe=lambda terms, value: ("pble", terms, value),
        PbGe=lambda terms, value: ("pbge", terms, value),
        And=lambda *values: ("and", values),
        Solver=FakeSolver,
    )
    monkeypatch.setitem(sys.modules, "z3", fake_z3)

    with pytest.raises(RuntimeError, match="unknown: timeout"):
        z3_incidence_search(5)
