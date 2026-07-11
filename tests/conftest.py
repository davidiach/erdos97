from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.ci_sharding import (  # noqa: E402
    SHARD_ALGORITHM,
    stable_shard,
    validate_shard,
)


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("erdos97 deterministic sharding")
    group.addoption(
        "--shard-count",
        action="store",
        type=int,
        default=1,
        help="number of deterministic pytest shards",
    )
    group.addoption(
        "--shard-index",
        action="store",
        type=int,
        default=0,
        help="zero-based deterministic pytest shard to run",
    )


def _pytest_shard(config: pytest.Config) -> tuple[int, int]:
    shard_count = config.getoption("--shard-count")
    shard_index = config.getoption("--shard-index")
    try:
        validate_shard(shard_index, shard_count)
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc
    return shard_index, shard_count


def pytest_report_header(config: pytest.Config) -> str | None:
    shard_index, shard_count = _pytest_shard(config)
    if shard_count == 1:
        return None
    return (
        f"erdos97 shard {shard_index + 1}/{shard_count} "
        f"({SHARD_ALGORITHM})"
    )


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    shard_index, shard_count = _pytest_shard(config)
    if shard_count == 1:
        return
    selected: list[pytest.Item] = []
    deselected: list[pytest.Item] = []
    for item in items:
        destination = stable_shard(item.nodeid, shard_count)
        (selected if destination == shard_index else deselected).append(item)
    items[:] = selected
    if deselected:
        config.hook.pytest_deselected(items=deselected)
