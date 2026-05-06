"""Gröbner basis attack on Erdős #97 at n = 10.

For each pre-vertex-circle survivor of the n = 10 selected-witness search
(use_vertex_circle=False in :class:`erdos97.generic_vertex_search.GenericVertexSearch`),
we encode the pattern as a polynomial system over QQ:

  * Coordinates ``(x_0, y_0, ..., x_9, y_9) in Q^{20}``.
  * Gauge: ``x_0 = y_0 = y_1 = 0``, ``x_1 = 1``.
  * For each row ``i`` with selected witnesses ``{a, b, c, d}`` (cyclic order),
    three independent equations
    ``|p_i - p_a|^2 = |p_i - p_b|^2 = |p_i - p_c|^2 = |p_i - p_d|^2``.

This gives 30 polynomial equations in 16 free variables. We compute a grevlex
Gröbner basis with sympy and time-box each computation. A trivial basis ``{1}``
proves the pattern is unrealizable in the Euclidean plane. For nontrivial
bases we attempt to extract a univariate elimination polynomial in one of
``y_8, y_9, x_8, x_9`` and check whether real roots exist.

Survivor enumeration is itself slow at n = 10 (the row0=0 slice alone has
~52K nodes and yields ~160 pre-vertex-circle survivors in ~60 s of pure
Python). The script:

  1. Walks row0 choices in order, collecting all pre-vertex-circle survivors.
  2. Stops once SURVIVOR_CAP patterns have been collected or the wall-clock
     budget for collection (COLLECT_BUDGET_SEC) is exhausted.
  3. If more survivors were collected than SAMPLE_SIZE, samples
     SAMPLE_SIZE of them uniformly (deterministic seed) for the GB pass.

The output JSON lists every pattern attempted, with verdicts:

  * ``GB_TRIVIAL``      - GB = {1}, no complex solutions, unrealizable.
  * ``GB_NO_REAL``      - GB nontrivial, but a univariate elimination
    polynomial has no real roots; unrealizable.
  * ``GB_NONTRIVIAL``   - GB nontrivial; either we did not find a
    univariate elimination polynomial in the chosen variables or it does have
    real roots. Decoder follow-up needed.
  * ``GB_TIMEOUT``      - GB computation exceeded the per-pattern budget.
  * ``GB_ERROR``        - sympy raised an unexpected exception.
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from erdos97.generic_vertex_search import GenericVertexSearch  # noqa: E402

import sympy as sp  # noqa: E402
from sympy import Symbol, S, expand, groebner  # noqa: E402
from sympy.polys.orderings import grevlex  # noqa: E402

N = 10
ROW_SIZE = 4
DEFAULT_COLLECT_BUDGET_SEC = 1500.0
DEFAULT_SURVIVOR_CAP = 400
DEFAULT_SAMPLE_SIZE = 100
DEFAULT_GB_TIMEOUT_SEC = 60
DEFAULT_REAL_ROOT_TIMEOUT_SEC = 30
DEFAULT_RANDOM_SEED = 20260506


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds: int):
    if seconds is None or seconds <= 0:
        yield
        return

    def handler(signum, frame):
        raise TimeoutException()

    old_handler = signal.signal(signal.SIGALRM, handler)
    signal.alarm(int(seconds))
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def mask_to_witnesses(mask: int, n: int) -> list[int]:
    return [i for i in range(n) if (mask >> i) & 1]


def cyclic_order(center: int, witnesses: list[int], n: int) -> list[int]:
    return sorted(witnesses, key=lambda w: (w - center) % n)


def build_system(rows: list[list[int]], n: int) -> tuple[list[Symbol], list[sp.Expr]]:
    """Build the polynomial system for one pattern.

    rows[i] is the cyclic-order list of 4 witnesses for vertex i.
    Returns (free_vars, polynomials) after applying the gauge.
    """
    xs = [Symbol(f"x{i}") for i in range(n)]
    ys = [Symbol(f"y{i}") for i in range(n)]
    subs = {xs[0]: S.Zero, ys[0]: S.Zero, ys[1]: S.Zero, xs[1]: S.One}

    def D(i: int, j: int) -> sp.Expr:
        return (xs[i] - xs[j]) ** 2 + (ys[i] - ys[j]) ** 2

    polys: list[sp.Expr] = []
    for i, witnesses in enumerate(rows):
        if len(witnesses) != ROW_SIZE:
            raise ValueError(f"row {i} has {len(witnesses)} witnesses, expected {ROW_SIZE}")
        a, b, c, d = witnesses
        polys.append(expand(D(i, a) - D(i, b)).subs(subs))
        polys.append(expand(D(i, b) - D(i, c)).subs(subs))
        polys.append(expand(D(i, c) - D(i, d)).subs(subs))

    polys = [p for p in polys if p != 0]
    seen: set[str] = set()
    unique_polys: list[sp.Expr] = []
    for p in polys:
        key = sp.srepr(p)
        if key not in seen:
            seen.add(key)
            unique_polys.append(p)

    free = [xs[i] for i in range(2, n)] + [ys[i] for i in range(2, n)]
    return free, unique_polys


def find_univariate_in_basis(
    basis: list[sp.Expr],
    free: list[Symbol],
    preferred: list[Symbol] | None = None,
) -> tuple[Symbol | None, sp.Expr | None]:
    """Look for an element of the basis that is a univariate polynomial in a single variable.

    Returns (variable, polynomial) or (None, None) if none is found.
    Tries the preferred variables first.
    """
    candidates = list(preferred or [])
    seen_set = set(candidates)
    for v in free:
        if v not in seen_set:
            candidates.append(v)

    for var in candidates:
        for poly in basis:
            free_syms = poly.free_symbols
            if free_syms == {var}:
                return var, poly
    return None, None


def real_roots_count(poly: sp.Expr, var: Symbol, timeout: int) -> tuple[int | None, str]:
    """Return number of distinct real roots, or None if timed out / errored."""
    try:
        with time_limit(timeout):
            poly_obj = sp.Poly(poly, var)
            if poly_obj.is_zero:
                return None, "zero polynomial"
            roots = sp.real_roots(poly_obj)
            return len(roots), "ok"
    except TimeoutException:
        return None, "timeout"
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def attempt_groebner(
    rows: list[list[int]],
    n: int,
    timeout_sec: int,
    real_root_timeout_sec: int,
) -> dict[str, Any]:
    free, polys = build_system(rows, n)
    info: dict[str, Any] = {
        "num_polys": len(polys),
        "num_free_vars": len(free),
    }
    t0 = time.time()
    try:
        with time_limit(timeout_sec):
            G = groebner(polys, *free, order=grevlex, domain="QQ")
        elapsed = time.time() - t0
        basis = list(G)
        info["gb_time_sec"] = elapsed
        info["gb_size"] = len(basis)
        info["is_trivial"] = (len(basis) == 1 and basis[0] == 1)
        info["basis_repr_head"] = [str(p) for p in basis[:6]]
        if info["is_trivial"]:
            info["verdict"] = "GB_TRIVIAL"
            return info

        xs = [Symbol(f"x{i}") for i in range(n)]
        ys = [Symbol(f"y{i}") for i in range(n)]
        preferred = [ys[n - 1], ys[n - 2], xs[n - 1], xs[n - 2]]
        preferred = [v for v in preferred if v in free]
        var, uni_poly = find_univariate_in_basis(basis, free, preferred)
        if uni_poly is not None and var is not None:
            info["univariate_var"] = str(var)
            info["univariate_poly"] = str(uni_poly)
            num_real, status = real_roots_count(uni_poly, var, real_root_timeout_sec)
            info["univariate_real_status"] = status
            info["univariate_real_root_count"] = num_real
            if status == "ok" and num_real == 0:
                info["verdict"] = "GB_NO_REAL"
            else:
                info["verdict"] = "GB_NONTRIVIAL"
        else:
            info["verdict"] = "GB_NONTRIVIAL"
        return info
    except TimeoutException:
        info["gb_time_sec"] = time.time() - t0
        info["verdict"] = "GB_TIMEOUT"
        return info
    except Exception as exc:
        info["gb_time_sec"] = time.time() - t0
        info["verdict"] = "GB_ERROR"
        info["error"] = f"{type(exc).__name__}: {exc}"
        return info


def collect_survivors(
    n: int,
    survivor_cap: int,
    budget_sec: float,
    per_row0_cap: int | None = None,
    progress: bool = True,
) -> tuple[list[list[list[int]]], dict[str, Any]]:
    """Walk row0 choices and gather all pre-vertex-circle full assignments,
    capped by ``survivor_cap`` and a wall-clock ``budget_sec`` budget.

    If ``per_row0_cap`` is set, stop collection within a single row0 slice
    after that many survivors so the global sample sees more row0 diversity.

    Returns (patterns, meta) where each pattern is a list of cyclic-order
    witness lists (one list per row).
    """
    search = GenericVertexSearch(n)
    row0_count = search.row0_choice_count
    patterns: list[list[list[int]]] = []
    meta: dict[str, Any] = {
        "n": n,
        "row0_count": row0_count,
        "survivor_cap": survivor_cap,
        "budget_sec": budget_sec,
        "per_row0_cap": per_row0_cap,
        "row0_processed": 0,
        "row0_total_nodes": 0,
        "row0_truncated": False,
        "row0_done": False,
    }

    target = survivor_cap

    def collect_for_row0(row0_index: int, row0: int) -> int:

        n_local = search.n
        mask_bits = search.mask_bits
        row_pair_indices = search.row_pair_indices

        nodes = 0
        slice_initial = len(patterns)

        def search_fn(
            assign: dict[int, int],
            column_counts: list[int],
            witness_pair_counts: list[int],
        ) -> bool:
            """Returns True if survivor cap reached."""
            nonlocal nodes
            nodes += 1
            if len(assign) == n_local:
                witnesses = []
                for i in range(n_local):
                    raw = mask_to_witnesses(assign[i], n_local)
                    raw = cyclic_order(i, raw, n_local)
                    witnesses.append(raw)
                patterns.append(witnesses)
                if per_row0_cap is not None and (
                    len(patterns) - slice_initial >= per_row0_cap
                ):
                    return True
                return len(patterns) >= target

            best_center = None
            best_options = None
            for center in range(n_local):
                if center in assign:
                    continue
                opts = search.valid_options_for_center(
                    center, assign, column_counts, witness_pair_counts
                )
                if best_options is None or len(opts) < len(best_options):
                    best_center = center
                    best_options = opts
                    if not opts:
                        break
            if not best_options:
                return False

            center = best_center
            assert center is not None
            for mask in best_options:
                assign[center] = mask
                for target_idx in mask_bits[mask]:
                    column_counts[target_idx] += 1
                for pidx in row_pair_indices[mask]:
                    witness_pair_counts[pidx] += 1
                if search_fn(assign, column_counts, witness_pair_counts):
                    return True
                for pidx in row_pair_indices[mask]:
                    witness_pair_counts[pidx] -= 1
                for target_idx in mask_bits[mask]:
                    column_counts[target_idx] -= 1
                del assign[center]
            return False

        assign = {0: row0}
        column_counts = [0] * n_local
        witness_pair_counts = [0] * len(search.pairs)
        for target_idx in mask_bits[row0]:
            column_counts[target_idx] += 1
        for pidx in row_pair_indices[row0]:
            witness_pair_counts[pidx] += 1
        search_fn(assign, column_counts, witness_pair_counts)
        return nodes

    t_start = time.time()
    for row0_index in range(row0_count):
        if time.time() - t_start > budget_sec:
            meta["row0_truncated"] = True
            break
        row0 = search.options[0][row0_index]
        before = len(patterns)
        nodes = collect_for_row0(row0_index, row0)
        meta["row0_processed"] = row0_index + 1
        meta["row0_total_nodes"] += nodes
        gained = len(patterns) - before
        if progress:
            elapsed = time.time() - t_start
            print(
                f"  row0={row0_index:3d}: +{gained:3d} survivors "
                f"(total={len(patterns):4d}/{survivor_cap}), "
                f"nodes={nodes:6d}, elapsed={elapsed:7.1f}s",
                flush=True,
            )
        if len(patterns) >= survivor_cap:
            break
    else:
        meta["row0_done"] = True

    meta["collect_elapsed_sec"] = time.time() - t_start
    meta["survivors_collected"] = len(patterns)
    return patterns, meta


def main() -> int:
    parser = argparse.ArgumentParser(description="n=10 Gröbner basis attack")
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "data" / "certificates" / "n10_groebner_results.json",
    )
    parser.add_argument(
        "--collect-budget-sec",
        type=float,
        default=DEFAULT_COLLECT_BUDGET_SEC,
        help="Wall-clock budget for collecting pre-vertex-circle survivors",
    )
    parser.add_argument(
        "--survivor-cap",
        type=int,
        default=DEFAULT_SURVIVOR_CAP,
        help="Stop collecting after this many survivors",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help="If more survivors collected, sample down to this many",
    )
    parser.add_argument(
        "--gb-timeout-sec",
        type=int,
        default=DEFAULT_GB_TIMEOUT_SEC,
    )
    parser.add_argument(
        "--real-root-timeout-sec",
        type=int,
        default=DEFAULT_REAL_ROOT_TIMEOUT_SEC,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_RANDOM_SEED,
    )
    parser.add_argument(
        "--row0-limit",
        type=int,
        default=None,
        help="Limit number of row0 choices to process (for fast testing)",
    )
    parser.add_argument(
        "--per-row0-cap",
        type=int,
        default=None,
        help="Cap number of survivors per row0 slice for diversity",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
    )
    parser.add_argument(
        "--cached-survivors",
        type=Path,
        default=None,
        help="Path to cached survivor JSON (skip collection if present)",
    )
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="Only collect survivors and write the cache, do not run GB",
    )
    args = parser.parse_args()

    out_path: Path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(
        f"n={N}: collecting pre-vertex-circle survivors "
        f"(cap={args.survivor_cap}, budget={args.collect_budget_sec:.0f}s)",
        flush=True,
    )

    cache_path = args.cached_survivors
    survivors: list[list[list[int]]] | None = None
    collect_meta: dict[str, Any] | None = None
    if cache_path and cache_path.is_file():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        survivors = cached["survivors"]
        collect_meta = cached["meta"]
        print(
            f"  loaded {len(survivors)} cached survivors from {cache_path}",
            flush=True,
        )
    else:
        if args.row0_limit is not None:
            # crude: cap by limiting time too
            cap = args.survivor_cap
        else:
            cap = args.survivor_cap
        survivors, collect_meta = collect_survivors(
            N,
            survivor_cap=cap,
            budget_sec=args.collect_budget_sec,
            per_row0_cap=args.per_row0_cap,
            progress=not args.no_progress,
        )
        if cache_path:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(
                json.dumps({"survivors": survivors, "meta": collect_meta}),
                encoding="utf-8",
            )
            print(f"  cached survivors at {cache_path}", flush=True)

    print(
        f"  collected {len(survivors)} survivors "
        f"(row0_processed={collect_meta['row0_processed']}/"
        f"{collect_meta['row0_count']}, "
        f"row0_done={collect_meta['row0_done']}, "
        f"truncated={collect_meta['row0_truncated']}, "
        f"elapsed={collect_meta['collect_elapsed_sec']:.1f}s)",
        flush=True,
    )

    if args.collect_only:
        print("--collect-only specified, exiting before GB pass.", flush=True)
        return 0

    sample_indices: list[int]
    if len(survivors) > args.sample_size:
        import random

        rng = random.Random(args.seed)
        sample_indices = sorted(rng.sample(range(len(survivors)), args.sample_size))
        sampled = [survivors[i] for i in sample_indices]
        print(
            f"  sampling {len(sampled)} of {len(survivors)} survivors "
            f"(seed={args.seed})",
            flush=True,
        )
    else:
        sample_indices = list(range(len(survivors)))
        sampled = survivors

    print(
        f"running grevlex Gröbner over QQ on {len(sampled)} patterns "
        f"(GB timeout {args.gb_timeout_sec}s, real-root timeout "
        f"{args.real_root_timeout_sec}s)",
        flush=True,
    )

    results: list[dict[str, Any]] = []
    counts: dict[str, int] = {
        "GB_TRIVIAL": 0,
        "GB_NO_REAL": 0,
        "GB_NONTRIVIAL": 0,
        "GB_TIMEOUT": 0,
        "GB_ERROR": 0,
    }
    total_gb_time = 0.0
    t_run = time.time()
    for k, pattern in enumerate(sampled):
        info = attempt_groebner(
            pattern,
            n=N,
            timeout_sec=args.gb_timeout_sec,
            real_root_timeout_sec=args.real_root_timeout_sec,
        )
        verdict = info.get("verdict", "GB_ERROR")
        counts[verdict] = counts.get(verdict, 0) + 1
        total_gb_time += float(info.get("gb_time_sec", 0.0) or 0.0)

        record: dict[str, Any] = {
            "sample_index": k,
            "survivor_index": sample_indices[k],
            "rows": pattern,
            **info,
        }
        results.append(record)

        gb_time = info.get("gb_time_sec", 0.0) or 0.0
        elapsed_run = time.time() - t_run
        print(
            f"  [{k+1:3d}/{len(sampled)}] survivor#{sample_indices[k]:5d}: "
            f"verdict={verdict:14s} gb={float(gb_time):6.2f}s "
            f"size={info.get('gb_size','?')} "
            f"running={counts} elapsed={elapsed_run:7.1f}s",
            flush=True,
        )

    payload: dict[str, Any] = {
        "type": "n10_groebner_results_v1",
        "trust": "REVIEW_PENDING",
        "n": N,
        "row_size": ROW_SIZE,
        "sympy_version": sp.__version__,
        "monomial_order": "grevlex",
        "domain": "QQ",
        "gauge": ["x_0=0", "y_0=0", "y_1=0", "x_1=1"],
        "gb_timeout_sec": args.gb_timeout_sec,
        "real_root_timeout_sec": args.real_root_timeout_sec,
        "collect": collect_meta,
        "survivors_collected": len(survivors),
        "sampled": len(sampled),
        "sample_seed": args.seed,
        "sample_indices": sample_indices,
        "verdict_counts": counts,
        "total_gb_time_sec": total_gb_time,
        "wall_clock_groebner_pass_sec": time.time() - t_run,
        "results": results,
        "notes": [
            "No general proof of Erdős Problem #97 is claimed.",
            "No counterexample is claimed.",
            "GB_TRIVIAL means the grevlex Gröbner basis over QQ equals {1}: no complex solutions, hence no Euclidean realization.",
            "GB_NO_REAL means the basis was nontrivial but a univariate elimination polynomial in y_8/y_9/x_8/x_9 has no real roots.",
            "GB_NONTRIVIAL means the basis was nontrivial and either no univariate elimination polynomial was found in y_8/y_9/x_8/x_9, or it does admit real roots; decoder follow-up needed.",
            "GB_TIMEOUT means the Gröbner basis computation exceeded the budget; honest unresolved.",
        ],
    }

    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"\nWrote {out_path} ({len(results)} records). "
        f"Verdict counts: {counts}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
