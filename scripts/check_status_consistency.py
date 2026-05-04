#!/usr/bin/env python3
"""Check top-level status text for stale or overclaiming contradictions."""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Sequence

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
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")


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


def require_string_field(mapping: object, key: str, label: str) -> str:
    if not isinstance(mapping, dict):
        fail(f"{label} should be a mapping")
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"{label}.{key} should be a non-empty string")
    return value


def parse_iso_date(value: str, label: str) -> date:
    if not DATE_RE.fullmatch(value):
        fail(f"{label} should be YYYY-MM-DD")
    return datetime.strptime(value, "%Y-%m-%d").date()


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


def validate_metadata(max_official_status_age_days: int | None = None) -> None:
    path = ROOT / "metadata" / "erdos97.yaml"
    if not path.exists():
        fail("metadata/erdos97.yaml is missing")

    metadata = load_metadata(path)
    official_status = metadata_value(metadata, ("problem", "official_status"))
    if not isinstance(official_status, str) or official_status.lower() != "falsifiable/open":
        fail("metadata official_status should be falsifiable/open")
    official = metadata_value(metadata, ("problem",))
    if not isinstance(official, dict):
        fail("metadata problem should be a mapping")
    parse_iso_date(
        require_string_field(official, "official_page_last_edited", "metadata problem"),
        "metadata problem.official_page_last_edited",
    )
    validate_official_status_freshness(official, max_official_status_age_days)
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

    validate_nearby_literature(metadata)


def validate_official_status_freshness(
    official: dict[str, object],
    max_age_days: int | None,
    today: date | None = None,
) -> None:
    checked = parse_iso_date(
        require_string_field(official, "official_status_last_checked", "metadata problem"),
        "metadata problem.official_status_last_checked",
    )
    if max_age_days is None:
        return
    if max_age_days < 0:
        fail("--max-official-status-age-days should be nonnegative")
    today = today or date.today()
    age_days = (today - checked).days
    if age_days < 0:
        fail("metadata problem.official_status_last_checked is in the future")
    if age_days > max_age_days:
        fail(
            "metadata problem.official_status_last_checked is "
            f"{age_days} days old, above the {max_age_days}-day limit"
        )


def validate_nearby_literature(metadata: dict[str, object]) -> None:
    nearby = metadata_value(metadata, ("nearby_literature",))
    if not isinstance(nearby, dict):
        fail("metadata nearby_literature should be a mapping")

    last_swept = require_string_field(nearby, "last_swept", "metadata nearby_literature")
    if not DATE_RE.fullmatch(last_swept):
        fail("metadata nearby_literature.last_swept should be YYYY-MM-DD")

    entries = nearby.get("entries")
    if not isinstance(entries, list) or not entries:
        fail("metadata nearby_literature.entries should be a non-empty list")

    for index, entry in enumerate(entries):
        label = f"metadata nearby_literature.entries[{index}]"
        require_string_field(entry, "key", label)
        require_string_field(entry, "title", label)
        require_string_field(entry, "status", label)
        if not isinstance(entry, dict) or not isinstance(entry.get("citation"), dict):
            fail(f"{label}.citation should be a mapping")
        citation = entry["citation"]
        has_reference = any(
            isinstance(citation.get(field), str) and citation.get(field).strip()
            for field in ("source", "doi", "url")
        )
        if not has_reference:
            fail(f"{label}.citation should include a non-empty source, doi, or url")


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


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-official-status-age-days",
        type=int,
        default=None,
        help=(
            "Fail if metadata problem.official_status_last_checked is older "
            "than this many days. Intended for artifact-audit or release paths."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    validate_metadata(args.max_official_status_age_days)
    validate_top_level_status()
    validate_archived_synthesis()


if __name__ == "__main__":
    main()
