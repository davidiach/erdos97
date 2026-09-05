"""Exercise the corrected CLI without rewriting hash-pinned research evidence."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess

import pytest

PACKET = Path(__file__).resolve().parents[1] / "incoming/radius-descent-n11-2026-09-05"
ARCHIVED_SHA256 = "c54766f191a022fbc0f8f653266f9373ef02fe8f4de37fcd342848a06877ab48"


@pytest.fixture(scope="module")
def search_binary(tmp_path_factory):
    compiler = shlex.split(os.environ.get("CXX", "g++"))
    if not compiler or shutil.which(compiler[0]) is None:
        pytest.skip("a C++17 compiler is required")
    binary = tmp_path_factory.mktemp("radius-reporting") / "search_n9"
    subprocess.run([*compiler, "-std=c++17", "-O2", "-DSEARCH_N=9",
                    str(PACKET / "search_cli.cpp"), "-o", str(binary)],
                   check=True, capture_output=True, text=True, timeout=60)
    return binary


def run(binary, *args):
    result = subprocess.run([str(binary), *args], capture_output=True,
                            text=True, timeout=30, check=False)
    return result.returncode, json.loads(result.stdout)


def test_archived_source_unchanged():
    assert hashlib.sha256((PACKET / "exact_search.cpp").read_bytes()).hexdigest() == ARCHIVED_SHA256


def test_first_survivor_is_a_decision_not_exhaustion(search_binary):
    code, data = run(search_binary, "--no-turn", "--no-kalmanson")
    assert code == 0
    assert data["decision_complete"] is True
    assert data["complete"] is data["exhausted"] is False
    assert data["termination_reason"] == "survivor_found"
    assert data["survivor"] is True and data["relaxation_unsat"] is False
    assert data["solution_count"] == 1 and data["nodes"] == 2265


def test_full_frontier_enumeration_is_exhausted(search_binary):
    code, data = run(search_binary, "--no-turn", "--no-kalmanson", "--enumerate-all")
    assert code == 0
    assert data["complete"] is data["exhausted"] is data["decision_complete"] is True
    assert data["termination_reason"] == "exhausted"
    assert data["survivor"] is True and data["relaxation_unsat"] is False
    assert data["solution_count"] == 184 and data["nodes"] == 100818


def test_full_n9_exclusion_keeps_original_counters(search_binary):
    code, data = run(search_binary)
    assert code == 0
    assert data["exhausted"] is data["decision_complete"] is data["relaxation_unsat"] is True
    assert data["termination_reason"] == "exhausted"
    assert data["survivor"] is False and data["nodes"] == 18472


def test_node_limit_without_survivor_is_not_a_decision(search_binary):
    code, data = run(search_binary, "--limit", "1")
    assert code == 3
    assert data["complete"] is data["exhausted"] is data["decision_complete"] is False
    assert data["termination_reason"] == "node_limit"
    assert data["relaxation_unsat"] is False and data["nodes"] == 1


def test_enumeration_aborted_after_survivor_still_decides_existence(search_binary):
    code, data = run(search_binary, "--no-turn", "--no-kalmanson", "--enumerate-all", "--limit", "2300")
    assert code == 3
    assert data["complete"] is data["exhausted"] is False
    assert data["decision_complete"] is data["survivor"] is True
    assert data["termination_reason"] == "node_limit" and data["relaxation_unsat"] is False


@pytest.mark.parametrize("args", [("--limit",), ("--limit", "-1"), ("--limit", "1x"),
                                  ("-1",), ("0", "1"), ("70",), ("--typo",)])
def test_malformed_arguments_are_not_search_results(search_binary, args):
    result = subprocess.run([str(search_binary), *args], capture_output=True,
                            text=True, check=False, timeout=30)
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr
