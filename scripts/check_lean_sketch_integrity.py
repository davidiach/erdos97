"""Check Lean proof-sketch guardrails.

This checker is intentionally lightweight. It does not prove mathematics; it
keeps AI-editable Lean sketches inside marked regions and flags common
"miracle lemma" shapes before they become review noise.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


START_MARKER = "-- EVOLVE-BLOCK-START"
END_MARKER = "-- EVOLVE-BLOCK-END"

DECL_RE = re.compile(r"^\s*(axiom|lemma|theorem)\s+([A-Za-z0-9_'.]+)\b")

BANNED_DECL_NAME_PARTS = (
    "no_bad_convex_polygon",
    "no_counterexample",
    "global_obstruction",
    "vertex_circle_obstruction_general",
    "erdos_97_solved",
    "erdos97_solved",
    "n9_complete",
)


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    message: str

    def as_dict(self, root: Path) -> dict[str, object]:
        return {
            "path": str(self.path.relative_to(root)),
            "line": self.line,
            "message": self.message,
        }


def _line_is_inside_block(line_number: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= line_number <= end for start, end in ranges)


def _evolve_ranges(path: Path, lines: list[str]) -> tuple[list[tuple[int, int]], list[Finding]]:
    findings: list[Finding] = []
    ranges: list[tuple[int, int]] = []
    active_start: int | None = None

    for idx, line in enumerate(lines, start=1):
        has_start = START_MARKER in line
        has_end = END_MARKER in line
        if has_start and has_end:
            findings.append(
                Finding(path, idx, "start and end markers must be on separate lines")
            )
            continue
        if has_start:
            if active_start is not None:
                findings.append(Finding(path, idx, "nested EVOLVE blocks are not allowed"))
            active_start = idx
            continue
        if has_end:
            if active_start is None:
                findings.append(Finding(path, idx, "EVOLVE block end without a start"))
            else:
                ranges.append((active_start, idx))
            active_start = None

    if active_start is not None:
        findings.append(Finding(path, active_start, "EVOLVE block start without an end"))

    return ranges, findings


def check_file(path: Path, sketch_root: Path, lean_root: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    findings: list[Finding] = []
    is_sketch = path.is_relative_to(sketch_root)

    ranges, marker_findings = _evolve_ranges(path, lines)
    findings.extend(marker_findings)

    if is_sketch and not ranges:
        findings.append(Finding(path, 1, "sketch file has no EVOLVE block"))

    for idx, line in enumerate(lines, start=1):
        if "sorry" in line or "admit" in line:
            if not is_sketch:
                findings.append(
                    Finding(path, idx, "sorry/admit is only allowed in sketch files")
                )
            elif not _line_is_inside_block(idx, ranges):
                findings.append(
                    Finding(path, idx, "sorry/admit must stay inside an EVOLVE block")
                )

        match = DECL_RE.match(line)
        if match is None:
            continue

        kind, name = match.groups()
        lower_name = name.lower()
        if kind == "axiom":
            findings.append(Finding(path, idx, "axioms are not allowed in Lean pilot files"))
        for banned in BANNED_DECL_NAME_PARTS:
            if banned in lower_name:
                findings.append(
                    Finding(
                        path,
                        idx,
                        f"declaration name looks like a miracle lemma: {name}",
                    )
                )

        if kind in {"lemma", "theorem"} and "known" in line.lower() and "sorry" in text:
            findings.append(
                Finding(
                    path,
                    idx,
                    "do not cite a 'known' theorem in a sketch that still contains sorry",
                )
            )

    if path == lean_root / "Erdos97" / "Basic.lean" and "official geometric statement" not in text:
        findings.append(
            Finding(path, 1, "Basic.lean must state that it is not the official theorem")
        )

    return findings


def check_tree(root: Path) -> list[Finding]:
    lean_root = root / "lean"
    sketch_root = lean_root / "Erdos97" / "Sketches"
    if not lean_root.exists():
        return [Finding(lean_root, 1, "lean directory does not exist")]

    findings: list[Finding] = []
    for path in sorted(lean_root.rglob("*.lean")):
        findings.extend(check_file(path, sketch_root, lean_root))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", help="emit JSON findings")
    args = parser.parse_args()

    root = args.root.resolve()
    findings = check_tree(root)

    if args.json:
        print(json.dumps([finding.as_dict(root) for finding in findings], indent=2))
    elif findings:
        for finding in findings:
            rel = finding.path.relative_to(root)
            print(f"{rel}:{finding.line}: {finding.message}")
    else:
        print("Lean sketch integrity checks passed")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
