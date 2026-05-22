# Erdős Problem #97 — counterexample/proof search

![tests](https://github.com/davidiach/erdos97/actions/workflows/tests.yml/badge.svg)

This repository is a public research log and reproducibility workspace for Erdős Problem #97.

**Status:** No general proof and no counterexample are claimed. This repo records reproducible searches, obstruction lemmas, failed approaches, finite-case proofs, and exact-certification attempts.

## Where to start

- For the short working state, read [`STATE.md`](STATE.md).
- For the long-form canonical synthesis and claim reconciliation, read
  [`docs/canonical-synthesis.md`](docs/canonical-synthesis.md) before adding
  new claims, search branches, or proof attempts.
- For upstream alignment with `teorth/erdosproblems`, read
  [`docs/upstream-alignment.md`](docs/upstream-alignment.md).
- For independent audit instructions, read
  [`docs/reviewer-guide.md`](docs/reviewer-guide.md).
- For current review priorities, read
  [`docs/review-priorities.md`](docs/review-priorities.md).
- For canonical status metadata, see
  [`metadata/erdos97.yaml`](metadata/erdos97.yaml).
- For documentation navigation, read [`docs/index.md`](docs/index.md).
- For the compact results ledger, read [`RESULTS.md`](RESULTS.md).
- For proved local facts, read [`docs/claims.md`](docs/claims.md).
- For the reproducible `n=7` Fano enumeration, read [`docs/n7-fano-enumeration.md`](docs/n7-fano-enumeration.md).
- For the reproducible `n=8` incidence-completeness enumeration, read
  [`docs/n8-incidence-enumeration.md`](docs/n8-incidence-enumeration.md).
- For the `n=8` exact survivor obstruction artifact, read
  [`docs/n8-exact-survivors.md`](docs/n8-exact-survivors.md).
- For the SymPy-free independent recheck of the `n=8` cyclic-order counts and
  11 survivor-class obstructions, read
  [`docs/n8-independent-obstruction.md`](docs/n8-independent-obstruction.md).
- For the focused class `14` Groebner/strict-interior audit, read
  [`docs/n8-class14-certificate.md`](docs/n8-class14-certificate.md).
- For the focused residual class `3`, `4`, and `5` certificate audit, read
  [`docs/n8-residual-certificates.md`](docs/n8-residual-certificates.md).
- For the review-pending exhaustive `n=9` vertex-circle finite-case checker,
  read [`docs/n9-vertex-circle-exhaustive.md`](docs/n9-vertex-circle-exhaustive.md).
- For the compact `n=9` Kalmanson self-edge replay certificate, read
  [`docs/n9-kalmanson-selfedge.md`](docs/n9-kalmanson-selfedge.md).
- For the derived `n=9` vertex-circle template lemma-candidate catalog, read
  [`docs/n9-vertex-circle-template-lemma-catalog.md`](docs/n9-vertex-circle-template-lemma-catalog.md).
- For the relation-skeleton extraction from focused `n=9`
  vertex-circle local packets, read
  [`docs/relation-skeleton-catalog.md`](docs/relation-skeleton-catalog.md).
- For the review-pending `n=10` singleton-slice finite-case draft, read
  [`docs/n10-vertex-circle-singleton-slices.md`](docs/n10-vertex-circle-singleton-slices.md).
- For the bounded `n=10` row0 turn-frontier pilot and its weak-turn escape
  self-edge templates, read
  [`docs/n10-turn-row0-pilot.md`](docs/n10-turn-row0-pilot.md) and
  [`docs/n10-turn-row0-escape-self-edges.md`](docs/n10-turn-row0-escape-self-edges.md).
- For a compact human-readable proof-note draft excluding bad convex octagons,
  read [`docs/n8-geometric-proof.md`](docs/n8-geometric-proof.md).
- For an interactive visualization of that proof idea, open
  [`docs/octagon-trap.html`](docs/octagon-trap.html).
- For the crossing-bisector, mutual-rhombus, phi 4-cycle rectangle-trap, and
  vertex-circle fixed-pattern filters, read
  [`docs/mutual-rhombus-filter.md`](docs/mutual-rhombus-filter.md),
  [`docs/phi4-rectangle-trap.md`](docs/phi4-rectangle-trap.md), and
  [`docs/vertex-circle-order-filter.md`](docs/vertex-circle-order-filter.md).
- For the round-two fixed-order Kalmanson/Farkas certificate, read
  [`docs/round2/round2_merged_report.md`](docs/round2/round2_merged_report.md)
  and [`docs/round2/kalmanson_distance_filter.md`](docs/round2/kalmanson_distance_filter.md).
- For the weak exact minimum-radius short-chord filter, read
  [`docs/minimum-radius-filter.md`](docs/minimum-radius-filter.md).
- For a partial bridge theorem from minimality to fragile-cover witness
  systems, read
  [`docs/minimal-fragile-cover-bridge.md`](docs/minimal-fragile-cover-bridge.md).
- For radius-blocker packet diagnostics, including the full exact-four
  natural-order `n=9` blocker `{0,1,2,3}` packet, the natural-order
  four-blocker shape sweep, its order-reduction crosswalk, a bounded
  richer-class projection pilot, a full rich-class quotient replay pilot, a
  generated rich-class quotient sweep, a bounded rich-extension neighborhood
  sweep, a one-packet full rich-extension product pilot, and an all-packet
  generated rich-extension product sweep, plus the generator-independent
  all-five-rich support obstruction, mixed rich-support reduction, and the
  mixed-support-to-frontier crosswalk,
  read
  [`docs/radius-blocker-vertex-circle-pilot.md`](docs/radius-blocker-vertex-circle-pilot.md)
  and
  [`docs/n9-full-radius-blocker-vertex-circle-packet.md`](docs/n9-full-radius-blocker-vertex-circle-packet.md)
  and
  [`docs/n9-radius-blocker-shape-sweep.md`](docs/n9-radius-blocker-shape-sweep.md)
  and
  [`docs/n9-radius-blocker-order-reduction.md`](docs/n9-radius-blocker-order-reduction.md)
  and
  [`docs/n9-radius-blocker-rich-projection-pilot.md`](docs/n9-radius-blocker-rich-projection-pilot.md)
  and
  [`docs/n9-radius-blocker-rich-quotient-pilot.md`](docs/n9-radius-blocker-rich-quotient-pilot.md)
  and
  [`docs/n9-radius-blocker-rich-quotient-sweep.md`](docs/n9-radius-blocker-rich-quotient-sweep.md)
  and
  [`docs/n9-radius-blocker-rich-extension-neighborhood.md`](docs/n9-radius-blocker-rich-extension-neighborhood.md)
  and
  [`docs/n9-radius-blocker-rich-extension-product-pilot.md`](docs/n9-radius-blocker-rich-extension-product-pilot.md)
  and
  [`docs/n9-radius-blocker-rich-extension-product-sweep.md`](docs/n9-radius-blocker-rich-extension-product-sweep.md)
  and
  [`docs/n9-all-five-rich-support-obstruction.md`](docs/n9-all-five-rich-support-obstruction.md).
  For the follow-up mixed four/five support reduction, read
  [`docs/n9-mixed-rich-support-reduction.md`](docs/n9-mixed-rich-support-reduction.md)
  and
  [`docs/n9-mixed-rich-frontier-crosswalk.md`](docs/n9-mixed-rich-frontier-crosswalk.md).
- For the stored geometric gates and fixed-order widenings on the block-6
  fragile-cover negative control, read
  [`docs/block6-fragile-vertex-circle-extension-audit.md`](docs/block6-fragile-vertex-circle-extension-audit.md).
- For the block-6 fifth/sixth-row survivor diagnostics, which explain why
  very local closure subclaims fail before the stronger full-extension gates
  take over, read
  [`docs/block6-fragile-fifth-row-obstruction-catalog.md`](docs/block6-fragile-fifth-row-obstruction-catalog.md)
  and
  [`docs/block6-fragile-sixth-row-survivor-catalog.md`](docs/block6-fragile-sixth-row-survivor-catalog.md).
- For the rich-triple closure / bootstrap-core bridge fork, read
  [`docs/bootstrap-core-bridge.md`](docs/bootstrap-core-bridge.md).
- For the bootstrap-core rank/capacity crosswalk on current fixed-row
  frontier motifs, read
  [`docs/bootstrap-core-crosswalk.md`](docs/bootstrap-core-crosswalk.md).
- For the bootstrap-core / vertex-circle overlay on the tight `n=9`
  non-ear-orderable rows, read
  [`docs/bootstrap-vertex-circle-overlay.md`](docs/bootstrap-vertex-circle-overlay.md).
- For the follow-up T12 forcing-target ledger naming the missing row centers
  and direct private-pair contacts, read
  [`docs/bootstrap-t12-forcing-targets.md`](docs/bootstrap-t12-forcing-targets.md).
- For the row-pressure refinement classifying those missing T12 row centers
  by core deficit, deletion-closure exposure, and private-halo support, read
  [`docs/bootstrap-t12-row-pressure.md`](docs/bootstrap-t12-row-pressure.md).
- For the closure-exposed subpacket isolating the two activation-ready T12
  row-pressure rows, read
  [`docs/bootstrap-t12-closure-exposed.md`](docs/bootstrap-t12-closure-exposed.md).
- For the one-outside-label subpacket isolating the three singleton-support
  T12 row-pressure rows, read
  [`docs/bootstrap-t12-one-outside.md`](docs/bootstrap-t12-one-outside.md).
- For the outside-pair subpacket isolating the remaining pair-supported T12
  row-pressure row, read
  [`docs/bootstrap-t12-outside-pair.md`](docs/bootstrap-t12-outside-pair.md).
- For the role-sensitive T12 activation-support requirement ledger separating
  connector pairs and strict-edge endpoint sets from unproved row forcing, read
  [`docs/bootstrap-t12-activation-requirements.md`](docs/bootstrap-t12-activation-requirements.md).
- For the joined T12 bridge-target map that names the exact next lemma target
  for each missing row, read
  [`docs/bootstrap-t12-bridge-target-map.md`](docs/bootstrap-t12-bridge-target-map.md).
- For the hard strict-endpoint subpacket isolating rows `151:7` and `151:8`,
  read
  [`docs/bootstrap-t12-hard-strict-endpoints.md`](docs/bootstrap-t12-hard-strict-endpoints.md).
- For the open connector-pair subpacket isolating row `151:5`, read
  [`docs/bootstrap-t12-open-connector-pair.md`](docs/bootstrap-t12-open-connector-pair.md).
- For the relation-sufficient row subpacket isolating rows `81:3`, `81:8`,
  and `151:6`, read
  [`docs/bootstrap-t12-relation-sufficient-rows.md`](docs/bootstrap-t12-relation-sufficient-rows.md).
- For the focused `81:3` closure target, where full-row deletion-closure
  exposure, relation sufficiency, and the final T12 connector role meet, read
  [`docs/bootstrap-t12-81-3-closure-target.md`](docs/bootstrap-t12-81-3-closure-target.md).
- For the follow-up `81:3` rich-triple connector contract, which reduces the
  target from full-row forcing to the pair `[0,1]` and records the exact
  connector-avoiding escape, read
  [`docs/bootstrap-t12-81-3-rich-triple-contract.md`](docs/bootstrap-t12-81-3-rich-triple-contract.md).
- For the order-resolved `81:3` fixed-row escape audit, where label `6`
  appears only after center `3` in the fixed singleton-rich closure, read
  [`docs/bootstrap-t12-81-3-order-escape.md`](docs/bootstrap-t12-81-3-order-escape.md).
- For the relaxed `81:3` escape-candidate scans, auxiliary/rich-support CSPs,
  and trigger-family uniqueness audit, which probe center-`3` connector and
  center-`6` supply escapes around source `81`, read
  [`docs/bootstrap-t12-81-3-escape-candidates.md`](docs/bootstrap-t12-81-3-escape-candidates.md)
  and
  [`docs/bootstrap-t12-81-3-escape-one-row-drop.md`](docs/bootstrap-t12-81-3-escape-one-row-drop.md),
  then
  [`docs/bootstrap-t12-81-3-escape-two-row-drop.md`](docs/bootstrap-t12-81-3-escape-two-row-drop.md)
  and
  [`docs/bootstrap-t12-81-3-escape-full-neighborhood.md`](docs/bootstrap-t12-81-3-escape-full-neighborhood.md),
  plus
  [`docs/bootstrap-t12-81-3-escape-auxiliary-csp.md`](docs/bootstrap-t12-81-3-escape-auxiliary-csp.md)
  and
  [`docs/bootstrap-t12-81-3-trigger-uniqueness.md`](docs/bootstrap-t12-81-3-trigger-uniqueness.md),
  then
  [`docs/bootstrap-t12-81-3-escape-rich-support-csp.md`](docs/bootstrap-t12-81-3-escape-rich-support-csp.md).
- For the source-`81` row-`8` singleton-support audit, where all fixed and
  one-row-drop activation-row survivors keep the original row `8`, read
  [`docs/bootstrap-t12-81-8-singleton-support-audit.md`](docs/bootstrap-t12-81-8-singleton-support-audit.md).
- For the source-`151` row-`6` outside-pair audit, where all fixed and
  one-row-drop activation-row survivors keep the original row `6`, read
  [`docs/bootstrap-t12-151-6-outside-pair-audit.md`](docs/bootstrap-t12-151-6-outside-pair-audit.md).
- For the source-`151` singleton-support audit covering rows `5` and `8`,
  where all fixed and one-row-drop activation-row survivors keep the original
  target rows, read
  [`docs/bootstrap-t12-151-singleton-support-audit.md`](docs/bootstrap-t12-151-singleton-support-audit.md).
- For fixed-selection stuck-set mining around the bridge/peeling program, read
  [`docs/stuck-set-miner.md`](docs/stuck-set-miner.md).
- For search patterns, read [`docs/candidate-patterns.md`](docs/candidate-patterns.md).
- For known bad proof routes, read [`docs/failed-ideas.md`](docs/failed-ideas.md).
- For the verification standard, read [`docs/verification-contract.md`](docs/verification-contract.md).
- For archive synthesis provenance, read [`inventory.json`](inventory.json),
  [`kernels.json`](kernels.json), [`contradictions.md`](contradictions.md),
  and [`dropped_kernels.md`](dropped_kernels.md).
- For formalization alignment, read [`docs/formalization.md`](docs/formalization.md).
- For possible OEIS connections, read
  [`docs/oeis-possibilities.md`](docs/oeis-possibilities.md).
- For repository-level Codex guidance, read [`AGENTS.md`](AGENTS.md).
- For runnable verification, start with [`scripts/verify_candidate.py`](scripts/verify_candidate.py).
- For current work items, see [`docs/review-priorities.md`](docs/review-priorities.md),
  [`docs/codex-backlog.md`](docs/codex-backlog.md), and the live
  [open GitHub issues](https://github.com/davidiach/erdos97/issues).

## Problem

Let `P` be a strictly convex polygon in the Euclidean plane with vertex set `V`, `|V| = n >= 5`. For a vertex `v`, define

```text
E(v) = max_{r > 0} #{ w in V \ {v} : |vw| = r }.
```

The question is whether every convex polygon must have some vertex `v` with `E(v) <= 3`.

Equivalently, can one find a strictly convex polygon whose every vertex has **four** other vertices on a circle centered at that vertex?

A counterexample consists of:

```text
n >= 5
strictly convex points p_0,...,p_{n-1}
4-sets S_i subset {0,...,n-1} \ {i}
```

such that, for each center `i`, all values

```text
|p_i - p_j|^2,  j in S_i
```

are equal. The radius may depend on `i`; the selected set may depend on `i`; the directed incidence graph need not be symmetric.

## Current status in this repo

Official/global status remains falsifiable/open.

No general proof and no counterexample are claimed.

The selected-witness incidence method rules out `n <= 8` in this repo-local,
machine-checked finite-case sense. In the `n=7`
equality case, the 720 pointed Fano patterns fall into 54 cyclic-dihedral
classes; in every case the common-witness chord map has cycle type `7+7+7`,
so the required perpendicularity relation has an odd cycle. See
[`docs/n7-fano-enumeration.md`](docs/n7-fano-enumeration.md).

For `n=8`, [`scripts/enumerate_n8_incidence.py`](scripts/enumerate_n8_incidence.py)
derives indegree regularity from the column-pair cap, enumerates all necessary
incidence survivors, and reduces them to 15 canonical classes. Exact
cyclic-order and perpendicular-bisector/equal-distance checks then leave no
strictly convex realization for those classes. See
[`docs/n8-incidence-enumeration.md`](docs/n8-incidence-enumeration.md) and
[`docs/n8-exact-survivors.md`](docs/n8-exact-survivors.md). External/public
theorem claims should still get independent review of the computer-assisted
artifacts.

The crossing-bisector, mutual-rhombus, phi 4-cycle rectangle-trap, cyclic
crossing-CSP, and vertex-circle order filters now exactly kill several
previously live fixed selected-witness patterns, including
`B12_3x4_danzer_lift`, `B20_4x5_FR_lift`, `C17_skew`, `C20_pm_4_9`,
`C16_pm_1_6`, `C13_pm_3_5`, `C9_pm_2_4`, `P18_parity_balanced`, and
`P24_parity_balanced`. The phi 4-cycle rectangle-trap filter also kills a
registered fixed `n=9` selected-witness pattern containing
`{0,6}->{2,8}->{1,5}->{4,7}->{0,6}`. These are fixed-pattern obstructions, not
a general proof of the problem.

A review-pending exhaustive `n=9` vertex-circle checker now records a candidate
repo-local finite-case extension: the cross-check leaves 184 full
selected-witness assignments after the pair/crossing/count filters, and the
vertex-circle filter kills all 184 by exact self-edge or strict-cycle
obstructions. This is not yet promoted to the source-of-truth strongest local
result; independent review is required before any public theorem-style claim.
The companion Kalmanson self-edge replay stores one strict Kalmanson
self-edge certificate for each of the same 184 terminal assignments, giving a
compact certificate-only audit path. It is also review-pending and does not
promote `n=9`.
Its independent stored-input replay checks the same JSON rows, incidence
filters, quotients, self-edge records, assignment uniqueness, and digest
without importing the Kalmanson generator module.
The companion input-data audit checks the stored row0 witness coverage and
summary arithmetic without rerunning the brancher. An incidence-filter audit
checks the row-level two-overlap crossing, witness-pair cap, and
selected-indegree cap tables. A fixed-center-order replay checks agreement
with the dynamic minimum-remaining-options brancher but still does not prove
the pruning lemmas. A strict-edge geometry audit checks the local
proper-interval inequality generator for all candidate selected rows. A
quotient-soundness audit checks selected-distance quotient status agreement on
the stored local-core and frontier rows. A partial-pruning audit checks all
nonempty selected-row subsets of the stored 184 frontier assignments for
monotone obstruction persistence and checker/replay status agreement only.
A frontier-assignment audit checks the stored frontier rows directly against
the base row-shape, crossing, witness-pair, and selected-indegree predicates.
A branch-option audit compares the fixed-order branch helper options and
maintained count arrays against a direct recomputation on every
no-vertex-circle fixed-order search state. A dynamic-MRO choice audit replays
the actual minimum-remaining-options brancher and checks every reached state
against direct all-center option counts and first-minimum tie breaking. A
frontier-coverage crosswalk regenerates the 184 dynamic no-vertex complete
assignments and compares them row-for-row with the stored frontier
classification artifact. A dihedral-orbit audit independently replays the
18 cyclic/reflection relabelings for the stored 16 motif representatives and
checks orbit sizes, disjointness, and assignment-to-orbit maps.
A motif-obstruction audit then treats those 16 stored representatives as
input and verifies their stored self-edge equality paths or strict-cycle edge
records with a small local quotient replay.
A local-core subset audit checks that each compact local-core packet is an
actual subset of its full motif representative and already obstructs by a
direct quotient replay.
A focused packet catalog audit checks that the 12 proof-facing focused
local-lemma packets agree with the source template packets, template catalog,
and aggregate focused-note crosschecks; this is packet/catalog bookkeeping only.
See [`docs/n9-vertex-circle-exhaustive.md`](docs/n9-vertex-circle-exhaustive.md).

An incoming `n=10` singleton-slice continuation is now recorded as a
review-pending finite-case draft: all 126 row0 singleton slices report zero
full assignments, with 4,142,738 total visited nodes and no aborted slices.
The artifact is an audit target only and is not promoted to the source-of-truth
strongest local result. See
[`docs/n10-vertex-circle-singleton-slices.md`](docs/n10-vertex-circle-singleton-slices.md).

Round two first added an exact compact Kalmanson/Farkas certificate for one
fixed `C19_skew` selected-witness pattern and one fixed cyclic order:
`[18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1]`. The checked certificate is
`data/certificates/round2/c19_kalmanson_known_order_two_unsat.json`; the earlier
94-inequality certificate remains checked as provenance.

A follow-up SMT refinement now kills the fixed abstract `C19_skew` pattern
across all cyclic orders: every cyclic order contains a two-inequality
Kalmanson inverse-pair obstruction after selected-distance quotienting. The
checked certificate is
`data/certificates/c19_skew_all_orders_kalmanson_z3.json`, and the verifier is
`scripts/check_kalmanson_two_order_z3.py`. This retires the registered sparse
`C19_skew` fixed-pattern lead, but it is still not a proof of Erdos #97.

Separate sampled-prefix C19 artifacts record a prefix/fourth/fifth refinement
chain for the first 480 deterministic three-boundary-prefix states. The
catalog-prefilter sweep over indices 288-479 keeps the two-row lookup intact,
adds three checked unit-support prefilter rules for the eight two-row misses,
and reduces ordinary fifth-pair Farkas fallbacks from eight to zero. This is
sampled-window work only, not a new all-order C19 claim. See
[`docs/c19-kalmanson-prefix-window-catalog-prefilter-sweep.md`](docs/c19-kalmanson-prefix-window-catalog-prefilter-sweep.md).

A C13 Kalmanson pilot kills one registered non-natural
`C13_sidon_1_2_4_10` order `[5,0,10,8,9,7,4,6,2,11,12,3,1]` by the exact
certificate
`data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json`.
The follow-up exact order search now kills this fixed C13 Sidon pattern across
all cyclic orders; see `docs/kalmanson-two-order-search.md`. This does not
settle the larger sparse frontier or prove Erdos #97.

A later sparse-frontier probe tested the larger Sidon entries
`C25_sidon_2_5_9_14` and `C29_sidon_1_3_7_15`. The C25 Kalmanson-filter
survivor is exactly killed by vertex-circle and Altman filters. The recorded
C29 order first survived the lightweight fixed-order exact sweep, the
two-inequality Kalmanson inverse-pair search, the metric LP diagnostic, and a
slow global Ptolemy NLP diagnostic, but it is now exactly killed by the
165-inequality fixed-order Kalmanson/Farkas certificate
`data/certificates/c29_sidon_fixed_order_kalmanson_165_unsat.json`. This is
still only a fixed selected-witness pattern plus fixed cyclic-order
obstruction, not an all-order C29 result and not a counterexample claim. See
[`data/certificates/c25_c29_sparse_frontier_probe.json`](data/certificates/c25_c29_sparse_frontier_probe.json)
and [`docs/sparse-frontier-diagnostic.md`](docs/sparse-frontier-diagnostic.md).

The previous best numerical near-miss was `B12_3x4_danzer_lift`. It remains a
useful degeneration diagnostic, but the fixed selected pattern is now exactly
killed by the mutual-rhombus midpoint filter. The saved numerical artifact is
still retained as provenance for the failed route, **not** as a solution.

The best saved B12 object is **not** a counterexample: its max
selected-distance spread is about `0.0068`, and its convexity margin is about
`1e-6`.

Any claimed counterexample needs exact coordinates, or an exact algebraic
certificate, verifying the distance equalities and strict convexity.

Key diagnostics for the best saved near-miss:

```text
n: 12
pattern: B12_3x4_danzer_lift
max squared-distance spread: 0.006806368780585714
RMS equality residual:       0.0019599509549614457
convexity margin:            9.999999943508973e-07
minimum edge length:         0.0007465865604262556
status: numerical artifact only; fixed selected pattern exactly killed
```

See [`STATE.md`](STATE.md) for the most compact working summary and
[`docs/canonical-synthesis.md`](docs/canonical-synthesis.md) for the full
canonical synthesis.

## Trust levels used here

Use these labels consistently:

- **THEOREM**: fully proved and checked.
- **LEMMA**: fully justified local result, preferably with tests or formalizable proof.
- **CONJECTURE**: plausible but unproved mathematical claim.
- **HEURISTIC**: useful search guidance, not a proof ingredient.
- **NUMERICAL_EVIDENCE**: floating-point result; never a proof of equality.
- **FAILED_APPROACH**: route that currently appears invalid or degenerate.
- **LITERATURE_RISK**: reference or missing reference that could change the project status.
- **INCIDENCE_COMPLETENESS**: exhaustive finite enumeration under proved incidence constraints.
- **EXACT_OBSTRUCTION**: exact arithmetic, algebraic, interval, SMT, or formal certificate killing a pattern.
- **EXACTIFICATION**: algebraic, interval, SMT, or certificate work.
- **SAT_SMT**: finite abstraction or solver encoding.
- **INCIDENCE_PATTERN**: directed 4-neighbor pattern proposal or enumeration.
- **COUNTEREXAMPLE_CANDIDATE**: candidate requiring independent verification; not a counterexample.

## Repository map

```text
.
├── AGENTS.md                         # repository-level Codex guidance
├── README.md
├── RESULTS.md
├── STATE.md
├── metadata/
│   └── erdos97.yaml                  # canonical status metadata snapshot
├── pyproject.toml
├── src/erdos97/search.py              # main search/verification engine
├── src/erdos97/incidence_filters.py   # exact incidence obstruction filters
├── src/erdos97/stuck_sets.py          # fixed-selection stuck-set miner core
├── src/erdos97/motif_fingerprint.py   # cyclic/dihedral motif fingerprints
├── src/erdos97/stuck_motif_search.py  # bounded SMT stuck-motif search
├── src/erdos97/stuck_motif_sweep.py   # motif sweep and geometry smoke tests
├── src/erdos97/n7_fano.py             # exact n=7 Fano enumeration
├── scripts/                           # thin CLI helpers
├── tests/                             # smoke tests and incidence checks
├── docs/
│   ├── index.md                       # documentation navigation
│   ├── upstream-alignment.md          # relation to teorth/erdosproblems
│   ├── reviewer-guide.md              # independent audit instructions
│   ├── formalization.md               # Lean/formalization alignment
│   ├── oeis-possibilities.md          # exploratory OEIS notes
│   ├── canonical-synthesis.md         # long-form canonical project synthesis
│   ├── claims.md                      # proved vs heuristic statements
│   ├── candidate-patterns.md          # ranked incidence patterns
│   ├── failed-ideas.md                # failed arguments to avoid repeating
│   ├── exactification-plan.md         # numerical-to-exact certificate route
│   ├── stuck-set-miner.md             # bridge/peeling obstruction tooling
│   ├── n8-incidence-enumeration.md    # n=8 incidence-completeness proof
│   ├── n8-exact-survivors.md          # n=8 exact survivor obstructions
│   ├── mutual-rhombus-filter.md       # exact fixed-pattern filters
│   ├── vertex-circle-order-filter.md  # exact cyclic-order distance filter
│   ├── sat-smt-plan.md                # finite abstraction plan
│   ├── literature-risk.md             # what has/has not been checked
│   └── verification-contract.md       # candidate acceptance requirements
├── data/
│   ├── incidence/n7_fano_dihedral_representatives.json
│   ├── incidence/n8_incidence_completeness.json
│   ├── incidence/n8_reconstructed_15_survivors.json
│   ├── patterns/candidate_patterns.json
│   └── runs/best_B12_slsqp_m1e-6.json
└── certificates/
    ├── best_B12_certificate_template.json
    ├── n8_exact_analysis.json
    └── n8_polynomial_systems.txt
```

New generated checked certificates should normally live under
`data/certificates/`. The top-level `certificates/` directory is retained for
legacy n=8 artifacts and manual templates whose paths are already referenced by
docs, tests, and manifests.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
make verify-fast
```

`make verify-lint` runs the sub-minute text/status/provenance/ruff tier
without pytest. The default pytest configuration excludes tests marked
`artifact`, `slow`, or `exhaustive`; run `python -m pytest -q -m ""` when you
intentionally want the full marker set.

If `make` is not available, run the fast tier directly:

```bash
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
python scripts/check_artifact_provenance.py
git diff --check
python -m ruff check .
python -m pytest -q
```

Artifact and frontier checks are slower and should be run before finite-case,
certificate, or public theorem-style updates:

```bash
make verify-artifacts
```

The manual/scheduled artifact-audit workflow runs the same artifact commands
with command, commit, Python version, dependency snapshot, elapsed-time, and
output-hash metadata. It also includes the dated official-status consistency
check:

```bash
make audit-artifacts
```

If `make` is unavailable, treat `Makefile` and
`scripts/run_artifact_audit.py` as the source of truth for the current raw
command set. The current raw commands are:

```bash
python scripts/check_status_consistency.py --max-official-status-age-days 90
python scripts/check_artifact_provenance.py
python scripts/independent_check_n8_artifacts.py --check --json
python scripts/enumerate_n8_incidence.py --summary
python scripts/analyze_n8_exact_survivors.py --check --json
python scripts/check_round2_certificates.py
python scripts/check_kalmanson_certificate.py data/certificates/round2/c19_kalmanson_known_order_two_unsat.json --summary-json
python scripts/check_kalmanson_certificate.py data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json --summary-json
python scripts/check_kalmanson_two_order_search.py --name C13_sidon_1_2_4_10 --n 13 --offsets 1,2,4,10 --assert-obstructed --assert-c13-expected --json
python scripts/check_kalmanson_two_order_z3.py --certificate data/certificates/c19_skew_all_orders_kalmanson_z3.json --assert-unsat
python scripts/analyze_kalmanson_inverse_pair_templates.py --assert-expected --json
python scripts/analyze_kalmanson_sparse_frontier_templates.py --assert-expected --json
python scripts/check_speculative_circulant_frontier_obstructions.py --check --json
python scripts/analyze_kalmanson_z3_clauses.py --assert-expected --check-artifact reports/c19_kalmanson_z3_clause_diagnostics.json
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
python scripts/analyze_n9_vertex_circle_obstruction_shapes.py --check --assert-expected --json
python scripts/analyze_n9_vertex_circle_motif_families.py --check --assert-expected --json
python scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_input_audit.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_branch_options.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_dynamic_mro_choices.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_mro_branching_replay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check --assert-expected --json
python scripts/check_n9_kalmanson_selfedge.py --verify-certificate data/certificates/n9_kalmanson_selfedge.json --assert-expected --json
python scripts/check_n9_kalmanson_selfedge_independent_replay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_local_core_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_local_core_subset_audit.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_core_templates.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_frontier_motif_classification.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_dihedral_orbit_audit.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_motif_obstruction_audit.py --check --assert-expected --json
python scripts/compare_n9_vertex_circle_frontier.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_frontier_assignment_audit.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_quotient_soundness.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_partial_pruning.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_self_edge_path_join.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_self_edge_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_strict_cycle_path_join.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_strict_cycle_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_local_lemmas.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_local_lemma_simple_replay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t01_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t02_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t03_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t04_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t04_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t05_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t05_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t06_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t06_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t07_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t07_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t08_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t08_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t09_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t09_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t10_strict_cycle_minireplay.py --check --assert-expected --json
python scripts/check_n9_t10_paired_square_entry.py --check --assert-expected --json
python scripts/check_relation_skeleton_catalog.py --check --assert-expected --json
python scripts/check_relation_skeleton_local_lemma_crosswalk.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t11_strict_cycle_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t12_strict_cycle_minireplay.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_product_cancellations.py --check --json
python scripts/check_n9_row_ptolemy_family_signatures.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_order_sensitivity.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_order_admissible_census.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_admissible_gap_replay.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_gap_self_edge_cores.py --check --assert-expected --json
python scripts/check_n9_base_apex_low_excess_ledgers.py --check --json
python scripts/check_n9_base_apex_escape_budget.py --check --json
python scripts/check_n9_selected_baseline_escape_budget_overlay.py --check --json
python scripts/check_n9_selected_baseline_d3_escape_class_crosswalk.py --check --json
python scripts/check_n9_selected_baseline_d3_vertex_circle_template_join.py --check --json
python scripts/check_n9_d3_escape_slice.py --check --json
python scripts/check_n9_base_apex_d3_escape_frontier_packet.py --check --json
python scripts/check_n9_base_apex_low_excess_escape_ladder.py --check --json
python scripts/check_n9_base_apex_low_excess_escape_crosswalk.py --check --json
python scripts/check_n9_base_apex_d3_p19_incidence_capacity_pilot.py --check --json
python scripts/check_n9_base_apex_d3_incidence_capacity_packet.py --check --json
python scripts/check_n9_base_apex_d3_artifact_join.py --check --json
python scripts/check_n9_base_apex_audit_path.py --check --json
python scripts/check_bridge_lemma_frontier.py --check --assert-expected --json
python scripts/check_bootstrap_core_crosswalk.py --check --assert-expected --json
python scripts/check_bootstrap_vertex_circle_overlay.py --check --assert-expected --json
python scripts/check_bootstrap_t12_forcing_targets.py --check --assert-expected --json
python scripts/check_bootstrap_t12_row_pressure.py --check --assert-expected --json
python scripts/check_bootstrap_t12_closure_exposed.py --check --assert-expected --json
python scripts/check_bootstrap_t12_one_outside.py --check --assert-expected --json
python scripts/check_bootstrap_t12_outside_pair.py --check --assert-expected --json
python scripts/check_bootstrap_t12_activation_requirements.py --check --assert-expected --json
python scripts/check_bootstrap_t12_bridge_target_map.py --check --assert-expected --json
python scripts/check_bootstrap_t12_hard_strict_endpoints.py --check --assert-expected --json
python scripts/check_bootstrap_t12_open_connector_pair.py --check --assert-expected --json
python scripts/check_bootstrap_t12_relation_sufficient_rows.py --check --assert-expected --json
python scripts/check_bootstrap_t12_81_3_closure_target.py --check --assert-expected --json
python scripts/check_bootstrap_t12_81_3_rich_triple_contract.py --check --assert-expected --json
python scripts/check_bootstrap_t12_81_3_order_escape.py --check --assert-expected --json
python scripts/check_bootstrap_t12_81_3_escape_candidates.py --check --assert-expected --json
python scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py --check --assert-expected --json
python scripts/check_bootstrap_t12_81_3_escape_two_row_drop.py --check --assert-expected --json
python scripts/check_bootstrap_t12_81_3_escape_full_neighborhood.py --check --assert-expected --json
python scripts/check_bootstrap_t12_81_3_escape_auxiliary_csp.py --check --assert-expected --json
python scripts/check_bootstrap_t12_81_3_trigger_uniqueness.py --check --assert-expected --json
python scripts/check_bootstrap_t12_81_3_escape_rich_support_csp.py --check --assert-expected --json
python scripts/check_bootstrap_t12_81_8_singleton_support_audit.py --check --assert-expected --json
python scripts/check_bootstrap_t12_151_6_outside_pair_audit.py --check --assert-expected --json
python scripts/check_bootstrap_t12_151_singleton_support_audit.py --check --assert-expected --json
python scripts/check_closure_activation_wrong_fourth_negative_control.py --check --assert-expected --json
python scripts/check_closure_activation_negative_controls.py --check --assert-expected --json
python scripts/check_bootstrap_t12_anti_activation_negative_control.py --check --assert-expected --json
python scripts/check_closure_visibility_anti_activation_control.py --check --assert-expected --json
python scripts/check_block6_fragile_vertex_circle_extension.py --check --assert-expected --json
python scripts/check_block6_terminal_crossing_vertex_circle_sample.py --check --assert-expected --json
python scripts/check_block6_terminal_crossing_vertex_circle_sample.py --full-sweep --check --assert-expected --json
python scripts/check_block6_fixed_order_vertex_circle_probe.py --check --assert-expected --json
python scripts/check_block6_shuffle_order_vertex_circle_sweep.py --check --assert-expected --json
python scripts/check_block6_reversed_block_shuffle_vertex_circle_escape.py --check --assert-expected --json
python scripts/check_block6_reversed_block_clean_kalmanson.py --check --assert-expected --json
python scripts/check_block6_reversed_block_two_stage_closure.py --check --assert-expected --json
python scripts/check_block6_forward_block_two_orientation_closure.py --check --assert-expected --json
python scripts/check_block6_oriented_block_reversal_closure.py --check --assert-expected --json
python scripts/check_n10_turn_row0_pilot.py --check --assert-expected --json
python scripts/check_n10_turn_row0_escape_self_edges.py --check --assert-expected --json
python scripts/check_n10_singleton_input_audit.py --check --assert-expected --json
python scripts/check_n10_vertex_circle_singletons.py --assert-expected --spot-check-row0 0 --spot-check-row0 63 --spot-check-row0 125
python scripts/check_n10_secondary_singleton_replay.py --check --assert-expected --json
```

Useful exploratory commands:

```bash
erdos97-search --list-patterns
erdos97-search --verify data/runs/best_B12_slsqp_m1e-6.json --tol 1e-6
python scripts/interval_verify_candidate.py data/runs/best_B12_slsqp_m1e-6.json
python scripts/check_mutual_rhombus_filter.py --assert-expected
python scripts/check_vertex_circle_order_filter.py --pattern P18_parity_balanced --search --assert-obstructed
python scripts/check_min_radius_filter.py --pattern C19_skew --assert-pass
```

For a version-matched reproduction environment, install the checked snapshot
before installing this package:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
pip install -e . --no-deps
```

Run a small search:

```bash
erdos97-search --pattern B12_3x4_danzer_lift --mode polar --restarts 10 --max-nfev 1000 --out data/runs/new_attempt.json
```

Optional dependencies:

```bash
pip install sympy z3-solver
```

## Research hygiene

1. Do not present floating-point equalities as exact.
2. Keep optional search heuristics separate from necessary mathematical constraints.
3. Record failed approaches with enough detail that future work can avoid repeating them.
4. Prefer small reproducible JSON artifacts over screenshots or prose-only claims.
5. Any proposed counterexample should include an independent verifier output and then an exactification plan.

## Known nearby examples

The 3-neighbor version is false: Danzer produced a 9-point convex polygon where every vertex has 3 equidistant vertices, and Fishburn--Reeds produced a 20-point convex polygon where every vertex has 3 equidistant vertices at a common radius. These do not automatically extend to the 4-neighbor target.

A 1975 Erdos paper reports an unpublished all-`k` Danzer claim, but the official #97 page says this was not repeated later and was presumably mistaken. This repository treats that statement as unverified literature risk, not as a `k=4` counterexample; see [`docs/literature-risk.md`](docs/literature-risk.md).

## Contribution policy

Contributions are welcome if they are reproducible and clearly labelled. Especially useful contributions:

- new incidence patterns satisfying known necessary filters;
- independent verification scripts;
- exact obstruction lemmas;
- interval/SOS/SMT certificates for restricted classes;
- numerical candidates with robust convexity margins and residual below `1e-10`.

Please avoid presenting numerical near-equalities as counterexamples.

## License and citation

Code is licensed under the MIT License. Research notes, documentation, data artifacts, issue templates, and certificate templates are licensed under CC-BY-4.0. See [`LICENSE.md`](LICENSE.md).

If you use this repository, please cite it using [`CITATION.cff`](CITATION.cff).

## Maintenance checklist

- Run `make verify-fast` or the equivalent raw fast-tier commands.
- Run `make verify-artifacts` before finite-case, certificate, or public
  theorem-style updates, or record why a command could not be run.
- Run `make audit-artifacts` for audit metadata; it includes the dated
  official-status consistency check.
- Run `python scripts/check_text_clean.py`.
- Run `python scripts/check_status_consistency.py`.
- Confirm this README still says no general proof and no counterexample are claimed.
- Create labels matching `.github/labels.yml`.
- Keep current-work pointers aligned with `docs/review-priorities.md`,
  `docs/codex-backlog.md`, and the live GitHub issue list.
