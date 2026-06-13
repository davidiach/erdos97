"""Tests for the three-orbit quarter-cell reduction / closure checker."""

from __future__ import annotations

import importlib.util
import math
import pathlib
import sys

import pytest

SPEC = importlib.util.spec_from_file_location(
    "check_quarter_cell_closure",
    pathlib.Path(__file__).resolve().parents[1]
    / "scripts"
    / "check_quarter_cell_closure.py",
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

MS = (4, 8, 12, 16)


def test_offsets_for_satisfy_witness_equation():
    """Every offset returned by offsets_for(p, m) puts a vertex at the modelled
    witness angle: cos(phi + 2k h) = p for some integer k."""
    for m in MS:
        h = math.pi / m
        for p in (-0.3, -0.05, 0.0, 0.05, 0.3):
            for phi in MOD.offsets_for(p, m):
                assert 0.0 <= phi < 2 * h + 1e-12
                hit = min(abs(math.cos(phi + 2 * k * h) - p) for k in range(m))
                assert hit < 1e-9, (m, p, phi, hit)


def test_boundary_band_lemma():
    """The exact boundary-band confinement self-test passes for all m."""
    for m in MS:
        assert MOD.boundary_band_ok(m)


def test_boundary_band_is_geometrically_real():
    """Independently: for window radii, a vertex at squared distance 2 from
    A_0 has an offset within delta = arcsin(P(sec h)) of 0 or 2h (mod 2h)."""
    for m in MS:
        h = math.pi / m
        twoh = 2 * h
        sech = 1.0 / math.cos(h)
        omega = (sech * sech - 1) / (2 * sech)
        delta = math.asin(min(1.0, omega))
        lo, hi = math.cos(h), sech
        for i in range(25):
            y = lo + (hi - lo) * (i + 0.5) / 25
            p = (y * y - 1) / (2 * y)
            for phi in MOD.offsets_for(p, m):
                assert phi < delta + 1e-9 or phi > twoh - delta - 1e-9, (m, y, phi)


def test_small_grid_screen_nonconvex():
    """A small grid already shows every (i)&(ii) config strictly non-convex
    for m=4 and m=8 (max min-turn < 0); cheap smoke of the screen."""
    for m in (4, 8):
        rec = MOD.screen_m(m, grid=40)
        assert rec["ii_configs"] > 0
        assert rec["max_min_turn"] is not None
        assert rec["max_min_turn"] < 0, rec


@pytest.mark.slow
def test_full_screen_clear():
    """Full default-grid screen passes its reproducibility check (needs minutes)."""
    for m in MS:
        rec = MOD.screen_m(m, grid=160 if m <= 8 else 120)
        assert rec["clear"], rec
