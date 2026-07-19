from __future__ import annotations

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
