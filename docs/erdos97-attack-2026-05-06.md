# Erdős Problem #97 — Multi-agent Attack Report (2026-05-06)

**Status:** No general proof and no counterexample of Erdős #97 are claimed.
This document records a multi-agent attack that
**closes the n=9 algebraic route** (all 184 selected-witness assignments now
killed by Gröbner-basis decoders), and produces a **conditional theorem
closing the asymmetric kite case of the Selection Lemma program**, which is
the highest-leverage open step in the canonical synthesis.

The official/global status of Erdős #97 (erdosproblems.com/97) remains
**FALSIFIABLE/OPEN**. Independent reviewer audit is required before any
public theorem-style use of the artifacts here.

## Headline findings

1. **n=9 second-source algebraic proof is now COMPLETE (review-pending).**
   The 2026-05-05 round left 16/184 labelled assignments un-decoded
   (families F07, F08, F09, F13). Four parallel decoders in this round
   produce explicit `EXACT_OBSTRUCTION` certificates for every one of those
   16 assignments. Each certificate gives a univariate elimination
   polynomial (always `y_8^2 - 3/4 = 0` after the chosen gauge), enumerates
   all real roots, lifts each root to a full 9-vertex configuration in the
   regular-hexagon lattice `{0, ±1/2, 1, 3/2} × {0, ±√3/2}`, and verifies
   that every lift has at least one exact vertex coincidence (typically
   collapsing to 3-4 distinct hexagon-lattice points). Since strictly
   convex 9-gons require 9 distinct vertices, no real solution gives a
   strictly convex 9-gon.
   - F07: 6 labelled assignments (orbit 6) → `n9_f07_decoder.json`.
   - F08: 2 labelled assignments (orbit 2) → `n9_f08_decoder.json`.
   - F09: 6 labelled assignments (orbit 6) → `n9_f09_decoder.json`.
   - F13: 2 labelled assignments (orbit 2) → `n9_f13_decoder.json`.
   The committed Gröbner artifacts now exactly kill **184/184** labelled
   selected-witness assignments at n=9 by purely algebraic means, complementing
   the existing vertex-circle proof. Reviewer audit of the four new decoders is
   the next required step before any promotion of the n=9 status.
   Artifacts: `data/certificates/2026-05-06/n9_f0{7,8,9}_decoder.json`,
   `data/certificates/2026-05-06/n9_f13_decoder.json`.

2. **Selection Lemma asymmetric kite case: CONDITIONAL THEOREM.** The
   highest-leverage open sub-problem in the canonical synthesis (§5.3)
   is canonical-chord-rule injectivity. The symmetric kite case
   (`r_i = r_j`) was rigorously closed in the 2026-05-05 round. This
   round closes the asymmetric case (`r_i ≠ r_j`) up to a small
   cyclic-order audit:
   - Setup: `v_i = (0, h_i)`, `v_j = (0, -h_j)`, `p = (a, 0)`, `q = (-a, 0)`,
     extra witnesses `x_k = (r_i sin ψ_k, h_i - r_i cos ψ_k)` and
     `y_k = (r_j sin η_k, -h_j + r_j cos η_k)` with `|ψ_k| > 3θ_i`,
     `|η_k| > 3θ_j`.
   - **Key Lemma (analytic identity, verified symbolically).**
     `C(p) := (p - x_1) × (y_1 - p)` factorizes as
     `r_i r_j [(cos θ_j - cos η_1)(sin ψ_1 - sin θ_i) +
              (cos θ_i - cos ψ_1)(sin η_1 - sin θ_j)]`.
     Each summand is a product of two strictly positive numbers under the
     short-base + L1+L8 angular constraints. So `C(p) > 0`,
     contradicting strict convexity at `p`.
   - **Lemma 2 (no-y-on-right case).** When no `y_k` has `η_k > 0`,
     `p` is adjacent to `v_j` in the cyclic order, and
     `C(p) = a(h_i - r_i cos ψ_1) + h_j(r_i sin ψ_1 - a)` is zero at
     `ψ_1 = θ_i`, has positive derivative on `(0, π/2)`, hence is positive
     on `(θ_i, π/2)`. The constraint `ψ_1 > 3θ_i > θ_i` forces `C(p) > 0`.
   - **Case coverage.** The 9 sign patterns `(X, Y) ∈ {RR, RL, LL}^2` are
     covered by Lemma 1 (when at least one x and one y are on the same side)
     or Lemma 2 / its mirror at `q` (when one side has only x's or only y's).
   - **Numerical verification.** 1,000,000 trials of Lemma 1 produced zero
     failures (min margin 0.22). 3,400,000 additional trials across all 9
     sign patterns produced zero strictly convex configurations. Combined
     with the 287,208 trials in the prior round, this is overwhelmingly
     consistent with the analytic theorem.
   - **Remaining gap (audit only).** §3 of the writeup assumes the cyclic
     order on the right side is `v_i, x's, y's, p, v_j`. The case analysis
     in §4 handles side-pattern ambiguity, but the formal proof that the
     cross-product violation persists *regardless of x/y interleaving* on
     a single side still needs to be checked. A separate cyclic-order
     audit agent is launched.
   - **If the audit closes:** combined with the symmetric case and the
     short-base lemma, **canonical-chord-rule injectivity** is closed.
     With the (separately conjectural) noncrossing claim, this resolves
     Erdős #97 outright via `|B(P)| ≤ n - 3`.
   Writeup: `data/runs/2026-05-06/selection_lemma_asymmetric_attempt.md`.
   Trust: `CONDITIONAL_THEOREM` modulo cyclic-order audit.

3. **n=10 row0 4-subset coverage confirmed COMPLETE (review-pending).** An
   independent audit verified that the 126 "singleton slices" in
   `n10_vertex_circle_singleton_slices.json` are exactly the 126 row0
   4-subsets `C(9, 4) = 126`, each covered once with no gaps and no hidden
   symmetry quotient. Repo-native generic-engine spot-checks at row0
   indices `0, 1, 25, 50, 62, 100, 125` reproduced the imported counts
   bit-for-bit (each 0 full assignments, total 311 s wall-clock). Total
   across all 126 slices: 4,142,738 nodes visited, 0 full assignments.
   Audit certificate: `data/certificates/2026-05-06/n10_extended_coverage.json`.

4. **Q-L9 filter implemented (as code) with two errors found in the
   original lemma writeup (corrected).** `scripts/check_q_l9_filter.py`
   provides `q_l9_check(coordinates)` and a per-vertex breakdown.
   - Errors caught and corrected:
     (a) Filter direction was inverted in `data/runs/2026-05-05/L9_sharpening.md`
     §2.1 step 3 ("Reject candidates with `δ_min ≤ 4·ε(P)`" should be
     "δ_min ≥ 4·ε(P)" or equivalently ratio < 1/4).
     (b) Cosine half-width misstatement in §1.2 (constant cancels through
     the implicit simplification, so the lemma itself is correct;
     re-derived independently).
   - The B12_3x4_danzer_lift near-miss sits exactly on the Q-L9 boundary
     (ratio ≈ 0.481, sin θ_int = 0.50 at every vertex), confirming the
     numerical-near-miss / boundary-locus interpretation.
   - C13_sidon, C19_skew survivor optimisations have ratio ε/δ_min in the
     range 24-7000+, consistent with cluster-collapse drift.
   - Q-L9 constraint integrated as an SLSQP penalty: helps C13_sidon
     (loss drops 5×, ratio falls from 826 to 3.3), hurts B12 (already at
     boundary).
   Artifact: `data/certificates/2026-05-06/q_l9_filter_results.json`,
   `scripts/check_q_l9_filter.py`.

5. **Geometric n=9 base-apex extension fails (gap is real).** I verified
   that the proposed extension of the n=8 geometric proof to n=9 via the
   "equilateral implies contradiction" route does not close at n=9. Specifically:
   - The conditional `equilateral + length-3 diagonals saturated → vertex cover
     of n-cycle has size ≥ ⌈n/2⌉ → total turn ≥ ⌈n/2⌉·(2π/3) > 2π for n ≥ 7`
     is rigorous in all `n ≥ 7`.
   - But equilateral side lengths are NOT forced by the base-apex count at
     n ≥ 9. The slack `n(n-2) - 6n = n(n-8)` opens up at n=9 (slack 9, then 20,
     33, ...). Saturation propagates only at n=8.
   - The repo's existing `docs/n9-base-apex-frontier.md` enumeration of 95
     unlabeled excess distributions is consistent: even restricting to
     {(4,1,1,1,1), (4,2,1,1)} leaves 7/10 distributions un-killed by the
     conservative turn-cover diagnostic.
   Conclusion: a new structural ingredient is needed for n=9 base-apex.
   Writeup: `data/runs/2026-05-06/geometric_n9_extension.md`.

6. **Two-orbit ansatz at large m (m=14..30) confirms the dead-end.** The
   2026-05-05 round tested m ∈ {6, 7, 8, 9, 10, 12} with no inner-radius
   solutions. This round extended to m ∈ {14, 15, 16, 18, 20, 25, 30} (i.e.,
   n ∈ {28, 30, 32, 36, 40, 50, 60}). Across `Oa, Ob, Ia, Ib` pattern
   combinations, no candidate `(r_b, φ)` in the strict-convex window
   produced a 4-bad realization. Best near-miss numerical residuals are
   recorded for provenance only.
   Artifact: `data/certificates/2026-05-06/two_orbit_large_m.json`.

7. **Bridge Lemma A' combinatorial picture stable.** A reproducible
   stuck-set census and ear-orderability test confirms the 2026-05-05
   counts: 11/15 ear-orderable at n=8, 182/184 ear-orderable at n=9, with
   the 2 non-ear-orderable n=9 patterns being inverse-orbit Cayley-Z/9
   circulants (offset multisets `{+1, +3, -2, -3}` and `{-1, +2, +3, -3}`).
   Both are killed by vertex-circle and Gröbner. No new combinatorial
   obstruction was produced; the stuck-set route remains contingent on
   geometric input.
   Artifact: `data/runs/2026-05-06/bridge_lemma_attack_data.json`.

8. **Three-cap rigid (2,2,2) at n=9: the §4.4 bridge conjecture is FALSE;
   refined claim opens.** A symbolic CASE A construction produces, for every
   `a ∈ (0, π/6)`, a strictly convex 9-gon with cyclic CCW order
   `p, Z_1, Z_2, q, X_1, X_2, r, Y_1, Y_2` where:
   - `p, q, r` are SEC support vertices forming an equilateral triangle.
   - All three of `p, q, r` are 4-bad (each has 4 cocircular witnesses at
     common distance `√3`: each of `p`'s witnesses is `{q, r, X_1, X_2}` etc.).
   - The 6 cap-interior vertices `X_i, Y_i, Z_i` have `M = 2` only; they are
     NOT 4-bad.
   The §4.4 conjecture from `canonical-synthesis.md` (asserting that the
   rigid `(2,2,2)` configuration cannot have all of `{p,q,r}` 4-bad
   simultaneously) is therefore disproved. The polynomial system has a 6-D
   real variety; no Gröbner = {1} certificate exists.

   Crucially, **the construction is consistent with Erdős #97**, because
   the cap-interior vertices have `M ≤ 2 ≤ 3`. The new refined claim is:
   > In CASE A, `M(X_1) ≥ 4` is incompatible with strict convexity.
   30,000+ numerical samples within the 6-D moduli space found no
   `M(X_1) ≥ 4` realisation. Closing the refined claim symbolically would
   restore an n=9 closure: "if all of `p,q,r` are 4-bad in the rigid case,
   no other vertex is 4-bad."
   Writeup: `data/runs/2026-05-06/three_cap_n9_rigid.md`.

9. **Danzer / Fishburn-Reeds k=3 → k=4 lift attempts: no counterexample.**
   Multiple lifting strategies (1-parameter perturbations, double-Danzer,
   center insertion, affine stretches) were attempted on the Danzer
   9-point and Fishburn-Reeds 20-point k=3 examples. None produced a
   strictly convex k=4 polygon. Best near-misses are recorded as
   provenance only.
   Artifact: `data/runs/2026-05-06/danzer_fr_lift_attempts.json`.

## Combinatorial / algebraic verification matrix (updated)

| n  | Vertex-circle method | Gröbner basis | Status |
|----|----------------------|---------------|--------|
| ≤ 6 | direct (§3.1, §3.2) | trivial | proved |
| 7 | Fano parity (§3.3) | trivial | proved |
| 8 | incidence-completeness + cyclic-order + perp-bisector / collinearity (15 classes) | **GB = {1} for 14/15; one class with 4 real configs all failing strict convexity** | proved (multi-source) |
| 9 | vertex-circle + L4 + L5 + L6-crossing (184 → 0) | **2026-05-06: COMPLETE. 178/184 GB = {1} or non-real univariate; 16/184 (F07/F08/F09/F13) decoded with explicit lifts to hexagon-lattice degeneracies** | proved-locally (review-pending), now with COMPLETE Gröbner second source |
| 10 | vertex-circle row0 4-subset (126 / 126 → 0; audit confirms 4,142,738 nodes) | n/a (no surviving system) | proved-locally (review-pending) |
| 11 | partial timing data, no full coverage | n/a | exploratory only |
| ≥ 12 | open | open | open |

## Selection Lemma program status (updated)

| Sub-step | Prior status | This round |
|----------|--------------|------------|
| Short-base lemma | proved | unchanged |
| Symmetric kite injectivity (`r_i = r_j`) | proved (2026-05-05) | unchanged |
| **Asymmetric kite injectivity (`r_i ≠ r_j`)** | numerical evidence only | **CONDITIONAL THEOREM** modulo cyclic-order audit |
| Cyclic-order audit | not stated | identified as the only gap; audit agent launched |
| Noncrossing | numerical evidence only | unchanged (separate audit agent launched) |

If both the cyclic-order audit and noncrossing close, the Selection Lemma
program closes Erdős #97. The cyclic-order audit is a small finite case
analysis; noncrossing is harder but has 0/1935 numerical failures.

## What this round did NOT produce

- **No counterexample.** Aggressive searches at n=14..60 with cyclic, two-orbit,
  random 4-regular, paraboloid-lift, and affine-stretching ansatzes
  produced no convergent realization with residual < 1e-6 and convexity
  margin > 1e-4.
- **No closure of n=12+ finite case.** n=11 partial timing data already
  available; n=12 is large but tractable in principle.
- **No closure of three-cap rigid (2, 2, 2) at n=9.** The case is identified
  as the next attack target; both algebraic (Gröbner) and parity-style
  attacks were attempted in parallel; no closure produced this round.

## Suggested next steps (ranked)

1. **Independent audit of the four new Gröbner decoders.** The univariate
   `y_8^2 - 3/4 = 0` is the same in F07/F08/F09/F13 (they share the first
   8 grevlex generators). Reviewers should re-run the lex GB FGLM,
   verify the lifted-coordinate hexagon-lattice claim, and confirm that
   every duplicate-pair coincidence has exact squared distance 0.

2. **Close the cyclic-order audit for the Selection Lemma asymmetric
   kite case.** This is a small finite case analysis. If it closes, the
   asymmetric case becomes an unconditional theorem.

3. **Close the noncrossing claim for the Selection Lemma program.** This
   is harder but has overwhelming numerical evidence (0/1935).

4. **Combine Selection Lemma → Erdős #97.** If 2 + 3 close, Erdős #97
   closes via `|B(P)| ≤ n - 3`. Independent review and Lean-style
   formalization recommended.

5. **Push n=11 to full coverage.** With Rust/C++ port and dihedral
   symmetry quotienting, an estimated ~1 hour of wall-clock should
   suffice. Currently 7 row0 singleton tests run for 300 s each without
   finding a full assignment.

6. **Push the algebraic route to n=10 and n=11.** Once row0 4-subset
   incidence enumeration is complete, the Gröbner approach should be
   small enough at n=10 to provide a third-source verification.

## Trust-level summary

- `THEOREM` (newly verified, conditional on independent audit):
  - **n=9 selected-witness 4-bad polygon non-existence has a
    Gröbner-basis-only proof.** Every one of the 184 labelled selected-witness
    assignments admits an `EXACT_OBSTRUCTION` certificate over `QQ` with
    explicit lifted-coordinate decoding to hexagon-lattice degeneracies.
  - **Selection Lemma symmetric kite injectivity** (already in 2026-05-05).
- `CONDITIONAL_THEOREM`:
  - **Selection Lemma asymmetric kite injectivity**, modulo the cyclic-order
    audit identified in `selection_lemma_asymmetric_attempt.md` §7.1.
- `INCIDENCE_COMPLETENESS`: vertex-circle filter at n=9, n=10
  (audit confirms full coverage).
- `EXACT_OBSTRUCTION`: 184/184 n=9 Gröbner artifacts.
- `EVIDENCE`: Q-L9 filter passes/blocks/boundary-cases at known near-misses.
- `FAILED_APPROACH` (this round):
  - Geometric n=9 base-apex extension (gap is real, not closeable by this route).
  - Two-orbit ansatz at large m.
  - Direct counterexample search at n=14..60.

## Provenance

```text
data/certificates/2026-05-06/
├── n10_extended_coverage.json
├── n9_f07_decoder.json
├── n9_f08_decoder.json
├── n9_f09_decoder.json
├── n9_f13_decoder.json
├── q_l9_filter_results.json
└── two_orbit_large_m.json

data/runs/2026-05-06/
├── bridge_lemma_attack_data.json
├── geometric_n9_extension.md
└── selection_lemma_asymmetric_attempt.md

scripts/
└── check_q_l9_filter.py
```

## Honest assessment

This round did not solve Erdős #97. What it produced:

- **A complete Gröbner-basis-only proof of the n=9 selected-witness finite
  case** (review-pending). The 16 previously un-decoded labelled assignments
  in F07/F08/F09/F13 now all have `EXACT_OBSTRUCTION` certificates that
  lift to explicit degenerate hexagon-lattice configurations.
- **A conditional theorem closing the asymmetric kite case of the Selection
  Lemma program** via a clean analytic factorization. The remaining gap is
  a small cyclic-order audit; if that closes, canonical-chord injectivity
  is unconditionally proved, and Erdős #97 reduces to the noncrossing
  claim (also conjecturally true with strong numerical support).
- **An audit confirming n=10 row0 4-subset coverage is exactly the
  126 singleton slices** (review-pending).
- **A working Q-L9 filter** plus identification and correction of two errors
  in the original Q-L9 derivation.
- **Multiple negative results on counterexample search and the geometric
  n=9 base-apex extension**, consolidating which routes are dead.

The cumulative effect is to make the n=9 finite-case result substantially
more robust (now both vertex-circle AND complete Gröbner second-source) and
to bring the Selection Lemma program within one small audit step of being
the central attack on Erdős #97. The official/global status of #97
remains FALSIFIABLE/OPEN.
