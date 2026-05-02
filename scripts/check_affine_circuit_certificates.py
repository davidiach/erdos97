#!/usr/bin/env python3
"""Check Prompt 2 affine-circuit quotient and certificate reductions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.affine_circuit_certificates import (  # noqa: E402
    affine_circuit_matrix,
    analysis_to_json,
    golden_decagon_example,
    lifted_matrix,
    minimal_cofactor_certificates,
    pair_gain_components,
    quotient_matrix,
    quotient_reduction,
    single_circle_row_example,
    two_core_matrix,
    valid_lifted_bases,
    weighted_two_core,
)


EXAMPLES = {
    "golden-decagon": golden_decagon_example,
    "single-circle-row": single_circle_row_example,
}


def parse_base(raw: str) -> list[int]:
    try:
        base = [int(item.strip()) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid comma-separated base: {raw}") from exc
    if len(base) != 4:
        raise argparse.ArgumentTypeError("base must contain exactly four labels")
    return base


def analyze(args: argparse.Namespace) -> dict[str, object]:
    points, cohorts = EXAMPLES[args.example]()
    L = affine_circuit_matrix(points, cohorts)
    Z = lifted_matrix(points)
    bases = valid_lifted_bases(points)
    if not bases:
        raise SystemExit(f"{args.example}: no nonsingular lifted base")
    base = args.base if args.base is not None else bases[0]

    quotient = quotient_reduction(L, Z, base)
    LN, quotient_columns = quotient_matrix(L, base)
    core = weighted_two_core(LN, quotient_columns)
    A_core = two_core_matrix(LN, core)
    certs = minimal_cofactor_certificates(
        A_core,
        core.core_columns,
        max_support_size=args.max_support_size,
        stop_after=args.stop_after,
    )
    pair_components = pair_gain_components(A_core, core.core_columns)

    return analysis_to_json(
        example=args.example,
        base=base,
        L=L,
        Z=Z,
        quotient=quotient,
        core=core,
        certificates=certs,
        pair_components=pair_components,
    )


def assert_expected(row: dict[str, object]) -> None:
    if not row["lz_zero"]:
        raise AssertionError(f"{row['example']}: expected LZ=0")
    if row["rank_z"] != 4:
        raise AssertionError(f"{row['example']}: expected rank_z=4")
    if row["kernel_dim_l"] != 4 + row["kernel_dim_quotient"]:
        raise AssertionError(f"{row['example']}: quotient dimension mismatch")

    if row["example"] == "single-circle-row":
        core = row["two_core"]  # type: ignore[assignment]
        if core["core_columns"] != [5]:  # type: ignore[index]
            raise AssertionError("single-circle-row should leave isolated quotient column 5")
        if not row["certificates"]:
            raise AssertionError("single-circle-row should emit isolated-column certificate")


def print_summary(row: dict[str, object]) -> None:
    core = row["two_core"]  # type: ignore[assignment]
    print("example  n  rankZ  LZ=0  kerL  kerQ  core cols  certs  pair comps")
    print(
        f"{row['example']}  {row['n']}  {row['rank_z']}  {row['lz_zero']}  "
        f"{row['kernel_dim_l']}  {row['kernel_dim_quotient']}  "
        f"{core['core_columns']}  {len(row['certificates'])}  "
        f"{len(row['pair_gain_components'])}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example", choices=sorted(EXAMPLES), default="golden-decagon")
    parser.add_argument("--base", type=parse_base, help="comma-separated lifted base")
    parser.add_argument("--json", action="store_true", help="print JSON instead of summary")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--max-support-size", type=int, default=8)
    parser.add_argument("--stop-after", type=int, default=16)
    args = parser.parse_args()

    row = analyze(args)
    if args.assert_expected:
        assert_expected(row)

    if args.json:
        print(json.dumps(row, indent=2, sort_keys=True))
    else:
        print_summary(row)
        if args.assert_expected:
            print("OK: affine-circuit expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
