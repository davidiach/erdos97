#!/usr/bin/env python3
"""Degree-residue obstruction for the n=9 D=3 P19 profile-capacity rows.

This checker is finite profile-capacity bookkeeping only.  It closes the P19
rows of ``data/certificates/n9_base_apex_d3_incidence_capacity_packet.json`` by
an incident-degree congruence.  It does not prove n=9, does not claim a
counterexample, and does not test geometric realizability.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = (
    ROOT / "data" / "certificates" / "n9_base_apex_d3_incidence_capacity_packet.json"
)

SCHEMA = "erdos97.n9_base_apex_d3_p19_degree_obstruction.v1"
STATUS = "EXACT_FINITE_PROFILE_CAPACITY_OBSTRUCTION"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
CLAIM_SCOPE = (
    "Exact finite profile-capacity obstruction for the P19 rows R000..R007 of "
    "the n=9 base-apex D=3 incidence-capacity packet. This closes only the "
    "P19 profile multiset [0,0,0,0,0,0,0,0,6] inside that packet; it is not a "
    "proof of n=9, not a counterexample, not a geometric realizability test, "
    "not an incidence-completeness result, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_base_apex_d3_p19_degree_obstruction.py",
    "command": (
        "python scripts/check_n9_base_apex_d3_p19_degree_obstruction.py "
        "--check --assert-expected --json"
    ),
}

N = 9
P19_PROFILE_LEDGER_ID = "P19"
P19_REPRESENTATIVE_IDS = [f"R{index:03d}" for index in range(8)]
P19_EXCESS_MULTISET = [0, 0, 0, 0, 0, 0, 0, 0, 6]
FULL_INCIDENT_CAPACITY = 14
EXPECTED_PACKET_REPRESENTATIVE_COUNT = 88
EXPECTED_CLOSED_ROWS = 8
EXPECTED_REMAINING_ROWS = 80


def load_json(path: Path) -> Any:
    """Load a JSON value from ``path``."""

    return json.loads(path.read_text(encoding="utf-8"))


def deficient_degrees(row: Mapping[str, Any]) -> list[int]:
    """Return endpoint degrees of the three deficient base chords in one row."""

    degrees = [0] * N
    chords = row.get("deficient_base_chords")
    if not isinstance(chords, list):
        raise ValueError("row is missing deficient_base_chords")
    if len(chords) != 3:
        raise ValueError(f"expected exactly three deficient chords, got {len(chords)}")
    for item in chords:
        if not isinstance(item, Mapping):
            raise ValueError("deficient_base_chords entry is not an object")
        chord = item.get("chord")
        if (
            not isinstance(chord, list)
            or len(chord) != 2
            or not all(type(value) is int for value in chord)
        ):
            raise ValueError(f"malformed deficient chord: {chord!r}")
        left, right = chord
        if not (0 <= left < N and 0 <= right < N and left != right):
            raise ValueError(f"deficient chord has invalid endpoints: {chord!r}")
        degrees[left] += 1
        degrees[right] += 1
    return degrees


def repo_display_path(path: Path) -> str:
    """Return a stable POSIX-style path for JSON payloads."""

    if path.is_absolute():
        try:
            return path.relative_to(ROOT).as_posix()
        except ValueError:
            return path.as_posix()
    return path.as_posix()


def p19_row_obstruction(row: Mapping[str, Any]) -> dict[str, Any]:
    """Return the degree-residue obstruction record for one P19 row."""

    degrees = deficient_degrees(row)
    target_incident = [FULL_INCIDENT_CAPACITY - degree for degree in degrees]
    residues = [value % 3 for value in target_incident]
    failed_vertices = [vertex for vertex, residue in enumerate(residues) if residue]
    status = (
        "EXACT_PROFILE_CAPACITY_OBSTRUCTION"
        if failed_vertices
        else "NO_DEGREE_RESIDUE_OBSTRUCTION"
    )
    return {
        "representative_id": row.get("representative_id"),
        "profile_ledger_id": row.get("profile_ledger_id"),
        "escape_class_id": row.get("escape_class_id"),
        "status": status,
        "deficient_degree_by_vertex": degrees,
        "target_incident_capacity_by_vertex": target_incident,
        "target_incident_capacity_mod_3": residues,
        "failed_vertices": failed_vertices,
        "obstruction": (
            "In P19 every center has profile [4,1,1,1,1] or [4,4]. Either "
            "profile contributes 0 or 3 to the incident base-pair count of "
            "each vertex, so every realizable target incident count must be "
            "divisible by 3. The displayed deficient chords make at least one "
            "target incident count nonzero modulo 3."
        ),
    }


def p19_degree_obstruction_payload(
    packet: Mapping[str, Any],
    *,
    packet_path: Path = DEFAULT_PACKET,
) -> dict[str, Any]:
    """Return the P19 degree-obstruction audit payload."""

    errors: list[str] = []
    rows_value = packet.get("rows")
    if not isinstance(rows_value, list):
        rows: list[Mapping[str, Any]] = []
        errors.append("packet rows must be a list")
    else:
        rows = [row for row in rows_value if isinstance(row, Mapping)]
        if len(rows) != len(rows_value):
            errors.append("every packet row must be an object")

    p19_rows = [row for row in rows if row.get("profile_ledger_id") == P19_PROFILE_LEDGER_ID]
    p19_rows = sorted(p19_rows, key=lambda row: str(row.get("representative_id")))
    representative_ids = [str(row.get("representative_id")) for row in p19_rows]

    if packet.get("representative_count") != EXPECTED_PACKET_REPRESENTATIVE_COUNT:
        errors.append(
            "packet representative_count mismatch: "
            f"expected {EXPECTED_PACKET_REPRESENTATIVE_COUNT}, got "
            f"{packet.get('representative_count')!r}"
        )
    if representative_ids != P19_REPRESENTATIVE_IDS:
        errors.append(
            f"P19 representative ids mismatch: expected {P19_REPRESENTATIVE_IDS!r}, "
            f"got {representative_ids!r}"
        )

    row_records: list[dict[str, Any]] = []
    for row in p19_rows:
        if row.get("excess_multiset") != P19_EXCESS_MULTISET:
            errors.append(
                f"{row.get('representative_id')}: unexpected excess_multiset "
                f"{row.get('excess_multiset')!r}"
            )
        try:
            record = p19_row_obstruction(row)
        except ValueError as exc:
            errors.append(f"{row.get('representative_id')}: {exc}")
            continue
        if record["status"] != "EXACT_PROFILE_CAPACITY_OBSTRUCTION":
            errors.append(
                f"{row.get('representative_id')}: degree obstruction did not fire"
            )
        row_records.append(record)

    rows_closed = sum(
        1 for row in row_records if row["status"] == "EXACT_PROFILE_CAPACITY_OBSTRUCTION"
    )
    remaining_rows = max(0, EXPECTED_PACKET_REPRESENTATIVE_COUNT - rows_closed)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifact": repo_display_path(packet_path),
        "profile_ledger_id": P19_PROFILE_LEDGER_ID,
        "closed_representative_ids": P19_REPRESENTATIVE_IDS,
        "rows_closed": rows_closed,
        "remaining_packet_rows": remaining_rows,
        "modulus": 3,
        "full_incident_capacity_per_vertex": FULL_INCIDENT_CAPACITY,
        "degree_obstruction_summary": {
            "p19_profile_multiset": P19_EXCESS_MULTISET,
            "profile_incident_residue_reason": (
                "A [4,1,1,1,1] row contributes 3 to vertices in its 4-class "
                "and 0 to the other vertices. A [4,4] row contributes 3 to "
                "every non-center vertex. Hence P19 profile-capacity incident "
                "counts are vertexwise multiples of 3."
            ),
            "target_residue_reason": (
                "In a nonagon the full base-apex incident capacity at one "
                "vertex is 2 side capacities plus 6 diagonal capacities, "
                "namely 2*1 + 6*2 = 14. A D=3 row subtracts one from each "
                "endpoint of its three deficient chords."
            ),
            "global_sum_check": (
                "If all target incident counts were divisible by 3, every "
                "deficient endpoint degree would have to be 2 mod 3. With only "
                "three deficient chords the total deficient endpoint degree is "
                "6, so this is impossible for all nine vertices."
            ),
        },
        "rows": row_records,
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed check closes the P19 slice of the D=3 profile-capacity "
            "packet by exact incident-degree arithmetic. The other D=3 profile "
            "ledgers P20..P29 remain separate finite targets."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_p19_degree_obstruction(payload: Mapping[str, Any]) -> None:
    """Assert stable expected values for the P19 degree obstruction."""

    expected_top = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "profile_ledger_id": P19_PROFILE_LEDGER_ID,
        "closed_representative_ids": P19_REPRESENTATIVE_IDS,
        "rows_closed": EXPECTED_CLOSED_ROWS,
        "remaining_packet_rows": EXPECTED_REMAINING_ROWS,
        "modulus": 3,
        "full_incident_capacity_per_vertex": FULL_INCIDENT_CAPACITY,
        "provenance": PROVENANCE,
        "validation_status": "passed",
    }
    for key, expected in expected_top.items():
        if payload.get(key) != expected:
            raise AssertionError(
                f"payload[{key!r}] mismatch: expected {expected!r}, got {payload.get(key)!r}"
            )

    claim_scope = str(payload.get("claim_scope", ""))
    for required in (
        "not a proof of n=9",
        "not a counterexample",
        "not a geometric realizability test",
        "not an incidence-completeness result",
        "not a global status update",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")

    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) != EXPECTED_CLOSED_ROWS:
        raise AssertionError("unexpected P19 row record count")
    if [row.get("representative_id") for row in rows] != P19_REPRESENTATIVE_IDS:
        raise AssertionError("unexpected P19 row ids")
    for row in rows:
        if row.get("status") != "EXACT_PROFILE_CAPACITY_OBSTRUCTION":
            raise AssertionError(f"row did not close: {row!r}")
        residues = row.get("target_incident_capacity_mod_3")
        if not isinstance(residues, list) or all(residue == 0 for residue in residues):
            raise AssertionError(f"row has no nonzero residue: {row!r}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--check", action="store_true", help="load and check the packet artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    packet_path = args.packet if args.packet.is_absolute() else ROOT / args.packet
    try:
        packet = load_json(packet_path)
    except OSError as exc:
        print(f"FAILED: could not load {packet_path}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"FAILED: could not parse {packet_path}: {exc}", file=sys.stderr)
        return 1
    if not isinstance(packet, Mapping):
        print("FAILED: packet JSON must be an object", file=sys.stderr)
        return 1

    payload = p19_degree_obstruction_payload(packet, packet_path=packet_path)
    if args.assert_expected:
        try:
            assert_expected_p19_degree_obstruction(payload)
        except AssertionError as exc:
            print(f"FAILED: {exc}", file=sys.stderr)
            return 1

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "n=9 D=3 P19 degree obstruction: "
            f"{payload['rows_closed']} rows closed; "
            f"{payload['remaining_packet_rows']} packet rows remain"
        )
        if payload["validation_status"] != "passed":
            print("validation errors:", file=sys.stderr)
            for error in payload["validation_errors"]:
                print(f"- {error}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
