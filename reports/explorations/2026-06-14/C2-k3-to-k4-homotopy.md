# C2: exact / validated k=3 -> k=4 witness-lift continuation

Date: 2026-06-14
Lane: C2 (exact/validated homotopy lifting a 4th equal-distance witness from a
k=3 base). Owns ONLY the k=3 -> k=4 continuation route; does not overlap C1
(free-form global numerical search).

Problem (Erdos #97): Is there a strictly convex n-gon in which every vertex i
has a 4-set S_i of other vertices all at one (per-center) squared distance? The
k=3 analogue is FALSE (finite examples exist: Danzer 9-point; Fishburn--Reeds
20-point). The k=4 status is open.

Trust labels used below: `EXACT_OBSTRUCTION` (symmetric arm closed form),
`NUMERICAL_EVIDENCE` (asymmetric deformation arm). No `COUNTEREXAMPLE_CANDIDATE`
is produced; nothing here proves or disproves Erdos #97.

Reproduction:

```bash
python scripts/exploration/c2_k3_to_k4_homotopy.py \
  --m-values 4 5 6 7 8 10 12 --asym-m 6 --dps 45 --trials 8 \
  --out data/runs/c2_k3_to_k4_2026-06-14/c2_k3_to_k4_homotopy.json
```

Stored artifact:
`data/runs/c2_k3_to_k4_2026-06-14/c2_k3_to_k4_homotopy.json`.

---

## The NEW ingredient vs failed-ideas.md #20

failed-ideas.md #20 (Fishburn--Reeds cut-matrix nearest-fourth homotopy,
`docs/fr-cut-homotopy.md`, `scripts/fr_cut_homotopy.py`) had a specific failure
mode driven by four design choices:

1. base = a **decimal transcription** of the FR 20-point k=3 table used as a
   two-class cut-matrix scaffold;
2. fourth-witness rule = the **nearest non-edge vertex across the cut**, a
   combinatorial pick fixed once at the seed;
3. homotopy parameter `t` = the **soft residual weight** on the new equality
   (`res += sqrt(t) * (dist^2 - R)`), relaxed by a float `least_squares`
   smoother with simultaneous radius release;
4. convexity read off **floating-point** margins only.

Its informative runs either rode the strict-convexity boundary before leaving
`t=0` or reached `t=1` with four-witness RMS residual ~7e-2 (no candidate).

This lane changes the failure mode on four independent axes (so it is not the
same route and is permitted by the C2 guardrail):

1. **Continuation parameter is geometric**, not a constraint weight: the
   radius-ratio `b` of an exact alternating two-radius `m`-gon (symmetric arm)
   and direct vertex positions (asymmetric arm). There is no `t` multiplying a
   residual.
2. **Fourth-witness rule = paired-distance merge** `D(r_even) = D(r_odd)`: the
   exact algebraic coincidence of two already-present paired distances at a
   vertex, not a nearest-non-edge choice.
3. **The 4th equality is enforced as a hard equation** -- closed form
   (symmetric arm) or hard equality residual with an **mpmath `dps>=45`
   recheck** (asymmetric arm) -- never down-weighted.
4. **Convexity is exact / high-precision**: signed turn determinants in sympy
   (symmetric) and an mpmath recheck of the best configuration (asymmetric).

---

## Symmetric arm (EXACT_OBSTRUCTION)

Base family: the alternating two-radius regular `m`-gon (`n = 2m`), vertices on
equally spaced rays at angle `k*h`, `h = pi/m`, radii alternating `1, b`. It is
strictly convex exactly on the window `cos h < b < sec h`
(`docs/two-orbit-radius-propagation.md`).

In this family each vertex already has equal-distance **pairs**: vertex 0 and
the vertex at offset `r` have squared distance `2 - 2 cos(r h)` for even `r`
(same ring, independent of `b`) and `1 + b^2 - 2 b cos(r h)` for odd `r`; the
offsets `r` and `2m - r` collide, giving a pair. A genuine **4-set** at vertex 0
needs two distinct pairs to merge: an even offset `r_e` and an odd offset `r_o`
with `D(r_e) = D(r_o)`, i.e. the quadratic in `b`

```text
q(b) = b^2 - 2 cos(r_o h) b + (2 cos(r_e h) - 1) = 0.
```

Result (exact, sympy): for every tested `m` in `{4,5,6,7,8,10,12}`, EVERY real
positive merge root `b` lies OUTSIDE the strict-convexity window
`(cos h, sec h)`. Sample (nearest merge `r_e=2, r_o=1`):

| m | convex window | nearest merge roots b | in window? |
|---|---|---|---|
| 4 | (0.7071, 1.4142) | 1.9319 | no |
| 5 | (0.8090, 1.2361) | 1.8271 | no |
| 6 | (0.8660, 1.1547) | 1.7321 | no |
| 8 | (0.9239, 1.0824) | 0.2611, 1.5867 | no |
| 12 | (0.9659, 1.0353) | 0.5176, 1.4142 | no |

Closed-form certificate for the nearest merge (`r_e=2, r_o=1`), symbolic in `h`
(so for all `m`), with both window endpoints evaluated on `q`:

```text
q(cos h)              = -3 sin^2 h                         < 0   on (0, pi/4],
q(sec h) * cos^2 h    = -(cos 2h - cos 4h)/2
                      = sin^2 h * (1 - 4 cos^2 h)          < 0   on (0, pi/4],
```

because on `(0, pi/4]` we have `cos^2 h >= 1/2`, hence `1 - 4 cos^2 h <= -1 < 0`.
Both identity checks (`q(cos h) + 3 sin^2 h` and
`q(sec h) cos^2 h - sin^2 h (1 - 4 cos^2 h)`) simplify to exactly `0` in sympy.
Since `q` opens upward and is negative at both endpoints of `[cos h, sec h]`, it
has no root in the closed window: **the nearest 4-set merge cannot occur while
the polygon is strictly convex, for every `m`.**

Interpretation and scope. This strengthens failed-ideas.md #17, which proved
that the specific quarter-turn selected-distance four-pattern on the half-step
two-orbit ansatz is concave. Here the statement is the cleaner, more general
"no even-vertex 4-set of any offset pair is realizable inside the convex window
of the alternating two-radius family", with a closed-form certificate for the
nearest case. It is an EXACT_OBSTRUCTION for this symmetric family only and is
NOT a proof of Erdos #97 (it says nothing about asymmetric polygons, odd
vertices that could couple both rings differently, or `>2` rings).

---

## Asymmetric arm (NUMERICAL_EVIDENCE)

The symmetric family is rigid by construction. The honest question for the lift
is whether breaking the `C_m` symmetry lets a vertex acquire a 4-set while
staying convex. Starting from the convex midpoint base `b0 = (cos h + sec h)/2`
at `m=6` (`n=12`), with the 4th equality enforced as a hard equality residual
and the best configuration rechecked in mpmath at `dps=45`:

- (A) LOCAL -- one even vertex `v*=0` made to have a genuine 4-set
  `D(0,1) = D(0,2) = D(0,10) = D(0,11)`, all other vertices free: the relative
  spread is driven to `2.75e-9` while strictly convex (mpmath convex margin
  `+0.050`, min pair distance `0.18`). A single strictly-convex vertex with
  four concyclic neighbours is geometrically unconstrained, so this is EASY.
  **The k=3 -> k=4 lift is locally unobstructed.**

- (B) GLOBAL -- all six even vertices simultaneously made to have their local
  4-set `D(c, c+-1) = D(c, c+-2)` (the Erdos #97-style stress), full
  deformation: the best worst-center relative spread reached is `6.4e-7` at
  mpmath convex margin `+0.030`, min pair `0.12`. This does NOT reach the
  exactification threshold (`spread < 1e-10`, margin `> 1e-3`) and is recorded
  strictly as a NEAR-MISS. It is consistent with the known B12-type near-miss
  behaviour (failed-ideas.md #7) and establishes nothing on its own.

The decisive qualitative finding is the LOCAL/GLOBAL contrast that #20 never
drew: the lift is free at one vertex and only becomes tight when imposed at
every vertex simultaneously. This is direct, if heuristic, evidence that any
Erdos #97 obstruction must be GLOBAL (a simultaneous, all-vertices phenomenon),
not a single-vertex circle-membership obstruction.

---

## What was NOT established

- No counterexample candidate. The global near-miss (`6.4e-7`) is far from the
  `1e-10` exactification threshold and is not promoted.
- No general obstruction. The exact result is confined to the alternating
  two-radius **symmetric** family; the asymmetric arm is a finite numerical
  deformation scan, not an exhaustive statement over fourth-witness choices,
  deformation directions, `m`, or cyclic orders.
- The closed-form certificate covers only the **nearest** merge `(r_e, r_o) =
  (2, 1)`; the non-nearest merges are checked exactly only for the tabulated
  `m` values (all outside the window), not by a symbolic-in-`m` certificate.
- Odd-vertex 4-sets and configurations on more than two concentric rings are
  out of scope here.
- The asymmetric global deformation may be optimizer-limited; a lower achievable
  spread (or a true obstruction) for the simultaneous all-center system is NOT
  ruled out and would need an exact rank / Positivstellensatz argument (A-lane).

## Suggested next step (not done here)

Promote only the symmetric-arm closed-form result toward a reusable lemma by
extending the nearest-merge certificate to a symbolic-in-`m`, all-offset
statement (currently only the nearest offset has a closed form; the rest are
per-`m` checks). For the global asymmetric stress, the right follow-up is an
exact rank / SOS infeasibility analysis of the simultaneous all-even-center
4-set system at fixed convex cyclic order, which belongs to the A-lane rather
than this continuation lane.
