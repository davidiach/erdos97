from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

from scripts import build_n8_release_packet as release


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "papers" / "release"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checksum_map(path: Path) -> dict[str, str]:
    return {
        line.split("  ", 1)[1]: line.split("  ", 1)[0]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    }


def test_zip_writer_is_byte_stable_and_platform_neutral(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    (bundle / "zeta").mkdir(parents=True)
    (bundle / "zeta" / "b.txt").write_bytes(b"second\n")
    (bundle / "alpha.txt").write_bytes(b"first\n")
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"

    release.zip_bundle(bundle, first)
    os.utime(bundle / "alpha.txt", (1_900_000_000, 1_900_000_000))
    release.zip_bundle(bundle, second)

    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        infos = archive.infolist()
    assert [info.filename for info in infos] == sorted(info.filename for info in infos)
    for info in infos:
        assert "\\" not in info.filename
        assert info.date_time == release.ZIP_TIMESTAMP
        assert info.compress_type == zipfile.ZIP_STORED
        assert info.create_system == 3
        assert info.external_attr >> 16 == release.ZIP_FILE_MODE
        assert info.extra == b""
        assert info.comment == b""


def test_release_manifest_names_rebuildable_source_snapshot() -> None:
    manifest = json.loads(
        (RELEASE / release.BUNDLE_MANIFEST_NAME).read_text(encoding="utf-8")
    )
    source = manifest["source"]
    assert manifest["schema"] == "erdos97.n8_release_bundle.v2"
    assert source["repository_url"] == release.REPOSITORY_URL
    assert source["builder"] == {
        "path": release.BUILDER_PATH,
        "sha256": digest(ROOT / release.BUILDER_PATH),
    }
    tree = subprocess.check_output(
        ["git", "rev-parse", f"{source['commit']}^{{tree}}"], cwd=ROOT, text=True
    ).strip()
    assert source["tree"] == tree
    committed_builder = subprocess.check_output(
        ["git", "show", f"{source['commit']}:{release.BUILDER_PATH}"], cwd=ROOT
    )
    assert hashlib.sha256(committed_builder).hexdigest() == source["builder"]["sha256"]
    assert source["worktree"]["dirty"] is False
    assert manifest["environment"] == release.dependency_snapshot()


def test_extracted_bundle_checksums_links_and_reproduction_smoke(
    tmp_path: Path,
) -> None:
    zip_path = RELEASE / release.ZIP_NAME
    with zipfile.ZipFile(zip_path) as archive:
        infos = archive.infolist()
        assert [info.filename for info in infos] == sorted(info.filename for info in infos)
        assert all("\\" not in info.filename for info in infos)
        archive.extractall(tmp_path)

    bundle = tmp_path / release.BUNDLE_DIRECTORY_NAME
    internal_manifest = bundle / "BUNDLE_MANIFEST.json"
    assert internal_manifest.read_bytes() == (
        RELEASE / release.BUNDLE_MANIFEST_NAME
    ).read_bytes()
    manifest = json.loads(internal_manifest.read_text(encoding="utf-8"))
    for record in manifest["files"]:
        path = bundle / record["path"]
        assert path.is_file()
        assert path.stat().st_size == record["size_bytes"]
        assert digest(path) == record["sha256"]

    checksums = checksum_map(bundle / "SHA256SUMS.txt")
    for relative_path, expected in checksums.items():
        assert digest(bundle / relative_path) == expected
    for relative_path in release.BUNDLE_README_REFERENCES:
        assert (bundle / relative_path).is_file()

    assert not (bundle / "STATE.md").exists()
    assert not (bundle / "RESULTS.md").exists()
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(bundle / "src")
    smoke = subprocess.run(
        [
            sys.executable,
            "scripts/independent_check_n8_incidence_json.py",
            "--json",
        ],
        cwd=bundle,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert smoke.returncode == 0, smoke.stderr
    assert json.loads(smoke.stdout)["canonical_class_count"] == 15


def test_release_checksums_cover_every_output() -> None:
    checksums = checksum_map(RELEASE / "SHA256SUMS.txt")
    expected_names = set(release.RELEASE_OUTPUT_NAMES) - {"SHA256SUMS.txt"}
    assert set(checksums) == expected_names
    for name, expected in checksums.items():
        assert digest(RELEASE / name) == expected


def test_check_mode_does_not_modify_release_files() -> None:
    before = {name: digest(RELEASE / name) for name in release.RELEASE_OUTPUT_NAMES}
    check = subprocess.run(
        [sys.executable, "scripts/build_n8_release_packet.py", "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert check.returncode == 0, check.stderr
    after = {name: digest(RELEASE / name) for name in release.RELEASE_OUTPUT_NAMES}
    assert after == before
