"""Guard the imported replay's portable sample contract, not its geometry."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def replay(monkeypatch):
    packet = Path(__file__).resolve().parents[1] / "incoming/radius-descent-n11-2026-09-05"
    monkeypatch.syspath_prepend(str(packet))
    spec = importlib.util.spec_from_file_location("radius_n11_replay", packet / "replay.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("n,count", [(9, 7236), (9, 7500), (11, 9906), (11, 10000)])
def test_accepts_valid_platform_dependent_samples(replay, n, count):
    replay.validate_oracle(dict(n=n, seed=970905, states_checked=count, predicate_mismatches=0), n)


@pytest.mark.parametrize("change", [
    {"n": 9}, {"seed": 1}, {"states_checked": 5999},
    {"states_checked": 11001}, {"states_checked": True},
    {"predicate_mismatches": 1}, {"predicate_mismatches": False},
])
def test_rejects_wrong_identity_incomplete_samples_and_mismatches(replay, change):
    result = dict(n=11, seed=970905, states_checked=9906, predicate_mismatches=0)
    result.update(change)
    with pytest.raises(ValueError):
        replay.validate_oracle(result, 11)
