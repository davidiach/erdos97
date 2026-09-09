"""Load the byte-pinned preceding packet in temporary directories."""
from pathlib import Path
import hashlib,importlib.util,tempfile,zipfile,sys
ROOT=Path(__file__).resolve().parent
EXPECTED='dfd032636763cf67c45338c22f24334eb9e5b17367a0de57b00eb074cdfea0e1'
_holders=[]
_cache={}

def unpack(archive,destination):
    with zipfile.ZipFile(archive)as z:
        for item in z.infolist():
            path=Path(item.filename)
            if path.is_absolute()or'..'in path.parts:raise ValueError('unsafe archive member')
        z.extractall(destination)

def previous_root():
    if 'root'not in _cache:
        archive=ROOT/'inputs/internal_support.zip'
        if hashlib.sha256(archive.read_bytes()).hexdigest()!=EXPECTED:raise ValueError('preceding archive hash mismatch')
        t=tempfile.TemporaryDirectory(prefix='erdos97-prior-');_holders.append(t);unpack(archive,t.name)
        roots=list(Path(t.name).glob('*/kalmanson.py'))
        if len(roots)!=1:raise ValueError('unexpected prior layout')
        _cache['root']=roots[0].parent
    return _cache['root']

def module_from(name,path):
    if name not in _cache:
        spec=importlib.util.spec_from_file_location(name,path)
        if spec is None or spec.loader is None:raise ValueError('cannot load prior module')
        mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);_cache[name]=mod
    return _cache[name]

def load_kalmanson():
    return module_from('erdos97_prior_kalmanson',previous_root()/'kalmanson.py')

def load_quadratic():
    root=previous_root();archive=root/'inputs/cap_closure.zip'
    if 'cap'not in _cache:
        t=tempfile.TemporaryDirectory(prefix='erdos97-cap-');_holders.append(t);unpack(archive,t.name)
        candidates=list(Path(t.name).glob('*/prior_math/quadratic.py'))
        if len(candidates)!=1:raise ValueError('unexpected nested cap layout')
        _cache['cap']=candidates[0]
    return module_from('erdos97_prior_quadratic',_cache['cap'])
