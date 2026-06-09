# Dynamic-witness free-pattern search

Trust labels: `NUMERICAL_EVIDENCE` for the recorded runs, `HEURISTIC` for the
search design. This note records search diagnostics only. Nothing here is a
proof, nothing here is a counterexample, and no candidate found so far meets
the repo exactification gate. The official/global status of Erdos Problem #97
remains falsifiable/open.

## Why this lane exists

All previous numerical searches in this repository optimize coordinates for
one fixed registered selected-witness pattern at a time
(`erdos97.search` with the `candidate-patterns.md` catalog). That leaves a
coverage gap on the construction side: a strictly convex configuration could
satisfy the four-equal-distance condition with a witness pattern nobody
registered.

The dynamic-witness searcher closes that gap heuristically: at every
objective evaluation, every center re-selects its own best witness 4-set as
the minimum-spread sliding window over that center's sorted squared
distances. One continuous optimization run therefore probes every witness
pattern reachable by the configuration family at once. The witness
re-selection alternates with Levenberg-Marquardt steps on the selected
equality residuals plus guard penalties.

Context from the 2025 literature: the AlphaEvolve mass-experiment paper
(arXiv:2511.02864) reports an attempt on exactly this problem in which the
evolutionary searcher exploited the verifier by collapsing many points into
near-coincident clusters, so that float distances became indistinguishable.
That matches this repository's historical `B12_3x4_danzer_lift` failure mode.
The guards below are designed so that this exploit is structurally visible
instead of silently rewarded.

## Method

Code: `src/erdos97/dynamic_witness_search.py`,
CLI: `scripts/search_dynamic_witness.py`,
tests: `tests/test_dynamic_witness_search.py`.

- Equivariant mode: cyclic symmetry `C_m` with `t` free orbits
  (`n = m*t` points, `2t - 2` parameters after gauge fixing). Only the `t`
  orbit representatives need windows, so large `n` stays cheap.
- Asymmetric mode: `m = 1`, `t = n` is the same code path with no symmetry.
- Anti-degeneracy guards (all scale-normalized): strict-convexity
  cross-product floor (default `5%` of the regular-`n`-gon margin), angular
  gap floor, and a pairwise-separation floor at `0.1/n` of the diameter. The
  pairwise floor is the anti-cluster wall and is never annealed.
- Floor annealing: after converging under the default floors, the
  convexity/angle floors are lowered (`x0.05` / `x0.3`) and the alternation
  re-runs, because a genuine candidate only needs a strictly positive
  convexity margin, not the conservative default floor.
- Three reporting tiers per cell: best under default floors
  (`best_feasible`), best strictly convex with the pair floor enforced
  (`best_convex`), and best overall (`best`). Records flag
  `near_pair_floor` when the minimum pairwise separation sits within `1.5x`
  of the anti-cluster floor, which marks the known degenerate exploit.
- Known-solution control: with the convexity guard dropped, the alternation
  converges from a perturbed start to the exact nonconvex 24-point
  metric-linear configuration
  (`scripts/verify_p24_metric_linear_nonconvex.py`) at relative spread below
  `1e-10` (deterministic unit test
  `tests/test_dynamic_witness_search.py::test_refine_converges_to_known_nonconvex_solution`).
  This shows the machinery can land on exact solutions when one is in the
  basin, which is what makes the strictly convex plateaus informative. The
  `--with-controls` sweep lane runs the same cells from random starts; at
  the recorded 16-restart budget those control cells reach spreads around
  `1e-2` to `3e-3` without finding the exact basin, a useful reminder that
  restart budgets bound what any cell's plateau means.

## Recorded run

Artifact: `data/runs/dynamic_witness_sweep_2026-06-09/summary.json`
(seed `20260609`, 16 restarts per symmetric cell, 8 per asymmetric cell).
Grid: `t=2` with `m=5..18`, `t=3` with `m=4..12`, `t=4` with `m=3..9`,
`t=5` with `m=3..7`, `t=6` with `m=3..6`, `t=7` with `m=3..5`,
`t=8` with `m=3..4`, `(m,t)=(3,9),(3,10)`, plus asymmetric `n=10..14`,
covering `10 <= n <= 36`.

Headline: no run reached the candidate gate (relative spread below `1e-10`
with strictly positive convexity margin and healthy separations). The
recorded outcomes split into two classes:

1. Structural plateaus: strictly convex local optima with healthy margins
   stall at relative spreads around `1e-2` to `1e-1` (for example the
   `m=5, t=2` cell). These look like genuine geometric obstruction walls in
   the symmetric families, consistent with the exactly-killed two-orbit
   half-step ansatz (`docs/two-orbit-radius-propagation.md`).
2. Floor-riding degenerations: every strictly convex record with relative
   spread below `2e-3` has normalized convexity margin below `1e-4` (most
   below `5e-6`), and the smallest spreads also pin the minimum pairwise
   separation within `1.25x` of the anti-cluster floor. A typical example is
   the `m=5, t=3` best (spread `1.6e-4`, margin `7e-7`), whose three orbits
   collapse toward near-coincident triples on a pentagon (orbit angles
   within `0.013` rad, separation `1.04x` the floor). This is the
   B12/AlphaEvolve cluster exploit, held off by the pair floor rather than
   eliminated, and it is diagnostic data for the degeneration boundary, with
   no counterexample value on its own.

The spread-versus-margin coupling is the quantitative content: across all
cells, pushing the dynamic-witness spread toward zero forces the
configuration toward the convexity boundary or the separation floor. No cell
shows an interior strictly convex basin with spread tending to zero.

## Second recorded run (deep pass)

Artifact: `data/runs/dynamic_witness_sweep_2026-06-09b/summary.json`.
This pass reruns the 32 symmetric `t >= 3` cells at 64 restarts each (4x the
first budget; the `t = 2` family is now covered exactly by
`docs/two-orbit-circulant-obstruction.md` and
`docs/symmetric-two-orbit-reduction.md`), plus asymmetric `n = 10..16`. The
asymmetric cells ran at 8 restarts because the single-cell driver passed
`--restarts` but not `--asym-restarts`; that flag gap is recorded here so
the next pass corrects it.

Outcome unchanged and sharpened: still no candidate. The best strictly
convex relative spread across all 39 cells is `8.3e-5` (`m=7, t=3`), and it
is a floor-riding degeneration (margin `2.1e-7`, separation at the
anti-cluster floor). Every strictly convex record below `1e-3` is either
flagged `near_pair_floor` or has margin below `1e-5`; healthy-margin
plateaus stay at relative spreads near `1e-2` or above. The unconstrained
lane meanwhile reaches `1.1e-7` (`m=8, t=4`), consistent with exact
nonconvex solutions existing while the strictly convex side walls off.

## Non-claims

- This is a finite, seeded, heuristic search; it proves nothing about
  patterns or configurations outside the visited basins, and it does not
  change any repository status.
- Small spreads at degenerate margins are not near-counterexamples; the
  historical record shows such configurations collapse under exact scrutiny.
- The candidate gate for any future hit remains the repo standard: exact
  coordinates or exact algebraic/interval/SMT certificates for both the
  distance equalities and strict convexity.

## Next steps recorded for the loop

1. Two-orbit lemma target: inside `C_m` two-orbit configurations, four
   vertices on one circle force either radially aligned orbits (nonconvex or
   coincident) or the exact half-step offset `pi/m`; in the half-step case
   every row reduces to two quadratics in the radius ratio that must share a
   root inside the strict-convexity window `(cos(pi/m), sec(pi/m))`. The
   numerical `t=2` walls above suggest the shared-root set is empty for all
   `m`, which would retire the entire two-orbit family exactly and supersede
   the fixed quarter-turn ansatz obstruction. This needs an exact derivation
   and a checked certificate enumeration over the discrete offsets.
2. Deeper restarts on the asymmetric cells (`n = 10..14`) and `t >= 3` angle
   alignment analysis (which cosine equalities can hold off the half-step
   locus when three or more orbits interact).
3. If any future run beats the structural plateaus at healthy margins,
   exactify with the standard pipeline before any claim language.
