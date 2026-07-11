"""Portable replay comparison for float-bearing diagnostic artifacts.

Stored diagnostic artifacts are replayed on multiple platforms (author
machines and CI runners) whose libm implementations differ in the last few
ulps. Claim-bearing payload semantics -- strings, integers, booleans, list
lengths, key sets, and float signs -- must still compare exactly; only the
tails of finite nonzero floats are allowed a narrow portability envelope.
A sign change or an exact-zero mismatch is treated as a semantic change.
"""

from __future__ import annotations

import math
from typing import Any


PORTABLE_FLOAT_REL_TOL = 5e-13
PORTABLE_FLOAT_ABS_TOL = 1e-17


def assert_portable_payload_equal(
    stored: Any,
    current: Any,
    *,
    path: str = "$",
) -> None:
    """Compare payload semantics exactly and diagnostic floats portably."""
    if type(stored) is not type(current):
        raise AssertionError(
            f"{path}: type mismatch ({type(stored).__name__} != "
            f"{type(current).__name__})"
        )
    if isinstance(current, dict):
        if stored.keys() != current.keys():
            missing = sorted(set(current) - set(stored))
            extra = sorted(set(stored) - set(current))
            raise AssertionError(f"{path}: key mismatch (missing={missing}, extra={extra})")
        for key in current:
            assert_portable_payload_equal(stored[key], current[key], path=f"{path}.{key}")
        return
    if isinstance(current, list):
        if len(stored) != len(current):
            raise AssertionError(f"{path}: length mismatch ({len(stored)} != {len(current)})")
        for index, (stored_item, current_item) in enumerate(zip(stored, current, strict=True)):
            assert_portable_payload_equal(
                stored_item,
                current_item,
                path=f"{path}[{index}]",
            )
        return
    if isinstance(current, float):
        if not math.isfinite(stored) or not math.isfinite(current):
            if stored != current:
                raise AssertionError(f"{path}: non-finite float mismatch")
            return
        if stored == current:
            return
        # A sign change is a semantic change even if both values are tiny.
        sign_changed = math.copysign(1.0, stored) != math.copysign(1.0, current)
        if stored == 0.0 or current == 0.0 or sign_changed:
            raise AssertionError(
                f"{path}: float sign/zero mismatch ({stored!r} != {current!r})"
            )
        if not math.isclose(
            stored,
            current,
            rel_tol=PORTABLE_FLOAT_REL_TOL,
            abs_tol=PORTABLE_FLOAT_ABS_TOL,
        ):
            raise AssertionError(f"{path}: material float mismatch ({stored!r} != {current!r})")
        return
    if stored != current:
        raise AssertionError(f"{path}: exact value mismatch ({stored!r} != {current!r})")
