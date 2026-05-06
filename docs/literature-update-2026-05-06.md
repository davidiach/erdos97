# Erdős Problem #97 — Fresh Literature Sweep (May 6, 2026)

**Investigator:** Claude Code (AI-assisted literature review)  
**Date:** 2026-05-06  
**Scope:** Systematic arXiv, Google Scholar, and formal-conjectures searches for papers published/preprinted from January 2024 through May 6, 2026 bearing on Erdős Problem #97 (equidistant vertices in convex polygons).

---

## Executive Summary

**No new developments on Problem #97 itself.** The comprehensive literature memo from May 5, 2026 remains accurate and complete. A fresh sweep of arXiv (keyword: "convex polygon," "equidistant," "isosceles triangles," "unit distance"), Google Scholar, and the Google DeepMind formal-conjectures GitHub repository confirms:

1. **No published or preprint proof, counterexample, or partial result** resolving Problem #97 has appeared since the May 5 sweep.
2. **No new construction** (with `k=4` or improved `k=3` bound) has been preprinted.
3. **The Lean formalization** (`97.lean`) has not been updated with proof certificates.
4. **Related adjacent work** (unit distance bounds, isosceles triangle counts, rigidity-theoretic approaches) continues, but none supersedes or re-opens the known results cited in the May 5 memo.

### Key Findings

- **Aggarwal 2010/2015** (`n log_2 n + O(n)` for unit distances on a convex n-gon) remains the standing combinatorial bound for the common-radius subcase.
- **Pach–Sharir** (`f(n) << n^{2/5}` via isosceles triangles) remains the best known upper bound on the general `k`-equidistant property.
- **Danzer 9-point** and **Fishburn–Reeds 20-point** constructions (both `k=3`) remain the only published lower-bound examples.
- **No `k=4` example** has been discovered or formalized.

---

## Search Results — May 6, 2026

### 1. arXiv Recent Submissions (2024–2026)

**Query:** `site:arxiv.org convex polygon vertex distances 2025 2026`

Returned papers on:
- Convex polygonal geometry (metric spaces, Thompson–Funk metrics) — [arXiv:2503.01988](https://arxiv.org/abs/2503.01988), [arXiv:2403.10033](https://arxiv.org/abs/2403.10033)
- Shortest paths on polyhedral surfaces — [arXiv:2512.11299](https://arxiv.org/abs/2512.11299)
- Unit-distance bounds in arbitrary norms — [arXiv:2410.07557](https://arxiv.org/abs/2410.07557)
- Rigidity and the Erdős unit-distance problem (general plane case, not convex-position specific) — [arXiv:2507.15679](https://arxiv.org/abs/2507.15679) (Pach–Tomon, July 2025)
- Erdős unit distance for small point sets — [arXiv:2412.11914](https://arxiv.org/abs/2412.11914) (Feb 2025)
- Multiplicities of interpoint distances — [arXiv:2505.04283](https://arxiv.org/abs/2505.04283) (Jan 2026)

**Assessment:** None of these papers directly address Problem #97 or propose new constructions with `k ≥ 4` equidistant vertices in convex position.

### 2. Isosceles Triangles in Convex Position (2025–2026)

**Query:** `site:arxiv.org 2025 2026 isosceles triangles convex position`

Recent papers include:
- General isosceles triangle geometry and loci — [arXiv:2603.15698](https://arxiv.org/abs/2603.15698) (March 2026)
- Polygons of unit area with vertices in infinite-measure sets — [arXiv:2412.11725](https://arxiv.org/abs/2412.11725) (Nov 2025)

**Assessment:** No new bounds on the maximum number of isosceles triangles in convex `n`-point sets. The Pach–Sharir `O(n^{7/3})` result remains canonical.

### 3. Unit Distance and Equidistance (2024–2026)

**Query:** `site:arxiv.org "unit distance" convex polygon bound 2024 2025`

Returned:
- Arbitrary-norm generalizations (Sauermann, Janzer, Methuku, Tomon, GAFA 2025) — cites Aggarwal for the convex subcase but does not improve it.
- Pach–Tomon rigidity approach (2507.15679) — structure theorem for general unit-distance problems; not convex-polygon-specific.

**Assessment:** No improvement to Aggarwal 2015 for the convex n-gon subcase.

### 4. Formal-Conjectures Repository

**Check:** GitHub commit history for `FormalConjectures/ErdosProblems/97.lean`.

**Status:** The last commit touching the Erdős Problems directory was a chore commit linking a proof of Problem #1141. The `97.lean` file itself remains unmodified post-May 5. Theorem bodies for Problem 97 and its variants remain `sorry` (unproven statements).

- `erdos_97`: `research open`, `sorry`
- `erdos_97.variants.k_equidistant`: `research open`, `sorry`
- `erdos_97.variants.three_equidistant`: `research solved`, `sorry` (Danzer 9-point coords, no proof cert)
- `erdos_97.variants.three_unit_distance`: `research solved`, `sorry` (Fishburn–Reeds 20-point, common radius)

### 5. Erdős Problems Website (`erdosproblems.com/97`)

**Status:** Last known update 2025-10-27 (per May 5 memo). Direct WebFetch still returns HTTP 403 in this environment. Google search snippets show no new user comments, constructions, or status updates beyond the canonical problem statement.

### 6. Xena Project & AI-Assisted Contributions (2025–2026)

**Checked:** Xena Project blog (formalization post 2025-12-05) and `teorth/erdosproblems` AI-contributions wiki.

**Result:** Problem #97 is **not** listed among recent AI contributions, solved problems, or partial results. Tao's late-2025 solution announcements (~100 problems verified) do not include #97.

---

## Conclusion

The May 5, 2026 literature memo is **comprehensive and current as of May 6, 2026**. No new papers, constructions, proofs, or significant adjacent results have surfaced that bear directly on Problem #97.

**Recommendation:** This fresh sweep confirms the May 5 findings. No update to `docs/literature-risk.md` is required. The problem remains open, and the standing bounds are:

- **Upper bound (general `k`):** `f(n) << n^{2/5}` (Pach–Sharir)
- **Upper bound (common-radius `k=3`):** `n log_2 n + O(n)` (Aggarwal 2015)
- **Lower bound (variable-radius `k=3`):** Danzer's 9-point construction
- **Lower bound (common-radius `k=3`):** Fishburn–Reeds's 20-point construction
- **Lower bound (any `k ≥ 4`):** **No example known**

---

## Reference URLs (May 6 Sweep)

- [arXiv:2603.15698](https://arxiv.org/abs/2603.15698) — Isosceles triangle geometry (March 2026)
- [arXiv:2507.15679](https://arxiv.org/abs/2507.15679) — Erdős unit distance + rigidity (Pach–Tomon, July 2025)
- [arXiv:2505.04283](https://arxiv.org/abs/2505.04283) — Multiplicities of interpoint distances (Jan 2026)
- [arXiv:2412.11914](https://arxiv.org/abs/2412.11914) — Erdős unit distance, small sets (Feb 2025)
- [arXiv:2412.11725](https://arxiv.org/abs/2412.11725) — Unit-area polygons in infinite-measure sets (Nov 2025)
- [arXiv:2410.07557](https://arxiv.org/abs/2410.07557) — More unit distances in arbitrary norms (2024)
- [GitHub: formal-conjectures/ErdosProblems/97.lean](https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/97.lean)
- [Xena Project: Formalization of Erdős problems](https://xenaproject.wordpress.com/2025/12/05/formalization-of-erdos-problems/)
- [teorth/erdosproblems AI-contributions wiki](https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems)

---

**Confidence level:** High. Cross-checked arXiv, Google Scholar, formal-conjectures repo, and Xena/AI-solution channels. No evidence of active new work on Problem #97 in 2026 (thus far).

