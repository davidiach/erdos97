"""Fail-closed, source-pinned audit of selected external Lean declarations.

A passing receipt checks the named consumers, not the external project as a
whole. It never promotes the local repository's accepted mathematical claims.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import signal
import subprocess
from typing import Any

from erdos97.json_io import load_json, write_json

CORE_AXIOMS = frozenset({'propext', 'Classical.choice', 'Quot.sound'})
NAME = re.compile(r'[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*\Z')
SHA = re.compile(r'[0-9a-f]{40}\Z')
AXIOM_REPORT = re.compile(
    r"^'([^'\n]+)' (?:depends on axioms:\s*\[([^\]]*)\]|"
    r"does not depend on any axioms)", re.MULTILINE,
)


class AuditError(ValueError):
    """A required audit condition was not established."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(data: bytes) -> str:
    """Git's object ID, including the blob header (not a raw-content SHA-1)."""
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def check_blob(path: Path, expected: str) -> None:
    if not SHA.fullmatch(expected) or expected == '0' * 40:
        raise AuditError(f'Invalid blob pin for {path.name}')
    actual = git_blob_sha(path.read_bytes())
    if actual != expected:
        raise AuditError(f'Blob mismatch for {path.name}: {actual} != {expected}')


def check_axioms(text: str, expected: list[str]) -> dict[str, list[str]]:
    """Require exactly one complete report per expected declaration.

    Grepping for the absence of sorryAx is not enough: an empty or incomplete
    log, duplicate report, or unexpected declaration is an error as well.
    """
    if not expected or len(expected) != len(set(expected)):
        raise AuditError('The expected declaration roster must be nonempty and unique')
    matches = list(AXIOM_REPORT.finditer(text))
    headers = re.findall(
        r"^'[^'\n]+' (?:depends on axioms:|does not depend on any axioms)",
        text, re.MULTILINE,
    )
    if len(matches) != len(headers):
        raise AuditError('Incomplete or malformed axiom report')
    found: dict[str, list[str]] = {}
    for match in matches:
        name, raw = match.groups()
        if name in found:
            raise AuditError(f'Duplicate axiom report: {name}')
        axioms = [] if raw is None or not raw.strip() else [s.strip() for s in raw.split(',')]
        if any(not NAME.fullmatch(s) for s in axioms):
            raise AuditError(f'Malformed axiom list for {name}')
        if len(axioms) != len(set(axioms)):
            raise AuditError(f'Duplicate axiom in report for {name}')
        forbidden = set(axioms) - CORE_AXIOMS
        if forbidden:
            raise AuditError(f'Unapproved axioms for {name}: {sorted(forbidden)}')
        found[name] = sorted(axioms)
    if set(found) != set(expected):
        raise AuditError(
            f'Axiom roster mismatch: missing={sorted(set(expected) - set(found))}, '
            f'unexpected={sorted(set(found) - set(expected))}'
        )
    return found


def confined_file(root: Path, relative: str) -> Path:
    path = root / relative
    if Path(relative).is_absolute() or root.resolve() not in path.resolve().parents:
        raise AuditError(f'Path escapes its audit root: {relative}')
    if not path.is_file():
        raise AuditError(f'Missing input: {relative}')
    return path


def read_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    if not isinstance(manifest, dict) or manifest.get('schema') != 'external-n9-d2-audit/v1':
        raise AuditError('Unsupported audit manifest')
    upstream = manifest['upstream']
    if upstream['repository'] != 'mysticflounder/erdos-97-96-formalization':
        raise AuditError('Unexpected upstream repository')
    if not SHA.fullmatch(upstream['commit']) or upstream['commit'] == '0' * 40:
        raise AuditError('Upstream must be pinned to a nonzero full commit SHA')
    if set(manifest['permitted_axioms']) != CORE_AXIOMS:
        raise AuditError('This audit does not permit a compiler-trusted tier')
    if set(manifest['groups']) != {'n9', 'd2'}:
        raise AuditError('The n9/D2 audit group roster changed')
    for group in manifest['groups'].values():
        names = group['declarations']
        modules = group['modules']
        if not names or len(names) != len(set(names)) or not modules:
            raise AuditError('Empty or duplicate target roster')
        if any(not isinstance(n, str) or not NAME.fullmatch(n) for n in names + modules):
            raise AuditError('Invalid Lean declaration or module name')
        confined_file(path.parent, group['harness'])
    if any(value is not False for value in manifest['scope'].values()):
        raise AuditError('This audit cannot promote or broaden a claim')
    if not manifest['source_blobs']:
        raise AuditError('Missing source-blob pins')
    return manifest


def git_text(checkout: Path, *args: str) -> str:
    return subprocess.check_output(
        ['git', '-C', str(checkout), *args], text=True, stderr=subprocess.STDOUT,
    ).strip()


def require_fresh_project(lean_root: Path) -> None:
    """Dependency caches are allowed; previous project proof outputs are not."""
    if any((lean_root / '.lake' / 'build').rglob('*.olean')):
        raise AuditError('Stale project .olean files: use a fresh isolated checkout')
    for source_root in lean_root.iterdir():
        if source_root.name == '.lake':
            continue
        if (source_root.is_file() and source_root.suffix == '.olean') or (
            source_root.is_dir() and any(source_root.rglob('*.olean'))
        ):
            raise AuditError('Precompiled files in the project source tree')


def source_preflight(checkout: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    upstream = manifest['upstream']
    actual = git_text(checkout, 'rev-parse', 'HEAD')
    if actual != upstream['commit']:
        raise AuditError(f'Wrong upstream commit: {actual}')
    if git_text(checkout, 'status', '--porcelain', '--untracked-files=all'):
        raise AuditError('Upstream checkout is not clean')
    for relative, expected in manifest['source_blobs'].items():
        check_blob(confined_file(checkout, relative), expected)
    if (checkout / 'lean-toolchain').read_text().strip() != upstream['toolchain']:
        raise AuditError('Unexpected upstream toolchain')
    for key in ('LEAN_PATH', 'LEAN_SRC_PATH', 'LEAN_SYSROOT', 'ELAN_TOOLCHAIN'):
        if os.environ.get(key):
            raise AuditError(f'Remove the environment override {key}')
    require_fresh_project(checkout / 'lean')
    return {
        'commit': actual,
        'tree': git_text(checkout, 'rev-parse', 'HEAD^{tree}'),
        'source_blobs': manifest['source_blobs'],
        'toolchain': upstream['toolchain'],
        'lake_manifest_sha256': sha256(checkout / 'lean' / 'lake-manifest.json'),
        'project_outputs_initially_absent': True,
    }


def check_dependencies(lean_root: Path) -> dict[str, str]:
    """Check materialized Git dependencies against the committed Lake lock."""
    lock = load_json(lean_root / 'lake-manifest.json')
    if lock.get('packagesDir', '.lake/packages') != '.lake/packages':
        raise AuditError('Unexpected Lake dependency directory')
    packages: dict[str, str] = {}
    for package in lock['packages']:
        name, revision = package['name'], package.get('rev', '')
        if (package.get('type') != 'git' or not SHA.fullmatch(revision)
                or not re.fullmatch(r'[A-Za-z0-9_-]+', name)):
            raise AuditError(f'Unpinned or unsupported dependency: {name}')
        root = lean_root / '.lake' / 'packages' / name
        actual = git_text(root, 'rev-parse', 'HEAD')
        if actual != revision or git_text(root, 'status', '--porcelain', '--untracked-files=all'):
            raise AuditError(f'Dependency source mismatch: {name}')
        if name in packages:
            raise AuditError(f'Duplicate dependency name: {name}')
        packages[name] = actual
    if not packages:
        raise AuditError('No locked dependencies were checked')
    return packages


def run_logged(command: list[str], cwd: Path, log: Path, timeout: int) -> int:
    """Capture complete output and terminate subprocess trees on timeout."""
    print('Running: ' + ' '.join(command), flush=True)
    with log.open('w', encoding='utf-8', newline='\n') as stream:
        process = subprocess.Popen(
            command, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            stream.write('\nAUDIT COMMAND TIMED OUT\n')
            return 124


def run_audit(checkout: Path, packet: Path, output: Path, timeout: int) -> int:
    checkout, packet, output = checkout.resolve(), packet.resolve(), output.resolve()
    if output == checkout or checkout in output.parents:
        raise AuditError('Keep audit outputs outside the upstream checkout')
    if output.exists() and any(output.iterdir()):
        raise AuditError('Refusing to reuse an evidence directory; choose an empty output')
    output.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        'schema': 'external-n9-d2-receipt/v1',
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'NOT_VERIFIED',
        'accepted_claims_changed': False,
        'independent_second_kernel_replay': False,
        'groups': {},
    }
    try:
        manifest_path = packet / 'manifest.json'
        manifest = read_manifest(manifest_path)
        report['manifest_sha256'] = sha256(manifest_path)
        report['source'] = source_preflight(checkout, manifest)
        lean_root = checkout / 'lean'
        report['dependencies'] = check_dependencies(lean_root)
        version = subprocess.check_output(['lake', 'env', 'lean', '--version'], cwd=lean_root, text=True)
        expected_version = manifest['upstream']['toolchain'].split(':v', 1)[1]
        if not re.search(r'\bversion ' + re.escape(expected_version) + r'(?=,|\s|\))', version):
            raise AuditError(f'Unexpected compiler version: {version.strip()}')
        report['compiler_version'] = version.strip()
        for name in ('n9', 'd2'):
            group = manifest['groups'][name]
            result: dict[str, Any] = {'status': 'NOT_VERIFIED'}
            report['groups'][name] = result
            harness = confined_file(packet, group['harness'])
            result['harness_sha256'] = sha256(harness)
            build_log, axiom_log = output / f'{name}-build.log', output / f'{name}-axioms.log'
            build_command = ['lake', 'build', *('+' + module for module in group['modules'])]
            result['build_command'] = build_command
            result['build_exit_code'] = run_logged(build_command, lean_root, build_log, timeout)
            result['build_log_sha256'] = sha256(build_log)
            if result['build_exit_code'] != 0:
                result['status'] = 'BUILD_FAILED'
                continue
            lean_command = ['lake', 'env', 'lean', str(harness)]
            result['harness_command'] = lean_command
            result['harness_exit_code'] = run_logged(lean_command, lean_root, axiom_log, timeout)
            result['axiom_log_sha256'] = sha256(axiom_log)
            if sha256(harness) != result['harness_sha256']:
                raise AuditError('A statement harness changed during compilation')
            if result['harness_exit_code'] != 0:
                result['status'] = 'HARNESS_FAILED'
                continue
            try:
                result['axioms'] = check_axioms(axiom_log.read_text(), group['declarations'])
                result['status'] = 'CORE_AXIOM_AUDIT_PASSED'
            except AuditError as exc:
                result['status'], result['error'] = 'AXIOM_AUDIT_FAILED', str(exc)
        # Recheck source and lock stability after executing external build code.
        if git_text(checkout, 'rev-parse', 'HEAD') != manifest['upstream']['commit']:
            raise AuditError('Upstream commit changed during the build')
        for relative, expected in manifest['source_blobs'].items():
            check_blob(confined_file(checkout, relative), expected)
        if sha256(manifest_path) != report['manifest_sha256']:
            raise AuditError('The audit manifest changed during the build')
        if git_text(checkout, 'status', '--porcelain', '--untracked-files=all'):
            raise AuditError('Upstream sources changed during the build')
        if check_dependencies(lean_root) != report['dependencies']:
            raise AuditError('Dependency pins changed during the build')
        if sha256(lean_root / 'lake-manifest.json') != report['source']['lake_manifest_sha256']:
            raise AuditError('Lake manifest changed during the build')
        if all(row['status'] == 'CORE_AXIOM_AUDIT_PASSED' for row in report['groups'].values()):
            report['status'] = 'CORE_AXIOM_AUDIT_PASSED'
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        report['status'], report['error'] = 'NOT_VERIFIED', str(exc)
    report['finished_utc'] = datetime.now(timezone.utc).isoformat()
    write_json(report, output / 'receipt.json')
    print(f"Audit status: {report['status']}; receipt: {output / 'receipt.json'}", flush=True)
    return 0 if report['status'] == 'CORE_AXIOM_AUDIT_PASSED' else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkout', required=True, type=Path)
    parser.add_argument('--packet', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--timeout', type=int, default=1800)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 3600:
        parser.error('--timeout must be between 1 and 3600 seconds per command')
    try:
        return run_audit(args.checkout, args.packet, args.output, args.timeout)
    except (AuditError, OSError) as exc:
        parser.exit(1, f'Audit refused: {exc}\n')
