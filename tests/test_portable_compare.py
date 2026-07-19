"""Regression tests for portable float-bearing artifact comparisons."""

from __future__ import annotations

import math

import pytest

from erdos97.portable_compare import assert_portable_payload_equal


@pytest.mark.parametrize(
    ("stored", "current"),
    (
        (0.0, -0.0),
        (-0.0, 0.0),
        (0.0, math.ulp(0.0)),
        (-0.0, -math.ulp(0.0)),
    ),
)
def test_portable_comparison_rejects_sign_and_exact_zero_drift(
    stored: float,
    current: float,
) -> None:
    with pytest.raises(AssertionError, match="float sign/zero mismatch"):
        assert_portable_payload_equal(stored, current)


@pytest.mark.parametrize("value", (0.0, -0.0))
def test_portable_comparison_accepts_identically_signed_zero(value: float) -> None:
    assert_portable_payload_equal(value, value)
