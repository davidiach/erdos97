# A4 — Endpoint-Control descent + Three-cap diameter bridge

Date: 2026-06-14
Lane: A4 (endpoint-control + diameter caps). Adjacent lane A3 (ear-orderability) NOT touched.
Author context: research subagent, repo erdos97, branch claude/amazing-goldberg-8tcsju.

Trust labels used: `EXACT_NEGATIVE_CONTROL`, `EXACT_DIAGNOSTIC`,
`OPEN_GAP_RESTATEMENT`, `CONDITIONAL_REPAIR_HYPOTHESIS`. **No general proof and no
counterexample of Erdős #97 is claimed.** The official/global status is unchanged
(open). Any impossibility route below uses strict convexity explicitly.

Reproduction:
```bash
python scripts/exploration/a4_failed18_endpoint_reexam.py     # Sec A,B,C below
python scripts/exploration/a4_three_cap_diameter_bridge.py    # Sec D,E below
```
Both use only `sympy` Rational arithmetic and finish in < 10 s.

---

## A. The two open gaps, stated precisely

### A.1 §5.1 Endpoint-Control Auxiliary Claim (descent step) — `OPEN_GAP_RESTATEMENT`

Setup (canonical-synthesis §5.1). Let `m := min_i M(i) >= 4` and pick
`(i*, r*)` with `|S_{i*}(r*)| = m`. Set `A := S_{i*}(r*)`, angular endpoints
`v_-, v_+` (indices `j^-, j^+`). The following are **proved** (L1, L3, L7):
the witnesses are angular-ordered with span `< pi`; endpoint chord-lengths are
strictly monotone; hence `|S_{j}(rho) ∩ (A ∪ {i*})| <= 2` for any endpoint `j`
and any `rho`.

> **Open descent step (Endpoint Control).** Some endpoint `j ∈ {j^-, j^+}` has
> `|S_j(rho) \ (A ∪ {i*})| <= m - 3` for every `rho > 0`.

If true, then `M(j) <= 2 + (m-3) = m-1`, contradicting minimality of `m` and
forcing a vertex with `M <= 3` by descent. The gap is the global "outside-of-A"
control.

### A.2 §5.4 Three-cap diameter bridge — `OPEN_GAP_RESTATEMENT`

The smallest enclosing circle (SEC) of `V` is supported either by 2 antipodal
vertices (**diameter case: cited as proved**) or by 3 vertices `p, q, r` forming
a non-obtuse triangle (**three-cap case: open**). Caps `K_pq, K_qr, K_rp`.
Chord `pq` has `p, q` as endpoints, so a cap lemma controls `p`'s distances into
`K_pq, K_rp` but **not** into the opposite cap `K_qr`. So a bad `p` has `>= 2`
witnesses in `K_qr` (symmetrically `q → K_rp`, `r → K_pq`).

> **Open three-cap bridge.** If `p` is bad, some equal-distance pair `{x,y}` at
> `p` lies in a single cap (a diagonal inside that cap); then witness-packing in
> caps closes the case.

---

## B. Failed-idea-#18 re-examination (the core deliverable) — `EXACT_NEGATIVE_CONTROL`

Heeding the SHARED-CONTEXT instruction (do **not** re-assert the local
shortcut), I re-derived in exact arithmetic *why* the purely-local endpoint
claim fails on the #18 9-point config, and what the minimal global input is.

**All #18 facts verified exactly** (`a4_failed18_endpoint_reexam.py`, §1–§2):
- Base config `O, L0, L1, A1, A2, A3, A4, U1, U0` is strictly convex (all 9 turn
  determinants `> 0`, matching the recorded values `3/65, 4/65, 1/50, 6/25,
  6/25, 1/50, 4/65, 3/65, 1161/4225`).
- `|O A_k|^2 = 1` for `k=1..4` (O-unit-rich).
- Endpoint `A1`: `|A1 L0|^2 = |A1 L1|^2 = 1/4`. Endpoint `A4`:
  `|A4 U0|^2 = |A4 U1|^2 = 1/4`. So **both endpoints carry 2 outside witnesses**
  at `rho = 1/2`, i.e. `|S_{A1}(1/4) \ (A ∪ O)| = 2 > m-3 = 1` and likewise for
  `A4`. The local "at least one endpoint is outside-poor" reading is **exactly
  false**. (The #18 extension makes each endpoint carry 4 such outside points.)
- Outside points are off O's unit circle: `|O L0|^2 = |O U0|^2 = 261/260`,
  `|O L1|^2 = |O U1|^2 = 5/4`.

**The decisive new finding (§3 of the script).** I computed the full per-vertex
maximum equal-distance multiplicity `M(i)` of the base config:

| vertex | `M(i)` |
|---|---|
| O | **4** |
| A1, A4 | 2 |
| L0, L1, A2, A3, U1, U0 | 1 |

So **`min_i M(i) = 1`, attained at the outside/middle vertices — while
`M(O) = 4` is the maximum.** The #18 configuration places the descent center O
at a *maximizer* of `M`, not the minimizer the §5.1 reduction requires.

**Why the local shortcut is unfixable, and what repairs it.** The §5.1 reduction
is only allowed to invoke the endpoint claim at a center `i*` chosen as a
**global minimizer** of `M`. The shortcut dropped that hypothesis and asked O's
endpoints to be outside-poor as if O's row were a *minimal* row. But O is the
richest vertex here; its angular-endpoint witnesses `A1, A4` are interior-type
vertices free to be rich. Thus #18 lies **entirely outside the minimal-descent
regime** and is fully consistent with the (still open) global Aux Claim — it
neither certifies nor refutes it. The minimal global ingredient the shortcut is
missing is precisely:

> **`CONDITIONAL_REPAIR_HYPOTHESIS` — minimality of the chosen center.** `i*` is
> a global minimizer of `M(i)`. Under minimality, an endpoint `j` with
> `M(j) <= m-1` is an immediate contradiction; the reduction's real content is
> "`m` cannot be the minimum unless some vertex already has `M <= 3`", i.e. a
> finite descent. #18 violates minimality (`M(O)=4 ≠ min = 1`), so it is not a
> witness against the claim.

This matches `docs/failed-ideas.md` #18's own closing note ("Any proof must use
additional global minimal-counterexample information, not only these local
hypotheses") and sharpens it to a concrete, checkable statement: *the descent
center must be a global `M`-minimizer, and #18 is a global `M`-maximizer at O.*

---

## C. A candidate descent ingredient, and where it still falls short

The shortcut needs a *quantitative* obstruction the local cap geometry cannot
supply. The **turn-inequality lemma** (`docs/turn-inequality-lemma.md`) is the
natural lever: for any center and any equal-distance witness pair at offsets
`a < b`, the exterior turn on the connecting arc strictly exceeds `pi/2`. Its
driver `u·v = -|v|^2/2 < 0` was verified **exactly** at O for all six witness
pairs (`a4_failed18_endpoint_reexam.py` §4): e.g. pair `(A1,A2)` gives
`u·v = -1/25`, pair `(A1,A4)` gives `-32/25`, etc., each exactly `-|v|^2/2`.

**Candidate charging argument (sketch, NOT proved).** At a global minimizer `i*`,
suppose for contradiction that *both* endpoints fail, i.e. each of `j^-, j^+`
carries `>= m-2` equal-distance witnesses outside `A ∪ {i*}`. The two boundary
chains from `j^-` to `j^+` partition `V \ A \ {i*}` (§5.1 sub-question 3). Each
outside equal pair at an endpoint spends `> pi/2` of exterior turn on a sub-arc
of those chains (turn-inequality). Summing the forced turns over both endpoints'
outside pairs must not exceed the total `2π` turning of the polygon minus the
turn already consumed by the A-cap. For `m` large relative to `n` this
over-spends the budget — giving the contradiction and the descent.

**Why it is not yet a proof (the exact remaining hypothesis).** The budget
argument closes only when `m` is bounded relative to `n` — concretely the
endpoint claim is *non-vacuous* only for `m < (n+2)/2` (§5.1 sub-question 2),
and the turn accounting needs the outside pairs at the two endpoints to live on
*disjoint* arcs so their `> pi/2` charges add. Neither is currently established:
- the `m < (n+2)/2` bound is not derived from minimality in the archive;
- the disjoint-arc/non-overlap condition is exactly the L–R asymmetry flagged in
  §5.1 sub-question 1 (why "at least one" endpoint, not "both") and in
  `docs/erdos97-attack-2026-05-05.md` ("same-side cases require a tie-breaking
  rule on `(i*, r*)`").

So the honest status: **minimality + turn-inequality is a plausible route to the
descent step, but it requires (i) an `m`-vs-`n` bound and (ii) a tie-break /
non-overlap lemma that breaks the endpoint symmetry.** I did not prove either.

---

## D. Three-cap bridge: what closes, what doesn't — `EXACT_DIAGNOSTIC`

(`a4_three_cap_diameter_bridge.py`.)

### D.1 The n=8 cap-occupancy closure is sound (reproduced exactly)
If `p, q, r` are all bad, each sends `>= 2` witnesses to its **opposite** cap;
the three opposite caps are disjoint and contain only non-support vertices, so
`n - 3 >= 6`, i.e. `n >= 9`. Hence for `n = 8` some support vertex has `M <= 3`.
The count: `n=8 → n-3 = 5 < 6` (forces), `n=9 → 6 = 6` (counting insufficient),
`n=10 → 7 ≥ 6` (insufficient). This count needs **no** intra-cap distinctness, so
it is independent of the Moser caveat below.

### D.2 The Moser cap-lemma caveat, pinned down exactly
The §5.4 wording "distances from a chord endpoint to convex-position points
inside the cap are all distinct" is only the **inscribed** statement. I verified
exactly:
- **On the SEC arc** distances from `p=(-1,0)` are strictly monotone
  (`4/5 < 2 < 16/5 < 18/5`) — inscribed Moser holds.
- **Strictly inside** the SEC disk, two points `X=(-2/5,4/5)`, `Y=(-1/5,3/5)` are
  at *equal* distance `1` from `p` (both interior, `|X|^2=4/5`, `|Y|^2=2/5 < 1`).

**Structural conclusion.** In a strictly convex polygon with 3-support SEC,
every non-support vertex is strictly *inside* the open SEC disk, so inscribed
monotonicity does **not** apply to it. The cap lemma controls only on-arc
vertices — of which a generic cap has none besides the two support endpoints. It
gives **no** distinctness control over the interior cap vertices where a bad
center's witnesses actually live. (The #18 arc `A1..A4` is itself four
convex-position points equidistant from a hull vertex — equidistance among
convex-position points off a common SEC arc is the rule, not the exception.)

This is the precise reason three-cap does not close by the diameter case's
one-line argument: the opposite cap `K_qr` is a **blind spot** for `p`.

### D.3 The diameter case (caveat noted, not re-proved)
canonical-synthesis §5.4 cites the diameter case as proved via the Moser cap
lemma (Dumitrescu survey). `docs/erdos97-attack-2026-05-05.md` flags that the
§5.4 wording needs the stricter inscribed reading and recommends re-deriving the
diameter `E(p) <= 2` conclusion under it; it records that the n=8 cap-occupancy
count uses only the inscribed special case at SEC-support vertices and is safe.
**I did not re-prove the full diameter `E(p) <= 2` statement**; I flag it as
cited / review-pending, consistent with no-overclaiming.

---

## E. The exact global hypothesis the three-cap bridge needs

The missing handle is on the **opposite (blind) cap**. Two candidate global
ingredients, with my assessment:

1. **Diameter-pair isolation — does NOT directly apply.** A non-obtuse 3-support
   SEC has no antipodal diameter pair, so there is no diameter to isolate; the
   only metric handles are the three SEC-radius equalities `|Op|=|Oq|=|Or|`.

2. **Radius-drop cascade / per-cap occupancy descent — the natural target.** A
   witness pair `{x,y}` of `p` both inside `K_qr` is a diagonal whose endpoints
   are themselves bad; their opposite caps are `K_pq, K_rp`. Chaining "every bad
   vertex pushes `>= 2` witnesses to its opposite cap" around the 3 caps yields a
   closed per-cap occupancy system that can be counted cap-by-cap. This is the
   concrete finite-descent target.

3. **n=9 rigid `(2,2,2)` case — the sharp sub-case (open).** For `n=9` all-bad
   with 3-support SEC, occupancy saturates: exactly 2 non-support vertices per
   cap, and each support vertex's 2 opposite-cap vertices are *forced*
   equidistant from it. Via L6 (`W_p ∩ W_q = {a,b} ⇒ pq ⟂ ab`) plus the 3 SEC
   radius equalities and the full 4-witness rows, this is an **overdetermined
   perpendicularity system** — the direct analogue of the §3.3 `n=7` parity
   argument. This is exactly the attack target named in
   `docs/erdos97-attack-2026-05-05.md`. **It remains open; I did not resolve it.**

---

## F. What I did NOT establish (explicit)

- I did **not** prove the Endpoint-Control Auxiliary Claim or close the §5.1
  descent step.
- I did **not** derive the `m < (n+2)/2` bound from minimality, nor the
  endpoint non-overlap / tie-break lemma needed by the turn-budget route.
- I did **not** prove the Three-Cap Bridge Lemma, the per-cap occupancy descent,
  or the `n=9` `(2,2,2)` L6-overdetermination.
- I did **not** re-prove the full diameter-case `E(p) <= 2` statement (cited /
  review-flagged).
- Nothing here promotes any finite-case artifact or changes the open status.

## G. Net contributions

1. **Sharpened the §5.1 gap with an exact root cause:** in #18, `min_i M(i)=1`
   but `M(O)=4`, so #18 is a global `M`-maximizer at the descent center — it lies
   outside the minimal-descent regime and the missing ingredient is *minimality
   of the chosen center* (made concrete and checkable). This explains the #18
   negative control without re-asserting the local shortcut.
2. **Identified turn-inequality + minimality as the candidate descent lever,**
   verified its exact driver at O, and stated the two precise sub-hypotheses
   (`m`-vs-`n` bound; endpoint non-overlap) that still block it.
3. **Pinned the Moser cap-lemma caveat exactly:** inscribed monotonicity holds
   on the SEC arc but non-support cap vertices are strictly interior, so the cap
   lemma cannot see them — the structural reason the opposite cap is a blind spot
   and three-cap is hard. Confirmed the n=8 count is safe because it uses
   opposite-cap occupancy, not intra-cap distinctness.
4. **Restated the exact global hypotheses** for three-cap (per-cap occupancy
   descent; `n=9` `(2,2,2)` L6-overdetermination) and noted diameter-pair
   isolation does not apply to a non-obtuse 3-support SEC.

Artifacts: `scripts/exploration/a4_failed18_endpoint_reexam.py`,
`scripts/exploration/a4_three_cap_diameter_bridge.py` (both exact, ruff-clean).
