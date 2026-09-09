#!/usr/bin/env python3
"""Check immutable research imports and replay them in isolated working copies.

Publication checks are not independent mathematical review. The default mode
checks provenance only. --scoped runs all 262 original unit tests plus the
listed bounded exact checks. --full adds the two complete two-free replayers
and the exhaustive C++ metric checks. All original snapshot bytes are checked
before and after; generated outputs stay in temporary copies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

ROOT = Path(__file__).resolve().parent
PACKETS = {
    "codesign": "erdos97_codesign_packet_2026_09_08",
    "cap-closure": "erdos97_cap_closure_packet_2026_09_08",
    "internal-support": "erdos97_internal_support_2026_09_08",
    "final-push": "erdos97_final_push_2026_09_09",
    "mixed-lens": "erdos97_mixed_support_2026_09_09",
    "two-free": "erdos97_two_free_2026_09_09",
}
# (relative working directory, arguments following Python)
SCOPED_COMMANDS: dict[str, list[tuple[str, list[str]]]] = {
    "codesign": [
        (".", ["verify.py"]),
        (".", ["oracle.py"]),
        (".", ["-m", "unittest", "-v", "test_research.py"]),
    ],
    "cap-closure": [
        (".", ["verify.py"]),
        (".", ["oracle.py"]),
        (".", ["-m", "unittest", "-v", "test_closure.py"]),
        (".", ["exploratory/one_free_relaxation.py"]),
    ],
    "internal-support": [
        (".", ["one_free.py"]),
        (".", ["audit_one_free.py"]),
        (".", ["combinatorics.py"]),
        (".", ["-m", "unittest", "-v", "test_internal_support.py"]),
    ],
    "final-push": [
        (".", ["grid_metric.py", "--check"]),
        (".", ["grid_oracle.py"]),
        (".", ["circle_star_metric.py", "--check"]),
        (".", ["circle_star_oracle.py"]),
        (".", ["turn_control.py", "--check"]),
        (".", ["audit_medians.py", "--check"]),
        (".", ["-m", "unittest", "-v", "test_final_push.py", "test_star_extension.py"]),
        ("parabola", ["verify.py", "--check"]),
        ("parabola", ["-m", "unittest", "-v", "test_parabola.py"]),
    ],
    "mixed-lens": [
        (".", ["verify.py", "--check"]),
        (".", ["oracle.py", "--check"]),
        (".", ["cap_pair_probe.py", "--check"]),
        (".", ["-m", "unittest", "-v", "test_mixed_lens.py"]),
        (".", ["check_manifest.py"]),
    ],
    "two-free": [
        (".", ["-S", "build_certificate.py", "--check"]),
        (".", ["-S", "last_leaf_audit.py", "--check"]),
        (".", ["-S", "sharpness.py", "--check"]),
        (".", ["-S", "audit_sharpness.py", "--check"]),
        (".", ["-S", "-m", "unittest", "-v", "test_two_free.py"]),
    ],
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_path(root: Path, name: str) -> Path:
    """Reject ambiguous paths, escapes, and symlink traversal."""
    p = PurePosixPath(name)
    if not name or p.is_absolute() or ".." in p.parts or "\\" in name:
        raise ValueError(f"unsafe path: {name!r}")
    target = root.joinpath(*p.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes root: {name!r}")
    for parent in (target, *target.parents):
        if parent == root:
            break
        if parent.is_symlink():
            raise ValueError(f"symlink forbidden: {name!r}")
    return target


def check_provenance(root: Path = ROOT) -> dict[str, Any]:
    """Check exact archive membership, original manifests, and nested archives."""
    data = json.loads((root / "provenance.json").read_text(encoding="utf-8"))
    snapshots = root / "snapshots"
    records = data["source_archives"]
    if len(records) != 6 or data["source_archive_count"] != 6:
        raise ValueError("expected all six source archives")
    if {x["root"] for x in records} != set(PACKETS.values()):
        raise ValueError("unexpected or missing source packet")
    names: set[str] = set()
    manifest_checks = 0
    nested_matches = []
    archives_by_hash = {x["archive_sha256"]: x["archive"] for x in records}
    for archive in records:
        packet_root = checked_path(snapshots, archive["root"])
        for entry in archive["files"]:
            name = entry["path"]
            if name in names or not name.startswith(archive["root"] + "/"):
                raise ValueError(f"duplicate or misassigned file: {name}")
            names.add(name)
            raw = checked_path(snapshots, name).read_bytes()
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if len(raw) != entry["bytes"] or digest(raw) != entry["sha256"] or blob != entry["git_blob_sha"]:
                raise ValueError(f"source-byte mismatch: {name}")
            if name.endswith(".zip") and digest(raw) in archives_by_hash:
                nested_matches.append({"path": name, "matches_archive": archives_by_hash[digest(raw)]})
        text_manifest = packet_root / "MANIFEST.sha256"
        if text_manifest.is_file():
            pairs = []
            for line in text_manifest.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    expected, name = line.split(None, 1)
                    pairs.append((name.strip(), expected))
        else:
            original = json.loads((packet_root / "manifest.json").read_text(encoding="utf-8"))
            pairs = [(name, meta["sha256"]) for name, meta in original["files"].items()]
        for name, expected in pairs:
            if digest(checked_path(packet_root, name).read_bytes()) != expected:
                raise ValueError(f"original manifest mismatch: {archive['root']}/{name}")
            manifest_checks += 1
    actual = {
        p.relative_to(snapshots).as_posix()
        for p in snapshots.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc")
    }
    if actual != names or len(names) != 325 or data["source_file_count"] != 325:
        raise ValueError("source snapshot file inventory mismatch")
    return {
        "status": "passed",
        "source_archives": len(records),
        "source_files": len(names),
        "original_manifest_entries": manifest_checks,
        "nested_archives_matched": nested_matches,
    }


def run_packet(key: str, *, full: bool = False, timeout: int = 3600) -> dict[str, Any]:
    """Run one packet in a temporary copy; never change the retained evidence."""
    if key not in PACKETS:
        raise ValueError(f"unknown packet: {key}")
    before = check_provenance()
    result: dict[str, Any] = {"packet": key, "full": full, "commands": [], "status": "running"}
    env = dict(
        os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0",
        PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
    )
    with tempfile.TemporaryDirectory(prefix="erdos97-publication-") as temporary:
        work = Path(temporary) / PACKETS[key]
        shutil.copytree(ROOT / "snapshots" / PACKETS[key], work)
        commands = list(SCOPED_COMMANDS[key])
        if full and key == "two-free":
            commands += [(".", ["-S", "verify.py", "--check"]), (".", ["-S", "oracle.py", "--check"])]
        if full and key == "final-push":
            commands.append((".", ["replay.py", "--full-metric", "--output", "publication-full.json"]))
        for subdir, args in commands:
            start = time.monotonic()
            argv = [sys.executable, *args]
            item: dict[str, Any] = {"command": ["python", *args], "relative_directory": subdir}
            try:
                completed = subprocess.run(
                    argv, cwd=work / subdir, env=env, text=True, encoding="utf-8",
                    capture_output=True, timeout=timeout, check=False,
                )
                item.update(returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
            except subprocess.TimeoutExpired as exc:
                def text(value: bytes | str | None) -> str:
                    return value.decode(errors="replace") if isinstance(value, bytes) else (value or "")
                item.update(returncode=None, timed_out=True, stdout=text(exc.stdout), stderr=text(exc.stderr))
            item["elapsed_seconds"] = round(time.monotonic() - start, 3)
            result["commands"].append(item)
            if item["returncode"] != 0:
                result["status"] = "failed"
                break
        else:
            result["status"] = "passed"
    result["source_integrity_unchanged"] = check_provenance() == before
    result["unit_tests_run"] = sum(
        int(m.group(1))
        for item in result["commands"]
        for m in re.finditer(r"^Ran (\d+) tests? in ", item.get("stderr", ""), re.MULTILINE)
    )
    # unittest counts a skipped setUpClass as one skip event, regardless of
    # how many test methods the class would have run. Do not call this a
    # count of skipped test methods or infer that all original tests ran.
    result["unittest_reported_skips"] = sum(
        int(m.group(1))
        for item in result["commands"]
        for m in re.finditer(
            r"^(?:OK|FAILED) \([^\n]*skipped=(\d+)",
            item.get("stderr", ""), re.MULTILINE,
        )
    )
    return result


def write_report(path: Path, result: Any) -> None:
    """Write portable JSON without Windows newline conversion."""
    if path.resolve().is_relative_to((ROOT / "snapshots").resolve()):
        raise ValueError("report cannot overwrite an immutable snapshot")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scoped", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--packet", choices=tuple(PACKETS))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result: dict[str, Any] = {
        "schema": "erdos97.research_continuation_publication_replay.v1",
        "python": sys.version.split()[0],
        "provenance": check_provenance(),
        "mode": "full" if args.full else ("scoped" if args.scoped else "integrity"),
        "independent_mathematical_review": False,
        "repository_wide_ci": False,
        "packets": [],
    }
    if args.scoped or args.full:
        for key in ([args.packet] if args.packet else list(PACKETS)):
            item = run_packet(key, full=args.full)
            result["packets"].append(item)
            print(
                f"{key}: {item['status']} ({item['unit_tests_run']} unit tests; "
                f"{item['unittest_reported_skips']} unittest skip events)",
                file=sys.stderr, flush=True,
            )
            if item["status"] != "passed":
                break
    result["status"] = "passed" if all(x["status"] == "passed" for x in result["packets"]) else "failed"
    result["source_integrity_after"] = check_provenance()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        write_report(args.output, result)
    print(rendered if not args.output else json.dumps({"status": result["status"], "report": str(args.output)}))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
