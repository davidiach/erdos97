# Quarter-cell mixed-derivative cells: exact all-m SMT closure

Trust label: `EXACT_OBSTRUCTION` (SMT + exact symbolic identities), scoped to
the three mixed-derivative signed band cells of the three-orbit quarter-cell
program only. This note upgrades those three cells from the finite
`m = 8, 12, 16` interval certificate
(`docs/quarter-cell-derivative-certificate.md`) to a single exact closure
covering all `m >= 8` at once. The other nine signed cells are closed for
all `m >= 8` by the follow-up dominance artifact
(`docs/quarter-cell-first-derivative-all-m-dominance.md`). Conditional on
the quarter-cell A-row reduction
and boundary-band confinement (`docs/quarter-cell-closure.md`,
review-pending prose). Not a closure of the quarter cells by itself, not the
three-orbit family, not Erdos Problem #97, and not a counterexample.

## What exactly is certified

In the signed-band split of `docs/quarter-cell-signed-band-preflight.md`
(`T = 2*pi/m`, band variables `0 < d, e < delta_m` with
`sin(delta_m) = sin(h)^2 / (2 cos h)`, `h = T/2`, offsets
`beta in {d, T-d}`, `gamma in {e, T-e}`, radius signs `P(y) = ys sin d`,
`P(z) = zs sin e`), the missing exact lemma per cell is:

```text
In each signed boundary-band cell, the listed killer turn is negative
throughout the full strict window.
```

This artifact proves that lemma, for every `m >= 8` at once (hence for every
quarter-cell `m = 0 mod 4`, `m >= 8`), in the three cells whose stored proof
rule is `F(d,0) = F(0,e) = 0 and F_de < 0`:

| cell | beta | gamma | radius signs | killer turn |
| --- | --- | --- | --- | --- |
| `LL_y-_z+` | `d` | `e` | `P(y) = -sin d`, `P(z) = +sin e` | `tau_2` |
| `LH_y+_z+` | `d` | `T-e` | `P(y) = +sin d`, `P(z) = +sin e` | `tau_1` |
| `HH_y+_z-` | `T-d` | `T-e` | `P(y) = +sin d`, `P(z) = -sin e` | `tau_3` |

Here `tau_1, tau_2, tau_3` are the per-period turn determinants
`cross(C_{-1}, A_0, B_0)`, `cross(A_0, B_0, C_0)`, `cross(B_0, C_0, A_1)`
of the preflight, with the radii eliminated through the positive root
`y = ys sin d + sqrt(1 + sin^2 d)` of `P(y) = ys sin d` (and likewise `z`).

## Proof structure

**Step 1 (exact boundary identities, m-uniform).** For each of the three
cells, sympy verifies symbolically that the killer turn `F` satisfies
`F(0, e) == 0` identically in `(e, T)` and `F(d, 0) == 0` identically in
`(d, T)`. (Geometrically: `d = 0` or `e = 0` collapses one orbit point onto
a neighbor, degenerating the relevant turn.)

**Step 2 (mixed-derivative sign, all m at once).** Differentiating `F` in
`d` and `e` uses `dy/dd = ys cos(d) y / S_d` with
`S_d = sqrt(1 + sin^2 d) = y - ys sin d > 0` (and likewise `dz/de`).
Clearing the positive denominator `S_d^a S_e^b` leaves a polynomial
numerator `N` in `(sin d, cos d, sin e, cos e, sin T, cos T, y, z)` with
`sign(F_de) = sign(N)`. Every integer instance embeds in the polynomial
relaxation

```text
ch^2 + sh^2 = 1,  sh > 0,  ch > 0
cT = 2 ch^2 - 1,  sT = 2 sh ch,  cT >= sT          [T in (0, pi/4], i.e. m >= 8]
cd^2 + sd^2 = 1,  sd >= 0,  cd > 0,  2 ch sd <= sh^2    [d in [0, delta]]
ce^2 + se^2 = 1,  se >= 0,  ce > 0,  2 ch se <= sh^2    [e in [0, delta]]
y^2 - 2 ys sd y - 1 = 0,  y > 0
z^2 - 2 zs se z - 1 = 0,  z > 0
```

(cosine monotonicity turns `m >= 8`, i.e. `T <= pi/4`, into `cos T >= sin T`,
and the closed band `sin d <= sin(h)^2/(2 cos h)` into `2 ch sd <= sh^2`;
`2a - p` parity plays no role here -- the band square is a continuous
region, so the only integer data is `T` itself, and the relaxation simply
lets `T` range over all of `(0, pi/4]`). z3 nonlinear real arithmetic
proves `N >= 0` unsatisfiable over this relaxation, for each of the three
cells, so `F_de < 0` on the whole closed band square for every
`T in (0, pi/4]`.

**Step 3 (double integration, elementary).** `F` is smooth on the band
square (`1 + sin^2` never vanishes), so with both boundary edges identically
zero,

```text
F(d, e) = integral_0^d integral_0^e F_de(s, t) dt ds  <  0
```

for all `0 < d, e <= delta`, because the integrand is strictly negative on
the whole rectangle. In particular `F < 0` throughout each strict cell cone
(`d < e`, `d + e < T`, or `e < d` respectively), which is the killer-turn
lemma for these three cells -- now for every `m >= 8`.

## Controls and self-tests

Per cell, the checker records three z3 decisions and two redundant checks:

| decision | expected |
| --- | --- |
| `mixed_derivative_nonnegative` (relaxation + `N >= 0`) | `unsat` |
| `domain_nonempty` (relaxation alone) | `sat` |
| `negative_side_reachable` (relaxation + `N < 0`) | `sat` |

The two `sat` controls show the relaxation is non-empty and sees the
negative side of `N`, so the main `unsat` is neither vacuous nor a
mis-signed contradiction. A deterministic finite-difference lattice ties `N`
back to the raw geometric turn built from the preflight's point coordinates
(sign agreement and positive numerator/derivative ratio at every lattice
point), guarding the symbolic differentiation and denominator-clearing
pipeline. The canonical monomial expansion of each `N` is stored in the
certificate for auditability. An embedding spot-check confirms the
quarter-cell instances `m = 0 mod 4, m in [8, 120]` land in the relaxation.

## Route record for the remaining nine cells

This is the honest boundary of the current technique, recorded so the route
is not blindly re-run:

- The direct all-m killer-turn sign claim (`F >= 0` unsatisfiable over the
  same style of relaxation) returned `unknown` from z3 NRA within 450-480 s
  budgets in both a circle-variable encoding and a 5-variable
  tangent-half-angle rationalization. A plausible structural cause: `F`
  vanishes on the whole `d, e -> 0` boundary (that is the proved boundary
  identity), so the negation is tangent to the feasible set along a curve.
- The nine first-derivative cells (proof rules `F_d < 0` or `F_e < 0` with
  one vanishing edge) do not have that tangency -- their derivative claims
  degenerate only in the `T -> 0` limit -- but z3 NRA still returned
  `unknown` at 120 s per cell on the cleared-numerator encodings. An
  exploratory continuous-`T` numeric screen during development found no
  violation of any of the twelve derivative claims; that screen is not
  archived as an artifact, and only the deterministic finite-difference
  lattice inside the checker is reproducible from this repo.
- The named next target -- a small-T dominance lemma -- is now executed by
  `docs/quarter-cell-first-derivative-all-m-dominance.md`: the corner
  values are exactly `+/-A` with `A = 2 sin(h)(cos h - sin h) = Theta(sin h)`
  while the band radius is `O(sin^2 h)`, and a certified interval Lipschitz
  bound plus two small z3 inequalities close all nine first-derivative
  cells for every `m >= 8`, completing the twelve-cell signed-band closure.

## Commands

```bash
python scripts/check_quarter_cell_mixed_cells_all_m_smt.py --assert-clear
python scripts/check_quarter_cell_mixed_cells_all_m_smt.py --assert-clear \
  --check-artifact data/certificates/quarter_cell_mixed_cells_all_m_smt.json
python -m pytest tests/test_quarter_cell_mixed_cells_all_m_smt.py -q -m "not slow and not exhaustive"
```

The finite-`m` interval certificate
(`scripts/check_quarter_cell_derivative_certificate.py`,
`data/certificates/quarter_cell_derivative_certificate.json`) remains in
place as an independent finite-`m` cross-check; the nine first-derivative
cells, originally left at its `m = 8, 12, 16` grade by this note, are now
closed for all `m >= 8` by
`docs/quarter-cell-first-derivative-all-m-dominance.md`.

## Scope and non-claims

- Covers exactly the three mixed-derivative signed band cells, all
  `m >= 8`. (The nine first-derivative cells, outside this artifact's
  scope, are closed separately by the follow-up dominance artifact.)
- Conditional on the quarter-cell A-row reduction and boundary-band
  confinement (review-pending prose in `docs/quarter-cell-closure.md` and
  `docs/quarter-cell-signed-band-preflight.md`), which reduce quarter-cell
  4-badness to these signed band cells.
- The exactness standard trusts z3's nonlinear-real-arithmetic `unsat`
  answers (as in the repo's other SMT artifacts; no independent proof
  object is stored) and, additionally, sympy's symbolic algebra: the
  boundary identities rest on `simplify`-to-zero, and the polynomial
  numerator `N` that z3 decides is itself produced by sympy
  differentiation, trig expansion, and denominator clearing, guarded by
  the deterministic finite-difference lattice. This is a strictly larger
  symbolic trust root than the pure-z3 precedents
  (`three_square_m4_closure`, `two_orbit_window_all_m_smt`).
- Nothing here closes the `m = 8, 12, 16` quarter cells beyond their
  existing certificates, the all-`m` quarter-cell family, the three-orbit
  program, `n = 9`, or Erdos Problem #97, and the official/global status is
  unchanged.
