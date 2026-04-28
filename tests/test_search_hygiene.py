from __future__ import annotations

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
