#!/usr/bin/env python3
"""Check whether one fixed-order certificate footprint covers all cyclic orders.

The probe takes the ordered quadrilateral footprint of a Kalmanson-style
certificate and asks Z3 whether every cyclic order contains one translated
copy, optionally in either orientation. For a circulant selected-witness
pattern, such a copy would replay the same fixed-order certificate after
relabeling.

This is only a single-footprint coverage diagnostic. SAT means the footprint
family misses at least one cyclic order. UNSAT would prove only that this
specific footprint family covers every cyclic order of the fixed abstract
pattern; it would not prove Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

try:
    from z3 import Distinct, Int, Or, Solver, sat, unsat
except ImportError as exc:  # pragma: no cover - depends on optional dev dep
    raise SystemExit("z3-solver is required for this checker") from exc

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.quotient_cone import (  # noqa: E402
    selected_rows_from_certificate,
    strict_items_from_certificate,
)

Quad = tuple[int, int, int, int]


def ordered_kalmanson_quads(cert: dict[str, object]) -> list[Quad]:
    quads: list[Quad] = []
    for item in strict_items_from_certificate(cert):
        if "quad" not in item:
            raise ValueError("footprint cover currently requires Kalmanson quad rows")
        quad = tuple(int(label) for label in item["quad"])  # type: ignore[index]
        if len(quad) != 4 or len(set(quad)) != 4:
            raise ValueError(f"bad Kalmanson quad: {quad}")
        quads.append(quad)  # type: ignore[arg-type]
    return sorted(set(quads))


def _transform_quad(quad: Quad, n: int, shift: int, reverse: bool) -> Quad:
    shifted = tuple((label + shift) % n for label in quad)
    if reverse:
        shifted = tuple(reversed(shifted))
    return shifted  # type: ignore[return-value]


def _not_in_cyclic_order(positions: Sequence[object], quad: Quad) -> object:
    return Or(
        positions[quad[0]] > positions[quad[1]],
        positions[quad[1]] > positions[quad[2]],
        positions[quad[2]] > positions[quad[3]],
    )


def _order_from_model(model: object, positions: Sequence[object], n: int) -> list[int]:
    return sorted(
        range(n),
        key=lambda label: model.evaluate(positions[label], model_completion=True).as_long(),
    )


def check_footprint_cover(
    cert: dict[str, object],
    *,
    include_reversal: bool,
    random_seed: int,
    timeout_ms: int,
) -> dict[str, object]:
    pattern = cert.get("pattern")
    if not isinstance(pattern, dict):
        raise ValueError("certificate pattern must be an object")
    if "circulant_offsets" not in pattern:
        raise ValueError("footprint translations require a circulant certificate pattern")
    pattern_name, rows = selected_rows_from_certificate(cert)
    n = len(rows)
    quads = ordered_kalmanson_quads(cert)

    positions = [Int(f"p{label}") for label in range(n)]
    solver = Solver()
    solver.set("random_seed", random_seed)
    solver.set("timeout", timeout_ms)
    solver.add(positions[0] == 0)
    solver.add(Distinct(positions))
    for position in positions:
        solver.add(position >= 0, position < n)

    orientations = (False, True) if include_reversal else (False,)
    motif_count = 0
    for shift in range(n):
        for reverse in orientations:
            motif_count += 1
            transformed = sorted(
                {_transform_quad(quad, n, shift, reverse) for quad in quads}
            )
            solver.add(Or(*[_not_in_cyclic_order(positions, quad) for quad in transformed]))

    solver_result = solver.check()
    payload: dict[str, object] = {
        "type": "quotient_cone_footprint_cover_probe_v1",
        "pattern": pattern_name,
        "n": n,
        "certificate_rows": len(strict_items_from_certificate(cert)),
        "unique_order_quads": len(quads),
        "motifs_tested": motif_count,
        "include_reversal": include_reversal,
        "rotation_quotient": "label 0 fixed at position 0",
        "solver": "z3",
        "solver_result": str(solver_result),
        "semantics": (
            "SAT means some cyclic order avoids every translated/oriented copy "
            "of this one fixed-order certificate footprint. UNSAT would be an "
            "all-order result only for this footprint family."
        ),
    }
    if solver_result == sat:
        payload["candidate_order"] = _order_from_model(solver.model(), positions, n)
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--no-reversal", action="store_true")
    parser.add_argument("--random-seed", type=int, default=17)
    parser.add_argument("--timeout-ms", type=int, default=60000)
    parser.add_argument("--assert-sat", action="store_true")
    parser.add_argument("--assert-unsat", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    cert = json.loads(args.certificate.read_text(encoding="utf-8"))
    payload = check_footprint_cover(
        cert,
        include_reversal=not args.no_reversal,
        random_seed=args.random_seed,
        timeout_ms=args.timeout_ms,
    )
    if args.assert_sat and payload["solver_result"] != str(sat):
        raise AssertionError(f"expected SAT footprint miss, got {payload['solver_result']}")
    if args.assert_unsat and payload["solver_result"] != str(unsat):
        raise AssertionError(f"expected UNSAT footprint cover, got {payload['solver_result']}")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            f"{payload['pattern']} footprint-cover {payload['solver_result']} "
            f"motifs={payload['motifs_tested']} unique_quads={payload['unique_order_quads']}"
        )
        if "candidate_order" in payload:
            print("candidate_order=" + ",".join(str(v) for v in payload["candidate_order"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
