#!/usr/bin/env python3
"""Check tracked text files for hidden Unicode controls and CR line endings."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

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


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    return [Path(line) for line in result.stdout.splitlines()]


def is_text_target(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name.startswith("LICENSE")


def line_col(text: str, index: int) -> tuple[int, int]:
    line = text.count("\n", 0, index) + 1
    last_newline = text.rfind("\n", 0, index)
    col = index + 1 if last_newline == -1 else index - last_newline
    return line, col


def main() -> int:
    errors: list[str] = []
    for path in tracked_files():
        if not is_text_target(path):
            continue
        data = path.read_bytes()
        if b"\r" in data:
            errors.append(f"{path}: contains CR or CRLF line endings")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{path}: not valid UTF-8: {exc}")
            continue
        for index, char in enumerate(text):
            if char in HIDDEN_CHARS:
                line, col = line_col(text, index)
                codepoint = f"U+{ord(char):04X}"
                errors.append(
                    f"{path}:{line}:{col}: hidden character {codepoint} "
                    f"({HIDDEN_CHARS[char]})"
                )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("tracked text files are clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
