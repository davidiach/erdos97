#!/usr/bin/env python3
"""Regenerate the exact n=9 equilateral-hinge forcing artifact.

The checker searches labelled four-witness rows in a fixed cyclic order.  It
uses no stored frontier as search input and no symmetry quotient.  Its scope is
one review-pending finite implication; it neither proves Erdos Problem #97 nor
completes independent review of the repository's n=9 reduction.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import hashlib
from itertools import combinations
import json
from pathlib import Path
from typing import Any

from erdos97.n9_hinge_forcing import (
    EXPECTED_HINGE_COMPILER_REQUIREMENTS,
    EXPECTED_HINGE_COMPILER_SATISFACTION_ENTRIES,
    EXPECTED_HINGE_COMPILER_SHA256,
    Axiom,
    AxiomConfig,
    Rows,
    SearchResult,
    assert_expected_baseline,
    audit_compiled_hinge_semantics,
    baseline_result,
    chords_cross,
    hinge_instances,
    search,
    theorem_config,
    validate_terminal,
)

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n9_hinge_forcing.json"

SCHEMA = "erdos97.n9_hinge_forcing.v1"
STATUS = "REVIEW_PENDING_N9_EQUILATERAL_HINGE_FORCING"
TRUST = "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING"
CLAIM_SCOPE = (
    "Exact labelled n=9 finite search showing that self-excluding selected "
    "four-witness rows satisfying the row-intersection cap and two-overlap "
    "proper-crossing rule contain a Kalmanson equilateral hinge; "
    "review-pending audit evidence only, not a proof of n=9 or Erdos Problem "
    "#97 and not completed independent review."
)
PROVENANCE = {
    "generator": "scripts/check_n9_hinge_forcing.py",
    "command": (
        "python scripts/check_n9_hinge_forcing.py "
        "--write --assert-expected"
    ),
}

THEOREM_ASSUMPTIONS = (
    Axiom.ROW_INTERSECTION_CAP_2,
    Axiom.TWO_OVERLAP_CHORD_CROSSING,
)
HINGE_FREE = Axiom.KALMANSON_EQUILATERAL_HINGE_FREE

# Filled from a complete deterministic replay.  These pin traversal behavior
# as well as the mathematical terminal counts, making accidental brancher
# changes visible during review.
EXPECTED = {
    "baseline_sha256": (
        "3cc536f266fc0c6f563881a63aafdc80a731d1031091054d737334744dcf5b20"
    ),
    "baseline_nodes": 26_746,
    "explicit_frontier_sha256": (
        "5dfe8f667c5ab22c99b8f20eba08a8ba3d037d79d5f30b8bf2738f6ebf6e9fe9"
    ),
    "derived_frontier_sha256": (
        "94737399b7b657a6c97bf76481c43050a5a8f20a9f3bfcfca09cd45bc129fd9a"
    ),
    "frontier_assignment_sha256": (
        "dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55"
    ),
    "frontier_terminals": 184,
    "drop_witness_sha256": {
        Axiom.ROW_INTERSECTION_CAP_2.value: (
            "bf9d97b24acb4a6a51ea1912dd3badb3210cca7be5859b68270afdf1e5fa060d"
        ),
        Axiom.TWO_OVERLAP_CHORD_CROSSING.value: (
            "a67a47c0450d3c298ab71a5fe3502ea82dea81f7dd4c5f00d5a3156bfc833bfc"
        ),
    },
}

# Small exact negative controls found independently of the production DFS.
# They are inputs to validation only: each is checked against every retained
# constraint and must fail when its omitted assumption is restored.
DROP_WITNESSES: dict[Axiom, Rows] = {
    Axiom.ROW_INTERSECTION_CAP_2: (
        (1, 2, 4, 6),
        (2, 3, 5, 7),
        (0, 3, 5, 7),
        (1, 2, 4, 8),
        (2, 3, 5, 6),
        (0, 3, 7, 8),
        (0, 5, 7, 8),
        (1, 4, 6, 8),
        (0, 1, 4, 6),
    ),
    Axiom.TWO_OVERLAP_CHORD_CROSSING: (
        (2, 4, 5, 7),
        (0, 2, 5, 8),
        (3, 4, 7, 8),
        (2, 4, 6, 8),
        (1, 3, 5, 7),
        (1, 6, 7, 8),
        (0, 1, 3, 4),
        (0, 1, 2, 6),
        (0, 3, 5, 6),
    ),
}

NOT_CLAIMED = [
    "general proof of Erdos Problem #97",
    "counterexample to Erdos Problem #97",
    "n=9 is proved",
    "n=9 external review complete",
    "bridge from arbitrary larger counterexamples to n=9",
    "official/global status update",
]


def canonical_json(value: object) -> bytes:
    """Return stable compact JSON bytes."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write one deterministic human-readable JSON object."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _result_payload(result: SearchResult) -> dict[str, object]:
    """Return one result with its canonical payload digest."""
    return {"result_sha256": result.sha256, **result.to_dict()}


def _require_unsat_complete(name: str, result: SearchResult) -> None:
    if result.satisfiable or not result.search_complete:
        raise AssertionError(f"{name} must be a complete UNSAT search")


def _reenable(config: AxiomConfig, axiom: Axiom) -> AxiomConfig:
    return replace(config, **{axiom.value: True})


def _witness_diagnostics(witness: Rows) -> dict[str, object]:
    """Return direct, brancher-independent checks for one negative control."""
    overlaps: Counter[int] = Counter()
    crossing_violations = 0
    for first, second in combinations(range(9), 2):
        shared = sorted(set(witness[first]) & set(witness[second]))
        overlaps[len(shared)] += 1
        if len(shared) == 2 and not chords_cross(
            (first, second), (shared[0], shared[1])
        ):
            crossing_violations += 1

    pair_counts: Counter[tuple[int, int]] = Counter()
    for row in witness:
        pair_counts.update(combinations(row, 2))
    indegrees = [sum(label in row for row in witness) for label in range(9)]
    return {
        "indegrees": indegrees,
        "row_intersection_size_histogram": {
            str(size): count for size, count in sorted(overlaps.items())
        },
        "maximum_row_intersection": max(overlaps),
        "two_overlap_crossing_violations": crossing_violations,
        "maximum_witness_pair_multiplicity": max(pair_counts.values()),
        "hinge_instance_count": hinge_instances(witness),
    }


def _drop_witness_payload(axiom: Axiom, witness: Rows) -> dict[str, object]:
    """Validate that one SAT witness violates exactly the restored obligation."""
    config = theorem_config().drop(axiom)
    validate_terminal(witness, config)
    witness_sha256 = hashlib.sha256(canonical_json(witness)).hexdigest()
    try:
        validate_terminal(witness, _reenable(config, axiom))
    except ValueError as exc:
        restored_rejection = str(exc)
    else:
        raise AssertionError(
            f"witness for dropping {axiom.value} also satisfies that axiom"
        )
    return {
        "dropped_assumption": axiom.value,
        "kept_constraints_validated": True,
        "restored_assumption_rejected": True,
        "restored_rejection": restored_rejection,
        "witness_sha256": witness_sha256,
        "diagnostics": _witness_diagnostics(witness),
        "witness": [list(row) for row in witness],
    }


def build_payload() -> dict[str, Any]:
    """Run the direct complement checker and all finite sensitivity audits."""
    compiler_audit = audit_compiled_hinge_semantics()
    if compiler_audit.requirement_count != EXPECTED_HINGE_COMPILER_REQUIREMENTS:
        raise AssertionError("unexpected compiled hinge requirement count")
    if (
        compiler_audit.satisfaction_table_entry_count
        != EXPECTED_HINGE_COMPILER_SATISFACTION_ENTRIES
    ):
        raise AssertionError("unexpected compiled hinge satisfaction-table size")
    if compiler_audit.compiler_sha256 != EXPECTED_HINGE_COMPILER_SHA256:
        raise AssertionError("compiled hinge semantics digest changed")

    base = baseline_result()
    assert_expected_baseline(base)
    _require_unsat_complete("hinge-free theorem complement", base)
    if base.config != theorem_config():
        raise AssertionError("baseline_result must use theorem_config")

    # Dropping hinge-free enumerates the full incidence frontier.  Running it
    # once without either derived filter and once with both explicit filters
    # gives a finite cross-check of the elementary derivations below.
    derived_frontier_config = theorem_config().drop(HINGE_FREE)
    derived_frontier = search(derived_frontier_config)
    explicit_frontier = search(AxiomConfig(kalmanson_equilateral_hinge_free=False))
    if not derived_frontier.search_complete or not explicit_frontier.search_complete:
        raise AssertionError("frontier comparison searches must be complete")
    if derived_frontier.stats.terminal_assignments != explicit_frontier.stats.terminal_assignments:
        raise AssertionError("explicit and derived-filter frontier counts disagree")
    if derived_frontier.witness is None or explicit_frontier.witness is None:
        raise AssertionError("the incidence frontier must be nonempty")
    validate_terminal(
        derived_frontier.witness,
        AxiomConfig(kalmanson_equilateral_hinge_free=False),
    )

    drops: dict[str, object] = {}
    for axiom in THEOREM_ASSUMPTIONS:
        drops[axiom.value] = _drop_witness_payload(axiom, DROP_WITNESSES[axiom])

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "domain": {
            "n": 9,
            "cyclic_order": list(range(9)),
            "one_self_excluding_selected_row_per_center": True,
            "row_size": 4,
            "row_is_selected_subset_of_one_rich_class": True,
            "selected_row_size_four_is_fixed_domain": True,
            "underlying_rich_classes_may_be_larger": True,
            "symmetry_quotient_used": False,
            "stored_frontier_used_as_search_input": False,
        },
        "finite_implication": {
            "assumptions": [axiom.value for axiom in THEOREM_ASSUMPTIONS],
            "proper_crossing_semantics": (
                "relative-interior chord intersection, equivalently alternating "
                "endpoints for four distinct cyclic labels"
            ),
            "conclusion": "at least one Kalmanson equilateral hinge",
            "complement_constraint": HINGE_FREE.value,
            "explicit_indegree_exact_4_assumed": False,
            "explicit_witness_pair_capacity_2_assumed": False,
        },
        "hinge_compiler_audit": compiler_audit.to_dict(),
        "derived_consequences": {
            "witness_pair_capacity_2": {
                "statement": "every witness pair occurs together in at most two rows",
                "proof": [
                    "Rows containing {x,y} have centers in the two open cyclic arcs cut by x and y.",
                    "The intersection cap and crossing rule require every two such centers to lie in opposite arcs.",
                    "Three centers cannot be pairwise separated by a two-part partition, so the multiplicity is at most two.",
                ],
                "explicit_filter_used_by_baseline": False,
            },
            "indegree_exact_4": {
                "statement": "every witness label has selected indegree exactly 4",
                "proof": [
                    "For fixed x, each row containing x contributes three witness pairs, so 3*d_x = sum_{y != x} m_xy.",
                    "For each hull neighbor y of x, m_xy <= 1 because all possible centers lie in the same open arc and their chord cannot properly cross the hull edge xy.",
                    "For the other six labels, the derived witness-pair capacity gives m_xy <= 2; hence 3*d_x <= 2*1 + 6*2 = 14 and d_x <= 4.",
                    "The nine four-witness rows have total indegree 36, so all nine upper bounds are equalities: d_x = 4.",
                ],
                "explicit_filter_used_by_baseline": False,
            },
            "finite_crosscheck": {
                "derived_filter_frontier": _result_payload(derived_frontier),
                "explicit_filter_frontier": _result_payload(explicit_frontier),
                "terminal_count_agreement": True,
            },
        },
        "hinge_free_complement": _result_payload(base),
        "assumption_drop_witnesses": drops,
        "positive_control": {
            "dropped_constraint": HINGE_FREE.value,
            "interpretation": (
                "Removing the negated conclusion reaches 184 terminal row systems; "
                "every terminal satisfies the derived pair-capacity and balance "
                "lemmas."
            ),
            "search": _result_payload(derived_frontier),
        },
        "interpretation_warnings": [
            "This is a finite labelled row-system implication under two necessary incidence filters.",
            "The checker does not prove that an arbitrary larger counterexample reduces to nine vertices.",
            "The n=9 geometric reduction and the Kalmanson lemma remain subject to the repository's external-review gates.",
        ],
        "not_claimed": list(NOT_CLAIMED),
        "provenance": dict(PROVENANCE),
    }


def summary_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a compact summary without full countermodel rows."""
    value = json.loads(json.dumps(payload))
    drops = value.get("assumption_drop_witnesses", {})
    if isinstance(drops, dict):
        for drop in drops.values():
            if isinstance(drop, dict):
                drop.pop("witness", None)
    for path in (
        ("derived_consequences", "finite_crosscheck", "derived_filter_frontier"),
        ("derived_consequences", "finite_crosscheck", "explicit_filter_frontier"),
        ("positive_control", "search"),
    ):
        current: object = value
        for key in path:
            if not isinstance(current, dict):
                break
            current = current.get(key)
        if isinstance(current, dict):
            current.pop("witness", None)
    return value


def assert_expected_payload(payload: dict[str, Any]) -> None:
    """Assert trust boundaries, exact counts, witnesses, and replay digests."""
    errors: list[str] = []
    for key, expected in {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "not_claimed": NOT_CLAIMED,
    }.items():
        if payload.get(key) != expected:
            errors.append(f"{key}: expected {expected!r}, got {payload.get(key)!r}")

    complement = payload.get("hinge_free_complement")
    if not isinstance(complement, dict):
        errors.append("hinge_free_complement must be an object")
        complement = {}
    stats = complement.get("stats")
    if not isinstance(stats, dict):
        errors.append("hinge_free_complement.stats must be an object")
        stats = {}
    if complement.get("satisfiable") is not False:
        errors.append("hinge-free complement must be UNSAT")
    if complement.get("search_complete") is not True:
        errors.append("hinge-free complement search must be complete")
    if stats.get("terminal_assignments") != 0:
        errors.append("hinge-free complement must have zero terminals")
    if complement.get("result_sha256") != EXPECTED["baseline_sha256"]:
        errors.append("baseline result digest changed")
    if stats.get("nodes_visited") != EXPECTED["baseline_nodes"]:
        errors.append("baseline node count changed")

    crosscheck = payload.get("derived_consequences", {}).get(
        "finite_crosscheck", {}
    )
    if not isinstance(crosscheck, dict):
        errors.append("derived-filter finite crosscheck must be an object")
        crosscheck = {}
    derived = crosscheck.get("derived_filter_frontier", {})
    explicit = crosscheck.get("explicit_filter_frontier", {})
    for name, result, expected_digest in (
        ("derived", derived, EXPECTED["derived_frontier_sha256"]),
        ("explicit", explicit, EXPECTED["explicit_frontier_sha256"]),
    ):
        if not isinstance(result, dict):
            errors.append(f"{name} frontier must be an object")
            continue
        result_stats = result.get("stats", {})
        if not isinstance(result_stats, dict):
            errors.append(f"{name} frontier stats must be an object")
            result_stats = {}
        terminals = result_stats.get("terminal_assignments")
        if terminals != EXPECTED["frontier_terminals"]:
            errors.append(f"{name} frontier terminal count changed: {terminals!r}")
        if result_stats.get("terminal_assignment_sha256") != EXPECTED[
            "frontier_assignment_sha256"
        ]:
            errors.append(f"{name} frontier assignment-set digest changed")
        if result.get("result_sha256") != expected_digest:
            errors.append(f"{name} frontier digest changed")

    drops = payload.get("assumption_drop_witnesses")
    if not isinstance(drops, dict):
        errors.append("assumption_drop_witnesses must be an object")
        drops = {}
    for axiom in THEOREM_ASSUMPTIONS:
        entry = drops.get(axiom.value)
        if not isinstance(entry, dict):
            errors.append(f"missing drop witness for {axiom.value}")
            continue
        if entry.get("witness_sha256") != EXPECTED["drop_witness_sha256"][axiom.value]:
            errors.append(f"drop witness digest changed for {axiom.value}")
        witness = entry.get("witness")
        if not isinstance(witness, list) or len(witness) != 9:
            errors.append(f"drop witness for {axiom.value} must have nine rows")
        if entry.get("kept_constraints_validated") is not True:
            errors.append(f"kept constraints not validated for {axiom.value}")
        if entry.get("restored_assumption_rejected") is not True:
            errors.append(f"restored assumption not rejected for {axiom.value}")
        diagnostics = entry.get("diagnostics")
        if not isinstance(diagnostics, dict):
            errors.append(f"missing diagnostics for {axiom.value}")
        elif diagnostics.get("hinge_instance_count") != 0:
            errors.append(f"drop witness for {axiom.value} must be hinge-free")
        elif (
            axiom is Axiom.ROW_INTERSECTION_CAP_2
            and diagnostics.get("maximum_row_intersection", 0) <= 2
        ):
            errors.append("row-cap countermodel must have an overlap above two")
        elif (
            axiom is Axiom.TWO_OVERLAP_CHORD_CROSSING
            and diagnostics.get("two_overlap_crossing_violations", 0) <= 0
        ):
            errors.append("crossing countermodel must have a crossing violation")

    compiler_audit = payload.get("hinge_compiler_audit")
    expected_compiler_audit = {
        "requirement_count": EXPECTED_HINGE_COMPILER_REQUIREMENTS,
        "public_exact_match_count": EXPECTED_HINGE_COMPILER_REQUIREMENTS,
        "satisfaction_table_entry_count": (
            EXPECTED_HINGE_COMPILER_SATISFACTION_ENTRIES
        ),
        "compiler_sha256": EXPECTED_HINGE_COMPILER_SHA256,
    }
    if compiler_audit != expected_compiler_audit:
        errors.append("hinge compiler audit changed")

    if errors:
        raise AssertionError("\n".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true")
    output.add_argument("--summary-json", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    if args.assert_expected:
        assert_expected_payload(payload)
    if args.check:
        stored = load_json(args.artifact)
        if stored != payload:
            raise AssertionError(f"{args.artifact} does not match regenerated payload")
    if args.write:
        write_json(args.artifact, payload)

    if args.summary_json:
        print(json.dumps(summary_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        base = payload["hinge_free_complement"]
        stats = base["stats"]
        print("n=9 Kalmanson equilateral-hinge forcing")
        print(f"hinge-free terminals: {stats['terminal_assignments']}")
        print(f"search nodes: {stats['nodes_visited']}")
        print(
            "incidence frontier terminals: "
            f"{EXPECTED['frontier_terminals']} (explicit and derived filters)"
        )
        print("single-assumption drops: both have validated countermodels")
        print(f"baseline result sha256: {base['result_sha256']}")
        if args.write:
            print(f"wrote {args.artifact}")
        if args.assert_expected:
            print("OK: expected hinge-forcing invariants verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
