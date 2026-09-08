#!/usr/bin/env python3
"""Replay exact archived checks in isolation without rewriting provenance."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def check_manifest(root: Path = ROOT) -> int:
    provenance = json.loads((root / "provenance.json").read_text())
    entries = provenance["original_files"]
    expected = {entry["path"] for entry in entries}
    if len(expected) != len(entries) or len(entries) != 18:
        raise AssertionError("Expected 18 unique original files")
    actual = {
        p.relative_to(root / "snapshot").as_posix()
        for p in (root / "snapshot").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }
    if actual != expected:
        raise AssertionError("Snapshot inventory differs from provenance")
    for entry in entries:
        rel = Path(entry["path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise AssertionError("Unsafe snapshot path")
        data = (root / "snapshot" / rel).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if (len(data) != entry["bytes"]
                or hashlib.sha256(data).hexdigest() != entry["sha256"]
                or blob != entry["git_blob_sha1"]):
            raise AssertionError(f"Original bytes changed: {rel}")
    return len(entries)


def run_replay(root: Path = ROOT) -> dict:
    if sys.flags.optimize:
        raise RuntimeError("Do not disable assertions when replaying archived checks")
    count = check_manifest(root)
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    commands = [
        ["verify/check_opposite_triangles.py", "--check"],
        ["verify/symbolic_checks.py", "--check"],
        ["verify/exact_controls.py", "--which", "12", "--check"],
        ["verify/exact_controls.py", "--which", "27"],
        ["verify/exact_controls.py", "--which", "27", "--check"],
    ]
    records = []
    with tempfile.TemporaryDirectory(prefix="erdos97-carrier-replay-") as tmp:
        work = Path(tmp) / "snapshot"
        shutil.copytree(root / "snapshot", work, ignore=shutil.ignore_patterns("__pycache__"))
        for args in commands:
            proc = subprocess.run(
                [sys.executable, *args], cwd=work, env=env,
                check=True, capture_output=True, text=True, timeout=180,
            )
            records.append({"command": ["python", *args], "returncode": proc.returncode,
                            "stdout": json.loads(proc.stdout), "stderr": proc.stderr})
        comparisons = []
        for source, retained in [
            ("candidate_counterexamples/product_27_exact_nonconvex.json",
             "generated/product_27_exact_nonconvex.json"),
            ("reports/exact_controls_27.json", "generated/exact_controls_27.json"),
        ]:
            data = (work / source).read_bytes()
            if data != (root / retained).read_bytes():
                raise AssertionError(f"Regenerated file mismatch: {retained}")
            comparisons.append({"path": retained, "bytes": len(data),
                                "sha256": hashlib.sha256(data).hexdigest()})
        # Run non-check modes too, and compare all four original generated outputs.
        for args in [["verify/check_opposite_triangles.py"], ["verify/symbolic_checks.py"],
                     ["verify/exact_controls.py", "--which", "12"]]:
            subprocess.run([sys.executable, *args], cwd=work, env=env,
                           check=True, capture_output=True, text=True, timeout=180)
        for rel in ["reports/opposite_triangle_exact_verification.json",
                    "reports/symbolic_checks.json", "reports/exact_controls_12.json",
                    "candidate_counterexamples/convex_diamond_12.json"]:
            new = json.loads((work / rel).read_text())
            old = json.loads((root / "snapshot" / rel).read_text())
            if rel == "reports/symbolic_checks.json":
                new.pop("sympy_version")
                old.pop("sympy_version")
            if new != old:
                raise AssertionError(f"Regenerated original report mismatch: {rel}")
            comparisons.append({"path": "snapshot/" + rel,
                                "comparison": "JSON equality; SymPy version metadata excluded where present"})
    if check_manifest(root) != count:
        raise AssertionError("Manifest changed during replay")
    return {
        "status": "PASS_SCOPED_PUBLICATION_REPLAY", "python": platform.python_version(),
        "original_files_verified": count, "commands": records,
        "regenerated_comparisons": comparisons,
        "exact_certificate_orders": 30, "symbolic_identity_checks": 49,
        "convex_control_vertices": 12, "convex_control_strict_halfplanes": 120,
        "nonconvex_control_points": 27, "nonconvex_control_hull_vertices": 18,
        "nonconvex_control_distance_equalities": 108,
        "nonconvex_control_strict_halfplanes": 450,
        "numerical_optimization_rerun": False,
        "independent_external_mathematical_review": False, "unrestricted_solution": False,
        "repository_wide_fast_and_artifact_gates_run": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-only", action="store_true")
    parser.add_argument("--check", action="store_true", help="Check regenerated outputs (also the default)")
    parser.add_argument("--output", type=Path, help="Optional fresh report path")
    args = parser.parse_args()
    report = ({"status": "PASS_ORIGINAL_MANIFEST", "original_files": check_manifest()}
              if args.manifest_only else run_replay())
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
