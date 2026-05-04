"""Small CLI path-display helpers."""

from __future__ import annotations

from pathlib import Path


def display_path(path: str | Path, root: str | Path) -> str:
    """Return a stable display path without requiring ``path`` to sit under ``root``."""

    resolved = Path(path).resolve()
    resolved_root = Path(root).resolve()
    try:
        return resolved.relative_to(resolved_root).as_posix()
    except ValueError:
        return str(resolved)
