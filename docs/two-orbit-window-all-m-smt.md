# Two-orbit window exclusion: exact all-m SMT certificate

Trust label: `EXACT_OBSTRUCTION` (SMT certificate), scoped to the Step 5
window-root exclusion of `docs/two-orbit-circulant-obstruction.md` only. The
parent two-orbit lemma remains a review-pending draft; this note upgrades its
machine audit of Step 5 from a finite float64 screen (`m <= 400`) to one
exact z3 certificate covering all `m >= 3` simultaneously. It is not a proof
of the full two-orbit lemma by itself, not a proof of Erdos Problem #97, and
not a counterexample.

## What exactly is certified

Step 5 of the two-orbit note claims: for every `m >= 3`, with `h = pi/m`,
every same-orbit offset `a in {1, ..., ceil(m/2) - 1}` and every odd
cross-orbit offset `p in {1, ..., m - 1}`, the row equation

```text
E_A:   4 sin^2(ah) = x^2 + 1 - 2x cos(ph)
```

has no root `x` in the open strict-convexity window `(cos h, sec h)`.

This certificate proves that claim, for all `m >= 3` at once, by exhibiting a
single polynomial system whose unsatisfiability (decided by z3 nonlinear real
arithmetic, which is exact for polynomial constraints) implies every integer
instance. It also pins the equality boundary exactly: any contact of `E_A`
with the *closed* window boundary within the relaxation forces
`cos h = 1/2`, `cos 2ah = -1/2`, `cos ph = 1/2` -- the known `m = 3`,
`a = 1`, `p = 1` corner with root `x = sec(pi/3) = 2`, which the open window
excludes.

The claim is conditional on nothing inside Step 5 itself, but its relevance
to the two-orbit lemma is conditional on Steps 1-4 of the parent note (offset
forcing to the half-step, row-shape forcing, and the convexity window
derivation), which remain review-pending prose. Strict convexity enters this
certificate only through the window endpoints `cos h`, `sec h` and through
the openness of the window (both supplied by Step 4).

## Reduction to the window inequalities

On the window, `g(x) = x^2 + 1 - 2x cos(ph)` is strictly increasing:
`g'(x) = 2(x - cos(ph)) > 0` because `x > cos h >= cos(ph)` (using `p >= 1`,
`ph <= pi`, and that cosine is decreasing on `[0, pi]`). So `E_A` has a root
in the open window iff

```text
g(cos h) < 4 sin^2(ah) < g(sec h).
```

Write `ch = cos h`, `sh = sin h`, `u = 2ah`, `v = ph`, `cu = cos u`,
`cv = cos v`, and `T = 2 cv ch - 2 cu`. Using `4 sin^2(ah) = 2 - 2 cu` and
`g(cos h) = ch^2 + 1 - 2 ch cv`, the lower inequality becomes

```text
ch^2 + 1 - 2 ch cv < 2 - 2 cu   <=>   T > ch^2 - 1 = -sh^2.
```

Multiplying the upper inequality `2 - 2 cu < g(1/ch)` by `ch^2 > 0` gives

```text
(2 - 2 cu) ch^2 < 1 + ch^2 - 2 ch cv   <=>   T < (1 - 2 cu) sh^2.
```

This `T`-interval form is the same one used by the parent note's Step 5 and
by the finite screen (`T = C_r + C_{r+1} - 2 C_a = 2 cos(ph) cos h -
2 cos(2ah)` with `p = 2r + 1`).

## Embedding lemma (integer instances land in the relaxation)

Lemma. For every integer `m >= 3`, every `a in {1, ..., ceil(m/2) - 1}`, and
every odd `p in {1, ..., m - 1}`, the point

```text
(ch, sh, cu, su, cv, sv)
  = (cos h, sin h, cos 2ah, sin 2ah, cos ph, sin ph),    h = pi/m,
```

satisfies all constraints (1)-(12) below.

Proof. `h = pi/m in (0, pi/3]`, so `sh > 0` and `ch >= cos(pi/3) = 1/2`
(cosine is decreasing on `[0, pi]`); this gives (1)-(3) with (1) the
Pythagorean identity. For `u = 2ah`: `a >= 1` gives `u >= 2h`, and
`a <= ceil(m/2) - 1` gives `2a <= m - 1` for odd `m` and `2a <= m - 2` for
even `m`, hence `u <= (m-1)h = pi - h` in both cases; so `u in [2h, pi - h]
subset [0, pi]` and `su = sin u >= 0`, giving (4)-(5). For `v = ph`:
`1 <= p <= m - 1` gives `v in [h, pi - h] subset [0, pi]` and `sv >= 0`,
giving (6)-(7). Monotonicity of cosine on `[0, pi]` converts the four range
bounds into (8) `cu <= cos 2h = 2 ch^2 - 1`, (9) `cu >= cos(pi - h) = -ch`,
(10) `cv <= ch`, and (11) `cv >= -ch`. Finally `2a - p` is odd, hence
nonzero, so `|u - v| = |2a - p| h >= h`; both `u, v in [0, pi]` give
`|u - v| in [0, pi]`, so cosine monotonicity yields (12)
`cos(u - v) = cu cv + su sv <= cos h = ch`. QED.

Consequently, if the system (1)-(12) plus the two window inequalities is
unsatisfiable over the reals, then no integer instance `(m, a, p)` satisfies
the window inequalities, i.e. `E_A` never has an open-window root. The
converse direction is not claimed and not needed: a real satisfying point
would not necessarily come from an integer instance, so UNSAT here is
strictly stronger than the integer statement.

## The encoded system

```text
(1)  ch^2 + sh^2 == 1        (5)  su >= 0                 (9)  cu >= -ch
(2)  sh > 0                  (6)  cv^2 + sv^2 == 1        (10) cv <= ch
(3)  ch >= 1/2               (7)  sv >= 0                 (11) cv >= -ch
(4)  cu^2 + su^2 == 1        (8)  cu <= 2 ch^2 - 1        (12) cu cv + su sv <= ch

window lower:   2 cv ch - 2 cu > -sh^2
window upper:   2 cv ch - 2 cu < (1 - 2 cu) sh^2
```

z3 decisions recorded in the certificate:

| decision | system | result |
| --- | --- | --- |
| `main_strict` | (1)-(12) + both strict window inequalities | `unsat` |
| `nonstrict_upper` | upper inequality relaxed to `<=` | `sat` |
| `nonstrict_upper_ch_above_half` | non-strict variant + `ch > 1/2` | `unsat` |
| `nonstrict_upper_off_corner` | non-strict variant + not `(ch, cu, cv) = (1/2, -1/2, 1/2)` | `unsat` |
| `lower_boundary_contact` | (1)-(12) + `T == -sh^2` + non-strict upper | `unsat` |
| `no_gap` | (1)-(11) + strict window inequalities, gap (12) dropped | `sat` |

The `main_strict` UNSAT is the all-m certificate. The three `nonstrict`
decisions prove that the only upper-boundary contact in the relaxation is
the `m = 3` corner, and the `lower_boundary_contact` UNSAT shows exact
lower-boundary contact (a root at `x = cos h`) is impossible in the
relaxation altogether, so the `m = 3` upper corner is the only
closed-boundary contact of any kind. The `no_gap` SAT shows the odd-gap constraint (12) is
load-bearing: without the integer structure `|2a - p| >= 1` the window
inequalities are jointly satisfiable, so the main UNSAT is not an artifact of
a mis-signed contradiction elsewhere in the encoding.

## Exact and redundant self-tests

The checker verifies, in exact rational arithmetic (no z3, no floats):

- the corner point `ch = 1/2, sh^2 = 3/4, cu = -1/2, su^2 = 3/4, cv = 1/2,
  sv^2 = 3/4` satisfies every constraint of the non-strict variant with the
  upper window inequality holding with equality (`T = 3/2 = (1 - 2cu) sh^2`);
- the corner corresponds to `(m, a, p) = (3, 1, 1)`, where `E_A` reads
  `x^2 - x + 1 = 3` with positive root exactly `x = 2 = sec(pi/3)`, the
  excluded open-window endpoint (matching the boundary hit recorded by the
  finite screen);
- the pinned witness `ch = 3/4, sh^2 = 7/16, cu = cv = 0, su = sv = 1`
  (i.e. `u = v = pi/2`) satisfies every constraint except (12), which it
  violates (`1 > 3/4`), certifying the `no_gap` SAT without trusting a z3
  model.

Two float spot-checks, redundant with the exact prose above and with the
finite screen, are also recorded: every integer instance with `m <= 120`
(142,190 pairs, the same count as the screen's `m <= 120` sub-range) maps
into the relaxed region, and the root-location and `T`-form window tests
agree for all instances with `m <= 40` outside a `1e-9` boundary band whose
single member is the `m = 3` corner.

## Commands

```bash
python scripts/check_two_orbit_window_all_m_smt.py --assert-clear
python scripts/check_two_orbit_window_all_m_smt.py --assert-clear \
  --check-artifact data/certificates/two_orbit_window_all_m_smt.json
python -m pytest tests/test_two_orbit_window_all_m_smt.py -q -m ""
```

The finite screen `scripts/check_two_orbit_dynamic_window_lemma.py` remains
in place as an independent per-m cross-check of the same claim through
`m <= 400`; it is now corroborating rather than primary.

## Scope and non-claims

- This certificate covers only Step 5 of the two-orbit circulant obstruction:
  the nonexistence of an open-window root of `E_A` for all valid
  `(m, a, p)`. Steps 1-4 (offset forcing, row-shape forcing, window
  derivation) remain review-pending prose in
  `docs/two-orbit-circulant-obstruction.md`.
- The exactness claim is at the standard of the repo's other SMT artifacts
  (`data/certificates/n8_survivors_smt.json`,
  `data/certificates/three_square_m4_closure.json`): it trusts z3's
  nonlinear-real-arithmetic UNSAT answers; no independent proof object
  (e.g. a positivstellensatz certificate) is stored.
- Nothing here changes the official/global falsifiable/open status, proves
  three-or-more-orbit cases, `n = 9`, or Erdos Problem #97, or produces a
  counterexample.
