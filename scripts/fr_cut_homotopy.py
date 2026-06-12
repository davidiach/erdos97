#!/usr/bin/env python3
"""Fishburn-Reeds cut-matrix mixed-radius homotopy diagnostic.

This is a numerical failed-route probe for Erdos Problem #97.  It records
floating-point homotopy diagnostics only; it does not certify a counterexample.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

# Fishburn--Reeds Table 1 (published as 1000*x_i, 1000*y_i).  A_i=(-x_i,y_i), B_i=(x_i,y_i).
FR_X = (
    np.array(
        [
            469.633821777,
            471.414237018,
            473.126180256,
            520.0,
            520.996246864,
            522.0,
            429.872125856,
            429.224646090,
            428.539574537,
            390.440922261,
        ]
    )
    / 1000.0
)
FR_Y = (
    np.array(
        [
            -92.982777730,
            -89.969229800,
            -87.048665472,
            30.0,
            33.0,
            36.1,
            342.595442083,
            344.599064292,
            346.658610393,
            417.185267785,
        ]
    )
    / 1000.0
)
EDGES = [
    (1, 6),
    (1, 9),
    (1, 10),
    (2, 5),
    (2, 8),
    (2, 10),
    (3, 4),
    (3, 7),
    (3, 10),
    (4, 3),
    (4, 8),
    (4, 9),
    (5, 2),
    (5, 7),
    (5, 9),
    (6, 1),
    (6, 7),
    (6, 8),
    (7, 3),
    (7, 5),
    (7, 6),
    (8, 2),
    (8, 4),
    (8, 6),
    (9, 1),
    (9, 4),
    (9, 5),
    (10, 1),
    (10, 2),
    (10, 3),
]


@dataclass
class Cfg:
    y_pad: float = 0.025
    common_w: float = 1.0
    conv_floor: float = 1e-8
    edge_floor: float = 1e-4
    pair_floor: float = 1e-4
    geom_w: float = 10.0
    gap_w: float = 2.0
    gap_floor_fraction: float = 0.003
    lr_tether: float = 1e-5
    seed_jitter: float = 0.0
    max_nfev_seed: int = 80
    max_nfev_corrector: int = 30
    initial_step: float = 0.05
    max_step: float = 0.10
    min_step: float = 0.001
    max_steps: int = 80
    exact_trigger_spread: float = 1e-10
    exact_trigger_margin: float = 1e-3


def mat():
    M = np.zeros((10, 10), bool)
    for i, j in EDGES:
        M[i - 1, j - 1] = True
    return M


def frD():
    D = np.zeros((10, 10))
    for i in range(10):
        for j in range(10):
            D[i, j] = math.sqrt((FR_X[i] + FR_X[j]) ** 2 + (FR_Y[j] - FR_Y[i]) ** 2)
    return D


def rows(augment="nearest"):
    M, D = mat(), frD()
    S3 = []
    S4 = []
    fourth = []
    for i in range(10):
        r = [10 + j for j in range(10) if M[i, j]]
        cand = [j for j in range(10) if not M[i, j]]
        j = (
            min(cand, key=lambda k: abs(D[i, k] - 1.0))
            if augment == "nearest"
            else cand[(i + 1) % len(cand)]
        )
        S3.append(r)
        S4.append(r + [10 + j])
        fourth.append(10 + j)
    for j in range(10):
        r = [i for i in range(10) if M[i, j]]
        cand = [i for i in range(10) if not M[i, j]]
        i = (
            min(cand, key=lambda k: abs(D[k, j] - 1.0))
            if augment == "nearest"
            else cand[(j + 1) % len(cand)]
        )
        S3.append(r)
        S4.append(r + [i])
        fourth.append(i)
    return S3, S4, fourth


def softmax(z):
    z = np.asarray(z, float)
    z = z - np.max(z)
    e = np.exp(z)
    return e / e.sum()


def hinge(y, scale=30.0):
    x = np.clip(scale * np.asarray(y, float), -60, 60)
    return np.log1p(np.exp(x)) / scale


def normP(P):
    Q = P - P.mean(axis=0, keepdims=True)
    rms = math.sqrt(float(np.mean(np.sum(Q * Q, axis=1))))
    return Q / rms


def order():
    return list(range(10)) + list(range(19, 9, -1))


def yends(cfg):
    return float(FR_Y[0] - cfg.y_pad), float(FR_Y[-1] + cfg.y_pad)


def gaps_logits(y, cfg):
    lo, hi = yends(cfg)
    g = np.diff(np.r_[lo, y, hi])
    return np.log(g / g.sum())


def unpack(x, cfg):
    zA, zB = x[:11], x[11:22]
    lwA, lwB = x[22:32], x[32:42]
    lr = x[42:62]
    lo, hi = yends(cfg)
    span = hi - lo
    gA, gB = softmax(zA) * span, softmax(zB) * span
    yA, yB = lo + np.cumsum(gA[:-1]), lo + np.cumsum(gB[:-1])
    wA, wB = np.exp(np.clip(lwA, -12, 4)), np.exp(np.clip(lwB, -12, 4))
    P = np.zeros((20, 2))
    P[:10, 0] = -wA
    P[:10, 1] = yA
    P[10:, 0] = wB
    P[10:, 1] = yB
    return (
        normP(P),
        np.exp(np.clip(lr, -20, 10)),
        dict(gA=gA, gB=gB, lr=lr, wA=wA, wB=wB, yA=yA, yB=yB),
    )


def init(seed, cfg, S3):
    rng = np.random.default_rng(seed)
    zA = gaps_logits(FR_Y, cfg) + rng.normal(0, cfg.seed_jitter, 11)
    zB = gaps_logits(FR_Y, cfg) + rng.normal(0, cfg.seed_jitter, 11)
    lwA = np.log(FR_X) + rng.normal(0, cfg.seed_jitter, 10)
    lwB = np.log(FR_X) + rng.normal(0, cfg.seed_jitter, 10)
    x = np.r_[zA, zB, lwA, lwB, np.zeros(20)]
    P, _, _ = unpack(x, cfg)
    R = np.array(
        [np.mean([np.sum((P[i] - P[j]) ** 2) for j in S3[i]]) for i in range(20)]
    )
    return np.r_[zA, zB, lwA, lwB, np.log(np.maximum(R, 1e-15))]


def area2(P, ordr):
    Q = P[ordr]
    return float(
        np.sum(Q[:, 0] * np.roll(Q[:, 1], -1) - Q[:, 1] * np.roll(Q[:, 0], -1))
    )


def margins(P, ordr):
    s = 1.0 if area2(P, ordr) >= 0 else -1.0
    vals = []
    tri = []
    for k, a in enumerate(ordr):
        b = ordr[(k + 1) % len(ordr)]
        e = P[b] - P[a]
        for c in ordr:
            if c == a or c == b:
                continue
            vals.append(
                s * float(e[0] * (P[c, 1] - P[a, 1]) - e[1] * (P[c, 0] - P[a, 0]))
            )
            tri.append((a, b, c))
    vals = np.array(vals)
    idx = int(np.argmin(vals))
    return vals, tri[idx]


def minedge(P, ordr):
    pairs = [
        (
            float(np.linalg.norm(P[ordr[k]] - P[ordr[(k + 1) % len(ordr)]])),
            (ordr[k], ordr[(k + 1) % len(ordr)]),
        )
        for k in range(len(ordr))
    ]
    return min(pairs, key=lambda z: z[0])


def minpair(P):
    pairs = [
        (float(np.linalg.norm(P[i] - P[j])), (i, j))
        for i in range(20)
        for j in range(i + 1, 20)
    ]
    return min(pairs, key=lambda z: z[0])


def eqstats(P, S):
    spreads = []
    rel = []
    centered = []
    for i, row in enumerate(S):
        d = np.array([np.sum((P[i] - P[j]) ** 2) for j in row])
        m = float(np.mean(d))
        sp = float(np.max(d) - np.min(d))
        spreads.append(sp)
        rel.append(sp / max(abs(m), 1e-15))
        centered += (d - m).tolist()
    centered = np.array(centered)
    return dict(
        max_spread=float(max(spreads)),
        max_relative_spread=float(max(rel)),
        rms_centered_residual=float(math.sqrt(float(np.mean(centered * centered)))),
    )


def rstats(P, R, S):
    v = np.array(
        [np.sum((P[i] - P[j]) ** 2) - R[i] for i, row in enumerate(S) for j in row]
    )
    return dict(
        max_abs=float(np.max(np.abs(v))), rms=float(math.sqrt(float(np.mean(v * v))))
    )


def diag(x, t, cfg, S3, S4):
    P, R, a = unpack(x, cfg)
    ordr = order()
    mg, tri = margins(P, ordr)
    me, mep = minedge(P, ordr)
    mp, mpp = minpair(P)
    A, B = P[:10], P[10:]
    return dict(
        t=float(t),
        convexity_margin=float(np.min(mg)),
        min_edge_length=float(me),
        min_pair_distance=float(mp),
        signed_area2_in_boundary_order=area2(P, ordr),
        active_convexity_edge_vertex=list(tri),
        active_min_edge=list(mep),
        active_min_pair=list(mpp),
        min_gap_A=float(np.min(a["gA"])),
        min_gap_B=float(np.min(a["gB"])),
        seed3_equal_distance=eqstats(P, S3),
        full4_equal_distance=eqstats(P, S4),
        seed3_radius_residual=rstats(P, R, S3),
        full4_radius_residual=rstats(P, R, S4),
        class_geometry=dict(
            A_x_range=[float(A[:, 0].min()), float(A[:, 0].max())],
            B_x_range=[float(B[:, 0].min()), float(B[:, 0].max())],
            cut_gap_min_B_x_minus_max_A_x=float(B[:, 0].min() - A[:, 0].max()),
            A_diameter=float(
                max(
                    np.linalg.norm(A[i] - A[j])
                    for i in range(10)
                    for j in range(i + 1, 10)
                )
            ),
            B_diameter=float(
                max(
                    np.linalg.norm(B[i] - B[j])
                    for i in range(10)
                    for j in range(i + 1, 10)
                )
            ),
        ),
    )


def residual(x, t, cfg, S3, S4):
    P, R, a = unpack(x, cfg)
    res = []
    for i, row in enumerate(S3):
        for j in row:
            res.append(float(np.sum((P[i] - P[j]) ** 2) - R[i]))
    if t > 0:
        w = math.sqrt(t)
        for i in range(20):
            res.append(w * float(np.sum((P[i] - P[S4[i][3]]) ** 2) - R[i]))
    if t < 1:
        lr = a["lr"]
        res += (cfg.common_w * math.sqrt(1 - t) * (lr - lr.mean())).tolist()
    res += (cfg.lr_tether * a["lr"]).tolist()
    ordr = order()
    mg, _ = margins(P, ordr)
    res += (cfg.geom_w * hinge(cfg.conv_floor - mg)).tolist()
    edges = np.array(
        [
            cfg.edge_floor - np.linalg.norm(P[ordr[k]] - P[ordr[(k + 1) % len(ordr)]])
            for k in range(len(ordr))
        ]
    )
    res += (cfg.geom_w * hinge(edges)).tolist()
    pairs = np.array(
        [
            cfg.pair_floor - np.linalg.norm(P[i] - P[j])
            for i in range(20)
            for j in range(i + 1, 20)
        ]
    )
    res += (cfg.geom_w * hinge(pairs)).tolist()
    lo, hi = yends(cfg)
    gf = cfg.gap_floor_fraction * (hi - lo) / 11.0
    res += (cfg.gap_w * hinge(gf - a["gA"])).tolist()
    res += (cfg.gap_w * hinge(gf - a["gB"])).tolist()
    return np.array(res, float)


def solve(x, t, cfg, S3, S4, seed_stage=False):
    return least_squares(
        lambda y: residual(y, t, cfg, S3, S4),
        x,
        method="lm",
        max_nfev=cfg.max_nfev_seed if seed_stage else cfg.max_nfev_corrector,
        ftol=1e-11,
        xtol=1e-11,
        gtol=1e-11,
    )


def accept(d, cfg):
    if d["convexity_margin"] <= 0:
        return False, "convexity_collapse"
    if d["min_edge_length"] <= 1e-10:
        return False, "edge_collapse"
    if d["min_pair_distance"] <= 1e-10:
        return False, "pair_collision"
    return True, "geometry_ok"


def path(seed, cfg, S3, S4):
    x = init(seed, cfg, S3)
    t = 0.0
    h = cfg.initial_step
    acc = [
        dict(
            step_index=0,
            diagnostics=diag(x, 0, cfg, S3, S4),
            solver=dict(
                stage="published_FR_table_no_t0_corrector",
                success=True,
                nfev=0,
                cost=float(np.sum(residual(x, 0, cfg, S3, S4) ** 2) / 2.0),
                message="t=0 is the Fishburn-Reeds coordinate-table seed; no geometry-improving correction applied",
            ),
        )
    ]
    rej = []
    term = "running"
    step = 0
    while t < 1 - 1e-14 and step < cfg.max_steps:
        target = min(1.0, t + h)
        print(
            f"[FR-cut] seed={seed} target={target:.6f} h={h:.2e}",
            file=sys.stderr,
            flush=True,
        )
        sol = solve(x, target, cfg, S3, S4, False)
        d = diag(sol.x, target, cfg, S3, S4)
        ok, why = accept(d, cfg)
        if ok and np.isfinite(sol.cost):
            step += 1
            acc.append(
                dict(
                    step_index=step,
                    diagnostics=d,
                    solver=dict(
                        success=bool(sol.success),
                        status=int(sol.status),
                        message=str(sol.message),
                        nfev=int(sol.nfev),
                        cost=float(sol.cost),
                        optimality=float(sol.optimality),
                        incoming_step=float(h),
                    ),
                )
            )
            x = sol.x.copy()
            t = target
            h = (
                max(cfg.min_step, 0.5 * h)
                if d["convexity_margin"] < 10 * cfg.conv_floor
                else min(
                    cfg.max_step,
                    h if sol.nfev >= 0.4 * cfg.max_nfev_corrector else 1.25 * h,
                )
            )
            term = "reached_t1" if t >= 1 - 1e-14 else "running"
        else:
            rej.append(
                dict(
                    from_t=float(t),
                    target_t=float(target),
                    incoming_step=float(h),
                    reason=why,
                    solver_success=bool(sol.success),
                    solver_status=int(sol.status),
                    solver_message=str(sol.message),
                    diagnostics=d,
                )
            )
            h *= 0.5
            if h < cfg.min_step:
                term = why
                break
    if step >= cfg.max_steps and term == "running":
        term = "max_steps_reached"
    f = acc[-1]["diagnostics"]
    return dict(
        path_seed=seed,
        termination_reason=term,
        accepted_points=acc,
        rejected_points=rej,
        final_t=float(f["t"]),
        final_geometry_first_diagnostics={
            k: f[k]
            for k in [
                "convexity_margin",
                "min_edge_length",
                "min_pair_distance",
                "active_convexity_edge_vertex",
                "active_min_edge",
                "active_min_pair",
            ]
        },
        final_residual_diagnostics=dict(
            seed3_equal_distance=f["seed3_equal_distance"],
            full4_equal_distance=f["full4_equal_distance"],
            seed3_radius_residual=f["seed3_radius_residual"],
            full4_radius_residual=f["full4_radius_residual"],
        ),
        final_x=x.tolist(),
    )


def summary(paths):
    pts = [
        (p["path_seed"], pt["diagnostics"])
        for p in paths
        for pt in p["accepted_points"]
    ]
    best = min(pts, key=lambda z: z[1]["full4_equal_distance"]["rms_centered_residual"])
    deep = max(paths, key=lambda p: p["final_t"])
    collapses = [
        p
        for p in paths
        if p["termination_reason"]
        in {"convexity_collapse", "edge_collapse", "pair_collision"}
    ]
    return dict(
        num_paths=len(paths),
        num_paths_reached_t1=sum(
            p["termination_reason"] == "reached_t1" for p in paths
        ),
        num_paths_geometry_collapse=len(collapses),
        all_terminated_by_geometry_collapse=len(collapses) == len(paths),
        best_full4_rms_point=dict(
            path_seed=best[0],
            t=best[1]["t"],
            full4_rms_centered_residual=best[1]["full4_equal_distance"][
                "rms_centered_residual"
            ],
            full4_max_spread=best[1]["full4_equal_distance"]["max_spread"],
            convexity_margin=best[1]["convexity_margin"],
            min_edge_length=best[1]["min_edge_length"],
        ),
        deepest_path=dict(
            path_seed=deep["path_seed"],
            final_t=deep["final_t"],
            termination_reason=deep["termination_reason"],
            final_convexity_margin=deep["final_geometry_first_diagnostics"][
                "convexity_margin"
            ],
            final_full4_rms_centered_residual=deep["final_residual_diagnostics"][
                "full4_equal_distance"
            ]["rms_centered_residual"],
        ),
    )


def exactification_trigger_points(paths, cfg):
    triggered = []
    for path_record in paths:
        for point in path_record["accepted_points"]:
            diagnostics = point["diagnostics"]
            if (
                diagnostics["full4_equal_distance"]["max_spread"]
                < cfg.exact_trigger_spread
                and diagnostics["convexity_margin"] > cfg.exact_trigger_margin
                and diagnostics["min_edge_length"] > cfg.exact_trigger_margin
                and diagnostics["min_pair_distance"] > cfg.exact_trigger_margin
            ):
                triggered.append(
                    {
                        "path_seed": path_record["path_seed"],
                        "step_index": point["step_index"],
                        "t": diagnostics["t"],
                        "full4_max_spread": diagnostics["full4_equal_distance"][
                            "max_spread"
                        ],
                        "convexity_margin": diagnostics["convexity_margin"],
                        "min_edge_length": diagnostics["min_edge_length"],
                        "min_pair_distance": diagnostics["min_pair_distance"],
                    }
                )
    return triggered


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-dir", default=".")
    ap.add_argument("--seed", type=int, default=97120)
    ap.add_argument("--paths", type=int, default=3)
    ap.add_argument("--augment", choices=["nearest", "cyclic_next"], default="nearest")
    ap.add_argument("--max-nfev-seed", type=int)
    ap.add_argument("--max-nfev-corrector", type=int)
    ap.add_argument("--initial-step", type=float)
    ap.add_argument("--max-step", type=float)
    ap.add_argument("--min-step", type=float)
    ap.add_argument("--max-steps", type=int)
    ap.add_argument("--geom-w", type=float)
    ap.add_argument("--out")
    a = ap.parse_args()
    cfg = Cfg()
    for k, v in [
        ("max_nfev_seed", a.max_nfev_seed),
        ("max_nfev_corrector", a.max_nfev_corrector),
        ("initial_step", a.initial_step),
        ("max_step", a.max_step),
        ("min_step", a.min_step),
        ("max_steps", a.max_steps),
        ("geom_w", a.geom_w),
    ]:
        if v is not None:
            setattr(cfg, k, v)
    repo = Path(a.repo_dir).resolve()
    outdir = repo / "data" / "runs"
    outdir.mkdir(parents=True, exist_ok=True)
    S3, S4, fourth = rows(a.augment)
    paths = []
    for p in range(a.paths):
        seed = a.seed + 1009 * p
        print(f"[FR-cut] path {p} seed={seed}", file=sys.stderr, flush=True)
        paths.append(path(seed, cfg, S3, S4))
        print(
            f"[FR-cut] done {p} final_t={paths[-1]['final_t']:.4f} term={paths[-1]['termination_reason']}",
            file=sys.stderr,
            flush=True,
        )
    sm = summary(paths)
    label = (
        "FAILED_APPROACH"
        if sm["all_terminated_by_geometry_collapse"]
        else "NUMERICAL_EVIDENCE"
    )
    exact_triggers = exactification_trigger_points(paths, cfg)
    artifact = dict(
        schema="erdos97.numerical_run.v1",
        trust_label=label,
        pattern_name=f"FR20_cut_matrix_{a.augment}4_mixed_radius_cut_arc_homotopy",
        seed=a.seed,
        fishburn_reeds_seed=dict(
            coordinate_table_scaled_by=0.001,
            A_i="(-x_i,y_i), labels 0..9",
            B_i="(x_i,y_i), labels 10..19",
            boundary_order=order(),
            seed_matrix_edges_1_indexed=EDGES,
        ),
        fourth_witness_rule=a.augment,
        fourth_witnesses_by_center_label=fourth,
        S3=S3,
        S4=S4,
        homotopy=dict(
            t0="Fishburn--Reeds 3-neighbor cut matrix with soft common-radius tie",
            t1="same rows plus closest non-edge fourth witness; per-center radii independent",
            step_control=dict(
                predictor="previous corrected point",
                corrector="scipy.optimize.least_squares(method='lm')",
                acceptance_order="convexity margin, min edge, min pair checked before residual",
                initial_step=cfg.initial_step,
                max_step=cfg.max_step,
                min_step=cfg.min_step,
                reject_action="halve step; terminate below min_step",
            ),
        ),
        config=asdict(cfg),
        paths=paths,
        summary=sm,
        exactification_trigger=dict(
            max_selected_distance_spread=cfg.exact_trigger_spread,
            convexity_margin=cfg.exact_trigger_margin,
            min_edge_length=cfg.exact_trigger_margin,
            min_pair_distance=cfg.exact_trigger_margin,
            source="docs/exactification-plan.md",
        ),
        exact_verifier_triggered=bool(exact_triggers),
        exact_verifier_results=[],
        exactification_trigger_points=exact_triggers,
        interpretation=dict(
            label=label,
            text="No counterexample candidate is claimed; floating-point equalities are diagnostics only.",
        ),
        environment=dict(
            python=sys.version,
            numpy=np.__version__,
            scipy=sys.modules["scipy"].__version__,
            created_utc=datetime.now(timezone.utc).isoformat(),
        ),
    )
    out = (
        Path(a.out)
        if a.out
        else outdir
        / f"FR20_cutmatrix_{a.augment}4_mixed_radius_homotopy_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_seed{a.seed}.json"
    )
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print(out)
    print(json.dumps(sm, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
