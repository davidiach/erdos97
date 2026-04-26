# Literature-risk notes

The baseline is intentionally modest: no proof and no counterexample are
claimed here.

## Nearby facts to track

- Danzer constructed a 9-point convex polygon where every vertex has three
  equidistant vertices. This is a `k=3` example, not a `k=4` counterexample.[^digest]
- Fishburn--Reeds constructed a 20-point convex polygon where every vertex has
  three unit-distance neighbors. This is again `k=3`, with a uniform distance,
  and does not imply the variable-radius `k=4` target.[^digest]
- Common-radius or unit-distance reductions belong to a stricter subcase.
  Convex unit-distance bounds may settle that subcase without touching the
  full variable-radius problem.[^syn]

## Current risks

- Recheck the public Erdos Problems listing and any formal-conjectures records
  before announcing a solution or counterexample.[^repo]
- Verify exact statements and citations for Danzer and Fishburn--Reeds before
  using them in a paper-style introduction.[^digest]
- Keep the uniform-radius literature separate from the selected-witness problem
  where each center may have its own radius.[^syn]
- Before claiming a new obstruction, search related work on repeated distances
  in convex polygons, convex unit distances, Delaunay/order-k Voronoi
  degeneracies, and oriented-matroid realizability with metric constraints.[^repo]
- Treat any numerical near-equality as only numerical evidence unless it has an
  exact or certified verification artifact.[^repo]

[^digest]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/01_USEFUL_FINDINGS_DIGEST.md`.
[^syn]: Source file: `erd archive/outputs/erdos97_synthesis.md`.
[^repo]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/16_repo_handoff_and_claim_taxonomy.md`.
