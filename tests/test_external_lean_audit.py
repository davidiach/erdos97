"""Synthetic harness tests; these are not Lean proof-verification receipts."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from erdos97 import external_lean_audit as audit

PACKET = Path(__file__).resolve().parents[1] / 'incoming/external-n9-d2-audit-2026-09-10'


def axiom_line(name: str, axioms: str = 'propext, Classical.choice, Quot.sound') -> str:
    return f"'{name}' depends on axioms:\n[{axioms}]\n"


def test_core_axiom_reports():
    assert audit.check_axioms(axiom_line('A') + axiom_line('B', 'Quot.sound'), ['A', 'B']) == {
        'A': ['Classical.choice', 'Quot.sound', 'propext'], 'B': ['Quot.sound'],
    }


def test_axiom_free_reports():
    assert audit.check_axioms("'A' does not depend on any axioms\n", ['A']) == {'A': []}
    assert audit.check_axioms(axiom_line('A', ''), ['A']) == {'A': []}


@pytest.mark.parametrize('text', [
    '', 'Build completed successfully.\n', axiom_line('Wrong'),
    axiom_line('A') + axiom_line('Extra'),
    "'A' depends on axioms: [propext\n",
    axiom_line('A') + "'B' depends on axioms: [\n",
    "'A' depends on axioms: [propext] trailing text\n",
    "'A' does not depend on any axioms trailing text\n",
])
def test_missing_unexpected_or_incomplete_report_fails(text):
    with pytest.raises(audit.AuditError):
        audit.check_axioms(text, ['A'])


@pytest.mark.parametrize('axiom', ['sorryAx', 'Lean.ofReduceBool', 'Lean.trustCompiler', 'custom.axiom'])
def test_no_unapproved_axiom(axiom):
    with pytest.raises(audit.AuditError, match='Unapproved'):
        audit.check_axioms(axiom_line('A', f'propext, {axiom}'), ['A'])


@pytest.mark.parametrize('text', [axiom_line('A') * 2, axiom_line('A', 'propext, propext')])
def test_duplicates_fail(text):
    with pytest.raises(audit.AuditError, match='Duplicate'):
        audit.check_axioms(text, ['A'])


@pytest.mark.parametrize('expected', [[], ['A', 'A']])
def test_empty_or_duplicate_roster_fails(expected):
    with pytest.raises(audit.AuditError):
        audit.check_axioms('', expected)


def test_source_blob_hash_is_checked(tmp_path):
    path = tmp_path / 'source.lean'
    path.write_bytes(b'original\n')
    pin = audit.git_blob_sha(path.read_bytes())
    audit.check_blob(path, pin)
    path.write_bytes(b'changed\n')
    with pytest.raises(audit.AuditError, match='mismatch'):
        audit.check_blob(path, pin)
    with pytest.raises(audit.AuditError, match='Invalid'):
        audit.check_blob(path, '0' * 40)
    with pytest.raises(audit.AuditError, match='Invalid'):
        audit.check_blob(path, pin[:7])


def test_paths_cannot_escape(tmp_path):
    inside = tmp_path / 'inside'
    inside.mkdir()
    outside = tmp_path / 'outside.txt'
    outside.write_text('x')
    (inside / 'link').symlink_to(outside)
    for name in ('../outside.txt', str(outside), 'link'):
        with pytest.raises(audit.AuditError, match='escapes'):
            audit.confined_file(inside, name)


def test_only_dependency_caches_are_allowed(tmp_path):
    dependency = tmp_path / '.lake/packages/mathlib/.lake/build/lib/lean/Mathlib.olean'
    dependency.parent.mkdir(parents=True)
    dependency.write_bytes(b'cache')
    audit.require_fresh_project(tmp_path)
    stale = tmp_path / '.lake/build/lib/lean/Erdos9796Proof.olean'
    stale.parent.mkdir(parents=True)
    stale.write_bytes(b'stale')
    with pytest.raises(audit.AuditError, match='Stale'):
        audit.require_fresh_project(tmp_path)


@pytest.mark.parametrize('relative', ['Erdos9796Proof/X.olean', 'Erdos9796.olean'])
def test_adjacent_compiled_sources_fail(tmp_path, relative):
    stale = tmp_path / relative
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_bytes(b'stale')
    with pytest.raises(audit.AuditError, match='Precompiled'):
        audit.require_fresh_project(tmp_path)


def test_manifest_is_readable():
    manifest = audit.read_manifest(PACKET / 'manifest.json')
    assert manifest['scope']['accepted_claims_changed'] is False
    assert set(manifest['groups']) == {'n9', 'd2'}


@pytest.mark.parametrize('mutation', ['native_axiom', 'zero_pin', 'missing_group', 'duplicate_root', 'scope_change', 'missing_declaration', 'substituted_declaration'])
def test_manifest_mutations_fail(tmp_path, mutation):
    manifest = json.loads((PACKET / 'manifest.json').read_text())
    for harness in ('N9Audit.lean', 'D2Audit.lean'):
        (tmp_path / harness).write_bytes((PACKET / harness).read_bytes())
    if mutation == 'native_axiom':
        manifest['permitted_axioms'].append('Lean.trustCompiler')
    elif mutation == 'zero_pin':
        manifest['upstream']['commit'] = '0' * 40
    elif mutation == 'missing_group':
        del manifest['groups']['n9']
    elif mutation == 'scope_change':
        manifest['scope']['accepted_claims_changed'] = True
    elif mutation == 'missing_declaration':
        manifest['groups']['n9']['declarations'].pop()
    elif mutation == 'substituted_declaration':
        manifest['groups']['n9']['declarations'][0] = 'Different.statement'
    else:
        manifest['groups']['n9']['declarations'] *= 2
    path = tmp_path / 'manifest.json'
    path.write_text(json.dumps(manifest))
    with pytest.raises(audit.AuditError):
        audit.read_manifest(path)


def test_run_logged_captures_failure(tmp_path):
    log = tmp_path / 'log'
    code = audit.run_logged([sys.executable, '-c', "print('complete'); raise SystemExit(7)"], tmp_path, log, 5)
    assert code == 7
    assert 'complete' in log.read_text()


def test_run_logged_times_out(tmp_path):
    log = tmp_path / 'log'
    code = audit.run_logged([sys.executable, '-u', '-c', "import time; print('start'); time.sleep(60)"], tmp_path, log, 1)
    assert code == 124
    assert 'AUDIT COMMAND TIMED OUT' in log.read_text()


def test_preflight_failure_writes_nonverification_receipt(tmp_path, monkeypatch):
    def fail(*args):
        raise audit.AuditError('wrong pin')
    monkeypatch.setattr(audit, 'source_preflight', fail)
    output = tmp_path / 'out'
    assert audit.run_audit(tmp_path / 'checkout', PACKET, output, 5) == 1
    receipt = json.loads((output / 'receipt.json').read_text())
    assert receipt['status'] == 'NOT_VERIFIED'
    assert receipt['accepted_claims_changed'] is False
    assert receipt['groups'] == {}


@pytest.mark.parametrize('failure', [None, 'build', 'missing_report', 'sorry', 'lock_change', 'head_change', 'harness_during_build', 'later_harness', 'earlier_harness', 'cancelled'])
def test_receipt_requires_both_groups_and_stable_inputs(tmp_path, monkeypatch, failure):
    checkout = tmp_path / 'checkout'
    (checkout / 'lean').mkdir(parents=True)
    lock = checkout / 'lean/lake-manifest.json'
    lock.write_text('{}')
    source = {'lake_manifest_sha256': audit.sha256(lock)}
    raw_manifest = json.loads((PACKET / 'manifest.json').read_text())
    packet = tmp_path / 'packet'
    packet.mkdir()
    for name in ('manifest.json', 'N9Audit.lean', 'D2Audit.lean'):
        (packet / name).write_bytes((PACKET / name).read_bytes())
    for relative in raw_manifest['source_blobs']:
        source_file = checkout / relative
        source_file.parent.mkdir(parents=True, exist_ok=True)
        if not source_file.exists():
            source_file.write_text('synthetic source')
    monkeypatch.setattr(audit, 'source_preflight', lambda *args: copy.deepcopy(source))
    monkeypatch.setattr(audit, 'check_dependencies', lambda *args: {'mathlib': 'a' * 40})
    def fake_git(_checkout, *args):
        if args == ('rev-parse', 'HEAD'):
            return 'b' * 40 if failure == 'head_change' else 'd6b8e128af554eb430d060a31f26f863cea97c14'
        return ''
    monkeypatch.setattr(audit, 'git_text', fake_git)
    monkeypatch.setattr(audit, 'check_blob', lambda *args: None)
    monkeypatch.setattr(subprocess, 'check_output', lambda *args, **kwargs: 'Lean (version 4.33.1, release)')
    manifest = audit.read_manifest(PACKET / 'manifest.json')
    def fake_run(command, cwd, log, timeout):
        name = log.name.split('-')[0]
        if failure == 'cancelled':
            raise KeyboardInterrupt
        if name == 'n9' and 'build' in log.name and failure == 'harness_during_build':
            (packet / 'N9Audit.lean').write_text('changed consumer')
        if name == 'n9' and failure == 'later_harness':
            (packet / 'D2Audit.lean').write_text('changed later consumer')
        if name == 'd2' and failure == 'earlier_harness':
            (packet / 'N9Audit.lean').write_text('changed earlier consumer')
        if 'build' in log.name:
            log.write_text('synthetic build result\n')
            return 1 if name == 'n9' and failure == 'build' else 0
        declarations = manifest['groups'][name]['declarations']
        text = ''.join(axiom_line(n) for n in declarations)
        if name == 'n9' and failure == 'missing_report':
            text = ''
        if name == 'n9' and failure == 'sorry':
            text = text.replace('propext', 'sorryAx')
        log.write_text(text)
        if failure == 'lock_change':
            lock.write_text('{"changed": true}')
        return 0
    monkeypatch.setattr(audit, 'run_logged', fake_run)
    output = tmp_path / 'out'
    if failure == 'cancelled':
        with pytest.raises(KeyboardInterrupt):
            audit.run_audit(checkout, packet, output, 5)
        receipt = json.loads((output / 'receipt.json').read_text())
        assert receipt['status'] == 'NOT_VERIFIED'
        assert receipt['inputs_rechecked_after_execution'] is False
        assert receipt['groups']['n9']['status'] == 'NOT_VERIFIED'
        assert 'finished_utc' not in receipt
        return
    result = audit.run_audit(checkout, packet, output, 5)
    receipt = json.loads((output / 'receipt.json').read_text())
    assert (result == 0) == (failure is None)
    if failure != 'harness_during_build':
        assert set(receipt['groups']) == {'n9', 'd2'}
    assert receipt['inputs_rechecked_after_execution'] == (failure in (None, 'build', 'missing_report', 'sorry'))
    assert receipt['accepted_claims_changed'] is False
    assert receipt['independent_second_kernel_replay'] is False


def test_existing_evidence_is_never_silently_reused(tmp_path):
    output = tmp_path / 'out'
    output.mkdir()
    (output / 'receipt.json').write_text('old')
    with pytest.raises(audit.AuditError, match='reuse'):
        audit.run_audit(tmp_path / 'checkout', PACKET, output, 5)
