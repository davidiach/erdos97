#!/usr/bin/env python3
"""Replay the all-k three-row Kalmanson circuit exclusion.

For the scalable abstract family, the checker classifies the only possible
primitive weights of a three-row positive dependence and decides every
weight/Kalmanson-kind case in quantifier-free Presburger arithmetic.

This excludes certificates of at most three inequalities only for this
family.  The k=8 member has an explicit four-inequality certificate, so the
result is a sharp minimal-support statement for that member, not a Euclidean
realization or a counterexample to Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.scalable_strict_cycle_control import (  # noqa: E402
    assert_expected_symbolic_three_circuit_classification,
    symbolic_three_circuit_classification,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = symbolic_three_circuit_classification(timeout_ms=args.timeout_ms)
    if args.assert_expected:
        assert_expected_symbolic_three_circuit_classification(summary)

    payload = {
        "status": "EXACT_ABSTRACT_ALL_K_NEGATIVE_CONTROL",
        "claim_scope": (
            "For the scalable abstract family and every k>=8, no positive "
            "Kalmanson quotient circuit uses three or fewer strict "
            "inequalities. The explicit k=8 four-inequality circuit is "
            "therefore support-minimal. This is family-specific and is not "
            "a Euclidean realization or a counterexample to Erdos Problem #97."
        ),
        **summary,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("scalable Kalmanson three-row control")
        print(
            "all k>=8:",
            summary["decisions"]["all_k_at_least_8"],  # type: ignore[index]
        )
        print(
            "weight/kind cases:",
            summary["symmetry_reduced_case_count"],
        )
        if args.assert_expected:
            print("OK: all-k exclusion and k=6,7 controls verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
