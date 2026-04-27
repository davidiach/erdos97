# STATE.md - Erdos Problem #97 working state

Status: no general proof and no counterexample are claimed.

This is the short working dashboard. For the long-form canonical synthesis,
claim taxonomy, failed-route reconciliation, and source/hash inventory, read
`docs/canonical-synthesis.md` before adding new claims, search branches, or
proof attempts.

Canonical status metadata is recorded in `metadata/erdos97.yaml`. It separates
the official/global falsifiable-open status from this repo's local finite-case
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
two-circle cap `|S_a cap S_b| <= 2`, radical-axis perpendicularity when two
rows share exactly two witnesses, the incidence count forcing `n >= 7`, and
the `n=8` column-pair cap forcing all witness indegrees to equal 4.
At `n=7`, the equality case forces a chord permutation on 21 chords, and odd
cycle parity contradicts alternating perpendicularity.[^small]

For `n=8`, `scripts/enumerate_n8_incidence.py` enumerates all necessary
selected-witness incidence survivors and reduces them to 15 canonical classes.
Exact cyclic-order noncrossing kills 1 class, and exact perpendicular-bisector /
equal-distance algebra kills the other 14. See
`docs/n8-incidence-enumeration.md` and `docs/n8-exact-survivors.md`.

## Best saved near-miss

The best saved near-miss remains `B12_3x4_danzer_lift`. It is numerical only
and is rejected as proof or counterexample because the residual improves toward
a clustered boundary degeneration.[^repo]

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
status: numerical only, rejected as proof/counterexample
```

The archive also contained two C12 numerical artifacts. They were normalized
under `data/runs/`, but excluded from this dashboard: one fails the `1e-6`
verification threshold and the other collapses to a non-strict configuration.[^comp]

## Top live patterns

1. `B12_3x4_danzer_lift`: leading saved degeneration diagnostic, not a
   counterexample candidate in its current form.[^repo]
2. `B20_4x5_FR_lift`: next block/symmetric margin sweep with anti-clustering
   diagnostics.[^repo]
3. `P18_parity_balanced`: period-2 pattern worth broader numerical search.[^repo]

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
