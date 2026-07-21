"""Shared JSON read/write helpers.

These helpers centralize the repository's stable JSON serialization
convention: two-space indentation, sorted keys, a single trailing newline,
UTF-8 encoding, and LF line endings. Scripts and library modules should
import them instead of redefining local copies.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    """Load JSON content from ``path``."""
    return json.loads(path.read_text(encoding="utf-8"))


def dumps_stable(payload: Any) -> str:
    """Serialize ``payload`` in the repository's stable JSON format."""
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def write_json(payload: Any, path: Path) -> None:
    """Write ``payload`` to ``path`` in the stable JSON format.

    Parent directories are created as needed and line endings are forced to
    LF so generated artifacts match the repository text policy on every
    platform.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps_stable(payload), encoding="utf-8", newline="\n")
