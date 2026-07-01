# n <= 8 Review Summary

One-page external-review summary for the repo-local selected-witness n <= 8 finite-case artifact.

## Purpose

This packet is ready for an external reviewer to inspect the repo-local
selected-witness n <= 8 result for Erdos Problem #97. The global problem
remains open; the request is only to review the small finite-case
artifact and the short human-readable proof trail.

## What To Review

1. The selected-witness incidence route: n <= 7 by counting/crossing,
n=8 by 15 canonical survivor classes and exact obstruction.

2. The focused delicate certificates: classes 3, 4, 5, and 14, with
class 14 the main Groebner plus strict-convexity branch audit.

3. The independent replays: SymPy-free partial recheck and z3 NRA
all-class cross-check.

## Minimal Commands

```bash
python scripts/independent_check_n8_artifacts.py --check --json
python scripts/enumerate_n8_incidence.py --summary
python scripts/analyze_n8_exact_survivors.py --check --json
python scripts/check_n8_class14_certificate.py --check --json
```

## Safe Review Outcomes

Accepted: the repo-local n <= 8 selected-witness finite-case artifact is
suitable for paper-style citation with the stated scope.

Gap found: record the exact failed lemma, checker, certificate, or
convention; do not change global status without a separate
source-of-truth update.
