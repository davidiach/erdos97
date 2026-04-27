from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_status_consistency.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_status_consistency", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_local_n8_status_must_be_in_one_paragraph() -> None:
    checker = load_checker()

    good = (
        "The selected-witness method rules out `n <= 8` in this repo-local, "
        "machine-checked finite-case sense."
    )
    bad = (
        "The selected-witness method is important.\n\n"
        "Elsewhere, repo-local machine-checked finite-case artifacts are discussed for `n <= 8`."
    )

    assert checker.has_local_n8_status(good)
    assert not checker.has_local_n8_status(bad)


def test_stale_n8_line_requires_archival_context() -> None:
    checker = load_checker()

    stale = ['- $n = 8$ status — all 5 main docs agree on "open".']
    archived = [
        "- Archived/pre-current-artifact source-corpus status.",
        '- $n = 8$ status — all 5 main docs agree on "open".',
        "- Do not use this as current repo-local status.",
    ]

    assert any(pattern.search(stale[0]) for pattern in checker.STALE_N8_PATTERNS)
    assert not checker.stale_line_is_archived(stale, 0)
    assert checker.stale_line_is_archived(archived, 1)


def test_metadata_parser_reads_structured_yaml(tmp_path: Path) -> None:
    checker = load_checker()
    metadata = tmp_path / "erdos97.yaml"
    metadata.write_text(
        """
problem:
    official_status: "falsifiable/open"
local_repo:
    overall_claim: "No general proof and no counterexample are claimed."
trust_policy:
    no_overclaiming: true
""".lstrip(),
        encoding="utf-8",
    )

    parsed = checker.load_metadata(metadata)

    assert checker.metadata_value(parsed, ("problem", "official_status")) == "falsifiable/open"
    assert checker.metadata_value(parsed, ("trust_policy", "no_overclaiming")) is True
