# STATE.md - Erdos Problem #97 working state

Status: no general proof and no counterexample are claimed.

This is the short working dashboard. For the long-form canonical synthesis,
claim taxonomy, failed-route reconciliation, and source/hash inventory, read
`docs/canonical-synthesis.md` before adding new claims, search branches, or
proof attempts.

Canonical status metadata is recorded in `metadata/erdos97.yaml`. It separates
the official/global falsifiable/open status from this repo's local finite-case
artifacts.

## Target

Find, or rule out, a strictly convex polygon with vertices
`p_0,...,p_{n-1}` such that every center `i` has a 4-set
`S_i` of other vertices with all squared distances `|p_i-p_j|^2`,
`j in S_i`, equal. Radii and selected 4-sets may vary with `i`;
the directed incidence graph need not be symmetric.[^repo]

## Strongest proved state

The selected-witness method rules out `n <= 8` in this repo-local,
machine-checked finite-case sense. The core filters are the
two-circle cap `|S_a cap S_b| <= 2`, radical-axis crossing/bisection when two
rows share exactly two witnesses, the sharpened incidence count forcing
`n >= 8`, and
the `n=8` column-pair cap forcing all witness indegrees to equal 4.
The older `n=7` Fano enumeration remains in the repo because it is a useful
independent reproduction of the equality-case obstruction.[^small]

For `n=8`, `scripts/enumerate_n8_incidence.py` enumerates all necessary
selected-witness incidence survivors and reduces them to 15 canonical classes.
Exact cyclic-order noncrossing kills 1 class, and exact perpendicular-bisector /
equal-distance algebra kills the other 14. See
`docs/n8-incidence-enumeration.md` and `docs/n8-exact-survivors.md`.
External independent review remains recommended before public theorem-style
claims.

For the general bridge problem, minimality now gives a small proved foothold:
every minimal counterexample admits a partial fragile-cover witness system made
from exact critical 4-ties. This is necessary structure only; the block-6
abstract family shows that fragile-cover hypergraph constraints alone are too
weak. See `docs/minimal-fragile-cover-bridge.md`.

## New exact fixed-pattern obstructions

The crossing-bisector, mutual-rhombus, phi 4-cycle rectangle-trap, cyclic
crossing-CSP, and vertex-circle order filters now exactly kill several
previously live fixed selected-witness patterns. In particular,
`B12_3x4_danzer_lift` is no longer live as a fixed selected pattern: its
mutual-rhombus midpoint equations force labels `[0,4,8]`, `[1,5,9]`,
`[2,6,10]`, and `[3,7,11]` to coincide. The old numerical near-miss remains
useful as a degeneration diagnostic, but not as a counterexample candidate.

Also killed as fixed selected patterns: `B20_4x5_FR_lift`, `C17_skew`,
`C20_pm_4_9`, `C16_pm_1_6`, `C13_pm_3_5`, `C9_pm_2_4`,
`P18_parity_balanced`, and `P24_parity_balanced`. The `P18_parity_balanced`
abstract-incidence obstruction uses the crossing constraints plus the
vertex-circle order strict-cycle filter; `P24_parity_balanced` is already
killed by the finite cyclic crossing CSP.

Round two first added an exact Kalmanson/Farkas fixed-order obstruction for the
registered `C19_skew` selected-witness pattern with offsets `[-8,-3,5,9]` and
cyclic order `[18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1]`. The preferred
compact certificate is a positive integer combination of 2 strict convex
Kalmanson distance inequalities whose coefficient vector is exactly zero after
selected-distance quotienting. The earlier 94-inequality certificate remains
checked as provenance. See `docs/round2/kalmanson_distance_filter.md`.

A follow-up Z3 refinement certificate now kills the fixed abstract `C19_skew`
pattern across all cyclic orders. The certificate stores 7,981 exact forbidden
ordered-quadrilateral pairs; each pair is checked to be a Kalmanson inverse
pair after selected-distance quotienting, and Z3 verifies that the accumulated
cyclic-order constraints are unsatisfiable. See
`docs/kalmanson-two-order-search.md`,
`scripts/check_kalmanson_two_order_z3.py`, and
`data/certificates/c19_skew_all_orders_kalmanson_z3.json`.

A C13 Kalmanson pilot also kills the registered non-natural
`C13_sidon_1_2_4_10` order `[5,0,10,8,9,7,4,6,2,11,12,3,1]` by an exact
2-inequality Kalmanson/Farkas certificate. The follow-up exact order search now
kills this fixed C13 Sidon pattern across all cyclic orders by proving that
every cyclic order contains a two-inequality inverse-pair obstruction. See
`docs/kalmanson-two-order-search.md`.

The phi 4-cycle rectangle-trap filter kills a registered fixed `n=9`
selected-witness pattern with directed cycle
`{0,6}->{2,8}->{1,5}->{4,7}->{0,6}`. The obstruction is the exact determinant
identity `D1 + D3 + D5 + D7 = -4*a*b` under cyclic-order signs `a,b > 0`.
See `docs/phi4-rectangle-trap.md` and
`data/certificates/n9_phi4_rectangle_trap.json`. This is not an `n=9`
completeness result.

A review-pending exhaustive `n=9` vertex-circle checker has been imported from
the 2026-05-03 archive bundle and refactored into
`scripts/check_n9_vertex_circle_exhaustive.py`. It records 184 full
selected-witness systems after the pair/crossing/count filters and kills all
184 by exact vertex-circle self-edge or strict-cycle obstructions. This is a
candidate repo-local finite-case extension only; it does not change the
official/global falsifiable/open status, and it is not promoted beyond the
current `n <= 8` source-of-truth result until independent review.

A 2026-05-05 multi-agent attack adds an independent Gröbner-basis verification
at n=8 (all 15 incidence-completeness survivors unrealizable by algebra alone)
and partial n=9 algebraic corroboration: 150 labelled assignments are killed
by GB={1}, and 18 more by F12's `y_8^2 + 1/4 = 0`. The remaining 16 labelled
assignments in F07/F08/F09/F13 still need replayable real-root /
non-degeneracy decoders before the algebraic route becomes a complete
second-source proof. The same audit reports no soundness defect in the
vertex-circle checker filters. See
`docs/erdos97-attack-2026-05-05.md` and
`data/certificates/2026-05-05/n9_groebner_results.json`. Independent
reviewer audit is still required.

A later incoming `n=10` continuation is now recorded as a
`MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING` artifact at
`data/certificates/n10_vertex_circle_singleton_slices.json`. It covers all 126
row0 singleton slices, reports 4,142,738 total visited nodes, zero full
assignments, and no aborted slices. The repo-native generic checker reproduces
the n=9 counts and spot-checks row0 singleton `0`, but the n=10 package is an
audit target only and is not promoted to the source-of-truth finite-case result.

## Best saved near-miss

The best saved near-miss is still the historical `B12_3x4_danzer_lift`
artifact. It is numerical only, rejected as proof or counterexample, and now
also attached to a fixed selected pattern that is exactly killed by the
mutual-rhombus midpoint filter.[^repo]

Numerical near-misses are not counterexamples. Any solution claim needs exact
coordinates, or an exact algebraic/interval certificate, for both the selected
distance equalities and strict convexity.

```text
n: 12
pattern: B12_3x4_danzer_lift
max squared-distance spread: 0.006806368780585714
RMS equality residual:       0.0019599509549614457
convexity margin:            9.999999943508973e-07
minimum edge length:         0.0007465865604262556
status: numerical artifact only; fixed selected pattern exactly killed
```

The archive also contained two C12 numerical artifacts. They were normalized
under `data/runs/`, but excluded from this dashboard: one fails the `1e-6`
verification threshold and the other collapses to a non-strict configuration.[^comp]

## Top remaining live / unresolved patterns

The registered sparse circulant leads `C13_sidon_1_2_4_10` and `C19_skew` are
now both killed across all cyclic orders by exact two-certificate Kalmanson
order obstructions. This retires those fixed selected-witness patterns as live
counterexample leads.

The global problem remains open: a counterexample could use a different
selected-witness incidence pattern, and the current repository still has no
bridge proving that arbitrary counterexamples reduce to the registered sparse
families.

Retired sparse lead: `C13_sidon_1_2_4_10`, a (13,4,1)
Singer planar-difference-set circulant, is now killed across all cyclic orders
by the exact two-certificate Kalmanson order search. The older numerical
evidence below is retained as historical diagnostic data only.

## Numerical status: C13 Sidon-type circulant

NUMERICAL_EVIDENCE. Constrained SLSQP under hard strict-convexity / edge /
pair margins, polar parameterisation, 20 restarts, seed `2026`, on
`C13_sidon_1_2_4_10`:

```text
n: 13
pattern: C13_sidon_1_2_4_10
margin schedule: 1e-3, 1e-4, 1e-5, 1e-6
RMS equality residual at each margin:  0.848, 0.841, 0.839, 0.838
max squared-distance spread:           3.38, 3.37, 3.37, 3.37
convexity margin achieved:             1e-3, 1e-4, 1e-5, 1e-6 (hits bound)
min edge length:                       3.3e-2, 1.1e-2, 3.3e-3, 1.0e-3
status: equality residual shows an apparent positive plateau; not a
        cluster-collapse signature; numerical only, not a proof
```

The residual does not decrease monotonically as the margin tightens
(`eq_rms` moves only from `0.848` to `0.838` over three orders of
magnitude in margin), and the optimum does not cluster. This is
qualitatively different from the B12 cluster degeneration. It is
consistent with the prior LLM-run conjecture that Sidon-type cohort
patterns form a structural wall against the row-4 matrix bound but are
not realisable by a strictly convex polygon. **It is not a proof.** The
trust label is NUMERICAL_EVIDENCE; the pattern is not promoted to
COUNTEREXAMPLE_CANDIDATE because the simultaneous criteria
(`residual < 1e-10`, `convexity margin > 1e-3`, `min edge length > 1e-3`)
are not met, and -- the opposite reading -- a positive residual does not
by itself constitute an obstruction proof. Independent verification with
different parameterisations (`direct`, `support`) and more restarts is
recommended before any structural claim. See
`docs/sidon-patterns.md` and `data/runs/C13_sidon_m{1e-3,1e-4,1e-5,1e-6}.json`.

The catalog also contains `C25_sidon_2_5_9_14` and `C29_sidon_1_3_7_15`
as cheap-to-define INCIDENCE_PATTERN entries. A 2026-05-05 sparse-frontier
probe found that a C25 Kalmanson-filter survivor is exactly killed by
vertex-circle and Altman filters. The same probe found one fixed C29 cyclic
order that survived the lightweight fixed-order exact filters, the
two-inequality Kalmanson inverse-pair search, the metric LP diagnostic, and a
slow global Ptolemy NLP diagnostic. A later exact full Kalmanson/Farkas
certificate now kills that fixed C29 order:
`data/certificates/c29_sidon_fixed_order_kalmanson_165_unsat.json`. This is a
fixed-order obstruction only; it is not an all-order obstruction for the
abstract C29 pattern and not a counterexample claim. The original probe remains
provenance at `data/certificates/c25_c29_sparse_frontier_probe.json`.

## Top killed approaches

1. Middle-neighbor forest proof: killed by an affine regular 24-gon cycle in
   the proposed middle-neighbor graph.[^forest]
2. `C39_pm_18_19`: killed exactly because adjacent rows share three selected
   targets, violating the two-circle cap.[^n39]
3. Generic rank obstruction: rank `2n-3` at non-solutions is only diagnostic;
   exact solutions have an extra scaling kernel.[^rank]
4. Cube witness pattern as an `n=8` proof: the pattern is obstructed, but this
   is not an exhaustive `n=8` argument.[^syn]
5. Uniform-radius shortcut via `2n-7`: this is a direction-of-bound error; the
   cited result is a lower-bound construction, not the needed upper bound.[^canon]

## Exactification frontier

The current frontier is fixed-pattern certification on special rank-drop loci.
Distance-equality equations are polynomial and center-affine; exact convexity
should be certified with edge-line orientation inequalities. The rank route is
promising only as a conditional program: repair the ear-orderable rank proof,
then prove or refute the bridge that every realizable counterexample admits an
ear-orderable selected witness pattern.[^alg][^rank]

The `n=8` artifacts are now the sharpest computer-assisted proof objects in the
repo. The incidence checker proves completeness of the 15 survivor classes, and
the exact checker verifies the class `3` duplicate certificate, the class `4`
collinearity certificate, the class `14` strict-interior certificate, and the
archived-ID provenance mapping when the archive JSON is available.

## Open literature questions

- Recheck the public Erdos Problems listing before any solution claim.[^repo]
- Pin exact citations and statements for Danzer's 9-point `k=3` example.[^digest]
- Treat the Erdos 1975 unpublished all-`k` Danzer statement as unverified
  literature risk unless a primary construction or exact certificate is found.
- Pin exact citations and statements for the Fishburn--Reeds 20-point
  unit-distance `k=3` example.[^digest]
- Keep convex unit-distance bounds separate from the variable-radius problem.[^syn]
- In particular, do not cite the `2n-7` unit-distance construction as an upper
  bound resolving the uniform-radius subcase.[^canon]
- Search related work on repeated distances, order-k Voronoi degeneracies, and
  metric oriented-matroid realizability before paper-style claims.[^repo]

[^repo]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/16_repo_handoff_and_claim_taxonomy.md`.
[^small]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/02_SMALL_CASES_N5_N6_N7.md`.
[^comp]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/04_COMPUTATIONAL_FINDINGS.md`.
[^forest]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/11_forest_lemma_counterexample_review.md`.
[^n39]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/12_n39_circulant_degeneracy.md`.
[^rank]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/03_RANK_AND_BRIDGE_STATUS.md`.
[^alg]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/04_algebraic_and_semicircle_corrections.md`.
[^digest]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/01_USEFUL_FINDINGS_DIGEST.md`.
[^syn]: Source file: `erd archive/outputs/erdos97_synthesis.md`.
[^canon]: Source file: `docs/canonical-synthesis.md`.
