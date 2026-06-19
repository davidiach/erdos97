#!/usr/bin/env python3
"""Interval-derivative certificate for Erdos97 three-orbit quarter cells.

It addresses the A-row-reduced quarter-cell target described in
`docs/quarter-cell-closure.md` and `docs/quarter-cell-signed-band-preflight.md`.
For m in {8,12,16}, it certifies the 12 signed boundary-band cells by proving a
fixed derivative (or mixed derivative) sign for the stored killer turn on the
whole boundary-band square 0 <= d,e <= delta_m.

Trust boundary: this is interval arithmetic using mpmath.iv. It is a compact,
reproducible machine certificate, not a Lean/formal proof.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import mpmath as mp

SCHEMA = "erdos97.quarter_cell_derivative_certificate.v1"
STATUS = "REPO_LOCAL_INTERVAL_DERIVATIVE_CERTIFICATE"
TRUST = "machine interval arithmetic (mpmath.iv), review recommended"
DEFAULT_M_VALUES = (8, 12, 16)
DEFAULT_ARTIFACT = Path("data/certificates/quarter_cell_derivative_certificate.json")
PROVENANCE = {
    "generator": "scripts/check_quarter_cell_derivative_certificate.py",
    "command": (
        "python scripts/check_quarter_cell_derivative_certificate.py "
        "--m-values 8,12,16 --assert-expected "
        "--write data/certificates/quarter_cell_derivative_certificate.json"
    ),
}

# Turn names used by this checker.  They correspond to the three consecutive
# per-period turns in the angular order
#     A_0, B_0, C_0, A_1, B_1, C_1, ...
# with
#     tau_A = orient(C_{-1}, A_0, B_0) = orient(C_0, A_1, B_1)
#     tau_B = orient(A_0, B_0, C_0)
#     tau_C = orient(B_0, C_0, A_1)
# The preflight note numbers these as killer turns 1,2,3 respectively.
TURN_NUMBERING = {
    "preflight_1": "tau_A = orient(C_0, A_1, B_1)",
    "preflight_2": "tau_B = orient(A_0, B_0, C_0)",
    "preflight_3": "tau_C = orient(B_0, C_0, A_1)",
}

# (band_order, y_sign, z_sign, turn, derivative component, sign, proof rule)
# y_sign/z_sign encode P(y)=sign*sin(d), P(z)=sign*sin(e).
# band_order is one of
#   LL: beta=d,     gamma=e,     0<d<e
#   LH: beta=d,     gamma=T-e,   d,e>0 and d+e<T
#   HH: beta=T-d,   gamma=T-e,   0<e<d
CELL_PLANS: tuple[tuple[str, int, int, str, str, str, str], ...] = (
    ("LL", +1, +1, "tau_A", "d", "<", "F(0,e)=0 and F_d<0"),
    ("LL", +1, -1, "tau_A", "d", "<", "F(0,e)=0 and F_d<0"),
    ("LL", -1, +1, "tau_B", "de", "<", "F(d,0)=F(0,e)=0 and F_de<0"),
    ("LL", -1, -1, "tau_C", "e", "<", "F(d,d)=0 and F_e<0; integrate from e=d to e>d"),
    ("LH", +1, +1, "tau_A", "de", "<", "F(d,0)=F(0,e)=0 and F_de<0"),
    ("LH", +1, -1, "tau_C", "e", "<", "F(d,0)=0 and F_e<0"),
    ("LH", -1, +1, "tau_B", "d", "<", "F(0,e)=0 and F_d<0"),
    ("LH", -1, -1, "tau_B", "d", "<", "F(0,e)=0 and F_d<0"),
    ("HH", +1, +1, "tau_A", "e", "<", "F(d,0)=0 and F_e<0"),
    ("HH", +1, -1, "tau_C", "de", "<", "F(d,0)=F(0,e)=0 and F_de<0"),
    ("HH", -1, +1, "tau_A", "e", "<", "F(d,0)=0 and F_e<0"),
    ("HH", -1, -1, "tau_B", "e", ">", "F(d,d)=0 and F_e>0; integrate backward from e=d to e<d"),
)


def _iv_zero() -> Any:
    return mp.iv.mpf([0, 0])


@dataclass(frozen=True)
class Jet2:
    """Value plus d/e first partials and mixed d-e partial over intervals."""

    v: Any
    d: Any
    e: Any
    de: Any

    def __add__(self, other: Any) -> "Jet2":
        other = to_jet(other)
        return Jet2(self.v + other.v, self.d + other.d, self.e + other.e, self.de + other.de)

    __radd__ = __add__

    def __neg__(self) -> "Jet2":
        return Jet2(-self.v, -self.d, -self.e, -self.de)

    def __sub__(self, other: Any) -> "Jet2":
        return self + (-to_jet(other))

    def __rsub__(self, other: Any) -> "Jet2":
        return to_jet(other) + (-self)

    def __mul__(self, other: Any) -> "Jet2":
        other = to_jet(other)
        return Jet2(
            self.v * other.v,
            self.d * other.v + self.v * other.d,
            self.e * other.v + self.v * other.e,
            self.de * other.v + self.d * other.e + self.e * other.d + self.v * other.de,
        )

    __rmul__ = __mul__

    def __truediv__(self, other: Any) -> "Jet2":
        return self * inv(to_jet(other))

    def __rtruediv__(self, other: Any) -> "Jet2":
        return to_jet(other) * inv(self)


def to_jet(x: Any) -> Jet2:
    if isinstance(x, Jet2):
        return x
    return Jet2(x, _iv_zero(), _iv_zero(), _iv_zero())


def inv(f: Jet2) -> Jet2:
    # phi(x)=1/x, phi'=-1/x^2, phi''=2/x^3
    v = 1 / f.v
    fp = -1 / (f.v**2)
    fpp = 2 / (f.v**3)
    return Jet2(v, fp * f.d, fp * f.e, fp * f.de + fpp * f.d * f.e)


def sin(f: Any) -> Jet2:
    f = to_jet(f)
    return Jet2(
        mp.iv.sin(f.v),
        mp.iv.cos(f.v) * f.d,
        mp.iv.cos(f.v) * f.e,
        mp.iv.cos(f.v) * f.de - mp.iv.sin(f.v) * f.d * f.e,
    )


def cos(f: Any) -> Jet2:
    f = to_jet(f)
    return Jet2(
        mp.iv.cos(f.v),
        -mp.iv.sin(f.v) * f.d,
        -mp.iv.sin(f.v) * f.e,
        -mp.iv.sin(f.v) * f.de - mp.iv.cos(f.v) * f.d * f.e,
    )


def sqrt(f: Any) -> Jet2:
    f = to_jet(f)
    root = mp.iv.sqrt(f.v)
    fp = 1 / (2 * root)
    fpp = -1 / (4 * root**3)
    return Jet2(root, fp * f.d, fp * f.e, fp * f.de + fpp * f.d * f.e)


def r_signed(sign: int, u: Jet2) -> Jet2:
    """Positive radius solving P(r)=(r^2-1)/(2r)=sign*sin(u)."""

    q = sign * sin(u)
    return q + sqrt(1 + q * q)


def iv_box(a: Any, b: Any) -> Any:
    return mp.iv.mpf([a, b])


def iv_component_bounds(x: Any) -> dict[str, str]:
    return {"lower": mp.nstr(x.a, 50), "upper": mp.nstr(x.b, 50)}


def float_component_bounds(x: Any) -> tuple[float, float]:
    return (float(x.a), float(x.b))


def delta_interval(m: int) -> Any:
    """Interval enclosure of delta_m = asin(P(sec(pi/m))).

    The mpmath interval context used in this environment has sin/cos/sqrt but
    no asin.  We compute the scalar high-precision value and pad it by a large
    precision-relative amount.  The derivative intervals have margins many
    orders of magnitude larger than this padding for the certified m values.
    """

    h = mp.pi / m
    omega = (mp.sin(h) ** 2) / (2 * mp.cos(h))
    center = mp.asin(omega)
    pad = mp.mpf(10) ** (-(mp.mp.dps // 2))
    return mp.iv.mpf([center - pad, center + pad])


def turn_jet(order: str, y_sign: int, z_sign: int, turn_name: str, T: Any, d_box: Any, e_box: Any) -> Jet2:
    d = Jet2(d_box, mp.iv.mpf([1, 1]), _iv_zero(), _iv_zero())
    e = Jet2(e_box, _iv_zero(), mp.iv.mpf([1, 1]), _iv_zero())
    Tj = to_jet(T)

    y = r_signed(y_sign, d)
    z = r_signed(z_sign, e)

    if order == "LL":
        beta = d
        gamma = e
    elif order == "LH":
        beta = d
        gamma = Tj - e
    elif order == "HH":
        beta = Tj - d
        gamma = Tj - e
    else:
        raise ValueError(f"unknown order: {order!r}")

    # Polar orientation identity for three points (r_i, theta_i):
    # orient(1,2,3) = r1*r2*sin(theta2-theta1)
    #               + r2*r3*sin(theta3-theta2)
    #               + r3*r1*sin(theta1-theta3).
    tau_b = y * sin(beta) + y * z * sin(gamma - beta) - z * sin(gamma)
    tau_c = y * z * sin(gamma - beta) + z * sin(Tj - gamma) - y * sin(Tj - beta)
    tau_a = z * sin(Tj - gamma) + y * sin(beta) - y * z * sin(Tj + beta - gamma)

    if turn_name == "tau_A":
        return tau_a
    if turn_name == "tau_B":
        return tau_b
    if turn_name == "tau_C":
        return tau_c
    raise ValueError(f"unknown turn: {turn_name!r}")


def certify_m(m: int) -> dict[str, Any]:
    if m <= 0:
        raise ValueError("m must be positive")
    T = 2 * mp.iv.pi / m
    delta = delta_interval(m)
    # Use the upper endpoint for both d and e. This intentionally certifies the
    # whole square 0<=d,e<=upper(delta_m), a superset of the open triangular
    # cells after adding the order inequalities d<e, e<d, or d+e<T.
    dmax = delta.b
    d_box = iv_box(0, dmax)
    e_box = iv_box(0, dmax)

    records: list[dict[str, Any]] = []
    ok = True
    for order, y_sign, z_sign, turn_name, component, sign, proof_rule in CELL_PLANS:
        F = turn_jet(order, y_sign, z_sign, turn_name, T, d_box, e_box)
        interval = {"d": F.d, "e": F.e, "de": F.de}[component]
        lower, upper = float_component_bounds(interval)
        certified = bool(upper < 0) if sign == "<" else bool(lower > 0)
        ok = ok and certified
        records.append(
            {
                "cell": f"{order}_y{'+' if y_sign > 0 else '-'}_z{'+' if z_sign > 0 else '-'}",
                "band_order": order,
                "y_radius_sign": y_sign,
                "z_radius_sign": z_sign,
                "killer_turn": turn_name,
                "certified_component": component,
                "required_sign": sign,
                "component_interval": iv_component_bounds(interval),
                "component_interval_float": {"lower": lower, "upper": upper},
                "certified": certified,
                "proof_rule": proof_rule,
            }
        )

    return {
        "m": m,
        "T_interval": iv_component_bounds(T),
        "delta_m_interval": iv_component_bounds(delta),
        "delta_m_upper_used": mp.nstr(dmax, 50),
        "domain_certified": "0 <= d,e <= upper(delta_m); cell order inequalities are a subset",
        "all_cells_certified": ok,
        "cells": records,
    }


def build_payload(m_values: Iterable[int], dps: int) -> dict[str, Any]:
    mp.mp.dps = dps
    mp.iv.dps = dps
    m_values = tuple(int(m) for m in m_values)
    results = [certify_m(m) for m in m_values]
    ok = all(item["all_cells_certified"] for item in results)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "provenance": PROVENANCE,
        "mpmath_dps": dps,
        "claim_scope": (
            "For the A-row-reduced three-orbit C_m quarter-cell witness locus, "
            "the 12 signed boundary-band cells for the listed m values have a "
            "fixed non-positive killer turn throughout the strict cell. This "
            "closes those quarter-cell subcases in the repo-local interval "
            "arithmetic sense. It is not a global proof of Erdos Problem #97, "
            "not a counterexample, not a proof for arbitrary cyclic-order or "
            "non-three-orbit configurations, and not a formal proof-assistant "
            "certificate."
        ),
        "turn_numbering": TURN_NUMBERING,
        "method": [
            "Write T=2*pi/m and P(r)=(r^2-1)/(2r).",
            "In each boundary-band cell set beta/gamma to d,e,T-d,T-e as appropriate and set P(y)=+/-sin(d), P(z)=+/-sin(e).",
            "Evaluate the preflight killer turn F as a Jet2 interval expression carrying F_d, F_e, and F_de.",
            "Certify the required derivative sign on the whole square 0<=d,e<=upper(delta_m), which contains each open cell.",
            "Use the exact boundary identities listed per cell to integrate the derivative sign and obtain F<0 in the strict cell.",
        ],
        "m_values": list(m_values),
        "certified_quarter_cell_m_values": list(m_values) if ok else [],
        "signed_cell_count_per_m": len(CELL_PLANS),
        "certified_cell_count": sum(len(item["cells"]) for item in results if item["all_cells_certified"]),
        "all_certified": ok,
        "does_not_claim": [
            "general proof of Erdos Problem #97",
            "counterexample to Erdos Problem #97",
            "all-m quarter-cell obstruction",
            "all-m three-orbit obstruction",
            "closure of non-quarter three-orbit cells",
            "closure of arbitrary cyclic-order or non-three-orbit configurations",
            "formal proof-assistant certificate",
            "official/global status update",
        ],
        "results": results,
    }


def parse_m_values(text: str) -> tuple[int, ...]:
    out = []
    for part in text.split(","):
        part = part.strip()
        if part:
            out.append(int(part))
    if not out:
        raise argparse.ArgumentTypeError("at least one m value is required")
    return tuple(out)


def assert_expected(payload: dict[str, Any]) -> None:
    if payload["schema"] != SCHEMA:
        raise AssertionError("schema mismatch")
    if payload["status"] != STATUS:
        raise AssertionError("status mismatch")
    if payload["signed_cell_count_per_m"] != 12:
        raise AssertionError("expected 12 signed cells per m")
    expected_count = payload["signed_cell_count_per_m"] * len(payload["m_values"])
    if payload["certified_cell_count"] != expected_count:
        raise AssertionError(f"expected {expected_count} certified cells")
    if not payload["all_certified"]:
        raise AssertionError("not all cells certified")


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, dict):
        raise ValueError(f"artifact must contain a JSON object: {path}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--m-values",
        type=parse_m_values,
        default=DEFAULT_M_VALUES,
        help="comma-separated m values; default: 8,12,16",
    )
    parser.add_argument("--dps", type=int, default=80, help="mpmath decimal precision for interval arithmetic")
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT, help="artifact path for --check")
    parser.add_argument("--write", type=Path, help="write JSON payload to this path")
    parser.add_argument("--check", action="store_true", help="compare stored artifact to deterministic regeneration")
    parser.add_argument("--json", action="store_true", help="print full JSON payload")
    parser.add_argument("--assert-expected", action="store_true", help="exit nonzero unless all cells certify")
    args = parser.parse_args()

    payload = build_payload(args.m_values, args.dps)
    if args.assert_expected:
        assert_expected(payload)
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        stored = _read_json(args.artifact)
        if stored != payload:
            print(
                json.dumps(
                    {
                        "schema": SCHEMA,
                        "status": "ARTIFACT_MISMATCH",
                        "artifact": str(args.artifact),
                    },
                    indent=2,
                    sort_keys=True,
                ),
                file=sys.stderr,
            )
            return 1
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        summary = {
            "schema": payload["schema"],
            "status": payload["status"],
            "m_values": payload["m_values"],
            "all_certified": payload["all_certified"],
            "cell_count": sum(len(item["cells"]) for item in payload["results"]),
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
