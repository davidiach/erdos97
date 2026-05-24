"""Compile Lean pilot files when Lake is available."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--require-lean",
        action="store_true",
        help="fail instead of skipping when lake is not on PATH",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    lake = shutil.which("lake")
    if lake is None:
        print("lake not found; skipped Lean compilation")
        return 1 if args.require_lean else 0

    files = sorted((root / "lean").rglob("*.lean"))
    if not files:
        print("no Lean files found")
        return 0

    for path in files:
        rel = path.relative_to(root)
        print(f"checking {rel}")
        subprocess.run([lake, "env", "lean", str(path)], cwd=root, check=True)

    print(f"checked {len(files)} Lean file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
