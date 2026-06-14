# E1 — Literature Transfer Mining (Erdős #97, 4-equidistant selected-witness)

Lane: E1 (external literature transfer). Date: 2026-06-14. Web access: available
(WebSearch worked; WebFetch was 403-blocked on arXiv / NYU / JoCG / ResearchGate
PDFs, so exact constants below are taken from search-engine snippets and the repo's
already-cited footnotes, NOT from a re-read of the primary PDFs — see trust labels).

Status discipline: this memo does NOT change official/global status (#97 open, $100).
`uses_strict_convexity` is **n/a** for a literature memo — each cited theorem has its
OWN hypotheses; what matters is whether those hypotheses transfer to the
variable-radius, per-center-selected-4-set object. No incidence lemma is quoted as
established (guardrail #19). The common-radius sublane (guardrail #15) is kept
separate in §B.

Object of #97 (restated): a strictly convex n-gon is **4-bad** if every vertex p_i has
a 4-element set S_i of OTHER vertices at one common distance r_i, where r_i and S_i may
differ per center. Forbidding 4-bad polygons for all n solves #97.

---

## A. Variable-radius–relevant results (the real lane)

### A1. Dumitrescu isosceles bound — ALREADY the repo's shortcut; the best transferable quadratic
- **Statement.** For n points in convex position, the number of isosceles triangles
  (apex-counted: `Z(P) = Σ_p Σ_δ C(m_p(δ),2)`) is at most `(11 n² − 18 n)/12`.
- **Cite.** A. Dumitrescu, "On Distinct Distances from a Vertex of a Convex Polygon"
  (also stated in Nivasch–Pach–Pinchasi–Zerbib 2013). Trust: `LITERATURE_BACKED`
  (constant cross-confirmed by 3 independent web snippets: ScienceDirect, NPPZ,
  and the isosceles-survey results).
- **Transfer.** EXACT and already exploited: 4-bad ⇒ each apex gives ≥ C(4,2)=6 isosceles
  triangles ⇒ `Z ≥ 6n`; combined with the bound gives `n ≥ 90/11 ≈ 8.18`, i.e. no 4-bad
  n-gon for n ≤ 8. This is `docs/dumitrescu-isosceles-n8-shortcut.md`.
- **Why it does NOT give all-n.** The bound is **Θ(n²)** while the 4-bad lower bound is
  only **linear (6n)**. For large n the quadratic upper bound is far above 6n, so there is
  unbounded slack. **A purely isosceles-counting argument with a Θ(n²) cap can never reach
  beyond a constant n.** Improving the constant `11/12` does NOT help asymptotically — even
  a hypothetical `(c·n² )/12` with small c still dominates 6n. So this lane is structurally
  capped at small n. (Confirms repo's "stops before n=9" note: at n=9, `Z ≤ 60` vs `≥ 54`.)

### A2. Improved isosceles constant (NPPZ 2013) — does NOT change the small-n wall materially
- **Statement.** Nivasch, Pach, Pinchasi, Zerbib improve the maximum number of isosceles
  triangles in convex position below Dumitrescu's `(11n²−18n)/12` by a small additive-in-the
  -leading-constant amount, as the engine for the distinct-distance result A3.
- **Cite.** G. Nivasch, J. Pach, R. Pinchasi, S. Zerbib, "The number of distinct distances
  from a vertex of a convex polygon," J. Comput. Geom. 4(1):1–12, 2013; arXiv:1207.1266.
  Trust: `LITERATURE_BACKED` for existence of the improvement; `UNVERIFIED` for the exact
  improved constant (could not fetch PDF; snippets did not expose the explicit new leading
  coefficient — they only state ε≈1/23000 for A3, not the isosceles coefficient).
- **Transfer.** Same shape as A1: still **Θ(n²)**, so the same structural cap applies. The
  improvement is calibrated to push the distinct-distance constant from 13/36 to
  13/36+ε; the gain is ~1/23000, far too small to move the 4-bad wall to n=9. **Does not
  give an all-n bound; does not beat n=8.** Flag: if the explicit improved isosceles
  coefficient were recovered exactly it could be plugged into the shortcut, but the n=9
  slack is 6 isosceles triangles against a Θ(n²) cap — a 1/23000-scale constant gain is
  nowhere near closing it. Low value.

### A3. Distinct distances from a vertex (Erdős 1946 / Dumitrescu / NPPZ)
- **Statement.** Every n-point set in convex position has a vertex determining
  ≥ `(13/36 + ε)n − O(1)` distinct distances to the others, ε ≈ 1/23000 (Dumitrescu's
  13n/36 − O(1) is the predecessor). Conjectured optimum ⌊n/2⌋ (regular n-gon).
- **Cite.** Erdős 1946 (conjecture); A. Dumitrescu 2006 (13/36); NPPZ 2013 (+ε).
  Trust: `LITERATURE_BACKED`.
- **Transfer — DIRECTION IS WRONG for #97.** This LOWER-bounds distinct distances at SOME
  vertex, i.e. it says some vertex has MANY different distances. #97 needs an UPPER bound on
  the multiplicity at EVERY vertex (no distance repeated ≥4 from any vertex). A
  many-distinct-distances theorem at one vertex does not bound the max multiplicity at all
  vertices: a vertex can simultaneously realize many distinct distances AND have one
  distance with multiplicity ≥4. **Does not rule out 4-bad. Missing hypothesis: a per-vertex
  multiplicity (not diversity) bound.** Useful only as the source of the A1 counting lemma.

### A4. Per-vertex single-circle multiplicity — NO usable upper bound found (key gap)
- **What I searched for.** A theorem bounding the number of OTHER vertices on ONE circle
  centered at a polygon vertex in convex position (this is exactly m_p(δ); a bound `m_p(δ) ≤ 3`
  would instantly kill 4-bad).
- **Result.** No such sub-trivial upper bound exists in the literature I could find, and the
  repo's own guardrails (`failed-ideas.md` #4, #5, #19) explicitly warn that a circle
  centered at a convex-polygon vertex CAN pass through many other vertices, and that "≤3n"
  or "≤4n−4" one-circle-per-center incidence lemmas are NOT established. Trust:
  `LITERATURE_GAP` / consistent with repo. **This is the missing ingredient: the entire
  difficulty of #97 is that no per-vertex single-circle multiplicity bound below 4 is known
  or expected unconditionally.** Do NOT manufacture one (guardrail #19).
- **Implication.** Any all-n proof must come from a STRUCTURAL convexity argument (cyclic
  order / one-sidedness / Kalmanson), not from importing a multiplicity bound — consistent
  with the repo's metric-linear negative control (#16, p24).

---

## B. Common-radius / unit-distance sublane (SEPARATE — guardrail #15)

These bound a SINGLE global distance's multiplicity among all vertex pairs. They apply only
to the uniform-radius slice of #97 (all r_i equal), which §5.5 of canonical-synthesis notes
is NOT the content of #97 for n≥8 (the bidirectional-pigeonhole forcing all r_i equal breaks
at n≥8). Kept strictly separate.

### B1. Füredi (1990): same distance occurs O(n log n) times in a convex n-gon
- **Statement.** The maximum number of times one fixed distance can occur among the vertices
  of a convex n-gon is `O(n log n)`.
- **Cite.** Z. Füredi, "The maximum number of times the same distance can occur among the
  vertices of a convex n-gon is O(n log n)," J. Combin. Theory Ser. A 55 (1990) 316–320.
  Trust: `LITERATURE_BACKED` (title cross-confirmed, ScienceDirect S0097316500931339).
- **Transfer.** Common-radius only. Even within that slice it is **super-linear** and thus
  gives nothing against the needed `< 2n` threshold (uniform 4-bad ⇒ ≥2n unit pairs). It is
  an UPPER bound but too weak by a log factor. **Does not rule out even the uniform subcase.**

### B2. Erdős–Fishburn conjecture: `< 2n` pairs at any one distance (convex) — OPEN
- **Statement (conjecture).** A convex n-gon has fewer than `2n` pairs at any single distance.
- **Cite.** Fishburn–Reeds 1992 context; recorded in canonical-synthesis §5.5. Trust:
  `CONJECTURE / OPEN`.
- **Transfer.** IF proved, it would close ONLY the uniform-radius subcase of #97 (since
  uniform 4-bad forces ≥2n equal pairs). It is open since 1992, and even if proved leaves the
  variable-radius case — the actual #97 — untouched. **Does not rule out 4-bad; wrong slice +
  unproved.**

### B3. Aggarwal (2015) upper bound + cut-matrix patterns; Edelsbrunner–Hajnal lower bound
- **Statements.** Convex n-gon unit-distance count ≤ `n log₂ n + O(n)` (Aggarwal 2015,
  improving Füredi); ≥ `2n − 7` achievable (Edelsbrunner–Hajnal 1991). Aggarwal also records
  forbidden cut-matrix cycle patterns for unit-distance (antipodal-cut) matrices.
- **Cite.** A. Aggarwal, Discrete Math. 338(3):88–92, 2015, arXiv:1009.2216; H. Edelsbrunner,
  P. Hajnal, JCTA 56(2):312–316, 1991. Trust: `LITERATURE_BACKED`.
- **Transfer.** Common-radius only. The `2n−7` is a LOWER-bound construction (guardrail #15
  direction-of-bound warning), not an upper bound; the upper bound is super-linear. The
  cut-matrix patterns require distance-like / antipodal-cut hypotheses that the
  variable-radius selected-witness matrix does not supply without a separate proof. **Does not
  transfer to variable radius.**

### B4. Aggarwal 2010 "On Isosceles Triangles…" (arXiv:1009.2218) — adjacent, common-radius flavored
- **Statements (from abstract).** Vertices of a convex n-gon form at most `n²/2 + Θ(n log n)`
  isosceles triangles with two UNIT sides (optimal to first order); conjecturally
  `≤ 3n²/4 + o(n²)` isosceles triangles total (proved for a special class); at most `⌊n/k⌋`
  regular k-gons for k≥4 (optimal).
- **Cite.** A. Aggarwal, "On Isosceles Triangles and Related Problems in a Convex Polygon,"
  arXiv:1009.2218, 2010. Trust: `LITERATURE_BACKED` (abstract confirmed via search).
- **Transfer.** The "two unit sides" result is common-radius (fixed leg length). The general
  isosceles conjecture is Θ(n²) — same structural cap as A1, so even if proved it can't beat
  the linear 6n lower bound asymptotically. **Does not give all-n; does not beat n=8.** The
  `⌊n/k⌋` regular-k-gon bound is unrelated (counts regular sub-polygons, not equidistant
  witnesses). Low value.

---

## C. Bárány–Roldán-Pensado (boundary-intersection) — NOT a finite-vertex transfer
- **Statement.** Convex bodies K with `N(K)=6` boundary intersections exist (simplest a
  15-gon); for any boundary point of an acute triangle some centered circle meets the boundary
  4×. Cite: I. Bárány, E. Roldán-Pensado, Discrete Comput. Geom. 50:253–261, 2013. Trust:
  `LITERATURE_BACKED` (matches repo `docs/literature-risk.md`).
- **Transfer.** Their equal-radius hits are on the BOUNDARY (edge interiors allowed), not at
  vertices, so this is a strictly looser problem than #97's finite-vertex requirement. **Does
  not yield a finite 4-bad polygon.** No new transfer beyond what the repo already records.

---

## D. Brass–Moser–Pach "Research Problems in Discrete Geometry"
- The repeated-distances chapter collects exactly B1/B2/B3 above (Füredi O(n log n),
  Erdős–Fishburn `<2n` conjecture, diameter ≤ n, second-largest ≤ (4/3)n, top-k ≤ 3kn with
  ≤2n for k=2). Trust: `LITERATURE_BACKED` for the catalogue; these are the same common-radius
  results as §B and carry the same non-transfer verdict. The book also poses Erdős 1946 (A3).
- Useful secondary facts (common-radius, snippet-sourced, `LITERATURE_BACKED`): diameter
  occurs ≤ n times (tight: regular odd n-gon); second-largest distance ≤ (4/3)n; top-2
  distances ≤ 2n. **None bound per-vertex multiplicity for an ARBITRARY (variable) distance,
  so none transfer.**

---

## E. Net assessment for the lane

- **No literature result improves on the n≤8 wall, and none gives an all-n bound.** The one
  result that bites (Dumitrescu isosceles, A1) is already the repo's shortcut and is
  structurally capped at small n because its Θ(n²) form dominates the linear 6n requirement.
- The asymptotic obstruction is sharp: 4-bad contributes only **linear** structure (6n
  isosceles triangles, ~2n unit pairs in the uniform slice), while every relevant upper bound
  is **super-linear** (Θ(n²) isosceles, Θ(n log n) repeated distances). **No counting/incidence
  theorem in this literature can close the gap for large n.**
- The genuinely missing ingredient is a **per-vertex single-circle multiplicity bound (< 4)
  under strict convexity**, which is exactly what is NOT known (A4) and what guardrail #19
  forbids fabricating. This re-confirms that #97 needs a convexity-structural argument
  (cyclic order / one-sidedness / Kalmanson), aligning with the repo's metric-linear negative
  control (#16).
- Recommendation: keep B1–B4 quarantined as common-radius-only; do not cite NPPZ/Dumitrescu
  distinct-distance bounds in the variable-radius direction (A3 is direction-reversed). The
  only safe paper-style import remains the Dumitrescu isosceles constant for n≤8.

Confidence: 78/100 that no published literature transfer beats n=8 or yields all-n for the
variable-radius problem (high on the asymptotic-direction argument and the Dumitrescu cap;
the −22 reflects unfetched exact constants in NPPZ 2013 and Aggarwal 2010, and that I could
not exhaustively rule out an obscure per-vertex multiplicity bound — though guardrails and
the open status of #97 make its existence very unlikely).

### Sources
- NPPZ 2013: https://jocg.org/index.php/jocg/article/view/2937 ; arXiv:1207.1266
- Füredi 1990 (O(n log n)): https://www.sciencedirect.com/science/article/pii/S0097316500931339
- Aggarwal 2015 (unit distances): https://www.sciencedirect.com/science/article/pii/S0012365X14003847 ; arXiv:1009.2216
- Aggarwal 2010 (isosceles in convex polygon): https://arxiv.org/abs/1009.2218
- Erdős distinct distances / 1946 convex conjecture: https://en.wikipedia.org/wiki/Erd%C5%91s_distinct_distances_problem
- Brass–Moser–Pach, Research Problems in Discrete Geometry: https://link.springer.com/book/10.1007/0-387-29929-7
- Repo: docs/dumitrescu-isosceles-n8-shortcut.md, docs/literature-risk.md, docs/failed-ideas.md (#4,#15,#16,#19), docs/canonical-synthesis.md §5.5
