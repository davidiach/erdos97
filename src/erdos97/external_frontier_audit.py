"""Fail-closed source audit for the external removable-vertex frontier.

This module checks source shape and provenance only.  It does not validate
Lean proofs, mathematical claims, or the external repository's build.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
import subprocess


TAIL_SOURCE = Path("lean/Erdos9796Proof/P97/U1LargeCapRouteBTail.lean")
EXPECTED_COMMIT = "5e43baeb6fb5f5c51745e05696a7f1b29bf52b0a"
EXPECTED_SOURCE_SHA256 = (
    "03478c4ba4bd2b5019ea047b96748c333408d487857bdcc227ba5ae534227e48"
)
EXPECTED_README_SHA256 = (
    "6625641332bdb1d18ba11459158ee77951e7d50fc7a575c735a94974a8a10004"
)

EXPECTED_OPEN_DECLARATIONS = frozenset(
    {
        "DoubleApexOffSurplusSharedRadiusPair",
        "liveData_Q_l1_false",
        "liveData_Q_l2_false",
        "liveData_Q_l3_false",
        "liveData_Q_l4_false",
        "liveData_C_center_q_false",
        "liveData_C_center_t1_false",
        "liveData_C_center_t2_named_false",
        "liveData_C_center_t2_rowFailure_false",
        "liveData_C_center_t3_false",
        "liveData_C_center_u_false",
        "liveData_C_center_fresh_false",
    }
)
EXPECTED_TEXTUAL_HOLES = 32


def _lf_bytes(data: bytes) -> bytes:
    """Normalize checkout line endings to the committed LF convention."""
    return data.replace(b"\r\n", b"\n")


@dataclass(frozen=True)
class ExternalFrontierAudit:
    checkout: str
    commit: str | None
    source_path: str
    source_sha256: str
    readme_sha256: str
    textual_holes: int
    direct_open_declarations: tuple[str, ...]
    hole_lines_by_declaration: dict[str, tuple[int, ...]]
    readme_declared_symbols: int | None
    readme_declared_holes: int | None
    expected_snapshot_match: bool
    readme_source_agree: bool

    def to_json(self) -> dict[str, object]:
        return {
            "type": "external_removable_vertex_frontier_source_audit",
            "trust": "EXTERNAL_PROVENANCE_AUDIT_ONLY",
            "checkout": self.checkout,
            "expected_snapshot": {
                "commit": EXPECTED_COMMIT,
                "source_sha256": EXPECTED_SOURCE_SHA256,
                "readme_sha256": EXPECTED_README_SHA256,
            },
            "commit": self.commit,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "readme_sha256": self.readme_sha256,
            "textual_holes": self.textual_holes,
            "direct_open_declaration_count": len(self.direct_open_declarations),
            "direct_open_declarations": list(self.direct_open_declarations),
            "hole_lines_by_declaration": {
                name: list(lines)
                for name, lines in sorted(self.hole_lines_by_declaration.items())
            },
            "readme_declared_symbols": self.readme_declared_symbols,
            "readme_declared_holes": self.readme_declared_holes,
            "expected_snapshot_match": self.expected_snapshot_match,
            "readme_source_agree": self.readme_source_agree,
            "claims": {
                "external_lean_build_checked": False,
                "external_mathematics_checked": False,
                "proves_erdos97": False,
                "proves_n9": False,
                "changes_local_strongest_result": False,
            },
        }


def strip_lean_comments_and_strings(source: str) -> str:
    """Replace Lean comments and string contents while preserving line breaks."""
    out: list[str] = []
    index = 0
    block_depth = 0
    in_string = False
    escaped = False

    while index < len(source):
        char = source[index]
        pair = source[index : index + 2]

        if block_depth:
            if pair == "/-":
                block_depth += 1
                out.extend("  ")
                index += 2
            elif pair == "-/":
                block_depth -= 1
                out.extend("  ")
                index += 2
            else:
                out.append("\n" if char == "\n" else " ")
                index += 1
            continue

        if in_string:
            if char == "\n":
                out.append("\n")
            else:
                out.append(" ")
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if pair == "/-":
            block_depth = 1
            out.extend("  ")
            index += 2
            continue
        if pair == "--":
            while index < len(source) and source[index] != "\n":
                out.append(" ")
                index += 1
            continue
        if char == '"':
            in_string = True
            out.append(" ")
            index += 1
            continue

        out.append(char)
        index += 1

    return "".join(out)


def _open_declarations(source: str) -> tuple[dict[str, tuple[int, ...]], int]:
    cleaned = strip_lean_comments_and_strings(source)
    declarations = list(
        re.finditer(
            r"(?m)^\s*(?:private\s+)?(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)",
            cleaned,
        )
    )
    holes = list(re.finditer(r"\bsorry\b", cleaned))
    by_name: dict[str, list[int]] = {}

    declaration_index = 0
    for hole in holes:
        while (
            declaration_index + 1 < len(declarations)
            and declarations[declaration_index + 1].start() < hole.start()
        ):
            declaration_index += 1
        if not declarations or declarations[declaration_index].start() > hole.start():
            raise ValueError("found a source-level sorry outside a theorem or lemma")
        name = declarations[declaration_index].group(1)
        line = cleaned.count("\n", 0, hole.start()) + 1
        by_name.setdefault(name, []).append(line)

    return ({name: tuple(lines) for name, lines in by_name.items()}, len(holes))


def _readme_counts(readme: str) -> tuple[int | None, int | None]:
    match = re.search(
        r"(?P<symbols>\d+)\s+`sorry`-carrying symbols\s*/\s*"
        r"(?P<holes>\d+)\s+textual\s+holes",
        readme,
    )
    if match is None:
        return None, None
    return int(match.group("symbols")), int(match.group("holes"))


def _git_commit(checkout: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def audit_external_frontier(checkout: Path) -> ExternalFrontierAudit:
    checkout = checkout.resolve()
    source_path = checkout / TAIL_SOURCE
    readme_path = checkout / "README.md"
    if not source_path.is_file():
        raise FileNotFoundError(f"missing external tail source: {source_path}")
    if not readme_path.is_file():
        raise FileNotFoundError(f"missing external README: {readme_path}")

    source_bytes = _lf_bytes(source_path.read_bytes())
    readme_bytes = _lf_bytes(readme_path.read_bytes())
    source = source_bytes.decode("utf-8")
    readme = readme_bytes.decode("utf-8")
    hole_lines, textual_holes = _open_declarations(source)
    names = tuple(sorted(hole_lines))
    readme_symbols, readme_holes = _readme_counts(readme)
    commit = _git_commit(checkout)
    source_digest = sha256(source_bytes).hexdigest()
    readme_digest = sha256(readme_bytes).hexdigest()
    expected_match = (
        set(names) == EXPECTED_OPEN_DECLARATIONS
        and textual_holes == EXPECTED_TEXTUAL_HOLES
        and commit == EXPECTED_COMMIT
        and source_digest == EXPECTED_SOURCE_SHA256
        and readme_digest == EXPECTED_README_SHA256
    )
    readme_agree = (
        readme_symbols == len(names) and readme_holes == textual_holes
    )

    return ExternalFrontierAudit(
        checkout=str(checkout),
        commit=commit,
        source_path=TAIL_SOURCE.as_posix(),
        source_sha256=source_digest,
        readme_sha256=readme_digest,
        textual_holes=textual_holes,
        direct_open_declarations=names,
        hole_lines_by_declaration=hole_lines,
        readme_declared_symbols=readme_symbols,
        readme_declared_holes=readme_holes,
        expected_snapshot_match=expected_match,
        readme_source_agree=readme_agree,
    )
