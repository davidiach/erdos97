from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

SOFT_CLAIM_SCOPE_COERCION = re.compile(
    r"claim_scope\s*=\s*str\(\s*payload\.get\(\s*['\"]claim_scope['\"]"
)


def test_scripts_do_not_accept_claim_scope_by_string_coercion() -> None:
    offenders = []
    for path in sorted(SCRIPTS.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if SOFT_CLAIM_SCOPE_COERCION.search(text):
            offenders.append(path.relative_to(ROOT).as_posix())

    assert offenders == [], (
        "claim_scope validators must compare against the exact expected string; "
        f"found soft string-coercion guards in {offenders}"
    )
