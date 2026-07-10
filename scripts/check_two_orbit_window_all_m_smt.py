#!/usr/bin/env python3
"""Exact all-m SMT certificate for the two-orbit window-root exclusion (Step 5).

Context (`docs/two-orbit-circulant-obstruction.md`, review-pending lemma
draft): the two-orbit reduction forces the half-step offset ``phi = h`` with
``h = pi/m``, forces every first-orbit row to one same-orbit pair (offset
``a``) plus one cross-orbit pair (odd offset ``p``), and pins the radius
ratio ``x`` to the strict-convexity window ``(cos h, sec h)``. Step 5 of that
note claims the row equation

    E_A:  4*sin(a*h)^2 = x^2 + 1 - 2*x*cos(p*h)

has no root ``x`` in the open window, for every ``m >= 3``, every
``a in {1, ..., ceil(m/2) - 1}``, and every odd ``p in {1, ..., m - 1}``.
Until now the machine audit of Step 5 was a float64 screen with high-precision
escalation over ``m <= 400`` (`scripts/check_two_orbit_dynamic_window_lemma.py`).
This script replaces that finite screen with one exact certificate covering
all ``m >= 3`` simultaneously.

Encoding. Because ``g(x) = x^2 + 1 - 2*x*cos(p*h)`` is strictly increasing on
the window (``g'(x) = 2*(x - cos(p*h)) > 0`` there, since ``x > cos h >=
cos(p*h)``), ``E_A`` has a root in the open window iff

    -sin(h)^2  <  T  <  (1 - 2*cos(u)) * sin(h)^2,
    where  u = 2*a*h,  v = p*h,  T = 2*cos(v)*cos(h) - 2*cos(u).

Substitute ``ch = cos h``, ``sh = sin h``, ``cu = cos u``, ``su = sin u``,
``cv = cos v``, ``sv = sin v``. Every integer instance ``(m, a, p)`` maps to a
real point satisfying the polynomial relaxation

    ch^2 + sh^2 = 1,   sh > 0,   ch >= 1/2            [h = pi/m, m >= 3]
    cu^2 + su^2 = 1,   su >= 0                        [u in [0, pi]]
    cv^2 + sv^2 = 1,   sv >= 0                        [v in [0, pi]]
    cu <= 2*ch^2 - 1                                  [u >= 2h]
    cu >= -ch                                         [u <= pi - h]
    cv <= ch                                          [v >= h]
    cv >= -ch                                         [v <= pi - h]
    cu*cv + su*sv <= ch                               [|u - v| >= h]

(the last constraint holds because ``|2a - p|`` is odd, hence nonzero). z3
nonlinear real arithmetic decides that this relaxation together with the two
window inequalities is UNSAT, so no integer instance has a window root --
uniformly in ``m``. The embedding argument is written out in
`docs/two-orbit-window-all-m-smt.md` and spot-checked here numerically.

Controls (guarding against a vacuous or mis-signed encoding):

* relaxing the strict upper inequality to ``<=`` makes the system SAT, and
  two further z3 decisions pin every such equality point to the corner
  ``ch = 1/2, cu = -1/2, cv = 1/2`` -- exactly the known ``m = 3, a = 1,
  p = 1`` boundary hit at ``x = sec(pi/3) = 2``, verified here in exact
  rational arithmetic; a companion decision shows exact lower-boundary
  contact (``T = -sin(h)^2``, a root at ``x = cos h``) is impossible in the
  relaxation even with the upper inequality relaxed, so the m = 3 upper
  corner is the only closed-boundary contact of any kind;
* dropping the odd-gap constraint ``|u - v| >= h`` makes the system SAT (a
  pinned rational witness is verified exactly), so that constraint is
  load-bearing and the window inequalities alone are not contradictory.

Trust: ``EXACT_OBSTRUCTION`` (SMT certificate) for the Step 5 window-root
exclusion only, over all ``m >= 3`` at once. Steps 1-4 of the two-orbit note
(offset forcing, row-shape forcing, convexity window) remain review-pending
prose; this artifact does not prove the full two-orbit lemma by itself, is
not a proof of Erdos Problem #97, and is not a counterexample.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction

# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------

CONSTRAINT_DOC = [
    ("unit_h", "ch^2 + sh^2 == 1"),
    ("h_positive", "sh > 0"),
    ("m_at_least_3", "ch >= 1/2"),
    ("unit_u", "cu^2 + su^2 == 1"),
    ("u_in_0_pi", "su >= 0"),
    ("unit_v", "cv^2 + sv^2 == 1"),
    ("v_in_0_pi", "sv >= 0"),
    ("u_ge_2h", "cu <= 2*ch^2 - 1"),
    ("u_le_pi_minus_h", "cu >= -ch"),
    ("v_ge_h", "cv <= ch"),
    ("v_le_pi_minus_h", "cv >= -ch"),
    ("odd_gap", "cu*cv + su*sv <= ch"),
    ("window_lower", "2*cv*ch - 2*cu > -sh^2"),
    ("window_upper_strict", "2*cv*ch - 2*cu < (1 - 2*cu)*sh^2"),
]


def _base_solver(z3, *, timeout_ms: int):
    ch, sh, cu, su, cv, sv = z3.Reals("ch sh cu su cv sv")
    s = z3.Solver()
    s.set("timeout", timeout_ms)
    s.add(ch * ch + sh * sh == 1, sh > 0, ch >= z3.Q(1, 2))
    s.add(cu * cu + su * su == 1, su >= 0)
    s.add(cv * cv + sv * sv == 1, sv >= 0)
    s.add(cu <= 2 * ch * ch - 1)  # u >= 2h
    s.add(cu >= -ch)  # u <= pi - h
    s.add(cv <= ch)  # v >= h
    s.add(cv >= -ch)  # v <= pi - h
    return s, (ch, sh, cu, su, cv, sv)


def solver_for(
    z3,
    *,
    upper_strict: bool = True,
    with_gap: bool = True,
    lower_equality: bool = False,
    require_ch_above_half: bool = False,
    require_off_corner: bool = False,
    timeout_ms: int = 60000,
):
    s, (ch, sh, cu, su, cv, sv) = _base_solver(z3, timeout_ms=timeout_ms)
    if with_gap:
        s.add(cu * cv + su * sv <= ch)  # |u - v| >= h
    t_expr = 2 * cv * ch - 2 * cu
    if lower_equality:
        s.add(t_expr == -sh * sh)  # exact lower-boundary contact
    else:
        s.add(t_expr > -sh * sh)  # window lower inequality
    if upper_strict:
        s.add(t_expr < (1 - 2 * cu) * sh * sh)  # window upper inequality
    else:
        s.add(t_expr <= (1 - 2 * cu) * sh * sh)
    if require_ch_above_half:
        s.add(ch > z3.Q(1, 2))
    if require_off_corner:
        s.add(
            z3.Or(
                ch != z3.Q(1, 2),
                cu != -z3.Q(1, 2),
                cv != z3.Q(1, 2),
            )
        )
    return s


def decide_all(*, timeout_ms: int) -> dict:
    import z3

    def run(**kw):
        return str(solver_for(z3, timeout_ms=timeout_ms, **kw).check())

    return {
        "main_strict": run(),
        "nonstrict_upper": run(upper_strict=False),
        "nonstrict_upper_ch_above_half": run(
            upper_strict=False, require_ch_above_half=True
        ),
        "nonstrict_upper_off_corner": run(
            upper_strict=False, require_off_corner=True
        ),
        "lower_boundary_contact": run(lower_equality=True, upper_strict=False),
        "no_gap": run(with_gap=False),
    }


EXPECTED_DECISIONS = {
    "main_strict": "unsat",
    "nonstrict_upper": "sat",
    "nonstrict_upper_ch_above_half": "unsat",
    "nonstrict_upper_off_corner": "unsat",
    "lower_boundary_contact": "unsat",
    "no_gap": "sat",
}


# ---------------------------------------------------------------------------
# Exact rational self-tests (no z3)
# ---------------------------------------------------------------------------


def corner_point_exact_check() -> bool:
    """The m=3 corner (h=pi/3, u=2pi/3, v=pi/3) satisfies every constraint of
    the non-strict variant, with the upper window inequality holding with
    equality, in exact rational arithmetic.

    Point: ch=1/2, sh^2=3/4, cu=-1/2, su^2=3/4, cv=1/2, sv^2=3/4. Since
    su = sv = sqrt(3)/2 >= 0, the product su*sv equals exactly 3/4.
    """

    ch, cu, cv = Fraction(1, 2), Fraction(-1, 2), Fraction(1, 2)
    sh2 = su2 = sv2 = Fraction(3, 4)
    su_sv = Fraction(3, 4)  # sqrt(3)/2 * sqrt(3)/2, both nonnegative
    t_val = 2 * cv * ch - 2 * cu
    checks = [
        ch * ch + sh2 == 1,
        sh2 > 0,
        ch >= Fraction(1, 2),
        cu * cu + su2 == 1,
        su2 >= 0,
        cv * cv + sv2 == 1,
        sv2 >= 0,
        cu <= 2 * ch * ch - 1,
        cu >= -ch,
        cv <= ch,
        cv >= -ch,
        cu * cv + su_sv <= ch,
        t_val > -sh2,
        t_val <= (1 - 2 * cu) * sh2,  # non-strict variant
        t_val == (1 - 2 * cu) * sh2,  # equality: on the boundary
    ]
    return all(checks)


def corner_is_m3_boundary_root() -> bool:
    """The corner corresponds to (m, a, p) = (3, 1, 1) and to the E_A root
    x = 2 = sec(pi/3) at the closed window boundary, exactly.

    With m=3: cos(p*h) = cos(pi/3) = 1/2 and 4*sin(a*h)^2 = 4*(3/4) = 3, so
    E_A reads x^2 - x + 1 = 3, i.e. (x - 2)*(x + 1) = 0; the positive root
    x = 2 equals sec(pi/3), the excluded open-window endpoint.
    """

    cos_h = Fraction(1, 2)  # cos(pi/3)
    cos_ph = Fraction(1, 2)  # p = 1
    target = Fraction(3)  # 4*sin(pi/3)^2
    x = 1 / cos_h  # sec(pi/3) = 2, the upper window endpoint
    e_a_at_x = x * x + 1 - 2 * x * cos_ph
    return e_a_at_x == target


NO_GAP_WITNESS = {
    "ch": Fraction(3, 4),
    "sh2": Fraction(7, 16),
    "cu": Fraction(0),
    "su": Fraction(1),
    "cv": Fraction(0),
    "sv": Fraction(1),
}


def no_gap_witness_exact_check() -> bool:
    """A pinned rational witness (h = arccos(3/4), u = v = pi/2) satisfies
    every constraint except the odd-gap constraint, which it violates.

    This shows the window inequalities are jointly satisfiable once the
    integer structure (|u - v| >= h) is dropped, so the main UNSAT is a
    genuine consequence of that structure rather than of a mis-signed
    contradiction elsewhere in the encoding.
    """

    w = NO_GAP_WITNESS
    ch, sh2 = w["ch"], w["sh2"]
    cu, su, cv, sv = w["cu"], w["su"], w["cv"], w["sv"]
    t_val = 2 * cv * ch - 2 * cu
    non_gap_ok = all(
        [
            ch * ch + sh2 == 1,
            sh2 > 0,
            ch >= Fraction(1, 2),
            cu * cu + su * su == 1,
            su >= 0,
            cv * cv + sv * sv == 1,
            sv >= 0,
            cu <= 2 * ch * ch - 1,
            cu >= -ch,
            cv <= ch,
            cv >= -ch,
            t_val > -sh2,
            t_val < (1 - 2 * cu) * sh2,
        ]
    )
    gap_violated = cu * cv + su * sv > ch  # 1 > 3/4
    return non_gap_ok and gap_violated


# ---------------------------------------------------------------------------
# Embedding spot-check and formulation agreement (float, redundant with the
# exact prose argument in docs/two-orbit-window-all-m-smt.md and with the
# finite float screen in scripts/check_two_orbit_dynamic_window_lemma.py)
# ---------------------------------------------------------------------------


def valid_pairs(m: int) -> list[tuple[int, int]]:
    """Same (a, p) ranges as scripts/check_two_orbit_dynamic_window_lemma.py."""

    a_max = (m - 1) // 2
    p_max = m - 1 if m % 2 == 0 else m - 2
    return [(a, p) for a in range(1, a_max + 1) for p in range(1, p_max + 1, 2)]


def embedding_spot_check(max_m: int, tol: float = 1e-9) -> dict:
    """Every integer instance maps into the relaxed constraint region.

    Constraints with exact-equality cases (m = 3 hits u = 2h = pi - h and
    v = h simultaneously) are allowed to sit on the boundary; the check
    requires slack >= -tol only. The unit-circle identities hold by
    construction and are not re-checked.
    """

    pairs_checked = 0
    min_slack = math.inf
    for m in range(3, max_m + 1):
        h = math.pi / m
        ch, sh = math.cos(h), math.sin(h)
        for a, p in valid_pairs(m):
            u, v = 2 * a * h, p * h
            cu, su = math.cos(u), math.sin(u)
            cv, sv = math.cos(v), math.sin(v)
            slacks = (
                sh,  # sh > 0
                ch - 0.5,  # ch >= 1/2
                su,  # su >= 0
                sv,  # sv >= 0
                (2 * ch * ch - 1) - cu,  # u >= 2h
                cu + ch,  # u <= pi - h
                ch - cv,  # v >= h
                cv + ch,  # v <= pi - h
                ch - (cu * cv + su * sv),  # |u - v| >= h
            )
            min_slack = min(min_slack, min(slacks))
            pairs_checked += 1
    return {
        "max_m": max_m,
        "pairs_checked": pairs_checked,
        "ok": min_slack >= -tol,
    }


def formulation_agreement_check(max_m: int, band: float = 1e-9) -> dict:
    """Direct root location in the open window agrees with the T-form used by
    the SMT encoding, for every (m, a, p) with m <= max_m, outside a tiny
    boundary band (the only in-band pair is the m=3 corner)."""

    pairs_checked = 0
    mismatches = 0
    band_hits = 0
    for m in range(3, max_m + 1):
        h = math.pi / m
        x_low, x_high = math.cos(h), 1 / math.cos(h)
        for a, p in valid_pairs(m):
            target = 4 * math.sin(a * h) ** 2

            def g(x: float) -> float:
                return x * x + 1 - 2 * x * math.cos(p * h)

            low_gap = target - g(x_low)
            high_gap = g(x_high) - target
            root_inside = low_gap > 0 and high_gap > 0
            t_val = 2 * math.cos(p * h) * math.cos(h) - 2 * math.cos(2 * a * h)
            lo = -math.sin(h) ** 2
            hi = (1 - 2 * math.cos(2 * a * h)) * math.sin(h) ** 2
            t_inside = lo < t_val < hi
            near = (
                abs(low_gap) < band
                or abs(high_gap) < band
                or abs(t_val - lo) < band
                or abs(t_val - hi) < band
            )
            if near:
                band_hits += 1
            elif root_inside != t_inside:
                mismatches += 1
            pairs_checked += 1
    return {
        "max_m": max_m,
        "pairs_checked": pairs_checked,
        "mismatches": mismatches,
        "boundary_band_hits": band_hits,
    }


# ---------------------------------------------------------------------------
# Payload / CLI
# ---------------------------------------------------------------------------


def compare_artifact_replay(payload, artifact_path: str) -> list[str]:
    """Compare the freshly generated deterministic payload with a stored artifact."""

    with open(artifact_path, encoding="utf-8") as fh:
        stored = json.load(fh)
    if payload == stored:
        return []
    errors: list[str] = []
    for key in sorted(set(payload) | set(stored)):
        if payload.get(key) != stored.get(key):
            errors.append(f"{key}: replay differs from stored artifact")
    return errors


def build_payload(args) -> dict:
    decisions = decide_all(timeout_ms=args.timeout_ms)
    corner_ok = corner_point_exact_check()
    corner_root_ok = corner_is_m3_boundary_root()
    no_gap_ok = no_gap_witness_exact_check()
    embedding = embedding_spot_check(args.max_m)
    agreement = formulation_agreement_check(args.agreement_max_m)
    clear = (
        decisions == EXPECTED_DECISIONS
        and corner_ok
        and corner_root_ok
        and no_gap_ok
        and embedding["ok"]
        and agreement["mismatches"] == 0
        and agreement["boundary_band_hits"] == 1
    )
    return {
        "schema": "erdos97.two_orbit_window_all_m_smt.v1",
        "status": "EXACT_STEP5_ALL_M_SMT" if clear else "INCOMPLETE",
        "trust": "EXACT_OBSTRUCTION",
        "provenance": {
            "generator": "scripts/check_two_orbit_window_all_m_smt.py",
            "command": (
                "python scripts/check_two_orbit_window_all_m_smt.py "
                "--assert-clear --write-artifact "
                "data/certificates/two_orbit_window_all_m_smt.json"
            ),
        },
        "scope": (
            "Exact SMT (z3 nonlinear real arithmetic) certificate for Step 5 "
            "of the review-pending two-orbit circulant obstruction: for every "
            "m >= 3, every a in {1, ..., ceil(m/2) - 1}, and every odd p in "
            "{1, ..., m - 1}, the row equation E_A has no root in the open "
            "strict-convexity window (cos h, sec h), h = pi/m. Proved via a "
            "continuous polynomial relaxation in (cos h, sin h, cos 2ah, "
            "sin 2ah, cos ph, sin ph) that contains every integer instance "
            "and is UNSAT; equality contact with the closed window boundary "
            "is pinned uniquely to the m=3, a=1, p=1 corner x = sec(pi/3) = 2. "
            "This covers all m >= 3 at once, uniformly, and supersedes the "
            "finite float64 screen as the machine audit of Step 5. It is "
            "conditional on the Step 1-4 reduction of "
            "docs/two-orbit-circulant-obstruction.md (offset forcing, row "
            "shape, convexity window), which remains review-pending prose. "
            "Not a proof of the full two-orbit lemma by itself, not a proof "
            "of Erdos Problem #97, not a counterexample, and not an "
            "official/global status update."
        ),
        "encoding_constraints": [list(item) for item in CONSTRAINT_DOC],
        "decisions": decisions,
        "expected_decisions": dict(EXPECTED_DECISIONS),
        "exact_checks": {
            "corner_point_verified": corner_ok,
            "corner_is_m3_boundary_root_x2": corner_root_ok,
            "no_gap_witness_verified": no_gap_ok,
        },
        "embedding_spot_check": embedding,
        "formulation_agreement": agreement,
        "clear": clear,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout-ms", type=int, default=60000)
    ap.add_argument(
        "--max-m",
        type=int,
        default=120,
        help="embedding spot-check bound (redundant with the exact argument)",
    )
    ap.add_argument(
        "--agreement-max-m",
        type=int,
        default=40,
        help="formulation-agreement spot-check bound",
    )
    ap.add_argument(
        "--assert-clear",
        action="store_true",
        help="exit nonzero unless all six z3 decisions match expectations "
        "and every exact/embedding/agreement self-test passes",
    )
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-artifact", type=str, default="")
    ap.add_argument(
        "--check-artifact",
        type=str,
        default="",
        help="compare deterministic replay fields against a stored artifact",
    )
    args = ap.parse_args()
    if args.max_m < 3:
        ap.error("--max-m must be at least 3 (the smallest valid m)")
    if args.agreement_max_m < 3:
        ap.error(
            "--agreement-max-m must be at least 3 so the scan includes the "
            "m=3 boundary corner that the clear predicate expects"
        )

    payload = build_payload(args)

    if args.check_artifact:
        errors = compare_artifact_replay(payload, args.check_artifact)
        if errors:
            print("artifact replay mismatch:", file=sys.stderr)
            for err in errors:
                print(f"- {err}", file=sys.stderr)
            return 1
    if args.write_artifact:
        if not payload["clear"]:
            print(
                "refusing to write a non-clear payload (a z3 decision "
                "returned an unexpected result or a self-test failed); "
                "the target artifact is left untouched",
                file=sys.stderr,
            )
            return 1
        with open(args.write_artifact, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
            fh.write("\n")
    if args.json:
        print(json.dumps(payload, indent=1, sort_keys=True))
    else:
        print(f"decisions: {payload['decisions']}")
        print(
            "exact_checks:",
            payload["exact_checks"],
        )
        print(
            f"embedding m<= {payload['embedding_spot_check']['max_m']}: "
            f"pairs={payload['embedding_spot_check']['pairs_checked']} "
            f"ok={payload['embedding_spot_check']['ok']}"
        )
        print(
            f"agreement m<= {payload['formulation_agreement']['max_m']}: "
            f"pairs={payload['formulation_agreement']['pairs_checked']} "
            f"mismatches={payload['formulation_agreement']['mismatches']} "
            f"boundary_band_hits="
            f"{payload['formulation_agreement']['boundary_band_hits']}"
        )
        print(f"clear={payload['clear']}")
    if args.assert_clear and not payload["clear"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
