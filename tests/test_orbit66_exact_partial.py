import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.check_orbit66_exact_partial import build_payload, validate_payload


def test_orbit66_exact_partial_summary() -> None:
    payload = build_payload(bits=128)

    assert validate_payload(payload) == []
    assert payload["status"] == "EXACT_PARTIAL_CONSTRUCTION_NOT_A_COUNTEREXAMPLE"
    assert payload["summary"]["exact_maximum_multiplicity_distribution"] == {
        2: 3,
        3: 3,
        4: 60,
    }
    assert payload["summary"]["exceptional_orbits"] == [3, 7]


@pytest.mark.parametrize("output_mode", ["--json", "--summary-json"])
def test_failed_cli_verification_preserves_json_stdout(output_mode: str) -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "check_orbit66_exact_partial.py"),
            "--bits",
            "64",
            output_mode,
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["validation_status"] == "failed"
    assert payload["errors"]
    assert payload["errors"][0] in result.stderr
