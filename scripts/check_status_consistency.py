#!/usr/bin/env python3
"""Check top-level status text for stale or overclaiming contradictions."""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only without dev dependencies.
    yaml = None

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_STATUS_FILES = ["README.md", "STATE.md", "RESULTS.md"]

NO_OVERCLAIM_RE = re.compile(r"no\s+general\s+proof\s+and\s+no\s+counterexample", re.I)
OFFICIAL_OPEN_RE = re.compile(r"falsifiable\s*[/ -]\s*open", re.I)
LOCAL_N8_RE = re.compile(
    r"\bselected-witness\b"
    r"(?=.{0,500}\bn\s*<=\s*8\b)"
    r"(?=.{0,500}\brepo-local\b)"
    r"(?=.{0,500}\bmachine-checked\b)",
    re.I,
)
REVIEW_RE = re.compile(
    r"(?:independent\s+(?:external\s+)?review|external\s+independent\s+review)"
    r"|(?:before\s+(?:paper-style|public\s+theorem-style|public theorem-style))",
    re.I,
)

STALE_N8_PATTERNS = [
    re.compile(r"(?:n\s*=\s*8|\$n\s*=\s*8\$|\$8\$|`8`)\s*\|\s*\*\*?Open", re.I),
    re.compile(r"(?:n\s*=\s*8|n=8|\$n\s*=\s*8\$)[^.\n]{0,140}\ball\s+docs[^.\n]{0,140}\bopen\b", re.I),
    re.compile(
        r"(?:n\s*=\s*8|n=8|\$n\s*=\s*8\$)[^.\n]{0,140}\bstatus[^.\n]{0,140}\bopen\b",
        re.I,
    ),
    re.compile(r"\ball\s+5\s+main\s+docs\s+agree\s+on\s+[\"'`]?open[\"'`]?", re.I),
]
ARCHIVAL_MARKERS = (
    "archived",
    "superseded",
    "pre-current-artifact",
    "source-corpus",
    "not current repo-local status",
)

METADATA_EXPECTED_TRUE = (
    "no_overclaiming",
    "numerical_evidence_is_not_proof",
    "exact_certificates_required_for_counterexamples",
    "independent_review_required_for_public_theorem_claims",
)


def fail(msg: str) -> None:
    print(f"status consistency error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def load_metadata(path: Path) -> dict[str, object]:
    if yaml is None:
        fail("PyYAML is required to parse metadata/erdos97.yaml; install with `pip install -e .[dev]`")
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        fail(f"metadata/erdos97.yaml is not valid YAML: {exc}")
    if not isinstance(loaded, dict):
        fail("metadata/erdos97.yaml should parse as a mapping")
    return loaded


def metadata_value(metadata: dict[str, object], path: tuple[str, ...]) -> object:
    current: object = metadata
    for key in path:
        if not isinstance(current, dict) or key not in current:
            fail(f"metadata/erdos97.yaml is missing {'.'.join(path)}")
        current = current[key]
    return current


def require_pattern(label: str, text: str, pattern: re.Pattern[str], detail: str) -> None:
    if not pattern.search(text):
        fail(f"{label} should state {detail}")


def has_local_n8_status(text: str) -> bool:
    for paragraph in re.split(r"\n\s*\n", text):
        normalized = " ".join(paragraph.split())
        if LOCAL_N8_RE.search(normalized):
            return True
    return False


def require_local_n8_status(label: str, text: str) -> None:
    if not has_local_n8_status(text):
        fail(f"{label} should state repo-local machine-checked selected-witness n <= 8 status")


def stale_line_is_archived(lines: list[str], index: int) -> bool:
    window = "\n".join(lines[max(0, index - 3) : min(len(lines), index + 4)]).lower()
    return any(marker in window for marker in ARCHIVAL_MARKERS)


def validate_metadata() -> None:
    path = ROOT / "metadata" / "erdos97.yaml"
    if not path.exists():
        fail("metadata/erdos97.yaml is missing")

    metadata = load_metadata(path)
    official_status = metadata_value(metadata, ("problem", "official_status"))
    if not isinstance(official_status, str) or official_status.lower() != "falsifiable/open":
        fail("metadata official_status should be falsifiable/open")
    require_pattern(
        "metadata local_repo.overall_claim",
        str(metadata_value(metadata, ("local_repo", "overall_claim"))),
        NO_OVERCLAIM_RE,
        "no general proof and no counterexample",
    )
    require_local_n8_status(
        "metadata local_repo.strongest_result",
        str(metadata_value(metadata, ("local_repo", "strongest_result"))),
    )
    require_pattern(
        "metadata local_repo.strongest_result_review_status",
        str(metadata_value(metadata, ("local_repo", "strongest_result_review_status"))),
        REVIEW_RE,
        "independent review before public theorem-style claims",
    )
    for key in METADATA_EXPECTED_TRUE:
        if metadata_value(metadata, ("trust_policy", key)) is not True:
            fail(f"metadata trust_policy.{key} should be true")


def validate_top_level_status() -> None:
    for rel in REQUIRED_STATUS_FILES:
        text = read_text(rel)
        require_pattern(rel, text, NO_OVERCLAIM_RE, "no general proof and no counterexample")
        require_pattern(rel, text, OFFICIAL_OPEN_RE, "official/global falsifiable/open status")
        require_local_n8_status(rel, text)
        require_pattern(rel, text, REVIEW_RE, "independent review before public theorem-style claims")

    readme_state = read_text("README.md") + "\n" + read_text("STATE.md")
    if "metadata/erdos97.yaml" not in readme_state:
        fail("README.md or STATE.md should reference metadata/erdos97.yaml")


def validate_archived_synthesis() -> None:
    synthesis = ROOT / "docs" / "canonical-synthesis.md"
    if not synthesis.exists():
        return

    lines = synthesis.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if not any(pattern.search(line) for pattern in STALE_N8_PATTERNS):
            continue
        if not stale_line_is_archived(lines, i):
            fail(f"unarchived stale n=8 Open wording at {synthesis}:{i + 1}")


def main() -> None:
    validate_metadata()
    validate_top_level_status()
    validate_archived_synthesis()


if __name__ == "__main__":
    main()
