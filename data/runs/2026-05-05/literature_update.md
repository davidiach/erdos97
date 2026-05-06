# Erdős Problem #97 — Literature Update Memo

**Investigator note.** Date 2026-05-05. Time-boxed search across erdosproblems.com, arXiv, the Google DeepMind `formal-conjectures` repo, and recent author lists (Aggarwal, Pach, Pinchasi, Sharir, Tardos). Several direct fetches to `erdosproblems.com` and to selected arXiv abstract pages returned HTTP 403 in this environment, so primary sourcing relied on Google search snippets and one direct fetch of the canonical Lean file. Findings are conservative.

## TL;DR

- **No published or preprint resolution of Problem #97.** It remains open. No partial result, counterexample for `k=4`, or new lower-bound construction (in the variable-radius sense) has surfaced post-2010 from authors working on this problem.
- **The unpublished 1975 Erdős all-`k` Danzer claim has not resurfaced.** It still appears only as a remark in Erdős 1975, and the canonical commentary on `erdosproblems.com/97` continues to describe it as presumably mistaken; the search returned no preprint, paper, or note with the actual all-`k` construction.
- **The strongest cited combinatorial bound is still Pach–Sharir** giving `f(n) << n^{2/5}` (via O(n^{7/3}) isosceles triangles), well above what would resolve `f(n) <= n^{o(1)}`.
- **Aggarwal's 2010 (DM 2015) `n log_2 n + O(n)` upper bound** for unit distances on a convex n-gon remains state-of-the-art; no paper found that supersedes it through 2025. It only addresses the common-radius / unit-distance subcase.
- **The Lean formalization** in `google-deepmind/formal-conjectures` carries Problem 97 as `category research open, AMS 52` with the theorem body still `sorry`. Adjacent Danzer (`three_equidistant`, 9-point coords listed) and Fishburn–Reeds (`three_unit_distance`, `three_unit_distance_cut_min`) variants are also `sorry` (i.e. statements only, no proof certificates).
- **Erdős–Fishburn 6-distance conjecture `g(6)=13`** was resolved (proved) in 2012 (electronic JC). No further movement directly applies to #97. The "Erdős–Fishburn" label in the literature points primarily to that distinct-distance counting problem, not to the variable-radius `k`-equidistant-vertices problem.

## 1. The official `erdosproblems.com/97` entry

Repo notes record `2025-10-27` as the last-edited timestamp. Direct WebFetch and `curl` against `https://www.erdosproblems.com/97` and `https://erdosproblems.com/97` both returned HTTP 403 in this sandbox; this is a fetch-side restriction, not evidence of a takedown — the page was indexed and quoted by Google search snippets in the same session. The reconstructed snippet from search:

> "f(n) maximal such that there exists a set A of n points in R^2 in which every x in A has at least f(n) points in A equidistant from x. Is it true that f(n) <= n^{o(1)}? [...] Erdős originally conjectured that no 3 vertices would be equidistant, but Danzer found a convex polygon on 9 points such that every vertex has three vertices equidistant from it (but this distance depends on the vertex), and Fishburn and Reeds found a convex polygon on 20 points such that every vertex has three vertices equidistant from it. Erdős offered \$500 for a proof that f(n) <= n^{o(1)} but only \$100 for a counterexample. A result of Pach and Sharir implies f(n) << n^{2/5}."

This matches the snapshot in `docs/literature-risk.md`, including the prize asymmetry ($100 advertised on the page is for the counterexample; $500 for the proof). I did not get back any user-comment, partial-result, or new-construction text via search snippets, which is consistent with the 2026-04-30 sweep recorded in `docs/literature-risk.md`. URL: <https://www.erdosproblems.com/97>.

## 2. Lean / formal-conjectures status

The canonical Lean file `FormalConjectures/ErdosProblems/97.lean` was retrieved successfully via `raw.githubusercontent.com`. Key takeaways:

- Header comment `Copyright 2025 The Formal Conjectures Authors`. The file is alive but its theorem bodies are all `sorry`.
- `theorem erdos_97` is annotated `@[category research open, AMS 52]` and is stated as: a `ConvexIndep` finite point set `A` does not satisfy `HasNEquidistantProperty 4 A` (the variable-radius `k=4` formulation — each vertex has its own radius).
- `erdos_97.variants.three_equidistant` is annotated `research solved` and specifies the Danzer 9-point coordinates explicitly (with `√3` rationals). Body is `sorry` — i.e. coordinates are formal placeholders, the certificate is not in tree.
- `erdos_97.variants.k_equidistant` is `research open` — this is the `∃ k` version, which is what the unpublished 1975 Danzer claim would have refuted.
- Two Fishburn–Reeds variants — `three_unit_distance` (existence, 20 points, common radius 1) and `three_unit_distance_cut_min` (n=20 minimality with a `IsCut` condition) — are `research solved`, both `sorry`.
- Cited references: `[Er46b]` (Amer. Math. Monthly, 1946) and `[Er87b]` (Intuitive geometry, Siófok 1985) for the Danzer/conjecture history; `[FiRe92]` (Comput. Geom. 1992) for Fishburn–Reeds.

URL: <https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/97.lean>. Local cache at `/tmp/97.lean`.

The Xena Project blog post "Formalization of Erdős problems" (2025-12-05) and the `teorth/erdosproblems` AI-contributions wiki list a number of recent solved/contributed problems, but **neither lists Problem 97 among recent contributions, claims, or partial results** — confirming the open status. URLs: <https://xenaproject.wordpress.com/2025/12/05/formalization-of-erdos-problems/>, <https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems>.

## 3. Status of the unpublished 1975 Danzer all-`k` claim

The targeted query "Danzer construction equidistant convex polygon all k 1975 unpublished resurfaced" returned **no paper, note, or preprint that recovers the construction.** What did surface:

- Boben (arXiv:1301.1067, "Danzer's configuration revisited") deals with Danzer's `(n_4)` incidence configuration (combinatorial designs / point-line geometry), which is a different Danzer construction unrelated to the `k`-equidistant convex-polygon problem.
- Adiceam et al. (arXiv:2010.06756, "Around the Danzer Problem and the Construction of Dense Forests") concerns the Danzer set problem in covering geometry, also unrelated.
- General Danzer-set entries on Wikipedia, etc. — covering geometry, not equidistance.

So the 1975 Erdős remark — that Danzer told him a stronger all-`k` construction existed — remains unverified in the literature. The repo's `UNVERIFIED` label for the all-`k` claim should stand.

## 4. Aggarwal 2010 / 2015 and follow-ups

- A. Aggarwal, "On Unit Distances in a Convex Polygon," arXiv:1009.2216 (2010, v3 Oct 2014); Discrete Mathematics 338(3), 88–92, 2015. Bound: `<= n log_2 n + 4n`. URL: <https://arxiv.org/abs/1009.2216>.
- I found **no later paper that improves the asymptotic constant** for the maximum number of unit distances in a convex n-gon. Searches for follow-ups by Aggarwal in 2020–2025 turned up only adjacent topics (e.g. an Aggarwal–Lükő alternative proof on a different perimeter-distance sum problem). The 2015 Springer chapter "Erdős's Unit Distance Problem" by Szemerédi and the 2025 GAFA paper "Unit and Distinct Distances in Typical Norms" (Sauermann, Janzer, et al., DOI 10.1007/s00039-025-00698-x) cite Aggarwal as the standing record for the convex-polygon subcase. URL: <https://link.springer.com/article/10.1007/s00039-025-00698-x>.

Two recent generalizations worth flagging:

- **Pach–Tomon and successors on rigidity:** "Erdős's unit distance problem and rigidity," arXiv:2507.15679 (July 2025). Reduces the *plane* unit-distance problem (the general, non-convex form) to a rigid-framework conjecture. Convex-position version is not the focus, but rigidity-theoretic tools may eventually transfer. URL: <https://arxiv.org/abs/2507.15679>.
- **"On multiplicities of interpoint distances,"** arXiv:2505.04283 (v5, Jan 2026). Considers multiplicities including in convex position. Direct relevance to #97 needs the abstract (fetch returned 403 in this sandbox); search snippet flags 1959 Erdős–Moser as the convex-position prior. URL: <https://arxiv.org/abs/2505.04283>.
- **"The Erdős unit distance problem for small point sets,"** arXiv:2412.11914 (Feb 2025). Plane case, exact small-`n` enumeration; not specifically convex-position-focused. URL: <https://arxiv.org/abs/2412.11914>.

## 5. Equidistant points in convex position; repeated distances

The closest combinatorial-geometry results that bear on #97:

- **Pach, Sharir** — old result that the number of isosceles triangles spanned by `n` points is `O(n^{7/3})`. This is what produces `f(n) << n^{2/5}` on `n` convex-position points (each vertex with `f(n)` equidistant neighbors yields `n · binom(f(n),2)` isosceles triangles incident to it, hence `f(n)^2 << n^{4/3}`). Still the standing combinatorial upper bound.
- **Nivasch, Pach, Pinchasi, Zerbib (2013, arXiv:1207.1266)** — improved the lower bound on the maximum number of *distinct* distances from a single vertex of a convex polygon from Dumitrescu's `13n/36 - O(1)` to `(13/36 + ε)n - O(1)` via an improved bound on isosceles triangles. Adjacent rather than direct: it bounds distinct distances at one vertex, not the global `k`-equidistant property at every vertex. URL: <https://arxiv.org/abs/1207.1266>.
- **Pach, Pinchasi, "How Many Unit Equilateral Triangles Can Be Generated by N Points in Convex Position?"** Established that the number of unit-distance equilateral triangles is `<= floor(2(n-1)/3)`. Tight; convex-position-specific. Constraints any common-radius `k=3` construction.
- **"Almost-equidistant sets,"** Balko et al., arXiv:1706.06375. Different problem (no two distances differ by more than ε), but methodology is in the same neighborhood. URL: <https://arxiv.org/pdf/1706.06375>.

Searches for "convex polygon" + "every vertex" + "k equidistant" in 2023–2025 yielded **no new direct construction beyond Danzer's 9-point and Fishburn–Reeds's 20-point**. Neither produces `k=4`.

## 6. Erdős–Fishburn conjecture status

The "Erdős–Fishburn" label most often refers to the `g(k)` problem: max number of points in the plane that determine exactly `k` distinct distances. The `g(6)=13` case was resolved by Wei (Electronic Journal of Combinatorics 2012). URL: <https://www.combinatorics.org/ojs/index.php/eljc/article/view/v19i4p38>. Larger `k` remain open; no 2024–2025 announcement was found. This is **not** the same problem as #97 (which is about equidistant neighbors at each vertex, not the count of distinct distances), so progress here does not transfer.

The Fishburn–Reeds paper itself ("Unit distances between vertices of a convex polygon," Comput. Geom. 1992) is `k=3` common-radius — already encoded in Lean as `solved` but unproven there.

## 7. Recent papers by Pach, Pinchasi, Sharir, Tardos (2023–2026)

The following 2024–2025 papers turned up but **none directly address Problem #97 or the variable-radius `k=4` question**:

- Pach et al., "Erdős's unit distance problem and rigidity," arXiv:2507.15679 (July 2025).
- Sauermann, Janzer, Methuku, Tomon, "Unit and Distinct Distances in Typical Norms," GAFA 2025, DOI `10.1007/s00039-025-00698-x`. Generic-norm extensions of the unit-distance bound; the convex-polygon subcase is referenced via Aggarwal but not reopened.
- Holmsen–Mojarrad–Pach–Tardos, "Two extensions of the Erdős–Szekeres problem," arXiv:1710.11415 (still cited as the latest Pach–Tardos collaboration on convex-position structure).
- Saturation results around Erdős–Szekeres (Damásdi–Hubai et al., LIPIcs SoCG 2024.46; Suk et al., LIPIcs SoCG 2025.13). Convex-position combinatorics, not equidistance.
- Tao, "Planar point sets with forbidden four-point patterns and few distinct distances," 2024-09-03 blog post. Different focus (forbidden patterns), and the search snippet did not surface a connection to #97. URL: <https://terrytao.wordpress.com/2024/09/03/planar-point-sets-with-forbidden-four-point-patterns-and-few-distinct-distances/>.

The `terrytao.wordpress.com` 2025 posts on AI-driven Erdős solutions (blog 2025-08-31 OEIS post; story-of-#1196 on 2026-05-03; story-of-#126 on 2025-12-08) **do not list Problem 97** among solved or partially solved problems. The `teorth/erdosproblems` AI-contributions wiki likewise does **not** list Problem 97.

## 8. Convex point sets with specific equal-distance properties (k=4 lower bounds)

I could not find any new lower-bound construction beyond:

- Danzer 9 vertices, variable-radius, `k=3`. Still the strongest variable-radius construction in the verified literature.
- Fishburn–Reeds 20 vertices, common-radius `=1`, `k=3`. Strongest common-radius construction.
- No `k=4` lower-bound construction (variable or common radius) has been published or preprinted. The Lean variants file confirms: there is no `four_equidistant` companion theorem stated as `solved`. The next-`k` variant `k_equidistant` is `open`.

## 9. New tools or techniques worth tracking

- **Rigidity-theoretic reduction** (Pach et al., 2507.15679) — possibly portable to convex position.
- **Norm-theoretic distinct/unit distance machinery** (Sauermann et al., GAFA 2025) — currently sharper for arbitrary norms, but might inform constructions where each center carries its own radius.
- **AI-assisted formalization** — Aristotle / Gemini case studies (arXiv:2601.22401) and DeepMind's Formal Conjectures show ongoing momentum, with Tao verifying ~100 problems in late 2025. None list #97. The empty `sorry` body in `97.lean` is therefore a current opportunity, not an oversight.

## 10. Net effect on `docs/literature-risk.md`

The 2026-04-30 anchors in the repo's literature-risk file remain accurate as of 2026-05-05:

- Problem #97 status `FALSIFIABLE/Open`, prize `$100` (counterexample), $500 (proof).
- No published `k=4` counterexample.
- Pach–Sharir `f(n) << n^{2/5}` is still the cited combinatorial bound.
- Aggarwal 2015 still standard for the unit-distance subcase.
- The 1975 unpublished all-`k` Danzer claim remains unverified.
- The Lean formalization's `sorry`-bodies have not been replaced by certificates.

No changes to the literature-risk memo are warranted from this sweep. Recommend re-running the sweep prior to any solution announcement.

---

### Reference URLs

- `erdosproblems.com/97`: <https://www.erdosproblems.com/97>
- Lean formalization: <https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/97.lean>
- `teorth/erdosproblems` AI wiki: <https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems>
- Aggarwal 2010/2015: <https://arxiv.org/abs/1009.2216>
- Nivasch–Pach–Pinchasi–Zerbib 2013: <https://arxiv.org/abs/1207.1266>
- Pach–Pinchasi unit equilateral triangles: <https://www.semanticscholar.org/paper/82da8ced857ae410c97a76c8f97b726c08a01de0>
- Erdős unit distance + rigidity (2025): <https://arxiv.org/abs/2507.15679>
- Multiplicities of interpoint distances (2026): <https://arxiv.org/abs/2505.04283>
- Erdős unit distance, small sets (2025): <https://arxiv.org/abs/2412.11914>
- Unit/Distinct Distances in Typical Norms (GAFA 2025): <https://link.springer.com/article/10.1007/s00039-025-00698-x>
- Erdős–Fishburn `g(6)=13` (2012): <https://www.combinatorics.org/ojs/index.php/eljc/article/view/v19i4p38>
- Tao 2024 blog post on forbidden 4-point patterns: <https://terrytao.wordpress.com/2024/09/03/planar-point-sets-with-forbidden-four-point-patterns-and-few-distinct-distances/>
- Xena Project formalization post (2025-12-05): <https://xenaproject.wordpress.com/2025/12/05/formalization-of-erdos-problems/>
- Boben "Danzer configuration revisited" (unrelated incidence config): <https://arxiv.org/abs/1301.1067>
- Adiceam, "Around the Danzer Problem" (unrelated covering): <https://arxiv.org/abs/2010.06756>

### Methodology caveats

- WebFetch returned 403 for `erdosproblems.com`, several arXiv abs pages, and selected Springer/Wiley pages in this environment. These are sandbox-side blocks; cross-checked content via Google search snippets where possible.
- `gh` CLI not installed; GitHub API unauthenticated requests were rate-limited. Commit-history check for `97.lean` could not be performed.
- Time-boxed at ~15 min. A fuller sweep should re-fetch erdosproblems.com/97 directly, retrieve the abstract pages of arXiv:2505.04283, arXiv:2507.15679, arXiv:2412.11914, and search MathSciNet/zbMATH for citations of Aggarwal 2015 and Fishburn–Reeds 1992 since 2020.
