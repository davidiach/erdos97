#!/usr/bin/env python3
"""Select expensive CI lanes from changed paths; errors must fail the scope job."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess

ARTIFACT_ROOTS = {'certificates', 'cpp', 'data', 'incoming', 'metadata', 'papers', 'reports', 'scripts', 'src', 'tests'}
DEPENDENCY_FILES = {'pyproject.toml', 'requirements-lock.txt', 'scripts/ci_scope.py'}


def classify(paths: list[str]) -> dict[str, bool]:
    workflows = any(p.startswith('.github/workflows/') for p in paths)
    return {
        'artifact': workflows or any(
            p.split('/')[0] in ARTIFACT_ROOTS or p in DEPENDENCY_FILES | {'Makefile', 'pytest.ini'}
            for p in paths
        ),
        'compatibility': workflows or any(p in DEPENDENCY_FILES for p in paths),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default=os.environ.get('PR_BASE'))
    parser.add_argument('--head', default=os.environ.get('PR_HEAD'))
    args = parser.parse_args()
    if args.base and args.head:
        output = subprocess.check_output(['git', 'diff', '--name-only', '--no-renames', '-z', f'{args.base}...{args.head}'])
        flags = classify([p for p in output.decode().split('\0') if p])
    elif args.base or args.head:
        parser.error('base and head must be supplied together')
    else:
        flags = {'artifact': True, 'compatibility': True}
    text = ''.join(f'{key}={str(value).lower()}\n' for key, value in flags.items())
    print(text, end='')
    if path := os.environ.get('GITHUB_OUTPUT'):
        with Path(path).open('a', encoding='utf-8') as stream:
            stream.write(text)


if __name__ == '__main__':
    main()
