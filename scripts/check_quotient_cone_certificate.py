#!/usr/bin/env python3
"""Check exact quotient-cone certificates.

The accepted certificate format includes either generalized ``strict_rows`` or
legacy Kalmanson ``inequalities``. Legacy Kalmanson certificates are replayed as
the zero-sum special case of the quotient-cone condition.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.quotient_cone import (  # noqa: E402
    check_quotient_cone_certificate,
    footprint_summary,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificates", nargs="+", type=Path)
    parser.add_argument("--summary-json", action="store_true")
    parser.add_argument("--footprint-json", action="store_true")
    args = parser.parse_args(argv)

    payloads: list[dict[str, object]] = []
    for path in args.certificates:
        cert = json.loads(path.read_text(encoding="utf-8"))
        if args.footprint_json:
            payload = footprint_summary(cert)
            payload["path"] = path.as_posix()
        else:
            result = check_quotient_cone_certificate(cert)
            payload = {**result.__dict__, "path": path.as_posix()}
        payloads.append(payload)

    if args.summary_json or args.footprint_json:
        output: object = payloads[0] if len(payloads) == 1 else payloads
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0

    for payload in payloads:
        print("quotient-cone certificate OK")
        print(f"path={payload['path']}")
        print(f"pattern={payload['pattern']} n={payload['n']}")
        print(f"strict rows={payload['strict_rows']}")
        print(f"distance classes={payload['distance_classes']}")
        print(f"weight sum={payload.get('weight_sum', '-')}")
        print(f"combined nonzero coefficients={payload['combined_nonzero_coefficient_count']}")
        print(f"zero sum={payload['zero_sum_verified']}")
        print(f"nonpositive sum={payload['nonpositive_sum_verified']}")
        print("claim strength: fixed selected-witness pattern plus fixed cyclic order only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
