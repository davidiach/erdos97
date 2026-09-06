#!/usr/bin/env python3
"""Replay the four immutable research snapshots in isolated temporary directories.

No historical report is overwritten in the checkout. The ordinary check runs
all packet generators, compares their exact bytes, runs the 101 archived unit
tests, and validates the displayed nine-orbit pattern's existing obstruction.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
PACKETS = {
    "chain-conic": "chain-conic-obstructions-2026-09-06",
    "rank-one": "rank-one-bridge-2026-09-06",
    "rank-two": "rank-two-layer-escape-2026-09-06",
    "closure-audit": "bridge-closure-audit-2026-09-06",
}
UNIT_FILES = {
    "rank-one": "test_bridge.py",
    "rank-two": "test_bridge.py",
    "closure-audit": "test_audit.py",
}
PRIMARY_BLOB = "5129c71381353f70c6a30f4b151f1f3a5a1ff86f"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifests() -> dict:
    provenance = json.loads((ROOT / "provenance.json").read_text())
    records = provenance["original_archives"]
    require(len(records) == 4, "Exactly four original archives required")
    count = 0
    inner_count = 0
    for record in records:
        relative = Path(record["path"])
        require(
            not relative.is_absolute()
            and len(relative.parts) == 2
            and relative.parts[0] == "snapshots"
            and relative.parts[1] in PACKETS.values(),
            "Invalid snapshot path",
        )
        folder = ROOT / relative
        files = record["files"]
        require(record["file_count"] == len(files), "File-count mismatch")
        actual = {p.name for p in folder.iterdir() if p.is_file()}
        require(actual == set(files), f"Unexpected/missing snapshot file: {relative}")
        for name, metadata in files.items():
            require(Path(name).name == name, "Invalid snapshot filename")
            path = folder / name
            require(path.stat().st_size == metadata["bytes"], f"Size changed: {path}")
            require(sha256(path) == metadata["sha256"], f"Bytes changed: {path}")
            count += 1
        if (folder / "MANIFEST.sha256").exists():
            inner = {}
            for line in (folder / "MANIFEST.sha256").read_text().splitlines():
                checksum, name = line.split(maxsplit=1)
                inner[name] = checksum
        else:
            manifest = json.loads((folder / "manifest.json").read_text())
            inner = manifest.get("files", manifest)
            inner = {
                name: entry["sha256"] if isinstance(entry, dict) else entry
                for name, entry in inner.items()
            }
        for name, checksum in inner.items():
            require(name in files, f"Unknown historical manifest file: {name}")
            require(
                sha256(folder / name) == checksum,
                f"Historical manifest mismatch: {name}",
            )
            inner_count += 1
    require(count == 41, "Expected 41 byte-preserved packet files")
    return {
        "original_archives": 4,
        "preserved_files": count,
        "historical_manifest_entries": inner_count,
    }


def run_command(folder: Path, arguments: list[str]) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(folder)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    process = subprocess.run(
        [sys.executable, *arguments],
        cwd=folder,
        env=env,
        text=True,
        capture_output=True,
        timeout=300,
        check=False,
    )
    require(
        process.returncode == 0,
        f"Command failed: {arguments}\n{process.stdout}\n{process.stderr}",
    )
    return {
        "command": arguments,
        "returncode": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }


def replay_packet(name: str, mode: str) -> dict:
    source = ROOT / "snapshots" / PACKETS[name]
    commands = []
    compared = []
    with tempfile.TemporaryDirectory(prefix="erdos97-bridge-replay-") as temporary:
        folder = Path(temporary) / PACKETS[name]
        shutil.copytree(source, folder)
        if mode != "units":
            if name == "chain-conic":
                commands.append(
                    run_command(folder, ["verify.py", "--output", "fresh-report.json"])
                )
                generated = {"fresh-report.json": "verification.json"}
            else:
                commands.append(run_command(folder, ["verify.py", "--write"]))
                generated = {"verification.json": "verification.json"}
                if name == "rank-two":
                    generated.update(
                        {
                            "exact_controls.json": "exact_controls.json",
                            "return_control.json": "return_control.json",
                        }
                    )
            for output, expected in generated.items():
                require(
                    (folder / output).read_bytes() == (source / expected).read_bytes(),
                    f"Regenerated bytes differ: {name}/{expected}",
                )
                compared.append({"file": expected, "sha256": sha256(folder / output)})
            if name == "rank-two":
                commands.append(run_command(folder, ["oracle.py"]))
        if mode != "reports" and name in UNIT_FILES:
            commands.append(
                run_command(folder, ["-m", "unittest", "-v", UNIT_FILES[name]])
            )
    return {
        "packet": name,
        "mode": mode,
        "compared_reports": compared,
        "commands": commands,
    }


def candidate_replay(require_primary: bool = False) -> dict:
    commands = [
        run_command(
            ROOT, ["check_candidate.py", "--check", "nine-orbit-candidate.json"]
        )
    ]
    report = json.loads((ROOT / "nine-orbit-candidate.json").read_text())
    require(report["survives_earlier_filters"] is True, "Earlier-filter status changed")
    certificates = report["right_angle_containment_obstructions"]
    require(
        len(certificates) == 6, "Expected six existing-rule containment certificates"
    )
    primary = (
        ROOT.parents[1]
        / "incoming/c3-own-side-eight-orbits-2026-09-05/c3_eight_check.py"
    )
    if primary.exists():
        content = primary.read_bytes()
        blob = hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()
        require(
            blob == PRIMARY_BLOB,
            "Pinned primary checker source changed; review required",
        )
        spec = importlib.util.spec_from_file_location(
            "erdos97_bridge_publication_primary", primary
        )
        require(
            spec is not None and spec.loader is not None, "Cannot load primary checker"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        geometry = module.Geometry(report["rows"])
        for certificate in certificates:
            require(
                geometry.verify_containment(certificate),
                "Primary containment rejection failed",
            )
        primary_result = {
            "checked": True,
            "certificates": len(certificates),
            "source_git_blob": blob,
        }
    else:
        require(
            not require_primary,
            "Existing repository checker is required but unavailable",
        )
        primary_result = {
            "checked": False,
            "reason": "Isolated packet copy lacks the repository checker",
        }
    return {
        "commands": commands,
        "existing_checker_replay": primary_result,
        "geometric_status": "REJECTED_BY_EXISTING_RIGHT_ANGLE_CONTAINMENT_RULE",
        "scope": "This fixed nine-orbit order only; no all-nine-orbit exclusion",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--manifest-only", action="store_true")
    mode.add_argument("--unit-only", action="store_true")
    mode.add_argument("--report-only", action="store_true")
    mode.add_argument("--candidate-only", action="store_true")
    parser.add_argument("--packet", choices=["all", *PACKETS], default="all")
    parser.add_argument("--require-primary", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {
        "schema": 1,
        "status": "FOCUSED_REPLAY_NOT_MATHEMATICAL_ACCEPTANCE",
        "manifests": verify_manifests(),
        "runs": [],
    }
    if not args.manifest_only and not args.candidate_only:
        chosen = list(PACKETS) if args.packet == "all" else [args.packet]
        selected_mode = (
            "units" if args.unit_only else "reports" if args.report_only else "full"
        )
        for packet in chosen:
            result["runs"].append(replay_packet(packet, selected_mode))
    if args.check or args.candidate_only:
        result["candidate"] = candidate_replay(args.require_primary)
    result["post_replay_manifests"] = verify_manifests()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
