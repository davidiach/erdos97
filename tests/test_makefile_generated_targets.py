from __future__ import annotations

from scripts.generate_makefile_verify_targets import (
    MAKEFILE_PATH,
    check_makefile,
    generated_block,
    split_makefile,
)
from scripts.run_artifact_audit import MAKE_TARGET_COMMAND_IDS


def test_registry_defines_the_expected_generated_targets() -> None:
    assert list(MAKE_TARGET_COMMAND_IDS) == [
        "verify-n8",
        "verify-kalmanson",
        "verify-n9-review",
        "verify-bridge-frontier",
        "verify-n10-review",
    ]


def test_makefile_generated_targets_match_registry() -> None:
    assert check_makefile() == []


def test_generated_block_is_the_marker_delimited_makefile_region() -> None:
    text = MAKEFILE_PATH.read_text(encoding="utf-8")
    _, block, _ = split_makefile(text)
    assert block == generated_block()
