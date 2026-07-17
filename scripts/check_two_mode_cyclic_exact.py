#!/usr/bin/env python3
"""Repository entry point for the exact real two-mode cyclic verifier."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.two_mode_cyclic_exact import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
