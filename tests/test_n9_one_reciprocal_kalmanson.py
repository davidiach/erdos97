from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_n9_one_reciprocal_kalmanson import (
    EXPECTED_DIHEDRAL_ORBITS,
    EXPECTED_LABELLED_STATUS_PAIRS,
    audit_one_reciprocal,
    edge_index,
    find_acyclic_orientation,
    one_reciprocal_status_orbits,
)


ROOT = Path(__file__).resolve().parents[1]


def test_one_reciprocal_status_orbit_count() -> None:
    orbits = one_reciprocal_status_orbits()

    assert len(orbits) == EXPECTED_DIHEDRAL_ORBITS
    assert sum(orbits.values()) == EXPECTED_LABELLED_STATUS_PAIRS


def test_one_reciprocal_single_status_closes() -> None:
    survivor, search_nodes = find_acyclic_orientation(
        edge_index(0, 1),
        edge_index(0, 2),
    )

    assert survivor is None
    assert search_nodes > 0


def test_one_reciprocal_audit_cli_limited_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_one_reciprocal_kalmanson.py",
            "--limit-representatives",
            "3",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert '"checked_representatives": 3' in result.stdout
    assert '"kalmanson_acyclic_survivors_found": 0' in result.stdout
    assert '"checked_all": false' in result.stdout
    assert '"trust": "REVIEW_PENDING_DIAGNOSTIC"' in result.stdout


def test_one_reciprocal_limited_import_audit() -> None:
    audit = audit_one_reciprocal(limit_representatives=2)

    assert audit["checked_representatives"] == 2
    assert audit["kalmanson_acyclic_survivors_found"] == 0
    assert audit["checked_all"] is False
    assert audit["schema"] == "erdos97.n9_one_reciprocal_kalmanson.v1"
