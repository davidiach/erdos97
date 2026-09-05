#!/usr/bin/env python3
"""Discover certificates with SciPy; accept them only after integer replay.

The verifier does not import this file or SciPy. Run this generator explicitly
when changing the certificate artifact; floating-point infeasibility alone is
never saved as proof evidence.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from functools import reduce
from math import gcd, lcm
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from core import AngleModel, MetricModel, all_cases, decode_case, verify_certificate

ROOT = Path(__file__).resolve().parent


def certificate(A, E):
    d, na, ne = len(A[0]), len(A), len(E)
    for i, row in enumerate(A):
        if not any(row):
            return [[i, 1]], []
    matrix = np.hstack([np.array(A).T, np.array(E).T if E else np.empty((d, 0))])
    matrix = np.vstack([matrix, np.array([1] * na + [0] * ne)])
    result = linprog(np.zeros(na + ne), A_eq=matrix, b_eq=[0] * d + [1],
                     bounds=[(0, None)] * na + [(None, None)] * ne, method="highs")
    if not result.success:
        return None
    values = [Fraction(float(x)).limit_denominator(10**7) if abs(x) > 1e-9 else Fraction(0)
              for x in result.x]
    denominator = lcm(*(x.denominator for x in values))
    integers = [int(x * denominator) for x in values]
    divisor = reduce(gcd, (abs(x) for x in integers if x))
    integers = [x // divisor for x in integers]
    positive = [[i, x] for i, x in enumerate(integers[:na]) if x]
    equality = [[i, x] for i, x in enumerate(integers[na:]) if x]
    verify_certificate(A, E, positive, equality)
    return positive, equality


def main():
    models = [AngleModel(), MetricModel()]
    records = []
    counts = Counter()
    for case in all_cases():
        arrows, greater = decode_case(case)
        for kind, model in enumerate(models):
            A, E = model.build(arrows, greater)
            result = certificate(A, E)
            if result is not None:
                p, e = result
                records.append([*case, kind, p, e])
                counts[kind] += 1
                break
        else:
            raise RuntimeError(f"No exactly verified certificate found for {case}")
    artifact = {"schema": "erdos97.c3_common_supplier_certificates.v1",
                "encoding": "[topology,gain_code,mode,kind,strict_row_weights,equality_row_weights]",
                "records": records}
    (ROOT / "certificates.json").write_text(json.dumps(artifact, separators=(",", ":")) + "\n")
    print(json.dumps({"exact_certificates": len(records), "kinds": dict(counts),
                      "maximum_terms": max(len(r[-2]) + len(r[-1]) for r in records),
                      "maximum_weight": max(abs(t[1]) for r in records for ts in r[-2:] for t in ts)}))


if __name__ == "__main__":
    main()
