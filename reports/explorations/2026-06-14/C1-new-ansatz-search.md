# Lane C1 — new-ansatz global numerical search (orchestrator-recovered)

Status / trust label: `NUMERICAL_EVIDENCE` (heuristic search only). No proof, no
counterexample, no candidate promoted. Official/global status unchanged.

> Provenance note: the C1 subagent completed its run but did not emit its final
> structured summary or write this report file (its returned message was lost).
> This note was reconstructed by the orchestrator by re-running the lane's own
> committed script `scripts/exploration/c1_new_ansatz_search.py` under a reduced
> time budget. The numbers below are from that recovery run; rerun the script at
> a larger `--seconds` budget for sharper figures.

## Objective

Search for an approximately 4-bad **strictly convex** polygon using a
genuinely new ansatz — asymmetric multistart / basin-hopping over `2n` free
coordinates with a strict-convexity penalty and **per-center free radius** —
explicitly avoiding the forbidden ansätze from `docs/failed-ideas.md`
(#7 B12 danzer-lift, #17 two-orbit half-step, #20 Fishburn–Reeds cut homotopy).

## Recovery run (reduced budget: `--n 10 12 16 --seconds 25`)

| n | best strictly-convex result | best "any" (diagnostic) residual | convex? | margin |
|---|---|---|---|---|
| 10 | none found | eq_rms 2.69e-2, max_spread 5.83e-2 | No | 1.98e-3 (collapsing) |
| 12 | none found | eq_rms 3.30e-3, max_spread 4.98e-3 | No | 2.00e-3 (collapsing) |
| 16 | none found | eq_rms 1.48e-2, max_spread 2.90e-2 | No | 1.99e-3 (collapsing) |

## Result

- The search found **no strictly convex** approximately-4-bad configuration at
  any tested `n`.
- The only low-residual configurations are **not strictly convex**: their
  equal-distance residual shrinks while the convexity margin collapses toward 0
  — i.e. the residual improves only as the polygon degenerates to the convexity
  boundary. This is exactly the `docs/failed-ideas.md` #7 failure mode, now
  reproduced under a different (asymmetric, free-radius) ansatz.
- **No `EXACTIFICATION-TRIGGER` candidate** (no residual `< 1e-10` with a robust
  convexity margin). Nothing is routed to `docs/exactification-plan.md`.

## Uses strict convexity

Yes — strict convexity is the binding constraint: dropping it makes small
residuals trivially attainable, and every low-residual point the search reaches
is non-convex with a collapsing margin.

## What this does NOT establish

- It does not rule out a 4-bad strictly convex polygon for any `n` (heuristic
  search, not a proof).
- A larger time budget or smarter global optimizer could behave differently;
  this is bounded-effort evidence, not an exhaustive search.

## Reproduction

```bash
python scripts/exploration/c1_new_ansatz_search.py --n 10 12 16 --seconds 60
ruff check scripts/exploration/c1_new_ansatz_search.py
```

## Cross-lane note

This converges with lane C2 (the lift is "locally free but globally tight") and
lane E1 (4-bad is a *global*/linear structure): single relaxations are easy, but
the **simultaneous all-centers strictly-convex** demand is what resists, which
is where the obstruction must live.
