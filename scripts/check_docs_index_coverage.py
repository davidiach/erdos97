#!/usr/bin/env python3
"""Check that docs/index.md links every documentation file under docs/.

`README.md` advertises `docs/index.md` as the full documentation map and the
complete packet inventory. This checker keeps that promise mechanical: every
tracked `.md`/`.html` file under `docs/` must appear as a relative link target
in `docs/index.md`, and every relative link target in `docs/index.md` must
resolve to a file that exists.

This is a navigation-coverage check only. It reads no mathematical content, and
it neither validates nor promotes any claim.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
INDEX = DOCS_ROOT / "index.md"

INDEXED_SUFFIXES = {".html", ".md"}

# `index.md` is the map itself, so it does not list itself.
EXEMPT_RELATIVE_PATHS = {"index.md"}

LINK_RE = re.compile(r"\]\(([^)]+)\)")


def documentation_files() -> list[Path]:
    """Return the docs/ files the index is expected to cover."""

    def filesystem_files() -> list[Path]:
        return sorted(path for path in DOCS_ROOT.rglob("*") if path.is_file())

    def git_listed(*extra_args: str) -> list[str]:
        result = subprocess.run(
            ["git", "ls-files", *extra_args, "--", "docs"],
            check=True,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.splitlines()

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
    """Return the relative link targets recorded in the index, in order."""

    targets = []
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split("#", 1)[0].strip()
        if target:
            targets.append(target)
    return targets


def main() -> int:
    if not INDEX.exists():
        print(f"missing documentation index: {INDEX}", file=sys.stderr)
        return 1

    text = INDEX.read_text(encoding="utf-8")
    targets = index_link_targets(text)
    linked = {(DOCS_ROOT / target).resolve() for target in targets}

    errors: list[str] = []

    missing = [
        path.relative_to(DOCS_ROOT).as_posix()
        for path in documentation_files()
        if path.resolve() not in linked
    ]
    for relative in missing:
        errors.append(f"docs/index.md does not link docs/{relative}")

    for target in sorted(set(targets)):
        if not (DOCS_ROOT / target).exists():
            errors.append(f"docs/index.md links a missing path: {target}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(
            f"\n{len(errors)} documentation-index coverage problem(s); "
            "add the missing entries to docs/index.md",
            file=sys.stderr,
        )
        return 1

    covered = len(documentation_files())
    print(f"docs/index.md covers all {covered} documentation files under docs/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
