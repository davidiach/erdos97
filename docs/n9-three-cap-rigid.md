# n=9 three-cap rigid (2,2,2) case — closure under the cap-occupancy hypothesis

**Status:** MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING. No general
proof and no counterexample of Erdős #97 is claimed. This memo records a
conditional combinatorial closure of the rigid (2, 2, 2) sub-case of the
three-cap SEC reduction at n = 9 (canonical-synthesis.md §5.4). The
official/global FALSIFIABLE/OPEN status of #97 is unchanged.

## 1. Setup

Following §5.4 and erdos97-attack-2026-05-05.md, suppose by contradiction
that a strictly convex 9-gon V is 4-bad (every vertex has 4 other polygon
vertices on a common circle around it). The smallest enclosing circle
(SEC) of V is supported by either two diametrically opposite vertices
(diameter case) or by a non-obtuse triangle (three-cap case). The
diameter case is closed via the inscribed-arc Moser cap lemma applied at
the two SEC support endpoints. We address the three-cap case at n = 9.

In the three-cap case, let p, q, r be the SEC supports. The polygon V
decomposes by its cyclic order into three caps K_pq, K_qr, K_rp (the
cyclic arcs of V between consecutive SEC supports, excluding the supports
themselves). Cap-occupancy counting at n = 8 (2026-05-05 attack) ruled
out all-three-bad: each support being 4-bad requires >= 2 of its 4
witnesses inside the opposite cap, summing to >= 6 cap-interior vertices,
hence n >= 9. At n = 9 the only configuration consistent with the cap
forcing is the rigid (2, 2, 2) case where each open cap holds exactly 2
polygon vertices.

Layout (cyclic order): p, a, b, q, c, d, r, e, f, with vertex indices
0..8. Caps: K_pq = {a, b}, K_qr = {c, d}, K_rp = {e, f}. The
cap-occupancy bound gives the **forced witness inclusions**

    {c, d} ⊆ W_p,    {e, f} ⊆ W_q,    {a, b} ⊆ W_r.

Each of W_p, W_q, W_r has 4 elements: 2 forced and 2 free.

## 2. Cap-occupancy hypothesis (used here)

For SEC support p, p is on the SEC and the inscribed-arc form of the
Moser cap lemma gives chord-length monotonicity along the SEC arc from p
to q, hence at most 1 SEC-arc point at any given distance from p. As
flagged in `data/runs/2026-05-05/three_cap_analysis.md`, this argument
applies cleanly at the SEC support points but the cap-interior polygon
vertices are not on the SEC. So the strict "≤ 1 cap-interior witness in
each near cap" claim only applies to inscribed configurations and is
weaker in general. The cap-occupancy hypothesis we use is the form that
suffices for the n = 8 closure: each of p, q, r being 4-bad requires
**at least two witnesses inside its opposite cap**. We do not strengthen
this further. The closure below is conditional on this hypothesis.

## 3. Combinatorial enumeration

Stage (i) enumerates all triples (W_p, W_q, W_r) where each W_x is a
4-subset of V \\ {x} containing the forced cap-pair, modulo the dihedral
D_3 action on the (p, q, r) cycle, after applying

- L4 (perpendicular-bisector vertex bound: at most 2 polygon vertices on
  any pair's perpendicular bisector — non-trivial only for pairs lying in
  all three of W_p, W_q, W_r),
- L5 (two-circle bound: |W_i ∩ W_j| <= 2 for i != j).

**Result.** 373 canonical D_3-classes survive.

The L6 perpendicular-overlap distribution across the 373 classes is

    num_overlaps_size_2 = 0:   24 classes
    num_overlaps_size_2 = 1:  148 classes
    num_overlaps_size_2 = 2:  152 classes
    num_overlaps_size_2 = 3:   49 classes

This 3-row metric system has 9 polynomial equidistance equations on 14
coordinate variables (after gauge-fixing): generically the variety is
high-dimensional (≥ 5), so direct sympy Gröbner trivialisation is not
expected. The over-determination needed for a parity / rank obstruction
analogous to §3.3's n = 7 argument requires *more* simultaneous
equidistance constraints (i.e., row equidistances at additional vertices
of V).

## 4. Cross-check against the n = 9 cross-check survivors

Stage (ii) leverages the existing n = 9 vertex-circle exhaustive
enumeration (committed at
`data/certificates/n9_vertex_circle_exhaustive.json` and
`data/certificates/2026-05-05/n9_groebner_results.json`). That
enumeration produced **184 selected-witness assignments at n = 9** (in
cyclic order, no symmetry quotient) that pass the basic L4 + L5 + L6 +
pair-cap + indegree filters. They collapse into **16 dihedral D_9
families**.

Concretely, for each family representative we ask: does any of the 18
elements of D_9 (rotations × reflections) applied to the representative
admit a placement (p, q, r) at cyclic positions (s, s+3, s+6) (mod 9)
satisfying the rigid (2, 2, 2) cap-occupancy

    W_s     ⊇ {s + 4, s + 5},
    W_{s+3} ⊇ {s + 7, s + 8},
    W_{s+6} ⊇ {s + 1, s + 2}    (mod 9).

The check covers all 184 individual assignments at all 3 possible
(p, q, r) cyclic placements (the only way to give cap sizes (2, 2, 2) for
n = 9 is to have SEC supports evenly spaced at gaps of 3).

**Result.** **0 / 16 dihedral families** and **0 / 184 individual
assignments** admit the rigid (2, 2, 2) cap-occupancy under any element
of D_9.

A sanity sub-check: even the *single-row* condition "some vertex i has
both (i + 4) mod 9 and (i + 5) mod 9 in its witness set" already fails
for 14 / 16 families. The remaining 2 families that do exhibit a single
such vertex (F02, F03; both are GB = {1} families that are also killed
by the vertex-circle filter for self-edge reasons) still fail the joint
3-vertex condition.

## 5. Conclusion

**Claim.** Conditional on the cap-occupancy hypothesis, the rigid
(2, 2, 2) sub-case of the three-cap SEC reduction at n = 9 is closed at
the L4 + L5 + L6 + pair-cap + indegree level: no selected-witness
assignment that survives those filters even admits the
(2, 2, 2) cap-occupancy combinatorial structure.

**What this gives.** Combined with the (review-pending) n = 9
vertex-circle exhaustive result (which already kills all 184 cross-check
survivors via filter 5), this gives an independent, parallel route to the
same conclusion that does not rely on the vertex-circle / Gröbner step
for the (2, 2, 2) sub-case specifically. Note however that the
vertex-circle exhaustive result has already closed n = 9 at the level of
the *combinatorial* finite case; the present check refines this by
showing that *under the cap-occupancy hypothesis* the closure happens at
an even earlier filter stage.

**What this does NOT give.**

1. It does **not** prove Erdős #97. The general n problem is unaffected.

2. It does not close the diameter case at n = 9 (already closed via the
   Moser cap lemma) — that was independent.

3. It does not address the **non-rigid three-cap cases** (a, b, c) ≠
   (2, 2, 2) at n >= 10, which are the next attackable sub-cases. At
   n = 10 with three-cap sums to 7, the partitions (2, 2, 3),
   (1, 3, 3), and (1, 2, 4) all need separate analysis.

4. The cap-occupancy hypothesis is the form actually needed for the
   n = 8 closure but is weaker than the strong "interior-cap distances
   from p are pairwise distinct" sometimes invoked in earlier drafts.
   The strong form remains an open audit item (see
   `data/runs/2026-05-05/three_cap_analysis.md`).

5. Stage (i)'s 373-class enumeration is independent of the n = 9
   vertex-circle artifact and would also be closed if a parity / rank
   obstruction analogous to the §3.3 n = 7 argument could be derived
   directly from the 3-row equidistance system. We did not produce such
   an obstruction; the system has only 9 quadratic equations on 14
   variables and is generically positive-dimensional.

## 6. Reproducibility

```
python3 scripts/check_n9_three_cap_222.py --write
```

writes the certificate at `data/certificates/n9_three_cap_222.json`.

## 7. Provenance

| Artifact | Description |
| --- | --- |
| `scripts/check_n9_three_cap_222.py` | Combinatorial enumeration + cross-check |
| `data/certificates/n9_three_cap_222.json` | Machine-readable certificate (this round) |
| `data/certificates/2026-05-05/n9_groebner_results.json` | The 16 dihedral families used in stage (ii) |
| `data/certificates/n9_vertex_circle_exhaustive.json` | The base 184 cross-check survivors |
| `docs/canonical-synthesis.md` §5.4 | Three-cap reduction setup |
| `docs/erdos97-attack-2026-05-05.md` | Cap-occupancy bound at n = 8; identified n = 9 (2,2,2) target |
| `data/runs/2026-05-05/three_cap_analysis.md` | Cap-lemma audit + open gaps |
