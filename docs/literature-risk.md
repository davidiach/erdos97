# Literature-risk notes

The baseline is intentionally modest: no general proof and no counterexample
are claimed here.

## Nearby facts to track

- Danzer constructed a 9-point convex polygon where every vertex has three
  equidistant vertices. This is a `k=3` example, not a `k=4` counterexample.[^digest]
- Fishburn--Reeds constructed a 20-point convex polygon where every vertex has
  three unit-distance neighbors. This is again `k=3`, with a uniform distance,
  and does not imply the variable-radius `k=4` target.[^digest]
- Common-radius or unit-distance reductions belong to a stricter subcase.
  Convex unit-distance bounds may settle that subcase without touching the
  full variable-radius problem.[^syn]
- The canonical synthesis corrects a prior uniform-radius shortcut:
  Edelsbrunner--Hajnal's `2n-7` unit-distance result is a lower-bound
  construction, not an upper bound resolving the subcase. Furedi's separate
  convex-`n`-gon unit-distance work belongs to the upper-bound side of the
  common-radius problem.[^edels-hajnal][^aggarwal][^canon]

## Checked external anchors, 2026-04-30

- Official Erdos Problem #97 page: status `FALSIFIABLE/Open`, prize `$100`,
  no comment-claimed partial or complete solution, and page last edited
  `2025-10-27`.[^erdos97]
- Danzer's 9-point construction is a `k=3` variable-radius construction. It is
  not a `k=4` counterexample. The official page points to Erdos 1987 for the
  construction explanation.[^erdos97][^erdos1987]
- Erdos 1975 reports an unpublished stronger Danzer claim for every `k`, but
  the official page says this was not repeated in later papers and was
  presumably mistaken. Treat that all-`k` statement as `UNVERIFIED` and do not
  cite it as a `k=4` counterexample unless an exact primary construction or
  certificate is recovered.[^erdos97][^erdos1975]
- Fishburn--Reeds 1992 is a `k=3` common-radius/unit-distance construction on
  20 points, with a cut-minimality statement in the accessible abstract. It is
  not a variable-radius `k=4` result.[^fishburn-reeds]
- The Google DeepMind Formal Conjectures entry is a formal statement/alignment
  source, not a proof certificate: `erdos_97` is marked `research open` and the
  theorem body uses `sorry`; nearby Danzer and Fishburn--Reeds variants also
  use `sorry`.[^formal97]

## Current risks

- Recheck the public Erdos Problems listing and any formal-conjectures records
  before announcing a solution or counterexample.[^repo]
- Verify exact statements and citations for Danzer and Fishburn--Reeds before
  using them in a paper-style introduction.[^digest]
- Keep the uniform-radius literature separate from the selected-witness problem
  where each center may have its own radius.[^syn]
- Check `docs/canonical-synthesis.md` before using unit-distance literature in
  any proof program or solution announcement.[^canon]
- Before claiming a new obstruction, search related work on repeated distances
  in convex polygons, convex unit distances, Delaunay/order-k Voronoi
  degeneracies, and oriented-matroid realizability with metric constraints.[^repo]
- Before using the base-apex lemma from `docs/n8-geometric-proof.md` in
  paper-style prose, pin an external literature reference or state it as a
  self-contained elementary lemma.
- Treat any numerical near-equality as only numerical evidence unless it has an
  exact or certified verification artifact.[^repo]

[^digest]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/01_USEFUL_FINDINGS_DIGEST.md`.
[^syn]: Source file: `erd archive/outputs/erdos97_synthesis.md`.
[^repo]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/16_repo_handoff_and_claim_taxonomy.md`.
[^canon]: Source file: `docs/canonical-synthesis.md`.
[^erdos97]: T. F. Bloom, "Erdos Problem #97," Erdos Problems, accessed 2026-04-30. <https://www.erdosproblems.com/97>
[^erdos1987]: P. Erdos, "Some combinatorial and metric problems in geometry," Intuitive Geometry, Colloquia Mathematica Societatis Janos Bolyai 48, 167--177, 1987. <https://www.renyi.hu/~p_erdos/1987-27.pdf>
[^erdos1975]: P. Erdos, "On some problems of elementary and combinatorial geometry," Annali di Matematica Pura ed Applicata 103, 99--108, 1975. <https://www.renyi.hu/~p_erdos/1975-25.pdf>
[^fishburn-reeds]: P. C. Fishburn and J. A. Reeds, "Unit distances between vertices of a convex polygon," Computational Geometry 2(2), 81--91, 1992. DOI: `10.1016/0925-7721(92)90026-O`.
[^formal97]: `google-deepmind/formal-conjectures`, `FormalConjectures/ErdosProblems/97.lean`, accessed 2026-04-30. <https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/97.lean>
[^edels-hajnal]: H. Edelsbrunner and P. Hajnal, "A lower bound on the number of unit distances between the points of a convex polygon," Journal of Combinatorial Theory, Series A 56(2), 312--316, 1991. DOI: `10.1016/0097-3165(91)90042-F`.
[^aggarwal]: A. Aggarwal, "On Unit Distances in a Convex Polygon," Discrete Mathematics 338(3), 88--92, 2015; arXiv:1009.2216. DOI: `10.1016/j.disc.2014.10.009`.
