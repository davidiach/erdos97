#!/usr/bin/env python3
"""Audit checker for the two-orbit dynamic-window obstruction (draft lemma).

Claim being audited (`docs/two-orbit-circulant-obstruction.md`, review
pending): a strictly convex polygon whose vertex set is two concentric
regular ``m``-gons (radii ``R`` and ``x*R``, relative rotation ``phi``)
cannot have, at every vertex, four other vertices on a circle centered at
that vertex.

The written derivation reduces the claim to: ``phi`` is forced to the exact
half-step ``h = pi/m``; each first-orbit row is forced to consist of one
same-orbit pair ``{A_{+a}, A_{-a}}`` and one cross-orbit pair with odd offset
``p``; and the resulting radius-ratio equation

    x^2 - 2*x*cos(p*h) + 1 - 4*sin(a*h)^2 = 0

must have a root in the strict-convexity window ``(cos h, sec h)``.  This
script verifies, for every ``m`` up to ``--max-m`` and every valid pair
``(a, p)``, that no root lies in the open window.  Two redundant tests are
used and must agree:

1. root-location: both quadratic roots are outside ``(cos h, sec h)``;
2. interval form: ``T = cos(2rh) + cos(2(r+1)h) - 2*cos(2ah)`` with
   ``p = 2r + 1`` is outside the open interval
   ``(-sin(h)^2, (1 - 2*cos(2ah)) * sin(h)^2)``.

Borderline values (within ``1e-30`` of zero at 60-digit precision) are
escalated to exact sympy zero-equivalence checks; the only equality cases
expected are exact window-boundary hits, which are excluded by strictness.

This checker is an audit aid for a review-pending lemma draft about one
restricted configuration family. It is not a proof of Erdos Problem #97 and
it does not produce or certify any counterexample.
"""

from __future__ import annotations

import argparse
import json
import sys

import mpmath as mp

mp.mp.dps = 60

BORDER = mp.mpf("1e-30")


def exact_sign(value: mp.mpf, m: int, a: int, p: int, which: str) -> int:
    """Return the sign of a borderline quantity via exact sympy arithmetic."""

    import sympy as sp

    h = sp.pi / m
    x_low = sp.cos(h)
    x_high = 1 / sp.cos(h)
    target = 4 * sp.sin(a * h) ** 2
    if which == "low":
        expr = target - (x_low**2 + 1 - 2 * x_low * sp.cos(p * h))
    else:
        expr = (x_high**2 + 1 - 2 * x_high * sp.cos(p * h)) - target
    simplified = sp.simplify(sp.expand_trig(expr))
    if simplified == 0 or sp.simplify(simplified) == 0:
        return 0
    sign = simplified.evalf(80)
    if sign > 0:
        return 1
    if sign < 0:
        return -1
    raise RuntimeError(f"could not resolve sign for m={m} a={a} p={p} {which}")


def window_root_exists(m: int, a: int, p: int) -> tuple[bool, int]:
    """Return (root in open window?, boundary hits) for one (m, a, p)."""

    h = mp.pi / m
    x_low = mp.cos(h)
    x_high = 1 / mp.cos(h)
    target = 4 * mp.sin(a * h) ** 2

    def g(x: mp.mpf) -> mp.mpf:
        return x * x + 1 - 2 * x * mp.cos(p * h)

    # g is strictly increasing on the window because x > cos h >= cos(p h),
    # so a root lies in the open window iff g(x_low) < target < g(x_high).
    low_gap = target - g(x_low)
    high_gap = g(x_high) - target
    boundary = 0
    if abs(low_gap) < BORDER:
        sign = exact_sign(low_gap, m, a, p, "low")
        if sign == 0:
            boundary += 1
        low_inside = sign > 0
    else:
        low_inside = low_gap > 0
    if abs(high_gap) < BORDER:
        sign = exact_sign(high_gap, m, a, p, "high")
        if sign == 0:
            boundary += 1
        high_inside = sign > 0
    else:
        high_inside = high_gap > 0
    return (low_inside and high_inside), boundary


def interval_form_root_exists(m: int, a: int, p: int) -> bool:
    """Equivalent T-interval formulation; must agree with the root test."""

    h = mp.pi / m
    r = (p - 1) // 2
    t_value = mp.cos(2 * r * h) + mp.cos(2 * (r + 1) * h) - 2 * mp.cos(2 * a * h)
    lower = -mp.sin(h) ** 2
    upper = (1 - 2 * mp.cos(2 * a * h)) * mp.sin(h) ** 2
    if abs(t_value - lower) < BORDER or abs(t_value - upper) < BORDER:
        # Boundary hit: handled exactly by the root test escalation; the
        # open interval excludes exact boundaries.
        return False
    return lower < t_value < upper


def valid_pairs(m: int) -> list[tuple[int, int]]:
    a_max = (m - 1) // 2
    p_max = m - 1 if m % 2 == 0 else m - 2
    return [(a, p) for a in range(1, a_max + 1) for p in range(1, p_max + 1, 2)]


FAST_BAND = 1e-9


def _fast_screen(m: int) -> list[tuple[int, int]]:
    """Float64 screen; returns pairs needing slow (mpmath/sympy) handling.

    A pair needs slow handling when it either looks like a window root or
    sits within ``FAST_BAND`` of an endpoint, or when the two formulations
    disagree at float precision.
    """

    import numpy as np

    a_max = (m - 1) // 2
    p_max = m - 1 if m % 2 == 0 else m - 2
    if a_max < 1 or p_max < 1:
        return []
    h = np.pi / m
    a = np.arange(1, a_max + 1, dtype=float)[:, None]
    p = np.arange(1, p_max + 1, 2, dtype=float)[None, :]
    x_low = np.cos(h)
    x_high = 1.0 / np.cos(h)
    target = 4.0 * np.sin(a * h) ** 2
    g_low = x_low**2 + 1.0 - 2.0 * x_low * np.cos(p * h)
    g_high = x_high**2 + 1.0 - 2.0 * x_high * np.cos(p * h)
    low_gap = target - g_low
    high_gap = g_high - target
    r = (p - 1.0) / 2.0
    t_val = np.cos(2 * r * h) + np.cos(2 * (r + 1) * h) - 2.0 * np.cos(2 * a * h)
    lower = -np.sin(h) ** 2
    upper = (1.0 - 2.0 * np.cos(2 * a * h)) * np.sin(h) ** 2
    inside_root = (low_gap > 0.0) & (high_gap > 0.0)
    inside_interval = (t_val > lower) & (t_val < upper)
    near = (
        (np.abs(low_gap) < FAST_BAND)
        | (np.abs(high_gap) < FAST_BAND)
        | (np.abs(t_val - lower) < FAST_BAND)
        | (np.abs(t_val - upper) < FAST_BAND)
    )
    suspicious = inside_root | inside_interval | near | (
        inside_root != inside_interval
    )
    rows, cols = np.nonzero(suspicious)
    return [(int(a[i, 0]), int(p[0, j])) for i, j in zip(rows, cols)]


def check_m(m: int) -> dict[str, object]:
    pairs = valid_pairs(m)
    violations: list[dict[str, int]] = []
    boundary_hits = 0
    for a, p in _fast_screen(m):
        in_window, boundary = window_root_exists(m, a, p)
        boundary_hits += boundary
        mirror = interval_form_root_exists(m, a, p)
        if in_window != mirror:
            raise RuntimeError(
                f"formulation mismatch at m={m} a={a} p={p}: "
                f"root={in_window} interval={mirror}"
            )
        if in_window:
            violations.append({"a": a, "p": p})
    return {
        "m": m,
        "pairs_checked": len(pairs),
        "window_roots": violations,
        "boundary_hits": boundary_hits,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-m", type=int, default=3)
    parser.add_argument("--max-m", type=int, default=400)
    parser.add_argument(
        "--assert-clear",
        action="store_true",
        help="exit nonzero if any (m, a, p) admits a window root",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    total_pairs = 0
    total_boundary = 0
    bad: list[dict[str, object]] = []
    for m in range(args.min_m, args.max_m + 1):
        record = check_m(m)
        total_pairs += record["pairs_checked"]
        total_boundary += record["boundary_hits"]
        if record["window_roots"]:
            bad.append(record)
    payload = {
        "tool": "scripts/check_two_orbit_dynamic_window_lemma.py",
        "scope": (
            "two concentric regular m-gons, half-step-reduced first-orbit row "
            "equation; not a proof of Erdos Problem #97 and not a "
            "counterexample search"
        ),
        "min_m": args.min_m,
        "max_m": args.max_m,
        "pairs_checked": total_pairs,
        "boundary_equality_hits": total_boundary,
        "cells_with_window_roots": bad,
        "clear": not bad,
    }
    if args.json:
        print(json.dumps(payload, indent=1, sort_keys=True))
    else:
        print(
            f"m={args.min_m}..{args.max_m}: pairs={total_pairs} "
            f"boundary_hits={total_boundary} clear={not bad}"
        )
    if args.assert_clear and bad:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
