"""Verify retained packet bytes without importing any mathematical checker."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent

def main():
    m=json.loads((ROOT/'manifest.json').read_text())
    for name,d in m['files'].items():
        p=ROOT/name
        if not p.is_file():raise ValueError('missing '+name)
        b=p.read_bytes()
        if len(b)!=d['bytes']or hashlib.sha256(b).hexdigest()!=d['sha256']:raise ValueError('hash mismatch '+name)
    print(json.dumps({'status':'passed','verified_files':len(m['files'])}))
if __name__=='__main__':main()
