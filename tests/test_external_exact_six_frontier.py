from __future__ import annotations

from hashlib import sha256
import json

from erdos97.external_exact_six_frontier import (
    EXPECTED_LF_SHA256,
    EXPECTED_ORBITS,
    EXPECTED_SOURCE_MARKERS,
    _lf_bytes,
    _missing_markers,
    _summarize_cut_bank,
)


def test_lf_bytes_makes_checkout_hash_line_ending_invariant() -> None:
    lf = b"alpha\nbeta\n"
    crlf = b"alpha\r\nbeta\r\n"
    assert _lf_bytes(lf) == lf
    assert _lf_bytes(crlf) == lf
    assert sha256(_lf_bytes(crlf)).digest() == sha256(lf).digest()


def test_missing_markers_is_fail_closed() -> None:
    source = EXPECTED_SOURCE_MARKERS[0]
    assert _missing_markers(source) == EXPECTED_SOURCE_MARKERS[1:]


def test_pinned_inventory_and_orbits_are_nonempty() -> None:
    assert len(EXPECTED_LF_SHA256) == 7
    assert len(EXPECTED_ORBITS) == 7
    assert all(EXPECTED_SOURCE_MARKERS)


def test_cut_bank_summary_counts_shell_conditioning(tmp_path) -> None:
    path = tmp_path / "cuts.jsonl"
    records = [
        {"constraints": [{"name": "kal1_0_1_2_3"}]},
        {"constraints": [{"name": "shell_9_0_1"}]},
    ]
    path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )
    assert _summarize_cut_bank(path) == {
        "cut_count": 2,
        "shell_conditioned_count": 1,
    }
