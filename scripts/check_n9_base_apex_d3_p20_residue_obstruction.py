#!/usr/bin/env python3
"""Residue-count obstruction for the n=9 D=3 P20 profile-capacity rows.

This checker is finite profile-capacity bookkeeping only. It closes the P20
rows of ``data/certificates/n9_base_apex_d3_incidence_capacity_packet.json`` by
a mod-3 incident-residue support count. It does not prove n=9, does not claim a
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

SCHEMA = "erdos97.n9_base_apex_d3_p20_residue_obstruction.v1"
STATUS = "EXACT_FINITE_PROFILE_CAPACITY_OBSTRUCTION"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
CLAIM_SCOPE = (
    "Exact finite profile-capacity obstruction for the P20 rows R008..R015 of "
    "the n=9 base-apex D=3 incidence-capacity packet. This closes only the "
    "P20 profile multiset [0,0,0,0,0,0,0,1,5] inside that packet; it is not a "
    "proof of n=9, not a counterexample, not a geometric realizability test, "
    "not an incidence-completeness result, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_base_apex_d3_p20_residue_obstruction.py",
    "command": (
        "python scripts/check_n9_base_apex_d3_p20_residue_obstruction.py "
        "--check --assert-expected --json"
    ),
}

N = 9
P20_PROFILE_LEDGER_ID = "P20"
P20_REPRESENTATIVE_IDS = [f"R{index:03d}" for index in range(8, 16)]
P20_EXCESS_MULTISET = [0, 0, 0, 0, 0, 0, 0, 1, 5]
FULL_INCIDENT_CAPACITY = 14
EXPECTED_PACKET_REPRESENTATIVE_COUNT = 88
EXPECTED_CLOSED_ROWS = 8
P19_ROWS_ALREADY_CLOSED = 8
EXPECTED_COMBINED_CLOSED_ROWS = 16
EXPECTED_REMAINING_AFTER_THIS_CHECKER_ONLY = 80
EXPECTED_REMAINING_AFTER_P19_P20 = 72
PROFILE_MAX_RESIDUE_TWO_VERTICES = 2


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


def p20_row_obstruction(row: Mapping[str, Any]) -> dict[str, Any]:
    """Return the residue-support obstruction record for one P20 row."""

    degrees = deficient_degrees(row)
    target_incident = [FULL_INCIDENT_CAPACITY - degree for degree in degrees]
    target_residues = [value % 3 for value in target_incident]
    zero_deficient_vertices = [vertex for vertex, degree in enumerate(degrees) if degree == 0]
    target_residue_two_vertices = [
        vertex for vertex, residue in enumerate(target_residues) if residue == 2
    ]
    status = (
        "EXACT_PROFILE_CAPACITY_OBSTRUCTION"
        if len(target_residue_two_vertices) > PROFILE_MAX_RESIDUE_TWO_VERTICES
        else "NO_RESIDUE_SUPPORT_OBSTRUCTION"
    )
    return {
        "representative_id": row.get("representative_id"),
        "profile_ledger_id": row.get("profile_ledger_id"),
        "escape_class_id": row.get("escape_class_id"),
        "status": status,
        "deficient_degree_by_vertex": degrees,
        "zero_deficient_vertices": zero_deficient_vertices,
        "target_incident_capacity_by_vertex": target_incident,
        "target_incident_capacity_mod_3": target_residues,
        "target_residue_two_vertices": target_residue_two_vertices,
        "profile_max_residue_two_vertices": PROFILE_MAX_RESIDUE_TWO_VERTICES,
        "obstruction": (
            "In P20 the seven [4,1,1,1,1] rows contribute only multiples of 3 "
            "to every vertex incident count. The single [4,2,1,1] row can add "
            "residue 1 at exactly two vertices, and the single [5,2,1] row can "
            "add residue 1 at exactly seven vertices. Therefore residue 2 can "
            "appear at no more than two vertices on the profile side. The three "
            "deficient chords leave at least three vertices with deficient "
            "degree 0, and each such vertex has target incident capacity 14, "
            "which is 2 modulo 3."
        ),
    }


def p20_residue_obstruction_payload(
    packet: Mapping[str, Any],
    *,
    packet_path: Path = DEFAULT_PACKET,
) -> dict[str, Any]:
    """Return the P20 residue-obstruction audit payload."""

    errors: list[str] = []
    rows_value = packet.get("rows")
    if not isinstance(rows_value, list):
        rows: list[Mapping[str, Any]] = []
        errors.append("packet rows must be a list")
    else:
        rows = [row for row in rows_value if isinstance(row, Mapping)]
        if len(rows) != len(rows_value):
            errors.append("every packet row must be an object")

    p20_rows = [row for row in rows if row.get("profile_ledger_id") == P20_PROFILE_LEDGER_ID]
    p20_rows = sorted(p20_rows, key=lambda row: str(row.get("representative_id")))
    representative_ids = [str(row.get("representative_id")) for row in p20_rows]

    if packet.get("representative_count") != EXPECTED_PACKET_REPRESENTATIVE_COUNT:
        errors.append(
            "packet representative_count mismatch: "
            f"expected {EXPECTED_PACKET_REPRESENTATIVE_COUNT}, got "
            f"{packet.get('representative_count')!r}"
        )
    if representative_ids != P20_REPRESENTATIVE_IDS:
        errors.append(
            f"P20 representative ids mismatch: expected {P20_REPRESENTATIVE_IDS!r}, "
            f"got {representative_ids!r}"
        )

    row_records: list[dict[str, Any]] = []
    for row in p20_rows:
        if row.get("excess_multiset") != P20_EXCESS_MULTISET:
            errors.append(
                f"{row.get('representative_id')}: unexpected excess_multiset "
                f"{row.get('excess_multiset')!r}"
            )
        try:
            record = p20_row_obstruction(row)
        except ValueError as exc:
            errors.append(f"{row.get('representative_id')}: {exc}")
            continue
        if record["status"] != "EXACT_PROFILE_CAPACITY_OBSTRUCTION":
            errors.append(
                f"{row.get('representative_id')}: residue obstruction did not fire"
            )
        row_records.append(record)

    rows_closed = sum(
        1 for row in row_records if row["status"] == "EXACT_PROFILE_CAPACITY_OBSTRUCTION"
    )
    remaining_after_this_checker_only = max(
        0, EXPECTED_PACKET_REPRESENTATIVE_COUNT - rows_closed
    )
    combined_closed_rows = P19_ROWS_ALREADY_CLOSED + rows_closed
    remaining_after_p19_p20 = max(0, EXPECTED_PACKET_REPRESENTATIVE_COUNT - combined_closed_rows)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifact": repo_display_path(packet_path),
        "profile_ledger_id": P20_PROFILE_LEDGER_ID,
        "closed_representative_ids": P20_REPRESENTATIVE_IDS,
        "rows_closed": rows_closed,
        "remaining_packet_rows_after_this_checker_only": remaining_after_this_checker_only,
        "p19_rows_already_closed": P19_ROWS_ALREADY_CLOSED,
        "combined_p19_p20_closed_rows": combined_closed_rows,
        "remaining_packet_rows_after_p19_p20": remaining_after_p19_p20,
        "modulus": 3,
        "full_incident_capacity_per_vertex": FULL_INCIDENT_CAPACITY,
        "profile_residue_support_summary": {
            "p20_profile_multiset": P20_EXCESS_MULTISET,
            "profile_residue_reason": (
                "The P20 multiset has seven excess-0 rows, one excess-1 row, "
                "and one excess-5 row. Modulo 3, only the excess-1 and excess-5 "
                "rows can contribute nonzero incident residues. Their residue-1 "
                "supports have sizes 2 and 7 respectively, so their overlap can "
                "create residue 2 at at most two vertices."
            ),
            "target_residue_reason": (
                "In a nonagon the full base-apex incident capacity at one vertex "
                "is 2 side capacities plus 6 diagonal capacities, namely "
                "2*1 + 6*2 = 14. A D=3 row subtracts one from each endpoint of "
                "its three deficient chords, so every vertex missed by those "
                "three chords has target residue 14 mod 3 = 2."
            ),
            "global_support_check": (
                "Three deficient chords touch at most six vertices, hence miss at "
                "least three vertices. The target therefore needs residue 2 at at "
                "least three vertices, exceeding the P20 profile-side maximum of "
                "two residue-2 vertices."
            ),
        },
        "rows": row_records,
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed check closes the P20 slice of the D=3 profile-capacity "
            "packet by exact incident-residue support counting. Together with "
            "the existing P19 degree obstruction, this reduces the finite D=3 "
            "packet target from 88 rows to 72 rows. It does not decide any of "
            "the remaining P21..P29 rows."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_p20_residue_obstruction(payload: Mapping[str, Any]) -> None:
    """Assert stable expected values for the P20 residue obstruction."""

    expected_top = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "profile_ledger_id": P20_PROFILE_LEDGER_ID,
        "closed_representative_ids": P20_REPRESENTATIVE_IDS,
        "rows_closed": EXPECTED_CLOSED_ROWS,
        "remaining_packet_rows_after_this_checker_only": EXPECTED_REMAINING_AFTER_THIS_CHECKER_ONLY,
        "p19_rows_already_closed": P19_ROWS_ALREADY_CLOSED,
        "combined_p19_p20_closed_rows": EXPECTED_COMBINED_CLOSED_ROWS,
        "remaining_packet_rows_after_p19_p20": EXPECTED_REMAINING_AFTER_P19_P20,
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

    if payload.get("claim_scope") != CLAIM_SCOPE:
        raise AssertionError(f"claim_scope mismatch: {payload.get('claim_scope')!r}")
    claim_scope = CLAIM_SCOPE
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
        raise AssertionError("unexpected P20 row record count")
    if [row.get("representative_id") for row in rows] != P20_REPRESENTATIVE_IDS:
        raise AssertionError("unexpected P20 row ids")
    for row in rows:
        if row.get("status") != "EXACT_PROFILE_CAPACITY_OBSTRUCTION":
            raise AssertionError(f"row did not close: {row!r}")
        target_residue_two_vertices = row.get("target_residue_two_vertices")
        if (
            not isinstance(target_residue_two_vertices, list)
            or len(target_residue_two_vertices) <= PROFILE_MAX_RESIDUE_TWO_VERTICES
        ):
            raise AssertionError(f"row has insufficient target residue-2 support: {row!r}")


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

    payload = p20_residue_obstruction_payload(packet, packet_path=packet_path)
    if args.assert_expected:
        try:
            assert_expected_p20_residue_obstruction(payload)
        except AssertionError as exc:
            print(f"FAILED: {exc}", file=sys.stderr)
            return 1

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "n=9 D=3 P20 residue obstruction: "
            f"{payload['rows_closed']} rows closed; "
            "72 packet rows remain after P19+P20"
        )
        if payload["validation_status"] != "passed":
            print("validation errors:", file=sys.stderr)
            for error in payload["validation_errors"]:
                print(f"- {error}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
