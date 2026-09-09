"""Create or check the file manifest; optionally build a verified research ZIP."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def inventory():
    result = {}
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc':
            continue
        name = path.relative_to(ROOT).as_posix()
        if name == 'manifest.json':
            continue
        data = path.read_bytes()
        result[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    return result


def verify_validation():
    report = json.loads((ROOT / 'validation.json').read_text())
    if report['status'] != 'passed' or not report['mathematical_sources_unchanged']:
        raise ValueError('A complete successful validation is required')
    current = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(ROOT.glob('*.py'))
    }
    if current != report['source_hashes_after']:
        raise ValueError('Validated root source files have changed')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--zip', type=Path)
    args = parser.parse_args()
    verify_validation()
    files = inventory()
    manifest = {
        'schema': 'erdos97.two_free_manifest.v1',
        'claim_status': 'restricted computer-assisted proof candidate; review pending',
        'unrestricted_solution': False,
        'files': files,
    }
    path = ROOT / 'manifest.json'
    text = json.dumps(manifest, indent=2, sort_keys=True) + '\n'
    if args.check:
        if path.read_text() != text:
            raise ValueError('Manifest does not match actual packet files')
    else:
        path.write_text(text)
    result = {'status': 'passed', 'manifest_entries': len(files)}
    if args.zip is not None:
        target = args.zip.resolve()
        if target == ROOT or ROOT in target.parents:
            raise ValueError('Write the ZIP outside the source packet')
        members = sorted([*files, 'manifest.json'])
        with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name in members:
                info = zipfile.ZipInfo(f'{ROOT.name}/{name}', (2026, 9, 9, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, (ROOT / name).read_bytes())
        with zipfile.ZipFile(target) as archive:
            expected = [f'{ROOT.name}/{name}' for name in members]
            if archive.namelist() != expected or archive.testzip() is not None:
                raise ValueError('ZIP membership or CRC check failed')
            for name in members:
                if archive.read(f'{ROOT.name}/{name}') != (ROOT / name).read_bytes():
                    raise ValueError(f'ZIP bytes differ: {name}')
        # Guard against a file changing during packaging.
        if inventory() != files:
            raise ValueError('Packet changed while it was being packaged')
        data = target.read_bytes()
        result.update(zip=str(target), zip_files=len(members), zip_bytes=len(data),
                      zip_sha256=hashlib.sha256(data).hexdigest())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
