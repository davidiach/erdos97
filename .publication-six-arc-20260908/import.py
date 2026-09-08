"""One-shot, hash-pinned import on the explicitly authorized feature branch."""
from pathlib import Path, PurePosixPath
import base64
import hashlib
import importlib.metadata
import json
import lzma
import os
import platform
import shutil
import subprocess
import sys

BRANCH = "research/six-arc-product-obstructions-2026-09-08"
BASE = "d6ca181df32bb6fd5445280c049384da5d21ed01"
PREFIX = "incoming/six-arc-product-obstructions-2026-09-08/"
TRANSPORT = Path(".publication-six-arc-20260908")
WORKFLOW = Path(".github/workflows/import-six-arc-20260908.yml")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def run(args, **kwargs):
    return subprocess.run(args, check=True, text=True, capture_output=True, **kwargs)


def guard():
    require(os.environ.get("GITHUB_REPOSITORY") == "davidiach/erdos97", "Wrong repository")
    require(os.environ.get("GITHUB_REF") == "refs/heads/" + BRANCH, "Wrong branch")
    require(run(["git", "rev-parse", "HEAD"]).stdout.strip() == os.environ["GITHUB_SHA"], "HEAD changed")
    run(["git", "merge-base", "--is-ancestor", BASE, "HEAD"])


def extract():
    guard()
    parts = [TRANSPORT / f"chunk-{i:02d}.txt" for i in range(13)]
    encoded = "".join(p.read_text(encoding="ascii") for p in parts)
    require(len(encoded) == 76684, "Transport size mismatch")
    packed = base64.b64decode(encoded, validate=True)
    require(hashlib.sha256(packed).hexdigest() == "f1552c1350f9b2563b8d5db13fd6ad4bf7306deec7efca68abdf1fabebfed23a", "Packed hash mismatch")
    raw = lzma.decompress(packed)
    require(hashlib.sha256(raw).hexdigest() == "6cc1fa749dfea6a37f666fba02b678f2f10a311c6f7bd5f2f3ebf91dab0f8203", "Payload hash mismatch")
    mapping = json.loads(raw)
    require(isinstance(mapping, dict) and len(mapping) == 28, "Wrong file count")
    require(not Path(PREFIX).exists(), "Destination already exists")
    for name, text in mapping.items():
        rel = PurePosixPath(name)
        require(name.startswith(PREFIX) and not rel.is_absolute() and ".." not in rel.parts, "Unsafe path")
        require(isinstance(text, str), "Expected UTF-8 text")
        path = Path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    index = Path("incoming/README.md")
    require(run(["git", "hash-object", str(index)]).stdout.strip() == "54a9d040e01abb3399cbfbba24605be8d6f99ffe", "Incoming inventory changed")
    text = index.read_text(encoding="utf-8")
    require(text.count("All ten entries below") == 1, "Unexpected inventory count")
    require(text.count("\n## Historical imports\n") == 1, "Unexpected inventory layout")
    row = "| [Six-arc carrier and fixed-product obstructions](six-arc-product-obstructions-2026-09-08/README.md) | Review-pending six-arc good-point theorem, matched-equilateral certificates, fixed 27-point witness-system obstruction, and exact convex/nonconvex controls | `python replay.py --check`; `python -m pytest -q -o addopts='' test_publication.py` |\n"
    text = text.replace("All ten entries below", "All eleven entries below", 1)
    text = text.replace("\n## Historical imports\n", row + "\n## Historical imports\n", 1)
    index.write_text(text, encoding="utf-8")
    print("Imported 28 UTF-8 files; 18 archived originals will be hash-checked by replay.")


def validate_publish():
    guard()
    commands = [
        ([sys.executable, "replay.py", "--check", "--output", "reports/hosted-publication-replay.json"], PREFIX),
        ([sys.executable, "-m", "pytest", "-q", "-o", "addopts=", "test_publication.py"], PREFIX),
        ([sys.executable, "-m", "ruff", "check", PREFIX], "."),
        ([sys.executable, "scripts/generate_navigation.py", "--check"], "."),
    ]
    records = []
    for command, cwd in commands:
        proc = run(command, cwd=cwd, timeout=240)
        print(proc.stdout, end="")
        print(proc.stderr, end="", file=sys.stderr)
        records.append({"command": ["python", *command[1:]], "cwd": cwd,
                        "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})
    report = {
        "status": "PASS_HOSTED_SCOPED_PUBLICATION_VALIDATION",
        "python": platform.python_version(),
        "packages": {p: importlib.metadata.version(p) for p in ("sympy", "pytest", "ruff")},
        "workflow_run": f"https://github.com/davidiach/erdos97/actions/runs/{os.environ['GITHUB_RUN_ID']}",
        "source_base": BASE, "transport_commit": os.environ["GITHUB_SHA"], "branch": BRANCH,
        "original_files": 18, "publication_tests": 24, "commands": records,
        "repository_wide_fast_and_artifact_gates_run": False,
        "independent_external_mathematical_review": False, "unrestricted_solution": False,
    }
    (Path(PREFIX) / "reports/hosted-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    readme = Path(PREFIX) / "README.md"
    text = readme.read_text(encoding="utf-8")
    old = "A separate hosted report may record another execution;\nreplaying the same code is not external independent mathematical review."
    require(old in text, "Missing hosted-report insertion point")
    text = text.replace(old, "The separate [hosted validation](reports/hosted-validation.json) records\na successful Python 3.12 replay, all 24 focused tests, packet Ruff, and the\nrepository navigation check. Replaying the same code is not external\nindependent mathematical review.", 1)
    readme.write_text(text, encoding="utf-8")
    run([sys.executable, "replay.py", "--manifest-only"], cwd=PREFIX)
    shutil.rmtree(TRANSPORT)
    WORKFLOW.unlink()
    for directory in (".pytest_cache", "__pycache__"):
        for path in list(Path(PREFIX).rglob(directory)):
            if path.is_dir():
                shutil.rmtree(path)
    run(["git", "add", "--", PREFIX, "incoming/README.md", str(TRANSPORT), str(WORKFLOW)])
    run(["git", "diff", "--cached", "--check"])
    diff = run(["git", "diff", "--cached", "--name-only", BASE]).stdout.splitlines()
    require(all(p.startswith(PREFIX) or p == "incoming/README.md" for p in diff), "Out-of-scope final diff")
    require(len(diff) == 31, f"Unexpected final diff file count: {len(diff)}")
    run(["git", "config", "user.name", "github-actions[bot]"])
    run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])
    run(["git", "commit", "-m", "Research: preserve six-arc and fixed-product obstructions with audited exact replays"])
    print(run(["git", "push", "origin", "HEAD:refs/heads/" + BRANCH]).stdout)
    print(run(["git", "rev-parse", "HEAD"]).stdout)


if __name__ == "__main__":
    require(len(sys.argv) == 2 and sys.argv[1] in {"extract", "publish"}, "Use extract or publish")
    (extract if sys.argv[1] == "extract" else validate_publish)()
