from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ARCHIVE_TO_RECONSTRUCTED = {
    2: 12,
    7: 11,
    8: 10,
    9: 14,
    19: 7,
    28: 9,
    51: 5,
    70: 6,
    88: 8,
    92: 2,
    117: 4,
    120: 1,
    134: 13,
    138: 3,
    139: 0,
}

EXPECTED_COMPATIBLE_COUNTS = {
    0: 2520,
    1: 280,
    2: 21,
    3: 2520,
    4: 280,
    5: 4,
    6: 280,
    7: 50,
    8: 538,
    9: 100,
    10: 74,
    11: 44,
    12: 0,
    13: 280,
    14: 72,
}


def run_artifact_script(repo: Path, *args: str) -> dict:
    script = repo / "scripts" / "analyze_n8_exact_survivors.py"
    result = subprocess.run(
        [sys.executable, str(script), "--check", "--json", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return json.loads(result.stdout)


def test_n8_exact_survivor_artifact_checks() -> None:
    repo = Path(__file__).resolve().parents[1]
    summary = run_artifact_script(repo)
    assert summary["survivor_classes"] == 15
    assert summary["cyclic_order_killed_ids"] == [12]
    assert summary["cyclic_order_remaining_count"] == 14
    assert summary["class3_duplicate_vertex_certificate_verified"] is True
    assert summary["class4_collinearity_certificate_verified"] is True
    assert summary["class5_groebner_contains_y2_after_exact_substitution"] is True
    assert summary["class14_pb_ed_groebner_basis_verified"] is True
    assert summary["class14_solution_branches_solve_pb_ed"] is True
    assert summary["class14_strict_interior_certificate_verified"] is True


def test_n8_archive_id_mapping_check(tmp_path: Path) -> None:
    repo = Path(__file__).resolve().parents[1]
    data_path = repo / "data" / "incidence" / "n8_reconstructed_15_survivors.json"
    reconstructed = json.loads(data_path.read_text(encoding="utf-8"))
    by_id = {int(item["id"]): item for item in reconstructed}

    archive_fixture = {"classes": []}
    for archive_id, reconstructed_id in sorted(ARCHIVE_TO_RECONSTRUCTED.items()):
        cls = by_id[reconstructed_id]
        rows_as_witness_sets = [
            [j for j, value in enumerate(row) if value]
            for row in cls["rows"]
        ]
        archive_fixture["classes"].append(
            {
                "id": archive_id,
                "rows": rows_as_witness_sets,
                "compatible_cyclic_orders_count": EXPECTED_COMPATIBLE_COUNTS[reconstructed_id],
            }
        )

    provenance_path = tmp_path / "n8_archive_fixture.json"
    provenance_path.write_text(json.dumps(archive_fixture), encoding="utf-8")

    summary = run_artifact_script(repo, "--provenance-json", str(provenance_path))
    provenance = summary["provenance_identity"]
    assert provenance["verified"] is True
    assert provenance["sets_equal"] is True
    assert provenance["expected_mapping_verified"] is True
    assert provenance["compatible_counts_verified"] is True
