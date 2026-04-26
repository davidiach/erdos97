# STATE.md — Erdős Problem #97 working state

Status: no proof and no counterexample are claimed.

## Problem target
Find a strictly convex polygon with vertices `p_0,...,p_{n-1}` such that for every center `i` there is a 4-set `S_i` not containing `i` and all four squared distances `|p_i-p_j|^2`, `j in S_i`, are equal. Radii and selected 4-sets may vary with `i`; the directed incidence graph need not be symmetric.

## Literature baseline checked 2026-04-26
The Erdős Problems page still lists #97 as open/falsifiable. Known nearby examples: Danzer gave a 9-point convex polygon with 3 equidistant vertices from every vertex, radius depending on the center; Fishburn–Reeds gave a 20-point convex polygon with 3 unit-distance vertices from every vertex. These do not imply the 4-neighbor target.

## Rigorously survived lemmas
1. Circle-intersection incidence cap: in any true counterexample, for distinct centers `a,b`, `|S_a ∩ S_b| <= 2`. Proof: two distinct Euclidean circles intersect in at most two points.
2. Consequence: no counterexample with `n <= 6`. For `n=5`, every pair of 4-sets shares 3 points. For `n=6`, write `S_i = V \ {i,f(i)}`; the pair `(i,f(i))` has intersection at least 3.
3. Incidence counting: if `d_j` is the indegree of vertex `j`, then `sum_j binom(d_j,2) <= 2 binom(n,2)` and `sum_j d_j=4n`; convexity of `binom(d,2)` gives `n>=7`.
4. Equality case `n=7`: all indegrees are 4 and every pair of selected 4-sets intersects in exactly 2 points. Complements `T_i=V\S_i` are Fano lines of size 3 with `i in T_i`. For any centers `i,j`, if `S_i ∩ S_j={a,b}`, then segment `p_a p_b` is perpendicular to segment `p_i p_j` by the radical-axis theorem.
5. Finite `n=7` Fano obstruction: the reproducible enumeration in `scripts/enumerate_n7_fano.py` finds 30 labelled Fano planes, 720 pointed equality families, and 54 cyclic-dihedral classes. Every class has chord-cycle type `7+7+7`, so the required perpendicularity constraints contain odd cycles and cannot be realized by nonzero Euclidean chords. See `docs/n7-fano-enumeration.md`.

## Candidate incidence patterns
Priority patterns in the current code:
- `B12_3x4_danzer_lift`: `i=(a,b)` mod `(3,4)`, `S_i={(a+1,b),(a+2,b),(a+1,b+1),(a+2,b-1)}`.
- `B20_4x5_FR_lift`: `i=(a,b)` mod `(4,5)`, `S_i={(a+1,b),(a-1,b),(a+1,b+2),(a-1,b-2)}`.
- `P18_parity_balanced`, `P24_parity_balanced`.
- Skew circulants `C17_skew`, `C19_skew`.
- Palindromic circulants `C9_pm_2_4`, `C13_pm_3_5`, `C16_pm_1_6`, `C20_pm_4_9`.

All built-in patterns satisfy the pairwise common-selected-neighbor cap `<=2`.

## Numerical status
Best current near-miss is `B12_3x4_danzer_lift` with constrained SLSQP at margin `1e-6`:
- max squared-distance spread: about `0.00680637`
- RMS equality residual: about `0.00195995`
- convexity margin: about `1e-6`
- minimum edge length: about `7.47e-4`
Coordinates are essentially four tiny clusters near each vertex of an equilateral triangle. As the enforced convexity/edge margins are decreased, residual decreases, so this is probably a boundary degeneration, not evidence for a strict counterexample.

Saved files:
- `src/erdos97/search.py`: runnable search engine.
- `data/runs/best_B12_slsqp_m1e-6.json`: best numerical near-miss.
- `certificates/best_B12_certificate_template.json`: exact-certificate skeleton.

## Failed/unsafe proof ideas
- Do not claim equal-distance vertices around one center are limited to two; Danzer's 3-neighbor example already rules out the naive version.
- Do not use an end-neighbor/middle-neighbor/forest argument without proof. The selected directed graph is not planar, need not be symmetric, and selected radii need not be nearest/farthest distances.
- Do not impose common radius unless explicitly searching the Fishburn–Reeds-like subclass.
- Do not assume coordinate symmetry from incidence symmetry. Full cyclic coordinate symmetry forces a regular polygon and usually kills the desired two-offset equalities.

## Next experiments
1. Analyze the `B12` cluster degeneration symbolically; add a penalty lower-bounding cluster diameter / convexity margin and see whether residual has a positive lower bound.
2. Run the same constrained margin sweep for `B20_4x5_FR_lift`; look for non-cluster near-misses.
3. Add a true interval/SOS lower-bound attempt for fixed patterns: minimize equality residual subject to rational convexity margins.
4. Implement incidence SAT with stronger necessary geometric constraints, but keep optional heuristics separate from necessary constraints.
5. If a candidate reaches residual <1e-10 with convexity margin and edge length comfortably >1e-3, start exactification via algebraic recognition.
