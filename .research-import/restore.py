"""Temporary, hash-pinned publication adapter; removed from the final PR diff."""
from __future__ import annotations

import gzip
import hashlib
import json
import lzma
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'incoming/c3-seven-orbit-diamond-2026-09-05'
SOURCE = ROOT / 'incoming/c3-common-suppliers-2026-09-05'
PACK_HASH = 'd33b3897ab42f213e99bfe95922634f29e6f2de17544c1b443d20e04e7665bb7'
MANIFEST_HASH = '3c99862cbdb2125ea1c0240c7c4f16abddefd67a8222460accbd7ded5b793cd6'
RAW_HASH = 'f893b7f903123e8898af9021b156d2d66be87988b496fdd1aaa03efd42c6c2f7'
COPIES = {
    'common-supplier-background.md': 'README.md',
    'common_supplier_background.py': 'check_common_suppliers.py',
    'common_supplier_certificates.json': 'certificates.json',
    'audit_expanded_model.py': 'audit_expanded_model.py',
    'core.py': 'core.py',
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def check_files(allow_missing_proof: bool = False) -> dict:
    manifest_data = (DEST / 'manifest.json').read_bytes()
    require(digest(manifest_data) == MANIFEST_HASH, 'Pinned manifest mismatch')
    manifest = json.loads(manifest_data)
    expected = {item['file'] for item in manifest['files']} | {'manifest.json'}
    actual = {p.name for p in DEST.iterdir() if p.is_file()}
    if allow_missing_proof:
        expected.remove('phase_certificates.bin.gz')
    require(actual == expected, 'Unexpected publication file set')
    for item in manifest['files']:
        if allow_missing_proof and item['file'] == 'phase_certificates.bin.gz':
            continue
        data = (DEST / item['file']).read_bytes()
        require(len(data) == item['bytes'] and digest(data) == item['sha256'],
                'File hash mismatch: ' + item['file'])
    return manifest


def main() -> None:
    require(not DEST.exists(), 'Publication directory already exists')
    packed = b''.join((ROOT / '.research-import' / f'payload-{i}.xzpart').read_bytes() for i in range(7))
    require(digest(packed) == PACK_HASH, 'Source package hash mismatch')
    texts = json.loads(lzma.decompress(packed))
    require(isinstance(texts, dict) and len(texts) == 22, 'Wrong source package shape')
    require(all(isinstance(k, str) and Path(k).name == k and not k.startswith('.') and isinstance(v, str)
                for k, v in texts.items()), 'Unsafe source filename')
    DEST.mkdir(parents=True)
    for name, text in texts.items():
        (DEST / name).write_bytes(text.encode('utf-8'))
    for dest_name, source_name in COPIES.items():
        shutil.copyfile(SOURCE / source_name, DEST / dest_name)
    check_files(allow_missing_proof=True)
    compiler = shutil.which('c++')
    require(compiler is not None, 'C++17 compiler missing')
    print('Text files restored and hash-verified; regenerating the binary proof.', flush=True)
    with tempfile.TemporaryDirectory(prefix='seven-import-') as temp:
        tmp = Path(temp)
        binary = tmp / 'phase_search'
        proof = tmp / 'phase.bin'
        subprocess.run([compiler, '-std=c++17', '-O3', str(DEST / 'phase_search.cpp'), '-o', str(binary)],
                       check=True, timeout=180)
        with (DEST / 'radial_graphs.txt').open('rb') as src, (tmp / 'residuals.jsonl').open('wb') as out, (tmp / 'search.log').open('wb') as err:
            subprocess.run([str(binary), str(proof)], stdin=src, stdout=out, stderr=err, check=True, timeout=1200)
        raw = proof.read_bytes()
        require(len(raw) == 38592008 and digest(raw) == RAW_HASH, 'Regenerated raw proof mismatch')
        with (DEST / 'phase_certificates.bin.gz').open('wb') as out:
            with gzip.GzipFile(filename='', mode='wb', fileobj=out, compresslevel=9, mtime=0) as compressed:
                compressed.write(raw)
    check_files()
    print(json.dumps({'restored_files': 28, 'zlib': zlib.ZLIB_RUNTIME_VERSION,
                      'compressed_sha256': digest((DEST / 'phase_certificates.bin.gz').read_bytes()),
                      'all_original_bytes_preserved': True}), flush=True)
    validation = Path(os.environ.get('RUNNER_TEMP', tempfile.gettempdir())) / 'seven-import-validation.json'
    subprocess.run([sys.executable, 'verify.py', '--check', '--full', '--output', str(validation)],
                   cwd=DEST, check=True, timeout=1200)
    subprocess.run([sys.executable, '-m', 'unittest', '-v', 'test_diamond_seven.py'],
                   cwd=DEST, check=True, timeout=300)
    check_files()
    print('Publication replay and all unit tests passed; original hashes unchanged.', flush=True)


if __name__ == '__main__':
    main()
