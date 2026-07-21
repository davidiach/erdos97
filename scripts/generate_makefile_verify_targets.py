#!/usr/bin/env python3
"""Generate the registry-backed Makefile verify targets.

The verify targets between the GENERATED markers in the Makefile are derived
from the ``make_targets`` section of ``scripts/audit_commands.json``. Use
``--check`` to verify the Makefile matches the registry and ``--write`` to
regenerate the block in place. The ``verify-n9-candidate`` target is a
curated review surface mirrored in ``metadata/n9_candidate_review.yaml`` and
checked by its own manifest checker, so it is intentionally not generated.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_artifact_audit import (  # noqa: E402
    MAKE_TARGET_COMMAND_IDS,
    make_target_commands,
)

MAKEFILE_PATH = ROOT / "Makefile"
BEGIN_MARKER = "# BEGIN GENERATED VERIFY TARGETS (from scripts/audit_commands.json)"
END_MARKER = "# END GENERATED VERIFY TARGETS"


def generated_block() -> str:
    """Render the generated verify targets, marker lines included."""
    lines: list[str] = [BEGIN_MARKER]
    for target in MAKE_TARGET_COMMAND_IDS:
        lines.append(f"{target}:")
        for command in make_target_commands(target):
            if command.command[0] != "python":
                raise ValueError(
                    f"{target}: command {command.ident!r} does not start with 'python'"
                )
            lines.append("\t$(PYTHON) " + " ".join(command.command[1:]))
        lines.append("")
    lines.append(END_MARKER)
    return "\n".join(lines)


def split_makefile(text: str) -> tuple[str, str, str]:
    """Split Makefile text into (before, block, after) around the markers."""
    begin = text.find(BEGIN_MARKER)
    end = text.find(END_MARKER)
    if begin == -1 or end == -1 or end < begin:
        raise ValueError(
            "Makefile generated-target markers not found; expected "
            f"{BEGIN_MARKER!r} ... {END_MARKER!r}"
        )
    return (
        text[:begin],
        text[begin : end + len(END_MARKER)],
        text[end + len(END_MARKER) :],
    )


def check_makefile() -> list[str]:
    """Return alignment errors between the Makefile and the registry."""
    text = MAKEFILE_PATH.read_text(encoding="utf-8")
    try:
        _, block, _ = split_makefile(text)
    except ValueError as exc:
        return [str(exc)]
    if block != generated_block():
        return [
            "Makefile verify targets do not match scripts/audit_commands.json; "
            "run: python scripts/generate_makefile_verify_targets.py --write"
        ]
    return []


def write_makefile() -> bool:
    """Regenerate the Makefile block in place; return True when changed."""
    text = MAKEFILE_PATH.read_text(encoding="utf-8")
    before, block, after = split_makefile(text)
    expected = generated_block()
    if block == expected:
        return False
    MAKEFILE_PATH.write_text(before + expected + after, encoding="utf-8")
    return True


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--check",
        action="store_true",
        help="Verify the Makefile verify targets match the registry.",
    )
    mode.add_argument(
        "--write",
        action="store_true",
        help="Regenerate the Makefile verify targets in place.",
    )
    args = parser.parse_args(argv)
    if args.check:
        errors = check_makefile()
        for error in errors:
            print(error, file=sys.stderr)
        if errors:
            return 1
        print("Makefile verify targets match scripts/audit_commands.json")
        return 0
    changed = write_makefile()
    if changed:
        print("Makefile verify targets regenerated from scripts/audit_commands.json")
    else:
        print("Makefile verify targets already up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
