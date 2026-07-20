from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pytest

import erdos97.external_exact_five_contract as exact_five
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


def test_public_audit_normalizes_crlf_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checkout = tmp_path / "external"
    expected_hashes = {}
    for relative_path, markers in exact_five.EXPECTED_MARKERS.items():
        source_lf = ("\n".join(markers) + "\n").encode()
        source_path = checkout / relative_path
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_bytes(source_lf.replace(b"\n", b"\r\n"))
        expected_hashes[relative_path] = sha256(source_lf).hexdigest()

    monkeypatch.setattr(exact_five, "_git_commit", lambda _: "fixture-commit")
    monkeypatch.setattr(exact_five, "EXPECTED_COMMIT", "fixture-commit")
    monkeypatch.setattr(
        exact_five, "EXPECTED_SOURCE_SHA256", expected_hashes
    )

    result = exact_five.audit_external_exact_five_contract(checkout)

    assert result.expected_snapshot_match
    assert not result.missing_markers
    assert result.source_sha256 == {
        path.as_posix(): digest for path, digest in expected_hashes.items()
    }
