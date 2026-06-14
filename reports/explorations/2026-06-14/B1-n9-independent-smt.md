# B1 — Independent n=9 re-derivation via from-scratch z3 SMT (coordinate geometry)

- Lane: B1 (Erdős Problem #97 research).
- Date: 2026-06-14.
- Branch: `claude/amazing-goldberg-8tcsju`; commit at run time `71f0f8b`.
- Trust label of this artifact: **`MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`**
  (an *independent second source* corroborating the stored combinatorial
  vertex-circle obstruction on the assignments it actually decided — NOT a proof
  of n=9, NOT a counterexample, NOT a promotion of any status).
- Official/global status of Erdős #97: unchanged — falsifiable/open.

## Objective

Independently re-derive (or refute) the repository's stored claim that all 184
pre-vertex-circle n=9 selected-witness incidence frontier assignments are
geometrically obstructed, using a *from-scratch* nonlinear-real coordinate
model handed to z3, sharing **no code** with the repo's combinatorial
vertex-circle brancher.

## The problem clause being tested

For a fixed nonagon labelled `0..8` in cyclic order, "center `i` has a 4-set
`S_i` of OTHER vertices at equal squared distance" means there is a circle
centred at `p_i` through the four vertices in `S_i`. The frontier supplies, per
assignment, one such `S_i` for every center (per-center radius and 4-set vary;
the incidence digraph need not be symmetric). The question per assignment:
*does this incidence pattern embed as a strictly convex 9-gon?*

## Model (QF_NRA, built directly from coordinates)

Script: `scripts/exploration/b1_n9_independent_smt.py`.

Variables and constraints for one fixed assignment:

- **Coordinates**: `x_i, y_i ∈ Reals`, `i = 0..8` (18 real variables).
- **Gauge**: `p0 = (0,0)`, `p1 = (1,0)`. Kills translation, rotation, and the
  scale of edge `0→1`, cutting the similarity group. Sound for both SAT and
  UNSAT: any realizable convex 9-gon can be similarity-mapped so edge `0→1` is
  `(0,0)–(1,0)`; reflection (a similarity) fixes orientation, so requiring CCW
  loses no solutions.
- **Strict convexity (REQUIRED ingredient)**: for every cyclically consecutive
  triple `(p_a,p_b,p_c)` in the stored cyclic order, the signed turn
  `cross((p_b−p_a),(p_c−p_a)) > 0` — all 9 turns **strictly** positive (CCW).
  This is the strict-convexity encoding the impossibility lane must contain;
  it is what distinguishes this from a generic metric-equation feasibility test
  (cf. failed-idea #16, the non-convex P24 negative control).
- **Distinctness**: `p_i ≠ p_j` for all `i<j` (asserted explicitly as the
  problem requires distinct vertices; strict convexity already implies it).
- **Equal-distance witnesses**: for each center `i` with `S_i={a,b,c,d}`,
  `|p_i−p_a|² = |p_i−p_b|² = |p_i−p_c|² = |p_i−p_d|²` (3 equations/center, 27
  polynomial equations total).

Per assignment z3 is asked `check()` in QF_NRA. Reading:

- `unsat` → this incidence pattern admits **no** strictly convex 9-gon →
  independently confirms the pattern is obstructed.
- `sat` → a realization exists → would **refute** the stored "all obstructed"
  claim; flagged for exact certification, **NOT** a counterexample claim
  (nonlinear-real z3 models are subject to solver trust; any model must be
  re-certified with exact arithmetic).
- `unknown`/`timeout` → z3 could not decide within the budget. Reported
  honestly; establishes **nothing** about that pattern.

## Independence from the repo pipeline (disjointness audit)

- `b1_n9_independent_smt.py` imports only stdlib (`argparse, json, sys, time,
  pathlib`) plus `z3`. **Zero** imports from `erdos97.*`. The only textual
  mention of the brancher is in the docstring, citing what it does *not* reuse.
- The combinatorial brancher `src/erdos97/n9_vertex_circle_exhaustive.py` has
  **0** occurrences of `z3`/`Real`/coordinate/`sqrt`; it never introduces point
  coordinates and reasons purely about chord-crossing/quotient combinatorics.
- The two methods are therefore methodologically independent: combinatorial
  chord-order/quotient reasoning vs. direct nonlinear-real coordinate geometry.

## Input data (treated as INPUT, not truth)

The 184 frontier assignments come from
`data/certificates/n9_vertex_circle_frontier_motif_classification.json`
(the exhaustive JSON itself stores only the count `184`; the motif
classification file carries the actual `selected_rows`). Each record's
`selected_rows` is 9 rows `[center, w1, w2, w3, w4]`.

Defensive validation performed (independently, before any solving):

- 184 assignments, unique `assignment_id`s.
- Every assignment has exactly 9 rows; centers cover `0..8`.
- Every row is `center + 4 distinct witnesses`, all in `0..8`, center not a
  witness.
- Stored status multiset is `158 self_edge + 26 strict_cycle` (matches the
  repo's documented frontier accounting — used only to bucket results, not as
  ground truth).
- Order-independent frontier digest (sha256 of the sorted multiset of sorted
  row-sets): `15ad4222be9a99066f37fbd18984512078b64fb9f678be4d8f8c6e3788c09e2d`.

## Positive controls (guard against vacuous UNSAT)

Run before the sweep, to prove the encoding is not over-constrained and that
UNSAT results are caused by the witness equations interacting with convexity:

1. A CCW regular 9-gon satisfies all 9 turn inequalities (`>0`) — confirms the
   strict-convexity encoding accepts a genuine convex polygon and is
   orientation-correct.
2. Convexity + gauge + distinctness, **no** witness equations → **SAT**
   (the constraint frame alone is satisfiable; not vacuously UNSAT).
3. Convexity + gauge + distinctness + a **single** 4-witness equal-distance row
   → **SAT** (the equal-distance machinery alone forces no spurious
   contradiction; obstruction must arise from the full 9-row system).

All three controls passed.

## Coverage and results

z3 4.16.0, QF_NRA. The decidable assignments resolve very fast (UNSAT in
0.01–2.4 s); the rest are hard QF_NRA instances that exhaust the per-assignment
timeout and return `unknown`. The raw `qfnra-nlsat` tactic was tested and gave
no speedup over the default solver on the hard cases (default already dispatches
to nlsat). Compute was bounded to a few minutes total per lane policy, so full
184-coverage with a *decisive* timeout is not achievable in budget; the runs
below report coverage honestly.

Three runs were executed (z3 4.16.0, on this machine):

| run | per-asg timeout | wall budget | distinct attempted | unsat | sat | unknown |
|-----|-----------------|-------------|--------------------|-------|-----|---------|
| R1 (deep prefix) | 6000 ms | 230 s | 48 (A001–A048) | 10 | 0 | 38 |
| R2 (broad)       | 1500 ms | 220 s | 155 (A001–A155) | 24 | 0 | 131 |
| R3 (tail)        | 1500 ms | 60 s  | 31 (A049,A050,A156–A184) | 5 | 0 | 26 |

**Consolidated across all three runs (union of decided verdicts):**

| metric | value |
|--------|-------|
| distinct assignments attempted | **184 / 184** (whole frontier) |
| distinct **UNSAT** (independently obstructed, strict convexity encoded) | **30** |
| distinct **SAT** | **0** |
| not decided (`unknown` in every run that reached it) | 154 |
| stored-status of the 30 UNSAT | 29 `self_edge` + 1 `strict_cycle` |
| motif families with ≥1 UNSAT | 11 / 16 (F01,F02,F03,F04,F06,F07,F08,F09,F10,F11,F14) |
| local-core templates with ≥1 UNSAT | 8 / 12 (T01,T02,T05,T06,T07,T08,T09,T11) |

The 30 distinct UNSAT assignment IDs:
`A001 A004 A008 A009 A011 A014 A019 A022 A038 A039 A051 A060 A061 A067 A072
A073 A076 A085 A098 A099 A101 A114 A119 A121 A136 A166 A168 A178 A182 A184`.

Comparison with the stored claim: the repo records all 184 as vertex-circle
obstructed (158 self_edge + 26 strict_cycle). This lane independently agrees on
the 30 it could decide (all UNSAT, **no SAT**), so on the decided subset the two
methods **corroborate**. The remaining 154 are an honest coverage gap (QF_NRA
hardness under the few-minute budget), **not** disagreement. The strict_cycle
families are mostly among the hard/undecided cases (only 1 of 26 strict_cycle
assignments was decided).

### Interpretation

- **No SAT** was found on any decided assignment in any run. Every assignment
  that z3 decided came back `unsat`, i.e. independently obstructed by the
  coordinate model **with strict convexity encoded**. This *corroborates* the
  stored combinatorial claim on the decided subset.
- The `unknown` assignments establish nothing either way; they are an honest
  coverage gap driven by QF_NRA hardness + the time budget, not evidence.
- This run therefore **does not** independently re-derive the full
  "all 184 obstructed" result. It provides a partial independent second source:
  a strict-convexity coordinate model agrees (UNSAT, no SAT) on the decided
  subset and surfaces **no** counterexample candidate.

## What this does NOT establish

- It does **not** prove n=9, does **not** promote the n=9 finite-case artifact,
  and does **not** touch the official/global falsifiable-open status.
- It does **not** decide the `unknown` assignments; the full frontier is **not**
  independently closed by this lane.
- A z3 `unsat` is a solver result, not a machine-checked proof object; promoting
  even the decided subset to source-of-truth would require an exact/independent
  UNSAT replay (e.g. exact CAD, an SOS/Positivstellensatz certificate, or a
  proof-producing solver). That is out of scope here and overlaps lane A2 (SOS).
- No exact certification of any SAT model was needed (there were none).

## Reproduction

```bash
# from repo root, on branch claude/amazing-goldberg-8tcsju
# full-coverage attempt, short decisive timeout, wall-budget capped:
python scripts/exploration/b1_n9_independent_smt.py \
    --all --timeout-ms 1500 --budget-seconds 220 \
    --json data/exploration/b1_n9_independent_smt_results.json

# deeper per-assignment effort on a prefix (more UNSATs, fewer assignments):
python scripts/exploration/b1_n9_independent_smt.py \
    --all --timeout-ms 6000 --budget-seconds 230 \
    --json data/exploration/b1_n9_independent_smt_results.json
```

The JSON output records `counts`, `by_stored_status`, `sat_assignment_ids`
(empty), and a per-assignment `results` list with z3 verdict and elapsed time.
Results vary slightly run-to-run because timeouts/`unknown` depend on machine
speed; the set of fast-UNSAT assignments is stable, and **no SAT** is the
invariant claim.

Lint: `ruff check scripts/exploration/b1_n9_independent_smt.py` → clean.
