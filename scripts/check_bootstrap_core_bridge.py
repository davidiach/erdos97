#!/usr/bin/env python3
"""Check bootstrap-core bridge bookkeeping packets."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from erdos97.bootstrap_cores import (
    audit_bootstrap_core,
    cyclic_capacity_from_runs,
    cyclic_capacity_sum,
    outside_runs,
    search_generating_seed,
)
from erdos97.bridge_negative_controls import c13_sidon_rows
from erdos97.adaptive_blockers import (
    singleton_rich_classes_from_pattern,
)

def complete_five_packet() -> dict[str, object]:
    rich_classes = tuple(
        (tuple(label for label in range(5) if label != center),)
        for center in range(5)
    )
    rank = search_generating_seed(rich_classes, limit=3)
    assert rank.generating_closure is not None
    return {
        "name": "complete_five_rich_classes",
        "interpretation": "positive closure-rank sanity check",
        "rank_search": asdict(rank),
    }


def c13_bootstrap_packet() -> dict[str, object]:
    rich_classes = singleton_rich_classes_from_pattern(c13_sidon_rows())
    rank = search_generating_seed(rich_classes, limit=3)
    core = [0, 1, 2, 3]
    audit = audit_bootstrap_core(core, rich_classes)
    return {
        "name": "C13_sidon_singleton_rich_classes",
        "interpretation": (
            "fixed-row incidence benchmark only; C13 is already killed across "
            "all cyclic orders by the repo's Kalmanson/Farkas checker"
        ),
        "rank_search_limit_3": asdict(rank),
        "core_audit": asdict(audit),
    }


def capacity_formula_packet() -> dict[str, object]:
    n = 6
    core = [0, 2, 4]
    runs = outside_runs(core, n)
    return {
        "name": "cyclic_capacity_formula_smoke",
        "n": n,
        "core": core,
        "outside_runs": runs,
        "cyclic_capacity_sum": cyclic_capacity_sum(core, n),
        "run_formula_capacity": cyclic_capacity_from_runs(runs),
    }


def all_packets() -> dict[str, object]:
    return {
        "type": "bootstrap_core_bridge_checks_v1",
        "status": "BRIDGE_BOOKKEEPING_ONLY",
        "packets": {
            "complete_five": complete_five_packet(),
            "c13_sidon_bootstrap": c13_bootstrap_packet(),
            "capacity_formula": capacity_formula_packet(),
        },
        "interpretation": (
            "These packets check rich-triple closure, bootstrap-core deletion "
            "closures, private halos, and weighted cyclic capacity. They do "
            "not claim a proof or counterexample."
        ),
    }


def assert_expected(payload: dict[str, object]) -> None:
    packets = payload["packets"]
    if not isinstance(packets, dict):
        raise AssertionError("packets must be a dict")

    complete = packets["complete_five"]
    if not isinstance(complete, dict):
        raise AssertionError("complete_five packet must be a dict")
    complete_rank = complete["rank_search"]
    if not isinstance(complete_rank, dict):
        raise AssertionError("complete_five rank search must be a dict")
    if not complete_rank["rank_leq_limit"]:
        raise AssertionError("complete five should have rank <= 3")
    if complete_rank["generating_seed"] != [0, 1, 2]:
        raise AssertionError("complete five should first generate from [0,1,2]")

    c13 = packets["c13_sidon_bootstrap"]
    if not isinstance(c13, dict):
        raise AssertionError("C13 packet must be a dict")
    c13_rank = c13["rank_search_limit_3"]
    if not isinstance(c13_rank, dict):
        raise AssertionError("C13 rank search must be a dict")
    if c13_rank["rank_leq_limit"]:
        raise AssertionError("C13 fixed-row singleton family should have rho > 3")
    if c13_rank["checked_seed_count"] != 377:
        raise AssertionError("C13 should check all 1-, 2-, and 3-seeds")

    c13_audit = c13["core_audit"]
    if not isinstance(c13_audit, dict):
        raise AssertionError("C13 audit must be a dict")
    if not c13_audit["core_generates_all"]:
        raise AssertionError("C13 core should generate all labels")
    if not c13_audit["inclusion_minimal"]:
        raise AssertionError("C13 core should be inclusion-minimal")
    if not c13_audit["private_halo_requirement_ok"]:
        raise AssertionError("C13 core should satisfy private-halo requirements")
    if c13_audit["private_pair_lower_bound"] != 4:
        raise AssertionError("C13 lower bound should count one pair per core row")
    if c13_audit["private_pair_count"] != 6:
        raise AssertionError("C13 actual private-pair count should be 6")
    if c13_audit["cyclic_capacity_sum"] != 36:
        raise AssertionError("C13 cyclic capacity should be 36 in natural order")
    if not c13_audit["weighted_capacity_ok"]:
        raise AssertionError("C13 weighted capacity ledger should pass")

    formula = packets["capacity_formula"]
    if not isinstance(formula, dict):
        raise AssertionError("capacity formula packet must be a dict")
    if formula["cyclic_capacity_sum"] != formula["run_formula_capacity"]:
        raise AssertionError("cyclic capacity and run formula should match")
    if formula["cyclic_capacity_sum"] != 6:
        raise AssertionError("interleaved three-outside capacity should be 6")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--write-certificate", help="write JSON to this path")
    args = parser.parse_args()

    payload = all_packets()
    if args.assert_expected:
        assert_expected(payload)

    if args.write_certificate:
        path = Path(args.write_certificate)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        packets = payload["packets"]
        assert isinstance(packets, dict)
        c13 = packets["c13_sidon_bootstrap"]
        assert isinstance(c13, dict)
        c13_audit = c13["core_audit"]
        assert isinstance(c13_audit, dict)
        print("bootstrap-core bridge checks")
        print("complete_five: rank <= 3")
        print(
            "C13_sidon: rho > 3, core [0,1,2,3], "
            f"private_pairs={c13_audit['private_pair_count']}, "
            f"capacity={c13_audit['cyclic_capacity_sum']}"
        )
        if args.assert_expected:
            print("OK: bootstrap-core bridge expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
