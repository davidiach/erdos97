from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUN_DIRECTORIES = (
    "complex_three_mode_cyclic_2026-07-22",
    "complex_two_mode_cyclic_2026-07-22",
    "free_cartesian_sparse_2026-07-22",
    "sparse_full_cone_cegar_2026-07-22",
    "sparse_full_cone_compression_2026-07-23",
    "sparse_full_cone_seeded_cegar_2026-07-23",
)
SHA256_PATTERN = re.compile(r"\b[0-9a-f]{64}\b")


@pytest.mark.parametrize("directory", RUN_DIRECTORIES)
def test_summary_sha256_matches_run_readme(directory: str) -> None:
    run_dir = ROOT / "data" / "runs" / directory
    advertised = SHA256_PATTERN.findall(
        (run_dir / "README.md").read_text(encoding="utf-8")
    )

    assert len(advertised) == 1
    observed = hashlib.sha256((run_dir / "summary.json").read_bytes()).hexdigest()
    assert observed == advertised[0]
