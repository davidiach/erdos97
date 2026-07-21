#!/usr/bin/env python3
"""Replay the exact n=10 self-edge/primitive-inverse Kalmanson closure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n10_kalmanson_pair_filter import N10KalmansonPairSearch  # noqa: E402


EXPECTED_CPP = {
    "n": 10,
    "nodes": 261_511,
    "self_edge_prunes": 360_742,
    "inverse_pair_prunes": 1_213_492,
    "satisfiable": False,
}

EXPECTED_SPOT_SLICES = {
    0: {
        "row0_start": 0,
        "row0_end": 1,
        "nodes": 835,
        "self_edge_prunes": 245,
        "inverse_pair_prunes": 2_620,
        "full_assignments": 0,
        "closed": True,
    },
    63: {
        "row0_start": 63,
        "row0_end": 64,
        "nodes": 2_411,
        "self_edge_prunes": 3_316,
        "inverse_pair_prunes": 10_426,
        "full_assignments": 0,
        "closed": True,
    },
    125: {
        "row0_start": 125,
        "row0_end": 126,
        "nodes": 1_329,
        "self_edge_prunes": 1_322,
        "inverse_pair_prunes": 4_052,
        "full_assignments": 0,
        "closed": True,
    },
}


def python_spot_replay(indices: list[int]) -> list[dict[str, int | bool]]:
    search = N10KalmansonPairSearch()
    return [search.search_slice(index, index + 1).to_dict() for index in indices]


def cpp_replay() -> dict[str, int | bool]:
    compiler = shutil.which("g++")
    if compiler is None:
        raise RuntimeError("g++ is required for --run-cpp")
    source = ROOT / "cpp" / "n10_kalmanson_pair_filter_probe.cpp"
    with tempfile.TemporaryDirectory(prefix="erdos97-n10-kalmanson-") as directory:
        binary = Path(directory) / "n10_kalmanson_pair_filter"
        subprocess.run(
            [compiler, "-std=c++17", "-O3", "-DNDEBUG", str(source), "-o", str(binary)],
            check=True,
        )
        completed = subprocess.run(
            [str(binary)],
            check=True,
            capture_output=True,
            text=True,
        )
    payload = json.loads(completed.stdout)
    if not isinstance(payload, dict):
        raise TypeError("C++ replay must emit one JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spot-row0",
        action="append",
        type=int,
        help="Python-replay one row-zero index; defaults to 0, 63, and 125",
    )
    parser.add_argument(
        "--run-cpp",
        action="store_true",
        help="compile and run the complete labelled C++ search",
    )
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    indices = args.spot_row0 if args.spot_row0 is not None else [0, 63, 125]
    if any(index not in range(126) for index in indices):
        raise ValueError("row-zero indices must lie in [0,126)")
    spots = python_spot_replay(indices)
    cpp = cpp_replay() if args.run_cpp else None

    if args.assert_expected:
        for index, result in zip(indices, spots):
            expected = EXPECTED_SPOT_SLICES.get(index)
            if expected is None:
                if result["closed"] is not True:
                    raise AssertionError(f"row-zero slice {index} did not close")
            elif result != expected:
                raise AssertionError(
                    f"unexpected Python slice {index}: {result!r} != {expected!r}"
                )
        if cpp is not None and cpp != EXPECTED_CPP:
            raise AssertionError(f"unexpected C++ replay: {cpp!r}")

    payload = {
        "status": "MACHINE_CHECKED_FINITE_CASE_REPLAY",
        "claim_scope": (
            "Exact closure of the labelled n=10 selected-row domain under the "
            "listed incidence, Kalmanson self-edge, and primitive-inverse "
            "pair filters only; "
            "not a proof of Erdos Problem #97."
        ),
        "python_spot_slices": spots,
        "cpp_full_replay": cpp,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("n=10 Kalmanson pair-filter replay")
        for row in spots:
            print(
                f"row0 {row['row0_start']}: nodes={row['nodes']}, "
                f"self={row['self_edge_prunes']}, "
                f"inverse={row['inverse_pair_prunes']}, full={row['full_assignments']}"
            )
        if cpp is not None:
            print(
                "full C++: "
                f"nodes={cpp['nodes']}, self={cpp['self_edge_prunes']}, "
                f"inverse={cpp['inverse_pair_prunes']}, "
                f"satisfiable={cpp['satisfiable']}"
            )
        if args.assert_expected:
            print("OK: expected replay counts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
