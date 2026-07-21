#!/usr/bin/env python3
"""Validate the portable C++ second-source n=10 singleton replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from erdos97.json_io import load_json, write_json

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n10_fast_cpp_singleton_replay.json"
DEFAULT_PRIMARY_ARTIFACT = (
    ROOT / "data" / "certificates" / "n10_vertex_circle_singleton_slices.json"
)
DEFAULT_CPP_SOURCE = ROOT / "cpp" / "n_vertex_search_fast.cpp"

SCHEMA = "erdos97.n10_fast_cpp_singleton_replay.v1"
STATUS = "SECOND_SOURCE_CPP_N10_SINGLETON_REPLAY_REVIEW_PENDING"
TRUST = "MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING_SECONDARY"
CLAIM_SCOPE = (
    "Second-source portable C++ replay of the draft review-pending n=10 "
    "selected-witness singleton-slice artifact. It compares all 126 row0 "
    "slices against the checked Python artifact and records an n=9 calibration "
    "run. It does not prove n=10, does not prove Erdos Problem #97, does not "
    "claim a counterexample, and does not update the official/global status or "
    "the repo source-of-truth strongest local result."
)

EXPECTED_N9 = {
    "N": 9,
    "M": 70,
    "row0_start": 0,
    "row0_end": 70,
    "vertex_circle_pruning": True,
    "nodes": 16_752,
    "full": 0,
    "aborted": False,
    "counts": {
        "partial_self_edge": 11_271,
        "partial_strict_cycle": 11_011,
    },
}
EXPECTED_N10 = {
    "N": 10,
    "M": 126,
    "row0_start": 0,
    "row0_end": 126,
    "vertex_circle_pruning": True,
    "nodes": 4_142_738,
    "full": 0,
    "aborted": False,
    "counts": {
        "partial_self_edge": 4_467_592,
        "partial_strict_cycle": 5_318_250,
    },
}
EXPECTED_N10_ROW_DIGEST = (
    "64ebe12406c8777bcc7d7e2c5f1db3adb7703cbdba3898bb069bf964091b2fbb"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_json(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_primary_rows(primary: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = primary.get("rows")
    if not isinstance(rows, list):
        raise AssertionError("primary artifact rows must be a list")
    normalized: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise AssertionError("primary row must be an object")
        normalized.append(
            {
                "row0_index": int(row["row0_index"]),
                "row0_witnesses": [int(item) for item in row["row0_witnesses"]],
                "nodes": int(row["nodes"]),
                "full": int(row["full"]),
                "counts": {
                    str(key): int(value)
                    for key, value in sorted(row["counts"].items())  # type: ignore[union-attr]
                },
            }
        )
    return normalized


def normalize_cpp_rows(output: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = output.get("row_summaries")
    if not isinstance(rows, list):
        raise AssertionError("C++ output row_summaries must be a list")
    normalized: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise AssertionError("C++ row must be an object")
        normalized.append(
            {
                "row0_index": int(row["row0_index"]),
                "row0_witnesses": [int(item) for item in row["row0_witnesses"]],
                "nodes": int(row["nodes"]),
                "full": int(row["full"]),
                "counts": {
                    str(key): int(value)
                    for key, value in sorted(row["counts"].items())  # type: ignore[union-attr]
                },
            }
        )
    return normalized


def summary_from_output(output: Mapping[str, Any]) -> dict[str, Any]:
    summary = output.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("C++ output summary must be an object")
    counts = summary.get("counts")
    if not isinstance(counts, Mapping):
        raise AssertionError("C++ output summary counts must be an object")
    return {
        "N": int(summary["N"]),
        "M": int(summary["M"]),
        "row0_start": int(summary["row0_start"]),
        "row0_end": int(summary["row0_end"]),
        "vertex_circle_pruning": bool(summary["vertex_circle_pruning"]),
        "nodes": int(summary["nodes"]),
        "full": int(summary["full"]),
        "aborted": bool(summary["aborted"]),
        "counts": {
            "partial_self_edge": int(counts.get("partial_self_edge", 0)),
            "partial_strict_cycle": int(counts.get("partial_strict_cycle", 0)),
        },
    }


def run_cpp_replay(
    *,
    source: Path,
    compiler: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    compiler_path = compiler or shutil.which("g++") or shutil.which("c++")
    if compiler_path is None:
        raise RuntimeError("no C++17 compiler found; pass --compiler")
    with tempfile.TemporaryDirectory(prefix="erdos97_n10_cpp_") as tmp:
        tmp_path = Path(tmp)
        binary = tmp_path / "n_vertex_search_fast"
        compile_command = [
            compiler_path,
            "-O3",
            "-std=c++17",
            str(source),
            "-o",
            str(binary),
        ]
        subprocess.run(compile_command, cwd=ROOT, check=True)
        n9 = _run_binary(binary, 9)
        n10 = _run_binary(binary, 10)
    stable_command = (
        f"{Path(compiler_path).name} -O3 -std=c++17 "
        f"{display_path(source)} -o <tmp>/n_vertex_search_fast"
    )
    return n9, n10, stable_command


def _run_binary(binary: Path, n: int) -> dict[str, Any]:
    completed = subprocess.run(
        [str(binary), "--n", str(n)],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    payload = json.loads(completed.stdout)
    if not isinstance(payload, dict):
        raise AssertionError("C++ output must be a JSON object")
    return payload


def build_payload(
    *,
    primary: Mapping[str, Any],
    primary_path: Path,
    cpp_source: Path,
    n9_output: Mapping[str, Any],
    n10_output: Mapping[str, Any],
    compile_command: str,
) -> dict[str, Any]:
    n9_summary = summary_from_output(n9_output)
    n10_summary = summary_from_output(n10_output)
    primary_rows = normalize_primary_rows(primary)
    cpp_rows = normalize_cpp_rows(n10_output)
    n9_rows = normalize_cpp_rows(n9_output)
    row_digest = digest_json(cpp_rows)
    primary_row_digest = digest_json(primary_rows)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "cpp_source": {
            "path": display_path(cpp_source),
            "sha256": sha256_file(cpp_source),
            "compile_command": compile_command,
            "run_commands": [
                "n_vertex_search_fast --n 9",
                "n_vertex_search_fast --n 10",
            ],
        },
        "source_artifact": {
            "path": display_path(primary_path),
            "type": primary.get("type"),
            "trust": primary.get("trust"),
            "sha256": sha256_file(primary_path),
        },
        "n9_calibration": {
            "summary": n9_summary,
            "expected_summary": dict(EXPECTED_N9),
            "row_summaries_digest_sha256": digest_json(n9_rows),
            "row0_choices_covered": len(n9_rows),
        },
        "n10_replay": {
            "summary": n10_summary,
            "expected_summary": dict(EXPECTED_N10),
            "row_summaries": cpp_rows,
            "row_summaries_digest_sha256": row_digest,
            "primary_row_summaries_digest_sha256": primary_row_digest,
            "rows_match_primary_artifact": cpp_rows == primary_rows,
        },
        "review_independence": {
            "language": "C++17",
            "uses_repo_python_search": False,
            "uses_primary_artifact_as_input_to_search": False,
            "comparison_target": display_path(primary_path),
        },
        "summary": {
            "n9_calibration_ok": n9_summary == EXPECTED_N9,
            "n10_rows_match_primary_artifact": cpp_rows == primary_rows,
            "n10_row_summaries_digest_sha256": row_digest,
            "n10_row0_choices_covered": len(cpp_rows),
            "n10_total_nodes": n10_summary["nodes"],
            "n10_total_full": n10_summary["full"],
            "n10_counts": n10_summary["counts"],
            "solves_n10": False,
            "solves_erdos97": False,
        },
        "validation_status": "passed",
        "validation_errors": [],
    }


def validate_payload(
    payload: Mapping[str, Any],
    *,
    primary: Mapping[str, Any],
    primary_path: Path,
    cpp_source: Path,
) -> list[str]:
    errors: list[str] = []
    _check_equal(errors, "schema", payload.get("schema"), SCHEMA)
    _check_equal(errors, "status", payload.get("status"), STATUS)
    _check_equal(errors, "trust", payload.get("trust"), TRUST)
    claim_scope = payload.get("claim_scope")
    _check_equal(errors, "claim_scope", claim_scope, CLAIM_SCOPE)
    if isinstance(claim_scope, str):
        for required in (
            "does not prove n=10",
            "does not prove Erdos Problem #97",
            "does not claim a counterexample",
            "does not update the official/global status",
            "source-of-truth strongest local result",
        ):
            if required not in claim_scope:
                errors.append(f"claim_scope missing {required!r}")

    cpp_source_record = payload.get("cpp_source")
    if not isinstance(cpp_source_record, Mapping):
        errors.append("cpp_source must be an object")
    else:
        _check_equal(errors, "cpp_source.path", cpp_source_record.get("path"), display_path(cpp_source))
        _check_equal(errors, "cpp_source.sha256", cpp_source_record.get("sha256"), sha256_file(cpp_source))

    source_artifact = payload.get("source_artifact")
    if not isinstance(source_artifact, Mapping):
        errors.append("source_artifact must be an object")
    else:
        _check_equal(errors, "source_artifact.path", source_artifact.get("path"), display_path(primary_path))
        _check_equal(errors, "source_artifact.sha256", source_artifact.get("sha256"), sha256_file(primary_path))

    primary_rows = normalize_primary_rows(primary)
    expected_primary_digest = digest_json(primary_rows)
    n9 = payload.get("n9_calibration")
    if not isinstance(n9, Mapping):
        errors.append("n9_calibration must be an object")
    else:
        _check_equal(errors, "n9.summary", n9.get("summary"), EXPECTED_N9)
        _check_equal(errors, "n9.row0_choices_covered", n9.get("row0_choices_covered"), 70)

    n10 = payload.get("n10_replay")
    if not isinstance(n10, Mapping):
        errors.append("n10_replay must be an object")
    else:
        _check_equal(errors, "n10.summary", n10.get("summary"), EXPECTED_N10)
        rows = n10.get("row_summaries")
        if not isinstance(rows, list):
            errors.append("n10.row_summaries must be a list")
        else:
            normalized_rows = normalize_cpp_rows({"row_summaries": rows})
            _check_equal(errors, "n10.row_count", len(normalized_rows), 126)
            _check_equal(errors, "n10.rows_match_primary", normalized_rows, primary_rows)
            _check_equal(
                errors,
                "n10.row_summaries_digest_sha256",
                n10.get("row_summaries_digest_sha256"),
                digest_json(normalized_rows),
            )
            _check_equal(
                errors,
                "n10.expected_row_summaries_digest_sha256",
                n10.get("row_summaries_digest_sha256"),
                EXPECTED_N10_ROW_DIGEST,
            )
        _check_equal(
            errors,
            "n10.primary_row_summaries_digest_sha256",
            n10.get("primary_row_summaries_digest_sha256"),
            expected_primary_digest,
        )
        _check_equal(errors, "n10.rows_match_primary_artifact", n10.get("rows_match_primary_artifact"), True)

    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        errors.append("summary must be an object")
    else:
        _check_equal(errors, "summary.n9_calibration_ok", summary.get("n9_calibration_ok"), True)
        _check_equal(
            errors,
            "summary.n10_rows_match_primary_artifact",
            summary.get("n10_rows_match_primary_artifact"),
            True,
        )
        _check_equal(
            errors,
            "summary.n10_row0_choices_covered",
            summary.get("n10_row0_choices_covered"),
            126,
        )
        _check_equal(
            errors,
            "summary.n10_total_nodes",
            summary.get("n10_total_nodes"),
            EXPECTED_N10["nodes"],
        )
        _check_equal(
            errors,
            "summary.n10_total_full",
            summary.get("n10_total_full"),
            EXPECTED_N10["full"],
        )
        _check_equal(
            errors,
            "summary.n10_counts",
            summary.get("n10_counts"),
            EXPECTED_N10["counts"],
        )
        _check_equal(errors, "summary.solves_n10", summary.get("solves_n10"), False)
        _check_equal(errors, "summary.solves_erdos97", summary.get("solves_erdos97"), False)
        _check_equal(
            errors,
            "summary.n10_row_summaries_digest_sha256",
            summary.get("n10_row_summaries_digest_sha256"),
            EXPECTED_N10_ROW_DIGEST,
        )
    _check_equal(errors, "validation_status", payload.get("validation_status"), "passed")
    _check_equal(errors, "validation_errors", payload.get("validation_errors"), [])
    return errors


def compare_live_payload(stored: Mapping[str, Any], live: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for path in (
        ("n9_calibration", "summary"),
        ("n9_calibration", "row_summaries_digest_sha256"),
        ("n10_replay", "summary"),
        ("n10_replay", "row_summaries"),
        ("n10_replay", "row_summaries_digest_sha256"),
        ("summary", "n10_rows_match_primary_artifact"),
    ):
        stored_value: Any = stored
        live_value: Any = live
        for key in path:
            stored_value = stored_value[key]  # type: ignore[index]
            live_value = live_value[key]  # type: ignore[index]
        if stored_value != live_value:
            errors.append(f"live C++ replay mismatch at {'.'.join(path)}")
    return errors


def _check_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def compact_summary(payload: Mapping[str, Any], errors: Sequence[str]) -> dict[str, Any]:
    summary = payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {}
    return {
        "ok": not errors,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "n9_calibration_ok": summary.get("n9_calibration_ok") if isinstance(summary, Mapping) else None,
        "n10_rows_match_primary_artifact": (
            summary.get("n10_rows_match_primary_artifact")
            if isinstance(summary, Mapping)
            else None
        ),
        "n10_row0_choices_covered": (
            summary.get("n10_row0_choices_covered") if isinstance(summary, Mapping) else None
        ),
        "n10_total_nodes": summary.get("n10_total_nodes") if isinstance(summary, Mapping) else None,
        "n10_total_full": summary.get("n10_total_full") if isinstance(summary, Mapping) else None,
        "n10_counts": summary.get("n10_counts") if isinstance(summary, Mapping) else None,
        "n10_row_summaries_digest_sha256": (
            summary.get("n10_row_summaries_digest_sha256")
            if isinstance(summary, Mapping)
            else None
        ),
        "solves_n10": summary.get("solves_n10") if isinstance(summary, Mapping) else None,
        "solves_erdos97": summary.get("solves_erdos97") if isinstance(summary, Mapping) else None,
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--primary-artifact", type=Path, default=DEFAULT_PRIMARY_ARTIFACT)
    parser.add_argument("--cpp-source", type=Path, default=DEFAULT_CPP_SOURCE)
    parser.add_argument("--compiler", help="C++17 compiler to use with --run-cpp")
    parser.add_argument("--run-cpp", action="store_true", help="compile and rerun the C++ replay")
    parser.add_argument("--write", action="store_true", help="write artifact from a live C++ replay")
    parser.add_argument("--check", action="store_true", help="validate the stored artifact")
    parser.add_argument("--json", action="store_true", help="print compact JSON summary")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact
    primary_path = (
        args.primary_artifact if args.primary_artifact.is_absolute() else ROOT / args.primary_artifact
    )
    cpp_source = args.cpp_source if args.cpp_source.is_absolute() else ROOT / args.cpp_source
    primary = load_json(primary_path)
    if not isinstance(primary, Mapping):
        raise SystemExit("primary artifact must be a JSON object")

    live_payload: dict[str, Any] | None = None
    if args.run_cpp:
        n9_output, n10_output, compile_command = run_cpp_replay(
            source=cpp_source,
            compiler=args.compiler,
        )
        live_payload = build_payload(
            primary=primary,
            primary_path=primary_path,
            cpp_source=cpp_source,
            n9_output=n9_output,
            n10_output=n10_output,
            compile_command=compile_command,
        )

    if args.write:
        if live_payload is None:
            raise SystemExit("--write requires --run-cpp")
        write_json(live_payload, artifact)

    payload: Mapping[str, Any]
    if args.check or not args.run_cpp:
        raw_payload = load_json(artifact)
        if not isinstance(raw_payload, Mapping):
            raise SystemExit("stored artifact must be a JSON object")
        payload = raw_payload
    else:
        payload = live_payload if live_payload is not None else {}

    errors = validate_payload(
        payload,
        primary=primary,
        primary_path=primary_path,
        cpp_source=cpp_source,
    )
    if args.run_cpp and args.check and live_payload is not None:
        errors.extend(compare_live_payload(payload, live_payload))

    result = compact_summary(payload, errors)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif errors:
        print("FAILED: n=10 fast C++ singleton replay", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=10 fast C++ singleton replay")
        print(f"artifact: {display_path(artifact)}")
        print(f"row0 choices covered: {result['n10_row0_choices_covered']}")
        print(f"total nodes: {result['n10_total_nodes']}")
        print(f"total full assignments: {result['n10_total_full']}")
        print(f"row digest: {result['n10_row_summaries_digest_sha256']}")
        print("OK: C++ replay artifact matches the primary n=10 singleton artifact")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
