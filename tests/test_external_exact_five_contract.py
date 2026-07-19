from __future__ import annotations

from erdos97.external_exact_five_contract import (
    EXPECTED_MARKERS,
    EXPECTED_SOURCE_SHA256,
    _missing_markers,
)


def test_missing_markers_is_fail_closed() -> None:
    assert _missing_markers("alpha beta", ("alpha", "gamma")) == ("gamma",)
    assert _missing_markers("alpha beta", ("alpha", "beta")) == ()


def test_every_pinned_source_has_contract_markers() -> None:
    assert set(EXPECTED_SOURCE_SHA256) == set(EXPECTED_MARKERS)
    assert all(EXPECTED_MARKERS.values())


def test_marker_inventory_has_no_duplicates() -> None:
    markers = [
        marker
        for source_markers in EXPECTED_MARKERS.values()
        for marker in source_markers
    ]
    assert len(markers) == len(set(markers))
