#!/usr/bin/env python3
"""Check that docs/inventory.md links every documentation file under docs/.

`docs/index.md` links the complete inventory in `docs/inventory.md`.
This checker keeps that promise mechanical: every
tracked `.md`/`.html` file under `docs/` must appear as a relative link target
in `docs/inventory.md`, and every relative Markdown link target there must
resolve to a file that exists.

This is a navigation-coverage check only. It reads no mathematical content, and
it neither validates nor promotes any claim.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
INDEX = DOCS_ROOT / "inventory.md"

INDEXED_SUFFIXES = {".html", ".md"}

# The generated inventory covers the landing page but does not list itself.
EXEMPT_RELATIVE_PATHS = {"inventory.md"}

MARKDOWN = MarkdownIt("commonmark").enable("table")


def documentation_files() -> list[Path]:
    """Return the docs/ files the index is expected to cover."""

    def filesystem_files() -> list[Path]:
        return sorted(path for path in DOCS_ROOT.rglob("*") if path.is_file())

    def git_listed(*extra_args: str) -> list[str]:
        result = subprocess.run(
            ["git", "ls-files", "-z", *extra_args, "--", "docs"],
            check=True,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        return [path for path in result.stdout.split("\0") if path]

    try:
        # Tracked files plus new, not-yet-added ones, so a doc added in the
        # working tree fails here rather than first failing in CI. Ignored
        # paths stay out via --exclude-standard.
        listed = git_listed() + git_listed("--others", "--exclude-standard")
    except (FileNotFoundError, subprocess.CalledProcessError):
        paths = filesystem_files()
    else:
        paths = [REPO_ROOT / line for line in listed]

    return sorted(
        path
        for path in paths
        if path.suffix in INDEXED_SUFFIXES
        and path.is_file()
        and path.relative_to(DOCS_ROOT).as_posix() not in EXEMPT_RELATIVE_PATHS
    )


def index_link_targets(text: str) -> list[str]:
    """Return file paths from actual CommonMark navigation links.

    Inline, reference, and titled links are supported. Comments, code blocks,
    code spans, images, and raw HTML are not Markdown navigation entries.
    Decode URL paths only after separating query strings and fragments.
    """

    targets = []
    for block in MARKDOWN.parse(text):
        for token in block.children or []:
            if token.type != "link_open":
                continue
            target = urlsplit(token.attrGet("href") or "")
            if target.scheme or target.netloc or not target.path:
                continue
            targets.append(unquote(target.path))
    return targets


def main() -> int:
    if not INDEX.exists():
        print(f"missing documentation index: {INDEX}", file=sys.stderr)
        return 1

    text = INDEX.read_text(encoding="utf-8")
    targets = index_link_targets(text)
    linked = {(DOCS_ROOT / target).resolve() for target in targets}

    errors: list[str] = []

    files = documentation_files()
    missing = [
        path.relative_to(DOCS_ROOT).as_posix()
        for path in files
        if path.resolve() not in linked
    ]
    for relative in missing:
        errors.append(f"docs/inventory.md does not link docs/{relative}")

    for target in sorted(set(targets)):
        if not (DOCS_ROOT / target).is_file():
            errors.append(f"docs/inventory.md links a missing file: {target}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(
            f"\n{len(errors)} documentation-index coverage problem(s); "
            "add the missing entries to docs/inventory.md",
            file=sys.stderr,
        )
        return 1

    covered = len(files)
    print(f"docs/inventory.md covers all {covered} documentation files under docs/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
