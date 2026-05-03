#!/usr/bin/env python3
"""Run all exact certificate checks in the merged round-two handoff."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    kal = load_script("check_kalmanson_certificate", ROOT / "scripts" / "check_kalmanson_certificate.py")
    pto = load_script("check_ptolemy_log_filter", ROOT / "scripts" / "check_ptolemy_log_filter.py")
    c19 = ROOT / "data" / "certificates" / "round2" / "c19_kalmanson_known_order_two_unsat.json"
    c19_legacy = ROOT / "data" / "certificates" / "round2" / "c19_kalmanson_known_order_unsat.json"
    c17_pto = ROOT / "data" / "certificates" / "round2" / "c17_skew_ptolemy_log_certificate.json"
    c17_kal = ROOT / "data" / "certificates" / "round2" / "c17_skew_kalmanson_from_ptolemy_method_note.json"
    c19_summary = dict(kal.check_certificate_file(c19)._asdict())
    c19_summary["path"] = str(c19.relative_to(ROOT))
    c19_legacy_summary = dict(kal.check_certificate_file(c19_legacy)._asdict())
    c19_legacy_summary["path"] = str(c19_legacy.relative_to(ROOT))
    c17_kal_summary = dict(kal.check_certificate_file(c17_kal)._asdict())
    c17_kal_summary["path"] = str(c17_kal.relative_to(ROOT))
    summaries = {
        "c19_kalmanson_promoted_compact": c19_summary,
        "c19_kalmanson_legacy_large": c19_legacy_summary,
        "c17_ptolemy_method_note": pto.verify_certificate_object(json.loads(c17_pto.read_text(encoding="utf-8"))),
        "c17_kalmanson_translation_regression": c17_kal_summary,
    }
    print(json.dumps(summaries, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
