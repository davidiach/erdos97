"""Full isolated incoming-artifact replay, separate from fast unit checks."""
import importlib.util
from pathlib import Path
import pytest


@pytest.mark.artifact
def test_all_preserved_exact_evidence_20260910():
    path = Path(__file__).with_name('publication.py')
    spec = importlib.util.spec_from_file_location('_publication_artifact_20260910', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    result = mod.run_scoped()
    assert result['status'] == 'PASS_SCOPED_PUBLICATION_REPLAY'
    assert result['stored_fixed_system_contradiction_records'] == 2531
    assert result['exact_geometric_controls'] == 9
