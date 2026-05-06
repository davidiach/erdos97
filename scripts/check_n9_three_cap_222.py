#!/usr/bin/env python3
"""Combinatorial closure of the n=9 three-cap rigid (2,2,2) case
(Erdős Problem #97, §5.4).

Setup (canonical-synthesis.md, §5.4 + erdos97-attack-2026-05-05.md):
    Suppose a strictly convex 9-gon V is 4-bad (every vertex has 4 other
    polygon vertices on a common circle around it, the standard counter-
    example assumption). The smallest enclosing circle (SEC) of V is
    supported by 2 or 3 vertices. The diameter case (2 supports) is closed
    by the Moser cap lemma. In the three-cap case the supports
    {p, q, r} form a non-obtuse triangle and the polygon decomposes into
    caps K_pq, K_qr, K_rp (the cyclic arcs). The 2026-05-05 round closed
    n = 8 by the cap-occupancy count: each of p, q, r being 4-bad would
    require >= 2 witnesses inside its opposite cap, summing to >= 6 cap
    interior vertices, so n >= 9. The remaining n = 9 case is the rigid
    (2, 2, 2): each open cap holds exactly 2 polygon vertices.

This script tests the rigid (2, 2, 2) case combinatorially. The cyclic
order is fixed at p, a, b, q, c, d, r, e, f (vertex indices 0..8), with
{a,b} = K_pq, {c,d} = K_qr, {e,f} = K_rp. The cap-occupancy bound at
n = 9 forces

    {c, d} ⊆ W_p,    {e, f} ⊆ W_q,    {a, b} ⊆ W_r,

so each of W_p, W_q, W_r has 2 forced witnesses and 2 free choices.

We do two passes:

(i) **Independent enumeration.** Enumerate all 4-element subsets W_p, W_q,
    W_r containing the forced cap-pair, modulo the dihedral D_3 acting on
    the (p, q, r) cycle. Apply the elementary necessary conditions L4
    (perpendicular-bisector vertex bound) and L5 (two-circle bound) and
    record the L6 perpendicular-overlap structure for each survivor.

(ii) **Cross-check against the n = 9 vertex-circle exhaustive cross-check
     survivors.** The committed artifact
     `data/certificates/2026-05-05/n9_groebner_results.json` records the
     16 dihedral D_9 families (covering all 184 cross-check survivors) of
     selected-witness assignments at n = 9 that pass the L4 + L5 + L6 +
     pair-cap + indegree filters. We test, for each family, whether ANY
     dihedral image admits a (p, q, r) cyclic placement at positions
     (s, s+3, s+6) for which the (2, 2, 2) cap-occupancy constraints

         W_s ⊇ {s+4, s+5},
         W_{s+3} ⊇ {s+7, s+8},
         W_{s+6} ⊇ {s+1, s+2}    (mod 9)

     are simultaneously satisfied.

The cross-check finding (this round): **no D_9 image of any of the 184
n = 9 cross-check survivors satisfies the rigid (2,2,2) cap-occupancy
constraints.** Combined with the n = 9 vertex-circle exhaustive result,
this gives a *combinatorial-only* closure of the (2, 2, 2) rigid case at
n = 9 conditional on the cap-occupancy hypothesis: the survivors of the
basic L4 + L5 + L6 + pair-cap + indegree filters already fail to
combinatorially admit a three-cap (2, 2, 2) layout.

Caveat / scope: the cap-occupancy hypothesis (|W_p ∩ K_qr| >= 2 when p is
an SEC support and 4-bad) is itself a corollary of the inscribed-arc Moser
cap lemma applied to the SEC supports {p, q, r}. The 2026-05-05 audit
flagged that the chord-monotonicity argument only applies to inscribed
arcs at SEC support vertices, so this is the form actually used here. We
do **not** claim this script proves Erdős #97. We claim it closes the
rigid (2, 2, 2) sub-case of the three-cap reduction at n = 9 under the
cap-occupancy hypothesis.

Outputs:
    data/certificates/n9_three_cap_222.json -- machine-readable certificate
    docs/n9-three-cap-rigid.md -- human-readable summary
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_three_cap_222.json"
N9_FAMILIES_PATH = ROOT / "data" / "certificates" / "2026-05-05" / "n9_groebner_results.json"

# Canonical (2,2,2) layout: 0=p, 1=a, 2=b, 3=q, 4=c, 5=d, 6=r, 7=e, 8=f
P, A, B, Q, C, D, R, E, F = range(9)
LABELS = ["p", "a", "b", "q", "c", "d", "r", "e", "f"]

K_PQ = (A, B)
K_QR = (C, D)
K_RP = (E, F)

# Forced witnesses by the cap-occupancy bound (rigid 2,2,2)
FORCED_W = {
    P: {C, D},
    Q: {E, F},
    R: {A, B},
}


def eligible(center: int) -> list[int]:
    """Candidates for the 2 free entries of W_center (rigid 2,2,2 case)."""
    forbidden = FORCED_W[center] | {center}
    return [i for i in range(9) if i not in forbidden]


def enumerate_w(center: int) -> list[frozenset[int]]:
    """All 4-element witness sets containing FORCED_W[center]."""
    forced = FORCED_W[center]
    eligs = eligible(center)
    return [
        frozenset(forced | set(extra))
        for extra in itertools.combinations(eligs, 2)
    ]


# --- Necessary combinatorial filters (L4, L5) -------------------------------

def pair_intersections(W_p, W_q, W_r):
    return {
        (P, Q): W_p & W_q,
        (P, R): W_p & W_r,
        (Q, R): W_q & W_r,
    }


def passes_l5(W_p, W_q, W_r) -> bool:
    return all(len(s) <= 2 for s in pair_intersections(W_p, W_q, W_r).values())


def l4_check(W_p, W_q, W_r) -> dict[str, object]:
    rows = {P: W_p, Q: W_q, R: W_r}
    pair_to_centers: dict[tuple[int, int], list[int]] = {}
    for c, w in rows.items():
        for a, b in itertools.combinations(sorted(w), 2):
            pair_to_centers.setdefault((a, b), []).append(c)
    bad = [
        (LABELS[a], LABELS[b], [LABELS[c] for c in cs])
        for (a, b), cs in pair_to_centers.items()
        if len(cs) > 2
    ]
    return {"violations": bad}


# --- L6 overlap bookkeeping (used for downstream analysis) ------------------

def l6_overlap_pairs(W_p, W_q, W_r):
    rows = {P: W_p, Q: W_q, R: W_r}
    out = []
    for i, j in [(P, Q), (P, R), (Q, R)]:
        ov = rows[i] & rows[j]
        if len(ov) == 2:
            out.append((i, j, frozenset(ov)))
    return out


def triangle_overdetermination(W_p, W_q, W_r):
    overlaps = l6_overlap_pairs(W_p, W_q, W_r)
    return {
        "num_l6_overlaps": len(overlaps),
        "overlaps": [
            {
                "centers": [LABELS[i], LABELS[j]],
                "shared": sorted(LABELS[k] for k in s),
            }
            for i, j, s in overlaps
        ],
    }


# --- Dihedral D_3 quotienting on (p, q, r) ----------------------------------

D3_CYCLE_FORWARD = {
    P: Q, Q: R, R: P,
    A: C, B: D,
    C: E, D: F,
    E: A, F: B,
}

D3_CYCLE_REVERSE = {v: k for k, v in D3_CYCLE_FORWARD.items()}

D3_REFLECT = {
    P: P, Q: R, R: Q,
    A: F, B: E, E: B, F: A,
    C: D, D: C,
}


def apply_perm(perm, ws):
    Wp, Wq, Wr = ws
    inv = {v: k for k, v in perm.items()}
    role_to_old_W = {P: Wp, Q: Wq, R: Wr}
    def img_set(S):
        return frozenset(perm[s] for s in S)
    return tuple(img_set(role_to_old_W[inv[r]]) for r in (P, Q, R))


def canonical_form(W_p, W_q, W_r) -> tuple:
    perms = [
        {i: i for i in range(9)},
        D3_CYCLE_FORWARD,
        D3_CYCLE_REVERSE,
    ]
    candidates = []
    for perm in perms:
        ws = apply_perm(perm, (W_p, W_q, W_r))
        candidates.append(tuple(tuple(sorted(s)) for s in ws))
        ws_ref = apply_perm(D3_REFLECT, ws)
        candidates.append(tuple(tuple(sorted(s)) for s in ws_ref))
    return min(candidates)


# --- (i) Pure enumeration ---------------------------------------------------

def enumerate_classes() -> list[dict[str, object]]:
    options_p = enumerate_w(P)
    options_q = enumerate_w(Q)
    options_r = enumerate_w(R)
    seen_canonical = {}
    classes: list[dict[str, object]] = []
    for Wp in options_p:
        for Wq in options_q:
            for Wr in options_r:
                if not passes_l5(Wp, Wq, Wr):
                    continue
                l4 = l4_check(Wp, Wq, Wr)
                if l4["violations"]:
                    continue
                key = canonical_form(Wp, Wq, Wr)
                if key in seen_canonical:
                    seen_canonical[key]["multiplicity"] += 1
                    continue
                triple = {
                    "W_p_labels": sorted(LABELS[i] for i in Wp),
                    "W_q_labels": sorted(LABELS[i] for i in Wq),
                    "W_r_labels": sorted(LABELS[i] for i in Wr),
                    "canonical_key": [list(t) for t in key],
                    "multiplicity": 1,
                    "l6_diagnostic": triangle_overdetermination(Wp, Wq, Wr),
                    "l4_check": l4,
                    "_W_p_int": sorted(Wp),
                    "_W_q_int": sorted(Wq),
                    "_W_r_int": sorted(Wr),
                }
                seen_canonical[key] = triple
                classes.append(triple)
    return classes


# --- (ii) Cross-check vs. n=9 vertex-circle cross-check survivors -----------

def cyclic_shift(rows, s):
    """Apply the cyclic rotation that sends vertex i to vertex (i - s) mod 9
    (and updates the witness labels correspondingly)."""
    n = 9
    new_rows = [None] * n
    for i in range(n):
        new_rows[i] = sorted([(w - s) % n for w in rows[(i + s) % n]])
    return new_rows


def reflect_rows(rows):
    """Reflect: vertex i -> -i mod n, witnesses also negated."""
    n = 9
    new_rows = [None] * n
    for i in range(n):
        new_rows[i] = sorted([(-w) % n for w in rows[(-i) % n]])
    return new_rows


def is_222_compatible_at_offset(rows, s_off):
    """Test whether (p, q, r) = (s_off, s_off+3, s_off+6) gives the rigid
    (2, 2, 2) cap-occupancy:
        W_{s_off}     ⊇ {s_off+4, s_off+5}
        W_{s_off+3}   ⊇ {s_off+7, s_off+8}
        W_{s_off+6}   ⊇ {s_off+1, s_off+2}    (mod 9)
    """
    Wp_required = {(s_off + 4) % 9, (s_off + 5) % 9}
    Wq_required = {(s_off + 7) % 9, (s_off + 8) % 9}
    Wr_required = {(s_off + 1) % 9, (s_off + 2) % 9}
    Wp = set(rows[s_off % 9])
    Wq = set(rows[(s_off + 3) % 9])
    Wr = set(rows[(s_off + 6) % 9])
    return (
        Wp_required <= Wp
        and Wq_required <= Wq
        and Wr_required <= Wr
    )


def family_222_compatible(rows) -> list[dict[str, object]]:
    """Return all (rotation, reflection, s_offset) under which the family
    representative satisfies the (2, 2, 2) cap-occupancy.
    """
    found = []
    for ref in [False, True]:
        base = reflect_rows(rows) if ref else rows
        for s_rot in range(9):
            shifted = cyclic_shift(base, s_rot)
            for s_off in range(9):
                if is_222_compatible_at_offset(shifted, s_off):
                    found.append({
                        "reflect": ref,
                        "shift": s_rot,
                        "s_off": s_off,
                        "shifted_rows": shifted,
                    })
    return found


def cross_check_survivors(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"available": False, "path": str(path)}
    families = json.loads(path.read_text())
    out = []
    total_orbit = 0
    total_compatible_orbit = 0
    for fam in families:
        rows = fam["rows"]
        compat = family_222_compatible(rows)
        out.append({
            "family_id": fam["family_id"],
            "orbit_size": fam["orbit_size"],
            "status": fam["status"],
            "is_trivial_groebner": fam.get("is_trivial"),
            "is_zero_dim_groebner": fam.get("is_zero_dim"),
            "rows": rows,
            "(2,2,2)_compatible_witnesses": [
                {"reflect": c["reflect"], "shift": c["shift"], "s_off": c["s_off"]}
                for c in compat
            ],
            "(2,2,2)_compatible": len(compat) > 0,
        })
        total_orbit += fam["orbit_size"]
        if compat:
            total_compatible_orbit += fam["orbit_size"]
    return {
        "available": True,
        "path": str(path),
        "num_families": len(families),
        "total_orbit_size": total_orbit,
        "num_222_compatible_families": sum(
            1 for f in out if f["(2,2,2)_compatible"]
        ),
        "total_222_compatible_orbit": total_compatible_orbit,
        "families": out,
    }


# ----------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="write the JSON certificate")
    parser.add_argument("--out", default=str(DEFAULT_OUT),
                        help="path for --write")
    args = parser.parse_args()

    print("Stage (i): independent enumeration of (2,2,2) classes...")
    t0 = time.time()
    classes = enumerate_classes()
    t1 = time.time()
    print(f"  {len(classes)} canonical D_3 classes pass L4 + L5; "
          f"elapsed {t1 - t0:.3f}s")

    print("Stage (ii): cross-check against n=9 cross-check survivors...")
    t2 = time.time()
    cross = cross_check_survivors(N9_FAMILIES_PATH)
    t3 = time.time()
    if cross["available"]:
        print(f"  read {cross['num_families']} dihedral families, "
              f"orbit total {cross['total_orbit_size']} assignments; "
              f"elapsed {t3 - t2:.3f}s")
        print(f"  (2,2,2)-compatible families: "
              f"{cross['num_222_compatible_families']} / {cross['num_families']}")
        print(f"  (2,2,2)-compatible orbit total: "
              f"{cross['total_222_compatible_orbit']} / {cross['total_orbit_size']}")
    else:
        print(f"  cross-check artifact unavailable: {cross['path']}")

    summary = {
        "n": 9,
        "case": "three-cap rigid (2,2,2)",
        "type": "n9_three_cap_222_v1",
        "trust": "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
        "scope": (
            "Closes the rigid (2,2,2) cap-occupancy sub-case at n=9 of the "
            "three-cap SEC reduction (canonical-synthesis.md §5.4) under the "
            "cap-occupancy hypothesis. Does not promote the official/global "
            "FALSIFIABLE/OPEN status of Erdős #97."
        ),
        "notes": [
            "No general proof of Erdős #97 is claimed.",
            "No counterexample is claimed.",
            "Conditional on the cap-occupancy hypothesis "
            "(|W_p ∩ K_qr| >= 2 when p is an SEC support of a 4-bad polygon).",
        ],
        "stage_i_independent_enumeration": {
            "description": (
                "All 4-witness assignments for (W_p, W_q, W_r) compatible "
                "with the rigid (2,2,2) cap-occupancy, modulo D_3 on the "
                "(p, q, r) cycle, after L4 + L5 filtering."
            ),
            "total_classes_after_L4_L5_D3": len(classes),
            "classes": [
                {
                    "id": idx,
                    "W_p": cls["W_p_labels"],
                    "W_q": cls["W_q_labels"],
                    "W_r": cls["W_r_labels"],
                    "canonical_key": cls["canonical_key"],
                    "multiplicity": cls["multiplicity"],
                    "l6_diagnostic": cls["l6_diagnostic"],
                    "l4_check": cls["l4_check"],
                }
                for idx, cls in enumerate(classes)
            ],
        },
        "stage_ii_cross_check": cross,
    }

    if cross["available"]:
        if cross["num_222_compatible_families"] == 0:
            summary["conclusion"] = (
                "Conditional on the cap-occupancy hypothesis, the rigid "
                "(2,2,2) case at n=9 is closed: NO selected-witness "
                "assignment that survives the L4+L5+L6+pair-cap+indegree "
                "filters at n=9 (the 184 cross-check survivors / 16 dihedral "
                "families) admits a (p,q,r) cyclic placement compatible with "
                "the rigid (2,2,2) cap-occupancy."
            )
        else:
            summary["conclusion"] = (
                "Stage (ii) found compatible families; rigid (2,2,2) NOT "
                "closed at this layer."
            )

    if args.write:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, sort_keys=True))
        print(f"Wrote certificate: {out}")
    else:
        print(json.dumps(summary, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    sys.exit(main())
