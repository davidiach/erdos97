from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "reviewer-guide.md"


def _review_target_h() -> str:
    text = GUIDE.read_text(encoding="utf-8")
    return text.split("## Review target H - `n=9` base-apex audit path", 1)[
        1
    ].split("## Known weak points", 1)[0]


def test_reviewer_guide_base_apex_target_points_to_audit_path() -> None:
    section = _review_target_h()

    assert "docs/n9-base-apex-frontier.md" in section
    assert "scripts/check_n9_base_apex_audit_path.py" in section
    assert "python scripts/check_n9_base_apex_audit_path.py --check --json" in section
    assert "low-excess ledger" in section
    assert "selected-baseline D=3 crosswalk" in section


def test_reviewer_guide_base_apex_target_is_nonclaiming() -> None:
    section = _review_target_h().lower()

    for phrase in (
        "finite bookkeeping",
        "not as incidence completeness",
        "geometric realizability",
        "a proof of `n=9`",
        "a counterexample",
        "official/global status update",
    ):
        assert phrase in section
