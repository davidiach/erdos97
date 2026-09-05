#!/usr/bin/env python3
"""Compile, rerun and compare the self-contained exact selected-row search."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from validate import COLUMNS, ROOT, require, validate



def validate_oracle(result: dict, n: int) -> None:
    """Check the sample contract without assuming a std::shuffle implementation.

    All 500 unconstrained runs visit n states; each of the 500 compatible
    runs visits between one and n states. The exact sample size depends on
    the C++ standard library even with the same mt19937 seed.
    """
    require(result.get("n") == n and result.get("seed") == 970905,
            "Oracle identity mismatch")
    require(type(result.get("states_checked")) is int
            and 500 * (n + 1) <= result["states_checked"] <= 1000 * n,
            "Oracle sample coverage mismatch")
    require(type(result.get("predicate_mismatches")) is int
            and result["predicate_mismatches"] == 0, "Oracle predicate mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--quick", action="store_true")
    mode.add_argument("--full-n11", action="store_true")
    parser.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--compiler", default="g++")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--sanitize", action="store_true", help="also run the n=11 oracle under UBSan")
    args = parser.parse_args()
    require(args.jobs > 0 and args.timeout_seconds > 0, "jobs and timeout must be positive")
    compiler = shutil.which(args.compiler)
    require(compiler is not None, f"C++ compiler not found: {args.compiler}")
    payload = json.loads((ROOT / "results.json").read_text())
    report = {"artifact_validation": validate(), "mode": "full-n11" if args.full_n11 else "quick",
              "repository_wide_CI_run": False, "checks": []}
    version = subprocess.run([compiler, "--version"], check=True, text=True, capture_output=True).stdout
    report["compiler"] = version.splitlines()[0]

    def run_json(command: list[str]) -> dict:
        result = subprocess.run(command, check=True, text=True, capture_output=True, timeout=args.timeout_seconds)
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"Invalid JSON output from {command}: {result.stdout!r}") from error

    with tempfile.TemporaryDirectory(prefix="erdos97-radius-n11-") as tmp:
        build = Path(tmp)

        def compile_source(n: int, source: str, sanitize: bool = False) -> Path:
            target = build / f"{Path(source).stem}-{n}{'-ubsan' if sanitize else ''}"
            flags = ["-O3", "-std=c++17", f"-DSEARCH_N={n}"]
            if sanitize:
                flags = ["-O1", "-g", "-std=c++17", f"-DSEARCH_N={n}",
                         "-fsanitize=undefined", "-fno-sanitize-recover=undefined"]
            subprocess.run([compiler, *flags, str(ROOT / source), "-o", str(target)],
                           check=True, text=True, capture_output=True, timeout=args.timeout_seconds)
            return target

        def compare_run(result: dict, expected: dict) -> None:
            require(result.get("complete") is True and result.get("survivor") is False,
                    f"Search did not exhaust with zero survivors: {result}")
            for key in COLUMNS[1:]:
                require(result[key] == expected[key], f"Counter mismatch for {key}: {result[key]} != {expected[key]}")

        binary11 = compile_source(11, "exact_search.cpp")
        indices = list(range(210)) if args.full_n11 else [0, 1, 209]

        def one_slice(index: int) -> dict:
            result = run_json([str(binary11), str(index)])
            require(result["n"] == 11 and result["row_count"] == 210 and result["slice"] == index,
                    "Slice identity mismatch")
            compare_run(result, dict(zip(COLUMNS, payload["n11_slices"][index])))
            return result

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            slices = list(executor.map(one_slice, indices))
        report["checks"].append({"n11_slices_compared": indices, "counter_mismatches": 0,
                                 "nodes_replayed": sum(row["nodes"] for row in slices)})
        if args.full_n11:
            for key in COLUMNS[1:]:
                require(sum(row[key] for row in slices) == payload["aggregate"][key], "Full aggregate mismatch")

        if args.quick:
            for n in [9, 10]:
                binary = compile_source(n, "exact_search.cpp")
                result = run_json([str(binary)])
                require(result["n"] == n and result["slice"] == -1, "Unsliced identity mismatch")
                compare_run(result, payload[f"n{n}"])
                report["checks"].append({"complete_search_n": n, "nodes": result["nodes"], "survivors": 0})
            for n in [9, 11]:
                oracle = compile_source(n, "oracle.cpp")
                result = run_json([str(oracle)])
                validate_oracle(result, n)
                report["checks"].append({
                    "oracle": result,
                    "archived_sample_states": payload["oracle_states"][f"n{n}"],
                    "matches_archived_sample_count":
                        result["states_checked"] == payload["oracle_states"][f"n{n}"],
                })
                if n == 9:
                    calibration = run_json([str(oracle), "--calibrate"])
                    require(calibration["incidence_frontier"] == 184 and calibration["nodes"] == 100818,
                            "Incidence calibration mismatch")
                    report["checks"].append({"incidence_calibration": calibration})
        if args.sanitize:
            oracle = compile_source(11, "oracle.cpp", sanitize=True)
            result = run_json([str(oracle)])
            validate_oracle(result, 11)
            report["checks"].append({"ubsan_oracle": result, "undefined_behavior_errors": 0})
    report["status"] = "all requested checks passed"
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
