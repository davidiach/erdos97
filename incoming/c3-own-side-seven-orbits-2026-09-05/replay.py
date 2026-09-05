#!/usr/bin/env python3
"""Compile and replay the bounded seven-orbit certificate. No status promotion.

--collect reads completed execution records; it does NOT rerun the search.
--full performs fresh primary and separate-oracle exhaustive replays.
--deferred additionally regenerates all 138 cases from before the new lemma.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("c3_seven_verify", ROOT / "verify.py")
assert SPEC is not None and SPEC.loader is not None
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)
COUNT_KEYS = ("graphs", "angle_orders", "phase_cases", "right_angle_rejections",
              "pair_rejections", "radial_kalmanson_rejections", "cycle_kalmanson_rejections",
              "pre_right_frontier", "survivors", "phase_dfs_nodes", "metric_rejections")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    verify.require(isinstance(value, dict), "execution report is not an object")
    return value


def sum_shards(records: list[dict], total: int) -> dict:
    verify.require(bool(records), "missing execution shards")
    cursor = 0
    for record in sorted(records, key=lambda r: r["first"]):
        verify.require(record.get("exhausted") is True and record.get("survivors") == 0,
                       "incomplete or surviving execution")
        verify.require(type(record["first"]) is int and record["first"] == cursor and type(record["stop"]) is int
                       and cursor <= record["stop"] <= total, "overlap/gap/invalid shard range")
        verify.require(record["input_graphs"] == total and record["graphs"] == record["stop"]-cursor,
                       "shard coverage mismatch")
        for key in COUNT_KEYS:
            if key in record:
                verify.require(type(record[key]) is int and record[key] >= 0, "invalid integer counter")
        metric = record.get("metric_rejections", record.get("radial_kalmanson_rejections", 0)
                            + record.get("cycle_kalmanson_rejections", 0))
        verify.require(record["phase_cases"] == record["right_angle_rejections"]
                       + record["pair_rejections"] + metric, "phase partition mismatch")
        cursor = record["stop"]
    verify.require(cursor == total, "uncovered final graph range")
    return {key: sum(r.get(key, 0) for r in records) for key in COUNT_KEYS if any(key in r for r in records)}


def collect(directory: Path, include_deferred: bool = False) -> dict:
    graphs = {}
    for m in (5, 6, 7):
        primary = load(directory / f"graphs{m}_report.json")
        oracle = load(directory / f"graphs{m}_oracle_report.json")
        verify.require(primary.get("exhausted") is oracle.get("exhausted") is True,
                       "incomplete graph enumeration")
        verify.require(primary["orbits"] == oracle["orbits"] == m, "wrong graph size")
        expected_raw = ((m-1)*(m-2)//2)**m
        verify.require(oracle["raw_tuples"] == expected_raw, "raw row-tuple coverage mismatch")
        for key in ("oriented_graphs", "shortcut_rejections", "graphs"):
            verify.require(type(primary[key]) is int and primary[key] == oracle[key],
                           "graph enumerators disagree")
        verify.require(primary["oriented_graphs"] == primary["shortcut_rejections"]+primary["graphs"],
                       "graph count partition mismatch")
        data = directory / f"graphs{m}_masks.txt"
        independent = directory / f"graphs{m}_oracle_masks.txt"
        verify.require(data.read_bytes() == independent.read_bytes(), "graph listings differ")
        verify.require(len(data.read_text().splitlines()) == primary["graphs"], "graph listing truncated")
        graphs[str(m)] = {"raw_tuples": expected_raw, "oriented": primary["oriented_graphs"],
                          "shortcut_rejections": primary["shortcut_rejections"],
                          "remaining": primary["graphs"], "list_sha256": sha(data)}
    small = {}
    for m in (5, 6):
        small[str(m)] = sum_shards([load(directory / f"phase{m}_fast_report.json")], graphs[str(m)]["remaining"])
    total = graphs["7"]["remaining"]
    fast = sum_shards([load(p) for p in sorted((directory / "final_runs").glob("fast-*.json"))], total)
    oracle = sum_shards([load(p) for p in sorted((directory / "final_runs").glob("oracle-*.json"))], total)
    for key in ("graphs", "angle_orders", "phase_cases", "right_angle_rejections", "pair_rejections", "survivors"):
        verify.require(fast[key] == oracle[key], f"phase oracle mismatch: {key}")
    verify.require(fast["radial_kalmanson_rejections"]+fast["cycle_kalmanson_rejections"]
                   == oracle["metric_rejections"], "metric oracle mismatch")
    result = {"schema": 1, "status": "REVIEW_PENDING_RESTRICTED_COMPUTER_ASSISTED_OBSTRUCTION",
              "scope": "C3 own-triangle-side four-witness systems with at most seven orbits only",
              "graphs": graphs, "small_phase_runs": small, "seven_fast": fast,
              "seven_separate_phase_oracle": oracle,
              "frontier": verify.audit_frontier(full=True)}
    if include_deferred:
        runs = directory / "final_runs"
        result["seven_deferred"] = sum_shards([load(p) for p in sorted(runs.glob("deferred-*.json"))], total)
        records = [json.loads(line) for p in sorted(runs.glob("deferred-*.jsonl"))
                   for line in p.read_text(encoding="utf-8").splitlines()]
        expected = load(ROOT / "frontier.json")["records"]
        verify.require(records == expected, "deferred frontier regeneration mismatch")
        verify.require(result["seven_deferred"]["pre_right_frontier"] == 138
                       and result["seven_deferred"]["right_angle_rejections"] == 138,
                       "deferred frontier census mismatch")
    return result


def command(args: list[str], destination: Path | None = None, timeout: int = 1800) -> dict | None:
    process = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout, check=False)
    if process.returncode != 0:
        raise RuntimeError(f"Command failed ({process.returncode}): {args}\n{process.stderr}\n{process.stdout}")
    if destination is None:
        return None
    data = json.loads(process.stdout)
    destination.write_text(json.dumps(data, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    return data


def execute(directory: Path, jobs: int, full: bool, deferred: bool, sanitize: bool) -> dict:
    compiler = shutil.which("c++") or shutil.which("g++") or shutil.which("clang++")
    verify.require(compiler is not None, "C++17 compiler not found")
    flags = ["-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-O2" if sanitize else "-O3"]
    if sanitize:
        flags += ["-fsanitize=undefined", "-fno-sanitize-recover=all"]
    for m in (5, 6, 7):
        binary = directory / f"search{m}"
        command([compiler, *flags, f"-DORBIT_COUNT={m}", str(ROOT / "search.cpp"), "-o", str(binary)])
        for suffix, extra in [("", []), ("_oracle", ["--raw-oracle"])]:
            command([str(binary), "--graphs", *extra, "--output", str(directory / f"graphs{m}{suffix}_masks.txt")],
                    directory / f"graphs{m}{suffix}_report.json")
        if m < 7:
            command([str(binary), "--phases", str(directory / f"graphs{m}_masks.txt"),
                     "--output", str(directory / f"phase{m}_fast.jsonl")], directory / f"phase{m}_fast_report.json")
    oracle = directory / "oracle7"
    command([compiler, *flags, str(ROOT / "oracle.cpp"), "-o", str(oracle)])
    if not full:
        for i in (0, 50, 2754):
            primary = command([str(directory / "search7"), "--phases", str(directory / "graphs7_masks.txt"),
                               "--start", str(i), "--stop", str(i+1), "--output", str(directory / f"quick-{i}.jsonl")],
                              directory / f"quick-{i}.json")
            secondary = command([str(oracle), str(directory / "graphs7_oracle_masks.txt"), str(i), str(i+1)],
                                directory / f"oracle-quick-{i}.json")
            for key in ("graphs", "phase_cases", "right_angle_rejections", "pair_rejections", "survivors"):
                verify.require(primary[key] == secondary[key], f"quick oracle mismatch: {key}")
        return {"scope": "quick controls, graph enumeration, m<=6 replay, and three m=7 slices only",
                "sanitized": sanitize, "frontier": verify.audit_frontier(full=True)}
    runs = directory / "final_runs"
    runs.mkdir(exist_ok=True)
    total = load(directory / "graphs7_report.json")["graphs"]
    step = (total+jobs-1)//jobs
    intervals = [(i, min(i+step, total)) for i in range(0, total, step)]
    def phase_task(item):
        index, (first, stop), mode = item
        if mode == "oracle":
            args = [str(oracle), str(directory / "graphs7_oracle_masks.txt"), str(first), str(stop)]
        else:
            args = [str(directory / "search7"), "--phases", str(directory / "graphs7_masks.txt"),
                    "--start", str(first), "--stop", str(stop), "--output", str(runs / f"{mode}-{index}.jsonl")]
            if mode == "deferred":
                args.append("--defer-right-angle")
        return command(args, runs / f"{mode}-{index}.json")
    for mode in (["fast", "oracle", "deferred"] if deferred else ["fast", "oracle"]):
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            list(executor.map(phase_task, [(i, interval, mode) for i, interval in enumerate(intervals)]))
    return collect(directory, include_deferred=deferred)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--quick", action="store_true")
    modes.add_argument("--full", action="store_true")
    modes.add_argument("--collect", type=Path, help="validate saved completed-run records, not regeneration")
    parser.add_argument("--deferred", action="store_true")
    parser.add_argument("--sanitize", action="store_true")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--write", action="store_true", help="write generated report.json (not for quick mode)")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--workdir", type=Path)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 16 or (args.write and args.quick) or (args.deferred and args.quick):
        parser.error("invalid jobs/mode combination")
    if args.collect:
        result = collect(args.collect.resolve(), include_deferred=args.deferred)
    elif args.workdir:
        args.workdir.mkdir(parents=True, exist_ok=True)
        if any(args.workdir.iterdir()):
            parser.error("--workdir must be empty to prevent stale replay records")
        result = execute(args.workdir.resolve(), args.jobs, args.full, args.deferred, args.sanitize)
    else:
        with tempfile.TemporaryDirectory(prefix="c3-seven-") as temp:
            result = execute(Path(temp), args.jobs, args.full, args.deferred, args.sanitize)
    text = json.dumps(result, indent=2, sort_keys=True)+"\n"
    if args.write:
        (ROOT / "report.json").write_text(text, encoding="utf-8")
    if args.check:
        stored = load(ROOT / "report.json")
        if args.quick:
            verify.require(result["frontier"] == stored["frontier"], "frontier check mismatch")
        else:
            for key, value in result.items():
                verify.require(stored.get(key) == value, f"regenerated report mismatch: {key}")
    print(text, end="")


if __name__ == "__main__":
    main()
