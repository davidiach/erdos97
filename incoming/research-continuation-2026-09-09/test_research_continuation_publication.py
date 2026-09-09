"""Publication integrity checks plus explicitly artifact-marked research replays."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("erdos97_continuation_publication_20260909", ROOT / "publication.py")
assert SPEC is not None and SPEC.loader is not None
PUB = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PUB
SPEC.loader.exec_module(PUB)


def test_all_source_bytes_and_original_manifests() -> None:
    result = PUB.check_provenance()
    assert result["source_files"] == 325
    assert result["original_manifest_entries"] == 319
    assert len(result["nested_archives_matched"]) == 5


@pytest.mark.parametrize("name", ["../escape", "/absolute", "folder/../../escape", r"folder\escape", ""])
def test_unsafe_paths_rejected(name: str, tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        PUB.checked_path(tmp_path, name)


def test_symlink_rejected(tmp_path: Path) -> None:
    original = tmp_path / "real"
    original.write_text("retained", encoding="utf-8")
    (tmp_path / "link").symlink_to(original)
    with pytest.raises(ValueError):
        PUB.checked_path(tmp_path, "link")


def test_six_packets_and_unique_replay_names() -> None:
    assert len(PUB.PACKETS) == 6
    assert len(set(PUB.PACKETS.values())) == 6
    assert set(PUB.SCOPED_COMMANDS) == set(PUB.PACKETS)
    assert all(PUB.SCOPED_COMMANDS.values())


@pytest.mark.parametrize("returncode", [0, 7])
def test_replay_unicode_and_failure_reporting(tmp_path: Path, monkeypatch, returncode: int) -> None:
    """Exercise real subprocess output and failure handling under a legacy locale."""
    source = tmp_path / "snapshots" / "sample"
    source.mkdir(parents=True)
    (source / "message.txt").write_text("Erd\u0151s", encoding="utf-8")
    (source / "check.py").write_text(
        "from pathlib import Path\nimport sys\n"
        "print(Path('message.txt').read_text())\n"
        f"sys.exit({returncode})\n", encoding="utf-8",
    )
    monkeypatch.setattr(PUB, "ROOT", tmp_path)
    monkeypatch.setattr(PUB, "PACKETS", {"sample": "sample"})
    monkeypatch.setattr(PUB, "SCOPED_COMMANDS", {"sample": [(".", ["check.py"])]})
    monkeypatch.setattr(PUB, "check_provenance", lambda: {"status": "passed"})
    monkeypatch.setenv("PYTHONUTF8", "0")
    monkeypatch.setenv("PYTHONIOENCODING", "ascii")
    result = PUB.run_packet("sample")
    assert result["status"] == ("passed" if returncode == 0 else "failed")
    assert result["commands"][0]["stdout"] == "Erd\u0151s\n"
    assert result["commands"][0]["returncode"] == returncode
    assert result["source_integrity_unchanged"]


def test_replay_exposes_skipped_test_class(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "snapshots" / "sample"
    source.mkdir(parents=True)
    (source / "check.py").write_text(
        "import unittest\n"
        "class NeedsCompiler(unittest.TestCase):\n"
        "    @classmethod\n"
        "    def setUpClass(cls): raise unittest.SkipTest('compiler absent')\n"
        "    def test_one(self): pass\n"
        "    def test_two(self): pass\n"
        "unittest.main()\n", encoding="utf-8",
    )
    monkeypatch.setattr(PUB, "ROOT", tmp_path)
    monkeypatch.setattr(PUB, "PACKETS", {"sample": "sample"})
    monkeypatch.setattr(PUB, "SCOPED_COMMANDS", {"sample": [(".", ["check.py"])]})
    monkeypatch.setattr(PUB, "check_provenance", lambda: {"status": "passed"})
    result = PUB.run_packet("sample")
    assert result["status"] == "passed"
    assert result["unit_tests_run"] == 0
    assert result["unittest_reported_skips"] == 1


@pytest.mark.artifact
@pytest.mark.parametrize("packet", list(PUB.PACKETS))
def test_isolated_packet_replay(packet: str) -> None:
    result = PUB.run_packet(packet, full=True)
    assert result["source_integrity_unchanged"]
    assert result["status"] == "passed", result
