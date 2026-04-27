"""Pattern-level obstruction lemmas.

This module formalizes lower bounds on the equality residual ``r`` of selected
incidence patterns whose only zero-residual limits are non-strictly-convex
degenerations.  It complements :mod:`erdos97.incidence_filters` (purely
combinatorial obstructions) by providing a quantitative analytic obstruction
that is checkable on any candidate JSON.

Currently implemented:

* :class:`ThreeFoldClusterObstruction` for ``B12_3x4_danzer_lift``.

The lemma underlying ``ThreeFoldClusterObstruction`` is documented in
``docs/lemmas/no_3fold_cluster_obstruction.md``.  The constants stored here
are the analytic exponent and an empirically calibrated lower-bound
coefficient, with the empirical sweep recorded in
``data/obstructions/three_fold_cluster_runs.json``.

The diagnostics use the same definitions as :mod:`erdos97.search`:

* ``r``      = RMS equality residual over the centered selected squared
  distances (``independent_diagnostics``'s ``eq_rms`` field);
* ``gamma``  = strict convexity margin (``convexity_margin``);
* ``rho``    = minimum intra-cluster pairwise distance, where the cluster
  decomposition is the canonical ``B12_3x4`` block partition
  ``{0..3}, {4..7}, {8..11}``.

This module is intentionally narrow: it only handles the documented pattern.
Generalizations belong in follow-up issues.
"""
from __future__ import annotations

import dataclasses
import json
import math
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
from numpy.typing import NDArray

from erdos97.search import (
    convexity_margin,
    independent_diagnostics,
    normalize_points,
    pairwise_distances,
)

Array = NDArray[np.float64]


# --------------------------------------------------------------------------
# B12_3x4_danzer_lift cluster decomposition
# --------------------------------------------------------------------------

#: Canonical block-(3,4) cluster partition of the 12 vertex labels.
B12_3x4_CLUSTERS: Tuple[Tuple[int, int, int, int], ...] = (
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (8, 9, 10, 11),
)


def _block_clusters(n: int, m: int, q: int) -> Tuple[Tuple[int, ...], ...]:
    if n != m * q:
        raise ValueError(f"block partition requires n == m*q, got {n}, {m}, {q}")
    return tuple(tuple(a * q + b for b in range(q)) for a in range(m))


def cluster_partition(pattern_id: str, n: int) -> Tuple[Tuple[int, ...], ...]:
    """Return the canonical cluster partition for ``pattern_id``.

    Currently only ``B12_3x4_danzer_lift`` is supported.  Other patterns
    raise ``KeyError``; this is intentional, see the module docstring.
    """
    if pattern_id == "B12_3x4_danzer_lift":
        if n != 12:
            raise ValueError(f"B12_3x4_danzer_lift requires n=12, got n={n}")
        return _block_clusters(12, 3, 4)
    raise KeyError(f"no cluster partition registered for pattern {pattern_id!r}")


def min_intra_cluster_distance(P: Array, clusters: Sequence[Sequence[int]]) -> float:
    """Minimum Euclidean distance between two points in the same cluster."""
    P = np.asarray(P, dtype=float)
    best = math.inf
    for cl in clusters:
        idx = list(cl)
        if len(idx) < 2:
            continue
        Pc = P[idx]
        D = pairwise_distances(Pc)
        iu = np.triu_indices(len(idx), 1)
        local = float(np.min(D[iu]))
        if local < best:
            best = local
    return float(best)


def cluster_orientation_angle(P: Array, clusters: Sequence[Sequence[int]]) -> float:
    """Mean angle, in radians, between each cluster's principal tangent and
    the line from that cluster's centroid to the triangle centroid.

    Returns a value in ``[0, pi/2]``.  ``0`` means tangents are radial
    (the orthogonal regime in the lemma), ``pi/2`` means tangents are
    perpendicular to the radial direction (the generic regime).
    """
    P = np.asarray(P, dtype=float)
    centroids = np.array([P[list(cl)].mean(axis=0) for cl in clusters])
    triangle_centroid = centroids.mean(axis=0)
    angles = []
    for k, cl in enumerate(clusters):
        Pc = P[list(cl)] - centroids[k]
        # Cluster spans a degenerate or near-degenerate 1D arc; the principal
        # right-singular vector is the cluster's tangent direction.
        _, _, vh = np.linalg.svd(Pc, full_matrices=False)
        tangent = vh[0]
        radial = centroids[k] - triangle_centroid
        nr = float(np.linalg.norm(radial))
        if nr <= 0.0:
            continue
        radial_unit = radial / nr
        cos_abs = abs(float(np.dot(tangent, radial_unit)))
        cos_abs = min(1.0, max(0.0, cos_abs))
        angles.append(math.acos(cos_abs))
    if not angles:
        return float("nan")
    return float(np.mean(angles))


# --------------------------------------------------------------------------
# Obstruction class and report
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ThreeFoldClusterObstruction:
    """Analytic lower bound ``r >= C1 * gamma^alpha`` for 3-fold cluster
    selected patterns whose only zero-residual limit is the equilateral
    3-cluster collapse.

    Attributes
    ----------
    alpha:
        Analytic exponent in the lower bound.  ``1/3`` in the generic
        cluster orientation, ``2/3`` in the (degenerate) orthogonal
        orientation.
    C1:
        Lower-bound coefficient.  Empirically calibrated so that
        ``r >= C1 * gamma^alpha`` holds across the SLSQP restart sweep
        recorded in ``data/obstructions/three_fold_cluster_runs.json``,
        with a safety factor.
    applicable_patterns:
        Tuple of pattern names this obstruction applies to.
    regime:
        Human-readable label of the orientation regime.
    """

    alpha: float
    C1: float
    applicable_patterns: Tuple[str, ...]
    regime: str

    def predicted_lower_bound(self, gamma: float) -> float:
        if gamma <= 0.0:
            return 0.0
        return float(self.C1 * (gamma ** self.alpha))

    def applies_to(self, pattern_id: str) -> bool:
        return pattern_id in self.applicable_patterns


# Default obstruction: generic-regime (alpha=1/3) lower bound for the
# B12_3x4_danzer_lift pattern.  The coefficient ``C1`` is set conservatively
# below the smallest empirically observed ratio ``r / gamma^(1/3)`` in the
# sweep; it is a safe lower-bound constant, not a tight fit.
DEFAULT_THREEFOLD_OBSTRUCTION = ThreeFoldClusterObstruction(
    alpha=1.0 / 3.0,
    C1=0.05,
    applicable_patterns=("B12_3x4_danzer_lift",),
    regime="generic",
)


@dataclasses.dataclass
class ObstructionReport:
    """Per-config obstruction check."""

    pattern_id: str
    gamma: float
    r: float
    rho: float
    cluster_orientation_angle: float
    alpha: float
    C1: float
    predicted_lower_bound: float
    holds: bool
    slack: float

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _load_config(config_json_path: Path) -> Tuple[Array, List[List[int]], Optional[str]]:
    with open(config_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    P = np.array(data["coordinates"], dtype=float)
    S = [[int(j) for j in row] for row in data["S"]]
    pat = data.get("pattern_name") or data.get("pattern")
    return P, S, pat


def verify_obstruction(
    config_json_path: Path,
    pattern_id: str,
    obstruction: ThreeFoldClusterObstruction = DEFAULT_THREEFOLD_OBSTRUCTION,
) -> ObstructionReport:
    """Load a saved candidate config and check the analytic lower bound.

    Notes
    -----
    The convexity margin in this repo (see :func:`erdos97.search.convexity_margin`)
    is the minimum signed-area cross product over every directed boundary
    edge and every non-incident vertex.  For a strictly convex polygon it is
    positive.  ``r`` is the RMS of the centered selected squared distances,
    matching ``independent_diagnostics``'s ``eq_rms`` field.
    """
    if not obstruction.applies_to(pattern_id):
        raise ValueError(
            f"obstruction {obstruction!r} does not apply to pattern {pattern_id!r}"
        )

    P, S, _stored = _load_config(Path(config_json_path))
    # We do not normalize; the lemma is scale invariant in r and gamma but the
    # ratio r / gamma^alpha is not, so we report the values as stored to
    # match the saved diagnostics.
    diag = independent_diagnostics(P, S)
    gamma = float(diag["convexity_margin"])
    r = float(diag["eq_rms"])
    clusters = cluster_partition(pattern_id, len(P))
    rho = min_intra_cluster_distance(P, clusters)
    angle = cluster_orientation_angle(P, clusters)

    bound = obstruction.predicted_lower_bound(gamma)
    holds = bool(r >= bound)
    slack = float(r - bound)

    return ObstructionReport(
        pattern_id=pattern_id,
        gamma=gamma,
        r=r,
        rho=rho,
        cluster_orientation_angle=angle,
        alpha=obstruction.alpha,
        C1=obstruction.C1,
        predicted_lower_bound=bound,
        holds=holds,
        slack=slack,
    )


# --------------------------------------------------------------------------
# Empirical fit
# --------------------------------------------------------------------------


@dataclasses.dataclass
class FitResult:
    """Linear fit of ``log r`` against ``log gamma``."""

    n_points: int
    slope: float
    intercept: float
    r_squared: float
    log_gamma: List[float]
    log_r: List[float]

    @property
    def alpha_estimate(self) -> float:
        return self.slope

    @property
    def C1_estimate(self) -> float:
        return float(math.exp(self.intercept))

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["alpha_estimate"] = self.alpha_estimate
        d["C1_estimate"] = self.C1_estimate
        return d


def _read_one_run(path: Path) -> Optional[Tuple[float, float]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    g = data.get("convexity_margin")
    r = data.get("eq_rms")
    if g is None or r is None:
        return None
    g = float(g)
    r = float(r)
    if g <= 0.0 or r <= 0.0:
        return None
    return g, r


def fit_obstruction_constants(runs: Iterable[Path]) -> FitResult:
    """Least-squares fit of ``log r = alpha * log gamma + beta``.

    Inputs are paths to JSON config artifacts containing scalar fields
    ``convexity_margin`` and ``eq_rms``.  Records with non-positive values
    are skipped.
    """
    log_g: List[float] = []
    log_r: List[float] = []
    for p in runs:
        rec = _read_one_run(Path(p))
        if rec is None:
            continue
        g, r = rec
        log_g.append(math.log(g))
        log_r.append(math.log(r))
    if len(log_g) < 2:
        raise ValueError("need at least two valid (gamma, r) pairs to fit")
    x = np.array(log_g, dtype=float)
    y = np.array(log_r, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    yhat = slope * x + intercept
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0.0 else 1.0
    return FitResult(
        n_points=len(log_g),
        slope=float(slope),
        intercept=float(intercept),
        r_squared=float(r_squared),
        log_gamma=log_g,
        log_r=log_r,
    )


__all__ = [
    "B12_3x4_CLUSTERS",
    "ThreeFoldClusterObstruction",
    "DEFAULT_THREEFOLD_OBSTRUCTION",
    "ObstructionReport",
    "FitResult",
    "cluster_partition",
    "cluster_orientation_angle",
    "min_intra_cluster_distance",
    "verify_obstruction",
    "fit_obstruction_constants",
]
