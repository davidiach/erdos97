# Erdős #97 — multi-agent exploration synthesis (2026-06-14)

Status: exploration meta-summary only; **not** proof-facing and **not** a status
change. No general proof and no counterexample are claimed. Official/global
status remains **falsifiable/open**; `n ≤ 8` remains repo-local machine-checked;
`n = 9` / `n = 10` remain review-pending / draft. Aligned with
`metadata/erdos97.yaml`.

This run spawned 13 orthogonal exploration lanes plus an independent verifier,
each deliberately aimed at directions the repository had **not** yet explored (or
only shallowly), and each hard-fenced against the 20 entries of
`docs/failed-ideas.md` and the deeply-worked lanes (bootstrap-T12, block-6
shuffles, radius-blocker product sweeps, one-more-fixed-pattern Kalmanson).

## 1. Cross-cutting finding

Independent lanes converged on one message: **the obstruction is global and
convexity-structural, not local or purely metric.**

- C2 (exact + numeric): a single vertex's 4-set is *locally free* (residual
  driven to 2.75e-9, strictly convex), but enforcing all centers simultaneously
  is *globally tight* (stuck at 6.4e-7).
- E1 (literature): a 4-bad polygon produces only **linear** structure (~6n
  isosceles triangles), while every relevant convex-position bound is
  **super-linear** (Θ(n²) isosceles, Θ(n log n) repeats) — so no counting /
  incidence import can close the gap asymptotically.
- A1 + A4 + A6 (exact): the load-bearing ingredient is the **turn / convexity
  sign** structure — turn-packing Farkas (A1), the >π/2 turn-inequality lemma
  (A4), and forced-perpendicularity parity (A6) — and the P24 control confirms a
  metric/rank-only route necessarily fails.

This re-confirms the repo's own strategic diagnosis (scope gap → a bridge from
"arbitrary counterexample" to "forbidden structure") and says the bridge must be
convexity-specific and global.

## 2. Run ledger

| Lane | Direction | Result (one line) | Trust label | Reproduced by verifier |
|---|---|---|---|---|
| A1 | dimension / elimination | turn-packing Farkas kills fixed patterns from convexity structure; exact P24 separation | EXACT (per pattern) + HEURISTIC | yes |
| A2 | SOS / Positivstellensatz | exact degree-1 **Nullstellensatz** for 13/14 n=8 classes; class 14 is the lone convexity-driven class | EXACT_OBSTRUCTION + NUMERICAL | yes |
| A3 | Bridge Lemma A′ | localizes A′ to a single **rich-class-availability** sub-question; corroborates A′ | REVIEW_PENDING_DIAGNOSTIC | (read) |
| A4 | endpoint / diameter | #18's descent center is an M-**maximizer** → missing ingredient = **center minimality** | proof-mining | (read) |
| A5 | Aggarwal antipodal-cut | 0 new kills; proves Aggarwal ℓ=2 ≡ strict-Kalmanson; reusable single-class filter for n≥10 | EXACT filter + SHARP_NO_GO | (read) |
| A6 | topological / parity | **parity + parallel-endpoint kills all 184 n=9 frontier combinatorially**; provenance gap in the n=9 pipeline | EXACT_FINITE_COMPUTATION | **yes — SOUND** |
| A7 | inversion / Möbius | sharp no-go: inversion cannot compress (destroys convexity + center-blindness) | EXACT_DIAGNOSTIC / NO_GO | (read) |
| B1 | independent n=9 SMT | disjoint z3 second source: **30/184 UNSAT, 0 SAT**, 154 timeout | REVIEW_PENDING (partial) | (read) |
| B2 | scalable incidence | **reproduces n=9 frontier digest exactly**, 0 survivors; n=10 partial (engineering bottleneck) | REVIEW_PENDING | yes |
| C1 | new-ansatz search | no strictly-convex candidate; low residual ⟺ #7 degeneration | NUMERICAL_EVIDENCE | (recovered) |
| C2 | k=3 → k=4 homotopy | **exact** symmetric two-radius obstruction (extends #17); "locally free, globally tight" | EXACT + NUMERICAL | (read) |
| D1 | Lean formalization | hardened kernel sketch statements; fixed a pre-existing integrity-check failure | PROVENANCE | (read) |
| E1 | literature transfer | no published bound beats n=8; linear-vs-super-linear gap | LITERATURE_BACKED / NO_GO | (read) |

Independent verifier (`EVAL-verifier.md`) re-ran A1/A2/A6/B2 and found **no
material issues, no overclaims, no cross-lane contradictions** (B1's "0 SAT,
30/184 UNSAT", A6's "all 184 killed", and B2's "0 survivors" are mutually
consistent).

## 3. Ranked findings (top 5)

### #1 — A6: a sound, lighter combinatorial closure of the n=9 frontier (+ a provenance gap)
- **New ingredient:** generalize the n=7 perpendicularity-cycle *parity* argument
  to an n-independent filter = (a) the forced-perpendicularity graph `G_⊥`
  (built only when `|S_i∩S_j| = 2`, i.e. exactly L6) must be **bipartite**;
  (b) **parallel-endpoint**: two even-parity chords in one `G_⊥` component that
  share an endpoint force 3 collinear vertices (L2 violation under strict
  convexity).
- **Result (verified SOUND, reproduced):** kills **all 184** pre-vertex-circle
  n=9 frontier assignments combinatorially (22 by parity + 162 by
  parallel-endpoint) — no vertex-circle / metric reasoning. Cross-checks against
  the repo's own `forced_perpendicular_graph` / `odd_forced_perpendicular_cycle`.
- **Provenance gap (confirmed independently):** `src/erdos97/n9_incidence_frontier.py`
  uses `odd_forced_perpendicular_cycle` (catches the 22) but has **no**
  parallel-endpoint filter; that filter exists only in `n8_incidence.py`. So
  162/184 were never tested combinatorially before the heavy vertex-circle
  machinery.
- **Weakest assumption / honest limit:** necessary-only — it leaves **all 15
  n=8 survivors alive** (they need exact algebra), so it is route-consolidation
  and a *simpler* repo-local n=9 obstruction, **not** a theorem and **not** a
  path to #97 by itself.
- **Next experiment (scoped follow-up PR, needs review):** lift
  `parallel_endpoint_violation` into `incidence_filters.py` + the
  `n9_incidence_frontier` prefilters and confirm the live n=9 search closes
  without vertex-circle. (Do **not** slam into the review-pending pipeline in an
  exploration sweep.)
- **Verify:** `python scripts/exploration/a6_topological_parity.py`

### #2 — A2: an orthogonal exact Nullstellensatz second source for n=8
- **New ingredient:** an exact rational Nullstellensatz certifier `Σ λ_k g_k = 1`
  + a numeric moment/SOS pipeline (no SOS machinery existed before).
- **Result:** 13/14 post-cyclic n=8 classes are "equality-empty" (metric ideal
  contains 1, convexity not needed) with exactly-verified degree-1 certificates;
  class 14 is the unique convexity-driven class (its 4 variety points are
  non-convex in all 72 orders). Independently confirms the repo's "class 14 is
  delicate" claim by a route orthogonal to its Groebner/linear-span certs.
- **Weakest:** class 14 needs convexity; n=9 exact certificate not obtained
  (degree ≥ 2 needs a C-backed rational solver / FLINT).
- **Next:** degree-≥2 Positivstellensatz with the turn inequalities for class 14
  and a genuinely-open n=9 assignment.
- **Verify:** `python scripts/exploration/a2_sos_exact_certify.py --classify`

### #3 — A1: turn-packing isolates the load-bearing convexity injection
- **New ingredient:** feed the convexity premises (`t_i > 0 ∀i`, `Σt_i = 4`) into
  the turn-inequality lemma's linear elimination; a **Farkas** certificate
  (5 inequalities > 4·λ) kills fixed patterns from the combinatorial turn
  structure alone — *cheaper than Gröbner* — and the P24 control's turn-sign
  premise is false, giving an exact metric/rank-vs-convexity separation.
- **Weakest:** per-fixed-pattern; the Bridge Lemma is untouched. Also surfaced a
  real subtlety: convexity tests **must include vertex distinctness** (the F07
  "convex" points are a degenerate triangle triple-cover).
- **Next:** attempt the bridge for a single n=8 class; test whether turn-packing
  alone closes a super-set of patterns at n=10/11.
- **Verify:** `python scripts/exploration/a1_dimension_elimination.py`

### #4 — B2 + B1: three disjoint methods now corroborate the review-pending n=9
- B2 independently reproduces the **exact 184-frontier digest** and n=9→0
  survivors (both symmetry modes, matching the 38 canonical classes); B1's
  from-scratch z3 finds **0 SAT** anywhere (30/184 UNSAT, rest timeout). With A6
  (parity) this is **three disjoint corroborations** of the n=9 obstruction —
  useful evidence for the Priority-5 review, still review-pending.
- **Weakest:** B2's Python per-node cost stalls n=10; B1's QF_NRA is
  non-decisive on 154/184.
- **Next:** CP-SAT/bitset port of B2 (likely closes n=10 in minutes);
  exact-certify B1's 154 unknowns via A2's path.
- **Verify:** `python scripts/exploration/b2_scalable_incidence_search.py --n 9`

### #5 — A3 + A4: the bridge program, sharpened
- A3 localizes Bridge Lemma A′ to one decisive **rich-class-availability**
  question (and shows convex-order is the *wrong* strengthening; the n8/n9
  non-ear dichotomy is real). A4 shows the failed-idea-#18 obstruction is exactly
  a missing **center-minimality** hypothesis (M(O)=4 = maximizer). Both stay
  open but give concrete next lemmas.
- **Verify:** `python scripts/exploration/a3_ear_orderability_frontier.py`

## 4. Honest negatives (so future runs skip them)

- **A7 inversion/Möbius:** reasoned no-go — inversion is metric-equivalent to the
  original equations and destroys both strict convexity and center-information.
  Supersedes `docs/inversive-incidence-pilot.md` with the exact reason. *Do not
  revisit* except an exotic Lie-sphere invariant (low value; center-blind).
- **A5 Aggarwal antipodal-cut:** the deferred checker is now built; **0 new
  kills**; its ℓ=2 content is provably identical to strict-Kalmanson. Keep the
  reusable single-class filter as a candidate for n≥10; archive as
  negative-control otherwise.
- **E1 literature transfer:** no published convex-position bound beats n=8 or is
  all-n; the path is convexity-structural, not import-based. Lane exhausted.
- **C1 new-ansatz search:** no strictly-convex candidate at n=10/12/16; low
  residual only at the convexity boundary (#7 mode). Negative-control.

## 5. Artifact index

All under `reports/explorations/2026-06-14/` (notes) and
`scripts/exploration/` (code); all ruff-clean.

- `00-SYNTHESIS.md` (this file), `EVAL-verifier.md` (independent verifier)
- A1 `A1-dimension-elimination.md` / `a1_dimension_elimination.py`
- A2 `A2-sos-infeasibility.md` / `a2_sos_exact_certify.py`, `a2_class14_convexity_sos.py`, `a2_sos_infeasibility.py`
- A3 `A3-bridge-ear-orderability.md` / `a3_ear_orderability_frontier.py`
- A4 `A4-endpoint-diameter.md` / `a4_failed18_endpoint_reexam.py`, `a4_three_cap_diameter_bridge.py`
- A5 `A5-aggarwal-antipodal-cut.md` / `a5_aggarwal_antipodal_cut.py`
- A6 `A6-topological-parity.md` / `a6_topological_parity.py`
- A7 `A7-inversion-mobius.md` / `a7_inversion_mobius.py`
- B1 `B1-n9-independent-smt.md` / `b1_n9_independent_smt.py` (+ `data/exploration/b1_n9_independent_smt_results.json`)
- B2 `B2-scalable-incidence-smt.md` / `b2_scalable_incidence_search.py`, `b2_realizability_spotcheck.py`
- C1 `C1-new-ansatz-search.md` (orchestrator-recovered) / `c1_new_ansatz_search.py`
- C2 `C2-k3-to-k4-homotopy.md` / `c2_k3_to_k4_homotopy.py` (+ `data/runs/c2_k3_to_k4_2026-06-14/`)
- D1 `D1-lean-formalization.md` + Lean edits under `lean/Erdos97/`
- E1 `E1-literature-transfer.md`

## 6. One recommendation

**Fund A6.** Open a scoped, reviewed follow-up that lifts the parallel-endpoint
necessary filter into the n=9 incidence pipeline. Independently verified as
**sound**, it closes 162/184 of the n=9 frontier combinatorially (the remaining
22 are already caught by the existing odd-perpendicularity-cycle filter),
yielding a **simpler, lighter-weight repo-local n=9 obstruction** than the
vertex-circle machinery — strengthening the Priority-5 review case **without**
moving official/global status. Pair it with the A1/A4 **turn-inequality** thread
as the medium-term bridge direction, since multiple lanes independently identify
the convexity-sign structure as load-bearing.

Reminder of scope: A6 is **necessary-only** (cannot settle n=8, let alone #97);
it is a route simplification and an audit win, not a theorem and not a proof of
Erdős #97.
