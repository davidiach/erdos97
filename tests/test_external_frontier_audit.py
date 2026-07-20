from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pytest

import erdos97.external_frontier_audit as frontier
from erdos97.external_frontier_audit import (
    _open_declarations,
    _readme_counts,
    strip_lean_comments_and_strings,
)


def test_comment_stripper_ignores_nested_comments_and_strings() -> None:
    source = '''
/- comment sorry /- nested sorry -/ -/
theorem first : True := by
  have label := "sorry"
  sorry
-- sorry
theorem second : False := by sorry
'''
    cleaned = strip_lean_comments_and_strings(source)
    assert cleaned.count("sorry") == 2


def test_open_declarations_groups_textual_holes() -> None:
    source = '''
theorem first : True := by
  sorry
  sorry
lemma second : False := by sorry
'''
    holes, count = _open_declarations(source)
    assert count == 3
    assert holes == {"first": (3, 4), "second": (5,)}


def test_readme_counts_are_fail_closed() -> None:
    assert _readme_counts("12 `sorry`-carrying symbols / 32 textual holes") == (
        12,
        32,
    )
    assert _readme_counts("proof complete") == (None, None)


def test_public_audit_normalizes_crlf_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checkout = tmp_path / "external"
    source_path = checkout / frontier.TAIL_SOURCE
    source_path.parent.mkdir(parents=True)
    source_lf = b"""theorem first : True := by
  sorry
  sorry
lemma second : False := by sorry
"""
    readme_lf = b"2 `sorry`-carrying symbols / 3 textual holes\n"
    source_path.write_bytes(source_lf.replace(b"\n", b"\r\n"))
    (checkout / "README.md").write_bytes(
        readme_lf.replace(b"\n", b"\r\n")
    )

    monkeypatch.setattr(frontier, "_git_commit", lambda _: "fixture-commit")
    monkeypatch.setattr(frontier, "EXPECTED_COMMIT", "fixture-commit")
    monkeypatch.setattr(
        frontier, "EXPECTED_OPEN_DECLARATIONS", frozenset({"first", "second"})
    )
    monkeypatch.setattr(frontier, "EXPECTED_TEXTUAL_HOLES", 3)
    monkeypatch.setattr(
        frontier, "EXPECTED_SOURCE_SHA256", sha256(source_lf).hexdigest()
    )
    monkeypatch.setattr(
        frontier, "EXPECTED_README_SHA256", sha256(readme_lf).hexdigest()
    )

    result = frontier.audit_external_frontier(checkout)

    assert result.expected_snapshot_match
    assert result.readme_source_agree
    assert result.source_sha256 == sha256(source_lf).hexdigest()
    assert result.readme_sha256 == sha256(readme_lf).hexdigest()
