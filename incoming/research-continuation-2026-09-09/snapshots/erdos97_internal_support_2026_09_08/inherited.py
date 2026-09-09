"""Read-only, hash-bound extraction of the delivered preceding packet."""
from pathlib import Path
import atexit
import hashlib
import importlib.util
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
_CACHE = {}
_TEMP = None
EXPECTED_ARCHIVE_SHA256 = "0a81018d0cb791362dda69506bc5044b260ef8d21d8627820dcf5f86234cc33c"

def archive_hash():
    return hashlib.sha256((ROOT/'inputs/cap_closure.zip').read_bytes()).hexdigest()

def location():
    global _TEMP
    if archive_hash() != EXPECTED_ARCHIVE_SHA256:
        raise ValueError("inherited archive SHA256 differs from the delivered input")
    if _TEMP is None:
        _TEMP = tempfile.TemporaryDirectory(prefix='erdos97-cap-input-')
        atexit.register(_TEMP.cleanup)
        destination = Path(_TEMP.name).resolve()
        with zipfile.ZipFile(ROOT/'inputs/cap_closure.zip') as archive:
            for info in archive.infolist():
                target = (destination/info.filename).resolve()
                if destination not in target.parents:
                    raise ValueError('unsafe inherited archive member')
            archive.extractall(destination)
    return Path(_TEMP.name)/'erdos97_cap_closure_packet_2026_09_08'

def load(name):
    if name not in ('core','oracle','replay'):
        raise ValueError('unrecognized dependency')
    if name not in _CACHE:
        path = location()/f'{name}.py'
        key = '_erdos97_inherited_'+name
        spec = importlib.util.spec_from_file_location(key,path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[key] = module
        spec.loader.exec_module(module)
        _CACHE[name] = module
    return _CACHE[name]
