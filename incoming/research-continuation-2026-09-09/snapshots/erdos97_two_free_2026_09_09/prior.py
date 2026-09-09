"""Load the preceding packet without modifying its archived source files."""
from __future__ import annotations

import atexit
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
from types import ModuleType
import zipfile

ROOT = Path(__file__).resolve().parent
EXPECTED_SHA256 = "dfd032636763cf67c45338c22f24334eb9e5b17367a0de57b00eb074cdfea0e1"
_CACHE: dict[str, ModuleType] = {}
_TEMP: tempfile.TemporaryDirectory | None = None


def archive_hash() -> str:
    digest = hashlib.sha256((ROOT / "inputs/internal_support.zip").read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("Preceding research archive has a different hash")
    return digest


def location() -> Path:
    global _TEMP
    if archive_hash() != EXPECTED_SHA256:
        raise ValueError("Preceding research archive has a different hash")
    if _TEMP is None:
        _TEMP = tempfile.TemporaryDirectory(prefix="erdos97-two-free-input-")
        atexit.register(_TEMP.cleanup)
        destination = Path(_TEMP.name).resolve()
        with zipfile.ZipFile(ROOT / "inputs/internal_support.zip") as archive:
            for entry in archive.infolist():
                target = (destination / entry.filename).resolve()
                if destination not in target.parents:
                    raise ValueError("Unsafe archive path")
            archive.extractall(destination)
    return Path(_TEMP.name) / "erdos97_internal_support_2026_09_08"


def load(name: str) -> ModuleType:
    if name not in ("one_free", "audit_one_free"):
        raise ValueError("Unknown mathematical dependency")
    if name not in _CACHE:
        directory = location()
        sys.path.insert(0, str(directory))
        key = "_two_free_preceding_" + name
        spec = importlib.util.spec_from_file_location(key, directory / (name + ".py"))
        if spec is None or spec.loader is None:
            raise ImportError(name)
        module = importlib.util.module_from_spec(spec)
        sys.modules[key] = module
        spec.loader.exec_module(module)
        _CACHE[name] = module
    return _CACHE[name]
