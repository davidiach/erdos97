import ast
import importlib
from pathlib import Path


def test_migrated_cli_writers_preserve_historical_bytes(tmp_path):
    root = Path(__file__).resolve().parents[2]
    migrated = []
    for path in (root / 'scripts').glob('*.py'):
        tree = ast.parse(path.read_text())
        if any(isinstance(node, ast.ImportFrom) and node.module == 'erdos97.json_io' and any(alias.name == 'write_artifact' for alias in node.names) for node in tree.body):
            migrated.append(path)
    assert migrated
    for path in migrated:
        module = importlib.import_module(f'scripts.{path.stem}')
        destination = tmp_path / path.stem / 'artifact.json'
        module.write_artifact(destination, {'z': [2, 1], 'a': '\u00e9'})
        assert destination.read_bytes() == b'{\n  "a": "\\u00e9",\n  "z": [\n    2,\n    1\n  ]\n}\n'
