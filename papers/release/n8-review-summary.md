# n <= 8 Review Summary

One-page external-review summary for the repo-local elementary n <= 8 theorem and selected-witness corroboration.

## Purpose

This packet is ready for an external reviewer to inspect the repo-local
elementary n <= 8 theorem and selected-witness corroboration. The global
problem remains open; the request is only to review this small-case
proof and its finite-case artifact.

## What To Review

1. The elementary route: base-apex counting, octagon equality
saturation, equilateral turns, and the C8 vertex-cover contradiction.

2. The selected-witness incidence route: n <= 7 by counting/crossing,
n=8 by 15 canonical survivor classes and exact obstruction.

3. The focused delicate certificates: classes 3, 4, 5, and 14, with
class 14 the main Groebner plus strict-convexity branch audit.

4. The independent replays: SymPy-free partial recheck and z3 NRA
all-class cross-check.

## Minimal Commands

```bash
python scripts/independent_check_n8_artifacts.py --check --json
python scripts/enumerate_n8_incidence.py --summary
python scripts/analyze_n8_exact_survivors.py --check --json
python scripts/check_n8_class14_certificate.py --check --json
```

## Safe Review Outcomes

Accepted: the elementary n <= 8 theorem and/or selected-witness
corroboration are suitable for paper-style citation with stated scope.

Gap found: record the exact failed lemma, checker, certificate, or
convention; do not change global status without a separate
source-of-truth update.
