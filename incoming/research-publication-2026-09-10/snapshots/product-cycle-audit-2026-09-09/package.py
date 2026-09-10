"""Create/check a file integrity manifest and a byte-verified ZIP.
No integrity result is a mathematical proof or a claim of exhaustive search.
"""
from pathlib import Path
import argparse,hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parent
EXCLUDED={'__pycache__','.pytest_cache','.git'}

def files():
    return sorted(p for p in ROOT.rglob('*')if p.is_file()and not EXCLUDED.intersection(p.relative_to(ROOT).parts)and p.name!='manifest.json'and p.suffix not in {'.pyc','.zip'})

def inventory():
    return {p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in files()}

def validate(saved):
    if saved.get('schema')!=1 or saved.get('files')!=inventory():raise ValueError('File inventory or SHA256 mismatch')
    return len(saved['files'])

def main():
    if sys.flags.optimize:raise ValueError('Keep assertions enabled')
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--zip',type=Path);a=p.parse_args()
    manifest=ROOT/'manifest.json'
    if a.check:
        count=validate(json.loads(manifest.read_text()));print(json.dumps({'status':'PASS_FILE_INTEGRITY_ONLY','files':count}));return
    data={'schema':1,'scope':'byte integrity only, not mathematical validation','files':inventory()};manifest.write_text(json.dumps(data,indent=2)+'\n');validate(data)
    result={'status':'PASS_MANIFEST_GENERATED','files':len(data['files'])}
    if a.zip:
        if ROOT==a.zip.resolve()or ROOT in a.zip.resolve().parents:raise ValueError('Put the ZIP outside the packet')
        a.zip.parent.mkdir(parents=True,exist_ok=True)
        members=files()+[manifest]
        with zipfile.ZipFile(a.zip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
            for source in members:z.write(source,arcname=ROOT.name+'/'+source.relative_to(ROOT).as_posix())
        with zipfile.ZipFile(a.zip)as z:
            if len(z.infolist())!=len(members):raise ValueError('ZIP member count')
            for source in members:
                if z.read(ROOT.name+'/'+source.relative_to(ROOT).as_posix())!=source.read_bytes():raise ValueError('ZIP bytes differ')
            if z.testzip()is not None:raise ValueError('ZIP CRC failure')
        result.update(zip=str(a.zip),zip_members=len(members),zip_bytes=a.zip.stat().st_size,zip_sha256=hashlib.sha256(a.zip.read_bytes()).hexdigest(),byte_readback=True)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
