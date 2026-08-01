from __future__ import annotations

from pathlib import Path

from scripts.check_text_clean import hidden_char_description, is_text_target


def test_repository_text_formats_are_covered() -> None:
    for name in (
        "proof.lean",
        "search.cpp",
        "report.html",
        "pytest.ini",
        ".gitattributes",
        ".gitignore",
        "lean-toolchain",
        "Makefile",
        "LICENSE-CODE.md",
    ):
        assert is_text_target(Path(name)), name


def test_binary_artifacts_are_not_decoded_as_text() -> None:
    for name in ("paper.pdf", "bundle.zip", "figure.png"):
        assert not is_text_target(Path(name)), name


def test_ascii_controls_are_rejected_except_tab_and_line_feed() -> None:
    assert hidden_char_description("\x08") == "CONTROL CHARACTER"
    assert hidden_char_description("\t") is None
    assert hidden_char_description("\n") is None
