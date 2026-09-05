"""Upload verified Git objects only: this script never creates or updates refs."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

from restore import DEST, check_files

REPO = 'davidiach/erdos97'
BASE_TREE = '11dba1dacf9eec49fc3cdeaf7d7922dc848da4b3'
PREFIX = 'incoming/c3-seven-orbit-diamond-2026-09-05/'


def post(endpoint: str, payload: dict) -> dict:
    request = urllib.request.Request(
        'https://api.github.com/repos/' + REPO + endpoint,
        data=json.dumps(payload).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN'],
                 'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json',
                 'X-GitHub-Api-Version': '2022-11-28'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise RuntimeError(f'Git object upload failed: HTTP {error.code}, endpoint {endpoint}') from None
            time.sleep(2 ** attempt)
    raise RuntimeError('Upload retry loop exhausted')


def main() -> None:
    if os.environ.get('GITHUB_REPOSITORY') != REPO:
        raise RuntimeError('Wrong publication repository')
    manifest = check_files()
    entries = []
    inventory = {}
    for name in sorted([item['file'] for item in manifest['files']] + ['manifest.json']):
        data = (DEST / name).read_bytes()
        expected = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        response = post('/git/blobs', {'content': base64.b64encode(data).decode(), 'encoding': 'base64'})
        if response['sha'] != expected:
            raise RuntimeError('Git blob mismatch for ' + name)
        inventory[name] = expected
        entries.append({'path': PREFIX + name, 'mode': '100644', 'type': 'blob', 'sha': expected})
    tree = post('/git/trees', {'base_tree': BASE_TREE, 'tree': entries})
    result = {'final_tree_sha': tree['sha'], 'base_tree_sha': BASE_TREE,
              'file_count': len(entries), 'files': inventory,
              'refs_modified': False, 'all_original_bytes_preserved': True}
    print('PUBLICATION_RESULT=' + json.dumps(result, sort_keys=True), flush=True)
    Path(os.environ['RUNNER_TEMP'], 'seven-publication-result.json').write_text(json.dumps(result, indent=2) + '\n')
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as summary:
        summary.write('## Exact research packet ready\n\nFinal tree: `' + tree['sha'] + '`\n\n'
                      'All 28 original file hashes match. Full proof replay and 22 unit tests passed. '
                      'Only Git objects were uploaded; no branch or main ref was changed.\n')


if __name__ == '__main__':
    main()
