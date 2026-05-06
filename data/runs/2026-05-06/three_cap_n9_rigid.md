# Rigid (2,2,2) three-cap at n = 9: the §4.4 bridge lemma is FALSE

Cross-checked: `data/runs/2026-05-05/L9_sharpening.md` §4,
`data/runs/2026-05-05/three_cap_analysis.md` §§4–7, `docs/canonical-synthesis.md` §5.4.

Scripts: `/tmp/three_cap_n9_caseA_canonical.py`, `caseA_verify.py`,
`caseA_bounds.py`, `caseA_X1bad.py`, `v3.py` (Gröbner), `v4.py`,
`check_initial.py`.

## 1. THEOREM (sympy proof in `caseA_canonical.py`, `caseA_verify.py`)

> For every `a ∈ (0, π/6)`, the 9 points
>
> ```
> p = (1,0),  q = (−1/2, √3/2),  r = (−1/2, −√3/2)
> X_1 = p + √3·(cos(π−a), sin(π−a)),  X_2 = p + √3·(cos(π+a), sin(π+a))
> Y_i = R_{2π/3} X_i,  Z_i = R_{4π/3} X_i  (i = 1,2)
> ```
>
> form a strictly convex 9-gon (CCW order `p, Z_1, Z_2, q, X_1, X_2, r, Y_1, Y_2`)
> with SEC the unit circle, supported by `{p, q, r}`, and
> `M(p) = M(q) = M(r) = 4` (witness radius `√3`; witnesses `{X_1,X_2,q,r}`
> and Z₃-rotates), `M(V) = 2` for every cap-interior `V`.

**Proof outline.** `|p−X_i|² = 3 = |p−q|² = |p−r|²` directly; Z₃ rotation
gives the same at `q, r`. From `X_1`, only `{Y_1, Z_1}` lies at common squared
distance `12 − 6√3 cos a`, so `M(X_1) = 2`. The nine cyclic-cross terms split
as six copies of `3 sin(a)(2 cos(a) − √3)` and three further factors all
strictly positive on `(0, π/6)`. Cap-interior squared norm
`|O − V|² = 4 − 2√3 cos a < 1` iff `a < π/6`. ∎

This contradicts the §4.4 conjecture `min{M(p), M(q), M(r)} ≤ 3` in the
rigid `(2,2,2)` configuration.

## 2. Where §4.4 misses

§4.2 bound (cap lemma): at most 1 witness of `p` in cap `K_pq`. **In CASE A
this is saturated by `q` itself, not by a cap-interior vertex** — identically
at `K_pr` by `r`. §4.4 implicitly read "≤ 1 *cap-interior* witness," but
`three_cap_analysis.md` §6 already flagged this as "configuration (A)" —
CASE A is the explicit `n = 9` realisation. The hoped-for `X_*` (vertex in
`K_qr` witness of `p` only) does not exist; the perpendicular-bisector
parity attack has nothing to act on.

## 3. Gröbner status

**FAILED_APPROACH.** No `Gröbner = {1}` certificate:

* CASE A (`r_p = √3`): six equations, 12 vars ⇒ **6-D complex variety**,
  with a 6-D real open subset (each cap-vertex on its 60° arc).
* CASE B (`r_p ≠ √3`, one cap-interior witness per neighbour cap): nine
  equations, Gröbner basis size 9 over `ℚ[√3]`, variety naively 3-D
  (`v3.py`).

The three perpendicular-bisector constraints are mutually compatible; no
§3.3-style algebraic obstruction arises.

## 4. CASE A and Erdős #97

CASE A is **not** a #97 counterexample (cap-interior vertices have `M=2`).
**NUMERICAL_EVIDENCE (`caseA_X1bad.py`):** 30,000 random non-Z₃ CASE A
configurations + strict-convexity check yielded zero hits with `M(X_1) ≥ 4`.

**CONJECTURE.** If the SEC of a strictly convex `n=9`-gon is supported by
three 4-bad vertices `p, q, r`, then `r_p = r_q = r_r = |pq| = |qr| = |rp|`
(CASE A) and no other vertex is 4-bad. If true, the rigid `(2,2,2)`
configuration has exactly 3 bad vertices, hence #97 holds at `n=9` for the
3-cap subcase.

## 5. Next attacks

1. **Refined conjecture §4.** Show no 4-equidistant set among the 8
   vertices `{p, q, r, X_2, Y_1, Y_2, Z_1, Z_2}` exists in the 6-D moduli.
2. **Drop equilateral.** CASE A needs `r_p = |pq| = |pr|` (isoceles at `p`).
   Imposing this at all three apexes forces equilateral. So non-equilateral
   non-obtuse `△pqr` cannot support all three being 4-bad — easier subcase.
3. **L4 constraint.** In CASE A the perpendicular bisector of `X_1 X_2` is
   `Op`, already saturated by `X_1, X_2`. Restricts the moduli further.

## 6. Concrete sample (`a = 1/5`)

```
p   = (1, 0)                    q = (−0.5, 0.866025)    r = (−0.5, −0.866025)
X_1 = (−0.697525,  0.344105)    X_2 = (−0.697525, −0.344105)
Y_1 = ( 0.050759, −0.776127)    Y_2 = ( 0.646767, −0.432022)
Z_1 = ( 0.646767,  0.432022)    Z_2 = ( 0.050759,  0.776127)
```

All `|p−X_i| = |p−q| = |p−r| = √3` exactly (and Z₃-rotates).

## 7. Summary

| Claim | Status |
|---|---|
| §4.4 rigid (2,2,2) bridge lemma at `n=9` | **THEOREM (false).** 1-parameter family. |
| §5.4 three-cap bridge lemma | Open; §4.4 form blocked, refined claim §4 is new target. |
| Erdős #97 at `n = 9` | **Open**; CASE A does NOT counterexample it. |
| Gröbner certificate | **FAILED_APPROACH** (6-D real variety). |
| `n = 8` three-cap closure (§4.3) | Unaffected. |

## 8. Takeaways

* The three "forced perpendicularities" §3.3-analogue **fails** in the
  equilateral 3-cap: the three bisectors are the medians of `△pqr`,
  through `O`, no extra algebraic content.
* §4.2 cap-lemma counting bounds *cap closures*, not *interiors*. The bridge
  lemma must distinguish SEC-support from cap-interior witnesses of `p`.
* For #97 the obstruction must come from cap-interior vertices: in CASE A
  they cannot all be 4-bad (numerical evidence; symbolic proof open).
* `canonical-synthesis.md` §5.4: the three-cap bridge lemma should be
  reclassified — §4.4 form **false**, refined claim §4 is the new target.
