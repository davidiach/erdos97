# A2 — Sum-of-Squares / Positivstellensatz infeasibility certificates

Lane: A2 (SOS / moment (Lasserre) relaxation infeasibility certificates).
Date: 2026-06-14. Branch: `claude/amazing-goldberg-8tcsju`.

This note records an attempt to certify, via SOS/moment relaxations, that a
strictly convex `n`-gon with every center 4-equidistant is infeasible. It
validates the pipeline on the known-infeasible `n=8` exact-survivor systems,
applies it to one `n=9` frontier incidence assignment, and reports scaling
honestly.

**No general proof and no counterexample are claimed.** Every statement labelled
EXACT below is produced and checked over the rationals with sympy only (no
floating-point equality). Numeric SDP outputs are labelled NUMERICAL_EVIDENCE.

New ingredient relative to the repo: there was no SOS/SDP machinery in the
codebase. This lane adds (a) a numeric moment/SOS relaxation built on
cvxpy+SCS/CLARABEL and (b) an **exact rational Nullstellensatz / Positivstellensatz
certifier** solved with `fractions.Fraction` linear algebra.

---

## 1. Objects studied

Gauge throughout: `p0=(0,0)`, `p1=(1,0)`, free variables `x2,y2,...` (12 vars for
`n=8`, 14 for `n=9`).

* **n=8 validation**: the 14 post-cyclic-filter `n=8` selected-witness survivor
  classes from `certificates/n8_exact_analysis.json` /
  `certificates/n8_polynomial_systems.txt`. Each class supplies a metric
  *equality* system: perpendicular-bisector (dot + midpoint) equations and full
  equal-distance equations. The repo already proves (machine-checked, review
  pending) that all 15 reconstructed classes are obstructed.
* **n=9 frontier**: assignment `A003` from
  `data/certificates/n9_high_risk_frontier_packet.json` (family F03), with
  `S_i` rows
  `[[1,2,3,8],[0,3,5,7],[1,3,4,6],[2,4,5,8],[0,3,6,8],[2,4,6,7],[1,5,7,8],[0,2,5,6],[0,1,4,7]]`.
  Equalities: 3 equal-distance equations per center (27 total). (This assignment
  is already recorded in the repo as `kill_reason: vertex_circle_self_edge`; the
  SOS work here is an independent cross-check, not a new open-case result.)

---

## 2. Method

Given equalities `g_k(x)=0` and (optional) inequalities `h_j(x)>=0`:

* **Primal moment (Lasserre) relaxation, order d**: seek a pseudo-moment vector
  `y` with `y_0=1`, moment matrix `M_d(y) >= 0`, localizing constraints
  `L_y(g_k x^a)=0` and `L_y(h_j · ...) >= 0` (localizing PSD matrices). If this
  SDP is **infeasible**, the real feasible set is empty (any real solution would
  give a genuine moment vector). Implemented in
  `scripts/exploration/a2_sos_infeasibility.py`.
* **Dual SOS refutation**: `sum_k lambda_k g_k + sigma + 1 = 0`, `sigma` SOS,
  degree `<= 2d`. Feasibility of this SDP is the Positivstellensatz infeasibility
  certificate. Same file.
* **EXACT rational Nullstellensatz** (the rigorous layer):
  `sum_k lambda_k g_k = 1` with `deg lambda_k <= D`. This is a linear feasibility
  problem in the rational coefficients of the `lambda_k`; solved exactly with
  `fractions.Fraction` Gaussian elimination and the identity verified by exact
  polynomial expansion. Implemented in
  `scripts/exploration/a2_sos_exact_certify.py`. An exactly verified identity is
  a rigorous, solver-independent infeasibility certificate **for that one fixed
  incidence class**.
* **Strict-convexity encoding** (plan-recommended, `docs/exactification-plan.md`):
  for a fixed compatible cyclic order, `sign * orient(p_a, p_b, p_j) >= 0` for
  every directed edge `(a,b)` and every non-edge vertex `j` ("all other vertices
  on one side of every edge"). Both orientation signs are tried (CCW and CW).
  Implemented in `scripts/exploration/a2_class14_convexity_sos.py`.

---

## 3. Key structural finding: two regimes among the n=8 classes

Running `a2_sos_exact_certify.py --classify` (a Groebner `1 in ideal?` test per
class) splits the 14 post-cyclic `n=8` classes into:

| regime | classes | meaning |
| --- | --- | --- |
| **equality-empty** | 0,1,2,3,4,5,6,7,8,9,10,11,13 (13 classes) | the metric equality ideal already contains `1`; the perpendicular-bisector + equal-distance system is contradictory **over C** — convexity is NOT needed |
| **convexity-only** | 14 (1 class) | the metric variety is non-empty (a finite set of 4 real points); infeasibility comes **only** from strict convexity |

This refines `docs/n8-exact-survivors.md`: that note kills 0,1,2,6,7,8,9,10,11,13
by "y2 in the rational linear span" and 3,4,5 by duplicate-vertex / collinearity /
Groebner-y2. The SOS-route observation is that once the **full** equal-distance
equations are added to the PB equations, the entire metric ideal of all 13 of
these classes contains `1` (empty over C) — a uniform and slightly stronger
statement than the per-class certificates. For classes 3 and 4 the PB-only ideal
is non-empty (matching the recorded "nondegenerate branch"); adding the full
equal-distance equations is what produces `1 in ideal`.

Consequence for the bridge to Erdos #97: the `n=8` aggregate obstruction is **not**
a single uniform convexity argument. Most classes die on metric equalities alone;
**exactly one class (14) genuinely requires strict convexity**, and it is the
`n=8` analogue of the repo P24 metric-only negative control.

---

## 4. Results

### 4.1 EXACT_OBSTRUCTION — n=8 equality-empty classes (rigorous)

For every equality-empty class a **degree-1 rational Nullstellensatz certificate**
`sum_k lambda_k g_k = 1` exists and is **verified exactly over Q**. Confirmed for
all 13 classes (0–11, 13); see `--certify` output. Example (class 5): 14 nonzero
multipliers, max multiplier degree 1, `exact_identity_verified: true`. Trust
label per class: **EXACT_OBSTRUCTION** (for that fixed incidence class only). This
does NOT use strict convexity — and correctly so, because these classes do not
need it.

Reproduce one:
```
python scripts/exploration/a2_sos_exact_certify.py --certify 5 --mult-deg 1 --json
```

### 4.2 EXACT_OBSTRUCTION — n=8 class 14 via strict convexity (the P24-analogue)

The class-14 metric equality variety is exactly 4 real points (each a square /
diamond on four labels with the other four labels strictly interior; exact
coordinates use `±1/2, ±sqrt(3)/2, ±1, ±(sqrt(3)/2 ± 1)`). Evaluating the
full edge-side convexity polynomials at these 4 exact points, for all 72
compatible cyclic orders and both orientation signs, shows **no branch is
strictly convex in any order** (exact sympy, `no_branch_strictly_convex: true`).
Trust label: **EXACT_OBSTRUCTION** (class 14). **Uses strict convexity** (this is
the only ingredient that excludes the otherwise-valid metric points).

Reproduce:
```
python scripts/exploration/a2_class14_convexity_sos.py
```

### 4.3 NUMERICAL_EVIDENCE — the moment/SOS relaxation genuinely uses convexity

The decisive SDP discriminator, class 14, order `[0,1,2,3,4,5,6,7]`, **d=2 moment
relaxation with SCS**:

| system | status |
| --- | --- |
| equality-only | **feasible** (optimal) |
| equality + convexity localizers (CCW, consecutive-turn) | **infeasible** |
| equality + convexity localizers (CW, consecutive-turn) | **infeasible** |
| equality + convexity localizers (CCW, full edge-side, 48 ineqs) | **infeasible** |
| equality + convexity localizers (CW, full edge-side, 48 ineqs) | **infeasible** |

So the relaxation certifies infeasibility **iff** the strict-convexity constraints
are present, for both orientations — exactly the P24 behaviour: a metric/rank-only
route stays feasible, convexity forces infeasibility. This is NUMERICAL_EVIDENCE
(SCS floating-point) consistent with the EXACT result in 4.2.

### 4.4 n=9 frontier assignment A003

* The 27-equation equal-distance ideal has `1 in ideal` (Groebner): the metric
  variety is **empty over C** — like the `n=8` equality-empty classes, this
  particular frontier assignment is killed by the metric equalities alone, no
  convexity needed.
* **Primal moment relaxation**: d=1 is feasible (too weak); **d=2 with SCS returns
  INFEASIBLE** (moment matrix 120x120, 3060 moments, 3800 equality rows, ~14 s).
  Trust label: **NUMERICAL_EVIDENCE** of infeasibility for the A003 metric
  equality system.
* Exact certificate: degree-1 Nullstellensatz multipliers do **not** suffice for
  A003 (verified, ~6 s); a degree-2 exact certificate is needed. The pure-Python
  rational solver does not reach D=2 in 14 variables within the compute budget
  (~3000+ columns), so **no exact n=9 certificate was produced**.

---

## 5. Methodological finding: trust the exact layer, not the SDP status

At `d=1`, CLARABEL gave inconsistent / spurious statuses on several
equality-empty `n=8` classes (e.g. a SOLVER_ERROR on class 0; "primal optimal /
dual infeasible" on classes 7, 11, 13) **even though** those classes provably have
exactly-verified degree-1 Nullstellensatz certificates. The floating-point SDP
status is therefore **not** a reliable certificate at this scale; only the
rationalized identity is. This reinforces the repo discipline that floating-point
near-equalities are not certificates and checked-in artifacts are inputs.

---

## 6. Scaling discussion (honest)

* **Exact Nullstellensatz**: tractable at `n=8` (D=1, ~20–30 s/class in pure
  Python). At `n=9` the needed multiplier degree rises to D>=2; the rational
  Gaussian-elimination solver has ~3000+ columns and does not finish within
  budget. A C-backed exact linear solver (e.g. FLINT) or a Groebner-cofactor
  extraction would be required to push `n=9` exact.
* **Numeric moment SDP**: `d=1` is uniformly too weak (degree-2 equalities and
  convexity need order-2 localizers). `d=2` is the working order, with moment
  matrix `91x91` (`n=8`) / `120x120` (`n=9`). **CLARABEL is unreliable at d=2**
  here (failed on class 14); **SCS is the workhorse** and solved every d=2 case
  tried (~14–50 s). The dominant cost is the `d=2` moment-matrix PSD block plus
  thousands of equality rows; this will grow roughly like the number of degree-4
  monomials in `2(n-2)` variables and become impractical by `n` in the low teens
  without symmetry reduction or exact preprocessing to eliminate variables.

---

## 7. What this does and does NOT establish

**Rules out (for the studied objects, rigorously):**
* Each of the 13 equality-empty `n=8` classes — no real configuration satisfies
  its metric equalities (exact Nullstellensatz). [does not use convexity]
* `n=8` class 14 — no strictly convex configuration satisfies its metric
  equalities (exact edge-side test at the 4 variety points). [uses strict
  convexity]

**Does NOT rule out / does NOT establish:**
* Anything about the general Erdos #97 problem or any `n >= 9` open case.
* No counterexample is found or implied (the contrary: every studied system is
  infeasible).
* No exact `n=9` SOS/Nullstellensatz certificate (only NUMERICAL_EVIDENCE for
  A003, which is already a repo-obstructed assignment anyway).
* The d=2 SCS "infeasible" statuses are floating-point and are NOT exact
  certificates.

**Bridge strengthened:** modestly. The SOS lane contributes an *independent*
exact infeasibility route for the `n=8` equality-empty classes (degree-1
Nullstellensatz, orthogonal to the repo's linear-span / Groebner certificates),
and an independent exact + numeric confirmation that class 14 is convexity-only.
The pipeline is validated to use strict convexity correctly (it fires on class 14
only when convexity is added, both orientations), satisfying the P24 guardrail.
The new exact certifier is reusable for any fixed incidence class at `n<=8`.

---

## 8. Reproduction

```bash
# regime split (which n=8 classes need convexity)
python scripts/exploration/a2_sos_exact_certify.py --classify

# exact degree-1 Nullstellensatz certificate for an equality-empty class
python scripts/exploration/a2_sos_exact_certify.py --certify 5 --mult-deg 1 --json
python scripts/exploration/a2_sos_exact_certify.py --certify 7 --mult-deg 1
# (works for all of 0,1,2,3,4,5,6,7,8,9,10,11,13)

# exact strict-convexity obstruction for class 14 (4 variety points x 72 orders)
python scripts/exploration/a2_class14_convexity_sos.py

# numeric moment/SOS relaxation driver (n=8 classes)
python scripts/exploration/a2_sos_infeasibility.py 5 1     # class, order d
```

The numeric class-14 d=2 convexity probe and the n=9 d=2 primal moment run use
SCS (CLARABEL is unreliable at d=2); see the `moment_probe(..., solver="SCS")`
and `solve_primal(..., solver="SCS")` entry points. Each d=2 SDP is ~14–50 s.

## 9. Files

* `scripts/exploration/a2_sos_infeasibility.py` — numeric moment + dual SOS
  relaxation (pre-existing scaffold; numpy import cleaned).
* `scripts/exploration/a2_sos_exact_certify.py` — exact rational Nullstellensatz
  certifier + regime classifier (new).
* `scripts/exploration/a2_class14_convexity_sos.py` — exact + numeric
  strict-convexity probe for class 14 (new).

`ruff check` passes on all three. No general proof claim, no counterexample
claim. All EXACT results are sympy-verified over Q; all SDP results are
NUMERICAL_EVIDENCE.
