#!/usr/bin/env python3
"""Signed-band preflight for the three-orbit quarter-cell turn-sign lemma.

Context: ``docs/quarter-cell-closure.md`` reduces the remaining
``m = 0 mod 4`` three-orbit quarter cells to the A-row witness locus.  In
that locus the cross-orbit offsets live in two boundary bands.  Writing

    T = 2*pi/m,  beta in {d, T-d},  gamma in {e, T-e},

and choosing radius signs

    P(y) = +/- sin(d),  P(z) = +/- sin(e),

splits the locus into three band-order cases and twelve signed cells:

    LL: beta=d,   gamma=e,   d < e
    LH: beta=d,   gamma=T-e, d + e < T
    HH: beta=T-d, gamma=T-e, d > e

This script records the exact first nonzero boundary term for a fixed
"killer" per-period turn determinant in each signed cell.  For
``0 < T <= pi/4`` (i.e. ``m >= 8``), every listed leading term is negative on
its open cone.  Thus every signed cell is infinitesimally on the non-convex
side of the orbit-coincidence boundary.

Important scope: this is a preflight for the missing global turn-sign proof,
not that proof.  The packet also runs a deterministic floating grid stress of
the same fixed killer turns for selected m-values, but the grid is only
evidence.  It does not close the m=8,12,16 quarter cells, does not prove an
all-m three-orbit obstruction, and does not prove Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence


SCHEMA = "erdos97.quarter_cell_signed_band_preflight.v1"
STATUS = "QUARTER_CELL_SIGNED_BAND_TURN_PREFLIGHT_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
DEFAULT_MS = (8, 12, 16, 20, 40, 100)
OPEN_QUARTER_MS = (8, 12, 16)
DEFAULT_GRID = 72


@dataclass(frozen=True)
class SignedBandCase:
    case_id: str
    band_case: str
    beta_form: str
    gamma_form: str
    cone: str
    y_sign: int
    z_sign: int
    killer_turn: int
    leading_term: str
    sign_reason: str


SIGNED_CASES: tuple[SignedBandCase, ...] = (
    SignedBandCase("LL_y+_z+", "LL", "d", "e", "0 < d < e", 1, 1, 1, "-d*A", "A>0"),
    SignedBandCase("LL_y+_z-", "LL", "d", "e", "0 < d < e", 1, -1, 1, "-d*A", "A>0"),
    SignedBandCase("LL_y-_z+", "LL", "d", "e", "0 < d < e", -1, 1, 2, "-2*d*e", "d,e>0"),
    SignedBandCase("LL_y-_z-", "LL", "d", "e", "0 < d < e", -1, -1, 3, "(d-e)*A", "d-e<0 and A>0"),
    SignedBandCase(
        "LH_y+_z+",
        "LH",
        "d",
        "T-e",
        "d,e>0 and d+e<T",
        1,
        1,
        1,
        "-2*d*e",
        "d,e>0",
    ),
    SignedBandCase(
        "LH_y+_z-",
        "LH",
        "d",
        "T-e",
        "d,e>0 and d+e<T",
        1,
        -1,
        3,
        "e*D",
        "e>0 and D<0",
    ),
    SignedBandCase(
        "LH_y-_z+",
        "LH",
        "d",
        "T-e",
        "d,e>0 and d+e<T",
        -1,
        1,
        2,
        "-d*A",
        "d>0 and A>0",
    ),
    SignedBandCase(
        "LH_y-_z-",
        "LH",
        "d",
        "T-e",
        "d,e>0 and d+e<T",
        -1,
        -1,
        2,
        "-d*A",
        "d>0 and A>0",
    ),
    SignedBandCase("HH_y+_z+", "HH", "T-d", "T-e", "0 < e < d", 1, 1, 1, "-e*A", "e>0 and A>0"),
    SignedBandCase("HH_y+_z-", "HH", "T-d", "T-e", "0 < e < d", 1, -1, 3, "-2*d*e", "d,e>0"),
    SignedBandCase("HH_y-_z+", "HH", "T-d", "T-e", "0 < e < d", -1, 1, 1, "-e*A", "e>0 and A>0"),
    SignedBandCase("HH_y-_z-", "HH", "T-d", "T-e", "0 < e < d", -1, -1, 2, "(d-e)*D", "d-e>0 and D<0"),
)


def _radius(sign: int, band_angle: float) -> float:
    """Positive radius with P(r) = sign*sin(band_angle)."""
    return math.exp(math.asinh(sign * math.sin(band_angle)))


def _point(radius: float, angle: float) -> tuple[float, float]:
    return (radius * math.cos(angle), radius * math.sin(angle))


def _cross(
    u: tuple[float, float],
    v: tuple[float, float],
    w: tuple[float, float],
) -> float:
    return (v[0] - u[0]) * (w[1] - v[1]) - (v[1] - u[1]) * (w[0] - v[0])


def _turns(m: int, case: SignedBandCase, d: float, e: float) -> tuple[float, float, float]:
    t_step = 2 * math.pi / m
    beta = d if case.beta_form == "d" else t_step - d
    gamma = e if case.gamma_form == "e" else t_step - e
    y = _radius(case.y_sign, d)
    z = _radius(case.z_sign, e)
    a0 = _point(1.0, 0.0)
    a1 = _point(1.0, t_step)
    b0 = _point(y, beta)
    c0 = _point(z, gamma)
    c_minus_1 = _point(z, gamma - t_step)
    return (
        _cross(c_minus_1, a0, b0),
        _cross(a0, b0, c0),
        _cross(b0, c0, a1),
    )


def _omega(m: int) -> float:
    h = math.pi / m
    sec_h = 1.0 / math.cos(h)
    return (sec_h * sec_h - 1.0) / (2.0 * sec_h)


def _delta(m: int) -> float:
    return math.asin(_omega(m))


def _case_samples(m: int, band_case: str, grid: int) -> list[tuple[float, float]]:
    delta = _delta(m)
    values = [delta * (i + 1) / (grid + 1) for i in range(grid)]
    if band_case == "LL":
        return [(d, e) for i, d in enumerate(values) for e in values[i + 1 :]]
    if band_case == "HH":
        return [(d, e) for i, d in enumerate(values) for e in values[:i]]
    if band_case == "LH":
        t_step = 2 * math.pi / m
        return [(d, e) for d in values for e in values if d + e < t_step]
    raise ValueError(f"unknown band case: {band_case}")


def _sample_fixed_killers(ms: Sequence[int], grid: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for m in ms:
        m_record: dict[str, Any] = {
            "m": m,
            "grid": grid,
            "delta": _delta(m),
            "case_records": [],
        }
        all_negative = True
        global_max = -math.inf
        for case in SIGNED_CASES:
            samples = _case_samples(m, case.band_case, grid)
            max_killer = -math.inf
            max_min_turn = -math.inf
            argmax: dict[str, Any] | None = None
            for d, e in samples:
                turns = _turns(m, case, d, e)
                killer = turns[case.killer_turn - 1]
                min_turn = min(turns)
                if killer > max_killer:
                    max_killer = killer
                    argmax = {
                        "d": d,
                        "e": e,
                        "turns": list(turns),
                    }
                if min_turn > max_min_turn:
                    max_min_turn = min_turn
            case_clear = max_killer < 0.0
            all_negative = all_negative and case_clear
            global_max = max(global_max, max_killer)
            m_record["case_records"].append(
                {
                    "case_id": case.case_id,
                    "killer_turn": case.killer_turn,
                    "sample_count": len(samples),
                    "max_killer_turn": max_killer,
                    "max_min_turn": max_min_turn,
                    "sampled_killer_negative": case_clear,
                    "argmax": argmax,
                }
            )
        m_record["sampled_fixed_killer_all_negative"] = all_negative
        m_record["max_killer_turn_over_cases"] = global_max
        records.append(m_record)
    return records


def _leading_sign_constants(m: int) -> dict[str, float | bool]:
    t_step = 2 * math.pi / m
    sin_t = math.sin(t_step)
    cos_t = math.cos(t_step)
    a = sin_t + cos_t - 1.0
    b = cos_t - sin_t - 1.0
    c = 1.0 + sin_t - cos_t
    d = 1.0 - sin_t - cos_t
    return {
        "m": m,
        "T": t_step,
        "A=sinT+cosT-1": a,
        "B=cosT-sinT-1": b,
        "C=1+sinT-cosT": c,
        "D=1-sinT-cosT": d,
        "signs_ok_for_0_lt_T_le_pi_over_4": a > 0 and b < 0 and c > 0 and d < 0,
    }


def _validate_inputs(ms: Sequence[int], grid: int) -> None:
    if not ms:
        raise ValueError("at least one m-value is required")
    if any(m < 8 for m in ms):
        raise ValueError("quarter-cell signed-band preflight is scoped to m >= 8")
    if grid < 2:
        raise ValueError("grid must be at least 2 so LL/HH samples are nonempty")


def build_payload(ms: Sequence[int], grid: int) -> dict[str, Any]:
    _validate_inputs(ms, grid)
    leading_signs = [_leading_sign_constants(m) for m in ms]
    sample_records = _sample_fixed_killers(ms, grid)
    all_leading_ok = all(record["signs_ok_for_0_lt_T_le_pi_over_4"] for record in leading_signs)
    all_sampled_negative = all(record["sampled_fixed_killer_all_negative"] for record in sample_records)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Quarter-cell signed-band turn preflight for the three-orbit "
            "(t=3) m=0 mod 4 residual. Records the exact boundary-band "
            "case split and the first nonzero negative turn term in each "
            "signed cell, plus deterministic float stress of those fixed "
            "killer turns. This is not the global sign proof: m=8,12,16 "
            "quarter cells remain open, and this is not an all-m "
            "three-orbit obstruction, proof of Erdos Problem #97, "
            "counterexample, or official/global status update."
        ),
        "provenance": {
            "generator": "scripts/check_quarter_cell_signed_band_preflight.py",
            "command": (
                "python scripts/check_quarter_cell_signed_band_preflight.py "
                "--write --assert-expected"
            ),
        },
        "definitions": {
            "T": "2*pi/m",
            "P(r)": "(r^2 - 1)/(2*r)",
            "radius_sign": "P(y)=y_sign*sin(d), P(z)=z_sign*sin(e)",
            "A": "sin(T)+cos(T)-1",
            "B": "cos(T)-sin(T)-1",
            "C": "1+sin(T)-cos(T)",
            "D": "1-sin(T)-cos(T)",
            "turns": [
                "turn_1 = orient(C_{-1}, A_0, B_0)",
                "turn_2 = orient(A_0, B_0, C_0)",
                "turn_3 = orient(B_0, C_0, A_1)",
            ],
        },
        "side_cases": [
            {
                "band_case": "LL",
                "beta": "d",
                "gamma": "e",
                "cone": "0 < d < e",
            },
            {
                "band_case": "LH",
                "beta": "d",
                "gamma": "T-e",
                "cone": "d,e>0 and d+e<T",
            },
            {
                "band_case": "HH",
                "beta": "T-d",
                "gamma": "T-e",
                "cone": "0 < e < d",
            },
        ],
        "signed_case_count": len(SIGNED_CASES),
        "signed_cases": [asdict(case) for case in SIGNED_CASES],
        "leading_killer_case_count": len(SIGNED_CASES),
        "leading_sign_constants": leading_signs,
        "leading_sign_ok_for_sample_ms": all_leading_ok,
        "sample_grid": grid,
        "sample_ms": list(ms),
        "sample_records": sample_records,
        "sampled_fixed_killer_all_negative": all_sampled_negative,
        "open_quarter_cells_still_open": list(OPEN_QUARTER_MS),
        "next_exact_target": (
            "Prove the listed killer turn is negative on each full signed "
            "band cell, or produce a different exact CAD/resultant/interval "
            "certificate. The leading-term table only proves the boundary "
            "tangent direction."
        ),
        "does_not_claim": [
            "m=8,12,16 quarter cells closed",
            "exact certificate for m>=8 quarter cells",
            "all-m quarter-cell obstruction",
            "all-m three-orbit obstruction",
            "general proof of Erdos Problem #97",
            "counterexample to Erdos Problem #97",
            "official/global status update",
        ],
    }


def assert_expected(payload: dict[str, Any]) -> None:
    assert payload["schema"] == SCHEMA
    assert payload["status"] == STATUS
    assert payload["trust"] == TRUST
    assert payload["signed_case_count"] == 12
    assert payload["leading_killer_case_count"] == 12
    assert payload["leading_sign_ok_for_sample_ms"] is True
    assert payload["sampled_fixed_killer_all_negative"] is True
    assert payload["open_quarter_cells_still_open"] == list(OPEN_QUARTER_MS)


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ms", type=int, nargs="*", default=list(DEFAULT_MS))
    parser.add_argument("--grid", type=int, default=DEFAULT_GRID)
    parser.add_argument(
        "--artifact",
        default="data/certificates/quarter_cell_signed_band_preflight.json",
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = build_payload(args.ms, args.grid)
    if args.assert_expected:
        assert_expected(payload)

    artifact_path = Path(args.artifact)
    if args.write:
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        with artifact_path.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    if args.check:
        stored = _read_json(artifact_path)
        if stored != payload:
            print(
                json.dumps(
                    {
                        "schema": SCHEMA,
                        "status": "ARTIFACT_MISMATCH",
                        "artifact": str(artifact_path),
                    },
                    indent=1,
                    sort_keys=True,
                ),
                file=sys.stderr,
            )
            return 1
    if args.json:
        print(json.dumps(payload, indent=1, sort_keys=True))
    elif not args.write:
        print(
            f"{STATUS}: signed_cases={payload['signed_case_count']} "
            f"leading_ok={payload['leading_sign_ok_for_sample_ms']} "
            f"sampled_fixed_killer_all_negative="
            f"{payload['sampled_fixed_killer_all_negative']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
