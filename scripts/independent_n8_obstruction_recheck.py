#!/usr/bin/env python3
"""Independent SymPy-free recheck of n=8 obstruction certificates.

This script re-verifies as much of the n=8 obstruction-certificate set
as is feasible in pure-Python rational arithmetic, with no SymPy and
no shared code path with ``scripts/analyze_n8_exact_survivors.py``.

It is a repo-local cross-check artifact pending external review.  It
does not turn the ``n <= 8`` finite-case result into a public
theorem-style claim.

Coverage:
- Cyclic-order compatible-orbit count for every class (independent
  enumeration; 11/11 expected counts confirmed).
- Cyclic-order kill for class 12.
- y_2-in-PB-span kill for classes 0, 1, 2, 6, 7, 8, 9, 10, 11, 13.
- Squared-distance / Cayley-Menger linear diagnostic for every class.
- First-stage linear identities x_3 - x_2, y_3 + y_2 (in the Q-linear
  span of the PB polynomials; auxiliary cross-reference).

Not covered (require Groebner-basis machinery):
- Class 3 duplicate-vertex full kill.
- Class 4 collinearity full kill.
- Class 5 Groebner contradiction.
- Class 14 four-branch strict-interior obstruction.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from erdos97 import n8_independent_obstruction as ind


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def survivors_path() -> Path:
    return repo_root() / "data" / "incidence" / "n8_reconstructed_15_survivors.json"


def run() -> dict:
    survivors = json.loads(survivors_path().read_text(encoding="utf-8"))
    rows_results: list[dict] = []
    independent_kills: list[int] = []
    cyclic_count_mismatches: list[dict] = []
    expected_independent_kill_failures: list[dict] = []
    for cls in survivors:
        cid = int(cls["id"])
        info = ind.verify_class(cid, cls["rows"])
        expected_count = ind.expected_cyclic_count(cid)
        if info.cyclic_order_compatible_count != expected_count:
            cyclic_count_mismatches.append(
                {
                    "class_id": cid,
                    "expected": expected_count,
                    "actual": info.cyclic_order_compatible_count,
                }
            )
        expected_attr = ind.expected_independent_kill_attribute(cid)
        if expected_attr is not None:
            attr_val = bool(getattr(info, expected_attr))
            if not attr_val:
                expected_independent_kill_failures.append(
                    {"class_id": cid, "expected_attribute": expected_attr}
                )
        if info.killed_by_some_independent_check:
            independent_kills.append(cid)
        rows_results.append(
            {
                "class_id": cid,
                "cyclic_order_compatible_count": info.cyclic_order_compatible_count,
                "cyclic_order_kill": info.cyclic_order_kill,
                "y2_in_pb_span": info.y2_in_pb_span,
                "linear_span_identities": info.linear_span_identities,
                "squared_distance_rank": info.squared_distance_rank,
                "squared_distance_free_d_count": info.squared_distance_free_d_count,
                "killed_by_some_independent_check": (
                    info.killed_by_some_independent_check
                ),
                "expected_independent_kill_attribute": expected_attr,
            }
        )

    verified = (
        not cyclic_count_mismatches
        and not expected_independent_kill_failures
        and sorted(independent_kills) == ind.CLASSES_KILLED_INDEPENDENTLY
    )
    summary = {
        "type": "n8_independent_obstruction_recheck_v1",
        "trust": "REPO_LOCAL_INDEPENDENT_CROSS_CHECK_PENDING_EXTERNAL_REVIEW",
        "claim_scope": (
            "Independent SymPy-free cross-check of the n=8 finite-case "
            "obstruction certificates.  Reverifies cyclic-order counts, "
            "the cyclic-order kill of class 12, and the y_2-in-PB-span "
            "kill of ten survivor classes.  Does not reproduce the "
            "Groebner-basis substitution chains required for classes "
            "3, 4, 5, and 14."
        ),
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "Repo-local artifact pending external review.",
        ],
        "verified": verified,
        "classes_killed_independently": sorted(independent_kills),
        "expected_classes_killed_independently": ind.CLASSES_KILLED_INDEPENDENTLY,
        "classes_requiring_groebner_machinery": ind.CLASSES_REQUIRING_GROEBNER,
        "cyclic_count_mismatches": cyclic_count_mismatches,
        "expected_independent_kill_failures": expected_independent_kill_failures,
        "per_class": rows_results,
        "checked_conditions": [
            "cyclic-order compatible-orbit counts via independent enumeration",
            "y_2 in Q-linear span of dot+bisector PB polynomials via Fraction Gauss-Jordan",
            "first-stage linear identities x_3-x_2 and y_3+y_2 in Q-linear span",
            "squared-distance Gauss-Jordan rank in d-coordinates",
        ],
        "does_not_check": [
            "class 3 duplicate-vertex Groebner substitution chain",
            "class 4 collinearity Groebner substitution chain",
            "class 5 Groebner contradiction",
            "class 14 four-branch strict-interior obstruction",
            "incidence completeness (the 15 classes themselves)",
            "general Erdos Problem #97 proof",
        ],
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the cross-check verification fails",
    )
    args = parser.parse_args()

    summary = run()
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif summary["verified"]:
        kills = summary["classes_killed_independently"]
        groebner = summary["classes_requiring_groebner_machinery"]
        print(
            f"verified independent SymPy-free recheck: "
            f"{len(kills)} of 15 classes killed independently "
            f"({kills}); "
            f"{len(groebner)} require Groebner machinery ({groebner})"
        )
    else:
        print("independent recheck reported failures:")
        for mismatch in summary["cyclic_count_mismatches"]:
            print(
                f"- class {mismatch['class_id']}: cyclic-order count "
                f"{mismatch['actual']} != expected {mismatch['expected']}"
            )
        for failure in summary["expected_independent_kill_failures"]:
            print(
                f"- class {failure['class_id']}: expected attribute "
                f"{failure['expected_attribute']} did not verify"
            )

    if args.check and not summary["verified"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
