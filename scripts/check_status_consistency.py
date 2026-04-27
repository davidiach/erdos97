#!/usr/bin/env python3
"""Check top-level status text for stale or overclaiming contradictions."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_NO_OVERCLAIM_FILES = ["README.md", "STATE.md", "RESULTS.md"]
NO_OVERCLAIM_RE = re.compile(r"no\s+general proof and no counterexample", re.I)
STALE_N8_RE = re.compile(r"(?:n\s*=\s*8|\$8\$|`8`)\s*\|\s*\*\*?Open", re.I)
ARCHIVAL_MARKERS = ("archived", "superseded", "provenance")


def fail(msg: str) -> None:
    print(f"status consistency error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def main() -> None:
    if not (ROOT / "metadata" / "erdos97.yaml").exists():
        fail("metadata/erdos97.yaml is missing")

    for rel in REQUIRED_NO_OVERCLAIM_FILES:
        if not NO_OVERCLAIM_RE.search(read_text(rel)):
            fail(f"{rel} is missing the no-overclaiming status sentence")

    synthesis = ROOT / "docs" / "canonical-synthesis.md"
    if synthesis.exists():
        lines = synthesis.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if STALE_N8_RE.search(line):
                window = "\n".join(lines[max(0, i - 8) : i + 1]).lower()
                if not any(marker in window for marker in ARCHIVAL_MARKERS):
                    fail(f"unarchived stale n=8 Open wording at {synthesis}:{i + 1}")

    readme_state = read_text("README.md") + "\n" + read_text("STATE.md")
    if "metadata/erdos97.yaml" not in readme_state:
        fail("README.md or STATE.md should reference metadata/erdos97.yaml")


if __name__ == "__main__":
    main()
