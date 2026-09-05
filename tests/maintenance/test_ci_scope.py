from __future__ import annotations

from pathlib import Path
import subprocess

import pytest
import yaml

from scripts.ci_scope import classify

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('path', ['src/erdos97/a.py', 'incoming/new/report.json', 'data/certificates/a.json', 'scripts/check.py', 'papers/release/a.zip', 'tests/a.py'])
def test_evidence_changes_require_artifact_checks(path):
    assert classify([path])['artifact']


def test_navigation_only_skips_expensive_lanes():
    assert classify(['docs/topics/a.md', 'STATE.md', 'CONTRIBUTING.md']) == {'artifact': False, 'compatibility': False}


@pytest.mark.parametrize('path', ['pyproject.toml', 'requirements-lock.txt', '.github/workflows/tests.yml', 'scripts/ci_scope.py'])
def test_dependency_changes_require_both_lanes(path):
    assert classify([path]) == {'artifact': True, 'compatibility': True}


@pytest.mark.parametrize('workflow,job,dependency', [
    ('tests.yml', 'compatibility-gate', 'compatibility-collect'),
    ('artifact-audit.yml', 'artifact-gate', 'artifact-pytest'),
])
def test_aggregate_fails_closed_and_accepts_only_intended_skips(workflow, job, dependency):
    config = yaml.load((ROOT / '.github/workflows' / workflow).read_text(), Loader=yaml.BaseLoader)
    assert 'pull_request' in config['on']
    assert not config['on']['pull_request']  # gate must report even for docs-only PRs
    gate = config['jobs'][job]
    assert gate['if'] == 'always()'
    assert set(gate['needs']) == {'scope', dependency}
    shell = gate['steps'][0]['run']
    for required, result, scope, passes in [
        ('true', 'success', 'success', True),
        ('false', 'skipped', 'success', True),
        ('true', 'skipped', 'success', False),
        ('true', 'failure', 'success', False),
        ('true', 'cancelled', 'success', False),
        ('false', 'skipped', 'failure', False),
    ]:
        outcome = subprocess.run(['bash', '-e', '-c', shell], env={'REQUIRED': required, 'RESULT': result, 'SCOPE_RESULT': scope})
        assert (outcome.returncode == 0) == passes


def test_ruleset_requires_always_reported_gate_names():
    import json

    rules = json.loads((ROOT / '.github/main-ruleset.json').read_text())['rules']
    required = next(rule['parameters']['required_status_checks'] for rule in rules if rule['type'] == 'required_status_checks')
    jobs = {}
    for path in (ROOT / '.github/workflows').glob('*.yml'):
        workflow = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
        jobs.update({job.get('name', key): job for key, job in workflow['jobs'].items()})
    for check in required:
        assert jobs[check['context']]['if'] == 'always()'
        assert check['integration_id'] == 15368
