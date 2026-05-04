#!/usr/bin/env python3
"""Check tracked text files for hidden Unicode controls and CR line endings."""
from __future__ import annotations

import subprocess
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TEXT_SUFFIXES = {
    ".cff",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "venv",
}

HIDDEN_CHARS = {
    "\u200e": "LEFT-TO-RIGHT MARK",
    "\u200f": "RIGHT-TO-LEFT MARK",
    "\u2028": "LINE SEPARATOR",
    "\u2029": "PARAGRAPH SEPARATOR",
    "\u202a": "LEFT-TO-RIGHT EMBEDDING",
    "\u202b": "RIGHT-TO-LEFT EMBEDDING",
    "\u202c": "POP DIRECTIONAL FORMATTING",
    "\u202d": "LEFT-TO-RIGHT OVERRIDE",
    "\u202e": "RIGHT-TO-LEFT OVERRIDE",
    "\u2066": "LEFT-TO-RIGHT ISOLATE",
    "\u2067": "RIGHT-TO-LEFT ISOLATE",
    "\u2068": "FIRST STRONG ISOLATE",
    "\u2069": "POP DIRECTIONAL ISOLATE",
    "\ufeff": "BYTE ORDER MARK",
}

BIDI_CONTROL_CLASSES = {"LRE", "RLE", "LRO", "RLO", "PDF", "LRI", "RLI", "FSI", "PDI"}


def tracked_files() -> list[Path]:
    def filesystem_files() -> list[Path]:
        return [
            path
            for path in sorted(REPO_ROOT.rglob("*"))
            if path.is_file() and not any(part in SKIP_DIRS for part in path.relative_to(REPO_ROOT).parts)
        ]

    try:
        root_result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        if Path(root_result.stdout.strip()).resolve() != REPO_ROOT.resolve():
            return filesystem_files()
        result = subprocess.run(
            ["git", "ls-files"],
            check=True,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return filesystem_files()
    return [REPO_ROOT / line for line in result.stdout.splitlines()]


def is_text_target(path: Path) -> bool:
    return (
        path.suffix in TEXT_SUFFIXES
        or path.name == "Makefile"
        or path.name.startswith("LICENSE")
    )


def line_col(text: str, index: int) -> tuple[int, int]:
    line = text.count("\n", 0, index) + 1
    last_newline = text.rfind("\n", 0, index)
    col = index + 1 if last_newline == -1 else index - last_newline
    return line, col


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def hidden_char_description(char: str) -> str | None:
    if char in HIDDEN_CHARS:
        return HIDDEN_CHARS[char]
    # Policy: tracked text files should contain no Unicode format controls.
    # They are invisible in review and too easy to mistake for ordinary text.
    if unicodedata.category(char) == "Cf" or unicodedata.bidirectional(char) in BIDI_CONTROL_CLASSES:
        return unicodedata.name(char, "FORMAT OR BIDI CONTROL")
    return None


def main() -> int:
    errors: list[str] = []
    for path in tracked_files():
        if not is_text_target(path):
            continue
        data = path.read_bytes()
        shown = display_path(path)
        if b"\r" in data:
            errors.append(f"{shown}: contains CR or CRLF line endings")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{shown}: not valid UTF-8: {exc}")
            continue
        for index, char in enumerate(text):
            description = hidden_char_description(char)
            if description is not None:
                line, col = line_col(text, index)
                codepoint = f"U+{ord(char):04X}"
                errors.append(f"{shown}:{line}:{col}: hidden character {codepoint} ({description})")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("tracked text files are clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
