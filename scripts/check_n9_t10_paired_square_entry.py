#!/usr/bin/env python3
"""Generate or check the n=9 T10 paired-square entry audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_CLASSIFICATION = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_frontier_motif_classification.json"
)
DEFAULT_STRICT_CYCLE_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_strict_cycle_template_packet.json"
)
DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n9_t10_paired_square_entry_audit.json"

SCHEMA = "erdos97.n9_t10_paired_square_entry_audit.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Paired-square Kalmanson entry audit for the 18 T10/F12 n=9 "
    "vertex-circle strict-cycle assignments only; not a proof of n=9, not a "
    "counterexample, and not a global status update."
)
EXPECTED_ASSIGNMENT_COUNT = 18
EXPECTED_HIT_ASSIGNMENT_COUNT = 18
EXPECTED_MISS_ASSIGNMENT_COUNT = 0
EXPECTED_HIT_COUNT = 54


Pair = tuple[int, int]


class DSU:
    """Tiny disjoint-set structure for unordered pair quotient classes."""

    def __init__(self) -> None:
        self.parent: dict[Pair, Pair] = {}

    def find(self, item: Pair) -> Pair:
        self.parent.setdefault(item, item)
        parent = self.parent[item]
        if parent != item:
            parent = self.find(parent)
            self.parent[item] = parent
        return parent

    def union(self, left: Pair, right: Pair) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            if right_root < left_root:
                left_root, right_root = right_root, left_root
            self.parent[right_root] = left_root


def pair(left: int, right: int) -> Pair:
    """Return a canonical unordered pair."""

    if left == right:
        raise ValueError("degenerate pair")
    return (left, right) if left < right else (right, left)


def load_json(path: Path) -> Any:
    """Load a JSON file."""

    return json.loads(path.read_text(encoding="utf-8"))


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def digest_json(payload: object) -> str:
    """Return the SHA-256 digest of a stable JSON rendering."""

    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def crosses(first: Pair, second: Pair, position: dict[int, int]) -> bool:
    """Return whether two chords cross in a fixed cyclic order."""

    a, b = sorted(first, key=position.__getitem__)
    c, d = sorted(second, key=position.__getitem__)

    def between(label: int, left: int, right: int) -> bool:
        return position[left] < position[label] < position[right]

    return between(c, a, b) != between(d, a, b)


def square_orientation(
    *,
    i: int,
    n: int,
    s: int,
    j: int,
    position: dict[int, int],
) -> str | None:
    """Return A/B when that selected-center square has a diagonal matching."""

    if len({i, n, s, j}) != 4:
        return None
    a_matching = (pair(i, s), pair(j, n))
    b_matching = (pair(i, n), pair(j, s))
    a_diagonal = crosses(*a_matching, position)
    b_diagonal = crosses(*b_matching, position)
    if a_diagonal == b_diagonal:
        return None
    return "A" if a_diagonal else "B"


def selected_rows_by_center(selected_rows: Sequence[Sequence[int]]) -> dict[int, set[int]]:
    """Parse compact selected rows into center -> witness set."""

    rows: dict[int, set[int]] = {}
    for raw in selected_rows:
        if len(raw) != 5:
            raise ValueError(f"selected row must have center plus four witnesses: {raw!r}")
        center = int(raw[0])
        witnesses = {int(label) for label in raw[1:]}
        if len(witnesses) != 4 or center in witnesses:
            raise ValueError(f"invalid selected row: {raw!r}")
        if center in rows:
            raise ValueError(f"duplicate selected row center: {center}")
        rows[center] = witnesses
    return rows


def quotient_for_rows(rows: dict[int, set[int]], n: int) -> DSU:
    """Build the selected-distance quotient for all unordered pairs."""

    dsu = DSU()
    for left in range(n):
        for right in range(left + 1, n):
            dsu.find((left, right))
    for center, witnesses in rows.items():
        spokes = [pair(center, witness) for witness in sorted(witnesses)]
        first = spokes[0]
        for spoke in spokes[1:]:
            dsu.union(first, spoke)
    return dsu


def quotient_vector(
    *,
    positive: Sequence[Pair],
    negative: Sequence[Pair],
    dsu: DSU,
) -> dict[str, int]:
    """Return the reduced quotient vector for a Kalmanson row."""

    coeffs: Counter[Pair] = Counter()
    for item in positive:
        coeffs[dsu.find(item)] += 1
    for item in negative:
        coeffs[dsu.find(item)] -= 1
    return {
        f"{left},{right}": coeff
        for (left, right), coeff in sorted(coeffs.items())
        if coeff
    }


def class_key(item: Pair) -> str:
    """Return the stable JSON key for one quotient class representative."""

    return f"{item[0]},{item[1]}"


def quotient_class_members(dsu: DSU, n: int) -> dict[Pair, list[Pair]]:
    """Return all unordered pair members of each quotient class."""

    groups: dict[Pair, list[Pair]] = defaultdict(list)
    for left in range(n):
        for right in range(left + 1, n):
            item = (left, right)
            groups[dsu.find(item)].append(item)
    return {root: sorted(members) for root, members in sorted(groups.items())}


def expected_reduction_vector(
    *,
    selected_class: Pair,
    nonselected_class: Pair,
    orientation: str,
) -> dict[str, int]:
    """Return the expected two-term quotient vector for the square row."""

    if orientation == "A":
        return {class_key(selected_class): 1, class_key(nonselected_class): -1}
    if orientation == "B":
        return {class_key(selected_class): -1, class_key(nonselected_class): 1}
    raise ValueError(f"unexpected orientation: {orientation}")


def pair_as_list(left: int, right: int) -> list[int]:
    """Return one canonical unordered pair as a JSON list."""

    return list(pair(left, right))


def square_record(
    *,
    i: int,
    residual: int,
    s: int,
    j: int,
    orientation: str,
    selected_class: Pair,
    nonselected_class: Pair,
    dsu: DSU,
) -> dict[str, Any]:
    """Return a compact auditable selected-center square record."""

    if orientation == "A":
        positive = [pair(i, s), pair(j, residual)]
        negative = [pair(i, residual), pair(j, s)]
        reduction = "R_i > X_i_n"
    elif orientation == "B":
        positive = [pair(i, residual), pair(j, s)]
        negative = [pair(i, s), pair(j, residual)]
        reduction = "X_i_n > R_i"
    else:
        raise ValueError(f"unexpected orientation: {orientation}")
    quotient = quotient_vector(
        positive=positive,
        negative=negative,
        dsu=dsu,
    )
    cancelling_class = dsu.find(pair(j, residual))
    if cancelling_class != dsu.find(pair(j, s)):
        raise AssertionError("selected-center square does not cancel in its center row")
    expected_vector = expected_reduction_vector(
        selected_class=selected_class,
        nonselected_class=nonselected_class,
        orientation=orientation,
    )
    if quotient != expected_vector:
        raise AssertionError(
            f"unexpected quotient vector for orientation {orientation}: {quotient}"
        )
    return {
        "center": j,
        "cancelling_class_key": class_key(cancelling_class),
        "forced_orientation": orientation,
        "literal_square_lift": True,
        "nonselected_class_key": class_key(nonselected_class),
        "positive_pairs": [list(item) for item in positive],
        "negative_pairs": [list(item) for item in negative],
        "quotient_vector": quotient,
        "reduction": reduction,
        "selected_class_key": class_key(selected_class),
        "selected_witness": s,
    }


def t10_assignment_ids(strict_cycle_packet: dict[str, Any]) -> list[str]:
    """Return the T10 assignment ids from the strict-cycle packet."""

    for template in strict_cycle_packet.get("templates", []):
        if template.get("template_id") == "T10":
            return [str(item) for item in template["assignment_ids"]]
    raise ValueError("T10 template not found")


def assignment_records(
    *,
    classification: dict[str, Any],
    strict_cycle_packet: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return paired-square audit records for the T10 assignment ids."""

    n = int(classification["n"]) if "n" in classification else 9
    position = {label: index for index, label in enumerate(range(n))}
    wanted = set(t10_assignment_ids(strict_cycle_packet))
    assignments = [
        assignment
        for assignment in classification["assignments"]
        if assignment.get("assignment_id") in wanted
    ]
    if len(assignments) != len(wanted):
        found = {str(assignment.get("assignment_id")) for assignment in assignments}
        missing = sorted(wanted - found)
        raise ValueError(f"missing T10 assignments in classification: {missing}")

    records: list[dict[str, Any]] = []
    for assignment in sorted(assignments, key=lambda item: str(item["assignment_id"])):
        rows = selected_rows_by_center(assignment["selected_rows"])
        dsu = quotient_for_rows(rows, n)
        members = quotient_class_members(dsu, n)
        hits: list[dict[str, Any]] = []
        for i in sorted(rows):
            witnesses = rows[i]
            ri_class = dsu.find(pair(i, min(witnesses)))
            for residual in range(n):
                if residual == i or residual in witnesses:
                    continue
                x_class = dsu.find(pair(i, residual))
                if x_class == ri_class:
                    continue
                x_members = members[x_class]
                if x_members != [pair(i, residual)]:
                    continue
                squares: list[dict[str, Any]] = []
                for selected_witness in sorted(witnesses):
                    for j in sorted(rows):
                        if j in {i, residual, selected_witness}:
                            continue
                        row_j = rows[j]
                        if residual not in row_j or selected_witness not in row_j:
                            continue
                        orientation = square_orientation(
                            i=i,
                            n=residual,
                            s=selected_witness,
                            j=j,
                            position=position,
                        )
                        if orientation in {"A", "B"}:
                            squares.append(
                                square_record(
                                    i=i,
                                    residual=residual,
                                    s=selected_witness,
                                    j=j,
                                    orientation=orientation,
                                    selected_class=ri_class,
                                    nonselected_class=x_class,
                                    dsu=dsu,
                                )
                            )
                a_squares = [
                    square for square in squares if square["forced_orientation"] == "A"
                ]
                b_squares = [
                    square for square in squares if square["forced_orientation"] == "B"
                ]
                if a_squares and b_squares:
                    hits.append(
                        {
                            "residual_pair": [i, residual],
                            "selected_class_label": f"R_{i}",
                            "selected_class_key": class_key(ri_class),
                            "selected_class_size": len(members[ri_class]),
                            "nonselected_class_label": f"X_{i}_{residual}",
                            "nonselected_class_key": class_key(x_class),
                            "nonselected_class_members": [
                                list(item) for item in x_members
                            ],
                            "nonselected_class_is_singleton": True,
                            "a_square": a_squares[0],
                            "b_square": b_squares[0],
                            "available_a_square_count": len(a_squares),
                            "available_b_square_count": len(b_squares),
                        }
                    )
        records.append(
            {
                "assignment_id": str(assignment["assignment_id"]),
                "family_id": str(assignment["family_id"]),
                "template_id": str(assignment["template_id"]),
                "hit_count": len(hits),
                "paired_square_entry": hits[0] if hits else None,
                "status": "paired_square_entry_found" if hits else "no_paired_square_entry",
            }
        )
    return records


def payload(
    *,
    classification: dict[str, Any],
    strict_cycle_packet: dict[str, Any],
) -> dict[str, Any]:
    """Build the audit payload."""

    records = assignment_records(
        classification=classification,
        strict_cycle_packet=strict_cycle_packet,
    )
    hit_assignment_count = sum(
        1 for record in records if record["status"] == "paired_square_entry_found"
    )
    total_hit_count = sum(int(record["hit_count"]) for record in records)
    records_digest = digest_json(records)
    return {
        "assignment_count": len(records),
        "claim_scope": CLAIM_SCOPE,
        "cyclic_order": list(range(9)),
        "hit_assignment_count": hit_assignment_count,
        "interpretation": [
            "Each record audits one T10/F12 strict-cycle assignment.",
            "Each record stores one representative incident residual pair whose nonselected class is the literal singleton pair.",
            "The per-record hit_count and top-level total_hit_count count all surviving entries, not just the stored representatives.",
            "The two selected-center squares have opposite Kalmanson diagonal orientations.",
            "The stored quotient vectors are checked against actual selected and nonselected class keys.",
            "The selected class may coincide across centers; center-uniqueness is not used by the cancellation.",
            "This is a paired-square entry audit only; it is not an n=9 proof.",
        ],
        "miss_assignment_count": len(records) - hit_assignment_count,
        "n": 9,
        "provenance": {
            "command": "python scripts/check_n9_t10_paired_square_entry.py --assert-expected --write",
            "generator": "scripts/check_n9_t10_paired_square_entry.py",
        },
        "records": records,
        "records_digest": records_digest,
        "row_size": 4,
        "schema": SCHEMA,
        "source_artifacts": [
            {
                "path": "data/certificates/n9_vertex_circle_frontier_motif_classification.json",
                "role": "full selected rows for the 184 n=9 frontier assignments",
                "trust": "REVIEW_PENDING_DIAGNOSTIC",
            },
            {
                "path": "data/certificates/n9_vertex_circle_strict_cycle_template_packet.json",
                "role": "T10/F12 assignment ids and strict-cycle template metadata",
                "trust": "REVIEW_PENDING_DIAGNOSTIC",
            },
        ],
        "status": STATUS,
        "template_id": "T10",
        "total_hit_count": total_hit_count,
        "trust": TRUST,
    }


def validate_payload(object_payload: dict[str, Any], *, recompute: bool = True) -> list[str]:
    """Validate a paired-square entry audit payload."""

    errors: list[str] = []
    expected = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "row_size": 4,
        "template_id": "T10",
        "assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "hit_assignment_count": EXPECTED_HIT_ASSIGNMENT_COUNT,
        "miss_assignment_count": EXPECTED_MISS_ASSIGNMENT_COUNT,
        "total_hit_count": EXPECTED_HIT_COUNT,
    }
    for key, value in expected.items():
        if object_payload.get(key) != value:
            errors.append(f"{key} mismatch: expected {value!r}, got {object_payload.get(key)!r}")

    cyclic_order = object_payload.get("cyclic_order")
    if (
        not isinstance(cyclic_order, list)
        or len(cyclic_order) != 9
        or set(cyclic_order) != set(range(9))
    ):
        errors.append("cyclic_order must be the natural order on 0..8")
        position: dict[int, int] | None = None
    else:
        position = {int(label): index for index, label in enumerate(cyclic_order)}

    records = object_payload.get("records")
    if not isinstance(records, list):
        errors.append("records must be a list")
    else:
        if len(records) != object_payload.get("assignment_count"):
            errors.append("records length does not match assignment_count")
        for record in records:
            if not isinstance(record, dict):
                errors.append("records entries must be objects")
                continue
            if record.get("template_id") != "T10":
                errors.append(f"{record.get('assignment_id')} template_id is not T10")
            if record.get("status") != "paired_square_entry_found":
                errors.append(f"{record.get('assignment_id')} has no paired-square entry")
            entry = record.get("paired_square_entry")
            if not isinstance(entry, dict):
                errors.append(f"{record.get('assignment_id')} paired_square_entry must be object")
                continue
            a_square = entry.get("a_square")
            b_square = entry.get("b_square")
            if entry.get("nonselected_class_is_singleton") is not True:
                errors.append(
                    f"{record.get('assignment_id')} nonselected class is not singleton"
                )
            nonselected_members = entry.get("nonselected_class_members")
            if not isinstance(nonselected_members, list) or nonselected_members != [
                entry.get("residual_pair")
            ]:
                errors.append(
                    f"{record.get('assignment_id')} nonselected class members invalid"
                )
            selected_key = entry.get("selected_class_key")
            nonselected_key = entry.get("nonselected_class_key")
            expected_a_vector = {selected_key: 1, nonselected_key: -1}
            expected_b_vector = {selected_key: -1, nonselected_key: 1}
            residual_pair = entry.get("residual_pair")
            expected_a_pairs: tuple[list[list[int]], list[list[int]]] | None = None
            expected_b_pairs: tuple[list[list[int]], list[list[int]]] | None = None
            a_orientation: str | None = None
            b_orientation: str | None = None
            if isinstance(residual_pair, list) and len(residual_pair) == 2:
                try:
                    i = int(residual_pair[0])
                    residual = int(residual_pair[1])
                    if isinstance(a_square, dict):
                        a_center = int(a_square["center"])
                        a_witness = int(a_square["selected_witness"])
                        if position is not None:
                            a_orientation = square_orientation(
                                i=i,
                                n=residual,
                                s=a_witness,
                                j=a_center,
                                position=position,
                            )
                        expected_a_pairs = (
                            [
                                pair_as_list(i, a_witness),
                                pair_as_list(a_center, residual),
                            ],
                            [
                                pair_as_list(i, residual),
                                pair_as_list(a_center, a_witness),
                            ],
                        )
                    if isinstance(b_square, dict):
                        b_center = int(b_square["center"])
                        b_witness = int(b_square["selected_witness"])
                        if position is not None:
                            b_orientation = square_orientation(
                                i=i,
                                n=residual,
                                s=b_witness,
                                j=b_center,
                                position=position,
                            )
                        expected_b_pairs = (
                            [
                                pair_as_list(i, residual),
                                pair_as_list(b_center, b_witness),
                            ],
                            [
                                pair_as_list(i, b_witness),
                                pair_as_list(b_center, residual),
                            ],
                        )
                except (KeyError, TypeError, ValueError):
                    errors.append(f"{record.get('assignment_id')} invalid square labels")
            else:
                errors.append(f"{record.get('assignment_id')} residual_pair invalid")
            if (
                not isinstance(a_square, dict)
                or a_square.get("reduction") != "R_i > X_i_n"
                or a_square.get("forced_orientation") != "A"
                or a_square.get("literal_square_lift") is not True
                or a_square.get("selected_class_key") != selected_key
                or a_square.get("nonselected_class_key") != nonselected_key
                or not isinstance(a_square.get("cancelling_class_key"), str)
                or a_square.get("quotient_vector") != expected_a_vector
                or a_orientation != "A"
                or expected_a_pairs is None
                or a_square.get("positive_pairs") != expected_a_pairs[0]
                or a_square.get("negative_pairs") != expected_a_pairs[1]
            ):
                errors.append(f"{record.get('assignment_id')} invalid A-square reduction")
            if (
                not isinstance(b_square, dict)
                or b_square.get("reduction") != "X_i_n > R_i"
                or b_square.get("forced_orientation") != "B"
                or b_square.get("literal_square_lift") is not True
                or b_square.get("selected_class_key") != selected_key
                or b_square.get("nonselected_class_key") != nonselected_key
                or not isinstance(b_square.get("cancelling_class_key"), str)
                or b_square.get("quotient_vector") != expected_b_vector
                or b_orientation != "B"
                or expected_b_pairs is None
                or b_square.get("positive_pairs") != expected_b_pairs[0]
                or b_square.get("negative_pairs") != expected_b_pairs[1]
            ):
                errors.append(f"{record.get('assignment_id')} invalid B-square reduction")
        if object_payload.get("records_digest") != digest_json(records):
            errors.append("records_digest mismatch")

    if recompute:
        try:
            expected_payload = payload(
                classification=load_json(DEFAULT_CLASSIFICATION),
                strict_cycle_packet=load_json(DEFAULT_STRICT_CYCLE_PACKET),
            )
        except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
            errors.append(f"recompute failed: {exc}")
        else:
            if object_payload != expected_payload:
                errors.append("payload does not match recomputed audit")
    return errors


def summary(object_payload: dict[str, Any]) -> dict[str, Any]:
    """Return a compact machine-readable summary."""

    return {
        "assignment_count": object_payload.get("assignment_count"),
        "hit_assignment_count": object_payload.get("hit_assignment_count"),
        "miss_assignment_count": object_payload.get("miss_assignment_count"),
        "records_digest": object_payload.get("records_digest"),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "template_id": object_payload.get("template_id"),
        "total_hit_count": object_payload.get("total_hit_count"),
        "trust": object_payload.get("trust"),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classification", type=Path, default=DEFAULT_CLASSIFICATION)
    parser.add_argument("--strict-cycle-packet", type=Path, default=DEFAULT_STRICT_CYCLE_PACKET)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_summary")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point."""

    args = parse_args(argv)
    classification_path = args.classification if args.classification.is_absolute() else ROOT / args.classification
    strict_cycle_path = (
        args.strict_cycle_packet
        if args.strict_cycle_packet.is_absolute()
        else ROOT / args.strict_cycle_packet
    )
    artifact_path = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact

    if args.check:
        object_payload = load_json(artifact_path)
    else:
        object_payload = payload(
            classification=load_json(classification_path),
            strict_cycle_packet=load_json(strict_cycle_path),
        )

    errors = validate_payload(object_payload, recompute=args.check)
    if args.assert_expected and errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    if args.write:
        write_json(object_payload, artifact_path)

    if args.json_summary:
        print(json.dumps(summary(object_payload), indent=2, sort_keys=True))
    else:
        result = summary(object_payload)
        print(
            "T10 paired-square entry audit: "
            f"{result['hit_assignment_count']}/{result['assignment_count']} assignments hit; "
            f"digest {result['records_digest']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
