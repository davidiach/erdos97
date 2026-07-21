#!/usr/bin/env python3
"""Replay the all-k primitive Kalmanson inverse-pair exclusion.

The checker expands the two strict-row kinds and the 24 possible matchings of
four positive to four negative quotient-class occurrences.  Pair-class
equality is encoded exactly for the disjoint-star quotient of the scalable
family, leaving quantifier-free linear integer arithmetic in ``k`` and seven
ordered labels.

This excludes one- and two-inequality Kalmanson quotient certificates only.
The family has a four-inequality certificate already at ``k=8`` and is not a
Euclidean realization or a counterexample to Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import json

from erdos97.scalable_strict_cycle_control import (
    assert_expected_symbolic_inverse_classification,
    symbolic_inverse_classification,
)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-ms", type=int, default=60_000)
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = symbolic_inverse_classification(timeout_ms=args.timeout_ms)
    if args.assert_expected:
        assert_expected_symbolic_inverse_classification(summary)

    payload = {
        "status": "EXACT_ABSTRACT_ALL_K_NEGATIVE_CONTROL",
        "claim_scope": (
            "For the scalable abstract family and every k>=8, no two strict "
            "Kalmanson quotient rows are opposite positive scalar multiples. "
            "This does not exclude circuits of three or more inequalities; "
            "k=8 has an explicit four-inequality circuit."
        ),
        **summary,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        decisions = summary["decisions"]
        classes = summary["template_classification"]
        print("scalable Kalmanson primitive-inverse control")
        print(f"all k>=8: {decisions['all_k_at_least_8']}")
        print(f"96-template classification: {classes}")
        if args.assert_expected:
            print("OK: all-k decision and exception controls verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
